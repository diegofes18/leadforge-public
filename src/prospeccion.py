"""Prospección de negocios locales con Google Places API (New).

Ejemplo:
    python -m src.prospeccion --query "peluquerías" --location "Madrid, España" --radius 5000 --max-results 60
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import config
from .utils import slugify

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prospección de negocios locales vía Google Places API (New).",
    )
    parser.add_argument("--query", required=True, help='Tipo de negocio. Ej: "peluquerías"')
    parser.add_argument("--location", required=True, help='Ubicación. Ej: "Madrid, España"')
    parser.add_argument(
        "--radius",
        type=int,
        default=config.DEFAULT_RADIUS_METERS,
        help=f"Radio en metros (default {config.DEFAULT_RADIUS_METERS}).",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=config.DEFAULT_MAX_RESULTS,
        help=f"Número máximo de resultados (default {config.DEFAULT_MAX_RESULTS}).",
    )
    return parser.parse_args()


def ensure_api_key() -> str:
    if not config.GOOGLE_PLACES_API_KEY:
        console.print(
            Panel.fit(
                "[bold red]Falta la API key de Google Places.[/bold red]\n\n"
                "1. Copia [cyan].env.example[/cyan] a [cyan].env[/cyan]\n"
                "2. Pega tu key en [cyan]GOOGLE_PLACES_API_KEY=...[/cyan]\n"
                "3. Activa [cyan]Places API (New)[/cyan] en Google Cloud Console\n"
                "   https://console.cloud.google.com/apis/library/places.googleapis.com",
                title="Configuración requerida",
                border_style="red",
            )
        )
        sys.exit(1)
    return config.GOOGLE_PLACES_API_KEY


def search_places(
    query: str,
    location: str,
    radius_meters: int,
    max_results: int,
    api_key: str,
) -> list[dict[str, Any]]:
    """Llama a places:searchText paginando hasta cubrir max_results."""
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": config.FIELD_MASK,
    }
    text_query = f"{query} en {location}"

    results: list[dict[str, Any]] = []
    page_token: str | None = None
    page_num = 0

    with httpx.Client(timeout=30.0) as client:
        while len(results) < max_results:
            page_num += 1
            remaining = max_results - len(results)
            page_size = min(config.PAGE_SIZE, remaining)

            body: dict[str, Any] = {
                "textQuery": text_query,
                "pageSize": page_size,
                "languageCode": config.LANGUAGE_CODE,
                "regionCode": config.REGION_CODE,
            }
            if radius_meters:
                # La API New no permite restringir por radio en Text Search, solo sesgar con
                # locationBias circular. Sin coords explícitas, la API resuelve location desde textQuery.
                pass
            if page_token:
                body["pageToken"] = page_token

            console.print(f"[dim]→ Página {page_num} (pageSize={page_size})…[/dim]")

            try:
                resp = client.post(config.PLACES_TEXT_SEARCH_URL, headers=headers, json=body)
            except httpx.HTTPError as exc:
                console.print(f"[bold red]Error de red:[/bold red] {exc}")
                break

            if resp.status_code != 200:
                console.print(
                    f"[bold red]Error API ({resp.status_code}):[/bold red] {resp.text}"
                )
                break

            data = resp.json()
            places = data.get("places", []) or []
            results.extend(places)

            page_token = data.get("nextPageToken")
            if not page_token or not places:
                break

            # El token recién creado necesita unos segundos para activarse en la API New.
            time.sleep(2)

    return results[:max_results]


def score_lead(row: dict[str, Any]) -> tuple[str, str]:
    """Devuelve (prioridad, motivo) según las reglas de negocio."""
    rating = row.get("rating") or 0.0
    reviews = row.get("userRatingCount") or 0
    tiene_web = row.get("tiene_web", False)

    if rating >= config.SCORE_ALTA_MIN_RATING and reviews >= config.SCORE_ALTA_MIN_REVIEWS:
        prioridad, motivo = "ALTA", "Negocio sólido y bien valorado"
    elif rating >= config.SCORE_MEDIA_MIN_RATING and reviews >= config.SCORE_MEDIA_MIN_REVIEWS:
        prioridad, motivo = "MEDIA", "Negocio con buena reputación"
    else:
        prioridad, motivo = "BAJA", "Pocas reseñas o rating bajo"

    if not tiene_web:
        motivo = f"{motivo} (sin web)"

    return prioridad, motivo


def normalize_places(raw_places: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for p in raw_places:
        display = (p.get("displayName") or {}).get("text", "")
        website = p.get("websiteUri", "") or ""
        row = {
            "displayName": display,
            "formattedAddress": p.get("formattedAddress", ""),
            "internationalPhoneNumber": p.get("internationalPhoneNumber", ""),
            "websiteUri": website,
            "tiene_web": bool(website.strip()),
            "rating": p.get("rating"),
            "userRatingCount": p.get("userRatingCount"),
            "googleMapsUri": p.get("googleMapsUri", ""),
            "businessStatus": p.get("businessStatus", ""),
            "primaryType": p.get("primaryType", ""),
        }
        prioridad, motivo = score_lead(row)
        row["prioridad"] = prioridad
        row["motivo"] = motivo
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        order = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
        df = df.sort_values(
            by=["prioridad", "userRatingCount"],
            key=lambda col: col.map(order) if col.name == "prioridad" else col,
            ascending=[True, False],
        ).reset_index(drop=True)
    return df


def build_output_path(query: str, location: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    name = f"prospeccion_{slugify(query)}_{slugify(location)}_{stamp}.csv"
    return config.OUTPUT_DIR / name


def print_summary(df: pd.DataFrame, output_path: Path) -> None:
    total = len(df)
    counts = df["prioridad"].value_counts().to_dict() if total else {}
    alta = counts.get("ALTA", 0)
    media = counts.get("MEDIA", 0)
    baja = counts.get("BAJA", 0)

    console.print()
    console.print(
        Panel.fit(
            f"[bold]Total encontrados:[/bold] {total}\n"
            f"[green]ALTA:[/green]  {alta}\n"
            f"[yellow]MEDIA:[/yellow] {media}\n"
            f"[dim]BAJA:[/dim]  {baja}\n\n"
            f"[bold]CSV guardado en:[/bold] {output_path}",
            title="Resumen prospección",
            border_style="cyan",
        )
    )

    top_alta = df[df["prioridad"] == "ALTA"].head(5)
    if top_alta.empty:
        console.print("[dim]No hay leads de prioridad ALTA en esta búsqueda.[/dim]")
        return

    table = Table(title="Top 5 leads ALTA", show_lines=False)
    table.add_column("#", style="dim", width=3)
    table.add_column("Nombre", style="bold")
    table.add_column("Tel.", style="cyan")
    table.add_column("Rating", justify="right")
    table.add_column("Reviews", justify="right")
    table.add_column("Web", justify="center")
    table.add_column("Dirección", style="dim")

    for i, (_, row) in enumerate(top_alta.iterrows(), start=1):
        table.add_row(
            str(i),
            str(row["displayName"]),
            str(row["internationalPhoneNumber"] or "—"),
            f"{row['rating']}" if pd.notna(row["rating"]) else "—",
            f"{int(row['userRatingCount'])}" if pd.notna(row["userRatingCount"]) else "—",
            "Sí" if bool(row.get("tiene_web")) else "No",
            str(row["formattedAddress"]),
        )
    console.print(table)


def main() -> int:
    args = parse_args()
    api_key = ensure_api_key()

    console.print(
        Panel.fit(
            f"[bold]Query:[/bold] {args.query}\n"
            f"[bold]Ubicación:[/bold] {args.location}\n"
            f"[bold]Radio:[/bold] {args.radius} m\n"
            f"[bold]Máx. resultados:[/bold] {args.max_results}",
            title="Prospección",
            border_style="cyan",
        )
    )

    raw = search_places(
        query=args.query,
        location=args.location,
        radius_meters=args.radius,
        max_results=args.max_results,
        api_key=api_key,
    )

    if not raw:
        console.print("[bold yellow]No se obtuvieron resultados.[/bold yellow]")
        return 1

    df = normalize_places(raw)
    output_path = build_output_path(args.query, args.location)
    df.to_csv(output_path, index=False, encoding="utf-8")

    print_summary(df, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

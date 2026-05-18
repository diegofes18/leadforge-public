"""Deduplica y consolida todos los CSV de prospección en uno solo.

Uso:
    python -m src.dedupe
    python -m src.dedupe --input-dir output/
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import config
from .utils import first_address_line, normalize_phone

console = Console()

PRIORITY_RANK = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deduplica y consolida CSVs de prospección.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=config.OUTPUT_DIR,
        help=f"Carpeta con los CSV prospeccion_*.csv (default: {config.OUTPUT_DIR}).",
    )
    return parser.parse_args()


def load_csvs(input_dir: Path) -> tuple[pd.DataFrame, int]:
    csv_files = sorted(input_dir.glob("prospeccion_*.csv"))
    if not csv_files:
        return pd.DataFrame(), 0

    frames: list[pd.DataFrame] = []
    for path in csv_files:
        try:
            frames.append(pd.read_csv(path))
        except Exception as exc:
            console.print(f"[yellow]Aviso:[/yellow] no se pudo leer {path.name}: {exc}")

    if not frames:
        return pd.DataFrame(), 0

    df = pd.concat(frames, ignore_index=True, sort=False)
    return df, len(csv_files)


def dedupe(df: pd.DataFrame) -> pd.DataFrame:
    """Dedupe en cascada: teléfono → googleMapsUri → nombre+dirección."""
    if df.empty:
        return df

    df = df.copy()

    for col in (
        "displayName",
        "formattedAddress",
        "internationalPhoneNumber",
        "googleMapsUri",
        "websiteUri",
        "rating",
        "userRatingCount",
        "prioridad",
        "motivo",
        "tiene_web",
    ):
        if col not in df.columns:
            df[col] = pd.NA

    df["_rank"] = df["prioridad"].map(PRIORITY_RANK).fillna(3).astype(int)
    df["_reviews"] = pd.to_numeric(df["userRatingCount"], errors="coerce").fillna(0)
    df = df.sort_values(by=["_rank", "_reviews"], ascending=[True, False]).reset_index(drop=True)

    df["_phone_norm"] = df["internationalPhoneNumber"].apply(normalize_phone)
    df["_maps_uri"] = df["googleMapsUri"].fillna("").astype(str).str.strip()
    df["_name_addr"] = (
        df["displayName"].fillna("").astype(str).str.lower().str.strip()
        + "||"
        + df["formattedAddress"].apply(first_address_line)
    )

    keep = pd.Series(True, index=df.index)

    seen_phones: set[str] = set()
    for idx, val in df["_phone_norm"].items():
        if not val:
            continue
        if val in seen_phones:
            keep.at[idx] = False
        else:
            seen_phones.add(val)

    seen_uris: set[str] = set()
    for idx in df.index[keep]:
        val = df.at[idx, "_maps_uri"]
        if not val:
            continue
        if val in seen_uris:
            keep.at[idx] = False
        else:
            seen_uris.add(val)

    seen_names: set[str] = set()
    for idx in df.index[keep]:
        val = df.at[idx, "_name_addr"]
        if val == "||" or not val.replace("|", "").strip():
            continue
        if val in seen_names:
            keep.at[idx] = False
        else:
            seen_names.add(val)

    result = df[keep].drop(
        columns=["_rank", "_reviews", "_phone_norm", "_maps_uri", "_name_addr"]
    )

    result = result.assign(
        _rank=result["prioridad"].map(PRIORITY_RANK).fillna(3).astype(int),
        _reviews=pd.to_numeric(result["userRatingCount"], errors="coerce").fillna(0),
    )
    result = result.sort_values(
        by=["_rank", "_reviews"], ascending=[True, False]
    ).drop(columns=["_rank", "_reviews"]).reset_index(drop=True)

    return result


def build_output_path() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    return config.OUTPUT_DIR / f"leads_consolidados_{stamp}.csv"


def print_summary(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    n_files: int,
    output_path: Path,
) -> None:
    total_before = len(df_before)
    total_after = len(df_after)
    eliminados = total_before - total_after

    counts = df_after["prioridad"].value_counts().to_dict() if total_after else {}
    alta = counts.get("ALTA", 0)
    media = counts.get("MEDIA", 0)
    baja = counts.get("BAJA", 0)

    console.print()
    console.print(
        Panel.fit(
            f"[bold]Archivos procesados:[/bold] {n_files}\n"
            f"[bold]Filas leídas (antes):[/bold] {total_before}\n"
            f"[bold]Filas tras dedupe:[/bold] {total_after}\n"
            f"[bold]Duplicados eliminados:[/bold] {eliminados}\n\n"
            f"[green]ALTA:[/green]  {alta}\n"
            f"[yellow]MEDIA:[/yellow] {media}\n"
            f"[dim]BAJA:[/dim]  {baja}\n\n"
            f"[bold]CSV consolidado:[/bold] {output_path}",
            title="Deduplicación",
            border_style="cyan",
        )
    )

    top_alta = df_after[df_after["prioridad"] == "ALTA"].head(10)
    if top_alta.empty:
        console.print("[dim]No hay leads de prioridad ALTA en el consolidado.[/dim]")
        return

    table = Table(title="Top 10 leads ALTA consolidados", show_lines=False)
    table.add_column("#", style="dim", width=3)
    table.add_column("Nombre", style="bold")
    table.add_column("Rating", justify="right")
    table.add_column("Reviews", justify="right")
    table.add_column("Web", justify="center")
    table.add_column("Dirección", style="dim")

    for i, (_, row) in enumerate(top_alta.iterrows(), start=1):
        rating = row.get("rating")
        reviews = row.get("userRatingCount")
        tiene_web = row.get("tiene_web")
        if isinstance(tiene_web, str):
            tiene_web = tiene_web.strip().lower() == "true"
        web_str = "Sí" if bool(tiene_web) else "No"

        table.add_row(
            str(i),
            str(row.get("displayName", "")),
            f"{rating}" if pd.notna(rating) else "—",
            f"{int(reviews)}" if pd.notna(reviews) else "—",
            web_str,
            str(row.get("formattedAddress", "")),
        )
    console.print(table)


def main() -> int:
    args = parse_args()
    input_dir: Path = args.input_dir

    if not input_dir.exists() or not input_dir.is_dir():
        console.print(f"[bold red]No existe la carpeta:[/bold red] {input_dir}")
        return 1

    df_raw, n_files = load_csvs(input_dir)
    if df_raw.empty:
        console.print(
            Panel.fit(
                f"[bold red]No hay CSVs prospeccion_*.csv en[/bold red] {input_dir}\n"
                f"Ejecuta primero [cyan]python -m src.prospeccion …[/cyan] para generar datos.",
                title="Sin datos",
                border_style="red",
            )
        )
        return 1

    df_clean = dedupe(df_raw)
    output_path = build_output_path()
    df_clean.to_csv(output_path, index=False, encoding="utf-8")

    print_summary(df_raw, df_clean, n_files, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

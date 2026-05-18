"""Pipeline end-to-end programático (alternativa a los 3 comandos CLI).

Útil si quieres encadenarlo desde un script propio, un cron, o un notebook.

Uso:
    .venv/bin/python examples/ejemplo_uso.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite ejecutar el script desde la raíz del repo sin haberlo instalado como paquete.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.prospeccion import (
    ensure_api_key,
    normalize_places,
    search_places,
    build_output_path,
)
from src.dedupe import dedupe, load_csvs, build_output_path as dedupe_output_path


QUERIES = [
    "fisioterapeuta",
    "clínica fisioterapia",
    "centro de fisioterapia",
]
LOCATION = "Madrid, España"
MAX_RESULTS = 30


def main() -> int:
    api_key = ensure_api_key()

    # ── Fase 1: prospección para cada query ──
    for query in QUERIES:
        print(f"\n▶ Prospectando: {query}")
        raw = search_places(
            query=query,
            location=LOCATION,
            radius_meters=config.DEFAULT_RADIUS_METERS,
            max_results=MAX_RESULTS,
            api_key=api_key,
        )
        if not raw:
            print(f"  (sin resultados para {query!r})")
            continue
        df = normalize_places(raw)
        out = build_output_path(query, LOCATION)
        df.to_csv(out, index=False, encoding="utf-8")
        print(f"  → {len(df)} leads en {out.name}")

    # ── Fase 1.5: dedupe ──
    print("\n▶ Consolidando + deduplicando")
    df_raw, n_files = load_csvs(config.OUTPUT_DIR)
    if df_raw.empty:
        print("  (no se encontró ningún CSV de prospección)")
        return 1
    df_clean = dedupe(df_raw)
    out = dedupe_output_path()
    df_clean.to_csv(out, index=False, encoding="utf-8")
    print(f"  → {n_files} archivos → {len(df_clean)} leads únicos en {out.name}")

    print("\n✓ Pipeline de prospección terminado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Configuración global de LeadForge."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()

PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# FieldMask: la API (New) exige declarar explícitamente los campos que devuelve.
# Cada campo extra puede afectar al SKU facturado, así que pedimos solo lo necesario.
FIELD_MASK = ",".join(
    [
        "places.displayName",
        "places.formattedAddress",
        "places.internationalPhoneNumber",
        "places.websiteUri",
        "places.rating",
        "places.userRatingCount",
        "places.googleMapsUri",
        "places.businessStatus",
        "places.primaryType",
        "nextPageToken",
    ]
)

DEFAULT_RADIUS_METERS = 5000
DEFAULT_MAX_RESULTS = 60
PAGE_SIZE = 20  # máximo permitido por la API
LANGUAGE_CODE = "es"
REGION_CODE = "ES"

# Umbrales del scoring (independientes de si tiene web)
SCORE_ALTA_MIN_RATING = 4.5
SCORE_ALTA_MIN_REVIEWS = 30
SCORE_MEDIA_MIN_RATING = 4.0
SCORE_MEDIA_MIN_REVIEWS = 10

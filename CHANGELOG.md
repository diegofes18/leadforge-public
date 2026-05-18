# Changelog

Todos los cambios relevantes de LeadForge se documentan en este archivo.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [1.0.0] — 2026-05-18 — Community Edition

### Lanzamiento inicial

- Prospección automática vía **Google Places API (New)** con paginación y `FieldMask` optimizado para coste.
- Scoring automático **ALTA / MEDIA / BAJA** por rating + nº de reseñas (con detección de "sin web").
- **Deduplicación inteligente** en cascada: teléfono → `googleMapsUri` → nombre+dirección.
- CLI con `rich`: tablas, paneles y resumen.
- Estructura de paquete (`src/`) con módulos invocables como `python -m src.<modulo>`.
- Guías: `QUICKSTART`, `CONFIGURACION_APIS`, `ARQUITECTURA`, `CASOS_DE_USO`, `FAQ`.
- `setup.sh` automatizado (venv + deps + `.env`).
- Ejemplos en `examples/` con datos ficticios.

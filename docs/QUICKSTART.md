# Quickstart — De cero a tu primer CSV en 5 minutos

Este flujo asume **Linux o macOS** y **Python 3.10+** ya instalado.
En Windows funciona idéntico desde WSL2 o Git Bash.

---

## 1. Clona el repo

```bash
git clone https://github.com/TU-USUARIO/leadforge-public leadforge
cd leadforge
```

## 2. Setup automático

```bash
bash setup.sh
```

El script:

1. Comprueba que tienes Python 3.10+.
2. Crea un entorno virtual en `.venv/`.
3. Instala las 4 dependencias (`httpx`, `pandas`, `rich`, `python-dotenv`).
4. Copia `.env.example` → `.env`.

Tarda ~30 segundos.

## 3. Configura la API key

Edita `.env` (recién creado) y pega tu key de Google Places:

```
GOOGLE_PLACES_API_KEY=AIza...
```

¿De dónde sacas la key? Guía paso a paso en [`CONFIGURACION_APIS.md`](CONFIGURACION_APIS.md).

## 4. Tu primera prospección

```bash
.venv/bin/python -m src.prospeccion \
    --query "fisioterapeuta" \
    --location "Madrid, España" \
    --max-results 30
```

Verás algo así en consola:

```
╭─── Prospección ───╮
│ Query: fisioterapeuta
│ Ubicación: Madrid, España
│ Radio: 5000 m
│ Máx. resultados: 30
╰────────────────────╯
→ Página 1 (pageSize=20)…
→ Página 2 (pageSize=10)…

╭── Resumen prospección ──╮
│ Total encontrados: 30
│ ALTA:  18
│ MEDIA: 9
│ BAJA:  3
│ CSV guardado en: output/prospeccion_fisioterapeuta_madrid_espa_a_20260518_1230.csv
╰─────────────────────────╯
```

El CSV está en `output/` y contiene: nombre, dirección, teléfono, web, rating, nº reseñas, prioridad y motivo.

## 5. (Opcional) Lanza varias búsquedas y deduplica

Repite el paso 4 con queries distintas (`clínica fisioterapia`, `centro de fisioterapia`, etc.) y consolida con:

```bash
.venv/bin/python -m src.dedupe
```

Genera `output/leads_consolidados_*.csv` sin duplicados (cascada teléfono → URI → nombre+dirección).

---

## Próximos pasos

- 📖 Lee [`CASOS_DE_USO.md`](CASOS_DE_USO.md) para queries listas para copiar (dentistas, gestorías, abogados, etc.).
- 🏗️ Lee [`ARQUITECTURA.md`](ARQUITECTURA.md) si quieres extender el pipeline.
- ❓ Si algo falla, mira [`FAQ.md`](FAQ.md).

> 💡 ¿Quieres además **auditar las webs de tus leads con IA** (screenshots, Lighthouse, pitch personalizado)? Es lo que añade la versión Pro: [bermejowebs.com](https://bermejowebs.com).

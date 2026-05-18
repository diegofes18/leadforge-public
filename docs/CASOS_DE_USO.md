# Casos de uso — 5 nichos listos para copiar

Cada caso incluye:

- **Queries exactas** (varias por nicho para combinar y dedupar).
- **Qué esperar** (volumen aproximado, % con web, % prioridad ALTA).
- **Qué hacer con los datos** (cómo abordar la venta).

> Los volúmenes son orientativos basados en pruebas reales en mayo 2026.

---

## 🩺 1. Fisioterapeutas en Madrid

```bash
.venv/bin/python -m src.prospeccion --query "fisioterapeuta" --location "Madrid, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "clínica fisioterapia" --location "Madrid, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "centro de fisioterapia" --location "Madrid, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "fisioterapia deportiva" --location "Madrid, España" --max-results 60
.venv/bin/python -m src.dedupe
```

**Esperable:** ~180-220 leads únicos tras dedupe. ~85% con web. ~40% prioridad ALTA. Coste total: ~$0.60.

**Aproximación de venta:** la mayoría tiene web pero antigua (sin reservas online, sin WhatsApp visible). Filtra por `prioridad=ALTA` y abre las webs una a una para detectar oportunidades.

---

## 🦷 2. Dentistas en Barcelona

```bash
.venv/bin/python -m src.prospeccion --query "dentista" --location "Barcelona, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "clínica dental" --location "Barcelona, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "implantes dentales" --location "Barcelona, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "ortodoncia" --location "Barcelona, España" --max-results 60
.venv/bin/python -m src.dedupe
```

**Esperable:** ~250-300 leads únicos. Casi 100% con web (sector muy competitivo). Solo ~25% prioridad ALTA.

**Aproximación:** nicho saturado, casi todos tienen agencia. Filtra por `userRatingCount > 100` para encontrar los que **facturan bien pero pueden descuidar la web**. Ahí está la oportunidad.

---

## ⚖️ 3. Abogados en Valencia

```bash
.venv/bin/python -m src.prospeccion --query "abogado laboralista" --location "Valencia, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "despacho de abogados" --location "Valencia, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "abogado familia" --location "Valencia, España" --max-results 60
.venv/bin/python -m src.dedupe
```

> ⚠️ **Baja umbrales antes** en `src/config.py` → `SCORE_ALTA_MIN_REVIEWS = 10` (los abogados tienen muchas menos reseñas que un fisio).

**Esperable:** ~150 leads únicos. ~70% con web. Pocas reseñas en general → más MEDIA que ALTA.

**Aproximación:** nicho con tickets altos (3.000€+ por web), pero ciclo de venta largo. **Filtra por sin web (`tiene_web=False`)**: ahí hay despachos rentables que aún no se han subido a internet.

---

## 📋 4. Gestorías en Sevilla

```bash
.venv/bin/python -m src.prospeccion --query "gestoría administrativa" --location "Sevilla, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "asesoría fiscal" --location "Sevilla, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "asesoría laboral" --location "Sevilla, España" --max-results 60
.venv/bin/python -m src.dedupe
```

**Esperable:** ~120-150 leads. ~75% con web, pero la mayoría son **webs de 2010-2015** sin responsive serio.

**Aproximación:** sector con poca rotación de clientes (alta LTV). Ofrecer rediseño + portal de cliente (subida de docs).

---

## 🍽️ 5. Restaurantes en Bilbao

```bash
.venv/bin/python -m src.prospeccion --query "restaurante" --location "Bilbao, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "bar de pintxos" --location "Bilbao, España" --max-results 60
.venv/bin/python -m src.prospeccion --query "asador" --location "Bilbao, España" --max-results 60
.venv/bin/python -m src.dedupe
```

**Esperable:** ~200 leads. **Solo ~40% tiene web**: la mayoría delega todo a Instagram + Google Maps. ALTA muy elevada por volumen de reseñas.

**Aproximación:** no vendas "web" — vende **"sistema de reservas + carta digital con QR + integración Google Maps"**. Filtra los `tiene_web=False` para encontrar los más necesitados.

---

## Patrón para cualquier nicho nuevo

1. **3-5 queries variadas** (sinónimos, especialidades, formato de negocio).
2. `dedupe` consolida y elimina solapamientos.
3. Abre el CSV consolidado y filtra los `prioridad=ALTA` que más te interesen (por reseñas, por barrio, etc.).
4. Llama / mandar email a los top 10-20.

Coste medio del flujo en un nicho nuevo: **~$0.50** y ~10 minutos de tu tiempo.

---

> 💡 ¿Quieres saltarte el paso de abrir cada web una a una? La versión Pro automatiza la auditoría visual y te genera un **pitch personalizado por lead** mencionando 1-2 problemas concretos de SU web. Más info: [bermejowebs.com](https://bermejowebs.com).

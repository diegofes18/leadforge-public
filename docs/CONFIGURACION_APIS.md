# Configuración de APIs — paso a paso

LeadForge Community usa **1 API externa**: Google Places API (New). El crédito de $200/mes de Google Cloud cubre el uso normal de un freelancer o agencia.

| API | Para qué | Coste real |
|---|---|---|
| Google Places API (New) | Buscar negocios | ~$0.12 / 60 leads; **$200/mes gratis** |

---

## Google Places API (New)

### 1. Crear un proyecto en Google Cloud

1. Entra en https://console.cloud.google.com/
2. Arriba a la izquierda, abre el selector de proyectos → **NUEVO PROYECTO**.
3. Nombre sugerido: `leadforge-prod`. Pulsa **Crear**.

> Si ya tienes un proyecto, puedes reutilizarlo.

### 2. Activar facturación

Google exige tarjeta para usar Places, **aunque no te cobrará nada hasta superar los $200/mes de crédito gratuito**.

1. Ve a https://console.cloud.google.com/billing
2. Vincula una cuenta de facturación al proyecto recién creado.

### 3. Habilitar la API "Places API (New)"

> ⚠️ Es la **New**, no la antigua "Places API". Son productos distintos con SKUs distintos.

1. Ve a https://console.cloud.google.com/apis/library/places.googleapis.com
2. Verifica que arriba pone "Places API (New)".
3. Pulsa **Habilitar**.

### 4. Crear la API key

1. Ve a **APIs y servicios → Credenciales**.
2. **Crear credenciales → Clave de API**.
3. Te aparecerá un modal con la key (`AIzaSy...`). **Cópiala YA**, luego es más difícil volver a verla completa.

### 5. Restringir la key (recomendado)

Una key sin restricciones es un riesgo: si se filtra, alguien podría hacer requests a tu cuenta.

1. En la lista de credenciales, pulsa el lápiz junto a tu key.
2. En **Restricciones de aplicación** → elige "Direcciones IP" si la usarás desde un servidor concreto, o déjalo en "Ninguno" si la usarás en local.
3. En **Restricciones de API** → "Restringir clave" → marca **Places API (New)**.
4. **Guardar**.

### 6. Pega la key en tu `.env`

```
GOOGLE_PLACES_API_KEY=AIzaSy_tu_key_aqui
```

---

## Tabla de costes

| Acción | Coste aproximado |
|---|---|
| 1 búsqueda Google Places (20 resultados, 1 página) | ~$0.04 |
| 1 búsqueda Google Places (60 resultados, 3 páginas) | ~$0.12 |
| 50 búsquedas / mes (uso típico) | ~$6 — **dentro del crédito gratuito** |

Los $200/mes de crédito dan para ~1.500 búsquedas. Para uso normal, es **de facto gratis**.

---

## Verificar que la key funciona

```bash
.venv/bin/python -c "from src import config; print('places:', 'OK' if config.GOOGLE_PLACES_API_KEY else 'FALTA')"
```

Salida esperada:

```
places: OK
```

---

> 💡 La versión Pro añade además **PageSpeed Insights** (gratis) y **Anthropic Claude** (~$0.02/lead) para auditar webs y generar pitches personalizados. Más info: [bermejowebs.com](https://bermejowebs.com).

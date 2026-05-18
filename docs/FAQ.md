# FAQ

## 💰 ¿Cuánto cuesta usar la API?

**Google Places (New)**: ~$0.12 por búsqueda de 60 leads. Google da **$200/mes de crédito gratis**, suficiente para ~1.500 búsquedas/mes. En la práctica, **gratis** para uso normal.

---

## ⚖️ ¿Es legal usar la Google Places API así?

Sí. Estás llamando a la API oficial de Google con tu propia key, pagando los SKUs que correspondan. **No es scraping**, son requests HTTP autorizados.

Los datos devueltos (nombre, dirección, teléfono, web) son **datos de negocio públicos**. No estás capturando información personal de clientes ni de empleados.

**Lo que sí debes cumplir:**

- No revender los datos en bruto (los ToS de Google lo prohíben).
- Atribuir Google Maps si publicas los datos en algún lado (raro, normalmente solo los usas para tu CRM/contacto).

---

## 💼 ¿Puedo usar LeadForge Community comercialmente?

**Sí.** La versión Community está bajo licencia **MIT**: uso libre, comercial y personal, sin restricciones.

---

## 🌍 ¿Funciona fuera de España?

**Sí, totalmente.** Cambia los parámetros:

```bash
.venv/bin/python -m src.prospeccion --query "dentist" --location "Lisbon, Portugal" --max-results 50
.venv/bin/python -m src.prospeccion --query "kine" --location "Lyon, France" --max-results 50
```

Para optimizar el comportamiento por país, edita `src/config.py`:

```python
LANGUAGE_CODE = "es"   # → "pt", "fr", "en", etc.
REGION_CODE = "ES"     # → "PT", "FR", "GB", etc.
```

El `normalize_phone()` de `dedupe.py` está optimizado para prefijos españoles (+34). Para otros países, edita esa función o desactiva la dedupe por teléfono.

---

## 🛠️ ¿Cómo lo extiendo para X nicho?

2 puntos típicos de customización:

1. **Umbrales de scoring**: edita `SCORE_ALTA_*` y `SCORE_MEDIA_*` en `src/config.py`. Los abogados / consultoría B2B necesitan umbrales más bajos que los restaurantes.
2. **Queries**: la guía [`CASOS_DE_USO.md`](CASOS_DE_USO.md) tiene 5 nichos completos para inspirarte.

---

## 📧 ¿Por qué los emails no aparecen en el CSV?

Google Places **no devuelve emails**. Solo teléfono, web y dirección.

Vías para enriquecer con email:

1. **Manual**: abre cada web del CSV y copia el email del footer / "Contacto". Es el más fiable.
2. **Scraper de emails sobre `websiteUri`**: añade un módulo `src/email_finder.py` que descargue la home + `/contacto` + `/aviso-legal` y extraiga emails con regex. Es un buen primer ejercicio para extender el pipeline.
3. **Servicios de terceros** (Hunter.io, Apollo): tienen APIs, pero son de pago y la cobertura para pymes locales españolas es regular.

---

## 🐛 Errores comunes

### `Falta la API key de Google Places`

No has rellenado `.env`. `cp .env.example .env` y pega tu key.

### `Error API (403)` en Places

Te falta habilitar la API en la consola, o la facturación. Ve a [CONFIGURACION_APIS.md](CONFIGURACION_APIS.md) §2-3.

### `Error API (400) ... API key not valid`

La key está mal copiada (espacio extra, salto de línea) o restringida a una API que no es Places New.

---

## ⏱️ ¿Cuánto tarda?

- **Fase 1 (prospección)**: ~10 segundos por búsqueda de 60 leads.
- **Fase 1.5 (dedupe)**: instantáneo.

---

## 💎 ¿Qué incluye la versión Pro?

La versión Pro (**29€** pago único) añade la **fase de auditoría automática**:

- **Screenshots desktop + móvil** de cada web con Playwright (Chromium headless).
- **Lighthouse** vía PageSpeed Insights (performance, accesibilidad, SEO, best-practices).
- **Análisis visual con Claude Sonnet 4.5**: detecta problemas reales (web no responsive, sin reservas online, sin WhatsApp visible, diseño desfasado…).
- **Pitch personalizado** por lead: 2-3 frases listas para meter en un email, mencionando 1-2 problemas concretos de SU web.
- **Plantillas de email de venta** adaptadas a los problemas detectados.
- **Documentación avanzada** (cómo cambiar de modelo de LLM, prompt caching, paralelización).
- **Soporte por email** durante 30 días.
- **Updates v1.x** mientras dure la versión.

Coste real del pipeline Pro: ~$2-3 USD por cada 100 leads auditados.

👉 **[Conseguir LeadForge Pro — 29€](https://bermejowebs.com)** *(precio early-bird limitado a las primeras 30 ventas)*.

---

## 🆘 ¿Y si me bloqueo?

- 🐛 **Bugs de la Community**: GitHub Issues.
- 💬 **Dudas comerciales, versión Pro**: [hola@bermejowebs.com](mailto:hola@bermejowebs.com).

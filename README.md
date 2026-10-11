# ADLE Tracker

Dashboard independiente de resultados documentados contra el crimen durante el periodo de gobierno configurado. Web estática adaptable a celular, sin dependencias de JavaScript ni claves API. Recolección RSS diaria mediante Python estándar y publicación en GitHub Pages.

## Estado de esta entrega

La primera consulta a los feeds de Fiscalía y Policía se ejecutó correctamente. No se han publicado eventos revisados ni cifras de ejemplo. La recolección descubre candidatos; la revisión de cantidades, fechas y duplicados es editorial. El repositorio público y GitHub Pages están activos. La primera ejecución de Actions terminó correctamente el 11 de octubre de 2026; la consulta diaria está programada para las 06:17 de Bogotá. Dashboard: https://isazaale.github.io/ADLE-tracker/. En la primera ejecución alojada la fuente de Fiscalía no respondió y se conservó el historial; la Policía respondió correctamente. El dashboard usa “sin datos”, no cero, mientras no existan eventos revisados. Esta versión no hace extracción semántica universal de artículos, ni ofrece un censo nacional exhaustivo. Los feeds solo cubren sus noticias recientes, no todo el periodo de gobierno.

## Publicación gratis

1. Crear el repositorio público `isazaale/ADLE-tracker` con rama `main`.
2. Subir el contenido de esta carpeta, incluyendo `.github/workflows/daily.yml`.
3. En Settings → Pages → Build and deployment, seleccionar **GitHub Actions**.
4. En Actions ejecutar **Recolectar y publicar** mediante Run workflow.
5. El workflow publica `docs/` y actualiza el JSON cada día a las 06:17 de Bogotá. GitHub puede retrasar ejecuciones y desactivar la programación después de 60 días sin actividad. Verificar periódicamente Actions y la última fecha exitosa visible.

No se requieren secretos para recolectar feeds públicos ni publicar con `GITHUB_TOKEN`. El repositorio público hace públicos el código y los datos incluidos. No almacenar información privada ni credenciales.

## Uso local

Requiere Python 3.12; no necesita instalar paquetes.

```bash
python scripts/collect.py
python -m unittest discover -s tests
python -m http.server 8000 --directory docs
```

Abrir `http://localhost:8000`. `ADLE-tracker-preview.html`, incluido en la entrega, es una instantánea autónoma que puede abrirse sin servidor; no se actualiza automáticamente.

## Revisión de eventos

Los candidatos se guardan en `docs/data/dashboard.json`. Verificar directamente el artículo original y confirmar fecha del hecho, cantidades, lugar y que no exista el operativo con otra fuente. Después:

```bash
python scripts/review.py ID_DE_NOTICIA --operation-id ID_UNICO --date YYYY-MM-DD --department Antioquia --location Medellin --reviewer editor --metric capturas=3
python scripts/collect.py --offline
```

Los argumentos del ejemplo describen el formato, no un operativo real. Para excluir una noticia: `python scripts/review.py ID_DE_NOTICIA --reject`.

Si varias noticias describen el mismo operativo, usar un único `operation_id` y añadir sus fuentes y `candidate_ids` al evento existente en `reviewed-events.json`. Si aparece una corrección, reemplazar el valor previo, no agregar otra copia. Los cambios quedan trazables en Git. La fecha de publicación no sustituye la fecha del hecho. Nunca sumar balances acumulados a eventos individuales.

Las capturas, bajas, extradiciones, rescatados y armas se almacenan como enteros no negativos en `metrics`. No se suman categorías: una persona capturada y extraditada puede aparecer en ambas. Los capturados se describen como presuntos implicados; “neutralizados” no es equivalente a muertos. Los datos reportados por las fuentes no implican una condena judicial ni una atribución causal del resultado al presidente.

## Estadísticas oficiales

`official_series` en `reviewed-events.json` admite filas con `metric` (homicidios, secuestros, extorsiones), `value`, `unit`, `scope` (Colombia), `period`, `cutoff` (YYYY-MM-DD) y `source_url` HTTPS. Importar exclusivamente cifras comparables de estadísticas oficiales, preservando el periodo, ámbito y unidad. El dashboard muestra el último corte nacional; los filtros de operativos no cambian el periodo de estas series. Esta primera versión no importa automáticamente PDFs oficiales ni calcula variaciones interanuales: las tarjetas permanecen pendientes hasta cargar una serie válida. No sumar noticias para inferir la tasa nacional.

## Fuentes y limitaciones

- Fiscalía: https://www.fiscalia.gov.co/colombia/feed/
- Policía: https://www.policia.gov.co/rss.xml
- Estadísticas: https://www.mindefensa.gov.co/defensa-y-seguridad/datos-y-cifras/informacion-estadistica

Los feeds fueron accesibles en la primera ejecución. Su disponibilidad puede cambiar. Los fallos quedan visibles y no borran eventos revisados. Para mayor cobertura se pueden agregar feeds oficiales en `sources.json`. RSS evita copiar artículos completos. El sistema conserva títulos, enlaces y metadatos. El frontend escapa texto, restringe enlaces HTTPS y protege CSV frente a fórmulas.

## Pruebas

Pruebas de separación de captura/extradición, rechazo de balances, no inferencia de fallecidos, restricciones de fuentes y fechas. Se comprobó sintaxis JavaScript y respuesta real de los dos feeds. Tras publicar se verificaron el dashboard, el filtro Hoy y la ventana de noticias pendientes en el navegador.

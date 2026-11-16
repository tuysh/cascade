# Registro de la revisión de Cascade

Registro vivo de la revisión a fondo del tema (diseño, bugs y núcleo) para que sea
digno de usarse a diario. Si una sesión se corta, **retomar desde "Siguiente paso"**.

- Rama de trabajo: `ccr-12ade6c3-2350h6` (separada de `main`).
- Firefox de referencia: **160.0** (BuildID 20261104181552). Trae el rediseño
  **Nova activado por defecto** (`browser.nova.enabled = true`); el CSS de Firefox
  lo separa con `@media -moz-pref("browser.nova.enabled")`. Cascade tiene que verse
  bien con Nova y sin Nova.

## Estado

| # | Fase | Estado |
|---|------|--------|
| 1 | Preparar entorno: Firefox 160 real + fuentes de su chrome + arnés de capturas | hecho |
| 2 | Capturas "antes" (37 escenarios) | hecho |
| 3 | Auditoría con agentes (9 áreas) + verificación adversarial de cada hallazgo | en curso |
| 4 | Implementar los hallazgos confirmados en commits pequeños | pendiente |
| 5 | Capturas "después" y comparación con "antes" | pendiente |
| 6 | Revisión independiente del diff final | pendiente |

## Siguiente paso

Esperar/recoger los resultados de la auditoría (fase 3) y apuntarlos abajo en
"Hallazgos verificados". Si los resultados se perdieron, relanzar la auditoría por
áreas (ver "Cómo se audita").

## Entorno para retomar

```sh
# 1. Firefox oficial (re-empaquetado por conda-forge) + fuentes de su chrome
tools/firefox-harness/setup.sh            # usa /tmp/cascade-harness por defecto

# 2. Capturas de todos los escenarios con una carpeta chrome/
python3 tools/firefox-harness/scenarios.py --chrome chrome --label after --jobs 4
#    -> /tmp/cascade-harness/shots/after/<escenario>.png
#    --only dark,light,urlbar-open   para un subconjunto
```

- Para tener una referencia "antes": `git worktree add /tmp/cascade-before <commit>` y
  pasar `--chrome /tmp/cascade-before/chrome --label before`.
- Variables: `CASCADE_HARNESS_DIR` (carpeta de trabajo), `FIREFOX_BIN` (binario).
- Dependencias: Xvfb, ImageMagick (`import`), xdotool, python3 + `zstandard`, unzip.
- El arnés usa Marionette en contexto chrome (`MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1`) y
  deja Firefox sin red (proxy a 127.0.0.1:9).
- Fuentes de Firefox extraídas en `$CASCADE_HARNESS_DIR/fxsrc/` (browser.xhtml,
  `skin/classic/browser/**`, `toolkit/skin/classic/global/**`, prefs por defecto).

## Cómo se audita

Áreas: pestañas, mapeo de colores + paneles, barra de URL, paletas + accesibilidad,
layout de una línea, página/ventana, configuración + arquitectura, diseño de
producto, integraciones con extensiones (Tab Center Reborn, Side View).

Cada área la revisa un agente contra las fuentes de Firefox 160 y las capturas; cada
hallazgo lo verifican dos agentes: uno intenta refutarlo y otro revisa que el
arreglo funcione (Nova sí/no, densidades, pestañas verticales, claro/oscuro).

Reglas de cascada importantes: `userChrome.css` es hoja de **usuario**; las hojas de
Firefox son de **autor**. Una declaración de usuario sin `!important` pierde frente a
cualquier declaración de autor de la misma propiedad, sin importar la especificidad.

## Observaciones propias (de las capturas "antes")

- El anillo de foco de teclado usa el azul de Firefox, no el color de acento
  (pestañas, botón de buscador en la barra de URL, buscador del panel lateral).
- El campo de la barra de búsqueda en página sale de color oliva.
- El borde del panel activo en vista dividida es azul de Firefox.
- En modo claro la página "flotante" casi no se distingue del marco.
- En vista dividida la primera pestaña queda muy recortada.
- `integrations/ayu/ayu.css`: el modo claro usa colores oscuros y en el oscuro
  `base == highlight` (no se ve la pestaña activa) y el texto es verde.
- Paleta clara por defecto: `--uc-muted-colour` (#191b1c) casi igual al texto.
- Las integraciones de color son copias completas de `cascade-colours.css`: cada
  cambio en el mapeo hay que copiarlo 8 veces.

## Hallazgos verificados

_(pendiente de la fase 3)_

## Cambios hechos

_(pendiente de la fase 4)_

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
| 3 | Auditoría con agentes (9 áreas) + verificación adversarial de cada hallazgo | hecho (146 hallazgos; 51 verificados por 2 agentes, el resto se verifica al implementar en Firefox real) |
| 4 | Implementar los hallazgos confirmados en commits pequeños | pendiente |
| 5 | Capturas "después" y comparación con "antes" | pendiente |
| 6 | Revisión independiente del diff final | pendiente |

## Siguiente paso

Implementar los bloques de "Plan de implementación" en orden, marcando cada uno
como hecho (con su commit) al terminarlo. El detalle completo de cada hallazgo
(problema, evidencia con archivo:línea de Firefox 160, arreglo propuesto y, si lo
hay, el veredicto de los verificadores y un `better_fix`) está en
`docs/audit/findings.json`, buscando por su id (p. ej. `tabs-01`).

Para cada bloque: leer los hallazgos del bloque en el JSON, aplicar el arreglo
(preferir `fixreview.better_fix` si existe), comprobar en Firefox real con el arnés
(escenarios afectados + `getComputedStyle`), commit pequeño, actualizar este archivo
y `git push`.

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

## Plan de implementación

Ids de `docs/audit/findings.json`. Los ids en el mismo bloque describen el mismo
problema visto desde áreas distintas. Orden = prioridad.

| Bloque | Qué | Ids | Estado |
|---|---|---|---|
| B1 | Separar paleta y mapeo de colores (integraciones = solo paleta, compatibles hacia atrás) | config-03, colours-18, urlbar-09, palettes-20 | hecho: mapeo en `cascade-colours-mapping.css`; 0 píxeles de diferencia, también con un userChrome.css viejo y con una integración vieja de copia completa |
| B2 | Privacidad: no ocultar los indicadores de cámara/micrófono/pantalla/ubicación | urlbar-01, config-01, product-10 | hecho: verificado en FF160 (icono de cámara visible al compartir) |
| B3 | Foco de teclado: anillos visibles y en color de acento (barra de URL, pestaña activa, botones), sin atenuar lo enfocado | urlbar-02, palettes-01, tabs-01, palettes-02, palettes-03, urlbar-06, product-05, palettes-04, colours-01, product-06 | hecho: verificado en FF160 (anillos en pestaña activa, pestaña con Ctrl+→, estrella; vista dividida y buscador lateral en acento) |
| B4 | Paletas: Ayu, por defecto (muted claro), Catppuccin, Rosé Pine, Nord, Gruvbox; highlight ≈ base | palettes-05..11, urlbar-07, colours-16, product-08 | hecho: 8 paletas renderizadas en FF160 en oscuro y claro (falta la barra de acento en el resultado seleccionado de palettes-11, va en B9) |
| B5 | Pestañas verticales: márgenes, anchos adaptativos, iconos centrados al plegar, hover ≠ activa | tabs-02, tabs-03, product-02, tabs-14, palettes-16, product-07 | hecho: verificado en FF160 (expandida, plegada, hover) |
| B6 | Layout de una línea: animación al redimensionar (@property), ventana nueva con URL enfocada, modo personalizar, código muerto, salto de 20px al crecer | oneline-01, oneline-03, oneline-04, config-09, oneline-06, oneline-08, product-01 | hecho: verificado en FF160 (redimensionar sin animación, menú » correcto, modo personalizar) |
| B7 | Quitar/neutralizar cascade-responsive-windows-fix.css (obsoleto en FF160) | oneline-02, oneline-05, config-14, extensions-02 | hecho: el archivo reenvía a cascade-responsive.css |
| B8 | Pestañas: grupos (selector roto), botones de cerrar, sonido en fijadas, línea de acento en fijadas, vista dividida, ancho adaptativo, botón nueva pestaña como opción, radios, arrastre, alturas por densidad | tabs-04..13, tabs-15..20, config-02, config-07, config-08, product-04, product-11, product-12, tabs-09 | hecho salvo tabs-15 (padding de fijadas en compacto), tabs-16 (inset de la línea de contenedor) y tabs-17 (va en B14); verificado en FF160 |
| B9 | Barra de URL: fila seleccionada visible, colores de selección de texto, #pageActionButton, contraste de URLs/enlaces, botón de menú de 1px, hover en cajas, radios | urlbar-03..05, urlbar-08, urlbar-10..16, colours-10, colours-15, palettes-13, product-03, palettes-11, config-11, config-12, palettes-19, product-09, product-17 | hecho salvo urlbar-13 (chip de extensión: se mantiene oculto, decisión previa del proyecto) y urlbar-15 |
| B10 | Colores: <select> de páginas ilegibles, fondo cuadrado de menús, degradado Nova, tinte violeta Nova, contenedores violet/gray, barras de notificación, panel de confianza, autocompletado, tooltips, privada, temas ligeros, botón primario contrast-color() | colours-02..09, colours-11..14, colours-17, palettes-12, product-18, product-19 | hecho salvo colours-11 (temas ligeros: hay que decidir si la paleta gana siempre o si se respeta el tema; pendiente de decisión del mantenedor) |
| B11 | Página/ventana: panel de estado espejo, hueco en vista dividida, diálogos modales, contorno de página en modo claro, controles de ventana como opción, barra de búsqueda, decoración de vista dividida | content-01..09, palettes-17, product-14, config-04, product-16 | hecho (el redondeo de la página encima de la barra de búsqueda de content-09 no se hizo); verificado en FF160 |
| B12 | Accesibilidad extra: opacidad inactiva vs contraste, forced-colors, reduced-motion | palettes-14, palettes-15, palettes-18, product-20 | pendiente |
| B13 | Menú (Alt), arrastre de ventana | oneline-07, product-13, oneline-09 | pendiente |
| B14 | Configuración: defaults :where para todas las opciones, restos obsoletos del config de ratón, nombres, comentarios, .editorconfig | config-05, config-06, config-10, config-13, config-16, config-17, config-21, tabs-17 | pendiente |
| B15 | Integraciones de extensiones (Tab Center Reborn, Side View) | extensions-01..13, config-15 | pendiente |
| B16 | Documentación: README, contributing, plantillas | config-18, config-19, config-20 | pendiente |

## Cambios hechos

- **B1** `refactor(colours)`: `cascade-colours.css` y las integraciones son solo
  paleta; el mapeo a las variables de Firefox está en
  `includes/cascade-colours-mapping.css` (importado en userChrome.css y, por
  compatibilidad, también al principio de cascade-layout.css). Añadidos los colores
  de contenedor `violet` y `gray` de FF160. Nota para usuarios: si editaron el
  mapeo dentro de su cascade-colours.css, deben mover esos cambios al final de
  userChrome.css.
- **B2** `fix(config)`: ya no se ocultan los indicadores rojos de cámara, micrófono,
  pantalla y ubicación en la barra de URL (solo el icono de "permisos concedidos" y
  los de permisos bloqueados, como antes).
- **B3** `fix(a11y)`: anillos de foco de teclado visibles en la barra de URL (antes
  `#urlbar *` los quitaba todos) y en la pestaña activa; lo enfocado ya no se atenúa;
  badges, progreso de descargas y botones con `[attention]` tampoco. El acento de
  Firefox (`--color-accent-primary`, enlaces, estrella, throbber, punto de atención,
  anillos de foco) sigue la paleta. Nuevo `--uc-accent-text-colour` (acento con la
  luminosidad ajustada en oklch para que se lea como texto en cualquier paleta) y
  texto de botones primarios con `contrast-color()`.
- **B4** `fix(colours)`: paletas corregidas con los valores oficiales y roles
  correctos. Ayu rehecha (Mirage/Light; antes el modo claro era oscuro y el oscuro no
  marcaba la pestaña activa). Catppuccin: highlight = surface0, muted = subtext0/1,
  rosa de Latte correcto. Rosé Pine: highlight = overlay, muted = subtle, contenedor
  azul y rosa correctos. Nord: muted distinguible, acento nord8/nord10. Gruvbox:
  highlight claro ya no es más claro que la base, hex corregidos. Por defecto:
  muted claro ya no es más oscuro que el texto, morado oscuro más legible, colores
  de contenedor claros con contraste ≥ 4.5:1.
- **B5** `fix(tabs)`: pestañas verticales separadas del borde, iconos centrados con la
  barra plegada, anchos adaptativos solo en horizontal (antes cortaban los títulos a
  200px en la barra lateral), línea de acento vertical junto a la pestaña activa, y
  hover a medio camino del highlight para no confundirse con la pestaña activa.
- **B6/B7** `fix(layout)`: se anima `--uc-urlbar-grow` (registrado con `@property`)
  en lugar del ancho, así redimensionar la ventana ya no deja botones dibujados
  encima de las pestañas ni atascados en el menú ». La barra crece solo con los
  resultados abiertos (una ventana nueva enfocaba la barra antes de llenar la
  barra de herramientas). Modo personalizar en una fila propia. Fuera el código
  muerto de anchos de #TabsToolbar y el «- 1px». Los muelles flexibles junto a la
  barra ya no le roban sitio (saltaba 20px al crecer).
  `cascade-responsive-windows-fix.css` ahora solo importa cascade-responsive.css
  (obsoleto desde FF133 y con bugs propios). Pendiente: actualizar la web de
  documentación externa, que aún dice que hay que cambiarlo en Windows.
- **B8** `fix(tabs)`: etiquetas de grupos (el selector ya no coincidía con FF160),
  botones de cerrar (»siempre« + »hover no« lo ocultaba al pasar el ratón; ahora con
  `@container style()`), indicador de sonido en fijadas visible en hover, línea de
  acento de pestaña fijada ≥ 16px (no parece el punto de atención), vista dividida
  con sitio para dos títulos, la pestaña activa se queda con más espacio cuando la
  barra está llena, sombra de arrastre de varias pestañas, radio de pestañas
  aplicado a todo lo de Firefox, vista previa al pasar el ratón con el radio del
  tema, atenuar solo título e icono (no los indicadores) y nada si se pide más
  contraste, pestañas tan altas como la barra de URL en todas las densidades con
  Nova y sin Nova (medido: 6/6 combinaciones). Botones de nueva pestaña: la regla
  pasa a los configs (el de ratón ya no los oculta).
- **B9** `fix(nav-bar)`: el resultado seleccionado lleva una línea de acento (se
  veía igual que el hover y casi invisible en paletas con highlight ≈ base); fuera
  la regla que pintaba esquinas cuadradas; selección de texto de la barra de URL y
  de búsqueda con los colores del tema (antes azul del sistema); `#pageActionButton`
  ya no se oculta (en ventanas ≤ 680px desaparecían la estrella y las acciones de
  extensiones); el botón de menú de 1px reaparece con foco o con algo que avisar
  (actualización, extensión, sesión de sync); hover/pulsado visibles en las cajas
  de la barra; botones con el radio del tema en vez de píldoras de Nova; comentarios
  de los configs actualizados al panel de confianza de FF160.
- **B10** `fix(colours)`: fuera el degradado violeta→naranja de Nova, texto e
  iconos sin el tinte violeta de Nova, menús `<select>` de páginas con estilo
  propio legibles (antes texto del tema sobre el fondo de la página), menús sin la
  caja cuadrada opaca encima de la redondeada, panel de información del sitio y
  promo de sync con la paleta, barras de notificación con la paleta, contenedores
  con nombre legible (color mezclado con el texto), autocompletado de logins con
  la paleta, tooltips con la paleta, borde lateral morado de ventanas privadas
  fuera, y **nueva opción** `--uc-private-urlbar-colour`: la barra de URL de las
  ventanas privadas se tiñe para distinguirlas.
- **B11** `fix(layout)`: panel de estado con margen simétrico (pegado al borde al
  pasar a la derecha) y con la paleta + borde; la vista dividida ya no reduce el
  hueco de la página en pestañas normales; fondo de diálogos modales redondeado;
  barras de desplazamiento de macOS fuera de las esquinas; **nueva opción**
  `--uc-content-outline-colour`: contorno fino alrededor de la página (en modo
  claro no se distinguía); paneles de vista dividida con el radio del tema; destello
  y »no encontrado« de la barra de búsqueda con la paleta; controles de ventana: en
  macOS ya no se ocultan (solapaban), y el config de ratón ya no los oculta.

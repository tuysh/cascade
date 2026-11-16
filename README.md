<div align="center">

# Cascade

**A minimalistic and keyboard centered userChrome**

![Cascade Preview](assets/preview.webp)

Cascade aims to remove a lot of the subjective clutter default Firefox comes with. The theme is also highly inspired by the stylistic choices of [SimpleFox](https://github.com/migueravila/SimpleFox) 🦊 by [Miguel Ávila](https://github.com/migueravila).

<br>

<div style="display: flex; justify-content: center; gap: 1rem;">
  <a href="https://cascadefox.github.io/installation.html">
    <img
      alt="Install"
      src="https://img.shields.io/badge/firefox-install-c6a0f6?style=for-the-badge&logo=firefox&logoColor=white&labelColor=363a4f"
  /></a>
  <a href="https://github.com/cascadefox/cascade/stargazers">
    <img
      alt="Stargazers"
      src="https://img.shields.io/github/stars/cascadefox/cascade?style=for-the-badge&logo=starship&color=7dc4e4&logoColor=white&labelColor=363a4f"
  /></a>
  <a href="https://github.com/cascadefox/cascade">
    <img
      alt="FFCSS Discord"
      src="https://img.shields.io/discord/837559961194070026?label=FFCSS+Discord&style=for-the-badge&logo=discord&color=a6da95&logoColor=white&labelColor=363a4f"
  /></a>
  <a href="https://github.com/cascadefox/cascade/issues">
    <img
      alt="Issues"
      src="https://img.shields.io/github/issues/cascadefox/cascade?style=for-the-badge&logo=gitbook&color=f5a97f&logoColor=white&labelColor=363a4f"
  /></a>
</div>

</div>

---

### Documentation

**[Installation](https://cascadefox.github.io/installation.html) • [Customisation](https://cascadefox.github.io/customisation.html) • [Integrations](https://cascadefox.github.io/integrations.html) • [Keyboard Shortcuts](https://cascadefox.github.io/shortcuts.html)**

<br>

---

### Status

Works with **Firefox 160**, with the Nova design on (the default) and off,
horizontal and vertical tabs, normal / compact / touch density, light and dark.

### Quick start

1. Open `about:config` and set `toolkit.legacyUserProfileCustomizations.stylesheets` to `true`.
2. Copy the `chrome` folder into your profile folder (`about:support` → Profile Folder).
3. Restart Firefox.

Everything you can tweak lives in `chrome/includes/cascade-config.css`, with a
comment above every option. Prefer the mouse? Import
`includes/cascade-config-mouse.css` instead (back/forward, close buttons on hover,
window controls, the new tab button); `userChrome.css` shows how.

### Colour schemes

Copy one of the files in `integrations/` (Catppuccin, Rosé Pine, Nord, Gruvbox,
ayu) over `chrome/includes/cascade-colours.css`. A colour file only holds the
palette (base, highlight, text, muted, accent and the container colours); how
those colours reach Firefox is in `cascade-colours-mapping.css`, which works with
every palette.

### Updating from an older version

Replace the whole `chrome` folder, then copy your own settings into the new
`cascade-config.css` (or `cascade-config-mouse.css`). If you would rather keep
your old config file, check these lines in it:

- `--uc-tab-margin: var(--tab-margin-block);` makes tabs taller than the URL
  Bar; use `calc((var(--tabstrip-min-height) - var(--urlbar-height)) / 2)`.
- On macOS, remove `.titlebar-buttonbox-container { display: none }`: the
  window buttons stay anyway, and the toolbar slides under them.
- The New Tab button next to the tabs is now hidden from the config file;
  copy the »Hides the New Tab button« block if you want it gone.
- Remove `#pageActionButton { display: none }`, the
  `.urlbar-page-action > image` margin and `#alltabs-button { margin-top: 5px }`
  if you have them; they no longer line up in Firefox 160.
- `#identity-permission-box { display: none }` no longer hides the camera,
  microphone, screen and location indicators while a site uses them.

If you changed the colour mapping inside your `cascade-colours.css`, move those
lines to the end of `userChrome.css`: the mapping now lives in
`cascade-colours-mapping.css`. `cascade-responsive-windows-fix.css` is no longer
needed on Windows.

### Credits

Cascade was created by [Andreas Grafen](https://andreas.grafen.info) and is
inspired by [SimpleFox](https://github.com/migueravila/SimpleFox) by Miguel Ávila.

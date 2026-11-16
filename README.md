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

### Credits

Cascade was created by [Andreas Grafen](https://andreas.grafen.info) and is
inspired by [SimpleFox](https://github.com/migueravila/SimpleFox) by Miguel Ávila.

# meshcentral_omarchy_theme

Omarchy themes for MeshCentral.

All 23 [Omarchy](https://github.com/omacom/omarchy) color themes for MeshCentral's **modern UI**
(`siteStyle: 3`). Every palette is generated from Omarchy's own `colors.toml`, so the colors match Omarchy exactly.

The themes show up in MeshCentral's own theme picker, **My Account → Switch theme**, in an "Omarchy" group
next to the built-in Bootswatch themes. The login page follows the theme each browser last picked.

**The look:** flat square panels, JetBrains Mono everywhere (bundled), and Waybar-style bars for the masthead,
left bar and tabs. Dialogs and menus get a 2px accent border like Hyprland's active window, including the gradient
borders of Hackerman, Last Horizon and Solitude. There are no gradients or glows, and the active tab or nav item is marked by an
accent underline or edge.

Themes: Catppuccin, Catppuccin Latte*, Ethereal, Everforest, Flexoki Light*, Gruvbox, Hackerman, Jade Horse,
Kanagawa, Last Horizon, Lumon, Lupine*, Matte Black, Miasma, Nord, Retro 82, Ristretto, Rose Pine*, Solitude,
Starship, Tokyo Night, Vantablack, White* (*light themes)

## Preview before installing

```bash
python -m http.server 8765
```

Then open <http://localhost:8765/preview/> and switch themes from the box in the bottom-right corner. The page is a mock of
the modern UI built on MeshCentral's real `style-bootstrap.css`, and `login.html` previews the login page.

## Install

MeshCentral serves files from `meshcentral-web/public/` ahead of its own, so these themes never touch
`node_modules/meshcentral`, and MeshCentral updates leave them in place. The folder sits next to `meshcentral-data/`.

```bash
cd /tmp && git clone https://github.com/<your-account>/meshcentral_omarchy_theme && cd meshcentral_omarchy_theme
sudo ./install.sh /opt/meshcentral                        # install / update
sudo ./install.sh /opt/meshcentral --default tokyo-night  # also set a default theme
sudo ./install.sh /opt/meshcentral --uninstall            # remove
```

Then:

1. If `meshcentral-web/` did not exist before, **restart MeshCentral once**. It only looks for the folder at startup.
2. Make sure the modern UI is on. In `meshcentral-data/config.json`, under your domain (`"domains": { "": { ... } }`), set `"siteStyle": 3`.
3. In MeshCentral, go to **My Account → Switch theme** and pick a theme under **Omarchy**.
4. If the old look is cached, hard-refresh with Ctrl+Shift+R.

To update later: `git pull` in the clone, then run `install.sh` again. Re-running the installer updates it in place. If you already have a `scripts/custom.js`, your code is kept: the
installer only adds or replaces its own block between `/* OMARCHY-THEMES-BEGIN */` and `/* OMARCHY-THEMES-END */`.
`styles/custom.css` is never touched.

### Manual / Docker install

Copy these from this repo's `meshcentral-web/public/` into the container's `meshcentral-web/public/`
(usually the volume mounted at `/opt/meshcentral/meshcentral-web`):

```
styles/omarchy/                 shared CSS, palettes, bundled font
styles/themes/omarchy-*/        one folder per theme (what the theme picker loads)
scripts/custom.js               registers the themes (append it if you already have one)
```

To set a default theme, edit `var DEFAULT_THEME = "";` in `custom.js`.

## How it works

MeshCentral's theme picker loads `styles/themes/<name>/bootstrap-min.css` in place of Bootstrap. Each
`omarchy-<name>/bootstrap-min.css` here is three imports:

1. MeshCentral's stock `styles/bootstrap-min.css`
2. `styles/omarchy/palettes/<name>.css`, which holds that theme's colors as `--om-*` variables
3. `styles/omarchy/omarchy.css`, which maps Bootstrap's variables to those colors and restyles MeshCentral's own elements (masthead, left bar, tabs, device list, dialogs, menus, forms, footer)

`scripts/custom.js` does the rest:

- It adds the Omarchy group to the **Switch theme** dialog.
- It tells MeshCentral which palettes are dark, so dark themes switch on Bootstrap dark mode, the same way MeshCentral handles Darkly.
- It keeps light palettes light even when night mode is on.
- It applies the saved theme before the page paints.
- On the login page, which has no Bootstrap, it loads the palette and `styles/omarchy/login.css`.

The choice is stored per browser under MeshCentral's own `theme` setting, the same as the built-in themes.

## Customizing

Override these in `styles/custom.css`. MeshCentral loads that file after the theme.

```css
:root {
  --om-font: "Segoe UI", system-ui, sans-serif;  /* if mono feels too dense */
  --om-radius: 4px;                               /* 0 is pure Omarchy */
  --om-window-width: 1px;                         /* dialog/menu border */
}
```

The stock MeshCentral logo banner is hidden in the masthead. To bring back a logo of your own:
`#masthead { background-image: url(../logo.png) !important; }`.

## Building / adding themes

```bash
python build/build.py
```

The build reads `palettes/*.toml`, which are Omarchy `colors.toml` files, and regenerates the palettes, the theme
folders, `scripts/custom.js` and `preview/palettes.js`. To add a new Omarchy theme, drop its `colors.toml` in
`palettes/` as `<id>.toml` and rebuild. Only edit `src/custom.js`, never the generated
`meshcentral-web/public/scripts/custom.js`.

## Compatibility notes

- Built against MeshCentral's current `default3.handlebars` and `style-bootstrap.css`, which has the theme switcher and `scripts/themes/theme-switcher.js`. Older MeshCentral versions without the Switch theme dialog won't list the themes.
- Don't run this together with MeshCentral-Stylish-UI's `custom.css`. Its hard-coded colors fight these palettes. Pick one.
- The terminal and remote desktop canvases keep MeshCentral's own colors. Only the chrome around them is themed.

## Credits

Color palettes: [Omarchy](https://github.com/omacom/omarchy) (MIT). The install approach was informed by
[MeshCentral-Stylish-UI](https://github.com/Melo-Professional/MeshCentral-Stylish-UI). The font is
[JetBrains Mono](https://www.jetbrains.com/lp/mono/) (SIL OFL 1.1, `styles/omarchy/fonts/OFL.txt`).
`preview/vendor/style-bootstrap.css` is from [MeshCentral](https://github.com/Ylianst/MeshCentral) (Apache-2.0),
used by the preview page only.

#!/usr/bin/env python3
"""
Build the Omarchy themes for MeshCentral's modern UI.

Reads every Omarchy colors.toml in ../palettes and writes:

  meshcentral-web/public/styles/omarchy/palettes/<id>.css      CSS variables for one theme
  meshcentral-web/public/styles/themes/omarchy-<id>/bootstrap-min.css
                                                              the file MeshCentral's theme
                                                              switcher loads for that theme
  meshcentral-web/public/scripts/custom.js                    theme registration (from src/custom.js)
  preview/palettes.js                                         palette data for the preview page

Usage:  python build/build.py
To add a theme: drop an Omarchy colors.toml into palettes/ (named <id>.toml) and rebuild.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALETTES = os.path.join(ROOT, "palettes")
PUBLIC = os.path.join(ROOT, "meshcentral-web", "public")
STYLES = os.path.join(PUBLIC, "styles")

# Nicer labels where simple title-casing is wrong.
LABELS = {"retro-82": "Retro 82", "rose-pine": "Rose Pine"}


# ---------------------------------------------------------------- colour maths
def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb)


def mix(a, b, t):
    """Mix colour a toward b by t (0 = a, 1 = b)."""
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def luminance(h):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = hex_to_rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def readable_on(color, prefer):
    """Pick text colour for a filled background: prefer the theme's own colours."""
    for c in prefer:
        if contrast(color, c) >= 4.5:
            return c
    return max(prefer + ["#000000", "#ffffff"], key=lambda c: contrast(color, c))


def rgb_triplet(h):
    return ", ".join(str(c) for c in hex_to_rgb(h))


# ---------------------------------------------------------------- palette parsing
def parse_toml(path):
    """Omarchy colors.toml is flat `key = "value"`; Python 3.10 has no tomllib."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r'\s*([A-Za-z0-9_]+)\s*=\s*"([^"]*)"', line)
            if m:
                key, val = m.group(1), m.group(2).strip()
                if re.fullmatch(r"#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?", val):
                    val = val.lower()[:7]
                out[key] = val
    return out


def is_hex(s):
    return isinstance(s, str) and re.fullmatch(r"#[0-9a-f]{6}", s) is not None


def hypr_gradient(spec):
    """Hyprland border spec, e.g. 'rgba(26a269ee) rgba(2ec27eee) 45deg' -> CSS gradient (or None)."""
    if not spec:
        return None
    cols = ["#" + m[:6] for m in re.findall(r"rgba?\(([0-9a-fA-F]{6,8})\)", spec)]
    if len(cols) < 2:
        return None
    m = re.search(r"(-?\d+)deg", spec)
    # Hyprland measures the angle like CSS but from the other axis.
    angle = (90 + int(m.group(1))) % 360 if m else 90
    return "linear-gradient(%ddeg, %s)" % (angle, ", ".join(cols))


def derive(theme_id, p):
    bg, fg, accent = p["background"], p["foreground"], p["accent"]
    mode = p.get("mode")
    dark = (mode == "dark") if mode in ("dark", "light") else luminance(bg) < 0.4
    get = lambda k, fb: p[k] if is_hex(p.get(k)) else fb

    lighter = get("lighter_background", mix(bg, fg, 0.10))
    v = {"bg": bg, "fg": fg, "accent": accent}
    # Omarchy's own background tiers: dark_background (bars) / darker_background (deepest)
    v["mantle"] = get("dark_background", mix(bg, "#000000" if dark else fg, 0.28 if dark else 0.045))
    v["crust"] = get("darker_background", mix(bg, "#000000" if dark else fg, 0.45 if dark else 0.085))
    v["surface0"] = mix(bg, lighter, 0.5)
    v["surface1"] = lighter
    v["surface2"] = mix(lighter, fg, 0.08)
    dim = get("muted", mix(bg, fg, 0.28))           # Omarchy "muted" = dim UI chrome colour
    v["border"] = mix(lighter, dim, 0.5)
    v["border-strong"] = dim
    # dark_foreground is Omarchy's comment/secondary text; keep it legible on bg.
    dfg = get("dark_foreground", mix(fg, bg, 0.4))
    v["muted"] = dfg if contrast(dfg, bg) >= 4 else mix(dfg, fg, 0.45)
    v["subtle"] = dfg if contrast(dfg, bg) >= 2.2 else mix(dfg, fg, 0.3)
    v["sel-bg"] = get("selection", mix(bg, accent, 0.3))
    v["sel-fg"] = get("bright_foreground", fg)
    v["cursor"] = get("bright_foreground", fg)

    v["red"], v["green"], v["yellow"] = get("red", "#e06c75"), get("green", "#98c379"), get("yellow", "#e5c07b")
    v["blue"], v["magenta"], v["cyan"] = get("blue", accent), get("magenta", "#c678dd"), get("cyan", "#56b6c2")
    v["orange"] = get("orange", v["yellow"])
    v["window"] = get("active_border_color", accent)  # Hyprland active window border
    v["window-image"] = hypr_gradient(p.get("hyprland_active_border")) or "none"
    v["tab-active"] = get("active_tab_background", accent)

    v["accent-hover"] = mix(accent, fg if dark else "#000000", 0.18 if dark else 0.12)
    v["accent-soft"] = mix(bg, accent, 0.16)
    v["accent-line"] = mix(bg, accent, 0.45)
    v["accent-text"] = accent if contrast(accent, bg) >= 3 else mix(accent, fg, 0.45)

    prefer = [bg, v["crust"], fg]
    v["on-accent"] = readable_on(accent, prefer)
    for name in ("red", "green", "yellow", "blue", "magenta", "cyan"):
        v["on-" + name] = readable_on(v[name], prefer)
        v[name + "-soft"] = mix(bg, v[name], 0.16)
        v[name + "-line"] = mix(bg, v[name], 0.45)
        v[name + "-text"] = v[name] if contrast(v[name], bg) >= 3 else mix(v[name], fg, 0.45)

    label = LABELS.get(theme_id) or " ".join(w.capitalize() for w in theme_id.split("-"))
    return {"id": theme_id, "label": label, "dark": dark, "vars": v}


# ---------------------------------------------------------------- writers
RGB_KEYS = ("bg", "fg", "accent", "mantle", "surface1", "muted", "border",
            "red", "green", "yellow", "blue", "magenta", "cyan")


def palette_css(t):
    v = t["vars"]
    lines = [
        "/* Omarchy · %s — generated by build/build.py from palettes/%s.toml. Do not edit. */"
        % (t["label"], t["id"]),
        ":root {",
        "  --om-theme: \"%s\";" % t["id"],
        "  --om-scheme: %s;" % ("dark" if t["dark"] else "light"),
        "  color-scheme: %s;" % ("dark" if t["dark"] else "light"),
    ]
    for k, val in v.items():
        lines.append("  --om-%s: %s;" % (k, val))
    for k in RGB_KEYS:
        lines.append("  --om-%s-rgb: %s;" % (k, rgb_triplet(v[k])))
    lines.append("}")
    return "\n".join(lines) + "\n"


def theme_entry_css(t):
    return (
        "/* Omarchy · %s for MeshCentral (modern UI). Generated by build/build.py. */\n"
        "/* MeshCentral's theme switcher loads this file in place of Bootstrap. */\n"
        "@import url(\"../../bootstrap-min.css\");\n"
        "@import url(\"../../omarchy/palettes/%s.css\");\n"
        "@import url(\"../../omarchy/omarchy.css\");\n" % (t["label"], t["id"])
    )


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    themes = []
    for name in sorted(os.listdir(PALETTES)):
        if name.endswith(".toml"):
            tid = name[:-5]
            p = parse_toml(os.path.join(PALETTES, name))
            missing = [k for k in ("background", "foreground", "accent") if k not in p]
            if missing:
                print("skip %s: missing %s" % (name, ", ".join(missing)), file=sys.stderr)
                continue
            themes.append(derive(tid, p))

    for t in themes:
        write(os.path.join(STYLES, "omarchy", "palettes", t["id"] + ".css"), palette_css(t))
        write(os.path.join(STYLES, "themes", "omarchy-" + t["id"], "bootstrap-min.css"), theme_entry_css(t))

    registry = [{"id": t["id"], "label": t["label"], "dark": t["dark"]} for t in themes]
    with open(os.path.join(ROOT, "src", "custom.js"), encoding="utf-8") as f:
        js = f.read()
    js = js.replace("/*@THEMES@*/[]", json.dumps(registry, separators=(",", ":")))
    write(os.path.join(PUBLIC, "scripts", "custom.js"), js)

    preview = {t["id"]: {"label": t["label"], "dark": t["dark"], "vars": t["vars"]} for t in themes}
    write(os.path.join(ROOT, "preview", "palettes.js"),
          "window.OMARCHY_PALETTES = " + json.dumps(preview, indent=1) + ";\n")

    print("built %d themes: %s" % (len(themes), ", ".join(t["id"] for t in themes)))


if __name__ == "__main__":
    main()

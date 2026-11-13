#!/usr/bin/env bash
# Omarchy themes for MeshCentral (modern UI) — installer.
#
#   ./install.sh /opt/meshcentral                     install / update
#   ./install.sh /opt/meshcentral --default tokyo-night   also make it the default for new browsers
#   ./install.sh /opt/meshcentral --uninstall          remove everything this installed
#
# The path is the MeshCentral root: the folder that holds meshcentral-data/.
# Files go to <root>/meshcentral-web/public/, MeshCentral's override folder. Nothing in
# node_modules/meshcentral is touched, so MeshCentral updates do not undo the install.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/meshcentral-web/public"

usage() { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

ROOT="" DEFAULT="" UNINSTALL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --default) DEFAULT="${2:-}"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) usage 0 ;;
    -*) echo "Unknown option: $1" >&2; usage 1 ;;
    *) ROOT="$1"; shift ;;
  esac
done
[ -n "$ROOT" ] || usage 1
[ -d "$ROOT/meshcentral-data" ] || { echo "No meshcentral-data/ in $ROOT — pass the MeshCentral root folder." >&2; exit 1; }

PUB="$ROOT/meshcentral-web/public"
JS="$PUB/scripts/custom.js"
FRESH_OVERRIDE=0
[ -d "$ROOT/meshcentral-web" ] || FRESH_OVERRIDE=1

strip_block() {  # remove our managed block from custom.js, keep everything else
  [ -f "$JS" ] || return 0
  sed '/\/\* OMARCHY-THEMES-BEGIN \*\//,/\/\* OMARCHY-THEMES-END \*\//d' "$JS" |
    awk '{ l[NR] = $0 } END { n = NR; while (n > 0 && l[n] ~ /^[[:space:]]*$/) n--; for (i = 1; i <= n; i++) print l[i] }' > "$JS.tmp"
  cat "$JS.tmp" > "$JS" && rm -f "$JS.tmp"   # cat keeps the file's owner and mode
}

if [ "$UNINSTALL" = 1 ]; then
  rm -rf "$PUB/styles/omarchy" "$PUB"/styles/themes/omarchy-*
  strip_block
  if [ -f "$JS" ] && ! grep -q '[^[:space:]]' "$JS"; then rm -f "$JS"; fi
  echo "Omarchy themes removed. Browsers that had one selected fall back to the default theme."
  exit 0
fi

if [ -n "$DEFAULT" ] && [ ! -f "$SRC/styles/omarchy/palettes/$DEFAULT.css" ]; then
  echo "Unknown theme '$DEFAULT'. Available:" >&2
  ls "$SRC/styles/omarchy/palettes" | sed 's/\.css$//; s/^/  /' >&2
  exit 1
fi

mkdir -p "$PUB/styles/themes" "$PUB/scripts"
rm -rf "$PUB/styles/omarchy" "$PUB"/styles/themes/omarchy-*
cp -R "$SRC/styles/omarchy" "$PUB/styles/omarchy"
cp -R "$SRC"/styles/themes/omarchy-* "$PUB/styles/themes/"

# custom.js: replace our block, keep any code of your own
strip_block
BLOCK="$(cat "$SRC/scripts/custom.js")"
if [ -n "$DEFAULT" ]; then BLOCK="${BLOCK/var DEFAULT_THEME = \"\";/var DEFAULT_THEME = \"$DEFAULT\";}"; fi
if [ -s "$JS" ]; then printf '\n%s\n' "$BLOCK" >> "$JS"; else printf '%s\n' "$BLOCK" > "$JS"; fi

# match ownership of meshcentral-data so a non-root MeshCentral can read the files
if [ "$(id -u)" = 0 ]; then
  OWNER="$(stat -c '%u:%g' "$ROOT/meshcentral-data" 2>/dev/null || true)"
  [ -n "$OWNER" ] && chown -R "$OWNER" "$ROOT/meshcentral-web" || true
fi

COUNT=$(ls -d "$PUB"/styles/themes/omarchy-* | wc -l | tr -d ' ')
echo "Installed $COUNT Omarchy themes into $PUB"
[ -n "$DEFAULT" ] && echo "Default for browsers with no saved theme: $DEFAULT"
echo
echo "Next:"
if [ "$FRESH_OVERRIDE" = 1 ]; then
  echo "  * meshcentral-web/ is new, so restart MeshCentral once so it picks up the override folder."
fi
echo "  * Make sure the modern UI is on: \"siteStyle\": 3 in the domain section of meshcentral-data/config.json"
echo "  * In MeshCentral: My Account -> Switch theme -> pick one from the Omarchy group."
echo "  * Hard refresh (Ctrl+Shift+R) if the old look is cached."

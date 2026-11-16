#!/bin/bash
# Downloads the official Firefox build repackaged by conda-forge (reachable from
# sandboxes that block mozilla.org), unpacks it, and extracts Firefox's own chrome
# CSS / markup (omni.ja) so the theme can be checked against the real sources.
#
#   CASCADE_HARNESS_DIR  where everything goes (default /tmp/cascade-harness)
#   FIREFOX_VERSION      conda-forge firefox version (default: newest)
#
# Needs: curl, python3 (+ pip install zstandard), unzip, Xvfb, ImageMagick (import), xdotool.
set -euo pipefail
D=${CASCADE_HARNESS_DIR:-/tmp/cascade-harness}
mkdir -p "$D" && cd "$D"
python3 -c "import zstandard" 2>/dev/null || pip install -q zstandard
if [ ! -f repodata.json ]; then
  curl -sS -o repodata.json https://conda.anaconda.org/conda-forge/linux-64/current_repodata.json
fi
FN=$(python3 - "${FIREFOX_VERSION:-}" <<'PY'
import json, sys
want = sys.argv[1]
d = json.load(open("repodata.json"))
c = [(fn, p) for k in ("packages", "packages.conda") for fn, p in d.get(k, {}).items() if p["name"] == "firefox"]
if want:
    c = [x for x in c if x[1]["version"] == want]
c.sort(key=lambda x: [int(n) if n.isdigit() else n for n in x[1]["version"].split(".")])
print(c[-1][0])
PY
)
echo "firefox package: $FN"
[ -f "$FN" ] || curl -sS -o "$FN" "https://conda.anaconda.org/conda-forge/linux-64/$FN"
rm -rf pkg && mkdir pkg && cd pkg
python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('.')" "../$FN"
python3 - <<'PY'
import glob, tarfile, zstandard
f = glob.glob("pkg-*.tar.zst")[0]
with open(f, "rb") as fh, zstandard.ZstdDecompressor().stream_reader(fh) as r:
    tarfile.open(fileobj=r, mode="r|").extractall("root", filter="data")
PY
cd "$D"
rm -rf firefox && mv pkg/root firefox && rm -rf pkg
FFD="$D/firefox/bin/FirefoxApp"
grep -E '^(Version|BuildID)=' "$FFD/application.ini"
# Firefox chrome sources (omni.ja uses a non standard zip layout; unzip copes with it)
rm -rf fxsrc && mkdir -p fxsrc/browser fxsrc/toolkit
(cd fxsrc/browser && unzip -qo "$FFD/browser/omni.ja" '*.css' '*.xhtml' '*.mjs' '*.js' '*.ftl' 2>/dev/null || true)
(cd fxsrc/toolkit && unzip -qo "$FFD/omni.ja" '*.css' '*.xhtml' '*.mjs' '*.js' 2>/dev/null || true)
echo "firefox: $FFD/firefox"
echo "sources: $D/fxsrc"

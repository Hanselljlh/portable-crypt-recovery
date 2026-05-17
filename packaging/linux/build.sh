#!/usr/bin/env bash
# Build script for PCR Linux portable release
# Run from repo root:  bash packaging/linux/build.sh
# Or with version:     bash packaging/linux/build.sh 0.1.0
#
# Output: dist/PCR-linux-portable/   (ready-to-tar portable folder)
#         dist/PCR-linux-portable-<version>.tar.gz

set -euo pipefail

VERSION="${1:-0.1.1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$REPO_ROOT/dist"
BUILD_DIR="$DIST_DIR/PCR"
PORT_DIR="$DIST_DIR/PCR-linux-portable"
TARBALL="$DIST_DIR/PCR-linux-portable-$VERSION.tar.gz"
SPEC_FILE="$SCRIPT_DIR/pyinstaller-one-folder.spec"

echo "=== PCR Linux build v$VERSION ==="
echo "Repo root : $REPO_ROOT"
echo "Output    : $PORT_DIR"

# ------------------------------------------------------------------
# 1. Verify python3 + pyinstaller
# ------------------------------------------------------------------
python3 --version >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

python3 -m PyInstaller --version >/dev/null 2>&1 || {
    echo "Installing PyInstaller..."
    python3 -m pip install pyinstaller
}

# ------------------------------------------------------------------
# 2. Install the package
# ------------------------------------------------------------------
echo ""
echo "Installing package..."
python3 -m pip install -e "$REPO_ROOT" --quiet

# ------------------------------------------------------------------
# 3. Run PyInstaller
# ------------------------------------------------------------------
echo ""
echo "Running PyInstaller..."
pushd "$REPO_ROOT" >/dev/null
python3 -m PyInstaller "$SPEC_FILE" \
    --distpath "$DIST_DIR" \
    --workpath "$DIST_DIR/build-work" \
    --noconfirm
popd >/dev/null

# ------------------------------------------------------------------
# 4. Assemble portable folder layout
# ------------------------------------------------------------------
echo ""
echo "Assembling portable layout..."

rm -rf "$PORT_DIR"
mkdir -p "$PORT_DIR"

# Copy PyInstaller output (binary + _internal/) into portable root
cp -r "$BUILD_DIR"/. "$PORT_DIR/"

# Create portable folder structure
for folder in app tools/hashcat workspaces/default config logs docs; do
    mkdir -p "$PORT_DIR/$folder"
done

# Copy docs
if [ -d "$REPO_ROOT/docs" ]; then
    cp -r "$REPO_ROOT/docs"/. "$PORT_DIR/docs/"
fi

# Copy hashcat placeholder
PLACEHOLDER="$REPO_ROOT/packaging/portable-template/PCR/tools/hashcat/README-place-hashcat-here.txt"
if [ -f "$PLACEHOLDER" ]; then
    cp "$PLACEHOLDER" "$PORT_DIR/tools/hashcat/"
fi

# Write README
cat >"$PORT_DIR/README.txt" <<EOF
Portable Crypt Recovery (PCR) v$VERSION
=======================================

QUICK START
-----------
1. Place hashcat (and its _internal/ or shared libs) into:
       tools/hashcat/hashcat

2. Run PCR from the portable folder:
       ./PCR

3. On first run, go to Settings -> Workspace to open or create
   your workspace folder (default workspace is pre-created in
   workspaces/default/).

4. Go to Settings -> Hashcat Setup and verify Hashcat.

FOLDER LAYOUT
-------------
  PCR                     - Application binary
  _internal/              - Runtime libraries (do not delete)
  workspaces/default/     - Default recovery workspace
  tools/hashcat/          - Place hashcat binary here
  config/                 - App configuration
  logs/                   - Application logs
  docs/                   - User guide

SUPPORT
-------
https://github.com/Hanselljlh/portable-crypt-recovery
EOF

chmod +x "$PORT_DIR/PCR" 2>/dev/null || true

echo "Portable folder assembled at: $PORT_DIR"

# ------------------------------------------------------------------
# 5. Create tarball
# ------------------------------------------------------------------
echo ""
echo "Creating tarball..."
rm -f "$TARBALL"
tar -czf "$TARBALL" -C "$PORT_DIR" .
SIZE_MB=$(du -sh "$TARBALL" | cut -f1)
echo "Archive: $TARBALL ($SIZE_MB)"

echo ""
echo "=== Build complete ==="
echo "Portable folder : $PORT_DIR"
echo "Tarball         : $TARBALL"

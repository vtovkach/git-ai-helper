#!/usr/bin/env bash
# Build/rebuild "gita" with PyInstaller (onedir), assemble a final ./gita folder,
# then package it into ./gita_install/ along with ./install.sh and ./uninstall.sh (from ./bash/).

set -euo pipefail

# --- Pre-flight checks ---
if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "Error: pyinstaller not found. Install with: pip install pyinstaller" >&2
  exit 1
fi

# Find src/main.py under the current directory (pick the first match deterministically)
mapfile -t CANDIDATES < <(find . -type f -path "*/src/main.py" -print | sort)
if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
  echo "Error: Could not find any 'src/main.py' under the current directory." >&2
  exit 1
fi
MAIN_PY="${CANDIDATES[0]}"
echo "Using entry point: ${MAIN_PY}"

# --- Decide build mode / cleanup ---
if [[ -d gita || -d gita_install ]]; then
  echo "Detected existing ./gita or ./gita_install -> rebuilding…"
  rm -rf gita gita_install build dist gita.spec
else
  echo "No existing ./gita or ./gita_install -> building fresh…"
  rm -rf build dist gita.spec
fi

# --- Build with PyInstaller (onedir) ---
# Result goes to ./dist/gita/
pyinstaller --clean --noconfirm --onedir --name gita "$MAIN_PY"

# --- Assemble ./gita directory ---
echo "Assembling ./gita directory..."
mkdir -p gita

if [[ ! -d dist/gita ]]; then
  echo "Error: Expected PyInstaller output at dist/gita was not found." >&2
  exit 1
fi
cp -a dist/gita/. gita/

# Copy optional project resources (only config now)
if [[ -d config ]]; then
  echo "Copying ./config -> ./gita/config"
  cp -a config gita/
else
  echo "Warning: ./config not found; skipping."
fi

# Copy uninstall.sh from ./bash into gita/
if [[ -f bash/uninstall.sh ]]; then
  cp bash/uninstall.sh gita/
  chmod +x gita/uninstall.sh
  echo "Copied ./bash/uninstall.sh -> ./gita/uninstall.sh"
else
  echo "Warning: ./bash/uninstall.sh not found; skipping."
fi

# --- Package into ./gita_install ---
echo "Packaging into ./gita_install…"
mkdir -p gita_install

# Move the built gita directory into gita_install
mv gita gita_install/

# Copy install.sh from ./bash into gita_install/
if [[ -f bash/install.sh ]]; then
  cp bash/install.sh gita_install/
  chmod +x gita_install/install.sh
  echo "Copied ./bash/install.sh -> ./gita_install/install.sh"
else
  echo "Warning: ./bash/install.sh not found; skipping."
fi

# Create gita_install/gita/OpenAi/ and copy info.md into it
mkdir -p gita_install/gita/OpenAi
if [[ -f OpenAi/info.md ]]; then
  cp OpenAi/info.md gita_install/gita/OpenAi/
  echo "Copied ./OpenAi/info.md -> ./gita_install/gita/OpenAi/info.md"
else
  echo "Warning: ./OpenAi/info.md not found; skipping."
fi

# --- Cleanup build artifacts (optional) ---
rm -rf build dist gita.spec

echo
echo "Done. Final layout:"
echo "  ./gita_install/"
echo "    ├─ gita/           # PyInstaller bundle (+ config/, uninstall.sh, OpenAi/info.md)"
echo "    └─ install.sh      # copied from ./bash/"
echo
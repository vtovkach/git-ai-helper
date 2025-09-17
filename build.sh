#!/usr/bin/env bash
# Build/rebuild "gita" with PyInstaller (onedir), assemble a final ./gita folder,
# then package it into ./gita_install/ along with ./install.sh (moved).

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

# Copy optional project resources
for D in config OpenAi; do
  if [[ -d "$D" ]]; then
    echo "Copying ./$D -> ./gita/$D"
    cp -a "$D" "gita/"
  else
    echo "Warning: ./$D not found; skipping."
  fi
done

# --- Create uninstall.sh inside gita ---
cat > gita/uninstall.sh <<'EOF'
#!/usr/bin/env bash
# Simple uninstaller for gita: remove the ./gita directory

set -euo pipefail

TARGET_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "This will remove: $TARGET_DIR"
read -p "Are you sure? [y/N] " CONFIRM
if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
  rm -rf "$TARGET_DIR"
  echo "gita has been uninstalled."
else
  echo "Uninstall cancelled."
fi
EOF
chmod +x gita/uninstall.sh

# --- Package into ./gita_install ---
echo "Packaging into ./gita_install…"
mkdir -p gita_install

# Move the built gita directory into gita_install
mv gita gita_install/

# Move install.sh from current directory into gita_install (if present)
if [[ -f install.sh ]]; then
  mv install.sh gita_install/
  chmod +x gita_install/install.sh || true
  echo "Moved ./install.sh -> ./gita_install/install.sh"
else
  echo "Warning: ./install.sh not found; skipping move."
fi

# --- Cleanup build artifacts (optional) ---
rm -rf build dist gita.spec

echo
echo "Done. Final layout:"
echo "  ./gita_install/"
echo "    ├─ gita/           # PyInstaller bundle (+ config/, OpenAi/, uninstall.sh)"
echo "    └─ install.sh      # moved from project root (if present)"
echo
echo "Run the app after install with: ./gita_install/gita/gita"

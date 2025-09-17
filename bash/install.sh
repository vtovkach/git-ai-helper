#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="gita"                    # local folder produced by PyInstaller --onedir
DEST_DIR="/usr/local/gita"        # installed location
BIN_LINK="/usr/local/bin/gita"    # symlink target

# Use sudo if not root
SUDO=""
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  SUDO="sudo"
fi

# 0) sanity checks
if [[ ! -d "$SRC_DIR" ]]; then
  echo "ERROR: '$SRC_DIR' directory not found. Run this script from the repo root."
  exit 1
fi
if [[ ! -x "$SRC_DIR/gita" ]]; then
  echo "ERROR: '$SRC_DIR/gita' executable not found or not executable."
  exit 1
fi

echo "Installing gita ..."
echo " - Source: $SRC_DIR/"
echo " - Dest:   $DEST_DIR"
echo " - Link:   $BIN_LINK"
echo

# 1) check for existing install
need_prompt=false
[[ -e "$DEST_DIR" ]] && echo "Found existing: $DEST_DIR" && need_prompt=true
[[ -e "$BIN_LINK" ]] && echo "Found existing: $BIN_LINK" && need_prompt=true

if $need_prompt; then
  read -rp "Remove existing install and continue? [y/N]: " ans
  ans=${ans,,}  # lowercase
  if [[ "$ans" == "y" || "$ans" == "yes" ]]; then
    [[ -e "$BIN_LINK" ]] && $SUDO rm -f "$BIN_LINK"
    [[ -e "$DEST_DIR" ]] && $SUDO rm -rf "$DEST_DIR"
  else
    echo "Aborting install. Nothing changed."
    exit 0
  fi
fi

# 2) copy directory and create symlink
$SUDO mkdir -p "$DEST_DIR"
$SUDO cp -a "$SRC_DIR/." "$DEST_DIR/"
# ensure main binary is executable (in case archive stripped it)
$SUDO chmod +x "$DEST_DIR/gita"

# create/update symlink
$SUDO ln -sf "$DEST_DIR/gita" "$BIN_LINK"

echo
echo "✅ gita installed."
echo "Try: gita --help"
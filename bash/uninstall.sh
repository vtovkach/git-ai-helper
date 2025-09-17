#!/usr/bin/env bash
set -euo pipefail

DEST_DIR="/usr/local/gita"
BIN_LINK="/usr/local/bin/gita"

# escalate if not root
SUDO=""
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  SUDO="sudo"
fi

echo "Uninstalling gita ..."

# safety guard against accidental rm -rf on wrong path
if [[ "$DEST_DIR" != "/usr/local/gita" ]]; then
  echo "Refusing to remove unexpected path: $DEST_DIR"
  exit 1
fi

# detect what exists
exists=false
[[ -e "$DEST_DIR" ]] && echo "Found: $DEST_DIR" && exists=true
if [[ -e "$BIN_LINK" ]]; then
  if [[ -L "$BIN_LINK" ]]; then
    target=$(readlink -f "$BIN_LINK" || true)
    echo "Found: $BIN_LINK -> ${target:-"(unresolvable)"}"
  else
    echo "Found: $BIN_LINK"
  fi
  exists=true
fi

# nothing to do
if ! $exists; then
  echo "Nothing to uninstall."
  exit 0
fi

# confirm
read -rp "Remove the files above? [y/N]: " ans
ans=${ans,,}
if [[ "$ans" != "y" && "$ans" != "yes" ]]; then
  echo "Aborted."
  exit 0
fi

# remove link and payload
[[ -e "$BIN_LINK" ]] && $SUDO rm -f "$BIN_LINK"
[[ -e "$DEST_DIR" ]] && $SUDO rm -rf "$DEST_DIR"

echo "✅ gita has been removed."
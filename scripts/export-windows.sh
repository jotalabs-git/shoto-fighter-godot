#!/usr/bin/env bash
# Export Rock Kombat for Windows x86_64 from Linux using official Godot templates.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${1:-release}"
case "$MODE" in
  release) FLAG="--export-release" ;;
  debug)   FLAG="--export-debug" ;;
  *) echo "Uso: $0 [release|debug]" >&2; exit 2 ;;
esac

if [[ -n "${GODOT:-}" ]]; then
  if ! command -v "$GODOT" >/dev/null 2>&1; then
    echo "ERROR: No encuentro GODOT='$GODOT'." >&2
    exit 127
  fi
  ENGINE="$GODOT"
elif command -v godot >/dev/null 2>&1; then
  ENGINE=godot
elif command -v godot4 >/dev/null 2>&1; then
  ENGINE=godot4
else
  echo "ERROR: Godot 4 no está instalado. Instalá el editor de Godot y sus plantillas de exportación." >&2
  exit 127
fi

if [[ ! -f export_presets.cfg ]]; then
  echo "ERROR: Falta export_presets.cfg (preset 'Windows Desktop')." >&2
  exit 1
fi

version="$("$ENGINE" --version)"
echo "Godot: $version"
echo "Plataforma de exportación: Windows Desktop x86_64 ($MODE)"

# Templates must match the editor's release version (exclude .official/hash).
# Download the official TPZ when missing, unless the user opts out.
version_folder="$(printf '%s\n' "$version" | sed -E 's/\.official(\..*)?$//')"
templates_base="${XDG_DATA_HOME:-$HOME/.local/share}/godot/export_templates"
if [[ ! -s "$templates_base/$version_folder/windows_debug_x86_64.exe" ||
      ! -s "$templates_base/$version_folder/windows_release_x86_64.exe" ]]; then
  if [[ "${GODOT_AUTO_TEMPLATES:-1}" == "0" ]]; then
    echo "ERROR: Faltan plantillas Windows para $version_folder." >&2
    echo "Instalalas con: make windows-setup" >&2
    exit 1
  fi
  echo "Instalando automáticamente las plantillas Windows ($version_folder)..."
  python3 scripts/install-windows-templates.py "$version"
fi
mkdir -p export/windows

echo "Importando GLB, texturas, fuentes y recursos..."
"$ENGINE" --headless --path "$ROOT" --editor --import --quit

exe="$ROOT/export/windows/RockKombat.exe"
pck="$ROOT/export/windows/RockKombat.pck"
# Prevent a previous successful export from masking a new failed one.
rm -f "$exe" "$pck"

echo "Generando el ejecutable Windows..."
"$ENGINE" --headless --path "$ROOT" "$FLAG" "Windows Desktop" "$exe"

if [[ ! -s "$exe" || ! -s "$pck" ]]; then
  echo "ERROR: Exportación incompleta. Se requieren RockKombat.exe y RockKombat.pck." >&2
  exit 1
fi

echo "OK: $exe"
echo "OK: $pck"
echo "Copiá AMBOS archivos a una misma carpeta de Windows antes de ejecutar el juego."

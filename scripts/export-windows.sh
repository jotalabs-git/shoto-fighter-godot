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

# Official templates must have the same version as the editor.
# Different distributions can choose custom data paths, so let Godot validate
# the templates and report its own precise error instead of guessing paths.
if [[ ! -d "$HOME/.local/share/godot/export_templates/$version" ]]; then
  echo "AVISO: No se detectaron plantillas en ~/.local/share/godot/export_templates/$version."
  echo "       Si la exportación falla, abrí Godot > Editor > Manage Export Templates"
  echo "       e instalá la versión EXACTA que informa: $version"
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

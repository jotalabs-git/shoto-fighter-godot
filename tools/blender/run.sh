#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Uso: $0 {generate|render|export-glb} PERSONAJE [opciones]" >&2
}
if (( $# < 2 )); then
  usage
  exit 2
fi
case "$1" in
  generate) script=generate_character.py ;;
  render) script=render_character.py ;;
  export-glb) script=export_glb.py ;;
  *) usage; exit 2 ;;
esac
shift
blender_bin=${BLENDER:-blender}
if ! command -v "$blender_bin" >/dev/null; then
  echo "No se encontró Blender. Indicá el ejecutable con BLENDER=/ruta/al/binario." >&2
  exit 127
fi
tools_dir=$(cd "$(dirname "$0")" && pwd)
exec "$blender_bin" --background --factory-startup --threads "${BLENDER_THREADS:-4}" \
  --python-exit-code 1 --python "$tools_dir/$script" -- "$@"

#!/usr/bin/env python3
"""Instala fuentes libres oficiales de Rock Kombat (Google Fonts, SIL OFL 1.1).

Descarga binarios TTF y comprueba el SHA de su objeto Git, fijado al
archivo verificado en google/fonts. Las licencias se distribuyen junto
al código en assets/fonts/licenses/ y no se modifican.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "fonts"
BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl"
FONTS = {
    "MetalMania-Regular.ttf": ("metalmania", "MetalMania-Regular.ttf",
                               "db41a35fadc970e011bc076bba3f511160c80dde"),
    "Bangers-Regular.ttf": ("bangers", "Bangers-Regular.ttf",
                            "9b0f8c1f1b45e7bb4971b7d6a8604f9aacacdd32"),
    "Oxanium-Variable.ttf": ("oxanium", "Oxanium%5Bwght%5D.ttf",
                             "ead485c7bf517197db91ef657614ac37d8007775"),
}


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    missing = []
    for destination, (family, source, expected_sha) in FONTS.items():
        target = OUT / destination
        if target.is_file() and git_blob_sha(target.read_bytes()) == expected_sha:
            print(f"OK: {destination} (verificada)")
            continue
        url = f"{BASE}/{family}/{source}"
        print(f"Descargando {family} desde Google Fonts...", flush=True)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "RockKombatFontInstaller/1"})
            with urllib.request.urlopen(request, timeout=35) as response:
                data = response.read(3_000_001)
            if len(data) > 3_000_000:
                raise ValueError("archivo de fuente demasiado grande")
            actual = git_blob_sha(data)
            if actual != expected_sha:
                raise ValueError(f"SHA Git inesperado: {actual}; esperado: {expected_sha}")
            if data[:4] not in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
                raise ValueError("el archivo no parece una fuente OpenType/TrueType")
            temp = target.with_suffix(".ttf.part")
            temp.write_bytes(data)
            temp.replace(target)
            print(f"OK: {destination}")
        except (OSError, ValueError, urllib.error.URLError) as exc:
            print(f"ERROR: {destination}: {exc}", file=sys.stderr)
            missing.append(destination)
    if missing:
        print("Fuentes incompletas. Godot utilizará su tipografía integrada como fallback.", file=sys.stderr)
        return 1
    print("Tipografías instaladas. Ejecutá la importación de Godot antes de iniciar el juego.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

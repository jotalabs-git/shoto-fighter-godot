#!/usr/bin/env python3
"""Install official Godot Windows x86_64 templates for the local editor.

Downloads the Godot Foundation's .tpz for the exact editor version and
extracts only the two required Windows templates. Does not modify Godot
project assets or install templates for any other version.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

WINDOWS_FILES = ("windows_debug_x86_64.exe", "windows_release_x86_64.exe")
VERSION = re.compile(r"^(\d+\.\d+(?:\.\d+)?\.(?:stable|dev\d+|alpha\d+|beta\d+|rc\d+))")
MAX_ARCHIVE_BYTES = 2_500_000_000


def parse_version(raw: str) -> tuple[str, str]:
    match = VERSION.match(raw)
    if not match:
        raise ValueError(f"No se reconoce la versión de Godot: {raw!r}")
    directory = match.group(1)
    version, channel = directory.rsplit(".", 1)
    return directory, f"{version}-{channel}"


def templates_dir(version: str) -> Path:
    data = os.environ.get("XDG_DATA_HOME")
    base = Path(data) if data and Path(data).is_absolute() else Path.home() / ".local/share"
    return base / "godot" / "export_templates" / version


def present(destination: Path) -> bool:
    return all((destination / name).is_file() and (destination / name).stat().st_size > 0
               for name in WINDOWS_FILES)


def download(url: str, path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "RockKombat-WindowsExport/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, path.open("wb") as output:
        total = 0
        while data := response.read(1024 * 1024):
            total += len(data)
            if total > MAX_ARCHIVE_BYTES:
                raise ValueError("Paquete excede el límite de 2.5 GB")
            output.write(data)
            if total % (64 * 1024 * 1024) < len(data):
                print(f"  Descargados {total // (1024 * 1024)} MiB...", flush=True)


def install(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as package:
        entries = {}
        for info in package.infolist():
            if info.filename.startswith("templates/"):
                basename = Path(info.filename).name
                if basename in WINDOWS_FILES:
                    entries[basename] = info
        missing = [name for name in WINDOWS_FILES if name not in entries]
        if missing:
            raise ValueError(f"El TPZ oficial no contiene: {', '.join(missing)}")
        for name, info in entries.items():
            if info.file_size <= 0 or info.file_size > 200 * 1024 * 1024:
                raise ValueError(f"Tamaño inesperado en plantilla {name}: {info.file_size}")
        # Replace via temp files: a failed extraction cannot leave a half-written exe.
        for name in WINDOWS_FILES:
            target = destination / name
            temporary = destination / (name + ".partial")
            try:
                with package.open(entries[name]) as source, temporary.open("wb") as out:
                    shutil.copyfileobj(source, out, length=1024 * 1024)
                if temporary.stat().st_size != entries[name].file_size:
                    raise ValueError(f"Extracción incompleta: {name}")
                temporary.replace(target)
                print(f"  Instalado: {target}")
            finally:
                temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("godot_version", help="Salida completa de godot --version")
    parser.add_argument("--archive", type=Path, help="TPZ descargado manualmente (sin descargar otra vez)")
    args = parser.parse_args()
    try:
        directory, release = parse_version(args.godot_version)
        destination = templates_dir(directory)
        if present(destination):
            print(f"Plantillas Windows instaladas: {destination}")
            return 0
        url = (
            f"https://downloads.godotengine.org/?version={release.rsplit('-', 1)[0]}"
            f"&flavor={release.rsplit('-', 1)[1]}&platform=templates&slug=export_templates.tpz"
        )
        print(f"Faltan las plantillas Windows de Godot {directory}.")
        print(f"Destino: {destination}")
        if args.archive is not None:
            if not args.archive.is_file():
                raise FileNotFoundError(f"No se encuentra el TPZ: {args.archive}")
            install(args.archive, destination)
        else:
            with tempfile.TemporaryDirectory(prefix="rock-kombat-templates-") as temporary:
                archive = Path(temporary) / "export_templates.tpz"
                print(f"Descargando paquete oficial: {url}", flush=True)
                download(url, archive)
                install(archive, destination)
        if not present(destination):
            raise RuntimeError("Las plantillas Windows aún no están completas")
        print("Plantillas Windows listas.")
        return 0
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print(f"ERROR instalando plantillas: {error}", file=sys.stderr)
        print("Alternativa: Godot > Editor > Manage Export Templates > Download and Install.",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

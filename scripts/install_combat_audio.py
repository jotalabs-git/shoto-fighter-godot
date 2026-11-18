#!/usr/bin/env python3
"""Instala las bibliotecas de audio verificadas para Rock Kombat.

Kenney (CC0): Impact Sounds y Voiceover Pack: Fighter.
OpenGameArt (CC0): 37 hits/punches de Independent.nu.
OpenGameArt (CC BY 3.0): 24 cute fighting game voices de bart.

Los 17 OGG seleccionados de Kenney ya se versionan en assets/audio/.
Este instalador añade los packs completos a la biblioteca local y sus
variantes de combate; nunca incorpora sonidos Sonniss a un repositorio.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "assets" / "audio"
LOCAL = AUDIO / "local"
LIBRARY = LOCAL / "library"

PACKS = {
    "kenney_impact": (
        "https://kenney.nl/media/pages/assets/impact-sounds/87b4ddecda-1677589768/kenney_impact-sounds.zip",
        "CC0 1.0", "Kenney", "https://kenney.nl/assets/impact-sounds",
    ),
    "kenney_announcer": (
        "https://kenney.nl/media/pages/assets/voiceover-pack-fighter/6ceb77c6f1-1677589837/kenney_voiceover-pack-fighter.zip",
        "CC0 1.0", "Kenney", "https://kenney.nl/assets/voiceover-pack-fighter",
    ),
    "oga_hits": (
        "https://opengameart.org/sites/default/files/independent_nu_ljudbank-hits_and_punches.7z",
        "CC0 1.0", "Independent.nu", "https://opengameart.org/content/37-hitspunches",
    ),
    "oga_cute": (
        "https://opengameart.org/sites/default/files/cute.zip",
        "CC BY 3.0", "bart", "https://opengameart.org/content/24-cute-fighting-game-voice-recordings",
    ),
}
ACTIONS = ("effort_light", "effort_heavy", "hurt")
CHARACTERS = ("guitarist", "frontman", "neutral")
HIT_KEYS = (
    "hit_punch_light", "hit_punch_medium", "hit_punch_heavy",
    "hit_kick_light", "hit_kick_medium", "hit_kick_heavy",
    "hit_sweep", "fall",
)


def _download(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "RockKombatAudioInstaller/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, target.open("wb") as output:
        total = 0
        while chunk := response.read(65536):
            total += len(chunk)
            if total > 120 * 1024 * 1024:
                raise ValueError("El archivo comprimido supera el límite de 120 MiB")
            output.write(chunk)


def _unpack(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as z:
            total = 0
            for info in z.infolist():
                if info.is_dir():
                    continue
                if info.file_size > 30 * 1024 * 1024:
                    continue
                if not info.filename.lower().endswith((".ogg", ".wav", ".mp3")):
                    continue
                total += info.file_size
                if total > 300 * 1024 * 1024:
                    raise ValueError("El paquete descomprimido supera 300 MiB")
                # Nombre plano y saneado, sin confiar en rutas del ZIP.
                basename = Path(info.filename.replace("\\", "/")).name
                out = destination / basename
                with z.open(info) as src, out.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
    else:
        seven_zip = shutil.which("7z") or shutil.which("7zz") or shutil.which("7za")
        if not seven_zip:
            raise RuntimeError("Hace falta 7z (p7zip / 7zip) para el paquete 37 hits/punches")
        with tempfile.TemporaryDirectory() as td:
            subprocess.run([seven_zip, "x", str(archive), "-y", "-o" + td],
                           check=True, stdout=subprocess.DEVNULL)
            for source in sorted(Path(td).rglob("*")):
                if source.is_file() and source.suffix.lower() in (".ogg", ".wav", ".mp3"):
                    if source.stat().st_size <= 30 * 1024 * 1024:
                        shutil.copy2(source, destination / source.name)
                elif source.is_file() and source.suffix.lower() == ".flac":
                    ffmpeg = shutil.which("ffmpeg")
                    if ffmpeg is None:
                        raise RuntimeError("Hace falta ffmpeg para convertir los FLAC de Independent.nu")
                    out = destination / (source.stem + ".wav")
                    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                                    "-i", str(source), "-ar", "22050", "-ac", "1", str(out)],
                                   check=True)


def _audio_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.iterdir() if p.is_file()
                  and p.suffix.lower() in (".ogg", ".wav", ".mp3"))


def _alias(source: Path, key: str) -> dict:
    if source.suffix.lower() not in (".ogg", ".wav"):
        raise ValueError("El recurso requiere WAV u OGG; MP3 no se copia como override")
    destination = LOCAL / (key + source.suffix.lower())
    shutil.copy2(source, destination)
    return {
        "event": key,
        "filename": str(source.name),
        "installed_as": destination.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    }


def _map_pack(key: str, directory: Path) -> list[dict]:
    files = [p for p in _audio_files(directory) if p.suffix.lower() in (".ogg", ".wav")]
    if not files:
        raise ValueError(f"{key}: no hay WAV/OGG reconocidos")
    mapped = []
    if key == "oga_cute":
        for index, (who, action) in enumerate(
                (who, action) for who in CHARACTERS for action in ACTIONS):
            # Asignación estable y explícita de variantes para comparar.
            # Selección artística final a revisar escuchando los archivos.
            source = files[index % len(files)]
            mapped.append(_alias(source, "voice_humor_" + who + "_" + action))
    elif key == "oga_hits":
        for index, event in enumerate(HIT_KEYS):
            source = files[index % len(files)]
            mapped.append(_alias(source, event + "_oga"))
    return mapped


def _install_pack(key: str, archives: Path) -> dict:
    url, license_name, author, source_url = PACKS[key]
    destination = LIBRARY / key
    if not destination.exists() or not _audio_files(destination):
        destination.mkdir(parents=True, exist_ok=True)
        filenames = {
            "kenney_impact": "kenney_impact-sounds.zip",
            "kenney_announcer": "kenney_voiceover-pack-fighter.zip",
            "oga_hits": "independent_nu_ljudbank-hits_and_punches.7z",
            "oga_cute": "cute.zip",
        }
        local_archive = archives / filenames[key]
        if local_archive.is_file():
            print(f"Instalando {key} desde {local_archive}", flush=True)
            _unpack(local_archive, destination)
        else:
            with tempfile.TemporaryDirectory() as td:
                path = Path(td) / ("sound.7z" if key == "oga_hits" else "sound.zip")
                print(f"Descargando {key}...", flush=True)
                _download(url, path)
                _unpack(path, destination)
    files = _audio_files(destination)
    mapped = _map_pack(key, destination)
    print(f"OK {key}: {len(files)} archivos, {len(mapped)} asignaciones")
    return {"pack": key, "author": author, "license": license_name,
            "source": source_url, "installed": len(files), "mapped": mapped}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", choices=(*PACKS, "all"), default="all",
                        help="Paquete por instalar (por defecto todos)")
    parser.add_argument("--archive-dir", type=Path,
                        default=LOCAL / "downloads",
                        help="Carpeta con ZIP/7z descargados manualmente (si existen)")
    parser.add_argument("--sonniss-impact", type=Path,
                        help="WAV/OGG de impacto obtenido legalmente del bundle Sonniss")
    parser.add_argument("--sonniss-fall", type=Path,
                        help="WAV/OGG de caída del bundle Sonniss")
    args = parser.parse_args()
    LOCAL.mkdir(parents=True, exist_ok=True)
    LIBRARY.mkdir(parents=True, exist_ok=True)
    manifest = []
    failed = []
    packs = list(PACKS) if args.pack == "all" else [args.pack]
    for key in packs:
        try:
            manifest.append(_install_pack(key, args.archive_dir))
        except Exception as exc:
            failed.append(key)
            print(f"ERROR {key}: {exc}", file=sys.stderr)
    for option, sound_key in ((args.sonniss_impact, "hit_punch_heavy_sonniss"),
                              (args.sonniss_fall, "fall_sonniss")):
        if option is not None:
            try:
                manifest.append({"pack": "sonniss_local", "license": "Sonniss #GameAudioGDC",
                                 "mapped": [_alias(option, sound_key)]})
            except Exception as exc:
                failed.append("sonniss")
                print(f"ERROR Sonniss: {exc}", file=sys.stderr)
    (LOCAL / "installed_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Créditos: assets/audio/CREDITS.md y pantalla CREDITOS del juego")
    if failed:
        print("Sin instalar: " + ", ".join(failed), file=sys.stderr)
        return 1
    print("Importá los assets en Godot antes de iniciar el juego.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

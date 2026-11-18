"""Validate the on-disk export without Godot or Blender."""
import argparse
import json
import re
import sys
import zlib
from pathlib import Path

from common import ASSETS, REFERENCE, read_json
from png import read_png


def validate_frame(path, canvas):
    width, height, pixels = read_png(path, canvas)
    alpha = pixels[3::4]
    if 0 not in alpha or 255 not in alpha:
        raise ValueError("se requieren píxeles transparentes y opacos")
    border = alpha[:width] + alpha[-width:] + alpha[::width] + alpha[width - 1::width]
    if any(value >= 128 for value in border):
        raise ValueError("silueta cortada por el borde del lienzo")
    return width, height, pixels


def validate(folder, complete=False):
    errors = []
    try:
        manifest = read_json(folder / "manifest.json")
    except (OSError, json.JSONDecodeError) as error:
        return [f"{folder}/manifest.json: {error}"]
    if not isinstance(manifest, dict):
        return ["manifest.json: se esperaba un objeto"]
    canvas = manifest.get("canvas")
    axis = manifest.get("axis")
    if not (isinstance(canvas, list) and len(canvas) == 2
            and all(type(value) is int and 0 < value <= 4096 for value in canvas)):
        return ["canvas: se requieren dos dimensiones enteras positivas hasta 4096"]
    if not (isinstance(axis, list) and len(axis) == 2
            and all(type(value) is int and 0 <= value < length for value, length in zip(axis, canvas))):
        errors.append("axis: se requieren dos coordenadas enteras dentro del canvas")
    actions = manifest.get("anims")
    if not isinstance(actions, dict):
        return errors + ["anims: se esperaba un objeto"]
    allowed = read_json(REFERENCE)["anims"]
    required = set(allowed) if complete else {"idle"}
    errors.extend(f"{name}: falta animación" for name in sorted(required - actions.keys()))
    for name, info in actions.items():
        if not re.fullmatch(r"[a-z][a-z_]*", name) or name not in allowed:
            errors.append(f"{name!r}: nombre no admitido")
            continue
        if not isinstance(info, dict):
            errors.append(f"{name}: se esperaba un objeto")
            continue
        count, durations, loop = (info.get(key) for key in ("frames", "durs", "loop"))
        if type(count) is not int or not 1 <= count <= 1000:
            errors.append(f"{name}: frames debe ser un entero entre 1 y 1000")
            continue
        if not (isinstance(durations, list) and len(durations) == count
                and all(type(tick) is int and tick > 0 for tick in durations)):
            errors.append(f"{name}: durs debe contener {count} enteros positivos")
        if type(loop) is not bool:
            errors.append(f"{name}: loop debe ser booleano")
        directory = folder / name
        if directory.is_symlink():
            errors.append(f"{name}: directorio simbólico no permitido")
            continue
        expected = {f"{index:03d}.png" for index in range(count)}
        actual = {path.name for path in directory.glob("*.png")}
        errors.extend(f"{name}/{file}: PNG no declarado" for file in sorted(actual - expected))
        for file in sorted(expected):
            path = directory / file
            try:
                if path.is_symlink():
                    raise ValueError("enlace simbólico no permitido")
                validate_frame(path, canvas)
            except (OSError, ValueError, zlib.error) as error:
                errors.append(f"{name}/{file}: {error}")
    for directory in sorted(folder.iterdir()):
        if directory.is_dir() and directory.name not in actions:
            errors.extend(f"{directory.name}/{file.name}: PNG sin animación declarada"
                          for file in sorted(directory.glob("*.png")))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Directorio de exportación o ID del personaje")
    parser.add_argument("--complete", action="store_true", help="Exigir el inventario KFM completo")
    args = parser.parse_args()
    folder = args.folder if args.folder.exists() else ASSETS / args.folder
    errors = validate(folder, args.complete)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    actions = read_json(folder / "manifest.json")["anims"]
    print(f"{folder.name}: {len(actions)} animaciones, {sum(info['frames'] for info in actions.values())} PNG RGBA válidos")
    return 0


if __name__ == "__main__":
    sys.exit(main())

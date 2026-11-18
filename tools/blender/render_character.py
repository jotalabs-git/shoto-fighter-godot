"""Render authored actions to numbered RGBA sprites and publish a validated manifest."""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ASSETS, REFERENCE, SOURCES, blender_args, read_json, write_json
from png import strip_text_metadata
from pose_controls import IK_PROPERTIES
from validate_character import validate


def export(args):
    started = time.monotonic()
    source = SOURCES / f"{args.character}.blend"
    fingerprint = hashlib.sha256(source.read_bytes() + bpy.app.version_string.encode()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    rig = bpy.data.objects["Rig"]
    for property_name in IK_PROPERTIES:
        if property_name in rig:
            rig[property_name] = 0.0
    rig.update_tag(refresh={"OBJECT"})
    catalog = json.loads(scene["sprite_catalog"])
    selected = args.actions or list(catalog)
    unknown = set(selected) - catalog.keys()
    if unknown:
        raise ValueError(f"acciones no disponibles: {', '.join(sorted(unknown))}")

    canvas = [scene.render.resolution_x, scene.render.resolution_y]
    projection = world_to_camera_view(scene, scene.camera, Vector((0, 0, 0)))
    axis = [round(projection.x * canvas[0]), round((1 - projection.y) * canvas[1])]
    calibration = list(scene["axis"])
    if axis != calibration or scene.render.resolution_percentage != 100:
        raise ValueError(f"proyección {axis} distinta de la calibración {calibration}")

    target = args.output or ASSETS / args.character
    prior = target / "manifest.json"
    manifest = read_json(prior) if prior.exists() else {"canvas": canvas, "axis": axis, "anims": {}}
    known = read_json(REFERENCE)["anims"]
    if set(manifest["anims"]) - known.keys():
        raise ValueError(f"{prior}: contiene nombres de animación no admitidos")
    if manifest["canvas"] != canvas or manifest["axis"] != axis:
        if set(manifest["anims"]) - set(selected):
            raise ValueError("cambió la calibración, reexportá todas las acciones existentes")
        manifest = {"canvas": canvas, "axis": axis, "anims": {}}

    target.parent.mkdir(parents=True, exist_ok=True)
    cache_path = target / ".render-cache.json"
    cache = read_json(cache_path) if cache_path.exists() else {}
    for directory in target.iterdir() if target.exists() else ():
        if directory.is_symlink():
            raise ValueError(f"{directory}: enlace simbólico no permitido")
        if directory.is_dir() and directory.name not in manifest["anims"] and any(directory.glob("*.png")):
            raise ValueError(f"{directory}: carpeta con PNG fuera del manifiesto")

    # Stage the full proposed export on the same filesystem and validate before replacing files.
    with tempfile.TemporaryDirectory(prefix=f".{target.name}-", dir=target.parent) as temporary:
        stage = Path(temporary)
        for name in manifest["anims"]:
            old = target / name
            if old.is_dir():
                for file in old.glob("*.png"):
                    if file.is_symlink():
                        raise ValueError(f"{file}: enlace simbólico no permitido")
                shutil.copytree(old, stage / name, ignore=shutil.ignore_patterns("*.import"))
        if target.exists():
            prior_errors = validate(target)
        else:
            prior_errors = ["exportación nueva"]
        changed = []
        for name in dict.fromkeys(selected):
            info = catalog[name]
            action = bpy.data.actions[name]
            if (not args.force and not prior_errors and cache.get(name) == fingerprint
                    and manifest["anims"].get(name) == info):
                print(f"{name}: caché ({info['frames']} PNG)", flush=True)
                continue
            directory = stage / name
            if directory.exists():
                shutil.rmtree(directory)
            directory.mkdir()
            rig.animation_data.action = action
            rig.animation_data.action_slot = action.slots[0]
            tick = 1
            for index, duration in enumerate(info["durs"]):
                scene.frame_set(tick)
                scene.render.filepath = str(directory / f"{index:03d}.png")
                bpy.ops.render.render(write_still=True)
                strip_text_metadata(Path(scene.render.filepath))
                tick += duration
            manifest["anims"][name] = info
            cache[name] = fingerprint
            changed.append(name)
            print(f"{name}: {info['frames']} PNG, {tick - 1} ticks", flush=True)
        write_json(stage / "manifest.json", manifest)
        errors = validate(stage)
        if errors:
            if args.diagnostics:
                shutil.copytree(stage, args.diagnostics, dirs_exist_ok=True)
            raise ValueError("\n".join(errors))
        target.mkdir(parents=True, exist_ok=True)
        for name in changed:
            directory = target / name
            directory.mkdir(exist_ok=True)
            for path in directory.glob("*.png"):
                if not (stage / name / path.name).exists():
                    path.unlink()
            for path in (stage / name).glob("*.png"):
                os.replace(path, directory / path.name)
        write_json(stage / ".render-cache.json", cache)
        os.replace(stage / "manifest.json", prior)
        os.replace(stage / ".render-cache.json", cache_path)
    print(f"{args.character}: {len(manifest['anims'])} acciones válidas en {time.monotonic() - started:.1f} s")


if __name__ == "__main__":
    parser, argv = blender_args(__doc__)
    parser.add_argument("--actions", nargs="+", help="Reemplazar solo las acciones indicadas")
    parser.add_argument("--output", type=Path, help="Exportar a un directorio de revisión")
    parser.add_argument("--force", action="store_true", help="Volver a renderizar aunque coincida la caché")
    parser.add_argument("--diagnostics", type=Path, help="Retener los renders de una exportación rechazada")
    export(parser.parse_args(argv))

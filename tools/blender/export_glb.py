"""Bake the existing editable puppet and supplementary poses into a Godot GLB."""
import json
import os
import struct
import sys
import tempfile
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arm_motion import sample_gesture
from common import ROOT, SOURCES, blender_args, write_json
from generate_character import key_pose
from pose_controls import IK_PROPERTIES
from poses import BONES
from poses_3d import ARTICULATED_ARMS, FALL_CLIPS, GAIT_TRAVEL, PUNCHES, performances


def down_floor(scene, rig, character):
    action = bpy.data.actions["down_hold"]
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    scene.frame_set(1)
    graph = bpy.context.evaluated_depsgraph_get()
    bottoms = {}
    for obj in rig.children:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        try:
            bottoms[obj.name] = min((evaluated.matrix_world @ vertex.co).z for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    bottom = min(bottoms.values())
    torso = {"frontman": "Bare torso · pelvis anchored", "guitarist": "Biker jacket · torso",
             "ozzy": "Ozzy · velvet coat torso", "bruce": "Bruce · leather jacket torso"}[character]
    clearance = bottoms[torso] - bottom
    if clearance > .075:
        raise ValueError(f"{character}: el torso de down_hold queda a {clearance:.3f} m del suelo")
    print(f"{character}: torso a {clearance:.3f} m del suelo en down_hold")
    return round(-bottom, 4)


def export(args):
    source = SOURCES / f"{args.character}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    bpy.ops.object.mode_set(mode="OBJECT")
    scene = bpy.context.scene
    rig = bpy.data.objects["Rig"]
    if not set(BONES).issubset(rig.data.bones.keys()):
        raise ValueError(f"{source}: esqueleto incompleto")
    for prop in IK_PROPERTIES:
        if prop in rig:
            rig[prop] = 0.0
    rig.update_tag(refresh={"OBJECT"})
    catalog = {
        name: {"ticks": sum(info["durs"]), "loop": info["loop"]}
        for name, info in json.loads(scene["sprite_catalog"]).items()
    }
    original = json.loads(scene["sprite_catalog"])
    for name, info in original.items():
        if "phases" in info:
            catalog[name]["impact"] = sum(info["durs"][:info["phases"][0]])
            catalog[name]["recovery"] = sum(info["durs"][:info["phases"][1]])
    for name, poses in performances(args.character).items():
        old = bpy.data.actions.get(name)
        action = bpy.data.actions.new(name + "_bake")
        rig.animation_data.action = action
        loop = name in GAIT_TRAVEL or catalog.get(name, {}).get("loop", False)
        if name in ARTICULATED_ARMS:
            frames = list(sample_gesture(poses, loop, args.character == "frontman"))
            frames.append(frames[0 if loop else -1])
            for tick, pose in enumerate(frames, 1):
                key_pose(rig, pose, tick)
        else:
            tick = 1
            for duration, pose in poses:
                key_pose(rig, pose, tick)
                tick += duration
            key_pose(rig, poses[0 if loop else -1][1], tick)
        action.use_frame_range = True
        action.frame_start, action.frame_end = 1, tick
        if old is not None:
            bpy.data.actions.remove(old)
        action.name = name
        action.use_fake_user = True
        catalog[name] = {**catalog.get(name, {}), "ticks": tick - 1, "loop": loop}
        if name in GAIT_TRAVEL:
            catalog[name]["travel"] = GAIT_TRAVEL[name]
        if name in FALL_CLIPS:
            catalog[name]["ground_contact"] = sum(duration for duration, _ in poses[:2])
        if name in PUNCHES:
            startup, active, *_ = PUNCHES[name]
            catalog[name].update(impact=startup, recovery=startup + active)
        elif name == "crouch_mk" or name.startswith(("jump_l", "jump_m", "jump_h")):
            catalog[name]["impact"] = poses[0][0]
            catalog[name]["recovery"] = sum(duration for duration, _ in poses[:2])
    scene.frame_start = 1
    scene.frame_end = int(max(action.frame_end for action in bpy.data.actions))
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    for obj in rig.children:
        if obj.type == "MESH":
            obj.select_set(True)
    floor_offset = down_floor(scene, rig, args.character)
    rig.animation_data.action = bpy.data.actions["idle"]
    rig.animation_data.action_slot = rig.animation_data.action.slots[0]
    scene.frame_set(1)

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output) as temporary:
        glb = Path(temporary) / f"{args.character}.glb"
        result = bpy.ops.export_scene.gltf(
            filepath=str(glb), export_format="GLB", use_selection=True,
            export_apply=True, export_def_bones=True, export_leaf_bone=False,
            export_hierarchy_flatten_bones=True,
            export_animations=True, export_animation_mode="ACTIONS",
            export_anim_single_armature=True, export_force_sampling=True,
            export_frame_range=False, export_anim_slide_to_zero=True,
            export_extras=False, export_lights=False,
            export_cameras=False,
        )
        if "FINISHED" not in result:
            raise RuntimeError("falló el exportador glTF")
        with glb.open("rb") as stream:
            signature, version, _ = struct.unpack("<4sII", stream.read(12))
            length, chunk = struct.unpack("<II", stream.read(8))
            if (signature, version, chunk) != (b"glTF", 2, 0x4E4F534A):
                raise ValueError("contenedor GLB inválido")
            model = json.loads(stream.read(length))
        clips = model.get("animations", [])
        names = [clip.get("name") for clip in clips]
        if set(names) != catalog.keys() or len(names) != len(catalog):
            raise ValueError(f"clips faltantes: {catalog.keys() - set(names)}; exportados: {names}")
        if not model.get("skins") or any(not clip.get("channels") for clip in clips):
            raise ValueError("GLB sin skin o con animaciones vacías")
        manifest = glb.with_suffix(".json")
        write_json(manifest, {"down_floor_offset": floor_offset, "clips": catalog})
        for artifact in (glb, manifest):
            os.replace(artifact, output / artifact.name)
    print(f"{args.character}: {len(clips)} clips, {len(model['skins'])} skins, fuente preservada")


if __name__ == "__main__":
    parser, argv = blender_args(__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "assets" / "models")
    export(parser.parse_args(argv))

"""Build a fresh editable rig, reference camera, lights and keyed actions."""
import json
import sys
from math import radians, sin, cos
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REFERENCE, SOURCES, SPEC, blender_args, read_json
from model import build
from poses import BONES, STANCE, actions, joint_positions, points


def make_rig():
    armature = bpy.data.armatures.new("Shared performer skeleton")
    rig = bpy.data.objects.new("Rig", armature)
    bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.show_in_front = True
    armature.display_type = "STICK"
    bpy.ops.object.mode_set(mode="EDIT")
    rest = joint_positions(STANCE)
    for name, (_, _, parent) in BONES.items():
        bone = armature.edit_bones.new(name)
        bone.head, bone.tail = points(rest, name)
        if parent:
            bone.parent = armature.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    return rig


def key_pose(rig, values, frame):
    joints = joint_positions(values)
    rests = joint_positions(STANCE)
    transforms = {}
    for name, (_, _, parent) in BONES.items():
        bone = rig.pose.bones[name]
        start, end = map(Vector, points(joints, name))
        rest_start, rest_end = map(Vector, points(rests, name))
        aim = end - start
        rest_aim = rest_end - rest_start
        rotation = rest_aim.rotation_difference(aim).to_matrix().to_4x4()
        rest_rotation = bone.bone.matrix_local.to_quaternion().to_matrix().to_4x4()
        # Keep sculpted volumes. A small longitudinal correction maintains
        # overlap at elbows and knees when a pose spreads or compresses.
        length_scale = aim.length / rest_aim.length if name not in ("head", "instrument") else 1
        matrix = Matrix.Translation(start) @ rotation @ rest_rotation @ Matrix.Diagonal((1, length_scale, 1, 1))
        transforms[name] = matrix
        parent_args = {}
        if parent:
            parent_args = {"parent_matrix": transforms[parent],
                           "parent_matrix_local": rig.data.bones[parent].matrix_local}
        basis = bone.bone.convert_local_to_pose(matrix, bone.bone.matrix_local, invert=True, **parent_args)
        bone.location, rotation_quaternion, bone.scale = basis.decompose()
        bone.rotation_mode = "QUATERNION"
        if frame > 1:
            rotation_quaternion.make_compatible(bone.rotation_quaternion)
        bone.rotation_quaternion = rotation_quaternion
        for channel in ("location", "rotation_quaternion", "scale"):
            bone.keyframe_insert(channel, frame=frame, group=name)


def add_actions(rig, character, complete):
    catalog = {}
    reference = read_json(REFERENCE)["anims"]
    scene = bpy.context.scene
    rig.animation_data_create()
    for name, frames in actions(character, complete).items():
        action = bpy.data.actions.new(name)
        action.use_fake_user = True
        rig.animation_data.action = action
        tick = 1
        loop = reference[name]["loop"]
        for duration, pose in frames:
            key_pose(rig, pose, tick)
            tick += duration
        if loop:
            key_pose(rig, frames[0][1], tick)
        else:
            key_pose(rig, frames[-1][1], tick - 1)
        action.use_cyclic = loop
        action.use_frame_range = True
        action.frame_start = 1
        action.frame_end = tick if loop else tick - 1
        catalog[name] = {"frames": len(frames), "durs": [duration for duration, _ in frames], "loop": loop}
    scene["sprite_catalog"] = json.dumps(catalog)
    rig.animation_data.action = bpy.data.actions["idle"]
    rig.animation_data.action_slot = rig.animation_data.action.slots[0]
    scene.frame_end = sum(catalog["idle"]["durs"])
    scene.frame_set(1)


def stage(settings):
    scene = bpy.context.scene
    width, height = settings["canvas"]
    ax, ay = settings["axis"]
    scale = settings["ortho_width"]
    angle = radians(settings["view_yaw_degrees"])
    direction = Vector((sin(angle), -cos(angle), 0))
    right = Vector((cos(angle), sin(angle), 0))
    center = ((.5 - ax / width) * scale * right
              + Vector((0, 0, (ay - height / 2) * scale / width)))
    camera = bpy.data.cameras.new("Calibrated sprite lens")
    camera.type = "ORTHO"
    camera.ortho_scale = scale
    obj = bpy.data.objects.new("Sprite Camera", camera)
    scene.collection.objects.link(obj)
    obj.location = center + direction * 9
    obj.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    scene.camera = obj
    scene["axis"] = [ax, ay]
    scene.world = bpy.data.worlds.new("Neutral studio")
    scene.world.color = (.21, .21, .21)
    for name, location, power, color, size in [
        ("Warm key", (3, -4, 6), 530, (1, .81, .65), 4.5),
        ("Cool fill", (-3, -3, 3), 290, (.63, .75, 1), 4),
        ("Stage rim", (-2, 3, 4.5), 590, (.68, .68, 1), 3),
    ]:
        light = bpy.data.lights.new(name, "AREA")
        light.energy, light.color, light.shape, light.size = power, color, "DISK", size
        lamp = bpy.data.objects.new(name, light)
        scene.collection.objects.link(lamp)
        lamp.location = location
        lamp.rotation_euler = (Vector((0, 0, 1.4)) - lamp.location).to_track_quat("-Z", "Y").to_euler()
    # CPU Cycles is available even on headless workstations without a GPU context.
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 12
    scene.cycles.seed = 19
    scene.cycles.use_animated_seed = False
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.render.use_persistent_data = True
    scene.render.fps = 60
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "AgX"


def generate(args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    settings = read_json(SPEC)
    character = settings["characters"][args.character]
    rig = make_rig()
    build(rig, character["palette"], args.character == "frontman")
    stage(settings["camera"])
    add_actions(rig, args.character, args.full)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
    SOURCES.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCES / f"{args.character}.blend"), compress=True)


if __name__ == "__main__":
    parser, argv = blender_args(__doc__)
    parser.add_argument("--full", action="store_true", help="Crear todas las acciones, además del corte inicial")
    generate(parser.parse_args(argv))

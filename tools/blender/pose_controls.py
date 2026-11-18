"""Optional manual IK for the puppet. Baked actions keep using the deform bones."""
from math import pi

import bpy
from mathutils import Vector

from poses import STANCE, joint_positions


IK_PROPERTIES = ("IK_hands", "IK_feet")


def calibrate_pole(bone, constraint, pivot):
    # The solver can respond nonlinearly when the authored pose scales a limb.
    def error(angle):
        angle = (angle + pi) % (2 * pi) - pi
        constraint.pole_angle = angle
        bpy.context.view_layer.update()
        return (bone.head - pivot).length_squared

    step = pi / 8
    angle = min((index * step for index in range(-8, 8)), key=error)
    for _ in range(6):
        step *= .5
        angle = min((angle - step, angle, angle + step), key=error)
    constraint.pole_angle = (angle + pi) % (2 * pi) - pi


def add_ik(rig):
    rest = joint_positions(STANCE)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    chains = []
    for kind, joints, end_bone in (
        ("hands", ("shoulder", "elbow", "hand"), "forearm"),
        ("feet", ("hips", "knee", "foot"), "shin"),
    ):
        for side in ("near", "far"):
            start, pivot, end = (Vector(rest[f"{joint}_{side}"]) for joint in joints)
            direction = (end - start).normalized()
            bend = (pivot - start) - direction * (pivot - start).dot(direction)
            pole = pivot + bend.normalized() * .38
            target_name = f"IK_{joints[-1]}_{side}"
            pole_name = f"Pole_{joints[1]}_{side}"
            for name, point in ((target_name, end), (pole_name, pole)):
                anchor = rig.data.edit_bones.new(name)
                anchor.head = point
                anchor.tail = point + Vector((0, 0, .12))
                anchor.use_deform = False
            chains.append((kind, f"{end_bone}_{side}", target_name, pole_name))
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    collection = rig.data.collections.new("Manual IK")
    for property_name in IK_PROPERTIES:
        rig[property_name] = 0.0
        rig.id_properties_ui(property_name).update(
            min=0.0, max=1.0,
            description="En 1, mover los controles IK y los polos. En 0, usar las acciones del juego.")
    for kind, owner, target, pole in chains:
        for name, palette in ((target, "THEME04"), (pole, "THEME03")):
            bone = rig.data.bones[name]
            for group in list(bone.collections):
                group.unassign(bone)
            collection.assign(bone)
            bone.color.palette = palette

        constraint = rig.pose.bones[owner].constraints.new("IK")
        constraint.name = "Manual pose · " + kind
        constraint.target = constraint.pole_target = rig
        constraint.subtarget, constraint.pole_subtarget = target, pole
        constraint.chain_count = 2
        constraint.use_stretch = False

        constraint.influence = 0
        driver = constraint.driver_add("influence").driver
        driver.type = "AVERAGE"
        slider = driver.variables.new()
        slider.name = "ik"
        slider.type = "SINGLE_PROP"
        slider.targets[0].id = rig
        slider.targets[0].data_path = f'["IK_{kind}"]'
    bpy.context.view_layer.update()


def align_ik_to_idle(rig):
    """Start the manual handles at the displayed stance."""
    chains = []
    for bone in rig.pose.bones:
        for constraint in bone.constraints:
            if constraint.type != "IK":
                continue
            start, pivot, end = bone.parent.head, bone.head, bone.tail
            chains.append((bone, constraint, pivot.copy()))
            axis = (end - start).normalized()
            bend = (pivot - start) - axis * (pivot - start).dot(axis)
            for name, position in (
                (constraint.subtarget, end),
                (constraint.pole_subtarget, pivot + bend.normalized() * .38),
            ):
                handle = rig.pose.bones[name]
                handle.location = handle.bone.matrix_local.inverted() @ position
    for name in IK_PROPERTIES:
        rig[name] = 1.0
    rig.update_tag(refresh={"OBJECT"})
    bpy.context.view_layer.update()
    for bone, constraint, pivot in chains:
        calibrate_pole(bone, constraint, pivot)
    for name in IK_PROPERTIES:
        rig[name] = 0.0
    rig.update_tag(refresh={"OBJECT"})
    bpy.context.view_layer.update()


def pose_view(area):
    space = area.spaces.active
    space.region_3d.view_perspective = "PERSP"
    space.region_3d.view_rotation = Vector((4.0, -5.7, 1.25)).to_track_quat("Z", "Y")
    space.region_3d.view_location = (0, 0, 1.44)
    space.region_3d.view_distance = 4.5
    space.overlay.show_extras = False
    space.overlay.show_floor = False
    space.overlay.show_axis_x = space.overlay.show_axis_y = False
    space.overlay.show_relationship_lines = False
    space.shading.color_type = "MATERIAL"
    space.shading.show_specular_highlight = False
    space.shading.show_cavity = True
    space.shading.cavity_type = "WORLD"
    space.shading.cavity_ridge_factor = .35
    space.shading.cavity_valley_factor = .55

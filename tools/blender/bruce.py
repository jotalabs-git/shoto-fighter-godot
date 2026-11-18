"""An original clay Bruce Dickinson with layered hair and a Union Jack sleeve patch."""
from math import cos, radians, sin

import bpy
from mathutils import Matrix, Vector

from frontman import combat_boot
from garment_surface import GarmentSurface
from model import Sculpt, angled_face, blend, clay_line, merge_clay
from poses import STANCE, joint_positions

HEAD = "head"
TORSO = "pelvis"


def face(s):
    l = s.lump
    head = merge_clay(s, "Bruce · sculpted head", [
        l("Sculpted forehead", HEAD, "skin", (.008, 0, 2.553), (.277, .254, .322), 9),
        l("Broad cheekbones", HEAD, "skin", (.092, 0, 2.418), (.233, .281, .217), 3),
        l("Angular jaw", HEAD, "skin", (.094, 0, 2.283), (.238, .203, .174), -9),
        l("Heavy chin", HEAD, "skin", (.209, 0, 2.204), (.150, .148, .108), -8),
        l("Upper lip plane", HEAD, "skin", (.271, -.005, 2.323), (.090, .141, .074), -7),
        l("Long nose bridge", HEAD, "skin", (.297, -.008, 2.483), (.091, .064, .137), 14),
        l("Nose tip", HEAD, "skin", (.369, -.014, 2.421), (.093, .087, .064), 9),
        *[l("Sloping cheek plane", HEAD, "skin", (.151, side * .177, 2.421),
             (.179, .100, .094), -18 if side == -1 else -11) for side in (-1, 1)],
        *[l("Pressed ear", HEAD, "skin", (-.095, side * .265, 2.398), (.089, .070, .105), -17)
          for side in (-1, 1)],
    ], "skin", HEAD, voxel=.009)
    bpy.context.view_layer.update()
    local = head.matrix_world.inverted()
    inward = local.to_3x3() @ Vector((-1, 0, 0))

    def on_face(points, margin):
        result = []
        for y, z, radius in points:
            hit, co, _, _ = head.ray_cast(local @ Vector((1, y, z)), inward)
            if not hit:
                raise ValueError(f"Bruce: no head surface at {y}, {z}")
            result.append(((head.matrix_world @ co).x + margin, y, z, radius))
        return result

    l("Neck", HEAD, "skin", (.033, 0, 2.024), (.158, .172, .177), -6)
    clay_line(s, "Asymmetric smirk", HEAD, "mouth", on_face([
        (-.145, 2.324, .27), (-.077, 2.302, .84), (0, 2.294, 1),
        (.061, 2.287, .80), (.117, 2.296, .27),
    ], .003), .014)
    clay_line(s, "Pinched lower lip", HEAD, "lip", on_face([
        (-.116, 2.301, .24), (-.061, 2.282, .70), (-.014, 2.269, 1),
        (.047, 2.264, .87), (.095, 2.275, .26),
    ], .003), .019)
    for side in (-1, 1):
        yaw = side * 26
        normal = Vector((cos(radians(yaw)), sin(radians(yaw)), 0))
        raised = .016 if side < 0 else -.013
        eye = Vector((.281, side * .150, 2.512 + raised * .42))
        angled_face(s, "Sculpted eyelid base", "skin", eye - normal * .030, (.055, .112, .064), yaw)
        angled_face(s, "Shaded eye", "lip", eye + normal * .007, (.030, .090, .043), yaw)
        angled_face(s, "Eye white", "white", eye + normal * .017, (.030, .083, .037), yaw)
        iris = eye + normal * .046 + Vector((0, -side * .015, -.002))
        angled_face(s, "Hazel iris", "iris", iris, (.012, .034, .034), yaw)
        angled_face(s, "Pupil", "dark", iris + normal * .010, (.008, .021, .023), yaw)
        l("Catchlight", HEAD, "white", iris + normal * .016 + Vector((0, -.008, .010)), (.007, .007, .007))
        clay_line(s, "Hand-rolled upper eyelid", HEAD, "skin", [
            (.316, side * .073, 2.528, .26), (.333, side * .118, 2.549 + raised, .90),
            (.308, side * .169, 2.554 + raised, 1), (.271, side * .224, 2.535, .32),
        ], .023)
        clay_line(s, "Press-shaped chestnut brow", HEAD, "brow", on_face([
            (side * .058, 2.565 + raised * .4, .69), (side * .113, 2.592 + raised, 1),
            (side * .179, 2.594 + raised, .96), (side * .231, 2.570 + raised * .4, .43),
        ], .014), .033)
        clay_line(s, "Pressed cheek crease", HEAD, "lip", on_face([
            (side * .106, 2.390, .20), (side * .128, 2.368, .49), (side * .155, 2.347, .11),
        ], .000), .010)
        l("Nostril", HEAD, "mouth", (.408, side * .056, 2.381), (.026, .022, .011), 11)


def hair(s):
    locks = [
        s.lump("Crown volume", HEAD, "hair", (-.154, .016, 2.706), (.292, .266, .224), 12),
        s.lump("Hair at the back", HEAD, "hair", (-.244, .01, 2.446), (.207, .249, .341), 15),
    ]
    for side in (-1, 1):
        locks.append(clay_line(s, "Hair over the crown", HEAD, "hair", [
            (.101, side * .035, 2.875, .52), (.023, side * .105, 2.908, .87),
            (-.126, side * .177, 2.865, 1), (-.263, side * .206, 2.760, .85),
            (-.336, side * .213, 2.595, .57),
        ], .103))
        for trail in range(2):
            shift = .055 * trail
            locks.append(clay_line(s, "Shoulder-length feathered layer", HEAD, "hair", [
                (.110 - shift, side * .062, 2.864, .71), (.141 - shift, side * .182, 2.773, 1),
                (.033 - shift * 1.7, side * .263, 2.611, 1),
                (-.079 - shift * 2, side * .289, 2.443, .95),
                (-.139 - shift, side * .303, 2.235, .87),
                (-.053 - shift * 2, side * .239, 2.022 + side * .030, .69),
                (.062 - shift * 2, side * .180, 1.918 + side * .035, .18),
            ], .100))
    merge_clay(s, "Feathered chestnut hair", locks, "hair", HEAD, voxel=.010)
    for side in (-1, 1):
        clay_line(s, "Swept fringe", HEAD, "copper", [
            (.129, side * .028, 2.874, .23), (.229, side * .103, 2.798, .82),
            (.248, side * .187, 2.668, 1), (.168, side * .254, 2.609, .74),
            (.081, side * .284, 2.533, .20),
        ], .059)
        for j in range(3):
            off = j * .043
            clay_line(s, "Feathered hair ridge", HEAD, "copper" if j == 0 else "hair_ridge", [
                (.202 - off, side * (.161 + off * .4), 2.818 - off * .08, .22),
                (.159 - off * 1.7, side * (.322 - off * .13), 2.684, .84),
                (.015 - off * 2.1, side * (.365 - off * .1), 2.489, 1),
                (-.082 - off * 2, side * (.391 - off * .24), 2.282 + off * .34, .80),
                (-.009 - off * 2.2, side * (.321 - off * .33), 2.046 + off, .52),
                (.070 - off * 2, side * (.239 - off * .2), 1.941 + off, .13),
            ], .021)


def flag(s, surface, side, center, weights):
    """Three stitched colors and the offset Irish saltire on the blue patch."""
    def polygon(name, color, coords, layer):
        outline = [(center.x - side * x * .245, center.z + z * .132) for x, z in coords]
        surface.applique(s, "Union Jack · " + name, color, outline, layer * .0015, weights=weights)

    rectangle = [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]
    polygon("embroidered edge", "rubber", [(x * 1.10, z * 1.17) for x, z in rectangle], 1)
    polygon("navy field", "flag_blue", rectangle, 2)
    for sx in (-1, 1):
        for sz in (-1, 1):
            polygon("white saltire", "flag_white", [
                (0, 0), (sx * .40, sz * .50), (sx * .50, sz * .50),
                (sx * .50, sz * .34), (sx * .09, 0),
            ], 3)
            offset = .035 if sx * sz > 0 else .096
            polygon("red saltire", "flag_red", [
                (sx * offset, 0), (sx * .50, sz * (.49 - offset)),
                (sx * .50, sz * (.43 - offset)), (sx * (offset + .070), 0),
            ], 4)
    for color, half in (("flag_white", .150), ("flag_red", .087)):
        lift = 5 if color == "flag_white" else 6
        polygon("horizontal cross", color, [(x, z * half * 2) for x, z in rectangle], lift)
        polygon("vertical cross", color, [(x * half * 1.42, z) for x, z in rectangle], lift + .15)


def jacket(s):
    l = s.lump
    body = merge_clay(s, "Bruce · leather jacket torso", [
        l("Jacket shoulders", TORSO, "leather", (-.035, 0, 1.797), (.252, .370, .232), -7),
        l("Jacket body", TORSO, "leather", (-.043, 0, 1.595), (.231, .318, .335), -6),
        l("Jacket waist", TORSO, "leather", (-.059, 0, 1.351), (.215, .299, .166), -7),
    ], "leather", TORSO, voxel=.012)
    surface = GarmentSurface(body, 0, 1)

    def seam(name, color, anchors, radius):
        clay_line(s, name, TORSO, color, [(*surface.point(y, z), width) for y, z, width in anchors], radius)

    surface.applique(s, "Faded charcoal tee", "tee", [
        (-.120, 1.970), (0, 1.917), (.120, 1.970), (.152, 1.850), (.101, 1.562),
        (-.098, 1.562), (-.153, 1.850),
    ], .002, bone=TORSO)
    for side in (-1, 1):
        outline = [(side * y, z) for y, z in [
            (.121, 1.958), (.231, 1.912), (.234, 1.746), (.090, 1.575), (.146, 1.756), (.109, 1.821),
        ]]
        surface.applique(s, "Folded biker lapel", "lapel", outline, .0045, bone=TORSO)
        l("Steel collar snap", TORSO, "metal", surface.point(side * .199, 1.884, .005), (.016, .023, .023))
        l("Steel lapel snap", TORSO, "metal", surface.point(side * .170, 1.753, .005), (.014, .019, .019))
        seam("Raised seam at jacket waist", "lapel", [
            (side * .232, 1.426, .50), (side * .182, 1.431, .85),
            (side * .124, 1.435, 1), (side * .074, 1.437, .87),
        ], .013)
    seam("Angled steel zipper", "metal", [
        (.115, 1.357, .43), (.122, 1.429, .74), (.143, 1.522, .76),
        (.162, 1.604, .78), (.183, 1.700, .65),
    ], .009)
    l("Zipper pull", TORSO, "metal", surface.point(.151, 1.548, .004), (.012, .015, .026), -11)
    l("Jacket belt buckle", TORSO, "metal", surface.point(-.106, 1.368, .004), (.021, .042, .027))


def limbs(s):
    rest = joint_positions(STANCE)
    l, t = s.lump, s.tube
    denim = [l("Denim waist", TORSO, "denim", (-.052, 0, 1.244), (.219, .302, .177))]
    for side, sign in (("near", -1), ("far", 1)):
        shoulder, elbow, wrist = (Vector(rest[f"{j}_{side}"]) for j in ("shoulder", "elbow", "hand"))
        hip, knee, foot = (Vector(rest[f"{j}_{side}"]) for j in ("hips", "knee", "foot"))
        upper, lower, fist, thigh, shin, boot = (f"{j}_{side}" for j in ("bicep", "forearm", "fist", "thigh", "shin", "boot"))
        upper_axis = (elbow - shoulder).normalized()
        bend = (upper_axis + (wrist - elbow).normalized()).normalized()

        def sleeve_weights(v):
            arm = blend((v - shoulder).dot(upper_axis), -.110, .120)
            forearm = blend((v - elbow).dot(bend), -.106, .090)
            return {TORSO: 1 - arm, upper: arm * (1 - forearm), lower: arm * forearm}

        sleeve = merge_clay(s, f"Articulated leather sleeve · {side}", [
            l("Rounded shoulder", upper, "leather", shoulder, (.156, .158, .165)),
            t("Leather upper arm", upper, "leather", shoulder, elbow, (.129, .133), .094),
            l("Elbow fold volume", lower, "leather", elbow, (.110, .124, .117)),
            t("Leather forearm", lower, "leather", elbow, wrist, (.111, .113), .032),
        ], "leather", weights=sleeve_weights, voxel=.013)
        flag(s, GarmentSurface(sleeve, 1, sign), sign, shoulder.lerp(elbow, .34), sleeve_weights)
        cuff = wrist.lerp(elbow, .1)
        t("Rolled leather cuff", lower, "lapel", cuff, cuff.lerp(elbow, .21), (.122, .117), .020)
        x, y, z = wrist
        fingers = []
        for dy, reach in ((-.076, .153), (-.028, .183), (.023, .181), (.073, .144)):
            fingers.append(clay_line(s, "Clay knuckle", fist, "skin", [
                (x + .063, y + dy * .74, z + .034, 1),
                (x + reach, y + dy, z + .044, .96),
                (x + reach + .008, y + dy, z - .018, .86),
                (x + reach - .026, y + dy * .93, z - .035, .69),
            ], .035))
        merge_clay(s, f"Bare fist · {side}", [
            l("Palm", fist, "skin", (x + .045, y, z), (.112, .101, .073)),
            clay_line(s, "Thumb across curled fingers", fist, "skin", [
                (x + .007, y - sign * .066, z + .024, 1),
                (x + .087, y - sign * .084, z - .005, 1),
                (x + .131, y - sign * .031, z - .050, .64),
            ], .044),
            *fingers,
        ], "skin", fist, voxel=.007)
        denim.extend([
            t("Jeans thigh", thigh, "denim", hip, knee, (.164, .155), .124),
            l("Jeans knee", shin, "denim", knee, (.141, .140, .138)),
            t("Jeans shin", shin, "denim", knee, foot.lerp(knee, .25), (.115, .140), .083),
        ])
        clay_line(s, "Contrast denim seam", thigh, "stitch", [
            (*tuple(hip + Vector((-.014, sign * .143, -.078))), .45),
            (*tuple(hip.lerp(knee, .54) + Vector((-.020, sign * .145, 0))), .76),
            (*tuple(knee + Vector((-.015, sign * .131, .040))), .24),
        ], .009)
        combat_boot(s, boot, side, foot)

    def denim_weights(v):
        leg = 1 - blend(v.z, 1.02, 1.32)
        knee = 1 - blend(v.z, .59, .82)
        far = blend(v.y, -.088, .088)
        return {TORSO: 1 - leg, "thigh_near": leg * (1 - far) * (1 - knee),
                "thigh_far": leg * far * (1 - knee), "shin_near": leg * (1 - far) * knee,
                "shin_far": leg * far * knee}

    merge_clay(s, "Weighted blue jeans", denim, "denim", weights=denim_weights, voxel=.014)


def build_bruce(rig, colors):
    s = Sculpt(rig, colors)
    for name, roughness in {"leather": .46, "lapel": .56, "metal": .36, "hair": .59}.items():
        s.colors[name].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    jacket(s)
    limbs(s)
    face(s)
    hair(s)
    # Keep the neck at the original joint and enlarge the sculpt above it.
    pivot = Vector((.038, 0, 2.099))
    scale = Matrix.Translation(pivot) @ Matrix.Diagonal((1.14, 1.20, 1.13, 1)) @ Matrix.Translation(-pivot)
    for obj in rig.children:
        if obj.parent_bone == HEAD and obj.name != "Neck":
            obj.matrix_world = scale @ obj.matrix_world
    for side in ("near", "far"):
        pivot = Vector(STANCE[f"hand_{side}"])
        scale = Matrix.Translation(pivot) @ Matrix.Diagonal((1.075, 1.13, 1.12, 1)) @ Matrix.Translation(-pivot)
        for obj in rig.children:
            if obj.parent_bone == f"fist_{side}":
                obj.matrix_world = scale @ obj.matrix_world
    for material, roughness in (("skin", .80), ("brow", .77), ("hair", .70), ("copper", .68)):
        nodes = s.colors[material].node_tree.nodes
        nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
        bump = next(node for node in nodes if node.type == "BUMP")
        bump.inputs["Strength"].default_value = .14
        bump.inputs["Distance"].default_value = .025

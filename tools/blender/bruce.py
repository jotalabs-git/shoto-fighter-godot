"""An original clay Bruce Dickinson with layered hair and a Union Jack sleeve patch."""
from math import cos, radians, sin

import bpy
from mathutils import Vector

from frontman import combat_boot
from model import Sculpt, angled_face, blend, clay_line, clay_plate, merge_clay
from poses import STANCE, joint_positions

HEAD = "head"
TORSO = "pelvis"


def face(s):
    l = s.lump
    head = merge_clay(s, "Bruce · sculpted head", [
        l("Rounded crown", HEAD, "skin", (-.043, 0, 2.543), (.304, .267, .343), 11),
        l("Broad cheekbones", HEAD, "skin", (.104, 0, 2.404), (.255, .258, .234), 7),
        l("Tapered jaw", HEAD, "skin", (.091, 0, 2.291), (.233, .216, .192), -7),
        l("Rounded chin", HEAD, "skin", (.193, 0, 2.205), (.157, .166, .120), -5),
        l("Upper muzzle", HEAD, "skin", (.262, 0, 2.329), (.108, .158, .087)),
        l("Straight nose bridge", HEAD, "skin", (.300, 0, 2.479), (.090, .068, .111), 18),
        l("Nose tip", HEAD, "skin", (.364, -.006, 2.417), (.106, .089, .068), 4),
        *[l("Cheek", HEAD, "skin", (.160, side * .168, 2.400), (.163, .105, .105), 9)
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
    clay_line(s, "Closed mouth", HEAD, "mouth", on_face([
        (-.117, 2.303, .36), (-.059, 2.293, .80), (0, 2.296, 1),
        (.056, 2.291, .89), (.115, 2.294, .30),
    ], .002), .012)
    clay_line(s, "Lower lip", HEAD, "lip", on_face([
        (-.084, 2.279, .42), (-.019, 2.273, 1), (.039, 2.273, .86), (.088, 2.279, .28),
    ], .002), .016)
    for side in (-1, 1):
        yaw = side * 26
        normal = Vector((cos(radians(yaw)), sin(radians(yaw)), 0))
        eye = Vector((.283, side * .148, 2.510))
        angled_face(s, "Creased eye socket", "skin", eye - normal * .024, (.060, .108, .063), yaw)
        angled_face(s, "Eye white", "white", eye + normal * .013, (.031, .084, .034), yaw)
        iris = eye + normal * .043 + Vector((0, -side * .012, .002))
        angled_face(s, "Hazel iris", "iris", iris, (.014, .037, .037), yaw)
        angled_face(s, "Pupil", "dark", iris + normal * .011, (.009, .022, .023), yaw)
        l("Catchlight", HEAD, "white", iris + normal * .020 + Vector((0, -.007, .010)), (.007, .007, .007))
        clay_line(s, "Upper eyelid", HEAD, "skin", [
            (.312, side * .073, 2.521, .30), (.329, side * .126, 2.544, 1),
            (.307, side * .176, 2.549, .90), (.271, side * .221, 2.537, .32),
        ], .019)
        clay_line(s, "Chestnut brow", HEAD, "brow", on_face([
            (side * .067, 2.565, .56), (side * .126, 2.588, 1),
            (side * .185, 2.587, .74), (side * .236, 2.562, .26),
        ], .012), .024)
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


def flag(s, bone, side, center):
    """Three stitched colors and the offset Irish saltire on the blue patch."""
    origin = Vector(center)
    right, up, normal = Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, side, 0))

    def polygon(name, color, coords, layer, thickness=.006):
        points = [origin + right * (x * .30) + up * (y * .161) + normal * (layer * .75) for x, y in coords]
        clay_plate(s, name, bone, color, points, thickness * normal, thickness * .27)

    rectangle = [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]
    polygon("Union Jack · leather border", "rubber", [(x * 1.13, z * 1.20) for x, z in rectangle], -.004, .018)
    polygon("Union Jack · navy field", "flag_blue", rectangle, .006)
    for sx in (-1, 1):
        for sz in (-1, 1):
            polygon("Union Jack · white saltire", "flag_white", [
                (0, 0), (sx * .40, sz * .50), (sx * .50, sz * .50),
                (sx * .50, sz * .34), (sx * .09, 0),
            ], .013)
            offset = .035 if sx * sz > 0 else .096
            polygon("Union Jack · red saltire", "flag_red", [
                (sx * offset, 0), (sx * .50, sz * (.49 - offset)),
                (sx * .50, sz * (.43 - offset)), (sx * (offset + .070), 0),
            ], .018)
    for color, half in (("flag_white", .150), ("flag_red", .087)):
        lift = .023 if color == "flag_white" else .030
        polygon("Union Jack · horizontal cross", color, [(x, z * half * 2) for x, z in rectangle], lift)
        polygon("Union Jack · vertical cross", color, [(x * half * 1.42, z) for x, z in rectangle], lift + .0006)


def jacket(s):
    l = s.lump
    merge_clay(s, "Bruce · leather jacket torso", [
        l("Jacket shoulders", TORSO, "leather", (-.035, 0, 1.797), (.252, .370, .232), -7),
        l("Jacket body", TORSO, "leather", (-.043, 0, 1.595), (.231, .318, .335), -6),
        l("Jacket waist", TORSO, "leather", (-.059, 0, 1.351), (.215, .299, .166), -7),
    ], "leather", TORSO, voxel=.012)
    l("Faded charcoal tee", TORSO, "tee", (.166, 0, 1.708), (.085, .198, .253), -6)
    for side in (-1, 1):
        clay_plate(s, "Folded biker lapel", TORSO, "lapel", [(x, side * y, z) for x, y, z in [
            (.149, .121, 1.979), (.190, .261, 1.911), (.220, .247, 1.720),
            (.252, .096, 1.572), (.249, .145, 1.750), (.235, .108, 1.817),
        ]], (.047, 0, 0), .025)
        l("Steel collar snap", TORSO, "metal", (.207, side * .223, 1.884), (.023, .032, .030))
        l("Steel lapel snap", TORSO, "metal", (.253, side * .143, 1.732), (.019, .024, .024))
        clay_line(s, "Raised seam at jacket waist", TORSO, "lapel", [
            (.197, side * .253, 1.426, .50), (.223, side * .182, 1.431, .95),
            (.236, side * .074, 1.437, 1),
        ], .018)
    clay_line(s, "Angled steel zipper", TORSO, "metal", [
        (.229, .122, 1.357, .43), (.242, .143, 1.537, .75), (.244, .183, 1.704, .84),
    ], .010)
    l("Zipper pull", TORSO, "metal", (.256, .173, 1.559), (.011, .026, .039), -11)
    l("Jacket belt buckle", TORSO, "metal", (.216, -.106, 1.368), (.037, .057, .036))


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

        merge_clay(s, f"Articulated leather sleeve · {side}", [
            l("Rounded shoulder", upper, "leather", shoulder, (.156, .158, .165)),
            t("Leather upper arm", upper, "leather", shoulder, elbow, (.129, .133), .094),
            l("Elbow fold volume", lower, "leather", elbow, (.110, .124, .117)),
            t("Leather forearm", lower, "leather", elbow, wrist, (.111, .113), .032),
        ], "leather", weights=sleeve_weights, voxel=.013)
        point = shoulder.lerp(elbow, .34)
        flag(s, upper, sign, point + Vector((0, sign * .142, .006)))
        cuff = wrist.lerp(elbow, .1)
        t("Rolled leather cuff", lower, "lapel", cuff, cuff.lerp(elbow, .21), (.122, .117), .020)
        x, y, z = wrist
        merge_clay(s, f"Bare fist · {side}", [
            l("Palm", fist, "skin", (x + .052, y, z), (.130, .110, .091)),
            l("Folded knuckles", fist, "skin", (x + .131, y, z + .016), (.101, .115, .088), 13),
            l("Thumb", fist, "skin", (x + .067, y - sign * .077, z + .052), (.071, .061, .050), -17),
        ], "skin", fist, voxel=.009)
        for dy in (-.048, .007, .059):
            l("Fist fold", fist, "lip", (x + .207, y + dy, z + .013), (.011, .008, .013))
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

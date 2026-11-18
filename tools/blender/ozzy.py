"""A full-body clay rocker with centre-parted hair, round shades and silver rings."""
from math import cos, radians, sin

import bpy
from mathutils import Vector

from frontman import combat_boot
from model import Sculpt, angled_face, blend, clay_line, clay_plate, merge_clay
from poses import STANCE, joint_positions


HEAD = "head"
TORSO = "pelvis"


def metal_loop(s, name, bone, center, normal, radius, width, color="metal"):
    bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=8, location=center,
                                    major_radius=radius, minor_radius=width)
    obj = bpy.context.object
    obj.rotation_euler = Vector(normal).to_track_quat("Z", "Y").to_euler()
    bpy.context.view_layer.update()
    return s.bind(obj, name, bone, color)


def sculpt_head(s):
    l = s.lump
    head = merge_clay(s, "Ozzy · sculpted head", [
        l("Cranium", HEAD, "skin", (-.032, 0, 2.527), (.301, .261, .370), 8),
        l("Long face", HEAD, "skin", (.127, 0, 2.383), (.239, .233, .329), 4),
        l("Round chin", HEAD, "skin", (.213, 0, 2.194), (.174, .165, .139), 5),
        l("Nose bridge", HEAD, "skin", (.303, .006, 2.488), (.095, .065, .128), 21),
        l("Nose tip", HEAD, "skin", (.389, -.008, 2.411), (.116, .093, .073), 9),
        *[l("Laughing cheek", HEAD, "skin", (.224, side * .149, 2.397), (.152, .103, .108), 12)
          for side in (-1, 1)],
    ], "skin", HEAD, voxel=.009)
    cutter = l("Carve grin", HEAD, "skin", (.383, 0, 2.277), (.118, .159, .084), 11)
    bpy.context.view_layer.objects.active = head
    carve = head.modifiers.new("Sculpted grin recess", "BOOLEAN")
    carve.operation, carve.object = "DIFFERENCE", cutter
    bpy.ops.object.modifier_apply(modifier=carve.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    l("Shadow in smile", HEAD, "mouth", (.278, 0, 2.289), (.038, .133, .058), 8)
    # Rounded rectangular crowns sit behind the lip on the upper dental arch.
    for side in (-1, 1):
        for y, x, z, width, height in [
            (.022, .326, 2.313, .021, .024),
            (.062, .319, 2.317, .018, .021),
            (.096, .302, 2.321, .016, .017),
            (.122, .284, 2.317, .013, .013),
        ]:
            clay_plate(s, "Ivory upper tooth", HEAD, "enamel", [
                (x - dy * .32, side * (y + dy), z + dz)
                for dy, dz in [(-width, height), (width, height),
                               (width * .85, -height), (-width * .87, -height)]
            ], (.041, 0, 0), .007)
    l("Tongue in recessed mouth", HEAD, "lip", (.291, 0, 2.254), (.030, .078, .016), 7)
    clay_line(s, "Lower lip", HEAD, "lip", [
        (.276, -.116, 2.289, .32), (.310, -.076, 2.243, .70),
        (.336, 0, 2.232, .94), (.310, .076, 2.243, .70), (.276, .116, 2.289, .32),
    ], .016)

    for side in (-1, 1):
        yaw = side * 20
        center = Vector((.316, side * .151, 2.526))
        normal = Vector((cos(radians(yaw)), sin(radians(yaw)), 0))
        angled_face(s, "Smoked violet lens", "lens", center, (.027, .105, .105), yaw)
        metal_loop(s, "Round spectacle rim", HEAD, center, normal, .110, .008)
        clay_line(s, "Spectacle temple", HEAD, "frame", [
            (.29, side * .251, 2.539, 1), (.10, side * .275, 2.546, .94),
            (-.18, side * .295, 2.511, .64),
        ], .012)
        l("Nose shadow", HEAD, "mouth", (.436, side * .050, 2.374), (.021, .022, .010), 13)
        clay_line(s, "Cheek crease", HEAD, "rose", [
            (.337, side * .123, 2.379, .14), (.329, side * .170, 2.337, .69),
            (.291, side * .174, 2.296, .38),
        ], .012)
    clay_line(s, "Silver spectacles bridge", HEAD, "metal", [
        (.315, -.046, 2.527, .78), (.359, 0, 2.550, 1), (.315, .046, 2.527, .78),
    ], .010)

    hair = [
        l("Crown", HEAD, "hair", (-.169, 0, 2.694), (.306, .264, .233), 8),
        l("Nape", HEAD, "hair", (-.236, 0, 2.399), (.192, .241, .289), 12),
    ]
    for side in (-1, 1):
        wave = [
            (.120, side * .044, 2.886, .58), (.142, side * .195, 2.796, 1),
            (.026, side * .274, 2.643, 1.08), (-.079, side * .285, 2.466, 1.06),
            (-.137, side * .305, 2.267, .98), (-.073, side * .306, 2.115, .87),
            (-.169, side * .344, 1.995 + side * .035, .30),
        ]
        hair.extend([
            clay_line(s, "Wavy face-framing lock", HEAD, "hair", wave, .111),
            clay_line(s, "Parted crown lock", HEAD, "hair", [
                (.145, side * .040, 2.858, .62), (.055, side * .117, 2.915, .93),
                (-.135, side * .164, 2.880, 1.13), (-.257, side * .222, 2.752, .97),
                (-.313, side * .223, 2.585, .82),
            ], .104),
            clay_line(s, "Long back lock", HEAD, "hair", [
                (-.290, side * .117, 2.669, 1), (-.310, side * .205, 2.465, 1.12),
                (-.291, side * .241, 2.260, 1.03), (-.272, side * .262, 2.050, .70),
                (-.204, side * .219, 1.937 + side * .031, .22),
            ], .127),
        ])
    merge_clay(s, "Centre-parted shoulder-length hair", hair, "hair", HEAD, voxel=.010)
    for side in (-1, 1):
        for index in range(3):
            shift = .037 * index
            clay_line(s, "Hand-sculpted waves", HEAD, "hair_ridge", [
                (.145 - shift, side * (.097 + shift), 2.913 - shift * .36, .22),
                (.162 - shift, side * (.220 + shift), 2.816 - shift, .68),
                (.009 - shift * 1.68, side * (.380 - shift * .2), 2.633, .9),
                (-.097 - shift * 1.6, side * (.391 - shift * .13), 2.441, .8),
                (-.106 - shift * 1.3, side * (.400 - shift * .18), 2.247, .9),
                (-.126 - shift, side * (.392 - shift * .43), 2.092 + shift * .53, .66),
                (-.171 - shift * .62, side * (.351 - shift * .30), 2.008 + side * .034, .16),
            ], .015)
        clay_line(s, "Crown comb line", HEAD, "hair_ridge", [
            (.150, side * .061, 2.911, .20), (.041, side * .153, 3.006, .80),
            (-.098, side * .193, 2.969, .80), (-.236, side * .246, 2.859, .55),
        ], .013)


def coat_and_jewelry(s):
    l = s.lump
    merge_clay(s, "Ozzy · velvet coat torso", [
        l("Coat shoulders", TORSO, "coat", (-.036, 0, 1.790), (.262, .376, .253), -8),
        l("Coat body", TORSO, "coat", (-.062, 0, 1.535), (.228, .316, .344), -4),
        l("Coat waist", TORSO, "coat", (-.069, 0, 1.284), (.222, .310, .188), -4),
    ], "coat", TORSO, voxel=.014)
    l("Neck", HEAD, "skin", (.048, 0, 2.037), (.143, .153, .167), -9)
    l("Oxblood waistcoat", TORSO, "vest", (.159, 0, 1.550), (.090, .204, .328), -7)
    for side in (-1, 1):
        clay_plate(s, "Satin collar lapel", TORSO, "lapel", [(x, side * y, z) for x, y, z in [
            (.193, .122, 1.964), (.207, .234, 1.874), (.220, .247, 1.689),
            (.245, .172, 1.712), (.243, .087, 1.516), (.246, .112, 1.738),
        ]], (.030, 0, 0), .017)
        for index in range(3):
            angle = -.05 + index * .041
            l("Coat rivet", TORSO, "frame", (.196, side * (.26 + angle), 1.777 + index * .023),
              (.024, .017, .017))
    for index in range(3):
        l("Waistcoat button", TORSO, "frame", (.249, 0, 1.366 + index * .074), (.018, .018, .018))
    for length, color in ((.31, "frame"), (.50, "metal")):
        clay_line(s, "Silver necklace", TORSO, color, [
            (.161, -.136, 1.960, .68), (.258, -.139, 1.903, .92),
            (.269, -.081, 1.953 - length * .75, 1), (.279, 0, 1.953 - length, 1),
            (.269, .081, 1.953 - length * .75, 1), (.258, .139, 1.903, .92),
            (.161, .136, 1.960, .68),
        ], .008)
    metal_loop(s, "Round silver pendant", TORSO, (.278, -.006, 1.612), (1, 0, 0), .046, .010)
    s.tube("Long silver cross", TORSO, "metal", (.280, 0, 1.459), (.285, 0, 1.245), (.016, .018), .009)
    s.tube("Silver crossbar", TORSO, "metal", (.288, -.071, 1.379), (.288, .072, 1.379), (.016, .017), .005)


def sculpt_limbs(s):
    rest = joint_positions(STANCE)
    l, t = s.lump, s.tube
    trousers = [l("Trouser waist", TORSO, "pants", (-.045, 0, 1.246), (.218, .299, .193))]
    for side, sign in (("near", -1), ("far", 1)):
        shoulder, elbow, hand = (Vector(rest[f"{joint}_{side}"]) for joint in ("shoulder", "elbow", "hand"))
        hip, knee, foot = (Vector(rest[f"{joint}_{side}"]) for joint in ("hips", "knee", "foot"))
        upper, lower, fist, thigh, shin, boot = [f"{part}_{side}"
                                                for part in ("bicep", "forearm", "fist", "thigh", "shin", "boot")]
        sleeve_axis = (elbow - shoulder).normalized()
        bend_axis = (sleeve_axis + (hand - elbow).normalized()).normalized()

        def sleeve_weights(v):
            arm = blend((v - shoulder).dot(sleeve_axis), -.112, .116)
            below = blend((v - elbow).dot(bend_axis), -.103, .094)
            return {TORSO: 1 - arm, upper: arm * (1 - below), lower: arm * below}

        merge_clay(s, f"Velvet sleeve · {side}", [
            l("Sleeve cap", upper, "coat", shoulder, (.154, .160, .173)),
            t("Upper sleeve", upper, "coat", shoulder, elbow, (.126, .141), .101),
            l("Rounded elbow", lower, "coat", elbow, (.108, .114, .117)),
            t("Lower sleeve", lower, "coat", elbow, hand, (.110, .114), .023),
        ], "coat", weights=sleeve_weights, voxel=.013)
        cuff = hand.lerp(elbow, .07)
        t("Satin cuff", lower, "lapel", cuff, cuff.lerp(elbow, .16), (.117, .119), .026)
        t("Silver wrist cuff", lower, "frame", cuff.lerp(elbow, .03), cuff.lerp(elbow, .088),
          (.120, .121), .009)
        x, y, z = hand
        fingers = []
        for index, dy in enumerate((-.081, -.026, .035, .090)):
            tip = x + (.159 if index in (0, 3) else .190)
            fingers.append(clay_line(s, "Curled finger", fist, "skin", [
                (x + .051, y + dy * .73, z + .018, 1), (tip, y + dy, z + .030, 1),
                (tip + .021, y + dy, z - .034, .88), (tip - .020, y + dy, z - .059, .72),
            ], .034))
        merge_clay(s, f"Ringed hand · {side}", [
            l("Palm", fist, "skin", (x + .039, y, z), (.108, .112, .073)),
            l("Thumb", fist, "skin", (x + .077, y - sign * .100, z + .025), (.085, .047, .056), -23),
            *fingers,
        ], "skin", fist, voxel=.009)
        for dx, dy in ((.135, -.026), (.129, .035)):
            metal_loop(s, "Silver knuckle ring", fist, (x + dx, y + dy, z + .032), (1, 0, 0), .033, .007)
            l("Garnet signet", fist, "gem", (x + dx, y + dy, z + .067), (.027, .027, .013))

        trousers.extend([
            t("Trouser thigh", thigh, "pants", hip, knee, (.153, .165), .131),
            l("Trouser knee", shin, "pants", knee, (.132, .149, .132)),
            t("Trouser shin", shin, "pants", knee, foot.lerp(knee, .24), (.116, .138), .100),
        ])
        l("Trouser hem", shin, "pants", foot.lerp(knee, .32), (.122, .150, .108), -14)
        combat_boot(s, boot, side, foot)
        clay_plate(s, "Split velvet coat skirt", TORSO, "coat", [
            (x, sign * y, z) for x, y, z in [
                (-.281, .233, 1.377), (-.033, .277, 1.338), (.031, .292, 1.239),
                (-.082, .297, 1.048), (-.210, .284, .892), (-.340, .258, .931),
                (-.323, .221, 1.095), (-.312, .214, 1.239),
            ]
        ], (0, .112 * sign, 0), .055)
        clay_line(s, "Satin edge on coat tail", TORSO, "lapel", [
            (-.012, sign * .302, 1.294, .38), (-.049, sign * .346, 1.170, .74),
            (-.139, sign * .345, 1.019, .89), (-.208, sign * .337, .942, .42),
        ], .013)

    def trouser_weights(v):
        leg = 1 - blend(v.z, 1.019, 1.315)
        bend = 1 - blend(v.z, .598, .819)
        far = blend(v.y, -.088, .088)
        return {TORSO: 1 - leg, "thigh_near": leg * (1 - bend) * (1 - far),
                "thigh_far": leg * (1 - bend) * far, "shin_near": leg * bend * (1 - far),
                "shin_far": leg * bend * far}

    merge_clay(s, "Articulated charcoal trousers", trousers, "pants", weights=trouser_weights, voxel=.014)


def build_ozzy(rig, colors):
    sculpt = Sculpt(rig, colors)
    for name, roughness in {"lens": .22, "metal": .28, "frame": .42, "hair": .56, "lapel": .50}.items():
        sculpt.colors[name].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    coat_and_jewelry(sculpt)
    sculpt_limbs(sculpt)
    sculpt_head(sculpt)

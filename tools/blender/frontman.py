"""Full-turnaround clay frontman with articulated limbs and a torn stage mic."""
from math import cos, radians, sin

import bpy
from mathutils import Vector

from model import Sculpt, angled_face, blend, clay, clay_line, clay_plate, merge_clay
from poses import STANCE, joint_positions


HEAD = "head"
TORSO = "pelvis"


def head(s):
    l = s.lump
    skull = merge_clay(s, "Frontman · head sculpt", [
        l("Skull", HEAD, "skin", (.010, 0, 2.449), (.335, .308, .353)),
        l("Squared jaw", HEAD, "skin", (.156, 0, 2.254), (.294, .269, .205), 10),
        l("Heavy chin", HEAD, "skin", (.235, 0, 2.177), (.211, .226, .147), 6),
        l("Nose bridge", HEAD, "skin", (.315, 0, 2.485), (.110, .088, .137), -17),
        l("Nose tip", HEAD, "skin", (.408, -.011, 2.425), (.125, .122, .087), 9),
        *[l("Cheek", HEAD, "skin", (.183, side * .196, 2.371), (.184, .134, .126), 8)
          for side in (-1, 1)],
        *[l("Outer ear", HEAD, "skin", (-.126, side * .295, 2.394), (.097, .075, .116), -12)
          for side in (-1, 1)],
    ], "skin", HEAD, voxel=.010)
    cutter = l("Mouth sculpt tool", HEAD, "skin", (.429, 0, 2.266), (.111, .141, .079), 12)
    bpy.context.view_layer.objects.active = skull
    mouth = skull.modifiers.new("Carve mouth", "BOOLEAN")
    mouth.operation, mouth.object = "DIFFERENCE", cutter
    bpy.ops.object.modifier_apply(modifier=mouth.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    l("Mouth interior", HEAD, "mouth", (.355, .005, 2.258), (.037, .121, .059), 9)
    l("Upper teeth", HEAD, "white", (.420, -.011, 2.298), (.024, .107, .020), 7)
    l("Tongue", HEAD, "rose", (.405, .016, 2.228), (.033, .070, .012), 11)
    for side in (-1, 1):
        l("Ear hollow", HEAD, "rose", (-.124, side * .356, 2.400), (.056, .025, .064), -7)
        l("Nostril", HEAD, "mouth", (.458, side * .082, 2.393), (.031, .035, .016))
        yaw = side * 30
        normal = Vector((cos(radians(yaw)), sin(radians(yaw)), 0))
        center = Vector((.291, side * .179, 2.519))
        angled_face(s, "Eye socket", "skin", center - normal * .035, (.086, .119, .084), yaw)
        angled_face(s, "Eye", "white", center, (.067, .099, .054), yaw)
        pupil = center + normal * .064
        angled_face(s, "Pupil", "dark", pupil, (.015, .035, .037), yaw)
        l("Eye glint", HEAD, "white", pupil + normal * .013 + Vector((0, -.006, .013)),
          (.010, .010, .010))
        clay_line(s, "Angled performer brow", HEAD, "hair", [
            (.340, side * .074, 2.549, .78), (.317, side * .156, 2.600, 1),
            (.281, side * .228, 2.604, .85), (.207, side * .296, 2.568, .26),
        ], .036)
    l("Silver earring", HEAD, "metal", (-.113, -.355, 2.321), (.034, .025, .035))
    merge_clay(s, "Swept stage crest", [
        l("Hair base", HEAD, "hair", (-.106, 0, 2.660), (.302, .307, .195), 8),
        l("Short back of head", HEAD, "hair", (-.258, 0, 2.521), (.145, .266, .205), 14),
        clay_line(s, "Pompadour volume", HEAD, "hair", [
            (-.254, .053, 2.681, .51), (-.129, .035, 2.829, 1),
            (.004, -.018, 2.970, 1), (.165, -.076, 2.957, .83),
            (.284, -.124, 2.860, .16),
        ], .153),
    ], "hair", HEAD, voxel=.011)
    clay_line(s, "Raspberry crest", HEAD, "hair_light", [
        (-.166, -.103, 2.762, .35), (-.059, -.126, 2.910, .86),
        (.097, -.156, 3.020, 1), (.207, -.192, 2.958, .70),
        (.266, -.193, 2.889, .22),
    ], .064)
    for side in (-1, 1):
        clay_line(s, "Side sweep", HEAD, "hair_light", [
            (-.275, side * .205, 2.648, .25),
            (-.164, side * .288, 2.715, .80),
            (-.025, side * .280, 2.748, .35),
        ], .026)


def microphone(s, wrist):
    l, t = s.lump, s.tube
    bone = "fist_far"
    x, y, z = wrist
    def at(dx, dy, dz):
        return x + dx, y + dy, z + dz

    bottom, top = at(.044, -.047, -.177), at(.157, -.060, .258)
    t("Microphone handle", bone, "dark", bottom, top, (.063, .063), .018)
    l("Silver mesh grille", bone, "grille", top, (.092, .089, .105), -15)
    l("Microphone grille collar", bone, "nickel", at(.145, -.058, .200), (.094, .091, .031), -15)
    l("Damaged mic connector", bone, "dark", bottom, (.068, .065, .052), -10)
    clay_line(s, "Torn microphone cable jacket", bone, "cable", [
        (*bottom, 1.15), (*at(.023, -.071, -.282), 1),
        (*at(.087, -.113, -.370), .97), (*at(.186, -.142, -.426), .91),
    ], .029)
    for dx, dy, dz, color in ((-.059, -.017, -.103, "accent"),
                             (.015, -.038, -.140, "trim"),
                             (.085, -.013, -.087, "wire_ivory")):
        splice = at(.186 + dx, -.142 + dy, -.422 + dz * .65)
        tip = at(.199 + dx * 1.30, -.142 + dy * 1.33, -.422 + dz)
        clay_line(s, "Exposed cable conductor insulation", bone, color, [
            (*at(.180 + dx * .14, -.142 + dy * .16, -.409), 1),
            (*at(.186 + dx * .53, -.142 + dy * .51, -.422 + dz * .32), .94),
            (*splice, .73),
        ], .014)
        t("Bare copper tip", bone, "copper", splice, tip, (.009, .009), .005)


def combat_boot(s, bone, side, foot):
    x, y, _ = foot
    sign = -1 if side == "near" else 1
    l = s.lump
    merge_clay(s, f"Black lace-up combat boot · {side}", [
        l("Boot shaft", bone, "boots", (x + .004, y, .251), (.158, .152, .179), -7),
        l("Reinforced instep", bone, "boots", (x + .141, y, .144), (.220, .150, .112), 3),
        l("Rounded toe cap", bone, "boots", (x + .251, y, .126), (.140, .151, .087), -7),
    ], "boots", bone, voxel=.010)
    clay_plate(s, "Heavy lug sole", bone, "sole", [
        (x + dx, y + dy, .052)
        for dx, dy in [(-.14, -.096), (-.076, -.150), (.209, -.158), (.338, -.112),
                       (.393, -.043), (.392, .050), (.331, .121), (.211, .160),
                       (-.083, .150), (-.14, .088)]
    ], (0, 0, .100), .019)
    l("Leather tongue", bone, "sole", (x + .137, y, .241), (.067, .080, .129), -17)
    for i in range(3):
        z = .185 + i * .052
        front = x + .193 - i * .014
        clay_line(s, "Crossed boot lace", bone, "lace", [
            (front, y - .058, z, .64), (front + .010, y, z + .014, 1),
            (front - .015, y + .058, z + .023, .66),
        ], .012)
        l("Boot eyelet", bone, "nickel", (front, y + sign * .062, z), (.014, .015, .015))
    l("Boot pull loop", bone, "boots", (x - .111, y, .397), (.031, .052, .055))


def body(s):
    l, t = s.lump, s.tube
    rest = joint_positions(STANCE)
    merge_clay(s, "Bare torso · pelvis anchored", [
        l("Rib cage", TORSO, "skin", (-.019, 0, 1.696), (.240, .300, .369), -8),
        l("Chest and back", TORSO, "skin", (-.021, 0, 1.820), (.237, .361, .217), -8),
        l("Waist", TORSO, "skin", (-.045, 0, 1.434), (.218, .256, .224), -7),
        l("Abdomen", TORSO, "skin", (.109, 0, 1.549), (.144, .176, .237), -8),
        *[l("Pectoral", TORSO, "skin", (.139, side * .157, 1.798), (.154, .170, .130), -9)
          for side in (-1, 1)],
    ], "skin", TORSO, voxel=.014)
    l("Neck", HEAD, "skin", (.048, 0, 2.028), (.151, .171, .179), -7)
    l("Navel", TORSO, "rose", (.187, 0, 1.416), (.012, .028, .022))
    for side in (-1, 1):
        l("Pectoral clay mark", TORSO, "rose", (.248, side * .177, 1.746), (.016, .028, .022), 4)

    shorts = [l("Cargo waist", TORSO, "pants", (-.051, 0, 1.253), (.240, .310, .220))]
    for side, sign in (("near", -1), ("far", 1)):
        shoulder, elbow, hand = (Vector(rest[f"{joint}_{side}"])
                                 for joint in ("shoulder", "elbow", "hand"))
        hip, knee, foot = (Vector(rest[f"{joint}_{side}"])
                           for joint in ("hips", "knee", "foot"))
        upper, lower, hand_bone, thigh, shin, boot = (
            f"{part}_{side}" for part in ("bicep", "forearm", "fist", "thigh", "shin", "boot"))
        upper_axis = (elbow - shoulder).normalized()
        bend_axis = (upper_axis + (hand - elbow).normalized()).normalized()

        def arm_weights(v):
            arm = blend((v - shoulder).dot(upper_axis), -.108, .114)
            forearm = blend((v - elbow).dot(bend_axis), -.094, .084)
            return {TORSO: 1 - arm, upper: arm * (1 - forearm), lower: arm * forearm}

        merge_clay(s, f"Bare arm · {side}", [
            l("Round deltoid", upper, "skin", shoulder, (.148, .154, .172), 6),
            t("Sculpted bicep", upper, "skin", shoulder, elbow, (.126, .133), .105),
            l("Elbow", lower, "skin", elbow, (.098, .110, .109)),
            t("Sculpted forearm", lower, "skin", elbow, hand, (.105, .113), .083),
        ], "skin", weights=arm_weights, voxel=.014)
        x, y, z = hand
        merge_clay(s, f"Sculpted hand · {side}", [
            l("Palm", hand_bone, "skin", (x + .055, y, z), (.134, .103, .099), -11),
            l("Bent fingers", hand_bone, "skin", (x + .123, y, z + .018), (.106, .116, .092), 13),
            l("Shaped thumb", hand_bone, "skin", (x + .064, y - sign * .079, z + .062),
              (.083, .068, .055), -20),
        ], "skin", hand_bone, voxel=.010)
        l("Black stage wristband", lower, "sole", hand.lerp(elbow, .135), (.063, .118, .108), 11)
        for offset in (-.042, .010, .057):
            l("Knuckle fold", hand_bone, "rose", (x + .193, y + offset, z + .011),
              (.014, .009, .022), -11)

        hem = foot.lerp(knee, .60)
        seam_space = Vector((0, sign * .020, 0))
        shorts.extend([
            t("Bermuda thigh", thigh, "pants", hip + seam_space, knee + seam_space,
              (.187, .151), .141),
            l("Roomy knee", shin, "pants", knee, (.158, .154, .146)),
            t("Three-quarter hem", shin, "pants", knee, hem, (.143, .143), .023),
        ])
        t("Rolled cargo hem", shin, "cuff", hem, hem.lerp(knee, .28), (.150, .150), .024)
        t("Visible shin", shin, "skin", hem, foot.lerp(hem, .41), (.104, .108), .044)
        pocket = hip.lerp(knee, .48) + Vector((-.035, sign * .152, 0))
        l("Cargo side pocket", thigh, "cargo", pocket, (.118, .041, .130), -8)
        flap = pocket + Vector((0, sign * .013, .085))
        l("Cargo flap", thigh, "cuff", flap, (.111, .037, .036), -8)
        combat_boot(s, boot, side, foot)

    def shorts_weights(v):
        leg = 1 - blend(v.z, 1.01, 1.31)
        # Keep the inseam attached to the waist as the two thighs separate.
        inner = (1 - blend(abs(v.y), .018, .136)) * blend(v.z, .77, 1.05)
        leg *= 1 - .92 * inner
        shin = 1 - blend(v.z, .59, .83)
        far = blend(v.y, -.083, .083)
        return {
            TORSO: 1 - leg,
            "thigh_near": leg * (1 - shin) * (1 - far),
            "shin_near": leg * shin * (1 - far),
            "thigh_far": leg * (1 - shin) * far,
            "shin_far": leg * shin * far,
        }

    merge_clay(s, "Articulated cargo bermudas", shorts, "pants", weights=shorts_weights, voxel=.015)
    l("Cargo waistband", TORSO, "sole", (-.039, 0, 1.326), (.232, .295, .038))
    l("Stage belt buckle", TORSO, "nickel", (.198, -.032, 1.325), (.037, .068, .041))
    microphone(s, rest["hand_far"])


def build_frontman(rig, colors):
    s = Sculpt(rig, colors)
    for name, title, color in [
        ("cuff", "Washed olive canvas", "85886a"), ("cargo", "Faded olive pocket", "777b5f"),
        ("sole", "Black rubber and straps", "24232c"), ("lace", "Charcoal laces", "59515c"),
        ("nickel", "Dull nickel hardware", "c3b7b8"), ("grille", "Worn silver mesh", "a5a4ab"),
        ("cable", "Ripped cable rubber", "303039"), ("wire_ivory", "Cable insulation ivory", "dfc39e"),
        ("copper", "Bare conductor tips", "dd8d5a"),
    ]:
        s.colors[name] = clay(title, color, metallic=.36 if name in ("nickel", "grille", "copper") else 0)
    for material in s.colors.values():
        nodes = material.node_tree.nodes
        nodes.get("Principled BSDF").inputs["Roughness"].default_value = .76
        bump = next(node for node in nodes if node.type == "BUMP")
        bump.inputs["Strength"].default_value = .11
        bump.inputs["Distance"].default_value = .023
    body(s)
    head(s)

"""Sculpt and deform the original, full-turnaround guitarist puppet."""
from math import cos, radians, sin

import bpy
from mathutils import Matrix, Vector

from model import Sculpt, angled_face, blend, build_guitar, clay, clay_line, clay_plate, merge_clay
from poses import STANCE, joint_positions


HEAD = "head"
BODY = "pelvis"


def shirt_panel(s, surface):
    # Sample the chest across the full garment so the cotton follows its
    # curvature between the shoulders, collar and waist.
    rows = [
        (2.006, 0, .109, .025),
        (1.962, -.006, .153, .004),
        (1.868, -.017, .149, 0),
        (1.741, -.024, .132, 0),
        (1.602, -.022, .118, 0),
        (1.493, -.015, .103, 0),
        (1.436, 0, .071, 0),
    ]
    columns = 9
    across = [i / 4 - 1 for i in range(columns)]
    verts = surface([(center + width * u, z + scoop * u * u)
                     for z, center, width, scoop in rows for u in across], .034)
    faces = []
    for row in range(len(rows) - 1):
        for col in range(columns - 1):
            i = row * columns + col
            faces.append((i, i + columns, i + columns + 1, i + 1))
    mesh = bpy.data.meshes.new("White crew-neck cotton")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    shirt = bpy.data.objects.new("White crew-neck T-shirt", mesh)
    bpy.context.collection.objects.link(shirt)
    solid = shirt.modifiers.new("Cotton edge", "SOLIDIFY")
    solid.thickness = .022
    return s.bind(shirt, "White crew-neck T-shirt", BODY, "shirt")


def face(s):
    l = s.lump
    volumes = [
        l("Skull", HEAD, "skin", (-.025, 0, 2.421), (.357, .317, .391)),
        l("Jaw and chin", HEAD, "skin", (.151, 0, 2.213), (.297, .250, .203), -17),
        l("Upper lip volume", HEAD, "skin", (.319, 0, 2.327), (.115, .166, .096)),
        l("Nose bridge", HEAD, "skin", (.336, 0, 2.476), (.094, .076, .133), -19),
        l("Nose tip", HEAD, "skin", (.457, -.018, 2.418), (.134, .113, .088), 12),
    ]
    for sign in (-1, 1):
        volumes.extend([
            l("Cheek plane", HEAD, "skin", (.156, sign * .205, 2.383), (.229, .130, .139), -11),
            l("Nostril wing", HEAD, "skin", (.444, sign * .085, 2.398), (.075, .065, .050)),
            l("Outer ear", HEAD, "skin", (-.139, sign * .296, 2.377), (.100, .073, .122), -11),
        ])
    skull = merge_clay(s, "Head · sculpted face", volumes, "skin", HEAD, voxel=.010)
    bpy.context.view_layer.update()
    from_world = skull.matrix_world.inverted()
    toward_face = from_world.to_3x3() @ Vector((-1, 0, 0))

    def surface(points, depth):
        anchors = []
        for y, z, radius in points:
            hit, point, _, _ = skull.ray_cast(from_world @ Vector((1, y, z)), toward_face)
            if not hit:
                raise ValueError(f"Face surface missing at {y}, {z}")
            x = (skull.matrix_world @ point).x
            anchors.append((x + depth, y, z, radius))
        return anchors

    l("Neck", HEAD, "skin", (.025, 0, 2.037), (.152, .174, .188), -7)

    for sign in (-1, 1):
        l("Ear hollow", HEAD, "rose", (-.133, sign * .354, 2.387), (.054, .027, .069), -15)
        l("Nostril", HEAD, "mouth", (.498, sign * .086, 2.376), (.035, .032, .015), 20)
        tilt = sign * 28
        angle = radians(tilt)
        normal = Vector((cos(angle), sin(angle), 0))
        center = Vector((.298, sign * .182, 2.504 if sign < 0 else 2.496))
        angled_face(s, "Socket", "skin", center - normal * .039, (.086, .120, .086), tilt)
        angled_face(s, "Eyeball", "white", center, (.064, .101, .048), tilt)
        iris = center + normal * .060
        angled_face(s, "Iris", "iris", iris, (.012, .044, .045), tilt)
        angled_face(s, "Pupil", "dark", iris + normal * .010, (.008, .030, .032), tilt)
        l("Eye highlight", HEAD, "white", iris + normal * .018 + Vector((0, -.009, .010)), (.008, .009, .008))
        clay_line(s, "Upper clay eyelid", HEAD, "skin", [
            (.344, sign * .095, center.z + .013, .36), (.345, sign * .150, center.z + .027, .9),
            (.317, sign * .221, center.z + .040, 1), (.275, sign * .275, center.z + .038, .30),
        ], .030)
        raised = .057 if sign < 0 else 0
        clay_line(s, "Expressive brow", HEAD, "hair", surface([
            (sign * .072, 2.552 + .3 * raised, .60), (sign * .144, 2.577 + raised, 1),
            (sign * .215, 2.586 + raised, .82), (sign * .280, 2.558 + .6 * raised, .26),
        ], .015), .038)
    clay_line(s, "Crooked stage grin", HEAD, "mouth", surface([
        (-.219, 2.325, .31), (-.139, 2.299, 1), (-.031, 2.276, .79),
        (.094, 2.264, .63), (.178, 2.257, .20),
    ], .005), .024)
    clay_line(s, "Lower lip", HEAD, "rose", surface([
        (-.149, 2.277, .29), (-.065, 2.249, .68), (.047, 2.242, .41),
    ], .002), .016)
    clay_line(s, "Short angular goatee", HEAD, "hair", surface([
        (-.068, 2.204, .30), (0, 2.183, 1), (.049, 2.204, .32),
    ], .007), .029)
    l("Gold stud", HEAD, "metal", (-.117, -.360, 2.286), (.033, .024, .035))


def hair(s):
    l = s.lump
    volumes = [
        l("Sculpted undercut", HEAD, "hair", (-.114, .020, 2.682), (.317, .301, .191), -15),
        l("Hair over nape", HEAD, "hair", (-.300, .091, 2.426), (.190, .271, .366), 18),
        clay_line(s, "Long clay lock", HEAD, "hair", [
            (.172, .232, 2.720, .40), (-.082, .327, 2.687, .96),
            (-.217, .367, 2.510, 1), (-.215, .365, 2.290, .84),
            (-.360, .313, 2.102, .19),
        ], .107),
        clay_line(s, "Short swept temple", HEAD, "hair", [
            (.195, -.259, 2.675, .14), (.020, -.310, 2.630, .68),
            (-.159, -.310, 2.588, .81), (-.254, -.298, 2.526, .25),
        ], .068),
    ]
    merge_clay(s, "Hair · continuous sculpt", volumes, "hair", HEAD, voxel=.013)
    clay_line(s, "Heavy swept forelock", HEAD, "hair_light", [
        (-.226, .157, 2.798, .28), (-.048, .104, 2.882, .83),
        (.176, .015, 2.911, 1), (.349, -.096, 2.833, .79),
        (.410, -.183, 2.711, .52), (.366, -.230, 2.626, .08),
    ], .103)
    clay_line(s, "Fold along the forelock", HEAD, "hair", [
        (-.090, .153, 2.915, .18), (.106, .090, 2.960, .74),
        (.274, -.009, 2.950, .81), (.368, -.133, 2.835, .11),
    ], .036)
    clay_line(s, "Raked sideburn", HEAD, "hair_light", [
        (.063, -.334, 2.632, .12), (-.097, -.366, 2.585, .76),
        (-.176, -.365, 2.538, .66), (-.218, -.341, 2.498, .12),
    ], .027)
    clay_line(s, "Long side ridge", HEAD, "hair_light", [
        (-.157, .324, 2.750, .20), (-.221, .428, 2.598, .80),
        (-.227, .443, 2.394, .73), (-.293, .408, 2.240, .16),
    ], .038)
    clay_line(s, "Back lock", HEAD, "hair_light", [
        (-.325, .107, 2.753, .22), (-.478, .161, 2.587, .83),
        (-.451, .208, 2.375, .78), (-.365, .252, 2.187, .17),
    ], .039)


def boxing_glove(s, bone, side, wrist):
    x, y, z = wrist
    inward = 1 if side == "near" else -1
    l = s.lump
    merge_clay(s, f"Boxing glove · {side}", [
        l("Leather wrist", bone, "glove", (x, y, z), (.116, .113, .108)),
        l("Padded knuckles", bone, "glove", (x + .122, y, z + .026), (.147, .145, .141)),
        l("Tucked boxing thumb", bone, "glove", (x + .070, y + inward * .110, z - .052),
          (.101, .069, .079), -20),
    ], "glove", bone, voxel=.009)
    l("Boxing wrist wrap", bone, "glove_wrap", (x - .032, y, z),
      (.066, .125, .120))
    clay_line(s, "Glove cuff seam", bone, "glove_stitch", [
        (x + .009, y - inward * .081, z + .074, .3),
        (x + .013, y - inward * .121, z + .006, 1),
        (x + .005, y - inward * .081, z - .081, .3),
    ], .009)


def western_boot(s, bone, side, foot):
    x, y, _ = foot
    outer = -1 if side == "near" else 1
    l = s.lump
    merge_clay(s, f"Western boot · {side}", [
        l("Western shaft", bone, "boots", (x - .022, y, .300), (.150, .150, .189), 7),
        l("Leather instep", bone, "boots", (x + .112, y, .158), (.217, .139, .115), 16),
        l("Tapered leather toe", bone, "boots", (x + .242, y, .114), (.148, .105, .076), 5),
    ], "boots", bone, voxel=.010)
    clay_plate(s, "Western sole", bone, "sole", [
        (x + dx, y + dy, z) for dx, dy, z in [
            (-.149, -.100, .085), (-.073, -.148, .084), (.157, -.130, .049),
            (.313, -.092, .045), (.394, -.021, .047), (.394, .021, .047),
            (.310, .093, .045), (.154, .132, .049), (-.078, .146, .084),
            (-.149, .100, .085),
        ]
    ], (0, 0, .048), .017)
    clay_plate(s, "Stacked western heel", bone, "sole", [
        (x + dx, y + dy, .049)
        for dx, dy in [(-.143, -.096), (-.069, -.140), (.021, -.120), (.029, .120),
                       (-.069, .140), (-.143, .096)]
    ], (0, 0, .096), .018)
    clay_line(s, "Western boot embroidery", bone, "boot_thread", [
        (x - .094, y + outer * .130, .379, .4),
        (x - .049, y + outer * .150, .317, .85),
        (x + .004, y + outer * .152, .264, 1),
        (x + .067, y + outer * .131, .346, .47),
    ], .011)
    l("Western pull tab", bone, "boot_thread", (x - .044, y + outer * .101, .447),
      (.035, .024, .037))


def jacket_details(s, coat):
    bpy.context.view_layer.update()
    local = coat.matrix_world.inverted()
    direction = local.to_3x3() @ Vector((-1, 0, 0))

    def panel(points, lift):
        result = []
        for y, z in points:
            ray = local @ Vector((.8, y, z))
            hit, point, _, _ = coat.ray_cast(ray, direction)
            if not hit:
                raise ValueError(f"Jacket front missing at {y}, {z}")
            result.append(((coat.matrix_world @ point).x + lift, y, z))
        return result

    # Keep the shirt and its facing on the torso with the zipper and lapels.
    shirt_panel(s, panel)
    for name, points in (
        ("Wide notched lapel", [(-.164, 2.015), (-.229, 1.913), (-.154, 1.901),
                                (-.225, 1.866), (-.090, 1.655), (-.080, 1.838)]),
        ("Short notched lapel", [(.155, 2.025), (.202, 1.932), (.146, 1.913),
                                 (.208, 1.876), (.116, 1.750), (.081, 1.929)]),
    ):
        clay_plate(s, name, BODY, "jacket_edge", panel(points, .054), (.047, 0, 0), .013)
    for y, z in ((-.168, 1.870), (.172, 1.885), (-.209, 1.957), (.168, 1.972)):
        (snap,) = panel([(y, z)], .086)
        s.lump("Silver lapel snap", BODY, "nickel", snap, (.013, .022, .022))
    for name, points in (
        ("Diagonal front zipper", [(.091, 1.470), (.071, 1.553), (-.026, 1.711), (-.094, 1.805)]),
        ("Slash chest pocket", [(-.230, 1.674), (-.202, 1.613), (-.169, 1.574)]),
    ):
        coords = panel(points, .061)
        clay_line(s, name, BODY, "nickel", [(*point, .8) for point in coords], .014)
        s.lump("Zipper pull", BODY, "nickel", coords[-1], (.018, .021, .032), 19)
    s.lump("Jacket waist belt", BODY, "dark", (-.022, 0, 1.429), (.245, .317, .047))
    s.lump("Silver jacket buckle", BODY, "nickel", (.229, .01, 1.425), (.036, .056, .045))


def body(s):
    l, t = s.lump, s.tube
    rest = joint_positions(STANCE)
    coat = merge_clay(s, "Biker jacket · torso", [
        l("Chest", BODY, "jacket", (-.007, 0, 1.722), (.278, .391, .369), -8),
        l("Cropped jacket hem", BODY, "jacket", (-.026, 0, 1.491), (.242, .313, .127), -8),
    ], "jacket", BODY)
    jacket_details(s, coat)
    pants = [l("Hip volume", BODY, "pants", (-.069, 0, 1.251), (.222, .313, .224))]
    for side, sign in (("near", -1), ("far", 1)):
        shoulder, elbow, hand = (rest[f"{key}_{side}"] for key in ("shoulder", "elbow", "hand"))
        hip, knee, foot = (rest[f"{key}_{side}"] for key in ("hips", "knee", "foot"))
        upper, lower, fist, thigh, shin, boot = (
            f"{key}_{side}" for key in ("bicep", "forearm", "fist", "thigh", "shin", "boot"))
        shoulder, elbow, hand = map(Vector, (shoulder, elbow, hand))
        upper_axis = (elbow - shoulder).normalized()
        forearm_axis = (hand - elbow).normalized()
        bend_axis = (upper_axis + forearm_axis).normalized()

        def sleeve_weights(v):
            arm = blend((v - shoulder).dot(upper_axis), -.09, .125)
            forearm = blend((v - elbow).dot(bend_axis), -.105, .095)
            return {BODY: 1 - arm, upper: arm * (1 - forearm), lower: arm * forearm}

        merge_clay(s, f"Biker jacket · sleeve {side}", [
            t("Upper sleeve", upper, "jacket", shoulder, elbow, (.142, .145), .107),
            l("Sleeve bend", lower, "jacket", elbow, (.111, .115, .117)),
            t("Lower sleeve", lower, "jacket", elbow, hand, (.112, .117), .066),
        ], "jacket", weights=sleeve_weights)
        t("Zipped leather cuff", lower, "jacket_edge", hand.lerp(elbow, .23),
          hand.lerp(elbow, .10), (.113, .115), .022)
        snap = hand.lerp(elbow, .17) + Vector((0, sign * .108, 0))
        l("Cuff snap", lower, "nickel", snap, (.020, .014, .020))
        cuff = Vector(foot).lerp(Vector(knee), .37)
        pants.extend([
            t("Trouser thigh", thigh, "pants", hip, knee, (.165, .159), .16),
            l("Knee sculpt", shin, "pants", knee, (.144, .137, .141)),
            t("Trouser shin", shin, "pants", knee, cuff, (.124, .134), .052),
        ])
        t("Turned denim cuff", shin, "denim_edge", cuff, cuff.lerp(Vector(knee), .19),
          (.128, .136), .026)
        boxing_glove(s, fist, side, hand)
        western_boot(s, boot, side, foot)

    def trouser_weights(v):
        side = "near" if v.y < 0 else "far"
        leg = 1 - blend(v.z, .94, 1.31)
        shin = 1 - blend(v.z, .59, .83)
        return {BODY: 1 - leg, f"thigh_{side}": leg * (1 - shin), f"shin_{side}": leg * shin}

    merge_clay(s, "Trousers · weighted continuous mesh", pants, "pants", weights=trouser_weights)


def mount_guitar(s):
    # Swing the existing instrument upright and turn its face outward over the back.
    rotation = (Matrix.Rotation(radians(-8), 4, "Y")
                @ Matrix.Rotation(radians(-57), 4, "Z")
                @ Matrix.Rotation(radians(-49), 4, "Y"))
    transform = (Matrix.Translation((-.46, .14, 1.30)) @ rotation
                 @ Matrix.Scale(.86, 4) @ Matrix.Translation((.33, .428, -1.26)))
    parts = build_guitar(s)
    bpy.context.view_layer.update()
    for part in parts:
        part.matrix_world = transform @ part.matrix_world

    for side in (-1, 1):
        clay_line(s, "Backpack shoulder strap", BODY, "harness", [
            (-.423, side * .132 + .14, 1.38, .76),
            (-.223, side * .289, 1.41, .9),
            (.081, side * .298, 1.53, .87),
            (.218, side * .205, 1.77, 1),
            (.160, side * .208, 1.955, 1),
            (.009, side * .216, 2.044, 1),
            (-.180, side * .190, 1.989, .89),
            (-.346, side * .102 + .076, 1.801, .76),
        ], .042)
        s.lump("Harness buckle", BODY, "metal", (.249, side * .218, 1.737),
               (.023, .041, .056), -15)
    clay_line(s, "Backpack neck cradle", BODY, "harness", [
        (-.344, -.031, 1.817, .83),
        (-.457, -.018, 1.798, .93),
        (-.533, .061, 1.782, 1),
        (-.426, .139, 1.793, .93),
        (-.345, .178, 1.821, .83),
    ], .033)


def build_guitarist(rig, colors):
    puppet = Sculpt(rig, colors)
    puppet.colors["iris"] = clay("Umber iris", "6e483a")
    puppet.colors["glove"] = clay("Plum boxing leather", "aa375f")
    puppet.colors["glove_wrap"] = clay("Black boxing wrap", "342337")
    puppet.colors["glove_stitch"] = clay("Wrist stitching", "c988a9")
    puppet.colors["harness"] = clay("Worn harness leather", "413049")
    puppet.colors["jacket_edge"] = clay("Folded black leather", "423845")
    puppet.colors["shirt"] = clay("White crew-neck cotton", "f3eee4")
    puppet.colors["nickel"] = clay("Dull silver jacket hardware", "c6bec3", metallic=.33)
    puppet.colors["denim_edge"] = clay("Turned light denim", "aac1d4")
    puppet.colors["boot_thread"] = clay("Western saddle stitching", "c38757")
    puppet.colors["sole"] = clay("Stacked leather sole", "483036")
    for material in puppet.colors.values():
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Roughness"].default_value = .81
        bump = next(node for node in material.node_tree.nodes if node.type == "BUMP")
        bump.inputs["Strength"].default_value = .105
        bump.inputs["Distance"].default_value = .027
    add_thumbprint(puppet.colors["glove"])
    for name in ("jacket", "jacket_edge"):
        shader = puppet.colors[name].node_tree.nodes.get("Principled BSDF")
        shader.inputs["Roughness"].default_value = .66
    body(puppet)
    face(puppet)
    hair(puppet)
    mount_guitar(puppet)


def add_thumbprint(material):
    tree = material.node_tree
    nodes = tree.nodes
    source = nodes.new("ShaderNodeTexCoord").outputs["Generated"]
    offset = nodes.new("ShaderNodeVectorMath")
    offset.operation = "SUBTRACT"
    offset.inputs[1].default_value = (.61, .08, .52)
    tree.links.new(source, offset.inputs[0])
    rings = nodes.new("ShaderNodeTexWave")
    rings.wave_type, rings.rings_direction = "RINGS", "Y"
    rings.inputs["Scale"].default_value = 13
    rings.inputs["Distortion"].default_value = .8
    tree.links.new(offset.outputs["Vector"], rings.inputs["Vector"])
    radius = nodes.new("ShaderNodeVectorMath")
    radius.operation = "LENGTH"
    tree.links.new(offset.outputs["Vector"], radius.inputs[0])
    falloff = nodes.new("ShaderNodeMapRange")
    falloff.interpolation_type = "SMOOTHSTEP"
    for name, value in (("From Min", .045), ("From Max", .29), ("To Min", 1), ("To Max", 0)):
        falloff.inputs[name].default_value = value
    tree.links.new(radius.outputs["Value"], falloff.inputs["Value"])
    mask = nodes.new("ShaderNodeMath")
    mask.operation = "MULTIPLY"
    tree.links.new(rings.outputs["Fac"], mask.inputs[0])
    tree.links.new(falloff.outputs["Result"], mask.inputs[1])
    surface = nodes.get("Principled BSDF")
    grain = surface.inputs["Normal"].links[0].from_socket
    mark = nodes.new("ShaderNodeBump")
    mark.inputs["Strength"].default_value = .12
    mark.inputs["Distance"].default_value = .009
    tree.links.new(grain, mark.inputs["Normal"])
    tree.links.new(mask.outputs[0], mark.inputs["Height"])
    tree.links.new(mark.outputs["Normal"], surface.inputs["Normal"])

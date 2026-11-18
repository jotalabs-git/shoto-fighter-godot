"""Sculpt and deform the original, full-turnaround guitarist puppet."""
from math import cos, radians, sin

import bpy
from mathutils import Matrix, Vector

from model import Sculpt, build_guitar, clay
from poses import STANCE, joint_positions


HEAD = "head"
BODY = "pelvis"


def blend(value, start, end):
    t = min(1.0, max(0.0, (value - start) / (end - start)))
    return t * t * (3.0 - 2.0 * t)


def merge_clay(sculpt, name, parts, color, bone=None, weights=None, voxel=.019):
    """Bake a sculpted union with enough topology to deform at the joints."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        world = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = world
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.data.remesh_voxel_size = voxel
    bpy.ops.object.voxel_remesh()
    smooth = obj.modifiers.new("Finger-smoothed clay", "SMOOTH")
    smooth.factor, smooth.iterations = .8, 4
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    obj.data.materials.clear()
    if weights is None:
        return sculpt.bind(obj, name, bone, color)
    obj.name = name
    obj.data.materials.append(sculpt.colors[color])
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    groups = {}
    for vert in obj.data.vertices:
        for joint, amount in weights(vert.co).items():
            if amount <= 0:
                continue
            if joint not in groups:
                groups[joint] = obj.vertex_groups.new(name=joint)
            groups[joint].add([vert.index], amount, "REPLACE")
    obj.parent = sculpt.rig
    modifier = obj.modifiers.new("Puppet skin", "ARMATURE")
    modifier.object = sculpt.rig
    modifier.use_deform_preserve_volume = True
    return obj


def clay_line(sculpt, name, bone, color, points, radius):
    """A tapered clay roll through sculpt control points."""
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 10
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    curve.use_fill_caps = True
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, (x, y, z, scale) in zip(spline.bezier_points, points):
        point.co = (x, y, z)
        point.radius = scale
        point.handle_left_type = point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    return sculpt.bind(bpy.context.object, name, bone, color)


def angled_face(sculpt, name, color, xyz, radii, tilt):
    obj = sculpt.lump(name, HEAD, color, xyz, radii)
    transform = obj.matrix_world.copy()
    # Rotate around the center of the sculpted feature in world space.
    center = transform.translation.copy()
    obj.matrix_world = Matrix.Translation(center) @ Matrix.Rotation(radians(tilt), 4, "Z") @ Matrix.Translation(-center) @ transform
    return obj


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


def body(s):
    l, t = s.lump, s.tube
    rest = joint_positions(STANCE)
    jacket = [
        l("Chest", BODY, "jacket", (-.007, 0, 1.722), (.278, .391, .369), -8),
        l("Cropped jacket hem", BODY, "jacket", (-.026, 0, 1.491), (.242, .313, .127), -8),
    ]
    pants = [l("Hip volume", BODY, "pants", (-.069, 0, 1.251), (.222, .313, .224))]
    for side, sign in (("near", -1), ("far", 1)):
        shoulder, elbow, hand = (rest[f"{key}_{side}"] for key in ("shoulder", "elbow", "hand"))
        hip, knee, foot = (rest[f"{key}_{side}"] for key in ("hips", "knee", "foot"))
        upper, lower, fist, thigh, shin, boot = (
            f"{key}_{side}" for key in ("bicep", "forearm", "fist", "thigh", "shin", "boot"))
        jacket.extend([
            t("Upper sleeve", upper, "jacket", shoulder, elbow, (.160, .165), .14),
            l("Sleeve bend", lower, "jacket", elbow, (.129, .130, .133)),
            t("Lower sleeve", lower, "jacket", elbow, hand, (.116, .122), .07),
        ])
        pants.extend([
            t("Trouser thigh", thigh, "pants", hip, knee, (.165, .159), .16),
            l("Knee sculpt", shin, "pants", knee, (.141, .133, .141)),
            t("Trouser shin", shin, "pants", knee, foot, (.123, .133), .09),
        ])
        boxing_glove(s, fist, side, hand)
        x, y, _ = foot
        merge_clay(s, f"Boot · {side}", [
            l("Boot ankle", boot, "boots", (x + .015, y, .246), (.154, .147, .201), -8),
            l("Boot toe", boot, "boots", (x + .127, y, .152), (.245, .150, .125)),
        ], "boots", boot, voxel=.013)
        l("Boot sole", boot, "dark", (x + .122, y, .047), (.251, .161, .047))
        l("Toe cap", boot, "trim", (x + .237, y, .143), (.128, .143, .073))
        l("Boot buckle", boot, "metal", (x + .060, y + sign * .140, .199), (.055, .018, .051))

    def coat_weights(v):
        side = "near" if v.y < 0 else "far"
        arm = max(blend(abs(v.y), .257, .390), blend(v.x, .243, .361))
        elbow = Vector(rest[f"elbow_{side}"])
        hand = Vector(rest[f"hand_{side}"])
        shoulder = Vector(rest[f"shoulder_{side}"])
        along_arm = ((elbow - shoulder).normalized() + (hand - elbow).normalized()).normalized()
        forearm = blend((v - elbow).dot(along_arm), -.118, .104)
        return {BODY: 1 - arm, f"bicep_{side}": arm * (1 - forearm), f"forearm_{side}": arm * forearm}

    def trouser_weights(v):
        side = "near" if v.y < 0 else "far"
        leg = 1 - blend(v.z, .94, 1.31)
        shin = 1 - blend(v.z, .59, .83)
        return {BODY: 1 - leg, f"thigh_{side}": leg * (1 - shin), f"shin_{side}": leg * shin}

    merge_clay(s, "Jacket · weighted continuous mesh", jacket, "jacket", weights=coat_weights)
    merge_clay(s, "Trousers · weighted continuous mesh", pants, "pants", weights=trouser_weights)
    l("Shirt under cropped jacket", BODY, "dark", (.234, 0, 1.532), (.048, .157, .210), -9)
    l("Belt", BODY, "dark", (-.022, 0, 1.314), (.223, .322, .036))
    l("Buckle", BODY, "metal", (.204, 0, 1.309), (.038, .070, .052))
    clay_line(s, "Folded leather lapel", BODY, "jacket_edge", [
        (.116, -.151, 2.028, .48), (.218, -.142, 1.901, 1),
        (.266, -.069, 1.798, .83), (.259, .012, 1.723, .24),
    ], .039)
    clay_line(s, "Diagonal jacket zip", BODY, "metal", [
        (.194, .094, 1.458, .31), (.248, .048, 1.562, .88),
        (.276, -.026, 1.704, 1), (.272, -.095, 1.789, .76),
    ], .014)
    l("Zip pull", BODY, "metal", (.282, -.093, 1.780), (.017, .021, .038), 25)
    arm = "bicep_near"
    l("Padded violet shoulder", arm, "shoulder", (.009, -.384, 1.874),
      (.200, .118, .122), -16)
    clay_line(s, "Shoulder pad edge", arm, "jacket_edge", [
        (-.146, -.410, 1.879, .18), (-.061, -.482, 1.904, .87),
        (.058, -.484, 1.913, 1), (.175, -.425, 1.932, .30),
    ], .022)
    for x in (-.078, .064):
        l("Shoulder rivet", arm, "metal", (x, -.479, 1.859), (.025, .017, .023))


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
    puppet = Sculpt(rig, {**colors, "jacket": "393445"})
    puppet.colors["iris"] = clay("Umber iris", "6e483a")
    puppet.colors["glove"] = clay("Plum boxing leather", "aa375f")
    puppet.colors["glove_wrap"] = clay("Black boxing wrap", "342337")
    puppet.colors["glove_stitch"] = clay("Wrist stitching", "c988a9")
    puppet.colors["harness"] = clay("Worn harness leather", "413049")
    puppet.colors["shoulder"] = clay("Violet shoulder pad", "8151ba")
    puppet.colors["jacket_edge"] = clay("Worn violet piping", "655274")
    for material in puppet.colors.values():
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Roughness"].default_value = .81
        bump = next(node for node in material.node_tree.nodes if node.type == "BUMP")
        bump.inputs["Strength"].default_value = .105
        bump.inputs["Distance"].default_value = .027
    add_thumbprint(puppet.colors["glove"])
    add_thumbprint(puppet.colors["shoulder"])
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

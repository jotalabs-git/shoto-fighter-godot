"""Original, jointed clay figures. Each mesh stays editable and bound to one bone."""
from math import radians

import bpy
from mathutils import Matrix, Vector

from poses import STANCE, joint_positions, points


def clay(name, hex_color, noise=.08, metallic=0):
    def linear(value):
        return value / 12.92 if value < .04045 else ((value + .055) / 1.055) ** 2.4

    material = bpy.data.materials.new(name)
    rgb = [linear(int(hex_color[i:i + 2], 16) / 255) for i in (0, 2, 4)]
    material.diffuse_color = (*rgb, 1)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    surface = nodes.get("Principled BSDF")
    surface.inputs["Base Color"].default_value = (*rgb, 1)
    surface.inputs["Roughness"].default_value = .66
    surface.inputs["Metallic"].default_value = metallic
    grain = nodes.new("ShaderNodeTexNoise")
    grain.inputs["Scale"].default_value = 25
    grain.inputs["Detail"].default_value = 2
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = noise
    bump.inputs["Distance"].default_value = .045
    material.node_tree.links.new(grain.outputs["Fac"], bump.inputs["Height"])
    material.node_tree.links.new(bump.outputs["Normal"], surface.inputs["Normal"])
    return material


class Sculpt:
    def __init__(self, rig, colors):
        self.rig = rig
        self.colors = {name: clay(name, color, metallic=.24 if name == "metal" else 0)
                       for name, color in colors.items()}
        self.colors.update({
            "dark": clay("Graphite", "191521"), "white": clay("Warm ivory", "fbe3c9"),
            "mouth": clay("Mouth", "62283d"), "rose": clay("Baked clay", "aa4f45"),
        })

    def bind(self, obj, name, bone, color):
        obj.name = name
        obj.data.materials.append(self.colors[color])
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        world = obj.matrix_world.copy()
        obj.parent = self.rig
        obj.parent_type = "BONE"
        obj.parent_bone = bone
        obj.matrix_world = world
        return obj

    def lump(self, name, bone, color, position, size, tilt=0):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=position)
        obj = bpy.context.object
        obj.scale = size
        obj.rotation_euler.y = radians(tilt)
        bpy.context.view_layer.update()
        return self.bind(obj, name, bone, color)

    def tube(self, name, bone, color, start, end, widths, overlap=0):
        start, end = Vector(start), Vector(end)
        obj = self.lump(name, bone, color, (start + end) / 2,
                        (*widths, (end - start).length / 2 + overlap))
        rotation = (end - start).to_track_quat("Z", "Y").to_matrix().to_4x4()
        obj.matrix_world = Matrix.Translation((start + end) / 2) @ rotation @ Matrix.Diagonal(
            (*widths, (end - start).length / 2 + overlap, 1))
        return obj

    def outline(self, name, bone, color, polygon, depth, thickness, bevel):
        count = len(polygon)
        verts = [(x, depth + side * thickness / 2, z) for side in (-1, 1) for x, z in polygon]
        faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
        faces.extend((i, (i + 1) % count, (i + 1) % count + count, i + count)
                     for i in range(count))
        data = bpy.data.meshes.new(name)
        data.from_pydata(verts, [], faces)
        data.update()
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        soft = obj.modifiers.new("Soft clay edges", "BEVEL")
        soft.width = bevel
        soft.segments = 3
        soft.affect = "EDGES"
        obj.modifiers.new("Weighted clay normals", "WEIGHTED_NORMAL")
        return self.bind(obj, name, bone, color)


def build(rig, colors, vocalist):
    s = Sculpt(rig, colors)
    l, t = s.lump, s.tube
    pelvis = "pelvis"
    head = "head"
    l("Waist", pelvis, "pants", (-.055, 0, 1.28), (.24, .30, .27))
    l("Jacket silhouette", pelvis, "jacket", (.015, 0, 1.67),
      (.25, .39 if vocalist else .35, .47 if vocalist else .50), -9)
    l("Shirt panel", pelvis, "dark", (.164, -.205, 1.66), (.13, .14, .33), -10)
    l("Jacket hem", pelvis, "trim", (.014, -.02, 1.36 if vocalist else 1.28), (.24, .30, .071))
    t("Raised collar", pelvis, "trim", (.19, -.31, 1.98), (.21, -.33, 1.75), (.063, .055), .015)
    t("Left lapel", pelvis, "trim", (-.01, -.317, 1.92), (.16, -.30, 1.58), (.073, .055))
    l("Belt clasp", pelvis, "metal", (.18, -.28, 1.30), (.087, .05, .066))
    l("Stage pin", pelvis, "accent", (-.073, -.343, 1.76), (.055, .030, .055))
    l("Neck", head, "skin", (.053, 0, 2.025), (.137, .15, .19))
    l("Head", head, "skin", (.088, -.017, 2.397),
      (.31 if vocalist else .299, .283 if vocalist else .253, .355 if vocalist else .369), -7)
    l("Jaw", head, "skin", (.235, -.039, 2.235),
      (.237 if vocalist else .177, .220 if vocalist else .181, .183), 8)
    l("Cheek", head, "skin", (.213, -.196, 2.373), (.151, .105, .133), -25)
    l("Nose bridge", head, "skin", (.348, -.137, 2.445), (.137, .104, .131), -30)
    l("Nose tip", head, "skin", (.433, -.156, 2.397), (.108, .08, .069))
    l("Nostril", head, "rose", (.444, -.217, 2.373), (.041, .020, .017), -12)
    l("Ear", head, "skin", (-.091, -.255, 2.381), (.087, .061, .113), -13)
    l("Ear fold", head, "rose", (-.099, -.305, 2.381), (.046, .020, .067), -13)
    l("Earring", head, "metal", (-.103, -.321, 2.284), (.043, .024, .05))
    l("Eye socket", head, "hair", (.260, -.231, 2.487), (.119, .062, .073), 10)
    l("Eye", head, "white", (.278, -.269, 2.481), (.080, .035, .045), 10)
    l("Pupil", head, "dark", (.314, -.298, 2.489), (.030, .018, .035))
    l("Eye reflection", head, "white", (.322, -.314, 2.507), (.011, .008, .012))
    l("Brow", head, "hair_light", (.24, -.269, 2.555), (.136, .048, .038), 16 if not vocalist else -18)
    l("Mouth crease", head, "mouth", (.333, -.191, 2.265), (.119, .061, .031), -9)
    if vocalist:
        l("Open mouth", head, "mouth", (.354, -.205, 2.242), (.098, .057, .057), -12)
        l("Teeth", head, "white", (.359, -.245, 2.261), (.068, .022, .015), -12)
        for x, z, tilt in [(-.22, 2.67, -20), (-.10, 2.81, -26), (.03, 2.88, -29),
                            (.18, 2.86, -35), (.29, 2.78, -45)]:
            color = "hair_light" if x in (-.10, .18) else "hair"
            l("Pompadour clay ridge", head, color, (x, -.026, z), (.116, .26, .234), tilt)
        l("Temple fade", head, "hair", (-.112, -.123, 2.575), (.185, .144, .19), -25)
    else:
        l("Crown", head, "hair", (-.049, .02, 2.65), (.334, .29, .203), 16)
        for x, y, z, tilt, color in [
            (-.24, .15, 2.25, -18, "hair"), (-.21, -.12, 2.29, -20, "hair"),
            (-.34, -.04, 2.22, -31, "hair_light"), (-.27, -.25, 2.29, -14, "hair"),
            (-.17, -.255, 2.45, -8, "hair_light"), (.08, -.216, 2.65, 59, "hair_light"),
            (.22, -.13, 2.649, 62, "hair"),
        ]:
            l("Sculpted hair lock", head, color, (x, y, z),
              (.096, .109, .39 if z < 2.5 else .217), tilt)

    joints = joint_positions(STANCE)
    for side in ("near", "far"):
        upper, forearm, fist, thigh, shin, boot = (
            f"{part}_{side}" for part in ("bicep", "forearm", "fist", "thigh", "shin", "boot"))
        shoulder, elbow = points(joints, upper)
        _, hand = points(joints, forearm)
        hip, knee = points(joints, thigh)
        _, foot = points(joints, shin)
        t("Sleeve", upper, "jacket", shoulder, elbow, (.146, .152), .13)
        t("Sleeve seam", upper, "trim", (shoulder[0], shoulder[1] - .075, shoulder[2]),
          (elbow[0], elbow[1] - .074, elbow[2] + .09), (.070, .079), .055)
        t("Forearm", forearm, "skin" if vocalist else "jacket", elbow, hand, (.113, .127), .098)
        l("Cuff", forearm, "metal" if vocalist else "accent", hand, (.112, .13, .112))
        l("Clay fist", fist, "skin", (hand[0] + .076, hand[1], hand[2]), (.151, .129, .123), -10)
        l("Thumb", fist, "skin", (hand[0] + .023, hand[1] - .066, hand[2] + .067),
          (.081, .084, .058), 18)
        t("Trouser thigh", thigh, "pants", hip, knee, (.167, .156), .14)
        t("Trouser shin", shin, "pants", knee, foot, (.131, .142), .095)
        l("Knee seam", shin, "trim", (knee[0], knee[1] - .099, knee[2]), (.10, .051, .077))
        l("Boot upper", boot, "boots", (foot[0] + .035, foot[1], foot[2] + .09), (.168, .144, .20))
        l("Boot toe", boot, "boots", (foot[0] + .125, foot[1], .134), (.25, .157, .126), 6)
        l("Boot sole", boot, "dark", (foot[0] + .13, foot[1], .049), (.261, .159, .049))
        l("Toe cap", boot, "trim", (foot[0] + .248, foot[1], .122), (.122, .146, .064), 10)
        l("Boot buckle", boot, "metal", (foot[0] + .024, foot[1] - .127, .194), (.052, .039, .05))

    if vocalist:
        x, y, z = joints["hand_far"]
        bottom, top = (x + .07, y, z - .20), (x + .11, y, z + .245)
        t("Mic body", "fist_far", "dark", bottom, top, (.06, .06), .02)
        l("Mic grille", "fist_far", "metal", top, (.100, .095, .117), -12)
        l("Mic grille band", "fist_far", "accent", (top[0] - .007, y, top[2] - .041),
          (.103, .097, .036), -12)
    else:
        build_guitar(s)


def build_guitar(s):
    bone = "instrument"
    # Asymmetric body and forked headstock designed for this fighter.
    body = [(-.74, 1.22), (-.70, 1.46), (-.54, 1.52), (-.39, 1.47),
            (-.22, 1.61), (-.04, 1.68), (-.11, 1.50), (.13, 1.50), (.14, 1.32),
            (.01, 1.19), (.11, 1.04), (-.14, 1.09), (-.33, .96), (-.57, .94), (-.73, 1.05)]
    s.outline("Guitar • carved body", bone, "trim", body, -.428, .151, .053)
    s.outline("Guitar • faceplate", bone, "accent",
              [(-.67, 1.25), (-.57, 1.42), (-.36, 1.41), (-.12, 1.56), (-.19, 1.38),
               (-.03, 1.35), (-.23, 1.22), (-.34, 1.06), (-.58, 1.06)],
              -.521, .03, .021)
    s.outline("Guitar • fretboard", bone, "dark",
              [(-.38, 1.23), (.88, 1.68), (.95, 1.82), (-.43, 1.36)],
              -.530, .084, .020)
    s.outline("Guitar • split headstock", bone, "trim",
              [(.80, 1.67), (1.09, 1.70), (1.25, 1.91), (1.04, 1.88),
               (1.03, 1.98), (.83, 1.85)], -.533, .11, .031)
    for i in range(7):
        x = -.10 + .129 * i
        z = 1.415 + .047 * i
        s.tube("Fret", bone, "metal", (x + .018, -.578, z - .051),
               (x - .017, -.578, z + .048), (.016, .015), .009)
    for x, z in [(-.47, 1.27), (-.30, 1.33), (.97, 1.84), (1.11, 1.86)]:
        s.lump("Guitar hardware", bone, "metal", (x, -.576, z), (.054, .028, .039))
    s.tube("Guitar strap", "pelvis", "dark", (-.54, -.40, 1.40), (.10, -.339, 1.97), (.054, .037), .040)

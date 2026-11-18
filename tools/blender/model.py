"""Original, jointed clay figures. Each mesh stays editable and bound to one bone."""
from math import radians

import bpy
from mathutils import Matrix, Vector


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
    return bind_skin(sculpt, obj, name, color, weights)


def bind_skin(sculpt, obj, name, color, weights):
    """Bind mesh vertices in the rig's rest space to the shared deform bones."""
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


def clay_plate(sculpt, name, bone, color, outline, thickness, radius):
    """A rounded appliqué with an explicit silhouette and thickness vector."""
    border = list(map(Vector, outline))
    depth = Vector(thickness)
    winding = sum(point.cross(border[(i + 1) % len(border)]).dot(depth)
                  for i, point in enumerate(border))
    if winding < 0:
        border.reverse()
    count = len(border)
    verts = [point - depth * .5 for point in border] + [point + depth * .5 for point in border]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces.extend((i, (i + 1) % count, (i + 1) % count + count, i + count)
                 for i in range(count))
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    bevel = obj.modifiers.new("Rounded clay seam", "BEVEL")
    bevel.width, bevel.segments = radius, 3
    obj.modifiers.new("Soft panel normals", "WEIGHTED_NORMAL")
    return sculpt.bind(obj, name, bone, color)


def angled_face(sculpt, name, color, xyz, radii, tilt):
    obj = sculpt.lump(name, "head", color, xyz, radii)
    transform = obj.matrix_world.copy()
    # Rotate around the center of the sculpted feature in world space.
    center = transform.translation.copy()
    obj.matrix_world = Matrix.Translation(center) @ Matrix.Rotation(radians(tilt), 4, "Z") @ Matrix.Translation(-center) @ transform
    return obj


def build_guitar(s):
    bone = "instrument"
    # Asymmetric body and forked headstock designed for this fighter.
    body = [(-.74, 1.22), (-.70, 1.46), (-.54, 1.52), (-.39, 1.47),
            (-.22, 1.61), (-.04, 1.68), (-.11, 1.50), (.13, 1.50), (.14, 1.32),
            (.01, 1.19), (.11, 1.04), (-.14, 1.09), (-.33, .96), (-.57, .94), (-.73, 1.05)]
    parts = [s.outline("Guitar • carved body", bone, "trim", body, -.428, .151, .053)]
    parts.append(s.outline("Guitar • faceplate", bone, "accent",
              [(-.67, 1.25), (-.57, 1.42), (-.36, 1.41), (-.12, 1.56), (-.19, 1.38),
               (-.03, 1.35), (-.23, 1.22), (-.34, 1.06), (-.58, 1.06)],
              -.521, .03, .021))
    parts.append(s.outline("Guitar • fretboard", bone, "dark",
              [(-.38, 1.23), (.88, 1.68), (.95, 1.82), (-.43, 1.36)],
              -.530, .084, .020))
    parts.append(s.outline("Guitar • split headstock", bone, "trim",
              [(.80, 1.67), (1.09, 1.70), (1.25, 1.91), (1.04, 1.88),
               (1.03, 1.98), (.83, 1.85)], -.533, .11, .031))
    for i in range(7):
        x = -.10 + .129 * i
        z = 1.415 + .047 * i
        parts.append(s.tube("Fret", bone, "metal", (x + .018, -.578, z - .051),
                            (x - .017, -.578, z + .048), (.016, .015), .009))
    for x, z in [(-.47, 1.27), (-.30, 1.33), (.97, 1.84), (1.11, 1.86)]:
        parts.append(s.lump("Guitar hardware", bone, "metal", (x, -.576, z), (.054, .028, .039)))
    return parts

"""Fit trim to the rest mesh so the same skinning also bends the trim."""
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

from model import bind_skin


class GarmentSurface:
    def __init__(self, garment, outward_axis, side):
        bpy.context.view_layer.update()
        self.garment = garment
        self.world = garment.matrix_world.copy()
        self.local = self.world.inverted()
        self.out = Vector(tuple(side if n == outward_axis else 0 for n in range(3)))
        self.axes = [n for n in range(3) if n != outward_axis]
        garment.data.calc_loop_triangles()
        self.triangles = [
            tuple(self.world @ garment.data.vertices[i].co for i in tri.vertices)
            for tri in garment.data.loop_triangles if (self.world.to_3x3() @ tri.normal).dot(self.out) > .23
        ]

    def point(self, u, v, offset=0):
        origin = self.out * 2
        origin[self.axes[0]], origin[self.axes[1]] = u, v
        hit, co, _, _ = self.garment.ray_cast(self.local @ origin, self.local.to_3x3() @ -self.out)
        if not hit:
            raise ValueError(f"{self.garment.name}: no support for trim at ({u:.3f}, {v:.3f})")
        return self.world @ co + self.out * offset

    def applique(self, sculpt, name, color, outline, offset, *, bone=None, weights=None):
        """Cut the garment's outward-facing triangles to the trim outline."""
        u, v = self.axes
        clip_coords = [Vector((x, y)) for x, y in outline]
        left, right = min(c.x for c in clip_coords), max(c.x for c in clip_coords)
        low, high = min(c.y for c in clip_coords), max(c.y for c in clip_coords)
        clips = [tuple(clip_coords[i] for i in indices) for indices in tessellate_polygon([clip_coords])]
        verts, faces, indices = [], [], {}
        for tri in self.triangles:
            if (max(p[u] for p in tri) < left or min(p[u] for p in tri) > right
                    or max(p[v] for p in tri) < low or min(p[v] for p in tri) > high):
                continue
            for clip in clips:
                polygon = self._clip(tri, clip)
                if len(polygon) < 3:
                    continue
                area = sum(p[u] * q[v] - q[u] * p[v] for p, q in zip(polygon, polygon[1:] + polygon[:1]))
                if abs(area) < 1e-9:
                    continue
                face = []
                for point in polygon:
                    key = tuple(round(value, 6) for value in point)
                    if key not in indices:
                        indices[key] = len(verts)
                        verts.append(point + self.out * offset)
                    face.append(indices[key])
                if len(set(face)) == len(face):
                    faces.append(tuple(face))
        if not faces:
            raise ValueError(f"{self.garment.name}: no surface for {name}")
        data = bpy.data.meshes.new(name)
        data.from_pydata(verts, [], faces)
        data.update()
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        if weights is None:
            return sculpt.bind(obj, name, bone, color)
        return bind_skin(sculpt, obj, name, color, lambda point: weights(point - self.out * offset))

    def _clip(self, polygon, triangle):
        u, v = self.axes
        a, b, c = triangle
        orientation = 1 if (b - a).cross(c - a) > 0 else -1
        for start, end in zip(triangle, triangle[1:] + triangle[:1]):
            du, dv = end - start

            def distance(point):
                return (du * (point[v] - start.y) - dv * (point[u] - start.x)) * orientation

            cut = []
            for previous, current in zip(polygon[-1:] + polygon[:-1], polygon):
                before, after = distance(previous), distance(current)
                if (before >= 0) != (after >= 0):
                    cut.append(previous.lerp(current, before / (before - after)))
                if after >= 0:
                    cut.append(current)
            polygon = cut
            if len(polygon) < 3:
                break
        return polygon

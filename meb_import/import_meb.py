import os
import struct
from math import radians

import bmesh
import bpy
from mathutils import Euler


class _BinaryStream:
    def __init__(self, data: memoryview):
        self.view = data
        self.pos = 0

    def read(self, n: int):
        start = self.pos
        self.pos += n
        return self.view[start:self.pos]

    def read_str(self):
        end = self.pos
        while end < len(self.view) and self.view[end] != 0:
            end += 1
        s = self.view[self.pos:end].tobytes().decode("utf-8", errors="replace")
        self.pos = end + 1
        return s

    def align4(self):
        pad = (4 - (self.pos % 4)) % 4
        self.pos += pad

    def u8(self):
        v = struct.unpack_from("B", self.view, self.pos)[0]
        self.pos += 1
        return v

    def u16(self):
        v = struct.unpack_from("<H", self.view, self.pos)[0]
        self.pos += 2
        return v

    def s16(self):
        v = struct.unpack_from("<h", self.view, self.pos)[0]
        self.pos += 2
        return v

    def u32(self):
        v = struct.unpack_from("<I", self.view, self.pos)[0]
        self.pos += 4
        return v

    def s32(self):
        v = struct.unpack_from("<i", self.view, self.pos)[0]
        self.pos += 4
        return v

    def f32(self):
        v = struct.unpack_from("<f", self.view, self.pos)[0]
        self.pos += 4
        return v


def _read_meb(path):
    with open(path, "rb") as f:
        data = f.read()
    stream = _BinaryStream(memoryview(data))

    header = stream.read(8)
    part_name = stream.read_str()
    stream.align4()

    num_verts = stream.u32()
    num_props = stream.u32()
    num_prims = stream.u32()
    stream.pos += 40

    has_skin = header[4] == 1
    if has_skin:
        num_bones = stream.u32()
        num_chars = stream.u32()
        stream.pos += num_chars
        stream.pos += num_bones * 48

    vprop_ids = []
    for _ in range(num_props):
        r1 = stream.u32()
        r2 = stream.u32()
        r3 = stream.u32()
        vprop_ids.append((r1, r2, r3))

    positions = []
    normals = []
    colors = []
    uvs_list = []
    tangents = []
    bone_weights = []

    for pid in vprop_ids:
        tag = pid[0] * 1000 + pid[1] * 100 + pid[2]

        if tag == 200:
            positions = [(stream.f32(), stream.f32(), stream.f32()) for _ in range(num_verts)]

        elif tag == 220:
            normals = [(stream.f32(), stream.f32(), stream.f32()) for _ in range(num_verts)]

        elif tag == 460:
            colors = [
                (stream.u8() / 255, stream.u8() / 255, stream.u8() / 255, stream.u8() / 255)
                for _ in range(num_verts)
            ]

        elif tag == 461:
            stream.pos += num_verts * 4

        elif tag in (240, 250):
            stream.pos += num_verts * 12

        elif 130 <= tag <= 134:
            uvs = [(stream.f32(), 1.0 - stream.f32()) for _ in range(num_verts)]
            uvs_list.append(uvs)

        elif 230 <= tag <= 234:
            uvs = [(stream.f32(), 1.0 - stream.f32()) for _ in range(num_verts)]
            stream.pos += num_verts * 4
            uvs_list.append(uvs)

        elif tag == 33:
            stream.pos += num_verts * 4

        elif tag == 580:
            stream.pos += num_verts * 4

        elif tag == 310:
            stream.pos += num_verts * 16

    materials = []
    faces_by_mat = []
    for _ in range(num_prims):
        mex_path = stream.read_str()
        mat_name = os.path.splitext(os.path.basename(mex_path))[0]
        stream.align4()
        stream.pos += 4
        num_faces = stream.s32()

        if has_skin:
            num_shorts = stream.s32()
            stream.pos += num_shorts * 2

        stream.align4()

        face_indices = []
        for _ in range(num_faces):
            i1 = stream.u16()
            i2 = stream.u16()
            i3 = stream.u16()
            face_indices.append((i3, i2, i1))

        stream.align4()
        stream.pos += 4
        stream.pos += 40

        materials.append(mat_name)
        faces_by_mat.append(face_indices)

    return {
        "name": part_name,
        "positions": positions,
        "normals": normals,
        "colors": colors,
        "uvs": uvs_list,
        "materials": materials,
        "faces_by_mat": faces_by_mat,
    }


def _build_mesh(data, part_name, rotate, hide_lodb, hide_lodc):
    verts = data["positions"]
    norms = data["normals"]

    if not verts:
        return None

    verts_swapped = [(v[0], v[2], v[1]) for v in verts]
    norms_swapped = [(n[0], n[2], n[1]) for n in norms] if norms else None

    poly_offsets = []
    flat_polys = []
    for faces in data["faces_by_mat"]:
        poly_offsets.append(len(flat_polys))
        flat_polys.extend(faces)

    mesh = bpy.data.meshes.new(name=part_name)
    mesh.from_pydata(verts_swapped, [], flat_polys)
    mesh.validate()

    if norms_swapped:
        mesh.normals_split_custom_set_from_vertices(norms_swapped)

    obj = bpy.data.objects.new(part_name, mesh)

    if data["uvs"]:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        uv_layers = []
        for i in range(len(data["uvs"])):
            uv_layers.append(bm.loops.layers.uv.new(f"UVMap{i}"))
        for face in bm.faces:
            for loop in face.loops:
                for uv_layer, uvs in zip(uv_layers, data["uvs"]):
                    loop[uv_layer].uv = uvs[loop.vert.index]
        if data["colors"]:
            col_layer = bm.verts.layers.color.new("Color")
            for vert in bm.verts:
                vert[col_layer] = data["colors"][vert.index]
        bm.to_mesh(mesh)
        bm.free()

    if data["materials"]:
        mat_idx = 0
        for mat_name, faces, offset in zip(data["materials"], data["faces_by_mat"], poly_offsets):
            mat = bpy.data.materials.get(mat_name)
            if mat is None:
                mat = bpy.data.materials.new(mat_name)
            obj.data.materials.append(mat)
            for i in range(len(faces)):
                mesh.polygons[offset + i].material_index = mat_idx
            mat_idx += 1

    if rotate:
        obj.rotation_euler = Euler((radians(180), radians(180), radians(180)), "XYZ")

    if hide_lodb and "LODB" in part_name:
        obj.hide_set(True)

    if hide_lodc and "LODC" in part_name:
        obj.hide_set(True)

    return obj


def import_part(path, rotate, ignore_damage, hide_lodb, hide_lodc):
    basename = os.path.splitext(os.path.basename(path))[0]

    if "dmg" in basename.lower() and ignore_damage:
        return

    data = _read_meb(path)
    if data is None:
        return

    data["name"] = basename
    if "dmg" in basename.lower():
        data["name"] += "_DMG"

    obj = _build_mesh(data, data["name"], rotate, hide_lodb, hide_lodc)
    if obj is None:
        return

    col_name = "Shift2_Import"
    if col_name not in bpy.data.collections:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections[col_name]
    col.objects.link(obj)


def load(filepath, importall, rotate, ignore_damage, hide_lodb, hide_lodc):
    if importall:
        directory = os.path.dirname(filepath)
        for entry in sorted(os.listdir(directory)):
            if entry.lower().endswith(".meb"):
                import_part(
                    os.path.join(directory, entry),
                    rotate, ignore_damage, hide_lodb, hide_lodc,
                )
    else:
        import_part(filepath, rotate, ignore_damage, hide_lodb, hide_lodc)

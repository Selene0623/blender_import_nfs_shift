bl_info = {
    "name": "NFS Shift 2 .meb Importer",
    "author": "auvy + ForzaTech-extraction-tools pattern",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "File > Import > Shift 2 mesh (.meb)",
    "description": "Import Need for Speed Shift 2 Unleashed .meb mesh files",
    "category": "Import-Export",
}

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


class ImportMEB(Operator, ImportHelper):
    bl_idname = "import_scene.meb"
    bl_label = "Import Shift 2 mesh (.meb)"
    bl_options = {"UNDO"}

    filename_ext = ".meb"
    filter_glob: StringProperty(default="*.meb", options={"HIDDEN"})

    importall: BoolProperty(
        name="Import entire folder",
        description="Import all .meb files in this folder",
        default=False,
    )
    rotate: BoolProperty(
        name="Rotate 180°",
        description="Apply 180° rotation on all axes",
        default=True,
    )
    ignore_dmg: BoolProperty(
        name="Ignore damage parts",
        description="Skip _DMG parts",
        default=True,
    )
    hide_lodb: BoolProperty(
        name="Hide LODB parts",
        description="Hide imported LODB meshes",
        default=True,
    )
    hide_lodc: BoolProperty(
        name="Hide LODC parts",
        description="Hide imported LODC meshes",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "importall")
        layout.prop(self, "rotate")
        layout.prop(self, "ignore_dmg")
        layout.prop(self, "hide_lodb")
        layout.prop(self, "hide_lodc")

    def execute(self, context):
        from . import import_meb
        import_meb.load(
            self.filepath,
            importall=self.importall,
            rotate=self.rotate,
            ignore_damage=self.ignore_dmg,
            hide_lodb=self.hide_lodb,
            hide_lodc=self.hide_lodc,
        )
        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(ImportMEB.bl_idname, text="Shift 2 mesh (.meb)")


def register():
    bpy.utils.register_class(ImportMEB)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ImportMEB)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()

bl_info = {
    "name": "Shift 2 .vhf mesh transforms",
    "blender": (2, 80, 0),
    "category": "Import",
}

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class importMEB(Operator, ImportHelper):
    """Import parameters from Shift 2 VHF format (.vhf)"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "import_params.vhf"
    bl_label = "Import Shift 2 (*.vhf)"
    bl_options = {'UNDO'}  # Enable undo for the operator.
    
    filename_ext = '.vhf'
    filter_glob = StringProperty(
        default="*.vhf", 
        options={'HIDDEN'}
    )
    rotate = BoolProperty(
        name="Apply rotate transform", 
        description="Apply rotate transform", 
        default=True)

    offset = BoolProperty(
        name="Apply offset transform", 
        description="Apply offset transform", 
        default=True)
    
    col_name = StringProperty(
        name="Name of collection", 
        description="Folder where mesh files are", 
        default="Coll")
    
    def draw(self, context):
        layout = self.layout
        sub = layout.row()
        sub.prop(self, "col_name")
        sub = layout.row()
        sub.prop(self, "rotate")
        sub = layout.row()
        sub.prop(self, "offset")
    

    def execute(self, context):        # execute() is called when running the operator.
        from . import import_vhf

        import_vhf.load(self.filepath, self.col_name, self.rotate, self.offset)

        return {'FINISHED'}






def menu_func(self, context):
    self.layout.operator(importMEB.bl_idname, text="Shift 2 transform (.vhf)")

def register():
    from bpy.utils import register_class
    register_class(importMEB)
    
    bpy.types.TOPBAR_MT_file_import.append(menu_func)  # Adds the new operator to an existing menu.

def unregister():
    from bpy.utils import unregister_class
    unregister_class(importMEB)

    bpy.types.TOPBAR_MT_file_import.append(menu_func)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
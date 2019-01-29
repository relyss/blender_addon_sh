# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#----------------------------------------------------------
# __init__.py
#----------------------------------------------------------

bl_info = {
    "name": "Stonehearth Add-On",
    "author": "Voxel Pirate",
    "version": (0, 9, 1),
    "blender": (2, 6, 9),
    "location": "File > Import-Export",
    "description": "Adding functionality to use Blender for Stonehearth",
    "warning": '',
    "wiki_url": "http://www.stonehearth.de/weblog/blender",
    "tracker_url": "http://www.stonehearth.de/weblog/blender",
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    if 'export_stonehearth' in locals():
        imp.reload(export_stonehearth)
    if 'import_stonehearth' in locals():
        imp.reload(import_stonehearth)

import bpy
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper
from math import radians

from . import operations_stonehearth

global_imported_file_type = 'none'                                                                                                             # Type ("skeleton", "animation" or "meta") related to the imported file.
global_imported_skeleton_data = []                                                                                                             # Mesh and armature data from an imported skeleton-file.
global_skeleton_name = 'none'                                                                                                                  # Name of the imported skeleton-file (without file-extension).
global_animation_name = 'none'                                                                                                                 # Name of the imported animation-file (without file-extension).
global_scene_mesh_amount = 0                                                                                                                   # Amount of meshes in the scene.
global_scene_armature_amount = 0                                                                                                               # Amount of armatures in the scene.
global_error_code = "no"                                                                                                                       # Error Code.
global_meshes_not_found = 0                                                                                                                    # Amount of meshes in the scene of which the name was not found in a skeleton file.
global_amount_bones_added = 0                                                                                                                  # Amount of bones added in scene based on file-input.
global_amount_pivots_adjusted = 0                                                                                                              # Amount of pivots adjusted.
global_animation_status = "no"                                                                                                                 # Includes the error message if root bone was not found to be moved in "Preparing Animation".
global_skeleton_status = "no"                                                                                                                  # Includes the error message if "Preparing Skeleton" did not work out.
global_imported_meta_helperBones = []                                                                                                          # Information on helperBones from an imported meta-file.
global_imported_meta_hierarchy = []                                                                                                            # Information on parent-child-relationships between meshes and armatures from an imported meta-file.
global_meta_name = 'none'                                                                                                                      # Name of the imported meta-file (without file-extension).
global_offset_data = []                                                                                                                        # Matrix containing the offset for animations (male/female).

#
#    Processing requests through custom menu and calling of related functions from "operations_stonehearth.py"
#

# Runs evaluation of scene vs. file:

class EVALUATE_SCENE(bpy.types.Operator):
    bl_idname = "object.validate_scene"
    bl_label = "Validate Scene"

    def execute(self, context):
        global global_scene_mesh_amount
        global global_scene_armature_amount
        global global_error_code
        global global_meshes_not_found
        global global_amount_bones_added
        global global_amount_pivots_adjusted
        global global_meta_name
        global global_imported_skeleton_data
        global global_imported_meta_helperBones
        global global_skeleton_status
        global global_skeleton_name

        if global_skeleton_name != 'none':                                                                                                     # Condition true if skeleton was loaded.
            global_scene_mesh_amount, global_scene_armature_amount = operations_stonehearth.CALCULATE_OBJECTS_IN_SCENE()                       # Counting how many objects are in the scene.
            if len(bpy.data.objects) < len(global_imported_skeleton_data):                                                                     # If objects in scene < objects in file...
                global_meshes_not_found = operations_stonehearth.VERIFY_NAMES_IN_SKELETON(global_imported_skeleton_data)                       # ... checking if names of objects in scene are included in file.
                global_error_code = "no"
                if global_meshes_not_found == 0:                                                                                                                                # Condition true if all scene meshes have been found in the skeleton file.
                    global_amount_bones_added = operations_stonehearth.ADD_ARMATURES(global_imported_skeleton_data, global_imported_meta_helperBones, global_meta_name)         # Adding armatures based on objects which are in the file but not in scene.
                    global_amount_pivots_adjusted = operations_stonehearth.ADJUST_PIVOTS(global_imported_skeleton_data)                                                         # Adjusting pivots based on values in the file.
                    operations_stonehearth.SET_HIERARCHY(global_imported_meta_hierarchy)                                                                                        # Set relationships / hierarchy between objects.
                    global_skeleton_status = "ok"
                else:
                    global_error_code = "Object-names in scene not found in skeleton-file!"                                                    # Name of mesh in scene not found in file.
                    global_amount_bones_added = 0
                    global_skeleton_status = "bad"
            else:
                global_error_code = "Scene requires less objects than in skeleton-file!"                                                       # Amount of objects in scene is larger than amount of objects in file.
                global_skeleton_status = "bad"
        else:
            global_error_code = "Is a skeleton-file loaded?"                                                                                   # No skeleton was loaded.
            global_skeleton_status = "bad"

        return {'FINISHED'}

# Prepare scene for animation:

class PREPARE_ANIMATION(bpy.types.Operator):
    bl_idname = "object.prepare_animation"
    bl_label = "Prepare Animation"

    def execute(self, context):
        global global_animation_status
        global_animation_status = operations_stonehearth.BONE_ROOT_ORIGIN()                                                                    # Moves model to the center of the scene and resets rotation.

        return {'FINISHED'}

# Reste imported meta-file:

class RESET_META(bpy.types.Operator):
    bl_idname = "object.reset_meta"
    bl_label = "Reset Meta-Data"

    def execute(self, context):
        global global_imported_meta_helperBones
        global global_imported_meta_hierarchy
        global global_meta_name
        global global_skeleton_status
        global global_animation_status

        global_imported_meta_helperBones = []
        global_imported_meta_hierarchy = []
        global_meta_name = 'none'        
        global_skeleton_status = "no"
        global_animation_status = "no"
        return {'FINISHED'}

# Reste imported skeleton-file:

class RESET_SKELETON(bpy.types.Operator):
    bl_idname = "object.reset_skeleton"
    bl_label = "Reset Skeleton-Data"

    def execute(self, context):
        global global_imported_skeleton_data
        global global_skeleton_name
        global global_scene_mesh_amount
        global global_scene_armature_amount 
        global global_skeleton_status
        global global_animation_status

        global_imported_skeleton_data = []
        global_skeleton_name = 'none'
        global_scene_mesh_amount = 0
        global_scene_armature_amount = 0
        global_skeleton_status = "no"
        global_animation_status = "no"
        return {'FINISHED'}

# Delete existing animation:

class DELETE_ANIMATION(bpy.types.Operator):
    bl_idname = "object.delete_animation"
    bl_label = "Delete Animation"

    def execute(self, context):
        global global_animation_name

        operations_stonehearth.ANIMATION_DELETE()
        global_animation_name = 'none'

        return {'FINISHED'}

# Add custom helper bone:

class ADD_CUSTOM_HELPER_BONE(bpy.types.Operator):
    bl_idname = "object.add_custom_helper_bone"
    bl_label = "Add Custom Helper Bone"

    def execute(self, context):
        scene = context.scene
        bone_location = (0, 0, 0)
        bone_rotation = (radians(90), 0, 0)
        bone_identifier = scene.helper_bone_string
        bone_name = scene.helper_bone_string
        bone_x = scene.helper_bone_x
        bone_z = scene.helper_bone_z
        bone_head = (0, 0, scene.helper_bone_head)
        bone_tail = (0, 0, scene.helper_bone_tail)

        object_found = 0                                                                                                                      # Sets counter to 0 which will indicate that helper bone does not exist.

        for single_object in bpy.data.objects:                                                                                                # Loop through all objects in scene.
            if single_object.name == bone_identifier and single_object.type == "ARMATURE":                                                    # True if actual object has the same name as the "planned" helper bone and is of type "ARMATURE".
                object_found = 1                                                                                                              # Counter is changed to 1 to indicate thet helper bone exists.
                operations_stonehearth.ADJUST_ARMATURES(bone_identifier, bone_name, bone_x, bone_z, bone_head, bone_tail)                     # Call of function to change values for existing helper bone.
        
        if object_found == 0:                                                                                                                 # If helper bone is not found in scene, new bone will be created.
            operations_stonehearth.ADD_ARMATURES_HELPER(bone_location, bone_rotation, bone_identifier, bone_name, bone_x, bone_z, bone_head, bone_tail)  

        return {'FINISHED'}

#
#    Processing the UI of the add-on.
#

# Class "OPERATIONS_PANEL" defines the look and functionality of the custom menu (UI):

class OPERATIONS_PANEL(bpy.types.Panel):
    bl_label = "Stonehearth UI"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"                                                                                                                       # Assignes the custom menu to the window "Scene".

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.label(" Standard-Workflow:", icon = 'OOPS')
        box = layout.box()
        box.label(" Skeleton-file loaded: " + str(global_skeleton_name))
        box.label(" Meta-file loaded: " + str(global_meta_name))

        if global_offset_data:
            global_offset_message = "yes"
        else: 
            global_offset_message = "none"

        box.label(" Offset calculated: " + global_offset_message)
        box.label(" Animation-file loaded: " + str(global_animation_name))

        button_check = box.row()
        button_check.active = False
        button_check.operator("object.validate_scene", text = "Prepare Skeleton", icon = "OUTLINER_OB_ARMATURE")

        if global_imported_skeleton_data:
            button_check.active = True

        box.operator("object.prepare_animation", text = "Prepare Animation", icon = "OUTLINER_OB_CAMERA")

        row = box.row(align=True)

        if global_skeleton_status == "no":
            row.label(" Skeleton", icon = "MATSPHERE")
        elif global_skeleton_status == "ok":
            row.label(" Skeleton", icon = "COLOR_GREEN")
        else:
            row.label(" Skeleton", icon = "COLOR_RED")
        if global_animation_status == "no":
            row.label(" Animation", icon = "MATSPHERE")
        elif global_animation_status == "ok":
            row.label(" Animation", icon = "COLOR_GREEN")
        else:
            row.label(" Animation", icon = "COLOR_RED")

        layout.label( "Reset:")
        row = layout.row()
        row.operator("object.reset_skeleton", text = "Skeleton")
        row.operator("object.reset_meta", text = "Meta")

        layout.label( "Delete:")
        row = layout.row()
        row.operator("object.delete_animation", text = "Delete Animation")

        row = layout.row()
        layout.prop(scene, 'custom_helper_switch')

        if scene.custom_helper_switch:
            layout.label(" Custom Helper Bones:", icon = 'BONE_DATA')
            box = layout.box()
            box.prop(scene, 'helper_bone_string')
            row = box.row()
            row.prop(scene, 'helper_bone_x')
            row.prop(scene, 'helper_bone_tail')
            row = box.row()
            row.prop(scene, 'helper_bone_z')
            row.prop(scene, 'helper_bone_head')
            row = box.row()
            row.operator("object.add_custom_helper_bone", text = "Add / Adjust Bone")

        row = layout.row()
        layout.prop(scene, 'debugging_switch')

        if scene.debugging_switch:
            layout.label(" Debugging Info:", icon = 'SCRIPT')
            box = layout.box()
            box.label(" Objects in file: " + (str(len(global_imported_skeleton_data))))
            box.label(" Objects in scene: %s Meshes and %s Bones" %(str(global_scene_mesh_amount), str(global_scene_armature_amount)))
            box.label(" Objects in scene but not in file: " + str(global_meshes_not_found))
            box.label(" Armatures added in scene: " + str(global_amount_bones_added))
            box.label(" Skeleton error: "  + global_error_code)
            box.label(" Animation error: " + global_animation_status)

            box.label(" File loaded last: " + global_imported_file_type)
            box.label(" Skeletton-data: " + str(global_imported_skeleton_data))
            box.label(" Helpers-data: " + str(global_imported_meta_helperBones))
            box.label(" Relations-data: " + str(global_imported_meta_hierarchy))

            for single_object in bpy.data.objects:
                if single_object.type == "LAMP":
                                box.label(" Lamp detected - could cause issues!")
                if single_object.type == "CAMERA":
                                box.label(" Camera detected - could cause issues!")

#
#    Processing the import of skeleton and animation data into Blender - utilizing file "import_stonehearth.py".
#

# Class "IMPORT_STONEHEARTH" defines and draws the import-options and includes the process logic:

class IMPORT_STONEHEARTH(bpy.types.Operator, ImportHelper):
    bl_idname = "import.stonehearth"
    bl_label = "Import File"

    filename_ext = ".json"

    filter_glob = StringProperty(
        default="*.json", 
        options={'HIDDEN'}
        )

    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for importing the Stonehearth JSON-file", 
        maxlen= 1024, default= "")

    selection_import_offset = BoolProperty(
        name="Import skeleton for offset",
        description="If skeleton already loaded, next skeleton will be used to calculate animation offset (male/female)",
        default=False,
        )

    # Defines what happens if import-button is clicked - calls function "PROCESS_IMPORT" in the file "import_stonehearth.py":

    def execute(self, context):
        from . import import_stonehearth

        global global_imported_file_type
        global global_imported_skeleton_data
        global global_skeleton_name
        global global_animation_name
        global global_imported_meta_helperBones
        global global_imported_meta_hierarchy                                                                                                           
        global global_meta_name
        global global_offset_data

        local_imported_skeleton_data = []
        local_offset_data = []
        local_imported_meta_helperBones = []
        local_imported_meta_hierarchy = []

        selection_import_offset_value=self.selection_import_offset

        global_imported_file_type, local_offset_data, local_imported_skeleton_data, local_imported_meta_helperBones, local_imported_meta_hierarchy = import_stonehearth.PROCESS_IMPORT(self.properties.filepath, selection_import_offset_value,global_imported_skeleton_data)         # Function "PROCESS_IMPORT" is called (file "import_stonehearth.py") and returned values are stored.

        if local_imported_skeleton_data:                                                                                                       # If returned value is empty, existing skeleton data should not be overwritten.
            global_imported_skeleton_data = local_imported_skeleton_data
        if local_imported_meta_helperBones:                                                                                                    # If returned value is empty, existing helperBones should not be overwritten.
            global_imported_meta_helperBones = local_imported_meta_helperBones
        if local_imported_meta_hierarchy:                                                                                                      # If returned value is empty, existing hierarchy should not be overwritten.
        	global_imported_meta_hierarchy = local_imported_meta_hierarchy
        if local_offset_data:                                                                                                                  # If returned value is empty, no offset was calculated.
        	global_offset_data = local_offset_data
        else:                                                                                                                                  # ... if value is empty, set string to []. 
            global_offset_data = []

        if global_imported_file_type == "skeleton":                                                                                            # If loaded file is a skeleton-file the name can be used to identify the skeleton-name. 
            global_skeleton_name = bpy.path.display_name_from_filepath(self.properties.filepath)                                               # Returned file-name (without extension via filepath) is stored in "global_skeleton_name.
        elif global_imported_file_type == "frames":                                                                                            # Otherwise loaded file is of type "animation"...
            global_animation_name = bpy.path.display_name_from_filepath(self.properties.filepath)                                              # ... and can be stored in variable "global_animation_name"...
        elif global_imported_file_type == "meta":                                                                                              # ... or of type "meta"...
        	global_meta_name = bpy.path.display_name_from_filepath(self.properties.filepath)                                                   # ... and can be stored in variable "global_meta_name".

        return {'FINISHED'}

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.label(text="Calculate offset:")

        box = layout.box()
        checkbox_check = box.row()
        checkbox_check.active = False
        checkbox_check.prop(self, "selection_import_offset", expand=True)                                                                      # Display checkbox as input to import skeleton as offset-file. 

        if global_imported_skeleton_data:
            checkbox_check.active = True

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#
#    Processing the export of skeleton and animation data into a format readable by Stonehearth - utilizing file "export_stonehearth.py".
#

# Class "EXPORT_STONEHEARTH" defines and draws the export-options and includes the process logic:

class EXPORT_STONEHEARTH(bpy.types.Operator, ExportHelper):
    bl_idname = "export.stonehearth"
    bl_label = "Export File"                                                                                                                   # Name of the "save"-button and headline for the export-options.

    filename_ext = ".json"                                                                                                                     # Assign file-ending.

    filter_glob = StringProperty(
        default="*.json", 
        options={'HIDDEN'}
        )                                                                                                                                      # Search folder for files with the relevant file-extension. 

    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for exporting the Stonehearth JSON-file", 
        maxlen= 1024, default= ""
        )

    export_selection = EnumProperty(
        name="Selection",
        items=(
           	('1', 'Skeleton', 'Export Skeleton', 'OUTLINER_OB_ARMATURE', 1),
           	('2', 'Meta', 'Export Meta-Data', 'OUTLINER_OB_SURFACE', 2),
            ('3', 'Animation', 'Export Animation', 'OUTLINER_OB_CAMERA', 3),
            ),
        )                                                                                                                                      # Defining radio-button with the options "Skeleton", "Meta" or "Animation".

    export_selection_animation = BoolProperty(
        name="Export taking offset into account",
        description="If offset was calculated, export will be adjusted by it (male/female)",
        default=False,
        )

    # Defines what happens if export-button is clicked - calls function "PROCESS_EXPORT" in file "export_stonehearth.py":

    def execute(self, context):
        from . import export_stonehearth

        global global_offset_data 

        export_selection_animation_value=self.export_selection_animation

        export_stonehearth.PROCESS_EXPORT(self.properties.filepath, self.export_selection, self.export_selection_animation, global_offset_data)      # Calls the function "PROCESS_EXPORT" in file "export_stonehearth.py" and handing over parameters.
        return {'FINISHED'}

    # Draws options-layout (including buttons) in the export-view:

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        box = layout.box()
        row = box.row()
        row.prop(self, "export_selection", expand=True)

        row = box.row()
        if self.export_selection == '3':
            row.label(text="Apply offset:")   

            checkbox_check = box.row()
            checkbox_check.active = False
            checkbox_check.prop(self, "export_selection_animation", expand=True)

            if global_offset_data:
                checkbox_check.active = True

#            row.prop(self, "export_selection_animation")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#
#    Registration
#

def menu_func_import(self, context):
    self.layout.operator(IMPORT_STONEHEARTH.bl_idname, text="Stonehearth (.json)")

def menu_func_export(self, context):
    self.layout.operator(EXPORT_STONEHEARTH.bl_idname, text="Stonehearth (.json)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

    bpy.types.Scene.debugging_switch = BoolProperty(
        name="Debugging Info (on / off)",
        description="Activate to show debugging information",
        default=False)

    bpy.types.Scene.custom_helper_switch = BoolProperty(
        name="Custom Helper Bones (on / off)",
        description="Activate to add custom helper bones",
        default=False)

    bpy.types.Scene.helper_bone_string = StringProperty(
        name="Name Bone",
        default="< enter name >")

    bpy.types.Scene.helper_bone_x = FloatProperty(
        name = "X", 
        description = "X Value",
        default = 3,
        min = .5,
        max = 50)

    bpy.types.Scene.helper_bone_z = FloatProperty(
        name = "z", 
        description = "Z Value",
        default = 3,
        min = .5,
        max = 50)

    bpy.types.Scene.helper_bone_tail = FloatProperty(
        name = "Tail", 
        description = "Tail Value",
        default = -3,
        min = -50,
        max = .5)

    bpy.types.Scene.helper_bone_head = FloatProperty(
        name = "Head", 
        description = "Head Value",
        default = 3,
        min = .5,
        max = 50)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
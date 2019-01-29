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
# operations_stonehearth.py
#----------------------------------------------------------

import bpy
from math import radians

# "ANIMATION_DELETE" deletes all keyframes in scene:

def ANIMATION_DELETE():
    bpy.data.scenes[0].frame_set(1)
    for single_object in bpy.data.objects:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = single_object                                                                                    # Activate object to avoid confusion.
        single_object.select = True 
        bpy.context.active_object.animation_data_clear()

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 25

# "BONE_ROOT_ORIGIN" moves the origin of the bone "root" to the center of the scene:

def BONE_ROOT_ORIGIN():
    local_animation_status = ''

    if bpy.context.mode != 'OBJECT':                                                                                                        # Check if Blender is in "Object-Mode"...
        bpy.ops.object.mode_set(mode='OBJECT')                                                                                              # ... and if not, set it (to avoid issues).
    for single_object in bpy.data.objects:                                                                                                  # Loop through all objects in a scene.
        single_object.rotation_mode="QUATERNION"                                                                                            # Change rotation mode for objects to "Quaternion".
        bpy.ops.object.transform_apply({'selected_editable_objects':[single_object]}, rotation=True)                                        # Remove rotation from objects.

    for single_object in bpy.data.objects:                                                                                                  # Loop through all objects in a scene.
        if single_object.name == 'root' and single_object.type == 'ARMATURE':                                                               # Condition is true if selected object is a bone named "root".
            single_object.location = [0, 0, 0]                                                                                              # Move location of root-bone to center.
            local_animation_status = "ok"
            break
    
    if local_animation_status != "ok":                                                                                                      # Check if root-bone was found...
        local_animation_status = "No root bone found!"                                                                                      # ... otherwise change return value.

    return(local_animation_status)

# "ADJUST_PIVOTS_HELPER" will move cursor to location handed over during call of the function:

def ADJUST_PIVOTS_HELPER(x, y, z):
    bpy.context.scene.cursor_location.x = x
    bpy.context.scene.cursor_location.y = y
    bpy.context.scene.cursor_location.z = z

# "ADJUST_PIVOTS" will set the origins / pivots of the objects:

def ADJUST_PIVOTS(local_imported_skeleton_data):
    local_amount_pivots_adjusted = 0

    for single_object in bpy.data.objects:                                                                                                  # Loop runs for each object in the scene...
        if single_object.type == "MESH" or single_object.type == "ARMATURE":                                                                # ... and checks if condition is true, i.e. if object is "MESH" or "ARMATURE".
            for single_entry in local_imported_skeleton_data:                                                                               # Loop runs once for each element in the string "local_imported_skeleton_data".
                words = single_entry.split(',')                                                                                             # Element in string is split, i.e. will result in 4 entries.
                if single_object.name == str(words[0]):                                                                                     # First element contains the name of a bone which is compared to object-name.
                    local_amount_pivots_adjusted += 1                                                                                       # If existance is confirmed, counter goes up by one.
                    ADJUST_PIVOTS_HELPER(float(words[1]), float(words[2]), float(words[3]))                                                 # Function "ADJUST_PIVOTS_HELPER" is called with values of entries 2, 3 and 4. 

            bpy.ops.object.select_all(action='DESELECT')                                                                                    # Deselects all objects in the scene.
            bpy.context.scene.objects.active = single_object                                                                                # Object assigned to "single_object" is set as active...
            single_object.select = True                                                                                                     # ... and selected.
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')                                                                                 # Function is called which sets origin to location of cursor.

    return(local_amount_pivots_adjusted)

# "CALCULATE_OBJECTS_IN_SCENE" returns amount of meshes and armatures available in the scene:

def CALCULATE_OBJECTS_IN_SCENE():
    local_scene_mesh_amount = 0
    local_scene_armature_amount = 0

    for single_object in bpy.data.objects:                                                                                                  # Loop through all objects in scene.
        if single_object.type == ('MESH'):                                                                                                  # If object is of type "MESH"...
            local_scene_mesh_amount += 1                                                                                                    # ... related counter goes up by one.
        elif single_object.type == ('ARMATURE'):                                                                                            # If object is of type "ARMATURE"...
            local_scene_armature_amount += 1                                                                                                # ... another counter is increased.

    return (local_scene_mesh_amount, local_scene_armature_amount)

# "VERIFY_NAMES" verifies if all names of meshes in scene, are also in the imported skeleton-file:

def VERIFY_NAMES_IN_SKELETON(local_imported_skeleton_data):
    local_meshes_not_found = 0

    for single_object in bpy.data.objects:                                                                                                  # Loop through all objects in scene.
        name_found_identifier = 0
        for single_entry in local_imported_skeleton_data:                                                                                   # Loop through all entries in the variable "local_imported_skeleton_data".
            words = single_entry.split(',')                                                                                                 # Entries are split into "words".
            if (single_object.type == ('MESH') or single_object.type == ('ARMATURE')) and single_object.name == words[0]:                   # If actual object is of type "MESH" or "ARMATURE" and exisists in words...
                name_found_identifier = 1                                                                                                   # ... existence is confirmed.
                break
        if name_found_identifier != 1:                                                                                                      # Condition is true if existence is not confirmed...
            local_meshes_not_found += 1                                                                                                     # ... which increases a counter y one.

    return (local_meshes_not_found)

# "ADJUST_ARMATURES" adjusts bone for each call:

def ADJUST_ARMATURES(bone_identifier, bone_name, bone_x, bone_z, bone_head, bone_tail):
    if bpy.context.mode != 'OBJECT':                                                                                                        # Check if Blender is in "Object-Mode"...
        bpy.ops.object.mode_set(mode='OBJECT')                                                                                              # ... and if not, set it (to avoid issues).

    bpy.context.scene.objects.active = bpy.data.objects[bone_identifier]                                                                    # Activate object to avoid confusion.
    bpy.data.objects[bone_identifier].select = True  

    bpy.data.objects[bone_identifier].data.draw_type="BBONE"                                                                                # Switch look of bones to "BBone".
    bpy.ops.object.mode_set(mode='EDIT')                                                                                                    # Switch to Edit-Mode (following code will not work in Object-Mode).
    bpy.data.objects[bone_identifier].data.edit_bones[bone_name].bbone_x = bone_x                                                           # Set x-size of Bbone.
    bpy.data.objects[bone_identifier].data.edit_bones[bone_name].bbone_z = bone_z                                                           # Set z-size of Bbone.
    bpy.data.objects[bone_identifier].data.edit_bones[bone_name].head = bone_head                                                           # Set location of head (one side of the bone).
    bpy.data.objects[bone_identifier].data.edit_bones[bone_name].tail = bone_tail                                                           # Set location of tail (other side of the bone).
    bpy.ops.object.mode_set(mode='OBJECT')                                                                                                  # Switch back to Object-Mode.

# "ADD_ARMATURES_HELPER" creates bone for each call:

def ADD_ARMATURES_HELPER(bone_location, bone_rotation, bone_identifier, bone_name, bone_x, bone_z, bone_head, bone_tail):
    if bpy.context.mode != 'OBJECT':                                                                                                        # Check if Blender is in "Object-Mode"...
        bpy.ops.object.mode_set(mode='OBJECT')                                                                                              # ... and if not, set it (to avoid issues).
    bpy.ops.object.select_all(action='DESELECT')                                                                                            # Deselecting all objects (to avoid confusion).
    bpy.ops.object.armature_add(location = bone_location, rotation = bone_rotation)                                                         # Add new bone at given location and rotation.

    for single_object in bpy.data.objects:                                                                                                  # Loop through all objects in the scene.
        if single_object.select:                                                                                                            # Only bone created above is selected, i.e. condition true if created bone is reached.
            bpy.context.scene.objects.active = single_object                                                                                # Activate object to avoid confusion.
            single_object.select = True                                                                                                     # Selecting object to ensure focus.
            single_object.name= bone_identifier                                                                                             # Naming of Armature...
            single_object.data.name = bone_identifier                                                                                       # ... Bone-Data...
            armature_name = single_object.name                                                                                              # ... naming...
            bpy.data.objects[armature_name].data.bones[0].name = bone_name                                                                  # ... and bone.
            bpy.data.objects[armature_name].data.draw_type="BBONE"                                                                          # Switch look of bones to "BBone".
            bpy.ops.object.mode_set(mode='EDIT')                                                                                            # Switch to Edit-Mode (following code will not work in Object-Mode).
            bpy.data.objects[armature_name].data.edit_bones[bone_name].bbone_x = bone_x                                                     # Set x-size of Bbone.
            bpy.data.objects[armature_name].data.edit_bones[bone_name].bbone_z = bone_z                                                     # Set z-size of Bbone.
            bpy.data.objects[armature_name].data.edit_bones[bone_name].head = bone_head                                                     # Set location of head (one side of the bone).
            bpy.data.objects[armature_name].data.edit_bones[bone_name].tail = bone_tail                                                     # Set location of tail (other side of the bone).
            bpy.ops.object.mode_set(mode='OBJECT')                                                                                          # Switch back to Object-Mode.

# "ADD_ARMATURES" calls "ADD_ARMATURES_HELPER" for every object found in the file but not in scene:

def ADD_ARMATURES(local_imported_skeleton_data, local_imported_meta_helperBones, local_meta_name):
    local_amount_bones_added = 0

    if local_meta_name  != "none":                                                                                                          # Condition is true if meta-file was imported / loaded.
        for single_helper in local_imported_meta_helperBones:                                                                               # Loop through all helperBones in the meta-file.
            words_helper = single_helper.split(',')                                                                                         # Entries are split to identify single helperBones. 

            for single_entry_skeleton in local_imported_skeleton_data:                                                                      # Loop through all objects in the skeleton-data.
                words_skeleton = single_entry_skeleton.split(',')                                                                           # Objects from the skeleton-file are split into single objects.
                if words_skeleton[0] == words_helper[0].replace('"',''):                                                                    # Condition is true if "Helper Bone" is similar to selected object from skeleton-file.
                    local_amount_bones_added += 1                                                                                           # Increasing counter which includes amount of added bones.

                    bone_location = (float(words_skeleton[1]), float(words_skeleton[2]), float(words_skeleton[3]))                          # Sets location of bone which has to be created (coordinates taken from skeleton-file).
                    bone_rotation = (radians(90), 0, 0)                                                                                     # Sets rotation of bone which has to be created.
                    bone_identifier = str(words_skeleton[0])                                                                                # Sets "identifier" of the bone (name taken from the skeleton-file).
                    bone_name = str(words_skeleton[0])                                                                                      # Sets "name" of the bone (name taken from the skeleton-file).
                    bone_x = float(words_helper[1])                                                                                         # Sets x-value (length) for the bone (from meta-file).
                    bone_z = float(words_helper[2])                                                                                         # Sets z-value (lenght) for the bone (from meta-file).
                    bone_head = (0, 0, float(words_helper[3]))                                                                              # Sets coordinates for head of bone (from meta-file).
                    bone_tail = (0, 0, float(words_helper[4]))                                                                              # Sets coodrinates for tail of bone (from meta-file).
                    
                    ADD_ARMATURES_HELPER(bone_location, bone_rotation, bone_identifier, bone_name, bone_x, bone_z, bone_head, bone_tail)    # Helper-function is called to set values of bone.
    else:                                                                                                                                   # If no meta-file was loaded, standard-armatures will be created for all "bones".
        for single_entry in local_imported_skeleton_data:                                                                                   # Loop through all objects in the skeleton-data.
            name_found_identifier = 0                                                                                                       # Set variable to 0 which is used to track if a name was found in both sources.
            words = single_entry.split(',')                                                                                                 # Split of entries from skeleton-file into single "words".
            for single_object in bpy.data.objects:                                                                                          # Loop through objects in scene. 
                if words[0] == single_object.name:                                                                                          # Condition is true if object meets naming-convention of an entry in the skeleton file.
                    name_found_identifier = 1                                                                                               # Name was found in both sources so variable can be sset to 1.
                    break                                                                                                                   # No need to look further.
            if name_found_identifier != 1:                                                                                                  # Condition true if name was not found in the scene.
                local_amount_bones_added += 1                                                                                               # Increasing counter which includes amount of added bones.

                bone_location = (float(words[1]), float(words[2]), float(words[3]))                                                         # Fill elements with pre-defined values to create a "standard"-bone.
                bone_rotation = (radians(90), 0, 0)
                bone_identifier = str(words[0])
                bone_name = str(words[0])
                bone_x = 3
                bone_z = 3
                bone_head = (0, 0, 3)
                bone_tail = (0, 0, -3)

                ADD_ARMATURES_HELPER(bone_location, bone_rotation, bone_identifier, bone_name, bone_x, bone_z, bone_head, bone_tail)        # Helper-function is called to set values of bone.

    return (local_amount_bones_added)

# "SET_HIERARCHY" will add relationships to the bones and armatures in the scene:

def SET_HIERARCHY(local_imported_meta_hierarchy):

    for single_relationship in local_imported_meta_hierarchy:                                                                               # Split list with all relationships into chunks ("single_relationship").
        bpy.ops.object.select_all(action='DESELECT')                                                                                        # Deselect all objects in the scene.
        for position in range(0, len(single_relationship)):                                                                                 # Loop through amount of "bones" / "meshes" included in the "chunk".
            if position != 0:                                                                                                               # First position includes "hierarchy" and can be skipped.
                adjusted_relationship = single_relationship[position].replace('[','')                                                       # "Chunk" is cleaned-up and [ as a symbol is removed. 
                adjusted_relationship = adjusted_relationship.replace(']','')                                                               # ... same for ].
                adjusted_relationship = adjusted_relationship.strip(',\"')                                                                  # ... same for , and ".
                bpy.data.objects[str(adjusted_relationship)].select=True                                                                    # Object with the name included in the chunk is activated.
            if position == (len(single_relationship)-1):                                                                                    # Last position inchludes the parent and has to be activated in addition to being selected.
                bpy.context.scene.objects.active = bpy.data.objects[str(adjusted_relationship)]                                             # Selection of the relevant object.

        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
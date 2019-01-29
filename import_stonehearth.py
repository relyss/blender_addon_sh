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
# import_stonehearth.py
#----------------------------------------------------------

import bpy
import os
from math import radians
from mathutils import Matrix, Quaternion

from . import operations_stonehearth

# Function is called from "PROCESS_IMPORT" and returns type of imported file and additional data:

def IMPORT_FILE(file_handler):
    local_imported_file_type = 'none'
    local_imported_skeleton_data = []
    local_imported_meta_helperBones = []
    local_imported_meta_hierarchy = []

    stopper = 0
    frame_actual = 0
    bpy.context.scene.frame_start = 1

    for single_line in file_handler:                                                                                                                                      # Loops for each line in the file.

        words_in_line = single_line.split()                                                                                                                               # Imported line is split into "words".
        if len(words_in_line) == False:                                                                                                                                   # If there are no words in the line it can be skipped as it is empty. 
            pass      
        else:
            for single_word in words_in_line:                                                                                                                             # Loops through all "words" included in the actual line.
                if single_word == "\"skeleton\":" or single_word == "\"skeleton\"" or single_word == "\"meta\":" or single_word == "\"frames\":":                         # Checks if file includes a label called "skeleton", "meta" or "frames".
                    local_imported_file_type = single_word.strip(':\"')                                                                                                   # Leading and tailing characters are removed from value.
            if local_imported_file_type == "skeleton":                                                                                                                    # Condition true if file is of type "skeleton". 
                word = words_in_line[0].strip(':\"')                                                                                                                      # Special characters (" and :) are removed.
                if word != "}," and word != "skeleton" and stopper != 1:                                                                                                  # Condition is true if adjusted line is not consisting of the "},"-character or the "skeleton"-label.
                    word_data = words_in_line[1].replace('[','').replace(']','')                                                                                          # Another two characters ([ and ]) are removed from the line.
                    local_imported_skeleton_data.append(word + ',' + word_data)                                                                                           # Append data to variable "local_imported_skeleton_data".
                elif word == "},":                                                                                                                                        # If line includes "},"...
                    stopper = 1                                                                                                                                           # ... a variable "stopper" is set to 1 to indicate EOF.
            elif local_imported_file_type == "meta":                                                                                                                      # Condition true if file is of type "meta".
                word = words_in_line[0].strip(':\"')                                                                                                                      # Special characters (" and :) are removed.
                if word != "}," and word != "meta" and stopper != 1:                                                                                                      # Condition is true if adjusted line is not consisting of the "},"-character or the "meta"-label.
                    word_data = words_in_line[1].replace('[','').replace(']','')                                                                                          # Another two characters ([ and ]) are removed from the line.
                    if word == "helperBone":                                                                                                                              # Condition is true if the line is related to a "helperBone".
                        words_in_line[5] = words_in_line[5].replace(']','')                                                                                               # The "]" at the end of the last element is removed. 
                        local_imported_meta_helperBones.append(word_data + words_in_line[2] + words_in_line[3] + words_in_line[4] + words_in_line[5])                     # Values are appended into the variable "local_imported_meta_helperBones".
                    elif word == "hierarchy":                                                                                                                             # Condition is true if the line is related to a "relationship".
                        local_imported_meta_hierarchy.append(words_in_line)                                                                                               # Adjusted line consisting of data for each relationship in the meta-file.
                elif word == "},":                                                                                                                                        # If line includes "},"...
                    stopper = 1                                                                                                                                           # ... a variable "stopper" is set to 1 to indicate EOF.
            elif local_imported_file_type == "frames":                                                                                                                    # Condition true if file is of type "animation".
                word = words_in_line[0].strip(':\"')
                if word == "{":
                    frame_actual += 1                                                                                                                                     # Counts which frame is actually loaded.
                    bpy.context.scene.frame_end = frame_actual                                                                                                            # Sets the end to the value of "frame_actual", i.e. all frames set once file end is reached.
                    bpy.data.scenes[0].frame_set(frame_actual)
                elif word != "pos" and word != "rot" and word != "}" and word != "}," and word != "]":                                                                    # Condition true if entry is not related to the position or rotation (and others).
                    object_actual_name = word
                    try: object_check = (bpy.data.objects[object_actual_name])                                                                                            # Checking if object exists and saving result in variable "object_check".
                    except: object_check = None
                    if (object_check == None and object_actual_name != "{" and object_actual_name != "frames"):                                                           # Condition true if object does not exist, object will be created.
                        bone_location = (0, 0, 0)
                        bone_rotation = (radians(90), 0, 0)
                        bone_identifier = object_actual_name
                        bone_name = object_actual_name
                        bone_x = 3
                        bone_z = 3
                        bone_head = (0, 0, 3)
                        bone_tail = (0, 0, -3)
                        operations_stonehearth.ADD_ARMATURES_HELPER(bone_location, bone_rotation, bone_identifier, bone_name, bone_x, bone_z, bone_head, bone_tail)
                elif word == "pos" and object_actual_name != "_main_hand" and object_actual_name != "_off_hand":                                                          # Condition true if data is related to position of the object. 
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.scene.objects.active = bpy.data.objects[object_actual_name]
                    bpy.data.objects[object_actual_name].select = True
                    pos_data = words_in_line[1].split(',')
                    pos_data[0] = pos_data[0].replace('[','') 
                    pos_data[2] = pos_data[2].replace(']','') 
                    vec = (float(pos_data[0]), float(pos_data[1]), float(pos_data[2]))                                                                                    # Create Vector "vec" and fill it with coordinates (location). 
                    bpy.context.object.matrix_world.translation = vec                                                                                                     # Assign location of active object to "vec"
                elif word == "rot" and object_actual_name != "_main_hand" and object_actual_name != "_off_hand":                                                          # Condition true if data is related to rotation of the object.
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.scene.objects.active = bpy.data.objects[object_actual_name]
                    bpy.data.objects[object_actual_name].select = True
                    rot_data = words_in_line[1].split(',')
                    rot_data[0] = rot_data[0].replace('[','') 
                    rot_data[3] = rot_data[3].replace(']','') 
                    quat = (float(rot_data[0]), float(rot_data[1]), float(rot_data[2]), float(rot_data[3]))                                                               # Fill Vector "quat" with values from Quaternion.
                    quat_quaternion = Quaternion(quat)                                                                                                                    # Create variable "quat_quaternion" of type "Quaternion" and fill with Vector "quat".
                    quat_matrix = quat_quaternion.to_matrix()                                                                                                             # Translate Quaternion to Matrix (3x3).
                    quat_matrix.resize_4x4()                                                                                                                              # Translate 3x3 Matrix to 4x4 format.
                    vec = (float(pos_data[0]), float(pos_data[1]), float(pos_data[2]))
                    vec_matrix = Matrix.Translation(vec)                                                                                                                  # Translate vector with location data to 4x4 Matrix.
                    bpy.context.object.matrix_world = vec_matrix * quat_matrix                                                                                            # Fill world_matrix of active object with result of multiplication (location * rotation).

                elif word == "}":
                    bpy.ops.object.select_all(action='SELECT')
                    bpy.ops.anim.keyframe_insert_menu(type = "BUILTIN_KSI_LocRot")

    return local_imported_file_type, local_imported_skeleton_data, local_imported_meta_helperBones, local_imported_meta_hierarchy

# Function is called from "PROCESS_IMPORT" in case offset has to be calculated (was selected as import-option):

def IMPORT_OFFSET(file_handler, global_imported_skeleton_data):
    local_imported_offset_buffer = []
    local_imported_offset_data = []
    local_imported_file_type = 'none'

    stopper = 0

    for single_line in file_handler:                                                                                                                                      # Loops for each line in the file to load second skeleton (used for offset).
        words_in_line = single_line.split()                                                                                                                               # Imported line is split into "words".
        if len(words_in_line) == False:                                                                                                                                   # If there are no words in the line it can be skipped as it is empty. 
            pass      
        else:
            for single_word in words_in_line:                                                                                                                             # Loops through all "words" included in the actual line.
                if single_word == "\"skeleton\":" or single_word == "\"skeleton\"":                                                                                       # Checks if file is of type "skeleton".
                    local_imported_file_type = single_word.strip(':\"')                                                                                                   # Leading and tailing characters are removed from value.
            if local_imported_file_type == "skeleton":                                                                                                                    # Condition true if file is of type "skeleton". 
                word = words_in_line[0].strip(':\"')                                                                                                                      # Special characters (" and :) are removed.
                if word != "}," and word != "skeleton" and stopper != 1:                                                                                                  # Condition is true if adjusted line is not consisting of the "},"-character or the "skeleton"-label.
                    word_data = words_in_line[1].replace('[','').replace(']','')                                                                                          # Another two characters ([ and ]) are removed from the line.
                    local_imported_offset_buffer.append(word + ',' + word_data)                                                                                           # Append data to variable "local_imported_offset_buffer".
                elif word == "},":                                                                                                                                        # If line includes "},"...
                    stopper = 1                                                                                                                                           # ... a variable "stopper" is set to 1 to indicate EOF.

    counter = 0

    for single_entry_skeleton in global_imported_skeleton_data:                                                                                                           # Loop runs once for each element in the string "global_imported_skeleton_data" (i.e. skeleton-file).
        words_skeleton = single_entry_skeleton.split(',')                                                                                                                 # Element in string is split, i.e. will result in 4 entries.
        for single_entry_offset in local_imported_offset_buffer:                                                                                                          # Loop runs once for each element int he string "local_imported_offset_buffer" (i.e. second skeleton for offset).
            words_offset = single_entry_offset.split(',')                                                                                                                 # Element in string is split.
            if (str(words_skeleton[0]) == str(words_offset[0])):                                                                                                          # First element contains the name of a bone which is compared to object-name.
                delta_1 = float(words_skeleton[1]) - float(words_offset[1])                                                                                               # Offset for first element per bone.
                delta_2 = float(words_skeleton[2]) - float(words_offset[2])                                                                                               # Offset for second element per bone.
                delta_3 = float(words_skeleton[3]) - float(words_offset[3])                                                                                               # Offset for third element per bone.
                local_imported_offset_data.append(words_skeleton[0] + ',' + str(delta_1) + ',' + str(delta_2) + ',' + str(delta_3))                                       # Create new string including offsets "local_imported_offset_data.
                counter = counter + 1

    if (counter != len(global_imported_skeleton_data) or counter != len(local_imported_offset_buffer)):
        local_imported_offset_data = []

    return local_imported_offset_data

# Function is called from "Import-Menu" and calls further functions to be processed based on import-options:

def PROCESS_IMPORT(filepath, selection_import_offset_value, global_imported_skeleton_data):

    fp = open(filepath, 'rU')

    if selection_import_offset_value and global_imported_skeleton_data:                                                                                                   # Check option which was checked in the import-GUI and if skeleton-data was already imported.
        local_imported_file_type = 'none'
        local_imported_skeleton_data = []
        local_imported_meta_helperBones = []
        local_imported_meta_hierarchy = []

        local_offset_data = IMPORT_OFFSET(fp, global_imported_skeleton_data)                                                                                              # ... if yes, function is called to load skeleton-data as offset.

    else:                                                                                                                                                                 # ... otherwise process skeleton-data as such (define origin, etc.). 
        local_offset_data = []

        local_imported_file_type, local_imported_skeleton_data, local_imported_meta_helperBones, local_imported_meta_hierarchy = IMPORT_FILE(fp)                          # Function "IMPORT_FILE" is called and return values are stored in variables.
        
    fp.close()

    return local_imported_file_type, local_offset_data, local_imported_skeleton_data, local_imported_meta_helperBones, local_imported_meta_hierarchy
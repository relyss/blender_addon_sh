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
# export_stonehearth.py
#----------------------------------------------------------

import bpy
import os

# Function "EXPORT_SKELETON" is called if radio-button (export) is set to "Skeleton":

def EXPORT_SKELETON(filepath, file_handler):
    file_name = bpy.path.display_name_from_filepath(filepath)
    file_handler.write('{\n')
    file_handler.write('\t "skeleton": {\n')

    amount_objects = len(bpy.data.objects)
    counter_objects = 0

    for single_object in bpy.data.objects:                                                                                                                                    # Loop through all objects in scene.
        counter_objects += 1
        if single_object.type == "MESH" or single_object.type == "ARMATURE":                                                                                                  # If object is of type "MESH" or "ARMATURE its name and coordinates are written into the file. 
            if counter_objects < amount_objects:
                file_handler.write('\t\t "%s": [%f,%f,%f],\n' % (single_object.name, single_object.location.x, single_object.location.y, single_object.location.z))
            else:
                file_handler.write('\t\t "%s": [%f,%f,%f]\n' % (single_object.name, single_object.location.x, single_object.location.y, single_object.location.z))

    file_handler.write('\t},\n')
    file_handler.write('\t <<< add links to effects and animations as collision data >>> \n')
    file_handler.write('}\n')

# Function "EXPORT_ANIMATIOIN" is called if radio-button (export) is set to "Animation":

def EXPORT_ANIMATION(filepath, file_handler, global_offset_data):
    file_name = bpy.path.display_name_from_filepath(filepath)
    file_handler.write('{\n')
    file_handler.write('\t\t "type": "animation",\n')
    file_handler.write('\t\t "frames": [\n')

    for frame in range(int(bpy.data.scenes[0].frame_start), int(bpy.data.scenes[0].frame_end) + 1):
        bpy.data.scenes[0].frame_set(frame)
        file_handler.write('\t\t\t{\n')
        amount_objects = len(bpy.data.objects)
        counter_objects = 0
        for single_object in bpy.data.scenes[0].objects:

            if global_offset_data:
                for single_object_offset in global_offset_data:
                    words_offset = single_object_offset.split(',')  
                    if (single_object.name == str(words_offset[0])):
        
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.context.scene.objects.active = single_object
                        single_object.select = True

                        single_object_quaternion = bpy.context.object.matrix_world.to_quaternion()
                        single_object_location = bpy.context.object.matrix_world.to_translation()

                        counter_objects += 1
                        file_handler.write('\t\t\t\t"%s": {\n' % (single_object.name)) 

                        delta_x = single_object_location.x - float(words_offset[1])
                        delta_y = single_object_location.y - float(words_offset[2])
                        delta_z = single_object_location.z - float(words_offset[3])

                        file_handler.write('\t\t\t\t\t"pos": [%f,%f,%f],\n' % (delta_x, delta_y, delta_z))
                        file_handler.write('\t\t\t\t\t"rot": [%f,%f,%f,%f]\n' % (single_object_quaternion.w, single_object_quaternion.x, single_object_quaternion.y, single_object_quaternion.z))
                        if counter_objects < amount_objects:
                            file_handler.write('\t\t\t\t},\n')
                        else:
                            file_handler.write('\t\t\t\t}\n')
            else:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = single_object
                single_object.select = True
 
                single_object_quaternion = bpy.context.object.matrix_world.to_quaternion()
                single_object_location = bpy.context.object.matrix_world.to_translation()

                counter_objects += 1
                file_handler.write('\t\t\t\t"%s": {\n' % (single_object.name)) 
                file_handler.write('\t\t\t\t\t"pos": [%f,%f,%f],\n' % (single_object_location.x, single_object_location.y, single_object_location.z))
                file_handler.write('\t\t\t\t\t"rot": [%f,%f,%f,%f]\n' % (single_object_quaternion.w, single_object_quaternion.x, single_object_quaternion.y, single_object_quaternion.z))

                if counter_objects < amount_objects:
                    file_handler.write('\t\t\t\t},\n')
                else:
                    file_handler.write('\t\t\t\t}\n')

        if frame < (int(bpy.context.scene.frame_end)):
            file_handler.write('\t\t\t},\n')
        else:
            file_handler.write('\t\t\t}\n')

    file_handler.write('\t\t]\n')
    file_handler.write('}')

# Function "EXPORT_META" is called if radio-button (export) is set to "Meta":

def EXPORT_META(filepath, file_handler):
    file_name = bpy.path.display_name_from_filepath(filepath)
    file_handler.write('{\n')
    file_handler.write('\t "meta": {\n')

    for single_object in bpy.data.objects:                                                                                          # Loop through all objects in scene.
        if single_object.type == "ARMATURE":                                                                                        # Condition is true if object is of type "ARMATURE" (helper bone).
            bone_x_scale = single_object.data.bones[0].bbone_x * single_object.scale.x
            bone_y_scale = single_object.data.bones[0].bbone_z * single_object.scale.y
            file_handler.write('\t\t"helperBone": ["%s", %f, %f, %f, %f],\n' % (single_object.name, bone_x_scale, bone_y_scale, single_object.data.bones[0].head.z, single_object.data.bones[0].tail.z))

    for single_object in bpy.data.objects:                                                                                          # Loop through all objects in scene.
        if single_object.children:                                                                                                  # Condition is true if object is parent of other objects. 
            file_handler.write('\t\t"hierarchy": [')
            for counter_children in range(len(single_object.children)):                                                             # Loop through all children of the object.
                file_handler.write('"%s", ' % single_object.children[counter_children].name)
            file_handler.write('"%s"],\n' % (single_object.name))                                                                   # Write name of object as last element. 

    file_handler.write('\t},\n')
    file_handler.write('}\n')

# Function "PROCESS_EXPORT" is called if user selects "File > Export" from the menu - called from file "__init__.py":

def PROCESS_EXPORT(filepath, export_selection, export_selection_animation, global_offset_data):

    file_handler = open(filepath, 'w')                                                                                              # Open file to write.

    if bpy.context.mode != 'OBJECT':                                                                                                # Check if Blender is in "Object-Mode"...
        bpy.ops.object.mode_set(mode='OBJECT')                                                                                      # ... and if not, set it (to avoid issues).

    if export_selection == '1':                                                                                                     # Condition is true if radio-button is set to "Skeleton" (Option 1) vs. "Animation" (Option 2).
        EXPORT_SKELETON(filepath, file_handler)
    elif export_selection == '2':                                                                                                   # Condition is true if user want to export meta-data.
        EXPORT_META(filepath, file_handler)
    elif export_selection == '3':                                                                                                   # Condition is true if user wants to export an animation.
        if export_selection_animation and global_offset_data:                                                                       # Condition true if offsset-data exists and if export with offset was selected as an export-option.
            EXPORT_ANIMATION(filepath, file_handler, global_offset_data)                                                            # ... if true variable "global_offset_data" contains data and is passed through. 
        else:
            global_offset_data = []                                                                                                 # ... if not true the varaible will be set to cleared ([])...
            EXPORT_ANIMATION(filepath, file_handler, global_offset_data)                                                            # ... and used later on to see if offset should be taken into account for export.

    file_handler.close
    return
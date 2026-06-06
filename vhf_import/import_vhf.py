from importlib import machinery
import os

from functools import partial
from genericpath import exists

# from .binary_stream import BinaryStream
from mathutils import Quaternion
from math import radians

import xml.etree.ElementTree as ET 

import bpy

def get_object_by_name(collection, name):
    return bpy.data.collections[collection].all_objects.get(name)


def name_filter(filter, partname, check):
    if check:
        if filter in partname:
            return True
    return False


def import_parts(filename, col_name, rotate, offset):

    tree = ET.parse(filename) 

    matrices = []
    nodes    = []

    for elem in tree.iter():
        if elem.tag == 'MATRIX':
            elem.attrib["Offset"] = elem.attrib["Offset"].split()
            elem.attrib["Orientation"] = elem.attrib["Orientation"].split()            
            matrices.append(elem.attrib)
        elif elem.tag == 'NODE':
            nodes.append(elem.attrib)
    
    
    
    for m in matrices:
        selected_nodes = []
        for n in nodes:
            if n["MatrixNumber"] == m["id"]:
                selected_nodes.append(n)
        if selected_nodes == []:
            continue
        
        for node in selected_nodes:
        
            obj_name = node["Name"]
            
            body = get_object_by_name(col_name, obj_name)
            
            if not body:
                s = ''
                for b in range (1, 13):
                    s = f".{str(b).zfill(3)}"
                    body = get_object_by_name(col_name, obj_name + s)
                    if body:
                        break
                if not body:
                    print(f"Didn't find {obj_name}")
                    continue
            
            print(f"object {obj_name}")
            
            transx      = float(m["Offset"][0])
            transy      = float(m["Offset"][2])
            transz      = float(m["Offset"][1])
            
            quatw  =  float(m["Orientation"][3])
            quatx  = -float(m["Orientation"][0])
            quaty  = -float(m["Orientation"][2])
            quatz  = -float(m["Orientation"][1])
                    
            if offset:
                body.location.x += transx
                body.location.y += transy
                body.location.z += transz      

            if rotate:
                body.rotation_mode = 'QUATERNION'
                body.rotation_quaternion = Quaternion((quatw, quatx, quaty, quatz))
        
    
def load(filepath, col_name, rotate, offset):
    import_parts(filepath, col_name, rotate, offset)



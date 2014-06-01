"""

Giraffe for Rhino
    developed and maintained by Peter Szerzo

Imports wireframe geometry as structural model into SOFiSTiK.
Giraffe organizes structural information using through a strict layer structure:
	- all input geometry in a main 'input' layer
	- 1st children: 'nodes', 'beams', 'trusses', 'cables', 'springs'
	- 2nd children: '{group number} [{layer properties}]'
		e.g. '2 [ncs 2 ahin mymz]' 
		rules:
			white spaces allowed
			group number is mandatory
			layer properties may be omitted, including square brackets
	- 3rd children: '{properties}'
		e.g. 'ncs 3 ahin n'
		rules:
			no square brackets this time (layer names cannot start with square brackets)
			no group numbers
			
	each element may be named in '{element number} [{element properties}]' format

"""

import rhinoscriptsyntax as rs

import math

import string

number_characters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

point_elements = ["node"]

line_elements = ["beam", "trus", "cabl"]

area_elements = ["quad"]

def english_to_sofi(word):
    
    dictionary = {
        "nodes": "node", 
        "beams": "beam", 
        "trusses": "trus", 
        "cables": "cabl", 
        "springs": "spri",
        "quads": "quad"
    }
    
    return dictionary[word]


def is_taken_number(array, no, grp):
    
    for element in array:
        
        if (element.no == no and (grp == -1 or grp == element.grp)):
                
                return True	
                
    return False



class Layer:
    
    def __init__(self, name):
        
        self.name = name
        self.path = name.split("::")
        self.depth = len(self.path)
        self.last = self.path[self.depth - 1]
        


class Description:
    
    def __init__(self, s):
        
        self.no = -1
        self.prop = ""
        
        s = s.strip()
        
        if (s != ""):
            
            i1 = s.find("[")
            i2 = s.find("]")
            
            if (i1 == -1 or i2 == -1):
                
                if (not s[0] in number_characters):
                    
                    self.prop = s
                    
                else:
                
                    self.no = int(s)
                
            else:
            
                no_string = s[0:(i1)].strip()	
                self.no = (-1) if (no_string == "") else int(no_string)
                self.prop = s[(i1 + 1):(i2)]



class StructuralElement():

    
    def __init__(self, typ, no, prop, grp = -1, strict_naming = False):
        
        self.typ = typ
        self.no = no
        self.prop = prop
        self.grp = grp
        self.strict_naming = strict_naming
        
        
    def output_base(self):
    
        return (self.typ + " no " + str(self.no))




class Node(StructuralElement):
    
    
    def __init__(self, no = -1, x = 0, y = 0, z = 0, prop = ""):
        
        StructuralElement.__init__(self, "node", no, prop)
        self.x = x
        self.y = y
        self.z = z
		
		
    def build_from_point(self, obj):
        
        attr = Description(rs.ObjectName(obj))
        coordinates = rs.PointCoordinates(obj)
        self.no = attr.no
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.z = coordinates[2]
        self.prop = attr.prop
		
		
    def export(self):
        
        output = self.output_base()
        output += " x " + str(self.x)
        output += " y " + str(self.y)
        output += " z " + str(self.z)
        output += " " + self.prop + "\n"
        return output	
        
        
    def distance_to(self, n):
        
        return ( (self.x - n.x) ** 2 + (self.y - n.y) ** 2 + (self.z - n.z) ** 2 ) ** 0.5
        
        
    def identical_to(self, n):
        
        return (self.distance_to(n) < 0.001)



class Member(StructuralElement):	


    def __init__(self, typ, grp, no, na, ne, prop):
        
        StructuralElement.__init__(self, typ, no, prop, grp)
        self.na = na
        self.ne = ne
        
        
    def export(self):
        
        output = self.output_base()
        output += " na " + str(self.na)
        output += " ne " + str(self.ne)
        output += " " + self.prop + "\n"
        
        return output



class Quad(StructuralElement):	


    def __init__(self, grp, no, corner_numbers, prop):
        
        StructuralElement.__init__(self, "quad", no, prop, grp)
        self.n1 = corner_numbers[0]
        self.n2 = corner_numbers[1]
        self.n3 = corner_numbers[2]
        self.n4 = self.n1 if (len(corner_numbers) <= 3) else corner_numbers[3]   
        
        
    def export(self):
        
        output = self.output_base()
        output += " n1 " + str(self.n1)
        output += " n2 " + str(self.n2)
        output += " n3 " + str(self.n4)
        output += " n4 " + str(self.n3)
        output += " " + self.prop + "\n"
        
        return output
        


class ElementList:

    def __init__(self):
        
        self.list = []
        self.fan = 1
        
    
    def update_fan(self, grp):
    
        self.fan = 1
        while(is_taken_number(self.list, self.fan, grp)):
            self.fan += 1



class StructuralModel:
    
    
    def __init__(self, name):	
    
        self.name = name	
        
        self.nodes = ElementList()
        self.members = ElementList()         
        self.quads = ElementList()  
        
        self.gdiv = 1000
        self.current_group = -1
        
        self.output_header = "$ generated by Giraffe for Rhino\n"
        self.output_header += "+prog sofimsha\nhead " + self.name + "\n\nsyst init gdiv 1000\n"
        self.output_nodes = "\n\n!*!Label Nodes\n"
        self.output_members = "\n\n!*!Label Line Members\n"
        self.output_quads = "\n\n!*!Label Area Elements\n"
        self.output_footer = "\nend"
        self.output = ""

			
    def add_node(self, n):
        
        if (n.no == -1):
            
            for node in self.nodes.list:
                if n.identical_to(node):
                    n.no = node.no
            if (n.no == -1):
                n.no = self.nodes.fan
                self.nodes.list.append(n)
                
        else:
            
            self.nodes.list.append(n)
            l = len(self.nodes.list)
            
            for i in range(0, l - 1):
                
                if self.nodes.list[l - 1].no == self.nodes.list[i].no:
                    
                    self.nodes.list[i].no = self.nodes.fan
                    
        self.nodes.update_fan(-1)
        
        return n
				
		
    def add_member(self, element, element_type):
        
        attr = Description(rs.ObjectName(element))
        
        pa = rs.CurveStartPoint(element)
        pe = rs.CurveEndPoint(element)
        
        node_a = self.add_node(Node(-1, pa[0], pa[1], pa[2], ""))
        node_e = self.add_node(Node(-1, pe[0], pe[1], pe[2], ""))
        
        if (attr.no == -1):
            
            attr.no = self.members.fan
            
        else:
            
            l = len(self.members.list)
            
            for i in range(0, l):
                
                if (attr.no == self.members.list[i].no) and (self.current_group == self.members.list[i].grp):
                    
                    self.members.list[i].no = self.members.fan
                    
        e = Member(element_type, self.current_group, attr.no, node_a.no, node_e.no, attr.prop)
        
        self.members.list.append(e)
        self.output_members += e.export()
        
        self.members.update_fan(self.current_group)
	
	
    def add_quad(self, obj):
        
        attr = Description(rs.ObjectName(obj))
        no = attr.no
        
        corner_numbers = []
        
        pts = rs.SurfacePoints(obj)
        for pt in pts:
            n = self.add_node(Node(-1, pt[0], pt[1], pt[2], ""))
            corner_numbers.append(n.no)
                
        if (no == -1):
            
            no = self.quads.fan
            
        else:
            
            l = len(self.quads.list)
            
            for i in range(0, l):
                
                if (attr.no == self.quads.list[i].no) and (self.current_group == self.quads.list[i].grp):
                    
                    self.quads.list[i].no = self.quads.fan
                    
        q = Quad(self.current_group, no, corner_numbers, attr.prop)
        
        self.quads.list.append(q)
        self.output_quads += q.export()
        
        self.quads.update_fan(self.current_group)
		
				
    def export_nodes(self):
        
        for node in self.nodes.list:
            
            self.output_nodes += node.export()	
            
        self.output_nodes += "\n"	
		
		
    def export(self):
        
        self.export_nodes()
        return self.output_header + self.output_nodes + self.output_members + self.output_quads + self.output_footer
        
    
    def make_file(self):
        
        f = open("system.dat", "w")
        
        f.write(self.export())
		
        f.close()
		

def Main():
    
    sofi = StructuralModel("some structure")
    layer_names = rs.LayerNames()	
    
    for name in layer_names:
        
        layer = Layer(name)
        
        if (layer.path[0] == "input") and (layer.depth > 1):
            
            element_type = english_to_sofi(layer.path[1])
            
            if (layer.depth > 2):
            
                attr = Description(layer.last)
                prop = attr.prop
                
                if (layer.depth == 3):
                    
                    sofi.current_group = attr.no
                    sofi.output_members += "\ngrp " + str(sofi.current_group) + "\n"
                
                if (prop != ""):
                    sofi.output_members += "\n" + element_type + " prop " + prop + "\n"
            
            if (element_type in point_elements):
            
                sofi.current_group = -1
                
                objects = rs.ObjectsByLayer(layer.name)[::-1]
                for obj in objects:
                    n = Node()
                    n.build_from_point(obj)
                    sofi.add_node(n)
                    
            elif (element_type in line_elements):
                    
                sofi.members.update_fan(sofi.current_group)
                    
                objects = rs.ObjectsByLayer(layer.name)[::-1]
                for obj in objects:
                    sofi.add_member(obj, element_type)
                    
            elif (element_type in area_elements):
                
                sofi.quads.update_fan(sofi.current_group)
                
                objects = rs.ObjectsByLayer(layer.name)[::-1]
                for obj in objects:
                    sofi.add_quad(obj)
                    
    sofi.make_file()
        
Main()
"""

Giraffe for Rhino, v0.0.0
Peter Szerzo

NOTE
This is a draft version used for proof of concept.

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

tolerance = 0.01 # how close points have to be to be considered one
z_coordinate_sign = +1

glass_loaded_groups = [1, 2, 3, 4, 5, 6, 7]

dictionary = {
    "nodes": "node", 
    "beams": "beam", 
    "trusses": "trus", 
    "cables": "cabl", 
    "springs": "spri",
    "quads": "quad"
}

layer_levels = [

    ["input"],
    ["nodes", "springs", "beams", "cables", "trusses", "quads"]

]

def get_conversion_factor():
    
    unit_system = rs.UnitSystem()
    
    unit_conversion = {
        2: 0.001,
        3: 0.01,
        4: 1.0,
        8: 0.0254,
        9: 0.3048
    }
    
    return unit_conversion[unit_system]


error_list = {
    
    0: "Export successful. No errors.",
    1: "Same name assigned to multiple elements: node 15 at [0, 0, 0] and [1, 0, 0].",
    2: "Beam elements shorter than the tolerance found."
    
}


def english_to_sofi(word):
    
    return dictionary[word]


def is_taken_number(array, no, grp):
    
    for element in array:
        
        if (element.no == no and (grp == -1 or grp == element.grp)):
                
                return True	
                
    return False


def round(f, n = 3):
    
    a = 10 ** n
    
    return int(f * a) / a


class ErrorMessage:
    
    def __init__(self):
        
        self._list = [0]
        
    def add(self, error_code):
        
        if (0 in self._list):
            
            self._list = []
        
        if not (error_code in self._list):
            
            self._list.append(error_code)
            
    def export(self):
        
        output = ""
        
        for code in self._list:
            
            output += "$ Error #" + str(code) + ": " + error_list[code] + "\n"
            
        return output
            

class Layer:
    
    def __init__(self, name):
        
        self.name = name
        self.path = name.split("::")
        self.depth = len(self.path)
        self.last = self.path[self.depth - 1]
        
        return self
        
    def to_int(self):
        
        level = 0
        result = 0
        index = 0
        
        for s in self.path:
        
            index = layer_levels[level].index(s)
            
            result += index * (10 ** (5 - level))

        return result;
        
    def create(self):
    
        dad = ""
        
        for s in self.path:
            
            son = s if (dad == "") else (dad + "::" + s)
            daddy = None if dad == "" else dad
            if(not rs.IsLayer(son)):
                rs.AddLayer(s, color = None, visible = True, locked = False, parent = daddy)      
            dad = son
            
        return self    
            
    def clear(self):
    
        objects = rs.ObjectsByLayer(self.name)
        for obj in objects:
            rs.DeleteObject(obj) 
            
        return self   
            
    

class Description:
    
    def __init__(self, s):
        
        self.no = -1
        self.prop = ""
        self.name = ""
        
        s = s.strip()
        
        if (s != ""):
            
            i1 = s.find("[")
            i2 = s.find("]")
            
            j1 = s.find("{")
            j2 = s.find("}")
            
            if (i1 == -1):
                
                i = j1
                
            elif (j1 == -1):
                
                i = i1
                
            else:
                
                i = min(i1, j1)
            
            if (i == -1):
            
                if (not s[0] in number_characters):
                    
                    self.prop = s
                    
                else:
                
                    self.no = int(s)
                
            else:
            
                no_string = s[0:(i)].strip()	
                self.no = (-1) if (no_string == "") else int(no_string)
                
                if (i1 != -1):
                    self.prop = s[(i1 + 1):(i2)]
                
                if (j1 != -1):
                    self.name = s[(j1 + 1):(j2)]



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
    
    
    def __init__(self, no = -1, pt = [0, 0, 0], prop = ""):
        
        k = get_conversion_factor()
        
        StructuralElement.__init__(self, "node", no, prop)
        self.x = round(+ pt[0] * k, 5)
        self.y = round(+ pt[1] * k, 5)
        self.z = round(z_coordinate_sign * pt[2] * k, 5)
		
		
    def build_from_point(self, obj):
        
        k = get_conversion_factor()
        
        attr = Description(rs.ObjectName(obj))
        coordinates = rs.PointCoordinates(obj)
        self.no = attr.no
        
        #if (attr.no != -1):
        
        #    self.strict_naming = True
        
        self.x = round(+ coordinates[0] * k, 5)
        self.y = round(+ coordinates[1] * k, 5)
        self.z = round(+ z_coordinate_sign * coordinates[2] * k, 5)
        self.prop = attr.prop
		
		
    def export(self):
        
        output = self.output_base()
        output += " x " + str(self.x)
        output += " y " + str(self.y)
        output += " z " + str(self.z)
        output += " " + self.prop + "\n"
        return output	
        
        
    def distance_to(self, n):
        
        d = ( (self.x - n.x) ** 2 + (self.y - n.y) ** 2 + (self.z - n.z) ** 2 ) ** 0.5
        
        return d
        
        
    def identical_to(self, n):
        
        return (self.distance_to(n) < tolerance)
        

class Member(StructuralElement):


    def __init__(self, typ, grp, no, na, ne, prop):
        
        StructuralElement.__init__(self, typ, no, prop, grp)
        self.na = na
        self.ne = ne
        self.length = 0
        
        
    def build_from_line(self):
        
        return 0
    
    def export(self):
        
        output = self.output_base()
        output += " na " + str(self.na)
        output += " ne " + str(self.ne)
        output += " " + self.prop
        output += " $ l = " + str(self.length) + " [m]\n"
        
        return output
        
        
    def export_glass_load(self):
        
        l = str(self.length)
        output = "$ " + str(self.grp) + "\n"
        output += "bepl " + str(self.grp * 1000 + self.no) + " type pzz p " + str(-z_coordinate_sign) + "*24*$(t)/1000*" + l + "/2*$(H)*$(FTtoM) a " + "#a" + "\n"
        output += "bepl " + str(self.grp * 1000 + self.no) + " type pzz p " + str(-z_coordinate_sign) + "*24*$(t)/1000*" + l + "/2*$(H)*$(FTtoM) a " + l + "-#a" + "\n\n"
        
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
        
        self.glass_load_groups = []
        
        self.gdiv = 1000
        self.current_group = -1
        
        self.output_header = "$ generated by Giraffe for Rhino\n"
        self.output_header += "+prog sofimsha\nhead " + self.name + "\n\nsyst init gdiv 1000\n"
        self.output_nodes = "\n\n!*!Label Nodes\n"
        self.output_members = "\n\n!*!Label Line Members\n"
        self.output_quads = "\n\n!*!Label Area Elements\n"
        self.output_footer = "\nend"
        self.output = ""
        
        self.output_glass_load = ""
        
        self.errors = ErrorMessage()


    def resolve_number_conflict(self, grp):
        
        return 0

			
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
        
        pa = rs.CurveStartPoint(element)
        pe = rs.CurveEndPoint(element)
        
        s = 0.1
        pb = [
            pa[0] * (1 - s) + pe[0] * s, 
            pa[1] * (1 - s) + pe[1] * s, 
            pa[2] * (1 - s) + pe[2] * s, 
        ]
        
        rs.CurrentLayer("output::startpoints")
        rs.AddPoint(pb)
        
        length = round(((pa[0] - pe[0]) ** 2 + (pa[1] - pe[1]) ** 2 + (pa[2] - pe[2]) ** 2) ** 0.5 * get_conversion_factor())
        
        node_a = self.add_node(Node(-1, pa, ""))
        node_e = self.add_node(Node(-1, pe, ""))
        
        if (node_a.no == node_e.no):
            
            self.errors.add(2);
            
        else:
        
            attr = Description(rs.ObjectName(element))
        
            if (attr.no == -1):
                
                attr.no = self.members.fan
                
            else:
                
                l = len(self.members.list)
                
                for i in range(0, l):
                    
                    if (attr.no == self.members.list[i].no) and (self.current_group == self.members.list[i].grp):
                        
                        self.members.list[i].no = self.members.fan
                        
            e = Member(element_type, self.current_group, attr.no, node_a.no, node_e.no, attr.prop)
            
            e.length = length
            
            self.members.list.append(e)
            self.output_members += e.export()
            
            if (self.current_group in glass_loaded_groups):
                self.output_glass_load += e.export_glass_load()
            
            self.members.update_fan(self.current_group)
	
	
    def add_quad(self, obj):
        
        attr = Description(rs.ObjectName(obj))
        no = attr.no
        
        corner_numbers = []
        
        pts = rs.SurfacePoints(obj)
        
        for pt in pts:
            n = self.add_node(Node(-1, pt, ""))
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
        
        self.output_header += self.errors.export()
        self.export_nodes()
        return self.output_header + self.output_nodes + self.output_members + self.output_quads + self.output_footer
        
    
    def make_file(self):
        
        path = rs.DocumentPath()
        
        i = path.rfind("\\")
        
        path = path[:i]
        
        f = open(path + "\system.dat", "w")
        
        f.write(self.export())
		
        f.close()
        
        f = open(path + "\glass_load.dat", "w")
        
        f.write(self.output_glass_load)
		
        f.close()
		

def Main():
    
    sp = Layer("output::startpoints").create().clear()
    
    sofi = StructuralModel("some structure")
    sofi.glass_load_groups = [1, 2, 3, 4, 5, 6, 7]
    
    layer_names = rs.LayerNames()
    
    layers = []
    
    
    for layer_name in layer_names:
    
        layers.append(Layer(layer_name))
        
    
    for layer in layers:
        
        if (layer.path[0] == "input") and (layer.depth > 1):
            
            if (layer.path[1] != "ignore"):
            
                element_type = english_to_sofi(layer.path[1])
                
                if (layer.depth > 2):
                
                    attr = Description(layer.last)
                    prop = attr.prop
                    
                    if (layer.depth == 3):
                        
                        sofi.current_group = attr.no
                        sofi.output_members += "\n\n!*!Label G" + str(sofi.current_group) + " (" + element_type + ") " + attr.name + "\n"
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
    
    rs.CurrentLayer("input")
    
Main()

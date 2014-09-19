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

tolerance = 0.1 # how close points have to be to be considered one
z_coordinate_sign = +1

glass_loaded_groups = []

dictionary = {
    "nodes": "node", 
    "beams": "beam", 
    "trusses": "trus", 
    "cables": "cabl", 
    "springs": "spri",
    "quads": "quad"
}

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


conversion_factor = get_conversion_factor()


def english_to_sofi(word):
    
    return dictionary[word]


def round(f, n = 3):
    
    a = 10 ** n
    
    return int(f * a) / a
            
    

class Description:
    
    def __init__(self, s):
        
        self.string = s.strip()

    def get_prop(self):

        i1 = self.string.find("[")
        i2 = self.string.find("]")

        if ((i1 != -1) and (i2 != -1) and (i2 > i1)):

            return self.string[(i1 + 1):(i2)]

        return ""


    def get_name(self):

        i1 = self.string.find("{")
        i2 = self.string.find("}")

        if ((i1 != -1) and (i2 != -1) and (i2 > i1)):
            
            return self.string[(i1 + 1):(i2)]

        return ""


    def get_no(self):

        return -1

        i1 = self.string.find("[")
        i2 = self.string.find("{")

        if ((i1 == -1) and (i2 == -1)):

            return int(self.string)

        j = i1 if (i2 == -1) else i2

        return int(self.string[0:(j + 1)].strip())


class StructuralElement():

    def __init__(self, typ, geo, grp = -1):
        
        self.typ = typ
        self.geo = geo

        self.grp = grp

        # default values
        self.no = -1
        self.prop = ""
        self.name = ""
        
        self.strict_naming = False
        self.build_base()


    def build_base(self):

        attr = Description(rs.ObjectName(self.geo))

        self.no = attr.get_no()
        if (self.no != -1):
            self.strict_naming = True

        self.name = attr.get_name()
        self.prop = attr.get_prop()
        
        
    def output_base(self):
    
        return (self.typ + " no " + str(self.no))


class Node(StructuralElement):
    
    
    def __init__(self, obj):
        
        StructuralElement.__init__(self, "node", obj)
        self.build()
		
		
    def build(self):

        coordinates = rs.PointCoordinates(self.geo)
        k = conversion_factor
        self.x = round(+ coordinates[0] * k, 5)
        self.y = round(+ coordinates[1] * k, 5)
        self.z = round(+ z_coordinate_sign * coordinates[2] * k, 5)
		
		
    def export(self):
        
        output = self.output_base()
        output += " x " + str(self.x)
        output += " y " + str(self.y)
        output += " z " + str(self.z)
        output += " " + self.prop
        if (self.name != ""):
            output += "$ " + self.name
        output += "\n"
        return output
        
        
    def distance_to(self, n):
        
        d = ( (self.x - n.x) ** 2 + (self.y - n.y) ** 2 + (self.z - n.z) ** 2 ) ** 0.5
        
        return d
        
        
    def identical_to(self, n):
        
        return (self.distance_to(n) < tolerance)
        

def is_taken_number(array, no, grp = -1):
    
    for element in array:
        
        if (element.no == no and (grp == element.grp)):
                
                return True	
                
    return False


class ElementList:

    def __init__(self, name):
        
        self.name = name
        self._list = []
        
    def add(self, element):
        
        self._list.append(element)
    
    def is_taken_number(number, group = -1):
        
        for element in self._list:
            
            if (element.no == number and element.grp == group):
                
                return True
                
        return False
    
    def get_available_number(self, grp):
    
        number = 1
        while(is_taken_number(self._list, number, grp)):
            
            number += 1

        return number
        

    def export(self):

        output = "\n\n!*!Label " + self.name + "\n"

        for item in self._list:
            
            output += item.export() 
            
        output += "\n"

        return output


class StructuralModel:
    
    
    def __init__(self, name):	
    
        self.name = name	
        
        self.nodes = ElementList("Nodes")
                
        self.gdiv = 1000
        self.current_group = -1
        
        self.output_header = "$ generated by Giraffe for Rhino\n"
        self.output_header += "+prog sofimsha\nhead " + self.name + "\n\nsyst init gdiv 1000\n"

        self.output_footer = "\nend"

			
    def add_node(self, pt):
            
        already_in_list = False

        n = Node(pt)
        
        for node in self.nodes._list:
            if n.identical_to(node) and (n.no != -1) and (node.strict_naming == False):
                node.no = n.no
                already_in_list = True
        
        if (not already_in_list):
            
            n.no = self.nodes.get_available_number(-1)
            self.nodes.add(n)
        
						
    def export(self):
        
        return self.output_header + self.nodes.export() + self.output_footer
        
    
    def make_file(self):
        
        f = open("system.dat", "w")
        
        f.write(self.export())
		
        f.close()
		

def Main():
    
    sofi = StructuralModel("some structure")
                    
    objects = rs.ObjectsByLayer("input::nodes")
    for obj in objects:
        sofi.add_node(obj)
                    
    sofi.make_file()
    
    rs.CurrentLayer("input")
    
Main()

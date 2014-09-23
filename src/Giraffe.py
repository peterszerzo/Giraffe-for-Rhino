"""

Giraffe for Rhino v1.0.0 Beta
Peter Szerzo

"""

import math
import string
import rhinoscriptsyntax as rs
import rhinoinput as ri

point_elements = ["node"]

tolerance = 0.1 # how close points have to be to be considered one


class GiraffeLayer():
    

    @classmethod
    def get_all(self):

        layer_names = rs.LayerNames()

        layers = []

        for layer_name in layer_names:
        
            layers.append(GiraffeLayer(layer_name))

        return layers


    def __init__(self, name):
        
        self.name = name
        self.path = name.split("::")
        self.depth = len(self.path)
        self.last = self.path[self.depth - 1]
        
        return self


    def create(self):
    
        mom = ""
        
        # create all ancestor layers if not yet created
        for s in self.path:
            
            son = s if (mom == "") else (mom + "::" + s)

            mommy = None if mom == "" else mom

            if(not rs.IsLayer(son)):

                rs.AddLayer(s, color = None, visible = True, locked = False, parent = mommy)

            mom = son
            
        return self    


    def get_geometry(self):

        return rs.ObjectsByLayer(self.name)


    def clear(self):
    
        objects = rs.ObjectsByLayer(self.name)

        for obj in objects:

            rs.DeleteObject(obj) 
            
        return self



class StructuralElement:


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

        attr = ri.RhinoInput(rs.ObjectName(self.geo))

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
        self.x = round(+ coordinates[0], 5)
        self.y = round(+ coordinates[1], 5)
        self.z = round(+ coordinates[2], 5)
        

    def distance_to(self, n):
        
        d = ( (self.x - n.x) ** 2 + (self.y - n.y) ** 2 + (self.z - n.z) ** 2 ) ** 0.5
        
        return d
        
        
    def identical_to(self, n):
        
        return (self.distance_to(n) < tolerance)


    def export(self):
        
        output = self.output_base()
        output += " x " + str(self.x) + "*#conversion_factor"
        output += " y " + str(self.y) + "*#conversion_factor"
        output += " z " + str(self.z) + "*#conversion_factor"
        output += " " + self.prop
        if (self.name != ""):
            output += "$ " + self.name
        output += "\n"

        return output



class LineElement(StructuralElement):


    def __init__(self, obj, type):

        StructuralElement.__init__(self, type, obj)


    def build(self):

        return True


    def identical_to(self, elem):

        return False


    def export(self):

        return True



class ElementList:


    def __init__(self, name):
        
        self.name = name
        self._list = []
        self._errors = []
        

    def contains(self, element):

        already_in_list = False
        
        for item in self._list:

            if element.identical_to(item):

                already_in_list = True

        return already_in_list


    def is_taken_number(self, number, grp = -1):
        
        for element in self._list:
            
            if (element.no == number and element.grp == grp):
                
                return True
                
        return False


    def get_conflicting_element(self, new_element):

        for element in self._list:
            
            if (element.no == new_element.no and element.grp == new_element.grp):
                
                return element
                
        return None


    def get_available_number(self, grp = -1):
    
        number = 1

        while(self.is_taken_number(number, grp)):
            
            number += 1

        return number


    # add first available number to any element
    def add_number(self, element):

        element.no = self.get_available_number(element.grp)


    # if there is a numbering conflict, resolve using the following rules:
    #   -> if the element already in the list does not have strict naming, the new element keeps its number
    #   -> if both conflicting elements have strict naming, the old element keeps its number. warning thrown 
    def resolve_numbering_conflict(self, existing_element, new_element):

        if (not existing_element.strict_naming):

            self.add_number(existing_element)

        else:

            self.add_number(new_element)

            self._errors.append("Numbering conflict, node number " + str(existing_element.no) + " changed to " + str(new_element.no) + ".")


    def add(self, new_element):
        
        if(not self.contains(new_element)):

            if(new_element.no == -1):

                self.add_number(new_element)

            else:

                conflict = self.get_conflicting_element(new_element)

                if (not conflict is None):

                    self.resolve_numbering_conflict(conflict, new_element)
            
            self._list.append(new_element)     


    def export(self):

        output = "\n\n!*!Label " + self.name + "\n"

        for item in self._errors:
            
            output += "$ " + item + "\n"

        for item in self._list:
            
            output += item.export() 
            
        output += "\n"

        return output



class StructuralModel:
    

    dictionary = {
        "nodes": "node", 
        "beams": "beam", 
        "trusses": "trus", 
        "cables": "cabl", 
        "springs": "spri",
        "quads": "quad"
    }


    unit_conversion = {
        2: 0.001,
        3: 0.01,
        4: 1.0,
        8: 0.0254,
        9: 0.3048
    }
    

    def __init__(self, name):   
    
        self.setup()

        self.name = name    
        
        self.nodes = ElementList("Nodes")
                
        self.gdiv = 1000
        self.current_group = -1
        
        self.output_header = "$ generated by Giraffe for Rhino\n"
        self.output_header += "+prog sofimsha\nhead " + self.name + "\n\nsyst init gdiv 1000\n"

        self.output_header += "\nlet#conversion_factor " + str(self.conversion_factor)

        self.output_footer = "\nend"


    def setup(self):

        self.conversion_factor = StructuralModel.unit_conversion[rs.UnitSystem()]


    def add_objects_from_layer(self, layer):

        if (layer.depth > 1):

            objects = layer.get_geometry()

            if(layer.path[1] == "nodes"):

                for obj in objects:

                    n = Node(obj)

                    self.nodes.add(n)


    def export(self):
        
        return self.output_header + self.nodes.export() + self.output_footer


    def make_file(self):
        
        f = open("system.dat", "w")
        
        f.write(self.export())
        
        f.close()



def Main():
    
    sofi = StructuralModel("structure")

    layers = GiraffeLayer.get_all()
                    
    for layer in layers:

        sofi.add_objects_from_layer(layer)
                    
    sofi.make_file()
    
    rs.CurrentLayer("input")
    
Main()
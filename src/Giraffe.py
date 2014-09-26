"""
Giraffe for Rhino v1.0.0 Beta
Peter Szerzo
"""

import math
import string
import rhinoscriptsyntax as rs
import rhinoinput as ri
import giraffe_configure as gc
import giraffe_setup as gs

def get_output_path():

    """Returns output path as 'system.dat' in the directory of the Rhino model (Windows + Mac OS)."""

    path = rs.DocumentPath()

    i = path.rfind("\\")

    if gc.operating_system == "mac":

        path = path[:i-3] + ".dat" 

    elif gc.operating_system == "win":

        path = path[:i] + "/system.dat" 

    return path

class GiraffeLayer():
    

    endpoints = None
    dummy = None


    @classmethod
    def setup(self):

        """Sets up layers."""

        # create basic input layer structure if it does not yet exist
        GiraffeLayer("input::nodes").create()
        GiraffeLayer("input::beams").create()

        self.dummy = GiraffeLayer("giraffe-dummy").create().unlock().clear().set_color([150, 150, 100])
        self.endpoints = GiraffeLayer("output::startpoints").create().unlock().clear().set_color([85, 26, 139])


    @classmethod
    def teardown(self):

        """Sets dummy as current layer and locks output."""

        self.dummy.set_current()
        self.endpoints.lock()


    @classmethod
    def get_all(self):

        """Returns a list of all layers as GiraffeLayer objects."""

        layer_names = rs.LayerNames()

        layers = []

        for layer_name in layer_names:

            layer = GiraffeLayer(layer_name)
        
            layers.append(layer)

        return layers


    @classmethod
    def get_all_structural(self):

        """Returns a list of all layers containing structural geometry GiraffeLayer objects."""

        layer_names = rs.LayerNames()

        layers = []

        for layer_name in layer_names:

            layer = GiraffeLayer(layer_name)
        
            if layer.is_structural():

                layers.append(layer)

        # sort layers to make sure numbered nodes are added first and to maintain regular order
        layers.sort(key = lambda x: x.to_int())

        return layers


    def __init__(self, name):

        """Constructor.
        Parameters:
          name = object name
        """
        
        self.name = name
        self.path = name.split("::")
        self.depth = len(self.path)
        self.last = self.path[self.depth - 1]
        
        return self


    def create(self):
    
        """Creates layer within Rhino, including all ancestors.
        Returns:
          self
        """

        if rs.IsLayer(self.name):

            return self

        mom = ""
        
        for s in self.path:
            
            son = s if (mom == "") else (mom + "::" + s)

            mommy = None if mom == "" else mom

            if not rs.IsLayer(son):

                rs.AddLayer(s, color = None, visible = True, locked = False, parent = mommy)

            mom = son
            
        return self


    def is_structural(self):

        """Returns whether layer is a valid structural layer."""

        if self.depth > 1:

            if (self.path[0] == "input") and (self.path[1] in gs.all_elements):

                return True

        return False


    def to_int(self):

        """Assigns integer value to the layer, adhering to the proper order."""

        if not self.is_structural():

            return -1

        value = gs.all_elements.index(self.path[1]) * 100

        value += (self.depth - 2) * 10

        return value


    def set_current(self):

        """Sets layer as current.
        Returns:
          self
        """

        rs.CurrentLayer(self.name)

        return self


    def set_color(self, c):

        """Sets layer color.
        Parameters:
          c = color as an RGB value array
        Returns:
          self
        """

        rs.LayerColor(self.name, c)

        return self


    def get_geometry(self):

        """Returns geometry from a given layer as a list. Sublayer objects are not included."""

        return rs.ObjectsByLayer(self.name)


    def get_allowed_geometry(self):

        """Returns geometry that is allowed in the current layer (point for nodes, line for beams etc.)"""

        objects = self.get_geometry()

        allowed_objects = []

        for obj in objects:

            if rs.ObjectType(obj) == gs.allowed_object_types[self.path[1]]:

                allowed_objects.append(obj)

        return allowed_objects


    def clear(self):

        """Deletes all objects from a given layer. Sublayer objects are kept.
        Returns:
          self
        """
    
        objects = self.get_geometry()

        for obj in objects:

            rs.DeleteObject(obj) 
            
        return self


    def lock(self):

        """Locks layer.
        Returns:
          self
        """

        rs.LayerLocked(self.name, True)

        return self


    def unlock(self):

        """Unlocks layer.
        Returns:
          self
        """

        rs.LayerLocked(self.name, False)

        return self


    def get_grp(self):

        """Returns group number from layer; -1 if not specified."""

        grp = -1

        if self.depth > 2:

            inp = ri.RhinoInput(self.path[2])

            grp = inp.get_no()

        return grp


    def get_grp_string(self):

        """Returns a string representation of the group number (e.g. 'grp 2')."""

        grp = self.get_grp()

        if grp == -1:

            return ""

        return "grp " + str(grp)


    def get_name(self):

        """Returns group name from layer (last child only)."""

        return ri.RhinoInput(self.last).get_name()


    def get_prop(self):

        """Returns structural properties from layer (last child only)."""

        if self.depth == 2:

            return ""

        return ri.RhinoInput(self.last).get_prop()


    def get_type(self):

        """Returns element type."""

        return gs.plural_to_sofi[self.path[1]]


    def get_export_header(self):

        """Return export header (SOFiSTiK label)."""

        name = self.get_name()

        if (self.name == "input::nodes"):

            name = "user-specified"

        grp_string = self.get_grp_string()

        if grp_string != "":

            grp_string = " " + grp_string

        return "\n!*!Label " + self.path[1] + " .." + grp_string + " .. " + name + "\n"


    def export(self):

        """Returns SOFiSTiK export."""

        name = self.get_name() 

        typ = self.get_type()
        prop = self.get_prop()

        output = self.get_export_header()

        grp_string = self.get_grp_string()

        if grp_string != "":

            output += grp_string + "\n"

        if prop != "":

            output += typ + " prop " + prop + "\n"

        return output



class StructuralElement:


    def __init__(self, geo, typ, grp = -1):

        """Constructor.
        Parameters:
          geo = Guid from Rhino; None if it does not exist (e.g. line endpoints)
          typ = object type
          grp = group number
        """
        
        self.geo = geo
        self.typ = typ

        self.grp = grp

        # default values
        self.no = -1
        self.prop = ""
        self.name = ""
        self.strict_naming = False

        # reference to containing layer
        self.layer = None

        self.build_base()


    def build_base(self):

        """Sets element attributes based on Guid name from Rhino."""

        # start- and endpoints of lines are nodes, but they do not need to have a point object associated to them
        # in this case, self.geo is None and the no, prop and name attributes stay as the default values set in the constructor
        if (self.geo):

            attr = ri.RhinoInput(rs.ObjectName(self.geo))

            self.no = attr.get_no()
            if (self.no != -1):
                self.strict_naming = True

            self.name = attr.get_name()
            self.prop = attr.get_prop()
        

    def export_base(self):

        """SOFiSTiK export common to all elements."""
    
        return (self.typ + " no " + str(self.no))



class Node(StructuralElement):
    

    def __init__(self, obj, coordinates = None):

        """Constructor.
        Parameters:
          obj = Guid from Rhino
          coordinates = if there is no Guid, coordinates should be set
        """
        
        StructuralElement.__init__(self, obj, "node")
        self.build(coordinates)
        
        
    def build(self, coordinates = None):

        """Build node from Rhino Guid or coordinates, whichever is set.
        Parameters:
          coordinates = coordinate array passed from constructor
        """

        # start- and endpoints of lines are nodes, but they do not need to have a point object associated to them
        # in this case, point coordinates should be set
        if (self.geo):
            coordinates = rs.PointCoordinates(self.geo)

        self.x = round(+ coordinates[0], 5)
        self.y = round(+ coordinates[1], 5)
        self.z = round(+ coordinates[2], 5)
        

    def distance_to(self, n):
        
        """Returns distance to specified node.
        Parameters:
          n = node to which distance is evaluated
        Returns:
          distance to n
        """

        d = ( (self.x - n.x) ** 2 + (self.y - n.y) ** 2 + (self.z - n.z) ** 2 ) ** 0.5
        
        return d
        
        
    def identical_to(self, n):

        """Returns True if node overlaps with specified node (distance smaller than tolerance)."""
        
        return (self.distance_to(n) < gc.tolerance)


    def export_coordinates(self):

        """Returns coordinate export."""

        return "x " + str(self.x) + "*#cf" + " y " + str(self.y) + "*#cf" + " z " + str(self.z) + "*#cf"


    def export(self):
        
        """Returns SOFiSTiK export."""

        output = self.export_base() + " " + self.export_coordinates() + " " + self.prop

        if (self.name != ""):
            output += "$ " + self.name

        return output


class SpringSN(StructuralElement): # single node spring
    

    def __init__(self, obj):

        """Constructor.
        Parameters:
          obj = Guid from Rhino
          coordinates = if there is no Guid, coordinates should be set
        """
        
        StructuralElement.__init__(self, obj, "spri")
        self.build()

        # node is not set in the constructor
        self.n = None
        
        
    def build(self):

        """Build node from Rhino line."""

        pt1 = rs.CurveStartPoint(self.geo)
        pt2 = rs.CurveEndPoint(self.geo)

        # get spring direction
        self.dx = round(+ pt2[0] - pt1[0], 5)
        self.dy = round(+ pt2[1] - pt1[1], 5)
        self.dz = round(+ pt2[2] - pt1[2], 5)

        # normalize direction
        d = (self.dx ** 2 + self.dy ** 2 + self.dz ** 2) ** 0.5
        self.dx /= d
        self.dy /= d
        self.dz /= d

                
        
    def identical_to(self, elem):

        """Returns True if node overlaps with specified node (distance smaller than tolerance)."""
        
        return (self.n == elem.n) and (math.fabs(self.dx - elem.dx) < 0.001) and (math.fabs(self.dy - elem.dy) < 0.001) and (math.fabs(self.dz - elem.dz) < 0.001)


    def export_direction(self):

        """Returns coordinate export."""

        return "dx " + str(self.dx) + " dy " + str(self.dy) + " dz " + str(self.dz)


    def export(self):
        
        """Returns SOFiSTiK export."""

        output = self.export_base() + " na " + str(self.n.no) + " " + self.export_direction() + " " + self.prop

        if (self.name != ""):
            output += "$ " + self.name

        return output        



class LineElement(StructuralElement):


    def __init__(self, obj, typ):

        """Constructor."""

        StructuralElement.__init__(self, obj, typ)

        # nodes are not set in the constructor, but assigned in the StructuralModel class once nodes are added
        self.n1 = None
        self.n2 = None


    def build(self):

        """Placeholder for a method analogous to Node.build()."""

        return True


    def get_point_on(self, s):

        """Gets point on element.
        Parameters:
          s = curve parameter between 0 (startpoint) and 1 (endpoint).
        """

        x = self.n1.x * (1 - s) + self.n2.x * s
        y = self.n1.y * (1 - s) + self.n2.y * s
        z = self.n1.z * (1 - s) + self.n2.z * s

        return [x, y, z]


    def mark_start_point(self):

        """Marks start point by drawing a point in 1/10 the way towards the endpoint."""

        GiraffeLayer.endpoints.set_current()
        rs.AddPoint(self.get_point_on(0.1))


    def identical_to(self, elem):

        """Returns true for overlapping line elements (identical start- and endnodes)."""

        return (self.n1 == elem.n1) and (self.n2 == elem.n2)


    def export(self):

        """Returns SOFiSTiK export."""

        output = self.export_base() + " na " + str(self.n1.no) + " ne " + str(self.n2.no) + " " + self.prop

        if (self.name != ""):
            output += "$ " + self.name

        return output


class AreaElement(StructuralElement):


    def __init__(self, obj):

        """Constructor."""

        StructuralElement.__init__(self, obj, "quad")

        # nodes are not set in the constructor, but assigned in the StructuralModel class once nodes are added
        self.n1 = None
        self.n2 = None
        self.n3 = None
        self.n4 = None


    def build(self):

        """Placeholder for a method analogous to Node.build()."""

        return True


    def identical_to(self, elem):

        """Returns true for overlapping line elements (identical start- and endnodes)."""

        return (self.n1 == elem.n1) and (self.n2 == elem.n2) and (self.n3 == elem.n3) and (self.n4 == elem.n4)


    def export(self):

        """Returns SOFiSTiK export."""

        output = self.export_base() + " n1 " + str(self.n1.no) + " n2 " + str(self.n2.no) + " n3 " + str(self.n3.no) + " n4 " + str(self.n4.no) + " " + self.prop

        if (self.name != ""):
            output += "$ " + self.name

        return output


class ElementList:


    def __init__(self, name):

        """Constructor."""
        
        self.name = name
        self._list = []
        self._errors = []
        

    def get_identical_to(self, element):

        """Returns first element in the list that is identical to the specified element. Returns None if none found."""

        already_in_list = False
        
        for item in self._list:

            if element.identical_to(item):

                return item

        return None


    def is_taken_number(self, number, grp = -1):
        
        """Returns True if a number if taken in a given group.
        Parameters:
          number = element number
          grp = group number
        Returns:
          whether the given number/group combination is already taken
        """

        for element in self._list:
            
            if (element.no == number) and (element.grp == grp):
                
                return True
                
        return False


    def get_available_number(self, grp = -1):
    
        """Returns lowest available number for a given group in the list.
        Parameters:
          grp = group number
        """

        number = 1

        while(self.is_taken_number(number, grp)):
            
            number += 1

        return number    


    def get_conflicting_element(self, new_element):

        """Returns element with a numbering conflict.
        Parameters:
          new_element
        Returns:
          conflicting element
        """

        for element in self._list:
            
            if (element.no == new_element.no) and (element.grp == new_element.grp):
                
                return element
                
        return None


    def add_number(self, element):

        """Add first available number to any element."""

        element.no = self.get_available_number(element.grp)

 
    def resolve_numbering_conflict(self, existing_element, new_element):

        """Resolves numbering conflict between two elements based on specified rules.
        Parameters:
          existing_element = element already in list
          new_element = element to be inserted into the list
        Returns:
          self
        """

        # rule 1: if the element already in the list does not have strict naming, the new element keeps its number
        if not existing_element.strict_naming:

            self.add_number(existing_element)

        # rule 2: if both conflicting elements have strict naming, the old element keeps its number; warning thrown
        else:

            self.add_number(new_element)

            self._errors.append("Numbering conflict, node number " + str(existing_element.no) + " changed to " + str(new_element.no) + ".")

        return self


    def add(self, new_element):

        """
        Adds new element to the list.
        If identical element is found in the list, the method returns that element and does not add the new one.
        If the new element has a -1 number (not specified), a new number is assigned.
        If the new element has a number, potential numbering conflicts are resolved.
        """
        
        identical = self.get_identical_to(new_element)

        if identical:

            return identical

        else:

            if new_element.no == -1:

                self.add_number(new_element)

            else:

                conflict = self.get_conflicting_element(new_element)

                if conflict:

                    self.resolve_numbering_conflict(conflict, new_element)
            
            self._list.append(new_element)

            return new_element


    def export_errors(self):

        """Returns all errors."""

        output = ""

        for item in self._errors:
            
            output += "$ " + item + "\n"

        return output


    def export(self):

        """Returns SOFiSTiK export."""

        if self._list == []:

            return ""

        output = "\n\n" + "!*!Label *** " + self.name.upper() + " ***\n"

        output += self.export_errors()

        current_layer = -1
        previous_layer = -1

        for item in self._list:
            
            previous_layer = current_layer

            current_layer = item.layer

            # if layer changes while traversing list, add layer export at this location
            if current_layer and (previous_layer != current_layer):

                output += current_layer.export()

            # special case for the endpoints of structural elements that do not have a Guid in Rhino
            elif (not current_layer) and (previous_layer != current_layer):

                output += "\n!*!Label nodes .. .. added and numbered by Giraffe" + "\n"

            output += item.export() + "\n"

        return output



class StructuralModel:
    

    unit_conversion = {
        2: 0.001,
        3: 0.01,
        4: 1.0,
        8: 0.0254,
        9: 0.3048
    }
    

    def __init__(self, name):   

        """Constructor
        Parameters:
          name = model name
        """
    
        self.conversion_factor = StructuralModel.unit_conversion[rs.UnitSystem()]

        self.name = name    
        
        self.nodes = ElementList("nodes")
        self.springs_sn = ElementList("single node springs")
        self.line_elements = ElementList("line elements")
        self.area_elements = ElementList("area elements")
                
        self.gdiv = 1000
        self.current_group = -1

        return self


    def add_node(self, obj, typ_sofi, layer):

        """Adds node from object."""

        n = Node(obj)
        n.layer = layer

        self.nodes.add(n)


    def add_line_element(self, obj, typ_sofi, layer):

        """Adds line element from object."""

        bm = LineElement(obj, typ_sofi)
        bm.n1 = self.nodes.add(Node(None, rs.CurveStartPoint(obj)))
        bm.n2 = self.nodes.add(Node(None, rs.CurveEndPoint(obj)))

        bm.mark_start_point()
        bm.layer = layer

        self.line_elements.add(bm)


    def add_spring_sn(self, obj, typ_sofi, layer):

        """Adds single node spring element from object."""

        sp = SpringSN(obj)
        sp.n = self.nodes.add(Node(None, rs.CurveStartPoint(obj)))

        sp.layer = layer

        self.springs_sn.add(sp)   


    def add_area_element(self, obj, typ_sofi, layer):

        """Adds area element from object."""

        qd = AreaElement(obj)

        pts = rs.SurfacePoints(obj)

        qd.n1 = self.nodes.add(Node(None, pts[0]))
        qd.n2 = self.nodes.add(Node(None, pts[1]))
        qd.n3 = self.nodes.add(Node(None, pts[3]))
        qd.n4 = self.nodes.add(Node(None, pts[2]))

        qd.layer = layer

        self.area_elements.add(qd) 


    def add_objects_from_layer(self, layer):

        """Adds objects from a given layer to the ElementLists of the structural model."""

        objects = layer.get_allowed_geometry()

        typ_plural = layer.path[1]
        typ_sofi = gs.plural_to_sofi[typ_plural]

        for obj in objects:

            # !! REFACTOR TO CALL PROGRAMATICALLY -> ELIMINATE CONDITIONALS !!

            if typ_plural in gs.point_elements:

                self.add_node(obj, typ_sofi, layer)

            if typ_plural in gs.line_elements:

                self.add_line_element(obj, typ_sofi, layer)

            if typ_plural in gs.spring_elements:

                self.add_spring_sn(obj, typ_sofi, layer)         

            if typ_plural in gs.area_elements:

                self.add_area_element(obj, typ_sofi, layer) 

        return self


    def build(self):

        """Builds model from current layer structure within the Rhino model."""

        layers = GiraffeLayer.get_all_structural()
                    
        for layer in layers:

            self.add_objects_from_layer(layer)

        return self


    def get_export_header(self):

        """Returns export header."""

        header = "$ generated by Giraffe for Rhino\n"
        header += "+prog sofimsha\nhead " + self.name + "\n\n\n!*!Label *** SETUP ***\n" + "\nsyst 3d gdir negz gdiv 1000\n"

        header += "\nlet#cf " + str(self.conversion_factor) + " $ conversion factor\n"

        return header


    def export(self):

        """Returns SOFiSTiK export."""
        
        return self.get_export_header() + self.nodes.export() + self.line_elements.export() + self.area_elements.export() + self.springs_sn.export() + "\n\nend"


    def make_file(self):

        """Creates or updates exported file.
        Returns:
          self
        """

        f = open(get_output_path(), "w")
        
        f.write(self.export())
        
        f.close()

        return self



def Main():
    
    GiraffeLayer.setup()

    sofi = StructuralModel("structure").build().make_file()

    GiraffeLayer.teardown()
    
Main()
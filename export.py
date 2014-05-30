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

f = open("system.dat", "w")

def english_to_sofi(word):
	
    if (word == "nodes"):
        return "node"
    elif (word == "beams"):
        return "beam"
    elif (word == "trusses"):
        return "trus"
    elif (word == "cables"):
        return "cabl"
    elif (word == "springs"):
        return "spri"	


def is_taken_number(array, no, grp):
	
    for element in array:
	
        if (element.no == no):
		
            if (grp == -1):
                return True
				
            elif (grp == element.grp):
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
        self.description = ""
		
        if (s != ""):
		
            i1 = s.find("[")
            i2 = s.find("]")
            
            j1 = s.find("{")
            j2 = s.find("}")
            
            if (i1 == -1 or i2 == -1):
			
                self.no = int(s.strip())
			
            else:
				
                no_string = s[0:(i1)].strip()
                self.no = (-1) if (no_string == "") else int(no_string)
                self.prop = s[(i1 + 1):(i2)]



class Node:
	
	
	def __init__(self, no = -1, x = 0, y = 0, z = 0, prop = ""):
	
		self.no = no
		self.x = x
		self.y = y
		self.z = z
		self.prop = prop
		self.strict_naming = False
		
		
	def build_from_point(self, obj):
	    
	    attr = Description(rs.ObjectName(obj))
	    coordinates = rs.PointCoordinates(obj)
	    self.no = attr.no
	    self.x = coordinates[0]
	    self.y = coordinates[1]
	    self.z = coordinates[2]
	    self.prop = attr.prop
		
		
	def export(self):
	
		output = "node no " + str(self.no)
		output += " x " + str(self.x)
		output += " y " + str(self.y)
		output += " z " + str(self.z)
		output += " " + self.prop + "\n"
		
		return output	
		
		
	def distance_to(self, n):
	
		return ( (self.x - n.x) ** 2 + (self.y - n.y) ** 2 + (self.z - n.z) ** 2 ) ** 0.5
		
		
	def identical_to(self, n):
	    
	    return (self.distance_to(n) < 0.001)



class Member:	


	def __init__(self, typ, grp, no, na, ne, prop):

		self.typ = typ
		self.grp = grp
		self.no = no
		self.na = na
		self.ne = ne
		self.prop = prop
		self.strict_naming = False	
		
		
	def export(self):
	
		output = self.typ + " no " + str(self.no)
		output += " na " + str(self.na)
		output += " ne " + str(self.ne)
		output += " " + self.prop + "\n"
		
		return output
		

		
class StructuralModel:


	def __init__(self, name):
		
		self.name = name
		
		# fan stands for first available number
		
		self.nodes = []
		self.fan_node = 1
		
		self.members = []
		self.fan_member = 1
		
		self.gdiv = 1000
		
		self.output_header = "$ generated by Giraffe for Rhino\n"
		self.output_header += "+prog sofimsha\nhead " + self.name + "\n\nsyst init gdiv 1000\n"
		self.output_nodes = "\n\n!*!Label Nodes\n"
		self.output_members = "\n!*!Label Structural Members"
		self.output_footer = "\nend"
		self.output = ""
		
		
	def add_node(self, n):
	
	    if (n.no == -1):
	        
	        for node in self.nodes:
		
	            if n.identical_to(node):
	                n.no = node.no
	                
	        if (n.no == -1):
	           
	           n.no = self.fan_node
	           self.nodes.append(n)

	    else:
			
	        n.strict_naming = True
	        self.nodes.append(n)
	        
	        l = len(self.nodes)
	        
	        for i in range(0, l - 1):
		        
	            if self.nodes[l - 1].no == self.nodes[i].no:
	                self.nodes[i].no = self.fan_node
	        
	        
	    while(is_taken_number(self.nodes, self.fan_node, -1)):
	        self.fan_node += 1
	        
	    return n
			
		
	def add_member(self, element, element_type, grp):
	
	    attr = Description(rs.ObjectName(element))
	
	    pa = rs.CurveStartPoint(element)
	    pe = rs.CurveEndPoint(element)
		
	    node_a = self.add_node(Node(-1, pa[0], pa[1], pa[2], ""))
	    node_e = self.add_node(Node(-1, pe[0], pe[1], pe[2], ""))
		
	    if (attr.no == -1):
	        
	        attr.no = self.fan_member
	        
	        
	    else:
	        
	        """
	        l = len(self.members)
	        
	        for i in range(0, l - 1):
	
	            if (self.members[l - 1].no == self.members[i].no) and (self.members[l - 1].grp == self.members[i].grp):
	                self.members[i].no = self.fan_member
	        """


	    e = Member(element_type, grp, attr.no, node_a.no, node_e.no, attr.prop)
	    self.members.append(e)
	    
	    self.output_members += e.export()
		
	    while(is_taken_number(self.members, self.fan_member, grp)):
	    	self.fan_member += 1
		
				
	def export_nodes(self):

		for node in self.nodes:
			self.output_nodes += node.export()	
			
		self.output_nodes += "\n"	
		
		
	def export(self):
	
		return self.output_header + self.output_nodes + self.output_members + self.output_footer
		
		

def Main():
    
    sofi = StructuralModel("some structure")
    
    layer_names = rs.LayerNames()
    	
    for name in layer_names:
    
    	layer = Layer(name)
    
    	if (layer.path[0] == "input") and (layer.depth > 1):
    	
    		if (layer.path[1] == "nodes"):
    		
    			objects = rs.ObjectsByLayer(layer.name)

    			for obj in objects:
    			    n = Node()
    			    n.build_from_point(obj)
    			    sofi.add_node(n)
    				
    	
    		elif (layer.depth > 2):
    	
	    		attr = Description(layer.last)
	    		group = attr.no
	    		prop = attr.prop
	    		
	    		element_type = english_to_sofi(layer.path[1])	
	    		
	    		if (layer.depth == 3):
	    		
	    			sofi.output_members += "\ngrp " + str(group) + "\n"
	    		
	    		if (prop != ""):
	    		
	    			sofi.output_members += "\n" + element_type + " prop " + prop + "\n"
	    	
	    		sofi.fan_member = 1
	    		while(is_taken_number(sofi.members, sofi.fan_member, group)):
	    			sofi.fan_member += 1
	    		
	    		objects = rs.ObjectsByLayer(layer.name)
	
	    		for obj in objects:
	    			
	    			sofi.add_member(obj, element_type, group)

    sofi.export_nodes()
    
    
    f.write(sofi.export())
    f.close()
    
Main()
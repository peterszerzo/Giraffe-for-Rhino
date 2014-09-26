plural_to_sofi = {

   "nodes": "node", 
   "beams": "beam", 
   "trusses": "trus", 
   "cables": "cabl", 
   "springs": "spri",
   "quads": "quad"

}

allowed_object_types = {
    
   "nodes": 1,
   "beams": 4,
   "trusses": 4,
   "cables": 4,
   "springs": 4,
   "quads": 8

}

object_types = {

   "Point"      : 1,
   "PointCloud" : 2,
   "Curve"      : 4,
   "Surface"    : 8,
   "Polysrf"    : 16, 
   "Mesh"       : 32,
   "Light"      : 256,
   "Annotation" : 512,
   "Block"      : 4096,
   "TextDot"    : 8192,
   "Grip"       : 16384,
   "Detail"     : 32768,
   "Hatch"      : 65536,
   "Morph"      : 131072,
   "Cage"       : 134217728,
   "Phantom"    : 268435456,
   "Clip"       : 536870912

}

point_elements = [ "nodes" ]
line_elements = [ "beams", "trusses", "cables" ]
area_elements = [ "quads" ]
spring_elements = [ "springs" ]

all_elements = point_elements + line_elements + area_elements + spring_elements
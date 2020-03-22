import numpy as np 
from scipy.spatial import ConvexHull
import ansystotal.ansyspreprocessing.ansys_file_reader as afr 

# After calculation
# encapsulate within a function 
# and use it in the g & r formulations
# for scar tissue !

nodes_fname = "nlist.dat"
elems_fname = "elist.dat"

reader_object = afr.ListReader()
nodes = reader_object.read_nodes(nodes_fname)
elems = reader_object.read_elements(elems_fname)

nodes_in_elem = elems.values()

for values in nodes_in_elem:
    elem_nodes = values[0]

# create_points_list

# Points_list

points_list = []

for node_no, coord in nodes.items():

    
from __future__ import division
from collections import defaultdict
import ansystotal.genericoperations.mesh_information_structures as mis
import numpy as np

# 1. Find the centroid of a 3d object based on its nodes -> here elements
# 2. Find the faces of the element < think about this
# 3. Find the centroid of the face.
# 4. Draw a fibre through the centroid in the face direction.
# 5. Sophisticate the code by allowing face selection in order to obtain a continuous fibre direction.
# -. allowing a physiological representation of the fibre geometry.

def get_unit_vector(input_vector):

    if type(input_vector) != np.ndarray:
        input_np_array = np.array(input_vector)
    else:
        input_np_array = input_vector

    input_np_norm  = np.linalg.norm(input_np_array)

    unit_vector = np.divide(input_np_array, input_np_norm)

    return  unit_vector

# noinspection PyPep8Naming
def centroid_finder(nodesCList):
    """
    supply the nodes C list here - nodes list with co ordinates in place.

    :param nodesCList:
    :return: centroid
    """
    x_sum = 0
    y_sum = 0
    z_sum = 0

    n_nodes = len(nodesCList)

    for node in nodesCList:
        x_sum += node.get_x()
        y_sum += node.get_y()
        z_sum += node.get_z()

    xC = float(x_sum / n_nodes)
    yC = float(y_sum / n_nodes)
    zC = float(z_sum / n_nodes)

    # returns the centroid as a tuple
    centroid = (xC, yC, zC)

    return centroid


# noinspection PyPep8Naming
def calculate_centroids(nodesDictionary, elementsDictionary):
    """

    From a list of nodes per element in a mesh provided by the elementDictionary input,
    a list of centroids per element is created and returned as a centroid dictionary.

    :param nodesDictionary:
    :param elementsDictionary:
    :return centroids:
    """
    centroids = defaultdict(list)

    for element_number, nodes_list in elementsDictionary.items():
        # Refresh temp list to accomodate the nodes of the next element.
        temp_list = []

        for nList in nodes_list:
            for node in nList:
                # create a temporary list of nodes pertaining to the current element
                temp_list.extend(nodesDictionary[node])

        # calculate the centroid for the element.
        centroid_cal = centroid_finder(temp_list)

        # Append found centroid to centroids dictionary
        centroids[element_number].append(centroid_cal)

    return centroids

# noinspection PyPep8Naming
def calculate_spheroid_fibres(centroids_dictionary):
    """

    Given the ECM configuration is dependent on the direction of the cardiac myocytes,
    why not provide  such a direction to the ones in the FEM (doing that as 0degrees in the myocardium.

    :param centroids_dictionary:
    :return fibres_dictionary:
    """
    fibres_dictionary = defaultdict(list)

    for e_no, centroid in centroids_dictionary.items():

        centroid_np = np.array(centroid)
        avec, bvec = create_circumferential_fibres(centroid_np)

        fibres_dictionary[e_no] = [avec, bvec]
    return fibres_dictionary

def create_circumferential_fibres(centroids_np):
    centroids_np = centroids_np[0]

    # Using the centroid left or right perp method
    mid_line_co_ordinate = [0.0, centroids_np[1], 0.0]
    centroids_np = centroids_np - mid_line_co_ordinate

    # centroid needs to be
    # centroid - (0, cent_y, 0) to get circ fibres in that plane

    avec_x = -centroids_np[2]
    avec_y = 0 #centroids_np[1]
    avec_z = centroids_np[0]

    bvec_x = centroids_np[2]
    bvec_y = 0 # centroids_np[1]
    bvec_z = -centroids_np[0]


    avec = np.array([avec_x, avec_y, avec_z])
    avec = avec + centroids_np
    avec = avec - centroids_np
    #
    bvec = np.array([bvec_x, bvec_y, bvec_z])
    bvec = bvec + centroids_np
    bvec = bvec - centroids_np
    # #
    long_vec = np.cross(avec, centroids_np)
    long_vec = get_unit_vector(long_vec)
    # #
    # avec = get_unit_vector(avec)
    # bvec = get_unit_vector(bvec)
    # #
    # avec = np.add(avec, long_vec)
    # bvec = np.subtract(bvec, long_vec)

    avec = get_unit_vector(avec)
    bvec = get_unit_vector(bvec)

    return avec, long_vec

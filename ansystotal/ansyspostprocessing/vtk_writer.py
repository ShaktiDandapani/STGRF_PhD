from collections import defaultdict

def vtk_fibre_writer(filename, materials_dictionary, centroid_dictionary):

    vtk_fibr_file = open(filename, "w")

    # Write down the routine for the fibres

    vtk_fibr_file.write('# vtk DataFile Version 4.2 \n')
    vtk_fibr_file.write('Fibres \n')
    vtk_fibr_file.write('ASCII \n')

    # either accept the materials dictionary or the fibres dictionary in this function

    vtk_fibr_file.write('DATASET UNSTRUCTURED_GRID\n\n')

    no_of_fibres    = len(materials_dictionary.keys())   # *3 for considering the centroid, avec and bvec

    vtk_fibr_file.write("POINTS %d float \n" %(no_of_fibres*3))

    for k, v in materials_dictionary.iteritems():

        cen_x   = centroid_dictionary[k][0][0]
        cen_y   = centroid_dictionary[k][0][1]
        cen_z   = centroid_dictionary[k][0][2]

        a_vec_x = v[0][0]
        a_vec_y = v[0][1]
        a_vec_z = v[0][2]

        b_vec_x = v[1][0]
        b_vec_y = v[1][1]
        b_vec_z = v[1][2]

        vtk_fibr_file.write("%0.3f %0.3f %0.3f \n" %(cen_x, cen_y, cen_z))
        vtk_fibr_file.write("%0.3f %0.3f %0.3f \n" %(cen_x + a_vec_x, cen_y + a_vec_y, cen_z + a_vec_z))
        vtk_fibr_file.write("%0.3f %0.3f %0.3f \n" %(cen_x + b_vec_x, cen_y + b_vec_y, cen_z + b_vec_z))

    # Write down the cells - basically lines
    vtk_fibr_file.write("CELLS %d %d \n" % (no_of_fibres * 2, no_of_fibres * 2 * 3))

    for i in range(no_of_fibres*2-2):
        vtk_fibr_file.write("2 %d %d \n" % (i, i + 1))
        vtk_fibr_file.write("2 %d %d \n" % (i, i + 2))

    vtk_fibr_file.write("CELL_TYPES %d \n" %(no_of_fibres * 2))
    for i in range(no_of_fibres):
        vtk_fibr_file.write("3 \n")

    # Close the open file :)
    vtk_fibr_file.close()



def vtk_mat_props_hexahedral_writer(filename,
                                    node_dictionary,
                                    element_dictionary,
                                    materials_dictionary,
                                    strain_dictionary,
                                    stress_dictionary):
    """
    Write out a vtk file using point data using the centroids of the finite element
    mesh and the fibres associated with each centroid

    Args:
        filename (str): Enter the filename to save the vtk file
        centroid_dictionary (dict): provide the centroid dictionary -> {e_no: [[c_x, c_y, c_z]]}
        fibre_dictionary (dict): provide the fibres dictionary -> {e_no:[[f1_x, f1_y, f1_z][f2_x, f2_y, f2_z]]}

    Returns:
        No return object. Fibres output file is written as filename.vtk

    """
    # print node_dictionary

    #Wrap the code into a function (write vtk file) - providing a generality to it

    total_number = len(node_dictionary.keys())
    vtk_file = open(filename, "w+")

    vtk_file.write('# vtk DataFile Version 4.2 \n')
    vtk_file.write('Left Ventricle \n')
    vtk_file.write('ASCII \n')
    # vtk_file.write('DATASET POLYDATA\n')
    vtk_file.write('DATASET UNSTRUCTURED_GRID\n\n')
    vtk_file.write('POINTS %d float \n' % (total_number))

    # The centroids are being writter here :)
    for _, coords in node_dictionary.iteritems():
        vtk_file.write('%.3f  %.3f  %.3f\n' % (coords[0][0] , coords[0][1] , coords[0][2]))

    total_elements = len(element_dictionary.keys())
    vtk_file.write('\nCELLS %d %d \n' %(total_elements, total_elements * 9))

    for _, nodes in element_dictionary.iteritems():
        vtk_file.write('8 %d %d %d %d %d %d %d %d\n' % (
        nodes[0][1] - 1, nodes[0][2] - 1, nodes[0][3] - 1, nodes[0][0] - 1, nodes[0][5] - 1, nodes[0][6] - 1, nodes[0][7] - 1, nodes[0][4] - 1))
    # Write out the fibres as points or lines connected to the centroid.

    vtk_file.write('\nCELL_TYPES %d\n' % (total_elements))
    for _ in element_dictionary.keys():
        vtk_file.write('12\n')

    # given the amount of information i.e. value lists
    # that many for loops for lookup tables :)

    vtk_file.write('\nCELL_DATA {}\n'.format(total_elements))
    vtk_file.write('SCALARS {} float 1\n'.format("c"))
    vtk_file.write('LOOKUP_TABLE default\n')
    for _, mat_props in materials_dictionary.iteritems():
        vtk_file.write('{}\n'.format(mat_props[0][0]))
    # if materials_dictionary is not None:
    #     vtk_file.write('\nCELL_DATA %d\n' %(total_elements))
    #     vtk_file.write('SCALARS %s float 1\n' %("c"))
    #     vtk_file.write('LOOKUP_TABLE default\n')
    #     for el_no, mat_props in materials_dictionary.iteritems():
    #         # print el_no, ': ', mat_props
    #         vtk_file.write('{}\n'.format(round(mat_props[0][0]),4))
    vtk_file.close()

# def vtk_mat_props_tetrahedral_writer(filename, centroid_dictionary, fibre_dictionary, node_dictionary, element_dictionary, materials_dictionary=None)


def vtk_mat_props_tetrahedral_writer(filename, centroid_dictionary, fibre_dictionary, node_dictionary, element_dictionary, materials_dictionary=None):
    """
    Write out a vtk file using point data using the centroids of the finite element
    mesh and the fibres associated with each centroid

    Args:.
    """
    # print node_dictionary

    # Introduce a flag so that you can plot c, k1 and k2 separate

    ## Open a separate file for the fibres to be plotted and make line components :)

    total_number = len(node_dictionary.keys())
    vtk_fib_file = open(filename, "w+")

    vtk_fib_file.write('# vtk DataFile Version 3.0 \n')
    vtk_fib_file.write('Centroids \n')
    vtk_fib_file.write('ASCII \n')
    # vtk_fib_file.write('DATASET POLYDATA\n')
    vtk_fib_file.write('DATASET UNSTRUCTURED_GRID\n\n')
    vtk_fib_file.write('POINTS %d float \n' % (total_number))

    # The centroids are being writter here :)
    for _, coords in node_dictionary.iteritems():
        vtk_fib_file.write('%.3f  %.3f  %.3f\n' % (coords[0][0] , coords[0][1] , coords[0][2]))

    total_elements = len(element_dictionary.keys())
    vtk_fib_file.write('\nCELLS %d %d \n' %(total_elements, total_elements * 5))

    for _, nodes in element_dictionary.iteritems():
        vtk_fib_file.write('4 %d %d %d %d\n' % (
        nodes[0][3] - 1, nodes[0][1] - 1, nodes[0][2] - 1, nodes[0][0] - 1))
    # Write out the fibres as points or lines connected to the centroid.

    vtk_fib_file.write('\nCELL_TYPES %d\n' % (total_elements))
    for el_no in element_dictionary.keys():
        vtk_fib_file.write('10\n')

    if materials_dictionary is not None:
        vtk_fib_file.write('CELL_DATA %d\n' %(total_elements))
        vtk_fib_file.write('SCALARS k2_value float 1\n')
        vtk_fib_file.write('LOOKUP_TABLE default\n')
        for el_no, mat_props in materials_dictionary.iteritems():
            # print el_no, ': ', mat_props
            vtk_fib_file.write('%f \n' %(mat_props[0][2]))
    else:
        pass

    vtk_fib_file.close()


def vtk_mat_props_muscle_tendon(filename, element_dictionary, nodes_dictionary, vf_dictionary):
    total_nodes     = len(nodes_dictionary.keys())
    total_elements  = len(element_dictionary.keys())

    vtk_file        = open(filename, 'w')

    vtk_file.write('# vtk DataFile Version 3.0 \n')
    vtk_file.write('Centroids \n')
    vtk_file.write('ASCII \n')
    # vtk_file.write('DATASET POLYDATA\n')
    vtk_file.write('DATASET UNSTRUCTURED_GRID\n\n')
    vtk_file.write('POINTS %d float \n' % (total_nodes))

    # The centroids are being writter here :)
    for node_number, coords in nodes_dictionary.iteritems():
        vtk_file.write('%.3f  %.3f  %.3f\n' % (coords[0][0] , coords[0][1] , coords[0][2]))

    total_elements = len(element_dictionary.keys())
    vtk_file.write('\nCELLS %d %d \n' %(total_elements, total_elements * 5))

    for el_no, nodes in element_dictionary.iteritems():
        vtk_file.write('4 %d %d %d %d\n' % (
        nodes[0][3] - 1, nodes[0][1] - 1, nodes[0][2] - 1, nodes[0][0] - 1))
    # Write out the fibres as points or lines connected to the centroid.

    vtk_file.write('\nCELL_TYPES %d\n' % (total_elements))
    for el_no in element_dictionary.keys():
        vtk_file.write('10\n')

    # Print in volume fractions
    if vf_dictionary is not None:
        vtk_file.write('CELL_DATA %d\n' %(total_elements))
        vtk_file.write('SCALARS k2_value float 1\n')
        vtk_file.write('LOOKUP_TABLE default\n')
        for el_no, vf in vf_dictionary.iteritems():
            # print el_no, ': ', mat_props
            vtk_file.write('%f \n' %(vf))
    else:
        pass


    vtk_file.close()


def vtk_unstructured_file_writer(filename, vtk_information, node_dictionary, element_dictionary, values_dicitonary):
    """
    Write a .vtk file using the provided nodes, elements and values associated with the particular element
    as inputs

    Args:
        filename(str)          : .inp file containing information for a neo-hookean material
        nodes_dict(defaultdict): dictionary containing the node information for the mesh geometry
        element_dictionary(defaultdict): dictionary containing the elements for the mesh geometry
        values_dicitonary(defaultdict) : dictionary containing the values associated with elements to be printed

    """

    total_number = len(node_dictionary.keys())
    vtk_file = open(filename, "w+")

    vtk_file.write('# vtk DataFile Version 4.2 \n')
    vtk_file.write('Centroids \n')
    vtk_file.write('ASCII \n')
    # vtk_file.write('DATASET POLYDATA\n')
    vtk_file.write('DATASET UNSTRUCTURED_GRID\n\n')
    vtk_file.write('POINTS %d float \n' % (total_number))

    # The centroids are being writter here :)
    for node_number, coords in node_dictionary.iteritems():
        vtk_file.write('%.3f  %.3f  %.3f\n' % (coords[0][0] , coords[0][1] , coords[0][2]))

    total_elements = len(element_dictionary.keys())
    vtk_file.write('\nCELLS %d %d \n' %(total_elements, total_elements * 9))

    for el_no, nodes in element_dictionary.iteritems():
        vtk_file.write('8 %d %d %d %d %d %d %d %d\n' % (
        nodes[0][1] - 1, nodes[0][2] - 1, nodes[0][3] - 1, nodes[0][0] - 1, nodes[0][5] - 1, nodes[0][6] - 1, nodes[0][7] - 1, nodes[0][4] - 1))
    # Write out the fibres as points or lines connected to the centroid.

    vtk_file.write('\nCELL_TYPES %d\n' % (total_elements))
    for el_no in element_dictionary.keys():
        vtk_file.write('12\n')

    # Let values dictionary be a dictionary of dictionaries :)
    # c, k1, k2, stress_c, stress_princi_1 etc...


    # Loop it down depending on whatever is available as scalar values :)
    # CELL_DATA only occurs once

    # vtk_file.write('CELL_DATA %d\n' %(total_elements))
    # if values_dicitonary is not None:
    #     vtk_file.write('SCALARS %s float 1\n' %(vtk_information[0]))
    #     vtk_file.write('LOOKUP_TABLE default\n')
    #     for el_no, value in values_dicitonary.iteritems():
    #         # print el_no, ': ', mat_props
    #         vtk_file.write('%f \n' %(value))
    # else:
    #     pass


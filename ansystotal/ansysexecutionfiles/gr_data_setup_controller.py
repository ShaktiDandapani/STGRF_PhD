# -*- coding: utf-8 -*-
"""
Created on 24.08.2016
Edited  on 17.12.2018

@Shaktidhar Dandapani - The University of Sheffield 2016
modified from the aneurysm library used in my masters thesis.
The current file writes an ANSYS .inp file for an exponential hyperelastic material.

Do note camelcase has been adopted. The legacy code contains lowercase underscored python naming.
Code is being updated to adopt the lowercase_underscored_naming_convention
Code is updated to the underscore_case convention. 

"""
import os

from collections import defaultdict

import ansystotal.ansyspreprocessing.ansys_file_reader as afr
import ansystotal.ansyspreprocessing.ansys_file_writer as afw
import ansystotal.genericoperations.centroid_fibre_gen as fg

# ------------------------------------------------- #
#                                                                                                                      #                                                                                                                      #
#                                          ANSYS .inp File Generator Script                                            #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #                                                                                                                      #


# noinspection PyPep8Naming
def write_inp_file(ansys_file_name=str,
                   data_directory=str,
                   fibre_dictionary=defaultdict(),
                   parameters=defaultdict(),
                   flag=str,):

    """
    The mesh information is formulated in this method/ function to be used in writing out various ANSYS apdl
    scripts for different simulations.
    """

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                                                                                                  #
    #                         Read nodes, element, areas, volumes, lines, keypoints                                    #
    #                                                                                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    mesh_data            = defaultdict()

    # Associating data to different files from the data directory
    nodes_file              = data_directory + "nlist.dat"
    elements_file           = data_directory + "elist.dat"
    materials_file          = data_directory + "materials.dat"

    # Read in the mesh information to be passed onto the writer function file :)
    v_file_reader           = afr.ListReader()
    nodes_dictionary        = v_file_reader.read_nodes(nodes_file)
    element_dictionary      = v_file_reader.read_elements(elements_file)

    # Basic data
    # Creation of fibres with centroids :D
    centroids_dictionary    = fg.calculate_centroids(nodes_dictionary, element_dictionary)

    # Structuring loose data into a neat dictionary
    mesh_data['nodes']              = nodes_dictionary
    mesh_data['elements']           = element_dictionary
    mesh_data['centroids']          = centroids_dictionary
    # All of this mesh_data can be encapsulated in the Mesh class

    # Instead of mesh_data -> create a mesh class itself
    if flag == "myocardium":
        # Check if file exists, else either create a mat file manually
        # or create a file with values to be read in
        if os.path.isfile(materials_file):
            materials_dictionary = afr.read_hgo_material(materials_file)
            mesh_data['materials'] = materials_dictionary
        # To be executed if the flag is for a simulation involving myocardial tissue
        inner_surface_file      = data_directory + "inner_surface.dat"
        fixed_supp_file         = data_directory + "fixed_support.dat"
        infarct_zone_file       = data_directory + "degradation_elements.dat"
        inner_base_nodes_file   = data_directory + "base_inner.dat"

        mesh_data['inner_surface']       = inner_surface_file
        mesh_data['fixed_support']       = fixed_supp_file
        mesh_data['infarct_zone']        = infarct_zone_file
        mesh_data['base_inner']          = inner_base_nodes_file

        o_writeFile = afw.AnsysInpWriter(ansys_file_name, mesh_data)
        o_writeFile.inp_writer_lv_hgo_model(parameters)

    elif flag == "cube":

        # read material files from the csv for muscle format :)
        if os.path.isfile(materials_file):
            materials_dictionary = afr.read_hgo_material_musc(materials_file)
            mesh_data['materials'] = materials_dictionary

        o_write_file = afw.AnsysInpWriter(ansys_file_name, mesh_data)
        o_write_file.write_cube_simulation(parameters)


    # ------------------------------------------------------------------------ #


    # o_writeFile.write_cube_sample_sim(mat_constants, fibre_dictionary)

    # return nodes_dictionary, element_dictionary, fibre_dictionary


# -*- coding: utf-8 -*-
"""
Created on 08.08.2016

Class file containing methods to write ANSYS APDL .inp scripts for execution.

Current implementation includes the HGO model and the neohookean model, considerations include
1. Defining a method to obtain boundary conditions -> defining nodal displacements.
2. Cleaner implementation to save in directory of choice.

"""

from collections import defaultdict

import ansystotal.ansyspreprocessing.ansys_component_writer as mw
import ansystotal.ansyspreprocessing.ansys_file_reader as afr
import ansystotal.genericoperations.calculate_displacement_function as cdf

# noinspection PyPep8Naming
class AnsysInpWriter:
    """
    ANSYS apdl script generator based on the material required. \n
    Current Implementation includes the neo-hookean material and \n
    the exponential form HGO material formulation.

    """

    def __init__(self,
                filename=None,
                mesh_data=None):

        self.filename       = filename
        self.mesh_data      = mesh_data
        # The dictionaries are provided below using simple names
        if mesh_data != None:
            self.nodes          = mesh_data['nodes']
            self.elements       = mesh_data['elements']


    def write_cube_simulation(self, parameters):

        job_fname = self.filename

        prep_fname            = 'prep.inp'
        boundary_cond_fname   = 'bcs.inp'
        nodes_fname           = 'nodes.inp'
        elements_fname        = 'elements.inp'
        materials_fname       = 'materials.inp'
        solution_fname        = 'solution.inp'
        post_processing_fname = 'post.inp'

        # Create remaining files
        self.create_prep_file_cube(prep_fname)

        mat_values_file = 'material_values_0.csv'

        mat_writer = mw.DataWriter()

        mat_writer.write_nodes(nodes_fname,
                               self.nodes)

        mat_writer.write_elements(elements_fname,
                                  self.elements)


        materials_dictionary = self.mesh_data['materials']
        # Here modify for skeletal muscle.
        mat_writer.write_material_ahyper_expo_original(materials_fname,
                                                 mat_values_file,
                                                 materials_dictionary)

        # Create Boundary Conditions
        self.create_bcs_cube_incomp_extension(boundary_cond_fname)

        disp_calculator = cdf.DisplacementCalculator(parameters=parameters)
        displacement = disp_calculator.calculate_displacement(str(parameters['step_function']))
        self.create_solu_inp_file_tissue_cube(solution_fname, displacement)
        post_directory = './libraries/ansysapdlscripts'
        # post_directory = 'ansysapdlscripts'
        write_post_processes(post_processing_fname, post_directory)

        # Create the ANSYS job file
        with open(job_fname, 'w') as jfile:
            # Change these to dynamically take in the variable names
            jfile.write('\n/INPUT,prep,inp')
            jfile.write('\nALLSEL')
            jfile.write('\n/INPUT,nodes,inp')
            jfile.write('\nALLSEL')
            jfile.write('\n/INPUT,elements,inp')
            jfile.write('\nALLSEL')
            jfile.write('\n/INPUT,materials,inp')
            jfile.write('\nALLSEL')
            jfile.write('\n/INPUT,bcs,inp')
            jfile.write('\nALLSEL')
            jfile.write('\n/INPUT,solution,inp')
            jfile.write('\nALLSEL')
            jfile.write('\n/INPUT,post,inp')
            jfile.write('\nALLSEL')


    @staticmethod
    def create_prep_file_cube(filename):
        # Template for everything ?
        with open(filename, 'w') as prep_file:
            prep_file.write('\n/PREP7')
            prep_file.write('\n/UNITS,MPA')
            prep_file.write('\nET,1,SOLID185')
            prep_file.write("\nET,2,SOLID186")  # 20 node solid element

    @staticmethod
    def create_solu_inp_file_tissue_cube(filename, displacement):

        # Calculate displacements using parameters dictionary and proceed
        # Read in the file for displacement !
        with open(filename, 'w') as solu_file:
            solu_file.write('\n/SOLU')
            solu_file.write('\nNLGEOM,ON')
            solu_file.write('\nNSEL,S,LOC,X,6')  # needs to be dynamic
            solu_file.write('\nD,ALL,UX,{}'.format(displacement))    # needs to be dynamically read in
            solu_file.write('\nALLSEL')
            # solu_file.write('\nNSEL,S,LOC,Z,4')  # needs to be dynamic
            # solu_file.write('\nD,ALL,UZ,{}'.format(displacement))    # needs to be dynamically read in
            solu_file.write('\nALLSEL')
            solu_file.write("\nNSUBST, 10, 100, 10, ON")
            solu_file.write('\nSOLVE')
            solu_file.write('\nFINISH')

    @staticmethod
    def create_solution_file(filename, displacement):

        # Calculate displacements using parameters dictionary and proceed
        # Read in the file for displacement !
        with open(filename, 'w') as solu_file:
            solu_file.write('\n/SOLU')
            solu_file.write('\nNLGEOM,ON')
            solu_file.write('\nNSEL,S,LOC,X,10')  # needs to be dynamic
            solu_file.write('\nD,ALL,UX,{}'.format(displacement))    # needs to be dynamically read in
            solu_file.write('\nALLSEL')
            # solu_file.write('\nNSEL,S,LOC,Z,4')  # needs to be dynamic
            # solu_file.write('\nD,ALL,UZ,{}'.format(displacement))    # needs to be dynamically read in
            solu_file.write('\nALLSEL')
            solu_file.write("\nNSUBST, 10, 100, 10, ON")
            solu_file.write('\nSOLVE')
            solu_file.write('\nFINISH')

    @staticmethod
    def create_bcs_cube_incomp_extension(filename):

        with open(filename, 'w') as bc_file:
            bc_file.write('\nNSEL,S,LOC,Y,0')
            bc_file.write('\nD,ALL,UY,0')
            bc_file.write('\nALLSEL')

            bc_file.write('\nNSEL,S,LOC,X,0')
            bc_file.write('\nD,ALL,ALL,0')
            bc_file.write('\nALLSEL')

            bc_file.write('\nNSEL,S,LOC,Z,0')
            bc_file.write('\nD,ALL,UZ,0')
            bc_file.write('\nALLSEL')
    """
    Writes the ANSYS input file for the HGO model.. think about how to define the materials for
    the various elements - fairly simple.

    """
    def inp_writer_lv_hgo_model(self, parameters):
        """
        This function/ method uses the other modules/ library to create a ansys simulation
        script for a hgo material.

        :param mat_constants:
        :param fibres:
        :return:
        """

        fs_file         = self.mesh_data['fixed_support']
        base_inner_file = self.mesh_data['base_inner']
        pface_file      = self.mesh_data['inner_surface']
        # -------------------------------------------------------------------------------------------------------------#
        #                                                                                                              #
        #                                        Writing of the ANSYS inp File                                         #
        #                                                                                                              #
        # ------------------------------------------------------------------------------------------------------------ #

        input_file = open(self.filename, "w+")

        input_file.write("\n/PREP7 \n")
        input_file.write("\n/UNITS,MPA \n")           # Set the units to MPa

        # While we do define multiple element types, it is necessary to note
        # that only one element type is used throughout the geometry
        # depending on what original elemenst have been established.
        input_file.write("\nET,1,SOLID185")             # 8 node solid element
        input_file.write("\nET,2,SOLID186")  # 8 node solid element
        input_file.write("\nKEYOPT,1,6,1 !Use mixed u-P formulation to avoid locking")
        input_file.write("KEYOPT,1,2,3 !Use Simplified Enhanced Strain method")

        # input_file.write("\nKEYOPT,2,3,0")
        # input_file.write("\nKEYOPT,2,6,1")

        e_file  = "elements"
        n_file  = "nodes"
        m_file  = "materials"

        e_file_inp      = e_file + ".inp"
        n_file_inp      = n_file + ".inp"
        m_file_inp      = m_file + ".inp"

        # -------------------------------------------------------------------------------------------------------------#
        #                                                                                                              #
        #                              Create Node, Elements, Materials Input Files                                    #
        #                                                                                                              #
        # ------------------------------------------------------------------------------------------------------------ #


        mat_writer = mw.DataWriter()

        mat_writer.write_nodes(n_file_inp,
                               self.nodes)

        mat_writer.write_elements(e_file_inp,
                                  self.elements)


        mat_values_file = 'material_values_0.csv'

        materials_dictionary = self.mesh_data['materials']
        # read hgo from csv and include that in the
        mat_writer.write_material_ahyper_expo_lv(m_file_inp,
                                                 mat_values_file,
                                                 materials_dictionary)

        input_file.write("\n\n/INPUT,{},inp".format(m_file))
        input_file.write("\nALLSEL\n")
        input_file.write("\n/INPUT,{},inp".format(n_file))
        input_file.write("\nALLSEL\n")
        input_file.write("\n/INPUT,{},inp".format(e_file))
        input_file.write("\nALLSEL\n")

        # Fixed Support
        comp_fs_name        = "fixedsupp"
        comp_fs_file        = comp_fs_name + ".inp"
        comp_fs_nodes_file  = fs_file

        comp_base_inner_name       = "baseinner"
        comp_base_inner_file       = comp_base_inner_name + ".inp"
        comp_base_inner_nodes_file = base_inner_file

        create_nodal_comp(comp_fs_file,
                          comp_fs_nodes_file,
                          comp_fs_name)

        create_nodal_comp(comp_base_inner_file,
                          comp_base_inner_nodes_file,
                          comp_base_inner_name)

        # Set up pressure nodes
        comp_pres_name          = "pface"
        comp_pres_file          = comp_pres_name + ".inp"
        comp_pres_nodes_file    = pface_file

        create_nodal_comp(comp_pres_file,
                          comp_pres_nodes_file,
                          comp_pres_name)

        # get in the fixed support and pressure file
        input_file.write("\n!Fixed Support Specification")
        input_file.write("\n/INPUT, %s, inp" % (comp_fs_name))
        input_file.write("\nD, %s, ALL, 0" % (comp_fs_name))

        # Inner base nodes rolling support file
        input_file.write("\n\n!Inner Base Nodes Specification")
        input_file.write("\n/INPUT, %s, inp" %(comp_base_inner_name))
        input_file.write("\nD, %s, UY, 0" % (comp_base_inner_name)) # for rolling support
        # input_file.write("\nD, %s, ALL, 0" % (comp_base_inner_name))   # for fixed support

        input_file.write("\n\n!Application of pressure to inner_surfaces")
        input_file.write("\n/INPUT, %s, inp" % (comp_pres_name))

        sol_f_name  = "solu"
        sol_file   = sol_f_name + ".inp"
        write_solution_file(sol_file, 1.33666e-3, comp_pres_name)
        input_file.write("\n\n!Solutions File")
        input_file.write("\n/INPUT, %s, inp" % (sol_f_name))

        # Directory in which post processing scripts are stored.
        post_directory = './libraries/ansysapdlscripts'

        input_file.write("\n\n!Post Processing ")
        write_post_processes('post_p.inp', post_directory)

        input_file.write("\n/INPUT, post_p, inp")
        input_file.close()

# Methods outside the writer class.
def write_solution_file(file_name, pressure, region):
    """
    Writes out the solution section of the ansys apdl script.

    :param file_name:
    :param pressure:
    :param region:
    :return:
    """

    with open(file_name, 'w+') as sol_file:
        # Solution - put it in a different file
        sol_file.write("\n/SOLU")
        sol_file.write("\nANTYPE, STATIC")
        sol_file.write("\nNLGEOM, ON")
        # sol_file.write("\nARCLEN, ON")              # Using the arc length method for newton-rahpson analysis
        # sol_file.write("\nNROPT, FULL, , OFF")    # This command instructs ANSYS to use the 'Full' Newton Raphson algorithm
                                                    # and prevents it from using the 'Adaptive Descent' algorithm.
        # sol_file.write("\nCNCHECK, AUTO")
        # sol_file.write("\nSOLCONTROL, ON")
        sol_file.write("\nPRED,ON,,ON")             # This makes ANSYS from use the converged solution at the
                                                    # last substep to estimate the solution for the current substep.
        # sol_file.write("\nCNVTOL,F,,,,-1")
        # sol_file.write("\nBCSOPTION, ,INCORE")
        # sol_file.write("\nNROPT,MODI\n")

        # sol_file.write("\nNSUBST, 10, 100, 10, ON")

        sol_file.write("\n!Apply pressure to all nodes")
        sol_file.write("\nSF, %s, PRES, %f" % (region, pressure))

        sol_file.write("\nALLSEL")
        sol_file.write("\nSOLVE")
        sol_file.write("\nFINISH")
        sol_file.write("\n")



def write_post_processes(file_name, directory):
    """
    Writes the post processing commands for apdl script.

    :param file_name:
    :param directory:
    :return:
    """

    post_file = open(file_name, 'w')

    post_file.write("\n\n!Post Processing Commands below:")
    post_file.write("\n!===============================!\n")
    post_file.write("\n/POST1\n")
    post_file.write("\n/INPUT, get_disp_nodes,inp,{}".format(directory))
    # post_file.write("\nRSYS,2") # change to spherical co-ordinate system ????
    post_file.write("\n/INPUT, get_stresses,inp,{}".format(directory))
    post_file.write("\n/INPUT, get_strains_comp,inp,{}".format(directory))

    # input_file.write("\n/OUT")
    post_file.write("\n\nFINISH")

    post_file.close()

def create_nodal_comp(filename,
                      nodes_file,
                      component_name):
    """
    A component is created, specifically a named selection in terms of ANSYS wb.


    :param filename:
    :param nodes_file:
    :param component_name:
    :return:
    """
    # Opens file to write in components from filename
    comp_file = open(filename, "w")

    reader = afr.ListReader()

    # Reads nodes from nodes_file
    nodes  = reader.read_nodes(nodes_file)
    nodes_list = list(nodes.keys())


    for i in range(0, len(nodes_list)):
        if i == 0:
            comp_file.write("\nNSEL,S,NODE,,%d" %nodes_list[i])
        else:
            comp_file.write("\nNSEL,A,NODE,,%d" % nodes_list[i])

    comp_file.write("\nCM, %s, NODE" %(component_name))
    comp_file.write("\nALLSEL")

    comp_file.close()

def create_elem_comp(filename,
                      nodes_file,
                      component_name):
    """
    A component is created, specifically a named selection in terms of ANSYS wb.


    :param filename:
    :param nodes_file:
    :param component_name:
    :return:
    """
    # Opens file to write in components from filename
    comp_file = open(filename, "w")

    reader = afr.ListReader()

    # Reads nodes from nodes_file
    elems  = reader.read_elements(nodes_file)
    elems_list = list(elems.keys())


    for i in range(0, len(elems_list)):
        if i == 0:
            comp_file.write("\nESEL,S,NODE,,%d" %elems_list[i])
        else:
            comp_file.write("\nESEL,A,NODE,,%d" % elems_list[i])

    comp_file.write("\nCM, %s, ELEM" %(component_name))
    comp_file.write("\nALLSEL")

    comp_file.close()


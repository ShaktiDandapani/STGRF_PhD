"""

Important thing left to be done:
Keep code commented for the old remodelling method.

This will help in comparing the results obtained by the
stress based remodelling approach and the 2004 based
anisotropic cauchy stress + fibroblast recruitment
field results ! .

One final thing to be implemented, is to uncomment the
code for the remodelling of the I_6 family of collagen
fibres :)

"""

# Major rework needed, error checking etc.
import math
import sys
from collections import defaultdict

from ansystotal.ansyspreprocessing import ansys_component_writer as acr
from ansystotal.ansyspreprocessing import ansys_file_reader as afr
from ansystotal.genericoperations import generic_commands as gc, gr_commands as grc
from ansystotal.ansyspostprocessing import vtk_file_writer as vfw, tensor_operations as to
import ansystotal.genericoperations.mesh_information_structures as mis

def remodelling_routine(
        strain_curr_step_file,
        strain_homeostatic_step_file,
        stress_previous_step_file,
        stress_homeostatic_step_file,
        material_curr_step_file,
        material_homeostatic_step_file,
        material_values_new_step_fname,
        material_inp_fname,
        fibroblast_info_homeo_fname,
        fibroblast_info_curr_fname,
        fibroblast_info_new_fname,
        parameters_file):

    # Read in the root directory from the directories_information.dat file
    data_directory = gc.return_read_root_directory_name('./parameters/directories_information.dat')

    # Read in the file to track the time step and other important
    # parameters
    parameter_dict   = grc.read_params_file(parameters_file)
    c_alpha_t   = float(parameter_dict['alpha'])
    c_beta_t    = float(parameter_dict['beta'])
    c_gamma_t   = float(parameter_dict['gamma'])

    # Update time file !
    # Time variables
    c_time_period       = int(parameter_dict['time_period'])
    c_no_of_iters       = int(parameter_dict['number_of_iterations'])
    c_curr_iteration    = int(parameter_dict['iteration'])
    c_delta_t           = float(c_time_period / c_no_of_iters)
    c_no_of_iters_per_t = float(c_no_of_iters / c_time_period)

    # Reader variable - Instantiate the ListReader() class
    infarct_reader_object = afr.ListReader()
    # Infarction Zone

    infarct_file = data_directory['myocardium'] + "degradation_elements.dat" # LV
    infarct_zone = infarct_reader_object.read_elements(infarct_file)

    # Read in the strain files
    hencky_strains_previous    = afr.read_strain_output(strain_curr_step_file)
    hencky_strains_homeostatic = afr.read_strain_output(strain_homeostatic_step_file)

    i4_dict_curr, i6_dict_curr = to.create_invariant_dictionaries(material_curr_step_file, hencky_strains_previous)
    i4_dict_home, i6_dict_home = to.create_invariant_dictionaries(material_homeostatic_step_file, hencky_strains_homeostatic)

    # Read in the material csv files
    material_values_previous_dict = afr.read_hgo_material(material_curr_step_file)
    material_values_homeosta_dict = afr.read_hgo_material(material_homeostatic_step_file)

    new_materials_dict            = material_values_previous_dict

    # Read in the fibroblast stretch file here and utilise that in the growth and remodelling situation
    fibroblast_info_dict_homeo     = afr.read_fibroblast_stretch_file(fibroblast_info_homeo_fname)
    fibroblast_info_dict_curr      = afr.read_fibroblast_stretch_file(fibroblast_info_curr_fname)

    fibroblast_info_dict_updated   = defaultdict(list)

    sigma_aniso_i4_h         = defaultdict()
    sigma_aniso_i4_curr      = defaultdict()
    sigma_aniso_i4_difference  = defaultdict()

    sigma_aniso_i6_h         = defaultdict()
    sigma_aniso_i6_curr      = defaultdict()
    sigma_aniso_i6_difference  = defaultdict()

    fibroblast_stretch_i4 = defaultdict()
    fibroblast_stretch_i6 = defaultdict()

    results_dictionary = defaultdict()
    results_dictionary['sigma_aniso_i4_h']          = sigma_aniso_i4_h
    results_dictionary['sigma_aniso_i4_curr']       = sigma_aniso_i4_curr
    results_dictionary['sigma_aniso_i4_difference'] = sigma_aniso_i4_difference

    results_dictionary['sigma_aniso_i6_h']          = sigma_aniso_i6_h
    results_dictionary['sigma_aniso_i6_curr']       = sigma_aniso_i6_curr
    results_dictionary['sigma_aniso_i6_difference'] = sigma_aniso_i6_difference

    results_dictionary['i4'] = i4_dict_curr
    results_dictionary['i6'] = i6_dict_curr

    results_dictionary['stretch_fibroblast_i4'] = fibroblast_stretch_i4
    results_dictionary['stretch_fibroblast_i6'] = fibroblast_stretch_i6

    # Extra constants
    d_time      = 7 * (c_no_of_iters / c_time_period)
    d_time_coll = 4 * (c_no_of_iters / c_time_period)

    for e_no, values in material_values_previous_dict.items():
        c1_homeo = material_values_homeosta_dict[e_no][0][0]

        # Read in the values
        c1    = float(values[0][0])
        k1    = float(values[0][1])
        k2    = float(values[0][2])
        k3    = float(values[0][3])
        k4    = float(values[0][4])

        avec    = values[1]
        bvec    = values[2]
        vol     = values[3]
        m_gm    = values[4][0]
        v_m_c_i4   = values[4][1]
        v_m_c_i6 = values[4][2]

        # Degrade
        if e_no in infarct_zone.keys():

            # if c_curr_iteration <= d_time or c1 >= 0.1:
            # This is obviously the problem you idiot !
            if c_curr_iteration <= d_time:
                m_gm         = 0.1 **(c_curr_iteration/d_time)
                c1_updated   = c1_homeo * m_gm

                if c1 <= 0.01 * c1_homeo:
                    c1_updated = 0.01 * c1_homeo
            else:
                c1_updated = 0.01 * c1_homeo
            #
            # if c_curr_iteration < d_time_coll:
            #     v_m_c = 0.2**(c_curr_iteration/d_time_coll)

            new_materials_dict[e_no] = [
                [c1_updated, k1, k2, k3, k4],
                avec,
                bvec,
                vol,
                [m_gm, v_m_c_i4, v_m_c_i6]
            ]

    # Remodel
    for k in material_values_previous_dict.keys():

        # Check the logic
        if k not in infarct_zone.keys():
            # You need to keep them in separate variables
            c_beta_t_curr = 0.0 * c_beta_t
            c_alpha_t_curr = 0.0 *c_alpha_t
            c_gamma_t_curr = 0.0 * c_gamma_t
        else:
            c_beta_t_curr = c_beta_t
            c_alpha_t_curr = c_alpha_t
            c_gamma_t_curr = c_gamma_t

        v_m_gm  = material_values_previous_dict[k][4][0]
        # v_m_c   = material_values_previous_dict[k][4][1]

        # For invariant 4
        aniso_pk_homeo_stress, an_cauchy_homeo_i4 = to.calculate_aniso_stresses(material_values_homeosta_dict[k][0][1],
                                                                                material_values_homeosta_dict[k][0][2],
                                                                                i4_dict_home[k])

        aniso_pk_stress, an_cauchys_i4 = to.calculate_aniso_stresses(material_values_previous_dict[k][0][1],
                                                                    material_values_previous_dict[k][0][2],
                                                                    i4_dict_curr[k])

        # For invariant_6
        an_pks_homeo_i6, an_cauchy_homeo_i6 = to.calculate_aniso_stresses(material_values_homeosta_dict[k][0][3],
                                                      material_values_homeosta_dict[k][0][4],
                                                      i6_dict_home[k])

        an_pks_i6, an_cauchys_i6 = to.calculate_aniso_stresses(material_values_previous_dict[k][0][3],
                                                               material_values_previous_dict[k][0][4],
                                                               i6_dict_curr[k])

        k1_homeo   = material_values_homeosta_dict[k][0][1]
        k2_homeo   = material_values_homeosta_dict[k][0][2]
        k3_homeo   = material_values_homeosta_dict[k][0][3]
        k4_homeo   = material_values_homeosta_dict[k][0][4]
        #

        # c _prev    = material_values_previous_dict[k][0][0]
        k1_curr    = material_values_previous_dict[k][0][1]
        k2_curr    = material_values_previous_dict[k][0][2]
        k3_curr    = material_values_previous_dict[k][0][3]
        k4_curr    = material_values_previous_dict[k][0][4]
        # m_gm_prev  = material_values_previous_dict[k][4][0]
        m_c_prev   = material_values_previous_dict[k][4][1]


        # ------------------------------- Fibroblast update ------------------------------------------------------ #

        # fibr_stretch_dict[element_number] = [fibro_rec_stretch_i4, fibro_rec_stretch_i6,
        #                                      fibroblast_rec_stretch_i4, fibroblast_rec_stretch_i6,
        #                                      tissue_stretch_i4, tissue_stretch_i6]

        fibro_stretch_homeo_i4 = fibroblast_info_dict_homeo[k][0]
        fibro_stretch_homeo_i6 = fibroblast_info_dict_homeo[k][1]

        fibro_stretch_rec_i4 = fibroblast_info_dict_curr[k][2]
        fibro_stretch_rec_i6 = fibroblast_info_dict_curr[k][3]

        tissue_stretch_i4 = math.sqrt(i4_dict_curr[k])
        tissue_stretch_i6 = math.sqrt(i6_dict_curr[k])

        # fibro_rec_curr      = fibroblast_info_dict_curr[k][1]
        fibro_stretch_curr_i4  = tissue_stretch_i4 / fibro_stretch_rec_i4
        fibro_stretch_curr_i6  = tissue_stretch_i6 / fibro_stretch_rec_i6


        fibro_rec_new_i4 = fibro_stretch_rec_i4 + c_gamma_t_curr *  c_delta_t * fibro_stretch_rec_i4 *\
                        ((fibro_stretch_curr_i4 - fibro_stretch_homeo_i4) / fibro_stretch_homeo_i4)

        fibro_rec_new_i6 = fibro_stretch_rec_i6 + c_gamma_t_curr *  c_delta_t * fibro_stretch_rec_i6 *\
                        ((fibro_stretch_curr_i6 - fibro_stretch_homeo_i6) / fibro_stretch_homeo_i6)



        fibroblast_info_dict_updated[k] = [fibro_stretch_curr_i4, fibro_stretch_curr_i6,
                                           fibro_rec_new_i4, fibro_rec_new_i6,
                                           tissue_stretch_i4, tissue_stretch_i6]

        # Update the values in the new materials dictionary to be fed ito the next simulation
        # if k in infarct_zone.keys():
        m_c_new_i4    = m_c_prev + c_beta_t_curr  *  m_c_prev * c_delta_t * \
                         ((fibro_stretch_curr_i4 - fibro_stretch_homeo_i4) / fibro_stretch_homeo_i4)

        m_c_new_i6    = m_c_prev + c_beta_t_curr  *  m_c_prev * c_delta_t * \
                         ((fibro_stretch_curr_i6 - fibro_stretch_homeo_i6) / fibro_stretch_homeo_i6)

        # ------------------------------- Fibroblast update end -------------------------------------------------- #

        if an_cauchys_i4 > 0 and an_cauchy_homeo_i4 > 0:
            k2_new = k2_curr - c_alpha_t_curr *  k2_curr * c_delta_t  * \
                           (((float(an_cauchys_i4) - float(an_cauchy_homeo_i4))
                             / float(an_cauchy_homeo_i4)))
        else:
            k2_new = k2_curr

        if an_cauchys_i6 > 0 and an_cauchy_homeo_i6 > 0:
            k4_new = k4_curr - c_alpha_t_curr *  k4_curr * c_delta_t  * \
                     (((float(an_cauchys_i6) - float(an_cauchy_homeo_i6))
                             / float(an_cauchy_homeo_i6)))
        else:
            k4_new = k4_curr

        if k2_new < 0:
            k2_new = k2_curr

        if k4_new < 0:
            k4_new = k4_curr

        k1_new = k1_homeo * m_c_new_i4 * (k2_new / k2_homeo)
        k3_new = k3_homeo * m_c_new_i6 * (k4_new / k4_homeo)

        if k1_new < 0:
            k1_new = k1_curr

        if k3_new < 0:
            k3_new = k3_curr

        new_materials_dict[k][0][1] = k1_new
        new_materials_dict[k][0][2] = k2_new
        new_materials_dict[k][0][3] = k3_new
        new_materials_dict[k][0][4] = k4_new
        # Mass density updates
        new_materials_dict[k][4][0] = v_m_gm
        new_materials_dict[k][4][1] = m_c_new_i4
        new_materials_dict[k][4][2] = m_c_new_i6

        # Store values
        sigma_aniso_i4_curr[k]       = an_cauchys_i4
        sigma_aniso_i4_h[k]          = an_cauchy_homeo_i4
        sigma_aniso_i4_difference[k] = an_cauchys_i4 - an_cauchy_homeo_i4
        #
        sigma_aniso_i6_curr[k]       = an_cauchys_i6
        sigma_aniso_i6_h[k]          = an_cauchy_homeo_i6
        sigma_aniso_i6_difference[k] = an_cauchys_i6 - an_cauchy_homeo_i6

        fibroblast_stretch_i4[k] = fibro_stretch_curr_i4
        fibroblast_stretch_i6[k] = fibro_stretch_curr_i6


    # Write in the new materials
    mat_writer = acr.DataWriter()

    mat_writer.write_material_ahyper_expo_lv(material_inp_fname, material_values_new_step_fname, new_materials_dict)

    grc.write_params_file(parameters_file,
                          c_time_period,
                          c_no_of_iters,
                          c_curr_iteration + 1,
                          c_alpha_t,
                          c_beta_t,
                          c_gamma_t)

    # Write out the fibroblast recruitment field file
    grc.write_fibrobast_file(fibroblast_info_new_fname, fibroblast_info_dict_updated)
    write_vtk_file(new_materials_dict, results_dictionary, c_curr_iteration)
    write_result_sheet_files(results_dictionary, c_curr_iteration)

def write_result_sheet_files(results_dictionary, c_curr_iteration):
    # Write it out
    for keys, values in results_dictionary.items():

        # keys -> name of the file
        # values -> {e_no: quantity_pair}
        new_fname = './results/' + str(keys) + '_step_rem_' + str(c_curr_iteration) + '.csv'
        with open(new_fname, 'w') as wfile:
            for e_no, quantity in values.items():
                wfile.write("{}, {}\n".format(int(e_no), float(quantity)))


def write_vtk_file(materials_dictionary, results_dictionary, curr_step):

    vtk_file = 'results_vtk_' + str(curr_step) + '.vtk'
    vtk_file_materials = 'materials_vtk_' + str(curr_step) + '.vtk'

    # Mesh data to pass onto the vtk file writer function
    root_dir = gc.return_read_root_directory_name('./parameters/directories_information.dat')
    # Gives us the directory
    data_directory = root_dir['myocardium']

    nodes_fname = data_directory + "nlist.dat"
    elems_fname = data_directory + "elist.dat"
    disp_nodes_fname = "./disp_nodes.txt"

    disp_nodes_reader = afr.ListReader()
    disp_nodes = disp_nodes_reader.read_nodes(disp_nodes_fname)

    # Read in the mesh data using STGRF functions
    mesh_reader = afr.ListReader()

    nodes = mesh_reader.read_nodes(nodes_fname)
    elems = mesh_reader.read_elements(elems_fname)

    new_nodes = defaultdict()

    for node, coords in disp_nodes.items():
        x_coord = coords[0].get_x() + nodes[node][0].get_x()
        y_coord = coords[0].get_y() + nodes[node][0].get_y()
        z_coord = coords[0].get_z() + nodes[node][0].get_z()
        new_nodes[node] = [mis.Point(x_coord, y_coord, z_coord, str(int(node)))]

    mesh_data = defaultdict()

    mesh_data['nodes'] = new_nodes
    mesh_data['elements'] = elems

    # Write VTK file
    vtk_writer = vfw.VTKFileWriter(mesh_data)
    # same for I4, I6
    vtk_writer.create_results_vtk_hexahedral(vtk_file, results_dictionary)
    vtk_writer.create_material_value_tables_myocardium_hexahedral(vtk_file_materials, materials_dictionary)

    # vtk_writer for stresses (change in the core file :) )

def exec_remodelling():

    strain_previous_step_file       = sys.argv[1]
    strain_homeostatic_step_file    = sys.argv[2]
    stress_previous_step_file       = sys.argv[3]
    stress_homeostatic_step_file    = sys.argv[4]
    material_previous_step_file     = sys.argv[5]
    material_homeostatic_step_file  = sys.argv[6]
    material_values_new_step_fname  = sys.argv[7]
    material_inp_fname              = sys.argv[8]
    fibroblast_info_homeo_fname     = sys.argv[9]
    fibroblast_info__curr_fname     = sys.argv[10]
    fibroblast_info_new_fname       = sys.argv[11]
    parameters_file                 = sys.argv[12]

    remodelling_routine(
        strain_previous_step_file,
        strain_homeostatic_step_file,
        stress_previous_step_file,
        stress_homeostatic_step_file,
        material_previous_step_file,
        material_homeostatic_step_file,
        material_values_new_step_fname,
        material_inp_fname,
        fibroblast_info_homeo_fname,
        fibroblast_info__curr_fname,
        fibroblast_info_new_fname,
        parameters_file)

if __name__ == '__main__':
    exec_remodelling()

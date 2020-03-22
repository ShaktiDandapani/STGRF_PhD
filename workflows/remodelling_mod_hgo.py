import math
import sys
from collections import defaultdict
import csv

from ansystotal.ansyspreprocessing import ansys_component_writer as acr
from ansystotal.ansyspreprocessing import ansys_file_reader as afr
from ansystotal.genericoperations import generic_commands as gc, gr_commands as grc
from ansystotal.ansyspostprocessing import vtk_file_writer as vfw, tensor_operations as to
import ansystotal.genericoperations.mesh_information_structures as mis


def read_updated_homeo_file(filename):

    curr_homeo_value_dict = defaultdict()

    with open(filename, 'rt') as uphome_file:
        reader = csv.reader(uphome_file, delimiter=',')

        # Cleanly instruct the csv reader to skip the header line
        # this has been done in order to maintain a header line
        # so as to be able to understand the csv file when opened
        # manually
        next(reader)
        for row in reader:
            el_no = int(row[0])
            sigma_h_i4 = float(row[1])
            sigma_h_i6 = float(row[2])
            curr_homeo_value_dict[el_no] = [sigma_h_i4, sigma_h_i6]

    return curr_homeo_value_dict


def write_updated_homeo_file(filename, home_stress_dict):

    # with open(filename)
    with open(filename, 'w') as uph_file:
        uph_file.write("e_no, sigma_ch_i4, sigma_ch_i6\n")
        for e_no, values in home_stress_dict.items():
            sigma_ch_i4 = values[0]
            sigma_ch_i6 = values[1]
            uph_file.write("{}, {}, {}\n".format(e_no, sigma_ch_i4, sigma_ch_i6))



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

    if curr_step < 10:
        vtk_file = 'results_vtk_0' + str(curr_step) + '.vtk'
        vtk_file_materials = 'materials_vtk_0' + str(curr_step) + '.vtk'
    else:
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

def remodelling_routine(strain_curr_step_file,
        strain_homeostatic_step_file,
        material_curr_step_file,
        material_homeostatic_step_file,
        material_values_new_step_fname,
        material_inp_fname,
        fibroblast_info_homeo_fname,
        fibroblast_info__curr_fname,
        fibroblast_info_new_fname,
        parameters_file,
        evo_flag):

    # a. Read in the output from ANSYS (log strains)
    # b. Calculate i4, i6
    # c. In turn calculate Cauchy Stresses in respective fibre directions
    # d. Growth based on fibroblast stretch changes
    # e. Remodelling based on Cauchy Stresses.
    # f. Update files for the next step

    parameters = grc.read_params_file(parameters_file)

    # data directory reader
    data_directory = gc.return_read_root_directory_name('./parameters/directories_information.dat')

    time_period = int(parameters['time_period'])
    steps = int(parameters['number_of_iterations'])
    alpha = float(parameters['alpha'])
    beta = float(parameters['beta'])
    gamma = float(parameters['gamma'])
    curr_step = int(parameters['iteration'])

    c_delta_t = float(time_period/steps)

    # Read infarcted tissue zone
    infarct_reader = afr.ListReader()
    infarct_file = data_directory['myocardium'] + "degradation_elements.dat"
    infarct_zone = infarct_reader.read_elements(infarct_file)

    # Read in the strain files
    hencky_strains_curr = afr.read_strain_output(strain_curr_step_file)
    hencky_strains_home = afr.read_strain_output(strain_homeostatic_step_file)

    material_values_dict_curr = afr.read_hgo_material(material_curr_step_file)
    material_values_dict_home = afr.read_hgo_material(material_homeostatic_step_file)

    i4_dict_curr, i6_dict_curr = to.create_invariant_dictionaries(material_values_dict_curr, hencky_strains_curr)
    i4_dict_home, i6_dict_home = to.create_invariant_dictionaries(material_values_dict_home, hencky_strains_home)

    # Read in the friboblast stretch files
    fibroblast_info_dict_curr = afr.read_fibroblast_stretch_file(fibroblast_info__curr_fname)
    fibroblast_info_dict_home = afr.read_fibroblast_stretch_file(fibroblast_info_homeo_fname)

    # Storing new values and dictionaries for the next step and vtk files
    new_materials_dict = material_values_dict_curr

    fibroblast_info_dict_new = defaultdict()

    sigma_aniso_i4_h         = defaultdict()
    sigma_aniso_i4_curr      = defaultdict()
    sigma_aniso_i4_difference  = defaultdict()

    sigma_aniso_i6_h         = defaultdict()
    sigma_aniso_i6_curr      = defaultdict()
    sigma_aniso_i6_difference  = defaultdict()

    fibroblast_stretch_i4 = defaultdict()
    fibroblast_stretch_i6 = defaultdict()

    # Homeo Update
    homeo_file_name_updated = "updated_homeo.csv"

    updated_homeo_stress = defaultdict()
    inp_up_homeo_stress = read_updated_homeo_file(homeo_file_name_updated)

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
    d_time      = 14 * (steps / time_period)
    d_time_coll = 5 * (steps/ time_period)

    for e_no, values in material_values_dict_curr.items():
        # Adjust rates for growth and remodelling
        # if e_no not in infarct_zone.keys() and time_period < d_time:
        #     _alpha = 0.0 * alpha
        #     _gamma = 0.0 * gamma
        #     _beta  = 0.0 * beta
        # elif e_no not in infarct_zone.keys() and time_period >= d_time:
        #     _alpha = 0.001 * alpha
        #     _gamma = 0.001 * gamma
        #     _beta  = 0.001 * beta
        # else:
        _alpha = 1.0 * alpha
        _gamma = 1.0 * gamma
        _beta  = 1.0 * beta

        # Read in the values for the homeostatic step file
        c_homeo = material_values_dict_home[e_no][0][0]
        k1_home = material_values_dict_home[e_no][0][1]
        k2_home = material_values_dict_home[e_no][0][2]
        k3_home = material_values_dict_home[e_no][0][3]
        k4_home = material_values_dict_home[e_no][0][4]


        # Read in the values for the current step file
        c_curr = values[0][0]
        k1_curr = values[0][1]
        k2_curr = values[0][2]
        k3_curr = values[0][3]
        k4_curr = values[0][4]

        avec = values[1]
        bvec = values[2]

        vol = values[3]
        m_gm = values[4][0]
        v_m_c_i4 = float(values[4][1])
        v_m_c_i6 = float(values[4][2])
        c_new = c_curr

        # Degrade
        if e_no in infarct_zone.keys():

            if curr_step <= d_time:
                m_gm =  0.001**(curr_step / d_time)
                c_new = c_homeo * m_gm
                if c_new <= 0.001 * c_homeo:
                    c_new = 0.001 * c_homeo # be careful how you degrade !
            else:
                c_new = 0.001 * c_homeo


        # Now proceed with the cauchy stress calculations
        i4_homeo = i4_dict_home[e_no]
        i6_homeo = i6_dict_home[e_no]

        i4_curr = i4_dict_curr[e_no]
        i6_curr = i6_dict_curr[e_no]

        an_pk_home_i4, an_cauchy_home_i4 = to.calculate_aniso_stresses(k1_home, k2_home, i4_homeo)
        an_pk_home_i6, an_cauchy_home_i6 = to.calculate_aniso_stresses(k3_home, k4_home, i6_homeo)
        up_homeo_cauchy_i4 = inp_up_homeo_stress[e_no][0]
        up_homeo_cauchy_i6 = inp_up_homeo_stress[e_no][1]


        an_pk_curr_i4, an_cauchy_curr_i4 = to.calculate_aniso_stresses(k1_curr, k2_curr, i4_curr)
        an_pk_curr_i6, an_cauchy_curr_i6 = to.calculate_aniso_stresses(k3_curr, k4_curr, i6_curr)


        # ------------------------------- Fibroblast update ------------------------------------------------------ #

        # fibr_stretch_dict[element_number] = [fibro_rec_stretch_i4, fibro_rec_stretch_i6,
        #                                      fibroblast_rec_stretch_i4, fibroblast_rec_stretch_i6,
        #                                      tissue_stretch_i4, tissue_stretch_i6]

        fibro_stretch_homeo_i4 = fibroblast_info_dict_home[e_no][0]
        fibro_stretch_homeo_i6 = fibroblast_info_dict_home[e_no][1]

        fibro_stretch_rec_i4 = fibroblast_info_dict_curr[e_no][2]
        fibro_stretch_rec_i6 = fibroblast_info_dict_curr[e_no][3]

        tissue_stretch_i4 = math.sqrt(i4_curr)
        tissue_stretch_i6 = math.sqrt(i6_curr)

        # fibro_rec_curr      = fibroblast_info_dict_curr[e_no][1]
        fibro_stretch_curr_i4  = tissue_stretch_i4 / fibro_stretch_rec_i4
        fibro_stretch_curr_i6  = tissue_stretch_i6 / fibro_stretch_rec_i6

        # if int(evo_flag) == 1:
        #     fibro_stretch_homeo_i4 = (fibro_stretch_curr_i4 + fibro_stretch_homeo_i4) / 2
        #     fibro_stretch_homeo_i6 = (fibro_stretch_curr_i6 + fibro_stretch_homeo_i6)/ 2

        fibro_rec_new_i4 = fibro_stretch_rec_i4 + _gamma *  c_delta_t * fibro_stretch_rec_i4 *\
                        ((fibro_stretch_curr_i4 - fibro_stretch_homeo_i4) / fibro_stretch_homeo_i4)

        fibro_rec_new_i6 = fibro_stretch_rec_i6 + _gamma *  c_delta_t * fibro_stretch_rec_i6 *\
                        ((fibro_stretch_curr_i6 - fibro_stretch_homeo_i6) / fibro_stretch_homeo_i6)


        fibroblast_info_dict_new[e_no] = [fibro_stretch_curr_i4, fibro_stretch_curr_i6,
                                           fibro_rec_new_i4, fibro_rec_new_i6,
                                           tissue_stretch_i4, tissue_stretch_i6]

        # Update the values in the new materials dictionary to be fed ito the next simulation
        # if k in infarct_zone.keys():

        m_c_new_i4    = v_m_c_i4 + _beta  *  v_m_c_i4 * c_delta_t * \
                         ((fibro_stretch_curr_i4 - fibro_stretch_homeo_i4) / fibro_stretch_homeo_i4)

        m_c_new_i6    = v_m_c_i6 + _beta  *  v_m_c_i6 * c_delta_t * \
                         ((fibro_stretch_curr_i6 - fibro_stretch_homeo_i6) / fibro_stretch_homeo_i6)

        # ------------------------------- Fibroblast update end -------------------------------------------------- #


        # Evolution of homoeostatic stress for colagen fibres.
        if int(evo_flag) == 1 and curr_step <= d_time - (1 * (steps / time_period)):
            an_cauchy_home_i4_temp = (an_cauchy_home_i4 + an_cauchy_curr_i4) / 2
            an_cauchy_home_i6_temp = (an_cauchy_home_i6 + an_cauchy_curr_i6) / 2

            if an_cauchy_home_i6_temp < up_homeo_cauchy_i6:
                an_cauchy_home_i6 = up_homeo_cauchy_i6
            else:
                an_cauchy_home_i6 = an_cauchy_home_i6_temp

            if an_cauchy_home_i4_temp < up_homeo_cauchy_i4:
                an_cauchy_home_i4 = up_homeo_cauchy_i4
            else:
                an_cauchy_home_i4 = an_cauchy_home_i4_temp
        # else:
        #     an_cauchy_home_i4 = up_homeo_cauchy_i4
        #     an_cauchy_home_i6 = up_homeo_cauchy_i6


        updated_homeo_stress[e_no] = [an_cauchy_home_i4, an_cauchy_home_i6]

        if an_cauchy_curr_i4 > 0 and an_cauchy_home_i4 > 0:
            k2_new = k2_curr - _alpha * k2_curr * c_delta_t * \
                    (v_m_c_i4 * an_cauchy_curr_i4 - an_cauchy_home_i4) / an_cauchy_home_i4

            if k2_new <= 0.01 * k2_home:
                k2_new = 0.01 * k2_home

        else:
            k2_new = k2_curr

        if an_cauchy_curr_i6 > 0 and an_cauchy_home_i6 > 0:
            k4_new = k4_curr - _alpha * k4_curr * c_delta_t * \
                     (v_m_c_i6 * an_cauchy_curr_i6 - an_cauchy_home_i6) / an_cauchy_home_i6

            if k4_new < 0.01 * k4_home:
                k4_new = 0.01 * k4_home
        else:
            k4_new = k4_curr

        k1_new = k1_home * (k2_new / k2_home) #* m_c_new_i4
        k3_new = k3_home * (k4_new / k4_home) #* m_c_new_i6

        # k1_new = m_c_new_i4 * k1_curr
        # k3_new = m_c_new_i6 * k3_curr

        if k1_new < 0.01 * k1_home:
            k1_new = 0.01 * k1_home #* m_c_new_i4

        if k3_new < 0.01 * k3_home:
            k3_new = 0.01 * k3_home #* m_c_new_i6

        # if e_no in infarct_zone.keys():
        new_materials_dict[e_no][0][0] = c_new
        new_materials_dict[e_no][0][1] = k1_new * m_c_new_i4
        new_materials_dict[e_no][0][2] = k2_new
        new_materials_dict[e_no][0][3] = k3_new * m_c_new_i6
        new_materials_dict[e_no][0][4] = k4_new
        # Mass density updates
        new_materials_dict[e_no][4][1] = m_c_new_i4
        new_materials_dict[e_no][4][2] = m_c_new_i6

        # Storing values
        # Store values
        sigma_aniso_i4_curr[e_no] = an_cauchy_curr_i4
        sigma_aniso_i4_h[e_no] = an_cauchy_home_i4
        sigma_aniso_i4_difference[e_no] = (an_cauchy_curr_i4 - an_cauchy_home_i4) #/ an_cauchy_home_i4
        #
        sigma_aniso_i6_curr[e_no] = an_cauchy_curr_i6
        sigma_aniso_i6_h[e_no] = an_cauchy_home_i6
        sigma_aniso_i6_difference[e_no] = (an_cauchy_curr_i6 - an_cauchy_home_i6) #/ an_cauchy_home_i6

        fibroblast_stretch_i4[e_no] = fibro_stretch_curr_i4
        fibroblast_stretch_i6[e_no] = fibro_stretch_curr_i6

    # Write Updated Homoeostatic File
    write_updated_homeo_file(homeo_file_name_updated, updated_homeo_stress)

    # Write in the new materials
    mat_writer = acr.DataWriter()

    mat_writer.write_material_ahyper_expo_lv(material_inp_fname, material_values_new_step_fname, new_materials_dict)

    grc.write_params_file(parameters_file,
                          time_period,
                          steps,
                          curr_step + 1,
                          alpha,
                          beta,
                          gamma)

    # Write out the fibroblast recruitment field file
    grc.write_fibrobast_file(fibroblast_info_new_fname, fibroblast_info_dict_new)
    write_vtk_file(new_materials_dict, results_dictionary, curr_step)
    # write_result_sheet_files(results_dictionary, curr_step)

def exec_remodelling():

    strain_curr_step_file = sys.argv[1]
    strain_homeostatic_step_file = sys.argv[2]
    material_curr_step_file = sys.argv[3]
    material_homeostatic_step_file = sys.argv[4]
    material_values_new_step_fname = sys.argv[5]
    material_inp_fname = sys.argv[6]
    fibroblast_info_homeo_fname = sys.argv[7]
    fibroblast_info__curr_fname = sys.argv[8]
    fibroblast_info_new_fname = sys.argv[9]
    parameters_file = sys.argv[10]
    evo_flag = sys.argv[11]

    remodelling_routine(
        strain_curr_step_file,
        strain_homeostatic_step_file,
        material_curr_step_file,
        material_homeostatic_step_file,
        material_values_new_step_fname,
        material_inp_fname,
        fibroblast_info_homeo_fname,
        fibroblast_info__curr_fname,
        fibroblast_info_new_fname,
        parameters_file,
        evo_flag)

if __name__ == '__main__':
    exec_remodelling()

import sys

from collections import defaultdict

import ansystotal.genericoperations.gr_commands as grc
import ansystotal.ansyspreprocessing.ansys_file_reader as afr
import ansystotal.ansyspreprocessing.ansys_component_writer as acw
import ansystotal.ansyspreprocessing.ansys_file_writer as afw
import ansystotal.ansyspostprocessing.tensor_operations as to
import ansystotal.genericoperations.calculate_displacement_function as cdf
import ansystotal.ansyspostprocessing.vtk_file_writer as vfw
import ansystotal.genericoperations.mesh_information_structures as mis
from ansystotal.genericoperations import generic_commands as gc


def remodel_material(strain_curr_file,          # Current step - strain file
                     strain_homeo_file,         # Homeostatic step - strain file
                     stress_curr_file,          # Current Step - Stress File
                     stress_homeo_file,         # Homeostatic step - stress file
                     material_curr_csv,         # Current Step - Materials File
                     materials_inp_fname,       # 'materials.inp'
                     material_new_csv,          # New File_name - next_step materials_values_*.csv
                     material_homeo_csv,        # Homeostatic Step - Materials File
                     parameters_file):          # Parameters file

    """
    Algorithm:

         1. read in the old material values file into a dictionary (read_hgo_material)
         2. read in old stress file and current stress file
         3. calculate tissue_stress_grad of the stresses
         4. remodel k2m, k2t
         5. Write in a new materials file and material value file
         6. Create the input for next simulation
    """

    # print("Files: {}, {}, {}, {}, {}".format(strain_curr_file, strain_homeo_file,
    #                                          material_curr_csv, material_homeo_csv, material_new_csv))

    # Read time info for rates and step info
    parameter_info  = grc.read_params_file(parameters_file)
    beta_t          = float(parameter_info['beta_t'])
    beta_m          = float(parameter_info['beta_m'])
    
    time_period             = int(parameter_info['time_period'])
    number_of_iterations    = int(parameter_info['number_of_iterations'])
    curr_step               = int(parameter_info['iteration'])

    init_time = int(parameter_info['init_time'])
    max_time  = int(parameter_info['max_time'])
    init_disp = float(parameter_info['init_disp'])
    max_disp  = float(parameter_info['max_disp'])

    c_delta_t = time_period / number_of_iterations

    # The variables below are required to calculate the displacement given
    # the step function :)

    # Initial time, Final Time


    # ---------------------------------------------------------------------------------------------------------------- #
    #                                                                                                                  #
    #                                              Remodelling of k2                                                   #
    #                                                                                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    # Remodelling

    # Reading in files and calculating new material values based on what information we have from the previous steps.
    # 1. Read in homeostatic strains
    # 2. Read in current strain values
    # 3. calculate the Cauchy stresses in collagen via I_4
    # 4. This will help us in the remodelling equation for k_2 = - a (stress_curre - stress_homeo) / stress_homeo  of
    # collagen

    # Reading in the strains
    hencky_strains_current  = afr.read_strain_output(strain_curr_file)
    hencky_strains_homeo    = afr.read_strain_output(strain_homeo_file)

    i4_dict_curr, i6_dict_curr      = to.create_i4_dictionary_musc(material_curr_csv, hencky_strains_current)
    i4_dict_homeo, i6_dict_homeo    = to.create_i4_dictionary_musc(material_homeo_csv, hencky_strains_homeo)

    # Read in the materials file to get a materials dictionary to be used in the calculation of stresses
    material_values_curr    = afr.read_hgo_material_musc(material_curr_csv)
    material_values_homeo   = afr.read_hgo_material_musc(material_homeo_csv)

    new_materials   = material_values_curr

    # Write to a new file sigma, sigma_h, sigma - sigma_h for each element for collagen fibres
    # now

    results_stress_csv_file = 'aniso_stresses_'+str(curr_step)+'.csv'

    # Tendon
    sigma_aniso_h_t         = defaultdict()
    sigma_aniso_curr_t      = defaultdict()
    sigma_aniso_difference_t  = defaultdict()

    # Muscle
    sigma_aniso_h_m         = defaultdict()
    sigma_aniso_curr_m      = defaultdict()
    sigma_aniso_difference_m  = defaultdict()



    for e_no in hencky_strains_homeo.keys():

        c1_homeo  = material_values_homeo[e_no][0][0]
        k1t_homeo = material_values_homeo[e_no][0][1]
        k2t_homeo = material_values_homeo[e_no][0][2]
        k1m_homeo = material_values_homeo[e_no][0][3]
        k2m_homeo = material_values_homeo[e_no][0][4]
        # av_x      = material_values_homeo[e_no][1][0]
        # av_y      = material_values_homeo[e_no][1][1]
        # av_z      = material_values_homeo[e_no][1][2]
        # bv_x      = material_values_homeo[e_no][2][0]
        # bv_y      = material_values_homeo[e_no][2][1]
        # bv_z      = material_values_homeo[e_no][2][2]
        # pvol      = material_values_homeo[e_no][3]
        # fx_homeo  = material_values_homeo[e_no][4]


        # need all values from current iteration so 
        # that materials can be set up for next run 
        c1_curr     = material_values_curr[e_no][0][0]
        k1t_curr    = material_values_curr[e_no][0][1]
        k2t_curr    = material_values_curr[e_no][0][2]
        k1m_curr    = material_values_curr[e_no][0][3]
        k2m_curr    = material_values_curr[e_no][0][4]
        av_x_curr   = material_values_curr[e_no][1][0]
        av_y_curr   = material_values_curr[e_no][1][1]
        av_z_curr   = material_values_curr[e_no][1][2]
        bv_x_curr   = material_values_curr[e_no][2][0]
        bv_y_curr   = material_values_curr[e_no][2][1]
        bv_z_curr   = material_values_curr[e_no][2][2]
        pvol_curr   = material_values_curr[e_no][3]
        fx_curr     = material_values_curr[e_no][4]

        # Remodelling values

        if fx_curr == 0:

            pk_stress_musc_homeo, cau_stress_muscle_homeo = to.calculate_aniso_stresses(k1m_homeo, k2m_homeo,
                                                                                        i6_dict_homeo[e_no])
            pk_stress_muscle_curr, cau_stress_muscle_curr = to.calculate_aniso_stresses(k1m_curr, k2m_curr,
                                                                                        i6_dict_curr[e_no])

            cau_stress_muscle_gradient = float(
                (cau_stress_muscle_curr - cau_stress_muscle_homeo) / cau_stress_muscle_homeo)

            # Store stresses
            sigma_aniso_curr_m[e_no] = cau_stress_muscle_curr
            sigma_aniso_h_m[e_no]    = cau_stress_muscle_homeo

            sigma_aniso_difference_m[e_no] = cau_stress_muscle_gradient

            sigma_aniso_curr_t[e_no] = 0
            sigma_aniso_h_t[e_no]    = 0

            sigma_aniso_difference_t[e_no] = 0

            new_k2m = k2m_curr - ((beta_m * cau_stress_muscle_gradient) * c_delta_t)

            if new_k2m <= 0.01:
                new_k2m=0.01

            new_k1m = new_k2m * (k1m_homeo/k2m_homeo)
            if new_k1m <= 0.1 * k1m_homeo:
                new_k1m = 0.1 * k1m_homeo


            new_materials[e_no] = [
                    [c1_curr, k2t_curr, k2t_curr, new_k1m, new_k2m],
                    [av_x_curr, av_y_curr, av_z_curr],
                    [bv_x_curr, bv_y_curr, bv_z_curr],
                    pvol_curr,
                    fx_curr
            ]

        elif fx_curr == 1:

            pk_stress_tendon_homeo, cau_stress_tendon_homeo = to.calculate_aniso_stresses(k1t_homeo, k2t_homeo,
                                                                                          i4_dict_homeo[e_no])  # Tendon
            pk_stress_tendon_curr, cau_stress_tendon_curr = to.calculate_aniso_stresses(k1t_curr, k2t_curr,
                                                                                        i4_dict_curr[e_no])

            cau_stress_tendon_gradient = float(
                (cau_stress_tendon_curr - cau_stress_tendon_homeo) / cau_stress_tendon_homeo)

            # Store stresses
            sigma_aniso_curr_m[e_no] = 0
            sigma_aniso_h_m[e_no]    = 0

            sigma_aniso_difference_m[e_no] = 0

            sigma_aniso_curr_t[e_no] = cau_stress_tendon_curr
            sigma_aniso_h_t[e_no]    = cau_stress_tendon_curr

            sigma_aniso_difference_t[e_no] = cau_stress_tendon_gradient

            new_k2t       = k2t_curr - ((beta_t * cau_stress_tendon_gradient) * c_delta_t)

            if new_k2t <= 0.01:
                new_k2t=0.01

            new_k1t = new_k2t * (k1t_homeo / k2t_homeo)
            if new_k1t < 0.1 * k1t_homeo:
                    new_k1t = 0.1 * k1t_homeo


            new_materials[e_no] = [
                    [c1_curr, new_k1t, new_k2t, k1m_curr, k2m_curr],
                    [av_x_curr, av_y_curr, av_z_curr],
                    [bv_x_curr, bv_y_curr, bv_z_curr],
                    pvol_curr,
                    fx_curr
            ]

        elif 0 < fx_curr < 1:

            pk_stress_tendon_homeo, cau_stress_tendon_homeo = to.calculate_aniso_stresses(k1t_homeo, k2t_homeo,
                                                                                          i4_dict_homeo[e_no])  # Tendon
            pk_stress_tendon_curr, cau_stress_tendon_curr = to.calculate_aniso_stresses(k1t_curr, k2t_curr,
                                                                                        i4_dict_curr[e_no])

            pk_stress_musc_homeo, cau_stress_muscle_homeo = to.calculate_aniso_stresses(k1m_homeo, k2m_homeo,
                                                                                        i6_dict_homeo[e_no])
            pk_stress_muscle_curr, cau_stress_muscle_curr = to.calculate_aniso_stresses(k1m_curr, k2m_curr,
                                                                                        i6_dict_curr[e_no])

            cau_stress_muscle_gradient = float(
                (cau_stress_muscle_curr - cau_stress_muscle_homeo) / cau_stress_muscle_homeo)

            cau_stress_tendon_gradient = float(
                (cau_stress_tendon_curr - cau_stress_tendon_homeo) / cau_stress_tendon_homeo)


            # Store stresses
            sigma_aniso_curr_m[e_no] = cau_stress_muscle_curr
            sigma_aniso_h_m[e_no]    = cau_stress_muscle_homeo

            sigma_aniso_difference_m[e_no] = cau_stress_muscle_gradient

            sigma_aniso_curr_t[e_no] = cau_stress_tendon_curr
            sigma_aniso_h_t[e_no]    = cau_stress_tendon_curr

            sigma_aniso_difference_t[e_no] = cau_stress_tendon_gradient

            # Remodelling

            new_k2t = k2t_curr - ((beta_t * cau_stress_tendon_gradient) * c_delta_t)
            new_k2m = k2m_curr - ((beta_m * cau_stress_muscle_gradient) * c_delta_t)

            if new_k2t <= 0.01:
                new_k2t=0.01

            if new_k2m <= 0.01:
                new_k2m = 0.01

            new_k1t = new_k2t * (k1t_homeo / k2t_homeo)
            if new_k1t < 0.1 * k1t_homeo:
                new_k1t = 0.1 * k1t_homeo

            new_k1m = new_k2m * (k1m_homeo/k2m_homeo)
            if new_k1m <= 0.1 * k1m_homeo:
                new_k1m = 0.1 * k1m_homeo
            # print(new_k2t, new_k2m, cau_stress_tendon_gradient, cau_stress_muscle_gradient)
            new_materials[e_no] = [
                    [c1_curr, new_k1t, new_k2t, new_k1m, new_k2m],
                    [av_x_curr, av_y_curr, av_z_curr],
                    [bv_x_curr, bv_y_curr, bv_z_curr],
                    pvol_curr,
                    fx_curr
            ]

    results_dictionary = defaultdict()

    results_dictionary['sigma_aniso_h_t']           = sigma_aniso_h_t
    results_dictionary['sigma_aniso_curr_t']        = sigma_aniso_curr_t
    results_dictionary['sigma_aniso_difference_t']  = sigma_aniso_difference_t
    #
    results_dictionary['sigma_aniso_h_m']           = sigma_aniso_h_m
    results_dictionary['sigma_aniso_curr_m']        = sigma_aniso_curr_m
    results_dictionary['sigma_aniso_difference_m']  = sigma_aniso_difference_m
    results_dictionary['i4_values']                 = i4_dict_curr
    results_dictionary['i6_values']                 = i6_dict_curr

    # Write function to write out to a file
    # 1. Isotropic, anisotropic(muscle and tendon) stresses, strains and stretches
    # 2. Stress differences (muscle and tendon) for sigma - sigma_h

    # 1. write the updated materials into a new csv file
    # 2. write updated materials in 'materials.inp'
    writer_object = acw.DataWriter()
    writer_object.write_material_ahyper_expo_musc(materials_inp_fname,material_new_csv, new_materials)

    # 3. update the parameters file\
    parameters           = parameter_info # unnecessary dummy variable
    step_function = str(parameters['step_function'])

    grc.write_params_muscle(parameters_file,
                            time_period,
                            number_of_iterations,
                            curr_step + 1,
                            beta_t,
                            beta_m,
                            init_time,
                            max_time,
                            init_disp,
                            max_disp,
                            step_function)

    # Calculate displacement for the next step
    displacement_calc = cdf.DisplacementCalculator(parameters=parameters)

    displacement      = displacement_calc.calculate_displacement(flag=step_function)

    print("\ncurrent Displacement:{}".format(displacement))

	# Update the ANSYS script for updated displacement for the next iteration
    sol_file_writer = afw.AnsysInpWriter()
    sol_file_writer.create_solu_inp_file_tissue_strip("solution.inp", displacement)

    write_vtk_file(new_materials, results_dictionary, curr_step)

    write_result_sheet_files(results_dictionary, curr_step)


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
        data_directory = root_dir['strip']

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
        vtk_writer.create_material_value_tables_muscle_hexahedral(vtk_file_materials, materials_dictionary)

        # vtk_writer for stresses (change in the core file :) )

def exec_remodelling():

    strain_curr_file            = sys.argv[1]
    strain_homeo_file           = sys.argv[2]
    stress_curr_file            = sys.argv[3]
    stress_homeo_file           = sys.argv[4]
    material_old_csv            = sys.argv[5]
    material_new_csv            = sys.argv[6]
    materials_inp_file          = sys.argv[7]
    material_homeo_csv          = sys.argv[8]
    parameters_file             = sys.argv[9]

    remodel_material(strain_curr_file,
                     strain_homeo_file,
                     stress_curr_file,
                     stress_homeo_file,
                     material_old_csv,
                     material_new_csv,
                     materials_inp_file,
                     material_homeo_csv,
                     parameters_file)

					 
if __name__ == '__main__':
    exec_remodelling()


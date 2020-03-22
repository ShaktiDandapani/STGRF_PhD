import sys

from ansystotal.ansysexecutionfiles import gr_data_setup_controller as anhgo
from ansystotal.genericoperations import generic_commands as gc, gr_commands as grc, useful_decorators as ud

"""
@Shaktidhar Dandapani - The University of Sheffield, 2018. ANSYS(c)

"""

# set up multiple instances, to understand the effect of different parameters
# on the model simulation.
# Also, let one set finish till the step it converges to (or set up a
# flag in perl/ python to stop as soon as an error occurs in the
# remodelling script.)

# Flags to:
#        a. Specify LV, Aneurysm, or whatever is on
#        b. GUI or manual ? (maybe not)
# Restructure code for the GUI.

def write_params_file_from_dict(fname, parameters):

    with open(fname, 'w') as pfile :
        for k, v in parameters.items():
            pfile.write("{}={}\n".format(k, v))

    return 1

def reset_parameters_file(parameters_file_name):
    parameters = grc.read_params_file(parameters_file_name)

    parameters['iteration'] = 0

    return parameters

@ud.calculate_time
def gr_hgo_expo(flag):
    """

    :param flag: based on the value provided, switch simulation context for
                 particular tissue type (myocardium, skeletal_muscle, artery)
    :return 1: For true ( dummy return )
    """

    # Provide a name for the ansys input file macro to be read in by the ANSYS MAPDL program.
    ansys_file_name    = 'ansys_job.inp'

    # Obtain the root directory for the data files stored in ansysdata using directories_information file
    root_dir           = gc.return_read_root_directory_name('./parameters/directories_information.dat')
    data_directory     = ''
    parameters         = ''

    # Based on the flag execute the corresponding script for simulation setup
    # Note this will set up a single simulation which could be regarded as
    # the healthy tissue state.
    if flag == "myocardium":
        data_directory = root_dir['myocardium']
        parameters_fname = './parameters/parameters_myocardium.dat'
        parameters = reset_parameters_file(parameters_fname)
        write_params_file_from_dict(parameters_fname, parameters)
        # replace iteration with iteration = 0
    elif flag == "cube":
        data_directory = root_dir['cube']
        parameters_fname = './parameters/parameters_cube.dat'
        parameters = reset_parameters_file(parameters_fname)
        write_params_file_from_dict(parameters_fname, parameters)

    # Call in the function to write the required MACRO files for ANSYS MAPDL to execute the structural
    # analysis.
    anhgo.write_inp_file(ansys_file_name=ansys_file_name,
                         data_directory=data_directory,
                         fibre_dictionary=None,
                         parameters=parameters,
                         flag=flag)
    return 1

if __name__ == '__main__':
    sim_flag = str(sys.argv[1])
    gr_hgo_expo(sim_flag)

from __future__ import division
from collections import defaultdict
import math
"""
This file contains code which is used to read in files for growth and remodelling which are not
completely integrated with the ansys code, thus its exclusion from ansys_file_reader.

"""

def read_params_file(filename):
    """
    Reads in the file with terms and values separated by an equal sign and puts
    them in a dictionary term = value

    :param filename:
    :return:
    """

    params_dictionary = defaultdict(list)

    # Reader for excel files
    file_contents = open(filename, 'r')

    for line in file_contents:
        line    = line.strip()
        line    = line.split('=')
        term    = line[0]
        value   = line[1]
        params_dictionary[term] = value

    file_contents.close()

    return params_dictionary

# Different writer for muscle parameters

def write_params_muscle(filename,
                        time_period,
                        number_of_iterations,
                        iteration,
                        beta_t,
                        beta_m,
                        init_time,
                        max_time,
                        init_disp,
                        max_disp,
                        step_function):

    with open(filename, 'w') as params_file:
        params_file.write('time_period={}\nnumber_of_iterations={}'.format(time_period, number_of_iterations))
        params_file.write('\nbeta_t={}\nbeta_m={}\ninit_time={}\nmax_time={}\niteration={}'.format(beta_t, beta_m, init_time, max_time, iteration))
        params_file.write('\ninit_disp={}\nmax_disp={}\nstep_function={}'.format(init_disp, max_disp, step_function))
    pass

def write_params_file(filename,
                      time_period,
                      number_of_iterations,
                      i, # current iteration
                      alpha,
                      beta,
                      gamma):

    # Create time information file
    params_file = open(filename, 'w')

    #with open()

    params_file.write('time_period={}\nnumber_of_iterations={}'.format(time_period, number_of_iterations))
    params_file.write('\nalpha={}\nbeta={}\ngamma={}\niteration={}'.format(alpha, beta, gamma, i))
    params_file.close()


def write_fibrobast_file(filename,
                         fib_stretch_dict = defaultdict(list)):
    """

    :param filename:
    :param fib_stretch_dict:
    :return:
    """
    fibro_stretch_file  = open(filename, 'w')

    fibro_stretch_file.write("Element Number, FStretch_i4, FStretch_i6, F_RecStretch_i4, F_RecStretch_i6, TisStretch_i4"
                             ", TisStretch_i6\n")
    for e_no, stretch_list in fib_stretch_dict.items():
        fibro_stretch_i4 = stretch_list[0]
        fibro_stretch_i6 = stretch_list[1]
        fibroblast_rec_stretch_i4 = stretch_list[2]
        fibroblast_rec_stretch_i6 = stretch_list[3]
        tissue_stretch_i4  = stretch_list[4]
        tissue_stretch_i6 = stretch_list[5]

        fibro_stretch_file.write("{}, {}, {}, {}, {}, {}, {}\n".format(e_no, fibro_stretch_i4, fibro_stretch_i6,
                                                                            fibroblast_rec_stretch_i4, fibroblast_rec_stretch_i6,
                                                                            tissue_stretch_i4, tissue_stretch_i6))
    fibro_stretch_file.close()


# This function is only for calculating the lambda_fibroblast
def fibroblast_stretch_calculation(fibroblast_rec_stretch,
                                   invariant_4):

    fibroblast_stretch = math.sqrt(invariant_4) / fibroblast_rec_stretch

    return fibroblast_stretch



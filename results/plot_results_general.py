from collections import defaultdict
from collections import OrderedDict
import matplotlib.pyplot as plt
import glob
import re
import os

import numpy as np
import pandas as pd
import seaborn as sns
import ansystotal.ansyspreprocessing.ansys_file_reader as afr

def read_result_file(filename):

    result_dictionary = defaultdict()

    with open(filename) as rfile:
        lines = rfile.readlines()
        for line in lines:
            line = line.rstrip()
            line = line.split(',')
            e_no = int(line[0])
            quantity = float(line[1])
            result_dictionary[e_no] = quantity

    return result_dictionary

def plot_result(filename, result_dictionary, flag):

    # Flags -> sigma_i4, sigma_i6, sigma_i4_diff, sigma_i6_diff
    # etc etc

    x_values = result_dictionary.keys()
    y_values = result_dictionary.items()
    title    = filename

    plt.figure()
    plt.plot(result_dictionary.keys(), result_dictionary.values())
    plt.title(title)
    plt.xlabel('Iteration')
    plt.ylabel(flag)


def calculate_mean_quantity_infarcted_elements(filename):
    """
    Read in a mesh results file and obtain the averaged quantity
    for the infarcted area.

    :param filename:
    :return:
    """
    # later on use glob etc to read in all the files and return relevant dictionaries for
    # each time point
    results = read_result_file(filename)

    # get infarcted elements out

    result_values = []
    for e_no, quantity in results.items():
            result_values.append(quantity)

    mean_result = np.mean(result_values)

    return mean_result
    # this is one time step in growth and remodelling and returns the mean value

def batch_calculate_average_values_per_step(filenames):

    mean_dictionary = defaultdict()
    step = 0
    # use regex to extract the last value before the .csv and get it out
    # use that as the int for the step/ iteration number

    for filename in filenames:
        get_number = lambda f: (''.join(filter(str.isdigit, f)))
        step_number = int(get_number(filename))
        mean_value = calculate_mean_quantity_infarcted_elements(filename)
        mean_dictionary[step_number] = mean_value
        print(step_number)

    # ordered_mean_dict = OrderedDict(mean_dictionary)
    
    return mean_dictionary

def gather_results_for_files():

    files = glob.glob('./sigma_aniso_curr_m_*.csv')

    mean_dictionary = batch_calculate_average_values_per_step(files)

    plt.figure()
    plt.plot(mean_dictionary.keys(), mean_dictionary.values(), '*')
    plt.grid()
    plt.show()

if __name__ == '__main__':
    gather_results_for_files()

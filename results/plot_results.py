from collections import defaultdict
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
    reader = afr.ListReader()
    infarct_elemnts = reader.read_elements('degradation_elements.dat')

    result_values = []
    for e_no, quantity in results.items():
        if e_no in infarct_elemnts.keys():
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
        mean_value = calculate_mean_quantity_infarcted_elements(filename)
        mean_dictionary[step] = mean_value
        step += 1

    return mean_dictionary

def gather_results_for_files():

    # files = glob.glob('./sigma_aniso_i4_difference_*.csv')
    files = glob.glob('./i4_step_rem_*.csv')
    # Sort in the ascending order !
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    for f in files:
        print(f)
    mean_dictionary = batch_calculate_average_values_per_step(files)

    x_values = []
    y_values = []

    for k, v in mean_dictionary.items():
        x_values.append(k)
        y_values.append(v)

    plt.figure()
    plt.plot(x_values, y_values)
    plt.grid()
    plt.show()



if __name__ == '__main__':
    # calculate_mean_quantity_infarcted_elements('./sigma_aniso_i4_curr_step_rem_0.csv')
    gather_results_for_files()

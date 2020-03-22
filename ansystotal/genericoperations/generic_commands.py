

"""

This python script file contains functions which are technically general
but modified to be applied to the STGRF.

"""
from collections import defaultdict

def return_read_root_directory_name(filename):
    # Return a dictionary with left and right values
    # and provide dictionary relevant to that particular
    # mesh and geometry

    directory_information = defaultdict()

    with open(filename, 'r') as d_file:
        lines = d_file.readlines()
        for line in lines:
            line  = line.split('=')

            directory_simulation = line[0]
            directory_root = line[1].rstrip()

            directory_information[directory_simulation] = directory_root

    return directory_information

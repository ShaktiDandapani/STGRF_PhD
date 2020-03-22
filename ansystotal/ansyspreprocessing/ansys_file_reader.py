# -*- coding: utf-8 -*-
"""
Created on 08.08.2016

Class file, containing methods/ functions to read in nodes and elements from
the nlist, elist exported from ANSYS APDL.

Current implementation includes reading in elements containing 4, 8 and 10 nodes.
Regular expressions are used to obtain the values from the .txt/.lis files

Regular expressions for elements and nodes can be cleaned up, like the stress retrieval regex.

"""

import csv
from collections import defaultdict
import ansystotal.genericoperations.mesh_information_structures as mo
import re


# noinspection PyPep8Naming
class ListReader:
    """
    \n
    Class for reading in nodes and elements. Individual objects for multiple files :)
    \n
    """

    def __init__(self, n_file_name = None, e_file_name = None,a_file_name = None, kp_file_name = None, l_file_name = None, v_file_name = None):

        self.n_file_name  = n_file_name
        self.e_file_name  = e_file_name
        self.a_file_name  = a_file_name
        self.kp_file_name = kp_file_name
        self.l_file_name  = l_file_name
        self.v_file_name  = v_file_name

    def read_nodes(self, n_file_name):
        """
        Reads the nodes in the file opened in a script.\n
        Returns a clean version of the node numbers with\n
        their co-ordinates

        Args:
		
            n_file_name (str): Name of the file containing ANSYS apdl formatted node description.

        Returns:
		
            node_coordinate_structure (dict): A dictionary containing the node numbers and node\n
            co-ordinates as follows - {node_no: [[x, y, z]]}
        """

        # Errors include - fileNotFound, InvalidParameter to int/float, invalid array index.
        # Empty line given regex mismatch.
        if n_file_name:
            self.n_file_name = n_file_name
            self.n_file = open(self.n_file_name, "r+")
        else:
            self.n_file = open(n_file_name, "r+")

        content = self.n_file.readlines()

        node_coordinate_structure = defaultdict(list)

        expr_nodeLine = re.compile(r"\s*([0-9]+)")
        expr_text     = re.compile(r"\s+[A-Z]+\s+")

        for line in content:
            if re.match(expr_nodeLine, line) and not re.search(expr_text, line):

                line = line.rstrip()
                # strip away the end character on the line string
                line = line.split(' ')
                clean_line = list(filter(None, line))

                node_number = clean_line[0]  # .replace('.','')
                node_number = float(node_number)

                # Create a Point class object to represent the node
                # and store in the dictionary using its label and coordinates
                point = mo.Point(float(clean_line[1]), float(clean_line[2]), float(clean_line[3]), str(int(node_number)))
                node_coordinate_structure[int(point.get_label())].append(
                    point)

        self.n_file.close()
        return node_coordinate_structure

    def read_elements(self, e_file):
        """
        Reads in an ANSYS apdl output formatted element list text file.\n
        Provides a dictionary with the relevant element connectivity\n
        information.

        Example usage:
		
        .. code-block:: python

            read_elements("elist.dat")

        Args:
		
            filename (str): Enter the file name for the ansys elist input.

        Returns:
		
            element_dictionary (dict): an element dictionary for use and manipulation in python.
            co-ordinates as follows - {el_no: [[node_0, ....., node_n]]}

        """
        el_file = open(e_file, "r+")
        el_line = el_file.readlines()
        match_1 = r"\s+([0-9]+)\s+"
        expr_text = r"\s+[A-Z]+\s+"

        regex = re.compile(match_1, re.MULTILINE)

        element_dictionary = defaultdict(list)

        clean_content = []
        refined_content = []

        for line in el_line:
            if re.match(regex, line) and not re.search(expr_text, line):
                line = line.rstrip()
                filtered_line = list(filter(None, line.split(' ')))
                clean_content.append(filtered_line)

        # can close the el_file here as all the rest is poured into clean_content
        el_file.close()

        # The code below needs refining
        for index in range(len(clean_content)):
            # First check if 8 nodes exist in ansys output file for elist.
            if len(clean_content[index]) is 14:
                refined_content.append(clean_content[index])
            elif len(clean_content[index]) is 10:
                refined_content.append(clean_content[index])
            elif len(clean_content[index]) < 14:
                refined_content[-1].extend(clean_content[index])

        for element_line in refined_content:
            nodes_list = []
            for i in range(6, len(element_line)):
                nodes_list.append(int(element_line[i]))
            element_dictionary[int(element_line[0])] = [nodes_list]

        return element_dictionary

    def read_a_lines(self, l_file):
        """
        Returns a lines file with the line number and the keypoints associated with it.

        :param l_file:
        :return:
        """
        l_file = open(l_file, "r+")
        content = l_file.readlines()

        cleaned_content = []

        lines_kp_dict = defaultdict(list)
        # line number : [kp list]

        expr_lineLine = re.compile(r"\s+([0-9]+)")
        expr_text = re.compile(r"s+[A-Z]+\s")

        for line in content:
            if re.match(expr_lineLine, line) and not re.search(expr_text, line):
                line = line.rstrip()  # strip away the end character on the line string
                cleaned_content.append(filter(None, line.split(' ')))  # strip the spaces away

        l_file.close()
        return lines_kp_dict

    def read_areas(self, a_file):
        """
        Returns an area dictionary with the area number and associated lines

        :param a_file: 
        :return: 
        """

        a_file = open(a_file, "r+")
        content = a_file.readlines()

        cleaned_content = []

        areas_line_dict = defaultdict(list)
        # line number : [kp list]

        expr_areaLine = re.compile(r"\s+([0-9]+)")
        expr_text = re.compile(r"s+[A-Z]+\s")

        for line in content:
            if re.match(expr_areaLine, line) and not re.search(expr_text, line):
                line = line.rstrip()  # strip away the end character on the line string
                cleaned_content.append(filter(None, line.split(' ')))  # strip the spaces away

        for clean_line in cleaned_content:
            area_number = clean_line[0]
            areas_line_dict[int(area_number)].append(
                [int(clean_line[2]), int(clean_line[3]), int(clean_line[4]), int(clean_line[5])])

        a_file.close()
        return areas_line_dict

    def read_key_points(self, kp_file):
        """
        returns a kp dictionary with kp number and co-ordinates

        :param kp_file: 
        :return: 
        """
        k_file = open(kp_file, "r+")
        content = k_file.readlines()

        cleaned_content = []

        keypoint_dict = defaultdict(list)

        expr_kpLine = re.compile(r"\s+([0-9]+)")
        expr_text = re.compile(r"s+[A-Z]+\s")

        for line in content:
            if re.match(expr_kpLine, line) and not re.search(expr_text, line):
                line = line.rstrip()  # strip away the end character on the line string
                cleaned_content.append(filter(None, line.split(' ')))  # strip the spaces away

        for clean_line in cleaned_content:
            kp_number = clean_line[0]
            keypoint_dict[int(kp_number)].append([float(clean_line[1]), float(clean_line[2]), float(clean_line[3])])

        k_file.close()
        return keypoint_dict

    def volumes(self, areas_dict):

        area_number = []
        for key in areas_dict.iterkeys():
            area_number.append(key)

        vol_dict = defaultdict(list)
        # Single volume for now .
        for i in range(0, len(area_number)):
            vol_dict[1].append(int(area_number[i]))

        return vol_dict


# noinspection PyPep8
def read_stress_file(stress_file):
    """
    Created on 26.02.2017, 22:08

    @author Shaktidhar Dandapani

    The current function reads in the equivalent stresses from an ansys stress result file.\n
    This could be used in the remodelling script to find the differences in the dictionaries\n
    of step 0 and step n. Which could be used as a remodelling parameter for the material\n
    properties.\n


    :param stress_file: input the file name of the stress results file:)
    :return: dictionary of elemental average equivalent stresses from nodes.
    """
    # Dictionary to contain: {'element_number' : stress_value}
    
    s_file = open(stress_file, "r")

    numerics_pattern = r"\s+[0-9]"
    element_number_line = r"^\s+ELEMENT"
    string_pattern = r"[A-Z]*E+"
    content = s_file.readlines()

    stress_dictionary = defaultdict(list)
    

    node_counter   = 0
    total_s11      = 0
    element_number = 0

    for line in content:

        if re.match(element_number_line, line):
            element_line = line.rstrip()
            element_line = element_line.split(' ')
            element_line = list(filter(None, element_line))
            element_number = int(element_line[1])

            # Reset node variables
            node_counter = 0
            total_s11 = 0

        elif re.match(numerics_pattern, line) and not re.match(string_pattern, line):

            node_counter += 1
            line_content = line.rstrip()
            line_content = line_content.split(' ')
            line_content = filter(None, line_content)

            # 1. Now add the stresses needed to a list
            # 2. Average the list
            # 3. Use the return value outside the if loop to
            #    insert {element_number : avg_stress}
            # 2 -> 2nd principal stress

            sigma_11    = float(line_content[1])
            total_s11   += sigma_11

            # Average first principal stress in that element based on nodal stresses
            avg_stress = total_s11 / node_counter
            stress_dictionary[element_number] = avg_stress

    s_file.close()

    return stress_dictionary


def read_hgo_material(filename):
    """
    Reads in a csv file containing hgo material information about a mesh
    and returns a dictionary to be further processed in a script.

    Example usage:

    .. code-block:: python

        read_hgo_material("material_values.csv")

    Args:
        filename(str): a csv file containing material information

    Returns:
        material_dictionary(dict):  dictionary structure containing all material
                                    information in one neat variable.
    """
    material_dictionary = defaultdict(list)

    with open(filename, 'rt') as csvfile:
        reader     = csv.reader(csvfile, delimiter=',')

        # Cleanly instruct the csv reader to skip the header line
        # this has been done in order to maintain a header line
        # so as to be able to understand the csv file when opened
        # manually
        next(reader)

        for row in reader:
            element_number = int(row[0])
            c1 = float(row[1])
            k1 = float(row[2])
            k2 = float(row[3])
            k3 = float(row[4])
            k4 = float(row[5])
            av_x = float(row[6])
            av_y = float(row[7])
            av_z = float(row[8])
            bv_x = float(row[9])
            bv_y = float(row[10])
            bv_z = float(row[11])
            pvol = float(row[12])
            m_gm = float(row[13])
            m_c_i4  = float(row[14])
            m_c_i6  = float(row[15])
            material_dictionary[element_number] = [
                                                      [c1, k1, k2, k3, k4], # c1, k1, k2
                                                      [av_x, av_y, av_z],   # avector
                                                      [bv_x, bv_y, bv_z],   # bvector
                                                      pvol,
                                                      [m_gm, m_c_i4, m_c_i6]
            ]

    return material_dictionary


def read_strain_output(filename):
    """
    Reads in all the strain values from the Strain output file
    and provides an output of the Strain tensor.

    :param filename:
    :return:
    """
    input_file = open(filename, 'r')

    file_data  = input_file.readlines()

    numerics_pattern = r"\s+[0-9]"
    element_number_line = r"^\s+ELEMENT"
    string_pattern = r"[A-Z]*E+"

    hencky_strain_dict = defaultdict(list)

    # Initialising variables to avoid errors
    node_counter   = 0
    total_e_x      = 0
    total_e_y      = 0
    total_e_z      = 0
    total_e_xy     = 0
    total_e_yz     = 0
    total_e_xz     = 0
    element_number = 0

    for line in file_data:

        if re.match(element_number_line, line):
            element_line = line.rstrip()
            element_line = element_line.split(' ')
            element_line = list(filter(None, element_line))
            element_number = int(element_line[1])
            # Reset node variables
            node_counter = 0

        elif re.match(numerics_pattern, line) and not re.match(string_pattern, line):

            # Here given the number of nodes -> calculate the average strain for each strain component and
            # set that up as a matrix to be added to the strain dictionary per element
            # This dictionary needs to be returned by this function so that the I_4 can be calculated for every
            # element :) -> cue for remodelling.

            node_counter += 1
            line_content = line.rstrip()
            line_content = line_content.split(' ')
            line_content = list(filter(None, line_content))

            # Problem is you need to average for every element and then provide the strain result for it proper

            e_x  = float(line_content[1])
            e_y  = float(line_content[2])
            e_z  = float(line_content[3])

            e_xy = float(line_content[4])
            e_yz = float(line_content[5])
            e_xz = float(line_content[6])

            if node_counter == 1:
                total_e_x = e_x
                total_e_y = e_y
                total_e_z = e_z

                total_e_xy = e_xy
                total_e_yz = e_yz
                total_e_xz = e_xz
            else:

                total_e_x += e_x
                total_e_y += e_y
                total_e_z += e_z

                total_e_xy += e_xy
                total_e_yz += e_yz
                total_e_xz += e_xz

            # Commit
            # Averaged Green Strain Tensor
            # convert to engineering :)
            avg_e_x     = total_e_x / node_counter
            # print(node_counter)
            avg_e_y     = total_e_y / node_counter
            avg_e_z     = total_e_z / node_counter

            avg_e_xy    = total_e_xy / node_counter
            avg_e_xz    = total_e_xz / node_counter
            avg_e_yz    = total_e_yz / node_counter

            avg_e_yx    = avg_e_xy
            avg_e_zx    = avg_e_xz
            avg_e_zy    = avg_e_yz

            # # arrange them in an e_whatever list for each strain component and sum them using math_ops or something.
            hencky_strain_dict[element_number] = [[avg_e_x, avg_e_xy, avg_e_xz],
                                                  [avg_e_yx, avg_e_y, avg_e_yz],
                                                  [avg_e_zx, avg_e_zy, avg_e_z]]
            #
            # hencky_strain_dict[element_number] = [[avg_e_x, 0.0, 0.0],
            #                                       [0.0, avg_e_y, 0.0],
            #                                       [0.0, 0.0, avg_e_z]]

    input_file.close()

    # Return the green strain tensor, for further use.
    return hencky_strain_dict


def read_fibroblast_stretch_file(filename):
    """
    Reads in a fibroblast file and provides a dictionary back as a data structure containing the information

    {e_no: lambda_f, lambda_f^R, lambda_tissue}

    :param filename:
    :return:
    """
    f_file  = open(filename, 'r')

    fibro_stretch_dictionary = defaultdict(list)

    words_regex = re.compile(r'[A-Z]+')

    for line in f_file:
        if re.match(words_regex, line):
            pass
        else:
            line        = line.rstrip()
            line        = line.split(',')
            e_no        = int(line[0])
            lambda_f_i4 = float(line[1])
            lambda_f_i6 = float(line[2])
            lambda_f__ri4 = float(line[3])
            lambda_f_r_i6 = float(line[4])
            lambda_t_i4 = float(line[5])
            lambda_t_i6 = float(line[6])

            fibro_stretch_dictionary[e_no] = [lambda_f_i4, lambda_f_i6, lambda_f__ri4, lambda_f_r_i6, lambda_t_i4,
                                              lambda_t_i6]

    f_file.close()

    return fibro_stretch_dictionary


def read_hgo_material_musc(filename):
    """
    Reads in a csv file containing hgo material information about a mesh
    and returns a dictionary to be further processed in a script.

    Example usage:

    .. code-block:: python

        read_hgo_material("material_values.csv")

    Args:
        filename(str): a csv file containing material information

    Returns:
        material_dictionary(dict):  dictionary structure containing all material
                                    information in one neat variable.
    """
    material_dictionary = defaultdict(list)

    # Get the step number return it and update it !
    regex = r'^step.*'

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        # Cleanly instruct the csv reader to skip the header line
        # this has been done in order to maintain a header line
        # so as to be able to understand the csv file when opened
        # manually
        next(reader)
        for row in reader:
            element_number = int(row[0])
            c1 = float(row[1])
            k1t = float(row[2])
            k2t = float(row[3])
            k1m = float(row[4])
            k2m = float(row[5])
            av_x = float(row[6])
            av_y = float(row[7])
            av_z = float(row[8])
            bv_x = float(row[9])
            bv_y = float(row[10])
            bv_z = float(row[11])
            pvol = float(row[12])
            fx = float(row[13])

            material_dictionary[element_number] = [
                                                      [c1, k1t, k2t, k1m, k2m, fx], # c1, k1, k2
                                                      [av_x, av_y, av_z], # avector
                                                      [bv_x, bv_y, bv_z], # bvector
                                                      pvol, # pvol,
                                                      fx
            ]

    return material_dictionary


# Default hgo material reader without modifications for specific tissues !
def read_hgo_material_original(filename):
    """
     Reads in a csv file containing hgo material information about a mesh
     and returns a dictionary to be further processed in a script.

     Example usage:

     .. code-block:: python

         read_hgo_material("material_values.csv")

     Args:
         filename(str): a csv file containing material information

     Returns:
         material_dictionary(dict):  dictionary structure containing all material
                                     information in one neat variable.
     """
    material_dictionary = defaultdict(list)

    with open(filename, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # Cleanly instruct the csv reader to skip the header line
        # this has been done in order to maintain a header line
        # so as to be able to understand the csv file when opened
        # manually
        next(reader)

        for row in reader:
            element_number = int(row[0])
            c1 = float(row[1])
            k1 = float(row[2])
            k2 = float(row[3])
            k3 = float(row[4])
            k4 = float(row[5])
            av_x = float(row[6])
            av_y = float(row[7])
            av_z = float(row[8])
            bv_x = float(row[9])
            bv_y = float(row[10])
            bv_z = float(row[11])
            pvol = float(row[12])
            material_dictionary[element_number] = [
                [c1, k1, k2, k3, k4],  # c1, k1, k2
                [av_x, av_y, av_z],  # avector
                [bv_x, bv_y, bv_z],  # bvector
                pvol,
            ]

    return material_dictionary

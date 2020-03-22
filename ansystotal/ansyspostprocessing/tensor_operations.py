import math
from collections import defaultdict

import numpy as np
from scipy.linalg import expm

import ansystotal.ansyspreprocessing.ansys_file_reader as afr


def create_invariant_dictionaries(mat_props=defaultdict, hencky_strain_dict=defaultdict):
    """
    Calculate i4 for each element provided the green strain dictionary as the input.
    The resultant dictionary contains the values for i4 for each individual element.

    Example usage:
	
    .. code-block:: python

       create_I_4_tensor_dict(gs_dictionary)

    Args:
	
        mat_props (defaultdict): provide the dictionary with material values
        hencky_strain_dict (defaultdict) : Dictionary containing average hencky strain tensor for each element.
		
    Returns:
	
        i4_dictionary (defaultdict): the value of i4 for each element is returned as a dictionary data structure
        as follows - {el_no: i4_value}

    """
    # Read in the material properties from the excel sheet

    # Instead of this get in the avec and bvec !!!
    I_4_dictionary = defaultdict()
    I_6_dictionary = defaultdict()

    # Convert the unit vectors into spherical co-ordinates
    # As RSYS, 2 has been activated therefore, there should be consistency in the
    # way the FEM results and the fibre vectors interact in the same co-ordinate system
    for element_number, g_strain_tensor in hencky_strain_dict.items():
        a_0_1 = mat_props[element_number][1]
        a_0_2 = mat_props[element_number][2]

        # a_0_1 = cart2sph(a_0_1)
        # a_0_2 = cart2sph(a_0_2)
        # Calculate the Cauchy Stress tensor.
        u_tensor, c_tensor  = hencky_strain_transformations(g_strain_tensor)

        I_4                 = calculate_invariants(c_tensor, a_0_1)
        I_6                 = calculate_invariants(c_tensor, a_0_2)
        I_4_dictionary[element_number] = I_4
        I_6_dictionary[element_number] = I_6

    return I_4_dictionary, I_6_dictionary

def cart2sph(vector):

    x = vector[0]
    y = vector[1]
    z = vector[2]

    XsqPlusYsq = x**2 + y**2
    r    = math.sqrt(XsqPlusYsq + z**2)
    theta = math.atan2(z,x)
    phi = math.atan2(r,y)

    # if y == 0:
    #     theta = np.pi

    # r   = 0
    # phi = 0

    return [r, theta, phi]

def create_i4_dictionary_musc(filename, hencky_strain_dict):
    """
    Calculate i4 for each element provided the green strain dictionary as the input.
    The resultant dictionary contains the values for i4 for each individual element.

    Example usage:
	
    .. code-block:: python

       create_I_4_tensor_dict(gs_dictionary)

    Args:
	
        filename (str): Provide the file containing the material properties for a current geometry.
        hencky_strain_dict (defaultdict) : Dictionary containing average hencky strain tensor for each element.
		
    Returns:
	
        i4_dictionary (defaultdict): the value of i4 for each element is returned as a dictionary data structure
        as follows - {el_no: i4_value}

    """
    # Read in the material properties from the excel sheet
    mat_props = afr.read_hgo_material_musc(filename)
    I_4_dictionary = defaultdict()
    I_6_dictionary = defaultdict()

    for element_number, g_strain_tensor in hencky_strain_dict.items():

        #
        a_0_1 = mat_props[element_number][1]
        a_0_2 = mat_props[element_number][2]

        # Calculate the Cauchy Stress tensor.
        u_tensor, c_tensor  = hencky_strain_transformations(g_strain_tensor)
        I_4                 = calculate_invariants(c_tensor, a_0_1)
        I_6                 = calculate_invariants(c_tensor, a_0_2)
        I_4_dictionary[element_number] = I_4
        I_6_dictionary[element_number] = I_6

    return I_4_dictionary, I_6_dictionary


# Functions to get basic quantities out
# For the functions below ! just do manual coding ma dude
def hencky_strain_transformations(hencky_strain_tensor):

    """
    Type in what hencky strain tensor it takes you idiot

    :param hencky_strain_tensor:
    :return u_tensor, c_tensor:
    """
    # Hencky strain is defined as:
    # h = ln(U)
    # therefore, U = exp(h)

    u_tensor = expm(np.matrix(hencky_strain_tensor))

    c_tensor = np.linalg.matrix_power(u_tensor, 2) # U^2

    return u_tensor, c_tensor

def calculate_invariants(cauchy_green_tensor, a_0_x):

    np_a_0_x = np.matrix(a_0_x)

    A = np.outer(np_a_0_x, np_a_0_x)

    np_cauchy_green_tensor = np.matrix(cauchy_green_tensor)

    invariant = np.tensordot(np_cauchy_green_tensor, A)

    #
    # rhs = np.matmul(np_cauchy_green_tensor, np.transpose(np_a_0_x))
    #
    # invariant = np.matmul(np_a_0_x, rhs)
    #

    return invariant
#
def calculate_aniso_stresses(k_num, k_den, invariant):

    if invariant > 1:
        # 2 * I4(i) * (I4(i) - 1) * k1_I4(i) * exp(k2_I4(i) * (I4(i) - 1) ^ 2);
        cauchy_stress = 2 * invariant * k_num * (invariant - 1) * (math.exp(k_den * (invariant - 1) ** 2))
        pk_stress = cauchy_stress / math.sqrt(invariant)

    else:
        cauchy_stress = 0
        pk_stress = 0

    return pk_stress, cauchy_stress

if __name__ == '__main__':

    # For getting variables in the variables screen

    hencky_strain_tensor = [[-0.070741, 0.0, 0.0], [0.0, -0.070741, 0.0], [0.0, 0.0, 0.7113199999999998]]
    hencky_strain_tensor = [
        [-0.27, 0, 0],
        [0 , 0.14, 0],
        [0, 0,0.14]
    ]

    u_tensor, c_tensor = hencky_strain_transformations(hencky_strain_tensor)

    i4 = calculate_invariants(c_tensor, [0,0,1])

    pk_stress, cauchy_stress = calculate_aniso_stresses(0.132e-2, 2.0, i4)

    print("Invariant_4: ", i4)
    print("Cauchy Stress(kPa): ",  cauchy_stress)

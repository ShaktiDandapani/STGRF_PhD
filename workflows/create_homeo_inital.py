# Necessary File ! - just need to call into the perl script run it to create the
# "updated_homeo.csv"
# Collagen fibre stress only !
from collections import defaultdict
import csv
import ansystotal.ansyspreprocessing.ansys_file_reader as afr
import ansystotal.ansyspostprocessing.tensor_operations as to

def read_updated_homeo_file(filename):

    curr_homeo_value_dict = defaultdict()

    with open(filename, 'r') as uphome_file:
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


material_homeostatic_step_file = "material_values_0.csv"
strain_homeostatic_step_file = "strain_list_0.txt"


hencky_strains_home = afr.read_strain_output(strain_homeostatic_step_file)

material_values_dict_home = afr.read_hgo_material(material_homeostatic_step_file)

i4_dict_home, i6_dict_home = to.create_invariant_dictionaries(material_values_dict_home, hencky_strains_home)
updated_homeo_stress = defaultdict()
# Calculate the stresses
for e_no, values in material_values_dict_home.items():
    k1_home = values[0][1]
    k2_home = values[0][2]
    k3_home = values[0][3]
    k4_home = values[0][4]
    i4_homeo = i4_dict_home[e_no]
    i6_homeo = i6_dict_home[e_no]

    an_pk_home_i4, an_cauchy_home_i4 = to.calculate_aniso_stresses(k1_home, k2_home, i4_homeo)
    an_pk_home_i6, an_cauchy_home_i6 = to.calculate_aniso_stresses(k3_home, k4_home, i6_homeo)

    updated_homeo_stress[e_no] = [an_cauchy_home_i4, an_cauchy_home_i6]

write_updated_homeo_file("updated_homeo.csv", updated_homeo_stress)


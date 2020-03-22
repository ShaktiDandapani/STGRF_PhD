from collections import defaultdict
import math

import ansystotal.genericoperations.gr_commands as grc
import ansystotal.ansyspreprocessing.ansys_file_reader as afr
import ansystotal.ansyspostprocessing.tensor_operations as to
import ansystotal.genericoperations.generic_commands as gc

# Testing a commit
root_dir       = gc.return_read_root_directory_name('./parameters/directories_information.dat')
root_dir_myo   = root_dir['myocardium']
#root_dir_cube   = root_dir['cube']
#root_dir_strip    = root_dir['uni_strip']

e_reader       = afr.ListReader()
strain_file    = './strain_list_0.txt'
materials_file = './material_values_0.csv'
elements_file  = root_dir_myo + "/elist.dat"
fibro_fname    = "./fibroblast_info_0.csv"

fibroblast_homeo_stretch_i4 = 1.05
fibroblast_homeo_stretch_i6 = 1.05

element_dict = e_reader.read_elements(elements_file)
h_strain_dict = afr.read_strain_output(strain_file)
materials_dict = afr.read_hgo_material(materials_file)
i4_dict, i6_dict = to.create_invariant_dictionaries(materials_dict, h_strain_dict)

fibr_stretch_dict = defaultdict(list)

for element_number in element_dict.keys():
    tissue_stretch_i4 = math.sqrt(i4_dict[element_number])
    tissue_stretch_i6 = math.sqrt(i6_dict[element_number])

    # depending on whats greater we place that to be the driving mechanobiological force for
    # remodelling  !
    fibroblast_rec_stretch_i4 = tissue_stretch_i4 / fibroblast_homeo_stretch_i4
    fibroblast_rec_stretch_i6 = tissue_stretch_i6 / fibroblast_homeo_stretch_i6

    fibr_stretch_dict[element_number] = [fibroblast_homeo_stretch_i4, fibroblast_homeo_stretch_i6,
                                         fibroblast_rec_stretch_i4, fibroblast_rec_stretch_i6,
                                         tissue_stretch_i4, tissue_stretch_i6]

grc.write_fibrobast_file(fibro_fname, fibr_stretch_dict)

# type it out
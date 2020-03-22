import ansystotal.ansyspreprocessing.ansys_file_reader as afr
import ansystotal.genericoperations.centroid_fibre_gen as cfg

from collections import defaultdict

def create_myocardium_materials_file(material_fname, material_dictionary):

    """
    These methods would be used on execution of the HGO STGRF framework,
    Particularly, writing a file for ansys and muscle based on th values
    required for simulation apart from the standard HGO model parameters.

    :param filename:
    :param material_fname:
    :param material_dictionary:
    :return:
    """

    with open(material_fname, 'w') as m_file:

        m_file.write("e_no,c,k1,k2,k3,k4,ax,ay,az,bx,by,bz,pvol,m_g,m_c\n")

        for element_number, m_values in material_dictionary.items():
            # print(element_number, m_values)
            c = m_values[0][0]
            k1 = m_values[0][1]
            k2 = m_values[0][2]
            k3 = m_values[0][3]
            k4 = m_values[0][4]
            avec_x = m_values[1][0]
            avec_y = m_values[1][1]
            avec_z = m_values[1][2]

            # Need to add to dictionary if you need to use bvec too (please just do this now in materials writer).
            bvec_x = m_values[2][0]
            bvec_y = m_values[2][1]
            bvec_z = m_values[2][2]

            vol = m_values[3]
            m_g = m_values[4][0]
            m_c_i4 = m_values[4][1]
            m_c_i6 = m_values[4][2]

            m_file.write("{e_no},{c},{k1},{k2},{k3},{k4},{ax},{ay},{az},{bx},{by},{bz},{pvol},{m_g},{m_c_i4}, {m_c_i6}\n"
                   .format(e_no=element_number, c=c, k1=k1, k2=k2, k3=k3, k4=k4, ax=avec_x, ay=avec_y, az=avec_z,
                           bx=bvec_x, by=bvec_y, bz=bvec_z, pvol=vol, m_g=m_g, m_c_i4=m_c_i4, m_c_i6=m_c_i6))


def create_material_constants():

    c  = 2.28e-2
    k1 = 132.0e-3 # MPa
    k2 = 3.45
    k3 = 132.0e-3 # MPa
    k4 = 3.45
    pvol = 0.2

    mesh_reader = afr.ListReader()
    nodes_dict  = mesh_reader.read_nodes('nlist.dat')
    elems_dict  = mesh_reader.read_elements('elist.dat')
    cents_dict  = cfg.calculate_centroids(nodes_dict, elems_dict)

    # fibre_dictionary = cfg.calculate_orthogonal_vectors(nodes_dict, elems_dict)
    fibre_dictionary = cfg.calculate_spheroid_fibres(cents_dict)
    material_dictionary = defaultdict()

    for e_no, nodes_list in elems_dict.items():
        avec = fibre_dictionary[e_no][0]
        bvec = fibre_dictionary[e_no][1]

        material_dictionary[e_no] = [
            [c, k1, k2, k3, k4],
            avec,
            bvec,
            pvol,
            [1.0, 1.0, 1.0]
        ]

    create_myocardium_materials_file("materials.dat", material_dictionary)

if __name__ == '__main__':
    create_material_constants()
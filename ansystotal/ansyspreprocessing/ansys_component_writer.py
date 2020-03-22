from collections import defaultdict

# -*- coding: utf-8 -*-
"""
Created on 18.08.2017

Class file containing methods to write out nodes, elements and material model into
respective .inp files to be used by the ansysfilewriter script.

"""

class DataWriter:

    def __init__(self):
        pass

    @staticmethod
    def write_elements(filename, elements_dict=defaultdict(list)):

        # Supply the type here or write in the type before the number of nodes...
        """
        Reads in the file_name to output the elements file to, and the element dictionary which \n
        contains the list of elements associated with the nodes as the rest of the row....

        Dictionary Format:

        [Element_number: 'n1, n2 ......... nn']

        :param filename:
        :param elements_dict:
        :return:
        """

        e_file = open(filename, "w+")
        # Element writing into the INP file

        # needs a better method to write the elements to a file, can have any number of nodes.

        # For 8 Nodes
        i = 1
        for element, nodes in elements_dict.items():
            # centroid = fg.centroidFinder()
            # print 'Current Centroid: ', centroid
            number_of_nodes = len(nodes[0])

            if number_of_nodes is 2:
                e_file.write("\nTYPE, 5")           # BEAM188
                e_file.write("MAT, %d\n" % i)
                e_file.write("E, %d, %d\n\n" % (nodes[0][0], nodes[0][1]))
                i += 1

            if number_of_nodes is 4:
                # write the element type here
                e_file.write("\nTYPE,4\n")
                e_file.write("MAT, %d\n" % i)
                e_file.write("E, %d, %d, %d, %d\n\n" % (nodes[0][0], nodes[0][1], nodes[0][2], nodes[0][3]))
                i += 1

            elif number_of_nodes is 8:
                # write the element type here
                e_file.write("\nTYPE,1\n")
                e_file.write("MAT, %d\n" % i)
                e_file.write("E, %d, %d, %d, %d, %d, %d, %d, %d \n\n" % (
                    nodes[0][0], nodes[0][1], nodes[0][2], nodes[0][3], nodes[0][4], nodes[0][5], nodes[0][6], nodes[0][7]))
                i += 1


            elif number_of_nodes is 10:
                # write the element type here
                e_file.write("\nTYPE,3\n")
                e_file.write("MAT, %d\n" % i)
                e_file.write("E, %d, %d, %d, %d, %d, %d, %d, %d\n" % (
                    nodes[0][0], nodes[0][1], nodes[0][2], nodes[0][3], nodes[0][4], nodes[0][5], nodes[0][6],
                    nodes[0][7]))
                e_file.write("\nEMORE, %d, %d" %(nodes[0][8], nodes[0][9]))
                i += 1

            elif number_of_nodes is 20:
                # write the element type here
                e_file.write("\nTYPE,2\n")
                e_file.write("MAT, %d\n" % i)
                e_file.write("\nE, %d, %d, %d, %d, %d, %d, %d, %d" % (
                    nodes[0][0], nodes[0][1], nodes[0][2], nodes[0][3], nodes[0][4], nodes[0][5], nodes[0][6],
                    nodes[0][7]))
                e_file.write("\nEMORE, %d, %d, %d, %d, %d, %d, %d, %d" %( nodes[0][8], nodes[0][9], nodes[0][10], nodes[0][11], nodes[0][12], nodes[0][13],
                    nodes[0][14], nodes[0][15]))
                e_file.write("\nEMORE, %d, %d, %d, %d\n" %(nodes[0][16], nodes[0][17], nodes[0][18], nodes[0][19]))
                i += 1

        e_file.close()

    @staticmethod
    def write_nodes(filename, nodes_dict=defaultdict(list)):
        """
        Read in the nodes information via a dictionary holding the information
        as nodes_dict = {node_number: Point(x, y, z)} and write out an input(.inp)
        file readable by the ANSYS MAPDL program.

        :param filename:
        :param nodes_dict:
        :return:
        """
        # Node Writing into the INP File
        # print(nodes_dict[1][0][0].get_x())

        with open(filename, 'w') as file:
            for node, coords in nodes_dict.items():
                file.write('\nN, {number}, {x}, {y}, {z}\n'.format
                           (number=node, x=coords[0].get_x(), y=coords[0].get_y(), z=coords[0].get_z()))

    @staticmethod
    def write_material_ahyper_expo_lv(filename, mat_values_csv_file, material_dictionary):
        """

        :param filename:
        :param mat_values_csv_file:
        :param material_dictionary:
        :return:
        """

        # print '\nThe material files now are: \n'
        # print filename, mat_values_file

        # Write these files into a .csv file as [e_no, c1, k1, k2, avec_x, avec_y, avec_z, bvec_x, bvec_y, bvec_z, vol]

        text_file = open(mat_values_csv_file, "w+")
        text_file.write(
            "ElementxNumber, c, k1, k2, k3, k4, avec_x, avec_y, avec_z, bvec_x, bvec_y, bvec_z, volume, m_ground_matrix, m_collagen_i4, m_collagen_i6\n")

        for element_number, m_values in material_dictionary.items():

            c1 = m_values[0][0]
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

            m_gm    = m_values[4][0]
            m_c_i4  = m_values[4][1]
            m_c_i6  = m_values[4][2]

            # print(avec_x, avec_y, avec_z, bvec_x, bvec_y, bvec_z)
            text_file.write("{el_no}, {c1}, {k1}, {k2}, {k3}, {k4}, {avec_x}, {avec_y}, "
                            "{avec_z}, {bvec_x}, {bvec_y}, {bvec_z}, {vol}, {m_gm}, {m_c_i4}, {m_c_i6} \n" \
                            .format(el_no=element_number, c1=c1, k1=k1, k2=k2, k3=k3, k4=k4,
                                    avec_x=avec_x, avec_y=avec_y, avec_z=avec_z, bvec_x=bvec_x,
                                    bvec_y=bvec_y, bvec_z=bvec_z, vol=vol, m_gm=m_gm, m_c_i4=m_c_i4, m_c_i6=m_c_i6))

        text_file.close()

        f_file = open(filename, "w+")

        for element_number, m_values in material_dictionary.items():
            # print element_number, fibresPos

            c1 = m_values[0][0]
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


            f_file.write('\nTB, AHYPER, %d, , , EXPO \n' % element_number)
            f_file.write('TBDATA, 1, %f, 0, 0, 0, 0, 0 \n' % c1)
            f_file.write('TBDATA, 7, %f, %f, %s, %f\n' % (k1, k2, k3, k4))
            f_file.write('TB, AHYPER, %d, , , PVOL \n' % element_number)
            f_file.write('TBDATA, , %f \n' % vol)

            f_file.write('TB, AHYPER, %d, , , AVEC \n' % element_number)
            f_file.write('TBDATA, , %f, %f, %f \n' % (avec_x, avec_y, avec_z))
            f_file.write('TB, AHYPER, %d, , , BVEC \n' % element_number)
            f_file.write('TBDATA, , %f, %f, %f \n' % (bvec_x, bvec_y, bvec_z))


        f_file.close()

    @staticmethod
    def write_material_ahyper_expo_musc(filename, mat_values_csv_file, material_dictionary):
        """

        :param filename:            'materials.inp'
        :param mat_values_csv_file: 'material_values_*.csv'
        :param material_dictionary: new_materials
        :return:
        """

        # print '\nThe material files now are: \n'
        # print filename, mat_values_file

        # Write these files into a .csv file as [e_no, c1, k1, k2, avec_x, avec_y, avec_z, bvec_x, bvec_y, bvec_z, vol]

        text_file = open(mat_values_csv_file, "w+")
        text_file.write("e_no,c,k1t,k2t,k1m,k2m,ax,ay,az,bx,by,bz,pvol,fx\n")

        for element_number, m_values in material_dictionary.items():
            c1      = m_values[0][0]
            k1t     = m_values[0][1]
            k2t     = m_values[0][2]
            k1m     = m_values[0][3]
            k2m     = m_values[0][4]
            avec_x  = m_values[1][0]
            avec_y  = m_values[1][1]
            avec_z  = m_values[1][2]
            bvec_x  = m_values[2][0]
            bvec_y  = m_values[2][1]
            bvec_z  = m_values[2][2]
            vol     = m_values[3]
            fx      = m_values[4]

            text_file.write("%d, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n" % (
                element_number, c1, k1t, k2t, k1m, k2m, avec_x, avec_y, avec_z, bvec_x, bvec_y, bvec_z, vol,
                fx))

        text_file.close()

        f_file = open(filename, "w+")
        for element_number, m_values in material_dictionary.items():
            # print element_number, fibresPos

            c1      = m_values[0][0]
            k1t     = m_values[0][1]
            k2t     = m_values[0][2]
            k1m     = m_values[0][3]
            k2m     = m_values[0][4]
            avec_x  = m_values[1][0]
            avec_y  = m_values[1][1]
            avec_z  = m_values[1][2]
            bvec_x      = m_values[2][0]
            bvec_y      = m_values[2][1]
            bvec_z      = m_values[2][2]
            # vol         = m_values[3]
            fx      = m_values[4]

            if fx == 0:

                f_file.write('\nTB, AHYPER, %s, , , EXPO \n' % element_number)
                f_file.write('TBDATA, 1, %f, 0, 0, 0, 0, 0\n' % (c1))
                f_file.write('TBDATA, 7, %f, %f, %f, %f\n' % (k1t, k2t, k1m, k2m))

                f_file.write('TB, AHYPER, %s, , , PVOL\n' % element_number)
                f_file.write('TBDATA, , 1 \n')

                f_file.write('TB, AHYPER, %s, , , AVEC\n' % element_number)
                f_file.write('TBDATA, , %f, %f, %f\n' % (avec_x, avec_y, avec_z))

                f_file.write('TB, AHYPER, %s, , , BVEC\n' % element_number)
                f_file.write('TBDATA, , %f, %f, %f\n' % (bvec_x, bvec_y, bvec_z))


            elif 0 < fx < 1:
                # k1 = k1t + k1m
                # k2 = k2t

                f_file.write('\nTB, AHYPER, %s, , , EXPO \n' % element_number)
                f_file.write('TBDATA, 1, %f, 0, 0, 0, 0, 0\n' % (c1))
                f_file.write('TBDATA, 7, %f, %f, %f, %f\n' % (k1t, k2t, k1m, k2m))

                f_file.write('TB, AHYPER, %s, , , PVOL\n' % element_number)
                f_file.write('TBDATA, , 1 \n')

                f_file.write('TB, AHYPER, %s, , , AVEC\n' % element_number)
                f_file.write('TBDATA, , %f, %f, %f\n' % (avec_x, avec_y, avec_z))

                f_file.write('TB, AHYPER, %s, , , BVEC\n' % element_number)
                f_file.write('TBDATA, , %f, %f, %f\n' % (bvec_x, bvec_y, bvec_z))

            elif fx == 1:

                f_file.write('\nTB, AHYPER, %s, , , EXPO \n' % element_number)
                f_file.write('TBDATA, 1, %f, 0, 0, 0, 0, 0\n' % (c1))
                f_file.write('TBDATA, 7, %f, %f, %f, %f\n' % (k1t, k2t, k1m, k2m))

                f_file.write('TB, AHYPER, %s, , , PVOL\n' % element_number)
                f_file.write('TBDATA, , 1 \n')

                f_file.write('TB, AHYPER, %s, , , AVEC\n' % element_number)
                f_file.write('TBDATA, , %f, %f, %f\n' % (avec_x, avec_y, avec_z))

                f_file.write('TB, AHYPER, %s, , , BVEC\n' % element_number)
                f_file.write('TBDATA, , %f, %f, %f\n' % (bvec_x, bvec_y, bvec_z))

        f_file.close()

    @staticmethod
    def write_material_ahyper_expo_original(filename, mat_values_csv_file, material_dictionary):
        """

        :param filename:
        :param mat_values_csv_file:
        :param material_dictionary:
        :return:
        """

        # print '\nThe material files now are: \n'
        # print filename, mat_values_file

        # Write these files into a .csv file as [e_no, c1, k1, k2, avec_x, avec_y, avec_z, bvec_x, bvec_y, bvec_z, vol]

        text_file = open(mat_values_csv_file, "w+")
        text_file.write(
            "ElementxNumber, c, k1, k2, k3, k4, avec_x, avec_y, avec_z, bvec_x, bvec_y, bvec_z, volume\n")

        for element_number, m_values in material_dictionary.items():
            c1 = m_values[0][0]
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

            # print(avec_x, avec_y, avec_z, bvec_x, bvec_y, bvec_z)
            text_file.write("{el_no}, {c1}, {k1}, {k2}, {k3}, {k4}, {avec_x}, {avec_y}, "
                            "{avec_z}, {bvec_x}, {bvec_y}, {bvec_z}, {vol}\n" \
                            .format(el_no=element_number, c1=c1, k1=k1, k2=k2, k3=k3, k4=k4,
                                    avec_x=avec_x, avec_y=avec_y, avec_z=avec_z, bvec_x=bvec_x,
                                    bvec_y=bvec_y, bvec_z=bvec_z, vol=vol))

        text_file.close()

        f_file = open(filename, "w+")

        for element_number, m_values in material_dictionary.items():
            # print element_number, fibresPos

            c1 = m_values[0][0]
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

            f_file.write('\nTB, AHYPER, %d, , , EXPO \n' % element_number)
            f_file.write('TBDATA, 1, %f, 0, 0, 0, 0, 0 \n' % c1)
            f_file.write('TBDATA, 7, %f, %f, %s, %f\n' % (k1, k2, k3, k4))
            f_file.write('TB, AHYPER, %d, , , PVOL \n' % element_number)
            f_file.write('TBDATA, , %f \n' % vol)

            f_file.write('TB, AHYPER, %d, , , AVEC \n' % element_number)
            f_file.write('TBDATA, , %f, %f, %f \n' % (avec_x, avec_y, avec_z))
            f_file.write('TB, AHYPER, %d, , , BVEC \n' % element_number)
            f_file.write('TBDATA, , %f, %f, %f \n' % (bvec_x, bvec_y, bvec_z))

        f_file.close()



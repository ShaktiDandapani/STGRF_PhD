
import numpy as np 
import matplotlib.pyplot as plt

import ansystotal.genericoperations.mesh_information_structures as mis
import ansystotal.ansyspreprocessing.ansys_file_reader as afr 
import ansystotal.genericoperations.centroid_fibre_gen as cfg

def cube_face_normals_inner():

    reader_object = afr.ListReader() 
    nodes = reader_object.read_nodes('nlist.dat')
    elements = reader_object.read_elements('elist.dat')

    # The co ordinates associated to identify the sides
    # are from the centroid co-ordinates of each face 

    # Counter clockwise node number arrangement - outward normals

    # ss1 - left side 
    # ss2 - right_side

    ax = plt.axes(projection='3d')

    for e_no, nodes_list in elements.items():
        lnode_1 = int(nodes_list[0][0]) # 2
        lnode_2 = int(nodes_list[0][1]) # 4
        lnode_3 = int(nodes_list[0][2]) # 3
        lnode_4 = int(nodes_list[0][3]) # 1
        lnode_5 = int(nodes_list[0][4]) # 5
        lnode_6 = int(nodes_list[0][5]) # 6
        lnode_7 = int(nodes_list[0][6]) # 7
        lnode_8 = int(nodes_list[0][7]) # 8

        node_2 = nodes[lnode_1][0]
        node_4 = nodes[lnode_2][0]
        node_3 = nodes[lnode_3][0]
        node_1 = nodes[lnode_4][0]
        node_5 = nodes[lnode_5][0]
        node_6 = nodes[lnode_6][0]
        node_7 = nodes[lnode_7][0]
        node_8 = nodes[lnode_8][0]
        nodes_test_list = [ node_2, node_4, node_3, node_1, node_5, node_6, node_7, node_8]

        side_a = [node_1, node_3, node_7, node_8]
        side_b = [node_2, node_4, node_5, node_6]
        side_c = [node_1, node_2, node_5, node_8]
        side_d = [node_3, node_4, node_6, node_7]
        side_e = [node_1, node_2, node_3, node_4]
        side_f = [node_5, node_6, node_7, node_8]
        element_full = [node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8]

        # Find the centroids and store them as a Point object 
        # This goes in the for loop as the element number will change for the number of elemnts in the
        # mesh

        # using the sides calculate the centroids

        element_centroid = cfg.centroid_finder(element_full)
        side_a_cent = cfg.centroid_finder(side_a)
        side_b_cent = cfg.centroid_finder(side_b)
        side_c_cent = cfg.centroid_finder(side_c)
        side_d_cent = cfg.centroid_finder(side_d)
        side_e_cent = cfg.centroid_finder(side_e)
        side_f_cent = cfg.centroid_finder(side_f)

        # using the min max of x y z co-ordinates delineate the different faces of the cube

        sa_centroid = mis.Point(side_a_cent[0], side_a_cent[1], side_a_cent[2])
        sb_centroid = mis.Point(side_b_cent[0], side_b_cent[1], side_b_cent[2])
        sc_centroid = mis.Point(side_c_cent[0], side_c_cent[1], side_c_cent[2])
        sd_centroid = mis.Point(side_d_cent[0], side_d_cent[1], side_d_cent[2])
        se_centroid = mis.Point(side_e_cent[0], side_e_cent[1], side_e_cent[2])
        sf_centroid = mis.Point(side_f_cent[0], side_f_cent[1], side_f_cent[2])

        side_centroids = [sa_centroid, sb_centroid, sc_centroid, sd_centroid, se_centroid, sf_centroid]
        #

        normal_dir_vec = mis.LineSegment(sa_centroid, sb_centroid)
        sheet_dir_vec  = mis.LineSegment(sc_centroid, sd_centroid)
        fibre_dir_vec  = mis.LineSegment(se_centroid, sf_centroid)

        # Store in a dictionary for fibres or avec bvec as implemnented before : )
        sdir_unit_vec = normal_dir_vec.get_unit_vector()
        ndir_unit_vec = sheet_dir_vec.get_unit_vector()
        fdir_unit_vec = fibre_dir_vec.get_unit_vector()


        # Code below uncomment to plot the element vector
        # Get both the unit vectors for the two directions in each case
        # select as appropriate

        point_list = [sa_centroid, sb_centroid, se_centroid, sf_centroid,  sc_centroid, sd_centroid ]

        x = []
        y = []
        z = []
        xe = []
        ye = []
        ze = []

        for point in point_list:
            x.append(point.get_x())
            y.append(point.get_y())
            z.append(point.get_z())

        for pt in element_full:
            xe.append(pt.get_x())
            ye.append(pt.get_y())
            ze.append(pt.get_z())


        ax.scatter(x, y, z, '.')
        ax.scatter(xe, ye, ze, color='r')

        ax.set_xlabel('X - Axis')
        ax.set_ylabel('Y - Axis')
        ax.set_zlabel('Z - Axis')

        # # plotting fibres to element centroid
        # r = np.array(x, dtype=np.float)
        # s = np.array([float(i) for i in y])
        # t = np.array(z) * 1.0
        # print(r, x)
        # print(s, y)
        # print(t, z)

        # for x, y, z in zip(x, y, z):
        #     ax.plot3D([x, element_centroid[0]], [y, element_centroid[1]], [z, element_centroid[2]], '--', color='k')

        # Lengthy code for all the edges of the cube
        xt = np.linspace(node_1.get_x(), node_2.get_x(), 10)
        yt = np.linspace(node_1.get_y(), node_2.get_y(), 10)
        zt = np.linspace(node_1.get_z(), node_2.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_4.get_x(), node_2.get_x(), 10)
        yt = np.linspace(node_4.get_y(), node_2.get_y(), 10)
        zt = np.linspace(node_4.get_z(), node_2.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_5.get_x(), node_2.get_x(), 10)
        yt = np.linspace(node_5.get_y(), node_2.get_y(), 10)
        zt = np.linspace(node_5.get_z(), node_2.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_1.get_x(), node_3.get_x(), 10)
        yt = np.linspace(node_1.get_y(), node_3.get_y(), 10)
        zt = np.linspace(node_1.get_z(), node_3.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_1.get_x(), node_8.get_x(), 10)
        yt = np.linspace(node_1.get_y(), node_8.get_y(), 10)
        zt = np.linspace(node_1.get_z(), node_8.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_5.get_x(), node_8.get_x(), 10)
        yt = np.linspace(node_5.get_y(), node_8.get_y(), 10)
        zt = np.linspace(node_5.get_z(), node_8.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_5.get_x(), node_6.get_x(), 10)
        yt = np.linspace(node_5.get_y(), node_6.get_y(), 10)
        zt = np.linspace(node_5.get_z(), node_6.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_7.get_x(), node_8.get_x(), 10)
        yt = np.linspace(node_7.get_y(), node_8.get_y(), 10)
        zt = np.linspace(node_7.get_z(), node_8.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_7.get_x(), node_3.get_x(), 10)
        yt = np.linspace(node_7.get_y(), node_3.get_y(), 10)
        zt = np.linspace(node_7.get_z(), node_3.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_7.get_x(), node_6.get_x(), 10)
        yt = np.linspace(node_7.get_y(), node_6.get_y(), 10)
        zt = np.linspace(node_7.get_z(), node_6.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_4.get_x(), node_6.get_x(), 10)
        yt = np.linspace(node_4.get_y(), node_6.get_y(), 10)
        zt = np.linspace(node_4.get_z(), node_6.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_4.get_x(), node_2.get_x(), 10)
        yt = np.linspace(node_4.get_y(), node_2.get_y(), 10)
        zt = np.linspace(node_4.get_z(), node_2.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(node_4.get_x(), node_3.get_x(), 10)
        yt = np.linspace(node_4.get_y(), node_3.get_y(), 10)
        zt = np.linspace(node_4.get_z(), node_3.get_z(), 10)
        ax.plot3D(xt, yt, zt, '-', color= 'g')

        xt = np.linspace(element_centroid[0] + ndir_unit_vec[0][0], element_centroid[0], 10)
        yt = np.linspace(element_centroid[1] + ndir_unit_vec[0][1], element_centroid[1], 10)
        zt = np.linspace(element_centroid[2] + ndir_unit_vec[0][2], element_centroid[2], 10)
        ax.plot3D(xt, yt, zt, '-', color='c')

        xt = np.linspace(element_centroid[0] - fdir_unit_vec[0][0], element_centroid[0], 10)
        yt = np.linspace(element_centroid[1] - fdir_unit_vec[0][1], element_centroid[1], 10)
        zt = np.linspace(element_centroid[2] - fdir_unit_vec[0][2], element_centroid[2], 10)
        ax.plot3D(xt, yt, zt, '-', color='c')
    plt.show()

    # return the 3 unit vectors, 
    # assign them as vectors for fibres :) 

if __name__ == "__main__":
    cube_face_normals_inner() 
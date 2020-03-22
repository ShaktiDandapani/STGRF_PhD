import ansystotal.ansyspostprocessing.vtk_file_writer as vfw
import ansystotal.ansyspreprocessing.ansys_file_reader as afr
import ansystotal.genericoperations.centroid_fibre_gen as cfg

from collections import defaultdict

def write_fibres_vtk(filename, centroids_dictionary, fibres_dictionary):

    no_of_centroids = len(centroids_dictionary.keys())

    print("Started Writing The Fibres file")
    with open(filename, 'w') as fib_file:
        fib_file.write("# vtk DataFile Version 2.0\n")
        fib_file.write("Fibres\n")
        fib_file.write("ASCII\n\n")

        fib_file.write("DATASET UNSTRUCTURED_GRID\n")
        fib_file.write("POINTS {} double\n".format(3 * no_of_centroids))
        # print("Number of Centroids: {}".format(no_of_centroids))

        for e_no, centroid in centroids_dictionary.items():

            centroid_x = centroid[0][0]
            centroid_y = centroid[0][1]
            centroid_z = centroid[0][2]

            avec = fibres_dictionary[e_no][0]
            bvec = fibres_dictionary[e_no][1]

            avec_x =  centroid_x - avec[0]
            avec_y =  centroid_y - avec[1]
            avec_z =  centroid_z - avec[2]

            bvec_x =  centroid_x - bvec[0]
            bvec_y =  centroid_y - bvec[1]
            bvec_z =  centroid_z - bvec[2]

            fib_file.write("{} {} {}\n".format(centroid_x, centroid_y, centroid_z))
            fib_file.write("{} {} {}\n".format(avec_x, avec_y, avec_z))
            fib_file.write("{} {} {}\n".format(bvec_x, bvec_y, bvec_z))

        # based on the logic of number of points and number of cells, and following the pattern
        # as we increase the number of points !
        total_number_of_points = 3 * no_of_centroids
        no_of_pts_by_3 = total_number_of_points / 3
        no_of_cells = int(no_of_pts_by_3 + no_of_pts_by_3)
        print(no_of_cells)

        fib_file.write("CELLS {} {}\n".format(no_of_cells, 3* no_of_cells))

        for i in range(int(no_of_cells/2)):
            centroid_index = i*3
            fib_file.write("2 {} {}\n".format(centroid_index, centroid_index + 1))
            fib_file.write("2 {} {}\n".format(centroid_index, centroid_index + 2))


        fib_file.write("\nCELL_TYPES {}\n".format(no_of_cells))

        for _ in range(int(no_of_cells)):
            fib_file.write("{}\n".format(3))

    print("Done")
    return 1

# This goes into the generic commands (as it is just a specific version of material reader)
def read_fibres(materials_file):

    read_hgo_mat = afr.read_hgo_material_musc(materials_file)
    
    fibres_dictionary = defaultdict() 

    for e_no, mat_values in read_hgo_mat.items(): 
        avec = mat_values[1]
        bvec = mat_values[2]
        fibres_dictionary[e_no] = [avec, bvec]

    return fibres_dictionary

def create_mesh():

    reader_object = afr.ListReader() 
    mesh_data = defaultdict()

    nodes = reader_object.read_nodes('nlist.dat')
    elems = reader_object.read_elements('elist.dat')

    fibres = read_fibres("material_values_0.csv")

    centroids = cfg.calculate_centroids(nodes, elems)

    mesh_data['nodes'] = nodes
    mesh_data['elements'] = elems

    # Write VTK file
    vtk_writer = vfw.VTKFileWriter(mesh_data)
    vtk_writer.create_hexahedral_mesh("test_mesh.vtk")

    # This goes into the vtk file writer module
    write_fibres_vtk("test_fibres.vtk", centroids, fibres)

    return 1

if __name__ == '__main__':
    create_mesh()
import ansystotal.genericoperations.mesh_information_structures as mis


def obtain_normals(element: dict):
    element_number = element.keys()
    nodes = element.values()

    # nodes would be of class point

    # elements would be of class polyhedron

    pass

def method_trial():

    origin = mis.Point(0.0, 0.0, 0.0, 'O')
    test_centroid = mis.Point(3, 2.7, 10, 'A')

    print(test_centroid.spherical_coords)
    test_centroid.calculate_spherical_co_ordinates()
    print(test_centroid.spherical_coords)




if __name__ == '__main__':
    method_trial()
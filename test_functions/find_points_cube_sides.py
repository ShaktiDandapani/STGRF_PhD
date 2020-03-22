# Test a sample
# give a few points
# based on max x y and z
# assign respective tags :D
import ansystotal.genericoperations.mesh_information_structures as mis
from collections import defaultdict


# function taking in the points list as an input

def find_face_centroids(points_list):
    cube_faces = defaultdict()

    max_x = points_list[0].get_x()
    min_x = points_list[0].get_x()
    max_y = points_list[0].get_y()
    min_y = points_list[0].get_y()
    max_z = points_list[0].get_z()
    min_z = points_list[0].get_z()

    # max_x_node = ''  # Right Face
    # min_x_node = ''  # Left Face
    # max_y_node = ''  # Upper Face
    # min_y_node = ''  # Lower Face
    # max_z_node = ''  # Back Face
    # min_z_node = ''  # Front Face

    for point in points_list:
        if point.get_x() > max_x:
            max_x = point.get_x()
            max_x_node = point.get_label()
            cube_faces['right_face'] = max_x_node

        if point.get_x() < min_x:
            min_x = point.get_x()
            min_x_node = point.get_label()
            cube_faces['left_face'] = min_x_node

        if point.get_y() > max_y:
            max_y = point.get_y()
            max_y_node = point.get_label()
            cube_faces['upper_face'] = max_y_node

        if point.get_y() < min_y:
            min_y = point.get_y()
            min_y_node = point.get_label()
            cube_faces['lower_face'] = min_y_node

        if point.get_z() > max_z:
            max_z = point.get_z()
            max_z_node = point.get_label()
            cube_faces['back_face'] = max_z_node

        if point.get_z() < min_z:
            min_z = point.get_z()
            min_z_node = point.get_label()
            cube_faces['front_face'] = min_z_node



    # print("Right Face {}: {}".format(max_x, cube_faces['right_face']))
    # print("Left Face  {}: {}".format(min_x, cube_faces['left_face']))
    # let the dictionary be cube_faces = {'max_x': 'label'}
    # max = max(x.get_x() for x in points_list)
    # print(max)
    return cube_faces

if __name__ == '__main__':
    p1 = mis.Point(1.4, -4.1, 0.5, '1')
    p2 = mis.Point(6.5, -10, 5, '2')
    p3 = mis.Point(1.5, 0.2, 1.1, '3')
    p4 = mis.Point(-3.2, 1.2, -5.1, '4')

    pts_list = [p1, p2, p3, p4]

    find_face_centroids(pts_list)

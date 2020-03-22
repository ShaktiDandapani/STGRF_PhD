import numpy as np
import ansystotal.genericoperations.mesh_information_structures as mis

def rotate_vector(vector: np.array, angle: float):

    y_axis = mis.Point(0.0, 1.0, 0.0, 'Y-Axis')

    temp_vector = mis.Point(vector[0], vector[1], vector[2])
    final_vector = vector


    angle_r, angle_d = mis.calculate_vectors_angle(temp_vector, y_axis)
    print(angle_r, angle_d)


    return final_vector


if __name__ == '__main__':
    point_1 = np.array([1.6, 1.8, 0.0])
    point_2 = np.array([2.4, -3.6, 0.0])
    vector = np.subtract(point_2, point_1)
    print(vector)
    final_vector = rotate_vector(vector, 115)



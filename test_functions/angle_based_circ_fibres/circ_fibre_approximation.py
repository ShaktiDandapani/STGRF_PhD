import numpy as np

def calculate_angle_from_x_axis(vector):

    if not isinstance(vector, np.ndarray):
        vector = np.array(vector)

    # Note all in terms of unit_vectors
    x_axis = np.array([1.0, 0.0, 0.0])
    x_axis_tangent = np.array([0.0, 1.0, 0.0])
    # we consider the x-z co-ordinate plane,
    # i.e rotation around the Y-axis

    # theta = 0 # just dot tan-1(z/x) for x-z plane ma dude
    numerator = np.dot(vector, x_axis)
    denominator = np.linalg.norm(vector * x_axis)
    theta = numerator / denominator
    ratio = numerator / denominator
    angle_rad = np.arccos(ratio)
    angle_deg = np.arccos(ratio) * 180 / np.pi

    theta = angle_rad 
    print(ratio, numerator, denominator, np.linalg.norm(vector))

    rotation_matrix = np.matrix([[np.cos(theta), 0, -np.sin(theta)],
                                 [0, 1, 0], 
                                [np.sin(theta),0,  np.cos(theta)]])

    print(rotation_matrix)

    # rotated_tangent = np.matrix_product(rotation_matrix, x_axis_tangent)
    rotated_tangent = rotation_matrix.dot(x_axis_tangent)

    print(rotated_tangent)

    pass 

calculate_angle_from_x_axis(np.array([0.0, 1.0, 2.0]))
import numpy as np

c_tensor = [[1.1, 0.0, 0.0],
            [0.0, 0.6, 0.0],
            [0.0, 0.0, 0.2]]

c_tensor = np.matrix(c_tensor)

a_unit_vector = [0.45, -0.9, 0.3]

a_unit_vector = np.matrix(a_unit_vector)


inv_4 = a_unit_vector * np.matmul(c_tensor, np.transpose(a_unit_vector))

print(inv_4)
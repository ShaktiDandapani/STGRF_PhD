from abc import ABC, abstractmethod
import numpy as np

class Point:
    """
    A class to define points in 3D vector space.
    """
    def __init__(self, x: float=None, y: float=None, z: float=None, label: str=None):
        """
        None indicates an empty point declaration
        """
        self.x = x
        self.y = y
        self.z = z
        self.spherical_coords = None
        self.label = label


    def get_point(self):
        """
        Returns the point as a numpy array.

        :return:
        """
        # Compare both labels as str so that it does
        # not clash with other data type while assigning
        # different types of labels to a node

        point = np.array((self.x, self.y, self.z))

        return point

        # if no point is returned return -1
    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z

    def get_label(self):
        return self.label

    def calculate_spherical_co_ordinates(self):

        r = np.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        theta = np.arctan(self.y / self.x)
        phi = np.arctan(np.sqrt(self.x ** 2 + self.y ** 2) / self.z)

        self.spherical_coords = (r, theta, phi)


    def get_cylindrical_co_ordinates(self):
        pass

    def calculate_distance(self, point_new: 'Point'):

        # Both are numpy arrays
        p1 = self.get_point()
        p2 = point_new.get_point()

        return np.linalg.norm(p1 - p2)

class LineSegment:
    """
    A class to define line segments given two end points.
    """

    def __init__(self, point_1: Point, point_2: Point):

        if type(point_1) != Point and type(point_2) != Point:
            print("Not a valid Point Class Object")

        self.point_1 = point_1
        self.point_2 = point_2

    def calculate_length(self):
        """
        Calculate the length of the line segment

        :return:
        """
        self.length = np.linalg.norm(self.point_1.get_point() - self.point_2.get_point())

        return self.length

    def calculate_angle(self, line: 'LineSegment'):
        """
        Calculate the angles between two line segments
        :param line:
        :return:
        """

        pass

    def get_vertices(self):

        vertices = (self.point_1, self.point_2)

        return vertices

    def get_unit_vector(self, label: str=None):

        # based on dirn you can get the unit vector
        unit_vector_dir_1 = (self.point_1.get_point() - self.point_2.get_point())   / self.calculate_length()
        unit_vector_dir_2 = (self.point_2.get_point() - self.point_1.get_point())   / self.calculate_length()

        d1_x = unit_vector_dir_1[0]
        d1_y = unit_vector_dir_1[1]
        d1_z = unit_vector_dir_1[2]

        d2_x = unit_vector_dir_2[0]
        d2_y = unit_vector_dir_2[1]
        d2_z = unit_vector_dir_2[2]

        unit_vec_d1 = Point(d1_x, d1_y, d1_z, label)
        unit_vec_d2 = Point(d2_x, d2_y, d2_z, label)

        return unit_vec_d1, unit_vec_d2

class Element(ABC):
    """
    This class can utilise the Line class to represent
    polygons of n sides n > 4. This can be the base abstract class
    and subclasses can be spawn (eq: Tetrahedron, Cube, Square etc)

    """

    def __init__(self, sides, number_of_sides, label):
        self.sides = sides
        self.number_of_sides = number_of_sides
        self.label = label


    @abstractmethod
    def calculate_volume(self):

        pass

    # @abstractmethod
    def calculate_normals(self):

        pass 

    pass

class Hexahedron(Element):

    def __init__(self, nodes, number_of_sides, label):
        super(Hexahedron, self).__init__(nodes, number_of_sides, label)
        # check number of sides
        if number_of_sides == 6:
            self.number_of_sides = number_of_sides
        else:
            print('Incorrect number of sides')
            raise ValueError

        if (isinstance(node, Point) for node in nodes):
            self.nodes = nodes
        else:
            print('Nodes must be of datatype: {}'.format(Point))
            raise TypeError


    def calculate_volume(self):

        pass 

    def list_nodes(self):

        for node in self.nodes:
            print(node)


class Tetrahedron(Element):

    pass

# Section with only functions (can be split into a different python file)

def calculate_vectors_angle(vector_1: Point, vector_2: Point):
    """
    Calculate the angle between two vectors and return two values
    i.e. in the radians and degrees format.

    :param vector_1: Point(x, y, z)
    :param vector_2: Point(x, y, z)
    :return: angle_rad, angle_deg
    """

    cartesian_def_origin = np.array((0.0, 0.0, 0.0))

    if np.array_equal(cartesian_def_origin, vector_1.get_point()) or np.array_equal(cartesian_def_origin, vector_2.get_point()):
        return 0.0, 0.0

    numerator = np.dot(vector_1.get_point(), vector_2.get_point())
    denominator = np.linalg.norm(vector_1.get_point()) * np.linalg.norm(vector_2.get_point())

    ratio = numerator / denominator

    angle_rad = np.arccos(ratio)
    angle_deg = np.arccos(ratio) * 180 / np.pi

    return angle_rad, angle_deg


"""

This class is made in an attempt to encapsulate the entire mesh information contained for a finite element model.
Eases the passing of the mesh without explicit functions required again and again to do simple calculations, for
example the number of nodes and elements, type of the elements, mesh quality etc.

"""

class Mesh:

    def __init__(self, nodes: dict, elements: dict, centroids: dict,
                 element_type: str, material_type: str, material_properties: dict):

        """
        using element type, we can invoke the respective vtk writer to
        correctly produce outputs.
        likewise material_type -> can be used to call the correct reader and writer function
        of the material


        material_properties - this needs some sort of standardisation, as checking material type
        and the structure of the dictionary provided for the values - kind of verifying the supplied
        input is correct (testing + error checking)

        P.S. In terms of the operations done for vtk writing, reading the files etcc. can be attributed to this
             class itself and the preprocessing reader function can be encapsulated here, depending on the type
             of mesh used and in question. All the loose scripts will be under 1 name !

        :param nodes:
        :param elements:
        :param element_type:
        :param material_type:
        :param material_properties:
        """


        self.nodes = nodes
        self.elements = elements
        self.element_type = element_type
        self.material_type = material_type              # AHYPER, EXPO ?
        self.material_properties = material_properties
        self.centroids = centroids

        pass

    def get_number_of_nodes(self):

        pass

    def get_number_of_elements(self):

        pass



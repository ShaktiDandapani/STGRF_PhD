
class VTKFileWriter:

    def __init__(self, mesh_data):
        # Filename, optional argumentf for what 
        # functions described below need to be used
        self.mesh_data = mesh_data
        self.nodes    = self.mesh_data['nodes']
        self.elements = self.mesh_data['elements']
        # self.fibres   = self.mesh_data['fibres']

    def create_tetrahedral_mesh(self, filename, results):

        total_nodes = len(self.nodes.keys())
        total_elems = len(self.elements.keys())

        with open(filename, 'w') as vtk_file:
            vtk_file.write("# vtk DataFile Version 4.2 \n")

            vtk_file.write("Gastrocnemius Muscle \n")
            vtk_file.write("ASCII \n")

            vtk_file.write("DATASET UNSTRUCTURED_GRID \n\n")

            vtk_file.write("POINTS {} FLOAT \n".format(total_nodes))

            for _, coords in self.nodes.items():
                vtk_file.write("{} {} {} \n".format(coords[0].get_x(), coords[0].get_y(), coords[0].get_z()))

            vtk_file.write("CELLS {} {}\n".format(total_elems, total_elems * 5))

            for _, nodes in self.elements.items():
                # 1250 1247 1517 1517 1252 1252 1252 1252
                # 3 1 2 0 ---- 4 1 2 0 or 2 1 4 0
                vtk_file.write("4 {} {} {} {} \n".format(
                    nodes[0][0] - 1, nodes[0][2] - 1, nodes[0][3] - 1, nodes[0][1]
                ))

            vtk_file.write("CELL_TYPES {}\n".format(total_elems))

            for _ in self.elements.keys():
                vtk_file.write("10 \n")

            vtk_file.write("\nCELL_DATA {}\n".format(total_elems))

            # Every result entry in the ditionary has the format:
            # results['mechanical_quantity'] =  {e_no: value}

            for key, items in results.items():
                # key   -> name of mechanical quantity
                # items  -> element, value dictionary pair
                vtk_file.write('\nSCALARS {} float 1\n'.format(str(key)))
                vtk_file.write('LOOKUP_TABLE default\n')
                for _, value in items.items():
                    vtk_file.write("{}\n".format(float(value)))

    def create_hexahedral_mesh(self, filename):

        total_nodes = len(self.nodes.keys())
        total_elems = len(self.elements.keys())

        with open(filename, 'w') as vtk_file:

            vtk_file.write("# vtk DataFile Version 4.2 \n")
            vtk_file.write("Muscle Strip \n")
            vtk_file.write("ASCII \n")

            vtk_file.write("DATASET UNSTRUCTURED_GRID \n\n")

            vtk_file.write("POINTS {} FLOAT \n".format(total_nodes))

            for _, coords in self.nodes.items():
                vtk_file.write("{} {} {} \n".format(coords[0].get_x(), coords[0].get_y(), coords[0].get_z()))

            vtk_file.write("CELLS {} {}\n".format(total_elems, total_elems * 9))

            for _, nodes in self.elements.items():
                vtk_file.write("8 {} {} {} {} {} {} {} {} \n".format(
                    nodes[0][1] - 1, nodes[0][2] - 1, nodes[0][3] - 1, nodes[0][0] - 1, nodes[0][5] - 1, nodes[0][6] - 1,
                    nodes[0][7] - 1, nodes[0][4] - 1
                ))

            vtk_file.write("CELL_TYPES {}\n".format(total_elems))

            for _ in self.elements.keys():
                vtk_file.write("12 \n")

        return 1

    # This function takes in the mesh data and uses the create_x_mesh
    # functions to create the mesh and append the values in a values
    # table to the same vtk file or a new one in total :)

    # @abstractmethod - could be and others just extending from it


    # Probably static or separate functions for stresses/ strains etc
    def create_material_value_tables_myocardium_hexahedral(self, filename, materials):

        total_nodes = len(self.nodes.keys())
        total_elems = len(self.elements.keys())

        with open(filename, 'w') as vtk_file:

            vtk_file.write("# vtk DataFile Version 4.2 \n")
            vtk_file.write(" Left Ventricle \n")
            vtk_file.write("ASCII \n")

            vtk_file.write("DATASET UNSTRUCTURED_GRID \n\n")

            vtk_file.write("POINTS {} FLOAT \n".format(total_nodes))

            for _, coords in self.nodes.items():
                vtk_file.write("{} {} {} \n".format(coords[0].get_x(), coords[0].get_y(), coords[0].get_z()))

            vtk_file.write("\nCELLS {} {}\n".format(total_elems, total_elems * 9))

            for _, nodes in self.elements.items():
                vtk_file.write("8 {} {} {} {} {} {} {} {} \n".format(
                    nodes[0][1] - 1, nodes[0][2] - 1, nodes[0][3] - 1, nodes[0][0] - 1, nodes[0][5] - 1, nodes[0][6] - 1,
                    nodes[0][7] - 1, nodes[0][4] - 1
                ))

            vtk_file.write("\nCELL_TYPES {}\n".format(total_elems))

            for _ in self.elements.keys():
                vtk_file.write("12 \n")

            vtk_file.write("\nCELL_DATA {}\n".format(total_elems))

            # Material Parameters
            # First Quantity 
            vtk_file.write('\nSCALARS {} float 1\n'.format("c"))
            vtk_file.write('LOOKUP_TABLE default\n')
            for _, values in materials.items():
                c = values[0][0]
                vtk_file.write("{} \n".format(c))
            
            # Second quantity
            vtk_file.write('\nSCALARS {} float 1\n'.format("k1"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                k1 = values[0][1]
                vtk_file.write("{} \n".format(k1))

            # Third quantity
            vtk_file.write('\nSCALARS {} float 1\n'.format("k2"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                k2 = values[0][2]
                vtk_file.write("{} \n".format(k2))

            vtk_file.write('\nSCALARS {} float 1\n'.format("k3"))
            vtk_file.write('LOOKUP_TABLE default\n')
            for _, values in materials.items():
                k3 = values[0][3]
                vtk_file.write("{} \n".format(k3))

            vtk_file.write('\nSCALARS {} float 1\n'.format("k4"))
            vtk_file.write('LOOKUP_TABLE default\n')
            for _, values in materials.items():
                k4 = values[0][4]
                vtk_file.write("{} \n".format(k4))
            # Mass Densities 
            # Fourth quantity
            vtk_file.write('\nSCALARS {} float 1\n'.format("m_gm"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                m_gm = values[4][0]
                vtk_file.write("{} \n".format(m_gm))
                
            # Fifth quantity
            vtk_file.write('\nSCALARS {} float 1\n'.format("m_c_i4"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                m_c = values[4][1]
                vtk_file.write("{} \n".format(m_c))

            # Fifth quantity
            vtk_file.write('\nSCALARS {} float 1\n'.format("m_c_i6"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                m_c = values[4][2]
                vtk_file.write("{} \n".format(m_c))

        return 1

    # Probably static or separate functions for stresses/ strains etc
    def create_material_value_tables_muscle_hexahedral(self, filename, materials):

        total_nodes = len(self.nodes.keys())
        total_elems = len(self.elements.keys())

        with open(filename, 'w') as vtk_file:

            vtk_file.write("# vtk DataFile Version 4.2 \n")
            vtk_file.write("Muscle Strip \n")
            vtk_file.write("ASCII \n")

            vtk_file.write("DATASET UNSTRUCTURED_GRID \n\n")

            vtk_file.write("POINTS {} FLOAT \n".format(total_nodes))

            for _, coords in self.nodes.items():
                vtk_file.write("{} {} {} \n".format(coords[0].get_x(), coords[0].get_y(), coords[0].get_z()))

            vtk_file.write("\nCELLS {} {}\n".format(total_elems, total_elems * 9))

            for _, nodes in self.elements.items():
                vtk_file.write("8 {} {} {} {} {} {} {} {} \n".format(
                    nodes[0][1] - 1, nodes[0][2] - 1, nodes[0][3] - 1, nodes[0][0] - 1, nodes[0][5] - 1, nodes[0][6] - 1,
                    nodes[0][7] - 1, nodes[0][4] - 1
                ))

            vtk_file.write("\nCELL_TYPES {}\n".format(total_elems))

            for _ in self.elements.keys():
                vtk_file.write("12 \n")

            vtk_file.write("\nCELL_DATA {}\n".format(total_elems))

            # First Quantity 
            vtk_file.write('\nSCALARS {} float 1\n'.format("k1t"))
            vtk_file.write('LOOKUP_TABLE default\n')
            for _, values in materials.items():
                k1t = values[0][1]
                vtk_file.write("{} \n".format(k1t))
            
            # Second quantity
            vtk_file.write('\nSCALARS {} float 1\n'.format("k2t"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                k2t = values[0][2]
                vtk_file.write("{} \n".format(k2t))
            
            # Third quantity 
            vtk_file.write('\nSCALARS {} float 1\n'.format("k1m"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                k1m = values[0][3]
                vtk_file.write("{} \n".format(k1m))

            # Fourth quantity 
            vtk_file.write('\nSCALARS {} float 1\n'.format("k2m"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                k2m = values[0][4]
                vtk_file.write("{} \n".format(k2m))
            
            # Fifth quantity 
            vtk_file.write('\nSCALARS {} float 1\n'.format("vf"))
            vtk_file.write('LOOKUP_TABLE default\n')

            for _, values in materials.items():
                vf = values[4]
                vtk_file.write("{} \n".format(vf))

        return 1

    def create_results_vtk_hexahedral(self, filename, results):

        total_nodes = len(self.nodes.keys())
        total_elems = len(self.elements.keys())

        # Read as keys and values -0> keys become names for vtk file properties

        with open(filename, 'w') as vtk_file:

            vtk_file.write("# vtk DataFile Version 4.2 \n")
            vtk_file.write("Muscle Strip \n")
            vtk_file.write("ASCII \n")

            vtk_file.write("DATASET UNSTRUCTURED_GRID \n\n")

            vtk_file.write("POINTS {} FLOAT \n".format(total_nodes))

            for _, coords in self.nodes.items():
                vtk_file.write("{} {} {} \n".format(coords[0].get_x(), coords[0].get_y(), coords[0].get_z()))

            vtk_file.write("\nCELLS {} {}\n".format(total_elems, total_elems * 9))

            for _, nodes in self.elements.items():
                vtk_file.write("8 {} {} {} {} {} {} {} {} \n".format(
                    nodes[0][1] - 1, nodes[0][2] - 1, nodes[0][3] - 1, nodes[0][0] - 1, nodes[0][5] - 1, nodes[0][6] - 1,
                    nodes[0][7] - 1, nodes[0][4] - 1
                ))

            vtk_file.write("\nCELL_TYPES {}\n".format(total_elems))

            for _ in self.elements.keys():
                vtk_file.write("12 \n")

            vtk_file.write("\nCELL_DATA {}\n".format(total_elems))

            # Every result entry in the ditionary has the format:
            # results['mechanical_quantity'] =  {e_no: value}

            for key, items in results.items():
                # key   -> name of mechanical quantity
                # items  -> element, value dictionary pair
                vtk_file.write('\nSCALARS {} float 1\n'.format(str(key)))
                vtk_file.write('LOOKUP_TABLE default\n')
                for _, value in items.items():
                    vtk_file.write("{}\n".format(float(value)))

        return 1


    def create_fibres_visualisation(self):

        pass

if __name__ == '__main__':
    print("Hey you are in the vtk_file_writer script, please use the functions elsewhere :P")
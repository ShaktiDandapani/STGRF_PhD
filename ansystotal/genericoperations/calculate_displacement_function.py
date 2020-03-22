from collections import defaultdict


class DisplacementCalculator:

    def __init__(self, parameters=defaultdict()):
        self.parameters = parameters


    def calculate_iter_per_unit_time_period(self):
        time_period = int(self.parameters['time_period'])
        no_of_iters = int(self.parameters['number_of_iterations'])

        iter_per_unit_time_period = 1 * no_of_iters / time_period

        return iter_per_unit_time_period

    def calculate_displacement(self, flag):

        # Flag can be single-ramp or multi-step

        # Take in an argument, which asks for smooth or discontinuous (direct or step wise)
        # Then number of steps to reach the max value :) 

        iter_per_unit_time_period = self.calculate_iter_per_unit_time_period()
        init_disp = float(self.parameters['init_disp'])
        max_disp  = float(self.parameters['max_disp'])
        print("\nInit disp:{}, Max Disp:{}\n".format(init_disp, max_disp))
        # The multiplication below would give the iteration number
        init_time = int(self.parameters['init_time']) * iter_per_unit_time_period
        max_time  = int(self.parameters['max_time']) * iter_per_unit_time_period
        curr_time = int(self.parameters['iteration']) * iter_per_unit_time_period

        # Use parameters dictionary to obtain the relevant values but read in proper
        # Using calculate_iter_per_unit_time_period -> obtain iteration number as curr_time,
        # get number of iterations for init and max time -> use in line equation
        displacement = 0.0


        # This is based on the slope ! 
        # If flag == 'smooth' or 'single_ramp'
        # elif flag == 'multiple_steps'
        # write in code for attaining a displacement after 
        # equally spaced time intervals
        point_one = (init_time, init_disp)
        point_two = (max_time, max_disp)
		
		
        inc_displace = 0.25 * (point_two[1] - point_one[1])
        inc_time = 0.25 * (point_two[0] - point_one[0])
        time1 = inc_time + init_time
        time2 = 2 * inc_time + init_time
        time3 = 3 * inc_time + init_time

        slope     = (point_two[1] - point_one[1])  \
                    / (point_two[0] - point_one[0])
        if flag == 'single-ramp':

            # Current time needs to be calculated from time period and number of iterations
            if init_time <= curr_time <= max_time:
                displacement = slope * (curr_time - init_time) + init_disp
            elif curr_time > max_time:
                displacement = max_disp
            elif curr_time < init_time:
                displacement = init_disp

        elif flag == 'multi-step':

            if curr_time < init_time:
                  displacement = init_disp
            elif init_time <= curr_time < time1:
                  displacement = init_disp+ inc_displace
            elif time1 <= curr_time < time2:
                  displacement = init_disp+ 2*inc_displace
            elif time2 <= curr_time < time3:
                  displacement = init_disp+ 3*inc_displace
            elif curr_time >= time3:
                 displacement = init_disp+ 4*inc_displace
        print("Displacement from Python: ".format(displacement))
        return displacement


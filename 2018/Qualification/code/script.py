import os
import pandas as pd

path = '../Data/'
filename = 'a_example.in'

class Manager:
    def __init__(self, overview):
        self.rows = overview['rows']
        self.cols = overview['cols']
        self.vehicles = overview['vehicles']
        self.rides = overview['rides']
        self.bonus = overview['bonus']
        self.steps = overview['steps']
    
    def ini_vehicles(self):
        return [Vehicle() for i in range(overview['vehicles'])]

    def ini_Ride(self):
        return [Ride(ride_details.loc[i]) for i in range(overview['rides'])]
    
    def assign_vehicle(self, v_list, r_list, step):
        for v_obj in v_list:
            if v_obj.available:
                for j, r_obj in enumerate(r_list):
                    if ~r_obj.complete:
                        dist_start = self.compute_x_dist(v_obj.v_row,   r_obj.row_st)+ self.compute_y_dist(v_obj.v_col, r_obj.col_st)
                        if (r_obj.step_st > dist_start + step) & (r_obj.step_fin > dist_start + r_obj.distance + step):
                            flag = 2
                        elif (r_obj.step_fin > dist_start+ r_obj.distance):
                            flag = 1
                        else:
                            flag = 0
                        self.compute_score(r_obj, v_obj, flag)
                        v_obj.booked_until = dist_start + r_obj.distance + step
                        v_obj.update_position(r_obj)
                        v_obj.update_availability()
                        r_obj.update_completion()
                        v_obj.rides_list.append(j)
                        v_obj.num_rides = v_obj.num_rides + 1
                        break
                        
    def check_availability(self, v_list, step):
        for v_obj in v_list:
            if ~v_obj.available:
                if step > v_obj.booked_until:
                    Vehicle.update_availability(v_obj)
            
        
    def compute_score(self, r_obj, v_obj, flag=0):
        """0: no score, 1: dist, 2: dist + bonus"""
        dist = self.compute_x_dist(r_obj.col_st, r_obj.col_fin)+self.compute_y_dist(r_obj.row_st, r_obj.row_fin)
        if flag == 2:
            v_obj.score = v_obj.score + dist + self.bonus
        elif flag ==1:
            v_obj.score = v_obj.score + dist
    
    def compute_x_dist(self, col_st, col_fin):
        return abs(col_st - col_fin)
    
    def compute_y_dist(self, row_st, row_fin):
        return abs(row_st - row_fin)

class Vehicle:
    def __init__(self):
        self.v_row = 0
        self.v_col = 0
        self.available = True
        self.score = 0
        self.booked_until = -1
        self.num_rides = 0
        self.rides_list = []
        
    def update_position(self, ride):
        """Updates Position of vehicle"""
        self.v_row = ride.row_fin
        self.v_col = ride.col_fin
        
    def update_availability(self):
        """Toggles Availability"""
        self.available = ~self.available

class Ride:
    def __init__(self, series):
        self.row_st = series['row_start']
        self.col_st = series['col_start']
        self.row_fin = series['row_end']
        self.col_fin = series['col_end']
        self.step_st = series['early_start']
        self.step_fin = series['late_finish']
        self.distance = series['ride_dist']
        self.complete = False
        
    def update_completion(self):
        """Toggles the flag that corresponds to completed ride"""
        self.complete = ~self.complete


# Read file
file = open(path+filename, 'r')
example = file.read()

# Ride Details on DataFrame
col_names = ['row_start', 'col_start', 'row_end', 'col_end', 'early_start', 'late_finish']
rename_cols = dict(zip(list(range(0, len(col_names))), col_names))
ride_details = pd.read_csv(path+filename, sep = ' ', header = None, skiprows = 1).rename(columns = rename_cols)
ride_details['ride_dist'] = abs(ride_details['row_start']-ride_details['row_end']) + abs(ride_details['col_start']-ride_details['col_end'])

# Parameters of problem on dict
over_keys = ['rows', 'cols', 'vehicles', 'rides', 'bonus', 'steps']
over_vals = [int(param) for param in example.split('\n')[0].split(' ')]
overview = dict(zip(over_keys, over_vals))

m1 = Manager(overview)
vehicle_list = m1.ini_vehicles()
ride_list = m1.ini_Ride()

for i in range(overview['steps']):
    m1.check_availability(vehicle_list, i)
    m1.assign_vehicle(vehicle_list, ride_list, i)
    rides_completed = [1 for i in ride_list if i.complete]
    if len(rides_completed) == overview['rides']:
        break
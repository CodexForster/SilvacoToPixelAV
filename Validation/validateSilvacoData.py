# Author: Danush Shekar, UIC (May 2, 2024)
# Description: Used for validating Silvaco simulation data when compared with DF-ISE data

import math
import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
import optparse


parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-e', '--pltEF', dest='pltEF', help="Plot electric fields")
parser.add_option('-w', '--pltWP', dest='pltWP', help="Plot weighting potentials")
parser.add_option('-d', '--pltDop', dest='pltDop', help="Plot doping conc.")
options, args = parser.parse_args()

if(int(options.pltEF) + int(options.pltWP) + int(options.pltDop) <= 0):
    print("Choose atleast one plotting-task.")
    exit()

pltEF = bool(int(options.pltEF))  # Convert to boolean
pltWP = bool(int(options.pltWP))
pltDoping = bool(int(options.pltDop))

def read_mesh(file_name):
    with open(file_name, 'r') as file:
        return [list(map(float, line.split())) for line in file]
    
def read_conc(file_name):
    with open(file_name, 'r') as file:
        data = [float(line.strip()) for line in file]
    return data

def calculate_distance(point1, point2):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(point1, point2)))

def calculate_magnitude(vector):
    return math.sqrt(sum(x ** 2 for x in vector))

def read_EF(file_path):
    with open(file_path, 'r') as file:
        data = []
        row = []
        for line in file:
            for value in line.split():
                row.append(float(value))
                if len(row) == 3:  # If we have collected X, Y, Z components for a point
                    data.append(row)
                    row = []  # Start a new row
    return data

def find_EF(electric_fields, line, mesh_points):
    EF = []
    for point in line:
        closest_point_index = min(range(len(mesh_points)), key=lambda i: calculate_distance(point, mesh_points[i]))
        # print("The mesh point is = ",mesh_points[closest_point_index])
        # print("The electric field at the nearest point is = ", calculate_magnitude(electric_fields[closest_point_index]))
        EF.append(calculate_magnitude(electric_fields[closest_point_index]))
    return EF

def read_WP(file_path):
    with open(file_path, 'r') as file:
        data = []
        row = []
        for line in file:
            for value in line.split():
                data.append(float(value))
    return data

def find_WP(weighting_pots, line, mesh_points):
    WP = []
    for point in line:
        closest_point_index = min(range(len(mesh_points)), key=lambda i: calculate_distance(point, mesh_points[i]))
        WP.append(weighting_pots[closest_point_index])
    return WP

def find_doping(arr, line, mesh_points):
    doping = []
    for point in line:
        closest_point_index = min(range(len(mesh_points)), key=lambda i: calculate_distance(point, mesh_points[i]))
        doping.append(arr[closest_point_index])
    return doping

# Define the line along which the electric field is to be plotted
line = []
# 100 125 31.25
y_cor = 43.875#11#20#
z_cor = 15.625#2#3#
for x in np.arange(0, 5, 0.3):
    line.append([x, y_cor, z_cor])
for x in np.arange(5, 85, 5):
    line.append([x, y_cor, z_cor])
for x in np.arange(85, 97, 2):
    line.append([x, y_cor, z_cor])
for x in np.arange(97, 100, 0.3):
    line.append([x, y_cor, z_cor])

# line = []
# x_cor = 99.0
# y_cor = 11.0
# for x in np.arange(0, 6, 0.3):
#     line.append([x_cor, y_cor, x])
# for x in np.arange(6, 6.25, 0.1):
#     line.append([x_cor, y_cor, x])
# line.append([x_cor, y_cor, 6.25])

x_coordinates = [point[0] for point in line]


# Create the plot
if(pltEF):
    # Read the mesh and electric field files
    mesh_points_EF = read_mesh('mesh_EF.txt')
    electric_fields = read_EF('EF.txt')
    # with open('allpixInput_morrisData.grd', 'w') as f:
    #     for row in mesh_points_EF:
    #         f.write(' '.join(map(str, row)) + '\n')
    # with open('allpixInput_morrisData.dat', 'w') as f:
    #     for row in electric_fields:
    #         f.write(' '.join(map(str, row)) + '\n')
    EF = find_EF(electric_fields, line, mesh_points_EF)
    save_data_EF = list(zip(x_coordinates, EF))
    # Write EF data to a CSV file
    with open('parsedEFdataVsDepth_at_'+str(y_cor)+'_'+str(z_cor)+'.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(save_data_EF)
    plt.plot(x_coordinates, EF, label='Electric field')
    plt.ylabel('Electric field [V/cm]')
    plt.title('Electric field across a line through the center of a pixel')
    plt.legend()
    # Add labels and title
    plt.xlabel('X-coordinate [um]')
    plt.grid(True)
    plt.savefig("EF.png")

if(pltWP):
    weighting_pots = read_WP('Wpot.txt')
    mesh_points_WP = read_mesh('mesh_WP.txt') 
    print("Test print of the last 5 pts in mesh: ",mesh_points_WP[-5:],"\n")
    WP = find_WP(weighting_pots, line, mesh_points_WP) 
    save_data_WP = list(zip(x_coordinates, WP))
    # Write Wpot data to a CSV file
    with open('parsedWPdataVsDepth_at_'+str(y_cor)+'_'+str(z_cor)+'.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(save_data_WP)
    plt.plot(x_coordinates, WP, label='Weighting potential')
    plt.ylabel('Weighting potential [V]')
    plt.title('Weighting potential across a line through the center of a pixel')
    plt.legend()
    # Add labels and title
    plt.xlabel('X-coordinate [um]')
    plt.grid(True)
    plt.savefig("Wpot.png")
    
elif(pltDoping):
    mesh_points_EF = read_mesh('mesh_EF.txt')
    abs_doping = read_conc('Abs_dop_conc.csv')
    B_doping = read_conc('B_conc.csv')
    P_doping = read_conc('P_conc.csv')

    AbsDoping = find_doping(abs_doping, line, mesh_points_EF)
    BDoping = find_doping(B_doping, line, mesh_points_EF)
    PDoping = find_doping(P_doping, line, mesh_points_EF)
    # plt.plot(x_coordinates, AbsDoping, label='Absolute doping')
    plt.plot(x_coordinates, BDoping, label='Boron doping')
    plt.plot(x_coordinates, PDoping, label='Phosporous doping')
    plt.ylabel('Doping concentration [cm^-3]')
    plt.title('Doping concentration across a line through the center of a pixel')
    plt.yscale('log')
    plt.legend()
    # Add labels and title
    plt.xlabel('X-coordinate [um]')
    plt.grid(True)
    plt.savefig("Doping.png")


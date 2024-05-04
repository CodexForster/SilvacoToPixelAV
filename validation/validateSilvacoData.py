# Author: Danush Shekar, UIC (May 2, 2024)
# Description: Used for validating Silvaco simulation data when compared with DF-ISE data

import math
import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
import optparse
import pandas as pd

parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-e', '--pltEF', action='store_true', dest='pltEF', help="Plot electric fields")
parser.add_option('-w', '--pltWP', action='store_true', dest='pltWP', help="Plot weighting potentials")
parser.add_option('-E', '--pltEF2d', action='store_true', dest='pltEF2d', help="Plot 2D electric fields")
parser.add_option('-W', '--pltWP2d', action='store_true', dest='pltWP2d', help="Plot 2D weighting potentials")
parser.add_option('-d', '--pltDop', action='store_true', dest='pltDop', help="Plot doping conc.")
options, args = parser.parse_args()

pltEF = options.pltEF
pltWP = options.pltWP
pltEF2d = options.pltEF2d
pltWP2d = options.pltWP2d
pltDop = options.pltDop

if not (pltEF or pltWP or pltEF2d or pltWP2d or pltDop):
    print("Choose atleast one plotting-task.")
    exit()

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
        closest_point = mesh_points[closest_point_index]
        print(f"Closest point to {point} is {closest_point}: {electric_fields[closest_point_index]}")
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
        closest_point = mesh_points[closest_point_index]
        print(f"Closest point to {point} is {closest_point}: {weighting_pots[closest_point_index]}")
        WP.append(weighting_pots[closest_point_index])
    return WP

def find_doping(arr, line, mesh_points):
    doping = []
    for point in line:
        closest_point_index = min(range(len(mesh_points)), key=lambda i: calculate_distance(point, mesh_points[i]))
        doping.append(arr[closest_point_index])
    return doping

# Define the line along which the electric field is to be plotted
if(pltWP):
    coordinates = [[110, 20], [43.875, 15.625], [11, 2], [20, 3], [100, 25]]
elif(pltEF):
    coordinates = [[11, 2], [17, 3], [2, 1], [23, 5]]

for iter in range(len(coordinates)):
    line = []
    # 100 125 31.25
    y_cor = coordinates[iter][0]
    z_cor = coordinates[iter][1]
    for x in np.arange(0, 5, 0.3):
        line.append([x, y_cor, z_cor])
    for x in np.arange(5, 85, 5):
        line.append([x, y_cor, z_cor])
    for x in np.arange(85, 97, 2):
        line.append([x, y_cor, z_cor])
    for x in np.arange(97, 100, 0.3):
        line.append([x, y_cor, z_cor])
    x_coordinates = [point[0] for point in line]

    # line = []
    # x_cor = 99.0
    # y_cor = 11.0
    # for x in np.arange(0, 6, 0.3):
    #     line.append([x_cor, y_cor, x])
    # for x in np.arange(6, 6.25, 0.1):
    #     line.append([x_cor, y_cor, x])
    # line.append([x_cor, y_cor, 6.25])

    # Create the plot
    if(pltEF):
        # Read the mesh and electric field files
        mesh_points_EF = read_mesh('mesh_EF.txt')
        electric_fields = read_EF('EF.txt')
        mesh_points_EF2 = read_mesh('mesh_EFMorris.txt')
        electric_fields2 = read_EF('EFMorris.txt')
        print("\n\nSILVACO\n\n")
        EF = find_EF(electric_fields, line, mesh_points_EF)
        print("\n\nDF-ISE\n\n")
        EF2 = find_EF(electric_fields2, line, mesh_points_EF2)
        save_data_EF = list(zip(x_coordinates, EF))
        # Write EF data to a CSV file
        with open('parsedEFdataVsDepth_at_'+str(y_cor)+'_'+str(z_cor)+'.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(save_data_EF)
        plt.clf()
        plt.plot(x_coordinates, EF, label='Silvaco Efield')
        plt.plot(x_coordinates, EF2, label='DF-ISE Efield', linestyle='--')
        plt.ylabel('Electric field [V/cm]')
        plt.title('Electric field vs depth at ('+str(y_cor)+','+str(z_cor)+') um')
        plt.legend()
        # Add labels and title
        plt.xlabel('X-coordinate/depth [um]')
        plt.grid(True)
        plt.savefig("EF_line("+str(y_cor)+'_'+str(z_cor)+").png")

    elif(pltWP):
        weighting_pots = read_WP('Wpot.txt')
        mesh_points_WP = read_mesh('mesh_Wpot.txt') 
        weighting_pots2 = read_WP('WpotMorris.txt')
        mesh_points_WP2 = read_mesh('mesh_WpotMorris.txt') 
        print("Test print of the last 5 pts in mesh: ",mesh_points_WP2[-5:],"\n")
        print("\n\nSILVACO\n\n")
        WP = find_WP(weighting_pots, line, mesh_points_WP)
        print("\n\nDF-ISE\n\n")
        WP2 = find_WP(weighting_pots2, line, mesh_points_WP2) 
        save_data_WP = list(zip(x_coordinates, WP2))
        # Write Wpot data to a CSV file
        with open('parsedWPdataVsDepth_at_'+str(y_cor)+'_'+str(z_cor)+'.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(save_data_WP)
        plt.clf()
        plt.plot(x_coordinates, WP, label='Silvaco weighting pot')
        plt.plot(x_coordinates, WP2, label='DF-ISE weighting pot', linestyle='--')
        plt.ylabel('Weighting potential [V]')
        plt.title('Weighting potential vs depth at ('+str(y_cor)+','+str(z_cor)+') um')
        plt.legend()
        # Add labels and title
        plt.xlabel('X-coordinate/depth [um]')
        plt.grid(True)
        plt.savefig("Wpot_line("+str(y_cor)+'_'+str(z_cor)+").png")
        
    elif(pltDop):
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
        plt.savefig("Doping_line"+iter+".png")

# elif(pltWP2d):
#     data = pd.read_csv('../../50x12P5wgt/silvaco_final_weighting.out', delim_whitespace=True, header=None)
#     filtered_data = data[data[1] == 6]
#     potential_values = filtered_data[3].values.reshape((int(np.sqrt(filtered_data.shape[0])), int(np.sqrt(filtered_data.shape[0]))))
#     plt.imshow(potential_values, cmap='viridis', origin='lower')
#     plt.colorbar(label='Potential')
#     plt.xlabel('X')
#     plt.ylabel('Z')
#     plt.title('2D XZ plot of potential values at Y=6')
#     plt.savefig('Wpot2D.png')

# elif(pltEF2d):
#     data = pd.read_csv('../../50x12P5/silvaco_final_efield_temp.out', delim_whitespace=True, header=None)
#     filtered_data = data[data[1] == 6]
#     plt.scatter(filtered_data[0], filtered_data[2], c=np.sqrt(filtered_data[3]**2 + filtered_data[4]**2 + filtered_data[5]**2), cmap='viridis')
#     plt.colorbar(label='Efield')
#     plt.xlabel('X')
#     plt.ylabel('Z')
#     plt.title('2D XZ plot of weighting potential values at Y=6')
#     plt.savefig('Wpot2D.png')

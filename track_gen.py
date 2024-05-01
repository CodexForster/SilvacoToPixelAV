# Author: Danush Shekar, UIC (April 16, 2024)
# Acknowledgement(s): Mohammad Abrar Wadud, Farhan Abid
# Description: Generates tracks for PixelAV

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import numpy as np
import math

def mm_to_metre(qty):
    return qty/1000

def metre_to_mm(qty):
    return qty*1000

# Constants: distance in metres, momentums in GeV/c
X_MIN = mm_to_metre(-8.1)  # Minimum X coordinate of sensor array
X_MAX = mm_to_metre(8.1)   # Maximum X coordinate of sensor array
Z_MIN = mm_to_metre(-30)   # Minimum Z coordinate of sensor array
Z_MAX = mm_to_metre(30)    # Maximum Z coordinate of sensor array
SENSOR_Y = mm_to_metre(30) # Y coordinate of the sensor array
STEPS = mm_to_metre(0.4)   # Step size for the particle trajectory
ptmax = 5 # in GeV
B_FIELD = 3.8   # Magnetic field strength in Tesla
tolerance = mm_to_metre(0.5) # Tolerance for checking when the particle crosses the sensor module


# Function to generate random particle tracks
def generate_init_info():
    # Generate random X and Z coordinates within the specified range
    x_coords = np.random.uniform(mm_to_metre(-2),mm_to_metre(2))
    y_coords = np.random.uniform(mm_to_metre(-2),mm_to_metre(2))
    z_coords = np.random.uniform(mm_to_metre(10),mm_to_metre(-10))
    pt = np.random.uniform(0, ptmax)
    pz = np.random.uniform(-1, 1)
    phi = np.random.uniform(0, 2*math.pi)
    charge = 1
    return np.array([x_coords, y_coords, z_coords, pt, phi, pz, charge])

def sensor_hit_tracks(num_particles):
    track_list = []
    counter = 0
    while (counter <= num_particles):
        initial_track = generate_init_info()
        # the beginning of track is at or around the beam pipe (2mm along x and y, and 20mm along z)
        temp = track_propagate(initial_track)
        if(temp[0]>0):
            cota = temp[1]
            cotb = temp[2]
            p = temp[3]
            flp = temp[4]
            local_x = temp[5]
            local_y = temp[6]
            pt = temp[7]
            # track_list format: cota, cotb, p, flp, localx, localy, pT
            track_list.append(np.array([cota, cotb, p, flp, metre_to_mm(local_x),metre_to_mm(local_y),pt]))# propagate the track
            counter += 1
            if(counter%1000==0 and counter!=0):
                print("Gen status = ", counter)
    return np.array(track_list)

def plot_traj(iter):
    vector = generate_init_info()
    # the beginning of track is at or around the beam pipe (2mm along x and y, and 20mm along z)
    x_init = vector[0]
    y_init = vector[1]
    z_init = vector[2]
    x_track = []
    y_track = []
    z_track = []
    pt = vector[3]
    Phi0 = vector[4]
    pz = vector[5]
    charge = vector[6]
    R = pt / (0.3 * B_FIELD)
    p = np.sqrt(pt**2 + pz**2)
    Lambda = np.arcsin(pz/p)
    h = -1#math.copysign(1, charge*B_FIELD)
    for s in np.arange(0, 2*math.pi*R, STEPS):
        x, y, z = particle_trajectory(s, x_init, y_init, z_init, R, Phi0, h, Lambda)
        x_track.append(metre_to_mm(x))
        y_track.append(metre_to_mm(y))
        z_track.append(metre_to_mm(z))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x_track, y_track, z_track)
    ax.set_xlabel('X [mm]')
    ax.set_ylabel('Y [mm]')
    ax.set_zlabel('Z [mm]')
    ax.view_init(azim=90)
    ax.view_init(elev=-45)
    plt.show()
    # plt.savefig('track'+str(iter)+'.png')

def track_propagate(vector):
    # Ref: https://cds.cern.ch/record/2308020/files/CERN-THESIS-2017-328.pdf
    #.   : https://cds.cern.ch/record/251912/files/cer-000168391.pdf
    x_init = vector[0]
    y_init = vector[1]
    z_init = vector[2]
    pt = vector[3]
    Phi0 = vector[4]
    pz = vector[5]
    charge = vector[6]
    R = pt / (0.3 * B_FIELD)
    p = np.sqrt(pt**2 + pz**2)
    Lambda = np.arcsin(pz/p)
    h = -1#math.copysign(1, charge*B_FIELD)
    if(2*math.pi*R<mm_to_metre(30)): 
        # in the best case, if circumference of loop is less than distance to sensor module, then drop event
        return np.array([0, 0, 0, 0, 0, 0, 0, 0])
    else:
        # Coarse search
        for s in np.arange(mm_to_metre(20), 2*math.pi*R, STEPS):
            x, y, z = particle_trajectory(s, x_init, y_init, z_init, R, Phi0, h, Lambda)
            if abs(y - SENSOR_Y) < tolerance:
                # Fine search
                for s_fine in np.arange(s - 1.2*tolerance, s + 1.2*tolerance+STEPS/10, STEPS/10):
                    x_fine, y_fine, z_fine = particle_trajectory(s_fine, x_init, y_init, z_init, R, Phi0, h, Lambda)
                    if abs(x_fine) < X_MAX and abs(y_fine - SENSOR_Y) < tolerance/10 and abs(z_fine) < Z_MAX:
                        # Once s is close to the sensor module, calculate the track list parameters needed by PixelAV
                        if y_fine<=SENSOR_Y:
                            x_fine2, y_fine2, z_fine2 = particle_trajectory(s_fine+STEPS/10, x_init, y_init, z_init, R, Phi0, h, Lambda)
                            cotPhi = (x_fine2-x_fine)/(y_fine2-y_fine)
                            cotGamma = (z_fine2-z_fine)/(y_fine2-y_fine)
                        else:
                            x_fine2, y_fine2, z_fine2 = particle_trajectory(s_fine-STEPS/10, x_init, y_init, z_init, R, Phi0, h, Lambda)
                            cotPhi = (x_fine-x_fine2)/(y_fine-y_fine2)
                            cotGamma = (z_fine-z_fine2)/(y_fine-y_fine2)
                        x_pav = z_fine
                        z_pav = y_fine
                        y_pav = x_fine
                        cota = cotPhi
                        cotb = cotGamma
                        return np.array([1, cota, cotb, p, 0, x_pav, y_pav, pt])
                        # return np.array([1, x_fine, y_fine, z_fine, np.sqrt(pt*pt + pz*pz), pt, pz])
        return np.array([0, 0, 0, 0, 0, 0, 0, 0])

def particle_trajectory(s, x0, y0, z0, R, Phi0, h, Lambda):
    x = x0 + R*(math.cos(Phi0 + h*s*math.cos(Lambda)/R) - math.cos(Phi0))
    y = y0 + R*(math.sin(Phi0 + h*s*math.cos(Lambda)/R) - math.sin(Phi0))
    z = z0 + s*math.sin(Lambda)
    return (x,y,z)


def plot(list1, list2, name, save_name, units):
    # Find and print the maximum and minimum values in each column
    print(f'New list: min = {min(list1)}, max = {max(list1)}')
    print(f'Old list: min = {min(list2)}, max = {max(list2)}')
    # Create histograms of the values
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    if("cotAlpha" in save_name):
        plt.hist(list1, bins=100, range=(-0.6, 0.6), edgecolor='black')
    else:
        plt.hist(list1, bins=100, edgecolor='black')
    plt.title('Distribution of '+name)
    plt.xlabel('Value ['+units+']')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    plt.hist(list2, bins=50, edgecolor='black')
    plt.title('Distribution of '+name)
    plt.xlabel('Value ['+units+']')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('hist'+save_name+'.png')

# Plot sample tracks
# plot_traj(1)
# plot_traj(2)
# plot_traj(3)
# plot_traj(4)
# plot_traj(5)

# Generate particle tracks
# num_particles = 100000  # Adjust the number of particles as needed
# tracks = sensor_hit_tracks(num_particles)

# # Save the hit positions, momentum, and pT to a file or use them for further analysis
# print("================")
# print("Track generation is complete.\nNumber of tracks generated: ", len(tracks))
# print("================")
# np.savetxt("new_track_list.txt", tracks, delimiter=' ', header='cota, cotb, p, flp, localx, localy, pT')

# Read the data from the file, skipping lines that start with '#'
with open('track_list.txt', 'r') as f:
    lines = [line for line in f if not line.startswith('#')]
# Read the data from the file, skipping lines that start with '#'
with open('track_list.txt', 'r') as f2:
    lines2 = [line for line in f2 if not line.startswith('#')]

values = ['cotAlpha', 'cotBeta', 'P [GeV/c]', 'Local X [mm]', 'Local Y [mm]', 'Pt [GeV/c]']
save_name = ['cotAlpha', 'cotBeta', 'P_values', 'Local_X_coord', 'Local_Y_coord', 'Pt_values']
units = ['', '', 'GeV/c', 'mm', 'mm', 'GeV/c']
qty1, qty2 = [], []
qty1.append([float(line.split()[0]) for line in lines2]) #cotAlpha
qty1.append([float(line.split()[1]) for line in lines2]) #cotBeta
qty1.append([float(line.split()[2]) for line in lines2]) #P
qty1.append([float(line.split()[4]) for line in lines2]) #Local X
qty1.append([float(line.split()[5]) for line in lines2]) #Local Y
qty1.append([float(line.split()[6]) for line in lines2]) #Pt

#cotb cota p flp localx localy pT
qty2.append([float(line.split()[0]) for line in lines]) #cotAlpha
qty2.append([float(line.split()[1]) for line in lines]) #cotBeta
qty2.append([float(line.split()[2]) for line in lines]) #P
qty2.append([float(line.split()[4]) for line in lines]) #Local X
qty2.append([float(line.split()[5]) for line in lines]) #Local Y
qty2.append([abs(float(line.split()[6])) for line in lines]) #Pt

for iter in range(len(values)):
    plot(qty1[iter], qty2[iter], values[iter], save_name[iter], units[iter])
# Author: Danush Shekar, April 16, 2024
# Acknowledgement(s): Mohammad Abrar Wadud, Farhan Abid

import matplotlib.pyplot as plt
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
    initial_track = generate_init_info()
    track_list = []
    counter = 0
    while (counter <= num_particles):
        # the beginning of track is at or around the beam pipe (2mm along x and y, and 20mm along z)
        temp = track_propagate(initial_track)
        if(temp[0]>0):
            x = temp[1]
            y = temp[2]
            z = temp[3]
            p = temp[4]
            pz = temp[5]
            track_list.append(np.array([metre_to_mm(x),metre_to_mm(y),metre_to_mm(z),p,pz]))# propagate the track
            counter += 1
            if(counter%100==0 and counter!=0):
                print("Gen status = ", counter)
    return np.array(track_list)

def track_propagate(vector):
    # Ref: https://cds.cern.ch/record/2308020/files/CERN-THESIS-2017-328.pdf
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
        return np.array([0, 0, 0, 0, 0, 0])
    else:
        for s in np.arange(mm_to_metre(20), 2*math.pi*R, mm_to_metre(0.4)):
            x, y, z = particle_trajectory(s, x_init, y_init, z_init, R, Phi0, h, Lambda)
            if abs(x) < X_MAX and abs(y - SENSOR_Y) < tolerance and abs(z) < Z_MAX:
                # return np.array([1, x, y, z, pt, pz])
                return np.array([1, x, y, z, np.sqrt(pt*pt + pz*pz), pz])
        return np.array([0, 0, 0, 0, 0, 0])

def particle_trajectory(s, x0, y0, z0, R, Phi0, h, Lambda):
    x = x0 + R*(math.cos(Phi0 + h*s*math.cos(Lambda)/R) - math.cos(Phi0))
    y = y0 + R*(math.sin(Phi0 + h*s*math.cos(Lambda)/R) - math.sin(Phi0))
    z = z0 + s*math.sin(Lambda)
    return (x,y,z)


def plot(list1, list2, name, save_name):
    # Find and print the maximum and minimum values in each column
    print(f'New list: min = {min(list1)}, max = {max(list1)}')
    print(f'Old list: min = {min(list2)}, max = {max(list2)}')
    # Create histograms of the values
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.hist(list1, bins=100, edgecolor='black')
    plt.title('Distribution of '+name)
    plt.xlabel('Value [mm]')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    plt.hist(list2, bins=100, edgecolor='black')
    plt.title('Distribution of '+name)
    plt.xlabel('Value [mm]')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('hist'+save_name+'.png')

# Generate particle tracks
num_particles = 1000  # Adjust the number of particles as needed
tracks = sensor_hit_tracks(num_particles)

# Save the hit positions, momentum, and pT to a file or use them for further analysis
print("================")
print("Track generation is complete.\nNumber of tracks generated: ", len(tracks))
print("================")
np.savetxt("new_track_list.txt", tracks, delimiter=' ', header='X,Y,Z,P,Pt')

# Read the data from the file, skipping lines that start with '#'
with open('track_list_L1_025GeV.txt', 'r') as f:
    lines = [line for line in f if not line.startswith('#')]
# Read the data from the file, skipping lines that start with '#'
with open('new_track_list.txt', 'r') as f2:
    lines2 = [line for line in f2 if not line.startswith('#')]

values = ['X [mm]', 'Y [mm]', 'Z [mm]', 'P [GeV/c]', 'Pt [GeV/c]']
save_name = ['X_coord', 'Y_coord', 'Z_coord', 'P_values', 'Pt_values']
qty1, qty2 = [], []
qty1.append([float(line.split()[0]) for line in lines2]) #X1
qty1.append([float(line.split()[1]) for line in lines2]) #Y1
qty1.append([float(line.split()[2]) for line in lines2]) #Z1
qty1.append([float(line.split()[3]) for line in lines2]) #P1
qty1.append([float(line.split()[4]) for line in lines2]) #Pt1

#cotb cota p flp localx localy pT
qty2.append([float(line.split()[5]) for line in lines]) #X2 (Y in pixelAV coordinates is X in global coordinates)
qty2.append([float(line.split()[1]) for line in lines2]) #Y2
qty2.append([float(line.split()[4]) for line in lines]) #Z2 (X in pixelAV coordinates is Z in global coordinates)
qty2.append([float(line.split()[2]) for line in lines]) #P2
qty2.append([float(line.split()[6]) for line in lines]) #Pt2

for iter in range(len(values)):
    plot(qty1[iter], qty2[iter], values[iter], save_name[iter])
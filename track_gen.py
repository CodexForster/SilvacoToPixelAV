import matplotlib.pyplot as plt
import random
import numpy as np
import math

# Constants
X_MIN = -8.1  # Minimum X coordinate of sensor array
X_MAX = 8.1   # Maximum X coordinate of sensor array
Z_MIN = -30   # Minimum Z coordinate of sensor array
Z_MAX = 30    # Maximum Z coordinate of sensor array
SENSOR_Y = 30   # Y coordinate of the sensor array
ptmax = 5 # in GeV
m_pion=0.13957 # in GeV/c^2
B_FIELD = 3.8   # Magnetic field strength in Tesla

# Function to generate random particle tracks
def generate_hit_info(num_particles):
    # Generate random X and Z coordinates within the specified range
    x_coords = np.random.uniform(X_MIN, X_MAX, num_particles)
    z_coords = np.random.uniform(Z_MIN, Z_MAX, num_particles)
    y_coords = np.ones(num_particles) * SENSOR_Y
    pt = np.random.uniform(0, ptmax, num_particles)
    return np.column_stack((x_coords, y_coords, z_coords, pt))

def generate_full_track(interim_tracks, num_particles):
    track_list = []
    for iter in range(len(interim_tracks)):
        quotient = 21
        counter = 0
        while quotient > 20:
            if counter >= 20:
                break
            # the beginning of track can be at or around the beam pipe (2mm along x and y, and 20mm along z)
            origin_track = (random.uniform(-2,2), random.uniform(-2,2), random.uniform(10,-10))
            track, quotient = calculate_pz(interim_tracks[iter], origin_track)
            counter += 1
        if counter < 20:
            track_list.append(track)
    return np.array(track_list)

def calculate_pz(interim_track, origin_track):
    pt = interim_track[3]
    # Ref: http://lppp.lancs.ac.uk/motioninb/en-GB/experiment.html?LPPPSession=1567036800030
    radius = pt / (0.3 * B_FIELD)
    delta = np.sqrt((interim_track[0] - origin_track[0])**2 + (interim_track[1] - origin_track[1])**2 + (interim_track[2] - origin_track[2])**2)
    quotient = 21
    if(2*radius > delta):
        quotient = 1
        # Ref: https://stackoverflow.com/questions/52210911/great-circle-distance-between-two-p-x-y-z-points-on-a-unit-sphere
        phi = np.arcsin(delta/(2*radius)) 
        A = 2*radius*phi
        pz = pt*(interim_track[2] - origin_track[2])/A
        p = np.sqrt(pt**2 + pz**2)
    else:
        quotient, remainder = divmod(delta, 2 * radius)
        phi = np.arcsin(remainder/(2*radius))
        A = 2*radius*phi
        pz = pt*(interim_track[2] - origin_track[2])/(A+2*math.pi*radius*quotient)
        p = np.sqrt(pt**2 + pz**2)
    print(interim_track[0], interim_track[1], interim_track[2], quotient, pz, p)
    return(interim_track[0], interim_track[1], interim_track[2], pz, pt), quotient

# Function to check if particles hit the sensor array and record position, momentum, and pT
def check_hits(tracks, pt):
    # Filter tracks that hit the sensor array
    sensor_hits = tracks[(tracks[:, 1] == SENSOR_Y)]
    # Record the X and Z positions, momentum, and pT of hits
    hit_positions = sensor_hits[:, [0, 2]]
    hit_momentum = pt[sensor_hits[:, 1] == SENSOR_Y]
    return hit_positions, hit_momentum

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
num_particles = 100000  # Adjust the number of particles as needed
interim_tracks = generate_hit_info(num_particles)
tracks = generate_full_track(interim_tracks, num_particles)
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
import csv
from scipy.spatial import KDTree
import numpy as np
import matplotlib.pyplot as plt

x_tolerance = 0.2
y_tolerance = 0.0005
z_tolerance = 0.04

def plot_hist(arr, title, Bins, LOGY=False, LOGX=False):
    plt.hist(arr, bins=Bins, range=(min(arr), max(arr)))
    plt.xlabel(title)
    plt.ylabel('Counts')
    if(LOGY):
        plt.yscale('log')
    if(LOGX):
        plt.xscale('log')
    plt.title('Histogram of ' + title + ' values')
    plt.savefig(title+'_hist.png')
    plt.close()

def plot_scatter(arr1, arr2, title1, title2, LOGY=False):
    plt.scatter(arr1, arr2)
    if(LOGY):
        plt.yscale('log')
    plt.xlabel(title1)
    plt.ylabel(title2)
    plt.title('Plot of '+title1+' vs '+title2)
    plt.savefig(title1+'vs'+title2+'_scatter.png')
    plt.close()

def read_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    coord = []
    data = []
    for line in lines:
        data = line.split()
        coord.append([float(data[0]), float(data[1]), float(data[2])])
        data.append([float(data[3]), float(data[4]), float(data[5])])
    return (np.array(coord), np.array(data))

def read_coordinates(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        coord = []
        data = []
        for row in reader:
            if row:
                coord.append([float(row[0]), float(row[1]), float(row[2])])
                data.append([float(row[3]), float(row[4]), float(row[5])])
        return (np.array(coord), np.array(data))

def compare_coordinates(coords1, coords2, data1, data2):
    # Build KD-tree from the points
    kdtree = KDTree(coords2)
    for index, (x1, y1, z1) in enumerate(coords1):
        tmp = np.array([x1, y1, z1])
        # Query the KD-tree for the closest point to the user-defined coordinate
        dist, idx = kdtree.query(tmp)
        # Closest point
        closest_point = coords2[idx]
        if abs(x1 - closest_point[0]) <= x_tolerance and abs(y1 - closest_point[1]) <= y_tolerance and abs(z1 - closest_point[2]) <= z_tolerance:
            ex1, ey1, ez1 = data1[index][:]
            ex2, ey2, ez2 = data2[idx][:]
            print(f'({x1}, {y1}, {z1}, {data1[index]}, {closest_point[0]}, {closest_point[1]}, {closest_point[2]}, {data2[idx]})')

def merge_data(coords1, coords2, data1, data2):
    # Defining histograms for data quality monitoring
    hist_x = []
    hist_y = []
    hist_z = []
    delta_x = []
    delta_y = []
    delta_z = []
    delta_x2 = []
    delta_y2 = []
    delta_z2 = []
    delta_data = []
    delta_data_X = []
    delta_data_Y = []
    delta_data_Z = []
    # Build KD-tree from the points
    kdtree = KDTree(coords2)
    with open('combined_data.txt', 'w') as combined_file:
        for index, (x1, y1, z1) in enumerate(coords1):
            tmp = np.array([x1, y1, z1])
            # Query the KD-tree for the closest point to the user-defined coordinate
            dist, idx = kdtree.query(tmp)
            # Closest point
            closest_point = coords2[idx]
            if (abs(x1 - closest_point[0]) <= x_tolerance) and (abs(y1 - closest_point[1]) <= y_tolerance) and (abs(z1 - closest_point[2]) <= z_tolerance):
                ex1, ey1, ez1 = data1[index][:]
                ex2, ey2, ez2 = data2[idx][:]
                # print(f'({x1}, {y1}, {z1}; {closest_point[0]}, {closest_point[1]}, {closest_point[2]}; {data1[index][1]}, {data2[idx][1]})')
                hist_x.append(x1)
                hist_y.append(y1)
                hist_z.append(z1)
                delta_x.append(x1 - closest_point[0])
                delta_y.append(y1 - closest_point[1])
                delta_z.append(z1 - closest_point[2])
                delta_data.append(ey1 - ey2)
                # Write into .txt files (both combined, and .grd+.dat file for Allpix input for interpolation)
                combined_file.write(f"{x1}, {y1}, {z1}, {ex1}, {ey1}, {ez2}\n")
                # Saving some quantities for data-quality monitoring
                if((abs(x1 - closest_point[0]) >= 0) and (abs(x1 - closest_point[0]) <= x_tolerance)):
                    delta_x2.append(x1 - closest_point[0])
                    delta_data_X.append(ey1 - ey2)
                if((abs(y1 - closest_point[1]) >= 0) and (abs(y1 - closest_point[1]) <= y_tolerance)):
                    delta_y2.append(y1 - closest_point[1])
                    delta_data_Y.append(ey1 - ey2)
                if((abs(z1 - closest_point[2]) >= 0) and (abs(z1 - closest_point[2]) <= z_tolerance)):
                    delta_z2.append(z1 - closest_point[2])
                    delta_data_Z.append(ey1 - ey2)
    # Plotting quantities for data quality monitoring
    plot_hist(delta_x, 'DeltaX', 30)
    plot_hist(delta_y, 'DeltaY', 30, False, True)
    plot_hist(delta_z, 'DeltaZ', 30)
    plot_hist(delta_data, 'DeltaEy', 100, True)
    plot_hist(hist_x, 'CoordX', 200)
    plot_hist(hist_y, 'CoordY', 500)
    plot_hist(hist_z, 'CoordZ', 200)
    plot_scatter(delta_x2, delta_data_X, 'DeltaX', 'Ey')
    plot_scatter(delta_y2, delta_data_Y, 'DeltaY', 'Ey')
    plot_scatter(delta_z2, delta_data_Z, 'DeltaZ', 'Ey')

file1 = 'EField_YX.txt'
file2 = 'EField_YZ.txt'
(coord1, data1) = read_coordinates(file1)
(coord2, data2) = read_coordinates(file2)
merge_data(coord1, coord2, data1, data2)
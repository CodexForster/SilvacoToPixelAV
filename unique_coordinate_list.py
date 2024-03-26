import csv

def read_coordinates(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        return [(float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])) for row in reader if row]

def compare_coordinates(coords1, coords2, x_tolerance, y_tolerance, z_tolerance):
    for x1, y1, z1, ex1, ey1, ez1 in coords1:
        for x2, y2, z2, ex2, ey2, ez2 in coords2:
            if z1>0.0:
                if abs(x1 - x2) <= x_tolerance and abs(y1 - y2) <= y_tolerance and abs(z1 - z2) <= z_tolerance:
                    print(f'({x1}, {y1}, {z1}, {ex1}, {ey1}, {ez1}, {x2}, {y2}, {z2}, {ex2}, {ey2}, {ez2})')

def unique_coordinates(filename, filetype):
    with open(filename, 'r') as f:
        if(filetype=='space'):
            data = f.readlines()
        elif(filetype=='csv'):
            reader = csv.reader(f)
            data = list(reader)
    x_coords = set()
    y_coords = set()
    z_coords = set()
    for line in data:
        if(filetype=='space'):
           x, y, z = line.split()[:3]  # get the first three values from each line
        elif(filetype=='csv'):
            x, y, z = line[:3]  # get the first three values from each line
        x_coords.add(float(x))
        y_coords.add(float(y))
        z_coords.add(float(z))
    x_coords = sorted(list(x_coords))
    y_coords = sorted(list(y_coords))
    z_coords = sorted(list(z_coords))
    return x_coords, y_coords, z_coords

task = 2

if (task==1):
    file1 = 'EField_YX.txt'
    file2 = 'EField_YZ.txt'
    x_tolerance = 0.25
    y_tolerance = 0.001
    z_tolerance = 0.025

    coords1 = read_coordinates(file1)
    coords2 = read_coordinates(file2)
    compare_coordinates(coords1, coords2, x_tolerance, y_tolerance, z_tolerance)

elif (task==2):
    file1 = 'EField_YX.txt'
    file2 = 'combined_data.txt'
    x_coords, y_coords, z_coords = unique_coordinates(file1, 'space')

    print("Unique X coordinates:", x_coords)
    print("=====================================")
    print("Unique Y coordinates:", y_coords)
    print("=====================================")
    print("Unique Z coordinates:", z_coords)
    print("=====================================")

    x_coords, y_coords, z_coords = unique_coordinates(file2, 'csv')
    print("Unique X coordinates:", x_coords)
    print("=====================================")
    print("Unique Y coordinates:", y_coords)
    print("=====================================")
    print("Unique Z coordinates:", z_coords)
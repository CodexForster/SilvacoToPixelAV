# Original author: Marco Bomben, https://docs.google.com/document/d/1_cMVVW3Z-kzEkRnzKBCPwtvXYCGjXNB8bO0RWyMA2pk/edit
# Modified by:     Danush Shekar, UIC (1 April, 2024) 

import os
import sys
import argparse
import re

# argument parser
def argumentParser(arguments):
  parser = argparse.ArgumentParser()
  parser.add_argument("--output",help="output file name",required=True)
  parser.add_argument("--input",nargs="+",action="append",help="input file names",required=True)
  parser.add_argument("--ncoord",nargs=1,help="space dimensions",default=3,type=int)
  parser.add_argument("--nproject",nargs=1,help="number of observable projections",default=3,type=int)


  args = parser.parse_args(arguments)


  return args

def file_exists(file_name):
  file_existence = os.path.exists(file_name)
  if not file_existence:
        print("%s does not exist" % (file_name))
  return file_existence

def get_file_size(file_name):
  file_size = os.path.getsize(file_name)
  if ( file_size == 0 ):
    print("%s has zero size" % (file_name))
  return file_size

def check_number_of_lines(nlines_input_file):
  nfiles = len(nlines_input_file)
  if (nlines_input_file != 1):
    for i in range(1,nfiles):
      if ( nlines_input_file[i-1] != nlines_input_file[i] ):
        print("Mismatch in number of lines")
        return i
  else:
    return 0
  return 0

def merge_maps(input_file_names,output_file_name,ncoord,nproject):


  #print("ncoord:")
  #print(ncoord)
  #print("\n\n\n")

  # reading input files
  input_file_lines = []
  nlines_input_file = []
  for input_file in input_file_names:
    with open(input_file,'r') as original:
      original_lines = original.readlines()
      nlines = len(original_lines)
      input_file_lines.append(original_lines)
      nlines_input_file.append(nlines)

  #print(nlines_input_file)
  #print("len(input_file_lines):")
  #print(len(input_file_lines))
  #print("\n\n\n")
  #print("input_file_lines:")
  #print(input_file_lines)
  #print("\n\n\n")

  # check if the files have all the same number of lines
  i = check_number_of_lines(nlines_input_file)
  if ( i ):
    print("%s and %s have different number of lines: %d vs %d\nExiting..." % (input_file_names[i-1],input_file_names[i],nlines_input_file[i-1],nlines_input_file[i]) )
    exit(i)
 
  # writing output file
  with open(output_file_name,'w') as ofile:
    for line_index in range(nlines_input_file[0]):
      # the list to be written in the output file
      outputlist = []
      # first the coordinates
      split_line = (input_file_lines[0])[line_index]
      coordinates = (split_line.split())
      coordinate_values = []
      for k in range(ncoord):
        coordinate_values.append(float(coordinates[k]))
      #print("coordinates:")
      #print(len(coordinate_values))
      #print(coordinate_values)
      #print("\n\n\n")
      for l in range(len(coordinate_values)):
        outputlist.append(coordinate_values[l])
      # then the observable projections
      for j in range(nproject):
        observable = float((((input_file_lines[j])[line_index]).split())[-1])
        # adding the observable projections
        outputlist.append(observable)
      #print(outputlist)
      ofile.write(' '.join(str(value) for value in outputlist))
      ofile.write('\n')




if __name__ == "__main__":
  args = argumentParser(sys.argv[1:])
  output_file_name  = args.output
  #print(output_file_name)
  input_file_names  = args.input[0]
  ncoord = int(args.ncoord)
  nproject = int(args.nproject)
  #print(input_file_names)

  if (len(input_file_names) != (nproject)):
    print("Number of input files should be equal to number of observable projections\nExiting...");
    exit(1)
  merge_maps(input_file_names,output_file_name,ncoord,nproject)
  print("\nmerged file is: %s" % (output_file_name))  


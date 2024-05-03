# Original author: Marco Bomben, https://docs.google.com/document/d/1_cMVVW3Z-kzEkRnzKBCPwtvXYCGjXNB8bO0RWyMA2pk/edit
# Modified by:     Danush Shekar, UIC (1 April, 2024) 

import argparse
import sys
import os.path
import re

# argument parser
def argumentParser(arguments):
  parser = argparse.ArgumentParser()
  parser.add_argument("--prefix",help="2D map name prefix",required=True)
  parser.add_argument("--suffix",help="2D map name suffix",required=True)
  parser.add_argument("--outputname",help="3D map output file name",required=True)
  parser.add_argument("--zmin",help="zmin",type=float,required=True)
  parser.add_argument("--zmax",help="zmax",type=float,required=True)
  parser.add_argument("--step",help="step",type=float,required=True)

  args = parser.parse_args(arguments)


  return args


if (__name__ == "__main__" ):
  args = argumentParser(sys.argv[1:])

  # we loop over all 2D electric field maps to create a single 3D file that merges all the 2D slices

  # prefix of the 2D map
  prefix = args.prefix
  # suffix of the 2D map
  suffix = args.suffix
  # 3D map output filename
  outputname = args.outputname
  zmin = args.zmin
  zmax = args.zmax
  stepZ = args.step

  tmpzmin = int(zmin*100)
  tmpzmax = int(zmax*100)
  tmpstepZ= int(stepZ*100)

  # let's open the file to write
  with open(outputname,'w') as fout:
    # loop over all z positions
    for iter, tmpz in enumerate(range(tmpzmin,tmpzmax+tmpstepZ, tmpstepZ)):
      z = round(tmpz/100,2)
      if(tmpz>tmpzmax):
        z = round(tmpzmax/100,2)
      # the name of the 2D map file for the actual X value
      Slice2D = prefix + str(iter) + suffix
      #print(Slice2D)
      if os.path.exists(Slice2D):
        print(Slice2D + " exists")
        #after having checked the file exists we read it line by line
        with open(Slice2D,'r') as fin:
          finlines = fin.readlines()
          #print(finlines)
          # now loop over each line to extrac the x and y coordinates and the observable
          for finline in finlines:
            # remove trailing new line
            finline.rstrip()
            # split to extract the values
            buff = finline.split()
            x = float(buff[0])
            y = float(buff[1])
            o = float(buff[2])
            # write the result in the output file, including the z component
            fout.write(("%f %f %f %f\n") % (x,y,z,o))
  
  print("3D output map is available here: %s" % (outputname))



import argparse
import sys
import os.path
import re
#import numpy

# argument parser
def argumentParser(arguments):
  parser = argparse.ArgumentParser()
  parser.add_argument("--template",help="set template file",required=True)
  parser.add_argument("--set",help="set file name",required=True)
  parser.add_argument("--TwoDname",help="2d map output file name",required=True)
  parser.add_argument("--ThreeDname",help="3d map input file name",required=True)
  parser.add_argument("--zmin",help="zmin",type=float,required=True)
  parser.add_argument("--zmax",help="zmax",type=float,required=True)
  parser.add_argument("--step",help="step",type=float,required=True)


  args = parser.parse_args(arguments)


  return args




if (__name__ == "__main__" ):
  args = argumentParser(sys.argv[1:])
  #print(args.TwoDname)

  # we now write a series of cut files, one per z value between zmin and zmax
  # the program will also print out a series of commands for tonyplot3d to extract the 2d maps

  # getting the arguments into variables
  # set template file
  templateFileName = args.template
  #print(templateFileName)
  # set file base name
  baseSetFileName = args.set
  #print(baseSetFileName)
  # 2D map name
  map2Dname = args.TwoDname
  # 3D map name
  map3Dname = args.ThreeDname
  zmin = args.zmin
  zmax = args.zmax
  stepZ = args.step

  tmpzmin = int(zmin*100)
  tmpzmax = int(zmax*100)
  tmpstepZ= int(stepZ*100)

  # auxiliary variables for ELEV calculation
  ymin = 1
  ymax = -1

  # preparing the different components of the filenames to be handled

  (dirName, fileName) = os.path.split(templateFileName)
  (fileBaseName, fileExtension)=os.path.splitext(fileName)
  #print (dirName)   
  #print (fileName)  
  #print (fileBaseName)    
  #print (fileExtension) 

  # keywords to be searched in the set template file
  pointHeader = "point_" 
  ELEVHeader = "ELEV"

  # open set template file for reading

  with open(templateFileName) as fin:
    inputLines = fin.readlines()
  #print(inputLines)

  # printing the command used to run the program
  print("#File produced using the following command:")
  print(("#python %s %s") % (sys.argv[0],(' '.join(f'--{k} {v}' for k, v in vars(args).items()))))

  # loop over all the z values to write out all the cut files and print the commands to run 
  # the projections to planes at fixed z value

  for iter, tmpz in enumerate(range(tmpzmin,tmpzmax+tmpstepZ, tmpstepZ)):
    # set output file name
    z = round(tmpz/100,2)
    if(tmpz>tmpzmax):
      z = round(tmpzmax/100,2)
    #setFileName = baseSetFileName + str(iter) + fileExtension
    integer_part, decimal_part = str(z).split('.')
    tempstr = integer_part+'P'+decimal_part
    setFileName = baseSetFileName + str(iter) + fileExtension
    # set output file name
    #print(setFileName)
    # open the set file in write mode
    with open(setFileName,'w') as fout:
      # read each line of the set template file
      for inputLine in inputLines:
        # look for keywords:
        # first is point_ header
        if (re.search(pointHeader,inputLine)):
          #print(("%s found in %s") % (pointHeader,inputLine))
          # write the point_ position with the z coordinate
          fout.write(("%s %.2f\n") % (inputLine.rstrip(),z))
        # second is the ELEV header
        elif(re.search(ELEVHeader,inputLine)):
          #print(("%s found in %s") % (ELEVHeader,inputLine))
          y = (ymax-ymin)*(z-zmin)/(zmax-zmin) + ymin
          fout.write(("%s %f\n") % (inputLine.rstrip(),y))
        # all other kid of lines - i.e. containing no keywords - will be just copied  
        else:
          fout.write(inputLine)
    print(("tonyplot3d -nohw %s -set %s -cut %s%d.str") % (map3Dname,setFileName,map2Dname,iter))

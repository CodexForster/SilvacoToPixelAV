# ========================
# ELECTRIC FIELD GEN - FST
# ========================
cd xy_extract
python3 extract-2D.py --template template_E_Field_Z.set --set  cutZ_ --TwoDname map2Dz_ --ThreeDname ../cmsPixel_50x13_postBias_-100V.str --zmin 0 --zmax 6.25 --step 0.1 > allCuts.txt
# check if the ELEV value in cutZ_i has the correct sign. Can differ in tonyplot versions.
source allCuts.txt
# Edit loop_Ei.in depending on the number of cuts
deckbuild -run loop_Ex.in -outfile loop_Ex.out &
deckbuild -run loop_Ey.in -outfile loop_Ey.out &
deckbuild -run loop_Ez.in -outfile loop_Ez.out &
python3 create-3D-map.py --prefix map2Dz_ --suffix _EFieldX.dat --outputname E_FieldX.dat --zmin 0 --zmax 6.25 --step 0.1
python3 create-3D-map.py --prefix map2Dz_ --suffix _EFieldY.dat --outputname E_FieldY.dat --zmin 0 --zmax 6.25 --step 0.1
python3 create-3D-map.py --prefix map2Dz_ --suffix _EFieldZ.dat --outputname E_FieldZ.dat --zmin 0 --zmax 6.25 --step 0.1
# important to pass inputs in this order
python merge_maps.py --output EField_YX.txt --input E_FieldX.dat E_FieldY.dat E_FieldZ.dat

python3 extract-2D.py --template template_E_Field_X.set --set  cutX_ --TwoDname map2Dx_ --ThreeDname ../cmsPixel_50x13_postBias_-100V.str --zmin 0 --zmax 25 --step 0.5 > allCuts.txt
source allCuts.txt
# Edit loop_Ei.in depending on the number of cuts
deckbuild -run loop_Ex.in -outfile loop_Ex.out &
deckbuild -run loop_Ey.in -outfile loop_Ey.out &
deckbuild -run loop_Ez.in -outfile loop_Ez.out &
python3 create-3D-map.py --prefix map2Dx_ --suffix _EFieldX.dat --outputname E_FieldX.dat --zmin 0 --zmax 25 --step 0.5
python3 create-3D-map.py --prefix map2Dx_ --suffix _EFieldY.dat --outputname E_FieldY.dat --zmin 0 --zmax 25 --step 0.5
python3 create-3D-map.py --prefix map2Dx_ --suffix _EFieldZ.dat --outputname E_FieldZ.dat --zmin 0 --zmax 25 --step 0.5
# important to pass inputs in this order
python merge_maps.py --output EField_YZ.txt --input E_FieldX.dat E_FieldY.dat E_FieldZ.dat

# gen final efield & grid files from silvaco data
# EField_YX.txt and EField_YZ.txt are generated from the prev steps and should be stored in prodname folder
python3 gen_gridAndFieldFile.py --prodname silvaco50x13
# Validation - copy the relecant mesh and wgt_pot files (Raw data, no header files) to validation folder
python3 validation/validateSilvacoData.py -e

# ========================
# WEIGHTING POTENTIAL GEN - FST
# ========================
cp ./cmsPixel_postBias_1V.str ./extract/
python3 extract-2D.py --template template_E_Field_Z.set --set  cutZ_ --TwoDname map2Dz_ --ThreeDname ../cmsPixel_postBias_1V.str --zmin 0 --zmax 31.25 --step 1 > allCuts.txt
# check if the ELEV value in cutZ_i has the correct sign. Can differ in tonyplot versions.
source allCuts.txt
# Edit loop_Ex.in depending on the number of cuts
deckbuild -run loop_Ex.in -outfile loop_Ex.out &
python3 create-3D-map.py --prefix map2Dz_ --suffix _Potential.dat --outputname Potential_YX.dat --zmin 0 --zmax 31.25 --step 1
# copy to prodname folder
cp ./Potential_YX.dat ../../Potential_YX.dat
# Potential_YX.txt is generated from the prev step and should be stored in prodname folder
python3 gen_wgtpotGridAndPotFile.py --prodname silvaco50x13wgt
# check if the last five coordinates and potential values match
# Validation - copy the relecant mesh and wgt_pot files (Raw data, no header files) to validation folder
python3 validateSilvacoData.py -w

# ========================
# INTERPOLATION - LOCAL
# ========================
# export is optional, 100 in last run-line stands for the bias voltage
export PATH=$PATH:/Users/danush/Documents/PixelAV/silvaco_datagen/recipes_c-ansi/lib/
gcc gen_efield.c -o gen_efield -I ./recipes_c-ansi/include/ -I ./recipes_c-ansi/lib/ -I ./recipes_c-ansi/recipes/ ./recipes_c-ansi/lib/librecipes_c.a -lm
./gen_efield silvaco50x13 100

# gen wpot
gcc gen_wpot.c -o gen_wpot -I ./recipes_c-ansi/include/ -I ./recipes_c-ansi/lib/ -I ./recipes_c-ansi/recipes/ ./recipes_c-ansi/lib/librecipes_c.a -lm
./gen_wpot silvaco50x13wgt 1

# Note 1: You might have to change the NSTACK size, array initialization size based on the no. of vertices your TCAD data has. I also had commented out the plotting part of code as it looked for field from specific points in the midplane.
# Note 2: recipes_c-ansi needs to be compiled and built:
# change LIBDIR (line 21) in Makefile to lib/ which is a folder you will make in recipes_c-ansi. Then remove the comment on first line of file "airy.c" in recipes_c-ansi/recipes/. Then run make. (I also had to change gnumake to make).

# IMPORTANT: Don't forget to add the header files after making the interpolated data.

# ========================
# TRACK GENERATION - LOCAL
# ========================
# If using conda env: myenv, no need of sourcing thisroot.sh
source /opt/homebrew/bin/thisroot.sh 
g++ -o genlist generate_cluster_inputs_low_pt.cxx `root-config --cflags --glibs`
./genlist

# ========================
# PIXELAV DATA GEN - LPC
# ========================
gcc -c ppixelav2_list_trkpy_n_2f.c
gcc -o pixelavrun ppixelav2_list_trkpy_n_2f.o -lm
ln -s ./dot1_50x13_phase3_100v_263k.init ppixel2.init
ln -s ./weighting_BPix_50x13x100.init wgt_pot.init
./pixelavrun 


# example output for gen_efield
# danush@danush silvaco_datagen % ./gen_efield silvaco50x13 100
# Grid file = silvaco50x13/silvaco50x13_msh.grd, dessis plot file = silvaco50x13/silvaco50x13_100_des.dat
# number of vertices = 47652
# detector dimensions = 25.000000 6.250000 100.000000 um 
# field = 441.889000 433.236000 -16.666500 V/cm 
# enter the number of output grid points in each dim: nx[21], ny[21], nz[92]
# 26 13 51
# (nx, ny, nz) = (26, 13, 51)
# total Lorentz Drift = 0.000000, average efield = nan 
# enter zmin (E = 0 for z>zmin) 
# 100
# zmin = 100.000000 um

# example output for gen_wpot
# danush@danush silvaco_datagen % ./gen_wpot silvaco50x13wgt 1
# Grid file = silvaco50x13wgt/silvaco50x13wgt_msh.grd, dessis plot file = silvaco50x13wgt/silvaco50x13wgt_1_des.dat
# number of vertices = 15444
# first node = 0.000000, last node = 0.000000 
# detector dimensions = 125.000000 31.250000 2.000000 um 
# enter the number of 1/2 pixels in each direction [5]
# 5
# enter the number of output grid points in each dim: nx[21], ny[21], nz[92]
# 26 13 51
# (nx, ny, nz) = (26, 13, 51)
# enter the x y coordinates and tolerance for plot axis
# 2 2 1

# example output for cluster generation
# (rootenv) [cmspixelsim@localhost generate_cluster_inputs]$ ./genlist 
# enter run number, flipped (0/1/2), number of clusters 
# 1 0 2000000
# opening file pt_cluster_cotangles_bp1_000001.txt
# 0.030500 0.000609 
# 0.040500 0.007572 
# 0.050500 0.016002 ...
# 2.090500 0.999677 
# Info in <TCanvas::Print>: pdf file pt_clust.pdf has been created
# Info in <TCanvas::Print>: Current canvas added to pdf file pt_clust.pdf
# Info in <TCanvas::SaveSource>: C++ Macro file: pt_course.C has been generated
# Info in <TCanvas::Print>: Current canvas added to pdf file pt_clust.pdf
# Info in <TCanvas::Print>: pdf file pt_clust.pdf has been closed

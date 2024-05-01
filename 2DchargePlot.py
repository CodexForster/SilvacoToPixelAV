# Original author: https://github.com/nhanvtran/directional-pixel-detectors/blob/main/datagen.py
# Modified by:     Danush Shekar, UIC (25 April, 2024) 
# Description:     Parses PixelAV ouput files and also makes 2D plots of charge deposition in sensor array

import sys
import numpy as np
import pandas as pd
import ROOT
import matplotlib.pyplot as plt
import langaus
import optparse

parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-p', '--prodname', dest='filename', help="The name of PixelAV dataset")
options, args = parser.parse_args()

filename = options.filename


def parseFile(filein,tag,nevents=-1):

        with open(filein) as f:
            lines = f.readlines()

        header = lines.pop(0).strip()
        pixelstats = lines.pop(0).strip()

        print("Header: ", header)
        print("Pixelstats: ", pixelstats)

        clusterctr = 0
        b_getclusterinfo = False
        b_geteventinfo = False
        # instantiate 4-d np array [cluster number, time slice, pixel row, pixel column]
        events = []
        cur_slice = []
        cluster_truth =[]

        for line in lines:
            ## Get cluster truth information
            if "<cluster>" in line:
                clusterctr += 1
                b_geteventinfo = False
                b_getclusterinfo = True
                if(len(cur_slice)!=0):
                    events.append(np.array(cur_slice))
                    cur_slice = []
                continue
            if b_getclusterinfo:
                cluster_truth.append(line.strip().split())
                b_getclusterinfo = False
            if "time slice 4000.000000 ps" in line:
                b_geteventinfo = True
                continue
            if b_geteventinfo == True:
                cur_row = line.strip().split()
                cur_slice.append([float(item) for item in cur_row])

        print("Number of pixel rows = ", len(events[0]))
        print(np.array(events).shape)
        print("Number of events = ", clusterctr, " or ", len(events))


        arr_truth = np.array(cluster_truth)
        arr_events = np.array(events)

        #convert into pandas DF
        df = {}
        #truth quantities - all are dumped to DF
        df = pd.DataFrame(arr_truth, columns = ['x-entry', 'y-entry','z-entry', 'n_x', 'n_y', 'n_z', 'number_eh_pairs', 'y-local', 'pt'])
        df['n_x']=df['n_x'].astype(float)
        df['n_y']=df['n_y'].astype(float)
        df['n_z']=df['n_z'].astype(float)
        
        #added angular variables
        #df['spherR'] = df['n_x']**2 + df['n_y']**2 + df['n_z']**2
        #df['theta'] = np.arccos(df['n_z']/df['spherR'])*180/math.pi
        #df['phi'] = np.arctan2(df['n_y'],df['n_x'])*180/math.pi
        #df['cosPhi'] = np.cos(df['phi'])
        df['cotAlpha'] = df['n_x']/df['n_z']
        df['cotBeta'] = df['n_y']/df['n_z']
        df.to_csv("labels_"+filename+".csv", index=False)

        return arr_events, arr_truth

def main():
        
    i = int(sys.argv[1])
    tag = "d"+str(i)
    arr_events, arr_truth = parseFile(filein="Runs/"+filename+".out",tag=tag)
    original_shape = arr_events.shape

    # first_event = arr_events[3] # 2, 3, 6

    # plt.imshow(first_event, cmap='Reds', interpolation='nearest')
    # plt.colorbar()
    # plt.show()

    arranged_events = arr_events.reshape(original_shape[0], -1)

    print("The shape of the event array: ", arranged_events.shape)
    print("The ndim of the event array: ", arranged_events.ndim)
    print("The dtype of the event array: ", arranged_events.dtype)
    print("The size of the event array: ", arranged_events.size)
    print("The max value in the array is: ", np.amax(arranged_events))
    print("The shape of the truth array: ", arr_truth.shape)

    df2 = {}
    max_val = []
    print("Setting up Langaus")
    fit = langaus.LanGausFit()
    print("Setup Langaus")
    canvas = ROOT.TCanvas("cv","cv",1000,800)
    hist = ROOT.TH1F("maxCharge", "Histogram of maximum total-charge induced in a pixel", 20000, 0, 20000)
    for iter in range(arranged_events.shape[0]):
        hist.Fill(np.amax(arranged_events[iter,:]))
    

    myMean = hist.GetMean()
    myRMS = hist.GetRMS()
    value = myMean            
    hist.Rebin(40)
    myLanGausFunction = fit.fit(hist, fitrange=(myMean-1.5*myRMS,myMean+3*myRMS))
    myMPV = myLanGausFunction.GetParameter(1)
    value = myMPV
    #For Debugging
    hist.Draw("hist")
    myLanGausFunction.Draw("same")
    hist.GetXaxis().SetTitle("Charge [e]")
    hist.GetYaxis().SetTitle("Counts")
    canvas.SaveAs("Runs/Charge_Histogram_"+filename+".png")

    #df2 is a df with the reconstructed clusters
    df2 = pd.DataFrame(arranged_events)
    df2.to_csv("recon_"+filename+".csv", index = False)

if __name__ == "__main__":
    main()

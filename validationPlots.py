import sys
import numpy as np
import pandas as pd
import ROOT
import matplotlib.pyplot as plt
import langaus
import optparse

parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-p', '--prodname', dest='filename', help="The name of 1st PixelAV dataset")
parser.add_option('-c', '--prodname2', dest='filename2', help="The name of 2nd PixelAV dataset")
options, args = parser.parse_args()

filename = options.filename
filename2 = options.filename2

def delta_histograms(arr1, arr2, name, unit):
    delta = np.array(arr1) - np.array(arr2)
    canvas = ROOT.TCanvas("cv","cv",1000,800)
    hist_tmp = ROOT.TH1F(name, "Hist", 40, -20, 20)
    for iter in range(len(delta)):
        hist_tmp.Fill(delta[iter])
    myMean = hist_tmp.GetMean()
    myRMS = hist_tmp.GetRMS()
    hist_tmp.Draw("hist")
    ROOT.gStyle.SetOptStat(1);
    hist_tmp.GetXaxis().SetTitle("Delta "+name+" ["+unit+"]")
    hist_tmp.GetYaxis().SetTitle("Counts")
    canvas.SaveAs("./delta_"+name+"_hist.png")
    canvas.Clear()

def single_histogram(arr,  name, unit, doFit=False, iter=1):
    canvas = ROOT.TCanvas(f"cv_{iter}", f"cv_{iter}",1000,800)
    hist_tmp = ROOT.TH1F(f'{name}', "Hist", 100, np.amin(arr), np.amax(arr))
    for value in arr:
        hist_tmp.Fill(value)
    myMean = hist_tmp.GetMean()
    myRMS = hist_tmp.GetRMS()
    hist_tmp.SetLineColor(1)
    hist_tmp.Draw("hist")
    if doFit:
        print("Setting up Langaus")
        fit = langaus.LanGausFit()
        print("Setup Langaus")
        myLanGausFunction = fit.fit(hist_tmp, fitrange=(myMean-1.5*myRMS,myMean+3*myRMS))
        myLanGausFunction.SetLineColor(1)
        myLanGausFunction.Draw("same")
    ROOT.gStyle.SetOptStat(1)
    ROOT.gStyle.SetOptFit(1111)
    hist_tmp.GetXaxis().SetTitle(name+" ["+unit+"]")
    hist_tmp.GetYaxis().SetTitle("Counts")
    canvas.SaveAs("./"+name+"_hist.png")
    canvas.Clear()

def analyze(event, threshold):
    maxCh = np.amax(event)
    (maxCh_idx, maxCh_idy) = np.unravel_index(np.argmax(event), event.shape)
    # if (maxCh<threshold):
    #     print("max ch less than threshold, warning.")
    #     maxCh=0
    #     maxCh_idx=0
    #     maxCh_idy=0
    max2Ch, (max2Ch_idx, max2Ch_idy) = find_second_max(event)
    # if (max2Ch<threshold):
    #     print("max2 ch less than threshold, warning.")
    #     max2Ch=0
    #     max2Ch_idx=0
    #     max2Ch_idy=0
    x_span, y_span = find_span(event, threshold)
    area = count_above_threshold(event, threshold)
    return maxCh, maxCh_idx, maxCh_idy, max2Ch, max2Ch_idx, max2Ch_idy, x_span, y_span, area

def count_above_threshold(arr, threshold):
    return np.sum(arr > threshold)

def find_span(arr, threshold):
    # Get the indices of non-zero elements
    indices = np.nonzero(arr > threshold)
    # Get the minimum and maximum indices
    x_min, x_max = np.min(indices[0]), np.max(indices[0])
    y_min, y_max = np.min(indices[1]), np.max(indices[1])
    # Calculate the spans
    x_span = x_max - x_min + 1
    y_span = y_max - y_min + 1
    print("x, y span = ",x_span, ", ", y_span)
    return x_span, y_span

def find_second_max(arr):
    # Flatten the array and find the second maximum value
    flat = arr.flatten()
    second_max_val = np.partition(flat, -2)[-2]
    # Find the index of the second maximum value in the flattened array
    second_max_idx_flat = np.argpartition(flat, -2)[-2]
    # Convert the index in the flattened array to the index in the original array
    (second_max_idx, second_max_idy) = np.unravel_index(second_max_idx_flat, arr.shape)
    return second_max_val, (second_max_idx, second_max_idy)

def parse_file(filein, threshold):
    with open(filein) as f:
        lines = f.readlines()

    header = lines.pop(0).strip()
    pixelstats = lines.pop(0).strip()

    print("Header: ", header)
    print("Pixelstats: ", pixelstats)
    events = []
    maxCharge = []
    maxCharge_idx = []
    maxCharge_idy = []
    max2Charge = []
    max2Charge_idx = []
    max2Charge_idy = []
    xSpan = []
    ySpan = []
    Area = []
    cur_event = []
    cluster_truth = []
    b_geteventinfo = False
    b_getclusterinfo = False

    for line in lines:
        if "<time slice 4000" in line:
            cur_event = []
            b_geteventinfo = True
            continue
        if "<cluster>" in line:
            b_geteventinfo = False
            b_getclusterinfo = True
            if cur_event:  # Only append if cur_event is not empty
                maxCh, maxCh_idx, maxCh_idy, max2Ch, max2Ch_idx, max2Ch_idy, x_span, y_span, area = analyze(np.array(cur_event), threshold)
                maxCharge.append(maxCh)
                maxCharge_idx.append(maxCh_idx)
                maxCharge_idy.append(maxCh_idy)
                max2Charge.append(max2Ch)
                max2Charge_idx.append(max2Ch_idx)
                max2Charge_idy.append(max2Ch_idy)
                xSpan.append(x_span)
                ySpan.append(y_span)
                Area.append(area)
                events.append(np.array(cur_event))
            cur_event = []
            continue
        if b_getclusterinfo:
                cluster_truth.append(line.strip().split())
                b_getclusterinfo = False
        if b_geteventinfo == True:
                cur_event.append([float(i) for i in line.strip().split()])

    # Handle the last event
    if cur_event:
        events.append(np.array(cur_event))
    # Convert list of arrays to a 3D numpy array
    events = np.array(events)
    return (events, maxCharge, maxCharge_idx, maxCharge_idy, max2Charge, max2Charge_idx, max2Charge_idy, xSpan, ySpan, Area)

def main():

    (arr_events, maxCharge, maxCharge_idx, maxCharge_idy, max2Charge, max2Charge_idx, max2Charge_idy, xSpan, ySpan, Area) = parse_file(filein="../Runs/"+filename+".out", threshold=10)
    print("Done analyzing dataset 1.")
    (arr_events2, maxCharge2, maxCharge_idx2, maxCharge_idy2, max2Charge2, max2Charge_idx2, max2Charge_idy2, xSpan2, ySpan2, Area2) = parse_file(filein="../Runs/"+filename2+".out", threshold=10)
    print("Done analyzing dataset 2.")

    print("The shape of the event array 1: ", arr_events[0].shape)
    print("The ndim of the event array 1: ", len(arr_events))
    print("The max value in the array 1 is: ", np.amax(arr_events))

    print("The shape of the event array 2: ", arr_events2[0].shape)
    print("The ndim of the event array 2: ", len(arr_events2))
    print("The max value in the array 2 is: ", np.amax(arr_events2))

    if len(arr_events) != len(arr_events2):
        print("\n\n\t WARNING WARNING WARNING")
        print("\n\nThe two datasets have different number of events. This will lead to incorrect comparison.\n\n")

    # delta_histograms
    # delta_hists1 = [maxCharge_idx, maxCharge_idy, max2Charge_idx, max2Charge_idy]
    # delta_hists2 = [maxCharge_idx2, maxCharge_idy2, max2Charge_idx2, max2Charge_idy2]
    # delta_hist_names = ['maxCharge_idx', 'maxCharge_idy', 'max2Charge_idx', 'max2Charge_idy']
    # delta_hist_units = ['pixel', 'pixel', 'pixel', 'pixel']
    delta_hists1 = [xSpan, ySpan]
    delta_hists2 = [xSpan2, ySpan2]
    delta_hist_names = ['xSpan', 'ySpan']
    delta_hist_units = ['pixel', 'pixel']
    for i in range (len(delta_hists1)):
        delta_histograms(delta_hists1[i], delta_hists2[i], delta_hist_names[i], delta_hist_units[i])

    single_hists1 = [maxCharge, max2Charge, xSpan, ySpan, Area, maxCharge2, max2Charge2, xSpan2, ySpan2, Area2]
    single_hist_names = ['maxCharge', 'max2Charge', 'xSpan', 'ySpan','Area', 'maxCharge2', 'max2Charge2', 'xSpan2', 'ySpan2', 'Area2']
    single_hist_doFit= [True, True, False, False, False, True, True, False, False, False]
    single_hist_units = ['e', 'e', 'pixel', 'pixel', 'pixel^2', 'e', 'e', 'pixel', 'pixel', 'pixel^2']
    for i in range (len(single_hists1)):
        single_histogram(single_hists1[i], single_hist_names[i], single_hist_units[i], single_hist_doFit[i], i)
    

if __name__ == "__main__":
    main()



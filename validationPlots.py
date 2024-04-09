import sys
import numpy as np
import pandas as pd
import ROOT
import matplotlib.pyplot as plt
import langaus
import optparse
from scipy.spatial import KDTree

parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-p', '--prodname', dest='filename', help="The name of 1st PixelAV dataset")
parser.add_option('-c', '--prodname2', dest='filename2', help="The name of 2nd PixelAV dataset")
options, args = parser.parse_args()

filename = options.filename
filename2 = options.filename2


def analyze(event, threshold):
    sumCh = np.sum(event)
    maxCh = np.amax(event)
    x_span, y_span = find_span(event, threshold)
    area = count_above_threshold(event, threshold)
    return sumCh, x_span, y_span, area

def remove_unmatched_evts(arr_events, cluster_truth, sumCharge, xSpan, ySpan, Area, arr_events2, cluster_truth2, sumCharge2, xSpan2, ySpan2, Area2):
    # Convert all inputs to NumPy arrays
    arr_events = np.array(arr_events)
    cluster_truth = np.array(cluster_truth)
    sumCharge = np.array(sumCharge)
    xSpan = np.array(xSpan)
    ySpan = np.array(ySpan)
    Area = np.array(Area)
    arr_events2 = np.array(arr_events2)
    cluster_truth2 = np.array(cluster_truth2)
    sumCharge2 = np.array(sumCharge2)
    xSpan2 = np.array(xSpan2)
    ySpan2 = np.array(ySpan2)
    Area2 = np.array(Area2)

    # Build KD-trees for both arrays
    tree1 = KDTree(cluster_truth[:, 3:6].astype(float))
    tree2 = KDTree(cluster_truth2[:, 3:6].astype(float))
    
    # Query common points using the KD-trees
    distances, indices_array1 = tree1.query(cluster_truth2[:, 3:6].astype(float), k=1)
    
    # Filter out non-matching points based on distances
    common_indices_array2 = np.where(distances == 0)[0]
    common_indices_array1 = indices_array1[common_indices_array2]
    
    # Select common points from the original arrays
    tmp_arr_events = arr_events[common_indices_array1]
    tmp_cluster_truth = cluster_truth[common_indices_array1]
    tmp_sumCharge = sumCharge[common_indices_array1]
    tmp_xSpan = xSpan[common_indices_array1]
    tmp_ySpan = ySpan[common_indices_array1]
    tmp_Area = Area[common_indices_array1]
    
    tmp_arr_events2 = arr_events2[common_indices_array2]
    tmp_cluster_truth2 = cluster_truth2[common_indices_array2]
    tmp_sumCharge2 = sumCharge2[common_indices_array2]
    tmp_xSpan2 = xSpan2[common_indices_array2]
    tmp_ySpan2 = ySpan2[common_indices_array2]
    tmp_Area2 = Area2[common_indices_array2]

    return (tmp_arr_events, tmp_cluster_truth, tmp_sumCharge, tmp_xSpan, tmp_ySpan, tmp_Area, tmp_arr_events2, tmp_cluster_truth2, tmp_sumCharge2, tmp_xSpan2, tmp_ySpan2, tmp_Area2)


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
    # print("x, y span = ",x_span, ", ", y_span)
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

    counter = 0 # For running on mini dataset for debugging
    events = []
    sumCharge = []
    xSpan = []
    ySpan = []
    Area = []
    cur_event = []
    cluster_truth = []
    b_geteventinfo = False
    b_getclusterinfo = False

    for line in lines:
        # if (counter == 10):
        #     break
        if "<cluster>" in line:
            b_geteventinfo = False
            b_getclusterinfo = True
            if cur_event:  # Only append if cur_event is not empty
                counter += 1
                sumCh, x_span, y_span, area = analyze(np.array(cur_event), threshold)
                sumCharge.append(sumCh)
                xSpan.append(x_span)
                ySpan.append(y_span)
                Area.append(area)
                events.append(np.array(cur_event))
            cur_event = []
            continue
        if b_getclusterinfo:
                cluster_truth.append(line.strip().split())
                b_getclusterinfo = False
        if "<time slice 4000" in line:
            cur_event = []
            b_geteventinfo = True
            continue
        if b_geteventinfo == True:
                cur_event.append([float(i) for i in line.strip().split()])

    # Handle the last event
    if cur_event:
        events.append(np.array(cur_event))
    # Convert list of arrays to a 3D numpy array
    events = np.array(events)
    return (events, cluster_truth, sumCharge, xSpan, ySpan, Area)

def delta_histograms(arr1, arr2, name, unit):
    delta = np.array(arr1) - np.array(arr2)
    canvas = ROOT.TCanvas("cv","cv",1000,800)
    hist_tmp = ROOT.TH1F(name, 'delta '+f'{name}', 20, -10, 10)
    for iter in range(len(delta)):
        hist_tmp.Fill(delta[iter])
    myMean = hist_tmp.GetMean()
    myRMS = hist_tmp.GetRMS()
    hist_tmp.Draw("hist")
    ROOT.gStyle.SetOptStat(1)
    hist_tmp.SetTitle(name)
    hist_tmp.GetYaxis().SetTitleSize(0.03)
    hist_tmp.GetYaxis().SetLabelSize(0.03)
    hist_tmp.GetXaxis().SetTitle("Delta "+name+" ["+unit+"]")
    hist_tmp.GetYaxis().SetTitle("Counts")
    canvas.SaveAs("./delta_"+name+"_hist.png")
    canvas.Clear()

def single_histogram(arr, arr2, name, unit, maxbin, nbins, doFit=False, iter=1):
    canvas = ROOT.TCanvas(f"cv_{iter}", f"cv_{iter}",1000,800)
    # Create and fill the first histogram
    hist_tmp1 = ROOT.TH1F(f'{name}_1', f'{name}', nbins, 0, maxbin)
    for value in arr:
        hist_tmp1.Fill(value)

    # Create and fill the second histogram
    hist_tmp2 = ROOT.TH1F(f'{name}_2', f'{name}', nbins, 0, maxbin)
    for value in arr2:
        hist_tmp2.Fill(value)

    ROOT.gStyle.SetOptStat(0)  # Turn off automatic stats box
    hist_tmp1.GetXaxis().SetTitle(name+" ["+unit+"]")
    hist_tmp1.GetYaxis().SetTitle("Counts")
    hist_tmp1.SetLineColor(2)
    hist_tmp2.SetLineColor(1)
    hist_tmp1.Draw("hist")
    hist_tmp2.Draw("hist same")  # Draw the second histogram on the same canvas
    hist_tmp2.GetYaxis().SetTitleSize(0.03)
    hist_tmp2.GetYaxis().SetLabelSize(0.03)

    # Create text boxes to display statistics for each histogram
    stats1 = ROOT.TPaveText(0.7, 0.7, 0.9, 0.9, "NDC")
    stats1.AddText(f"Name: Silvaco")
    stats1.AddText(f"Mean: {hist_tmp1.GetMean():.2f} ± {hist_tmp1.GetMeanError():.2f}")
    stats1.AddText(f"Std Dev: {hist_tmp1.GetStdDev():.2f} ± {hist_tmp1.GetStdDevError():.2f}")
    stats1.Draw()

    stats2 = ROOT.TPaveText(0.7, 0.5, 0.9, 0.7, "NDC")
    stats2.AddText(f"Name: DF-ISE")
    stats2.AddText(f"Mean: {hist_tmp2.GetMean():.2f} ± {hist_tmp2.GetMeanError():.2f}")
    stats2.AddText(f"Std Dev: {hist_tmp2.GetStdDev():.2f} ± {hist_tmp2.GetStdDevError():.2f}")
    stats2.Draw()
    # Create a legend
    legend = ROOT.TLegend(0.5,0.6,0.7,0.8)
    legend.AddEntry(hist_tmp1,"Silvaco","l")
    legend.AddEntry(hist_tmp2,"DF-ISE","l")
    legend.Draw()

    canvas.SaveAs("./"+name+"_hist.png")
    canvas.Clear()

def main():

    (arr_events, cluster_truth, sumCharge, xSpan, ySpan, Area) = parse_file(filein="../Runs/"+filename+".out", threshold=10)
    print("Done analyzing dataset 1.")
    (arr_events2, cluster_truth2, sumCharge2, xSpan2, ySpan2, Area2) = parse_file(filein="../Runs/"+filename2+".out", threshold=10)
    print("Done analyzing dataset 2.")

    cluster_truth = cluster_truth[:-1]
    cluster_truth2 = cluster_truth2[:-1]

    (arr_events, cluster_truth, sumCharge, xSpan, ySpan, Area, arr_events2, cluster_truth2, sumCharge2, xSpan2, ySpan2, Area2) = remove_unmatched_evts(arr_events, cluster_truth, sumCharge, xSpan, ySpan, Area, arr_events2, cluster_truth2, sumCharge2, xSpan2, ySpan2, Area2)

    # if(len(cluster_truth)-len(cluster_truth2) != 0):
    #     for iter in range(len(cluster_truth)):
    #         if(cluster_truth[iter][3] != cluster_truth2[iter][3]):
    #             print("\n Event ",iter," doesn't match: ",cluster_truth[iter][3],"\n")
    #         if(cluster_truth[iter][4] != cluster_truth2[iter][4]):
    #             print("\n Event ",iter," doesn't match: ",cluster_truth[iter][4],"\n")
    #         if(cluster_truth[iter][5] != cluster_truth2[iter][5]):
    #             print("\n Event ",iter," doesn't match: ",cluster_truth[iter][5],"\n")
    # else:
    #     print("\nLength of both datasets are not the same!!\n")
    
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

    single_hists1 = [sumCharge, xSpan, ySpan, Area]
    single_hists2 = [sumCharge2, xSpan2, ySpan2, Area2]
    single_hist_names = ['sumCharge', 'xSpan', 'ySpan','Area', 'sumCharge2', 'xSpan2', 'ySpan2', 'Area2']
    single_hist_doFit= [True, False, False, False, True, False, False, False]
    single_hist_units = ['e', 'pixel', 'pixel', 'pixel', 'e', 'pixel', 'pixel', 'pixel']
    single_hist_maxbin = [120000, 20, 20, 40]
    single_hist_nbins = [100, 20, 20, 40]
    for i in range (len(single_hists1)):
        single_histogram(single_hists1[i], single_hists2[i], single_hist_names[i], single_hist_units[i], single_hist_maxbin[i], single_hist_nbins[i], single_hist_doFit[i], i)
        # order in which arrays are passed, matters. First histograms are for silvaco, and second for df-ise
    

if __name__ == "__main__":
    main()



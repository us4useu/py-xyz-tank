import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binned_statistic_2d
from matplotlib.colors import ListedColormap, BoundaryNorm
import tkinter as tk
from tkinter import filedialog
import pandas as pd

HYDROPHONE_DIST = 0.00
NOISE_OFFSET = 850

def load_npz_file(key1, key2):
    root = tk.Tk()
    root.withdraw()

    # Open file dialog and return the selected file path
    file_path = filedialog.askopenfilename(
        title="Select .npz tank data file",
        filetypes=(("Numpy .npz files", "*.npz"), ("All files", "*.*"))
    )

    # Check if a file was selected
    if file_path:
        try:
            npzfile = np.load(file_path)
            if key1 in npzfile and key2 in npzfile:
                return npzfile[key1], npzfile[key2]
            else:
                raise KeyError(f"Data not found in the .npz file.")
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("No file selected")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Plot heatmap from arrays from an NPZ file.")
    parser.add_argument("axes", type=str, help="Select axes to draw: xy, xz or yz")
    args = parser.parse_args()

    if args.axes != "xy" and args.axes != "xz" and args.axes != "yz":
        print("Invalid axes " + args.axes)
        return

    try:
        waveforms, coordinates = load_npz_file("waveforms", "positions")
    except KeyError as e:
        print(e)
        return
    
    waveforms = waveforms[:, NOISE_OFFSET:]

    amplitudes = np.ptp(waveforms, axis=1) / 84 # in MPa
    #amplitudes = np.ptp(waveforms, axis=1) / 68 # in MPa

    x = 1 * coordinates[:, 0]
    y = 1 * coordinates[:, 1]
    z = 1 * coordinates[:, 2]

    if(args.axes == "xy"):
        a = x
        b = y
    
    if(args.axes == "xz"):
        a = x
        b = z

    if(args.axes == "yz"):
        a = y
        b = z

    #num_x_bins = len(np.unique(x))
    #num_y_bins = len(np.unique(y))
    #num_z_bins = len(np.unique(z))

    num_a_bins = len(np.unique(a))
    num_b_bins = len(np.unique(b))

    #statistic, x_edge, y_edge, binnumber = binned_statistic_2d(y, z, amplitudes, statistic='mean', bins=[num_y_bins, num_z_bins])
    statistic, a_edge, b_edge, binnumber = binned_statistic_2d(a, b, amplitudes, statistic='mean', bins=[num_a_bins, num_b_bins])
    
    #cmap = "jet"

    #jet_colors = plt.cm.jet(np.linspace(0, 1, 10))
    #cmap = ListedColormap(jet_colors)

    cmap = "jet"



    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(statistic.T, xticklabels=np.round(np.unique(a), 2), yticklabels=np.round(np.unique(b), 2), cmap=cmap, cbar_kws={'label': 'Pressure [MPa]'}, square=True)
    ax.set_aspect('equal', 'box')
    ax.set_aspect('equal', 'box')
    plt.xlabel('Y (mm)')
    plt.ylabel('Z (mm)')
    plt.show()

    statistic_df = pd.DataFrame(statistic.T)

    # Define x and y labels
    a_labels = (a_edge[:-1] + a_edge[1:]) / 2
    b_labels = (b_edge[:-1] + b_edge[1:]) / 2

    # Set the x and y labels as the DataFrame index and columns
    statistic_df.columns = np.round(a_labels, 2)
    statistic_df.index = np.round(b_labels, 2)

    # Save to CSV
    #statistic_df.to_csv('binned_statistic.csv')

if __name__ == "__main__":
    main()
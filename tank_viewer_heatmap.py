import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binned_statistic_2d
from matplotlib.colors import ListedColormap, BoundaryNorm
import tkinter as tk
from tkinter import filedialog
import pandas as pd

HYDROPHONE_DIST = 15.0
NOISE_OFFSET = 1600

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
    try:
        waveforms, coordinates = load_npz_file("waveforms", "positions")
    except KeyError as e:
        print(e)
        return
    
    waveforms = waveforms[:, NOISE_OFFSET:]

    amplitudes = np.ptp(waveforms, axis=1) * 0.013 # in MPa

    x = coordinates[:, 0]
    y = coordinates[:, 2]
    z = coordinates[:, 1]

    num_x_bins = len(np.unique(x))
    num_y_bins = len(np.unique(y))
    num_z_bins = len(np.unique(z))

    statistic, x_edge, y_edge, binnumber = binned_statistic_2d(x, y, amplitudes, statistic='mean', bins=[num_x_bins, num_y_bins])

    #cmap = "jet"

    #jet_colors = plt.cm.jet(np.linspace(0, 1, 10))
    #cmap = ListedColormap(jet_colors)

    cmap = "jet"

    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(statistic.T, xticklabels=np.round(np.unique(x), 0), yticklabels=np.round(np.unique(y), 0), cmap=cmap, cbar_kws={'label': 'Pressure [MPa]'}, square=True)
    ax.set_aspect('equal', 'box')
    ax.set_aspect('equal', 'box')
    plt.xlabel('X (mm)')
    plt.ylabel('Y (mm)')
    plt.show()

    statistic_df = pd.DataFrame(statistic.T)

    # Define x and y labels
    x_labels = (x_edge[:-1] + x_edge[1:]) / 2
    y_labels = (y_edge[:-1] + y_edge[1:]) / 2

    # Set the x and y labels as the DataFrame index and columns
    statistic_df.columns = np.round(x_labels, 2)
    statistic_df.index = np.round(y_labels, 2)

    # Save to CSV
    statistic_df.to_csv('binned_statistic.csv')

if __name__ == "__main__":
    main()
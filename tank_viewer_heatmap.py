import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binned_statistic_2d
import tkinter as tk
from tkinter import filedialog

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

    amplitudes = np.ptp(waveforms, axis=1)

    x = coordinates[:, 0]
    y = coordinates[:, 1] - HYDROPHONE_DIST
    z = coordinates[:, 2]

    num_bins = 50
    statistic, x_edge, y_edge, binnumber = binned_statistic_2d(x, y, amplitudes, statistic='mean', bins=num_bins)

    plt.figure(figsize=(10, 8))
    sns.heatmap(statistic.T, xticklabels=np.round(x_edge, 2), yticklabels=np.round(y_edge, 2), cmap='viridis', cbar_kws={'label': 'Amplitude'})
    plt.xlabel('X (mm)')
    plt.ylabel('Y (mm)')
    plt.show()

if __name__ == "__main__":
    main()
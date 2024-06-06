import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binned_statistic_2d
from matplotlib.colors import ListedColormap, BoundaryNorm
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

    amplitudes = np.ptp(waveforms, axis=1) * 0.013 # in MPa



    #cmap = "jet"

    #jet_colors = plt.cm.jet(np.linspace(0, 1, 10))
    #cmap = ListedColormap(jet_colors)

    cmap = "jet"

    plt.figure(figsize=(10, 8))
    plt.plot(amplitudes)
    plt.xlabel('Dist (mm)')
    plt.ylabel('Amplitude')
    plt.show()

if __name__ == "__main__":
    main()
import numpy as np
import tkinter as tk
from tkinter import filedialog
from scipy.io import savemat

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

    mat_data = {
        'coordinates': coordinates,
        'waveforms': waveforms
    }

    # Save to .mat file
    savemat('coordinates_and_waveforms.mat', mat_data)

if __name__ == "__main__":
    main()
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binned_statistic_2d

HYDROPHONE_DIST = 15.0
NOISE_OFFSET = 1600

def load_npz_file(filepath, key):
    npzfile = np.load(filepath)
    if key in npzfile:
        return npzfile[key]
    else:
        raise KeyError(f"The key '{key}' was not found in the .npz file.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Plot arrays from an NPZ file with navigation.")
    parser.add_argument("filename", type=str, help="Path to the NPZ file")
    args = parser.parse_args()

    try:
        waveforms = load_npz_file(args.filename, "waveforms")
        coordinates =  load_npz_file(args.filename, "positions")
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
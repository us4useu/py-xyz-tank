import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

class PlotNavigator:
    def __init__(self, data):
        self.data = data
        self.index = 0
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.2)

        self.axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
        self.axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
        self.bnext = Button(self.axnext, 'Next')
        self.bnext.on_clicked(self.next)
        self.bprev = Button(self.axprev, 'Previous')
        self.bprev.on_clicked(self.prev)

        self.show_plot()

    def show_plot(self):
        self.ax.clear()
        self.ax.plot(self.data[self.index])
        self.ax.set_ylim(-10.0, 10.0)
        self.ax.set_title(f'Plot {self.index + 1}')
        self.fig.canvas.draw()

    def next(self, event):
        if self.index < len(self.data) - 1:
            self.index += 1
            self.show_plot()

    def prev(self, event):
        if self.index > 0:
            self.index -= 1
            self.show_plot()

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
        data = load_npz_file(args.filename, "waveforms")
    except KeyError as e:
        print(e)
        return

    navigator = PlotNavigator(data)
    plt.show()

if __name__ == "__main__":
    main()
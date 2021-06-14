"""
Utility for plotting the improvements over number of epochs.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Enter lifespans file (raw text file) as the first argument.")
    else:
        filepath = sys.argv[1]

        fig = plt.figure(figsize=(12, 8))
        plt.title("Poprawa rozwiązania w dziedzinie liczby epok ({})".format(filepath[:-4].split('\\')[1]), fontsize=16)
        plt.xlabel("Numer epoki", fontsize=18)
        plt.ylabel("Minimalna liczba przeżytych kwantów czasu ocaleńców", fontsize=18)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        ys = []
        I_FROM = 0

        with open(filepath, mode="r") as file:
            for line in file:
                y = np.array(line.split(), dtype="int")
                ys += [y]

                x = np.arange(I_FROM, I_FROM + len(y))
                plt.plot(x, y, linewidth=0.5, color="g")

        plt.plot(x, np.mean(np.array(ys), axis=0), color="r")
        plt.errorbar(
            x, np.mean(np.array(ys), axis=0), np.std(np.array(ys), axis=0), fmt="o", capsize=5, color="r", linewidth=0.5
        )
        plt.grid(axis="y")
        plt.tight_layout()
        plt.savefig("lifespans/" + filepath[:-4].split('\\')[1] + ".png")

        print("Mean result: {:.3f} (std. {:.3f})".format(np.mean(np.array(ys), axis=0)[-1], np.std(np.array(ys), axis=0)[-1]))

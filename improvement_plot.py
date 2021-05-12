import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys


if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Enter lifespans file (raw text file) as the first argument.")
    else:
        filepath = sys.argv[1]

        fig = plt.figure(figsize=(12, 8))
        plt.title("Poprawa rozwiązania w dziedzinie liczby epok")
        plt.xlabel("Numer epoki")
        plt.ylabel("Minimalna liczba przeżytych kwantów czasu ocaleńców")
        ys = []
        i_from = 0

        with open(filepath, mode='r') as file:
            for line in file:
                y = np.array(line.split(), dtype='int')
                ys += [y]
                
                x = np.arange(i_from, i_from + len(y))
                plt.plot(x, y, linewidth=0.5, color='g')

        plt.plot(x, np.mean(np.array(ys), axis=0), color='r')
        plt.errorbar(x, np.mean(np.array(ys), axis=0), np.std(np.array(ys), axis=0),
                     fmt='o', capsize=5, color='r', linewidth=0.5)
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig('lifespans.png')

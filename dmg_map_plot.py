"""
Utility for plotting damage map.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Enter damage map (*.npy file) as the first argument.")
    else:
        filepath = sys.argv[1]
        dmg_map = np.load(filepath)

        fig = plt.figure(figsize=(9, 6))
        sns.heatmap(dmg_map, mask=(dmg_map == 0), cmap="rocket_r", annot=True)
        plt.title("Mapa zadawanych obrażeń")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig("dmg_map.png")

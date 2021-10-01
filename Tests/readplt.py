import json
import os

import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    os.chdir('..')

    notes = np.array(json.load(open("dataPoint2.json")))
    points = np.array(json.load(open("dataPoint.json")))

    print("note shape", len(notes))
    print("points shape", len(points))

    ax = plt.axes()

    # defining axes
    x = [i[0] for i in points]
    y = [i[1] for i in points]


    index_to_remove = np.where(notes != 0)

    x = np.delete(x, index_to_remove)
    y = np.delete(y, index_to_remove)


    ax.scatter(x, y)
    ax.set_xlabel("Taille de bloc")
    ax.set_ylabel("C")
    # ax.set_zlabel("nombre d'erreurs")
    # syntax for plotting
    ax.set_title('Distribution des points sans erreur de lecture par rapport aux paramètres ')
    plt.show()

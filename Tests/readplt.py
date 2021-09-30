import json
import os

import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    os.chdir('..')

    notes = np.array(json.load(open("dataPoint2.json")))
    points = np.array(json.load(open("dataPoint.json")))

    print("note shape", notes.shape)
    print("points shape", points.shape)
    print("point 1 shape", points[:][:])
    ax = plt.axes(projection="3d")

    # defining axes
    z = notes
    x = [i[0] for i in points]
    y = [i[1] for i in points]
    c = notes

    index_to_remove = np.where(notes > 5)

    x = np.delete(x, index_to_remove)
    y = np.delete(y, index_to_remove)
    z = np.delete(z, index_to_remove)
    c = np.delete(c, index_to_remove)

    ax.scatter(x, y, z, c=c)
    ax.set_xlabel("Taille de bloc")
    ax.set_ylabel("C")
    ax.set_zlabel("nombre d'erreurs")
    # syntax for plotting
    ax.set_title('Distribution des erreurs de lecture par rapport aux paramètres')
    plt.show()
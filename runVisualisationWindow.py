# Xueqi Guan 1098403

# Run this file to run the visualisation node alone for testing purpose

from os import listdir

from visualisation.visualisationGui import runVisualisation
import resourceManager as rm


if __name__ == "__main__":
    dataPath = rm.resourcePath(rm.SPHARM_DATA)
    filePaths = [dataPath + f for f in listdir(dataPath) if f[-4:] == ".vtk"]
    runVisualisation(filePaths)

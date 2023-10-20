# Jiayu Li 713551

import json

import qdarkstyle
from qdarkstyle import LightPalette, DarkPalette

import resourceManager as rm
from constants import LIGHT_MODE, DARK_MODE


# Key for the fields
FIRST_TIME = "firstTime"
INPUT_DIR = "inputDir"
OUTPUT_DIR = "outputDir"
THEME = "colorTheme"
NEXT_THEME = "nextColorTheme"
VIS = "visualisation"
AXIS_COLOR = "axisColors"
OPACITY = "boneOpacity"

LATEST = "latestPath"

# Spharm constants
DEFAULT = "default"
SPHARM = "spharm"
SLICERSALTPATH = "slicerSALTPath"


class UserConfig(object):

    # Check the existence of instance before __init__ to make UserConfig a singleton class.
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            UserConfig._instance = super().__new__(cls)
        return UserConfig._instance

    def __init__(self):
        self.config = self.readConfigFromFile()

    ######################################################
    #  Getters and setters
    ######################################################

    # Return a boolean about whether the app is opened for the first time.
    def isNewUser(self):
        return self.config[FIRST_TIME]

    # Set to false after the first time window is opened.
    def disableNewUserWindows(self):
        self.config[FIRST_TIME] = False
        self.writeConfigToFile()

    # Get user's favourite input directory.
    def getInputDirectory(self):
        return self.config[INPUT_DIR]

    # Get user's favourite input directory.
    def setInputDirectory(self, newDir):
        self.config[INPUT_DIR] = newDir
        self.writeConfigToFile()

    # Set user's favourite input directory.
    def getOutputDirectory(self):
        return self.config[OUTPUT_DIR]

    # Set user's favourite output directory.
    def setOutputDirectory(self, newDir):
        self.config[OUTPUT_DIR] = newDir
        self.writeConfigToFile()

    # Get the color theme.
    def getColorTheme(self):
        mode = self.config[THEME]
        if mode == LIGHT_MODE:
            return qdarkstyle.load_stylesheet(palette=LightPalette)
        elif mode == DARK_MODE:
            return qdarkstyle.load_stylesheet(palette=DarkPalette)
        return None

    def getColorThemeWhenStart(self):
        mode = self.config[NEXT_THEME]
        self.config[THEME] = mode
        self.writeConfigToFile()
        if mode == LIGHT_MODE:
            return qdarkstyle.load_stylesheet(palette=LightPalette)
        elif mode == DARK_MODE:
            return qdarkstyle.load_stylesheet(palette=DarkPalette)
        return None

    def getColorThemeCode(self):
        return self.config[THEME]

    # Set the color theme (light or dark).
    def setColorTheme(self, theme):
        self.config[NEXT_THEME] = theme
        self.writeConfigToFile()

    # Get the colors of the axes as a list.
    def getAxisColors(self):
        return self.config[VIS][AXIS_COLOR]

    # Get the hex value of the color of X-axis.
    def getXAxisColor(self):
        return self.config[VIS][AXIS_COLOR][0]

    # Get the hex value of the color of Y-axis.
    def getYAxisColor(self):
        return self.config[VIS][AXIS_COLOR][1]

    # Get the hex value of the color of Z-axis.
    def getZAxisColor(self):
        return self.config[VIS][AXIS_COLOR][2]

    # Set the hex values of the axis colors
    def setAxisColors(self, colors):
        self.config[VIS][AXIS_COLOR] = colors
        self.writeConfigToFile()

    # Get the opacity of the bone model
    def getBoneOpacity(self):
        return self.config[VIS][OPACITY]

    # Set the opacity of the bone model
    def setBoneOpacity(self, opacity):
        self.config[VIS][OPACITY] = opacity
        self.writeConfigToFile()

    # Node setters and getters
    def getLatestFolder(self):
        return self.config[LATEST]

    def setLatestFolder(self, path):
        self.config[LATEST] = path
        self.writeConfigToFile()

    # SPHARM getters and setters

    def getPCAColor(self, type):
        #dictionary
        switch = {1: "first", 2: "second", 3: "third"}
        return self.config[SPHARM][switch[type]]

    def setPCAColor(self, type, color):
        #dictionary
        switch = {1: "first", 2: "second", 3: "third"}

        self.config[SPHARM][switch[type]]=color
        self.writeConfigToFile()

    def getSlicerSALT(self):
        return self.config[SPHARM][SLICERSALTPATH]

    def setSlicerSALT(self, path):
        self.config[SPHARM][SLICERSALTPATH]=path
        self.writeConfigToFile()

    def getSPHARMLastFolder(self, type):
        return self.config[SPHARM][type]

    def getSPHARMDetails(self,animalType, dataType):
        return self.config[SPHARM][DEFAULT][animalType][dataType]

    def setSPHARMLastFolder(self, type, path):
        self.config[SPHARM][type] = path
        self.writeConfigToFile()

    ######################################################
    #  Private methods for internal use
    ######################################################

    # Read the config to self.config from config.json file. If the file doesn't exist,
    # create a new config.json file with the default settings copied from defaultConfig.json.
    def readConfigFromFile(self):
        fp = rm.resourcePath(rm.CONFIG)
        try:
            with open(fp, "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            success = self.writeDefaultSettingsToFile()
            if success:
                return self.config
        except Exception as e:
            print("An exception occurred: {}".format(e))
        raise Exception("An error occurred when reading file {}. Aborting.".format(fp))

    # Replace config.json with the default settings
    # (or create a new config.json with the default settings if it doesn't exist)
    def writeDefaultSettingsToFile(self):
        return self.writeConfigToFile(default=True)

    # Write the current self.config to file
    def writeConfigToFile(self, default=False):
        try:
            with open(rm.resourcePath(rm.CONFIG), "w") as f:
                if default:
                    with open(rm.resourcePath(rm.DEFAULT_CONFIG), "r") as d:
                        self.config = json.loads(d.read())
                json.dump(self.config, f)
            return True
        except Exception as e:
            print("An exception occurred when writing config to file {}".format(e))
            return False

    # Return all configuration object as a dictionary
    def getConfig(self):
        return self.config


# if __name__ == "__main__":
#     obj = UserConfig()
#     print(obj.getColorTheme())

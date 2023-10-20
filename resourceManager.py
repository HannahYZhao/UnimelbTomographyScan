# Jiayu Li 713551

import os
import sys

from PySide2.QtGui import QFontDatabase, QFont, QIcon, QPixmap

from constants import LIGHT_MODE, DARK_MODE
from userConfig import UserConfig

os.chdir(os.path.dirname(os.path.realpath(__file__)))
DIR = os.getcwd()

# Directories
ASSETS = "/assets/"
ICONS = ASSETS + "icons/"
ICONS_LIGHT = ICONS + "light/"
ICONS_DARK = ICONS + "dark/"
IMAGES = ASSETS + "images/"
FONTS = ASSETS + "fonts/"
DATA = ASSETS + "data/"
HTML = ASSETS + "html/"

# Data
SPHARM_DATA = DATA + "SPHARM/"
PROCESSES = DATA + "processes/"

# Fonts
TITLE_FONT = FONTS + "BONEAPA.TTF"
TEXT_FONT = FONTS + "SourceSansPro-Bold.ttf"

# Images
LANDING_PAGE_BG = IMAGES + "bg2.png"
EXAMPLE_BONE_IMG = IMAGES + "example.png"
FOLDER_IMG = IMAGES + "folder.png"

# Icons
INFO_ICON = "info.png"
QUESTION_ICON = "question.png"
NEW_ICON = "addnew.png"
LOAD_ICON = "loadexisting.png"
RESET_CAM_ICON = "reset_cam.png"
LEFT_ARROW = "left_arrow.png"
RIGHT_ARROW = "right_arrow.png"
REMOVE_IMG = "remove.png"
LOG_FILE_ICON = "log_file.png"
SETTINGS_ICON = "settings.png"
WARNING_ICON = "warning.png"

# HTMLs
HELP_QHC = HTML + "userManual.qhc"
WELCOME_HTML = HTML + "intro.html"

# Configurations
CONFIG = ASSETS + "config.json"
DEFAULT_CONFIG = ASSETS + "defaultConfig.json"


# Convert the relative path of an asset to a correct path, which is
# sys._MEIPASS + relativePath for installation version, and absolute path when running the code.
def resourcePath(relativePath):
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")
    return basePath + relativePath


# Read the welcome HTML file (intro.html).
# This is only called when the app is opened for the first time. For the user manual window,
# please use QHelpEngine (see userManual.py)
def getWelcomeHtml():
    with open(resourcePath(WELCOME_HTML), "r", encoding='utf-8') as f:
        html = f.read()
    return html


# Loads a font from assets and returns a QFont object.
def loadFont(path, size, weight):
    rPath = resourcePath(path)
    fontId = QFontDatabase.addApplicationFont(rPath)
    if fontId >= 0:
        family = QFontDatabase.applicationFontFamilies(fontId)[0]
        return QFont(family, pointSize=size, weight=weight)
    print("Font not loaded (" + rPath + ")")
    return QFont("SansSerif", pointSize=size, weight=weight)


# Returns a QIcon object of the specified path. If the icon depends on the color theme,
# put each version of it in the dark and light folder and set hasMode to True.
def getIcon(path, hasMode=False):
    ppath = resourcePath(ICONS + path)
    if hasMode:
        if UserConfig().getColorThemeCode() == LIGHT_MODE:
            ppath = resourcePath(ICONS_LIGHT + path)
        elif UserConfig().getColorThemeCode() == DARK_MODE:
            ppath = resourcePath(ICONS_DARK + path)
    return QIcon(ppath)


# Returns a QPixmap object of the specified path
def getPixmap(path):
    return QPixmap(resourcePath(path))

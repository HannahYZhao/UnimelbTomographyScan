# Jiayu Li 713551
# Xueqi Guan 1098403

from constants import *
from userConfig import UserConfig

# Icons
QUESTION_ICON = "question.png"
SETTINGS_ICON = "settings.png"
RESET_CAM_ICON = "reset_cam.png"
LEFT_ARROW = "left_arrow.png"
RIGHT_ARROW = "right_arrow.png"
REMOVE_IMG = "remove.png"
LOG_FILE_ICON = "log_file.png"

#############################################################
#                        File paths                         #
#############################################################

# Filename
FILENAME_INDEX = -1

#############################################################
#                          Names                            #
#############################################################
# Views
THREED = "3D"
TRANSVERSE = "Transverse/Axial (top)"
CORONAL = "Coronal (front)"
SAGITTAL = "Sagittal (left)"
VIEWS_LABELS = [THREED, TRANSVERSE, CORONAL, SAGITTAL]
# Axes
X = "X"
Y = "Y"
Z = "Z"
AXIS_NAMES = [X, Y, Z]

#############################################################
#                         Windows                           #
#############################################################
# main visualisation window
WINDOW_POS_X = 200
WINDOW_POS_Y = 60
WINDOW_WIDTH = 840
WINDOW_HEIGHT = 640
# settings window
SETTINGS_WIDTH = 300
SETTINGS_HEIGHT = 300
# example window
EXAMPLE_WIDTH = 600
EXAMPLE_HEIGHT = 700
EXAMPLE_IMG_DIM = 600

#############################################################
#                           UI                              #
#############################################################
# sizes
VTK_BOX_DIM = 300
BIG_ICON_DIM = 36
MIDDLE_ICON_DIM = 24
SMALL_ICON_DIM = 15
VTK_LIST_WIDTH = 500
SMALL_BTN_WIDTH = 35
FILENAME_LEN = 12
# Colors
MODEL_COLOR = "#F5F5F5"  # WhiteSmoke
BG_COLOR_LIGHT = "#EBEBEB"  # WhiteSmoke
BG_COLOR_DARK = "#5f6873"
# BG_COLOR_BOTTOM = "#F0FFF0"  # honeydew
BG_GRADIENT_ON = True
X_CAPTION_COLOR = "#FFFFFF"  # White
Y_CAPTION_COLOR = "#FFFFFF"  # White
Z_CAPTION_COLOR = "#FFFFFF"  # White

#############################################################
#                  Visualisation settings                   #
#############################################################
VIEW_OPTIONS = [1, 2, 4, 8, 12, 16, 20, 24]  # Number of bone models to display

#############################################################
#                     Interactions (UI)                     #
#############################################################
SEPARATOR_WIDTH = 2
# Rotation
ROT_LOWER_BOUND = -90
ROT_UPPER_BOUND = 90
ONE_CYCLE_DEGREE = 360
ROT_RATE = 0.7
# Zooming in/out
ZOOM_STEP = 0.1
# Flipping
FLIP_ANGLE = 180
X_AXIS = [1, 0, 0]
Y_AXIS = [0, 1, 0]
Z_AXIS = [0, 0, 1]

#############################################################
#                 Renderer and interactor                   #
#############################################################
# Camera
CAM_OFFSET_RATIO = 2.5  # factor for calculating the distance between model bounds and camera reset bound.
# (The bigger the number, the closer the bone (i.e. looks bigger))
# Axes
AXIS_SCALE_RATIO = 1  # factor for calculating the size of axes
AXIS_TIP_RADIUS = 0.3
AXIS_RADIUS = 0.02
AXIS_CAPTION_SCALE = 1
# Rotation
ROTATION_UNIT = 3.0  # in degrees
# Zoom (renderer)
ZOOM_FACTOR = 5  # default zoom factor
MIN_ZOOM_SCALE = 0.5  # 50% of original size
MAX_ZOOM_SCALE = 3  # 300% of original size

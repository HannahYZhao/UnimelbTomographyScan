# Jiayu Li 713551
# Xueqi Guan 1098403

#############################################################
#                          Texts                            #
#############################################################
APP_NAME = "ScanFlow"

#############################################################
#                 Landing page window pos                   #
#############################################################
LP_WINDOW_POS_X = 280
LP_WINDOW_POS_Y = 140

#############################################################
#                           GUI                             #
#############################################################
LIGHT_MODE = "light"
DARK_MODE = "dark"

#############################################################
#                          Styles                           #
#############################################################
VIS_MODULE_BTN_STYLE = """QPushButton {
                            color: white;
                            padding: 3px 10px;
                            background-color: #455364;
                        }

                        QPushButton:pressed {
                            background-color: #353f4d;
                        }

                        QPushButton:hover:!pressed {
                            background-color: #6d8da3;
                        }"""

LANDING_PAGE_BTN_STYLE = """QPushButton {
                                color: white;
                                border-radius: 24px;
                                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                                stop: 0 #056E99, stop: 1 #0A4183);
                                min-width: 80px;
                            }

                            QPushButton:pressed {
                                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                                stop: 0 #0E59B5, stop: 1 #0693CC);
                            }

                            QPushButton:hover:!pressed {
                                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                                stop: 0 #0693CC, stop: 1 #0E59B5);
                            }"""

#############################################################
#                 Error window pos                          #
#############################################################
EW_WIDTH = 450
EW_HEIGHT = 200
EW_MARGIN = 10
MSG_ICON_WIDTH = 50
MSG_TEXT_WIDTH = 360
BTN_WIDTH = 100

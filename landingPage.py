# Jiayu Li 713551

import sys

from PySide2 import QtGui
from PySide2.QtCore import QSize, Qt
from PySide2.QtWidgets import *
import qdarkstyle
from qdarkstyle import LightPalette, DarkPalette

from constants import *
from procBuilder import processBuilder
from mainWindow import MainWindow, LP_WINDOW_POS_X, LP_WINDOW_POS_Y
from userConfig import UserConfig
import resourceManager as rm


# Window size
LP_WINDOW_WIDTH = 900  # 2400
LP_WINDOW_HEIGHT = 675  # 1800

# Info button on the top right corner
INFO_BTN_SIZE = QSize(52, 52)

# The two buttons
BTN_WIDTH = 230
BTN_SIZE = QSize(BTN_WIDTH, round(BTN_WIDTH/1.5))
BTN_TOP_PADDING = 154
# Icon
BTN_ICON_SIZE = QSize(40, 40)
BTN_ICON_PADDING = 3
# Text
BTN_TEXT_SIZE = 25
BTN_TEXT_WEIGHT = 3

# Shadow effects
OFFSET_SHADOW = [6, 12]
BORDER_SHADOW = [0, 60]

# Layout size constraints
UPPER_HEIGHT = 82
LOWER_HEIGHT = LP_WINDOW_HEIGHT - UPPER_HEIGHT


# Landing page of the app
class LandingPage(MainWindow):
    def __init__(self):
        super().__init__(False)
        self.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.setWindowTitle(APP_NAME)
        self.setGeometry(LP_WINDOW_POS_X, LP_WINDOW_POS_Y, LP_WINDOW_WIDTH, LP_WINDOW_HEIGHT)
        self.setFixedWidth(LP_WINDOW_WIDTH)
        self.setFixedHeight(LP_WINDOW_HEIGHT)
        # GUI stuff
        self.textFont = rm.loadFont(rm.TEXT_FONT, BTN_TEXT_SIZE, BTN_TEXT_WEIGHT)
        self.vBox = QVBoxLayout()
        self.vBox.setMargin(0)
        self.wdg = QWidget()
        self.wdg.setLayout(self.vBox)
        self.setCentralWidget(self.wdg)
        # Add GUI elements
        self.addUpperLayout()
        self.addLowerLayout()
        # menu bar
        super().createSettingsMenuBarUI()
        super().createHelpMenuBarUI()
        # Process builder
        self.pb = None

    # Button on the top right corner (leads to the welcome window)
    def addUpperLayout(self):
        hBox = QHBoxLayout()
        btn = QPushButton()
        btn.setIcon(rm.getIcon(rm.INFO_ICON))
        btn.setIconSize(INFO_BTN_SIZE)
        btn.setStyleSheet("color: white; "
                          "border-radius: 24px; "
                          "min-width: 80px;")  # stylesheet that makes the button background transparent
        btn.clicked.connect(super().openWelcomeScreen)
        hBox.addWidget(btn)
        hBox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # create a widget that wraps the layout
        widget = QWidget()
        widget.setLayout(hBox)
        widget.setFixedHeight(UPPER_HEIGHT)
        # widget.setAutoFillBackground(True)
        # Add the widget to vBox
        self.vBox.addWidget(widget)

    # Add the two buttons (new and load)
    def addLowerLayout(self):
        hBox = QHBoxLayout()
        hBox.setContentsMargins(0, BTN_TOP_PADDING, 0, 0)  # left, top, right, down
        newBtn = QPushButton("     New\n  Process")
        loadBtn = QPushButton("     Load\n  Process")
        for btn in [newBtn, loadBtn]:
            btn.setFixedSize(BTN_SIZE)
            btn.setIconSize(BTN_ICON_SIZE)
            btn.setFont(self.textFont)
            btn.setStyleSheet(LANDING_PAGE_BTN_STYLE)
        newBtn.setIcon(rm.getIcon(rm.NEW_ICON))
        self.newBtnShadow = super().createShadow(BORDER_SHADOW[0], BORDER_SHADOW[1])
        newBtn.setGraphicsEffect(self.newBtnShadow)
        newBtn.clicked.connect(self.startProcessBuilder)
        loadBtn.setIcon(rm.getIcon(rm.LOAD_ICON))
        self.loadBtnShadow = super().createShadow(BORDER_SHADOW[0], BORDER_SHADOW[1])
        loadBtn.setGraphicsEffect(self.loadBtnShadow)
        loadBtn.clicked.connect(self.loadProcess)
        # Add the buttons
        hBox.addWidget(newBtn)
        hBox.addWidget(loadBtn)
        # create a widget that wraps the layout
        widget = QWidget()
        widget.setLayout(hBox)
        widget.setFixedHeight(LOWER_HEIGHT)
        # widget.setAutoFillBackground(True)
        # Add the widget to vBox
        self.vBox.addWidget(widget)

    # Override method. Paints the background
    def paintEvent(self, pe):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), rm.getPixmap(rm.LANDING_PAGE_BG))
        super().paintEvent(pe)

    # Override
    def setLightMode(self):
        self.iw.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette))
        self.um.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette))
        UserConfig().setColorTheme(LIGHT_MODE)

    # Override
    def setDarkMode(self):
        self.iw.setStyleSheet(qdarkstyle.load_stylesheet(palette=DarkPalette))
        self.um.setStyleSheet(qdarkstyle.load_stylesheet(palette=DarkPalette))
        UserConfig().setColorTheme(DARK_MODE)

    ######################################################
    #  button listeners
    ######################################################

    # Button listener for "new process" button
    def startProcessBuilder(self):
        print("Starting empty process builder")
        # Create the process builder window
        self.pb = processBuilder.ProcessBuilderWindow()
        self.pb.show()
        # self.hide()

    # Button listener for "load process" button
    def loadProcess(self):
        print("Loading processes")
        dialog = QFileDialog()
        dialog.setWindowTitle("Select a process to load")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setDirectory(rm.resourcePath(rm.PROCESSES))
        if dialog.exec_():
            filePaths = dialog.selectedFiles()
            self.pb = processBuilder.ProcessBuilderWindow(loaded_file=filePaths[0])
            self.pb.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = LandingPage()
    mw.show()
    if UserConfig().isNewUser():
        mw.iw.show()
    # Disable new user windows after app is first opened
    UserConfig().disableNewUserWindows()
    sys.exit(app.exec_())

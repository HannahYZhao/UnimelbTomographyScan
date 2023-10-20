# 1098403 Xueqi Guan
# Jiayu Li 713551 - wrote some helper methods and created the welcome window
# Hannah Zhao 1161094 - Wrote set light/dark mode so that processBuilder window could use it

from PySide2.QtWidgets import QGraphicsDropShadowEffect, QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QMenu
from qtpy.QtWidgets import QMainWindow, QAction

from userManual import UserManualWindow
from constants import *
from userConfig import UserConfig
import resourceManager as rm
from errorWindow import ErrorWindow


# info window dimensions
INFO_WIDTH = 1000
INFO_HEIGHT = 600


# A QMainWindow which contains the common GUI elements that appear on all windows.
# Other windows can inherit this class.
class MainWindow(QMainWindow):
    def __init__(self, hasMode=True):
        super().__init__()
        self.menuBar = self.menuBar()
        self.iw = WelcomeWindow()
        self.um = UserManualWindow()
        if hasMode:
            self.loadColorTheme()

    # Create the help menu bar
    def createHelpMenuBarUI(self):
        # For the welcome page
        welcomeAction = QAction('Welcome Screen', self)
        welcomeAction.triggered.connect(self.openWelcomeScreen)
        # For the user manual page
        userManualAction = QAction('User Manual', self)
        userManualAction.triggered.connect(self.openUserManual)
        # Add menu item
        runMenu = self.menuBar.addMenu("Help")
        runMenu.addAction(welcomeAction)
        runMenu.addAction(userManualAction)

    def createSettingsMenuBarUI(self):
        # Dark and light mode
        lightAction = QAction("Light", self)
        lightAction.triggered.connect(self.setLightMode)
        darkAction = QAction("Dark", self)
        darkAction.triggered.connect(self.setDarkMode)
        themeMenu = QMenu("Theme")
        themeMenu.addAction(lightAction)
        themeMenu.addAction(darkAction)
        # Add menu item
        settingMenu = self.menuBar.addMenu("Settings")
        settingMenu.addMenu(themeMenu)

    # show the infomation window
    def openWelcomeScreen(self):
        print('Open Welcome Screen')
        self.iw.show()

    # show the user manual window
    def openUserManual(self):
        print("Open User Manual")
        self.um.show()

    # Create a shadow effect for UI elements. Usage:
    # self.shadow = super().createShadow(offset, blurRadius)
    # uiElement.setGraphicsEffect(self.shadow)
    def createShadow(self, offset, blurRadius):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blurRadius)
        shadow.setXOffset(offset)
        shadow.setYOffset(offset)
        return shadow

    # Base method for setting light mode using the light stylesheet from qdarkstyle
    def setLightMode(self):
        self.messageWindow = ErrorWindow()
        self.messageWindow.setMessageText("Theme preference has been updated, please reopen the window to view.")
        UserConfig().setColorTheme(LIGHT_MODE)

    # Base method for setting dark mode using the dark stylesheet from qdarkstyle
    def setDarkMode(self):
        self.messageWindow = ErrorWindow()
        self.messageWindow.setMessageText("Theme preference has been updated, please reopen the window to view.")
        UserConfig().setColorTheme(DARK_MODE)

    # Get the current theme setting from user config
    def loadColorTheme(self):
        self.setStyleSheet(UserConfig().getColorThemeWhenStart())


# The welcome window
class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.setWindowTitle("Welcome")
        self.setGeometry(LP_WINDOW_POS_X - 50, LP_WINDOW_POS_Y + 40, INFO_WIDTH, INFO_HEIGHT)
        self.setStyleSheet(UserConfig().getColorTheme())
        self.wdg = QWidget()
        self.vBox = QVBoxLayout()
        self.wdg.setLayout(self.vBox)
        self.setCentralWidget(self.wdg)
        self.addHtmlUi()

    # Create the QTextBrowser for the welcome HTML
    def addHtmlUi(self):
        hBox = QHBoxLayout()
        textBrowser = QTextBrowser()
        textBrowser.setHtml(rm.getWelcomeHtml())
        textBrowser.setOpenExternalLinks(True)
        textBrowser.setReadOnly(True)
        hBox.addWidget(textBrowser)
        self.vBox.addLayout(hBox)

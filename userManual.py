# Jiayu Li 713551

import sys

from PySide2 import QtWidgets, QtHelp, QtCore
from PySide2.QtWidgets import QMainWindow, QTextBrowser, QWidget, QHBoxLayout

from constants import LP_WINDOW_POS_X, LP_WINDOW_POS_Y
import resourceManager as rm

INFO_WIDTH = 900
INFO_HEIGHT = 600

DEFAULT_SOURCE = QtCore.QUrl("qthelp://ts.usermanual/doc/intro.html")


# Parent class of help browser
class HelpBrowser(QTextBrowser):
    def __init__(self, helpEngine, parent=None):
        super().__init__(parent)
        self.helpEngine = helpEngine

    def loadResource(self, _type, name):
        if name.scheme() == "qthelp":
            return self.helpEngine.fileData(name)
        else:
            return super().loadResource(_type, name)


# Class for the user manual window
class UserManualWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.setWindowTitle("Help")
        self.setGeometry(LP_WINDOW_POS_X + 20, LP_WINDOW_POS_Y + 80, INFO_WIDTH, INFO_HEIGHT)
        self.wdg = QWidget()  # the central widget
        self.hBox = QHBoxLayout()
        self.wdg.setLayout(self.hBox)
        self.setCentralWidget(self.wdg)
        # Create the help engine
        self.helpEngine = QtHelp.QHelpEngine(rm.resourcePath(rm.HELP_QHC))
        self.helpEngine.setupData()
        self.widget = self.helpEngine.contentWidget()  # use the content widget of the help engine
        # Create the contents inside the help window
        self.createHelpWindow()
        # self.widget.expandAll()
        # self.widget.update()

    # Create the help window
    def createHelpWindow(self):
        # Table of contents on the left
        self.widget.setMaximumWidth(500)
        self.widget.setMinimumWidth(200)
        self.hBox.addWidget(self.widget)
        # Text viewer on the right that shows the HTMLs
        textViewer = HelpBrowser(self.helpEngine)
        textViewer.setMinimumWidth(640)
        textViewer.setMaximumWidth(640)
        textViewer.setSource(DEFAULT_SOURCE)
        self.hBox.addWidget(textViewer)
        # Connect the two sections
        self.helpEngine.setUsesFilterEngine(True)
        self.widget.linkActivated.connect(textViewer.setSource)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = UserManualWindow()
    w.show()
    sys.exit(app.exec_())

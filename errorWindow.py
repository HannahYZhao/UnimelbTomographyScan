# This code has been worked on by the following student:
# 1098403 Xueqi Guan

import sys

from PySide2.QtWidgets import *
import qdarkstyle
from qdarkstyle import LightPalette, DarkPalette
from constants import *
from userConfig import UserConfig
import resourceManager as rm

class ErrorWindow(QWidget):
    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen()
        xPosition = screen.size().width() / 2 - EW_WIDTH / 2
        yPosition = screen.size().height() / 2 - EW_HEIGHT / 2
        self.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.setWindowTitle("Notification")
        self.setGeometry(xPosition, yPosition, EW_WIDTH, EW_HEIGHT)
        self.ui()

    def setMessageText(self, message):
        self.messageTextLabel.setText(message)

    def ui(self):
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.createMessageUI()
        self.createButtonsUI()
        self.show()

    def createMessageUI(self):
        self.messageHBox = QHBoxLayout()
        self.vbox.addLayout(self.messageHBox)
        self.messageIconLabel = QLabel()
        self.messageIconLabel.setMargin(EW_MARGIN)
        # rm.getIcon(rm.INFO_ICON, False)
        self.messageIconLabel.setPixmap(rm.getPixmap(rm.ICONS + rm.WARNING_ICON).scaledToWidth(MSG_ICON_WIDTH))
        self.messageHBox.addWidget(self.messageIconLabel)
        self.messageTextLabel = QLabel()
        self.messageTextLabel.setStyleSheet("""QLabel {
                                                   font-family: Source Sans Pro;
                                                   font-size:   15px; 
                                               }""")
        self.messageTextLabel.setMargin(EW_MARGIN)
        self.messageTextLabel.setFixedWidth(MSG_TEXT_WIDTH)
        self.messageTextLabel.setWordWrap(True)
        self.messageHBox.addWidget(self.messageTextLabel)
        self.messageHBox.addStretch()

    def createButtonsUI(self):
        self.buttonHBox = QHBoxLayout()
        self.vbox.addLayout(self.buttonHBox)
        self.okButton = QPushButton("OK")
        self.okButton.setFixedWidth(BTN_WIDTH)
        #self.okButton.setStyleSheet(VIS_MODULE_BTN_STYLE)
        self.okButton.setStyleSheet(UserConfig().getColorTheme())
        self.okButton.clicked.connect(self.close)
        self.buttonHBox.addStretch()
        self.buttonHBox.addWidget(self.okButton)

    def show(self):
        self.setStyleSheet(UserConfig().getColorTheme())
        super().show()



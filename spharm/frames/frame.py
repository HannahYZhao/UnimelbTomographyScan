from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QDialog, QLabel, QPushButton, \
    QVBoxLayout, QTextEdit, QGraphicsDropShadowEffect

from spharm.managers.pathSingleton import pathSingleton
import resourceManager as rm

class frame(QWidget):

    def setOutput(self, output):
        self.output = output

    def refresh(self):
        pass

    def closeWindow(self):
        self.dialog.close()

    def issueWarning(self, text, output = None):
        if not (output == None):
            self.showWindowWithIcon(text, pathSingleton().getRelativePath('warningIcon.png'), output)
        else:
            self.showWindowWithIcon(text, pathSingleton().getRelativePath('warningIcon.png'))

    def issueComplete(self, text):
        self.showWindowWithIcon(text, pathSingleton().getRelativePath('completeIcon.png'))

    def showWindowWithIcon(self, text, icon, output = None):

        styleSheet = \
            """.QPushButton::hover {
                
                font-family: Source Sans Pro;
                font-size:   26px;
                font-weight: 700;
                color: rgb(255,255,255);
                background-color: rgb(10, 65, 131);
                
            }
            
            .QPushButton {
                
                background-color: rgb(242, 245, 249);
                font-size:   24px;
                font-weight: 700;
                color: rgb(1,42,88)
            }"""

        self.dialog = QDialog()

        warningLabel = QLabel()
        pixmap = QPixmap(icon)

        scaledPixmap = pixmap.scaled(128,128)
        warningLabel.setPixmap(scaledPixmap)
        warningLabel.setAlignment(Qt.AlignCenter)

        text = QLabel(text)
        text.setWordWrap(True)
        text.setStyleSheet("""font-family: Source Sans Pro;
        font-size:   24px;
        font-weight: 700;
        background-color: rgb(10,65,131);
        color: rgb(242, 245, 249);
        text-align: center;
        padding: 30""")
        text.setAlignment(Qt.AlignHCenter)

        button = QPushButton("Ok")
        button.setStyleSheet(styleSheet)
        button.setFixedSize(200,100)

        layout = QVBoxLayout()


        layout.addWidget(warningLabel)
        layout.addWidget(text)

        if not (output == None):
            console = QTextEdit()

            console.setReadOnly(True)

            output = sorted(output)

            for item in output:
                console.append(str(item))

            layout.addWidget(console)

        layout.addWidget(button, alignment = Qt.AlignHCenter)

        self.dialog.setLayout(layout)

        button.clicked.connect(self.closeWindow)

        shadow = QGraphicsDropShadowEffect()

        shadow.setYOffset(3)
        shadow.setXOffset(3)
        shadow.setBlurRadius(15)
        button.setGraphicsEffect(shadow)

        self.dialog.setFixedSize(600,600)
        self.dialog.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.dialog.setWindowTitle("Notification")
        self.dialog.show()

    def nextClicked(self):
        self.myParent.nextClicked(self.step)

    def prevClicked(self):
        self.myParent.prevClicked(self.step)

    def setParent(self, parent):
        self.myParent = parent

    def setStep(self, step):
        self.step = step


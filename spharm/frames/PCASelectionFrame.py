from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, \
    QGraphicsDropShadowEffect

from spharm.customWidgets.PCATablePane import PCATablePane
from spharm.customWidgets.instructionPane import instructionPaneWidget
from spharm.customWidgets.keyPane import keyPane
from spharm.customWidgets.navigationPane import navigationPaneWidget
from spharm.frames.frame import frame
from spharm.managers.dataSingleton import dataSingleton


class PCASelection(frame):

    def nextClicked(self):
        files = self.table.getSelected()

        directory = self.dataManager.getOutput("fileInput","inputDirectory")

        fullFiles = []

        for file in files:
            file = directory + file +".gipl"
            fullFiles.append(file)

        self.dataManager.addPCAFiles(fullFiles)
        super().nextClicked()

    def setTitle(self, titleName):
        self.instructions.setTitle(titleName)

    def setInstruction(self, text):
        self.instructions.setInstruction(text)

    def setInput(self, input):
        self.input = input

    def refresh(self):
        self.table.load()

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)

        self.dataManager = dataSingleton()

        layout = QVBoxLayout(self)

        self.instructions = instructionPaneWidget()

        layout.addWidget(self.instructions)

        key = keyPane(self)

        layout2 = QHBoxLayout()

        spacer1 = QWidget()
        spacer1.setFixedWidth(100)


        spacer2 = QWidget()
        spacer2.setFixedWidth(10)

        layout2.addWidget(spacer1)


        layout2.addWidget(key)

        layout2.addWidget(spacer2)

        layout.addLayout(layout2)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        key.setGraphicsEffect(shadow)

        self.table = PCATablePane()

        layout.addWidget(self.table, alignment = Qt.AlignHCenter)

        self.navigation = navigationPaneWidget(self)

        layout.addWidget(self.navigation, alignment = Qt.AlignBottom)


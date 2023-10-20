from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from spharm.customWidgets.highAndLowTableLoaderPane import \
    highAndLowTableLoaderPaneWidget
from spharm.customWidgets.instructionPane import instructionPaneWidget
from spharm.customWidgets.navigationPane import navigationPaneWidget
from spharm.customWidgets.radioPane import radioPaneWidget
from spharm.frames.frame import frame
from spharm.managers.dataSingleton import dataSingleton


class highAndLow(frame):

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


        self.table = highAndLowTableLoaderPaneWidget()

        layout.addWidget(self.instructions)

        layout2 = QHBoxLayout()

        spacer1 = QWidget()
        spacer1.setFixedWidth(100)

        spacer2 = QWidget()
        spacer2.setFixedWidth(10)

        layout2.addWidget(spacer1)

        radioPane = radioPaneWidget(self.table)

        layout2.addWidget(radioPane)

        layout2.addWidget(spacer2)

        layout.addLayout(layout2)

        layout.addWidget(self.table, alignment = Qt.AlignHCenter)

        self.navigation = navigationPaneWidget(self)

        layout.addWidget(self.navigation, alignment = Qt.AlignBottom)


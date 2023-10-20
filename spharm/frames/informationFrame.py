from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTextEdit

from spharm.customWidgets.instructionPane import instructionPaneWidget
from spharm.customWidgets.navigationPane import navigationPaneWidget
from spharm.frames.frame import frame
from spharm.managers.dataSingleton import dataSingleton

class information(frame):

    def nextClicked(self):
        if self.finish:

            if self.myParent.node is not None:
                dataManager = dataSingleton()
                self.myParent.node.setOutput(dataManager.getPCAFiles(),
                                             dataManager.getFiles("low"),
                                             dataManager.getFiles("high"))
            self.myParent.close()
        else:
            super().nextClicked()

    def setTitle(self, titleName):
        self.instructions.setTitle(titleName)

    def setInstruction(self, text):
        self.instructions.setInstruction(text)

    def setInput(self, input):
        self.input = input

    def setFinish(self):
        self.finish = True
        self.navigation.setFinish()

    def refresh(self):
        if (self.finish == True):
            dataManager = dataSingleton()

            self.console.clear()

            self.console.append("Files outputted:")

            self.console.append("Low resolution files:")

            lowFiles = dataManager.getFiles("low")


            for item in lowFiles:
                self.console.append(str(item))

            self.console.append("High resolution files:")

            highFiles = dataManager.getFiles("high")

            for item in highFiles:
                self.console.append(str(item))

            self.console.append("Selected for processing files:")

            PCAFiles = dataManager.getPCAFiles()

            for item in PCAFiles:
                self.console.append(str(item))

    def setConsole(self):

        self.console.setVisible(True)

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)

        self.dataFrame = dataSingleton()

        self.layout = QVBoxLayout(self)

        self.instructions = instructionPaneWidget()

        self.layout.addWidget(self.instructions)

        self.console = QTextEdit()
        self.console.setReadOnly(True)

        self.console.setVisible(False)

        self.layout.addWidget(self.console)

        self.navigation = navigationPaneWidget(self)

        self.layout.addWidget(self.navigation, alignment = Qt.AlignBottom)


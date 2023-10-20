from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QGraphicsDropShadowEffect, QLabel

import userConfig
from spharm.customWidgets.animalWidget import animalButton
from spharm.customWidgets.instructionPane import instructionPaneWidget
from spharm.frames.frame import frame
from spharm.managers.dataSingleton import dataSingleton


class animalFrame(frame):

    def rabbitClicked(self):

        animal = "rabbit"
        s = userConfig.UserConfig().getSPHARMDetails(animal,"scale")
        subdivLow = userConfig.UserConfig().getSPHARMDetails(animal,"subdivLow")
        degreeLow = userConfig.UserConfig().getSPHARMDetails(animal,"degreeLow")
        subdivHigh = userConfig.UserConfig().getSPHARMDetails(animal,"subdivHigh")
        degreeHigh = userConfig.UserConfig().getSPHARMDetails(animal,"degreeHigh")

        self.generateOutput(s, subdivLow, degreeLow, subdivHigh, degreeHigh)

    def ratClicked(self):
        animal = "rat"
        s = userConfig.UserConfig().getSPHARMDetails(animal,"scale")
        subdivLow = userConfig.UserConfig().getSPHARMDetails(animal,"subdivLow")
        degreeLow = userConfig.UserConfig().getSPHARMDetails(animal,"degreeLow")
        subdivHigh = userConfig.UserConfig().getSPHARMDetails(animal,"subdivHigh")
        degreeHigh = userConfig.UserConfig().getSPHARMDetails(animal,"degreeHigh")
        self.generateOutput(s, subdivLow, degreeLow, subdivHigh, degreeHigh)


    def mouseAnimalClicked(self):
        animal = "mouse"
        s = userConfig.UserConfig().getSPHARMDetails(animal,"scale")
        subdivLow = userConfig.UserConfig().getSPHARMDetails(animal,"subdivLow")
        degreeLow = userConfig.UserConfig().getSPHARMDetails(animal,"degreeLow")
        subdivHigh = userConfig.UserConfig().getSPHARMDetails(animal,"subdivHigh")
        degreeHigh = userConfig.UserConfig().getSPHARMDetails(animal,"degreeHigh")
        self.generateOutput(s, subdivLow, degreeLow, subdivHigh, degreeHigh)


    def generateOutput(self, s, subdivLow, degreeLow, subdivHigh, degreeHigh):

        self.dataManager.setOutput("animalLow", "sx", s)
        self.dataManager.setOutput("animalLow", "sy", s)
        self.dataManager.setOutput("animalLow", "sz", s)

        self.dataManager.setOutput("animalLow", "degree", degreeLow)
        self.dataManager.setOutput("animalLow", "subdiv", subdivLow)

        self.dataManager.setOutput("animalHigh", "degree", degreeHigh)
        self.dataManager.setOutput("animalHigh", "subdiv", subdivHigh)

        self.dataManager.setOutput("animalHigh", "sx", s)
        self.dataManager.setOutput("animalHigh", "sy", s)
        self.dataManager.setOutput("animalHigh", "sz", s)

        self.nextClicked()

    def setTitle(self, titleName):
        self.instructions.setTitle(titleName)

    def setInstruction(self, text):
        self.instructions.setInstruction(text)

    def setInput(self, input):
        self.input = input

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)

        self.dataManager = dataSingleton()

        layout = QVBoxLayout(self)

        self.instructions = instructionPaneWidget()

        layout.addWidget(self.instructions, alignment = Qt.AlignTop)


        container = QWidget()
        container.setMinimumHeight(50)
        layout.addWidget(container)

        hlayout = QHBoxLayout()



        self.buttonRabbit = animalButton("Rabbit")

        self.buttonRabbit.clicked.connect(self.rabbitClicked)

        self.buttonRat = animalButton("Rat")

        self.buttonRat.clicked.connect(self.ratClicked)

        self.buttonMouse = animalButton("Mouse")

        self.buttonMouse.clicked.connect(self.mouseAnimalClicked)



        hlayout.addWidget(self.buttonRabbit)
        hlayout.addWidget(self.buttonRat)
        hlayout.addWidget(self.buttonMouse)

        layout.addLayout(hlayout)

        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setYOffset(10)
        shadow1.setXOffset(10)
        shadow1.setBlurRadius(15)

        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setYOffset(10)
        shadow2.setXOffset(10)
        shadow2.setBlurRadius(15)

        shadow3 = QGraphicsDropShadowEffect()
        shadow3.setYOffset(10)
        shadow3.setXOffset(10)
        shadow3.setBlurRadius(15)

        self.buttonRabbit.setGraphicsEffect(shadow1)
        self.buttonRat.setGraphicsEffect(shadow2)
        self.buttonMouse.setGraphicsEffect(shadow3)

        self.buttonRabbit.setAttribute(Qt.WA_Hover)
        self.buttonRat.setAttribute(Qt.WA_Hover)
        self.buttonMouse.setAttribute(Qt.WA_Hover)

        container2 = QWidget()
        container2.setMinimumHeight(50)
        layout.addWidget(container2)






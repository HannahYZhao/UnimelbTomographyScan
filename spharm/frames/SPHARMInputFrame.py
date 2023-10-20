from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, \
    QCheckBox

from spharm.customWidgets.flipTemplatePane import flipPathPaneWidget
from spharm.customWidgets.instructionPane import instructionPaneWidget
from spharm.customWidgets.navigationPane import navigationPaneWidget
from spharm.customWidgets.sliderPane import sliderPaneWidget
from spharm.frames.frame import frame
from spharm.managers.dataSingleton import dataSingleton


class SPHARMInputFrame(frame):

    def toggleRescale(self):
        if self.rescaleCheckBox.isChecked():
            self.rescaleContainer.setEnabled(True)
        else:
            self.rescaleContainer.setEnabled(False)

    def toggleFlip(self):
        if self.flipCheckBox.isChecked():
            self.flipPanel.setEnabled(True)
        else:
            self.flipPanel.setEnabled(False)

    def refresh(self):

        if (self.output == "SPHARMInputLow"):

            sx = self.dataManager.getOutput("animalLow","sx")
            sy = self.dataManager.getOutput("animalLow","sy")
            sz = self.dataManager.getOutput("animalLow","sz")

            degree = self.dataManager.getOutput("animalLow","degree")
            subdiv = self.dataManager.getOutput("animalLow","subdiv")

        else:

            sx = self.dataManager.getOutput("animalHigh","sx")
            sy = self.dataManager.getOutput("animalHigh","sy")
            sz = self.dataManager.getOutput("animalHigh","sz")

            degree = self.dataManager.getOutput("animalHigh","degree")
            subdiv = self.dataManager.getOutput("animalHigh","subdiv")

        self.sxSlider.setValue(sx)
        self.sySlider.setValue(sy)
        self.szSlider.setValue(sz)

        self.subdivSlider.setValue(subdiv)
        self.degreeSlider.setValue(degree)

    def setParameters(self, sx, sy, sz, rescale, flip):

        self.sxSlider.setValue(sx)
        self.sySlider.setValue(sy)
        self.szSlider.setValue(sz)

        if (rescale):
            self.rescaleContainer.setEnabled(True)
            self.rescaleCheckBox.setChecked(True)
        else:
            self.rescaleContainer.setEnabled(False)
            self.rescaleCheckBox.setChecked(False)

        if (flip):
            self.flipPanel.setEnabled(True)
            self.flipCheckBox.setChecked(True)
        else:
            self.flipPanel.setEnabled(False)
            self.flipCheckBox.setChecked(False)


    def setTitle(self, titleName):
        self.instructions.setTitle(titleName)

    def setInstruction(self, text):
        self.instructions.setInstruction(text)

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)

        self.dataManager = dataSingleton()

        layout = QVBoxLayout(self)

        self.instructions = instructionPaneWidget()

        layout.addWidget(self.instructions)

        subtitlePost = QLabel("Post Processed Segmentation")

        layout.addWidget(subtitlePost)

        rescaleLayout = QHBoxLayout()

        rescaleLabel = QLabel("Rescale")

        self.rescaleCheckBox = QCheckBox()
        self.rescaleCheckBox.setChecked(False)

        # Connect the checkbox to a function
        self.rescaleCheckBox.clicked.connect(self.toggleRescale)

        rescaleLayout.addWidget(rescaleLabel)
        rescaleLayout.addWidget(self.rescaleCheckBox)

        rescaleLayout.setAlignment(Qt.AlignLeft)

        layout.addLayout(rescaleLayout)

        self.rescaleContainer = QWidget()

        layout.addWidget(self.rescaleContainer)

        layoutRescaleSliders = QVBoxLayout(self.rescaleContainer)

        self.sxSlider = sliderPaneWidget()
        self.sxSlider.setLabelText("sx: ")
        self.sxSlider.setTickInterval(0.1)
        self.sxSlider.setScale(0.01)
        self.sxSlider.setSpinBox(0.01,1.00,0.01)
        self.sxSlider.setSlider(0,100)

        self.sySlider = sliderPaneWidget()
        self.sySlider.setLabelText("sy: ")
        self.sySlider.setTickInterval(0.1)
        self.sySlider.setScale(0.01)
        self.sySlider.setSpinBox(0.01,1.00,0.01)
        self.sySlider.setSlider(0,100)

        self.szSlider = sliderPaneWidget()
        self.szSlider.setLabelText("sz: ")
        self.szSlider.setTickInterval(0.1)
        self.szSlider.setScale(0.01)
        self.szSlider.setSpinBox(0.01,1.00,0.01)
        self.szSlider.setSlider(0,100)

        layoutRescaleSliders.addWidget(self.sxSlider)
        layoutRescaleSliders.addWidget(self.sySlider)
        layoutRescaleSliders.addWidget(self.szSlider)

        if (self.rescaleCheckBox.isChecked()==False):
            self.rescaleContainer.setEnabled(False)


        subtitleMeshLabel = QLabel("Parameters to SPHARM Mesh")
        layout.addWidget(subtitleMeshLabel)


        self.subdivSlider = sliderPaneWidget()
        self.subdivSlider.setLabelText("SubdivLevel value: ")
        self.subdivSlider.setTickInterval(20)
        self.subdivSlider.setScale(1.00)
        self.subdivSlider.setSpinBox(1.00,100.00,10.0)
        self.subdivSlider.setSlider(1,100)

        layout.addWidget(self.subdivSlider)

        self.degreeSlider = sliderPaneWidget()
        self.degreeSlider.setLabelText("SPHARM Degree value: ")
        self.degreeSlider.setTickInterval(20)
        self.degreeSlider.setScale(1.00)
        self.degreeSlider.setSpinBox(0.00,95.00,10.0)
        self.degreeSlider.setSlider(0,95)

        layout.addWidget(self.degreeSlider)


        subtitleAdvancedLabel = QLabel(
            "Advanced Parameters to SPHARM Mesh")
        layout.addWidget(subtitleAdvancedLabel)

        flipLayout = QHBoxLayout()
        flipLayout.setAlignment(Qt.AlignLeft)

        flipLabel = QLabel("Use Flip Template")

        self.flipCheckBox = QCheckBox()
        self.flipCheckBox.setChecked(False)

        self.flipCheckBox.clicked.connect(self.toggleFlip)

        flipLayout.addWidget(flipLabel)
        flipLayout.addWidget(self.flipCheckBox)

        layout.addLayout(flipLayout)

        self.flipPanel = flipPathPaneWidget()
        self.flipPanel.setButtonText("Select Flip Template")

        layout.addWidget(self.flipPanel)

        buttonLayout = QHBoxLayout()

        self.navigation = navigationPaneWidget(self)

        layout.addWidget(self.navigation, alignment = Qt.AlignBottom)


    def nextClicked(self):

        #TODO: add checks to validate data

        sx = self.sxSlider.getValue()
        sy = self.sySlider.getValue()
        sz = self.szSlider.getValue()

        subdiv = self.subdivSlider.getValue()
        degree = self.degreeSlider.getValue()
        flip = self.flipCheckBox.isChecked()
        flipTemplate = self.flipPanel.getFilePath()

        #Output, parameter, value
        self.dataManager.setOutput(self.output, "sx",
                                 sx)
        self.dataManager.setOutput(self.output, "sy",
                                 sy)
        self.dataManager.setOutput(self.output, "sz",
                                 sz)

        self.dataManager.setOutput(self.output, "subdiv", subdiv)
        self.dataManager.setOutput(self.output, "degree", degree)
        self.dataManager.setOutput(self.output, "flip", flip)
        self.dataManager.setOutput(self.output, "flipTemplate", flipTemplate)

        super().nextClicked()

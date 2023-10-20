"""
Code written by: Robert Sharp 186477
Yuxiang Wu 1006014 (progress bar)

"""
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, \
    QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QTextEdit

from spharm.customWidgets.instructionPane import instructionPaneWidget
from spharm.customWidgets.navigationPane import navigationPaneWidget
from spharm.customWidgets.progressPane import progressPaneWidget
from spharm.frames.frame import frame
from spharm.managers.dataSingleton import dataSingleton


class progressFrame(frame):

    def fileProcessed(self):

        self.progressBar.fileProcessed()

    def setTitle(self, titleName):
        self.instructions.setTitle(titleName)

    def setInstruction(self, text):
        self.instructions.setInstruction(text)

    def cancelProcess(self):

        self.cancelButton.setEnabled(False)
        self.runButton.setEnabled(True)
        self.programManager.cancel()

    def runProcess(self):

        self.hasIssuedComplete = False

        self.runButton.setEnabled(False)

        self.cancelButton.setEnabled(True)

        self.progressBar.setTotalFiles(self.programManager.getTotalFiles())

        self.editor.clear()

        self.progressBar.startProcess()

        self.programManager.run()


    def setProgramManagerType(self, type):
        self.type = type
        if ((self.type == "low") or (self.type == "high")):
            self.programManager.setType(type)

    def setProgramManager(self, programManager):

        self.programManager = programManager

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)


        self.hasIssuedComplete = False

        layout = QVBoxLayout(self)

        self.type = None

        self.dataManager = dataSingleton()

        self.instructions = instructionPaneWidget()

        layout.addWidget(self.instructions)


        #self.checkButton = QPushButton("Check")
        #layout.addWidget(self.checkButton)

        #Run button


        self.runButton = QPushButton("Run")

        shadow = QGraphicsDropShadowEffect()
        shadow.setYOffset(10)
        shadow.setXOffset(10)
        shadow.setBlurRadius(15)
        self.runButton.setGraphicsEffect(shadow)

        self.runButton.setFixedSize(250,50)

        self.runButton.setStyleSheet("""padding: 10px;
                                     font-size:   24px;
        font-weight: 500;
                                     """)

        self.runButton.setContentsMargins(0,50,0,50)


        #layout.addWidget(self.runButton, alignment = Qt.AlignHCenter)

        #Cancel button

        self.cancelButton = QPushButton("Cancel")

        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setYOffset(10)
        shadow2.setXOffset(10)
        shadow2.setBlurRadius(15)
        self.cancelButton.setGraphicsEffect(shadow2)

        self.cancelButton.setFixedSize(250,50)

        self.cancelButton.setStyleSheet("""padding: 10px;
                                     font-size:   24px;
        font-weight: 500;
                                     """)

        self.cancelButton.setContentsMargins(0,50,10,50)

        #Connect buttons

        self.runButton.clicked.connect(self.runProcess)

        self.cancelButton.clicked.connect(self.cancelProcess)

        layoutCancelRun = QHBoxLayout()
        layoutCancelRun.addWidget(self.runButton)
        #layoutCancelRun.addWidget(self.cancelButton)
        self.cancelButton.setEnabled(False)

        layout.addLayout(layoutCancelRun)

        self.timeEstimateLabel = QLabel("")
        self.timeEstimateLabel.setContentsMargins(20,50,0,0)
        layout.addWidget(self.timeEstimateLabel, alignment = Qt.AlignBottom)


        self.progressBar = progressPaneWidget()



        label = QLabel()
        label.setFixedSize(10,50)
        layout.addWidget(label)


        layout.addWidget(self.progressBar)

        self.editor = QTextEdit()
        self.editor.setReadOnly(True)

        layout.addWidget(self.editor)

        self.navigation = navigationPaneWidget(self)

        self.navigation.nextDisabled()

        layout.addWidget(self.navigation, alignment = Qt.AlignBottom)


        #self.checkButton.clicked.connect(self.finishedProcess)

    def updateTimeEstimate(self, hour, min, sec):
        text = "Estimated time remaining is {} hours, {} mins and {} seconds".format(hour, min, sec)
        self.timeEstimateLabel.setText(text)

    def nextClicked(self):

        super().nextClicked()

    def finishedProcess(self):

        #print("Process finished")

        self.runButton.setEnabled(True)
        self.cancelButton.setEnabled(False)

        list = []

        if self.type == "low":
            #print("checking low")
            list = self.dataManager.checkFiles("low")
        if self.type == "high":
            #print("checking high")
            list = self.dataManager.checkFiles("high")

        #print("finished checking")
        #print(list)

        if (list==[]):
            #print("complete")
            if (self.hasIssuedComplete == False):
                self.hasIssuedComplete = True
                self.issueComplete('The Process has finished')
        else:
            #print("warning")
            self.issueWarning('The Process completed with the following files missing: ', list)
        self.navigation.nextEnabled()
        #print("done")


    def writeError(self, text):

        redOutput = "<span style=\" color:#FF0000;\" >"
        redOutput += text
        redOutput +="</span>"
        self.editor.append(redOutput)

    def writeCompletedOutput(self, text):

        greenOutput = "<span style=\" color:#009400;\" >"
        greenOutput += text
        greenOutput +="</span>"
        self.editor.append(greenOutput)

    def writeStandardOutput(self, text):

        self.editor.append(text)





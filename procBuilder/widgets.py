# Rohan Jahagirdar 835450 - Wrote most widgets
# Michael - minor improvements using signals
# Robert Sharp 186477 - Wrote Light Widget, updated formating to remove background

import subprocess

from PySide2 import QtCore, QtGui
from PySide2.QtCore import QStringListModel, Signal, QSize
from PySide2.QtGui import Qt, QIcon
from PySide2.QtWidgets import QFileDialog, QListWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, \
    QScrollArea, QCheckBox, QHBoxLayout, QTextEdit
from ryvencore_qt.src.WidgetBaseClasses import IWB, MWB

import resourceManager as rm

import userConfig
from constants import DARK_MODE
from visualisation.visualisationGui import VisualisationWindow
import procBuilder.nodes as nodes



class lightParentWidget():

    def __init__(self, parent):
        self.lightWidget = parent.lightWidget

    def changeToWait(self, type):

        self.lightWidget.changeToWait(type)

    def changeToError(self, e):

        self.lightWidget.changeToError(e)

    def changeToRun(self, hasOutput, path=None):
        print(path)
        self.lightWidget.changeToRun(hasOutput, path)

    def reset(self):
        self.lightWidget.reset()

    def startUpdate(self):
        self.lightWidget.startUpdate()

    def hasChanged(self):
        self.lightWidget.hasChanged()

    def hasAllInputs(self):
        self.lightWidget.hasAllInputs()

class singleLightWidget(MWB, QWidget, lightParentWidget):

    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.lightWidget = lightButton()

        lightParentWidget(self)
        layout = QHBoxLayout()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayout(layout)
        self.layout().addWidget(self.lightWidget)

class FileOpenWidget(MWB, QWidget):
    '''The Widget used in a FileOpen node'''
    value_changed = Signal(object)

    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.file_path = None
        self.file_count = 0
        self.listWidget = QListWidget(self)
        self.labelWidget = QLabel(str(self.file_count) + ' files selected')
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.labelWidget)
        b = QPushButton('Select File')
        b.clicked.connect(self.button_clicked)
        self.layout().addWidget(b)
        self.layout().addWidget(self.listWidget)

        self.setAttribute(Qt.WA_TranslucentBackground)

        if (userConfig.UserConfig().getColorThemeCode() == DARK_MODE):
            self.labelWidget.setStyleSheet("color: #4e585c")
            b.setStyleSheet(userConfig.UserConfig().getColorTheme())
            self.listWidget.setStyleSheet(userConfig.UserConfig().getColorTheme())

    def button_clicked(self):
        dialog = QFileDialog()
        dialog.setWindowTitle("Choose .vtk files to open")
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilters(["VTK files (*.vtk)"])
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setDirectory(userConfig.UserConfig().getLatestFolder())

        filename = QtCore.QStringListModel()
        if dialog.exec_():
            filename = dialog.selectedFiles()
            self.listWidget.clear()
            self.file_count = 0
            for file in filename:
                self.listWidget.addItem(file)
                self.file_count = self.file_count + 1
            self.value_changed.emit(filename)
            self.labelWidget.setText(str(self.file_count) + ' files selected')
        else:
            self.value_changed.emit(filename)

#Code for this lightButton class by Robert Sharp, 186477
class lightButton(QWidget):

    def __init__(self):

        styleSheet = """QToolTip {
        background: white;
        color: black;
        }"""

        QWidget.__init__(self)

        self.reset()

        layout = QVBoxLayout(self)

        self.setStyleSheet("border: 0px; background-color: transparent;")
        #self.setStyleSheet("border: 0px; background-color: white;")

        self.Button = QPushButton(self)
        #icon

        self.Button.clicked.connect(self.clicked)

        layout.addWidget(self.Button)

        self.Button.setIconSize(QSize(100,100))

        self.changeToWait("reset")

        self.Button.setStyleSheet(styleSheet)

    def setWaitingState(self):
        self.state = "wait"
        self.Button.setIcon(rm.getIcon("yellow_light.png"))
        self.Button.setToolTip("Module is waiting. "+self.waitReason) #Tool tip

    def setRunState(self):

        self.state = "run"

        self.Button.setIcon(rm.getIcon("green_light.png"))
        if (self.hasOutput):
            self.Button.setToolTip("Module successfully completed. Click to view output.") #Tool tip
        else:
            self.Button.setToolTip("Module successfully completed")

    def setErrorState(self):

        self.state = "error"

        self.Button.setIcon(rm.getIcon("red_light.png"))

        if self.errorCode:
            self.Button.setToolTip("Module encountered an error: "+ str(self.errorCode)) #Tool tip
        else:
            self.Button.setToolTip("Module encountered an error.")

    def clicked(self):
        if self.state == "run":
            if (self.hasOutput):
                subprocess.Popen( 'explorer '+self.outputPath.replace("/","\\") )

    def changeToWait(self, type):
        if type == "reset":
            self.errorCode = None
            self.reset()
            self.waitReason = "Yet to update."
        if type == "noChange":
            self.waitReason = "None of the inputs have changed."
        elif type == "missingInput":
            self.waitReason = "One or more inputs is missing."
        self.setWaitingState()

    def changeToError(self, e):
        if e:
            self.errorCode = e
        self.setErrorState()

    def changeToRun(self, hasOutput, path=None):
        if hasOutput:
            self.hasOutput = hasOutput
            self.outputPath = path
        self.setRunState()

    def reset(self):
        self.hasOutput = False
        self.errorCode = None
        self.waitReason = None
        self.outputPath = None
        self.state = None

    def startUpdate(self):
        if not (self.state == "error"):
            self.changeToWait("noChange")

    def hasChanged(self):
        if not (self.state == "error"):
            self.changeToWait("missingInput")

    def hasAllInputs(self):
        if not (self.state == "error"):
            self.changeToWait("noChange")

class FileOpenTFMATWidget(MWB, QWidget):
    '''The Widget used in a FileOpen node'''
    value_changed = Signal(object)

    def __init__(self, params):



        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.file_path = None
        self.file_count = 0
        self.listWidget = QListWidget(self)
        self.labelWidget = QLabel(str(self.file_count) + ' files selected')
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.labelWidget)
        b = QPushButton('Select File')
        b.clicked.connect(self.button_clicked)
        self.layout().addWidget(b)
        self.layout().addWidget(self.listWidget)
        self.setAttribute(Qt.WA_TranslucentBackground)

        if (userConfig.UserConfig().getColorThemeCode() == DARK_MODE):
            self.labelWidget.setStyleSheet("color: #4e585c")
            b.setStyleSheet(userConfig.UserConfig().getColorTheme())
            self.listWidget.setStyleSheet(userConfig.UserConfig().getColorTheme())


    def button_clicked(self):
        dialog = QFileDialog()
        dialog.setWindowTitle("Choose .dat files to open")
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilters(["TFMAT files (*.dat)"])
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setDirectory(userConfig.UserConfig().getLatestFolder())

        filename = QtCore.QStringListModel()
        if dialog.exec_():
            filename = dialog.selectedFiles()
            self.listWidget.clear()
            self.file_count = 0
            for file in filename:
                self.listWidget.addItem(file)
                self.file_count = self.file_count + 1
            self.value_changed.emit(filename)
            self.labelWidget.setText(str(self.file_count) + ' files selected')
        else:
            self.value_changed.emit(filename)

class OutputConsoleWidget(MWB, QWidget):
    '''Console'''


    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.console)
        b = QPushButton('Clear Console')
        b.clicked.connect(self.clear_output)
        self.layout().addWidget(b)

    def clear_output(self):
        self.console.clear()

    #text will be a single line
    def add_output(self, text):
        self.console.append(text)

class DirectorySelect2(MWB, QWidget):
    '''The Widget used in a FolderSelect node'''
    directory2_selected = Signal(object)
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.val = None

        self.checkBox = QCheckBox()
        self.checkBox.setChecked(False)
        self.checkBox.setEnabled(False)

        vLayout = QVBoxLayout()

        hLayout = QHBoxLayout()

        hLayout.setContentsMargins(0,10,50,10)
        hLayout.setSpacing(5)

        self.checkBox.setContentsMargins(0,0,0,0)

        hLayout.addWidget(self.checkBox, alignment=Qt.AlignLeft)

        b = QPushButton('Select Folder')
        b.clicked.connect(self.button_clicked)
        b.setMaximumWidth(120)

        b.setContentsMargins(0,0,0,0)

        hLayout.addWidget(b, alignment=Qt.AlignLeft)
        #self.layout().addWidget(b)
        vLayout.addLayout(hLayout)
        q = QScrollArea()
        q.setMaximumWidth(150)
        q.setMaximumHeight(50)

        self.l = QLabel("")

        q.setWidget(self.l)
        vLayout.addWidget(q)

        self.setLayout(vLayout)

        self.setAttribute(Qt.WA_TranslucentBackground)

        if (userConfig.UserConfig().getColorThemeCode() == DARK_MODE):
            self.l.setStyleSheet("color: #4e585c")
            b.setStyleSheet(userConfig.UserConfig().getColorTheme())
            q.setStyleSheet(userConfig.UserConfig().getColorTheme())
            self.checkBox.setStyleSheet(userConfig.UserConfig().getColorTheme())
            self.checkBox.setAttribute(Qt.WA_TranslucentBackground)


    def button_clicked(self):
        dialog = QFileDialog()
        folderpath = QtCore.QStringListModel()
        #folderpath = dialog.getExistingDirectory(None, 'Select Folder')
        folderpath = dialog.getExistingDirectory(None, 'Select directory',  userConfig.UserConfig().getLatestFolder())
        self.l.setText(folderpath)
        width = self.l.fontMetrics().boundingRect(folderpath).width()
        self.l.setMinimumWidth(width)
        if len(folderpath)>0:
            #Only update the outputs if the folder is not ""
            self.directory2_selected.emit(folderpath)
            userConfig.UserConfig().setLatestFolder(folderpath)
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)

class NameInput(MWB, QWidget, lightParentWidget):
    '''The Widget used in a Write File List Summary Node'''

    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)


        self.lightWidget = lightButton()

        lightParentWidget(self)

        lightLayout = QHBoxLayout()


        self.val = None

        self.checkBox = QCheckBox()
        self.checkBox.setChecked(False)
        self.checkBox.setEnabled(False)

        vLayout = QVBoxLayout()

        lightLayout.addLayout(vLayout)
        lightLayout.addWidget(self.lightWidget)

        hLayout = QHBoxLayout()

        hLayout.setContentsMargins(0,10,50,10)
        hLayout.setSpacing(5)

        self.checkBox.setContentsMargins(0,0,0,0)

        hLayout.addWidget(self.checkBox, alignment=Qt.AlignLeft)

        l = QLabel('Set file name:')

        l.setContentsMargins(0,0,0,0)

        hLayout.addWidget(l, alignment=Qt.AlignLeft)

        vLayout.addLayout(hLayout)
        self.le = QLineEdit()
        self.le.setMaximumWidth(150)
        self.le.setMaximumHeight(50)

        vLayout.addWidget(self.le)

        self.setLayout(lightLayout)

        self.le.textChanged.connect(self.checkBlank)

        self.setAttribute(Qt.WA_TranslucentBackground)

        if (userConfig.UserConfig().getColorThemeCode() == DARK_MODE):
            l.setStyleSheet("color: #4e585c")
            self.le.setStyleSheet(userConfig.UserConfig().getColorTheme())
            self.checkBox.setStyleSheet(userConfig.UserConfig().getColorTheme())
            self.checkBox.setAttribute(Qt.WA_TranslucentBackground)

    def getText(self):
        return self.le.text()

    def checkBlank(self):
        if self.le.text()!="":
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)



class DirectorySelect(MWB, QWidget):
    '''The Widget used in a FolderSelect node'''
    directory_selected = Signal(object)
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)
        self.val = None
        self.setLayout(QVBoxLayout())
        b = QPushButton('Select Folder')
        b.clicked.connect(self.button_clicked)
        self.layout().addWidget(b)

    def button_clicked(self):
        dialog = QFileDialog()
        folderpath = QtCore.QStringListModel()
        folderpath = dialog.getExistingDirectory(None, 'Select Folder')
        self.directory_selected.emit(folderpath)

class ButtonWidget(MWB, QWidget):
    '''The Widget used in a node with a Rerun on Same Inputs button'''
    button_press = Signal(object)
    def __init__(self, params):

        styleSheet = """QToolTip {
        background: white;
        color: black;
        }"""

        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.val = False
        self.setLayout(QVBoxLayout())
        b = QPushButton()
        b.setToolTip('Reopen visualisation window')
        b.setStyleSheet(styleSheet)
        b.setIconSize(QSize(100,100))
        if (userConfig.UserConfig().getColorThemeCode() == DARK_MODE):
            b.setIcon(rm.getIcon("play_circular_button_dark.png"))
        else:
            b.setIcon(rm.getIcon("play_circular_button_light.png"))
        b.clicked.connect(self.button_clicked)
        self.layout().addWidget(b)
        self.setStyleSheet("border: 0px; background-color: transparent;")

    def button_clicked(self):
        self.val = True
        #windowSingleton().makeRunable(self.session)
        self.button_press.emit(self.val)
        #nodes.NodeBase.makeUnRunable()

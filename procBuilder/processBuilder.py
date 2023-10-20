# Michael Thomas 912226 - Wrote most functions
# Robert Sharp 186477 - Reset process
# Rohan Jahagirdar 835450 - saving and loading


from PySide2 import QtGui
from PySide2.QtWidgets import QMessageBox

import resourceManager as rm
from errorWindow import ErrorWindow
from procBuilder.windowSingleton import windowSingleton
from userConfig import UserConfig
from mainWindow import MainWindow
from procBuilder import pbutil
from procBuilder.nodes import NodeBase, VisualiseVTKImage, FileOpenNode, FileOpenTFMATNode, SelectFolderNode, WriteFileNode, CalculateTFMAT, AlignedVTKFiles, SPHARMNode, CopyFilesNode, CreateDirectoriesNode, Connector
import json
from qtpy.QtWidgets import QApplication, QHBoxLayout, QWidget, QFileDialog, QAction
from constants import *
import sys
import os

import ryvencore_qt as rc
os.environ['QT_API'] = 'pyside2'
# from PySide2.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget
# --------------- IMPORTANT ---------------
# Import nodes used in diagram here

# The actual window where processes are placed


class ProcessBuilderWindow(MainWindow):
    def __init__(self, loaded_file=None):
        super().__init__()

        self.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.setWindowTitle("Process Builder")

        # start ryvencore session
        self.session = rc.Session()

        #Get unique windowID

        self.windowId = windowSingleton().getWindowId(self.session)

        #Make sure session is cleared
        windowSingleton().makeUnRunableWindow(self.windowId)
        windowSingleton().stopStepModeWindow(self.windowId)
        windowSingleton().setNextNodesSession(self.windowId, [])

        # some design specs
        self.session.design.set_flow_theme(name='pure light')
        self.session.design.set_performance_mode('pretty')

        # registering the nodes
        self.session.register_nodes(
            [
                # --------------- IMPORTANT ---------------
                # List nodes to use in diagram here
                VisualiseVTKImage,
                FileOpenNode,
                SelectFolderNode,
                WriteFileNode,
                CalculateTFMAT,
                AlignedVTKFiles,
                SPHARMNode,
                CopyFilesNode,
                CreateDirectoriesNode,
                FileOpenTFMATNode,
                Connector
            ]
        )
        self.loaded_file = loaded_file
        if self.loaded_file != None:
            scripts = self.getLoadedScripts(self.loaded_file)
            self.script = scripts[0]
            for script in scripts:
                view = self.session.flow_views[script]
                #TODO: check this?
                self.session.flow_views[script]._stylus_modes_widget.hide()
        else:
            self.script = self.session.create_script(title='main')
            view = self.session.flow_views[self.script]
            #TODO: check this?
            self.session.flow_views[self.script]._stylus_modes_widget.hide()

        # creating a widget and adding the flow view of the script
        self.w = QWidget()
        self.w.setLayout(QHBoxLayout())
        self.w.layout().addWidget(view)

        self.setCentralWidget(self.w)
        self.resize(1600, 900)  # resizing the window

        # Connect function for handling node type validation
        self.script.flow.connection_added.connect(self.doTypeChecking)

        # dtypes.dtypes.append(TypedData)

        self.createMenuBarUI()
        self.loadPBColorTheme()

    # Function to do type checking. Is a PyQt Slot. Called by connection_added.
    def doTypeChecking(self, connection):
        '''Callable function to check data types of connection created'''
        toRemove = None
        # Node that has the inputs, the 'output' side of the connection
        inNode = connection.inp.node
        # Node that has the outputs, the 'input' side of the connection
        outNode = connection.out.node

        # For nodes that have multiple ports, identify which ones are used in this connection, then check if the types are valid
        for inInd in range(len(inNode.inputs)):
            # Port is one in Connection object
            if connection.inp.GLOBAL_ID == inNode.inputs[inInd].GLOBAL_ID:
                for outInd in range(len(outNode.outputs)):
                    # Port is one in Connection object
                    if connection.out.GLOBAL_ID == outNode.outputs[outInd].GLOBAL_ID:
                        if not pbutil.isSameType(outNode.outputTypes[outInd], inNode.inputTypes[inInd]):
                            toRemove = (
                                connection, outNode.outputTypes[outInd], inNode.inputTypes[inInd])
                            break
                break

        # Removal done outside loops as function changes lists iterated over
        if toRemove:
            # Create message to let users know, and then remove the item
            self.errorWindow = ErrorWindow()
            self.errorWindow.setMessageText(
                "Invalid Connection: Types '" + toRemove[1] + "' and '" + toRemove[2] + "' are incompatible")
            self.script.flow.remove_connection(toRemove[0])

    def createNewProcess(self):
        '''Create a new Process Builder window and display it'''
        print('Create new process')
        self.pb = ProcessBuilderWindow()
        self.pb.show()

    def loadProcess(self):
        '''Load a saved process'''
        print('Load process')

        # Select file to load
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        # fileDialog.setDirectory(PROCESSES)
        filePath, _ = fileDialog.getOpenFileNames(
            self, "Open File ", rm.resourcePath(rm.PROCESSES), "*.json")
        if _:

            loaded_file = filePath[0]
            self.pb = ProcessBuilderWindow(loaded_file=loaded_file)
            self.pb.show()
         
    def getLoadedScripts(self, filePath):
        '''Helper function to load the scripts into a ryvencore session'''
        with open(filePath, 'r') as f:
            project_str = f.read()

        project_dict = json.loads(project_str)

        scripts = self.session.load(project_dict)
        return scripts

    def saveProcess(self):
        '''Save a process to a known json file. If file is unknown, call save as'''
        print('Save process')
        project: dict = self.session.serialize()

        if self.loaded_file is not None:
            with open(self.loaded_file, 'w') as f:
                f.write(json.dumps(project))
        else:
            self.saveProcessAs()

    def saveProcessAs(self):
        '''Save a process to a new json file'''
        print('Save process as...')
        # Select directory to save
        dirDialog = QFileDialog()
        filename, _ = dirDialog.getSaveFileName(
            None, "Save Process", dir=rm.resourcePath(rm.PROCESSES), filter="*.json")
        project: dict = self.session.serialize()
        temp = filename
        #Only add .json if it doesn't end with .json already
        if not temp.endswith(".json"):
            temp = temp + ".json"
        with open(temp, 'w') as f:
            f.write(json.dumps(project))

    def resetProcess(self):
        '''Reset the process'''
        print('Reset process')

        #windowSingleton().makeUnRunableWindow(self.windowId)
        windowSingleton().clearNextNodeRunWindow(self.windowId)

        for node in self.script.flow.nodes:
            node.clearData()
            node.hasRun = False
            #Set all the lights to yellow
            if node.isLightNode:
                node.main_widget().changeToWait("reset")
        #This avoids bug of having to press step twice after resetting
        if windowSingleton().isStepSession(self.session):
            self.runStep()
        #windowSingleton().makeRunableWindow(self.windowId)

    def runProcess(self):
        '''Run the process'''
        print('Run process')
        # Make the process runnable, then for each dataInputNode, call update
        windowSingleton().stopStepModeWindow(self.windowId)
        windowSingleton().makeRunableWindow(self.windowId)

        for node in self.script.flow.nodes:
            node.clearData()
            node.hasRun = False
            #Set all the lights to yellow
            if node.isLightNode:
                node.main_widget().changeToWait("reset")

        for node in self.script.flow.nodes:
            if node.isDataInputNode:
                node.update()


        # Once done, make un-runnable again
        windowSingleton().makeUnRunableWindow(self.windowId)

    def runStep(self):
        print("Running step")
        windowSingleton().stepThroughProcess(self.windowId, self.script.flow.nodes)

    def clearProcess(self):
        '''Remove all nodes from the screen'''
        print("Clear process")

        window = QMessageBox()
        window.setWindowTitle('Notification')
        window.setInformativeText("Are you sure you wish to delete nodes and connections?")
        window.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        window.setStyleSheet(UserConfig().getColorTheme())
        window.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        screen = QApplication.primaryScreen()
        xPosition = screen.size().width() / 2 - EW_WIDTH / 2
        yPosition = screen.size().height() / 2 - EW_HEIGHT / 2
        window.setGeometry(xPosition, yPosition, EW_WIDTH, EW_HEIGHT)
        answer = window.exec_()
        if answer == QMessageBox.Ok:

            s = self.session.scripts
            flow = s[0].flow
            nodes = []
            connections = []
            for n in flow.nodes:
                nodes.append(n)
            for c in flow.connections:
                connections.append(c)
            for connection in connections:
                flow.remove_connection(connection)
            for node in nodes:
                flow.remove_node(node)


    def activateStepMode(self, isChecked):
        '''Activate step mode'''
        if isChecked:
            self.runStepAction.setEnabled(True)
            self.runAction.setEnabled(False)
            windowSingleton().startStepModeWindow(self.windowId)
        else:
            self.runStepAction.setEnabled(False)
            self.runAction.setEnabled(True)
            windowSingleton().stopStepModeWindow(self.windowId)

    def createMenuBarUI(self):
        '''Helper function to create the menu bar'''
        self.createFileMenuBarUI()
        self.createProcessMenuBarUI()
        self.createRunStepMenuBarUI()
        super().createSettingsMenuBarUI()
        super().createHelpMenuBarUI()

    def createFileMenuBarUI(self):
        '''Create the File submenu on the menu bar'''
        fileMenu = self.menuBar.addMenu('File')

        newAction = QAction('New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.createNewProcess)

        loadAction = QAction('Load...', self)
        loadAction.setShortcut('Ctrl+L')
        loadAction.triggered.connect(self.loadProcess)

        saveAction = QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveProcess)

        saveAsAction = QAction('Save As...', self)
        saveAsAction.triggered.connect(self.saveProcessAs)

        fileMenu.addAction(newAction)
        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)

    def createProcessMenuBarUI(self):
        '''Create the Process submenu on the menu bar'''
        processMenu = self.menuBar.addMenu("Process")

        self.runAction = QAction('Run Process', self)
        self.runAction.triggered.connect(self.runProcess)

        resetAction = QAction('Reset Process', self)
        resetAction.triggered.connect(self.resetProcess)

        clearAction = QAction('Clear Process', self)
        clearAction.triggered.connect(self.clearProcess)

        activateStepMode = QAction('Activate Step Mode', self)
        activateStepMode.setCheckable(True)
        activateStepMode.triggered.connect(lambda: self.activateStepMode(activateStepMode.isChecked()))

        processMenu.addAction(self.runAction)
        processMenu.addAction(clearAction)
        processMenu.addAction(activateStepMode)
        processMenu.addAction(resetAction)

    def createRunStepMenuBarUI(self):
        '''Create the Run Step submenu on the menu bar'''
        runStepMenu = self.menuBar.addMenu("Run Step")

        self.runStepAction = QAction("Run Step", self)
        self.runStepAction.setShortcut('Ctrl+T')
        self.runStepAction.setEnabled(False)
        self.runStepAction.triggered.connect(self.runStep)

        runStepMenu.addAction(self.runStepAction)

    def loadPBColorTheme(self):
        if UserConfig().getColorThemeCode() == LIGHT_MODE:
            self.session.design.set_flow_theme(name='pure light')
        elif UserConfig().getColorThemeCode() == DARK_MODE:
            self.session.design.set_flow_theme(name='pure dark')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = ProcessBuilderWindow()
    mw.show()

    sys.exit(app.exec_())

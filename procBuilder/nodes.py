# Michael Thomas 912226 - Wrote template nodes, wrote the step process update, general clean up of nodes/refactoring
# Yibo Peng 1050419 - Wrote the orignal version of the CalculateTFMAT node and AlignedVTKFiles node
# Rohan Jahagirdar 835450 - Wrote the generic nodes such as file open, write file and select folder nodes

# Standard Libraries

import math
import os
import shutil
import time
import copy

# some Qt imports...
import ryvencore_qt as rc

# Custom files
import procBuilder.pbutil as pbutil
from errorWindow import ErrorWindow
from procBuilder.widgets import FileOpenWidget, ButtonWidget, DirectorySelect2, NameInput, FileOpenTFMATWidget, \
    OutputConsoleWidget, singleLightWidget
from procBuilder.windowSingleton import windowSingleton
from spharm.SPHARMDriver import SPHARMDriver
from visualisation.visualisationGui import VisualisationWindow
from transformation.MultipleVTKFileOperation import MultipleVTKFileOperation


# This is a base node that all node inherit from, and is used to set things all nodes share
class NodeBase(rc.Node):
    """Base class for the nodes in this application"""

    color = '#cc7777' # The colour of the node in the node selection menu
    init_inputs = [] # An array of the inputs to this node. Override in your node if there are inputs
    init_outputs = [] # An array of the outputs from this node. Override in your node if there are outputs
    inputTypes = [] # An array of the data type of each input (from pbutil). Must be same size as number of inputs
    outputTypes = [] # An array of the data type of each output (from pbutil). Must be same size as number of output

    # Constructor for a node.
    def __init__(self, params):
        super().__init__(params)

        self.windowId = windowSingleton().getWindowId(self.session)

        self.inputData = [None] * len(self.init_inputs) # Stores the input, so we can do logic on when to run a node again
        self.outputData = [None] * len(self.init_outputs) # Store the output, so we can do logic on when to run a node again
        self.isDataInputNode = False # By default, all nodes are not data input nodes that need to be run to start a process

        self.isLightNode = False #Set to false by default, set it to true if has a light widget in the node

        self.hasRun = False

        self.isInteresting = False #Set to true for interesting nodes

    # Makes saving a node work.
    def get_state(self) -> dict:
        # saving signal state
        return {
            'inputData': self.inputData,
            'outputData': self.outputData,
            "isDataInputNode": self.isDataInputNode
        }

    # Resets a nodes state after loading
    def set_state(self, data):
        # reloading signal state
        self.inputData = data['inputData']
        self.outputData = data['outputData']
        self.isDataInputNode = data['isDataInputNode']

    def update_event(self, inp=-1):


        #if NodeBase.PROCESS_STEP_MODE[self.windowId] and not NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
        if windowSingleton().isStepWindow(self.windowId) and not windowSingleton().canRunWindow(self.windowId):
            #if self not in NodeBase.NEXT_NODE_TO_RUN[self.windowId]:
            if not windowSingleton().nodeInNextToRunWindow(self.windowId, self):
                #NodeBase.NEXT_NODE_TO_RUN[self.windowId].insert(1, self)
                #windowSingleton().insertNextNodeToRunWindow(self.windowId, self)
                windowSingleton().addNextNodeWindow(self.windowId, self)

    def setOutputs(self, outputs):
        self.outputData = outputs
        for index in range(len(outputs)):
            self.set_output_val(index, outputs[index])

    #New functions to remove repetitive code:
    #Returns true if at least one input has changed
    def checkHasChangedInputs(self):
        n = len(self.inputData)
        for index in range(n):
            if self.input(index)!=self.inputData[index]:
                return True
        return False

    #Returns true if none of the inputs are None. Checks both data and type
    def checkHasAllInputs(self):
        n = len(self.inputData)
        for index in range(n):
            inData = self.input(index)
            if inData == None:
                return False
            if (inData['type']==None) or (inData['data']==None):
                return False
        return True

    #Updates the inputs. Should be called after a node has changed
    def updateInputs(self):
        n = len(self.inputData)
        for index in range(n):
            self.inputData[index] = self.input(index)
        # Once stored, reset inputs to None
        for input in self.inputs:
            input.val = None

    #Returns a list of inputs
    def getInputData(self):
        list = []
        for item in self.inputData:
            list.append(item['data'])
        return list

    def clearData(self):
        for index in range(len(self.inputData)):
            self.inputData[index] = None

        for input in self.inputs:
            input.val = None

        for index in range(len(self.outputData)):
            self.outputData[index] = None

        for index in range(len(self.outputData)):
            self.set_output_val(index, None)


# A node that allows the user to select a group of VTK files to enter into the 
class FileOpenNode(NodeBase):
    """Select a VTK file / group of VTK files"""

    title = 'Select VTK Files'
    init_outputs = [
        rc.NodeOutputBP(label="Selected files", type_="data")
    ]
    outputTypes = [
        pbutil.FILE_LIST_VTK
    ]
    main_widget_class = FileOpenWidget # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.val = None
        self.isDataInputNode = True

    def place_event(self): # When placed, update the widget
        self.update()

    # Register the widget for this node
    def view_place_event(self):
        self.main_widget().value_changed.connect(self.main_widget_val_changed)

    # Pass changes from the widget to the node itself
    def main_widget_val_changed(self, val):
        self.val = val
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            self.hasRun = True

            # Because dataInputNode, always set the output
            self.set_output_val(0, pbutil.getNewTypedData(pbutil.FILE_LIST, self.val))
            print("Files selected count: " + str(len(self.val) if self.val else 0))


# A node that allows the user to select a group of VTK files to enter into the
class FileOpenTFMATNode(NodeBase):
    """Open a TMAT file / group of TMAT files"""

    title = 'Select TFMAT Files'
    init_outputs = [
        rc.NodeOutputBP(label="Selected files", type_="data")
    ]
    outputTypes = [
        pbutil.FILE_LIST_TFMAT
    ]
    main_widget_class = FileOpenTFMATWidget # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.val = None
        self.isDataInputNode = True

    def place_event(self): # When placed, update the widget
        self.update()

    # Register the widget for this node
    def view_place_event(self):
        self.main_widget().value_changed.connect(self.main_widget_val_changed)

    # Pass changes from the widget to the node itself
    def main_widget_val_changed(self, val):
        self.val = val
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            self.hasRun = True

            # Because dataInputNode, always set the output
            self.set_output_val(0, pbutil.getNewTypedData(pbutil.FILE_LIST, self.val))
            print("Files selected count: " + str(len(self.val) if self.val else 0))


# Allows the user to specify a folder, and pass its path as output
class SelectFolderNode(NodeBase):
    """Selects a folder"""

    title = 'Select Folder'
    init_outputs = [
        rc.NodeOutputBP(label="Selected folder", type_="data")
    ]
    outputTypes = [
        pbutil.FOLDER_PATH
    ]
    main_widget_class = DirectorySelect2  # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.val = None
        self.isDataInputNode = True

    def place_event(self): # When placed, update the widget
        self.update()

    # Register the widget for this node
    def view_place_event(self):
        self.main_widget().directory2_selected.connect(self.directory_selection)

    # Pass changes from the widget to the node itself
    def directory_selection(self, val):
        self.val = val
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            self.hasRun = True

            # Because dataInputNode, always set the output
            self.set_output_val(0, pbutil.getNewTypedData(pbutil.FOLDER_PATH, self.val))
            print("Folder selected: " + str(self.val))


# Write an input to a file
# Original code by Rohan, minor modifications by Robert
class WriteFileNode(NodeBase):
    """Create a log file (that contains a list of files) to a folder"""

    title = 'Create Log File'
    init_inputs = [
        rc.NodeInputBP(label="Logged files"),  # Data
        rc.NodeInputBP(label="Destination folder")
    ]
    inputTypes = [
        pbutil.FILE_LIST,
        pbutil.FOLDER_PATH,
    ]
    main_widget_class = NameInput  # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.isInteresting = True
        self.isLightNode = True

    def place_event(self): # When placed, update the widget
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            self.main_widget().startUpdate()

            if self.checkHasAllInputs():

                self.main_widget().hasAllInputs()

                self.updateInputs()

                self.hasRun = True

                files, folder = self.getInputData()
                name = self.main_widget().getText()
                #Get the type of files
                type = self.inputData[0]["type"]
                print("Writing items...")
                try:
                    self.writeFileList(files, folder, name, type)
                    print("Writing done.")
                    self.main_widget().changeToRun(True, folder)
                except Exception as e:
                    self.errorWindow = ErrorWindow()
                    self.errorWindow.setMessageText("Unable to write the log file.")
                    self.main_widget().changeToError(e)

    def writeFileList(self, files, folder, name, type):
        '''Open a window prompting a user to save a file to their machine'''
        timestamp = time.time()
        if timestamp > math.pow(10, 11):
            timestamp = timestamp / 1000
        timeString = time.strftime("%Y-%m-%dT%H-%M-%S_", time.localtime(timestamp))

        #If the name is unspecified, then fill it in based on file type
        if (name == ""):
            if type == pbutil.FILE_LIST_VTK_VALID:
                name = "valid_files"
            elif type == pbutil.FILE_LIST_VTK_INVALID:
                name = "invalid_files"
            elif type == pbutil.FILE_LIST_GIPL:
                name = "gipl_files"
            elif type == pbutil.FILE_LIST_TFMAT:
                name = "TFMAT_files"  
            else:
                name = "unspecified_files"

        filename = folder + "/" + timeString + name+".txt"

        text = ""
        for file_name in files:
            file_name = file_name.replace("//","/")
            text = text + str(file_name) + "\n"

        print("Written Data: " + text[:50])
        f = open(filename, "w")
        f.write(text)
        f.close()

# Copy files to a new directory
class CopyFilesNode(NodeBase):
    """Copy files to a new folder"""

    title = 'Copy Files'
    init_inputs = [
        rc.NodeInputBP(label="Files"),  # Data
        rc.NodeInputBP(label="Destination folder")
    ]
    inputTypes = [
        pbutil.FILE_LIST,
        pbutil.FOLDER_PATH
    ]

    main_widget_class = singleLightWidget  # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.isLightNode = True
        self.isInteresting = True

    def place_event(self): # When placed, update the widget
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""

        if windowSingleton().canRunWindow(self.windowId):

            if windowSingleton().isStepWindow(self.windowId):

                windowSingleton().makeUnRunableWindow(self.windowId)


            self.main_widget().startUpdate()

            if self.checkHasAllInputs():

                self.main_widget().hasAllInputs()

                if self.checkHasChangedInputs():
                    self.updateInputs()

                    self.hasRun = True

                    files, folder = self.getInputData()
                    print("Copying items...")
                    try:
                        self.copyFiles(files, folder)
                        print("Copying done.")
                        self.main_widget().changeToRun(True, folder)
                    except Exception as e:
                        print(e)
                        self.errorWindow = ErrorWindow()
                        self.errorWindow.setMessageText("Unable to copy files.")
                        self.main_widget().changeToError(e)

    #If the selected folder is blank then prompt for input
    def copyFiles(self, files, folder):

        for file in files:
            shutil.copy(file, folder)

# Connector to make large processes look neater in the process builder
class Connector(NodeBase):
    """Connector to help keep large processes looking clean. Output foler will be set equal to input folder."""
    title = 'Connector'

    init_inputs = [
        rc.NodeInputBP(label="Folder")  # Data
    ]
    inputTypes = [
        pbutil.FOLDER_PATH

    ]

    init_outputs = [

        rc.NodeOutputBP(label="Folder", type_="data")

    ]

    outputTypes = [

        pbutil.FOLDER_PATH

    ]

    def  __init__(self, params):
        super().__init__(params)


    def place_event(self): # When placed, update the widget
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            if self.checkHasAllInputs():

                if self.checkHasChangedInputs():
                    self.updateInputs()

                    #We don't wnat the connectors to be hasRun since they aren't interesting
                    self.hasRun = True

                    folder = self.getInputData()[0]
                    #self.set_output_val(0, pbutil.getNewTypedData(pbutil.FOLDER_PATH, folder))
                    outputs = [pbutil.getNewTypedData(pbutil.FOLDER_PATH, folder)]
                    self.setOutputs(outputs)

                else:
                    print("Node Inputs Unchanged, Passing on saved Outputs")
                    self.setOutputs(self.outputData)

# Create folder structure
class CreateDirectoriesNode(NodeBase):
    """Create a folder structure for alignment"""

    title = 'Create Folder Structure'
    init_inputs = [
        rc.NodeInputBP(label="Root folder")  # Data
    ]
    inputTypes = [
        pbutil.FOLDER_PATH,
    ]
    init_outputs = [
        rc.NodeOutputBP(label="Low res .vtk folder", type_="data"),
        rc.NodeOutputBP(label="High res .vtk folder", type_="data"),
        rc.NodeOutputBP(label="Low res cleaned .vtk folder", type_="data"),
        rc.NodeOutputBP(label="High res cleaned .vtk folder", type_="data"),
        rc.NodeOutputBP(label=".ini files folder", type_="data"),
        rc.NodeOutputBP(label="TFMAT root folder", type_="data"),
        rc.NodeOutputBP(label="Aligned .vtk folder", type_="data"),
        rc.NodeOutputBP(label="Log file folder", type_="data")
    ]
    outputTypes = [
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH
    ]

    main_widget_class = singleLightWidget  # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.isLightNode = True
        self.isInteresting = True

    def place_event(self): # When placed, update the widget
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            self.main_widget().startUpdate()

            if self.checkHasAllInputs():

                self.main_widget().hasAllInputs()

                if self.checkHasChangedInputs():
                    self.updateInputs()

                    self.hasRun = True

                    rootAsList = self.getInputData()
                    root = rootAsList[0]
                    print("Creating directories...")
                    try:
                        self.createDirectories(root)
                        self.main_widget().changeToRun(True, root)
                        print("Creation of directories done.")
                    except Exception as e:
                        self.errorWindow = ErrorWindow()
                        self.errorWindow.setMessageText("Unable to complete creation of folders")
                        self.main_widget().changeToError(e)


                else:
                    print("Node Inputs Unchanged, Passing on saved Outputs")
                    self.setOutputs(self.outputData)

    def createDirectories(self, root):
        allPaths = [
            root + "/low res vtk/",
            root + "/high res vtk/",
            root + "/low res clean vtk/",
            root + "/high res clean vtk/",
            root + "/ini/",
            root + "/TFMAT/",
            root + "/aligned/",
            root + "/log/"
        ]

        for path in allPaths:
            if not os.path.isdir(path):
                os.mkdir(path)

        outputs = []
        for path in allPaths:
            outputs.append(pbutil.getNewTypedData(pbutil.FOLDER_PATH, path))
        self.setOutputs(outputs)


class SPHARMNode(NodeBase):
    '''Calls SlicerSALT to generate low and high res vtk images'''

    title = 'SPHARM Node'
    init_inputs = [
        rc.NodeInputBP(label=".gipl folder"),  # Data
        rc.NodeInputBP(label="Low res .vtk folder"),
        rc.NodeInputBP(label="High res .vtk folder"),
        rc.NodeInputBP(label=".ini files folder")
    ]
    inputTypes = [
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH
    ]
    init_outputs = [
        rc.NodeOutputBP(label="Flagged .gipl Files", type_="data"),
        rc.NodeOutputBP(label="Low res .vtk Files", type_="data"),
        rc.NodeOutputBP(label="High res .vtk Files", type_="data")
    ]
    outputTypes = [
        pbutil.FILE_LIST_GIPL,
        pbutil.FILE_LIST_VTK_VALID,
        pbutil.FILE_LIST_VTK_VALID
    ]

    def  __init__(self, params):
        super().__init__(params)

        self.isInteresting = True

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)

        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            if self.checkHasAllInputs():
                self.updateInputs()

                self.hasRun = True

                print("Running SPHARM...")
                gipl, low, high, ini = self.getInputData()
                SPHARMDriver(self, gipl, low, high, ini)

    def setOutput(self, selected, lowRes, highRes):
        #NodeBase.makeRunable(self.windowId)
        windowSingleton().makeRunableWindow(self.windowId)
        outputs = [
            pbutil.getNewTypedData(pbutil.FILE_LIST_GIPL, selected),
            pbutil.getNewTypedData(pbutil.FILE_LIST_VTK_VALID, lowRes),
            pbutil.getNewTypedData(pbutil.FILE_LIST_VTK_VALID, highRes)
        ]
        self.setOutputs(outputs)

        print("Finished SPHARM")
        #NodeBase.makeUnRunable(self.windowId)
        windowSingleton().makeUnRunableWindow(self.windowId)


class VisualiseVTKImage(NodeBase):
    '''Take a VTK image and visualise it'''

    title = 'Visualise VTK Image'
    init_inputs = [
        rc.NodeInputBP(label=".vtk files"),
    ]
    init_outputs = [
        rc.NodeOutputBP(label="unflagged files", type_="data"),
        rc.NodeOutputBP(label="flagged files", type_="data")
    ]
    inputTypes = [
        pbutil.FILE_LIST_VTK
    ]
    outputTypes = [
        pbutil.FILE_LIST_VTK_VALID,
        pbutil.FILE_LIST_VTK_INVALID
    ]
    main_widget_class = ButtonWidget  # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.button_clicked = False
        self.isInteresting = True
        
    # Register the widget for this node
    def view_place_event(self):
        self.main_widget().button_press.connect(self.is_button_clicked)
        self.update()
    
    # Pass changes from the widget to the node itself
    def is_button_clicked(self, val):
        #Make it runnable
        if not windowSingleton().canRunWindow(self.windowId):
            windowSingleton().makeRunableWindow(self.windowId)
            self.button_clicked = val
            self.update()
            windowSingleton().makeUnRunableWindow(self.windowId)
        else:
            self.button_clicked = val
            self.update()

    # Try running this node
    def update_event(self, inp=-1):


        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""

        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)
                
            # Check if a new input has been received, and try running the visualisation
            if self.checkHasAllInputs():
                if self.checkHasChangedInputs():
                    self.updateInputs()

                    self.hasRun = True

                    self.visNoOutput = False

                    self.tryRunVisualisation(self.getInputData()[0])
                else:
                    print("Node Inputs Unchanged, Passing on saved Outputs")
                    self.setOutputs(self.outputData)
            elif self.button_clicked:
                self.visNoOutput = True
                self.tryRunVisualisation(self.getInputData()[0])
        self.button_clicked = False

    def tryRunVisualisation(self, filePaths):
        '''Try to run the Visualisation Window on the provided fileList'''
        print("Running visualisation...")
        print("Visualise In Count: " + str(len(filePaths)))
        if filePaths != None:
            VisualisationWindow(filePaths, self)

    def setOutput(self, valid, logged):
        '''Return function once done with the Visualisation Window, passes along the valid files and those to log'''
        if self.visNoOutput:

            self.errorWindow = ErrorWindow()
            self.errorWindow.setMessageText("The output was not updated. If you wish to relog files, reset the process and then run process.")

            return

        #NodeBase.makeRunable(self.windowId)
        windowSingleton().makeRunableWindow(self.windowId)
        print("Valid Data Count:" + str(len(valid)))
        print("Log Data Count:" + str(len(logged)))
        outputs = [
            pbutil.getNewTypedData(pbutil.FILE_LIST_VTK_VALID, valid),
            pbutil.getNewTypedData(pbutil.FILE_LIST_VTK_INVALID, logged)
        ]
        self.setOutputs(outputs)
        print("Visualisation done.")
        #NodeBase.makeUnRunable(self.windowId)
        windowSingleton().makeUnRunableWindow(self.windowId)


class CalculateTFMAT(NodeBase):
    '''Calculates the TFMAT files for a set of .vtk images'''
    title = 'Calculate TFMAT'
    init_inputs = [
        rc.NodeInputBP(label=".vtk files"),
        rc.NodeInputBP(label="TFMAT root folder")
    ]
    init_outputs = [
        rc.NodeOutputBP(label="TFMAT root folder", type_="data")
    ]
    inputTypes = [
        pbutil.FILE_LIST_VTK,
        pbutil.FOLDER_PATH
    ]
    outputTypes = [
        pbutil.FOLDER_PATH
    ]
    main_widget_class = singleLightWidget # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.isLightNode = True
        self.isInteresting = True

    def place_event(self): # When placed, update the widget
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)

        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            self.main_widget().startUpdate()

            if self.checkHasAllInputs():

                self.main_widget().hasAllInputs()

                if self.checkHasChangedInputs():
                    self.updateInputs()
                    self.hasRun = True

                    filePaths, TFMATFolder = self.getInputData()
                    print("Calculating TFMAT...")
                    try:
                        self.Calculation_CALL(filePaths, TFMATFolder)
                        print("Calculation done")
                        self.main_widget().changeToRun(True, TFMATFolder)
                    except Exception as e:
                        self.errorWindow = ErrorWindow()
                        self.errorWindow.setMessageText("Unable to calculate and write TFMAT files")
                        self.main_widget().changeToError(e)
                else:
                    print("Node Inputs Unchanged, Passing on saved Outputs")
                    self.setOutputs(self.outputData)

    def Calculation_CALL(self, filePaths, TFMAT_folder):
        '''Try to run the TFMAT calculation on the provided VTK images'''

        TFMAT_folder = MultipleVTKFileOperation().ProcessFilesFromList(filePaths, TFMAT_folder)
        outputs = [pbutil.getNewTypedData(pbutil.FOLDER_PATH, TFMAT_folder)]
        self.setOutputs(outputs)

class AlignedVTKFiles(NodeBase):
    '''Aligns a .vtk image based on their TFMAT file'''
    title = 'Align VTK Files'
    init_inputs = [
        rc.NodeInputBP(label="TFMAT root folder"),
        rc.NodeInputBP(label="Aligned root folder"),
        rc.NodeInputBP(label=".vtk files")
    ]
    init_outputs = [
        rc.NodeOutputBP(label="Aligned .vtk files", type_="data")
    ]
    inputTypes = [
        pbutil.FOLDER_PATH,
        pbutil.FOLDER_PATH,
        pbutil.FILE_LIST_VTK
    ]
    outputTypes = [
        pbutil.FILE_LIST_VTK
    ]

    main_widget_class = singleLightWidget   # The widget this node uses
    main_widget_pos = 'between ports'

    def  __init__(self, params):
        super().__init__(params)

        self.isInteresting = True
        self.isLightNode = True

    # Register the widget for this node
    def view_place_event(self):
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        """if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False"""
        if windowSingleton().canRunWindow(self.windowId):
            if windowSingleton().isStepWindow(self.windowId):
                windowSingleton().makeUnRunableWindow(self.windowId)

            self.main_widget().startUpdate()

            if self.checkHasAllInputs():

                self.main_widget().hasAllInputs()

                if self.checkHasChangedInputs():
                    self.updateInputs()

                    self.hasRun = True

                    TFMATFolder, alignedFolder, filePaths = self.getInputData()
                    try:
                        print("Aligning .vtk files...")
                        self.alignedFiles_CALL(alignedFolder, filePaths, TFMATFolder)
                        print("Alignment done.")
                        self.main_widget().changeToRun(True, alignedFolder)
                    except Exception as e:
                        self.errorWindow = ErrorWindow()
                        self.errorWindow.setMessageText("Unable to align and create aligned .vtk images")
                        self.main_widget().changeToError(e)
                else:
                    print("Node Inputs Unchanged, Passing on saved Outputs")
                    self.setOutputs(self.outputData)

    def alignedFiles_CALL(self, Aligned_folder, filePaths, TFMATFolder):
        
        print("Number of files to align: " + str(len(filePaths)))

        # Open a window for the user to save the Aligned folder to a folder
        alignedFileList = MultipleVTKFileOperation().AlignMultipleFiles(filePaths,TFMATFolder, Aligned_folder)
        
        outputs = [pbutil.getNewTypedData(pbutil.FILE_LIST_VTK, alignedFileList)]
        self.setOutputs(outputs)
        


# **************************************************************
# **                       EXAMPLE NODES                      **
# **************************************************************

# This is an example of a node that just executes its code when it is called, and doesn't wait for user input
class TemplateNodeOne(NodeBase):
    '''Explanation that appears when the node is hovered over in the GUI'''
    title = 'Name of this Node'
    init_inputs = [
        rc.NodeInputBP(label="Name of input variable 1"),
        rc.NodeInputBP(label="Name of input variable 2")
    ]
    init_outputs = [
        rc.NodeOutputBP(label="Name of output variable", type_="data")
    ]
    inputTypes = [
        pbutil.STRING,
        pbutil.FOLDER_PATH
    ]
    outputTypes = [
        pbutil.STRING
    ]

    def  __init__(self, params):
        super().__init__(params)


        # Node attributes. 
        self.isDataInputNode = True # Only include if this node doesn't have an input and introduces data to the system

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            # If the node is in step mode, make sure only this node is run
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False
            
            # Below are a number of examples on how the node can be run. Select the one you feel is most appropriate to your scenario.

            # Check if a new input is being received. If any have changed, run this node on the input
            allSame = True
            for i in range(len(self.init_inputs)): # For each input
                if self.input(i) != self.inputData[i]: # If a new input has been received
                    allSame = False # Mark a new input as being received
                    self.inputData[i] = self.input(i) # Update the array that stores these inputs
                    print("Value In #" + str(i) +": " + str(self.input(i)))
            if not allSame: # If one was changed
                result = MODULE_FUNCTION_CALL(self.inputData) # Call the module you wrote on the data, and get the result
                for i in range(len(self.init_outputs)): # For each output
                    self.set_output_val(i, pbutil.getNewTypedData(self.outputTypes[i], result[i])) # Set the output as a typed data object
                    print("Value Out #" + str(i) +": " + str(result[i]))


            # Check if all inputs are changed from the last time the node was run, and run if they are
            tempInputData = [None, None] # Initialise array to store inputs
            for i in range(len(self.init_inputs)): # For each input
                tempInputData[i] = self.input(i) # Store the input
            if tempInputData[0] != self.inputData[0] and tempInputData[1] != self.inputData[1]: # If all are differnet
                self.inputData = tempInputData # Update the last list of inputs this was run on
                result = MODULE_FUNCTION_CALL(self.inputData) # Call the module you wrote on the data, and get the result
                for i in range(len(self.init_outputs)): # For each output
                    self.set_output_val(i, pbutil.getNewTypedData(self.outputTypes[i], result[i])) # Set the output as a typed data object
                    print("Value Out #" + str(i) +": " + str(result[i]))

def MODULE_FUNCTION_CALL(self, input):
    # Placeholder function to mimic call to actual module's function
    output = copy.deepcopy(input)
    if output[0]["type"] == pbutil.STRING:
        output[0]["data"] += " The function was called"
    elif output[0]["type"] == pbutil.NUMBER:
        output[0]["data"] += 100
    return output


# This is an example of a node that waits for the user to do something in a new window before continuing on
class TemplateNodeTwo(NodeBase):
    '''Explanation that appears when the node is hovered over in the GUI'''
    title = 'Name of this other Node'
    init_inputs = [
        rc.NodeInputBP(label="Input One"),
    ]
    init_outputs = [
        rc.NodeOutputBP(label="Output One", type_="data"),
        rc.NodeOutputBP(label="Output Two", type_="data")
    ]
    inputTypes = [
        pbutil.STRING
    ]
    outputTypes = [
        pbutil.STRING,
        pbutil.STRING
    ]

    def  __init__(self, params):
        super().__init__(params)

        

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        if NodeBase.PROCESS_ABLE_TO_RUN[self.windowId]:
            if NodeBase.PROCESS_STEP_MODE[self.windowId]:
                NodeBase.PROCESS_ABLE_TO_RUN[self.windowId] = False

            if self.input(0) != self.inputData[0]: # Check if new input has been received
                self.inputData[0] = self.input(0) # Store new input to check it
                stringData = self.input(0)['data']
                # Call a window that waits for the user to click close to continue

    # A function that is called when the window closes
    def windowClosed(self, string1, string2):
        NodeBase.makeRunable(self.windowId) # make the process runnable so the data will be passed along
        self.set_output_val(0, pbutil.getNewTypedData(pbutil.STRING, string1)) # Store the data in the typed data object, and set the output
        self.set_output_val(1, pbutil.getNewTypedData(pbutil.STRING, string2))  # Store the data in the typed data object, and set the output
        NodeBase.makeUnRunable(self.windowId) #Once done, make the process un-runnable as execution has finished

# There are also these things called widgets that can be placed on a node.
# There is no real way to give a template for this, as each widget will be custom made to the node it is for
# But in the nodes above, there are a number that have widgets. Here are they key information to understand.
# - The widget must be already defined in the widgets.py file and imported at the top of the document
# - The widet for a node must be told to the node. An example is: 
#       main_widget_class = ButtonWidget
# - We always want a widget to be between the input and output ports, as this makes the most visual sense. This is done by: 
#       main_widget_pos = 'between ports'
# - When a node is placed, it needs to be connected to the widget. This is done in view_place_event, and takes advantage of the Signals and Slots defined in QtPy

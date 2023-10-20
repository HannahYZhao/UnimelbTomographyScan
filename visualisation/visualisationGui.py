# Xueqi Guan 1098403
# Jiayu Li 713551 - GUI and logic of VTK image interaction
# Hannah Zhao 1161094 - Buttons and dark/light mode

import os
import sys

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize
import qdarkstyle
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from mainWindow import MainWindow
from visualisation.myInteractor import MyInteractorStyle
from visualisation.vtkRendererWrapper import VtkRendererWrapper
from visualisation.visualisationSettings import Settings
from visualisation.visConstants import *
from errorWindow import ErrorWindow
import resourceManager as rm

from constants import VIS_MODULE_BTN_STYLE


class VisualisationWindow(MainWindow):
    """ The main window for visualisation. """

    def __init__(self, files, node=None):
        super().__init__()
        self.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.setWindowTitle("Data visualisation")
        self.setGeometry(WINDOW_POS_X, WINDOW_POS_Y, WINDOW_WIDTH, WINDOW_HEIGHT)  # TODO: set appropriate window size

        # full paths of files starting from root directory
        self.filePaths = files
        # The visualisation node from pb
        self.node = node

        # GUI elements
        self.mainHBox = QHBoxLayout()
        # vertical box on the left
        self.leftVBox = QVBoxLayout()
        self.vtkFileList = QListWidget()
        self.vtkFileList.setMaximumWidth(VTK_LIST_WIDTH)
        self.selectAllCheckbox = QCheckBox()
        # vertical box on the right
        self.rightVBox = QVBoxLayout()
        self.grid = QGridLayout()  # Grid layout that are used to contain vtk images
        self.viewsCombo = QComboBox()  # Combo box for selecting views (transverse/coronal/sagittal)
        self.flipXBtn = QPushButton()
        self.flipYBtn = QPushButton()
        self.flipZBtn = QPushButton()
        self.hideAxesBox = QCheckBox()

        # Number of bone models to display on a page
        self.modelsPerPage = 1

        # Current page number
        self.currentPage = 0
        # The file paths of bone models that are being displayed on the current page
        self.currentBonePaths = []

        # Checked file items (file names, not paths). Gets updated when the "visualise" button is pressed
        self.checkedFileItems = []

        # Names of the files to write into 
        self.filesToLog = []

        # Renderer wrappers and VTK widgets being (or had been) displayed
        self.renWrappers = {}  # a dict of fPaths to active renderer wrappers
        self.vtkWidgets = {}  # a dict of fPaths to interactive vtk widgets
        self.allVtkWidgets = []

        # default axis colors in hex
        self.xAxisColor = UserConfig().getXAxisColor()
        self.yAxisColor = UserConfig().getYAxisColor()
        self.zAxisColor = UserConfig().getZAxisColor()

        # Example window
        self.example = Example()

        # Menu bar
        super().createSettingsMenuBarUI()
        super().createHelpMenuBarUI()

        # UI Initialisation
        self.wdg = QWidget()
        self.wdg.setLayout(self.mainHBox)
        self.setCentralWidget(self.wdg)
        self.createLeftVBoxUi()
        self.createRightVBoxUi()
        self.show()

        # Display VTK images once the window opens
        self.visualise()

    ######################################################
    #  GUI element creation (Left vbox)
    ######################################################

    def createLeftVBoxUi(self):
        self.mainHBox.addLayout(self.leftVBox)
        self.createFileSelectionUi()
        self.createVisSettingsUi()

    def createFileSelectionUi(self):
        # Select or unselect all files
        self.vtkFileList.itemChanged.connect(self.selectFile)
        if self.filePaths is not None:
            self.addFilesToFileList(self.filePaths)
        self.selectAllCheckbox.setText("Select All")
        self.selectAllCheckbox.setCheckState(Qt.Checked)
        self.selectAllCheckbox.stateChanged.connect(self.selectAllFiles)
        self.leftVBox.addWidget(self.selectAllCheckbox)
        self.leftVBox.addWidget(self.vtkFileList)
        # Horizontal box for add files, remove selected files buttons
        fileOperationsHBox = QHBoxLayout()
        self.leftVBox.addLayout(fileOperationsHBox)
        # Add files button
        addFileBtn = QPushButton("Add File(s)...")
        addFileBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        addFileBtn.clicked.connect(self.openFolder)
        fileOperationsHBox.addWidget(addFileBtn)
        # Remove selected files button
        removeSelectedBtn = QPushButton("Remove Selected")
        removeSelectedBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        removeSelectedBtn.clicked.connect(self.removeSelectedFiles)
        fileOperationsHBox.addWidget(removeSelectedBtn)

    def createVisSettingsUi(self):
        # Horizontal box for choosing number of models to show on each page
        modelHBox = QHBoxLayout()
        self.leftVBox.addLayout(modelHBox)
        numModelLabel = QLabel("Number of models to show on each page:")
        modelHBox.addWidget(numModelLabel)
        numModelCombo = QComboBox()
        numModelCombo.addItems([str(i) for i in VIEW_OPTIONS])
        numModelCombo.currentIndexChanged.connect(lambda: self.updateModelsPerPage(int(numModelCombo.currentText())))
        modelHBox.addWidget(numModelCombo)
        # Horizontal box for Visualise and Done buttons
        executionHBox = QHBoxLayout()
        self.leftVBox.addLayout(executionHBox)
        # Start visualisation button
        visualiseBtn = QPushButton("Visualise")
        visualiseBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        visualiseBtn.setDefault(True)
        visualiseBtn.clicked.connect(self.visualise)
        # Tool tip that appears when hovering the visualise button
        VISUALISE_TOOL_TIP = "Visualise the selected files"
        visualiseBtn.setToolTip(VISUALISE_TOOL_TIP)
        executionHBox.addWidget(visualiseBtn)
        # Done button
        doneBtn = QPushButton("Done")
        doneBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        doneBtn.clicked.connect(self.closeWindow)
        executionHBox.addWidget(doneBtn)

    ######################################################
    #  GUI element creation (Right vbox)
    ######################################################

    def createRightVBoxUi(self):
        self.mainHBox.addLayout(self.rightVBox)
        self.createInteractionBtnsUi()
        self.createEmptyGridUi()
        self.createFlipPageBtnUi()

    def createInteractionBtnsUi(self):
        # Horizontal box for reset options, flip toggle buttons, hide axes checkbox, and show example button
        interactionBtnsHBox = QHBoxLayout()
        self.rightVBox.addLayout(interactionBtnsHBox)
        # Create UI elements
        self.createResetUi(interactionBtnsHBox)  # Add UI elements for resetting camera
        self.insertSeparator(interactionBtnsHBox)  # Add a separator in between
        self.createFlippingUi(interactionBtnsHBox)  # Toggle boxes for flipping options
        self.insertSeparator(interactionBtnsHBox)  # Add another separator in between
        self.createHideAxesUi(interactionBtnsHBox)  # Checkbox for hiding and showing axes
        self.insertSeparator(interactionBtnsHBox)  # Add another separator in between
        self.createExampleBtnUi(interactionBtnsHBox)  # Question mark button (shows instructions and an example)
        self.createSettingsUi(interactionBtnsHBox)  # Change axis color

    # Insert a vertical bar to a given hbox
    def insertSeparator(self, hbox):
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setLineWidth(SEPARATOR_WIDTH)
        hbox.addWidget(separator)

    def createResetUi(self, hbox):
        # Dropdown menu for views selection
        self.viewsCombo.addItems([str(i) for i in VIEWS_LABELS])
        self.viewsCombo.currentIndexChanged.connect(lambda: self.resetVisualisation())
        hbox.addWidget(self.viewsCombo)
        # Reset button
        resetBtn = QPushButton()
        resetBtn.setIcon(rm.getIcon(rm.RESET_CAM_ICON))
        resetBtn.setIconSize(QSize(BIG_ICON_DIM, BIG_ICON_DIM))
        resetBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        resetBtn.clicked.connect(self.resetVisualisation)
        hbox.addWidget(resetBtn)

    def createFlippingUi(self, hbox):
        # Toggle boxes for flipping options
        self.flipXBtn.setText("Flip about x-axis")
        self.flipXBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        self.flipXBtn.setCheckable(True)
        self.flipXBtn.clicked.connect(self.flipModel)
        hbox.addWidget(self.flipXBtn)
        self.flipYBtn.setText("Flip about y-axis")
        self.flipYBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        self.flipYBtn.setCheckable(True)
        self.flipYBtn.clicked.connect(self.flipModel)
        hbox.addWidget(self.flipYBtn)
        self.flipZBtn.setText("Flip about z-axis")
        self.flipZBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        self.flipZBtn.setCheckable(True)
        self.flipZBtn.clicked.connect(self.flipModel)
        hbox.addWidget(self.flipZBtn)

    def createHideAxesUi(self, hbox):
        # check box for showing the axes or not
        self.hideAxesBox.setChecked(True)
        self.hideAxesBox.stateChanged.connect(lambda: self.hideOrShowAxes(self.hideAxesBox.isChecked()))
        hbox.addWidget(self.hideAxesBox)
        label = QLabel("Show Axes")
        hbox.addWidget(label)

    def createExampleBtnUi(self, hbox):
        # Question mark button (shows instructions adn an example)
        questionBtn = QPushButton()
        questionBtn.setIcon(rm.getIcon(rm.QUESTION_ICON))
        questionBtn.setIconSize(QSize(MIDDLE_ICON_DIM, MIDDLE_ICON_DIM))
        questionBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        questionBtn.clicked.connect(self.question)
        hbox.addWidget(questionBtn)

    def createSettingsUi(self, hbox):
        settingsBtn = QPushButton()
        settingsBtn.setIcon(rm.getIcon(rm.SETTINGS_ICON))
        settingsBtn.setIconSize(QSize(MIDDLE_ICON_DIM, MIDDLE_ICON_DIM))
        settingsBtn.setStyleSheet(VIS_MODULE_BTN_STYLE)
        settingsBtn.clicked.connect(self.changeSettings)
        hbox.addWidget(settingsBtn)

    def createEmptyGridUi(self):
        # Empty four-views layout
        threeDLayout = QVBoxLayout()  # 3D plane (interactive)
        transverseLayout = QVBoxLayout()  # Transverse plane
        coronalLayout = QVBoxLayout()  # Coronal plane
        sagittalLayout = QVBoxLayout()  # Sagittal plane

        # Set up the layouts
        layouts = [threeDLayout, transverseLayout, coronalLayout, sagittalLayout]
        for layout in layouts:
            self.createEmptyImgUi(layout, VIEWS_LABELS[layouts.index(layout)])

        self.grid.addLayout(threeDLayout, 0, 0)  # top left
        self.grid.addLayout(transverseLayout, 0, 1)  # top right
        self.grid.addLayout(coronalLayout, 1, 0)  # bottom left
        self.grid.addLayout(sagittalLayout, 1, 1)  # bottom right

        # Check if grid has already been added to rightVBox
        if self.rightVBox.itemAt(1) != self.grid:
            self.rightVBox.addLayout(self.grid)

    # Create empty image UI in layout
    def createEmptyImgUi(self, layout, view):
        # Header layout
        headerHBox = QHBoxLayout()
        label = QLabel(view)
        headerHBox.addWidget(label)
        layout.addLayout(headerHBox)
        # Image layout
        imageHBox = QHBoxLayout()
        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        img.setPixmap(rm.getPixmap(rm.FOLDER_IMG).scaledToWidth(VTK_BOX_DIM))
        imageHBox.addWidget(img)
        layout.addLayout(imageHBox)

    # Create VTK image UI of the given file in layout
    def createVtkImgUi(self, layout, view, fPath):
        # Set layout object name to filename
        layout.setObjectName(fPath.split("/")[FILENAME_INDEX])
        # Create a hbox for header and add it to the layout
        headerHBox = QHBoxLayout()
        layout.addLayout(headerHBox)
        # VTK widget layout
        vtkWidgetLayout = QHBoxLayout()
        frame = QFrame()
        vtkWidget = QVTKRenderWindowInteractor(frame)
        renWin = vtkWidget.GetRenderWindow()
        interactor = renWin.GetInteractor()
        # Add VTK widget to layout
        vtkWidgetLayout.addWidget(vtkWidget)
        layout.addLayout(vtkWidgetLayout)
        self.allVtkWidgets.append(vtkWidget)
        # Add widget based on view type
        if view == THREED:
            # Create header that contains that file name, log button, and remove button
            self.createHeaderInteractive(headerHBox, fPath)
            # Render interactive view
            renWin.AddRenderer(self.renWrappers.get(fPath).get3DRenderer())
            self.vtkWidgets[fPath] = vtkWidget
            style = MyInteractorStyle(self, self.renWrappers.get(fPath))
            interactor.SetInteractorStyle(style)
            self.renWrappers.get(fPath).setWidget(vtkWidget)
        else:
            # Create header that contains a label stating the angle of view
            self.createHeaderNonInteractive(headerHBox, view)
            # Render non-interactive views
            renWin.AddRenderer(self.renWrappers.get(fPath).getViewRenderer(view))
            interactor.RemoveAllObservers()  # disable observers for the non-interactive views
        # Initialise the interactor
        interactor.Initialize()
        interactor.Start()

    def createHeaderInteractive(self, headerHBox, fPath):
        # Add filename label and buttons in header layout for interactive (3D) layout only
        filename = fPath.split("/")[FILENAME_INDEX]
        filenameLabel = QLabel()
        if len(filename) > FILENAME_LEN:
            filenameLabel.setText(filename[0:FILENAME_LEN] + "...")
        else:
            filenameLabel.setText(filename)
        filenameLabel.setToolTip(filename)
        headerHBox.addWidget(filenameLabel)
        # Log button
        logBtn = QPushButton("Log")
        logBtn.setCheckable(True)
        logBtn.setChecked(filename in self.filesToLog)
        logBtn.clicked.connect(lambda: self.logFile(filename, logBtn.isChecked()))
        headerHBox.addWidget(logBtn)
        # Remove button
        removeBtn = QPushButton()
        removeBtn.setMaximumWidth(SMALL_BTN_WIDTH)
        removeBtn.setIcon(rm.getIcon(rm.REMOVE_IMG))
        removeBtn.setIconSize(QSize(SMALL_ICON_DIM, SMALL_ICON_DIM))
        removeBtn.clicked.connect(lambda: self.removeImage(filename))
        headerHBox.addWidget(removeBtn)

    def createHeaderNonInteractive(self, headerHBox, view):
        # Add view label for non-interactive views (transverse/coronal/sagittal)
        viewLabel = QLabel(view)
        headerHBox.addWidget(viewLabel)

    def createFlipPageBtnUi(self):
        flipPageBtnHbox = QHBoxLayout()
        # Flip left
        leftFlipBtn = QPushButton()
        leftFlipBtn.setIcon(rm.getIcon(rm.LEFT_ARROW))
        leftFlipBtn.setIconSize(QSize(BIG_ICON_DIM, BIG_ICON_DIM))
        leftFlipBtn.clicked.connect(self.leftFlip)
        # Page number label
        self.pageNumberLabel = QLabel("Page " + str(self.currentPage + 1))
        # Flip right
        rightFlipBtn = QPushButton()
        rightFlipBtn.setIcon(rm.getIcon(rm.RIGHT_ARROW))
        rightFlipBtn.setIconSize(QSize(BIG_ICON_DIM, BIG_ICON_DIM))
        rightFlipBtn.clicked.connect(self.rightFlip)
        # Add widgets to hbox
        flipPageBtnHbox.addStretch()
        flipPageBtnHbox.addWidget(leftFlipBtn)
        flipPageBtnHbox.addWidget(self.pageNumberLabel)
        flipPageBtnHbox.addWidget(rightFlipBtn)
        flipPageBtnHbox.addStretch()
        self.rightVBox.addLayout(flipPageBtnHbox)

    ######################################################
    #  events (left vbox)
    ######################################################

    # Check the boxes of all files
    def selectAllFiles(self, state):
        if state:
            for i in range(self.vtkFileList.count()):
                self.vtkFileList.item(i).setCheckState(Qt.Checked)
        else:
            for i in range(self.vtkFileList.count()):
                self.vtkFileList.item(i).setCheckState(Qt.Unchecked)

    # Select or unselect a single file
    def selectFile(self):
        # Count the number of selected files
        selectedFiles = 0
        for i in range(self.vtkFileList.count()):
            if self.vtkFileList.item(i).checkState() == Qt.Checked:
                selectedFiles += 1

        # Check if all files are selected
        if selectedFiles == self.vtkFileList.count():
            self.selectAllCheckbox.blockSignals(True)
            self.selectAllCheckbox.setCheckState(Qt.Checked)
            self.selectAllCheckbox.blockSignals(False)
        else:
            self.selectAllCheckbox.blockSignals(True)
            self.selectAllCheckbox.setCheckState(Qt.Unchecked)
            self.selectAllCheckbox.blockSignals(False)

    # Open a file dialog for file selection
    def openFolder(self):
        # Open vtk files
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        filePathList = QFileDialog.getOpenFileNames(self, "Add Folder(s)...", rm.resourcePath(rm.SPHARM_DATA), "*vtk",
                                                    options=QFileDialog.DontUseNativeDialog)[0]
        # filePathList = fileDialog.getOpenFileNames(self, "Add Folder(s)...", "/", "*vtk")[0]
        self.addFilesToFileList(filePathList)

    # Add a list of files to the file list GUI
    def addFilesToFileList(self, files):
        for filePath in files:
            fileItem = QListWidgetItem()
            # Store file path in file_time
            fileItem.setData(Qt.UserRole, filePath)
            # Extract file name from file path
            fileName = os.path.basename(filePath)
            fileItem.setText(fileName)
            # fileItem is checked by default
            fileItem.setCheckState(Qt.Checked)
            # Add fileItem only when it does not exist in vtkFileList
            if len(self.vtkFileList.findItems(fileName, Qt.MatchExactly)) == 0:
                self.vtkFileList.addItem(fileItem)
            # If file path is not already in file list, add it to self.filePaths
            if filePath not in self.filePaths:
                self.filePaths.append(filePath)

    # Remove selected files from VTK file list and corresponding VTK images
    def removeSelectedFiles(self):
        # Remove selected files from VTK file list
        i = 0
        while i < self.vtkFileList.count():
            file = self.vtkFileList.item(i)
            if file.checkState():
                row = self.vtkFileList.row(file)
                self.vtkFileList.takeItem(row)
                if file in self.checkedFileItems:
                    self.checkedFileItems.remove(file)
                for f in self.filePaths:
                    if self.getFileName(f) == file.text():
                        self.filePaths.remove(f)
            else:
                i += 1

        # Remove corresponding vtk images
        fPaths = [fp.data(Qt.UserRole) for fp in self.checkedFileItems]
        # If all files in the last page are removed, automatically flip to previous page
        if self.currentPage * self.modelsPerPage == len(fPaths):
            self.currentPage -= 1
            self.pageNumberLabel.setText("Page " + str(self.currentPage + 1))
        # Re-render VTK images
        if self.modelsPerPage == 1:
            self.visualiseOne()
        else:
            self.visualiseMultiple()

    # Visualise the vtk files in the grids on the right. If there is no files selected, error window pops up
    def visualise(self):
        self.checkedFileItems = []
        for i in range(self.vtkFileList.count()):
            if self.vtkFileList.item(i).checkState() == Qt.Checked:
                self.checkedFileItems.append(self.vtkFileList.item(i))
        # Check if there is at least one file selected
        if len(self.checkedFileItems) == 0:
            self.errorWindow = ErrorWindow()
            self.errorWindow.setMessageText("Please select at least one file.")
        else:
            # Reset the UI elements
            self.resetResetDropdown()
            self.resetFlippingToggles()
            self.resetHideCheckbox()
            # visualisation
            # Reset page number to zero
            self.currentPage = 0
            self.pageNumberLabel.setText("Page " + str(self.currentPage + 1))
            # Call different visualisation methods depending on number of images to display
            if self.modelsPerPage == 1:
                self.visualiseOne()
            else:
                self.visualiseMultiple()

    # Visualise one VTK image and its three views
    def visualiseOne(self):
        # Update the file path of the bone that's currently being displayed
        fPaths = [fp.data(Qt.UserRole) for fp in self.checkedFileItems]

        # Update the file paths of the bones that are currently being displayed
        start = self.currentPage * self.modelsPerPage
        self.currentBonePaths = fPaths[start:start+self.modelsPerPage]

        # Clear the existing images and VTK widgets
        self.deleteWidgetsInLayout(self.grid)
        self.allVtkWidgets = []

        # Create four views layouts
        threeDLayout = QVBoxLayout()  # 3D plane (interactive)
        transverseLayout = QVBoxLayout()  # Transverse plane
        coronalLayout = QVBoxLayout()  # Coronal plane
        sagittalLayout = QVBoxLayout()  # Sagittal plane
        self.grid.addLayout(threeDLayout, 0, 0)  # top left
        self.grid.addLayout(transverseLayout, 0, 1)  # top right
        self.grid.addLayout(coronalLayout, 1, 0)  # bottom left
        self.grid.addLayout(sagittalLayout, 1, 1)  # bottom right

        # Initialise render wrapper for each VTK file
        self.initialiseRenWrappers(fPaths)

        # If there is nothing to render, render the default empty grid layout
        if len(self.currentBonePaths) == 0:
            self.createEmptyGridUi()
            return

        # Render VTK files
        names = [THREED, TRANSVERSE, CORONAL, SAGITTAL]
        for i in range(self.grid.count()):
            self.createVtkImgUi(self.grid.itemAt(i), names[i], self.currentBonePaths[0])

    # Visualise multiple vtk files
    def visualiseMultiple(self):
        fPaths = [fp.data(Qt.UserRole) for fp in self.checkedFileItems]

        # Update the file paths of the bones that are currently being displayed
        self.currentBonePaths = fPaths[self.currentPage * self.modelsPerPage:self.currentPage * self.modelsPerPage + self.modelsPerPage]

        # Clear the existing images
        self.deleteWidgetsInLayout(self.grid)

        # Clear the existing VTK widget
        self.allVtkWidgets = []

        # Create layout
        if len(self.currentBonePaths) <= 4:
            modelsPerRow = 2
        else:
            modelsPerRow = 4
        for row in range(int(self.modelsPerPage/modelsPerRow)):
            for column in range(modelsPerRow):
                self.grid.addLayout(QVBoxLayout(), row, column)

        # Initialise render wrapper for each VTK file
        self.initialiseRenWrappers(fPaths)

        # If there is nothing to render, render the default empty grid layout
        if len(self.currentBonePaths) == 0:
            self.createEmptyGridUi()
            return

        # Render VTK files
        for i in range(self.grid.count()):
            if i < len(self.currentBonePaths):
                self.createVtkImgUi(self.grid.itemAt(i), THREED, self.currentBonePaths[i])

    # Initialise renderer wrappers for vtk images
    def initialiseRenWrappers(self, fPaths):
        for fPath in fPaths:
            if fPath in self.renWrappers.keys():  # Initialise the renderer wrapper if it is already in the dict
                self.renWrappers[fPath].initialize(self.xAxisColor, self.yAxisColor, self.zAxisColor)
            else:  # Create a renderer wrapper if it is not already in the dict
                wrapper = VtkRendererWrapper(fPath, self.xAxisColor, self.yAxisColor, self.zAxisColor)
                self.renWrappers[fPath] = wrapper

    # Settings for changing axes color
    def changeSettings(self):
        Settings(self, self.xAxisColor, self.yAxisColor, self.zAxisColor)

    # Close the visualisation window
    def closeWindow(self):
        self.close()

    ######################################################
    #  events (right vbox) (except for vtk interactions)
    ######################################################

    # Show the visualise example when the question mark button is clicked
    def question(self):
        self.example.show()

    # Remove VTK image and corresponding file from VTK file list
    def removeImage(self, filename):
        # Remove corresponding file in VTK file list
        for i in range(self.vtkFileList.count()):
            file = self.vtkFileList.item(i)
            if file.text() == filename:
                if file in self.checkedFileItems:
                    self.checkedFileItems.remove(file)
                for f in self.filePaths:
                    if self.getFileName(f) == filename:
                        self.filePaths.remove(f)
                        print(f + "removed from filepaths")
                        print(self.filePaths)
                row = self.vtkFileList.row(file)
                self.vtkFileList.takeItem(row)
                break

        fPaths = [fp.data(Qt.UserRole) for fp in self.checkedFileItems]
        # If all files in the last page are removed, automatically flip to previous page
        if self.currentPage * self.modelsPerPage == len(fPaths):
            self.currentPage -= 1
            self.pageNumberLabel.setText("Page " + str(self.currentPage + 1))
        # Re-render vtk images
        if self.modelsPerPage == 1:
            self.visualiseOne()
        else:
            self.visualiseMultiple()

    # Left flip to the previous page
    def leftFlip(self):
        fPaths = [fp.data(Qt.UserRole) for fp in self.checkedFileItems]

        # Check if current page is first page
        firstFileIndex = fPaths.index(self.currentBonePaths[0])
        if firstFileIndex == 0:
            return

        # Render previous page
        self.currentPage -= 1
        self.pageNumberLabel.setText("Page " + str(self.currentPage + 1))
        if self.modelsPerPage == 1:
            self.visualiseOne()
        else:
            self.visualiseMultiple()

    # Right flip to the next page
    def rightFlip(self):
        fPaths = [fp.data(Qt.UserRole) for fp in self.checkedFileItems]

        # Check if current page is last page
        lastFileIndex = fPaths.index(self.currentBonePaths[-1])
        if lastFileIndex == len(fPaths) - 1:
            return

        # Render next page
        self.currentPage += 1
        self.pageNumberLabel.setText("Page " + str(self.currentPage + 1))
        if self.modelsPerPage == 1:
            self.visualiseOne()
        else:
            self.visualiseMultiple()

    ######################################################
    #  VTK interactions
    ######################################################

    # Reset all vtk images to default angle
    def resetVisualisation(self):
        currentWrappers, currentVtkWidgets = self.getCurrentDisplay()
        if len(currentWrappers) > 0 and len(currentVtkWidgets) > 0:
            for cw in currentWrappers:
                cw.resetMyCamera(self.viewsCombo.currentText())
                self.updateAllVtkWidgets()
        else:
            print("Could not reset camera because renderer or VTK widget is not found")

    # flip the vtk image around X- and/or Y- and/or Z-axis
    def flipModel(self):
        currentWrappers, currentVtkWidgets = self.getCurrentDisplay()
        if len(currentWrappers) > 0 and len(currentVtkWidgets) > 0:
            for cw in currentWrappers:
                cw.flipModel(self.flipXBtn.isChecked(), self.flipYBtn.isChecked(), self.flipZBtn.isChecked())
                self.updateAllVtkWidgets()
        else:
            print("Could not flip the model because renderer or VTK widget is not found")

    # Given a boolean input, hide axes if the input is true, and show axes if the input is false
    def hideOrShowAxes(self, hide):
        currentWrappers, currentVtkWidgets = self.getCurrentDisplay()
        if len(currentWrappers) > 0 and len(currentVtkWidgets) > 0:
            for cw in currentWrappers:
                cw.hideOrShowAxes(hide)
                self.updateAllVtkWidgets()
        else:
            print("Could not hide/show axes because renderer or VTK widget is not found")

    # Set the color of the axes based to the colours specified by the input
    def setColors(self, xColor, yColor, zColor):
        self.xAxisColor = xColor
        self.yAxisColor = yColor
        self.zAxisColor = zColor
        currentWrappers = self.renWrappers.values()
        if len(currentWrappers) > 0:
            for cw in currentWrappers:
                cw.setAxesColors(x=xColor, y=yColor, z=zColor)
                self.updateAllVtkWidgets()
        else:
            print("Could not change the color of axes because renderer or VTK widget is not found")

    # Set the opacity of the bone. The higher the opacity, the more transparent the bone will be.
    def setBoneOpacity(self, opacity):
        currentWrappers = self.renWrappers.values()
        if len(currentWrappers) > 0:
            for cw in currentWrappers:
                cw.setBoneOpacity(opacity)
                self.updateAllVtkWidgets()
        else:
            print("Could not change the color of axes because renderer or VTK widget is not found")

    # Set the background colours of vtk images
    def setBackgroundColors(self, color):
        currentWrappers = self.renWrappers.values()
        if len(currentWrappers) > 0:
            for cw in currentWrappers:
                cw.setBackgroundColor(color)
                self.updateAllVtkWidgets()

    # Rotate all vtk images.
    def rotateAll(self, xRot, yRot):
        for fp in self.currentBonePaths:
            self.renWrappers[fp].rotateCamera(xRot, yRot)
        self.updateAllVtkWidgets()

    # Zoom in/out all VTK images. Zoom in if direction is 1 and zoom out if direction is -1.
    def zoomAll(self, direction):
        for fp in self.currentBonePaths:
            self.renWrappers[fp].myZoom(direction)
        self.updateAllVtkWidgets()

    # Pan all VTK images.
    def panAll(self, prev, curr):
        for fp in self.currentBonePaths:
            self.renWrappers[fp].calculatePickPoints(prev, curr)
        self.updateAllVtkWidgets()

    ######################################################
    #  override methods
    ######################################################

    # def setLightMode(self):
    #     self.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette))
    #     UserConfig().setColorTheme(LIGHT_MODE)
    #     self.setBackgroundColors(BG_COLOR_LIGHT)
    #     self.updateLogIcon()
    #
    # def setDarkMode(self):
    #     self.setStyleSheet(qdarkstyle.load_stylesheet(palette=DarkPalette))
    #     UserConfig().setColorTheme(DARK_MODE)
    #     self.setBackgroundColors(BG_COLOR_DARK)
    #     self.updateLogIcon()

    # def updateLogIcon(self):
    #     for fn in self.filesToLog:
    #         file = self.vtkFileList.findItems(fn, Qt.MatchExactly)[0]
    #         file.setIcon(rm.getIcon(rm.LOG_FILE_ICON, hasMode=True))

    # Override method. Before the window closes, all vtk widgets need to be finalised.
    def closeEvent(self, event):
        self.exportToLog()
        for vw in self.allVtkWidgets:
            vw.Finalize()
        event.accept()

    ######################################################
    #  methods for internal use
    ######################################################

    # Get the vtk wrappers and vtk widgets that are currently being displayed
    def getCurrentDisplay(self):
        wrappers = []
        vtkWidgets = []
        for path in self.currentBonePaths:
            if path is not None \
                    and path in self.renWrappers.keys() \
                    and self.renWrappers[path] is not None \
                    and path in self.vtkWidgets.keys() \
                    and self.vtkWidgets[path] is not None:
                wrappers.append(self.renWrappers[path])
                vtkWidgets.append(self.vtkWidgets[path])
        return wrappers, vtkWidgets

    # Reset the views combo box to default option
    def resetResetDropdown(self):
        self.viewsCombo.setCurrentIndex(0)

    # Reset the toggle buttons for flipping around axes
    def resetFlippingToggles(self):
        self.flipXBtn.setChecked(False)
        self.flipYBtn.setChecked(False)
        self.flipZBtn.setChecked(False)

    # Reset the checkbox for hiding/showing axes
    def resetHideCheckbox(self):
        self.hideAxesBox.setChecked(True)

    # Update all VTK widgets.
    def updateAllVtkWidgets(self):
        for vw in self.allVtkWidgets:
            vw.update()

    # Delete all widgets in given layout.
    def deleteWidgetsInLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                # Widget will be None if it is a layout
                if widget is not None:
                    if type(widget) == QVTKRenderWindowInteractor:  # Finalize if widget is a VTK widget
                        widget.Finalize()
                    widget.setParent(None)
                else:
                    self.deleteWidgetsInLayout(item.layout())

    # Get the logged file icon shown on the side of the left hand box
    def logFile(self, filename, logFile):
        file = self.vtkFileList.findItems(filename, Qt.MatchExactly)[0]
        if logFile:
            file.setIcon(rm.getIcon(rm.LOG_FILE_ICON, hasMode=True))
            self.filesToLog.append(file.text())
        else:
            file.setIcon(QIcon())
            self.filesToLog.remove(file.text())

    # Get the logging information saved to a write file node
    def exportToLog(self):
        loggedFiles = [f for f in self.filePaths if f.split("/")[-1] in self.filesToLog]
        validFiles = [f for f in self.filePaths if f not in loggedFiles]
        if self.node is not None:
            self.node.setOutput(validFiles, loggedFiles)

    # Given the full path of a file, get the file name by taking the substring after the last "/" character
    def getFileName(self, fullPath):
        return fullPath.split("/")[-1]

    # Update the visualisation window if the number of model per page updated
    def updateModelsPerPage(self, modelsPerPage):
        self.modelsPerPage = modelsPerPage


# The window which shows an example of correct bone alignment
class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.setWindowTitle("Information")
        x = WINDOW_POS_X + int(WINDOW_WIDTH / 2) - int(EXAMPLE_WIDTH / 2)
        y = WINDOW_POS_Y + int(WINDOW_HEIGHT / 2) - int(EXAMPLE_HEIGHT / 4)
        self.setGeometry(x, y, EXAMPLE_WIDTH, EXAMPLE_HEIGHT)
        self.ui()

    # Page layout
    def ui(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        instructionVBox = QVBoxLayout()
        iLabel = QLabel("<p style='line-height:150%'>"
                        "Visualisation controls:<br/>"
                        "  - Rotation: Hold down left click and drag the mouse<br/>"
                        "  - Panning: Hold down right click and drag the mouse<br/>"
                        "  - Zoom in/out: scroll wheel"
                        "</p>")
        instructionVBox.addWidget(iLabel)
        vbox.addLayout(instructionVBox)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setLineWidth(SEPARATOR_WIDTH)
        vbox.addWidget(separator)
        exampleVBox = QVBoxLayout()
        # text
        text_label = QLabel("Example of correct bone alignment:")
        exampleVBox.addStretch()
        exampleVBox.addWidget(text_label)
        # example image
        image = QLabel()
        image.setPixmap(rm.getPixmap(rm.EXAMPLE_BONE_IMG).scaled(EXAMPLE_IMG_DIM, EXAMPLE_IMG_DIM))
        exampleVBox.addWidget(image)
        exampleVBox.addStretch()
        vbox.addLayout(exampleVBox)

    def show(self):
        self.setStyleSheet(UserConfig().getColorTheme())
        super().show()


def runVisualisation(filePaths):
    app = QApplication()
    VisualisationWindow(filePaths)
    sys.exit(app.exec_())

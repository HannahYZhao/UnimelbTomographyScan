#THIS CODE TAKEN ENTIRELY FROM OLD VERSION BY VISUALISATION TEAM
#TODO: FIX ATTRIBUTION
#ATTRIBUTION likely Jiayu, Xueqi Guan, Hannah and Jihao
#Code was not worked on by Robert Sharp.

import vtk
import inspect

colors = vtk.vtkNamedColors()
# References for the names of colors:
# https://gitlab.kitware.com/vtk/vtk/-/blob/master/Common/Color/vtkNamedColors.cxx
# https://en.wikipedia.org/wiki/Web_colors#CSS_Color_5

# Model info
BONE_OPACITY = 0.2
TRANSVERSE = "Transverse/Axial (top)"
CORONAL = "Coronal (front)"
SAGITTAL = "Sagittal (left)"

# default camera info
ZOOM_FACTOR = 5  # default zoom factor
MIN_ZOOM_SCALE = 0.5  # 50% of original size
MAX_ZOOM_SCALE = 3   # 300% of original size
# factor for calculating the distance between model bounds and camera reset bound
CAM_OFFSET_RATIO = 2.5  # the bigger the number, the closer the bone (i.e. looks bigger)

# Axes info
AXIS_SCALE_RATIO = 1  # factor for calculating the size of axes
AXIS_TIP_RADIUS = 0.3
AXIS_RADIUS = 0.02
X_CAPTION_TEXT = "X"
Y_CAPTION_TEXT = "Y"
Z_CAPTION_TEXT = "Z"
AXIS_CAPTION_SCALE = 1

# colors
MODEL_COLOR = "WhiteSmoke"
BG_COLOR = "whitesmoke"
BG_COLOR_BOTTOM = "honeydew"
BG_GRADIENT_ON = True
NON_INTERACTIVE_BG_COLOR = "whitesmoke"
X_AXIS_COLOR = "Red"
Y_AXIS_COLOR = "Green"
Z_AXIS_COLOR = "Blue"
X_CAPTION_COLOR = "White"
Y_CAPTION_COLOR = "White"
Z_CAPTION_COLOR = "White"


class VtkRendererWrapper:

    # Initialise a VTK renderer
    def __init__(self, filePath):
        #print(filePath)
        self.filePath = filePath
        # VTK renderer
        self.ren = vtk.vtkRenderer()
        self.createRenderer()
        # Render window
        self.renWin = vtk.vtkRenderWindow()
        self.createRenderWindow()
        self.renWin.AddRenderer(self.ren)
        # Render window interactor
        self.iren = vtk.vtkRenderWindowInteractor()
        self.createRWInteractor()
        self.iren.SetRenderWindow(self.renWin)
        # Read data from VTK files and create knee joint actor
        self.jointActor = vtk.vtkActor()
        self.createJointActor()
        self.ren.AddActor(self.jointActor)
        # calculate the distance between model bounds and camera reset bound
        self.camOffset = self.calculateCamOffset()
        # Add axis actors
        self.axisScale = self.calculateAxisScale()
        self.axesActor = vtk.vtkAxesActor()
        self.createAxesActor()
        self.ren.AddActor(self.axesActor)
        # Reset camera with the focal point at the origin of the axes and store the info
        self.ren.ResetCamera(self.getCameraResetBounds())
        camera = self.ren.GetActiveCamera()
        camera.Zoom(ZOOM_FACTOR)
        self.initZoomFactor = ZOOM_FACTOR
        self.initCamPos = camera.GetPosition()
        self.initViewUp = camera.GetViewUp()

    # Reset the camera to the initial position
    def resetMyCamera(self):
        self.ren.ResetCamera(self.getCameraResetBounds())
        camera = self.ren.GetActiveCamera()
        camera.SetPosition(self.initCamPos)
        camera.SetViewUp(self.initViewUp)
        camera.Zoom(self.initZoomFactor)
        return self.ren

    # Return the interactive renderer
    def get3DRenderer(self):
        # #print("** " + inspect.stack()[1][3] + " method is calling Get3DRenderer")
        if hasattr(self, 'ren'):
            self.resetMyCamera()
            camera = self.ren.GetActiveCamera()
            camera.Roll(120)
            camera.Elevation(60)
            return self.ren
        else:
            #print("No renderer found in this wrapper")
            return None

    # Return the transvers/coronal/sagittal view
    def getViewRenderer(self, view):
        self.resetMyCamera()
        #print("Getting {} renderer of {}".format(view, self.filePath.split("/")[-1]))
        self.setBackgroundColors(colors.GetColor3d(BG_COLOR))
        if view == TRANSVERSE:
            return self.ren
        camera = self.ren.GetActiveCamera()
        camera.Elevation(90)
        if view == SAGITTAL:
            return self.ren
        elif view == CORONAL:
            camera.OrthogonalizeViewUp()
            camera.Azimuth(90)
            return self.ren
        return None

    def getScaledZoomFactor(self, zoomFactor):
        return self.initZoomFactor * zoomFactor

    def getCameraResetBounds(self):
        bounds = self.jointActor.GetBounds()
        return [bounds[0] - self.camOffset,
                bounds[1] + self.camOffset,
                bounds[2] - self.camOffset,
                bounds[3] + self.camOffset,
                bounds[4] - self.camOffset,
                bounds[5] + self.camOffset]

    # Set the colors of the axes
    def setAxesColors(self, x=None, y=None, z=None):
        if x is None:
            x = colors.GetColor3d(X_AXIS_COLOR)
        if y is None:
            y = colors.GetColor3d(Y_AXIS_COLOR)
        if z is None:
            z = colors.GetColor3d(Z_AXIS_COLOR)
        # TODO: to be implemented in later s#prints
        return False

    # Set the background colors
    def setBackgroundColors(self, color, colorBottom=None):
        if colorBottom is None:
            self.ren.SetBackground(color)
            self.ren.GradientBackgroundOff()
            return True
        self.ren.SetBackground(colorBottom)
        self.ren.SetBackground2(color)
        self.ren.GradientBackgroundOn()
        return True

    # #print camera info in console for testing purpose
    def printCameraInfo(self):
        camera = self.ren.GetActiveCamera()
        #print('-------')
        #print("position", camera.GetPosition())
        #print("Focal Point:", camera.GetFocalPoint())
        #print("Distance:", camera.GetDistance())
        #print("Roll:", camera.GetRoll())
        #print('-------')

    #######################################################
    # Private methods for internal use of this class
    #######################################################
    def createRenderer(self):
        if BG_GRADIENT_ON:
            self.setBackgroundColors(color=colors.GetColor3d(BG_COLOR),
                                     colorBottom=colors.GetColor3d(BG_COLOR_BOTTOM))
        else:
            self.setBackgroundColors(color=colors.GetColor3d(BG_COLOR))

    def createRenderWindow(self):
        self.renWin.SetSize(300, 300)

    def createRWInteractor(self):
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        # self.iren.SetInteractorStyle(MyInteractor())
        # TODO

    def createJointActor(self):
        # Create source (reader)
        vtkReader = vtk.vtkPolyDataReader()
        vtkReader.SetFileName(self.filePath)
        vtkReader.Update()
        # Create and set mappers of knee joint actor
        jointMapper = vtk.vtkPolyDataMapper()
        jointMapper.SetInputConnection(vtkReader.GetOutputPort())
        # set up joint actor
        self.jointActor.GetProperty().SetColor(colors.GetColor3d(MODEL_COLOR))
        self.jointActor.GetProperty().SetOpacity(BONE_OPACITY)
        self.jointActor.SetMapper(jointMapper)
        # Move the joint actor to the origin
        centre = self.calculateCentre(self.jointActor)
        transform = vtk.vtkTransform()
        transform.Translate([-n for n in centre])
        self.jointActor.SetUserTransform(transform)

    def calculateCamOffset(self):
        bounds = self.jointActor.GetBounds()
        xmin, xmax, ymin, ymax, zmin, zmax = bounds[:]
        return max(xmax-xmin, ymax-ymin, zmax-zmin) * CAM_OFFSET_RATIO

    def calculateAxisScale(self):
        bounds = self.jointActor.GetBounds()
        xmin, xmax, ymin, ymax, zmin, zmax = bounds[:]
        return max(xmax-xmin, ymax-ymin, zmax-zmin) * AXIS_SCALE_RATIO

    def calculateCentre(self, actor):
        bounds = actor.GetBounds()
        xmin, xmax, ymin, ymax, zmin, zmax = bounds[:]
        return [(xmin + xmax) / 2.0,
                (ymin + ymax) / 2.0,
                (zmin + zmax) / 2.0]

    def createAxesActor(self):
        self.axesActor.AxisLabelsOn()
        # Scale up the axes
        transform = vtk.vtkTransform()
        transform.Scale([self.axisScale] * 3)
        self.axesActor.SetUserTransform(transform)
        # Set the font of axis labels
        for label in [self.axesActor.GetXAxisCaptionActor2D(),
                      self.axesActor.GetYAxisCaptionActor2D(),
                      self.axesActor.GetZAxisCaptionActor2D()]:
            tprop = label.GetCaptionTextProperty()
            # Set colors
            if label.GetCaption == X_CAPTION_TEXT:
                tprop.SetColor(colors.GetColor3d(X_CAPTION_COLOR))
            elif label.GetCaption == Y_CAPTION_TEXT:
                tprop.SetColor(colors.GetColor3d(Y_CAPTION_COLOR))
            elif label.GetCaption == Z_CAPTION_TEXT:
                tprop.SetColor(colors.GetColor3d(Z_CAPTION_COLOR))
            label.SetCaptionTextProperty(tprop)
            # Rescale
            label.SetWidth(label.GetWidth() * AXIS_CAPTION_SCALE)
            label.SetHeight(label.GetHeight() * AXIS_CAPTION_SCALE)
        # Set attributes of axes
        self.axesActor.SetConeRadius(AXIS_TIP_RADIUS)
        self.axesActor.SetShaftTypeToCylinder()
        self.axesActor.SetCylinderRadius(AXIS_RADIUS)

    # #print axis info in console for testing purpose
    def printAxesInfo(self):
        pass
        #print("-----------")
        #print("Tip length: " + str(self.axesActor.GetNormalizedTipLength()))  # 0.2, 0.2, 0.2
        #print("Cone radius: " + str(self.axesActor.GetConeRadius()))  # 0.4
        #print("Cylinder radius: " + str(self.axesActor.GetCylinderRadius()))  # 0.05
        #print("-----------")

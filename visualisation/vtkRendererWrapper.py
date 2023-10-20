# Jiayu Li 713551

import vtk

from visualisation.visConstants import *


class VtkRendererWrapper:

    # Initialise a VTK renderer wrapper
    def __init__(self, filePath, xAxisColor, yAxisColor, zAxisColor):
        self.filePath = filePath
        # Renderer and actors for the interactive view
        self.ren = None  # Renderer
        self.w = None
        self.jointActor = None
        self.axesActor = None
        # Renderers for transverse/Coronal/Sagittal views
        self.transverse = None
        self.coronal = None
        self.sagittal = None
        self.viewJointActors = []  # Joint actors in transverse/Coronal/Sagittal renderers
        self.viewAxesActors = []  # Axes axtors transverse/Coronal/Sagittal renderers
        # Attributes
        self.jointVtkOrigin = [0, 0, 0]
        self.camOffset = None
        self.axisScale = None
        self.initZoomFactor = ZOOM_FACTOR
        self.initCamPos = None
        self.initViewUp = None
        # Axes colors
        self.xAxisColor = xAxisColor  # in hex
        self.yAxisColor = yAxisColor  # in hex
        self.zAxisColor = zAxisColor  # in hex
        # Initialise
        self.initialize(xAxisColor, yAxisColor, zAxisColor)

    def initialize(self, xAxisColor, yAxisColor, zAxisColor):
        # Read data from VTK files and create knee joint actor
        self.jointActor = self.createJointActor()
        self.jointVtkOrigin = self.calculateCentre(self.jointActor)
        self.moveActorToWorldOrigin(self.jointActor)
        # calculate the distance between model bounds and camera reset bound
        self.camOffset = self.getMaxBound() * CAM_OFFSET_RATIO
        # Add axis actors
        self.axisScale = self.getMaxBound() * AXIS_SCALE_RATIO
        self.axesActor = self.createAxesActor(xAxisColor, yAxisColor, zAxisColor)
        # VTK renderer
        self.ren = self.createRenderer()
        self.ren.AddActor(self.jointActor)
        self.ren.AddActor(self.axesActor)
        # Reset camera with the focal point at the origin of the axes and store the info
        self.ren.ResetCamera(self.getCameraResetBounds())
        camera = self.ren.GetActiveCamera()
        camera.Zoom(ZOOM_FACTOR)
        self.initZoomFactor = ZOOM_FACTOR
        self.initCamPos = camera.GetPosition()
        self.initViewUp = camera.GetViewUp()

    #######################################################
    # Getters and setters
    #######################################################

    # Returns the interactive renderer.
    def getRenderer(self):
        return self.ren

    # Resets and returns the interactive renderer.
    def get3DRenderer(self):
        # print("** " + inspect.stack()[1][3] + " method is calling Get3DRenderer")
        if hasattr(self, 'ren'):
            self.resetMyCamera()
            return self.ren
        else:
            print("No renderer found in this wrapper")
            return None

    # Returns the transvers/coronal/sagittal view.
    def getViewRenderer(self, view):
        # print("Getting {} renderer of {}".format(view, self.filePath.split("/")[-1]))
        if view == TRANSVERSE and self.transverse is not None:
            return self.transverse
        elif view == CORONAL and self.coronal is not None:
            return self.coronal
        elif view == SAGITTAL and self.sagittal is not None:
            return self.sagittal
        else:
            return self.createViewRenderer(view)

    # Get the focal point of the camera (normally the center of the bone)
    def getCameraFocalPoint(self):
        camera = self.ren.GetActiveCamera()
        return camera.GetFocalPoint()

    # Get the position of the camera
    def getCameraPosition(self):
        camera = self.ren.GetActiveCamera()
        return camera.GetPosition()

    # Sets the colors of the axes.
    def setAxesColors(self, x=None, y=None, z=None):
        if x is None:
            x = self.axesActor.GetXAxisShaftProperty().GetColor()
        if y is None:
            y = self.axesActor.GetYAxisShaftProperty().GetColor()
        if z is None:
            z = self.axesActor.GetZAxisShaftProperty().GetColor()
        self.xAxisColor = x
        self.yAxisColor = y
        self.zAxisColor = z
        for aa in [self.axesActor] + self.viewAxesActors:
            self.colorAxes(aa, x, y, z)
        return False

    # Set the opacity of the bone
    def setBoneOpacity(self, opacity):
        for ja in [self.jointActor] + self.viewJointActors:
            ja.GetProperty().SetOpacity(opacity)

    # set the background colour a vtk renderer
    def setBackgroundColor(self, color):
        self.ren.SetBackground(self.hexToRgb(color))
        if self.transverse is not None:
            self.transverse.SetBackground(self.hexToRgb(color))
        if self.coronal is not None:
            self.coronal.SetBackground(self.hexToRgb(color))
        if self.sagittal is not None:
            self.sagittal.SetBackground(self.hexToRgb(color))

    # Set the widget this is in
    def setWidget(self, w):
        self.w = w

    #######################################################
    # VTK image Interactions
    #######################################################

    # Resets the camera to the initial position
    def resetMyCamera(self, view=THREED):
        self.ren.ResetCamera(self.getCameraResetBounds())
        camera = self.ren.GetActiveCamera()
        camera.SetPosition(self.initCamPos)
        camera.SetViewUp(self.initViewUp)
        if view == THREED:
            camera.Roll(120)
            camera.Elevation(60)
        elif view == CORONAL:
            camera.Elevation(90)
            camera.OrthogonalizeViewUp()
            camera.Azimuth(90)
        elif view == SAGITTAL:
            camera.Elevation(90)
            camera.OrthogonalizeViewUp()
        camera.Zoom(self.initZoomFactor)
        self.ren.ResetCameraClippingRange()
        return self.ren

    # Rotate the camera based on given angles
    def rotateCamera(self, xAngle, yAngle):
        xAngle = self.validateRotateAngle(xAngle)
        yAngle = self.validateRotateAngle(yAngle)
        # Get camera parameters
        camera = self.ren.GetActiveCamera()
        fp = camera.GetFocalPoint()
        viewUp = camera.GetViewUp()
        position = camera.GetPosition()
        axis = [0, 0, 0]
        axis[0] = -camera.GetViewTransformMatrix().GetElement(0, 0)
        axis[1] = -camera.GetViewTransformMatrix().GetElement(0, 1)
        axis[2] = -camera.GetViewTransformMatrix().GetElement(0, 2)
        # Create the transformation
        transform = vtk.vtkTransform()
        # Rotate
        transform.RotateWXYZ(xAngle, viewUp)  # azimuth
        transform.RotateWXYZ(yAngle, axis)  # elevation
        # Update camera position and focal point
        newPos = [0, 0, 0]
        transform.TransformPoint(position, newPos)
        newFp = [0, 0, 0]
        transform.TransformPoint(fp, newFp)
        camera.SetPosition(newPos)
        camera.SetFocalPoint(newFp)
        # Reset camera
        camera.OrthogonalizeViewUp()
        self.ren.ResetCameraClippingRange()

    # Zoom in or out
    def myZoom(self, direction):
        camera = self.ren.GetActiveCamera()
        factor = 1 + ZOOM_STEP * direction
        camera.Zoom(factor)

    # With the previous and current mouse position, calculate the pick points
    def calculatePickPoints(self, prev, curr):
        viewFocus = self.getCameraFocalPoint()
        if self.w is None:
            print("widget not found")
            exit(0)
        interactor = self.w.GetRenderWindow().GetInteractor().GetInteractorStyle()
        # Calculate the display coordinate of the focal point
        viewFocusN = [0, 0, 0]
        interactor.ComputeWorldToDisplay(self.ren, viewFocus[0], viewFocus[1], viewFocus[2], viewFocusN)
        # Calculate the world coordinate of the old and new pick points
        focalDepth = viewFocusN[2]
        oldPickPoint = [0, 0, 0, 0]  # in world coordinate
        interactor.ComputeDisplayToWorld(self.ren, prev[0], prev[1], focalDepth, oldPickPoint)
        newPickPoint = [0, 0, 0, 0]  # in world coordinate
        interactor.ComputeDisplayToWorld(self.ren, curr[0], curr[1], focalDepth, newPickPoint)
        # Calculate the transformation of the camera
        self.calculateCameraMovement(oldPickPoint, newPickPoint)

    # With the pick points, calculate the transformation of the camera
    def calculateCameraMovement(self, oldPickPoint, newPickPoint):
        # Calculate the motion vector
        motionVector = (oldPickPoint[0] - newPickPoint[0],
                        oldPickPoint[1] - newPickPoint[1],
                        oldPickPoint[2] - newPickPoint[2])
        # Calculate the new focal point
        viewFocus = self.getCameraFocalPoint()
        newFocalPoint = (motionVector[0] + viewFocus[0],
                         motionVector[1] + viewFocus[1],
                         motionVector[2] + viewFocus[2])
        # Calculate the new position of camera
        viewPoint = self.getCameraPosition()
        newPosition = (motionVector[0] + viewPoint[0],
                       motionVector[1] + viewPoint[1],
                       motionVector[2] + viewPoint[2])
        # Apply transformation
        self.panTheModel(newFocalPoint, newPosition)

    # Pan the model (i.e., move the camera)
    def panTheModel(self, newFocalPoint, newPosition):
        camera = self.ren.GetActiveCamera()
        camera.SetFocalPoint(newFocalPoint)
        camera.SetPosition(newPosition)

    # Given three boolean values, flip the model around axes
    def flipModel(self, flipX, flipY, flipZ):
        transform = vtk.vtkTransform()
        if flipX:
            transform.RotateWXYZ(FLIP_ANGLE, X_AXIS)
        if flipY:
            transform.RotateWXYZ(FLIP_ANGLE, Y_AXIS)
        if flipZ:
            transform.RotateWXYZ(FLIP_ANGLE, Z_AXIS)
        transform.Translate([-n for n in self.jointVtkOrigin])
        self.jointActor.SetUserTransform(transform)
        for ja in self.viewJointActors:
            ja.SetUserTransform(transform)

    # Given a boolean value, hide or show axes
    def hideOrShowAxes(self, vis):
        self.axesActor.SetVisibility(vis)
        for aa in self.viewAxesActors:
            aa.SetVisibility(vis)

    #######################################################
    # VTK image creation
    #######################################################
    def createJointActor(self):
        jointActor = vtk.vtkActor()
        # Create source (reader)
        vtkReader = vtk.vtkPolyDataReader()
        vtkReader.SetFileName(self.filePath)
        vtkReader.Update()
        # Create and set mappers of knee joint actor
        jointMapper = vtk.vtkPolyDataMapper()
        jointMapper.SetInputConnection(vtkReader.GetOutputPort())
        # set up joint actor
        jointActor.GetProperty().SetColor(self.hexToRgb(MODEL_COLOR))
        jointActor.GetProperty().SetOpacity(UserConfig().getBoneOpacity())
        jointActor.SetMapper(jointMapper)
        return jointActor

    # Move actor to the origin.
    def moveActorToWorldOrigin(self, actor):
        centre = self.calculateCentre(actor)
        transform = vtk.vtkTransform()
        transform.Translate([-n for n in centre])
        actor.SetUserTransform(transform)

    def createAxesActor(self, xAxisColor, yAxisColor, zAxisColor):
        axesActor = vtk.vtkAxesActor()
        axesActor.AxisLabelsOn()
        # Scale up the axes
        transform = vtk.vtkTransform()
        transform.Scale([self.axisScale] * 3)
        axesActor.SetUserTransform(transform)
        # Set the font of axis labels
        for label in [axesActor.GetXAxisCaptionActor2D(),
                      axesActor.GetYAxisCaptionActor2D(),
                      axesActor.GetZAxisCaptionActor2D()]:
            tprop = label.GetCaptionTextProperty()
            # Set colors
            if label.GetCaption == X:
                tprop.SetColor(self.hexToRgb(X_CAPTION_COLOR))
            elif label.GetCaption == Y:
                tprop.SetColor(self.hexToRgb(Y_CAPTION_COLOR))
            elif label.GetCaption == Z:
                tprop.SetColor(self.hexToRgb(Z_CAPTION_COLOR))
            label.SetCaptionTextProperty(tprop)
            # Rescale
            label.SetWidth(label.GetWidth() * AXIS_CAPTION_SCALE)
            label.SetHeight(label.GetHeight() * AXIS_CAPTION_SCALE)
        # Set attributes of axes
        axesActor.SetConeRadius(AXIS_TIP_RADIUS)
        axesActor.SetShaftTypeToCylinder()
        axesActor.SetCylinderRadius(AXIS_RADIUS)
        self.colorAxes(axesActor, xAxisColor, yAxisColor, zAxisColor)
        return axesActor

    # Create a VTK renderer
    def createRenderer(self, isInteractive=True):
        ren = vtk.vtkRenderer()
        if UserConfig().getColorThemeCode() == LIGHT_MODE:
            self.initBackgroundColor(ren, color=BG_COLOR_LIGHT)
        else:
            self.initBackgroundColor(ren, color=BG_COLOR_DARK)
        # if isInteractive and BG_GRADIENT_ON:
        #     self.setBackgroundColors(ren, color=BG_COLOR_LIGHT, colorBottom=BG_COLOR_BOTTOM)
        return ren

    # Sets the background colors
    def initBackgroundColor(self, ren, color, colorBottom=None):
        if colorBottom is None:
            ren.SetBackground(self.hexToRgb(color))
            ren.GradientBackgroundOff()
            return True
        ren.SetBackground(self.hexToRgb(colorBottom))
        ren.SetBackground2(self.hexToRgb(color))
        ren.GradientBackgroundOn()
        return True

    # Create a renderer for transverse/coronal/sagittal view
    def createViewRenderer(self, view):
        jointActor = self.createJointActor()
        self.moveActorToWorldOrigin(jointActor)
        self.viewJointActors.append(jointActor)  # Add the joint actor to list
        axesActor = self.createAxesActor(self.xAxisColor, self.yAxisColor, self.zAxisColor)
        self.viewAxesActors.append(axesActor)  # Add the axes actor to list
        ren = self.createRenderer(False)
        ren.AddActor(jointActor)
        ren.AddActor(axesActor)
        ren.ResetCamera(self.getCameraResetBounds())
        camera = ren.GetActiveCamera()
        camera.Zoom(ZOOM_FACTOR)
        if view == TRANSVERSE:
            self.transverse = ren
            return ren
        elif view == CORONAL:
            camera.Elevation(90)
            camera.OrthogonalizeViewUp()
            camera.Azimuth(90)
            self.coronal = ren
            return ren
        elif view == SAGITTAL:
            camera.Elevation(90)
            self.sagittal = ren
            return ren
        else:
            return None

    def getMaxBound(self):
        bounds = self.jointActor.GetBounds()
        xmin, xmax, ymin, ymax, zmin, zmax = bounds[:]
        return max(xmax - xmin, ymax - ymin, zmax - zmin)

    def calculateCentre(self, actor):
        bounds = actor.GetBounds()
        xmin, xmax, ymin, ymax, zmin, zmax = bounds[:]
        return [(xmin + xmax) / 2.0,
                (ymin + ymax) / 2.0,
                (zmin + zmax) / 2.0]

    def getCameraResetBounds(self):
        bounds = self.jointActor.GetBounds()
        return [bounds[0] - self.camOffset,
                bounds[1] + self.camOffset,
                bounds[2] - self.camOffset,
                bounds[3] + self.camOffset,
                bounds[4] - self.camOffset,
                bounds[5] + self.camOffset]

    def colorAxes(self, actor, xColor, yColor, zColor):
        actor.GetXAxisShaftProperty().SetColor(self.hexToRgb(xColor))
        actor.GetXAxisTipProperty().SetColor(self.hexToRgb(xColor))
        actor.GetYAxisShaftProperty().SetColor(self.hexToRgb(yColor))
        actor.GetYAxisTipProperty().SetColor(self.hexToRgb(yColor))
        actor.GetZAxisShaftProperty().SetColor(self.hexToRgb(zColor))
        actor.GetZAxisTipProperty().SetColor(self.hexToRgb(zColor))

    def hexToRgb(self, s):
        return tuple(int(s.lstrip('#')[i:i + 2], 16)/255 for i in (0, 2, 4))

    # Make sure the rotation angle is between -89 and 89 (inclusive)
    def validateRotateAngle(self, angle):
        if angle < ROT_LOWER_BOUND:
            return ROT_LOWER_BOUND + 1
        elif angle > ROT_UPPER_BOUND:
            return ROT_UPPER_BOUND - 1
        else:
            return angle

    #######################################################
    # Print methods for testing purpose
    #######################################################
    def printAxesInfo(self):
        print("-----------")
        print("Tip length: " + str(self.axesActor.GetNormalizedTipLength()))  # 0.2, 0.2, 0.2
        print("Cone radius: " + str(self.axesActor.GetConeRadius()))  # 0.4
        print("Cylinder radius: " + str(self.axesActor.GetCylinderRadius()))  # 0.05
        print("-----------")

    def printCameraInfo(self):
        camera = self.ren.GetActiveCamera()
        print('-------')
        print("position", camera.GetPosition())
        print("Focal Point:", camera.GetFocalPoint())
        print("Distance:", camera.GetDistance())
        print("Roll:", camera.GetRoll())
        print("View Up:", camera.GetViewUp())
        print("View angle:", camera.GetViewAngle())
        print("View plane normal:", camera.GetViewPlaneNormal())
        print('-------')

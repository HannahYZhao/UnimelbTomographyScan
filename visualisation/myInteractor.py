# Jiayu Li 713551

import vtk

from visualisation.visConstants import *

# Manages the interaction of VTK images.
class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, gui, renWrapper):
        super(MyInteractorStyle, self).__init__()
        self.gui = gui
        self.renWrapper = renWrapper
        # self.AddObserver("KeyPressEvent", self.keyPressEvent)
        self.AddObserver("MouseMoveEvent", self.mouseMoveEvent)
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("LeftButtonReleaseEvent", self.leftButtonReleaseEvent)
        self.AddObserver("RightButtonPressEvent", self.rightButtonPressEvent)
        self.AddObserver("RightButtonReleaseEvent", self.rightButtonReleaseEvent)
        self.AddObserver("MouseWheelForwardEvent", self.wheelForward)
        self.AddObserver("MouseWheelBackwardEvent", self.wheelBackward)

        self.holdLeft = False  # Indicates whether the left button of the mouse is being pressed
        self.holdRight = False  # Indicates whether the right button of the mouse is being pressed
        self.prevPos = None  # the previous mouse position read

    # Update mouse status
    def leftButtonPressEvent(self, obj, event):
        self.updateMousePos()
        self.holdLeft = True

    # Update mouse status
    def leftButtonReleaseEvent(self, obj, event):
        self.holdLeft = False

    # Update mouse status
    def rightButtonPressEvent(self, obj, event):
        self.updateMousePos()
        self.holdRight = True

    # Update mouse status
    def rightButtonReleaseEvent(self, obj, event):
        self.holdRight = False

    # At mouse move events, call methods depending on which button is being hold.
    # Left for rotating and right for panning
    def mouseMoveEvent(self, obj, event):
        if self.holdLeft or self.holdRight:
            currPos = self.GetInteractor().GetEventPosition()
            if self.holdLeft:
                self.rotate(self.prevPos, currPos)
                self.updateMousePos()
            if self.holdRight:
                self.pan(self.prevPos, currPos)
                self.gui.updateAllVtkWidgets()
                self.updateMousePos()

    # Replace the previous mouse position with the current position
    def updateMousePos(self):
        self.prevPos = self.GetInteractor().GetEventPosition()

    # Detect wheel movement and zoom out when wheel moves forward
    def wheelForward(self, obj, event):
        self.gui.zoomAll(-1)

    # Detect wheel movement and zoom in when wheel moves backward
    def wheelBackward(self, obj, event):
        self.gui.zoomAll(1)

    # Method for Rotation
    def rotate(self, prev, curr):
        xDiff = curr[0] - prev[0]
        yDiff = curr[1] - prev[1]
        width, height = self.GetInteractor().GetSize()
        xRot = ONE_CYCLE_DEGREE * (xDiff / width) * ROT_RATE
        yRot = ONE_CYCLE_DEGREE * (yDiff / height) * ROT_RATE
        self.gui.rotateAll(-xRot, -yRot)

    # Method for panning
    def pan(self, prev, curr):
        self.gui.panAll(prev, curr)

    # def keyPressEvent(self, obj, event):
    #     key = self.iren.GetKeySym()
    #     if key == 'r' or key == 'R':
    #         print("Reset pan")
    #     return

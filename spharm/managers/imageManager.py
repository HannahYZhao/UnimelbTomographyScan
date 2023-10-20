# VTK to 2d image code taken from:
# https://discourse.vtk.org/t/painting-vtkwindowtoimagefilter-output-into-qpixmap-in-qt-widget/1226/3
# Code for lines taken from:
# https://kitware.github.io/vtk-examples/site/Python/GeometricObjects/ColoredLines/

import math

import vtk
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QLabel

from spharm.managers.vtkRendererWrapper import VtkRendererWrapper


TRANSVERSE = "Transverse/Axial (top)"
CORONAL = "Coronal (front)"
SAGITTAL = "Sagittal (left)"
RESET = "Reset"

class imageManager():

    def __init__(self, parent=None):
        pass

    def createImages(self, filePath, imageWidth, imageHeight):

        self.wrapper = VtkRendererWrapper(filePath)
        self.ren = self.wrapper.get3DRenderer()

        images = []

        views = [RESET, TRANSVERSE, CORONAL, SAGITTAL]

        # Code taken from: https://discourse.vtk.org/t/painting-vtkwindowtoimagefilter-output-into-qpixmap-in-qt-widget/1226/3

        # generate the view
        renderWin = self.wrapper.renWin
        renderWin.OffScreenRenderingOn()
        renderWin.SwapBuffersOff()

        for view in views:

            if view == RESET:

                pass

            else:

                renderWin.AddRenderer(self.wrapper.getViewRenderer(view))

            renderWin.Render()

            # copy the view to an image
            windowToImageFilter = vtk.vtkWindowToImageFilter()
            windowToImageFilter.SetInput(renderWin)
            windowToImageFilter.ReadFrontBufferOff(); # read from the back buffer
            windowToImageFilter.Update()
            img = windowToImageFilter.GetOutput()
            w, h, _ = img.GetDimensions()
            vtk_array = img.GetPointData().GetScalars()
            components = vtk_array.GetNumberOfComponents()

            # DEBUG: save image
            """writer = vtk.vtkPNGWriter()
            writer.SetFileName("test_image_{0}.png".format(str(view)))
            writer.SetInputConnection(windowToImageFilter.GetOutputPort())
            writer.Write()"""

            label = QLabel()

            qim = QImage(vtk_array, w, h, QImage.Format_RGB888)
            qPixmap = QPixmap.fromImage(qim)

            pixmap = qPixmap.scaled(imageWidth, imageHeight)

            label.setPixmap(pixmap)

            images.append(label)

        return images

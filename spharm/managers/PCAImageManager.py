# VTK to 2d image code taken from:
# https://discourse.vtk.org/t/painting-vtkwindowtoimagefilter-output-into-qpixmap-in-qt-widget/1226/3
# Code for lines taken from:
# https://kitware.github.io/vtk-examples/site/Python/GeometricObjects/ColoredLines/
# Code for hex to RGB taken from:
# https://www.delftstack.com/howto/python/python-hex-to-rgb/

import math

import vtk
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QLabel

import userConfig
from spharm.managers.vtkRendererWrapper import VtkRendererWrapper


TRANSVERSE = "Transverse/Axial (top)"
CORONAL = "Coronal (front)"
SAGITTAL = "Sagittal (left)"
RESET = "Reset"

class PCAImageManager():

    def __init__(self, parent=None):
        pass

    def getEigenVectors(self, filePath):

        overallscale = 1.0

        # Get data from the file
        inReader = vtk.vtkGenericDataObjectReader()
        inReader.SetFileName(filePath)
        inReader.Update()

        # mesh = vtk.vtkPolyData()
        mesh = inReader.GetPolyDataOutput()

        # PCA
        # These would be all of your "x" values.
        xArray = vtk.vtkDoubleArray()
        xArray.SetNumberOfComponents(1)
        xArray.SetName("x")

        # These would be all of your "y" values.
        yArray = vtk.vtkDoubleArray()
        yArray.SetNumberOfComponents(1)
        yArray.SetName("y")

        # These would be all of your "z" values.
        zArray = vtk.vtkDoubleArray()
        zArray.SetNumberOfComponents(1)
        zArray.SetName("z")

        for i in range(mesh.GetNumberOfPoints()):
            # print(i)
            p = [0, 0, 0]
            mesh.GetPoint(i, p)
            xArray.InsertNextValue(p[0])
            yArray.InsertNextValue(p[1])
            zArray.InsertNextValue(p[2])

        datasetTable = vtk.vtkTable()
        datasetTable.AddColumn(xArray)
        datasetTable.AddColumn(yArray)
        datasetTable.AddColumn(zArray)

        pcaStatistics = vtk.vtkPCAStatistics()
        pcaStatistics.SetInputData(vtk.vtkStatisticsAlgorithm.INPUT_DATA, datasetTable)

        pcaStatistics.SetColumnStatus("x", 1)
        pcaStatistics.SetColumnStatus("y", 1)
        pcaStatistics.SetColumnStatus("z", 1)

        pcaStatistics.RequestSelectedColumns()
        pcaStatistics.SetDeriveOption(True)
        pcaStatistics.Update()

        # Eigenvectors
        evec1 = vtk.vtkDoubleArray()
        pcaStatistics.GetEigenvector(0, evec1)

        evec2 = vtk.vtkDoubleArray()
        pcaStatistics.GetEigenvector(1, evec2)

        evec3 = vtk.vtkDoubleArray()
        pcaStatistics.GetEigenvector(2, evec3)

        #TODO: Okay to change center to 0,0,0?
        centre = [0.0,0.0,0.0]

        # Eigenvalues
        eigenvalues = vtk.vtkDoubleArray()
        pcaStatistics.GetEigenvalues(eigenvalues)

        # Eigenvector 1,1
        scale1 = math.sqrt(eigenvalues.GetValue(0)) * overallscale

        vec1Source = vtk.vtkLineSource()
        vec1Source.SetPoint1(centre[0], centre[1], centre[2])
        vec1Source.SetPoint2((scale1 * evec1.GetValue(0)) + centre[0],
                             (scale1 * evec1.GetValue(1)) + centre[1],
                             (scale1 * evec1.GetValue(2)) + centre[2])

        # Eigenvector 1,2
        scale2 = math.sqrt(eigenvalues.GetValue(1)) * overallscale
        vec2Source = vtk.vtkLineSource()
        vec2Source.SetPoint1(centre[0], centre[1], centre[2])
        vec2Source.SetPoint2((scale2 * evec2.GetValue(0)) + centre[0],
                             (scale2 * evec2.GetValue(1)) + centre[1],
                             (scale2 * evec2.GetValue(2)) + centre[2])

        # Eigenvector 1,3
        scale3 = math.sqrt(eigenvalues.GetValue(2)) * overallscale

        vec3Source = vtk.vtkLineSource()
        vec3Source.SetPoint1(centre[0], centre[1], centre[2])
        vec3Source.SetPoint2((scale3 * evec3.GetValue(0)) + centre[0],
                             (scale3 * evec3.GetValue(1)) + centre[1],
                             (scale3 * evec3.GetValue(2)) + centre[2])

        return vec1Source, vec2Source, vec3Source


    #Source: https://www.delftstack.com/howto/python/python-hex-to-rgb/
    def hex2RGB(self, string):
        string = string.lstrip('#')
        t = tuple(int(string[i:i+2], 16) for i in (0, 2, 4))
        return t

    def getLineActors(self, filePath):

        vec1Source, vec2Source, vec3Source = self.getEigenVectors(filePath)

        centre = [0.0,0.0,0.0]

        linesPolyData = vtk.vtkPolyData()

        pts = vtk.vtkPoints()
        pts.InsertNextPoint(centre[0], centre[1], centre[2])
        pts.InsertNextPoint(vec1Source.GetPoint2())
        pts.InsertNextPoint(vec2Source.GetPoint2())
        pts.InsertNextPoint(vec3Source.GetPoint2())

        # Add the points to the polydata container
        linesPolyData.SetPoints(pts)

        #Attribution statement: code for lines taken from
        #https://kitware.github.io/vtk-examples/site/Python/GeometricObjects/ColoredLines/
        # Create the first line (between Origin and P0)
        line0 = vtk.vtkLine()
        line0.GetPointIds().SetId(0, 0)  # the second 0 is the index of the Origin in linesPolyData's points
        line0.GetPointIds().SetId(1, 1)  # the second 1 is the index of P0 in linesPolyData's points

        # Create the second line (between Origin and P1)
        line1 = vtk.vtkLine()
        line1.GetPointIds().SetId(0, 0)  # the second 0 is the index of the Origin in linesPolyData's points
        line1.GetPointIds().SetId(1, 2)  # 2 is the index of P1 in linesPolyData's points

        # Create the second line (between Origin and P1)
        line2 = vtk.vtkLine()
        line2.GetPointIds().SetId(0, 0)  # the second 0 is the index of the Origin in linesPolyData's points
        line2.GetPointIds().SetId(1, 3)  # 2 is the index of P1 in linesPolyData's points

        # Create a vtkCellArray container and store the lines in it
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(line0)
        lines.InsertNextCell(line1)
        lines.InsertNextCell(line2)

        # Add the lines to the polydata container
        linesPolyData.SetLines(lines)

        namedColors = vtk.vtkNamedColors()

        # Create a vtkUnsignedCharArray container and store the colors in it
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        """try:
            colors.InsertNextTupleValue(namedColors.GetColor3ub("Tomato"))
            colors.InsertNextTupleValue(namedColors.GetColor3ub("BlueViolet"))
            colors.InsertNextTupleValue(namedColors.GetColor3ub("Gold"))
        except AttributeError:
            # For compatibility with new VTK generic data arrays.
            colors.InsertNextTypedTuple(namedColors.GetColor3ub("Tomato"))
            colors.InsertNextTypedTuple(namedColors.GetColor3ub("BlueViolet"))
            colors.InsertNextTypedTuple(namedColors.GetColor3ub("Gold"))"""

        #print(namedColors.GetColor3ub("Gold"))

        savedColor1 = userConfig.UserConfig().getPCAColor(1)
        savedColor2 = userConfig.UserConfig().getPCAColor(2)
        savedColor3 = userConfig.UserConfig().getPCAColor(3)

        colors.InsertNextTypedTuple(self.hex2RGB(savedColor1))
        colors.InsertNextTypedTuple(self.hex2RGB(savedColor2))
        colors.InsertNextTypedTuple(self.hex2RGB(savedColor3))

        # Color the lines.
        # SetScalars() automatically associates the values in the data array passed as parameter
        # to the elements in the same indices of the cell data array on which it is called.
        # This means the first component (red) of the colors array
        # is matched with the first component of the cell array (line 0)
        # and the second component (green) of the colors array
        # is matched with the second component of the cell array (line 1)
        linesPolyData.GetCellData().SetScalars(colors)

        # Setup the visualization pipeline
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(linesPolyData)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(4)

        return actor


    def createImages(self, lowFilePath, highFilePath, imageWidth, imageHeight):

        self.wrapper = VtkRendererWrapper(highFilePath)
        self.ren = self.wrapper.get3DRenderer()

        #Remove the axis and add the PCA vectors
        self.wrapper.ren.RemoveActor(self.wrapper.axesActor)
        self.wrapper.ren.AddActor(self.getLineActors(lowFilePath))

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

# Xueqi Guan 1098403
# Jiayu Li 713551 - Wrote the opacity slider

from PySide2.QtCore import Qt
from PySide2.QtWidgets import *

from visualisation.visConstants import *
import resourceManager as rm


# The windows which allows users to change colors of axies
class Settings(QWidget):
    def __init__(self, visWin, xAxisColor, yAxisColor, zAxisColor):
        super().__init__()
        self.setWindowIcon(rm.getIcon("scanFlowIcon.png"))
        self.setWindowTitle("Settings")
        x = WINDOW_POS_X + int(WINDOW_WIDTH / 2) - int(SETTINGS_WIDTH / 2)
        y = WINDOW_POS_Y + int(WINDOW_HEIGHT / 2) - int(SETTINGS_HEIGHT / 2)
        self.setGeometry(x, y, SETTINGS_WIDTH, SETTINGS_HEIGHT)
        self.setStyleSheet(UserConfig().getColorTheme())
        self.visWindow = visWin
        # Axis colours
        self.xAxisColor = xAxisColor  # in hex
        self.yAxisColor = yAxisColor  # in hex
        self.zAxisColor = zAxisColor  # in hex
        self.xAxisBtn = QPushButton()
        self.yAxisBtn = QPushButton()
        self.zAxisBtn = QPushButton()
        # Bone opacity
        self.opacitySlider = QSlider(Qt.Horizontal)
        self.opacityLabel = QLabel()
        # Initialisation
        self.ui()
        self.show()

    def ui(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        # Buttons for changing axis colors
        axisBtns = [self.xAxisBtn, self.yAxisBtn, self.zAxisBtn]
        axisColors = [self.xAxisColor, self.yAxisColor, self.zAxisColor]
        for i in range(len(axisBtns)):
            axisHBox = QHBoxLayout()
            vbox.addLayout(axisHBox)
            axisLabel = QLabel("{}-Axis Color".format(AXIS_NAMES[i]))
            axisHBox.addWidget(axisLabel)
            axisBtns[i].setStyleSheet("background-color: {}; border: 0px".format(axisColors[i]))
            axisBtns[i].clicked.connect(lambda *args, c=AXIS_NAMES[i]: self.changeColor(c))
            axisHBox.addWidget(axisBtns[i])
            axisHBox.addStretch()

        # Slider for bone opacity
        opacityHBox = QHBoxLayout()
        vbox.addLayout(opacityHBox)
        boLabel = QLabel()
        boLabel.setText("Bone opacity: ")
        boPercentage = round(UserConfig().getBoneOpacity()*100)
        opacityHBox.addWidget(boLabel)
        self.opacitySlider.setMaximum(100)
        self.opacitySlider.setMinimum(30)
        self.opacitySlider.setValue(boPercentage)
        self.opacitySlider.setTickInterval(10)
        self.opacitySlider.setTickPosition(QSlider.TicksAbove)
        self.opacitySlider.valueChanged.connect(self.sliderFunc)
        opacityHBox.addWidget(self.opacitySlider)
        self.opacityLabel.setText("{}%".format(boPercentage))
        opacityHBox.addWidget(self.opacityLabel)

        # Horizontal box for ok and cancel buttons
        btnHBox = QHBoxLayout()
        vbox.addLayout(btnHBox)
        # OK button
        okBtn = QPushButton("OK")
        okBtn.setDefault(True)
        okBtn.clicked.connect(self.ok)
        btnHBox.addStretch()
        btnHBox.addWidget(okBtn)
        # Cancel button
        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.cancel)
        btnHBox.addWidget(cancelBtn)

    def sliderFunc(self):
        self.opacityLabel.setText(str(self.opacitySlider.value()) + "%")

    def changeColor(self, axis):
        color = QColorDialog.getColor().name()
        if axis == X:
            self.xAxisColor = color
            self.xAxisBtn.setStyleSheet("background-color: {}; border: 0px".format(color))
        elif axis == Y:
            self.yAxisColor = color
            self.yAxisBtn.setStyleSheet("background-color: {}; border: 0px".format(color))
        elif axis == Z:
            self.zAxisColor = color
            self.zAxisBtn.setStyleSheet("background-color: {}; border: 0px".format(color))

    def ok(self):
        # Set axis colors
        # print("x color: {}, y color: {}, z color: {}".format(self.xAxisColor, self.yAxisColor, self.zAxisColor))
        self.visWindow.setColors(self.xAxisColor, self.yAxisColor, self.zAxisColor)
        UserConfig().setAxisColors([self.xAxisColor, self.yAxisColor, self.zAxisColor])
        # Set bone opacity
        opacity = self.opacitySlider.value() / 100.0
        self.visWindow.setBoneOpacity(opacity)
        UserConfig().setBoneOpacity(opacity)
        # close settings window
        self.close()

    def cancel(self):
        self.close()

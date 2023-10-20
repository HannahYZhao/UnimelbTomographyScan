from spharm.managers.dataSingleton import dataSingleton
from spharm.managers.frameManager import frameManager

class stackManager():

    def __init__(self, stack, parent):

        self.stack = stack
        self.dataManager = dataSingleton()
        self.parent = parent
        self.frameManager = frameManager(stack, parent)

    def next(self, step):

        self.stack.setCurrentIndex(step)

        self.stack.currentWidget().refresh()

    def previous(self, step):

        self.stack.setCurrentIndex(step - 1 -1)

        self.stack.currentWidget().refresh()

    def createStack(self, order):

        for item in order:
            self.frameManager.createFrame(item)



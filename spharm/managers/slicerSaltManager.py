from time import sleep

from PySide2.QtCore import QProcess, QThread, QObject, Signal

from spharm.managers.dataSingleton import dataSingleton

import os

from spharm.managers.timeManager import TimeManager

MESSAGE = "File created: "
MESSAGEALREADYCREATED = "File already created: "
#ARGUMENTS = ['--no-main-window', '--python-script', 'replaceWithScript', 'replaceWithIni']
ARGUMENTS = ['--python-script', 'replaceWithScript', 'replaceWithIni']

#SCRIPT = 2
#INI = 3

SCRIPT = 1
INI = 2


#Worker to find when files are done
class Worker(QObject):

    finished = Signal()
    finishedProcess = Signal()
    fileProcessed = Signal(str)

    def runLow(self):

        self.cancelled = False

        self.dataManager = dataSingleton()

        ##print("runLow")

        self.files = self.dataManager.getExpectedFiles("lowExpected")

        #print(self.files)

        self.run()

    def runHigh(self):

        self.cancelled = False

        self.dataManager = dataSingleton()

        self.files = self.dataManager.getExpectedFiles("highExpected")

        self.run()

        #print("runHigh")

    def run(self):

        #print("running")

        files = self.files

        #print(files)

        noFiles = len(files)

        processedFiles = []

        noFilesCreated = 0

        while(self.cancelled == False):


            for row in range(noFiles):

                if os.path.isfile(files[row]) and not (files[row] in processedFiles):

                    #print("file processed")
                    noFilesCreated+=1
                    self.fileProcessed.emit(files[row])
                    processedFiles.append(files[row])

            ##print(noFilesCreated)
            ##print(noFiles)

            if (noFilesCreated == noFiles):

                self.finishedProcess.emit()

                self.finished.emit()

                break

            sleep(1)

    def cancel(self):
        #print("worker cancelling")
        self.cancelled = True
        self.finishedProcess.emit()
        self.finished.emit()

class slicerSaltManager():

    #TODO: What if empty?
    def getTotalFiles(self):

        counter = 0
        directory = self.dataManager.getOutput("fileInput","inputDirectory")
        for file in os.listdir(directory):
            #print(file)
            if '.gipl' in file:
                counter+=1
        #print(counter)
        return counter

    def __init__(self, parent):

        self.dataManager = dataSingleton()

        self.parent = parent


    def writeOutput(self):

        data = self.process.readAllStandardOutput()
        output = bytes(data).decode("utf8")

        self.parent.writeStandardOutput(output)

    def writeError(self):
        data = self.process.readAllStandardError()
        output = bytes(data).decode("utf8")
        self.parent.writeError(output)

    def finishedProcess(self):

        #self.process = None #End the process

        #print("finishedProcess")

        self.parent.finishedProcess()

    def setIni(self, iniFile):

        self.iniFile = iniFile

    def setType(self, type):
        self.type = type

    def cancel(self):

        #print("cancelling")
        self.process.terminate()

        #Cancel the thread too
        self.worker.cancel()

        #print("finished cancelling")

    def reportProgress(self, string):
        #Increase the files processed bar
        self.parent.fileProcessed()
        #Output a message to the console
        self.parent.writeCompletedOutput(MESSAGE + string)

        self.timeManager.taskFinished()
        hourTime, minTime, secTime = self.timeManager.getEstimateHMS()
        self.parent.updateTimeEstimate(hourTime, minTime, secTime)

    def finished(self):

        #print("finished")

        self.finishedProcess()

        self.process.terminate()

    def checkAllFilesCreated(self):

        dataManager = dataSingleton()

        if self.type == "high":

            files = dataManager.getExpectedFiles("highExpected")

        elif self.type == "low":

            files = dataManager.getExpectedFiles("lowExpected")

        noFiles = len(files)

        noFilesCreated = 0

        for row in range(noFiles):

            if os.path.isfile(files[row]):

                noFilesCreated+=1

        if (noFilesCreated == noFiles):
            for row in range(noFiles):
                self.parent.writeCompletedOutput(MESSAGEALREADYCREATED + files[row])
                self.parent.fileProcessed()
            return True
        return False

    def run(self):

        #Time manager code
        self.timeManager = TimeManager()
        self.timeManager.setTasks(self.getTotalFiles())
        self.timeManager.start()

        self.process = QProcess()

        self.process.readyReadStandardOutput.connect(self.writeOutput)
        self.process.readyReadStandardError.connect(self.writeError)
        self.process.finished.connect(self.finishedProcess)

        arguments = ARGUMENTS
        #arguments[2] = pathSingleton().getRelativeScriptPath('SPHARM-PDM.txt')
        arguments[SCRIPT] = dataSingleton().getCopiedScriptPath()

        program = dataSingleton().getOutput("slicerSalt", "slicerSaltPath")

        if (self.type=="low"):
            arguments[INI] =  self.dataManager.getOutput("fileInput",
                                                         "lowResIniFile")
        else:
            arguments[INI] =  self.dataManager.getOutput("fileInput",
                                                         "highResIniFile")
        #print(str(program)+str(arguments))

        #Check the files haven't already been created
        if self.checkAllFilesCreated():
            #print("found all files")
            self.finishedProcess()
            return #Quit so a useless Slicer Salt window isn't created


        self.parent.writeCompletedOutput("Opening SlicerSALT...")
        self.process.start(program, arguments)

        self.thread = None
        self.worker = None

        #New method for detecting change in files
        #Use threading to prevent GUI hanging
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        if self.type == "high":
            self.thread.started.connect(self.worker.runHigh)
        else:
            self.thread.started.connect(self.worker.runLow)
        self.worker.finishedProcess.connect(self.finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.fileProcessed.connect(self.reportProgress)
        self.thread.start()



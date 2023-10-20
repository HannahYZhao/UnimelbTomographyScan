from PySide2.QtCore import QProcess

from spharm.managers.dataSingleton import dataSingleton

import os

from spharm.managers.pathSingleton import pathSingleton

MATCH = 'sec to run'
ARGUMENTS = ['--no-main-window', '--python-script', 'replaceWithScript', 'replaceWithIni']
MATCHFIN = 'All pipelines took:'

class slicerSaltManager():



    #TODO: What if empty?
    def getTotalFiles(self):

        counter = 0
        directory = self.dataManager.getOutput("fileInput","inputDirectory")
        for file in os.listdir(directory):
                print(file)
                if '.gipl' in file:
                    counter+=1
        print(counter)
        return counter

    def __init__(self, parent):

        self.dataManager = dataSingleton()

        self.parent = parent

    def writeOutput(self):

        data = self.process.readAllStandardOutput()
        output = bytes(data).decode("utf8")

        #Include last line in count
        if (MATCH.lower() in output.lower()):

            self.parent.writeCompletedOutput(output)

            #Count the number of times that complete occurs
            count = output.lower().count(MATCH.lower())
            for i in range(count):
                self.parent.fileProcessed()

        else:

            self.parent.writeStandardOutput(output)

        #Terminate the process when final line written
        if MATCHFIN.lower() in output.lower():

            print("reached end of console output")


            print("terminating")

            self.process.terminate()

            print("finished terminating")

    def writeError(self):
        data = self.process.readAllStandardError()
        output = bytes(data).decode("utf8")
        self.parent.writeError(output)

    def finishedProcess(self):

        #self.process = None #End the process

        self.parent.finishedProcess()

    def setIni(self, iniFile):

        self.iniFile = iniFile

    def setType(self, type):
            self.type = type

    def cancel(self):

        print("cancelling")
        self.process.terminate()

        print("finished cancelling")

    def run(self):

        self.process = QProcess()

        self.process.readyReadStandardOutput.connect(self.writeOutput)
        self.process.readyReadStandardError.connect(self.writeError)
        self.process.finished.connect(self.finishedProcess)

        arguments = ARGUMENTS
        arguments[2] = pathSingleton().getRelativeScriptPath('SPHARM-PDM.txt')

        program = dataSingleton().getOutput("slicerSalt", "slicerSaltPath")

        if (self.type=="low"):
            arguments[3] =  self.dataManager.getOutput("fileInput",
                                                       "lowResIniFile")
        else:
            arguments[3] =  self.dataManager.getOutput("fileInput",
                                                       "highResIniFile")
        print(str(program)+str(arguments))
        self.process.start(program, arguments)
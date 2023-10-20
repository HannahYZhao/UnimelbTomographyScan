import os

from spharm.managers.singleton import Singleton

class dataSingleton(Singleton):

    def addPCAFiles(self, files):
        self.PCAFiles = files

    def getPCAFiles(self):
        return self.PCAFiles

    def addFiles(self):

        directory = self.getOutput("fileInput","inputDirectory")
        for file in os.listdir(directory):

            if '.gipl' in file:
                fileReduced = file.replace('.gipl','')

                lowFile = self.getOutput("fileInput","outputVTKDirectoryLow") + "Step3_ParaToSPHARMMesh/"+fileReduced + '_pp_surf_SPHARM.vtk'
                highFile = self.getOutput("fileInput","outputVTKDirectoryHigh") + "Step3_ParaToSPHARMMesh/"+fileReduced + '_pp_surf_SPHARM.vtk'
                self.setFileInfo(fileReduced, "gipl",file)
                self.setFileInfo(fileReduced, "low",lowFile)
                self.setFileInfo(fileReduced, "lowExpected",lowFile)
                self.setFileInfo(fileReduced, "high",highFile)
                self.setFileInfo(fileReduced, "highExpected",highFile)
                self.setFileInfo(fileReduced, "verified",True)


    def checkFiles(self, type):

        list = []

        for key in self.getFileKeys():

            verified = self.getFileInfo(key, "verified")

            file = self.getFileInfo(key, type)

            #print(file)

            if not os.path.exists(file):
                #print("does not exist")
                list.append(file)
                verified = False

            if not verified:
                self.setFileInfo(key, "verified", False)
        return list

    def init(self):
        ##print("This is only executed when calling the singleton first time")
        ##print("calling init")
        pass

    def setParameters(self, parameters):
        self.parameters = parameters
        self.fileInfo = {}
        self.data = {}
        self.PCAFiles = []

    def __init__(self):
        ##print("This is executed both first and second time")
        ##print("calling __init__")
        pass

    # These are built in by Big
    def getParameter(self, key1, key2):

        output = self.parameters[key1][key2]

        return output

    # Only set at start by driver
    def setParameter(self, key1, key2, input):

        self.parameters[key1][key2] = input

    def setFileInfo(self, fileKey, infoKey, input):

        if not (fileKey in self.fileInfo):
            self.fileInfo[fileKey] = {}

        self.fileInfo[fileKey][infoKey] = input


    def getFileKeys(self):
        return sorted(self.fileInfo.keys())

    def getFiles(self, type):
        keys = self.getFileKeys()
        files = []
        for key in keys:
            if (self.getFileInfo(key, "verified")==True):
                if (type =="key"):
                    files.append(key)
                else:
                    files.append(self.getFileInfo(key, type))
        return files

    def getExpectedFiles(self, type):
        keys = self.getFileKeys()
        files = []
        for key in keys:
            files.append(self.getFileInfo(key, type))
        return files

    def getCopiedScriptPath(self):
        return self.scriptPath

    def setCopiedScriptPath(self, path):
        self.scriptPath = path

    def getTotalFiles(self):
        #print(len(self.getFiles("low")))
        return len(self.getFiles("low"))


    def getFileInfo(self, fileKey, infoKey):

        return self.fileInfo[fileKey][infoKey]

    def setOutput(self, key1, key2, input):

        try:

            self.data[key1][key2] = input

        except:

            dict = {}

            self.data[key1] = dict

            self.data[key1][key2] = input


    def getOutput(self, key1, key2):

        output = self.data[key1][key2]

        return output
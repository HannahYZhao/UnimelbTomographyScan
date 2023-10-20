# Code by Yuxiang Wu
# 1006014
import configparser
from shutil import copyfile

from spharm.managers.dataSingleton import dataSingleton
from spharm.managers.pathSingleton import pathSingleton


class iniManager():

    def __init__(self, parent):
        self.dataManager = dataSingleton()
        self.parent = parent

    def write(self, iniFileName, iniLocation, inputDirectory, outputDirectory,
              rescale, space, subdiv, degree, flip, flipTemplate):
        write_config = configparser.ConfigParser()

        write_config.add_section("DirectoryPath")
        write_config.set("DirectoryPath", "inputDirectoryPath", inputDirectory)
        write_config.set("DirectoryPath", "outputDirectoryPath", outputDirectory)

        write_config.add_section("SegPostProcess")
        write_config.set("SegPostProcess", "rescale", str(rescale))
        write_config.set("SegPostProcess", "space", str(space).strip('[]'))
        write_config.set("SegPostProcess", "label", "0")
        write_config.set("SegPostProcess", "gauss", str(False))
        write_config.set("SegPostProcess", "var", "10,10,10")


        write_config.add_section("GenParaMesh")
        write_config.set("GenParaMesh", "iter", "1000")

        write_config.add_section("ParaToSPHARMMesh")
        write_config.set("ParaToSPHARMMesh", "subdivLevel", str(subdiv))
        write_config.set("ParaToSPHARMMesh", "spharmDegree", str(degree))
        write_config.set("ParaToSPHARMMesh", "medialMesh", str(True))
        write_config.set("ParaToSPHARMMesh", "phiIteration", str(100))
        write_config.set("ParaToSPHARMMesh", "thetaIteration", str(100))
        write_config.set("ParaToSPHARMMesh", "regParaTemplateFileOn", str(False))
        write_config.set("ParaToSPHARMMesh", "flipTemplateOn",str(flip))
        write_config.set("ParaToSPHARMMesh", "flipTemplate",str(flipTemplate))
        write_config.set("ParaToSPHARMMesh", "flip", "0")

        write_config.set('ParaToSPHARMMesh', 'medialMesh', str(True))

        output = "Writing file {0} to location: {1}\n\n".format(iniFileName+".ini", iniLocation)
        self.parent.writeStandardOutput(output)

        sections = write_config.sections()
        for section in sections:
            #print(write_config.items(section))
            self.parent.writeStandardOutput(str(write_config.items(section)))

        #print(iniLocation)
        cfgfile = open(iniLocation+"/"+iniFileName+".ini", 'w')
        write_config.write(cfgfile)
        cfgfile.close()



    def createLowResIni(self):

        iniLocation = self.dataManager.getOutput("fileInput",
                                                   "outputWorkingDirectory")
        iniFileName = "lowIni"
        inputDirectory = self.dataManager.getOutput("fileInput",
                                                    "inputDirectory")
        outputDirectory = self.dataManager.getOutput("fileInput",
                                                    "outputVTKDirectoryLow")
        rescale = True
        sx = self.dataManager.getOutput("SPHARMInputLow","sx")
        sy = self.dataManager.getOutput("SPHARMInputLow","sy")
        sz = self.dataManager.getOutput("SPHARMInputLow","sz")
        space = [sx, sy, sz]

        subdiv = round(self.dataManager.getOutput("SPHARMInputLow","subdiv"))
        degree = round(self.dataManager.getOutput("SPHARMInputLow","degree"))
        flip = self.dataManager.getOutput("SPHARMInputLow","flip")
        flipTemplate = self.dataManager.getOutput("SPHARMInputLow","flipTemplate")

        self.write(iniFileName, iniLocation, inputDirectory,
                      outputDirectory, rescale, space, subdiv, degree, flip,
                   flipTemplate)





        #Output the ini file
        self.dataManager.setOutput("fileInput", "lowResIniFile", iniLocation+iniFileName+".ini")

    def createHighResIni(self):

        iniLocation = self.dataManager.getOutput("fileInput",
                                                 "outputWorkingDirectory")
        iniFileName = "highIni"
        inputDirectory = self.dataManager.getOutput("fileInput",
                                                    "inputDirectory")
        outputDirectory = self.dataManager.getOutput("fileInput",
                                                     "outputVTKDirectoryHigh")
        rescale = True
        sx = self.dataManager.getOutput("SPHARMInputHigh","sx")
        sy = self.dataManager.getOutput("SPHARMInputHigh","sy")
        sz = self.dataManager.getOutput("SPHARMInputHigh","sz")
        space = [sx, sy, sz]

        subdiv = round(self.dataManager.getOutput("SPHARMInputHigh","subdiv"))
        degree = round(self.dataManager.getOutput("SPHARMInputHigh","degree"))
        flip = self.dataManager.getOutput("SPHARMInputHigh","flip")
        flipTemplate = self.dataManager.getOutput("SPHARMInputHigh","flipTemplate")

        self.write(iniFileName, iniLocation, inputDirectory,
                   outputDirectory, rescale, space, subdiv, degree, flip,
                   flipTemplate)


        #Output the ini file
        self.dataManager.setOutput("fileInput", "highResIniFile", iniLocation+iniFileName+".ini")

    def getTotalFiles(self):
        #TODO: fix if low but not high outputed?
        return 2

    #Can't cancel it
    def cancel(self):

        pass

    def run(self):

        #Create low res ini
        self.createLowResIni()

        self.parent.fileProcessed()

        output = "\n\n Low res .ini file created. \n\n\n\n"

        self.parent.writeStandardOutput(output)

        #Create low res ini
        self.createHighResIni()

        self.parent.fileProcessed()

        output = "\n\n High res .ini file created."

        self.parent.writeStandardOutput(output)

        #Create file for slicer Salt

        originalFile = pathSingleton().getRelativeScriptPath('SPHARM-PDM.txt')
        iniLocation = self.dataManager.getOutput("fileInput",
                                                 "outputWorkingDirectory")
        copyfile(originalFile, iniLocation+'SPHARM-PDM.py')
        self.dataManager.setCopiedScriptPath(iniLocation+'SPHARM-PDM.py')

        self.parent.finishedProcess()


import userConfig
from spharm.frames.SPHARMInputFrame import SPHARMInputFrame
from spharm.frames.animalFrame import animalFrame
from spharm.frames.fileSelectionFrame import FileSelection
from spharm.frames.PCASelectionFrame import PCASelection
from spharm.frames.highAndLowFrame import highAndLow
from spharm.frames.informationFrame import information
from spharm.frames.progressFrame import progressFrame
from spharm.frames.slicerSaltFrame import slicerSalt

import pandas as pd

from spharm.managers.dataSingleton import dataSingleton
from spharm.managers.iniManager import iniManager
from spharm.managers.pathSingleton import pathSingleton
from spharm.managers.slicerSaltManager import slicerSaltManager


class frameManager():

    def __init__(self, stack, parent):



        self.stack = stack
        self.step = 0
        self.dataManager = dataSingleton()
        self.parent = parent

        self.information = pd.read_csv(pathSingleton().getRelativePath('instructions.csv'),
                                        header=0, usecols=[0,1,2], sep=','
                                        , names=['key','title','instruction'] )

        self.instructions = self.information.set_index('key')['instruction'].to_dict()

        self.titles = self.information.set_index('key')['title'].to_dict()

        for key in self.instructions.keys():
            self.instructions[key] = self.instructions[key].replace("\\n","\n")

        
    def createFrame(self, item):


        if item == "highAndLow":
            self.step+=1

            highAndLowModule = highAndLow()

            highAndLowModule.setStep(self.step)

            highAndLowModule.setTitle(self.titles[item])
            highAndLowModule.setInstruction(self.instructions[item])
            highAndLowModule.setParent(self.parent)
            self.stack.addWidget(
                highAndLowModule)

        if item == "flipSelection":
            self.step+=1

            flipSelectionModule = PCASelection()

            flipSelectionModule.setStep(self.step)

            flipSelectionModule.setTitle(self.titles[item])
            flipSelectionModule.setInstruction(self.instructions[item])
            flipSelectionModule.setParent(self.parent)
            self.stack.addWidget(
                flipSelectionModule)


        if item == "animal":
            self.step+=1

            animalModule = animalFrame()

            animalModule.setStep(self.step)

            #print(self.titles)
            #print(self.titles[item])

            animalModule.setTitle(self.titles[item])
            animalModule.setInstruction(self.instructions[item])
            animalModule.setParent(self.parent)

            animalModule.setOutput("animal")

            self.stack.addWidget(
                animalModule)


        if item == "summary":
            self.step+=1

            summaryModule = information()

            summaryModule.setStep(self.step)

            summaryModule.setTitle(self.titles[item])
            summaryModule.setInstruction(self.instructions[item])
            summaryModule.setParent(self.parent)
            summaryModule.setFinish()
            summaryModule.setConsole()
            self.stack.addWidget(
                summaryModule)

        if item == "introduction":
            self.step+=1

            introductionModule = information()

            introductionModule.setStep(self.step)

            introductionModule.setTitle(self.titles[item])
            introductionModule.setInstruction(self.instructions[item])
            introductionModule.setParent(self.parent)
            self.stack.addWidget(
                introductionModule)


        if item == "fileInput":
            self.step+=1

            fileSelectionModule = FileSelection()
            fileSelectionModule.setParameters(
                self.dataManager.getParameter("directoryParameters", "inputDirectory"),
                self.dataManager.getParameter("directoryParameters", "outputWorkingDirectory"),
                self.dataManager.getParameter("directoryParameters", "outputVTKDirectoryLow"),
                self.dataManager.getParameter("directoryParameters", "outputVTKDirectoryHigh"))

            """fileSelectionModule.setParameters(
                userConfig.UserConfig().getSPHARMLastFolder("gipl"),
                userConfig.UserConfig().getSPHARMLastFolder("ini"),
                userConfig.UserConfig().getSPHARMLastFolder("low"),
                userConfig.UserConfig().getSPHARMLastFolder("high")

            )"""

            fileSelectionModule.setStep(self.step)
            fileSelectionModule.setParent(self.parent)
            fileSelectionModule.setTitle(self.titles[item])
            fileSelectionModule.setInstruction(self.instructions[item])
            fileSelectionModule.setOutput(item)
            self.stack.addWidget(
                fileSelectionModule)

        if item == "slicerSalt":
            self.step+=1

            slicerSaltModule = slicerSalt()
            slicerSaltModule.setOutput(item)
            slicerSaltModule.setParameters(
                self.dataManager.getParameter("slicerSaltParameters",
                                     "slicerSaltPath"))

            #slicerSaltModule.setParameters(userConfig.UserConfig().getSlicerSALT())
            slicerSaltModule.setStep(self.step)
            slicerSaltModule.setParent(self.parent)
            slicerSaltModule.setTitle(self.titles[item])
            slicerSaltModule.setInstruction(self.instructions[item])
            self.stack.addWidget(
                slicerSaltModule)

        if item == "SPHARMInputLow":
            self.step+=1
            SPHARMInputModuleLow = SPHARMInputFrame()
            SPHARMInputModuleLow.setStep(self.step)
            SPHARMInputModuleLow.setParent(self.parent)
            SPHARMInputModuleLow.setOutput(item)
            lowSx = self.dataManager.getParameter("lowParameters", "sx")
            lowSy = self.dataManager.getParameter("lowParameters", "sy")
            lowSz = self.dataManager.getParameter("lowParameters", "sz")
            SPHARMInputModuleLow.setParameters(lowSx, lowSy, lowSz, True, False)
            SPHARMInputModuleLow.setTitle(self.titles[item])
            SPHARMInputModuleLow.setInstruction(self.instructions[item])
            self.stack.addWidget(SPHARMInputModuleLow)

        if item == "SPHARMInputHigh":
            self.step+=1
            SPHARMInputModuleHigh = SPHARMInputFrame()
            SPHARMInputModuleHigh.setStep(self.step)
            SPHARMInputModuleHigh.setParent(self.parent)
            SPHARMInputModuleHigh.setOutput(item)

            highSx = self.dataManager.getParameter("highParameters", "sx")
            highSy = self.dataManager.getParameter("highParameters", "sy")
            highSz = self.dataManager.getParameter("highParameters", "sz")
            SPHARMInputModuleHigh.setParameters(highSx, highSy, highSz, True, False)
            SPHARMInputModuleHigh.setTitle(self.titles[item])
            SPHARMInputModuleHigh.setInstruction(self.instructions[item])


            self.stack.addWidget(SPHARMInputModuleHigh)

        if item == "iniCreation":
            self.step+=1
            iniModule = progressFrame()
            manager=iniManager(iniModule)
            iniModule.setProgramManager(manager)
            iniModule.setProgramManagerType("ini")
            iniModule.setStep(self.step)
            iniModule.setParent(self.parent)
            iniModule.setTitle(self.titles[item])
            iniModule.setInstruction(self.instructions[item])
            self.stack.addWidget(iniModule)

        if item == "SPHARMLow":
            self.step+=1
            progressModule = progressFrame()
            manager=slicerSaltManager(progressModule)
            progressModule.setProgramManager(manager)
            progressModule.setStep(self.step)
            progressModule.setParent(self.parent)
            progressModule.setTitle(self.titles[item])
            progressModule.setInstruction(self.instructions[item])
            progressModule.setProgramManagerType("low")
            self.stack.addWidget(progressModule)

        if item == "SPHARMHigh":
            self.step+=1
            progressModule = progressFrame()
            manager=slicerSaltManager(progressModule)
            progressModule.setProgramManager(manager)
            progressModule.setStep(self.step)
            progressModule.setParent(self.parent)
            progressModule.setTitle(self.titles[item])
            progressModule.setInstruction(self.instructions[item])
            progressModule.setProgramManagerType("high")
            self.stack.addWidget(progressModule)
    

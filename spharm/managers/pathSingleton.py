from spharm.managers.singleton import Singleton

class pathSingleton(Singleton):

    def getRelativePath(self, path):
        return(self.rootDirectory + "/spharm/assets/"+path)
        #resourcePath("/spharm/assets/"+path)

    def getRelativeScriptPath(self, path):
        return(self.rootDirectory + "/spharm/externalScripts/"+path)
        #resourcePath("/spharm/externalScripts/"+path)

    #Get the directory that it first opens to when searching for files
    def getRelativeInputStart(self):
        return(self.inputStart)
        #return(resourcePath(""))

    def init(self):
        #print("This is only executed when calling the singleton first time")
        #print("calling init")
        pass

    def setParameters(self, rootDirectory, inputStart):
        self.rootDirectory = rootDirectory
        self.inputStart = inputStart

    def __init__(self):
        #print("This is executed both first and second time")
        #print("calling __init__")
        pass

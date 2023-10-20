#Robert Sharp - Refactored the step so it uses the object variables
# # Michael Thomas 912226 - Wrote original step through process

from errorWindow import ErrorWindow
from procBuilder.singleton import Singleton

MAXSESSIONS = 1000

class windowSingleton(Singleton):

    def stepThroughProcess(self, windowId, nodes):
        """if len(NodeBase.NEXT_NODE_TO_RUN) == 0:
            for node in nodes:
                if node.isDataInputNode:
                    NodeBase.NEXT_NODE_TO_RUN.append(node)
        if len(NodeBase.NEXT_NODE_TO_RUN) > 0:
            NodeBase.PROCESS_ABLE_TO_RUN = True
            NodeBase.NEXT_NODE_TO_RUN[0].update()
            NodeBase.NEXT_NODE_TO_RUN = NodeBase.NEXT_NODE_TO_RUN[1:]"""

        if self.checkNoNodesLeftWindow(windowId):

            allRun = True
            for node in nodes:
                if node.hasRun == False:
                    allRun = False
            if allRun:
                node.errorWindow = ErrorWindow()
                node.errorWindow.setMessageText("Process has finished.")
                return

            for node in nodes:
                if node.isDataInputNode:
                    self.addNextNodeWindow(windowId, node)

        if self.checkHasNodesLeftWindow(windowId):

            hasFoundInterestingRun = False

            while (hasFoundInterestingRun == False) and (self.checkHasNodesLeftWindow(windowId)):

                nodeTarget = self.getNextSingleNodeWindow(windowId)

                self.makeRunableWindow(windowId)

                nodeTarget.update()

                windowSingleton().removeNextSingleNodeWindow(windowId)

                if (nodeTarget.hasRun == True) and (nodeTarget.isInteresting):

                    hasFoundInterestingRun = True

    def getWindowId(self, session):

        if session in self.windowDict:
            return self.windowDict[session]

        self.windowId+=1
        self.windowDict[session] = self.windowId
        return self.windowId

    def canRunSession(self, session):
        return self.PROCESS_ABLE_TO_RUN[self.getWindowId(session)]

    def canRunWindow(self, windowId):
        return self.PROCESS_ABLE_TO_RUN[windowId]

    def isStepSession(self, session):
        return self.PROCESS_STEP_MODE[self.getWindowId(session)]

    def isStepWindow(self, windowId):
        return self.PROCESS_STEP_MODE[windowId]

    def getNextNodesWindow(self, windowId):
        return self.NEXT_NODE_TO_RUN[windowId]

    def getNextSingleNodeWindow(self, windowId):
        return self.NEXT_NODE_TO_RUN[windowId][0]

    def removeNextSingleNodeWindow(self, windowId):
        temp = self.NEXT_NODE_TO_RUN[windowId]
        temp2 = temp[1:]
        self.NEXT_NODE_TO_RUN[windowId] = temp2

    def getNextNodesSession(self, session):
        return self.NEXT_NODE_TO_RUN[self.getWindowId(session)]

    def nodeInNextToRunWindow(self, windowId, node):
        return (node in self.getNextNodesWindow(windowId))

    def checkNoNodesLeftWindow(self, windowId):
        return (len (self.NEXT_NODE_TO_RUN[windowId])==0)

    def checkHasNodesLeftWindow(self, windowId):
        return (len (self.NEXT_NODE_TO_RUN[windowId])>0)

    #Setters
    """def insertNextNodeToRunWindow(self, windowId, node):

        print("inserting")
        print(self.NEXT_NODE_TO_RUN[self.windowId])

        temp = self.NEXT_NODE_TO_RUN[self.windowId]
        temp.insert(1,node)

        self.NEXT_NODE_TO_RUN[self.windowId] = temp

        print(self.NEXT_NODE_TO_RUN[self.windowId])"""

    def startStepModeWindow(self, window):
        self.setStepWindow(window, True)

    def stopStepModeWindow(self, window):
        self.setStepWindow(window, False)

    def makeRunableWindow(self, window):
        self.setRunWindow(window, True)

    def makeUnRunableWindow(self, window):
        self.setRunWindow(window, False)

    def makeRunableSession(self, session):
        self.setRunWindow(self.getWindowId(session), True)

    def makeUnRunableSession(self, session):
        self.setRunWindow(self.getWindowId(session), False)

    def clearNextNodeRunWindow(self, windowId):
        self.setNextNodesWindow(windowId, [])

    def setRunSession(self, session, val):
        self.PROCESS_ABLE_TO_RUN[self.getWindowId(session)] = val

    def setRunWindow(self, windowId, val):
        self.PROCESS_ABLE_TO_RUN[windowId] = val

    def setStepSession(self, session, val):
        self.PROCESS_STEP_MODE[self.getWindowId(session)] = val

    def setStepWindow(self, windowId, val):
        self.PROCESS_STEP_MODE[windowId] = val

    def setNextNodesWindow(self, windowId, nodes):
        self.NEXT_NODE_TO_RUN[windowId] = nodes

    def setNextNodesSession(self, session, nodes):
        self.NEXT_NODE_TO_RUN[self.getWindowId(session)] = nodes

    #This appends, adds only one node
    def addNextNodeWindow(self, windowId, node):
        temp = self.NEXT_NODE_TO_RUN[windowId]
        temp.append(node)
        self.NEXT_NODE_TO_RUN[windowId] = temp

    def addNextNodeSession(self, session, node):
        self.NEXT_NODE_TO_RUN[self.getWindowId(session)].append(node)

    def init(self):
        ##print("This is only executed when calling the singleton first time")
        ##print("calling init")
        self.windowId=0
        self.windowDict = {}
        self.PROCESS_ABLE_TO_RUN = [[] for i in range(MAXSESSIONS)]
        self.PROCESS_STEP_MODE = [[] for i in range(MAXSESSIONS)]
        self.NEXT_NODE_TO_RUN = [[] for i in range(MAXSESSIONS)]

        #Set the dimensions of nodebase
        for index in range(MAXSESSIONS):
            self.PROCESS_ABLE_TO_RUN[index] = False
            self.PROCESS_STEP_MODE[index] = False
            self.NEXT_NODE_TO_RUN[index] = []

    def __init__(self):
        ##print("This is executed both first and second time")
        ##print("calling __init__")
        pass
import time
from time import sleep


class TimeManager():

    def __init__(self):
        self.times = []

    def calculateAverage(self, timeList):

        return sum(timeList)/len(timeList)

    def calculateTimeDifference(self, startTime, endTime):

        return endTime - startTime

    def setTasks(self, tasks):
        self.tasksRemaining = tasks

    def start(self):

        self.lastTime = time.time()

    def estimateTimeToComplete(self):

        return self.tasksRemaining * self.calculateAverage(self.times)

    def taskFinished(self):

        self.tasksRemaining -=1

        self.newTime = time.time()

        self.times.append(self.calculateTimeDifference(self.lastTime, self.newTime))

        self.lastTime = self.newTime

    def getEstimateHMS(self):

        secTotalTime = self.estimateTimeToComplete()

        hourTime = secTotalTime // 3600

        secTotalTime = secTotalTime - (hourTime * 3600)

        minTime = secTotalTime // 60

        secTime = secTotalTime - (minTime * 60)

        return round(hourTime), round(minTime), round(secTime)

"""print("Hello World")

timeManager = TimeManager()

timeManager.setTasks(300)
timeManager.start()

sleep(1)

timeManager.taskFinished()


print(timeManager.estimateTimeToComplete())

hourTime, minTime, secTime = timeManager.getEstimateHMS()

print("Estimated time remaining is {} hours, {} mins and {} seconds".format(hourTime, minTime, secTime))

sleep(2)


timeManager.taskFinished()

print(timeManager.estimateTimeToComplete())
hourTime, minTime, secTime = timeManager.getEstimateHMS()

print("Estimated time remaining is {} hours, {} mins and {} seconds".format(hourTime, minTime, secTime))

sleep(3)
timeManager.taskFinished()

print(timeManager.estimateTimeToComplete())
hourTime, minTime, secTime = timeManager.getEstimateHMS()

print("Estimated time remaining is {} hours, {} mins and {} seconds".format(hourTime, minTime, secTime))"""
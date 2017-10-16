import os
from .common import DictClass, getDirAndFileName
from .settings_loader import DataSettings
from .data import loadData, saveData


class SimulationChainData:
    def __init__(self, generalSettings, simulationChain):
        self._gs = gs = generalSettings
        self._simulationsData = []
        self._results = {}

        for singleSimParams in simulationChain:
            dataDir, dataFileName = getDirAndFileName(singleSimParams.data)
            ds = DataSettings(dataDir + '/' + gs.dataSettings)
            df = DictClass(loadData(singleSimParams.data + gs.dataExt))
            singleSimParams.update(dict(dataSettings=ds, train=df.train))
            self._simulationsData.append(singleSimParams)

    def getSimulationsData(self):
        return self._simulationsData

    def addResult(self, dataName, result):
        self._results[dataName] = result

    def getResult(self, dataName):
        # first search cash, then file
        r = self._results.get(dataName, None)
        if r:
            print("Results fatched from cache")
            return r

        r = loadData(dataName + self._gs.dataExt)
        if r:
            print("Results fatched from file: ", dataName)
            return r

        assert r, "No init data or file found! %s" % (dataName)

    def saveResults(self):
        gs = self._gs
        for dataPath, result in self._results.items():
            rfile = dataPath + gs.resultsExt
            print(rfile)
            saveData(rfile, **result)


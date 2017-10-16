from .network import Network, findPool
from .data import assertNoLearning
from . import plot

def simulate(generalSettings, simulationSettings, modelSettings, simulationChainData, save=True):
    gs = generalSettings
    ss = simulationSettings
    ms = modelSettings
    scd = simulationChainData

    for i, simData in enumerate(scd.getSimulationsData()):
        print("SIMULATION", i)

        # set number of input neurons based on nChannels in patterns
        findPool(ms.pools, "in")['N'] = simData.dataSettings.nChannels
        findPool(ms.pools, "in_")['N'] = simData.dataSettings.nChannels

        net = Network(ss, ms)
        net.simulate(0., simData.train.spikes)

        if simData.init:
            r = scd.getResult(simData.init)
            if r:
                print("Network initialized based on: ", simData.init)
                W = r["finalW"]
                net.setWeights('in', 'e', W)

        initW = net.getShapedWeights('in','e')
        net.setLearning(simData.learning, 'in', 'e')
        if simData.learning and ss.showLearningProgress:
            for i in range(10):
                net.simulate(simData.simTime / 10., None, reset=False)
                W = net.getShapedWeights('in','e')
                plot.showWeights(simData.dataSettings.patternShape, W)
        else:
            net.simulate(simData.simTime, None, reset=False)

        finalW = net.getShapedWeights('in','e')
        assertNoLearning(initW, finalW, simData.learning)
        scd.addResult(simData.result, dict(initW=initW, finalW=finalW,  spikes=net.getAllSpikes()))
    if save:
        scd.saveResults()


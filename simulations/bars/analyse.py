import numpy as np
from eim.settings_loader import GeneralSettings, SimulationSettings, NetworkModelSettings, DataSettings
from eim.common import DictClass
from eim.data import loadData, saveData
from eim.analysis import getActiveNeurons, getSpecializedNeurons, groupNeuronsBySpecialization, mapNeuronToPattern, numberOfSpikesInTrain
from eim.measures import spikePrecisionMeasure, spikeF1Measure
from eim.spike_train import train_sec2ms


##########    ANALYSE DATA SETTINGS    ##########
minTopPrecision = 0.8
maxSecondPrecision = 0.7
#################################################

##########          LOAD DATA          ##########
trr = DictClass(loadData('results/training.shelf'))
ter = DictClass(loadData('results/testing.shelf'))
ted = DictClass(loadData('data/testing.shelf'))
#################################################

print('trr', trr.__dict__.keys())
print('trr', trr.__dict__['spikes'].keys())

# LOAD SETTINGS
gs = GeneralSettings()
ss = SimulationSettings(gs.simulationSettings)
ms = NetworkModelSettings(gs, ss.model, ss.modelAdditionalParams)
ds = DataSettings(gs.dataPath + gs.dataSettings)

# PREPARE
spikesEtest_ms = train_sec2ms(ter.spikes['e'])
#testsimtime_ms = int(ter.simTime * 1000)
testsimtime_ms = int(ted.length * 1000)
tau_steps = int(np.ceil(ms.settings.REFRACTORY_E/1000. / ss.dt))
pd = ted.train.pd
patlen = ted.train.patlen

# ANALYSIS: calculate group F1
precision = spikePrecisionMeasure(pd, patlen, spikesEtest_ms, testsimtime_ms, tau_steps) 
active_neurons = getActiveNeurons(spikesEtest_ms, minSpikes=2)
spec, nonspec = getSpecializedNeurons(precision, minTopPrecision, maxSecondPrecision, active_neurons)
n2p = mapNeuronToPattern(precision, ds.patternIDs, thresh=minTopPrecision)
groups = groupNeuronsBySpecialization(n2p, spec, precision)
F1, _, _, _, _, _ = spikeF1Measure(pd, patlen, spikesEtest_ms, testsimtime_ms, tau_steps, groups)

# INFO
print("# active neurons = ", len(active_neurons))
print("# specialized neurons = ", len(spec))
print("# non-specialized neurons = ", len(nonspec))
print("Groups of neurons = ", groups)
print("# of groups = ", len(groups.keys()))
print("F1 = ", F1)
print("#spikes Z", numberOfSpikesInTrain(trr.spikes['e']))
print("#spikes I", numberOfSpikesInTrain(trr.spikes['i']))
# SAVE
saveData('results/analysis.shelf', 
         w=trr.finalW, precision=precision, F1=F1, active_neurons=active_neurons, groups=groups,
         specialized_neurons=spec, nonspecialized_neurons=nonspec)


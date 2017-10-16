from eim.settings_loader import GeneralSettings, DataSettings
from eim.data import saveData
from eim.spike_train import createSpikeTrainFromPatterns

gs = GeneralSettings()
ds = DataSettings(gs.dataPath + gs.dataSettings)

# dataSet: training
length = 400.  # sec
train, pg = createSpikeTrainFromPatterns(ds, length, patternSeed=7)
train.patterns = None  # remove due to heavy memory consumption, as well as pg
saveData(gs.dataPath + "training" + gs.dataExt, 
         patternShape=ds.patternShape, nPatterns=ds.nPatterns, nChannels=ds.nChannels, train=train, length=length)
	  

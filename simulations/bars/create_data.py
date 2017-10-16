from eim.settings_loader import GeneralSettings, DataSettings
from eim.data import saveData
from eim.spike_train import createSpikeTrainFromPatterns

gs = GeneralSettings()
ds = DataSettings(gs.dataPath + gs.dataSettings)

# dataSet: training
length = 400.  # sec
train, pg = createSpikeTrainFromPatterns(ds, length, patternSeed=6868348)
saveData(gs.dataPath + "training" + gs.dataExt,
         patternShape=ds.patternShape, nPatterns=ds.nPatterns, nChannels=ds.nChannels, pg=pg, train=train, length=length)

# dataSet: testing
length = 200.  # sec
train, pg = createSpikeTrainFromPatterns(ds, length, patternSeed=42)
saveData(gs.dataPath + "testing" + gs.dataExt,
         patternShape=ds.patternShape, nPatterns=ds.nPatterns, nChannels=ds.nChannels, pg=pg, train=train, length=length)


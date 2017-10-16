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
train, pg = createSpikeTrainFromPatterns(ds, length, patternSeed=6868348, pdSeed=3451734)
saveData(gs.dataPath + "testing" + gs.dataExt, 
		 patternShape=ds.patternShape, nPatterns=ds.nPatterns, nChannels=ds.nChannels, pg=pg, train=train, length=length)
	
# dataSet: testing short run - manual pattern distribution (pd)
length = 2.5  # sec
pd={1: [100, 580, 1010, 1400, 1737, 2060],
	2: [120, 520,  690, 1090, 1565, 2235]}
train, pg = createSpikeTrainFromPatterns(ds, length, pd=pd, patternSeed=6868348, pdSeed=3451734)
saveData(gs.dataPath + "testing_short" + gs.dataExt, 
		 patternShape=ds.patternShape, nPatterns=ds.nPatterns, nChannels=ds.nChannels, pg=pg, train=train, length=length)
		 
# dataSet: testing single spatio-temporal patterns
length = 200.  # sec
ds.maxOverlappingPatterns = 1
ds.mixingDistribution = [0.5]
train, pg = createSpikeTrainFromPatterns(ds, length, patternSeed=6868348, pdSeed=3451734)
saveData(gs.dataPath + "testing_singles" + gs.dataExt, 
		 patternShape=ds.patternShape, nPatterns=ds.nPatterns, nChannels=ds.nChannels, pg=pg, train=train, length=length)
		 

	  
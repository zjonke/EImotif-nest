from eim.settings_loader import GeneralSettings, DataSettings
from eim.data import loadData
from eim.common import DictClass
from eim.plot import showWeights

gs = GeneralSettings()
ds = DataSettings(gs.dataPath + gs.dataSettings)
trr = DictClass(loadData('results/training.shelf'))

showWeights(ds.patternShape, trr.initW)
showWeights(ds.patternShape, trr.finalW)


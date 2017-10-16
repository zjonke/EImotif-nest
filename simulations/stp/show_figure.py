from eim.settings_loader import GeneralSettings, DataSettings
from eim.common import DictClass
from eim.data import loadData
from eim.spike_train import train_sec2ms
from figure_helper import plotSTPFig
import matplotlib.pyplot as plt


##########      PLOTTING SETTINGS      ##########
train_start_time_ms = 0
train_end_time_ms = 2500
max_nrns_to_plot = 200
#################################################

##########          LOAD DATA          ##########
ter = DictClass(loadData('results/testing_short.shelf'))
ted = DictClass(loadData('data/testing_short.shelf'))
anr = DictClass(loadData('results/analysis.shelf'))
#################################################

# LOAD SETTINGS
gs = GeneralSettings()
ds = DataSettings(gs.dataPath + gs.dataSettings)

# PREPARE
IDs = ds.patternIDs
train = ted.train
pd = train.pd
patlen = train.patlen
pc = [(0.0, 0.3, 1.0), (0.0, 0.8, 0.0)]

# input neurons spikes
spikesIN_ms = train_sec2ms(ter.spikes['in'])[::2]  # take every 2nd

# excitatory neurons spikes
spikesE_ms = train_sec2ms(ter.spikes['e'])
# pattern prefered neurons - spikes
P1_spikesE_ms = [spikesE_ms[i] for i in anr.nrns_inds_P1]
P2_spikesE_ms = [spikesE_ms[i] for i in anr.nrns_inds_P2]
#non prefered neurons - subset
rest_spikesE_ms = [spikesE_ms[i] for i in anr.nrns_nondist][:max_nrns_to_plot - len(P1_spikesE_ms)-len(P2_spikesE_ms)]

# inhibitory neurons spikes
spikesI_ms = train_sec2ms(ter.spikes['i'])[::2]  # take every 2nd


# PLOT FIGURE
plotSTPFig(train, pd, patlen, ted.pg, 
		   train_start_time_ms, train_end_time_ms, IDs, pc, 
		   spikesIN_ms, P1_spikesE_ms, P2_spikesE_ms, rest_spikesE_ms, spikesI_ms, 
		   anr.nrntracesP1_P1, anr.nrntracesP1_P2, anr.nrntracesP2_P1, anr.nrntracesP2_P2)

# SAVE FIGURE
plt.savefig('plots/fig.png', dpi=600)
plt.savefig('plots/fig.eps')

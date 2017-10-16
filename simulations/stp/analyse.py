import numpy as np
import numpy.matlib as nm
from scipy import stats

from eim.settings_loader import GeneralSettings, SimulationSettings
from eim.common import DictClass
from eim.data import loadData, saveData
from eim.analysis import getActiveNeurons, convolveEventLists, meanTraceValues, sortTracesByPeakInTime, calculateMeanNormalizedTraces
from eim.spike_train import train_sec2ms
from eim.psp import createPSPShape


##########    ANALYSE DATA SETTINGS    ##########
patLen = 150  # both patterns are 150ms long
#################################################

##########          LOAD DATA          ##########
ter = DictClass(loadData('results/testing_singles.shelf'))
ted = DictClass(loadData('data/testing_singles.shelf'))
#################################################

# LOAD SETTINGS
gs = GeneralSettings()
ss = SimulationSettings(gs.simulationSettings)
	
# PREPARE
spikesE = ter.spikes['e']
testpd = ted.train.pd
simtime = ted.length
dt= ss.dt

numexc = len(spikesE)  # trebalo bi bit valjda
simtime_ms = int(simtime * 1000)
spikesE_ms = train_sec2ms(spikesE)


# PATTERNS TRACES
p_psp = createPSPShape({'shape': "rectangular", 'maxvalue': 1., 'duration': 150e-3}, dt)
p_traces = convolveEventLists([testpd[1], testpd[2]], simtime_ms, p_psp)


# SPIKES TRECES
psp = createPSPShape({'shape': "doubleexp", 'maxvalue': 1., 'trise': 1e-3, 'tfall': 20e-3, 'duration': 200e-3}, dt)
traces = convolveEventLists(spikesE_ms, simtime_ms, psp)


# ACTIVE NEURONS (if it has at least 2 spikes)
active_neurons = getActiveNeurons(spikesE_ms, minSpikes=2)
print("Number of active neurons=", len(active_neurons))


# PATTERN MODULATED NEURONS (if the activity of neuron is 2*higher during patterns presentation [0:150+15ms] then otherwise)
patON = np.logical_or(p_traces[0, :], p_traces[1, :])
patOFF = 1 - patON
patONsum, patOFFsum = patON.sum(), patOFF.sum()
assert patON.sum() > 0 and patOFF.sum() > 0

nrns_modulated = [i for i in range(numexc) if (traces[i, :] * patON).sum() * patOFFsum > 2 * (traces[i, :] * patOFF).sum() * patONsum]
print("Number of pattern modulated neurons =", len(nrns_modulated))
nrns_notmodulated = list(set(range(numexc)) - set(nrns_modulated))
print("Number of pattern non-modulated neurons =", len(nrns_notmodulated))


# DISTINGUISHING NEURONS (if traces for P1 or P2 are significanly different, p<0.05)

# traces for P1
piaP1 = nm.repmat(p_traces[0], numexc, 1)
itP1 = piaP1[0, :].nonzero()[0]
tracesP1 = piaP1 * traces

# traces for P2
piaP2 = nm.repmat(p_traces[1], numexc, 1)
itP2 = piaP2[0, :].nonzero()[0]
tracesP2 = piaP2 * traces


nrns_nondist = list(nrns_notmodulated)
nrns_dist=[]
nrns_P1=[]
nrns_P2=[]

# for each neuron compare traces for P1 and P2 trials
for i in nrns_modulated:
	# calculate mean trace over each trial
	mtP1 = meanTraceValues(itP1, tracesP1[i, :])
	mtP2 = meanTraceValues(itP2, tracesP2[i, :])

	# optimization: look only at non zero mean trace values - at least 1 spike per pattern
	mtP1 = mtP1[mtP1.nonzero()[0]]	
	mtP2 = mtP2[mtP2.nonzero()[0]]
	
	# take in consideration same number of trials
	if len(mtP1) < len(mtP2):		
		mtP2 = mtP2[:len(mtP1)]
	else:
		mtP1 = mtP1[:len(mtP2)]

	# calculate T-test: two sided test for hypothesis that mean trace values have identical average values
	p = stats.ttest_rel(mtP1, mtP2)
	print(i, p[1], len(mtP1), len(mtP2))
	
	if p[1] < 0.05:  # then samples are likely NOT drawn from the same distribution and the cell are distinguishing
		nrns_dist.append(i)
		# decide if neuron is P1 or P2 distinguishing
		if mtP2.mean() > mtP1.mean():
			nrns_P2.append(i)
		else:
			nrns_P1.append(i)
	else:
		nrns_nondist.append(i)

nrns_nondist = sorted(nrns_nondist)  # order nrn indecies

print("Number of non pattern distinguishing neurons = ", len(nrns_nondist))
print("Number of pattern distinguishing neurons = ", len(nrns_dist))
print("Number of pattern 1 distinguishing neurons = ", len(nrns_P1))
print("Number of pattern 2 distinguishing neurons = ", len(nrns_P2))


# AVERAGE NEURON ACTIVITY (for selective neurons (P1 or P2) calculate average activity during the pattern)

# neurons prefering P1 ordered by peak activity in time
nrntracesP1_P1, nrntracesP1_P2 = calculateMeanNormalizedTraces(nrns_P1, traces, testpd, simtime_ms, patLen)	
inds, nrntracesP1_P1 = sortTracesByPeakInTime(nrntracesP1_P1)
_, nrntracesP1_P2 = sortTracesByPeakInTime(nrntracesP1_P2)
nrns_inds_P1 = [nrns_P1[i] for i in inds][::-1]

# neurons prefering P2 ordered by peak activity in time
nrntracesP2_P1, nrntracesP2_P2 = calculateMeanNormalizedTraces(nrns_P2, traces, testpd, simtime_ms, patLen)	
_, nrntracesP2_P1 = sortTracesByPeakInTime(nrntracesP2_P1)
inds, nrntracesP2_P2 = sortTracesByPeakInTime(nrntracesP2_P2)
nrns_inds_P2 = [nrns_P2[i] for i in inds][::-1]


# SAVE
saveData('results/analysis.shelf', 
		 nrns_inds_P1=nrns_inds_P1, nrns_inds_P2=nrns_inds_P2, nrns_nondist=nrns_nondist,
		 nrntracesP1_P1=nrntracesP1_P1, nrntracesP1_P2=nrntracesP1_P2, nrntracesP2_P1=nrntracesP2_P1, nrntracesP2_P2=nrntracesP2_P2)

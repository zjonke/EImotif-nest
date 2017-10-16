import numpy as np
import scipy.signal as ss


def numberOfSpikesInTrain(spikeTrain):
    s=0
    for i in range(len(spikeTrain)):
        s += len(spikeTrain[i])
    return s


def getActiveNeurons(spikeTrain, minSpikes):
    activeNeurons=[]
    for i, ch in enumerate(spikeTrain):
        if len(ch) >= minSpikes:
            activeNeurons.append(i)
    return activeNeurons

def getSpecializedNeurons(precisionTable, minTopPrecision, maxSecondTopPrecision, activeNeurons):
    numNeurons = len(precisionTable)
    specializedNeurons = []
    nonspecializedNeurons = []
    for i in range(numNeurons):
        top2 = sorted(precisionTable[i, :])[-2:][::-1]
        if len(top2) == 1:
            top2.append(-1)  # add fake data in order to ignore maxSecondTopPrecision
        if i in activeNeurons:
            if top2[0] > minTopPrecision and top2[1] < maxSecondTopPrecision:
                specializedNeurons.append(i)
            else:
                nonspecializedNeurons.append(i)
    return specializedNeurons, nonspecializedNeurons

def mapNeuronToPattern(precisionTable, patternsID, thresh=0.3):
    prn = []
    for i in range(precisionTable.shape[0]):
        maxind = precisionTable[i].argmax()
        value = precisionTable[i][maxind]
        if value > thresh:
            prn.append([int(patternsID[maxind]), value])
        else:
            prn.append([int(-patternsID[maxind]), value])
    return prn


def groupNeuronsBySpecialization(prn, specializedNeurons, precisionTable):
    groups = {}

    for i, el in enumerate(prn):
        if i in specializedNeurons:
            groups.setdefault(el[0], []).append(i)

    for k in groups.keys():
        a = precisionTable[groups[k]].max(1)
        groups[k] = [y for (x, y) in sorted(zip(a, groups[k]), reverse=True)]

    return groups


def convolveEventLists(eventLists, simtime_ms, psp):
    # lists = [[list of events], ]
    nLists = len(eventLists)
    traces = np.zeros([nLists, simtime_ms + psp.shape[0] - 1])
    for i in range(nLists):
        traces[i, eventLists[i]] = 1.  # pd is 1-indexed
        traces[i, :] = np.convolve(traces[i, :-psp.shape[0] + 1], psp, 'full')
    # cut off psp ending
    traces = traces[:,:simtime_ms]
    return traces

def meanTraceValues(patInds, traces):
    mt = []
    m, n = 0, 0
    for j in range(len(patInds)):
        m += traces[patInds[j]]
        n += 1
        if j == len(patInds) - 1 or patInds[j + 1] - patInds[j] != 1:  # same trace
            mt.append(m / float(n))
            m, n = 0, 0
    return np.array(mt)


def sortTracesByPeakInTime(nrntraces):
    peaks=nrntraces.argmax(1)
    inds = [i[0] for i in sorted(enumerate(peaks), key=lambda x:x[1])]
    return inds, nrntraces[inds, :] 


def meanTrace(eventList, simtime_ms, trace, patLen):
    traces = np.zeros((len(eventList), patLen))
    for j, t in enumerate(eventList):
        traces[j, 0: min(patLen, simtime_ms - t)] = trace[t: t + min(patLen, simtime_ms - t)]

    avtrace = traces.mean(0)
    return avtrace


def calculateMeanNormalizedTraces(nrns, traces, pd, simtime_ms, patLen):
    nrntraces_P1 = np.zeros((len(nrns), patLen))
    nrntraces_P2 = np.zeros((len(nrns), patLen))
		
    for i, nid in enumerate(nrns):
        avtrace1 = meanTrace(pd[1], simtime_ms, traces[nid], patLen)
        avtrace2 = meanTrace(pd[2], simtime_ms, traces[nid], patLen)

        #normalize
        norm = max(avtrace1.max(), avtrace2.max())
        if norm > 0:
            avtrace1 /= norm
            avtrace2 /= norm

        nrntraces_P1[i, :] = avtrace1
        nrntraces_P2[i, :] = avtrace2

    return nrntraces_P1, nrntraces_P2


def calcRate(spikes,stime,dt,win):
    stime_steps=int(np.ceil(stime/dt))
    r=np.zeros(stime_steps)

    allsp=[s for ch in spikes for s in ch]
    allsp.sort()

    window_steps=int(np.ceil(win/dt))

    for sp in allsp:
        step=int(np.ceil(sp/dt))
        r[step:step+window_steps]+=1

    return r, len(allsp)


def calculateCorrelation(r1, r2, start, npts):
    a = r1[start: start + npts]                         # take segement of interest
    b = r2[start: start + npts]						

    a = (a - np.mean(a)) / (np.std(a) * len(a))         # remove mean and normalize
    b = (b - np.mean(b)) / (np.std(b) * len(b))

    c = ss.correlate(a, b)                              # calc correlation
    n = len(c)
    c_norm = c / max(c)                                 # normalize correlation
    dur = n / 2                                         # offset (shift)
    d = np.linspace(-dur, dur, n)                       # shift time points
    return c_norm, d, dur


def countSpikesForNonoverlappingPatterns(spikes_ms, pd, patlen):
    # flatten all patterns - they are not overlaping
    allp = []
    for k in pd.keys():
        for t in pd[k]:
            allp.append([k, t])
    #sort it
    sallp = sorted(allp, key=lambda a: a[1])

    npatterns = len(pd.keys())
    nneurons = len(spikes_ms)

    response = np.zeros((nneurons, npatterns))

    maxcp = len(sallp)
    if maxcp == 0:
        return response
		
    for nid in range(nneurons): # for each neuron
        cp = 0  # current pattern pointer
		
        cpID = sallp[cp][0]  # current pattern ID
        cps = sallp[cp][1] # current pattern start
        for sp in spikes_ms[nid]: # for each spike of neuron find during which pattern it spiked
            if sp >= cps:  # optimization, skip patterns that appearer before
                while cp < maxcp-1 and sp > cps + patlen[cpID]:  # start of pattern + pattern duration
                    cp += 1
                    cpID = sallp[cp][0]  # current pattern ID
                    cps = sallp[cp][1]  # current pattern start
                if cp < maxcp - 1 and sp <= cps + patlen[cpID]:  # if it is this pattern
                    response[nid, cpID - 1] += 1  # IDs are 1-indexed
    return response


import numpy as np


def spikeF1Measure(pd, patlen, output, duration, Nout, groups):
    """
        Calculate F1 measure between neurons group activity and corresponding patterns

        Precision:
            TP - +1 if there was at least 1 spike in neurons groups during pattern+Nout time
            FP - +1 if there was no 1 spike in neurons groups during pattern+Nout time outside of pattern activity
            pr=TP/(Tp+FP)
        Recall:
            FN - +1 if there was no 1 spike in neurons groups during pattern+Nout time 
            re=TP/(Tp+FN)
       F1:
            F1=2*pr*re/(pr+re)
    """

    npatterns = len(pd.keys())
    patternstate = np.zeros((npatterns, duration), dtype='bool')

    for ind, ID in enumerate(pd.keys()):
        for t in pd[ID]:
            patternlength = patlen[ID]
            start = min(t, duration - 1)
            length = min(patternlength + Nout, duration - t)
            patternstate[ind, start: t + length] = True

    ngroups = len(groups.keys())
    #include also non-existing groups (if a pattern was not learned)
    groupstate = np.zeros((npatterns, duration), dtype='bool')

    assert ngroups <= npatterns

    # all spikes per groups
    for ind, ID in enumerate(groups.keys()):
        for neuron in groups[ID]:
            for sp in output[neuron]:
                if sp < duration:
                    groupstate[ID - 1, sp] = True

    #calc FP and FN
    TP = np.zeros((npatterns))
    FN = np.zeros((npatterns))

    for ind, ID in enumerate(pd.keys()):
        for t in pd[ID]:
            patternlength = patlen[ID]
            start = min(t, duration - 1)
            length = min(patternlength + Nout, duration - t)
            a = groupstate[ind, start: t + length].sum() > 0
            TP[ind] += a
            FN[ind] += (1 - a)

    #calc recall
    re=np.zeros((npatterns))
    for i in range(npatterns):
        if TP[i] > 0 and FN[i] > 0:
            re[i] = TP[i] / (TP[i] + FN[i])

    #calc FP
    FP = np.zeros((npatterns))

    end = 0
    for ind, ID in enumerate(pd.keys()):
        for t in pd[ID]:
            if t < duration:
                patternlength = patlen[ID]
                start = min(t, duration - 1)
                length = min(patternlength + Nout, duration - t)
                #check the time between last end and this start
                #use the same timestep=length to check for false postive = if there was no pattern but group spiked
                tt = end
                while tt < start:
                    lengthTT = min(length, start - tt)
                    a = groupstate[ind, tt: tt + lengthTT].sum() > 0
                    FP[ind] += a
                    tt += length
                #set
                end = start + length

    #calc precision
    #pr = TP/(TP+FP)
    pr = np.zeros((npatterns))
    for i in range(npatterns):
        if TP[i] > 0 and FP[i] > 0:
            pr[i] = TP[i] / (TP[i] + FP[i])

    #calc F1
    #F1=2*pr*re/(pr+re)
    F1 = np.zeros((npatterns))
    for i in range(npatterns):
        if pr[i] > 0 and re[i] > 0:
            F1[i] = 2 * pr[i] * re[i] / (pr[i] + re[i])

    return F1, pr, re, TP, FP, FN


def spikePrecisionMeasure(pd, patlen, output, duration, Nout):
    npatterns = len(pd.keys())
    patternstate = np.zeros((npatterns, duration), dtype='bool')

    for ind, ID in enumerate(pd.keys()):
        for t in pd[ID]:
            if t < duration:
                patternlength = patlen[ID]
                start = min(t, duration - 1)
                length = min(patternlength + Nout, duration - t)
                patternstate[ind, start: t + length] = True

    numhid = len(output)
    TP = np.zeros((numhid, npatterns))
    FP = np.zeros((numhid, npatterns))

    # count TPs and FNs
    for i, ch in enumerate(output):
        for sp in ch:
            if sp < duration:
                TP[i, :] += patternstate[:, sp]
                FP[i, :] += (1 - patternstate[:, sp])

    #calc precision
    pr = TP / (TP + FP)
    return pr

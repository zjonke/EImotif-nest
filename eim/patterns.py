import numpy as np


def topattern(pd, patlen, patternlength):
    m=np.zeros((len(pd), patternlength))
    for i, ID in enumerate(pd.keys()):
        starts = pd[ID]
        length = patlen[ID]
        for t in starts:
            start = min(t, patternlength)
            le = min(length, patternlength - t)
            m[i, start: t + le] = 1
    return m


class PatternManager:
    """
    PatternManager is a container of different patterns, in charge of creating sequence of overlapping unsync patterns in time.
    The distribution of overlapping patterns that PatternManager creates is determined by mixing probabilities.
    If mixing probabilities has k elements, then each element represents probability that one of N available patterns in PatternManager (each with some possibly different lenght in time) is presented in the input.

    E.g. for some simulation time T and a mixing probability [0.9, 0.8, 0.7] PatternManager creates distribution of patterns in time such that:
        - there are at most 3 different patterns in the input at any given time (non-sync)
        - probability that there is no pattern present in the input is (1 - 0.9) * (1 - 0.8) * (1 - 0.7)
        - probability that some 3 (out of N) of patterns are present at the same time is 0.9 * 0.8 * 0.7
        - probability that there is exactly 1 pattern present is: 
            0.9 * (1 - 0.8) * (1 - 0.7) + (1 - 0.9) * 0.8 * (1 - 0.7) + (1 - 0.9) * (1 - 0.8) * 0.7
        - etc
    """
    def __init__(self, dt):
        self.dt = dt
        self.patterns = {}
        self.npatterns = 0
        self.patlen = {}

    def addPatterns(self, patterns, IDs):
        """
        Add patterns with IDs
        Patterns should be a list or an 2d array (nchannels x pattern_length)
        """
        for ind, p in enumerate(patterns):
            ID = IDs[ind]
            if ID not in self.patterns.keys():
                self.patterns[ID] = p
                self.patlen[ID] = p.shape[1]
                self.npatterns += 1

    def getPatternsIDs(self):
        return self.patterns.keys()
	
    # onoff: periods of patterns on and patterns off -> when they are shown and when they are not
    #		first param gives a range for patters on [0.5, 0.7] means patterns are on for random time between 0.5 and 0.7s
    #		second param gives a range for patters off [0.3, 0.5] means patterns are on for random time between 0.3 and 0.5s
    def createUnsyncPatterns(self, simulationtime, IDs, mixingprob, onoff, offset=0):
        onoff_isRange_on = isinstance(onoff[0], list)
        onoff_isRange_off = isinstance(onoff[1], list)
        assert not (onoff_isRange_on ^ onoff_isRange_off)

        # onofftimes: array with 0(no patterns) and 1(patterns are on)
        # simulationtime : sec
        simulationtimeTS = int(np.ceil(simulationtime / self.dt))  # sim time in timesteps

        onoffTS = np.array(np.ceil(np.array(onoff) / self.dt), dtype=int)  # sim time in timesteps

        #create onofftimes
        onofftimes=np.zeros(simulationtimeTS)
		
        t = 0
        onoroff = 0  #0 is on, 1 is off
        while t < simulationtimeTS:
            #duration of on/off time
            if onoff_isRange_on:
                minOnOffTime = onoff[onoroff][0]
                maxOnOffTime = onoff[onoroff][1]
                onofftime = minOnOffTime + np.random.rand() * (maxOnOffTime - minOnOffTime)
            else:
                onofftime = onoff[onoroff]
            steps=np.array(np.ceil(np.array(onofftime) / self.dt), dtype=int)
            steps = min(steps, simulationtimeTS - t)
            onofftimes[t: t + steps] = 1 - onoroff
            t += steps
            onoroff = 1 - onoroff

        # check weather all IDs exists
        pIDs = []
        patlen = []
        for ID in IDs:
            if ID in self.patterns.keys():
                pIDs.append(ID)
                patlen.append(self.patlen[ID])

        npatterns = len(pIDs)
        maxnpatterns = len(mixingprob) # max overlap of patterns
        patact = np.zeros((maxnpatterns, simulationtimeTS), dtype = 'int')

        # probability of mixing channels (each can contain any pattern)
        pa = np.array(mixingprob) # active percentage, size is maxnpatterns
        apatlen = sum(patlen) / float(len(patlen)) # average length of pattern
        pa /= (apatlen - pa * (apatlen - 1)) # probability of activating some pattern

        # prepare random numbers
        r = np.random.rand(maxnpatterns, simulationtimeTS)
        # nov generate patterns
        for t in range(simulationtimeTS):
            if onofftimes[t] == 1:  # if pattern time
                for p in range(maxnpatterns):
                    if patact[p, t] == 0: # if we can put new pattern
                        if pa[p] > r[p, t]: 
                            # then chose one of patterns to put, eliminate those that are already active
                            #available patterns are
                            s = list(range(1, npatterns + 1))
                            for pp in patact[:, t]:
                                if pp > 0 and pp in s:
                                    s.remove(pp)
                            rp = s[np.random.random_integers(0, len(s) - 1)] # random pattern, 1-based index
                            patact[p, t: t + min(patlen[rp - 1], simulationtimeTS - t)] = rp

        # count how many time combination occured (number of overlapping patterns)
        sp = sum(patact > 0)
        k = np.zeros(maxnpatterns + 1)
        for i in range(maxnpatterns + 1):
            k[i] = sum(sp == i) / float(simulationtimeTS)
        print("Distribution of number of overlapping patterns [ 0 to", maxnpatterns, "]")
        print(k)
        # now create activity of patterns to start times of patterns (conversion of IDs to pIDs!)
        # patterndistribution
        pd = dict()
        for i in range(npatterns):
            pd[pIDs[i]] = []

        for p in range(maxnpatterns):
            t = 0
            while t < simulationtimeTS:
                if patact[p, t] > 0:  # if there is start of pattern
                    ID = pIDs[patact[p, t] - 1]
                    pd[ID] += [t + offset]
                    t += self.patlen[ID]
                else:
                    t += 1

        for k in pd.keys():
            pd[k].sort()

        return pd


class TPattern:
    """
    General (abstract) class for pattern.
    It creates pattern of given length based on given rates.
        mask : pattern rates (array)
        length : length of pattern
    """
	
    def info(self):
        """
        Print some info about pattern (class).
        """
        print("Number of patterns:", self.npatterns)
        print("Number of channels in pattern:", self.nchannels)
        print("Lenght of pattern(sec):", self.length)
        print("Rates:", self.rates)
		
    def createFromRates(self, rates):
        """
        Creates one (poisson) pattern from rates.
            -> rates : array([nchannels, time])
                time == 1 means const rate for channel
        """
        if rates.shape[1] == 1:  # if is const rate
            trates = np.tile(rates, (1, self.lengthTS))
        else:
            trates = rates
        r = np.random.rand(self.nchannels, self.lengthTS) * 1000.
        spikes = []
        bsp = trates > r
        for ch in range(self.nchannels):
            spikes.append(bsp[ch, :].nonzero()[0])
        return [spikes, bsp.sum()]
		
    def limitRates(self, minrate, maxrate):
        """
        Limits rates to some range.
            -> minrate : minimum rate
            -> maxrate : maximum rate
        """
        self.patterns[self.patterns < minrate] = minrate
        self.patterns[self.patterns > maxrate] = maxrate


class BarRatePatterns(TPattern):
    """
    Create rate bar pattern generator.
    It creates internally set of patterns defined with rates : patterns
    and binary masks which defines for each channels whether is it high or low rate : masks
    """
    def __init__(self, patternshape, bars, rates, length,dt):
        """
        Inits class:
            -> patternshape : shape of pattern [width, height]
            -> bars : set of indecies (of bars vertical and horizontal) we want to create as pattern
            -> rates : dictionary with 'low' and 'high' rates
            -> lenght : lenght of pattern in sec
            -> dt : simulation timestep
        """
        self.patternshape = patternshape
        self.rates = rates
        self.length = length
        self.dt = dt

        self.lengthTS = int(np.ceil(self.length / dt))  # length in timesteps

        # create masks of patterns
        self.nchannels = self.patternshape[0] * self.patternshape[1]
        n = len(bars)
        if n == 0:
            n = self.patternshape[0] + self.patternshape[1]
            bars = range(n)
        self.npatterns = len(bars)
        self.masks = np.zeros((n, self.nchannels, self.lengthTS), dtype='byte')
        for ind, i in enumerate(bars):
            pattern = np.zeros(self.patternshape)
            # first vertical bars
            if i >= 0 and i < self.patternshape[1]:
                pattern[:, i] = 1
            elif i >= self.patternshape[1] and i < self.patternshape[1] + self.patternshape[0]:
                pattern[i - self.patternshape[1], :] = 1
            newpattern = pattern.ravel().reshape((self.nchannels, 1))
            self.masks[ind, :, :] = newpattern.repeat(self.lengthTS, 1)

        # each mask  multiply with rates
        HR = rates['high']
        LR = rates['low']
        self.patterns = np.array(self.masks * (HR - LR) + LR, dtype='float')

    def info(self):
        """
        Prints additional info about pattern
        """
        super(BarRatePatterns, self).info()
        print("Name : Bar rate pattern")
        print("Shape of pattern:", self.patternshape)


	
class OrientedBarRatePatterns(TPattern):
    """
    Create rate oriented (rotated) bar pattern generator.
    It creates internally set of patterns defined with rates : patterns
    and binary masks which defines for each channels whether is it high or low rate : masks

    Note:
        It can be seen as a special case of random rate patterns, with constraints 2,1 
        (even weaker due to max overlap all =1 for 2 groups (vertical and horizontal bars) 
        which dont have any overlap!)
    """
    def __init__(self, patternshape, barwidth, angles, rates, length, dt):
        """
        Inits class:
            -> patternshape : shape of pattern [width, height]
            -> angles : set of angles  (starting from vertical bar in clock-wise direction) we want to create as pattern
            -> rates : dictionary with 'low' and 'high' rates
            -> lenght : lenght of pattern in sec
            -> dt : simulation timestep
        """
        self.patternshape = patternshape
        self.barwidth = barwidth
        self.rates = rates
        self.length = length
        self.dt = dt

        self.lengthTS = int(np.ceil(self.length / dt))  # length in timesteps

        # create masks of patterns
        self.nchannels = self.patternshape[0] * self.patternshape[1]
        n = len(angles)
        self.npatterns = n
        self.masks = np.zeros((n, self.nchannels, self.lengthTS), dtype='byte')

        pattern0 = np.zeros(self.patternshape)
        pattern0[:, int(patternshape[1] / 2 - barwidth / 2) : int(patternshape[1] / 2 - barwidth / 2 + barwidth)] = 1

        from scipy import ndimage

        for ind, angle in enumerate(angles):
            # ensure angle is correct
            assert angle >= 0 and angle <= 360
            pattern = (ndimage.rotate(pattern0, angle, reshape=False) > 0.1) * 1.

            newpattern = pattern.ravel().reshape((self.nchannels, 1))
            self.masks[ind, :, :] = newpattern.repeat(self.lengthTS, 1)

        # each mask  multiply with rates
        HR = rates['high']
        LR = rates['low']
        self.patterns = np.array(self.masks * (HR - LR) + LR, dtype='float')

    def info(self):
        """
        Prints additional info about pattern
        """
        print("Name : Rotated bar rate pattern")
        print("Shape of pattern:", self.patternshape)
		
		
class SpatioTemporalPatterns(TPattern):
    """
    Create variable rate random pattern generator.
    It creates internally set of patterns defined with rates in time : time patterns
    (the binary mask is created for compatiblity reasons, it is set to 0)
    """
    def __init__(self, nchannels, npatterns, rates, length, dt, process=None, patternsrates=None):
        """
        Init class
            -> nchannels : (int) number of channels
            -> npatterns : (int) number of different patterns
            -> rates : dictionary defining max and min rates {'low', 'high'}
            -> length : (float) length of pattern in sec
            -> dt : simulation timestep
            -> process: process class which creates rates, it is applied to each pattern and each
                    channel in it for duration length
                    default process is random
                    It requires .Create(length) method
            -> patternsrates : external matrix of rates for each channel through time for each pattern
                        array(npatterns, nchannels, length)
        """
        self.rates = rates
        self.length = length
        self.nchannels = nchannels
        self.npatterns = npatterns
        self.dt = dt

        self.lengthTS = int(np.ceil(self.length / dt))  # length in timesteps

        print(self.lengthTS)
        # create masks for compatiblity reasons
        self.masks = np.zeros((self.npatterns, self.nchannels, self.lengthTS))

        self.patterns = np.zeros((self.npatterns, self.nchannels, self.lengthTS))
        if patternsrates == None:  # if external rates description not provided
            if process == None :  # if no external process is provided
                # process = random
                for n in range(self.npatterns):
                    for ch in range(self.nchannels):
                        rrs = np.random.random_integers(rates['low'], rates['high'], self.lengthTS)
                        self.patterns[n, ch, :] = rrs
            else: # process is defined so use it
                for n in range(self.npatterns):
                    for ch in range(self.nchannels):
                        self.patterns[n, ch, :] = process.create(self.lengthTS)
        else: # external description is provided
            self.patterns = patternsrates

    def info(self):
        """
        Prints additional info about pattern
        """
        super(VariableRatePatterns, self).info()
        print("Name : Variable rate pattern")


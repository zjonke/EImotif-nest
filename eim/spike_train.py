import numpy as np
from . import patterns
from .psp import createPSPShape
from .common import OUProcess

def sigmoid(Value, offset=0., width=1.):
    """
    Sigmoid function
        -> value : (single value or array of floats)
        -> offset : float
        -> width : float
    """
    return 1.0/(1.0 + np.exp(-(Value-offset)/width))


def createSpikeTrainFromPatterns(patternsParams, trainDuration, pd=None, patternSeed=None, pdSeed=None, spikeTrainSeed=None):
    if patternSeed:
        np.random.seed(patternSeed)
    pp = patternsParams
    if pp.patternsClass == "BarRatePatterns":
        pg = patterns.BarRatePatterns(pp.patternShape, pp.barsOn, pp.rates, pp.patternLength, pp.dt)
    elif pp.patternsClass == "OrientedBarRatePatterns":
        pg = patterns.OrientedBarRatePatterns(pp.patternShape, pp.barWidth, pp.angles, pp.rates, pp.patternLength, pp.dt)
    elif pp.patternsClass == "SpatioTemporalPatterns":
        oup = OUProcess(pp.oumean, pp.outheta, pp.ousigma, pp.dt)
        oup.f = lambda x: 1.5 * np.exp(x)
        pg = patterns.SpatioTemporalPatterns(pp.nChannels, pp.nPatterns, pp.rates, pp.patternLength, pp.dt, process=oup)
    else:
        raise ValueError("Unsupported pattern class: " + pp.patternsClass)

    pm = patterns.PatternManager(pp.dt)
    pm.addPatterns(pg.patterns, pp.patternIDs)

    if pd is None:
        if pdSeed:
            np.random.seed(pdSeed)
        pd = pm.createUnsyncPatterns(trainDuration, pp.patternIDs, pp.mixingDistribution, onoff=pp.dataOnOffPeriods)

    if spikeTrainSeed:
        np.random.seed(spikeTrainSeed)
    train = TTrain(pm.patterns, pp.nChannels, pp.dt)
    train.add(0., trainDuration, pd)
    train.combinePatterns(pp.combineRules)

    assert pp.maxOverlappingPatterns == len(pp.mixingDistribution)

    train.addFillNoise(pp.maxOverlappingPatterns, pp.dataFillNoiseRate, False, False)
    train.addInbetweenNoise(pp.dataInbetweenNoiseRate)

    train.createSpikes()

    return train, pg


def train_sec2ms(train):
    """
        Convert all train spikes to ms time (round to int)
    """
    mstrain=[]
    for ch in train:
        channel=[]
        for sp in ch:
            channel.append(int(np.round(sp*1000)))
        mstrain.append(channel)
    return mstrain


class TTrain:
    """
    Class for description of spike train
        -> holds references to all samples, duration of train, number of samples
        -> converts spikes to EPSPs
        -> plots
    """
    def __init__(self, patterns, nchannels, dt):
        """
        Inits class.
        Patterns are dict containing ID and rates for patterns.
        Patterns distribution contains for each pattern activation (start time).
        (overwrite mode is active in case time stamps are too close).
        """
        self.duration = 0 # total duration of train
        self.patterns = patterns
        self.patlen = {}
        self.pd = {}
        # create holder for each pattern
        for ID in self.patterns.keys():
            self.pd[ID] = []
            self.patlen[ID] = self.patterns[ID].shape[1]

        self.dt = dt # simultion time step in ms
        self.nchannels = nchannels
        self.noiseset = False

    def add(self, trainstart, trainlength, patternsdistribution):
        """
        Add patterns
        Patterns are dict containing ID and rates for patterns.
        Patterns distribution contains for each pattern activation (start time).
        (overwrite mode is active in case time stamps are too close).
        PD must be a dict (ID:list).
        Note that start times of patterns in patternsdistribution should be sorted to ensure overwriting!
        """
        self.duration += int(np.ceil(trainlength/self.dt)) # total duration of train in timesteps
        # add for each pattern positions
        for ID in patternsdistribution.keys():
            if ID in self.pd.keys():
                pom=np.array(patternsdistribution[ID])+int(np.ceil(trainstart/self.dt))
                self.pd[ID]+=pom.tolist()
                # sort added patternsdistribution
                self.pd[ID].sort()

    def combinePatterns(self, params = {'function':'linear'}):
        """
        """
        #first create rates array(nchannels x trainlength), sum up all
        # assumption is that all IDs in pd are described in patterns
        self.rates = np.zeros((self.nchannels,self.duration)) 
        for ID in self.pd.keys():
            patrates = self.patterns[ID]
            patlen = patrates.shape[1]
            pd = self.pd[ID]
            for t in pd:
                length = min(patlen,self.duration-t)
                self.rates[:,t:t+length] += patrates[:,:length]

         # by default rates are just summed up (linear function)
         # otherwise combine them nonlinearly
        if params['function'] == 'nonlinear':
            rates = params['rates']
            offset = rates['low'] + rates['high']/2.
            width = rates['high']/2.*1/params['precision']
            self.rates = rates['low']+rates['high']*sigmoid(self.rates, offset, width )

    def addNoise(self, maxrate, constTime = True, constCh = True):
        """
            Should be call before CreateSpikes!
            Add noise of maxrate rate on top over all patterns.
                constTime -> if True noise rate will be const in time,
                             otherwise will be randomly drawn from [0,maxrate]
                constCh -> if True noise rate will be const for all channels,
                             otherwise will be randomly drawn from [0,maxrate]
        """
        if maxrate == 0.:
            return
			
        if self.noiseset == False:
            self.noise = np.zeros((self.nchannels,self.duration)) 
            self.noiseset = True
        
        if constTime == False:
            if constCh == False:
                self.noise+=np.random.rand(self.nchannels,self.duration)*maxrate
            else:
                noise = np.random.rand(self.duration)*maxrate
                for ch in range(self.nchannels):
                    self.noise[ch,:]+= noise
        else:
            if constCh == False:
                noise = np.random.rand(self.nchannels)*maxrate
                for t in range(self.duration):
                    self.noise[:,t]+= noise
            else:
                self.noise[:,:]+= maxrate
              
    def addFillNoise(self, maxpatterns, maxrate, constTime = True, constCh = True):
        """
            Should be call before CreateSpikes!
            Add noise of (maxpatterns-npattern)*maxrate rate on top over all patterns.
                constTime -> if True noise rate will be const in time,
                             otherwise will be randomly drawn from [0,maxrate]
                constCh -> if True noise rate will be const for all channels,
                             otherwise will be randomly drawn from [0,maxrate]
        """
        if maxrate == 0.:
            return
			
        # create array of number of patterns at all points (time)
        npat = np.zeros(self.duration)
        for ID in self.pd.keys():
            patlen = self.patlen[ID]
            pd = self.pd[ID]
            for t in pd:
                length = min(patlen,self.duration-t)
                npat[t:t+length] += 1
        # calculate difference between maxpatterns and number of patterns at given time
        diff = np.maximum(maxpatterns-npat,0)
        # create noise
        noise = np.zeros((self.nchannels,self.duration)) 
        if constTime == False:
            if constCh == False:
                noise=np.random.rand(self.nchannels,self.duration)*maxrate
            else:
                noise = np.random.rand(self.duration)*maxrate
                for ch in range(self.nchannels):
                    noise[ch,:]= noise
        else:
            if constCh == False:
                noise = np.random.rand(self.nchannels)*maxrate
                for t in range(self.duration):
                    noise[:,t]= noise
            else:
                noise[:,:]= maxrate
        # now account for difference in target (max number of patterns) and actual number
        for ch in range(self.nchannels):
            noise[ch]*=diff
        print(noise)
        print(noise.sum() / (self.nchannels * self.duration))
        if self.noiseset == False:
            self.noise = np.zeros((self.nchannels,self.duration)) 
            self.noiseset = True
        # update the noise
        self.noise+=noise

    def addInbetweenNoise(self, noiserate):
        """
            Should be call before CreateSpikes!
            Add noise of (maxpatterns-npattern)*maxrate rate on top over all patterns.
                constTime -> if True noise rate will be const in time,
                             otherwise will be randomly drawn from [0,maxrate]
                constCh -> if True noise rate will be const for all channels,
                             otherwise will be randomly drawn from [0,maxrate]
        """
        if noiserate == 0.:
            return		
        # create array of number of patterns at all points (time)
        npat = np.zeros(self.duration)
        for ID in self.pd.keys():
            patlen = self.patlen[ID]
            pd = self.pd[ID]
            for t in pd:
                length = min(patlen,self.duration-t)
                npat[t:t+length] += 1
        # times when there are no patterns - fill with noise
        diff = (npat==0)*1.
        # create noise
        noise = np.zeros((self.nchannels,self.duration)) 
        noise[:,:]= noiserate

        # now account for difference in target (max number of patterns) and actual number
        for ch in range(self.nchannels):
            noise[ch]*=diff

        if self.noiseset == False:
            self.noise = np.zeros((self.nchannels,self.duration)) 
            self.noiseset = True
        # update the noise
        self.noise+=noise


    def createSpikes(self, freerates = True, inputtau=10e-3):
        """
        Creates (poisson) pattern from rates.
        It is kept inside in self.spikes = [ch1,...chN], chN = [spike1,...,spikeM], spikes times in sec
        Freerate : it frees memory allocated with self.rates (this can be rebuild always).
        """
        r = np.random.rand(self.nchannels, self.duration)/self.dt
        self.spikes = []
        inputtau_ms = int(inputtau/self.dt)
        if self.noiseset == True:
            bsp = self.rates + self.noise>r
        else:
            bsp = self.rates > r

        for ch in range(self.nchannels):
            chlen = len(bsp[ch,:])
            chspikes=bsp[ch,:].nonzero()[0]*self.dt
            self.spikes.append(chspikes)

        if freerates:
            self.rates = None
            if self.noiseset == True:
                self.noise = None

    def convertToEPSP(self, EPSP):
        """
        Convert the spike based samples into EPSP input given the EPSP shape and type
            -> EPSP: array containing EPSP shape (rectangular, plataue, alpha, double exponential ..)
            -> EPSPtype : string ("renewal","additive")
        Notes: No cutting off
        """

        #CreateSpikes and CombinePatterns should be invoked first!
        epsp = createPSPShape(EPSP,self.dt)
        EPSPtype = EPSP['type']
        EPSPduration = len(epsp)

        data = np.zeros((self.nchannels, self.duration))
        # for each channel and each spike in it put prefered epsp shape
        for nch,ch in enumerate(self.spikes):
            for sp in ch:
                epspdur = min(EPSPduration, self.duration-sp)
                if EPSPtype == "renewal":
                    data[nch,sp:sp+epspdur]=np.maximum(data[nch,sp:sp+epspdur],epsp[:epspdur])
                elif EPSPtype == "additive":
                    data[nch,sp:sp+epspdur]+=epsp[:epspdur]
        return data

    def convertToEPSP2(self, EPSP, start, end):
        """
        Convert the spike based samples into EPSP input given the EPSP shape and type
            -> EPSP: array containing EPSP shape (rectangular, plataue, alpha, double exponential ..)
            -> EPSPtype : string ("renewal","additive")
        Notes: No cutting off
        """

        #CreateSpikes and CombinePatterns should be invoked first!
        epsp = createPSPShape(EPSP,self.dt)
        EPSPtype = EPSP['type']
        EPSPduration = len(epsp)

        data = np.zeros((self.nchannels, end-start))
        # for each channel and each spike in it put prefered epsp shape
        for nch,ch in enumerate(self.spikes):
            for sp in ch:
                sp_ms=int(sp*1000)
                if sp_ms>=start and sp_ms<end:
                    epspdur = min(EPSPduration, end-sp_ms)
                    if EPSPtype == "renewal":
                        data[nch,sp_ms-start:sp_ms-start+epspdur]=np.maximum(data[nch,sp_ms-start:sp_ms-start+epspdur],epsp[:epspdur])
                    elif EPSPtype == "additive":
                        data[nch,sp_ms-start:sp_ms-start+epspdur]+=epsp[:epspdur]
        return data


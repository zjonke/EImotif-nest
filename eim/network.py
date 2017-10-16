import nest
import numpy as np
import multiprocessing
from .spike_train import train_sec2ms


def setup_nest(grng_seed, rng_seed, resolution):
    """
    Setup NEST multithreading and seeds, and load swtamodule.
    """
    try:
        nest.Install('swtamodule')
    except nest.NESTError as ex:
        err = "DynamicModuleManagementError in Install: Module 'swtamodule' is loaded already."
        if ex.args[0] == err:
            pass
        else:
            raise ex

    print("seeeeeeeds", grng_seed, rng_seed)
 
    nest.ResetKernel()
    nest.SetKernelStatus({'grng_seed': grng_seed, 'rng_seeds':[rng_seed], 'resolution': resolution * 1000.})
    nest.set_verbosity('M_FATAL')


def findPool(pools, poolName):
    for pool in pools:
        if pool["name"] == poolName:
            return pool

		
class NeuronsPool:
    """
        Represents a pool of same neurons: input, excitatory, inhibitory
    """

    def __init__(self, poolparams):
        self.N = poolparams.get('N', 1)  # at least 1 neuron
        neuronparams = poolparams.get('neuronparams',{})
        self.neurontype = poolparams.get('neuronType', 'swta_neuron_dbl_exp')
        self.isInput = poolparams.get('isInput', False)

        self.pop = nest.Create(self.neurontype, self.N, neuronparams)
        self.globalToLocalID = {globalID: localID for localID, globalID in enumerate(self.pop)}
        self.recording = False

        if poolparams.get('rec', False):
            self.rec_pop = nest.Create('spike_detector')
            nest.Connect(self.pop, self.rec_pop, {'rule': 'all_to_all'})
            self.recording = True

    # set spikes: spikes in sec
    def setSpikes(self, spikes):
        assert len(spikes) == self.N 
        if self.isInput:
            
            for i in range(len(self.pop)):
                for k, spike in enumerate(spikes[i]):
                    if spike == 0:
                        spikes[i][k] = 0.001

                neuronSpikes = np.array(spikes[i]) * 1000. # converting sec to ms
                if len(neuronSpikes) > 0:
                    nest.SetStatus([self.pop[i]], {'spike_times': neuronSpikes})

   # returns sikes: spikes in sec
    def getSpikes(self):
        events = nest.GetStatus(self.rec_pop)[0]['events']  # there is 1 recorder per population
        times = events['times']
        senders = events['senders']

        spikes = [[] for i in range(self.N)]
        for i in range(len(times)):
            spikes[self.globalToLocalID[senders[i]]].append(times[i])

        spikes = [np.array(s)/1000. for s in spikes]  # convert ms to sec

        return spikes

    def hasRecorder(self):
        return self.recording


class Network:
    def __init__(self, simulationSettings, modelSettings):
        ss, ms = simulationSettings, modelSettings
        self.dt = ss.dt
        self.simulationRNGSeed = ss.simulationRNGSeed
        self.generalRNGSeed = ms.generalRNGSeed

        pools = ms.pools
        poolsconns = ms.poolsconns
		
        # setup nest
        setup_nest(self.generalRNGSeed, self.simulationRNGSeed, self.dt)

        # pools holder
        self.pools = {}
        self.poolnames = []
		
        # create pools
        for pool in pools:
            self.pools[pool["name"]] = NeuronsPool(pool)
            self.poolnames.append(pool["name"])

        # connect pools
        self.conns = {}
        self.connslearning = []
        for conn in poolsconns:
            sourcePop = self.pools[conn['source']].pop
            targetPop = self.pools[conn['target']].pop
            nest.Connect(sourcePop, targetPop, conn['rule'], conn['syntype'])

    def setWeights(self, sourcePoolName, targetPoolName, W):
        sourcePool = self.pools[sourcePoolName]
        targetPool = self.pools[targetPoolName]
        assert len(sourcePool.pop) == W.shape[1] and len(targetPool.pop) == W.shape[0]
        conn = nest.GetConnections(sourcePool.pop, targetPool.pop)
        flattenWeights = [{'weight': W[targetPool.globalToLocalID[c[1]]][sourcePool.globalToLocalID[c[0]]]} for c in conn]
        nest.SetStatus(conn, flattenWeights)

    def getShapedWeights(self, sourcePoolName, targetPoolName):
        sourcePop = self.pools[sourcePoolName].pop
        targetPop = self.pools[targetPoolName].pop
        conn = nest.GetConnections(sourcePop, targetPop)
        stats = nest.GetStatus(conn)
        return np.array([s['weight'] for s in stats]).reshape((len(sourcePop), len(targetPop))).T

    def simulate(self, Tsim, stimulus=None, reset=True):
        if not stimulus is None:
            self.pools['in_'].setSpikes(stimulus)

        if reset:
            nest.ResetNetwork();

        print("Tsim(ms) = ", Tsim * 1000., " dt(ms) = ", self.dt * 1000.)

        nest.Simulate(Tsim * 1000.)
        print("Simulation complete")

    def getAllSpikes(self):
        return {poolName: pool.getSpikes() for poolName, pool in self.pools.items() if pool.hasRecorder()}

    def setLearning(self, onOff, sourcePoolName, targetPoolName):
        sourcePool = self.pools[sourcePoolName]
        targetPool = self.pools[targetPoolName]
        conn = nest.GetConnections(sourcePool.pop, targetPool.pop)
        values = [{'learning_is_active': 1.0 if onOff else 0.0} for c in conn]
        nest.SetStatus(conn, values)


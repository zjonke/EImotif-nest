import numpy as np

class NetworkModuleSettings:
    def __init__(self, module):
        self.__dict__ = {k:v for k,v in module.__dict__.items() if not k.startswith('__')}

    def update(self, settings):
        for k in settings.keys():
            assert k in self.__dict__, "Settings does not exist!"
            self.__dict__.update(settings)


def createSettings(module, additionalSettings):

    nms = NetworkModuleSettings(module)
    nms.update(additionalSettings)

    pool_in = {
        'name': 'in_',
        'neuronType': 'spike_generator',
        'isInput': True,
        'N': nms.NUMINP,
        'rec': True
    }

    pool_in_parrot = {
        'name': 'in',
        'neuronType': 'parrot_neuron',
        'N': nms.NUMINP,
        'rec': True
    }

    pool_e = {
        'name': 'e',
        'N': nms.NUMEXC,
        'neuronType': 'swta_neuron_dbl_exp',
        'neuronparams': {
            'V_m': nms.BIAS_E,
            'tau_r': nms.PSP_TRISE,
            'tau_f': nms.PSP_TFALL,
            'V_reset': nms.BIAS_E,
            'with_reset': True,
            'dead_time': nms.REFRACTORY_E,
            'c_1': 0.,
            'c_2': 1000./nms.REFRACTORY_E,
            'c_3': 2.,
            'c_4': 0.,
            'I_e': nms.BIAS_E,
            'z_scale': nms.PSP_SCALING,
            'I_scale': 1.,
            'tau_minus': nms.STDP_WINDOW_MINUS,
        },
        'rec': True
    }

    pool_i = {'name': 'i',
        'N': nms.NUMINH,
        'neuronType': 'swta_neuron_dbl_exp',
        'neuronparams': {
            'V_m': nms.BIAS_I,
            'tau_r': nms.PSP_TRISE,
            'tau_f': nms.PSP_TFALL,
            'V_reset': nms.BIAS_I,
            'with_reset': False,
            'dead_time': nms.REFRACTORY_I,
            'c_1': 1.,
            'c_2': 0.,
            'c_3': 0.,
            'c_4': 0.,
            'I_e': 0.,
            'z_scale': nms.PSP_SCALING,
            'I_scale': 1.,
            'tau_minus': nms.STDP_WINDOW_MINUS,
        },
        'rec': True
    }

    pools = [pool_in, pool_in_parrot, pool_e, pool_i]

    stdp_params = {
        'model': 'sem_synapse',
        'learning_is_active': 0.,
        'lambda': nms.ETA * np.e,
        'alpha': 1. / np.e,
        'nu_plus': -1.,
        'nu_minus': 0.,
        'A': 0.,
        'tau_plus': nms.STDP_WINDOW_PLUS,
        'Wmax': nms.SYN_IN_WEIGHT_MAX,
        'weight': {'distribution': 'uniform', 'low': nms.SYN_IN_WEIGHT_MIN, 'high': nms.SYN_IN_WEIGHT_MAX},
        'delay': {'distribution': 'uniform', 'low': nms.SYN_IN_DELAY_MIN, 'high': nms.SYN_IN_DELAY_MAX},
    }

    syntype_ei = {'model': 'static_synapse', 'delay': nms.SYN_EI_DELAY, 'weight': nms.SYN_EI_WEIGHT}
    syntype_ie = {'model': 'static_synapse', 'delay': nms.SYN_IE_DELAY, 'weight': nms.SYN_IE_WEIGHT}
    syntype_ii = {'model': 'static_synapse', 'delay': nms.SYN_II_DELAY, 'weight': nms.SYN_II_WEIGHT}


    poolsconns = [
        {'source': 'in_', 'target': 'in', 'rule': {'rule': 'one_to_one'}, 'syntype': {}},
        {'source': 'in', 'target': 'e', 'rule': {'rule': 'pairwise_bernoulli', 'p': nms.SYN_IN_CONN_PROB}, 'syntype': stdp_params},
        {'source': 'e',  'target': 'i', 'rule': {'rule': 'pairwise_bernoulli', 'p': nms.SYN_EI_CONN_PROB}, 'syntype': syntype_ei},
        {'source': 'i',  'target': 'e', 'rule': {'rule': 'pairwise_bernoulli', 'p': nms.SYN_IE_CONN_PROB}, 'syntype': syntype_ie},
        {'source': 'i',  'target': 'i', 'rule': {'rule': 'pairwise_bernoulli', 'p': nms.SYN_II_CONN_PROB}, 'syntype': syntype_ii}
    ]

    return dict(settings=nms, generalRNGSeed=nms.GENERAL_SEED, pools=pools, poolsconns=poolsconns)

# NOTE: time scale used for nest models is milliseconds

#########################################
##      NETWORK ANATOMY PARAMETERS     ##
#########################################

NUMINP = None                             # number of input neurons: if None NUMINP=number of input pattern channels
NUMEXC = 400                              # number of excitatory neurons
NUMINH = 100                              # number of inhibitory neurons

SYN_IN_CONN_PROB = 1.                     # connectivity probability between different pools of neurons
SYN_EI_CONN_PROB = 0.575
SYN_IE_CONN_PROB = 0.6
SYN_II_CONN_PROB = 0.55


GENERAL_SEED = 42                         # seed for constructing network

#########################################
##    NETWORK PHYSIOLOGY PARAMETERS    ##
#########################################

REFRACTORY_E = 10.                        # time excitatory neuron is on after spike (refactory period), in ms
REFRACTORY_I = 3.                         # time inhibitory neuron is on after spike (refactory period), in ms

BIAS_E = -5.57                            # intrisic activity of inhibitory neurons (current injection)
BIAS_I = 0.                               # intrisic activity of inhibitory neurons (current injection)

PSP_TRISE = 1.                            # rise const of double exp PSP in ms
PSP_TFALL = 10.                           # rise const of double exp PSP in ms
PSP_SCALING = 1.435                       # psp scaling const (peak of PSP is rescaled to 1.)


# SYNAPTIC WEIGHTS
SYN_IN_WEIGHT_MIN = 0.01
SYN_IN_WEIGHT_MAX = 1.
SYN_EI_WEIGHT = 13.57
SYN_IE_WEIGHT = -1.86
SYN_II_WEIGHT = -13.57

# SYNAPTIC DELAYS, in ms
SYN_IN_DELAY_MIN = 1.                     # delay has to be greater or equal to simulation timestep
SYN_IN_DELAY_MAX = 10.
SYN_EI_DELAY = 1.
SYN_IE_DELAY = 1.
SYN_II_DELAY = 1.

# STDP properties, in ms
STDP_WINDOW_PLUS = 10.
STDP_WINDOW_MINUS = 25.


#########################################
##         SWTA MODEL PARAMETERS       ##
#########################################

ETA = 0.01                                # learning speed factor

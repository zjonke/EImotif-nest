########################
## PATTERN PARAMETERS ##
########################

PATTERN_DT = 1e-3                                    # timestep precision - should be identical to the simulation step!
PATTERN_CLASS = "OrientedBarRatePatterns"            # other pattern classes: SpatioTemporalPatterns, BarRatePatterns (require different settings)

PATTERN_N_CHANNELS = 400                             # number of rate channels (pixels)
PATTERN_WIDTH = 20                                   # in pixels, it must be PATTERN_N_CHANNELS = PATTERN_WIDTH * PATTERN_HEIGHT
PATTERN_HEIGHT = 20                                  # used only for visualization
PATTERN_BAR_WIDTH = 2                                # width of oriented bar in pixels

PATTERN_ANGLES = range(180)                          # list of patterns to create: id equals angle (0-179)
PATTERN_IDS = range(1, 181)                          # IDs for patterns

PATTERN_LOW_RATE = 0.                                # firing rate in Hz
PATTERN_HIGH_RATE = 75.                              # firing rate in Hz

PATTERN_LENGTH = 50e-3                               # in sec


#########################
##    DATA PARAMETERS  ##
#########################

DATA_MAX_OVERLAP_PATTERNS = 1                        # max number of patterns that can appear at the same time
DATA_MIXING_DISTRIBUTION = [0.5]                     # each of DATA_MAX_OVERLAP_PATTERNS appears independently with given probability
DATA_MIXING_OVERLAP_FUNCTION = 'nonlinear'           # patterns are overlapped by combining theirs channel rates 
                                                     #     options: linear or nonlinear(requires DATA_MIXING_OVERLAP_PRECISION)
DATA_MIXING_OVERLAP_PRECISION = 5.                   # sigmoid function parameter used for overlapping patterns

DATA_ON_OFF_PERIODS = [1., 0.]                       # periods of on and off pattern times in s (here always show patterns: keep it on) 

DATA_INBETWEEN_NOISE_RATE = 2.                       # noise added whenever there is no pattern present in the input
DATA_FILL_NOISE_RATE = 	0.                           # adds noise (rate in Hz) for each missing pattern out of max DATA_MAX_OVERLAP_PATTERNS patterns
                                                     # that can be present in the input

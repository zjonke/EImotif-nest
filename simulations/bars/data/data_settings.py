###########################
##   PATTERN PARAMETERS  ##
###########################

PATTERN_DT = 1e-3                              # timestep precision - should be identical to the simulation step!
PATTERN_CLASS = "BarRatePatterns"              # other pattern classes: SpatioTemporalPatterns (requires different settings)

PATTERN_N_CHANNELS = 64                        # number of rate channels (pixels)
PATTERN_WIDTH = 8                              # in pixels, it must be PATTERN_N_CHANNELS = PATTERN_WIDTH * PATTERN_HEIGHT
PATTERN_HEIGHT = 8                             # used only for visualization

PATTERN_LIST = range(16)                       # list of pattern to create: vertical (0-7), horizontal bar(8-15) 
PATTERN_IDS = range(1, 17)                     # IDs for patterns

PATTERN_LOW_RATE = 0.                          # firing rate in Hz
PATTERN_HIGH_RATE = 75.                        # firing rate in Hz

PATTERN_LENGTH = 50e-3                         # in sec


###########################
##    DATA PARAMETERS    ##
###########################

DATA_MAX_OVERLAP_PATTERNS = 3                   # max number of patterns that can appear at the same time
DATA_MIXING_DISTRIBUTION = [0.9, 0.9, 0.9]      # each of DATA_MAX_OVERLAP_PATTERNS appears independently with given probability
DATA_MIXING_OVERLAP_FUNCTION = 'nonlinear'      # patterns are overlapped by combining theirs channel rates 
                                                # 	options: linear or nonlinear(requires DATA_MIXING_OVERLAP_PRECISION)
DATA_MIXING_OVERLAP_PRECISION = 5.              # sigmoid function parameter used for overlapping patterns

DATA_ON_OFF_PERIODS = [1., 0.]                  # periods of on and off pattern times in s (here always show patterns: keep it on) 

DATA_INBETWEEN_NOISE_RATE = 0.                  # noise added whenever there is no pattern present in the input
DATA_FILL_NOISE_RATE = 	3.                      # adds noise (rate in Hz) for each missing pattern out of max DATA_MAX_OVERLAP_PATTERNS patterns
                                                # that can be present in the input


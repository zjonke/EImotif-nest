########################
## PATTERN PARAMETERS ##
########################

PATTERN_DT = 1e-3					# timestep precision - should be identical to the simulation step
PATTERN_CLASS = "SpatioTemporalPatterns"		# other pattern classes: BarRatePatterns (requires different settings)

PATTERN_N_CHANNELS = 200				# number of rate channels (pixels)

PATTERN_NUMBER = 2					# number of different patterns to create
PATTERN_IDS = range(1, 3)				# IDs for patterns

PATTERN_LOW_RATE = 0. 					# firing rate in Hz
PATTERN_HIGH_RATE = 75.  				# firing rate in Hz

PATTERN_LENGTH = 150e-3  				# in sec

							# Ornestein-Uhlenback process params:
PATTERN_OU_PROCESS_MEAN = 0.				# convergence rate
PATTERN_OU_PROCESS_THETA = 5.				# how fast it converges to mean
PATTERN_OU_PROCESS_SIGMA = 0.5				# how abrouply it changes


#########################
##    DATA PARAMETERS  ##
#########################

DATA_MAX_OVERLAP_PATTERNS = 2 				# max number of patterns that can appear at the same time
DATA_MIXING_DISTRIBUTION = [0.5, 0.5]   		# each of DATA_MAX_OVERLAP_PATTERNS appears independently with given probability
DATA_MIXING_OVERLAP_FUNCTION = 'nonlinear'		# patterns are overlapped by combining theirs channel rates 
							# 	options: linear or nonlinear(requires DATA_MIXING_OVERLAP_PRECISION)
DATA_MIXING_OVERLAP_PRECISION = 5. 			# sigmoid function parameter used for overlapping patterns

DATA_ON_OFF_PERIODS =[[0.5, 0.5], [0.1, 0.7]]   	# ranges of on and off pattern times in s 

DATA_INBETWEEN_NOISE_RATE = 2.				# noise added whenever there is no pattern present in the input
DATA_FILL_NOISE_RATE = 	0.				# adds noise (rate in Hz) for each missing pattern out of max
							# DATA_MAX_OVERLAP_PATTERNS patterns that can be present in the input

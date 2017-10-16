#################################
##        NETWORK MODEL        ##
#################################

NETWORK_MODEL = "swta"
NETWORK_PARAMS = dict(  # overwrite model default settings
    SYN_EI_DELAY = 0.1, # shorten delays for better performance(effective delay includes psp delay)
    SYN_IE_DELAY = 0.1,
    SYN_II_DELAY = 0.1,
)					


#################################
##       SIMULATION CHAIN      ##
#################################

# Params:
#    data: path to data file (string)
#    simTime: simulation time in sec (float)
#    learning: enable/disable learning (bool)
#    result: path to result file (string)
#    init: path to data file to init model (string)
SIMULATION_CHAIN = [
	dict(data="data/training", simTime=400., learning=True, result="results/training"), 
	dict(data="data/testing", simTime=200., learning=False, result="results/testing", init="results/training"), 
	dict(data="data/testing_singles", simTime=200., learning=False, result="results/testing_singles", init="results/training"), 
	dict(data="data/testing_short", simTime=2.5, learning=False, result="results/testing_short", init="results/training"), 
	dict(data="data/testing", simTime=10., learning=False, result="results/testing_lag", init="results/training"),
]
					

#################################
##    SIMULATION PARAMETERS    ##
#################################
			
DT = 0.0001                       # duration of one time step in sec
SIMULATION_SEED = 42


#################################
##   SIMULATION VISUALIZATION  ##
#################################

SHOW_LEARNING_PROGRESS = False

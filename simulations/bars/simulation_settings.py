#################################
##        NETWORK MODEL        ##
#################################

NETWORK_MODEL = "swta"
NETWORK_PARAMS = dict(  # overwrite model default settings
    ETA = 0.02
)                                  


#################################
##        SIMULATION CHAIN     ##
#################################

# Params:
#    data: path to data file (string)
#    simTime: simulation time in sec (float)
#    learning: enable/disable learning (bool)
#    result: path to result file (string)
#    init: path to data file to init model (string)
SIMULATION_CHAIN = [
    dict(data="data/training", simTime= 400., learning=True, result="results/training"),
    dict(data="data/testing", simTime= 200., learning=False, result="results/testing", init="results/training")
]


#################################
##    SIMULATION PARAMETERS    ##
#################################

DT = 0.001                                               # simulation time step in sec
SIMULATION_SEED = 42

#################################
##   SIMULATION VISUALIZATION  ##
#################################

SHOW_LEARNING_PROGRESS = True                            # if True show network input weights every 10% of simulation time


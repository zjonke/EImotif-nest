import os
import imp

from .common import DictClass

def getModuleMembers(module):
    d = {}
    for member in dir(module):
        if member.startswith("__"):
            continue
        d[member] = getattr(module, member)
    return d


def setDefaultSettings(d, mustHaveSettings, optionalSettings):
    # assert all d params are optional or must keys
    for key in d:
        assert key in mustHaveSettings or key in optionalSettings, key
    # assert all musts are present
    for must in mustHaveSettings:
        assert must in d
    # set default values if missing
    for optional, value in optionalSettings.items():
        if optional not in d:
            d[optional] = value


class GeneralSettings(object):
    def __init__(self):
        from . import settings
        self.__dict__ = self._createSettings(settings)

    def _createSettings(self, module):
        settings = dict(
            # data settings
            dataPath=module.DATA_PATH,
            dataSettings=module.DATA_SETTINGS,
            dataExt=module.DATA_EXT,

            # model settings
            modelPath=module.MODEL_PATH,
            modelSettings=module.MODEL_SETTINGS,
            modelSettingsLoader=module.MODEL_SETTINGS_LOADER,

            # simulation settings
            simulationSettings=module.SIMULATION_SETTINGS,

            # results settings
            resultsPath=module.RESULTS_PATH,
            resultsExt=module.RESULTS_EXT
        )
        return settings


class DataSettings(object):
    def __init__(self, dataSettingsPath):
        fileExists = os.path.exists(dataSettingsPath)
        if not fileExists:
            raise ValueError("Missing data settings: %s"%(dataSettingsPath))

        dataSettingsFileName = os.path.basename(dataSettingsPath)
        settingsModule = imp.load_source(dataSettingsFileName, dataSettingsPath)
        self.__dict__ = self._createSettings(settingsModule)

    def _createSettings(self, module):
        if module.PATTERN_CLASS == "BarRatePatterns":
            return self._createBarPatternSettings(module)
        elif module.PATTERN_CLASS == "OrientedBarRatePatterns":
            return self._createOrientedBarPatternSettings(module)
        elif module.PATTERN_CLASS == "SpatioTemporalPatterns":
            return self._createSpatioTemporalPatternSettings(module)

    def _createBarPatternSettings(self, module):
        config = dict(
            dt=module.PATTERN_DT,
            patternsClass=module.PATTERN_CLASS,
            width=module.PATTERN_WIDTH, 
            height=module.PATTERN_HEIGHT, 
            patternShape=[module.PATTERN_WIDTH, module.PATTERN_HEIGHT], 
            nChannels=module.PATTERN_N_CHANNELS, 
            barsOn=module.PATTERN_LIST, 
            patternIDs=module.PATTERN_IDS, 
            rates={'low': module.PATTERN_LOW_RATE, 'high': module.PATTERN_HIGH_RATE}, 
            patternLength=module.PATTERN_LENGTH, 

            mixingDistribution=module.DATA_MIXING_DISTRIBUTION, 
            maxOverlappingPatterns=module.DATA_MAX_OVERLAP_PATTERNS,

            dataOnOffPeriods = module.DATA_ON_OFF_PERIODS,
            dataInbetweenNoiseRate = module.DATA_INBETWEEN_NOISE_RATE,
            dataFillNoiseRate = module.DATA_FILL_NOISE_RATE
        )
					  
        # additional params 
        config.update(dict(nPatterns=len(config["barsOn"]) if config["barsOn"] else config["width"] + config["height"]))

        combineRules=dict(
            function=module.DATA_MIXING_OVERLAP_FUNCTION, 
            precision=module.DATA_MIXING_OVERLAP_PRECISION,
            rates=config["rates"]
        )
				  
        config.update(dict(combineRules=combineRules))
        return config

    def _createOrientedBarPatternSettings(self, module):
        config = dict(
            dt=module.PATTERN_DT,
            patternsClass=module.PATTERN_CLASS,
            width=module.PATTERN_WIDTH, 
            height=module.PATTERN_HEIGHT, 
            patternShape=[module.PATTERN_WIDTH, module.PATTERN_HEIGHT], 
            barWidth=module.PATTERN_BAR_WIDTH,
            nChannels=module.PATTERN_N_CHANNELS, 
            angles=module.PATTERN_ANGLES, 
            patternIDs=module.PATTERN_IDS, 
            rates={'low': module.PATTERN_LOW_RATE, 'high': module.PATTERN_HIGH_RATE}, 
            patternLength=module.PATTERN_LENGTH, 

            mixingDistribution=module.DATA_MIXING_DISTRIBUTION, 
            maxOverlappingPatterns=module.DATA_MAX_OVERLAP_PATTERNS,

            dataOnOffPeriods = module.DATA_ON_OFF_PERIODS,
            dataInbetweenNoiseRate = module.DATA_INBETWEEN_NOISE_RATE,
            dataFillNoiseRate = module.DATA_FILL_NOISE_RATE
        )
		
        # additional params 
        config.update(dict(nPatterns=len(config["angles"])))

        combineRules=dict(function=module.DATA_MIXING_OVERLAP_FUNCTION, 
            precision=module.DATA_MIXING_OVERLAP_PRECISION,
            rates=config["rates"]
        )
						  
        config.update(dict(combineRules=combineRules))
        return config
		
    def _createSpatioTemporalPatternSettings(self, module):
        config = dict(
            dt=module.PATTERN_DT,
            patternsClass=module.PATTERN_CLASS,
            nPatterns=module.PATTERN_NUMBER,
            nChannels=module.PATTERN_N_CHANNELS, 
            patternIDs=module.PATTERN_IDS, 
            rates={'low': module.PATTERN_LOW_RATE, 'high': module.PATTERN_HIGH_RATE}, 
            patternLength=module.PATTERN_LENGTH, 

            oumean=module.PATTERN_OU_PROCESS_MEAN,
            outheta=module.PATTERN_OU_PROCESS_THETA,
            ousigma=module.PATTERN_OU_PROCESS_SIGMA,

            maxOverlappingPatterns=module.DATA_MAX_OVERLAP_PATTERNS,
            mixingDistribution=module.DATA_MIXING_DISTRIBUTION, 

            dataOnOffPeriods = module.DATA_ON_OFF_PERIODS,
            dataInbetweenNoiseRate = module.DATA_INBETWEEN_NOISE_RATE,
            dataFillNoiseRate = module.DATA_FILL_NOISE_RATE
        )

        # additional params 
        config.update(dict(patternShape=[config['nChannels'], 1]))

        combineRules=dict(
            function=module.DATA_MIXING_OVERLAP_FUNCTION, 
            precision=module.DATA_MIXING_OVERLAP_PRECISION,
            rates=config["rates"]
        )

        config.update(dict(combineRules=combineRules))
        return config


class SimulationSettings(object):
    def __init__(self, simulationSettingsName):
        fileExists = os.path.exists(simulationSettingsName)
        if not fileExists:
            raise ValueError("Missing simulation settings: %s"%(simulationSettingsName))
	
        settingsModule = imp.load_source(simulationSettingsName, simulationSettingsName)
        self.__dict__ = self._createSettings(settingsModule)
	
    def _createSettings(self, module):
        mustHaveSettings = ['SIMULATION_CHAIN', 'NETWORK_MODEL', 'NETWORK_PARAMS']
        optionalSettings = {'DT': 1e-3, 'SIMULATION_SEED': 42, 'SHOW_LEARNING_PROGRESS': False}
        settings = getModuleMembers(module)
        setDefaultSettings(settings, mustHaveSettings, optionalSettings)

        simChainMustHaveSettings = ['data', 'simTime', 'result']
        simChainOptionalSettings = {'learning': False, 'init': None}
        simChain = []
        for ds in module.SIMULATION_CHAIN:
            setDefaultSettings(ds, simChainMustHaveSettings, simChainOptionalSettings)
            simChain.append(DictClass(ds))

        config = dict(
            dt=settings['DT'], 
            simulationRNGSeed=settings['SIMULATION_SEED'],
            simulationChain=simChain,
            model=settings['NETWORK_MODEL'],
            modelAdditionalParams=settings['NETWORK_PARAMS'],
            showLearningProgress=settings['SHOW_LEARNING_PROGRESS']
        )
				
        return config
		
		
class ModuleSettings(object):
    def __init__(self, modulePath, moduleInstanceName, moduleSettingsName, moduleSettingsLoaderName, additionalSettings):
        self._loaded = False
        structureIsOk = False
		
        moduleDir = modulePath + moduleInstanceName
        settingsFile = modulePath + moduleInstanceName + "/" + moduleSettingsName
        settingsLoaderFile = modulePath + moduleInstanceName + "/" + moduleSettingsLoaderName
		
        dirExists = os.path.isdir(moduleDir) 
        if not dirExists:
            print("Missing module: ", moduleDir)
            return
			
        settingsExists = os.path.exists(settingsFile)
        if not settingsExists:
            print("Missing module settings: ", settingsFile)
            return
			
        settingsLoaderExists = os.path.exists(settingsLoaderFile)
        if not settingsLoaderExists:
            print("Missing module settings loader: ", settingsLoaderFile)
            return
	
        if dirExists and settingsExists and settingsLoaderExists:
            structureIsOk = True
		
        if structureIsOk:
            try:
                import imp
                # load settings loader and settings module
                settingsLoader = imp.load_source(moduleSettingsLoaderName, settingsLoaderFile)
                defaultSettings = imp.load_source(moduleSettingsLoaderName, settingsFile)
                self.__dict__ = settingsLoader.createSettings(defaultSettings, additionalSettings)
            except:
                raise ValueError("Failed to load settings: %s %s %s" % (moduleDir, settingsFile, settingsLoaderFile))
        else:
            raise ValueError("Module structure wrong:%s %s %s" % (moduleDir, settingsFile, settingsLoaderFile))


class NetworkModelSettings(ModuleSettings):
    def __init__(self, generalSettings, modelName, modelAdditionalParams):
        gs = generalSettings
        currentPath = os.path.dirname(os.path.realpath(__file__))
        super(NetworkModelSettings, self).__init__(currentPath + '/' + gs.modelPath, modelName, gs.modelSettings, gs.modelSettingsLoader, modelAdditionalParams)


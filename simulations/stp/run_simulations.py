from eim.settings_loader import GeneralSettings, SimulationSettings, NetworkModelSettings
from eim.simulation_chain import SimulationChainData
from eim.simulator import simulate

gs = GeneralSettings()
ss = SimulationSettings(gs.simulationSettings)
scs = SimulationChainData(gs, ss.simulationChain)
ms = NetworkModelSettings(gs, ss.model, ss.modelAdditionalParams)

simulate(gs, ss, ms, scs)

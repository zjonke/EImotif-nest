# EI motif - nest

This repository contains code used in the paper:
**Feedback inhibition shapes emergent computational properties of cortical microcircuit motifs**, 
by Z. Jonke, R. Legenstein, S. Habenschuss, and W. Maass,
Journal of Neuroscience, 37(35):8511-8523, 2017.

The paper is available at http://www.jneurosci.org/content/37/35/8511

Note: this is ported code to Python 3 and Nest simulator.
Original code can be found at https://github.com/zjonke/EImotif

## Requirements

- Nest simulator, http://www.nest-simulator.org/
- Python3
- IPython3
- Numpy
- Scipy
- Matplotlib

Anaconda Distribution (https://www.anaconda.com/download/) is a simple way to install all of them except Nest.


## Setup

Download or clone code.
Add eimotif-nest folder to the python path in the .bashrc file
```
PYTHONPATH=<path_to_eimotif_folder>:$PYTHONPATH
```

Install nest module(`swtamodule`) containing neuron and synapse models required by our EI motif model:
```
cd nest-swtamodule
bash install.sh
```


## Code organisation

- `eim` folder: contains common code and model definition
- `simulations` folder: contains all simulations, each in its own folder (e.g. bars, oriented_bars, ..)

Each simulation is self contained in its folder, containing simulation settings and scripts to create simulation data, run simulation, perform analysis and to show results of simulation (weights).

## Run simulations

To perform simulation of e.g. bars, go to the folder of simulation and run scripts in order:
- `python3 create_data.py` (creates data for simulation)
- `python3 run_simulations.py` (runs simulations of model, requires PCSIM, but we provide data so you can skip it)
- `python3 analyse.py` (performs analysis of network)

To visualize results run (if availalbe for particular simulation):
- `ipython3 -i show_weights.py` (plots network weights after learning)
- `ipython3 -i show_figure.py`


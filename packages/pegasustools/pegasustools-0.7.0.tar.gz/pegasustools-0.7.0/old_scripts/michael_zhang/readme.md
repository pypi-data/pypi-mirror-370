Attached are the various scripts that I use. I've split these into two folders, Matlab scripts I received from Jono, and python scripts I received from Silvio. I mainly use the ones from Jono.

Jono's scripts mainly work as follows:
chooseComputerAndFiles.m is called by other functions to select the directory that contains data for various simulations (which is then picked out by a name for a particular simulation in whichever analysis script you are using).
The read... scripts are called by the various analysis scripts to open and parse the various pegasus++ outputs into matlab arrays etc. to be handled/saved for analysis.
Some of the analysis scripts that use these various outputs are: distributionFunctions.m (spec output), distributionFunctionsAv.m (specav output), energyForMinor.m (reads history file and saves heating rates, temperatures and energy injection for 2 different simulations, also has functionality to look at energy in saved 2D spectra), plot_hst_energy.m (similar to energyForMinor.m but for 1 simulation), plot_hst_inject.m (similar to energyForMinor.m but only for energy injection for 1 simulation. Note that the number of components output for injection are different depending on if the forcing is imbalanced or not (which will also shift the start point of minor ions in the history dump)), readSwarm.m (reads swarm output and saves as a .mat for swarmSpectraNew.m - which calculates frequency spectra for fields) -- haven't developed a script for reading the output from trace yet but should in principle be similar to readSwarm.m. spectrum_2d.m calculates spectra for EM fields in 2D (e.g. kx ky). spectrum_kprlkprp.m calculates spectra vs kprl and kprp and so is much slower than spectrum_2d.m. spectrum_alf.m calculates spectra vs kprp. These EM spectra vs k all use readNBF etc. The other parts of scripts and plotting parts are more specific to my analysis. Key modifications I've made to Jono's scripts include the ability to read minor ion data (spec, specav, nbfs, .hst, etc.).

I haven't parsed Silvio's scripts as much, I mainly wanted to use his stochastic heating calculation, which is somewhat specific to my work. This has consisted of porting some of his stuff to jupyter notebooks (the ipynbs), which use some of his python scripts for reading data like pegasus_read.py and pegasus_computation.py. Naturally I've modified these to parse minor ion data too.


Bob's reformatting

- `chooseComputerAndFiles.m` is called by other functions to select the directory that contains data for various simulations (which is then picked out by a name for a particular simulation in whichever analysis script you are using).
- The `read...` scripts are called by the various analysis scripts to open and parse the various pegasus++ outputs into matlab arrays etc. to be handled/saved for analysis.
- `distributionFunctions.m` (spec output)
- `distributionFunctionsAv.m` (specav output)
- `energyForMinor.m` (reads history file and saves heating rates, temperatures and energy injection for 2 different simulations, also has functionality to look at energy in saved 2D spectra)
- `plot_hst_energy.m` (similar to energyForMinor.m but for 1 simulation)
- `plot_hst_inject.m` (similar to energyForMinor.m but only for energy injection for 1 simulation. Note that the number of components output for injection are different depending on if the forcing is imbalanced or not (which will also shift the start point of minor ions in the history dump))
- `readSwarm.m` (reads swarm output and saves as a .mat for swarmSpectraNew.m - which calculates frequency spectra for fields) -- haven't developed a script for reading the output from trace yet but should in principle be similar to readSwarm.m
- `spectrum_2d.m` calculates spectra for EM fields in 2D (e.g. kx ky)
- `spectrum_kprlkprp.m` calculates spectra vs kprl and kprp and so is much slower than spectrum_2d.m.
- `spectrum_alf.m` calculates spectra vs kprp. These EM spectra vs k all use readNBF etc.
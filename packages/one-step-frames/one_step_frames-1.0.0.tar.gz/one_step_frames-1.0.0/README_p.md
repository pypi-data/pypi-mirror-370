## Project description

# One-step-frames
```one-step-frames``` is a package that implements the algorithms for this [paper](https://www.sciencedirect.com/science/article/pii/S0168007214000785?via%3Dihub).

## Getting starting
### Installation
The package can be downloaded with the pip command. The source code can be found [here](https://github.com/lucianIrsigler/one_step_frames).

### Setup
The SPASS part of the algorithm requires a local folder(same level as the script) named ```spass39``` with the files for SPASS version 39. The download link is found [here](https://www.mpi-inf.mpg.de/departments/automation-of-logic/software/spass-workbench/classic-spass-theorem-prover/download/). You should download the 3.9 version.

### Modules
The package has the following modules:
- ```AST```: The data stucture used for parsing logical formula.
- ```spass```: The implementation of the SPASS algorithm required to check p-morphisms for first-order conditions on one-step frames 
- ```util```: Includes all the several steps of the algorithm, such as initialization,searching etc. Look at the github for a more in-depth ook.
- ```step_frame_conditions```- The main file that implements finding a first order condition on one-step frames from a given reduced rule. 

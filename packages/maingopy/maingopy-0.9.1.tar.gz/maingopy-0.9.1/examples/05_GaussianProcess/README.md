# Example Problem Number 05 - Optimization with Gaussian processes (Kriging) embedded

## About

In this problem the prediction of a Gaussian process is minimized.
The Gaussian process has 2 inputs and 1 output.
The Gaussian process uses a 3/2-Matern covariance function.
The Gaussian process parameters (e.g., hyperparameters, covariance matrix) are saved in a json-file called "testGP.json" in this folder.

Please copy the file into the folder where your MAiNGO executable is built in order to run the problem. If you are using Visual Studio, this should be the Release folder containing MAiNGO.exe.

The Gaussian process has been trained on 40 data points obtained from a Latin hypercube sampling of the peaks test function.
This folder inlcudes two problem formulations for comparison: a reduced-space and a full-space formulation.
The file "gaussianProcessReducedSpace.py" also shows how to solve the reduced-space version via the Python API of MAiNGO.

## Toolbox

If you want to train Gaussian processes on your data and embed them in an optimization, please use our open-source tool [MeLOn](https://git.rwth-aachen.de/avt.svt/public/MeLOn).
MeLOn provides scripts for the training of various machine-learning models and their C++ implementation which can be used in MAiNGO.
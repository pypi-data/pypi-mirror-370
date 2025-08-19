# Example Problem Number 04 - Optimization with artificial neural networks embedded

## About

In this problem the prediction of an artificial neural network is minimized.
The ANN has 2 inputs and 1 output.
The ANN has 1 input layer, 2 hidden layers, and 1 output layer.
The hidden layers have tanh activation function and the output layer has a linear activation function.
The ANN parameters (e.g., weights, biases) are saved in a set of csv files in the folder "myTestANN".

Please copy the folder "myTestANN" into the folder where your MAiNGO executable is built in order to run the problem. If you are using Visual Studio, this should be the Release folder containing MAiNGO.exe.

The ANN has been trained on data obtained from the peaks test function.
This folder inlcudes two problem formulations for comparison: a reduced-space and a full-space formulation.
The file "annReducedSpace.py" also shows how to solve the reduced-space version via the Python API of MAiNGO.
For more information on the optimization with ANNs embedded, please see our publications ([Schweidtmann & Mitsos  2019](#Schweidtmann2019ANN_Opt_Method)).

Note that the full-space formulation will require more CPU time to solve the proposed problem.

Also, constraint propagation is not beneficial in this example in the reduced-space formulation and can be omitted by changing the settings:
BAB_constraintPropagation              0

## Toolbox

If you want to train ANNs on your data and embed them in an optimization, please use our open-source toolbox [MeLOn](https://git.rwth-aachen.de/avt.svt/public/MeLOn).
MeLOn provides scripts for the training of various machine-learning models and their C++ implementation which can be used in MAiNGO.


## References
* Schweidtmann, A. M., & Mitsos, A. (2019). Deterministic global optimization with artificial neural networks embedded. Journal of Optimization Theory and Applications, 180(3), 925-948. [https://doi.org/10.1007/s10957-018-1396-0](https://doi.org/10.1007/s10957-018-1396-0)
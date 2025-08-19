# maingopy - Python interface for MAiNGO

Maingopy is the Python interface for MAiNGO, the McCormick-based Algorithm for mixed-integer Nonlinear Global Optimization.
MAiNGO is a deterministic global optimization solver for nonconvex mixed-integer nonlinear programming problems.
For more information on MAiNGO, please visit the [MAiNGO website](http://permalink.avt.rwth-aachen.de/?id=729717).
The open source version of MAiNGO is available on our [GitLab page](https://git.rwth-aachen.de/avt-svt/public/maingo).
The documentation of MAiNGO is available [here](https://avt-svt.pages.rwth-aachen.de/public/maingo).

## Obtaining maingopy

Maingopy can either be obtained as a source of binary distribution via PyPI or built from source via the git repository.

To obtain it via PyPI, run

    $ pip install maingopy

This will typically get you the binary distribution of the maingopy package that contains a pre-compiled version of MAiNGO along with its Python bindings, as well as an extension module for [MeLOn](https://git.rwth-aachen.de/avt-svt/public/melon), which contains machine learning models for use in optimization problems to be solved by MAiNGO.

Note that the pre-compiled version of MAiNGO contained in this package does not allow the use of 
1. the optional closed-source subsolvers CPLEX, Gurobi, or KNITRO, even if they are installed on your system,
2. the MPI parallelization of MAiNGO.

To use these features, you will need to build maingopy from source. In this case, please obtain the code from our [GitLab page](https://git.rwth-aachen.de/avt-svt/public/maingo) and follow the instructions provided there.

## Using maingopy

Maingopy provides Python bindings (enabled by [pybind11](https://pybind11.readthedocs.io/en/stable/index.html)) for the C++ API of MAiNGO.
Details on how to use it are available in the [documentation of MAiNGO](https://avt-svt.pages.rwth-aachen.de/public/maingo).
Example problems can be found in the [examples directory](https://git.rwth-aachen.de/avt-svt/public/maingo/-/tree/master/examples) in the MAiNGO repository.

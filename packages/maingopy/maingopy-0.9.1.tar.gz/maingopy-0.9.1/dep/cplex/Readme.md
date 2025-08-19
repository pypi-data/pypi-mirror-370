This is a wrapper for IBM ILOG CPLEX.
It requires a separate CPLEX installation and merely provides the CMakeLists.txt and FindCPLEX.cmake for including it in other software.
Primarily, this wrapper has been designed for using CPLEX in MAiNGO.
If CPLEX is found, the pre-processor variable HAVE_CPLEX will be defined, such that the client code can react accordingly.
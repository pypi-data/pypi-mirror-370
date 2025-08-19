This is a wrapper for Gurobi.
It requires a separate Gurobi installation and merely provides the CMakeLists.txt and FindGurobi.cmake for including it in other code (primarily, it was developed for use with our global MINLP solver MAiNGO).
The pre-processor flag HAVE_GUROBI can be used in the client code to check whether Gurobi was found.
Currently, we support Gurobi versions 8.x and 9.x.

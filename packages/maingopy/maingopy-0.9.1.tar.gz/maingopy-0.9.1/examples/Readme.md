# Example Problems

## About

This folder contains example problems for MAiNGO. 
If you are new to MAiNGO, we recommend looking at the following to get started:
* The [documentation of MAiNGO](https://avt-svt.pages.rwth-aachen.de/public/maingo) contains more detailed information on how to obtain, build and execute MAiNGO.
* `01_BasicExample`: This folder contains the most basic example for solving problems with MAiNGO.

Most examples are available in three forms:
* as text-based input using the Syntax of the [ALE library](https://git.rwth-aachen.de/avt-svt/public/libale)
* as C++ problem file for the C++ API of MAiNGO
* as Python script using the Python API of MAiNGO.

To solve a problem via the text-based ALE input, you need to build MAiNGO with the CMake variable `MAiNGO_build_parser` set to `true`.
After compiling MAiNGO, you obtain an executable called `MAiNGO` which contains a parser for reading ALE input.
By default, MAiNGO searches for a problem file called `problem.txt` in the current working directory from which you executed MAiNGO.
You can specify a different problem file name (including an absolute or relative path) as a command line argument.
As an optional second command line argument, you can specify the file name (and path) of a settings file. If no settings file is specified, MAiNGO looks for a file called `MAiNGOSettings.txt`.
An example for a settings file can be found in this directory (`examples`).

To solve a problem via the C++ API of MAiNGO, you need to build MAiNGO with the CMake variable `MAiNGO_build_standalone` set to `true`.
The problem is implemented by specializing the abstract `MAiNGOModel` class. In the examples, this is accomplished in a dedicated header file (e.g., `01_BasicExample/problem.h`).
You need to include the header file with your problem definition in the `mainCppApi.cpp` file in this directory and then compile MAiNGO. This will produce an executable called `MAiNGOcpp`.
When running this executable, the problem will be solved. Here, the only (optional) command line argument is the settings file name.

To solve a problem via the Python API of MAiNGO, you need to either build MAiNGO with its Python interface by setting the CMake variable `MAiNGO_build_python_interface` to `true`,
which builds a Python package called `maingopy`, or you can use the [maingopy package on PyPI](https://pypi.org/project/maingopy) that contains a pre-compiled version of MAiNGO.
In either case, you can use MAiNGO from Python as shown in the file `01_BasicExample/examplePythonInterface.py`, which you can run via `python3 examplePythonInterface.py`.
To ensure the `maingopy` package is available when building from source, you may want to copy the `examplePythonInterface.py` to your build directory, which (after a successful build) should contain a sub-directory called `maingopy`, and execute the command in your build directory.

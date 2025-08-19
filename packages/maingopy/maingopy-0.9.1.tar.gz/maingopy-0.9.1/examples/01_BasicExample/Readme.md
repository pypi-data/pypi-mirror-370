# Example Problem Number 01 - Basic Example

## About

This problem demonstrates some basic features in both the C++ and Python APIs of MAiNGO as well as the text-based input in ALE format.
The problem to be solved is

    min  -20 * exp(-0.2 * sqrt( (x^2 + y^2) / 2 )) - exp((cos(PI*x) + cos(PI*y)) / 2) + 20 + exp(1)  
    s.t. x <= 1  
         x^2 + x^2 = 1  
         x in {0, 1}  
         y in [-2,2]

The problem implementations in the files `problem.h` (for the C++ API), `examplePythonInterface.py` (for the Python API), and `problem.txt` (for text-based input via the ALE library) contain several detailed comments on the features that are required for implementing
not only this simple problem but also more complex ones.

To solve this example problem **via the text-based ALE input**, make sure to copy the file `problem.txt` into the directory where your MAiNGO executable is.
You can then solve the problem by executing the MAiNGO executable. As an alternative, you can provide a (relative or absolute) path to the `problem.txt` as the first command line argument to MAiNGO.

To solve this example problem **via the C++ API**, you need to include the `problem.h` file in the `mainCppApi.cpp` file
(with the correct relative path from the directory containing `mainCppApi.cpp` to the one containing `problem.h`, if they are not in the same directory). Make sure that you have set the CMake variable `MAiNGO_build_standalone` to `true`.
Then you need to compile MAiNGO and execute the `MAiNGOcpp` executable.

To solve this example problem **via the Python API**, you need to make sure you built MAiNGO with its Python interface, such that the pymaingo package is available.
To ensure that the pymaingo package is found, you may want to copy `examplePythonInterface.py` to your build directory, which should contain a sub-directory called pymaingo.
Then just run `python examplePythonInterface.py` in your build directory.
If you run into an error that pymaingo could not be found, also double check that the version of Python you are trying to run the example with is the same that was found by CMake when building MAiNGO (check the CMake output).
If not, choose a different Python version either for running the example or for building MAiNGO (for the latter, see the documentation of MAiNGO).

**Settings** of MAiNGO can be specified via a settings file. By default, MAiNGO looks for a file called MAiNGOSettings.txt in the working directory. You can specify a different file
(including an absolute or relative path) as the second (when running the `MAiNGO` executable, which expects the problem file name as first argument) or first (when running the `MAiNGOcpp` executable) command line argument.
In the example for the Python interface, you can just change the settings file name in the code of `examplePythonInterface.py`.
An example settings file can be found in the folder `examples` in the MAiNGO repository.
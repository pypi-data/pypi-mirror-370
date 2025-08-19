# babBase

## Purpose
This repository holds basic components to implement a branch and bound algorithm.

## Prerequisite

C++11 compatible compiler is necessary.

## Installation

Add the folder containing the contents of this repository to a CMake project using add_subdirectory and the target babbase with the command target_link_libraries.

## Tests

Test reside in the test subdirectory. Building testBranchAndBoundBase.cpp will run the tests. Note that only for testing two additional dependencies are used. One is boost_test and one is rapidCheck. The latter is included as a submodule in the dep folder. BOOST is not needed if test are not build (default)
.
### RapidCheck Tests

RapidCheck is used to perform systematic testing of invariants. It will create the parameters of the testcases at random. However, it will start with simple values (integers set to 0 or 1, vectors empty) and increase the difficulty or size of the tests. If a test fails, it will try and find a simple counter example to one of the assertions.

For example an possible output could be :

```text
Using configuration: seed=9928307433081493900

Falsifiable after 12 tests and 10 shrinks

std::tuple<std::vector<int>>:
([1, 0, 0, 0, 0, 0, 0, 0, 0, 0])

main.cpp:17:
RC_ASSERT(l0 == l1)

Expands to:
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

Here the vector in the second line is the counter example, that caused a test to fail. Afterwards, the failed assertion is given, as well as an expansion of its arguments.

### RapidCheck Configuration
RapidCheck has multiple configuration variables. A selection will be listed below. These can be configured by setting the RC_PARAMS environment variable to a configuration string. The configuration string as the format ```<key1>=<value1> <key2>=<value2>```. For example one could use the following line under Linux:

```text
env RC_PARAMS="max_success=1050  seed=9928307433081493900" ./TEST_BABBASE
```

RapidCheck uses random sampling of the space of testexamples. This can be expensive. The number of tests per test case can be specified with 


max_success - The maximum number of successful test cases to run before deciding that a property holds. Defaults to 100.
max_size - The maximum size to use. The size starts at 0 and increases to max_size as the final value. Defaults to 100.

Even thought the tests are randomized, we can reproduce the failling of a test, by forcing the programm to repeat the same test again.
For this we copy the seed from the output and give it as an parameter.

seed - The global random seed used. This is a 64-bit integer. If not set, a random one is chosen using the system random device.

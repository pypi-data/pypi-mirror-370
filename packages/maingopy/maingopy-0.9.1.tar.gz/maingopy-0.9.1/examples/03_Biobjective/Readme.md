# Example Problem Number 03 - Bi-Objective Optimization Problem

## About

This problem demonstrates the solution of bi-objective optimization problems using the epsilon-constraint method.
Note that currently bi-objective problems can only be solved via the C++ API of MAiNGO, *not* via ALE.
The problem to be solved is the Poloni test function 

    min  [ -10 * exp(-0.2 * sqrt(x^2+y^2)) - 10 * exp(-0.2 * sqrt(y^2+z^2)),
	       |x|^0.8 + 5 * sin(x^3) + |y|^0.8 + 5 * sin(y^3) + |z|^0.8 + 5 * sin(z^3) ]
    s.t. x in [-5,5]
         y in [-5,5]
         z in [-5,5]

To solve the problem, you need to
* include the file `problemEpsCon.h` in your main file (e.g., `mainCppApi.cpp`)
* call the method `solve_epsilon_constraint()` of MAiNGO instead of `solve()`. If you are using the example file `mainCppApi.cpp`, you need to comment out line 103 and instead uncomment line 105.
 
By default, MAiNGO computes 10 points on the Pareto front: the 2 lexicographic optima, and 8 points in between. You can change this using the option `EC_nPoints` (cf. the file `MAiNGOSettings.txt`).
For the points between the lexicographic optima, the second objective is always used in the epsilon constraint while the first objective is minimized.
If you wish to change this, simply change the order of the objectives in your problem file.

When solving a bi-objective problem, MAiNGO writes the following two additional result files:
* `MAiNGO_epsilon_constraint_objective_values.csv` contains the objective values of the points on the Pareto front
* `MAiNGO_epsilon_constraint_solution_points.csv` contains the corresponding points in the variable space




## References

Poloni, C., Giurgevich, A., Onesti, L., & Pediroda, V. (2000). [Hybridization of a multi-objective genetic algorithm, a neural network and a classical optimizer for a complex design problem in fluid dynamics](https://www.sciencedirect.com/science/article/pii/S0045782599003941). *Computer Methods in Applied Mechanics and Engineering* 186, 403–420 
# Example Problem Number 02 - Case Study 2 LCOE


## About

This problem illustrates the use of MAiNGO for a flowsheet optimization problem. 
The example is taken from ([Bongartz & Mitsos 2017](https://link.springer.com/article/10.1007/s10898-017-0547-4)).
The example considers the design of a bottoming cycle of a combined cycle power plant.
For a given stream of hot gas turbine exhaust and a given configuration of the power cycle, the levelized cost of electricity (LCOE) is to be minimized.
The flowsheet optimization problem is formulated in a reduced space as discussed by ([Bongartz & Mitsos 2017](https://link.springer.com/article/10.1007/s10898-017-0547-4)).
The optimization variables are the pressure level of the deaerator (p2), the upper cycle pressure (p4), the mass flow rate through the cycle (mdot), 
the enthalpy of the live steam leaving the superheater (h7), and the fraction of the mass flow rate used as turbine bleed (k).
There is only one equality constraint to make sure that the stream leaving the deaerator is in the saturated liquid state.
Multiple inequality constraints are used to ensure model validity or for restricting certain temperatures or vapor fractions to allowable values due to hardware limitations.

In the C++ version of the example problem, the thermodynamic models are implemented in external header files (e.g., `Thermo/IdealFluidModel.h`). Since they are derived from an
abstract base class (defined in `Thermo/ThermoModel.h`), the models can easily be exchanged for different ones.
In the ALE version, the thermodynamic models are directly included in the problem formulation.

![Flowsheet](../../doc/images/flowsheet.png)

## References
Bongartz, D. & Mitsos, A. (2017). [Deterministic global optimization of process flowsheets in a reduced space using McCormick relaxations](https://link.springer.com/article/10.1007/s10898-017-0547-4). *Journal of Global Optimization*, 69(4), 761-796.
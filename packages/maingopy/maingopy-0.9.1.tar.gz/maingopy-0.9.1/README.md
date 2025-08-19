# <img src="doc/images/MAiNGO.png" alt="MAiNGO" width="300"/> <br> McCormick-based Algorithm for mixed-integer Nonlinear Global Optimization

Thank you for using the beta version of MAiNGO! If you have any issues, concerns, or comments, please communicate them using the ["Issues"
functionality in GitLab](https://git.rwth-aachen.de/avt-svt/public/maingo/-/issues)	 or send an e-mail to [MAiNGO@avt.rwth-aachen.de](mailto:MAiNGO@avt.rwth-aachen.de).

## About

MAiNGO is a deterministic global optimization solver for nonconvex mixed-integer nonlinear programs (MINLPs). It is jointly being developed at [RWTH Aachen University](http://permalink.avt.rwth-aachen.de/?id=729717) and [KU Leuven](https://cit.kuleuven.be/creas/researchthemes).
General information about the capabilities and main algorithmic features of MAiNGO can be found in our technical report available [here](http://permalink.avt.rwth-aachen.de/?id=729717).
For a detailed installation guide, description of the algorithm, and a complete list of available options, please refer to the [MAiNGO documentation](https://avt-svt.pages.rwth-aachen.de/public/maingo).

## Obtaining MAiNGO

### Via Git

To acess the full functionality of MAiNGO including the C++ API, text-based parser, MPI parallelization and all supported subsolvers, you should obtain the code from this git repository. The MAiNGO repository uses submodules for all dependencies. Hence, to obtain MAiNGO, you need to run the following commands (on Windows, you might need to get Git Bash first).

	$ git clone https://git.rwth-aachen.de/avt-svt/public/maingo.git <directory>
	$ cd <directory>
	$ git submodule init
	$ git submodule update -j 1

If you want to check if the above has worked, you can check that each subfolder in the `dep` folder is non-empty.
A note for users more familiar with git: `git submodule update` is executed without the `--recursive` option.
This avoids instantiating any indirect dependencies; in the repository design of MAiNGO, all dependencies (including indirect ones) are present in `dep`.
Additionally, it is executed using only one process `-j 1` to avoid input failures.

If you have cloned the MAiNGO repository before and want to update to the latest version, use the following git commands

	$ git pull
	$ git submodule update -j 1

### Via PyPI

If you plan to use MAiNGO via its Python interface, you can also obtain the [<tt>maingopy</tt> package from PyPI](https://pypi.org/project/maingopy) via

	$ pip install maingopy

This package is available as source as well as binary distribution containing a precompiled version of MAiNGO for multiple Python versions under Windows, Linux, and MacOS.
It also includes the <tt>melonpy</tt> module, the Python interface of [MeLOn](https://git.rwth-aachen.de/avt-svt/public/melon), which contains various machine learning models for use in optimization problems to be solved with MAiNGO.
Note that the following features are *not* available in the maingopy package available via PyPI:
- the MPI parallelization of MAiNGO
- the C++ API and text-based model parser of MAiNGO
- the subsolvers CPLEX, GUROBI and KNITRO

If you want to use these features, you should obtain the MAiNGO code via git as described above.
This also enables you to build a version of the <tt>maingopy</tt> package that can use CPLEX, Gurobi, and KNITRO if you have them installed on your system.


## First steps

If you are new to MAiNGO, we recommend looking at the following to get started:
* The [documentation of MAiNGO](https://avt-svt.pages.rwth-aachen.de/public/maingo) contains more detailed information on how to obtain, build and execute MAiNGO.
* `examples/01_BasicExample`: This folder contains the most basic example for solving problems with MAiNGO.

## Example applications

MAiNGO has been successfully applied to flowsheet-optimization problems ([Bongartz & Mitsos 2017a](https://link.springer.com/article/10.1007/s10898-017-0547-4), [Bongartz & Mitsos 2019](https://aiche.onlinelibrary.wiley.com/doi/full/10.1002/aic.16507), [Bongartz et al. 2020](https://link.springer.com/article/10.1007/s11081-020-09502-1)),
optimization problems with artificial neural networks ([Schweidtmann & Mitsos 2018](https://link.springer.com/article/10.1007/s10957-018-1396-0)),
hybrid mechanistic models with applications in energy processes ([Schweidtmann et al. 2019a](https://www.sciencedirect.com/science/article/abs/pii/S009813541830886X), [Schweidtmann et al. 2019b](https://www.sciencedirect.com/science/article/pii/B9780128186343501570), [Huster et al. 2019a](https://www.sciencedirect.com/science/article/pii/B9780128185971500680), [Huster et al. 2019b](https://link.springer.com/article/10.1007/s11081-019-09454-1)),
hybrid mechanistic models with applications in membrane development ([Rall et al. 2019](https://www.sciencedirect.com/science/article/pii/S0376738818324293), [Rall et al. 2020](https://doi.org/10.1016/j.memsci.2020.117860)), [Rall et al. 2020b](https://doi.org/10.1016/j.memsci.2020.118208),
and nonlinear scheduling with artificial neural networks embedded ([Schäfer et al. 2020](https://doi.org/10.1016/j.compchemeng.2019.106598)).

![Applications](doc/images/applications.png)

MAiNGO works particularly well for problems which can be formulated in a reduced-space manner ([Bongartz & Mitsos 2017a](https://link.springer.com/article/10.1007/s10898-017-0547-4)).

MAiNGO holds specialized relaxations for functions found in the field of process engineering ([Najman & Mitsos 2016](https://www.sciencedirect.com/science/article/pii/B9780444634283502721), [Najman et al. 2019](https://www.sciencedirect.com/science/article/abs/pii/S0098135419309494), [Bongartz et al. 2020](https://link.springer.com/article/10.1007/s11081-020-09502-1)).
All implemented specialized intrinsic functions can be found at `doc/implementedFunctions/Implemented_functions.pdf`.

## How to cite

If you use MAiNGO, please cite the latest MAiNGO report:<br>
Bongartz, D., Najman, J., Sass, S., & Mitsos, A. (2018). MAiNGO - **M**cCormick-based **A**lgorithm for mixed-**i**nteger **N**onlinear **G**lobal **O**ptimization. Technical Report, Process Systems Engineering (AVT.SVT), RWTH Aachen University. [http://permalink.avt.rwth-aachen.de/?id=729717](http://permalink.avt.rwth-aachen.de/?id=729717).


## References

Bongartz, D., Najman, J., Sass, S., & Mitsos, A. (2018). [MAiNGO - **M**cCormick-based **A**lgorithm for mixed-**i**nteger **N**onlinear **G**lobal **O**ptimization](http://permalink.avt.rwth-aachen.de/?id=729717). *Technical Report*, Process Systems Engineering (AVT.SVT), RWTH Aachen University.<br><br>
Bongartz, D., & Mitsos, A. (2017a). [Deterministic global optimization of process flowsheets in a reduced space using McCormick relaxations](https://link.springer.com/article/10.1007/s10898-017-0547-4). *Journal of Global Optimization*, 69(4), 761-796.<br><br>
Bongartz, D., & Mitsos, A. (2017b). [Infeasible path global flowsheet optimization using McCormick relaxations](https://www.sciencedirect.com/science/article/pii/B9780444639653501070). In *Computer Aided Chemical Engineering* (Vol. 40, pp. 631-636). Elsevier.<br><br>
Bongartz, D., & Mitsos, A. (2019). [Deterministic global flowsheet optimization: Between equation-oriented and sequential-modular methods](https://aiche.onlinelibrary.wiley.com/doi/full/10.1002/aic.16507). *AIChE Journal*, 65(3), 1022-1034.<br><br>
Bongartz, D., Najman, J., & Mitsos, A. (2020). [Deterministic global optimization of steam cycles using the IAPWS-IF97 model](https://link.springer.com/article/10.1007/s11081-020-09502-1). *Optimization & Engineering*, in press.<br><br>
Huster, W. R., Schweidtmann, A. M., & Mitsos, A. (2019a). [Impact of accurate working fluid properties on the globally optimal design of an organic Rankine cycle](https://www.sciencedirect.com/science/article/pii/B9780128185971500680). In *Computer Aided Chemical Engineering* (Vol. 47, pp. 427-432). Elsevier.<br><br>
Huster, W. R., Schweidtmann, A. M., & Mitsos, A. (2019b). [Working fluid selection for organic rankine cycles via deterministic global optimization of design and operation](https://link.springer.com/article/10.1007/s11081-019-09454-1). *Optimization and Engineering*, 1-20.<br><br>
Najman, J., & Mitsos, A. (2016). [Convergence order of McCormick relaxations of LMTD function in heat exchanger networks](https://www.sciencedirect.com/science/article/pii/B9780444634283502721). In *Computer Aided Chemical Engineering* (Vol. 38, pp. 1605-1610). Elsevier.<br><br>
Najman, J., Bongartz, D., & Mitsos, A. (2019). [Relaxations of thermodynamic property and costing models in process engineering](https://www.sciencedirect.com/science/article/abs/pii/S0098135419309494). *Computers & Chemical Engineering*, 130, 106571.<br><br>
Rall, D., Menne, D., Schweidtmann, A. M., Kamp, J., von Kolzenberg, L., Mitsos, A., & Wessling, M. (2019). [Rational design of ion separation membranes](https://www.sciencedirect.com/science/article/pii/S0376738818324293). *Journal of membrane science*, 569, 209-219.<br><br>
Rall, D., Schweidtmann, A. M., Aumeier, B. M., Kamp, J., Karwe, J., Ostendorf, K., Mitsos, A., & Wessling, M. (2020). [Simultaneous rational design of ion separation membranes and processes](https://doi.org/10.1016/j.memsci.2020.117860 ). *Journal of Membrane Science*, 117860.<br><br>
Rall, D., Schweidtmann, A. M., Kruse, M.,Evdochenko, E., Mitsos, A., & Wessling, M. (2020). [Multi-scale membrane process optimization with high-fidelity ion transport models through machine learning](https://doi.org/10.1016/j.memsci.2020.118208). *Journal of Membrane Science*, 118208.<br><br>
Schäfer, P., Schweidtmann, A. M., Lenz, P. H., Markgraf, H. M., & Mitsos, A. (2020). [Wavelet-based grid-adaptation for nonlinear scheduling subject to time-variable electricity prices](https://doi.org/10.1016/j.compchemeng.2019.106598). *Computers & Chemical Engineering*, 132, 106598.<br><br>
Schweidtmann, A. M., & Mitsos, A. (2018) [Deterministic Global Optimization with Artificial Neural Networks Embedded](https://link.springer.com/article/10.1007/s10957-018-1396-0). *Journal of Optimization Theory and Applications*, 180, 925–948.<br><br>
Schweidtmann, A. M., Huster, W. R., Lüthje, J. T., & Mitsos, A. (2019a). [Deterministic global process optimization: Accurate (single-species) properties via artificial neural networks](https://www.sciencedirect.com/science/article/abs/pii/S009813541830886X). *Computers & Chemical Engineering*, 121, 67-74.<br><br>
Schweidtmann, A. M., Bongartz, D., Huster, W. R., & Mitsos, A. (2019b). [Deterministic Global Process Optimization: Flash Calculations via Artificial Neural Networks](https://www.sciencedirect.com/science/article/pii/B9780128186343501570). In *Computer Aided Chemical Engineering* (Vol. 46, pp. 937-942). Elsevier.<br><br>

/**********************************************************************************
 * Copyright (c) 2019-2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "babUtils.h"


/**
*   @namespace maingo
*   @brief namespace holding all essentials of MAiNGO
*/
namespace maingo {


/**
* @enum SETTING_NAMES
* @brief Enum for representing the setting names and making the tracking of set settings easier
*/
enum SETTING_NAMES {
    // The first name has to be 1 and the names have to be increasing (in numbering)
    EPSILONA = 1,                /*!< absolute optimality tolerance */
    EPSILONR,                    /*!< relative optimality tolerance */
    DELTAINEQ,                   /*!< absolute inequality tolerance */
    DELTAEQ,                     /*!< absolute equality tolerance */
    RELNODETOL,                  /*!< relative minimal node size tolerance */
    INFTY,                       /*!< infinity value */
    TARGETLOWERBOUND,            /*!< target value for LBD at which MAiNGO terminates */
    TARGETUPPERBOUND,            /*!< target value for UBD at which MAiNGO terminates */
    BAB_MAXNODES,                /*!< max number of nodes */
    BAB_MAXITERATIONS,           /*!< max number of iterations */
    MAXTIME,                     /*!< max CPU time */
    MAXWTIME,                    /*!< max wall time */
    CONFIRMTERMINATION,          /*!< whether to confirm termination */
    TERMINATEONFEASIBLEPOINT,    /*!< whether to terminate once a feasible point was found */
    PRE_MAXLOCALSEARCHES,        /*!< max local searches in pre-processing */
    PRE_OBBTMAXROUNDS,           /*!< max number of obbt rounds in pre-processing */
    PRE_PUREMULTISTART,          /*!< whether to do a pure multistart */
    BAB_NODESELECTION,           /*!< node selection heuristic */
    BAB_BRANCHVARIABLE,          /*!< branching variable heuristic */
    BAB_ALWAYSSOLVEOBBT,         /*!< whether to always solve obbt */
    BAB_OBBTDECAYCOEFFICIENT,    /*!<parameter for depth-dependent OBBT*/
    BAB_PROBING,                 /*!< whether to do probing */
    BAB_DBBT,                    /*!< whether to do dbbt */
    BAB_CONSTRAINTPROPAGATION,   /*!< whether to do constraint propagation */
    LBP_SOLVER,                  /*!< lower bounding solver */
    NUM_SUBDOMAINS,              /*!< parameter for subdomain LBP solver: the number of subdomains*/
    INTERVAL_ARITHMETIC,         /*!< option for subdomain LBP solver: the type of interval arithmetic, Natural Interval Extension or Centered Form*/
    SUBINTERVAL_BRANCH_STRATEGY, /*!< option for subdomain LBP solver: the strategy for partitioning subintervals, uniform partitioning or largest partioning*/
    THREADS_PER_BLOCK,           /*!< option for subdomain LBP solver: the number of threads in one block (set in cuda)*/
    CENTER_STRATEGY,             /*!< option for subdomain LBP solver: the strategy used for calculating centers, midpoint or the optimal center*/
    MIN_BRANCHING_PER_DIM,       /*!< option for subdomain LBP solver: the minum number of partitions on each dimension. By now only for checking whether to perform domain partitioning*/
    LBP_LINPOINTS,               /*!< linearization point strategy */
    LBP_SUBGRADIENTINTERVALS,    /*!< whether to use subgradient intervals heuristic */
    LBP_OBBTMINIMPROVEMENT,      /*!< minimal obbt improvement */
    LBP_ACTIVATEMORESCALING,     /*!< number of consecutive iterations with no lbd imrovement needed to activate more aggressive scaling in LP solver (e.g., CPLEX) */
    LBP_ADDAUXILIARYVARS,        /*!< whether to add auxiliary variables for common factors in the lower bounding problem */
    LBP_MINFACTORSFORAUX,        /*!< minimum number of common factors to add an auxiliary variable */
    LBP_MAXNUMBEROFADDEDFACTORS, /*!< maximum number of added factor as auxiliaries */
    MC_MVCOMPUSE,                /*!< whether to use multivariate mccormick */
    MC_MVCOMPTOL,                /*!< mccormick computational tolerance */
    MC_ENVELTOL,                 /*!< mccormick envelope computation tolerance */
    UBP_SOLVERPRE,               /*!< upper bounding solver in pre-processing */
    UBP_MAXSTEPSPRE,             /*!< max steps for upper bounding solver in pre-processing */
    UBP_MAXTIMEPRE,              /*!< max time for upper bounding solver in pre-processing */
    UBP_SOLVERBAB,               /*!< upper bounding solver in B&B */
    UBP_MAXSTEPSBAB,             /*!< max steps for upper bounding solver in B&B */
    UBP_MAXTIMEBAB,              /*!< max time for upper bounding solver in B&B */
    UBP_IGNORENODEBOUNDS,        /*!< whether to ignore bounds in upper bounding */
    EC_NPOINTS,                  /*!< number of points on the Pareto front in epsilon-constraint method */
    LBP_VERBOSITY,               /*!< lower bounding verbosity */
    UBP_VERBOSITY,               /*!< upper bounding verbosity */
    BAB_VERBOSITY,               /*!< b&b verbosity */
    BAB_PRINTFREQ,               /*!< frequency of printed b&b iterations */
    BAB_LOGFREQ,                 /*!< frequency of written b&b iterations */
    OUTSTREAMVERBOSITY,          /*!< verbosity for outstream */
    WRITECSV,                    /*!< whether to write csv */
    WRITEJSON,                   /*!< whether to write json */
    writeResultFile,             /*!< whether to write an additional log file containing non-standard information about the problem */
    WRITETOLOGSEC,               /*!< write to log/csv every x seconds */
    PRE_PRINTEVERYLOCALSEARCH,   /*!< whether to print every local search */
    WRITETOOTHERLANGUAGE,        /*!< write a file in a different modeling language */
    GROWING_APPROACHCHOSEN,      /*!< which approach of the B&B algorithm with growing datasets to use */
    GROWING_MAXTIMEPOST,         /*!< max time for heuristic B&B algorithm with growing datasets in post-processing */
    GROWING_USERESAMPLING,       /*!< whether to use resampling for calculating the lower bound based on the initial dataset when using the B&B algorithm with growing datasets */
    GROWING_SHUFFLEDATA,         /*!< whether to shuffle data such that data points are picked randomly when using the B&B algorithm with growing datasets */
    GROWING_RELATIVESIZING,      /*!< whether to size of each reduced dataset is given relatively to size of full dataset or given in absolute numbers */
    GROWING_INITPERCENTAGE,      /*!< relative size of initial dataset (= smallest reduced dataset) compared to full dataset */
    GROWING_AUGMENTPERCENTAGE,   /*!< percentage of full dataset to be added when augmenting */
    GROWING_MAXSIZE,             /*!< relative tolerance for considering dataset as full dataset */
    GROWING_AUGMENTRULE,         /*!< choose augmentation rule */
    GROWING_AUGMENTFREQ,         /*!< frequency of augmenting dataset (regarding depth of nodes) */
    GROWING_AUGMENTWEIGHT,       /*!< weighting factor of heuristic lower bound, see augmentation rule SCALING */
    GROWING_AUGMENTTOL,          /*!< absolute and relative tolerance of lower bound, see augmentation rule TOL */
    TS_USELBS,                   /*!< use lower bounding solvers for two-stage problems */
    TS_USEUBS,                   /*!< use upper bounding solvers for two-stage problems */
    TS_POBBT,                    /*!< whether to use parallel OBBT for two-stage problems */
    TS_STRONGBRANCHINGTHRESHOLD, /*!< percentage of the best strong branching score above which scenarios may be selected for branching in two-stage problems */
    TS_MAXBRANCHINGPOWER,        /*!< maximum branching power for two-stage problems, i.e., at most 2 ^ TS_MAXBRANCHINGPOWER nodes are created */
    TS_ORTHANTUBD,               /*!< whether to perform UBD for each orthant separately */
    UNKNOWN_SETTING = 500 /*!< unknown setting */
};

/**
* @enum VERB
* @brief Enum for controlling the output level of solvers (i.e., how much should be printed on the screen and, possibly, to the log file).
*/
enum VERB {
    VERB_NONE = 0,    //!< (=0): Print no output whatsoever.
    VERB_NORMAL,      //!< (=1): For BranchAndBound, this means that regular output on solution progress is printed according to the specified print frequency, as well as when the incumbent is updated. For LowerBoundingSolver and UpperBoundingSolver, only critical output is given (e.g., important warnings).
    VERB_ALL          //!< (=2): Highest output level (very noisy!).
};

/**
* @enum LOGGING_DESTINATION
* @brief Enum for controlling where logging information of MAiNGO should be written.
*/
enum LOGGING_DESTINATION {
    LOGGING_NONE = 0,          //!< (=0): Do not print or write any logging information
    LOGGING_OUTSTREAM,         //!< (=1): Print only to selected output stream. The stream can be selected via \ref maingo::MAiNGO::set_output_stream "set_output_stream"
    LOGGING_FILE,              //!< (=2): Write to a log file only. The log filename can be set via \ref maingo::MAiNGO::set_log_file_name "set_log_file_name"
    LOGGING_FILE_AND_STREAM    //!< (=3): Print to output stream AND write the same information to log file
};

/**
* @enum WRITING_LANGUAGE
* @brief Enum for representing the modeling language in which MAiNGO is supposed to write the current model to a file.
*/
enum WRITING_LANGUAGE {
    LANG_NONE = 0,    //!< (=0): Do not write the current model to a file
    LANG_ALE,         //!< (=1): Write the current model to a file using ALE syntax
    LANG_GAMS         //!< (=2): Write the current model to a file using GAMS syntax
};


/**
* @enum AUGMENTATION_APPROACH
* @brief Enum for controlling the augmentation rule used in the B&B algorithm with growing datasets
*/
enum AUGMENTATION_RULE {
    AUG_RULE_CONST = 0,    //!< (=0): Augment every growing_augmentFreq by growing_augmentPercentage data points
    AUG_RULE_SCALING,      //!< (=1): Augment if linear scaling of reduced LB to full LB suggests pruning
    AUG_RULE_OOS,          //!< (=2): Augment if UB is smaller than out-of-sample LB
    AUG_RULE_COMBI,        //!< (=3): Augment if UB is smaller than approximated LB which is a combination of reduced and out-of-sample LB
    AUG_RULE_TOL,          //!< (=4): Augment if UB is within tolerance of the lower bound used for pruning. Currently the same value is used for the absolute and relative tolerance
    AUG_RULE_SCALCST,      //!< (=5): Augment if SCALING or CONST is triggered
    AUG_RULE_OOSCST,       //!< (=6): Augment if OOS or CONST is triggered
    AUG_RULE_COMBICST,     //!< (=7): Augment if COMBI or CONST is triggered
    AUG_RULE_TOLCST        //!< (=8): Augment if TOL or CONST is triggered
};


/**
* @enum GROWING_APPROACH
* @brief Enum for controlling the approach of the B&B algorithm with growing datasets to be used
*
* Important note: When adding new approaches, ensure correct usage of this enum throughout code. As is, we exploit that DETERMINISTIC and
*                 SSEHEURISTIC use the same objective as well as that SSEHEURISTIC and MSEHEURISTIC use the same lower bound for pruning.
*/
enum GROWING_APPROACH {
    GROW_APPR_DETERMINISTIC = 0, //!< (=0): Deterministic approach, i.e., minimize summed squared error and use reduced lower bound for pruning
    GROW_APPR_SSEHEURISTIC,      //!< (=1): SSE heuristic, i.e., minimize summed squared error and use combined lower bound for pruning
    GROW_APPR_MSEHEURISTIC       //!< (=2): MSE heuristic, i.e., minimize mean squared error and use combined lower bound for pruning
};


/**
*   @namespace maingo::lbp
*   @brief namespace holding all essentials of the lower bounding solver
*/
namespace lbp {


/**
    * @enum LBP_SOLVER
    * @brief Enum for selecting the STRATegy so be used for solving the lower bounding problems
    */
enum LBP_SOLVER {
    LBP_SOLVER_MAiNGO = 0,    //!< (=0): MAiNGO internal lower bounding solver consisting of linearizing the objective function at only 1 point and minimizing the linearization over box constraints
    LBP_SOLVER_INTERVAL,      //!< (=1): solution of lower bounding problems using only interval based relaxations
    LBP_SOLVER_CPLEX,         //!< (=2): solution of lower bounding linear programs using CPLEX
    LBP_SOLVER_CLP,           //!< (=3): solution of lower bounding linear programs using CLP
    LBP_SOLVER_GUROBI,        //!< (=4): solution of lower bounding linear programs using Gurobi
    LBP_SOLVER_SUBDOMAIN      //!< (=5): solution of lower bounding problems using interval arithmetic with subdomains
};

/**
    * @enum LINP
    * @brief Enum for selecting the Linearization Points to be used in constructing affine relaxations.
    */
enum LINP {
    LINP_MID = 0,          //!< (=0) : Linearize only at the midpoint of the current node */
    LINP_INCUMBENT,        //!< (=1) : Linearize at the incumbent value if it is in the current interval, else linearize at mid point, if using the subgradient interval heuristic, the heuristic also linearizes each operation at the incumbent if possible
    LINP_KELLEY,           //!< (=2) : Linearize at points determined via an adapted version of Kelley's algorithm, each function is treated individually
    LINP_SIMPLEX,          //!< (=3) : Linearize at mid point + (n+1)/2 points given as vertices of the (n+1) simplex where n is the dimension of the problem
    LINP_RANDOM,           //!< (=4) : Linearize at mid point + (n+1)/2 random points
    LINP_KELLEY_SIMPLEX    //!< (=5) : Linearize at mid point + (n+1)/2 points given as vertices of the (n+1) simplex where n is the dimension of the problem and then apply Kelleys algorithm
};


}    // end namespace lbp


/**
*   @namespace maingo::ubp
*   @brief namespace holding all essentials of the upper bounding solvers
*/
namespace ubp {


/**
    * @enum UBP_SOLVER
    * @brief Enum for selecting the STRATegy so be used for solving the upper bounding problems
    */
enum UBP_SOLVER {
    UBP_SOLVER_EVAL = 0,      //!< (=0): no optimization, simple function evaluation at solution point of LBP
    UBP_SOLVER_COBYLA,        //!< (=1): local optimization using COBYLA (derivative free solver within NLopt, uses linear approximations via simplex of nvar+1 points)
    UBP_SOLVER_BOBYQA,        //!< (=2): local optimization using BOBYQA (derivative free unconstrained solver in NLopt, constructs quadratic approximations; constraints are moved to the objective via augmented Lagrangian method)
    UBP_SOLVER_LBFGS,         //!< (=3): local optimization using LBFGS (lower-storage BFGS algorithm (i.e., gradient-based) for unconstrained optimization within NLopt; constraints are moved to the objective via augmented Lagrangian method)
    UBP_SOLVER_SLSQP,         //!< (=4): local optimization using SLSQP (SQP solver within NLopt)
    UBP_SOLVER_IPOPT,         //!< (=5): local optimization using Ipopt (using the exact Hessian for problems with at most 50 variables, else using L-BFGS)
    UBP_SOLVER_KNITRO,        //!< (=6): local optimization using Knitro (using the exact Hessian)
    UBP_SOLVER_CPLEX = 42,    //!< (=42): optimization using CPLEX. Called only for (MI)LPs and (MI)QCPs.
    UBP_SOLVER_CLP,           //!< (=43): optimization using CLP. Called only for LPs.
    UBP_SOLVER_GUROBI         //!< (=44): optimization using Gurobi. Called only for (MI)LPs and (MI)QCPs.
};


}    // end namespace ubp


/**
* @struct Settings
* @brief Struct for storing settings for MAiNGO
*
* Contains settings for MAiNGO.
*
*/
struct Settings {

    /**
    * @name Tolerances
    */
    /**@{*/
    double epsilonA   = 1.0e-2;    //!< Absolute optimality tolerance, i.e., termination when (UBD-LBD) < BAB_epsilon_a
    double epsilonR   = 1.0e-2;    //!< Relative optimality tolerance, i.e., termination when (UBD-LBD) < BAB_epsilon_r * UBD
    double deltaIneq  = 1.0e-6;    //!< Absolute feasibility tolerance for inequality constraints, i.e., constraint is considered satisfied if gi_(x)<=UBP_delta_ineq
    double deltaEq    = 1.0e-6;    //!< Absolute feasibility tolerance for equality constraints, i.e., constraint is considered satisfied if |hi_(x)|<=UBP_delta_eq
    double relNodeTol = 1.0e-9;    //!< Relative tolerance for minimum node size. Nodes are discarded if in every dimension their width gets below this tolerance times the original width. In this case, global optimality to the desired optimality tolerances may not be reached.
    /**@}*/

    /**
    * @name Other termination settings
    */
    /**@{*/
    unsigned BAB_maxNodes         = std::numeric_limits<unsigned>::max();    //!< Maximum number of nodes (i.e., solver terminates when more than BAB_maxnodes are held in memory; used to avoid excessive branching)
    unsigned BAB_maxIterations    = std::numeric_limits<unsigned>::max();    //!< Maximum number of iterations (i.e., maximum number of nodes visited in the Branch-and-Bound tree)
    unsigned maxTime              = 86400 /*=24h*/;                          //!< CPU time limit in seconds
    unsigned maxwTime             = 86400 /*=24h*/;                          //!< Wall time limit in seconds
    bool confirmTermination       = false;                                   //!< Whether to ask the user before terminating when reaching time, node, or iteration limits
    bool terminateOnFeasiblePoint = false;                                   //!< Whether to terminate as soon as the first feasible point was found (no guarantee of global or local optimality!)
    double targetLowerBound       = std::numeric_limits<double>::max();      //!< Target value for the lower bound on the optimal objective. MAiNGO terminates once LBD>=targetLowerBound  (no guarantee of global or local optimality!)
    double targetUpperBound       = -std::numeric_limits<double>::max();     //!< Target value for the upper bound on the optimal objective. MAiNGO terminates once UBD<=targetUpperBound  (no guarantee of global or local optimality!)
    double infinity               = std::numeric_limits<double>::max();      //!< User definition of infinity (used to initialize UBD and LBD) [currently cannot be set by the user via set_option]
    /**@}*/

    /**
    * @name Output
    */
    /**@{*/
    VERB BAB_verbosity                     = VERB_NORMAL;                //!< How much output to print from Branch & Bound solver. See documentation of \ref maingo.VERB for possible values.
    VERB LBP_verbosity                     = VERB_NORMAL;                //!< How much output to print from Lower Bounding Solver. See documentation of \ref maingo.VERB for possible values.
    VERB UBP_verbosity                     = VERB_NORMAL;                //!< How much output to print from Upper Bounding Solver. See documentation of \ref maingo.VERB for possible values.
    unsigned BAB_printFreq                 = 100;                        //!< After how many iterations to print progress on screen (additionally, a line is printed when a new incumbent is found)
    unsigned BAB_logFreq                   = 100;                        //!< Like BAB_printFreq, but for log
    LOGGING_DESTINATION loggingDestination = LOGGING_FILE_AND_STREAM;    //!< Where to print or write the output. See documentation of \ref maingo.LOGGING_DESTINATION for possible values.
    unsigned writeToLogSec                 = 1800;                       //!< Write to log file after a given ammount of CPU seconds
    bool writeResultFile                   = true;                       //!< Whether to write an additional file containing non-standard information about the solved model
    bool writeCsv                          = false;                      //!< Whether to write csv-log files (named bab_statistics.csv and bab_iterations.csv).
    bool writeJson                         = false;                      //!< Whether to write a json-log file (named bab.json).
    bool PRE_printEveryLocalSearch         = false;                      //!< Whether to print every run during multistart at the root node
    WRITING_LANGUAGE modelWritingLanguage  = LANG_NONE;                  //!< In what modeling language to write the current model to a file in.  See documentation of \ref maingo.WRITING_LANGUAGE for possible values.
    /**@}*/

    /**
    * @name Pre-processing
    */
    /**@{*/
    unsigned PRE_maxLocalSearches = 3;        //!< Number of local searches in the multistart heuristic during preprocessing at the root node
    unsigned PRE_obbtMaxRounds    = 10;       //!< Maximum number of rounds of optimization-based range reduction (OBBT; cf., e.g., Gleixner et al., J. Glob. Optim. 67 (2017) 731; maximizing and minimizing each variable subject to relaxed constraints) at the root node. If >=1 and a feasible point is found during multistart, one round of OBBT using an objective cut (f_cv<=UBD) is conducted as well.
    bool PRE_pureMultistart       = false;    //!< Whether to perform a multistart only. A B&B tree will not be constructed and no lower bounding problems will be solved
    /**@}*/

    /**
    * @name B&B settings - Tree management
    */
    /**@{*/
    babBase::enums::NS BAB_nodeSelection  = babBase::enums::NS_BESTBOUND;    //!< How to select the next node to process. See documentation of babBase::enums::NS for possible values.
    babBase::enums::BV BAB_branchVariable = babBase::enums::BV_RELDIAM;      //!< Which dimension to branch in for the current node. See documentation of babBase::enums::BV for possible values.
    /**@}*/

    /**
    * @name B&B settings - Range reduction
    */
    /**@{*/
    bool BAB_alwaysSolveObbt        = true;     //!< Whether to solve OBBT (feasibility- and, once a feasible point has been found, also optimality-based) at every BaB node.
    double BAB_obbtDecayCoefficient = 0.;       //!< Parameter that influences the exponential distribution with which the probability that OBBT is preformed decays with increasing depth of the B&B tree.
    bool BAB_dbbt                   = true;     //!< Whether to do a single round of duality based bound tightening (DBBT, cf. Ryoo&Sahinidis, Comput. Chem. Eng. 19 (1995) 551). If false, no DBBT is used. If true, multipliers from CPLEX are used to tighten bounds (essentially for free). we tried additional rounds but without reasonable improvement.
    bool BAB_probing                = false;    //!< Whether to do probing (cf. Ryoo&Sahinidis, Comput. Chem. Eng. 19 (1995) 551) at every node (can only be done if BAB_DBBT_maxrounds>=1)
    bool BAB_constraintPropagation  = true;     //!< Whether to do constraint propagation. If false, no constraint propagation is executed.
    /**@}*/

    /**
    * @name LBP Settings
    */
    /**@{*/
#ifdef HAVE_CPLEX
    lbp::LBP_SOLVER LBP_solver = lbp::LBP_SOLVER_CPLEX;     //!< Solver for solution of (mixed-integer) linear lower bounding problems. It also sets the solver when solving purely (mixed-integer) quadratic/linear problems. See documentation of \ref lbp::LBP_SOLVER for possible values
#elif HAVE_GUROBI
    lbp::LBP_SOLVER LBP_solver = lbp::LBP_SOLVER_GUROBI;    //!< Solver for solution of (mixed-integer) linear lower bounding problems. It also sets the solver when solving purely (mixed-integer) quadratic/linear problems. See documentation of \ref lbp::LBP_SOLVER for possible values
#else
    lbp::LBP_SOLVER LBP_solver = lbp::LBP_SOLVER_CLP;       //!< Solver for solution of (mixed-integer) linear lower bounding problems. It also sets the solver when solving purely (mixed-integer) quadratic/linear problems. See documentation of \ref lbp::LBP_SOLVER for possible values
#endif
    int Num_subdomains                   = 1024;             //!< The number of subdomains used in subdomain LBP solver.
    int Interval_arithmetic              = 1;                //!< The type of interval arithmetic used: 1 for centered form, 0 for natural interval extension. 
    int Subinterval_branch_strategy      = 0;                //!< The branching strategy used for generating subintervals: 0 for partition equally, 1 for partition on the largest dimension. 
    int Center_strategy                  = 0;                //!< The strategy used to calculate centered in Centered Form. 0 for midpoint (Mean Value Form), 1 for the optimal center.   
    int MIN_branching_per_dim            = 2;                //!< The minum number of partitions on each dimension. By now only for checking whether to perform domain partitioning.
    int Threads_per_block                = 32;               //!< The number of threads in each block (cuda). No need to set if the CPU version of Subdomain Lower Bounding is used.   

    lbp::LINP LBP_linPoints              = lbp::LINP_MID;    //!< At which points to linearize for affine relaxation. See documentation of lbp::LINP for possible values
    bool LBP_subgradientIntervals        = true;             //!< Whether to use the heuristic to improve McCormick relaxations by tightening the range of each factor with the use of subgradients (cf. Najman & Mitsos, JOGO 2019)
    double LBP_obbtMinImprovement        = 0.01;             //!< How much improvement needs to be achievable (relative to initial diameter) to conduct OBBT for a variable
    unsigned LBP_activateMoreScaling     = 10000;            //!< Number of consecutive iterations without LBD improvement needed to activate more aggressive scaling in LP solver (e.g., CPLEX)
    bool LBP_addAuxiliaryVars            = false;            //!< Whether to add auxiliary variables for common factors in the lower bounding DAG/problem
    unsigned LBP_minFactorsForAux        = 2;                //!< Minimum number of common factors to add an auxiliary variable
    unsigned LBP_maxNumberOfAddedFactors = 1;                //!< Maximum number of added factor as auxiliaries
    /**@}*/

    /**
    * @name MC++ settings
    */
    /**@{*/
    bool MC_mvcompUse   = true;      //!< Whether to use multivariate composition theorem for computing McCormick relaxations  (see MC++ documentation for details)
    double MC_mvcompTol = 1.0e-9;    //!< Tolerance used in the multivariate composition theorem for computing McCormick relaxations (see MC++ documentation for details)
    double MC_envelTol  = 1.0e-9;    //!< Tolerance for computing the envelopes of intrinsic functions (see MC++ documentation for details)
    /**@}*/

    /**
    * @name UBP Settings
    */
    /**@{*/
    ubp::UBP_SOLVER UBP_solverPreprocessing = ubp::UBP_SOLVER_IPOPT;    //!< Solver to be used during pre-processing (i.e., multistart). See documentation of ubp::UBP_SOLVER for possible values.
    unsigned UBP_maxStepsPreprocessing      = 3000;                     //!< Maximum number of steps the local solver is allowed to take in each local run during multistart in pre-processing.
    double UBP_maxTimePreprocessing         = 100.0;                    //!< Maximum CPU time the local solver is allowed to take in each local run during multistart in pre-processing. Usually, this should only be a fall-back option to prevent truly getting stuck in local solution.
    ubp::UBP_SOLVER UBP_solverBab           = ubp::UBP_SOLVER_SLSQP;    //!< Solver to be used during Branch-and-Bound. See documentation of ubp::UBP_SOLVER for possible values.
    unsigned UBP_maxStepsBab                = 3;                        //!< Maximum number of steps the local solver is allowed to take at each BaB node.
    double UBP_maxTimeBab                   = 10.0;                     //!< Maximum CPU time the local solver is allowed to take at each BaB node. Usually, this should only be a fall-back option to prevent truly getting stuck in local solution.
    bool UBP_ignoreNodeBounds               = false;                    //!< Flag indicating whether the UBP solvers should ignore the box constraints of the current node during the B&B (and consider only the ones of the root node instead).
    /**@}*/

    /**
    * @name Two-Stage settings
    */
    /**@{*/
    bool TS_useLowerBoundingSubsolvers = true;    //!< Whether to use separate subsolvers for lower bounding of problems given in two-stage formulation
    bool TS_useUpperBoundingSubsolvers = true;    //!< Whether to use separate subsolvers for upper bounding of problems given in two-stage formulation
    bool TS_parallelOBBT = true;                  //!< Whether to use parallelizable subproblems also for OBBT (otherwise use 'standard' LP relaxation)
    double TS_strongBranchingThreshold = 1;       //!< Percentage of the best strong branching score above which scenarios may be selected for branching in two-stage problems
    unsigned int TS_maxBranchingPower  = 1;       //!< Maximum branching power for two-stage problems, i.e., at most 2 ^ TS_maxBranchinPower nodes are created
    /**@}*/

    /**
    * @name Epsilon-constraint settings
    */
    /**@{*/
    unsigned EC_nPoints = 10;    //!< Number of points on the Pareto front to be computed in epsilon-constraint method (only available via the C++ API)
    /**@}*/

    /**
    * @name Settings of B&B algorithm with growing datasets
    */
    /**@{*/
    GROWING_APPROACH growing_approach     = GROW_APPR_DETERMINISTIC;    //!< Flag indicating which approach of the B&B algorithm with growing datasets to use.
    double growing_maxTimePostprocessing  = 60.;                        //!< Maximum CPU time for post-processing the heuristic B&B algorithm with growing datasets.
    bool growing_useResampling            = false;                      //!< Flag indicating whether to use resampling for the lower bound based on the initial dataset.
    bool growing_shuffleData              = true;                       //!< Flag indicating whether to pick the data points randomly.
    bool growing_relativeSizing           = true;                       //!< Flag indicating whether the size of each reduced dataset is given relatively to the size of the full dataset.
    double growing_maxSize                = 0.9;                        //!< Dataset of this relative size to full dataset considered as full dataset.
    double growing_initPercentage         = 0.1;                        //!< Relative size of initial dataset (= smallest reduced dataset) compared to full dataset.
    double growing_augmentPercentage      = 0.25;                       //!< How many data points to be added when augmenting (fraction of the size of the full data).
    AUGMENTATION_RULE growing_augmentRule = AUG_RULE_TOLCST;            //!< Rule when to augment the dataset (default must be valid for any objective mode).
    unsigned growing_augmentFreq          = 10;                         //!< Augment dataset of all nodes whose depths is multiple of this frequency.
    double growing_augmentWeight          = 1.;                         //!< Weight of heuristic lower bound calculated in augmentation rule SCALING.
    double growing_augmentTol             = 1.e-1;                      //!< Absolute and relative tolerance of lower bound used in augmentation rule TOL.
    /**@}*/
};


}    // end namespace maingo

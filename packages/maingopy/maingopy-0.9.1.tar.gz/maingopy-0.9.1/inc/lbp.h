/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "MAiNGOdebug.h"
#include "constraint.h"
#include "intervalLibrary.h"
#include "lbpDagObj.h"
#include "logger.h"
#include "returnCodes.h"
#include "settings.h"
#include "TwoStageModel.h"

#include "babNode.h"
#include "babUtils.h"

#include <list>
#include <memory>
#include <string>
#include <vector>


namespace maingo {


namespace lbp {


/**
 * @enum OBBT
 * @brief Enum for communicating whether Optimization-Based Bound Tightening should consider only feasibility or also optimality
 */
enum OBBT {
    OBBT_FEAS = 0, /*!< Consider feasibility only, i.e., maximize and minimize each variable only subject to the relaxed (and linearized) constraints */
    OBBT_FEASOPT   /*!< Consider both feasibility and optimality, i.e., including the objective function cut f_cv<=UBD */
};


/**
 * @struct LbpDualInfo
 * @brief Container for information from the LBP that is needed in DBBT and probing, used for communicating the results via bab.
 *
 */
struct LbpDualInfo {
    std::vector<double> multipliers; /*!< Vector containing the multipliers of bound constraints for each variable in the LBP */
    double lpLowerBound;             /*!< Lower bound obtained from the solution of the lower bounding LP. This may be different from the lower bound returned by solve_LBP in case the interval bound is better than that obtained from the LP. */
};


/**
 * @class LowerBoundingSolver
 * @brief Wrapper for handling the lower bounding problems as well as optimization-based bounds tightening (OBBT)
 *
 * This class provides an interface between the Branch-and-Bound solver, the problem definition used by BigMC, and the actual sub-solver used for lower bounding (currently CPLEX).
 * It manages the CPLEX problem and solver instance(s), evaluates the Model using MC++ to obtain relaxations and subgradients, constructs the respective LP relaxations, and calls CPLEX to solve either the lower bounding problems (LBP) or OBBT as queried by the B&B solver.
 */
class LowerBoundingSolver {
  
  template<class subsolver_class>
  friend class LbpTwoStage;

  public:
    /**
     * @brief Constructor, stores information on the problem and constructs an own copy of the directed acyclic graph
     *
     * @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
     * @param[in] DAGvars are the variables corresponding to the DAG
     * @param[in] DAGfunctions are the functions corresponding to the DAG
     * @param[in] variables is a vector containing the optimization variables
     * @param[in] variableIsLinear is a vector containing information about which variables occur only linearly
     * @param[in] nineqIn is the number of inequality constraints
     * @param[in] neqIn is the number of equality
     * @param[in] nineqRelaxationOnlyIn is the number of inequality for use only in the relaxed problem
     * @param[in] neqRelaxationOnlyIn is the number of equality constraints for use only in the relaxed problem
     * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
     * @param[in] settingsIn is a pointer to the MAiNGO settings
     * @param[in] loggerIn is a pointer to the MAiNGO logger object
     * @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
     */
    LowerBoundingSolver(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
                        const std::vector<babBase::OptimizationVariable> &variables, const std::vector<bool>& variableIsLinear,
                        const unsigned nineqIn, const unsigned neqIn,
                        const unsigned nineqRelaxationOnlyIn, const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn,
                        std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn);

    /**
     * @brief Virtual destructor, only needed to make sure the correct destructor of the derived classes is called
     */
    virtual ~LowerBoundingSolver(){};

    /**
     * @brief Function called by B&B solver for solving the lower bounding problem on the current node
     *
     * @param[in] currentNode is the B&B node for which the lower bounding problem should be solved
     * @param[out] lowerBound is the lower bound on the optimal objective value obtained for the current node
     * @param[out] solutionPoint is the point at which lowerBound was achieved
     * @param[out] dualInfo is a struct containing information from the LP solver needed for DBBT and probing
     * @return Return code, either RETCODE_FEASIBLE or RETCODE_INFEASIBLE
     */
    SUBSOLVER_RETCODE solve_LBP(const babBase::BabNode &currentNode, double &lowerBound, std::vector<double> &solutionPoint, LbpDualInfo &dualInfo);

#ifdef HAVE_GROWING_DATASETS
    /**
        * @brief Function for evaluating the lower bounding problem on the current node at a given point
        *
        * @param[in] currentNode is the B&B node for which the lower bounding problem should be build
        * @param[in] evaluationPoint is the point at which the lower bounding problem should be evaluated
        * @param[out] resultValue is the function value obtained from the respective evaluation
        */
    void evaluate_LBP(const babBase::BabNode& currentNode, const std::vector<double>& evaluationPoint, double& resultValue);
#endif    // HAVE_GROWING_DATASETS

    /**
     * @brief Function called by B&B solver for optimality-based range reduction (cf., e.g., Gleixner et al., J. Glob. Optim. 67 (2017) 731)
     *
     * @param[in,out] currentNode is the B&B node for which the lower bounding problem should be solved; if OBBT is successful in tightening bounds, currentNode will be modified accordingly
     * @param[in] currentUBD is the current upper bounds (i.e., incumbent objective value); It is used for the objective function cut if reductionType==OBBT_FEASOPT
     * @param[in] reductionType determines whether OBBT should include only feasibility or also optimality (i.e., an objective function cut f_cv<=currentUBD)
     * @param[in] includeLinearVars determines whether OBBT runs should also be conducted for variables occurring only linearly
     * @return Return code, see enum TIGHTENING_RETCODE
     */
    virtual TIGHTENING_RETCODE solve_OBBT(babBase::BabNode &currentNode, const double currentUBD, const OBBT reductionType, const bool includeLinearVars = false);

    /**
     * @brief Function called by B&B solver for constraint propagation. This function is virtual as it may be overwritten for certain LBD solvers.
     *        The defaults for constraint propagation are 10 rounds and at least 1% improvement
     *
     * @param[in,out] currentNode is the B&B node for which constraint propagation should be executed; if constraint propagation is successful in tightening bounds, currentNode will be modified accordingly
     * @param[in] currentUBD is the current upper bounds (i.e., incumbent objective value); it is used for the upper bound of the objective constraint interval
     * @param[in] pass is the maximum number of consecutive propagation runs
     * @return Return code, see enum TIGHTENING_RETCODE
     */
    virtual TIGHTENING_RETCODE do_constraint_propagation(babBase::BabNode &currentNode, const double currentUBD, const unsigned pass = 3);

    /**
     * @brief Function called by B&B solver for DBBT and probing (for each variable depending on where the LBD solution lies)
     *
     * @param[in,out] currentNode is the B&B node for which constraint propagation should be executed; if DBBT or probing are successful in tightening bounds, currentNode will be modified accordingly
     * @param[in] lbpSolutionPoint is a vector containing the solution point of the LBP for currentNode
     * @param[in] dualInfo is a struct containing information from the LP solved during LBP
     * @param[in] currentUBD is the current upper bounds (i.e., incumbent objective value); it is used for the upper bound in DBBT / probing
     * @return Return code, see enum TIGHTENING_RETCODE
     */
    virtual TIGHTENING_RETCODE do_dbbt_and_probing(babBase::BabNode &currentNode, const std::vector<double> &lbpSolutionPoint, const LbpDualInfo &dualInfo, const double currentUBD);

    /**
     * @brief Function called by the B&B solver to update the incumbent and the ID of the node currently holding it, which is needed by some linearization heuristics
     *
     * @param[in] incumbentBAB is a vector containing the current incumbent
     */
    virtual void update_incumbent_LBP(const std::vector<double> &incumbentBAB);

    /**
     * @brief Function called by the B&B solver to heuristically activate more scaling in the LBS
     */
    virtual void activate_more_scaling();

    /**
     * @brief Function called by the B&B in preprocessing in order to check the need for specific options, currently for subgradient intervals & CPLEX no large values
     *
     * @param[in] rootNode is the rootNode on which some options are checked
     */
    virtual void preprocessor_check_options(const babBase::BabNode &rootNode);

#ifdef HAVE_GROWING_DATASETS
    /**
	* @brief Function for changing objective in dependence of a (reduced) dataset
	*
	* @param[in] indexDataset is the index number of the (reduced) dataset to be used
	*/
    void change_growing_objective(const int indexDataset);

    /**
    * @brief Function for calling respective function of DagObj
    */
    void change_growing_objective_for_resampling();

    /**
	 * @brief Function for passing dataset vector and position of data points to solver
	 *
	 * @param[in] datasets is a pointer to a vector containing the size all available datasets
     * @param[in] indexFirstData is the position of the first objective per data in MAiNGO::_DAGfunctions
	 */
    void pass_data_position_to_solver(const std::shared_ptr<std::vector<unsigned int>> datasets, const unsigned int indexFirstData);

    /**
    * @brief Function for passing resampled initial dataset to solver
    *
    * @param[in] dataset is a pointer to the resampled dataset
    */
    void pass_resampled_dataset_to_solver(const std::shared_ptr<std::set<unsigned int>> datasetIn);

    /**
    * @brief Function for telling solver whether mean squared error or summed squared error is used as objective function
    *
    * @param[in] useMse is the boolean to be passed
    */
    void pass_use_mse_to_solver(const bool useMse);
#endif    //HAVE_GROWING_DATASETS

  protected:
    /**
     * @brief Calls the proper function for computing linearization points and modifying the coefficients of the LP problem
     *        The function is virtual, since other solver types, e.g., an interval solver does not need to always compute McCormick relaxations
     *
     * @param[in] currentNode is current node of the branch-and-bound tree
     * @return returns a LINEARIZATION_RETCODE defining whether the final problem was already solved/proven infeasible during linearization
     */
    virtual LINEARIZATION_RETCODE _update_LP(const babBase::BabNode &currentNode);

    /**
     * @brief Virtual function for setting the bounds of variables
     *
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     */
    virtual void _set_variable_bounds(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief Virtual auxiliary function for updating LP objective, i.e., processing the linearization of the objective function
     *
     * @param[in] resultRelaxation is the McCormick object holding relaxation of objective iObj at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iLin is the number of the linearization point
     * @param[in] iObj is the number of the objective function
     */
    virtual void _update_LP_obj(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iObj);

    /**
     * @brief Virtual auxiliary function for updating LP inequalities, i.e., processing the linearization of the inequality
     *
     * @param[in] resultRelaxation is the McCormick object holding relaxation of inequality iIneq at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iLin is the number of the linearization point
     * @param[in] iIneq is the number of the inequality function
     */
    virtual void _update_LP_ineq(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                 const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneq);

    /**
     * @brief Virtual auxiliary function for updating LP equalities, i.e., processing the linearization of the equality
     *
     * @param[in] resultRelaxationCv is the McCormick object holding relaxation of equality iEq at linearizationPoint used for the convex part
     * @param[in] resultRelaxationCc is the McCormick object holding relaxation of equality iEq at linearizationPoint used for the concave part
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iLin is the number of the linearization point
     * @param[in] iEq is the number of the equality function
     */
    virtual void _update_LP_eq(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                               const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEq);

    /**
     * @brief Virtual auxiliary function for updating LP relaxation only inequalities, i.e., processing the linearization of the relaxation only inequality
     *
     * @param[in] resultRelaxation is the McCormick object holding relaxation of relaxation only inequality iIneqRelaxationOnly at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iLin is the number of the linearization point
     * @param[in] iIneqRelaxationOnly is the number of the relaxation only inequality function
     */
    virtual void _update_LP_ineqRelaxationOnly(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                               const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqRelaxationOnly);

    /**
     * @brief Virtual auxiliary function for updating LP relaxation only equalities, i.e., processing the linearization of the relaxation only equality
     *
     * @param[in] resultRelaxationCv is the McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the convex part
     * @param[in] resultRelaxationCc is the McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the concave part
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iLin is the number of the linearization point
     * @param[in] iEqRelaxationOnly is the number of the relaxation only equality function
     */
    virtual void _update_LP_eqRelaxationOnly(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                             const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEqRelaxationOnly);


    /**
     * @brief Virtual auxiliary function for updating LP squash inequalities, i.e., processing the linearization of the squash inequality
     *        No tolerances are allowed for squash inequalities!
     *
     * @param[in] resultRelaxation is the McCormick object holding relaxation of inequality iIneqSquash at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iLin is the number of the linearization point
     * @param[in] iIneqSquash is the number of the inequality function
     */
    virtual void _update_LP_ineq_squash(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                        const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqSquash);
    /**
     * @brief Virtual auxiliary function for updating whole LP at once
     *
     * @param[in] resultRelaxation is the vector holding McCormick relaxations at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iLin is the number of the linearization point
     */
    void _update_whole_LP_at_linpoint(const std::vector<MC> &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                      const std::vector<double> &upperVarBounds, unsigned const &iLin);

    /**
     * @brief Virtual auxiliary function for updating LP objective, i.e., processing the linearization of the objective function for vector McCormick relaxations
     *
     * @param[in] resultRelaxationVMC is the vector McCormick object holding relaxation of objective iObj at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iObj is the number of the objective function
     */
    virtual void _update_LP_obj(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                const std::vector<double> &upperVarBounds, unsigned const &iObj);

    /**
     * @brief Virtual auxiliary function for updating LP inequalities, i.e., processing the linearization of the inequality for vector McCormick relaxations
     *
     * @param[in] resultRelaxationVMC is the vector McCormick object holding relaxation of inequality iIneq at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iIneq is the number of the inequality function
     */
    virtual void _update_LP_ineq(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                 const std::vector<double> &upperVarBounds, unsigned const &iIneq);

    /**
     * @brief Virtual auxiliary function for updating LP equalities, i.e., processing the linearization of the equality for vector McCormick relaxations
     *
     * @param[in] resultRelaxationCvVMC is the vector McCormick object holding relaxation of equality iEq at linearizationPoint used for the convex part
     * @param[in] resultRelaxationCcVMC is the vector McCormick object holding relaxation of equality iEq at linearizationPoint used for the concave part
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iEq is the number of the equality function
     */
    virtual void _update_LP_eq(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                               const std::vector<double> &upperVarBounds, unsigned const &iEq);

    /**
     * @brief Virtual auxiliary function for updating LP relaxation only inequalities, i.e., processing the linearization of the relaxation only inequality for vector McCormick relaxations
     *
     * @param[in] resultRelaxationVMC is the vector McCormick object holding relaxation of relaxation only inequality iIneqRelaxationOnly at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iIneqRelaxationOnly is the number of the relaxation only inequality function
     */
    virtual void _update_LP_ineqRelaxationOnly(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                               const std::vector<double> &upperVarBounds, unsigned const &iIneqRelaxationOnly);

    /**
     * @brief Virtual auxiliary function for updating LP relaxation only equalities, i.e., processing the linearization of the relaxation only equality for vector McCormick relaxations
     *
     * @param[in] resultRelaxationCvVMC is the vector McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the convex part
     * @param[in] resultRelaxationCcVMC is the vector McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the concave part
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iEqRelaxationOnly is the number of the relaxation only equality function
     */
    virtual void _update_LP_eqRelaxationOnly(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                             const std::vector<double> &upperVarBounds, unsigned const &iEqRelaxationOnly);


    /**
     * @brief Virtual auxiliary function for updating LP squash inequalities, i.e., processing the linearization of the squash inequality for vector McCormick relaxations
     *        No tolerances are allowed for squash inequalities!
     *
     * @param[in] resultRelaxationVMC is the vector McCormick object holding relaxation of inequality iIneqSquash at linearizationPoint
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] iIneqSquash is the number of the inequality function
     */
    virtual void _update_LP_ineq_squash(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                        const std::vector<double> &upperVarBounds, unsigned const &iIneqSquash);

    /**
     * @brief Virtual auxiliary function for updating whole LP at once
     *
     * @param[in] resultRelaxationVMC is the vector holding vector McCormick relaxations at linearizationPoints
     * @param[in] linearizationPoints is the vector holding the linearization points
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     */
    void _update_whole_LP_at_vector_linpoints(const std::vector<vMC> &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoints, const std::vector<double> &lowerVarBounds,
                                              const std::vector<double> &upperVarBounds);

    /**
     * @brief Function for equilibrating a line in an LP
     *
     * @param[in,out] coefficients is the vector holding the coefficients aij in the corresponding LP line j: sum_i a_ji xi <= bj
     * @param[in,out] rhs is the right-hand side bj in the corresponding LP line j: sum_i a_ji xi <= bj
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     * @return Returns the scaling factor used for the present LP line
     */
    double _equilibrate_and_relax(std::vector<double> &coefficients, double &rhs, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief Virtual function for solving the currently constructed linear program.
     *        This function also internally sets the _solutionPoint, _multipliers, and the _LPstatus.
     *
     * @param[in] currentNode is the currentNode, needed for throwing exceptions or similar
     */
    virtual LP_RETCODE _solve_LP(const babBase::BabNode &currentNode);

    /**
     * @brief Virtual function returning the current status of the last solved linear program.
     *
     * @return Returns the current status of the last solved linear program.
     */
    virtual LP_RETCODE _get_LP_status();

    /**
     * @brief Virtual function for setting the solution to the solution point of the lastly solved LP.
     *
     * @param[in, out] solution is modified to hold the solution point of the lastly solved LP
     * @param[in, out] etaVal is modified to hold the value of eta variable of the lastly solved LP
     */
    virtual void _get_solution_point(std::vector<double> &solution, double &etaVal);

    /**
     * @brief Virtual function returning the objective value of the lastly solved LP.
     *
     * @return Returns the objective value of the lastly solved LP.
     */
    double _get_objective_value();

    /**
     * @brief Virtual function returning the objective value of the lastly solved LP for a specific solver.
     *
     * @return Returns the objective value of the lastly solved LP.
     */
    virtual double _get_objective_value_solver();

    /**
     * @brief Virtual function for setting the multipliers of the lastly solved LP.
     *
     * @param[in] multipliers is modified to hold the reduced costs of the lastly solved LP
     */
    virtual void _get_multipliers(std::vector<double> &multipliers);

    /**
     * @brief Virtual function deactivating all objective rows in the LP for feasibility OBBT.
     */
    virtual void _deactivate_objective_function_for_OBBT();

    /**
     * @brief Virtual function modifying the LP for feasibility-optimality OBBT.
     *
     * @param[in] currentUBD is the current upper bound
     * @param[in,out] toTreatMax is the list holding variables indices for maximization
     * @param[in,out] toTreatMin is the list holding variables indices for minimization
     */
    virtual void _modify_LP_for_feasopt_OBBT(const double &currentUBD, std::list<unsigned> &toTreatMax, std::list<unsigned> &toTreatMin);

    /**
     * @brief Virtual function for setting the optimization sense of variable iVar in OBBT.
     *
     * @param[in] iVar is the number of variable of which the optimization sense will be changed.
     * @param[in] optimizationSense describes whether the variable shall be maximized or minimized 1: minimize, 0: ignore,  -1: maximize.
     */
    virtual void _set_optimization_sense_of_variable(const unsigned &iVar, const int &optimizationSense);

    /**
     * @brief Virtual function for restoring proper coefficients and options in the LP after OBBT.
     */
    virtual void _restore_LP_coefficients_after_OBBT();

    /**
     * @brief Virtual function for fixing a variable to one of its bounds.
     *
     * @param[in] iVar is the number of variable which will be fixed.
     * @param[in] fixToLowerBound describes whether the variable shall be fixed to its lower or upper bound.
     */
    virtual void _fix_variable(const unsigned &iVar, const bool fixToLowerBound);

    /**
     * @brief Virtual function for checking if the current linear program is really infeasible by, e.g., resolving it with different algorithms.
     *
     * @return Returns true if the linear program is indeed infeasible, false if and optimal solution was found
     */
    virtual bool _check_if_LP_really_infeasible();

    /**
     * @brief Auxiliary function for calling the proper function to linearize functions at chosen linearization point
     *
     * @param[out] resultRelaxation is the vector holding McCormick relaxation after they have been evaluated at the linearization point
     * @param[in] linearizationPoint is the vector holding the linearization point
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] subgraph is the subgraph holding the list of operations of the underlying function(s) to be evaluated
     * @param[in] functions is the vector holding the FFVar pointers to function(s) to be evaluated
     */
    void _linearize_functions_at_linpoint(std::vector<MC> &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds,
                                          mc::FFSubgraph &subgraph, std::vector<mc::FFVar> &functions);

    /**
     * @brief Auxiliary function for calling the proper function to linearize functions at precomputed vector linearization point.
     *        The precomputed vector linearization point has to be saved in _DAGobj.vMcPoint.
     *
     * @param[out] resultRelaxationVMC is the vector holding vector McCormick relaxation after they have been evaluated at the vector linearization point
     * @param[in] linearizationPoints is the vector holding linearization points used for subgradient heuristic
     * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
     * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
     * @param[in] subgraph is the subgraph holding the list of operations of the underlying function(s) to be evaluated
     * @param[in] functions is the vector holding the FFVar pointers to function(s) to be evaluated
     */
    void _linearize_functions_at_preset_vector_linpoint(std::vector<vMC> &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoints,
                                                        const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds,
                                                        mc::FFSubgraph &subgraph, std::vector<mc::FFVar> &functions);


    /**
     * @brief This function linearizes each function of the model at the middle point of the underlying box
     *
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     * @return Returns LINEARIZATION_UNKNOWN, since the problem is not solved in this function
     */
    LINEARIZATION_RETCODE _linearize_model_at_midpoint(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief This function linearizes each function of the model at the incumbent if it is contained in the current node. Otherwise
     *        each function is linearized at the middle point of the underlying box
     *
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     * @return Returns LINEARIZATION_UNKNOWN, since the problem is not solved in this function
     */
    LINEARIZATION_RETCODE _linearize_model_at_incumbent_or_at_midpoint(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief This function adds linearizations to LP with the use of an adapted version of Kelley's algorithm.
     *        The number of points equals at most _nvar+2.
     *        This function requires the solution of auxiliary LPs.
     *        Linear functions will be computed only once, since McCormick returns envelopes.
     *        Superfluous rows in the resulting LP will be set to 0.
     *
     * @param[in] currentNode is the current node in the B&B
     * @return Returns LINEARIZATION_UNKNOWN if the problem was not solved completely during linearization,
     *         returns LINEARIZATION_INFEASIBLE if the problem was found to be infeasible,
     *         returns LINEARIZATION_FEASIBLE if the problem was solved during linearization
     */
    LINEARIZATION_RETCODE _linearization_points_Kelley(const babBase::BabNode &currentNode);

    /**
     * @brief This function linearizes each function of the model at (_nvar+2)/2 points (except for the linear ones).
     *        The points are computed by using the precomputed simplex vertices from _compute_and_rotate_simplex
     *
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     * @return Returns LINEARIZATION_UNKNOWN, since the problem is not solved in this function
     */
    LINEARIZATION_RETCODE _linearization_points_Simplex(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief This function linearizes each function of the model at (_nvar+2)/2 random points (except for the linear ones)
     *
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     * @return Returns LINEARIZATION_UNKNOWN, since the problem is not solved in this function
     */
    LINEARIZATION_RETCODE _linearization_points_random(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief This function adds linearizations to LP with the use of an adapted version of Kelley's algorithm.
     *        The number of points equals at most the size of the chosen linpoints vector +3.
     *        This function requires the solution of auxiliary LPs.
     *        Linear functions will be computed only once, since McCormick returns envelopes.
     *        Superfluous rows in the resulting LP will be set to 0.
     *
     * @param[in] currentNode is the current node in the B&B
     * @return Returns LINEARIZATION_UNKNOWN if the problem was not solved completely during linearization,
     *         returns LINEARIZATION_INFEASIBLE if the problem was found to be infeasible,
     *         returns LINEARIZATION_FEASIBLE if the problem was solved during linearization
     */
    LINEARIZATION_RETCODE _linearization_points_Kelley_Simplex(const babBase::BabNode &currentNode);

    /**
     * @brief This function properly builds the LP using previously determined nonlinear and linear functions
     *
     * @param[in] resultRelaxationVMCNonlinear is the vector of VMC objects holding relaxations of nonlinear functions
     * @param[in] resultRelaxationLinear is the vector of MC objects holding relaxations of linear functions
     * @param[in] linearizationPoint is the point where the subgradient heuristic was performed and acts as a reference point for linear functions
     * @param[in] scaledPoints are the simplex/random points scaled back to its original domain
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     */
    void _update_LP_nonlinear_linear(const std::vector<vMC> &resultRelaxationVMCNonlinear, const std::vector<MC> &resultRelaxationLinear, const std::vector<double> &linearizationPoint,
                                     const std::vector<std::vector<double>> &scaledPoints, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief This function properly builds the LP using previously determined nonlinear functions
     *
     * @param[in] resultRelaxationNonlinear is the vector of MC objects holding relaxations of nonlinear functions
     * @param[in] linearizationPoint is the point where the subgradient heuristic was performed
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     * @param[in] iLin is the number of linearization
     */
    void _update_LP_nonlinear(const std::vector<MC> &resultRelaxationNonlinear, const std::vector<double> &linearizationPoint,
                              const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, const unsigned iLin);

    /**
     * @brief The function resets the LP, meaning it sets all rhs to 1e19 and coefficients to 0. Eta coefficients are -1
     *
     * @param[in] linearizationPoint is a dummy point to save computation time
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     */
    void _reset_LP(const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief Function for the computation of simplex points lying on a sphere with radius sphereRadius rotated by angleIn
     *
     * @param[in] dim denotes the dimension of the current optimization problem
     * @param[in] angleIn is the rotation angle of the simplex, the simplex will be rotated alternating by angleIn and 180°+angleIn
     * @param[in] sphereRadius is the radius of the dim-dimensional ball on which the simplex vertices lie
     * @param[in] simplexPoints holds the computed points of the simplex
     */
    void _compute_and_rotate_simplex(const unsigned int dim, const double angleIn, const double sphereRadius, std::vector<std::vector<double>> &simplexPoints);

    /**
     * @brief Heuristical determination of good linearization points. This function is in testing phasing and is not used
     */
    void _choose_good_lin_points(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, bool firstTime = true);

    /**
     * @brief Virtual function for checking if a given node is feasible with the use of interval arithmetics.
     *        It is needed in cases where the LBD solver may return something misleading, e.g., says sth is optimal but it can't be verified.
     *
     * @param[in,out] newLBD ist the lower bound obtained through intervals by the fallback function
     * @return Returns whether the node is feasible in interval arithmetic or not
     */
    virtual SUBSOLVER_RETCODE _fallback_to_intervals(double &newLBD);

    /**
     * @brief Virtual function for checking if a specific option has to be turned off for a given lower bounding solver, e.g., interval-based solvers can't use OBBT
     */
    virtual void _turn_off_specific_options();

    /**
     *  @brief Function used for truncation of value digits which are not guaranteed to be correct
     *
     *  @param[in] value ist the double to be truncated
     *  @param[in] tolerance is a given tolerance up to which the value will be truncated, e.g., 10e9 means that 9 digits after comma will be cut off
     */
    void _truncate_value(double &value, const double tolerance)
    {
        value = std::trunc(value * (tolerance)) / (tolerance);
    }

#ifdef LP__OPTIMALITY_CHECK
    /**
     * @brief Virtual function for checking if the solution point returned by the LP solver is really infeasible
     *
     * @param[in] currentNode is holding the current node in the branch-and-bound tree
     * @return Returns whether the problem was confirmed to be infeasible or not
     */
    virtual SUBSOLVER_RETCODE _check_infeasibility(const babBase::BabNode &currentNode);

    /**
     * @brief Virtual function for checking if the solution point returned by the LP solver is really feasible
     *
     * @param[in] solution is holding the solution point to check
     * @return Returns whether the given solution was confirmed to be feasible or not
     */
    virtual SUBSOLVER_RETCODE _check_feasibility(const std::vector<double> &solution);

    /**
     * @brief Virtual function for checking if the solution point returned by the LP solver is really optimal
     *
     * @param[in] currentNode is holding the current node in the branch-and-bound tree
     * @param[in] newLBD is the value of the solution point to check
     * @param[in] solution is holding the solution point to check
     * @param[in] etaVal is holding the value of eta at the solution point
     * @param[in] multipliers is holding the dual multipliers of the solution
     * @return Returns whether the given solution was confirmed to be optimal or not
     */
    virtual SUBSOLVER_RETCODE _check_optimality(const babBase::BabNode &currentNode, const double newLBD, const std::vector<double> &solution,
                                                const double etaVal, const std::vector<double> &multipliers);

    /**
     * @brief Function for printing the current LP stored in _MatrixA, _MatrixA_eqs, _rhsB, _rhsB_eqs
     *
     * @param[in] lowerVarBounds is the vector of lower bounds on your variables
     * @param[in] upperVarBounds is the vector of upper bounds on your variables
     */
    void _print_LP(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
     * @brief Checks if a branch-and-bound node contains the current incumbent (if any). Also writes output to the logger.
     *
     * @param[in] node is the BabNode to be checked
     */
    bool _contains_incumbent(const babBase::BabNode &node);

#endif

#ifdef LP__WRITE_CHECK_FILES
    /**
     * @brief Function writing the current linear program to file
     *
     * @param[in] fileName is the name of the written file
     */
    virtual void _write_LP_to_file(const std::string &fileName);
#endif

    /**
     * @name Objects for dual optimality condition check, i.e., c^T * x = y^T * b
     */
    /**@{*/
    std::vector<std::vector<std::vector<double>>> _matrixObj;                /*!< objective(s) times _nLinObj times variables */
    std::vector<std::vector<std::vector<double>>> _matrixIneq;               /*!< inequalities times _nLinIneq times variables */
    std::vector<std::vector<std::vector<double>>> _matrixEq1;                /*!< equalities convex times _nLinEq variables */
    std::vector<std::vector<std::vector<double>>> _matrixEq2;                /*!< equalities concave times _nLinEq variables */
    std::vector<std::vector<std::vector<double>>> _matrixIneqRelaxationOnly; /*!< inequalities relaxation only times _nLinIneqRelaxationOnly times variables */
    std::vector<std::vector<std::vector<double>>> _matrixEqRelaxationOnly1;  /*!< equalities relaxation only convex times _nLinEqRelaxationOnly variables */
    std::vector<std::vector<std::vector<double>>> _matrixEqRelaxationOnly2;  /*!< equalities relaxation only concave times _nLinEqRelaxationOnly variables */
    std::vector<std::vector<std::vector<double>>> _matrixIneqSquash;         /*!< inequalities squash times _nLinIneqSquash times variables */
    std::vector<std::vector<double>> _rhsObj;                                /*!< right-hand side of the objective(s) of the lower bounding linear program */
    std::vector<std::vector<double>> _rhsIneq;                               /*!< right-hand side of the inequalities of the lower bounding linear program */
    std::vector<std::vector<double>> _rhsEq1;                                /*!< right-hand side of the equalities (convex) of the lower bounding linear program */
    std::vector<std::vector<double>> _rhsEq2;                                /*!< right-hand side of the equalities (concave) of the lower bounding linear program */
    std::vector<std::vector<double>> _rhsIneqRelaxationOnly;                 /*!< right-hand side of the relaxation only inequalities of the lower bounding linear program */
    std::vector<std::vector<double>> _rhsEqRelaxationOnly1;                  /*!< right-hand side of the relaxation only equalities (convex) of the lower bounding linear program */
    std::vector<std::vector<double>> _rhsEqRelaxationOnly2;                  /*!< right-hand side of the relaxation only equalities (concave) of the lower bounding linear program */
    std::vector<std::vector<double>> _rhsIneqSquash;                         /*!< right-hand side of the squash inequalities of the lower bounding linear program */
    /**@}*/

    std::vector<double> _incumbent;                            /*!< incumbent point, needed for some heuristics and checks*/
    std::vector<std::vector<double>> _objectiveScalingFactors; /*!< scaling factors used in the linearizations of the objective function(s) */

    /**
     * @name Pointers to several objects. Note that these are NOT const, since if we want to resolve with MAiNGO, the pointers have to change
     */
    /**@{*/
    std::shared_ptr<DagObj> _DAGobj;                                /*!< object holding the DAG */
    std::shared_ptr<Settings> _maingoSettings;                      /*!< pointer to object holding the settings */
    std::shared_ptr<Logger> _logger;                                /*!< pointer to MAiNGO logger */
    std::shared_ptr<std::vector<Constraint>> _constraintProperties; /*!< pointer to constraint properties determined by MAiNGO */
    /**@}*/

    /**
     * @name Internal variables for storing information on the problem
     */
    /**@{*/
    std::vector<unsigned> _nLinObj;                                /*!< vector holding the number of linearization points of the objective function(s) */
    std::vector<unsigned> _nLinIneq;                               /*!< vector holding the number of linearization points of each inequality constraint */
    std::vector<unsigned> _nLinEq;                                 /*!< vector holding the number of linearization points of each equality constraint */
    std::vector<unsigned> _nLinIneqRelaxationOnly;                 /*!< vector holding the number of linearization points of each inequality relaxation only constraint */
    std::vector<unsigned> _nLinEqRelaxationOnly;                   /*!< vector holding the number of linearization points of each equality relaxation only constraint */
    std::vector<unsigned> _nLinIneqSquash;                         /*!< vector holding the number of linearization points of each squash inequality constraint */
    unsigned _maxnParticipatingVariables;                          /*!< maximal number of participating variables over all functions */
    const unsigned _nvar;                                          /*!< number of variables in the original (not relaxed) problem */
    const unsigned _nineq;                                         /*!< number of non-constant inequalities in the original (not relaxed) problem */
    const unsigned _neq;                                           /*!< number of non-constant equalities in the original (not relaxed) problem */
    const unsigned _nineqRelaxationOnly;                           /*!< number of non-constant inequalities for use only in the relaxed problem */
    const unsigned _neqRelaxationOnly;                             /*!< number of non-constant equalities for use only in the relaxed problem */
    const unsigned _nineqSquash;                                   /*!< number of non-constant squash inequalities in the original (not relaxed) problem*/
    bool _onlyBoxConstraints;                                      /*!< flag indicating whether the relaxed problem has only box constraints, i.e., all constraint counters are 0 */
    std::vector<babBase::OptimizationVariable> _originalVariables; /*!< original variables (i.e., original upper and lower bounds, info on which variables are binary etc.) */
    std::vector<bool> _variableIsLinear;                           /*!< information about which variables occur only linearly in the problem */
    double _objectiveValue;                                        /*!< variable holding the objective value of the linear program for MAiNGO solver and Interval solver */
    std::vector<double> _solutionPoint;                            /*!< vector storing the solution point for MAiNGO solver and Interval solver */
    std::vector<double> _multipliers;                              /*!< vector storing the multipliers for MAiNGO solver and Interval solver */
    std::vector<double> _lowerVarBounds;                           /*!< vector storing the lower variable bounds for MAiNGO solver and Interval solver */
    std::vector<double> _upperVarBounds;                           /*!< vector storing the upper variable bounds for MAiNGO solver and Interval solver */
    LP_RETCODE _LPstatus;                                          /*!< variable holding the current LP status for MAiNGO solver and Interval solver */
    double _computationTol;                                        /*!< variable holding the computational tolerance given as max(deltaIneq,deltaEq) */
    bool _differentNumberOfLins = false;                           /*!< flag indicating whether the number of linearizations set in CPLEX and CLP equals the number of linearization points in vmccormick */
                                                                   /**@}*/


  private:
    /**
     * @brief Function called by do_dbbt_and_probing for solving the lower bounding problem for probing on the current node
     *
     * @param[in,out] currentNode is the B&B node for which the lower bounding problem should be solved
     * @param[out] dualInfo is a struct containing information from the LP solved during probing
     * @param[in] iVar is the variable to be fixed to its bound
     * @param[in] fixToLowerBound denotes whether the variable shall be fixed to its lower bound
     * @return Return code, either RETCODE_FEASIBLE or RETCODE_INFEASIBLE
     */
    SUBSOLVER_RETCODE _solve_probing_LBP(babBase::BabNode &currentNode, LbpDualInfo &dualInfo,
                                         const unsigned int iVar, const bool fixToLowerBound);

    /**
     * @brief Function for setting the correct number of linearization points depending on the LBP_linpoints setting
     *
     * @param[in] LBP_linPoints is the corresponding setting
     */
    void _set_number_of_linpoints(const unsigned int LBP_linPoints);


    // Prevent use of default copy constructor and copy assignment operator by declaring them private:
    LowerBoundingSolver(const LowerBoundingSolver &);            /*!< default copy constructor declared private to prevent use */
    LowerBoundingSolver &operator=(const LowerBoundingSolver &); /*!< default assignment operator declared private to prevent use */
};

/**
 * @brief Factory function for initializing different lower bounding solver wrappers
 *
 * @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
 * @param[in] DAGvars are the variables corresponding to the DAG
 * @param[in] DAGfunctions are the functions corresponding to the DAG
 * @param[in] variables is a vector containing the optimization variables
 * @param[in] variableIsLinear is a vector containing information about which variables occur only linearly
 * @param[in] nineqIn is the number of inequality constraints
 * @param[in] neqIn is the number of equality
 * @param[in] nineqRelaxationOnlyIn is the number of inequality for use only in the relaxed problem
 * @param[in] neqRelaxationOnlyIn is the number of equality constraints for use only in the relaxed problem
 * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
 * @param[in] settingsIn is a pointer to the MAiNGO settings
 * @param[in] loggerIn is a pointer to the MAiNGO logger object
 * @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
 */
std::shared_ptr<LowerBoundingSolver> make_lbp_solver(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
                                                     const std::vector<babBase::OptimizationVariable> &variables, const std::vector<bool>& variableIsLinear,
                                                     const unsigned nineqIn, const unsigned neqIn,
                                                     const unsigned nineqRelaxationOnlyIn, const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn,
                                                     std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn,
                                                     bool printSolver = true);


}    // end namespace lbp


}    // end namespace maingo

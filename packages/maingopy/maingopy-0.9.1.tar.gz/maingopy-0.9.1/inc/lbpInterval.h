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

#include "lbp.h"


namespace maingo {


namespace lbp {


/**
* @class LbpInterval
* @brief Wrapper for handling the lower bounding problems by using interval arithmetics.
*        We currently do a bit too much work, if the subgradient interval heuristic is not used, since we additionally compute the McCormick relaxations.
*/
class LbpInterval: public LowerBoundingSolver {

  public:
    /**
        * @brief Constructor, stores information on the problem.
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
    LbpInterval(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
                const std::vector<babBase::OptimizationVariable> &variables, const std::vector<bool>& variableIsLinear, const unsigned nineqIn, const unsigned neqIn,
                const unsigned nineqRelaxationOnlyIn, const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn,
                std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn);

    /**
        * @brief Function called by the B&B solver to heuristically activate more scaling in the LBS
        */
    void activate_more_scaling();

  protected:
    /**
        * @brief Function for setting the interval bounds.
        *
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        */
    void _set_variable_bounds(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
        * @brief Calls the proper function for computing Intervals
        *
        * @param[in] currentNode is current node of the branch-and-bound tree
        * @return returns a LINEARIZATION_RETCODE defining whether the final problem was already solved/proven infeasible during linearization
        */
    LINEARIZATION_RETCODE _update_LP(const babBase::BabNode &currentNode);

    /**
        * @brief Auxiliary function for updating LP objective, i.e., processing the linearization of the objective function ( CPLEX cannot work with coefficients >+1e19 or -1e19> )
        *
        * @param[in] resultRelaxation is the McCormick object holding relaxation of objective iObj at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iObj is the number of the objective function
        */
    void _update_LP_obj(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                        const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iObj);

    /**
        * @brief Auxiliary function for updating LP inequalities, i.e., processing the linearization of the inequality
        *
        * @param[in] resultRelaxation is the McCormick object holding relaxation of inequality iIneq at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iIneq is the number of the inequality function
        */
    void _update_LP_ineq(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                         const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneq);

    /**
        * @brief Auxiliary function for updating LP equalities, i.e., processing the linearization of the equality
        *
        * @param[in] resultRelaxationCv is the McCormick object holding relaxation of equality iEq at linearizationPoint used for the convex part
        * @param[in] resultRelaxationCc is the McCormick object holding relaxation of equality iEq at linearizationPoint used for the concave part
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iEq is the number of the equality function
        */
    void _update_LP_eq(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                       const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEq);

    /**
        * @brief Auxiliary function for updating LP relaxation only inequalities, i.e., processing the linearization of the relaxation only inequality
        *
        * @param[in] resultRelaxation is the McCormick object holding relaxation of relaxation only inequality iIneqRelaxationOnly at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iIneqRelaxationOnly is the number of the relaxation only inequality function
        */
    void _update_LP_ineqRelaxationOnly(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                       const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqRelaxationOnly);

    /**
        * @brief Auxiliary function for updating LP relaxation only equalities, i.e., processing the linearization of the relaxation only equality
        *
        * @param[in] resultRelaxationCv is the McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the convex part
        * @param[in] resultRelaxationCc is the McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the concave part
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iEqRelaxationOnly is the number of the relaxation only equality function
        */
    void _update_LP_eqRelaxationOnly(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                     const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEqRelaxationOnly);

    /**
        * @brief Auxiliary function for updating LP squash inequalities, i.e., processing the linearization of the squash inequality
		*        No tolerances are allowed for squash inequalities!
        *
        * @param[in] resultRelaxation is the McCormick object holding relaxation of inequality iIneqSquash at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iIneqSquash is the number of the inequality function
        */
    void _update_LP_ineq_squash(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqSquash);

    /**
        * @brief Function for solving the currently constructed linear program.
        *        This function also internally sets the _solutionPoint, _multipliers, and the _LPstatus.
        *
        * @param[in] currentNode is the currentNode, needed for throwing exceptions or similar
        */
	LP_RETCODE _solve_LP(const babBase::BabNode &currentNode);

    /**
        * @brief Function for checking if a specific option has to be turned off for a given lower bounding solver
        */
    void _turn_off_specific_options();

#ifdef LP__OPTIMALITY_CHECK
    /**
        * @brief Function for checking if the solution point returned is really infeasible. Not available in this solver.
        *
        * @param[in] currentNode is holding the current node in the branch-and-bound tree
        * @return Returns whether the problem was confirmed to be infeasible or not
        */
    SUBSOLVER_RETCODE _check_infeasibility(const babBase::BabNode &currentNode);

    /**
        * @brief Function for checking if the solution point returned is really feasible.  Not available in this solver.
        *
        * @param[in] solution is holding the solution point to check
        * @return Returns whether the given solution was confirmed to be feasible or not
        */
    SUBSOLVER_RETCODE _check_feasibility(const std::vector<double> &solution);

    /**
        * @brief Function for checking if the solution point returned is really optimal. Not available in this solver.
        *
        * @param[in] currentNode is holding the current node in the branch-and-bound tree
        * @param[in] newLBD is the value of the solution point to check
        * @param[in] solution is holding the solution point to check
        * @param[in] etaVal is holding the value of eta at the solution point
        * @param[in] multipliers is holding the dual multipliers of the solution
        * @return Returns whether the given solution was confirmed to be optimal or not
        */
    SUBSOLVER_RETCODE _check_optimality(const babBase::BabNode &currentNode, const double newLBD, const std::vector<double> &solution, const double etaVal, const std::vector<double> &multipliers);
#endif

#ifdef LP__WRITE_CHECK_FILES
    /**
        * @brief Function writing the current linear program to file
        *
        * @param[in] fileName is the name of the written file
        */
    void _write_LP_to_file(const std::string &fileName);
#endif

  private:
    /**
        * @name Internal interval variables
        */
    /**@{*/
    std::vector<I> _resultInterval; /*!< vector holding Interval bounds of all functions (it is only the objective in this solver) */
    std::vector<I> _Intervals;      /*!< intervals bound to the DAG variables */
    std::vector<I> _Iarray;         /*!< dummy vector of I objects for faster evaluation if subgradient heuristic is not used */
                                    /**@}*/
};


}    // end of namespace lbp


}    // end of namespace maingo
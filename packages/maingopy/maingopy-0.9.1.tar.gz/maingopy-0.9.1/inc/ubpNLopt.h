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

#include "ubp.h"

#include "nlopt.hpp"


namespace maingo {


namespace ubp {


/**
* @class UbpNLopt
* @brief Wrapper for handling the upper bounding problems by interfacing NLopt
*
* This class constructs and solves upper bounding problems using different solvers from the NLopt toolbox (http://ab-initio.mit.edu/wiki/index.php/NLopt). It thus evaluates the Model equations using either regular floating point arithmetics or FADBAD++ to obtain function values and gradients, and solves the resulting NLPs.
* The solution point obtained is checked for feasibility within the given tolerances.
*
*/
class UbpNLopt: public UpperBoundingSolver {

  public:
    /**
		* @brief Constructor, stores information on the problem and initializes the local-subsolvers used
		*
		* @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
		* @param[in] DAGvars are the variables corresponding to the DAG
		* @param[in] DAGfunctions are the functions corresponding to the DAG
		* @param[in] variables is a vector containing the initial optimization variables defined in problem.h
		* @param[in] nineqIn is the number of inequality constraints
		* @param[in] neqIn is the number of equality constraints
        * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
		* @param[in] settingsIn is a pointer to the MAiNGO settings
		* @param[in] loggerIn is a pointer to the MAiNGO logger object
		* @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
		* @param[in] useIn communicates what the solver is to be used for
		*/
    UbpNLopt(mc::FFGraph& DAG, const std::vector<mc::FFVar>& DAGvars, const std::vector<mc::FFVar>& DAGfunctions, const std::vector<babBase::OptimizationVariable>& variables,
             const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn);

  private:
    /**
		* @brief Function for actually solving the NLP sub-problem.
		*
		* @param[in] lowerVarBounds is the vector containing the lower bounds on the variables within the current node
		* @param[in] upperVarBounds is the vector containing the upper bounds on the variables within the current node
		* @param[out] objectiveValue is the objective value obtained for the solution point of the upper bounding problem (need not be a local optimum!)
		* @param[in,out] solutionPoint is the point at which objectiveValue was achieved (can in principle be any point within the current node!); it is also used for communicating the initial point (usually the LBP solution point)
		* @return Return code, either SUBSOLVER_FEASIBLE or SUBSOLVER_INFEASIBLE, indicating whether the returned solutionPoint (!!) is feasible or not
		*/
    virtual SUBSOLVER_RETCODE _solve_nlp(const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, double& objectiveValue, std::vector<double>& solutionPoint);

    /**
		* @name NLopt solver objects (_subopt is required for Augmented Lagrangian methods, see NLopt website)
		*/
    /**@{*/
    nlopt::opt _NLopt;       /*!< NLopt solver object */
    nlopt::opt _NLoptSubopt; /*!< NLopt solver object */
    /**@}*/

    /**
		* @name Functions provided to the NLopt interface
		*/
    /**@{*/
    /**
		* @brief Function returning the objective value to the NLopt interface
		*
		* @param[in] x is the current point
		* @param[in] grad is the derivative
		* @param[in] f_data is not used
		*/
    static double _NLopt_get_objective(const std::vector<double>& x, std::vector<double>& grad, void* f_data);

    /**
		* @brief Function providing gradient and value information on inequalities to the NLopt interface
		*
		* @param[in] m is the number of constraints
		* @param[in] n is the dimension of x
		* @param[in,out] result holds the values at x
		* @param[in] x is the current point
		* @param[in,out] grad is the derivative
		* @param[in] f_data is not used
		*/
    static void _NLopt_get_ineq(unsigned m, double* result, unsigned n, const double* x, double* grad, void* f_data);

    /**
		* @brief Function providing gradient and value information on equalities to the NLopt interface
		*
		* @param[in] m is the number of constraints
		* @param[in] n is the dimension of x
		* @param[in,out] result holds the values at x
		* @param[in] x is the current point
		* @param[in,out] grad is the derivative
		* @param[in] f_data is not used
		*/
    static void _NLopt_get_eq(unsigned m, double* result, unsigned n, const double* x, double* grad, void* f_data);
    /**@}*/

    // Prevent use of default copy constructor and copy assignment operator by declaring them private:
    UbpNLopt(const UbpNLopt&);            /*!< default copy constructor declared private to prevent use */
    UbpNLopt& operator=(const UbpNLopt&); /*!< default assignment operator declared private to prevent use */
};


}    // end namespace ubp


}    // end namespace maingo
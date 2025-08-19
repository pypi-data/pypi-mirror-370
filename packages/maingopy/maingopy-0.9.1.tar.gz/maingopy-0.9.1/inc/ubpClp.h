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

#include "ClpFactorization.hpp"
#include "ClpNetworkMatrix.hpp"
#include "ClpSimplex.hpp"

#include <list>


namespace maingo {


namespace ubp {


/**
* @class UbpClp
* @brief Wrapper for handling the upper bounding problems by interfacing CLP
*
* This class constructs and solves upper bounding problems which were recognized as LP using CLP (COIN-OR project).
*
*/
class UbpClp: public UpperBoundingSolver {

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
    UbpClp(mc::FFGraph& DAG, const std::vector<mc::FFVar>& DAGvars, const std::vector<mc::FFVar>& DAGfunctions, const std::vector<babBase::OptimizationVariable>& variables,
           const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn);

  private:
    /**
        * @brief Function for actually solving the NLP (actually, LP in this case) sub-problem.
        *
        * @param[in] lowerVarBounds is the vector containing the lower bounds on the variables within the current node
        * @param[in] upperVarBounds is the vector containing the upper bounds on the variables within the current node
        * @param[out] objectiveValue is the objective value obtained for the solution point of the upper bounding problem (need not be a local optimum!)
        * @param[in,out] solutionPoint is the point at which objectiveValue was achieved (can in principle be any point within the current node!); it is also used for communicating the initial point (usually the LBP solution point)
        * @return Return code, either SUBSOLVER_FEASIBLE or SUBSOLVER_INFEASIBLE, indicating whether the returned solutionPoint (!!) is feasible or not
        */
    virtual SUBSOLVER_RETCODE _solve_nlp(const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, double& objectiveValue, std::vector<double>& solutionPoint);

    /**
		* @name Internal CLP variables
		*/
    /**@{*/
    ClpSimplex _clp;                      /*!< CLP simplex object */
    CoinPackedMatrix _matrix;             /*!< CLP matrix object */
    size_t _numrows;                      /*!< total number of constraints in the LP */
    double _objectiveConstant;            /*!< to account for the case where the user uses a constant in the objective*/
    std::vector<double> _objectiveCoeffs; /*!< coefficients of variables in the LP objective */
    std::vector<double> _lowerRowBounds;  /*!< lower bounds on constraints */
    std::vector<double> _upperRowBounds;  /*!< upper bounds on constraints */
    std::vector<double> _lowerVarBounds;  /*!< lower bounds on variables */
    std::vector<double> _upperVarBounds;  /*!< upper bounds on variables */
    /**@}*/

    // Prevent use of default copy constructor and copy assignment operator by declaring them private:
    UbpClp(const UbpClp&);            /*!< default copy constructor declared private to prevent use */
    UbpClp& operator=(const UbpClp&); /*!< default assignment operator declared private to prevent use */
};


}    // end namespace ubp


}    // end namespace maingo
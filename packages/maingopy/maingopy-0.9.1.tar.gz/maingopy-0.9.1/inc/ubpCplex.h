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

#include "ilcplex/ilocplex.h"

#include <list>
#include <utility>


namespace maingo {


namespace ubp {


/**
* @class UbpCplex
* @brief Wrapper for handling the upper bounding problems by interfacing CPLEX
*
* This class constructs and solves upper bounding problems which were recognized as LP, MIP, QCP or MIQCP using CPLEX (International Business Machines Corporation: IBM ILOG CPLEX v12.8. Armonk (2009)).
*
*/
class UbpCplex: public UpperBoundingSolver {

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
    UbpCplex(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
             const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn);

    /**
        * @brief Destructor
        */
    ~UbpCplex() { _terminate_cplex(); }

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
    virtual SUBSOLVER_RETCODE _solve_nlp(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, double &objectiveValue, std::vector<double> &solutionPoint);

    /**
        * @brief Function for taking care of memory management by terminating Cplex (either called from destructor or when an exception is thrown)
        */
    void _terminate_cplex();

    /**
        * @name Internal CPLEX variables
        */
    /**@{*/
    IloEnv cplxEnv;          /*!< CPLEX environment  */
    IloModel cplxModel;      /*!< CPLEX model  */
    IloNumVarArray cplxVars; /*!< CPLEX variables  */
    IloCplex cplex;          /*!< CPLEX object  */
    /**@}*/

    // Prevent use of default copy constructor and copy assignment operator by declaring them private:
    UbpCplex(const UbpCplex &);            /*!< default copy constructor declared private to prevent use */
    UbpCplex &operator=(const UbpCplex &); /*!< default assignment operator declared private to prevent use */
};


}    // end namespace ubp


}    // end namespace maingo
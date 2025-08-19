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

#include "ubpStructure.h"

#include "babOptVar.h"

#include "KTRException.h"
#include "KTRProblem.h"
#include "KTRSolver.h"

#include <memory>
#include <vector>


namespace maingo {


namespace ubp {


struct DagObj;

/**
* @class KnitroProblem
* @brief Class for representing problems to be solved by Knitro, providing an interface to the problem definition in problem.h
*
* This class provides an interface between Knitro and the problem definition in problem.h. by evaluating the Model equations and preparing the information required by Knitro.
* An instance of this class is handed to Knitro as an argument of its KN_solve routine in ubpKnitro.cpp.
* For more information on the basic interface see  https://www.artelys.com/tools/knitro_doc/3_referenceManual/callableLibraryAPI.html#basic-problem-construction .
*
*/
class KnitroProblem: public knitro::KTRProblem {
  public:
    /**
		* @brief Constructor actually used in ubp.cpp. Initializes the corresponding members.
		*
		* @param[in] nvarIn is the number of optimization variables
		* @param[in] neqIn is the number of equality constraints
		* @param[in] nineqIn is the number of inequality constraints
        * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
		* @param[in] variables are the original problem variables
		* @param[in] structureIn is a struct containing information on sparsity patterns of the Lagrangian and Hessian
		* @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
		* @param[in] dagObj is a pointer to the struct holding the DAG to be evaluated
		*/
    KnitroProblem(unsigned nvarIn, unsigned neqIn, unsigned nineqIn, const unsigned nineqSquashIn, const std::vector<babBase::OptimizationVariable>& variables,
                  UbpStructure* structureIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, std::shared_ptr<DagObj> dagObj);

    /** @brief Destructor */
    virtual ~KnitroProblem();

    /**
		* @brief Function called by Knitro to get values of the objective and constraints at a point x
		*
		* @param[in] x is the current point
		* @param[out] c is the value of constraints
		* @param[out] objGrad is the gradient of the objective at x (not set in this function)
		* @param[out] jac holds the Jacobian values at x (not set in this function)
		* @return Returns the value of the objective function at x
		*/
    double evaluateFC(const double* const x, double* const c, double* const objGrad, double* const jac);

    /**
		* @brief Function called by Knitro to get derivatives of the objective and constraints at point x
		*
		* @param[in] x is the current point
		* @param[out] objGrad is the gradient of the objective at x
		* @param[out] jac holds the Jacobian values at x
		* @return Returns the value of the gradients of the objective function at x
		*/
    int evaluateGA(const double* const x, double* const objGrad, double* const jac);

    /**
		* @brief Function called by Knitro to get the hessian of the lagrangian at point x
		*
		* @param[in] x is the current point
		* @param[in] objScaler is value to scale objective component of the Hessian.
		* @param[in] lambda contains the values of the dual variables to evaluate.
		* @param[out] hess holds the values of non-zero elements of the Hessian to be evaluated at x.
		* @return KTR_RC_CALLBACK_ERR, a KNITRO error code indicating an error in evaluating the second derivatives.
		*/
    int evaluateHess(const double* const x, double objScaler, const double* const lambda, double* const hess);

  private:
    /**
		* @brief Set properties of objective function, i.e., type (linear, quadratic, general)
		*/
    void _setObjectiveProperties();

    /**
		* @brief Set properties of variables, i.e., type (continuous, binary, integer)
		*/
    void _setVariableProperties();

    /**
		* @brief Set properties of constraints, i.e., bounds and type (linear, quadratic, general)
		*/
    void _setConstraintProperties();

    /**
		* @brief Set properties of derivatives, i.e., correct indices for non zeros in Jacobian
		*/
    void _setDerivativeProperties();

    /**
		* @name Internal Knitro variables
		*/
    /**@{*/
    unsigned _nvar;                                                    /*!< number of variables */
    unsigned _nineq;                                                   /*!< number of inequalities */
    unsigned _nineqSquash;                                             /*!< number of squash inequalities */
    unsigned _neq;                                                     /*!< number of equalities */
    UbpStructure* _structure;                                          /*!< struct storing information on the problem structure */
    std::shared_ptr<std::vector<Constraint>> _constraintProperties;    /*!< pointer to constraint properties determined by MAiNGO */
    std::vector<babBase::OptimizationVariable> _optimizationVariables; /*!< optimization variables - needed to set if continuous, integer, binary */
    std::shared_ptr<DagObj> _DAGobj;                                   /*!< pointer to object containing DAG for upper bounding
	  /**@}*/

    // Copy constructors made private
    KnitroProblem(const KnitroProblem&);            /*!< default copy constructor declared private to prevent use */
    KnitroProblem& operator=(const KnitroProblem&); /*!< default assignment operator declared private to prevent use */
};


}    // end namespace ubp


}    // end namespace maingo
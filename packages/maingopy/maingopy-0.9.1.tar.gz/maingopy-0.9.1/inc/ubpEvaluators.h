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

#include <memory>


namespace maingo {


namespace ubp {


struct DagObj;


/**
* @brief Function for evaluating objective function at a given point
*
* @param[in] currentPoint is the point to be checked
* @param[in] nvar is the number of variables
* @param[in] computeGradient is a flag indicating whether the gradient of the objective function should be computed as well
* @param[out] gradient is the gradient of the objective function at currentPoint
* @param[in] dagObj is a pointer to the struct holding the DAG to be evaluated
* @return Objective function value at currentPoint
*/
double evaluate_objective(const double* currentPoint, const unsigned nvar, const bool computeGradient, double* gradient, std::shared_ptr<DagObj> dagObj);

/**
* @brief Function for evaluating residuals of inequality constraints at a given point
*
* @param[in] currentPoint is the point to be checked
* @param[in] nvar is the number of variables
* @param[in] nineq is the number of inequality constraints
* @param[in] computeGradient is a flag indicating whether the gradient of the inequality constraints should be computed as well
* @param[out] result is an array containing the residuals of the inequality constraints at currentPoint
* @param[out] gradient is an array containing the gradients of the inequality constraints at currentPoint
* @param[in] dagObj is a pointer to the struct holding the DAG to be evaluated
*/
void evaluate_inequalities(const double* currentPoint, const unsigned nvar, const unsigned nineq, const bool computeGradient, double* result, double* gradient, std::shared_ptr<DagObj> dagObj);

/**
* @brief Function for evaluating residuals of equality constraints at a given point
*
* @param[in] currentPoint is the point to be checked
* @param[in] nvar is the number of variables
* @param[in] neq is the number of equality constraints
* @param[in] computeGradient is a flag indicating whether the gradient of the equality constraints should be computed as well
* @param[out] result is an array containing the residuals of the inequality constraints at currentPoint
* @param[out] gradient is a vector containing the gradients of the equality constraints at currentPoint
* @param[in] dagObj is a pointer to the struct holding the DAG to be evaluated
*/
void evaluate_equalities(const double* currentPoint, const unsigned nvar, const unsigned neq, const bool computeGradient, double* result, double* gradient, std::shared_ptr<DagObj> dagObj);

/**
* @brief Function for evaluating residuals of inequality and equality constraints at a given point
*
* @param[in] currentPoint is the point to be checked
* @param[in] nvar is the number of variables
* @param[in] ncon is the number of constraints
* @param[in] computeGradient is a flag indicating whether the gradient of the equality constraints should be computed as well
* @param[out] result is an array containing the residuals of the constraints at currentPoint
* @param[out] gradient is a vector containing the gradients of the constraints at currentPoint
* @param[in] dagObj is a pointer to the struct holding the DAG to be evaluated
*/
void evaluate_constraints(const double* currentPoint, const unsigned nvar, const unsigned ncon, const bool computeGradient, double* result, double* gradient, std::shared_ptr<DagObj> dagObj);

/**
* @brief Function for evaluating the objective function along with the residuals of inequality and equality constraints at a given point
*
* @param[in] currentPoint is the point to be checked
* @param[in] nvar is the number of variables
* @param[in] ncon is the number of constraints
* @param[in] computeGradient is a flag indicating whether the gradient of the equality constraints should be computed as well
* @param[out] result is an array containing the objective function and the residuals of the constraints at currentPoint
* @param[out] gradient is a vector containing the gradients of the objective function and the constraints at currentPoint
* @param[in] dagObj is a pointer to the struct holding the DAG to be evaluated
*/
void evaluate_problem(const double* currentPoint, const unsigned nvar, const unsigned ncon, const bool computeGradient, double* result, double* gradient, std::shared_ptr<DagObj> dagObj);

/**
* @brief Function for evaluating the Hessian of the Lagrangian at a given point
*
* @param[in] currentPoint is the point to be checked
* @param[in] nvar is the number of variables
* @param[in] ncon is the number of constraints
* @param[out] hessian is an array containing the Hessian of the Lagrangian at currentPoint
* @param[in] dagObj is a pointer to the struct holding the DAG to be evaluated
*/
void evaluate_hessian(const double* currentPoint, const unsigned nvar, const unsigned ncon, double* hessian, std::shared_ptr<DagObj> dagObj);


}    // end namespace ubp


}    // end namespace maingo
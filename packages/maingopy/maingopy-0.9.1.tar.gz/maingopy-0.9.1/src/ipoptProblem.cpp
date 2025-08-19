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

#include "ipoptProblem.h"
#include "MAiNGOException.h"
#include "ubpEvaluators.h"

#include <cassert>


using namespace Ipopt;
using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor
IpoptProblem::IpoptProblem(unsigned nvarIn, unsigned neqIn, unsigned nineqIn, unsigned nineqSquashIn, UbpStructure* structureIn,
                           std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, std::shared_ptr<DagObj> dagObj):
    _nvar(nvarIn),
    _neq(neqIn), _nineq(nineqIn), _nineqSquash(nineqSquashIn), _structure(structureIn), _constraintProperties(constraintPropertiesIn), _DAGobj(dagObj)
{
}


/////////////////////////////////////////////////////////////////////////
// destructor
IpoptProblem::~IpoptProblem()
{
}


/////////////////////////////////////////////////////////////////////////
// returns the size of the problem
bool
IpoptProblem::get_nlp_info(Index& n, Index& m, Index& nnz_jac_g,
                           Index& nnz_h_lag, IndexStyleEnum& index_style)
{
    // # variables
    n = _nvar;

    // Total # of constraints (Ipopt does not differentiate between ineq and eq)
    m = _neq + _nineq + _nineqSquash;

    // # non zeros in Jacobian
    nnz_jac_g = _structure->nnonZeroJac;

    // # non zeros in Hessian of Lagrangian
    nnz_h_lag = _structure->nnonZeroHessian;

    // Use the C style indexing (0-based)
    index_style = TNLP::C_STYLE;

    return true;
}


/////////////////////////////////////////////////////////////////////////
// returns the variable bounds
bool
IpoptProblem::get_bounds_info(Index n, Number* x_l, Number* x_u,
                              Index m, Number* g_l, Number* g_u)
{

    // Variable bounds
    for (Index iVar = 0; iVar < _nvar; iVar++) {
        x_l[iVar] = _xL[iVar];
        x_u[iVar] = _xU[iVar];
    }

    // Constraints:
    // Ipopt interprets any number greater than nlp_upper_bound_inf as
    // infinity. The default value of nlp_upper_bound_inf and nlp_lower_bound_inf
    // is 1e19 and can be changed through ipopt options.

    // Inequalities
    for (Index iIneq = 0; iIneq < _nineq + _nineqSquash; iIneq++) {
        g_l[iIneq] = -2e19;
        g_u[iIneq] = 0;
    }

    // Equalities
    for (Index iEq = 0; iEq < _neq; iEq++) {
        g_l[_nineq + _nineqSquash + iEq] = 0;
        g_u[_nineq + _nineqSquash + iEq] = 0;
    }

    return true;
}


/////////////////////////////////////////////////////////////////////////
// returns the initial point for the problem
bool
IpoptProblem::get_starting_point(Index n, bool init_x, Number* x,
                                 bool init_z, Number* z_L, Number* z_U,
                                 Index m, bool init_lambda,
                                 Number* lambda)
{
    // Make sure Ipopt is only asking for an initial point, not multipliers
    assert(init_x == true);
    assert(init_z == false);
    assert(init_lambda == false);

    // Initialize to the given starting point
    for (Index iVar = 0; iVar < _nvar; iVar++) {
        x[iVar] = _xStart[iVar];
    }

    return true;
}


/////////////////////////////////////////////////////////////////////////
// returns the value of the objective function
bool
IpoptProblem::eval_f(Index n, const Number* x, bool new_x, Number& obj_value)
{
    obj_value = ubp::evaluate_objective(x, n, false, nullptr, _DAGobj);    // No need to compute gradient here
    return true;
}


/////////////////////////////////////////////////////////////////////////
// return the gradient of the objective function grad_{x} f(x)
bool
IpoptProblem::eval_grad_f(Index n, const Number* x, bool new_x, Number* grad_f)
{
    ubp::evaluate_objective(x, n, true, grad_f, _DAGobj);    // No need to compute gradient here
    return true;
}


/////////////////////////////////////////////////////////////////////////
// return the value of the constraints: g(x)
bool
IpoptProblem::eval_g(Index n, const Number* x, bool new_x, Index m, Number* g)
{
    ubp::evaluate_constraints(x, n, m, false, g, nullptr, _DAGobj);
    return true;
}


/////////////////////////////////////////////////////////////////////////
// return the structure or values of the jacobian
bool
IpoptProblem::eval_jac_g(Index n, const Number* x, bool new_x,
                         Index m, Index nele_jac, Index* iRow, Index* jCol,
                         Number* values)
{
    if (values == NULL) {

        // Return the structure of the jacobian
        for (Index i = 0; i < _structure->nonZeroJacIRow.size(); i++) {
            iRow[i] = _structure->nonZeroJacIRow[i];
            jCol[i] = _structure->nonZeroJacJCol[i];
        }
    }
    else {

        std::vector<double> gradient(n * m);
        ubp::evaluate_constraints(x, n, m, true, nullptr, gradient.data(), _DAGobj);

        Index consIndex = 0;
        unsigned nObj   = 1;    // We need Jacobian of constraints only
        for (size_t i = nObj; i < _constraintProperties->size(); i++) {
            for (Index j = 0; j < (signed)(*_constraintProperties)[i].nparticipatingVariables; j++) {
                values[consIndex] = gradient[(i - nObj) * n + (*_constraintProperties)[i].participatingVariables[j]];
                consIndex++;
            }
        }
    }

    return true;
}


/////////////////////////////////////////////////////////////////////////
// return the structure or values of the hessian
bool
IpoptProblem::eval_h(Index n, const Number* x, bool new_x,
                     Number obj_factor, Index m, const Number* lambda,
                     bool new_lambda, Index nele_hess, Index* iRow,
                     Index* jCol, Number* values)
{
    if (values == NULL) {
        // Return the structure of the hessian
        for (Index i = 0; i < _structure->nonZeroHessianIRow.size(); i++) {
            iRow[i] = _structure->nonZeroHessianIRow[i];
            jCol[i] = _structure->nonZeroHessianJCol[i];
        }
    }
    else {

        std::vector<double> hessian(n * n * (m + 1));
        ubp::evaluate_hessian(x, n, m, hessian.data(), _DAGobj);

        Number hess_f_value;    // Temp value for entry in hessian of f
        Number hess_g_value;    // Temp value for entry in hessian of contraints

        for (Index index = 0; index < _structure->nonZeroHessianIRow.size(); index++) {

            Index iVar    = _structure->nonZeroHessianIRow[index];
            Index jVar    = _structure->nonZeroHessianJCol[index];
            hess_f_value  = hessian[(0 * n + iVar) * n + jVar];
            hess_g_value  = 0;
            unsigned nObj = 1;
            for (size_t i = nObj; i < _constraintProperties->size(); i++) {
                hess_g_value += lambda[i - nObj] * hessian[(i * n + iVar) * n + jVar];
            }

            values[index] = obj_factor * hess_f_value + hess_g_value;
        }
    }
    return true;
}


/////////////////////////////////////////////////////////////////////////
// store solution
void
IpoptProblem::finalize_solution(SolverReturn status,
                                Index n, const Number* x, const Number* z_L, const Number* z_U,
                                Index m, const Number* g, const Number* lambda,
                                Number obj_value,
                                const IpoptData* ip_data,
                                IpoptCalculatedQuantities* ip_cq)
{
    _solutionX.clear();
    for (Index iVar = 0; iVar < _nvar; iVar++) {
        _solutionX.push_back(x[iVar]);
    }

    _solution_f = obj_value;
}


/////////////////////////////////////////////////////////////////////////
// report solution
double
IpoptProblem::get_solution(std::vector<double>& sol_x)
{
    sol_x = _solutionX;
    return _solution_f;
}


/////////////////////////////////////////////////////////////////////////
// modify bounds and starting point
void
IpoptProblem::set_bounds_and_starting_point(const std::vector<double>& xL, const std::vector<double>& xU, const std::vector<double>& xStart)
{
    _xL     = xL;
    _xU     = xU;
    _xStart = xStart;
}

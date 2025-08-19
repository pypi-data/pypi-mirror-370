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

#ifdef HAVE_KNITRO

#include "knitroProblem.h"
#include "ubpEvaluators.h"


using namespace knitro;
using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor
KnitroProblem::KnitroProblem(unsigned nvarIn, unsigned neqIn, unsigned nineqIn, unsigned nineqSquashIn, const std::vector<babBase::OptimizationVariable>& variables,
                             UbpStructure* structureIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, std::shared_ptr<DagObj> dagObj):
    KTRProblem((int)nvarIn, (int)(neqIn + nineqIn + nineqSquashIn), (int)(structureIn->nnonZeroJac), (int)(structureIn->nnonZeroHessian)),
    _nvar(nvarIn), _neq(neqIn), _nineq(nineqIn), _nineqSquash(nineqSquashIn),
    _optimizationVariables(variables), _structure(structureIn), _constraintProperties(constraintPropertiesIn), _DAGobj(dagObj)
{
    _setObjectiveProperties();
    _setVariableProperties();
    _setConstraintProperties();
    _setDerivativeProperties();
}


/////////////////////////////////////////////////////////////////////////
// destructor
KnitroProblem::~KnitroProblem()
{
}


/////////////////////////////////////////////////////////////////////////
// function setting the properties of the objective function
void
KnitroProblem::_setObjectiveProperties()
{
    setObjGoal(knitro::KTREnums::ObjectiveGoal::Minimize);
    switch ((*_constraintProperties)[0].dependency) {
        case LINEAR:
            setObjType(knitro::KTREnums::ObjectiveType::ObjLinear);
            break;
        case QUADRATIC:
            setObjType(knitro::KTREnums::ObjectiveType::ObjQuadratic);
            break;
        default:
            setObjType(knitro::KTREnums::ObjectiveType::ObjGeneral);
            break;
    }
    setObjFnType(knitro::KTREnums::FunctionType::Uncertain);
}


/////////////////////////////////////////////////////////////////////////
// function setting the properties of the variables
void
KnitroProblem::_setVariableProperties()
{

    for (unsigned int i = 0; i < _nvar; i++) {
        // Set the original bounds here once to avoid KNITRO warnings, e.g., if bounds are not set, KNITRO will make any binary to an integer variable
        setVarLoBnds(i, _optimizationVariables[i].get_lower_bound());
        setVarUpBnds(i, _optimizationVariables[i].get_upper_bound());
        switch (_optimizationVariables[i].get_variable_type()) {
            case babBase::enums::VT_CONTINUOUS:
                setVarTypes(i, knitro::KTREnums::VariableType::Continuous);
                break;
            case babBase::enums::VT_BINARY:
                setVarTypes(i, knitro::KTREnums::VariableType::Binary);
                break;
            case babBase::enums::VT_INTEGER:
                setVarTypes(i, knitro::KTREnums::VariableType::Integer);
                break;
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// function setting the properties of the constraints
void
KnitroProblem::_setConstraintProperties()
{

    unsigned nObj = 1;
    for (size_t i = nObj; i < _constraintProperties->size(); i++) {
        switch ((*_constraintProperties)[i].type) {
            case INEQ:
            case INEQ_SQUASH:
                setConLoBnds(i - nObj, -KTR_INFBOUND);
                setConUpBnds(i - nObj, 0);
                break;
            case EQ:
                setConLoBnds(i - nObj, 0);
                setConUpBnds(i - nObj, 0);
                break;
            default:
                break;
        }
        switch ((*_constraintProperties)[i].dependency) {
            case LINEAR:
                setConTypes(i - nObj, knitro::KTREnums::ConstraintType::ConLinear);
                break;
            case QUADRATIC:
                setConTypes(i - nObj, knitro::KTREnums::ConstraintType::ConQuadratic);
                break;
            default:
                setConTypes(i - nObj, knitro::KTREnums::ConstraintType::ConGeneral);
                break;
        }
        setConFnTypes(i - nObj, knitro::KTREnums::FunctionType::Uncertain);
    }
}


/////////////////////////////////////////////////////////////////////////
// function setting the properties of the derivatives
void
KnitroProblem::_setDerivativeProperties()
{

    // Jacobian
    unsigned consIndex = 0;
    unsigned nObj      = 1;

    for (size_t i = 0; i < _structure->nonZeroJacIRow.size(); i++) {
        setJacIndexCons(consIndex, _structure->nonZeroJacIRow[i]);
        setJacIndexVars(consIndex, _structure->nonZeroJacJCol[i]);
        consIndex++;
    }
    //Hessian
    consIndex = 0;    // It's actually valueIndex
    for (int i = 0; i < _structure->nonZeroHessianIRow.size(); i++) {
        // Switch rows and columns as knitro requires upper triangular sparse format
        setHessIndexRows(consIndex, _structure->nonZeroHessianJCol[i]);
        setHessIndexCols(consIndex, _structure->nonZeroHessianIRow[i]);
        consIndex++;
    }
}


/////////////////////////////////////////////////////////////////////////
// returns the value of the objective function and constraints
double
KnitroProblem::evaluateFC(const double* const x, double* const c, double* const objGrad, double* const jac)
{

    std::vector<double> result(1 + _nineq + _neq + _nineqSquash);
    ubp::evaluate_problem(x, _nvar, /*#constraints*/ _nineq + _neq + _nineqSquash, false, result.data(), nullptr, _DAGobj);

    for (unsigned int i = 0; i < _nineq + _neq + _nineqSquash; i++) {
        c[i] = result[i + 1];
    }
    return result[0];
}


/////////////////////////////////////////////////////////////////////////
// return the gradient of the objective function and constraints (Jacobian)
int
KnitroProblem::evaluateGA(const double* const x, double* const objGrad, double* const jac)
{

    std::vector<double> result(1 + _nineq + _neq + _nineqSquash);
    std::vector<double> gradient(_nvar * (1 + _nineq + _neq + _nineqSquash));
    ubp::evaluate_problem(x, _nvar, _nineq + _neq + _nineqSquash, true, result.data(), gradient.data(), _DAGobj);

    for (unsigned iVar = 0; iVar < _nvar; iVar++) {
        objGrad[iVar] = gradient[iVar];
    }

    unsigned int consIndex = 0;
    unsigned int nObj      = 1;
    for (size_t i = nObj; i < _constraintProperties->size(); i++) {
        for (unsigned j = 0; j < (*_constraintProperties)[i].nparticipatingVariables; j++) {
            jac[consIndex] = gradient[i * _nvar + (*_constraintProperties)[i].participatingVariables[j]];
            consIndex++;
        }
    }
    return 0;
}

/////////////////////////////////////////////////////////////////////////
// return the Hessian of the Lagrangian
int
KnitroProblem::evaluateHess(const double* const x, double objScaler, const double* const lambda, double* const hess)
{


    std::vector<double> hessian(_nvar * _nvar * (1 + _nineq + _neq + _nineqSquash));
    ubp::evaluate_hessian(x, _nvar, _nineq + _neq + _nineqSquash, hessian.data(), _DAGobj);

    double hess_f_value;    // Temp value for entry in hessian of f
    double hess_g_value;    // Temp value for entry in hessian of contraints

    for (unsigned index = 0; index < _structure->nonZeroHessianIRow.size(); index++) {

        unsigned jVar = _structure->nonZeroHessianIRow[index];
        unsigned iVar = _structure->nonZeroHessianJCol[index];
        hess_f_value  = hessian[jVar * _nvar + iVar];
        hess_g_value  = 0;
        unsigned nObj = 1;
        for (size_t i = nObj; i < _constraintProperties->size(); i++) {
            hess_g_value += lambda[i - nObj] * hessian[(i * _nvar + jVar) * _nvar + iVar];
        }

        hess[index] = objScaler * hess_f_value + hess_g_value;
    }
    return 0;
}


#endif
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

#ifdef HAVE_GUROBI

#include "ubpGurobi.h"
#include "MAiNGOException.h"
#include "ubpDagObj.h"
#include "ubpEvaluators.h"
#include "ubpQuadExpr.h"


using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor for the upper bounding solver
UbpGurobi::UbpGurobi(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
                     const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn,
                     std::shared_ptr< std::vector<Constraint> > constraintPropertiesIn, UBS_USE useIn) :
    UpperBoundingSolver(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn),
    grbEnv(GRBEnv()), grbModel(GRBModel(grbEnv))
{
    try {

        // Actual problem variables
        grbVars.resize(_nvar);
        std::vector<UbpQuadExpr> coefficients(_nvar);
        for (unsigned i = 0; i < _nvar; i++) {
            if (variables[i].get_variable_type() > babBase::enums::VT_CONTINUOUS) {
                grbVars[i] = grbModel.addVar(variables[i].get_lower_bound(), variables[i].get_upper_bound(), 0.0, GRB_INTEGER);
            }
            else {
                grbVars[i] = grbModel.addVar(variables[i].get_lower_bound(), variables[i].get_upper_bound(), 0.0, GRB_CONTINUOUS);
            }
            coefficients[i] = UbpQuadExpr(_nvar, i);
        }

        std::vector<UbpQuadExpr> resultCoefficients(_DAGobj->functions.size());
        std::vector<UbpQuadExpr> dummyCoefficients(_DAGobj->subgraph.l_op.size());

        _DAGobj->DAG.eval(_DAGobj->subgraph, dummyCoefficients, _DAGobj->functions.size(), _DAGobj->functions.data(), resultCoefficients.data(), _nvar, _DAGobj->vars.data(), coefficients.data());

        // Add functions to the model
        for (size_t i = 0; i < _constraintProperties->size(); i++) {
            unsigned index = (*_constraintProperties)[i].indexNonconstantUBP;
#ifdef LAZYQUAD
            ///QuadExpr constructedResult=resultCoefficients[index].assemble_quadratic_expression_element_wise(_nvar);
            QuadExpr constructedResult = resultCoefficients[index].assemble_quadratic_expression_matrix_wise(_nvar);
#endif
            GRBQuadExpr quadExpr = GRBQuadExpr();
            for (size_t k = 0; k < _nvar; k++) {
#ifdef LAZYQUAD
                double linearCoeff = constructedResult.linearPart.get_value(k);
#else
                double linearCoeff = resultCoefficients[index].coeffsLin[k];
#endif
                if (linearCoeff != 0.0) {
                    quadExpr += linearCoeff * grbVars[k];
                }
                for (size_t j = 0; j < _nvar; j++) {
#ifdef LAZYQUAD
                    double quadCoeff = constructedResult.quadraticPart.get_element(k,j);
#else
                    double quadCoeff = resultCoefficients[index].coeffsQuad[k][j];
#endif
                    if (quadCoeff != 0.0) {
                        quadExpr += quadCoeff * grbVars[k] * grbVars[j];
                    }
                }
            }
#ifdef LAZYQUAD
            quadExpr += constructedResult.linearPart.constant();
#else
            quadExpr += resultCoefficients[index].constant;
#endif
            switch ((*_constraintProperties)[i].type) {
                case OBJ:
                    grbModel.setObjective(quadExpr, GRB_MINIMIZE);
                    break;
                case INEQ:
                    grbModel.addQConstr(quadExpr, GRB_LESS_EQUAL, 0);
                    break;
                case EQ:
                    grbModel.addQConstr(quadExpr, GRB_EQUAL, 0);
                    break;
                case INEQ_SQUASH:
                    grbModel.addQConstr(quadExpr, GRB_LESS_EQUAL, 0);
                    break;
                case INEQ_REL_ONLY:
                case EQ_REL_ONLY:
                case AUX_EQ_REL_ONLY:
                default:
                    break;    // We don't use relaxation only constraint in upper bounding
            }
        }

        // Use the Barrier method
        grbModel.set(GRB_IntParam_Method, 2);
        // Suppress output
        // Before changing (and printing) settings
        if (_maingoSettings->UBP_verbosity <= VERB_NORMAL || _maingoSettings->loggingDestination == 0 || _maingoSettings->loggingDestination == 2) {
            grbModel.set(GRB_IntParam_OutputFlag, 0);
        }
        // Set option
        grbModel.set(GRB_DoubleParam_OptimalityTol, 1e-9);
        grbModel.set(GRB_DoubleParam_BarConvTol, _maingoSettings->epsilonA);
        grbModel.set(GRB_DoubleParam_BarQCPConvTol, _maingoSettings->epsilonA);
        grbModel.set(GRB_DoubleParam_FeasibilityTol, std::max(_maingoSettings->deltaIneq, _maingoSettings->deltaEq));
    }
    catch (const std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error initializing UbpGurobi.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error initializing UbpGurobi.");
    }
} // GCOVR_EXCL_STOP


/////////////////////////////////////////////////////////////////////////
// destructor for Gurobi
UbpGurobi::~UbpGurobi(){}


/////////////////////////////////////////////////////////////////////////
// solve the underlying problem
SUBSOLVER_RETCODE
UbpGurobi::_solve_nlp(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, double &objectiveValue, std::vector<double> &solutionPoint)
{

    // Solve the problem
    try {
        grbModel.optimize();
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while solving the UBP with Gurobi.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while solving UBP with Gurobi.");
    }
    // GCOVR_EXCL_STOP
    // Get Gurobi status
    int grbStatus = grbModel.get(GRB_IntAttr_Status);

    if ((grbStatus == GRB_INFEASIBLE) || (grbStatus == GRB_INF_OR_UNBD)) {
        return SUBSOLVER_INFEASIBLE;
    }
    else if (grbStatus == GRB_LOADED) {
        return SUBSOLVER_INFEASIBLE;
    }
    if (_maingoSettings->LBP_verbosity >= VERB_ALL) {
        std::ostringstream outstr;
        outstr << "  UBP status: " << grbStatus << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
    }

    // Get objective value
    objectiveValue = grbModel.get(GRB_DoubleAttr_ObjVal);

    // Process solution: solution point
    std::vector<double> vals(_nvar);
    try {
        for (unsigned i = 0; i < _nvar; i++) {
            vals[i] = grbVars[i].get(GRB_DoubleAttr_X);
        }
    }
    catch (GRBException &e) {
        std::vector<double> midPoint(_nvar);
        for (unsigned int i = 0; i < _nvar; i++) {
            int varType(_originalVariables[i].get_variable_type());
            if (varType == babBase::enums::VT_BINARY || varType == babBase::enums::VT_INTEGER) {
                midPoint[i] = lowerVarBounds[i];
            }
            else {
                midPoint[i] = 0.5 * (lowerVarBounds[i] + upperVarBounds[i]);
            }
        }
        double objValue = evaluate_objective(midPoint.data(), _nvar, false, nullptr, _DAGobj);
        SUBSOLVER_RETCODE isFeasible;
        if (objValue == objectiveValue) {
            isFeasible = check_feasibility(midPoint, objValue);
        }
        if (isFeasible != SUBSOLVER_FEASIBLE) {
            std::ostringstream outstr;
            outstr << "  Warning: Variables at solution of UBP could not be extracted from Gurobi:" << e.getMessage() << std::endl;
            _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
            // Return empty solution instead
            vals.end();
            solutionPoint.clear();
        }
        else {    // If point is feasible and the objective is correct, return it
            solutionPoint = midPoint;
        }
        return SUBSOLVER_FEASIBLE;
    }
    catch (...) { // GCOVR_EXCL_START
        throw MAiNGOException("  Unknown error while querying solution point from Gurobi.");
    }
    // GCOVR_EXCL_STOP
    // Ok, successfully obtained solution point
    solutionPoint.clear();
    for (unsigned int i = 0; i < _nvar; i++) {
        solutionPoint.push_back(vals[i]);
    }
    vals.end();

    _logger->print_vector(_nvar, solutionPoint, "  UBP solution point: ", VERB_ALL, UBP_VERBOSITY);

    return SUBSOLVER_FEASIBLE;
}

#endif

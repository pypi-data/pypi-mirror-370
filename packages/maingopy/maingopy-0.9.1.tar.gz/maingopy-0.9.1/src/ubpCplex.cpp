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

#ifdef HAVE_CPLEX

#include "ubpCplex.h"
#include "MAiNGOException.h"
#include "ubpDagObj.h"
#include "ubpEvaluators.h"
#include "ubpQuadExpr.h"


using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor for the upper bounding solver
UbpCplex::UbpCplex(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
                   const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn):
    UpperBoundingSolver(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn)
{
    try {
        // Initialize CPLEX problem
        // Model and variables
        cplxModel = IloModel(cplxEnv);

        // Actual problem variables
        cplxVars = IloNumVarArray(cplxEnv);
        std::vector<UbpQuadExpr> coefficients(_nvar);
        for (unsigned i = 0; i < _nvar; i++) {
            if (variables[i].get_variable_type() > babBase::enums::VT_CONTINUOUS) {
                cplxVars.add(IloNumVar(cplxEnv, variables[i].get_lower_bound(), variables[i].get_upper_bound(), ILOINT));
            }
            else {
                cplxVars.add(IloNumVar(cplxEnv, variables[i].get_lower_bound(), variables[i].get_upper_bound(), ILOFLOAT));
            }
            coefficients[i] = UbpQuadExpr(_nvar, i);
        }

        cplxModel.add(cplxVars);

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
            IloExpr expr(cplxEnv);
            for (size_t k = 0; k < _nvar; k++) {
#ifdef LAZYQUAD
                double linearCoeff = constructedResult.linearPart.get_value(k);
#else
                double linearCoeff = resultCoefficients[index].coeffsLin[k];
#endif
                if (linearCoeff != 0.0) {
                    expr += linearCoeff * cplxVars[k];
                }
                for (size_t j = 0; j < _nvar; j++) {
#ifdef LAZYQUAD
                    double quadCoeff = constructedResult.quadraticPart.get_element(k, j);
#else
                    double quadCoeff = resultCoefficients[index].coeffsQuad[k][j];
#endif
                    if (quadCoeff != 0.0) {
                        expr += quadCoeff * cplxVars[k] * cplxVars[j];
                    }
                }
            }
#ifdef LAZYQUAD
            expr += constructedResult.linearPart.constant();
#else
            expr += resultCoefficients[index].constant;
#endif
            switch ((*_constraintProperties)[i].type) {
                case OBJ:
                    cplxModel.add(IloMinimize(cplxEnv, expr));
                    break;
                case INEQ:
                    cplxModel.add(IloRange(cplxEnv, expr, 0.));
                    break;
                case EQ:
                    cplxModel.add(IloRange(cplxEnv, expr, 0.));
                    cplxModel.add(IloRange(cplxEnv, -expr, 0.));
                    break;
                case INEQ_SQUASH:
                    cplxModel.add(IloRange(cplxEnv, expr, 0.));
                    break;
                case INEQ_REL_ONLY:
                case EQ_REL_ONLY:
                case AUX_EQ_REL_ONLY:
                default:
                    break;    // We don't use relaxation only constraints in upper bounding
            }
        }

        cplex = IloCplex(cplxModel);
        // Use the Barrier method
        cplex.setParam(IloCplex::RootAlg, IloCplex::Dual);
        // Set options
        cplex.setParam(IloCplex::EpOpt, 1e-9);
        cplex.setParam(IloCplex::Param::Barrier::ConvergeTol, _maingoSettings->epsilonA);
        cplex.setParam(IloCplex::Param::Barrier::QCPConvergeTol, _maingoSettings->epsilonA);
        cplex.setParam(IloCplex::EpRHS, std::max(_maingoSettings->deltaIneq, _maingoSettings->deltaEq));
        cplex.setParam(IloCplex::Param::TimeLimit, _maingoSettings->maxTime);                            // Preprocessing not considered
        cplex.setParam(IloCplex::EpAGap, _maingoSettings->epsilonA);                                     // Absolute gap for MILP case
        cplex.setParam(IloCplex::EpGap, std::max(0.0,std::min(1.0,_maingoSettings->epsilonR)));          // Relative gap for MILP case
        cplex.setParam(IloCplex::Param::RandomSeed, 42);                                                 // Make the behavior of CPLEX deterministic

        // Suppress output:
        // Suppress output - unfortunately we cannot redirect the output of CPLEX to our log file right now...
        if ((_maingoSettings->LBP_verbosity <= VERB_NORMAL) || (_maingoSettings->loggingDestination == LOGGING_NONE) || (_maingoSettings->loggingDestination == LOGGING_FILE)) {
            cplex.setOut(cplxEnv.getNullStream());
            cplex.setWarning(cplxEnv.getNullStream());
        }
        // Obtain global solution of non-convex MIQCPs
        cplex.setParam(IloCplex::OptimalityTarget, CPX_OPTIMALITYTARGET_OPTIMALGLOBAL);
    }
    catch (const std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error initializing UbpCplex.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error initializing UbpCplex.");
    }
} // GCOVR_EXCL_STOP


/////////////////////////////////////////////////////////////////////////
// solve the underlying problem
SUBSOLVER_RETCODE
UbpCplex::_solve_nlp(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, double &objectiveValue, std::vector<double> &solutionPoint)
{

    // Solve the problem
    try {
        cplex.solve();
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while solving the UBP with CPLEX.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while solving UBP with CPLEX.");
    }
    // GCOVR_EXCL_STOP
    // Get CPLEX status
    IloAlgorithm::Status cplexStatus = cplex.getStatus();
    if ((cplexStatus == IloAlgorithm::Infeasible) || (cplexStatus == IloAlgorithm::InfeasibleOrUnbounded)) {
        return SUBSOLVER_INFEASIBLE;
    }
    else if (cplexStatus == IloAlgorithm::Unknown) {
        return SUBSOLVER_INFEASIBLE;
    }
    if (_maingoSettings->LBP_verbosity >= VERB_ALL) {
        std::ostringstream outstr;
        outstr << "  UBP status: " << cplexStatus << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
    }

    // Get objective value
    objectiveValue = cplex.getObjValue();

    // Process solution: solution point
    IloNumArray vals(cplxEnv);
    try {
        cplex.getValues(vals, cplxVars);
    }
    catch (IloException &e) {
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
            outstr << "  Warning: Variables at solution of UBP could not be extracted from CPLEX:" << e << std::endl;
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
        throw MAiNGOException("  Unknown error while querying solution point from CPLEX.");
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


/////////////////////////////////////////////////////////////////////////
// function for termination CPLEX
void
UbpCplex::_terminate_cplex()
{
    cplex.end();
    cplxVars.endElements();
    cplxVars.end();
    cplxModel.end();
    cplxEnv.end();
}

#endif

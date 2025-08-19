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

#include "lbpCplex.h"
#include "MAiNGOException.h"
#include "lbpDagObj.h"
#include "instrumentor.h"


using namespace maingo;
using namespace lbp;


/////////////////////////////////////////////////////////////////////////////////////////////
// constructor for the lower bounding solver
LbpCplex::LbpCplex(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
                         const std::vector<bool>& variableIsLinear, const unsigned nineqIn, const unsigned neqIn, const unsigned nineqRelaxationOnlyIn, const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn,
                         std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn):
    LowerBoundingSolver(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn, nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn)
{

    try {

        // Initialize generic CPLEX problem
        // Model and variables
        cplxModel = IloModel(cplxEnv);
        // Dummy objective variable
        eta = IloNumVar(cplxEnv, -IloInfinity, IloInfinity, ILOFLOAT);
        cplxModel.add(eta);
        // Actual problem variables
        cplxVars = IloNumVarArray(cplxEnv);
        for (unsigned i = 0; i < _nvar; i++) {
            cplxVars.add(IloNumVar(cplxEnv, variables[i].get_lower_bound(), variables[i].get_upper_bound(), ILOFLOAT));
        }
        cplxModel.add(cplxVars);
        // Dummy objective function: minimize eta
        cplxObjective = IloMinimize(cplxEnv, eta);
        cplxModel.add(cplxObjective);
        // Actual objective function(s) (i.e., the different linearizations of our objective function(s))
        linObj.resize(1);
        for (unsigned i = 0; i < 1; i++) {
            linObj[i] = IloRangeArray(cplxEnv);
            for (unsigned j = 0; j < _nLinObj[i]; j++) {
                linObj[i].add(IloRange(cplxEnv, -1.0 * eta, 1e19));
            }
            cplxModel.add(linObj[i]);
        }
        etaCoeff = -1;
        // Constraints:
        // Initialize inequality constraints
        linIneq.resize(_nineq);
        for (unsigned i = 0; i < _nineq; i++) {
            linIneq[i] = IloRangeArray(cplxEnv);
            for (unsigned j = 0; j < _nLinIneq[i]; j++) {
                linIneq[i].add(IloRange(cplxEnv, cplxVars[0], 1e19));
            }
            cplxModel.add(linIneq[i]);
        }
        // Initialize equality constraints (eqs --> two ineqs each)
        linEq1.resize(_neq);
        linEq2.resize(_neq);
        // Convex part equalities -- This order is important for the infeasibility check
        for (unsigned i = 0; i < _neq; i++) {
            linEq1[i] = IloRangeArray(cplxEnv);
            linEq2[i] = IloRangeArray(cplxEnv);
            for (unsigned j = 0; j < _nLinEq[i]; j++) {
                linEq1[i].add(IloRange(cplxEnv, cplxVars[0], 1e19));
                // linEq2[i].add(IloRange(cplxEnv,cplxVars[0],1e19));
            }
            cplxModel.add(linEq1[i]);
        }
        // Concave part equalities
        for (unsigned i = 0; i < _neq; i++) {
            linEq2[i] = IloRangeArray(cplxEnv);
            for (unsigned j = 0; j < _nLinEq[i]; j++) {
                linEq2[i].add(IloRange(cplxEnv, cplxVars[0], 1e19));
            }
            cplxModel.add(linEq2[i]);
        }
        // Relaxation-only inequalities
        linIneqRelaxationOnly.resize(_nineqRelaxationOnly);
        for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
            linIneqRelaxationOnly[i] = IloRangeArray(cplxEnv);
            for (unsigned j = 0; j < _nLinIneqRelaxationOnly[i]; j++) {
                linIneqRelaxationOnly[i].add(IloRange(cplxEnv, cplxVars[0], 1e19));    // Expression cplxVars[0] is used as a dummy since the actual coefficients are set for every node in function update_linearization
            }
            cplxModel.add(linIneqRelaxationOnly[i]);
        }
        // Relaxation-only equalities
        linEqRelaxationOnly1.resize(_neqRelaxationOnly);
        linEqRelaxationOnly2.resize(_neqRelaxationOnly);
        // Convex part relaxation only equalities -- This order is important for the infeasibility check
        for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
            linEqRelaxationOnly1[i] = IloRangeArray(cplxEnv);
            for (unsigned j = 0; j < _nLinEqRelaxationOnly[i]; j++) {
                linEqRelaxationOnly1[i].add(IloRange(cplxEnv, cplxVars[0], 1e19));
            }
            cplxModel.add(linEqRelaxationOnly1[i]);
        }
        // Concave part relaxation only equalities
        for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
            linEqRelaxationOnly2[i] = IloRangeArray(cplxEnv);
            for (unsigned j = 0; j < _nLinEqRelaxationOnly[i]; j++) {
                linEqRelaxationOnly2[i].add(IloRange(cplxEnv, cplxVars[0], 1e19));
            }
            cplxModel.add(linEqRelaxationOnly2[i]);
        }
        // Initialize squash inequality constraints
        linIneqSquash.resize(_nineqSquash);
        for (unsigned i = 0; i < _nineqSquash; i++) {
            linIneqSquash[i] = IloRangeArray(cplxEnv);
            for (unsigned j = 0; j < _nLinIneqSquash[i]; j++) {
                linIneqSquash[i].add(IloRange(cplxEnv, cplxVars[0], 1e19));
            }
            cplxModel.add(linIneqSquash[i]);
        }

        // Initialize CPLEX solver
        cplex = IloCplex(cplxModel);
        #ifdef _OPENMP
            // Ensure each CPLEX instance only starts one thread, since we're using one thread per logical core already
            cplex.setParam(IloCplex::Threads, 1);
        #endif
        // Do not warm-start from previous solution since problems are too dissimilar (warm-start can lead to spurious results!!):
        cplex.setParam(IloCplex::AdvInd, 0);
        cplex.setParam(IloCplex::RootAlg, IloCplex::Dual);
        // Set number of max iterations - Sometimes CPLEX just can't solve the LP in considerable time
        cplex.setParam(IloCplex::Param::Simplex::Limits::Iterations, 100000);
        cplex.setParam(IloCplex::Param::Barrier::Limits::Iteration, 100000);
        cplex.setParam(IloCplex::Param::Network::Iterations, 100000);
        // Set max time to half of the available - Sometimes CPLEX just can't solve the LP in considerable time
        cplex.setParam(IloCplex::Param::TimeLimit, _maingoSettings->maxTime / 2);
        // Set options
        cplex.setParam(IloCplex::EpOpt, 1e-9);              // Tightest possible opt tolerance in CPLEX
        cplex.setParam(IloCplex::EpRHS, 1e-9);              // Tightest possible feas tolerance in CPLEX
        cplex.setParam(IloCplex::Param::RandomSeed, 42);    // Make the behavior of CPLEX deterministic
        // Disable scaling of LP matrix, we experienced numerical problems within CPLEX for scaled problems, e.g., CPLEX declaring problems as infeasible although there is a delta-feasible point
        cplex.setParam(IloCplex::Param::Read::Scale, 0);
        // Suppress output - unfortunately we cannot redirect the output of CPLEX to our log file right now...
        if ((_maingoSettings->LBP_verbosity <= VERB_NORMAL) || (_maingoSettings->loggingDestination == LOGGING_NONE) || (_maingoSettings->loggingDestination == LOGGING_FILE)) {
            cplex.setOut(cplxEnv.getNullStream());
            cplex.setWarning(cplxEnv.getNullStream());
        }

#ifdef LP__OPTIMALITY_CHECK
        farkasCons = IloRangeArray(cplxEnv);
        farkasVals = IloNumArray(cplxEnv);
        dualValsObj.resize(1);
        dualValsObj[0] = IloNumArray(cplxEnv);
        dualValsIneq.resize(_nineq);
        for (unsigned i = 0; i < _nineq; i++) {
            dualValsIneq[i] = IloNumArray(cplxEnv);
        }
        dualValsEq1.resize(_neq);
        for (unsigned i = 0; i < _neq; i++) {
            dualValsEq1[i] = IloNumArray(cplxEnv);
        }
        dualValsEq2.resize(_neq);
        for (unsigned i = 0; i < _neq; i++) {
            dualValsEq2[i] = IloNumArray(cplxEnv);
        }
        dualValsIneqRelaxationOnly.resize(_nineqRelaxationOnly);
        for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
            dualValsIneqRelaxationOnly[i] = IloNumArray(cplxEnv);
        }
        dualValsEqRelaxationOnly1.resize(_neqRelaxationOnly);
        for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
            dualValsEqRelaxationOnly1[i] = IloNumArray(cplxEnv);
        }
        dualValsEqRelaxationOnly2.resize(_neqRelaxationOnly);
        for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
            dualValsEqRelaxationOnly2[i] = IloNumArray(cplxEnv);
        }
        dualValsIneqSquash.resize(_nineqSquash);
        for (unsigned i = 0; i < _nineqSquash; i++) {
            dualValsIneqSquash[i] = IloNumArray(cplxEnv);
        }
#endif
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error initializing CPLEX during initialization of LowerBoundingSolver.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error initializing CPLEX during initialization of LowerBoundingSolver.");
    }
}// GCOVR_EXCL_STOP


/////////////////////////////////////////////////////////////////////////////////////////////
// destructor for CPLEX
LbpCplex::~LbpCplex()
{

    _terminate_cplex();
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function called by the B&B in preprocessing in order to check the need for specific options, currently for subgradient intervals & CPLEX no large values
void
LbpCplex::activate_more_scaling()
{

    // Enable aggressive scaling of LP matrix. Since we experienced numerical problems within CPLEX if its scaling is enabled, we only turn scaling on if it was heuristically called from the B&B
    cplex.setParam(IloCplex::Param::Read::Scale, 1);
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for setting the bounds of variables
void
LbpCplex::_set_variable_bounds(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    IloNumArray tmpLower(cplxEnv), tmpUpper(cplxEnv);
    for (unsigned int i = 0; i < _nvar; i++) {
        tmpLower.add(lowerVarBounds[i]);
        tmpUpper.add(upperVarBounds[i]);
    }
    cplxVars.setBounds(tmpLower, tmpUpper);
    tmpLower.end();
    tmpUpper.end();
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an objective of the linear program
void
LbpCplex::_update_LP_obj(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iObj)
{

    // Linearize objective function:
    if (resultRelaxation.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of the relaxed objective function for CPLEX: objective function does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    double rhs = 0; // GCOVR_EXCL_STOP
    // If the numbers are too large, we simply set the whole row to 0
    // NOTE: second check is for NaN
    if (std::fabs(-resultRelaxation.cv()) > 1e19 || (resultRelaxation.cv() != resultRelaxation.cv())) {

        linObj[iObj][iLin].setUB(1e19);
        _objectiveScalingFactors[iObj][iLin] = 1.;
#ifdef LP__OPTIMALITY_CHECK
        _rhsObj[iObj][iLin] = 1e19;
#endif
        for (unsigned int j = 0; j < _nvar; j++) {
            linObj[iObj][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
            _matrixObj[iObj][iLin][j] = 0;
#endif
        }
    }
    else {
        rhs = -resultRelaxation.cv();
        for (unsigned int j = 0; j < _nvar; j++) {
            rhs += resultRelaxation.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxation.cvsub(), resultRelaxation.cvsub() + _nvar);    // Iterator range constructor
        coefficients.push_back(etaCoeff);
        _objectiveScalingFactors[iObj][iLin] = _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);    // This function does the scaling, but for the objective we also need the factor later for OBBT
        for (unsigned int j = 0; j < _nvar; j++) {
            linObj[iObj][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
            _matrixObj[iObj][iLin][j] = coefficients[j];
#endif
        }
        linObj[iObj][iLin].setLinearCoef(eta, coefficients[_nvar]);
        linObj[iObj][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
        _rhsObj[iObj][iLin] = rhs;
#endif
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LbpCplex::_update_LP_ineq(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneq)
{

    // Linearize inequality constraints:
    if (resultRelaxation.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed inequality constraint " << iIneq + 1 << " (of " << _nineq << ") for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    double rhs = 0; // GCOVR_EXCL_STOP
    if (std::fabs(-resultRelaxation.cv()) > 1e19 || (resultRelaxation.cv() != resultRelaxation.cv())) {
        linIneq[iIneq][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
        _rhsIneq[iIneq][iLin] = 0;
#endif
        for (unsigned int j = 0; j < _nvar; j++) {
            linIneq[iIneq][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
            _matrixIneq[iIneq][iLin][j] = 0;
#endif
        }
    }
    else {
        rhs = -resultRelaxation.cv() + _maingoSettings->deltaIneq;
        for (unsigned int j = 0; j < _nvar; j++) {
            rhs += resultRelaxation.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxation.cvsub(), resultRelaxation.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned int j = 0; j < _nvar; j++) {
            linIneq[iIneq][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
            _matrixIneq[iIneq][iLin][j] = coefficients[j];
#endif
        }
        linIneq[iIneq][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
        _rhsIneq[iIneq][iLin] = rhs;
#endif
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LbpCplex::_update_LP_eq(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEq)
{

    // Linearize equality Constraints:
    if (resultRelaxationCv.nsub() == 0 || resultRelaxationCc.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed equality constraint " << iEq + 1 << " (of " << _neq << ") for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    double rhs = 0; // GCOVR_EXCL_STOP
    // Convex relaxation <=0:
    if (std::fabs(resultRelaxationCv.cv()) > 1e19 || (resultRelaxationCv.cv() != resultRelaxationCv.cv())) {
        linEq1[iEq][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
        _rhsEq1[iEq][iLin] = 0;
#endif
        for (unsigned int j = 0; j < _nvar; j++) {
            linEq1[iEq][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
            _matrixEq1[iEq][iLin][j] = 0;
#endif
        }
    }
    else {
        rhs = -resultRelaxationCv.cv() + _maingoSettings->deltaEq;
        for (unsigned int j = 0; j < _nvar; j++) {
            rhs += resultRelaxationCv.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxationCv.cvsub(), resultRelaxationCv.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned int j = 0; j < _nvar; j++) {
            linEq1[iEq][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
            _matrixEq1[iEq][iLin][j] = coefficients[j];
#endif
        }
        linEq1[iEq][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
        _rhsEq1[iEq][iLin] = rhs;
#endif
    }
    // Set up concave >=0 part:
    if (std::fabs(resultRelaxationCc.cc()) > 1e19 || (resultRelaxationCc.cc() != resultRelaxationCc.cc())) {

        linEq2[iEq][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
        _rhsEq2[iEq][iLin] = 0;
#endif
        for (unsigned int j = 0; j < _nvar; j++) {
            linEq2[iEq][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
            _matrixEq2[iEq][iLin][j] = 0;
#endif
        }
    }
    else {
        rhs = resultRelaxationCc.cc() + _maingoSettings->deltaEq;
        for (unsigned int j = 0; j < _nvar; j++) {
            rhs -= resultRelaxationCc.ccsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxationCc.ccsub(), resultRelaxationCc.ccsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned int j = 0; j < _nvar; j++) {
            linEq2[iEq][iLin].setLinearCoef(cplxVars[j], -coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
            _matrixEq2[iEq][iLin][j] = -coefficients[j];
#endif
        }
        linEq2[iEq][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
        _rhsEq2[iEq][iLin] = rhs;
#endif
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only inequality of the linear program
void
LbpCplex::_update_LP_ineqRelaxationOnly(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqRelaxationOnly)
{

    // Linearize relaxation only inequalities
    if (resultRelaxation.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxation-only inequality constraint " << iIneqRelaxationOnly + 1 << " (of " << _nineqRelaxationOnly << ") for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    double rhs = 0; // GCOVR_EXCL_STOP
    if (std::fabs(resultRelaxation.cv()) > 1e19 || (resultRelaxation.cv() != resultRelaxation.cv())) {
        linIneqRelaxationOnly[iIneqRelaxationOnly][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
        _rhsIneqRelaxationOnly[iIneqRelaxationOnly][iLin] = 0;
#endif
        for (unsigned int j = 0; j < _nvar; j++) {
            linIneqRelaxationOnly[iIneqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
            _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][j] = 0;
#endif
        }
    }
    else {
        rhs = -resultRelaxation.cv() + _maingoSettings->deltaIneq;
        for (unsigned int j = 0; j < _nvar; j++) {
            rhs += resultRelaxation.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxation.cvsub(), resultRelaxation.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned int j = 0; j < _nvar; j++) {
            linIneqRelaxationOnly[iIneqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
            _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][j] = coefficients[j];
#endif
        }
        linIneqRelaxationOnly[iIneqRelaxationOnly][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
        _rhsIneqRelaxationOnly[iIneqRelaxationOnly][iLin] = rhs;
#endif
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LbpCplex::_update_LP_eqRelaxationOnly(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEqRelaxationOnly)
{

    // Linearize relaxation only equalities
    if (resultRelaxationCv.nsub() == 0 || resultRelaxationCc.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxation-only equality constraint " << iEqRelaxationOnly + 1 << " (of " << _neqRelaxationOnly << ") for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    double rhs = 0; // GCOVR_EXCL_STOP
    // Convex relaxation <=0:
    if (std::fabs(resultRelaxationCv.cv()) > 1e19 || (resultRelaxationCv.cv() != resultRelaxationCv.cv())) {
        linEqRelaxationOnly1[iEqRelaxationOnly][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
        _rhsEqRelaxationOnly1[iEqRelaxationOnly][iLin] = 0;
#endif
        for (unsigned int j = 0; j < _nvar; j++) {
            linEqRelaxationOnly1[iEqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
            _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][j] = 0;
#endif
        }
    }
    else {
        rhs = -resultRelaxationCv.cv() + _maingoSettings->deltaEq;
        for (unsigned int j = 0; j < _nvar; j++) {
            rhs += resultRelaxationCv.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxationCv.cvsub(), resultRelaxationCv.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned int j = 0; j < _nvar; j++) {
            linEqRelaxationOnly1[iEqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
            _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][j] = coefficients[j];
#endif
        }
#ifdef LP__OPTIMALITY_CHECK
        _rhsEqRelaxationOnly1[iEqRelaxationOnly][iLin] = rhs;
#endif
        linEqRelaxationOnly1[iEqRelaxationOnly][iLin].setUB(rhs);
    }
    // Set up concave >=0 part:
    if (std::fabs(resultRelaxationCc.cc()) > 1e19 || (resultRelaxationCc.cc() != resultRelaxationCc.cc())) {
        linEqRelaxationOnly2[iEqRelaxationOnly][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
        _rhsEqRelaxationOnly2[iEqRelaxationOnly][iLin] = 0;
#endif
        for (unsigned int j = 0; j < _nvar; j++) {
            linEqRelaxationOnly2[iEqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
            _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][j] = 0;
#endif
        }
    }
    else {
        rhs = resultRelaxationCc.cc() + _maingoSettings->deltaEq;
        for (unsigned int j = 0; j < _nvar; j++) {
            rhs -= resultRelaxationCc.ccsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxationCc.ccsub(), resultRelaxationCc.ccsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned int j = 0; j < _nvar; j++) {
            linEqRelaxationOnly2[iEqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], -coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
            _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][j] = -coefficients[j];
#endif
        }
#ifdef LP__OPTIMALITY_CHECK
        _rhsEqRelaxationOnly2[iEqRelaxationOnly][iLin] = rhs;
#endif
        linEqRelaxationOnly2[iEqRelaxationOnly][iLin].setUB(rhs);
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LbpCplex::_update_LP_ineq_squash(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqSquash)
{

    // Linearize inequality constraints:
    if (resultRelaxation.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed squash inequality constraint " << iIneqSquash + 1 << " (of " << _nineqSquash << ") for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    double rhs = 0; // GCOVR_EXCL_STOP
    if (std::fabs(-resultRelaxation.cv()) > 1e19 || (resultRelaxation.cv() != resultRelaxation.cv())) {
        linIneqSquash[iIneqSquash][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
        _rhsIneqSquash[iIneqSquash][iLin] = 0;
#endif
        for (unsigned int j = 0; j < _nvar; j++) {
            linIneqSquash[iIneqSquash][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
            _matrixIneqSquash[iIneqSquash][iLin][j] = 0;
#endif
        }
    }
    else {
        rhs = -resultRelaxation.cv();    // No tolerance added!
        for (unsigned int j = 0; j < _nvar; j++) {
            rhs += resultRelaxation.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxation.cvsub(), resultRelaxation.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned int j = 0; j < _nvar; j++) {
            linIneqSquash[iIneqSquash][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
            _matrixIneqSquash[iIneqSquash][iLin][j] = coefficients[j];
#endif
        }
        linIneqSquash[iIneqSquash][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
        _rhsIneqSquash[iIneqSquash][iLin] = rhs;
#endif
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an objective of the linear program
void
LbpCplex::_update_LP_obj(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iObj)
{

    // Linearize objective function:
    if (resultRelaxationVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of the relaxed objective function (vector) for CPLEX: objective function does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinObj[0];
    for (unsigned int iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        // If the numbers are too large, we simply set the whole row to 0
        // NOTE: second check is for NaN
        if (std::fabs(-resultRelaxationVMC.cv(iLin)) > 1e19 || (resultRelaxationVMC.cv(iLin) != resultRelaxationVMC.cv(iLin))) {

            linObj[iObj][iLin].setUB(1e19);
            _objectiveScalingFactors[iObj][iLin] = 1.;
#ifdef LP__OPTIMALITY_CHECK
            _rhsObj[iObj][iLin] = 1e19;
#endif
            for (unsigned int j = 0; j < _nvar; j++) {
                linObj[iObj][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
                _matrixObj[iObj][iLin][j] = 0;
#endif
            }
        }
        else {
            rhs = -resultRelaxationVMC.cv(iLin);
            for (unsigned int j = 0; j < _nvar; j++) {
                rhs += resultRelaxationVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationVMC.cvsub(iLin), resultRelaxationVMC.cvsub(iLin) + _nvar);    // Iterator range constructor
            coefficients.push_back(etaCoeff);
            _objectiveScalingFactors[iObj][iLin] = _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);    // This function does the scaling, but for the objective we also need the factor later for OBBT
            for (unsigned int j = 0; j < _nvar; j++) {
                linObj[iObj][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
                _matrixObj[iObj][iLin][j] = coefficients[j];
#endif
            }
            linObj[iObj][iLin].setLinearCoef(eta, coefficients[_nvar]);
            linObj[iObj][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
            _rhsObj[iObj][iLin] = rhs;
#endif
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LbpCplex::_update_LP_ineq(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneq)
{

    // Linearize inequality constraints:
    if (resultRelaxationVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed inequality constraint " << iIneq + 1 << " (of " << _nineq << ") (vector) for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinIneq[iIneq];
    for (unsigned int iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        if (std::fabs(-resultRelaxationVMC.cv(iLin)) > 1e19 || (resultRelaxationVMC.cv(iLin) != resultRelaxationVMC.cv(iLin))) {
            linIneq[iIneq][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
            _rhsIneq[iIneq][iLin] = 0;
#endif
            for (unsigned int j = 0; j < _nvar; j++) {
                linIneq[iIneq][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
                _matrixIneq[iIneq][iLin][j] = 0;
#endif
            }
        }
        else {
            rhs = -resultRelaxationVMC.cv(iLin) + _maingoSettings->deltaIneq;
            for (unsigned int j = 0; j < _nvar; j++) {
                rhs += resultRelaxationVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationVMC.cvsub(iLin), resultRelaxationVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned int j = 0; j < _nvar; j++) {
                linIneq[iIneq][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
                _matrixIneq[iIneq][iLin][j] = coefficients[j];
#endif
            }
            linIneq[iIneq][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
            _rhsIneq[iIneq][iLin] = rhs;
#endif
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LbpCplex::_update_LP_eq(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iEq)
{

    // Linearize equality Constraints:
    if (resultRelaxationCvVMC.nsub() == 0 || resultRelaxationCcVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed equality constraint " << iEq + 1 << " (of " << _neq << ") (vector) for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinEq[iEq];
    for (unsigned int iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        // Convex relaxation <=0:
        if (std::fabs(resultRelaxationCvVMC.cv(iLin)) > 1e19 || (resultRelaxationCvVMC.cv(iLin) != resultRelaxationCvVMC.cv(iLin))) {
            linEq1[iEq][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
            _rhsEq1[iEq][iLin] = 0;
#endif
            for (unsigned int j = 0; j < _nvar; j++) {
                linEq1[iEq][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
                _matrixEq1[iEq][iLin][j] = 0;
#endif
            }
        }
        else {
            rhs = -resultRelaxationCvVMC.cv(iLin) + _maingoSettings->deltaEq;
            for (unsigned int j = 0; j < _nvar; j++) {
                rhs += resultRelaxationCvVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationCvVMC.cvsub(iLin), resultRelaxationCvVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned int j = 0; j < _nvar; j++) {
                linEq1[iEq][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
                _matrixEq1[iEq][iLin][j] = coefficients[j];
#endif
            }
            linEq1[iEq][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
            _rhsEq1[iEq][iLin] = rhs;
#endif
        }
        // Set up concave >=0 part:
        if (std::fabs(resultRelaxationCcVMC.cc(iLin)) > 1e19 || (resultRelaxationCcVMC.cc(iLin) != resultRelaxationCcVMC.cc(iLin))) {

            linEq2[iEq][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
            _rhsEq2[iEq][iLin] = 0;
#endif
            for (unsigned int j = 0; j < _nvar; j++) {
                linEq2[iEq][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
                _matrixEq2[iEq][iLin][j] = 0;
#endif
            }
        }
        else {
            rhs = resultRelaxationCcVMC.cc(iLin) + _maingoSettings->deltaEq;
            for (unsigned int j = 0; j < _nvar; j++) {
                rhs -= resultRelaxationCcVMC.ccsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationCcVMC.ccsub(iLin), resultRelaxationCcVMC.ccsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned int j = 0; j < _nvar; j++) {
                linEq2[iEq][iLin].setLinearCoef(cplxVars[j], -coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
                _matrixEq2[iEq][iLin][j] = -coefficients[j];
#endif
            }
            linEq2[iEq][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
            _rhsEq2[iEq][iLin] = rhs;
#endif
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only inequality of the linear program
void
LbpCplex::_update_LP_ineqRelaxationOnly(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneqRelaxationOnly)
{

    // Linearize relaxation only inequalities
    if (resultRelaxationVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxation-only inequality constraint " << iIneqRelaxationOnly + 1 << " (of " << _nineqRelaxationOnly << ") (vector) for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinIneqRelaxationOnly[iIneqRelaxationOnly];
    for (unsigned int iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        if (std::fabs(resultRelaxationVMC.cv(iLin)) > 1e19 || (resultRelaxationVMC.cv(iLin) != resultRelaxationVMC.cv(iLin))) {
            linIneqRelaxationOnly[iIneqRelaxationOnly][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
            _rhsIneqRelaxationOnly[iIneqRelaxationOnly][iLin] = 0;
#endif
            for (unsigned int j = 0; j < _nvar; j++) {
                linIneqRelaxationOnly[iIneqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
                _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][j] = 0;
#endif
            }
        }
        else {
            rhs = -resultRelaxationVMC.cv(iLin) + _maingoSettings->deltaIneq;
            for (unsigned int j = 0; j < _nvar; j++) {
                rhs += resultRelaxationVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationVMC.cvsub(iLin), resultRelaxationVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned int j = 0; j < _nvar; j++) {
                linIneqRelaxationOnly[iIneqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
                _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][j] = coefficients[j];
#endif
            }
            linIneqRelaxationOnly[iIneqRelaxationOnly][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
            _rhsIneqRelaxationOnly[iIneqRelaxationOnly][iLin] = rhs;
#endif
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only equality of the linear program
void
LbpCplex::_update_LP_eqRelaxationOnly(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iEqRelaxationOnly)
{

    // Linearize relaxation only equalities
    if (resultRelaxationCvVMC.nsub() == 0 || resultRelaxationCcVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxation-only equality constraint " << iEqRelaxationOnly + 1 << " (of " << _neqRelaxationOnly << ") (vector) for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinEqRelaxationOnly[iEqRelaxationOnly];
    for (unsigned int iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        // Convex relaxation <=0:
        if (std::fabs(resultRelaxationCvVMC.cv(iLin)) > 1e19 || (resultRelaxationCvVMC.cv(iLin) != resultRelaxationCvVMC.cv(iLin))) {
            linEqRelaxationOnly1[iEqRelaxationOnly][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
            _rhsEqRelaxationOnly1[iEqRelaxationOnly][iLin] = 0;
#endif
            for (unsigned int j = 0; j < _nvar; j++) {
                linEqRelaxationOnly1[iEqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
                _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][j] = 0;
#endif
            }
        }
        else {
            rhs = -resultRelaxationCvVMC.cv(iLin) + _maingoSettings->deltaEq;
            for (unsigned int j = 0; j < _nvar; j++) {
                rhs += resultRelaxationCvVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationCvVMC.cvsub(iLin), resultRelaxationCvVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned int j = 0; j < _nvar; j++) {
                linEqRelaxationOnly1[iEqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
                _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][j] = coefficients[j];
#endif
            }
#ifdef LP__OPTIMALITY_CHECK
            _rhsEqRelaxationOnly1[iEqRelaxationOnly][iLin] = rhs;
#endif
            linEqRelaxationOnly1[iEqRelaxationOnly][iLin].setUB(rhs);
        }
        // Set up concave >=0 part:
        if (std::fabs(resultRelaxationCcVMC.cc(iLin)) > 1e19 || (resultRelaxationCcVMC.cc(iLin) != resultRelaxationCcVMC.cc(iLin))) {
            linEqRelaxationOnly2[iEqRelaxationOnly][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
            _rhsEqRelaxationOnly2[iEqRelaxationOnly][iLin] = 0;
#endif
            for (unsigned int j = 0; j < _nvar; j++) {
                linEqRelaxationOnly2[iEqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
                _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][j] = 0;
#endif
            }
        }
        else {
            rhs = resultRelaxationCcVMC.cc(iLin) + _maingoSettings->deltaEq;
            for (unsigned int j = 0; j < _nvar; j++) {
                rhs -= resultRelaxationCcVMC.ccsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationCcVMC.ccsub(iLin), resultRelaxationCcVMC.ccsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned int j = 0; j < _nvar; j++) {
                linEqRelaxationOnly2[iEqRelaxationOnly][iLin].setLinearCoef(cplxVars[j], -coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
                _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][j] = -coefficients[j];
#endif
            }
#ifdef LP__OPTIMALITY_CHECK
            _rhsEqRelaxationOnly2[iEqRelaxationOnly][iLin] = rhs;
#endif
            linEqRelaxationOnly2[iEqRelaxationOnly][iLin].setUB(rhs);
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LbpCplex::_update_LP_ineq_squash(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneqSquash)
{

    // Linearize inequality constraints:
    if (resultRelaxationVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed squash inequality constraint " << iIneqSquash + 1 << " (of " << _nineqSquash << ") (vector) for CPLEX: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    }
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinIneqSquash[iIneqSquash];
    for (unsigned int iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        if (std::fabs(-resultRelaxationVMC.cv(iLin)) > 1e19 || (resultRelaxationVMC.cv(iLin) != resultRelaxationVMC.cv(iLin))) {
            linIneqSquash[iIneqSquash][iLin].setUB(0);
#ifdef LP__OPTIMALITY_CHECK
            _rhsIneqSquash[iIneqSquash][iLin] = 0;
#endif
            for (unsigned int j = 0; j < _nvar; j++) {
                linIneqSquash[iIneqSquash][iLin].setLinearCoef(cplxVars[j], 0);
#ifdef LP__OPTIMALITY_CHECK
                _matrixIneqSquash[iIneqSquash][iLin][j] = 0;
#endif
            }
        }
        else {
            rhs = -resultRelaxationVMC.cv(iLin);    // No tolerance added!
            for (unsigned int j = 0; j < _nvar; j++) {
                rhs += resultRelaxationVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationVMC.cvsub(iLin), resultRelaxationVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned int j = 0; j < _nvar; j++) {
                linIneqSquash[iIneqSquash][iLin].setLinearCoef(cplxVars[j], coefficients[j]);
#ifdef LP__OPTIMALITY_CHECK
                _matrixIneqSquash[iIneqSquash][iLin][j] = coefficients[j];
#endif
            }
            linIneqSquash[iIneqSquash][iLin].setUB(rhs);
#ifdef LP__OPTIMALITY_CHECK
            _rhsIneqSquash[iIneqSquash][iLin] = rhs;
#endif
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// solves the current linear program
LP_RETCODE
LbpCplex::_solve_LP(const babBase::BabNode &currentNode)
{
    PROFILE_FUNCTION()

    try {
        cplex.solve();
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while solving the LP with CPLEX.", e, currentNode);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while solving the LP with CPLEX.", currentNode);
    }
    return LbpCplex::_get_LP_status();  // ensure we don't use any overrides
} // GCOVR_EXCL_STOP


/////////////////////////////////////////////////////////////////////////////////////////////
// function returning the current status of solved linear program
LP_RETCODE
LbpCplex::_get_LP_status()
{

    IloAlgorithm::Status cplexStatus = cplex.getStatus();
    switch (cplexStatus) {
        case IloAlgorithm::Optimal:
            return LP_OPTIMAL;
        case IloAlgorithm::Infeasible:
            return LP_INFEASIBLE;
        case IloAlgorithm::InfeasibleOrUnbounded:
            // Note that our LPs can never be unbounded, since we always give finite variable bounds.
            // Therefore, this return code (which apparently is caused by CPLEX identifying dual infeasibility
            // without further analyzing (for time reasons, apparently) whether this is caused by the primal
            // being infeasible or unbounded) can only be caused by infeasible problems.
            return LP_INFEASIBLE;
        default:
            return LP_UNKNOWN;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function setting the solution point and value of the eta variable to the solution point of the lastly solved LP
void
LbpCplex::_get_solution_point(std::vector<double> &solution, double &etaVal)
{

    IloNumArray vals(cplxEnv);
    try {
        cplex.getValues(vals, cplxVars);
        etaVal = cplex.getValue(eta);
    }
    catch (IloException &e) { // GCOVR_EXCL_START
        // Return empty solution instead
        vals.end();
        std::ostringstream errmsg;
        errmsg << "  Could not extract solution point from CPLEX: " << e;
        throw MAiNGOException(errmsg.str());
    }
    // GCOVR_EXCL_STOP
    // Ok, successfully obtained solution point
    solution.clear();
    for (unsigned int i = 0; i < _nvar; i++) {
        solution.push_back(vals[i]);
    }
    vals.end();
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function returning the objective value of lastly solved LP
double
LbpCplex::_get_objective_value_solver()
{
    return cplex.getObjValue();
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function setting the multipliers
void
LbpCplex::_get_multipliers(std::vector<double> &multipliers)
{

    IloNumArray cplxMultipliers(cplxEnv);
    try {
        multipliers.clear();
        cplex.getReducedCosts(cplxMultipliers, cplxVars);
        multipliers.resize(_nvar);
        for (unsigned int i = 0; i < _nvar; i++) {
            multipliers[i] = cplxMultipliers[i];
        }
        cplxMultipliers.end();
    }
    catch (const std::exception &e) { // GCOVR_EXCL_START
        // This is okay, not providing multipliers
        cplxMultipliers.end();
        throw MAiNGOException("  Could not extract multipliers from CPLEX.", e);
    }
} // GCOVR_EXCL_STOP


/////////////////////////////////////////////////////////////////////////////////////////////
// function deactivating the objective LP rows for feasibility OBBT
void
LbpCplex::_deactivate_objective_function_for_OBBT()
{
    for (unsigned iLinObj = 0; iLinObj < _nLinObj[0]; iLinObj++) {
        for (unsigned iVar = 0; iVar < _nvar; iVar++) {
            linObj[0][iLinObj].setLinearCoef(cplxVars[iVar], 0);
        }
        linObj[0][iLinObj].setLinearCoef(eta, 0);
        linObj[0][iLinObj].setUB(0);
    }
    // Clear CPLEX objective
    cplxObjective.setLinearCoef(eta, 0);
    etaCoeff = 0;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function modifying the LP for feasibility-optimality OBBT
void
LbpCplex::_modify_LP_for_feasopt_OBBT(const double &currentUBD, std::list<unsigned> &toTreatMax, std::list<unsigned> &toTreatMin)
{
    for (unsigned iLinObj = 0; iLinObj < _nLinObj[0]; iLinObj++) {
        linObj[0][iLinObj].setLinearCoef(eta, 0);
        if (std::fabs(linObj[0][iLinObj].getUB() / _objectiveScalingFactors[0][iLinObj] + currentUBD) > 1e19) {
            switch (_maingoSettings->LBP_linPoints) {
                case LINP_KELLEY:
                case LINP_KELLEY_SIMPLEX:
                    if (!_DAGobj->objRowFilled[iLinObj]) {
                        linObj[0][iLinObj].setUB(1e19);
                    }
                    else {
                        toTreatMax.clear();
                        toTreatMin.clear();
                    }
                    break;
                default:
                    toTreatMax.clear();
                    toTreatMin.clear();    // Don't solve OBBT if values are too large, since it may lead to declaring a node infeasible even if it is not
                    break;
            }
        }
        else {
            linObj[0][iLinObj].setUB(linObj[0][iLinObj].getUB() + currentUBD * _objectiveScalingFactors[0][iLinObj]);
        }
#ifdef LP__OPTIMALITY_CHECK
        _rhsObj[0][iLinObj] = linObj[0][iLinObj].getUB();
#endif
    }
    // Clear CPLEX objective
    cplxObjective.setLinearCoef(eta, 0);
    etaCoeff = 0;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for setting the optimization sense of variable iVar in OBBT
void
LbpCplex::_set_optimization_sense_of_variable(const unsigned &iVar, const int &optimizationSense)
{
    cplxObjective.setLinearCoef(cplxVars[iVar], optimizationSense);
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for fixing a variable to its bound, used in probing
void
LbpCplex::_fix_variable(const unsigned &iVar, const bool fixToLowerBound)
{
    if (fixToLowerBound) {
        cplxVars[iVar].setUB(cplxVars[iVar].getLB());
    }
    else {
        cplxVars[iVar].setLB(cplxVars[iVar].getUB());
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for setting the optimization sense of variable iVar in OBBT
void
LbpCplex::_restore_LP_coefficients_after_OBBT()
{
    // Restore proper objective function and disable warm-start
    for (unsigned iVar = 0; iVar < _nvar; iVar++) {
        cplxObjective.setLinearCoef(cplxVars[iVar], 0);
    }
    for (unsigned iLin = 0; iLin < _nLinObj[0]; iLin++) {
        linObj[0][iLin].setLinearCoef(eta, -1);
    }
    etaCoeff = -1;
    cplxObjective.setLinearCoef(eta, 1);
    cplex.setParam(IloCplex::AdvInd, 0);
    cplxObjective.setSense(IloObjective::Minimize);
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for checking whether the current linear program is really infeasible
bool
LbpCplex::_check_if_LP_really_infeasible()
{

    // Turn off pre-processor
    cplex.setParam(IloCplex::PreInd, 0);
    // Try all other 3 algorithms to make sure it is not a simplex fail <-- this happened before when dual was not used as default
    bool reallyInfeasible = true;
    if (reallyInfeasible) {
        // cplex.setParam(IloCplex::RootAlg, IloCplex::Dual); // Solve it with Dual (it is pre-set)  without preprocessing!
        cplex.solve();
        if (cplex.getStatus() == IloAlgorithm::Optimal) {
            reallyInfeasible = false;
        }
    }
    if (reallyInfeasible) {
        cplex.setParam(IloCplex::RootAlg, IloCplex::Primal);
        cplex.solve();
        if (cplex.getStatus() == IloAlgorithm::Optimal) {
            reallyInfeasible = false;
        }
    }
    if (reallyInfeasible) {
        cplex.setParam(IloCplex::RootAlg, IloCplex::Network);
        cplex.solve();
        if (cplex.getStatus() == IloAlgorithm::Optimal) {
            reallyInfeasible = false;
        }
    }
    if (reallyInfeasible) {
        cplex.setParam(IloCplex::RootAlg, IloCplex::Barrier);
        cplex.solve();
        if (cplex.getStatus() == IloAlgorithm::Optimal) {
            reallyInfeasible = false;
        }
    }
    // Reset options
    cplex.setParam(IloCplex::RootAlg, IloCplex::Dual);
    cplex.setParam(IloCplex::PreInd, 1);

    return reallyInfeasible;
}


#ifdef LP__OPTIMALITY_CHECK
/////////////////////////////////////////////////////////////////////////////////////////////
// infeasibility check using Farkas' Lemma
SUBSOLVER_RETCODE
LbpCplex::_check_infeasibility(const babBase::BabNode &currentNode)
{
    // Process dual Farkas certificate point
    // Don't forget the variable bounds!
    bool reallyInfeasible = false;
    try {
        if (cplex.getAlgorithm() != IloCplex::Dual) {
            cplex.setParam(IloCplex::PreInd, 0);                  // Need to turn of pre-solve, since some problems may be too easy and CPLEX won't use the Dual
            cplex.setParam(IloCplex::RootAlg, IloCplex::Dual);    // Since we solve LP only, we only need to set the algorithm for the root
            cplex.solve();
        }
        if (cplex.getStatus() == IloAlgorithm::Infeasible) {    // Yes, it may really change !!!
            cplex.dualFarkas(farkasCons, farkasVals);
            reallyInfeasible = true;
        }
        cplex.setParam(IloCplex::PreInd, 1);    // Turn on pre-solve
    }
    catch (IloException &e) { // GCOVR_EXCL_START
        std::ostringstream errmsg;
        errmsg << "  Error: Variables at dual point of Farkas' certificate of LBP could not be extracted from CPLEX: " << e << std::endl;
        errmsg << "         CPLEX status is: " << cplex.getStatus() << std::endl;
        throw MAiNGOException(errmsg.str(), currentNode);
    }
    if (reallyInfeasible) { // GCOVR_EXCL_STOP
        // Check Farkas' Lemma, for the application please read some literature.
        // In general, we want to find a point such that y^T *A>=0 and b^T *y <0 since then for x>=0 and A*x<=b, 0 > y^T *b >= y^T *A *x >=0 which is a contradiction, so y^T *b <= y^T *A *x has to hold for an x
        // Order of constraints in farkasVals: 1. obj constraint 2. ineq 3. eq convex 4. eq concave 5. rel_only_ineq  6. rel_only_eq convex 7. rel_only_eq concave 8. squash ineq
        std::vector<double> yA;    // y^T *A
        yA.resize(_nvar);
        std::vector<double> z;
        z.resize(_nvar);
        std::vector<double> pl(currentNode.get_lower_bounds()), pu(currentNode.get_upper_bounds());
        unsigned farkasVar = 0;
        for (unsigned int j = 0; j < _nvar; j++) {
            yA[j] = 0;
            // Objective
            for (unsigned int i = 0; i < 1; i++) {
                for (unsigned int k = 0; k < _nLinObj[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixObj[i][k][j];
                    farkasVar++;
                }
            }
            // Inequalities
            for (unsigned int i = 0; i < _nineq; i++) {
                for (unsigned int k = 0; k < _nLinIneq[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixIneq[i][k][j];
                    farkasVar++;
                }
            }
            // Equalities convex
            for (unsigned int i = 0; i < _neq; i++) {
                for (unsigned int k = 0; k < _nLinEq[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixEq1[i][k][j];
                    farkasVar++;
                }
            }
            // Equalities concave
            for (unsigned int i = 0; i < _neq; i++) {
                for (unsigned int k = 0; k < _nLinEq[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixEq2[i][k][j];
                    farkasVar++;
                }
            }
            // Relaxation only inequalities
            for (unsigned int i = 0; i < _nineqRelaxationOnly; i++) {
                for (unsigned int k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixIneqRelaxationOnly[i][k][j];
                    farkasVar++;
                }
            }
            // Relaxation only equalities convex
            for (unsigned int i = 0; i < _neqRelaxationOnly; i++) {
                for (unsigned int k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixEqRelaxationOnly1[i][k][j];
                    farkasVar++;
                }
            }
            // Relaxation only equalities concave
            for (unsigned int i = 0; i < _neqRelaxationOnly; i++) {
                for (unsigned int k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixEqRelaxationOnly2[i][k][j];
                    farkasVar++;
                }
            }
            // Squash inequalities
            for (unsigned int i = 0; i < _nineqSquash; i++) {
                for (unsigned int k = 0; k < _nLinIneqSquash[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixIneqSquash[i][k][j];
                    farkasVar++;
                }
            }
            if (yA[j] > 0) {
                z[j] = pu[j];
            }
            else {
                z[j] = pl[j];
            }
            farkasVar = 0;
        }
        farkasVar   = 0;
        double res1 = 0;
        // Objective
        for (unsigned int i = 0; i < 1; i++) {
            for (unsigned int k = 0; k < _nLinObj[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsObj[i][k];
                farkasVar++;
            }
        }
        // Inequalities
        for (unsigned int i = 0; i < _nineq; i++) {
            for (unsigned int k = 0; k < _nLinIneq[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsIneq[i][k];
                farkasVar++;
            }
        }
        // Equalities convex
        for (unsigned int i = 0; i < _neq; i++) {
            for (unsigned int k = 0; k < _nLinEq[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsEq1[i][k];
                farkasVar++;
            }
        }
        // Equalities concave
        for (unsigned int i = 0; i < _neq; i++) {
            for (unsigned int k = 0; k < _nLinEq[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsEq2[i][k];
                farkasVar++;
            }
        }
        // Relaxation only inequalities
        for (unsigned int i = 0; i < _nineqRelaxationOnly; i++) {
            for (unsigned int k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsIneqRelaxationOnly[i][k];
                farkasVar++;
            }
        }
        // Relaxation only equalities convex
        for (unsigned int i = 0; i < _neqRelaxationOnly; i++) {
            for (unsigned int k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsEqRelaxationOnly1[i][k];
                farkasVar++;
            }
        }
        // Relaxation only equalities concave
        for (unsigned int i = 0; i < _neqRelaxationOnly; i++) {
            for (unsigned int k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsEqRelaxationOnly2[i][k];
                farkasVar++;
            }
        }
        // Squash inequalities
        for (unsigned int i = 0; i < _nineqSquash; i++) {
            for (unsigned int k = 0; k < _nLinIneqSquash[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsIneqSquash[i][k];
                farkasVar++;
            }
        }
        double res2 = 0;
        for (unsigned int j = 0; j < _nvar; j++) {
            res2 += yA[j] * z[j];
        }
        if (res1 - res2 <= 0. && !mc::isequal(res1, res2, _computationTol * 1e1, _computationTol * 1e1)) {
#ifdef LP__WRITE_CHECK_FILES
            _write_LP_to_file("cplex_infeas_check");
#endif
            std::ostringstream outstr;
            outstr << "  Warning: Infeasibility condition violated" << std::endl
                   << "           It holds that (" << std::setprecision(16) << res1 << " =) y^T * b - y^T *A *x (=  " << std::setprecision(16) << res2
                   << ") <= 0. For further information, see Farkas' Lemma." << std::endl;
            _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
            return SUBSOLVER_FEASIBLE;
        }
        return SUBSOLVER_INFEASIBLE;
    }
    else {
        return SUBSOLVER_FEASIBLE;
    }    // end of reallyInfeasible
}


void
LbpCplex::_print_check_feasibility(const std::shared_ptr<Logger> logger, const VERB verbosity, const std::vector<double> &solution, const std::vector<std::vector<double>> rhs, const std::string name, const double value, const unsigned i, unsigned k, const unsigned nvar)
{
    std::ostringstream outstr;
    outstr << "  Warning: CPLEX returned FEASIBLE although the point is an infeasible one w.r.t. inequality " << i << "!" << std::endl;

    if (verbosity > VERB_NORMAL) {
        outstr << std::setprecision(16) << "           value: " << value << " _" << name << "[" << i << "][" << k << "]: " << rhs[i][k] << std::endl;
        outstr << "           LBP solution point: " << std::endl;
        for (unsigned i = 0; i < nvar; i++) {
            outstr << "            x(" << i << "): " << solution[i] << std::endl;
        }
    }

    outstr << "           Continuing with parent LBD." << std::endl;
    logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
}


/////////////////////////////////////////////////////////////////////////////////////////////
// feasibility check
SUBSOLVER_RETCODE
LbpCplex::_check_feasibility(const std::vector<double> &solution)
{

    double value = 0.;
    // Check inequalities
    for (unsigned int i = 0; i < _nineq; i++) {
        for (unsigned int k = 0; k < _nLinIneq[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                value += _matrixIneq[i][k][j] * solution[j];
            }
            if (value - _rhsIneq[i][k] > _maingoSettings->deltaIneq) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsIneq, "rhsIneq", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
        }
    }
    // Check equalities
    for (unsigned int i = 0; i < _neq; i++) {
        for (unsigned int k = 0; k < _nLinEq[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                value += _matrixEq1[i][k][j] * solution[j];
            }
            if (value - _rhsEq1[i][k] > _maingoSettings->deltaEq) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsEq1, "rhsEq1", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
            for (unsigned int j = 0; j < _nvar; j++) {
                value += _matrixEq2[i][k][j] * solution[j];
            }
            if (value - _rhsEq2[i][k] > _maingoSettings->deltaEq) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsEq2, "rhsEq2", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
        }
    }
    // Check relaxation only inequalities
    for (unsigned int i = 0; i < _nineqRelaxationOnly; i++) {
        for (unsigned int k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                value += _matrixIneqRelaxationOnly[i][k][j] * solution[j];
            }
            if (value - _rhsIneqRelaxationOnly[i][k] > _maingoSettings->deltaIneq) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsIneqRelaxationOnly, "rhsIneqRelaxationOnly", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
        }
    }
    // Check relaxation only equalities
    for (unsigned int i = 0; i < _neqRelaxationOnly; i++) {
        for (unsigned int k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                value += _matrixEqRelaxationOnly1[i][k][j] * solution[j];
            }
            if (value - _rhsEqRelaxationOnly1[i][k] > _maingoSettings->deltaEq) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsEqRelaxationOnly1, "rhsEqRelaxationOnly1", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
            for (unsigned int j = 0; j < _nvar; j++) {
                value += _matrixEqRelaxationOnly2[i][k][j] * solution[j];
            }
            if (value - _rhsEqRelaxationOnly2[i][k] > _maingoSettings->deltaEq) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsEqRelaxationOnly2, "rhsEqRelaxationOnly2", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
        }
    }
    // Check squash inequalities
    for (unsigned int i = 0; i < _nineqSquash; i++) {
        for (unsigned int k = 0; k < _nLinIneqSquash[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                value += _matrixIneqSquash[i][k][j] * solution[j];
            }
            if (value - _rhsIneqSquash[i][k] > 1e-9) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsIneqSquash, "rhsIneqSquash", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
        }
    }

    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// optimality check
SUBSOLVER_RETCODE
LbpCplex::_check_optimality(const babBase::BabNode &currentNode, const double newLBD, const std::vector<double> &solution, const double etaVal, const std::vector<double> &multipliers)
{

    // Process solution: dual solution point
    try {
        cplex.getDuals(dualValsObj[0], linObj[0]);
        for (unsigned i = 0; i < _nineq; i++) {
            cplex.getDuals(dualValsIneq[i], linIneq[i]);
        }
        for (unsigned i = 0; i < _neq; i++) {
            cplex.getDuals(dualValsEq1[i], linEq1[i]);
        }
        for (unsigned i = 0; i < _neq; i++) {
            cplex.getDuals(dualValsEq2[i], linEq2[i]);
        }
        for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
            cplex.getDuals(dualValsIneqRelaxationOnly[i], linIneqRelaxationOnly[i]);
        }
        for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
            cplex.getDuals(dualValsEqRelaxationOnly1[i], linEqRelaxationOnly1[i]);
        }
        for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
            cplex.getDuals(dualValsEqRelaxationOnly2[i], linEqRelaxationOnly2[i]);
        }
        for (unsigned i = 0; i < _nineqSquash; i++) {
            cplex.getDuals(dualValsIneqSquash[i], linIneqSquash[i]);
        }
    }
    catch (IloException &e) { // GCOVR_EXCL_START
        std::ostringstream errmsg;
        errmsg << "  Error in optimality check:: Variables at dual solution of LBP could not be extracted from CPLEX:" << e << std::endl;
        throw MAiNGOException(errmsg.str(), currentNode);
    }
    // GCOVR_EXCL_STOP
    // Ok, successfully obtained dual solution point
    // If multiplier[i] of variable x_i is >0 then you add multiplier[i]*lower bound, else multiplier[i]*upper bound
    std::vector<double> primal;
    primal.resize(_nLinObj[0]);
    double dual = 0;
    for (unsigned int k = 0; k < _nLinObj[0]; k++) {
        // Primal solution value
        primal[k] = -_rhsObj[0][k];
        for (unsigned int i = 0; i < _nvar; i++) {
            primal[k] += solution[i] * _matrixObj[0][k][i];
        }
        primal[k] = primal[k] / _objectiveScalingFactors[0][k];
        // Dual value of objective linearizations
        dual += dualValsObj[0][k] * _rhsObj[0][k];
    }
    // Dual value of inequality linearizations
    for (unsigned i = 0; i < _nineq; i++) {
        for (unsigned k = 0; k < _nLinIneq[i]; k++) {
            dual += dualValsIneq[i][k] * _rhsIneq[i][k];
        }
    }
    // Dual value of equality linearizations
    for (unsigned i = 0; i < _neq; i++) {
        for (unsigned k = 0; k < _nLinEq[i]; k++) {
            dual += dualValsEq1[i][k] * _rhsEq1[i][k];
            dual += dualValsEq2[i][k] * _rhsEq2[i][k];
        }
    }
    // Dual value of relaxation only inequality linearizations
    for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
        for (unsigned k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
            dual += dualValsIneqRelaxationOnly[i][k] * _rhsIneqRelaxationOnly[i][k];
        }
    }
    // Dual value of relaxation only equality linearizations
    for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
        for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
            dual += dualValsEqRelaxationOnly1[i][k] * _rhsEqRelaxationOnly1[i][k];
            dual += dualValsEqRelaxationOnly2[i][k] * _rhsEqRelaxationOnly2[i][k];
        }
    }
    // Dual value of inequality linearizations
    for (unsigned i = 0; i < _nineqSquash; i++) {
        for (unsigned k = 0; k < _nLinIneqSquash[i]; k++) {
            dual += dualValsIneqSquash[i][k] * _rhsIneqSquash[i][k];
        }
    }
    std::vector<double> pl(currentNode.get_lower_bounds()), pu(currentNode.get_upper_bounds());
    for (unsigned int i = 0; i < _nvar; i++) {
        if (multipliers[i] > 0.) {
            dual += multipliers[i] * pl[i];
        }
        else {
            dual += multipliers[i] * pu[i];
        }
    }
    // Check if our dual and CPLEX solution are the same
    if (!mc::isequal(dual, newLBD, _computationTol * 1e1, _computationTol * 1e1)) {
        std::ostringstream outstr;
        outstr << "  Warning: Calculated dual: " << dual << " does not equal the solution value returned by CPLEX: " << newLBD << "." << std::endl;
        outstr << "           Not using this bound." << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
#ifdef LP__WRITE_CHECK_FILES
        _write_LP_to_file("cplex_optim_check");
#endif
        return SUBSOLVER_INFEASIBLE;
    }
    bool checkOptimality = false;
    // At least one of the linearized objectives has to be equal to the dual objective value
    for (unsigned int k = 0; k < _nLinObj[0]; k++) {
        if ((std::fabs(primal[k] - newLBD) <= 1e-9) || mc::isequal(primal[k], newLBD, _computationTol * 1e1, _computationTol * 1e1)) {
            checkOptimality = true;
        }
    }
    // If none of the linearized objective inequalities is fulfilled, something went wrong
    if (!checkOptimality) {
        std::ostringstream outstr;
        if (_maingoSettings->LBP_verbosity > VERB_NORMAL) {
            for (unsigned int k = 0; k < _nLinObj[0]; k++) {
                outstr << "  Optimality condition violated" << std::endl
                       << "  Primal solution value [" << k << "]: " << primal[k] << " <> Dual solution value: " << dual << std::endl;
                outstr << "  | primal[" << k << "] - dual | = " << std::fabs(primal[k] - newLBD) << " > " << 1e-9 << std::endl;
                outstr << "  Terminating. " << std::endl;
            }
        }
        outstr << "  CPLEX failed in returning a correct objective value! Falling back to interval arithmetic and proceeding." << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
#ifdef LP__WRITE_CHECK_FILES
        _write_LP_to_file("cplex_optim_check");
#endif
        return SUBSOLVER_INFEASIBLE;
    }
    return SUBSOLVER_FEASIBLE;
}
#endif


#ifdef LP__WRITE_CHECK_FILES
/////////////////////////////////////////////////////////////////////////////////////////////
// write current LP to file
void
LbpCplex::_write_LP_to_file(const std::string &fileName)
{

    std::string str;
    if (fileName.empty()) {
        str = "MAiNGO_LP_WRITE_CHECK_FILES.lp";
    }
    else {
        str = fileName + ".lp";
    }
    try {
        cplex.exportModel(str.c_str());
    }
    catch (IloException &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while exporting model from CPLEX.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while exporting model from CPLEX.");
    }
} // GCOVR_EXCL_STOP
#endif

/////////////////////////////////////////////////////////////////////////
// function for termination CPLEX
void
LbpCplex::_terminate_cplex()
{

    cplex.end();
    eta.end();
    cplxVars.endElements();
    // We can't use _constraintProperties here, since it may have been deleted already!
    for (unsigned i = 0; i < linObj.size(); i++) {
        linObj[i].endElements();
    }
    for (unsigned i = 0; i < linIneq.size(); i++) {
        linIneq[i].endElements();
    }
    for (unsigned i = 0; i < linEq1.size(); i++) {
        linEq1[i].endElements();
    }
    for (unsigned i = 0; i < linEq2.size(); i++) {
        linEq2[i].endElements();
    }
    for (unsigned i = 0; i < linIneqRelaxationOnly.size(); i++) {
        linIneqRelaxationOnly[i].endElements();
    }
    for (unsigned i = 0; i < linEqRelaxationOnly1.size(); i++) {
        linEqRelaxationOnly1[i].endElements();
    }
    for (unsigned i = 0; i < linEqRelaxationOnly2.size(); i++) {
        linEqRelaxationOnly2[i].endElements();
    }
    for (unsigned i = 0; i < linIneqSquash.size(); i++) {
        linIneqSquash[i].endElements();
    }
    cplxVars.end();
    for (unsigned i = 0; i < linObj.size(); i++) {
        linObj[i].end();
    }
    for (unsigned i = 0; i < linIneq.size(); i++) {
        linIneq[i].end();
    }
    for (unsigned i = 0; i < linEq1.size(); i++) {
        linEq1[i].end();
    }
    for (unsigned i = 0; i < linEq2.size(); i++) {
        linEq2[i].end();
    }
    for (unsigned i = 0; i < linIneqRelaxationOnly.size(); i++) {
        linIneqRelaxationOnly[i].end();
    }
    for (unsigned i = 0; i < linEqRelaxationOnly1.size(); i++) {
        linEqRelaxationOnly1[i].end();
    }
    for (unsigned i = 0; i < linEqRelaxationOnly2.size(); i++) {
        linEqRelaxationOnly2[i].end();
    }
    for (unsigned i = 0; i < linIneqSquash.size(); i++) {
        linIneqSquash[i].end();
    }
#ifdef LP__OPTIMALITY_CHECK
    farkasCons.end();
    farkasVals.end();
    for (unsigned i = 0; i < dualValsObj.size(); i++) {
        dualValsObj[i].end();
    }
    for (unsigned i = 0; i < _nineq; i++) {
        dualValsIneq[i].end();
    }
    for (unsigned i = 0; i < _neq; i++) {
        dualValsEq1[i].end();
    }
    for (unsigned i = 0; i < _neq; i++) {
        dualValsEq2[i].end();
    }
    for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
        dualValsIneqRelaxationOnly[i].end();
    }
    for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
        dualValsEqRelaxationOnly1[i].end();
    }
    for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
        dualValsEqRelaxationOnly2[i].end();
    }
    for (unsigned i = 0; i < _nineqSquash; i++) {
        dualValsIneqSquash[i].end();
    }
#endif
    cplxModel.end();
    cplxObjective.end();

    cplxEnv.end();
}

#endif
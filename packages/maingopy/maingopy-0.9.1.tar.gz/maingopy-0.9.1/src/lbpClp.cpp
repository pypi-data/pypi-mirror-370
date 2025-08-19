
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

#include "lbpClp.h"
#include "MAiNGOException.h"

#include <algorithm>
#include <limits>

using namespace maingo;
using namespace lbp;


/////////////////////////////////////////////////////////////////////////////////////////////
// constructor for the lower bounding solver
LbpClp::LbpClp(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
                         const std::vector<bool>& variableIsLinear, const unsigned nineqIn, const unsigned neqIn, const unsigned nineqRelaxationOnlyIn, const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn,
                         std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn):
    LowerBoundingSolver(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn, nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn)
{
    try {

        // Initialize CLP matrix (also computes dimensions)
        _initialize_matrix();

        // Initialize lower and upper bounds on variables (here, need to include the dummy objective variable eta)
        _lowerVarBounds.resize(_nvar + 1);
        _upperVarBounds.resize(_nvar + 1);
        // Actual problem variables
        for (unsigned i = 0; i < _nvar; i++) {
            _lowerVarBounds[i] = variables[i].get_lower_bound();
            _upperVarBounds[i] = variables[i].get_upper_bound();
        }
        // Dummy objective variable: _eta
        _lowerVarBounds[_nvar] = -std::numeric_limits<double>::max();
        _upperVarBounds[_nvar] = std::numeric_limits<double>::max();

        // Lower and upper row bounds
        _lowerRowBounds = new double[_numrows];
        _upperRowBounds = new double[_numrows];
        std::fill_n(_lowerRowBounds, _numrows, -std::numeric_limits<double>::max());

        // Coefficients in objective function
        _objective = new double[_numcolumns];
        // Dummy objective function: minimize _eta
        for (unsigned i = 0; i < _nvar; i++) {
            _objective[i] = 0;
        }
        _objective[_nvar] = 1;
        _etaCoeff         = -1;


        // CLP settings
        _clp.scaling(0);
        _clp.setPrimalTolerance(1e-9);
        _clp.setDualTolerance(1e-9);
        _clp.setMaximumIterations(100000);
        _clp.setRandomSeed(42);    // Make the behavior of CLP deterministic
        // Suppress output - unfortunately we cannot redirect the output of CLP to our log file right now...
        if ((_maingoSettings->LBP_verbosity <= VERB_NORMAL) || (_maingoSettings->loggingDestination == LOGGING_NONE) || (_maingoSettings->loggingDestination == LOGGING_FILE)) {
            _clp.messageHandler()->setLogLevel(0);
        }

#ifdef LP__OPTIMALITY_CHECK
        _dualValsObj.resize(1);
        _dualValsIneq.resize(_nineq);
        _dualValsEq1.resize(_neq);
        _dualValsEq2.resize(_neq);
        _dualValsIneqRelaxationOnly.resize(_nineqRelaxationOnly);
        _dualValsEqRelaxationOnly1.resize(_neqRelaxationOnly);
        _dualValsEqRelaxationOnly2.resize(_neqRelaxationOnly);
        _dualValsIneqSquash.resize(_nineqSquash);

        for (size_t i = 0; i < _constraintProperties->size(); i++) {
            unsigned index = (*_constraintProperties)[i].indexTypeNonconstant;
            switch ((*_constraintProperties)[i].type) {
                case OBJ:
                    _dualValsObj[index].resize(_nLinObj[index]);
                    break;
                case INEQ:
                    _dualValsIneq[index].resize(_nLinIneq[index]);
                    break;
                case EQ:
                    _dualValsEq1[index].resize(_nLinEq[index]);
                    _dualValsEq2[index].resize(_nLinEq[index]);
                    break;
                case INEQ_REL_ONLY:
                    _dualValsIneqRelaxationOnly[index].resize(_nLinIneqRelaxationOnly[index]);
                    break;
                case EQ_REL_ONLY:
                case AUX_EQ_REL_ONLY:
                    _dualValsEqRelaxationOnly1[index].resize(_nLinEqRelaxationOnly[index]);
                    _dualValsEqRelaxationOnly2[index].resize(_nLinEqRelaxationOnly[index]);
                    break;
                case INEQ_SQUASH:
                    _dualValsIneqSquash[index].resize(_nLinIneqSquash[index]);
                    break;
                default:
                    break;
            }
        }
#endif
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error initializing CLP during initialization of LowerBoundingSolver.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error initializing CLP during initialization of LowerBoundingSolver.");
    }
} // GCOVR_EXCL_STOP


////////////////////////////////////////////////////////////////////////////////////////////
// destructor for CLP
LbpClp::~LbpClp()
{

    _terminate_Clp();
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for matrix initialization
void
LbpClp::_initialize_matrix()
{

    // Compute dimensions first
    _numcolumns = _nvar + 1;
    _numrows    = 0;
    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        unsigned index = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].type) {
            case OBJ:
                _numrows = _numrows + _nLinObj[index];
                break;
            case INEQ:
                _numrows = _numrows + _nLinIneq[index];
                break;
            case EQ:
                _numrows = _numrows + (2 * _nLinEq[index]);
                break;
            case INEQ_REL_ONLY:
                _numrows = _numrows + _nLinIneqRelaxationOnly[index];
                break;
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                _numrows = _numrows + (2 * _nLinEqRelaxationOnly[index]);
                break;
            case INEQ_SQUASH:
                _numrows = _numrows + _nLinIneqSquash[index];
                break;
            default:
                break;
        }
    }

    // Arrays needed to initialize CLP matrix object (these are deleted by CLP!)
    double *matrixEntries   = new double[_numrows * _numcolumns]();
    int *columnStartIndices = new int[_numcolumns + 1]();
    int *rowIndex           = new int[_numrows * _numcolumns]();
    int *lengths            = NULL;


    // Sparse matrix - column major - format
    unsigned count = 0;
    for (unsigned i = 0; i < _numcolumns; i++)
        for (unsigned j = 0; j < _numrows; j++) {
            rowIndex[count] = j;
            count++;
        }

    // Sparse matrix - column major - format
    for (unsigned i = 0; i <= _numcolumns; i++) {
        columnStartIndices[i] = i * _numrows;
    }

    // CLP matrix object
    _matrix.assignMatrix(true, _numrows, _numcolumns,
                         _numcolumns * _numrows, matrixEntries, rowIndex, columnStartIndices, lengths);
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function called by the B&B in preprocessing in order to check the need for specific options, currently for subgradient intervals & CPLEX no large values
void
LbpClp::activate_more_scaling()
{

    // Enable aggressive scaling of LP matrix. Since we experienced numerical problems within CPLEX if its scaling is enabled, we only turn scaling on if it was heuristically called from the B&B
    _clp.scaling(1);
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for setting the bounds of variables
void
LbpClp::_set_variable_bounds(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    for (unsigned i = 0; i < _nvar; i++) {
        _lowerVarBounds[i] = lowerVarBounds[i];
        _upperVarBounds[i] = upperVarBounds[i];
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an objective of the linear program
void
LbpClp::_update_LP_obj(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iObj)
{

    // Linearize objective function:
    if (resultRelaxation.nsub() == 0) {
        throw MAiNGOException("  Error in evaluation of the relaxed objective function for CLP: objective function does not depend on variables."); // GCOVR_EXCL_LINE
    }
    double rhs = 0;
    // If the numbers are too large, we simply set the whole row to 0
    // NOTE: second check is for NaN
    if (std::fabs(-resultRelaxation.cv()) > 1e19 || (resultRelaxation.cv() != resultRelaxation.cv())) {
        _rhsObj[iObj][iLin]                  = 1e19;
        _objectiveScalingFactors[iObj][iLin] = 1.;
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixObj[iObj][iLin][j] = 0;
        }
        _matrixObj[iObj][iLin][_nvar] = 0;
    }
    else {
        rhs = -resultRelaxation.cv();
        for (unsigned j = 0; j < _nvar; j++) {
            rhs += resultRelaxation.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxation.cvsub(), resultRelaxation.cvsub() + _nvar);    // Iterator range constructor
        coefficients.push_back(_etaCoeff);
        _objectiveScalingFactors[iObj][iLin] = _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);    // This function does the scaling, but for the objective we also need the factor later for OBBT
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixObj[iObj][iLin][j] = coefficients[j];
        }
        _matrixObj[iObj][iLin][_nvar] = coefficients[_nvar];
        _rhsObj[iObj][iLin]           = rhs;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LbpClp::_update_LP_ineq(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneq)
{

    // Linearize inequality constraints:
    if (resultRelaxation.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed inequality constraint " << iIneq + 1 << " (of " << _nineq << ") for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    double rhs = 0; // GCOVR_EXCL_STOP
    if (std::fabs(-resultRelaxation.cv()) > 1e19 || (resultRelaxation.cv() != resultRelaxation.cv())) {
        _rhsIneq[iIneq][iLin] = 0;

        for (unsigned j = 0; j < _nvar; j++) {
            _matrixIneq[iIneq][iLin][j] = 0;
        }
        _matrixIneq[iIneq][iLin][_nvar] = 0;
    }
    else {
        rhs = -resultRelaxation.cv() + _maingoSettings->deltaIneq;
        for (unsigned j = 0; j < _nvar; j++) {
            rhs += resultRelaxation.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxation.cvsub(), resultRelaxation.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixIneq[iIneq][iLin][j] = coefficients[j];
        }
        _matrixIneq[iIneq][iLin][_nvar] = 0;
        _rhsIneq[iIneq][iLin]           = rhs;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LbpClp::_update_LP_eq(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEq)
{

    if (resultRelaxationCv.nsub() == 0 || resultRelaxationCc.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed equality constraint " << iEq + 1 << " (of " << _neq << ") for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    double rhs = 0; // GCOVR_EXCL_STOP
    // Convex relaxation <=0:
    if (std::fabs(resultRelaxationCv.cv()) > 1e19 || (resultRelaxationCv.cv() != resultRelaxationCv.cv())) {
        _rhsEq1[iEq][iLin] = 0;

        for (unsigned j = 0; j < _nvar; j++) {
            _matrixEq1[iEq][iLin][j] = 0;
        }
        _matrixEq1[iEq][iLin][_nvar] = 0;
    }
    else {
        rhs = -resultRelaxationCv.cv() + _maingoSettings->deltaEq;
        for (unsigned j = 0; j < _nvar; j++) {
            rhs += resultRelaxationCv.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxationCv.cvsub(), resultRelaxationCv.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixEq1[iEq][iLin][j] = coefficients[j];
        }
        _matrixEq1[iEq][iLin][_nvar] = 0;
        _rhsEq1[iEq][iLin]           = rhs;
    }
    // Set up concave >=0 part:
    if (std::fabs(resultRelaxationCc.cc()) > 1e19 || (resultRelaxationCc.cc() != resultRelaxationCc.cc())) {

        _rhsEq2[iEq][iLin] = 0;

        for (unsigned j = 0; j < _nvar; j++) {
            _matrixEq2[iEq][iLin][j] = 0;
        }
        _matrixEq2[iEq][iLin][_nvar] = 0;
    }
    else {
        rhs = resultRelaxationCc.cc() + _maingoSettings->deltaEq;
        for (unsigned j = 0; j < _nvar; j++) {
            rhs -= resultRelaxationCc.ccsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxationCc.ccsub(), resultRelaxationCc.ccsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixEq2[iEq][iLin][j] = -coefficients[j];
        }
        _matrixEq2[iEq][iLin][_nvar] = 0;
        _rhsEq2[iEq][iLin]           = rhs;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only inequality of the linear program
void
LbpClp::_update_LP_ineqRelaxationOnly(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqRelaxationOnly)
{

    if (resultRelaxation.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxation-only inequality constraint " << iIneqRelaxationOnly + 1 << " (of " << _nineqRelaxationOnly << ") for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    double rhs = 0; // GCOVR_EXCL_STOP
    if (std::fabs(resultRelaxation.cv()) > 1e19 || (resultRelaxation.cv() != resultRelaxation.cv())) {
        _rhsIneqRelaxationOnly[iIneqRelaxationOnly][iLin] = 0;

        for (unsigned j = 0; j < _nvar; j++) {
            _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][j] = 0;
        }
        _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][_nvar] = 0;
    }

    else {
        rhs = -resultRelaxation.cv() + _maingoSettings->deltaIneq;
        for (unsigned j = 0; j < _nvar; j++) {
            rhs += resultRelaxation.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxation.cvsub(), resultRelaxation.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][j] = coefficients[j];
        }
        _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][_nvar] = 0;
        _rhsIneqRelaxationOnly[iIneqRelaxationOnly][iLin]           = rhs;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LbpClp::_update_LP_eqRelaxationOnly(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEqRelaxationOnly)
{

    // Linearize relaxation only equalities
    if (resultRelaxationCv.nsub() == 0 || resultRelaxationCc.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxation-only equality constraint " << iEqRelaxationOnly + 1 << " (of " << _neqRelaxationOnly << ") for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    double rhs = 0; // GCOVR_EXCL_STOP
    // Convex relaxation <=0:
    if (std::fabs(resultRelaxationCv.cv()) > 1e19 || (resultRelaxationCv.cv() != resultRelaxationCv.cv())) {
        _rhsEqRelaxationOnly1[iEqRelaxationOnly][iLin] = 0;

        for (unsigned j = 0; j < _nvar; j++) {
            _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][j] = 0;
        }
        _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][_nvar] = 0;
    }

    else {
        rhs = -resultRelaxationCv.cv() + _maingoSettings->deltaEq;
        for (unsigned j = 0; j < _nvar; j++) {
            rhs += resultRelaxationCv.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxationCv.cvsub(), resultRelaxationCv.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][j] = coefficients[j];
        }

        _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][_nvar] = 0;
        _rhsEqRelaxationOnly1[iEqRelaxationOnly][iLin]           = rhs;
    }
    // Set up concave >=0 part:
    if (std::fabs(resultRelaxationCc.cc()) > 1e19 || (resultRelaxationCc.cc() != resultRelaxationCc.cc())) {
        _rhsEqRelaxationOnly2[iEqRelaxationOnly][iLin] = 0;

        for (unsigned j = 0; j < _nvar; j++) {
            _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][j] = 0;
        }
        _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][_nvar] = 0;
    }

    else {
        rhs = resultRelaxationCc.cc() + _maingoSettings->deltaEq;
        for (unsigned j = 0; j < _nvar; j++) {
            rhs -= resultRelaxationCc.ccsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxationCc.ccsub(), resultRelaxationCc.ccsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][j] = -coefficients[j];
        }

        _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][_nvar] = 0;
        _rhsEqRelaxationOnly2[iEqRelaxationOnly][iLin]           = rhs;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a squash inequality of the linear program
void
LbpClp::_update_LP_ineq_squash(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqSquash)
{

    // Linearize inequality constraints:
    if (resultRelaxation.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed squash inequality constraint " << iIneqSquash + 1 << " (of " << _nineqSquash << ") for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    double rhs = 0; // GCOVR_EXCL_STOP
    if (std::fabs(-resultRelaxation.cv()) > 1e19 || (resultRelaxation.cv() != resultRelaxation.cv())) {
        _rhsIneqSquash[iIneqSquash][iLin] = 0;

        for (unsigned j = 0; j < _nvar; j++) {
            _matrixIneqSquash[iIneqSquash][iLin][j] = 0;
        }
        _matrixIneqSquash[iIneqSquash][iLin][_nvar] = 0;
    }
    else {
        rhs = -resultRelaxation.cv();    // No tolerance added!
        for (unsigned j = 0; j < _nvar; j++) {
            rhs += resultRelaxation.cvsub(j) * linearizationPoint[j];
        }
        std::vector<double> coefficients(resultRelaxation.cvsub(), resultRelaxation.cvsub() + _nvar);
        _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
        for (unsigned j = 0; j < _nvar; j++) {
            _matrixIneqSquash[iIneqSquash][iLin][j] = coefficients[j];
        }
        _matrixIneqSquash[iIneqSquash][iLin][_nvar] = 0;
        _rhsIneqSquash[iIneqSquash][iLin]           = rhs;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an objective of the linear program
void
LbpClp::_update_LP_obj(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iObj)
{

    // Linearize objective function:
    if (resultRelaxationVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of the relaxed objective function (vector) for CLP: objective function does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinObj[0];
    for (unsigned iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        // If the numbers are too large, we simply set the whole row to 0
        // NOTE: second check is for NaN
        if (std::fabs(-resultRelaxationVMC.cv(iLin)) > 1e19 || (resultRelaxationVMC.cv(iLin) != resultRelaxationVMC.cv(iLin))) {

            _rhsObj[iObj][iLin]                  = 1e19;
            _objectiveScalingFactors[iObj][iLin] = 1.;
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixObj[iObj][iLin][j] = 0;
            }
            _matrixObj[iObj][iLin][_nvar] = 0;
        }
        else {
            rhs = -resultRelaxationVMC.cv(iLin);
            for (unsigned j = 0; j < _nvar; j++) {
                rhs += resultRelaxationVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationVMC.cvsub(iLin), resultRelaxationVMC.cvsub(iLin) + _nvar);    // Iterator range constructor
            coefficients.push_back(_etaCoeff);
            _objectiveScalingFactors[iObj][iLin] = _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);    // This function does the scaling, but for the objective we also need the factor later for OBBT
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixObj[iObj][iLin][j] = coefficients[j];
            }
            _matrixObj[iObj][iLin][_nvar] = coefficients[_nvar];
            _rhsObj[iObj][iLin]           = rhs;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LbpClp::_update_LP_ineq(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneq)
{

    // Linearize inequality constraints:
    if (resultRelaxationVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed inequality constraint " << iIneq + 1 << " (of " << _nineq << ") (vector) for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinIneq[iIneq];
    for (unsigned iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        if (std::fabs(-resultRelaxationVMC.cv(iLin)) > 1e19 || (resultRelaxationVMC.cv(iLin) != resultRelaxationVMC.cv(iLin))) {
            _rhsIneq[iIneq][iLin] = 0;

            for (unsigned j = 0; j < _nvar; j++) {
                _matrixIneq[iIneq][iLin][j] = 0;
            }
            _matrixIneq[iIneq][iLin][_nvar] = 0;
        }
        else {
            rhs = -resultRelaxationVMC.cv(iLin) + _maingoSettings->deltaIneq;
            for (unsigned j = 0; j < _nvar; j++) {
                rhs += resultRelaxationVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationVMC.cvsub(iLin), resultRelaxationVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixIneq[iIneq][iLin][j] = coefficients[j];
            }
            _matrixIneq[iIneq][iLin][_nvar] = 0;
            _rhsIneq[iIneq][iLin]           = rhs;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LbpClp::_update_LP_eq(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iEq)
{

    // Linearize equality Constraints:
    if (resultRelaxationCvVMC.nsub() == 0 || resultRelaxationCcVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed equality constraint " << iEq + 1 << " (of " << _neq << ") (vector) for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinEq[iEq];
    for (unsigned iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        // Convex relaxation <=0:
        if (std::fabs(resultRelaxationCvVMC.cv(iLin)) > 1e19 || (resultRelaxationCvVMC.cv(iLin) != resultRelaxationCvVMC.cv(iLin))) {
            _rhsEq1[iEq][iLin] = 0;

            for (unsigned j = 0; j < _nvar; j++) {
                _matrixEq1[iEq][iLin][j] = 0;
            }
            _matrixEq1[iEq][iLin][_nvar] = 0;
        }
        else {
            rhs = -resultRelaxationCvVMC.cv(iLin) + _maingoSettings->deltaEq;
            for (unsigned j = 0; j < _nvar; j++) {
                rhs += resultRelaxationCvVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationCvVMC.cvsub(iLin), resultRelaxationCvVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixEq1[iEq][iLin][j] = coefficients[j];
            }
            _matrixEq1[iEq][iLin][_nvar] = 0;
            _rhsEq1[iEq][iLin]           = rhs;
        }
        // Set up concave >=0 part:
        if (std::fabs(resultRelaxationCcVMC.cc(iLin)) > 1e19 || (resultRelaxationCcVMC.cc(iLin) != resultRelaxationCcVMC.cc(iLin))) {

            _rhsEq2[iEq][iLin] = 0;

            for (unsigned j = 0; j < _nvar; j++) {
                _matrixEq2[iEq][iLin][j] = 0;
            }
            _matrixEq2[iEq][iLin][_nvar] = 0;
        }
        else {
            rhs = resultRelaxationCcVMC.cc(iLin) + _maingoSettings->deltaEq;
            for (unsigned j = 0; j < _nvar; j++) {
                rhs -= resultRelaxationCcVMC.ccsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationCcVMC.ccsub(iLin), resultRelaxationCcVMC.ccsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixEq2[iEq][iLin][j] = -coefficients[j];
            }
            _matrixEq2[iEq][iLin][_nvar] = 0;
            _rhsEq2[iEq][iLin]           = rhs;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only inequality of the linear program
void
LbpClp::_update_LP_ineqRelaxationOnly(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneqRelaxationOnly)
{

    // Linearize relaxation only inequalities
    if (resultRelaxationVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxation-only inequality constraint " << iIneqRelaxationOnly + 1 << " (of " << _nineqRelaxationOnly << ") (vector) for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinIneqRelaxationOnly[iIneqRelaxationOnly];
    for (unsigned iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        if (std::fabs(resultRelaxationVMC.cv(iLin)) > 1e19 || (resultRelaxationVMC.cv(iLin) != resultRelaxationVMC.cv(iLin))) {
            _rhsIneqRelaxationOnly[iIneqRelaxationOnly][iLin] = 0;

            for (unsigned j = 0; j < _nvar; j++) {
                _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][j] = 0;
            }
            _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][_nvar] = 0;
        }
        else {
            rhs = -resultRelaxationVMC.cv(iLin) + _maingoSettings->deltaIneq;
            for (unsigned j = 0; j < _nvar; j++) {
                rhs += resultRelaxationVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationVMC.cvsub(iLin), resultRelaxationVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][j] = coefficients[j];
            }
            _matrixIneqRelaxationOnly[iIneqRelaxationOnly][iLin][_nvar] = 0;
            _rhsIneqRelaxationOnly[iIneqRelaxationOnly][iLin]           = rhs;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only equality of the linear program
void
LbpClp::_update_LP_eqRelaxationOnly(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iEqRelaxationOnly)
{

    // Linearize relaxation only equalities
    if (resultRelaxationCvVMC.nsub() == 0 || resultRelaxationCcVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxation-only equality constraint " << iEqRelaxationOnly + 1 << " (of " << _neqRelaxationOnly << ") (vector) for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinEqRelaxationOnly[iEqRelaxationOnly];
    for (unsigned iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        // Convex relaxation <=0:
        if (std::fabs(resultRelaxationCvVMC.cv(iLin)) > 1e19 || (resultRelaxationCvVMC.cv(iLin) != resultRelaxationCvVMC.cv(iLin))) {
            _rhsEqRelaxationOnly1[iEqRelaxationOnly][iLin] = 0;

            for (unsigned j = 0; j < _nvar; j++) {
                _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][j] = 0;
            }
            _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][_nvar] = 0;
        }
        else {
            rhs = -resultRelaxationCvVMC.cv(iLin) + _maingoSettings->deltaEq;
            for (unsigned j = 0; j < _nvar; j++) {
                rhs += resultRelaxationCvVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationCvVMC.cvsub(iLin), resultRelaxationCvVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][j] = coefficients[j];
            }
            _matrixEqRelaxationOnly1[iEqRelaxationOnly][iLin][_nvar] = 0;
            _rhsEqRelaxationOnly1[iEqRelaxationOnly][iLin]           = rhs;
        }
        // Set up concave >=0 part:
        if (std::fabs(resultRelaxationCcVMC.cc(iLin)) > 1e19 || (resultRelaxationCcVMC.cc(iLin) != resultRelaxationCcVMC.cc(iLin))) {
            _rhsEqRelaxationOnly2[iEqRelaxationOnly][iLin] = 0;

            for (unsigned j = 0; j < _nvar; j++) {
                _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][j] = 0;
            }
            _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][_nvar] = 0;
        }
        else {
            rhs = resultRelaxationCcVMC.cc(iLin) + _maingoSettings->deltaEq;
            for (unsigned j = 0; j < _nvar; j++) {
                rhs -= resultRelaxationCcVMC.ccsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationCcVMC.ccsub(iLin), resultRelaxationCcVMC.ccsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][j] = -coefficients[j];
            }
            _matrixEqRelaxationOnly2[iEqRelaxationOnly][iLin][_nvar] = 0;
            _rhsEqRelaxationOnly2[iEqRelaxationOnly][iLin]           = rhs;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a squash inequality of the linear program
void
LbpClp::_update_LP_ineq_squash(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneqSquash)
{

    // Linearize inequality constraints:
    if (resultRelaxationVMC.nsub() == 0) {
        std::ostringstream errmsg; // GCOVR_EXCL_START
        errmsg << "  Error in evaluation of relaxed squash inequality constraint " << iIneqSquash + 1 << " (of " << _nineqSquash << ") (vector) for CLP: constraint does not depend on variables.";
        throw MAiNGOException(errmsg.str());
    } 
    // GCOVR_EXCL_STOP
    // Loop over all linearization points
    unsigned wantedLins = _differentNumberOfLins ? _DAGobj->chosenLinPoints.size() : _nLinIneqSquash[iIneqSquash];
    for (unsigned iLin = 0; iLin < wantedLins; iLin++) {
        double rhs = 0;
        if (std::fabs(-resultRelaxationVMC.cv(iLin)) > 1e19 || (resultRelaxationVMC.cv(iLin) != resultRelaxationVMC.cv(iLin))) {
            _rhsIneqSquash[iIneqSquash][iLin] = 0;

            for (unsigned j = 0; j < _nvar; j++) {
                _matrixIneqSquash[iIneqSquash][iLin][j] = 0;
            }
            _matrixIneqSquash[iIneqSquash][iLin][_nvar] = 0;
        }
        else {
            rhs = -resultRelaxationVMC.cv(iLin);    // No tolerance added!
            for (unsigned j = 0; j < _nvar; j++) {
                rhs += resultRelaxationVMC.cvsub(iLin, j) * linearizationPoint[j][iLin];
            }
            std::vector<double> coefficients(resultRelaxationVMC.cvsub(iLin), resultRelaxationVMC.cvsub(iLin) + _nvar);
            _equilibrate_and_relax(coefficients, rhs, lowerVarBounds, upperVarBounds);
            for (unsigned j = 0; j < _nvar; j++) {
                _matrixIneqSquash[iIneqSquash][iLin][j] = coefficients[j];
            }
            _matrixIneqSquash[iIneqSquash][iLin][_nvar] = 0;
            _rhsIneqSquash[iIneqSquash][iLin]           = rhs;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// solves the current linear program
LP_RETCODE
LbpClp::_solve_LP(const babBase::BabNode &currentNode)
{

    try {

        unsigned iRow = 0;

        // Copy data to CLP object
        // Objective
        for (unsigned iObj = 0; iObj < 1; iObj++) {
            for (unsigned iLin = 0; iLin < _nLinObj[iObj]; iLin++) {
                for (unsigned iVar = 0; iVar <= _nvar; iVar++) {
                    _matrix.modifyCoefficient(iRow, iVar, _matrixObj[iObj][iLin][iVar]);
                }
                _upperRowBounds[iRow] = _rhsObj[iObj][iLin];
                iRow++;
            }
        }

        // Inequality constraints
        for (unsigned iIneq = 0; iIneq < _nineq; iIneq++) {
            for (unsigned iLin = 0; iLin < _nLinIneq[iIneq]; iLin++) {
                for (unsigned iVar = 0; iVar <= _nvar; iVar++) {
                    _matrix.modifyCoefficient(iRow, iVar, _matrixIneq[iIneq][iLin][iVar]);
                }
                _upperRowBounds[iRow] = _rhsIneq[iIneq][iLin];
                iRow++;
            }
        }

        // Equality constraints
        for (unsigned iEq = 0; iEq < _neq; iEq++) {
            for (unsigned iLin = 0; iLin < _nLinEq[iEq]; iLin++) {
                for (unsigned iVar = 0; iVar <= _nvar; iVar++) {
                    _matrix.modifyCoefficient(iRow, iVar, _matrixEq1[iEq][iLin][iVar]);
                }
                _upperRowBounds[iRow] = _rhsEq1[iEq][iLin];
                iRow++;
            }
        }

        for (unsigned iEq = 0; iEq < _neq; iEq++) {
            for (unsigned iLin = 0; iLin < _nLinEq[iEq]; iLin++) {
                for (unsigned iVar = 0; iVar <= _nvar; iVar++) {
                    _matrix.modifyCoefficient(iRow, iVar, _matrixEq2[iEq][iLin][iVar]);
                }
                _upperRowBounds[iRow] = _rhsEq2[iEq][iLin];
                iRow++;
            }
        }

        // Relaxation Only inequality constraints
        for (unsigned iIneq = 0; iIneq < _nineqRelaxationOnly; iIneq++) {
            for (unsigned iLin = 0; iLin < _nLinIneqRelaxationOnly[iIneq]; iLin++) {
                for (unsigned iVar = 0; iVar <= _nvar; iVar++) {
                    _matrix.modifyCoefficient(iRow, iVar, _matrixIneqRelaxationOnly[iIneq][iLin][iVar]);
                }
                _upperRowBounds[iRow] = _rhsIneqRelaxationOnly[iIneq][iLin];
                iRow++;
            }
        }

        // Relaxation Only equality constraints
        for (unsigned iEq = 0; iEq < _neqRelaxationOnly; iEq++) {
            for (unsigned iLin = 0; iLin < _nLinEqRelaxationOnly[iEq]; iLin++) {
                for (unsigned iVar = 0; iVar <= _nvar; iVar++) {
                    _matrix.modifyCoefficient(iRow, iVar, _matrixEqRelaxationOnly1[iEq][iLin][iVar]);
                }
                _upperRowBounds[iRow] = _rhsEqRelaxationOnly1[iEq][iLin];
                iRow++;
            }
        }

        for (unsigned iEq = 0; iEq < _neqRelaxationOnly; iEq++) {
            for (unsigned iLin = 0; iLin < _nLinEqRelaxationOnly[iEq]; iLin++) {
                for (unsigned iVar = 0; iVar <= _nvar; iVar++) {
                    _matrix.modifyCoefficient(iRow, iVar, _matrixEqRelaxationOnly2[iEq][iLin][iVar]);
                }
                _upperRowBounds[iRow] = _rhsEqRelaxationOnly2[iEq][iLin];
                iRow++;
            }
        }

        // Squash inequality constraints
        for (unsigned iIneqSquash = 0; iIneqSquash < _nineqSquash; iIneqSquash++) {
            for (unsigned iLin = 0; iLin < _nLinIneqSquash[iIneqSquash]; iLin++) {
                for (unsigned iVar = 0; iVar <= _nvar; iVar++) {
                    _matrix.modifyCoefficient(iRow, iVar, _matrixIneqSquash[iIneqSquash][iLin][iVar]);
                }
                _upperRowBounds[iRow] = _rhsIneqSquash[iIneqSquash][iLin];
                iRow++;
            }
        }

        // CLP simplex object
        _clp.loadProblem(_matrix,
                         _lowerVarBounds.data(), _upperVarBounds.data(), _objective,
                         _lowerRowBounds, _upperRowBounds);

        // Set to minimize (also default)
        _clp.setOptimizationDirection(1);

        // Turn-off scaling. It was observed that turning off the scaling of the problem resulted in shorter runtimes.
        _clp.scaling(0);

        // Use dual algorithm
        _clp.dual();
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while solving the LP with CLP.", e, currentNode);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while solving the LP with CLP.", currentNode);
    }

	return LbpClp::_get_LP_status();  // ensure we don't use any overrides
} // GCOVR_EXCL_STOP


/////////////////////////////////////////////////////////////////////////////////////////////
// function returning the current status of solved linear program
LP_RETCODE
LbpClp::_get_LP_status()
{

    int clpStatus = _clp.status();
    switch (clpStatus) {
        case 1:
        case 2:
            return LP_INFEASIBLE;
        case 0:
            return LP_OPTIMAL;
        default:
            return LP_UNKNOWN;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function setting the solution point and value of the _eta variable to the solution point of the lastly solved LP
void
LbpClp::_get_solution_point(std::vector<double> &solution, double &etaVal)
{

    double *columnPrimal;

    try {
        columnPrimal = _clp.primalColumnSolution();
        etaVal       = _clp.objectiveValue();
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error querying solution point from CLP.", e);
    }
    // GCOVR_EXCL_STOP
    // Ok, successfully obtained solution point
    solution.clear();
    for (unsigned i = 0; i < _nvar; i++) {
        solution.push_back(columnPrimal[i]);
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function returning the objective value of lastly solved LP
double
LbpClp::_get_objective_value_solver()
{
    return _clp.objectiveValue();
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function setting the multipliers
void
LbpClp::_get_multipliers(std::vector<double> &multipliers)
{

    try {
        multipliers.clear();
        double *columnDual = _clp.dualColumnSolution();
        multipliers.resize(_nvar);
        for (unsigned i = 0; i < _nvar; i++) {
            multipliers[i] = columnDual[i];
        }
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while extracting multipliers from CLP", e);
    }
    // GCOVR_EXCL_STOP
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function deactivating the objective LP rows for feasibility OBBT
void
LbpClp::_deactivate_objective_function_for_OBBT()
{

    for (unsigned iLinObj = 0; iLinObj < _nLinObj[0]; iLinObj++) {
        for (unsigned iVar = 0; iVar < _nvar; iVar++) {
            _matrixObj[0][iLinObj][iVar] = 0;
        }
        _matrixObj[0][iLinObj][_nvar] = 0;
        _rhsObj[0][iLinObj]           = 0;
    }
    // Clear CLP objective
    _objective[_nvar] = 0;
    _etaCoeff         = 0;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function modifying the LP for feasibility-optimality OBBT
void
LbpClp::_modify_LP_for_feasopt_OBBT(const double &currentUBD, std::list<unsigned> &toTreatMax, std::list<unsigned> &toTreatMin)
{

    for (unsigned iLinObj = 0; iLinObj < _nLinObj[0]; iLinObj++) {
        _matrixObj[0][iLinObj][_nvar] = 0;
        if (std::fabs(_objectiveScalingFactors[0][iLinObj] * _rhsObj[0][iLinObj] + currentUBD) > 1e19) {
            switch (_maingoSettings->LBP_linPoints) {
                case LINP_KELLEY:
                case LINP_KELLEY_SIMPLEX:
                    if (!_DAGobj->objRowFilled[iLinObj]) {
                        _rhsObj[0][iLinObj] = 1e19;
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
            _rhsObj[0][iLinObj] = _rhsObj[0][iLinObj] + currentUBD * _objectiveScalingFactors[0][iLinObj];
        }
    }
    // Clear Clp objective
    _objective[_nvar] = 0;
    _etaCoeff         = 0;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for setting the optimization sense of variable iVar in OBBT
void
LbpClp::_set_optimization_sense_of_variable(const unsigned &iVar, const int &optimizationSense)
{
    _objective[iVar] = optimizationSense;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for fixing a variable to its bound, used in probing
void
LbpClp::_fix_variable(const unsigned &iVar, const bool fixToLowerBound)
{
    if (fixToLowerBound) {
        _upperVarBounds[iVar] = _lowerVarBounds[iVar];
    }
    else {
        _lowerVarBounds[iVar] = _upperVarBounds[iVar];
    }
}

/////////////////////////////////////////////////////////////////////////////////////////////
// function for setting the optimization sense of variable iVar in OBBT
void
LbpClp::_restore_LP_coefficients_after_OBBT()
{

    // Restore proper objective function and disable warm-start
    for (unsigned iVar = 0; iVar < _nvar; iVar++) {
        _objective[iVar] = 0;
    }
    for (unsigned iLin = 0; iLin < _nLinObj[0]; iLin++) {
        _matrixObj[0][iLin][_nvar] = -1;
    }
    _etaCoeff         = -1;
    _objective[_nvar] = 1;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for checking whether the current linear program is really infeasible
bool
LbpClp::_check_if_LP_really_infeasible()
{

    // It was observed that CLP returned some LPs to be infeasible when solved with scaling turned off. Here, we check again if that is really the case by solving again with scaling turned on.
    bool reallyInfeasible = true;

    if (reallyInfeasible) {
        _clp.scaling(1);
        _clp.dual();
        if (_clp.status() == 0) {
            reallyInfeasible = false;
        }
    }

    if (reallyInfeasible) {
        _clp.scaling(1);
        _clp.primal();
        if (_clp.status() == 0) {
            reallyInfeasible = false;
        }
    }

    return reallyInfeasible;
}


#ifdef LP__OPTIMALITY_CHECK
/////////////////////////////////////////////////////////////////////////////////////////////
// infeasibility check using Farkas' Lemma
SUBSOLVER_RETCODE
LbpClp::_check_infeasibility(const babBase::BabNode &currentNode)
{

    double *farkasVals;

    bool reallyInfeasible = false;
    try {

        _clp.scaling(0);
        _clp.dual();
        if (_clp.status() == 1 || _clp.status() == 2) {    // Yes, it may really change !!!

            farkasVals = _clp.infeasibilityRay();
            if (!farkasVals) {
                _logger->print_message("  Warning: Could not retrieve Farkas' values from CLP. Continuing with parent LBD...\n", VERB_NORMAL, LBP_VERBOSITY);
                return SUBSOLVER_FEASIBLE;
            }

            // Need to normalize and then scale by -1 the Farkas Certificate
            double norm = 0.;
            for (unsigned i = 0; i < _numrows; i++) {
                norm = norm + farkasVals[i] * farkasVals[i];
            }
            norm = std::sqrt(norm);
            for (unsigned i = 0; i < _numrows; i++) {
                farkasVals[i] = -farkasVals[i] / norm;
            }
            reallyInfeasible = true;
        }
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        std::ostringstream errmsg;
        errmsg << "  Error: Variables at dual point of Farkas' certificate of LBP could not be extracted from CLP. " << std::endl;
        errmsg << "  CLP status is: " << _clp.status();
        throw MAiNGOException(errmsg.str(), e, currentNode);
    }
    // GCOVR_EXCL_STOP
    if (reallyInfeasible) {
        // Check Farkas' Lemma, for the application please read some literature.
        // In general, we want to find a point such that y^T *A>=0 and b^T *y <0 since then for x>=0 and A*x<=b, 0 > y^T *b >= y^T *A *x >=0 which is a contradiction, so y^T *b <= y^T *A *x has to hold for an x
        // Order of constraints in farkasVals: 1. obj constraint 2. ineq 3. eq convex 4. eq concave 5. rel_only_ineq  6. rel_only_eq convex 7. rel_only_eq concave 8. squash ineq
        std::vector<double> yA;    // y^T *A
        yA.resize(_nvar);
        std::vector<double> z;
        z.resize(_nvar);
        std::vector<double> pl(currentNode.get_lower_bounds()), pu(currentNode.get_upper_bounds());
        unsigned farkasVar = 0;
        for (unsigned j = 0; j < _nvar; j++) {
            yA[j] = 0;
            // Objective
            for (unsigned i = 0; i < 1; i++) {
                for (unsigned k = 0; k < _nLinObj[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixObj[i][k][j];
                    farkasVar++;
                }
            }
            // Inequalities
            for (unsigned i = 0; i < _nineq; i++) {
                for (unsigned k = 0; k < _nLinIneq[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixIneq[i][k][j];
                    farkasVar++;
                }
            }
            // Equalities convex
            for (unsigned i = 0; i < _neq; i++) {
                for (unsigned k = 0; k < _nLinEq[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixEq1[i][k][j];
                    farkasVar++;
                }
            }
            // Equalities concave
            for (unsigned i = 0; i < _neq; i++) {
                for (unsigned k = 0; k < _nLinEq[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixEq2[i][k][j];
                    farkasVar++;
                }
            }
            // Relaxation only inequalities
            for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
                for (unsigned k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixIneqRelaxationOnly[i][k][j];
                    farkasVar++;
                }
            }
            // Relaxation only equalities convex
            for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
                for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixEqRelaxationOnly1[i][k][j];
                    farkasVar++;
                }
            }
            // Relaxation only equalities concave
            for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
                for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                    yA[j] += farkasVals[farkasVar] * _matrixEqRelaxationOnly2[i][k][j];
                    farkasVar++;
                }
            }
            // Squash inequalities
            for (unsigned i = 0; i < _nineqSquash; i++) {
                for (unsigned k = 0; k < _nLinIneqSquash[i]; k++) {
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
        for (unsigned i = 0; i < 1; i++) {
            for (unsigned k = 0; k < _nLinObj[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsObj[i][k];
                farkasVar++;
            }
        }
        // Inequalities
        for (unsigned i = 0; i < _nineq; i++) {
            for (unsigned k = 0; k < _nLinIneq[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsIneq[i][k];
                farkasVar++;
            }
        }
        // Equalities convex
        for (unsigned i = 0; i < _neq; i++) {
            for (unsigned k = 0; k < _nLinEq[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsEq1[i][k];
                farkasVar++;
            }
        }
        // Equalities concave
        for (unsigned i = 0; i < _neq; i++) {
            for (unsigned k = 0; k < _nLinEq[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsEq2[i][k];
                farkasVar++;
            }
        }
        // Relaxation only inequalities
        for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
            for (unsigned k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsIneqRelaxationOnly[i][k];
                farkasVar++;
            }
        }
        // Relaxation only equalities convex
        for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
            for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsEqRelaxationOnly1[i][k];
                farkasVar++;
            }
        }
        // Relaxation only equalities concave
        for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
            for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsEqRelaxationOnly2[i][k];
                farkasVar++;
            }
        }
        // Squash inequalities
        for (unsigned i = 0; i < _nineqSquash; i++) {
            for (unsigned k = 0; k < _nLinIneqSquash[i]; k++) {
                res1 += farkasVals[farkasVar] * _rhsIneqSquash[i][k];
                farkasVar++;
            }
        }
        double res2 = 0;
        for (unsigned j = 0; j < _nvar; j++) {
            res2 += yA[j] * z[j];
        }
        if (res1 - res2 <= 0. && !mc::isequal(res1, res2, _computationTol * 1e1, _computationTol * 1e1)) {

#ifdef LP__WRITE_CHECK_FILES
            _write_LP_to_file("clp_infeas_check");
#endif

            std::ostringstream outstr;
            outstr << "  Warning: CLP provided an invalid Farkas' certificate. Continuing with parent LBD..." << std::endl;
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
LbpClp::_print_check_feasibility(const std::shared_ptr<Logger> logger, const VERB verbosity, const std::vector<double> &solution, const std::vector<std::vector<double>> rhs, const std::string name, const double value, const unsigned i, unsigned k, const unsigned nvar)
{
    std::ostringstream outstr;
    outstr << "  Warning: CLP returned FEASIBLE although the point is an infeasible one w.r.t. inequality " << i << "!" << std::endl;

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
LbpClp::_check_feasibility(const std::vector<double> &solution)
{

    double value = 0.;
    // Check inequalities
    for (unsigned i = 0; i < _nineq; i++) {
        for (unsigned k = 0; k < _nLinIneq[i]; k++) {
            for (unsigned j = 0; j < _nvar; j++) {
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
    for (unsigned i = 0; i < _neq; i++) {
        for (unsigned k = 0; k < _nLinEq[i]; k++) {
            for (unsigned j = 0; j < _nvar; j++) {
                value += _matrixEq1[i][k][j] * solution[j];
            }
            if (value - _rhsEq1[i][k] > _maingoSettings->deltaEq) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsEq1, "rhsEq1", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
            for (unsigned j = 0; j < _nvar; j++) {
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
    for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
        for (unsigned k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
            for (unsigned j = 0; j < _nvar; j++) {
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
    for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
        for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
            for (unsigned j = 0; j < _nvar; j++) {
                value += _matrixEqRelaxationOnly1[i][k][j] * solution[j];
            }
            if (value - _rhsEqRelaxationOnly1[i][k] > _maingoSettings->deltaEq) {
                _print_check_feasibility(_logger, _maingoSettings->LBP_verbosity, solution, _rhsEqRelaxationOnly1, "rhsEqRelaxationOnly1", value, i, k, _nvar);
                return SUBSOLVER_INFEASIBLE;
            }
            value = 0.;
            for (unsigned j = 0; j < _nvar; j++) {
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
    for (unsigned i = 0; i < _nineqSquash; i++) {
        for (unsigned k = 0; k < _nLinIneqSquash[i]; k++) {
            for (unsigned j = 0; j < _nvar; j++) {
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
LbpClp::_check_optimality(const babBase::BabNode &currentNode, const double newLBD, const std::vector<double> &solution, const double etaVal, const std::vector<double> &multipliers)
{

    // Process solution: dual solution point
    try {

        double *rowDual = _clp.dualRowSolution();

        if (!rowDual) {
            _logger->print_message("Could not retreive Dual Row prices..", VERB_NORMAL, LBP_VERBOSITY);
            return SUBSOLVER_FEASIBLE;
        }

        unsigned dualVar = 0;
        for (unsigned i = 0; i < 1; i++)
            for (unsigned k = 0; k < _nLinObj[i]; k++) {
                _dualValsObj[i][k] = rowDual[dualVar];
                dualVar++;
            }
        for (unsigned i = 0; i < _nineq; i++)
            for (unsigned k = 0; k < _nLinIneq[i]; k++) {
                _dualValsIneq[i][k] = rowDual[dualVar];
                dualVar++;
            }
        for (unsigned i = 0; i < _neq; i++)
            for (unsigned k = 0; k < _nLinEq[i]; k++) {
                _dualValsEq1[i][k] = rowDual[dualVar];
                dualVar++;
            }
        for (unsigned i = 0; i < _neq; i++)
            for (unsigned k = 0; k < _nLinEq[i]; k++) {
                _dualValsEq2[i][k] = rowDual[dualVar];
                dualVar++;
            }
        for (unsigned i = 0; i < _nineqRelaxationOnly; i++)
            for (unsigned k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
                _dualValsIneqRelaxationOnly[i][k] = rowDual[dualVar];
                dualVar++;
            }
        for (unsigned i = 0; i < _neqRelaxationOnly; i++)
            for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                _dualValsEqRelaxationOnly1[i][k] = rowDual[dualVar];
                dualVar++;
            }
        for (unsigned i = 0; i < _neqRelaxationOnly; i++)
            for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
                _dualValsEqRelaxationOnly2[i][k] = rowDual[dualVar];
                dualVar++;
            }
        for (unsigned i = 0; i < _nineqSquash; i++)
            for (unsigned k = 0; k < _nLinIneqSquash[i]; k++) {
                _dualValsIneqSquash[i][k] = rowDual[dualVar];
                dualVar++;
            }
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error in optimality check: Variables at dual solution of LBP could not be extracted from CLP", e, currentNode);
    }
    // GCOVR_EXCL_STOP
    // Ok, successfully obtained dual solution point
    // If multiplier[i] of variable x_i is >0 then you add multiplier[i]*lower bound, else multiplier[i]*upper bound
    std::vector<double> primal;
    primal.resize(_nLinObj[0]);
    double dual = 0;
    for (unsigned k = 0; k < _nLinObj[0]; k++) {
        // Primal solution value
        primal[k] = -_rhsObj[0][k];
        for (unsigned i = 0; i < _nvar; i++) {
            primal[k] += solution[i] * _matrixObj[0][k][i];
        }
        primal[k] = primal[k] / _objectiveScalingFactors[0][k];
        // Dual value of objective linearizations
        dual += _dualValsObj[0][k] * _rhsObj[0][k];
    }
    // Dual value of inequality linearizations
    for (unsigned i = 0; i < _nineq; i++) {
        for (unsigned k = 0; k < _nLinIneq[i]; k++) {
            dual += _dualValsIneq[i][k] * _rhsIneq[i][k];
        }
    }
    // Dual value of equality linearizations
    for (unsigned i = 0; i < _neq; i++) {
        for (unsigned k = 0; k < _nLinEq[i]; k++) {
            dual += _dualValsEq1[i][k] * _rhsEq1[i][k];
            dual += _dualValsEq2[i][k] * _rhsEq2[i][k];
        }
    }
    // Dual value of relaxation only inequality linearizations
    for (unsigned i = 0; i < _nineqRelaxationOnly; i++) {
        for (unsigned k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
            dual += _dualValsIneqRelaxationOnly[i][k] * _rhsIneqRelaxationOnly[i][k];
        }
    }
    // Dual value of relaxation only equality linearizations
    for (unsigned i = 0; i < _neqRelaxationOnly; i++) {
        for (unsigned k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
            dual += _dualValsEqRelaxationOnly1[i][k] * _rhsEqRelaxationOnly1[i][k];
            dual += _dualValsEqRelaxationOnly2[i][k] * _rhsEqRelaxationOnly2[i][k];
        }
    }
    // Dual value of squash inequality linearizations
    for (unsigned i = 0; i < _nineqSquash; i++) {
        for (unsigned k = 0; k < _nLinIneqSquash[i]; k++) {
            dual += _dualValsIneqSquash[i][k] * _rhsIneqSquash[i][k];
        }
    }
    std::vector<double> pl(currentNode.get_lower_bounds()), pu(currentNode.get_upper_bounds());
    for (unsigned i = 0; i < _nvar; i++) {
        if (multipliers[i] > 0.) {
            dual += multipliers[i] * pl[i];
        }
        else {
            dual += multipliers[i] * pu[i];
        }
    }
    // Check if our dual and CLP solution are the same
    if (!mc::isequal(dual, newLBD, _computationTol, _computationTol)) {
        std::ostringstream outstr;
        outstr << "  Warning: Calculated dual: " << dual << " does not equal the solution value returned by CLP: " << newLBD << "." << std::endl;
        outstr << "           Not using this bound." << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);

#ifdef LP__WRITE_CHECK_FILES
        _write_LP_to_file("clp_optim_check");
#endif

        return SUBSOLVER_INFEASIBLE;
    }

    bool checkOptimality = false;
    // At least one of the linearized objectives has to be equal to the dual objective value
    for (unsigned k = 0; k < _nLinObj[0]; k++) {
        if ((fabs(primal[k] - newLBD) <= 1e-9) || mc::isequal(primal[k], newLBD, _computationTol, _computationTol)) {
            checkOptimality = true;
        }
    }
    // If none of the linearized objective inequalities is fulfilled, something went wrong
    if (!checkOptimality) {
        std::ostringstream outstr;
        if (_maingoSettings->LBP_verbosity > VERB_NORMAL) {
            for (unsigned k = 0; k < _nLinObj[0]; k++) {
                outstr << "  Optimality condition violated" << std::endl
                       << "  Primal solution value [" << k << "]: " << primal[k] << " <> Dual solution value: " << dual << std::endl;
                outstr << "  | primal[" << k << "] - dual | = " << std::fabs(primal[k] - newLBD) << " > " << 1e-9 << std::endl;
                outstr << "  Terminating. " << std::endl;
            }
        }
        outstr << "  CLP failed in returning a correct objective value! Falling back to interval arithmetic and proceeding." << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);

#ifdef LP__WRITE_CHECK_FILES
        _write_LP_to_file("clp_optim_check");
#endif

        return SUBSOLVER_INFEASIBLE;
    }
    return SUBSOLVER_FEASIBLE;
}

#endif


/////////////////////////////////////////////////////////////////////////
// function for termination CLP
void
LbpClp::_terminate_Clp()
{
    // Note that all arrays that are used in the _matrix.assignMatrix call are freed by CLP...
    // So here, we only take care of the remaining ones
    delete[] _lowerRowBounds;
    delete[] _upperRowBounds;
    delete[] _objective;
}


#ifdef LP__WRITE_CHECK_FILES
/////////////////////////////////////////////////////////////////////////////////////////////
// write current LP to file
void
LbpClp::_write_LP_to_file(const std::string &fileName)
{
    if (fileName.empty()) {
        _clp.writeLp("MAiNGO_LP_WRITE_CHECK_FILES", "lp", 0);
    }
    else {
        _clp.writeLp(fileName.c_str(), "lp", 0);
    }
}
#endif

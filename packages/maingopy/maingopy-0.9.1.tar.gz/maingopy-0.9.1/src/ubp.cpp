/**********************************************************************************
 * Copyright (c) 2019-2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "ubp.h"
#include "MAiNGOException.h"
#include "mpiUtilities.h"
#include "pointIsWithinNodeBounds.h"
#include "ubpDagObj.h"
#include "ubpEvaluators.h"
#include "ubpStructure.h"

#include <algorithm>
#include <numeric>
#include <set>


using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor for the upper bounding solver
UpperBoundingSolver::UpperBoundingSolver(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
                                         const std::vector<babBase::OptimizationVariable> &variables, const unsigned nineqIn, const unsigned neqIn,
                                         const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn):
    _originalVariables(variables),
    _maingoSettings(settingsIn), _logger(loggerIn), _constraintProperties(constraintPropertiesIn), _intendedUse(useIn)
{
    _DAGobj = std::make_shared<DagObj>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, constraintPropertiesIn, settingsIn, loggerIn);

    _nvar        = variables.size();
    _nineq       = nineqIn;
    _neq         = neqIn;
    _nineqSquash = nineqSquashIn;

    // Store vectors of original upper and lower bounds for more convenient access
    _originalLowerBounds.resize(_nvar);
    _originalUpperBounds.resize(_nvar);
    for (size_t i = 0; i < _nvar; ++i) {
        _originalLowerBounds[i] = _originalVariables[i].get_lower_bound();
        _originalUpperBounds[i] = _originalVariables[i].get_upper_bound();
    }

    // Determine problem structure; the result is stored in the _structure member
    _determine_structure();
}


/////////////////////////////////////////////////////////////////////////
// solve upper bounding problem. This is the function called by external clients.
SUBSOLVER_RETCODE
UpperBoundingSolver::solve(babBase::BabNode const &currentNode, double &objectiveValue, std::vector<double> &solutionPoint)
{

    std::vector<double> lowerVarBounds(currentNode.get_lower_bounds());
    std::vector<double> upperVarBounds(currentNode.get_upper_bounds());
    if (_maingoSettings->LBP_addAuxiliaryVars) {
        lowerVarBounds.resize(_nvar);
        upperVarBounds.resize(_nvar);
    }
    // Check if input "solutionPoint" contains something useful that can be used as initial point
    if (solutionPoint.size() != _nvar) {    // Use midpoint instead
        solutionPoint.clear();
        for (unsigned i = 0; i < _nvar; i++) {
            solutionPoint.push_back((lowerVarBounds[i] + upperVarBounds[i]) / 2.);
        }
    }
    else {
        // Make sure that the initial point is actually within the bounds (otherwise, e.g., NLOPT may throw an exception)
        // It can happen that the initial point is slightly outside the bounds because of round-off error (and possible tolerances of the LP solver)
        for (unsigned i = 0; i < _nvar; i++) {
            solutionPoint[i] = std::max(std::min(solutionPoint[i], upperVarBounds[i]), lowerVarBounds[i]);
        }
    }
    std::vector<double> initialPoint(solutionPoint);    // store initial point for later

    // Check if the initial point already is feasible
    double initialObjective                = _maingoSettings->infinity;
    SUBSOLVER_RETCODE initialPointFeasible = check_feasibility(initialPoint, initialObjective);

    // Call the subsolver to potentially find a better point
    SUBSOLVER_RETCODE subsolverFoundFeasiblePoint;
    if (_maingoSettings->UBP_ignoreNodeBounds) {
        subsolverFoundFeasiblePoint = _solve_nlp(_originalLowerBounds, _originalUpperBounds, objectiveValue, solutionPoint);
    }
    else {
        subsolverFoundFeasiblePoint = _solve_nlp(lowerVarBounds, upperVarBounds, objectiveValue, solutionPoint);
    }

    // Make sure we use the best point we found (be it from the local solver or the initial point...)
    if (initialPointFeasible == SUBSOLVER_FEASIBLE) {
        if (subsolverFoundFeasiblePoint == SUBSOLVER_FEASIBLE) {
            if (initialObjective < objectiveValue) {
                objectiveValue = initialObjective;
                solutionPoint  = initialPoint;
            }
        }
        else {
            objectiveValue = initialObjective;
            solutionPoint  = initialPoint;
        }
    }

    // Treat integers: if we are not integer feasible yet, round to the nearest integers, fix the integer variables and re-solve considering only the continuous variables.
    if ((initialPointFeasible == SUBSOLVER_INFEASIBLE) && (subsolverFoundFeasiblePoint == SUBSOLVER_INFEASIBLE)) {
        bool isInteger = false;
        std::vector<double> fixedIntegersLowerBounds, fixedIntegersUpperBounds;
        if (_maingoSettings->UBP_ignoreNodeBounds) {
            fixedIntegersLowerBounds = _originalLowerBounds;
            fixedIntegersUpperBounds = _originalUpperBounds;
        }
        else {
            fixedIntegersLowerBounds = lowerVarBounds;
            fixedIntegersUpperBounds = upperVarBounds;
        }
        for (unsigned i = 0; i < _nvar; ++i) {
            babBase::enums::VT varType(_originalVariables[i].get_variable_type());
            switch (varType) {
                case babBase::enums::VT_BINARY:
                case babBase::enums::VT_INTEGER:
                    solutionPoint[i]            = round(solutionPoint[i]);
                    fixedIntegersLowerBounds[i] = solutionPoint[i];
                    fixedIntegersUpperBounds[i] = solutionPoint[i];
                    isInteger                   = true;
                case babBase::enums::VT_CONTINUOUS:
                default:
                    break;
            }
        }
        if (isInteger) {
            // Check if new point obtained after rounding is feasible
            initialPoint         = solutionPoint;
            initialPointFeasible = check_feasibility(initialPoint, initialObjective);

            // Solve NLP again from rounded starting point, using variable bounds that fix the integers to one value
            subsolverFoundFeasiblePoint = _solve_nlp(fixedIntegersLowerBounds, fixedIntegersUpperBounds, objectiveValue, solutionPoint);

            // Again make sure we use the best point (be it from the local solver or the rounded initial point...)
            if (initialPointFeasible == SUBSOLVER_FEASIBLE) {
                if (subsolverFoundFeasiblePoint == SUBSOLVER_FEASIBLE) {
                    if (initialObjective < objectiveValue) {
                        objectiveValue = initialObjective;
                        solutionPoint  = initialPoint;
                    }
                }
                else {
                    objectiveValue = initialObjective;
                    solutionPoint  = initialPoint;
                }
            }
        }
    }

    // Return wether we found anything at all
    if ((initialPointFeasible == SUBSOLVER_FEASIBLE) || (subsolverFoundFeasiblePoint == SUBSOLVER_FEASIBLE)) {
        return SUBSOLVER_FEASIBLE;
    }
    else {
        return SUBSOLVER_INFEASIBLE;
    }
}


/////////////////////////////////////////////////////////////////////////
// solve upper bounding problem. This is the internal implementation.
SUBSOLVER_RETCODE
UpperBoundingSolver::_solve_nlp(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, double &objectiveValue, std::vector<double> &solutionPoint)
{

    // In this base class, we do not use any local solver.
    // In fact, we do not even check feasibility of the given point (which is the desired behavior when setting UBP_solverPreprocessing or UBP_solverBab to 0) since this is done in the solve routine *before* calling _solve_nlp.
    return SUBSOLVER_INFEASIBLE;
}


/////////////////////////////////////////////////////////////////////////
// multistart heuristic for automatically solving the UBP from multiple starting points
SUBSOLVER_RETCODE
UpperBoundingSolver::multistart(const babBase::BabNode &currentNode, double &objectiveValue, std::vector<double> &solutionPoint, std::vector<SUBSOLVER_RETCODE> &feasible, std::vector<double> &optimalObjectives, bool &initialPointFeasible)
{

    SUBSOLVER_RETCODE foundFeasible = SUBSOLVER_INFEASIBLE;

#ifdef HAVE_MAiNGO_MPI
    // Get MPI info
    int _rank, _nProcs;
    unsigned searchCount = 0;
    MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &_nProcs);
    // Variables for managing multistart-loop
    unsigned workCount = 0;
#endif
    MAiNGO_IF_BAB_MANAGER
        // Initialize stuff
        std::vector<double>
            lowerVarBounds(currentNode.get_lower_bounds());
        std::vector<double> upperVarBounds(currentNode.get_upper_bounds());
        if (_maingoSettings->LBP_addAuxiliaryVars) {
            lowerVarBounds.resize(_nvar);
            upperVarBounds.resize(_nvar);
        }
        std::vector<double> currentPoint(_nvar), incumbent(_nvar);
        bool usedInitial                 = false;
        bool usedCenter                  = false;
        bool terminationConditionReached = false;
        unsigned nInfeasible             = 0;
        unsigned nDifferentFeasible      = 0;
        double worstFeasible             = -_maingoSettings->infinity;
        double bestFeasible              = _maingoSettings->infinity;
        std::ostringstream outstr;

        // First, check user-specified initial point for feasibility
        double initialObjective = _maingoSettings->infinity;
        if (solutionPoint.empty()) {
            usedInitial          = true;
            initialPointFeasible = false;
        }
        else {
            currentPoint = solutionPoint;
            // Calling a simple feasibility check
            SUBSOLVER_RETCODE initialPointStatus = check_feasibility(currentPoint, initialObjective);
            if (initialPointStatus == SUBSOLVER_FEASIBLE) {
                foundFeasible = SUBSOLVER_FEASIBLE;
                optimalObjectives.push_back(initialObjective);
                outstr << "      User-specified initial point is feasible with objective value " << initialObjective << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
                if (_maingoSettings->PRE_printEveryLocalSearch) {
                    ++nDifferentFeasible;
                }
                bestFeasible         = initialObjective;
                incumbent            = currentPoint;
                worstFeasible        = initialObjective;
                initialPointFeasible = true;
            }
            else {
                if (_maingoSettings->PRE_printEveryLocalSearch) {
                    outstr.str("");
                    outstr.clear();
                    outstr << "      User-specified initial point is infeasible." << std::endl;
                    _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
                }
                initialPointFeasible = false;
            }
        }

        // Multistart local search
        unsigned iLoc                = 0;    // Number of local searches initiated ( sent to workers )
        unsigned iRun                = 0;    // Number of local search runs finished
        bool terminateMultistartLoop = (iLoc < _maingoSettings->PRE_maxLocalSearches) ? false : true;
        if (/* Initial point is infeasible or we are not satisfied with a single feasible point */ ((!_maingoSettings->terminateOnFeasiblePoint) || (!initialPointFeasible))
            /* Objective value of feasible initial point is not good enough for the user */
            && (initialObjective > _maingoSettings->targetUpperBound)
            /* User requested >0 searches */
            && !terminateMultistartLoop) {

#ifdef HAVE_MAiNGO_MPI
            // Send each worker an initial point for a local search
            for (unsigned int worker = 1; worker < (unsigned int)_nProcs; worker++) {

                // If number of processes is greater than number of local searches inform remaining workers to do nothing
                if (worker > _maingoSettings->PRE_maxLocalSearches) {
                    MPI_Send(NULL, 0, MPI_INT, worker, TAG_MS_STOP_SOLVING, MPI_COMM_WORLD);
                    continue;
                }
#endif
                if (!usedInitial) {    // Start from user-specified initial point first
                    usedInitial = true;
                }
                else {
                    currentPoint = this->_generate_multistart_point(usedCenter, lowerVarBounds, upperVarBounds);
                }
                iLoc++;
#ifdef HAVE_MAiNGO_MPI
                // Send generated point to worker
                MPI_Send(currentPoint.data(), _nvar, MPI_DOUBLE, worker, TAG_MS_NEW_POINT, MPI_COMM_WORLD);
                workCount++;
            }
#endif

            while (!terminateMultistartLoop) {    // We use while because we need the counter iLoc externally

                double currentObjective = _maingoSettings->infinity;
#ifdef HAVE_MAiNGO_MPI
                // Receive results from worker
                MPI_Status status;
                MPI_Probe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
                int src = status.MPI_SOURCE;

                MPI_Recv(NULL, 0, MPI_INT, src, MPI_ANY_TAG, MPI_COMM_WORLD, &status);

                SUBSOLVER_RETCODE ubpStatus = SUBSOLVER_INFEASIBLE;
                if (status.MPI_TAG == TAG_MS_FEAS) {    // Multistart is feasible
                    std::vector<double> rcvbuf(_nvar + 1);
                    // Recieve point and objective value
                    MPI_Recv(rcvbuf.data(), _nvar + 1, MPI_DOUBLE, src, TAG_MS_SOLUTION, MPI_COMM_WORLD, &status);
                    currentObjective = rcvbuf[0];
                    currentPoint     = std::vector<double>(rcvbuf.begin() + 1, rcvbuf.begin() + _nvar + 1);

                    ubpStatus = SUBSOLVER_FEASIBLE;
                }
#else
                // Solve
                SUBSOLVER_RETCODE ubpStatus = solve(currentNode, currentObjective, currentPoint);
#endif
                iRun++;

                // Check what we got
                if (ubpStatus == SUBSOLVER_FEASIBLE) {

                    foundFeasible = SUBSOLVER_FEASIBLE;
                    if (_maingoSettings->PRE_printEveryLocalSearch) {
                        outstr.str("");
                        outstr.clear();
                        outstr << "      Run " << iRun << ": Found feasible point with objective value " << currentObjective << std::endl;
                        _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
                        feasible.push_back(SUBSOLVER_FEASIBLE);
                        // Check if we found this point before
                        bool foundPreviously = false;
                        for (size_t i = 0; i < optimalObjectives.size(); ++i) {
                            if (std::fabs(optimalObjectives[i] - currentObjective) < std::max(_maingoSettings->epsilonR * std::fabs(currentObjective), _maingoSettings->epsilonA)) {
                                foundPreviously = true;
                                break;
                            }
                        }
                        if (!foundPreviously) {
                            ++nDifferentFeasible;
                        }
                        optimalObjectives.push_back(currentObjective);
                    }
                    else if (!babBase::larger_or_equal_within_rel_and_abs_tolerance(currentObjective, bestFeasible, _maingoSettings->epsilonR, _maingoSettings->epsilonA)) {
                        outstr.str("");
                        outstr.clear();
                        outstr << "      Found feasible point with objective value " << currentObjective << std::endl;
                        _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
                        optimalObjectives.push_back(currentObjective);
                    }

                    if (currentObjective < bestFeasible) {
                        bestFeasible = currentObjective;
                        incumbent    = currentPoint;
                    }
                    if (currentObjective > worstFeasible) {
                        worstFeasible = currentObjective;
                    }

                    if ((_maingoSettings->terminateOnFeasiblePoint) || (currentObjective <= _maingoSettings->targetUpperBound)) {
                        terminationConditionReached = true;
                    }
                }
                else {

                    ++nInfeasible;
                    if (_maingoSettings->PRE_printEveryLocalSearch) {
                        outstr.str("");
                        outstr.clear();
                        outstr << "      Run " << iLoc << ": No feasible point found." << std::endl;
                        _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
                        feasible.push_back(SUBSOLVER_INFEASIBLE);
                        optimalObjectives.push_back(-42);
                    }
                }

                // Generate point for next round
                if (iLoc < _maingoSettings->PRE_maxLocalSearches && !terminationConditionReached) {
                    currentPoint = this->_generate_multistart_point(usedCenter, lowerVarBounds, upperVarBounds);
                    iLoc++;
#ifdef HAVE_MAiNGO_MPI
                    MPI_Send(currentPoint.data(), _nvar, MPI_DOUBLE, src, TAG_MS_NEW_POINT, MPI_COMM_WORLD);
#endif
                }
                else {
#ifdef HAVE_MAiNGO_MPI
                    if (workCount > 0) {
                        MPI_Send(NULL, 0, MPI_INT, src, TAG_MS_STOP_SOLVING, MPI_COMM_WORLD);
                        workCount--;
                    }
                    if (workCount == 0) {
                        terminateMultistartLoop = true;
                    }
#else
                    terminateMultistartLoop = true;
#endif
                }

            }    // End of multistart for loop
        }        // End of if terminate on condition
#ifdef HAVE_MAiNGO_MPI
        else {
            for (unsigned int worker = 1; worker < (unsigned int)_nProcs; worker++) {
                MPI_Send(NULL, 0, MPI_INT, worker, TAG_MS_STOP_SOLVING, MPI_COMM_WORLD);
            }
        }
#endif

        // Output and cleanup
        if (foundFeasible == SUBSOLVER_FEASIBLE) {
            solutionPoint  = incumbent;
            objectiveValue = bestFeasible;
            if ((_maingoSettings->PRE_printEveryLocalSearch) && (iLoc > 0)) {
                outstr.str("");
                outstr.clear();
                outstr << "      Out of " << iLoc << " local searches, " << nInfeasible << " (i.e., " << nInfeasible * 100. / (double)iLoc << "%) failed to find a feasible point." << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
                if (nDifferentFeasible > 1) {
                    outstr.str("");
                    outstr.clear();
                    outstr << "      The successful ones (including user-specified initial point) returned points with " << nDifferentFeasible << " different objective values ranging from " << bestFeasible << " to " << worstFeasible << "." << std::endl;
                    _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
                }
                else {
                    outstr.str("");
                    outstr.clear();
                    outstr << "      The successful ones (including user-specified initial point) returned exactly one feasible point with objective value " << bestFeasible << "." << std::endl;
                    _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
                }
            }
        }
        else {
            if (_maingoSettings->PRE_maxLocalSearches > 0) {
                _logger->print_message("      No feasible point found.\n", VERB_NORMAL, UBP_VERBOSITY);
            }
        }

#ifdef HAVE_MAiNGO_MPI
        MAiNGO_ELSE    // Now worker
            std::vector<double>
                currentPoint(_nvar);

            MPI_Status status;
            MPI_Probe(0, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
            // Just return if manager tells to stop
            if (status.MPI_TAG == TAG_MS_STOP_SOLVING) {
                MPI_Recv(NULL, 0, MPI_INT, 0, TAG_MS_STOP_SOLVING, MPI_COMM_WORLD, &status);
                return SUBSOLVER_INFEASIBLE;
            }
            else {    // Otherwise get starting point
                MPI_Recv(currentPoint.data(), _nvar, MPI_DOUBLE, 0, TAG_MS_NEW_POINT, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            }

            // Multistart local search
            bool terminateMultistartLoop = false;
            while (!terminateMultistartLoop) {
                // Solve
                double objectiveValue = _maingoSettings->infinity;
                SUBSOLVER_RETCODE ubpStatus;
                try {
                    ubpStatus = solve(currentNode, objectiveValue, currentPoint);
                }
                catch (...) {
                    ubpStatus = SUBSOLVER_INFEASIBLE;
                }

                // Check what we got
                if (ubpStatus == SUBSOLVER_FEASIBLE) {
                    // Inform manager that worker found a feasible point
                    foundFeasible = SUBSOLVER_FEASIBLE;
                    MPI_Send(NULL, 0, MPI_INT, 0, TAG_MS_FEAS, MPI_COMM_WORLD);

                    std::vector<double> sendbuf(_nvar + 1);
                    sendbuf[0] = objectiveValue;
                    for (unsigned int i = 0; i < _nvar; i++) {
                        sendbuf[i + 1] = currentPoint[i];
                    }
                    // Send objective value and feasible point
                    MPI_Send(sendbuf.data(), _nvar + 1, MPI_DOUBLE, 0, TAG_MS_SOLUTION, MPI_COMM_WORLD);
                }
                else {
                    // Inform manager that worker didn't find a feasible point
                    MPI_Send(NULL, 0, MPI_INT, 0, TAG_MS_INFEAS, MPI_COMM_WORLD);
                }
                MPI_Probe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
                if (status.MPI_TAG == TAG_MS_NEW_POINT) {
                    // Keep on working
                    MPI_Recv(currentPoint.data(), _nvar, MPI_DOUBLE, 0, TAG_MS_NEW_POINT, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                }
                else if (status.MPI_TAG == TAG_MS_STOP_SOLVING) {
                    // Done
                    MPI_Recv(NULL, 0, MPI_INT, 0, status.MPI_TAG, MPI_COMM_WORLD, &status);
                    terminateMultistartLoop = true;
                }

            }    // End of multistart loop
#endif
        MAiNGO_END_IF

        return foundFeasible;
}


/////////////////////////////////////////////////////////////////////////
// generates Initial Points for Multistart
std::vector<double>
UpperBoundingSolver::_generate_multistart_point(bool &usedCenter, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    std::vector<double> currentPoint(_nvar);
    if (!usedCenter) {    // Start from center point
        for (unsigned iVar = 0; iVar < _nvar; iVar++) {
            currentPoint[iVar] = (lowerVarBounds[iVar] + upperVarBounds[iVar]) / 2;
        }
        usedCenter = true;
    }
    else {    // For other searches use random starting point
        for (unsigned iVar = 0; iVar < _nvar; iVar++) {
            double tmpRand     = std::rand() / ((double)RAND_MAX + 1);
            currentPoint[iVar] = lowerVarBounds[iVar] + tmpRand * (upperVarBounds[iVar] - lowerVarBounds[iVar]);
        }
    }

    return currentPoint;
}


/////////////////////////////////////////////////////////////////////////
// method for evaluating the objective function
double
maingo::ubp::evaluate_objective(const double *currentPoint, const unsigned nvar, const bool computeGradient, double *gradient, std::shared_ptr<DagObj> dagObj)
{

    if (!computeGradient) {    // Derivative-free solver
        dagObj->DAG.eval(dagObj->subgraphObj, dagObj->doubleArray, dagObj->functionsObj.size(), dagObj->functionsObj.data(), dagObj->resultDoubleObj.data(), nvar, dagObj->vars.data(), currentPoint);
        return dagObj->resultDoubleObj[0];
    }
    else {    // Gradient-based solver
        for (unsigned i = 0; i < nvar; i++) {
            dagObj->adPoint[i] = currentPoint[i];
            dagObj->adPoint[i].diff(i, nvar);
        }
        try {
            dagObj->DAG.eval(dagObj->subgraphObj, dagObj->fadbadArray, dagObj->functionsObj.size(), dagObj->functionsObj.data(), dagObj->resultADobj.data(), nvar, dagObj->vars.data(), dagObj->adPoint.data());
        }
        catch (std::exception &e) {
            if (!dagObj->warningFlag) {
                dagObj->warningFlag = true;
                std::ostringstream outstr;
                outstr << "    Warning: Evaluation of derivatives of objective resulted in an exception. \n             Reason: " << e.what() << std::endl;
                dagObj->logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
            }
        }
        for (unsigned i = 0; i < nvar; i++) {
            gradient[i] = dagObj->resultADobj[0].d(i);
        }
        return dagObj->resultADobj[0].x();
    }
}


/////////////////////////////////////////////////////////////////////////
// method for evaluating the residuals of the normal and squash inequality constraints
void
maingo::ubp::evaluate_inequalities(const double *currentPoint, const unsigned nvar, const unsigned /*_nineq+_nineqSquash*/ nineq, const bool computeGradient, double *result, double *gradient, std::shared_ptr<DagObj> dagObj)
{

    // We evaluate normal and squash inequalities at once
    if (!computeGradient) {
        dagObj->DAG.eval(dagObj->subgraphIneqSquashIneq, dagObj->doubleArray, dagObj->functionsIneqSquashIneq.size(), dagObj->functionsIneqSquashIneq.data(),
                         result, nvar, dagObj->vars.data(), currentPoint);
    }
    else {
        for (unsigned i = 0; i < nvar; i++) {
            dagObj->adPoint[i] = currentPoint[i];
            dagObj->adPoint[i].diff(i, nvar);
        }
        try {
            dagObj->DAG.eval(dagObj->subgraphIneqSquashIneq, dagObj->fadbadArray, dagObj->functionsIneqSquashIneq.size(), dagObj->functionsIneqSquashIneq.data(),
                             dagObj->resultADineqSquashIneq.data(), nvar, dagObj->vars.data(), dagObj->adPoint.data());
        }
        catch (std::exception &e) {
            if (!dagObj->warningFlag) {
                dagObj->warningFlag = true;
                std::ostringstream outstr;
                outstr << "    Warning: Evaluation of derivatives of inequalities resulted in an exception. \n             Reason: " << e.what() << std::endl;
                dagObj->logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
            }
        }
        if (result) {
            for (unsigned i = 0; i < /*_nineq+_nineqSquash*/ nineq; i++) {    // Loop over squash and normal inequality constraints
                result[i] = dagObj->resultADineqSquashIneq[i].x();
                for (unsigned j = 0; j < nvar; j++) {    // Loop over x
                    gradient[i * nvar + j] = dagObj->resultADineqSquashIneq[i].d(j);
                }
            }
        }
        else {
            for (unsigned i = 0; i < /*_nineq+_nineqSquash*/ nineq; i++) {    // Loop over constraints
                for (unsigned j = 0; j < nvar; j++) {                         // Loop over x
                    gradient[i * nvar + j] = dagObj->resultADineqSquashIneq[i].d(j);
                }
            }
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// method for evaluating the residuals of the equality constraints
void
maingo::ubp::evaluate_equalities(const double *currentPoint, const unsigned nvar, const unsigned neq, const bool computeGradient, double *result, double *gradient, std::shared_ptr<DagObj> dagObj)
{

    if (!computeGradient) {
        dagObj->DAG.eval(dagObj->subgraphEq, dagObj->doubleArray, dagObj->functionsEq.size(), dagObj->functionsEq.data(), result, nvar, dagObj->vars.data(), currentPoint);
    }
    else {
        for (unsigned i = 0; i < nvar; i++) {
            dagObj->adPoint[i] = currentPoint[i];
            dagObj->adPoint[i].diff(i, nvar);
        }
        try {
            dagObj->DAG.eval(dagObj->subgraphEq, dagObj->fadbadArray, dagObj->functionsEq.size(), dagObj->functionsEq.data(), dagObj->resultADeq.data(), nvar, dagObj->vars.data(), dagObj->adPoint.data());
        }
        catch (std::exception &e) {
            if (!dagObj->warningFlag) {
                dagObj->warningFlag = true;
                std::ostringstream outstr;
                outstr << "    Warning: Evaluation of derivatives of equalities resulted in an exception. \n             Reason: " << e.what() << std::endl;
                dagObj->logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
            }
        }
        if (result) {
            for (unsigned i = 0; i < neq; i++) {
                result[i] = dagObj->resultADeq[i].x();
                for (unsigned j = 0; j < nvar; j++) {    // Loop over x
                    gradient[i * nvar + j] = dagObj->resultADeq[i].d(j);
                }
            }
        }
        else {
            for (unsigned i = 0; i < neq; i++) {
                for (unsigned j = 0; j < nvar; j++) {    // Loop over x
                    gradient[i * nvar + j] = dagObj->resultADeq[i].d(j);
                }
            }
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// method for evaluating the residuals of the (squash) inequality and equality constraints
void
maingo::ubp::evaluate_constraints(const double *currentPoint, const unsigned nvar, const unsigned ncon, const bool computeGradient, double *result, double *gradient, std::shared_ptr<DagObj> dagObj)
{

    if (!computeGradient) {
        dagObj->DAG.eval(dagObj->subgraphIneqEq, dagObj->doubleArray, dagObj->functionsIneqEq.size(), dagObj->functionsIneqEq.data(), result, nvar, dagObj->vars.data(), currentPoint);
    }
    else {
        for (unsigned i = 0; i < nvar; i++) {
            dagObj->adPoint[i] = currentPoint[i];
            dagObj->adPoint[i].diff(i, nvar);
        }
        try {
            dagObj->DAG.eval(dagObj->subgraphIneqEq, dagObj->fadbadArray, dagObj->functionsIneqEq.size(), dagObj->functionsIneqEq.data(), dagObj->resultADineqEq.data(), nvar, dagObj->vars.data(), dagObj->adPoint.data());
        }
        catch (std::exception &e) {
            if (!dagObj->warningFlag) {
                dagObj->warningFlag = true;
                std::ostringstream outstr;
                outstr << "    Warning: Evaluation of derivatives of constraints resulted in an exception. \n             Reason: " << e.what() << std::endl;
                dagObj->logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
            }
        }
        if (result) {
            for (unsigned i = 0; i < ncon; i++) {
                result[i] = dagObj->resultADineqEq[i].x();
                for (unsigned j = 0; j < nvar; j++) {    // Loop over x
                    gradient[i * nvar + j] = dagObj->resultADineqEq[i].d(j);
                }
            }
        }
        else {
            for (unsigned i = 0; i < ncon; i++) {
                for (unsigned j = 0; j < nvar; j++) {    // Loop over x
                    gradient[i * nvar + j] = dagObj->resultADineqEq[i].d(j);
                }
            }
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// method for evaluating the objective function and the constraint residuals
void
maingo::ubp::evaluate_problem(const double *currentPoint, const unsigned nvar, const unsigned ncon, const bool computeGradient, double *result, double *gradient, std::shared_ptr<DagObj> dagObj)
{


    if (!computeGradient) {
        dagObj->DAG.eval(dagObj->subgraph, dagObj->doubleArray, dagObj->functions.size(), dagObj->functions.data(), result, nvar, dagObj->vars.data(), currentPoint);
    }
    else {
        for (unsigned i = 0; i < nvar; i++) {
            dagObj->adPoint[i] = currentPoint[i];
            dagObj->adPoint[i].diff(i, nvar);
        }
        try {
            dagObj->DAG.eval(dagObj->subgraph, dagObj->fadbadArray, dagObj->functions.size(), dagObj->functions.data(), dagObj->resultAD.data(), nvar, dagObj->vars.data(), dagObj->adPoint.data());
        }
        catch (std::exception &e) {
            if (!dagObj->warningFlag) {
                dagObj->warningFlag = true;
                std::ostringstream outstr;
                outstr << "    Warning: Evaluation of derivatives resulted in an exception. \n             Reason: " << e.what() << std::endl;
                dagObj->logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
            }
        }
        if (result) {
            for (unsigned i = 0; i < ncon + 1; i++) {
                result[i] = dagObj->resultAD[i].x();
                for (unsigned j = 0; j < nvar; j++) {    // Loop over x
                    gradient[i * nvar + j] = dagObj->resultAD[i].d(j);
                }
            }
        }
        else {
            for (unsigned i = 0; i < ncon + 1; i++) {
                for (unsigned j = 0; j < nvar; j++) {    // Loop over x
                    gradient[i * nvar + j] = dagObj->resultAD[i].d(j);
                }
            }
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// method for evaluating the Hessian of the Lagrangian
void
maingo::ubp::evaluate_hessian(const double *currentPoint, const unsigned nvar, const unsigned ncon, double *hessian, std::shared_ptr<DagObj> dagObj)
{

    // In the Ipopt documentation, it is recommended to ignore new_x since Ipopt caches points
    for (unsigned iVar = 0; iVar < nvar; iVar++) {
        dagObj->adPoint2ndOrder[iVar] = currentPoint[iVar];
        dagObj->adPoint2ndOrder[iVar].diff(iVar, nvar);
        dagObj->adPoint2ndOrder[iVar].x().diff(iVar, nvar);
    }
    try {
        dagObj->DAG.eval(dagObj->subgraph, dagObj->fadbadArray2ndOrder, dagObj->functions.size(), dagObj->functions.data(), dagObj->resultAD2ndOrder.data(), nvar, dagObj->vars.data(), dagObj->adPoint2ndOrder.data());
    }
    catch (std::exception &e) {
        if (!dagObj->warningFlag) {
            dagObj->warningFlag = true;
            std::ostringstream outstr;
            outstr << "    Warning: Evaluation of second derivatives resulted in an exception. \n             Reason: " << e.what() << std::endl;
            dagObj->logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
        }
    }
    for (unsigned i = 0; i < ncon + 1; i++) {
        for (unsigned j = 0; j < nvar; j++) {        // Loop over x
            for (unsigned k = 0; k < nvar; k++) {    // Loop over x
                hessian[(i * nvar + j) * nvar + k] = dagObj->resultAD2ndOrder[i].d(j).d(k);
            }
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// method for checking feasibility for equalities
SUBSOLVER_RETCODE
UpperBoundingSolver::_check_eq(const std::vector<double> &modelOutput) const
{
    //  Equalities
    for (unsigned int i = 0; i < _neq; i++) {
        if ( (std::fabs(modelOutput[i + 1 + _nineq + _nineqSquash]) > _maingoSettings->deltaEq) || (std::isnan(modelOutput[i + 1 + _nineq + _nineqSquash])) ) {
            std::ostringstream outstr;
            outstr << "  No feasible point found for UBP. First constraint violation in equality constraint " << i << "." << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
            return SUBSOLVER_INFEASIBLE;
        }
    }
    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////
// method for checking feasibility for inequalities
SUBSOLVER_RETCODE
UpperBoundingSolver::_check_ineq(const std::vector<double> &modelOutput) const
{
    for (unsigned int i = 0; i < _nineq; i++) {
        if ( (modelOutput[i + 1] > _maingoSettings->deltaIneq) || (std::isnan(modelOutput[i + 1])) ) {
            std::ostringstream outstr;
            outstr << "  No feasible point found for UBP. First constraint violation in inequality constraint " << i << "." << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
            return SUBSOLVER_INFEASIBLE;
        }
    }
    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////
// method for checking feasibility for squash inequalities
SUBSOLVER_RETCODE
UpperBoundingSolver::_check_ineq_squash(const std::vector<double> &modelOutput) const
{
    //  Squash Inequalities
    for (unsigned int i = 0; i < _nineqSquash; i++) {
        if ( (modelOutput[i + 1 + _nineq] > 0) || (std::isnan(modelOutput[i + 1 + _nineq])) ) {
            std::ostringstream outstr;
            outstr << "  No feasible point found for UBP. First constraint violation in squash inequality constraint " << i << "." << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);

            return SUBSOLVER_INFEASIBLE;
        }
    }
    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////
// method for checking feasibility with respect to the original variable bounds
SUBSOLVER_RETCODE
UpperBoundingSolver::_check_bounds(const std::vector<double> &currentPoint) const
{

    _logger->print_message("  Checking feasibility with respect to original variable bounds.\n", VERB_ALL, UBP_VERBOSITY);
    if (currentPoint.empty()) {
        _logger->print_message("  No feasible point found for UBP. Point empty.\n", VERB_ALL, UBP_VERBOSITY);
        return SUBSOLVER_INFEASIBLE;
    }
    else if (point_is_within_node_bounds(currentPoint, _originalLowerBounds, _originalUpperBounds)) {
        return SUBSOLVER_FEASIBLE;
    }
    else {
        _logger->print_message("  No feasible point found for UBP. Variable bounds violated.\n", VERB_ALL, UBP_VERBOSITY);
        return SUBSOLVER_INFEASIBLE;
    }
}


/////////////////////////////////////////////////////////////////////////
// method for checking integrality constraints of variables
SUBSOLVER_RETCODE
UpperBoundingSolver::_check_integrality(const std::vector<double> &currentPoint) const
{

    for (unsigned int i = 0; i < currentPoint.size(); i++) {
        // Indices should point to same variables in currentPoint and _originalVariables
        int varType(_originalVariables[i].get_variable_type());
        if (varType == babBase::enums::VT_BINARY && currentPoint[i] != 0 && currentPoint[i] != 1) {
            // Only exact 0 and 1 are permitted

            std::ostringstream outstr;
            outstr << "  No feasible point found for UBP. First constraint violation in binary feasibility of variable ";
            std::string varName(_originalVariables[i].get_name());
            if (varName != "") {
                outstr << "  " << varName;
            }
            else {
                outstr << "  var(" << i + 1 << ")";
            }
            outstr << "   with index " << i << ": " << currentPoint[i] << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);

            return SUBSOLVER_INFEASIBLE;
        }
        else if (varType == babBase::enums::VT_INTEGER) {
            // Only integers are permitted
            double temp = round(currentPoint[i]);
            if (currentPoint[i] != temp) {

                std::ostringstream outstr;
                outstr << "  No feasible point found for UBP. First constraint violation in binary feasibility of variable ";
                std::string varName(_originalVariables[i].get_name());
                if (varName != "") {
                    outstr << "  " << varName;
                }
                else {
                    outstr << "  var(" << i + 1 << ")";
                }
                outstr << "   with index " << i << ": " << currentPoint[i] << std::endl;
                _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);

                return SUBSOLVER_INFEASIBLE;
            }
        }
    }

    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////
// method for checking feasibility of a given point
SUBSOLVER_RETCODE
UpperBoundingSolver::check_feasibility(const std::vector<double> &currentPoint, double &objectiveValue) const
{

    try {
        if (_check_integrality(currentPoint) == SUBSOLVER_FEASIBLE) {
            // Ok, discrete variables take discrete values.
            // Check constraints only for binary/integer-feasible points.
#ifndef HAVE_GROWING_DATASETS
            _DAGobj->DAG.eval(_DAGobj->subgraph, _DAGobj->doubleArray, _DAGobj->functions.size(), _DAGobj->functions.data(), _DAGobj->resultDouble.data(),
                              _nvar, _DAGobj->vars.data(), currentPoint.data());
#else
            // Evaluation of UB and feasibility check always with full dataset
            _DAGobj->DAG.eval(*_DAGobj->storedSubgraph[0], _DAGobj->doubleArray, _DAGobj->storedFunctions[0].size(), _DAGobj->storedFunctions[0].data(), _DAGobj->resultDouble.data(),
                              _nvar, _DAGobj->vars.data(), currentPoint.data());
#endif    // !HAVE_GROWING_DATASETS

            if (_check_eq(_DAGobj->resultDouble) == SUBSOLVER_FEASIBLE) {
                // Ok, equalities are satisfied

                if (_check_ineq(_DAGobj->resultDouble) == SUBSOLVER_FEASIBLE) {
                    // Ok, inequalities are satisfied as well.

                    if (_check_ineq_squash(_DAGobj->resultDouble) == SUBSOLVER_FEASIBLE) {
                        // Ok, squash inequalities are satisfied as well.

                        if (_check_bounds(currentPoint) == SUBSOLVER_FEASIBLE) {
                            // Ok, we are in the original variable bounds

                            objectiveValue = _DAGobj->resultDouble[0];

                            if (! std::isnan(objectiveValue)) {
                                // Return the objective value and print solution if desired

                                std::ostringstream outstr;
                                outstr << "  Found valid UBD: " << objectiveValue << std::endl
                                       << "  UBP solution point: " << std::endl;
                                _logger->print_vector(_nvar, currentPoint, outstr.str(), VERB_ALL, UBP_VERBOSITY);


                                return SUBSOLVER_FEASIBLE;
                            }
                            else {
                                _logger->print_message("  Warning: found point that is feasible but returns objective that is NaN.", VERB_ALL, UBP_VERBOSITY);
                            }
                        }
                    }
                }
            }
        }

        // If we get here the point is infeasible
        return SUBSOLVER_INFEASIBLE;
    }
    catch (const std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error in evaluation of double Model equations while checking feasibility. ", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error in evaluation of double Model equations while checking feasibility. ");
    }
} // GCOVR_EXCL_STOP


#ifdef HAVE_GROWING_DATASETS
/////////////////////////////////////////////////////////////////////////
// passes index of new dataset to respective DagObj routine
void
UpperBoundingSolver::change_growing_objective(const unsigned int indexDataset)
{
    _DAGobj->change_growing_objective(indexDataset);
}


/////////////////////////////////////////////////////////////////////////
// passes index of new dataset to respective DagObj routine
void
UpperBoundingSolver::pass_data_position_to_solver(const std::shared_ptr<std::vector<unsigned int>> datasetsIn, const unsigned int indexFirstDataIn)
{
    _DAGobj->datasets       = datasetsIn;
    _DAGobj->indexFirstData = indexFirstDataIn;
}


/////////////////////////////////////////////////////////////////////////
// passes flag indicating whether to use mean squared error as the objective function to respective DagObj routine
void
UpperBoundingSolver::pass_use_mse_to_solver(const bool useMseIn)
{
    _DAGobj->useMse = useMseIn;
}
#endif    //HAVE_GROWING_DATASETS


/////////////////////////////////////////////////////////////////////////
// sets function properties, number of variables and type (linear, bilinear...)
void
UpperBoundingSolver::_determine_structure()
{
    _structure = UbpStructure();
    _determine_sparsity_jacobian();

    bool allFunctionsLinear = true;
    for (const Constraint &a : *_constraintProperties) {
        if (a.dependency != CONSTRAINT_DEPENDENCY::LINEAR) {
            allFunctionsLinear = false;
            break;
        }
    }

    if (allFunctionsLinear) {
        for (unsigned int jacFuncs = 0; jacFuncs < _DAGobj->functions.size(); jacFuncs++) {
            for (unsigned int iVars = 0; iVars < _nvar; iVars++) {
                std::vector<unsigned> pseudoParticipating(_nvar);
                std::iota(pseudoParticipating.begin(), pseudoParticipating.end(), 0);    //Fill with 0...nVar
                _structure.jacProperties.resize(_DAGobj->functions.size(), std::vector<std::pair<std::vector<unsigned>, CONSTRAINT_DEPENDENCY>>(_nvar));
                _structure.jacProperties[jacFuncs][iVars] = std::make_pair(pseudoParticipating, LINEAR);
            }
        }
    }
    else {


        const mc::FFVar *jacobian = _DAGobj->DAG.FAD(_DAGobj->functions.size(), _DAGobj->functions.data(), _nvar, _DAGobj->vars.data());
        std::vector<std::map<int, int>> funcDep;
        funcDep.resize(_DAGobj->functions.size() * _nvar);    // Jacobian has #funcs * #vars entries
        _structure.jacProperties.resize(_DAGobj->functions.size(), std::vector<std::pair<std::vector<unsigned>, CONSTRAINT_DEPENDENCY>>(_nvar));
        for (unsigned int i = 0; i < funcDep.size(); i++) {
            funcDep[i] = jacobian[i].dep().dep();
        }

        unsigned int jacIndex = 0;
        // Loop over all functions in the Jacobian, there are #funcs * #vars many
        for (unsigned int jacFuncs = 0; jacFuncs < _DAGobj->functions.size(); jacFuncs++) {
            for (unsigned int iVars = 0; iVars < _nvar; iVars++) {
                std::vector<unsigned> participatingVars;
                mc::FFDep::TYPE functionStructure = mc::FFDep::L;
                for (unsigned int k = 0; k < _nvar; k++) {
                    auto ito = funcDep[jacIndex].find(k);
                    // Count all participating variables
                    if (ito != funcDep[jacIndex].end()) {
                        participatingVars.push_back(k);
                        mc::FFDep::TYPE variableDep = (mc::FFDep::TYPE)(ito->second);
                        // Update function type
                        if (functionStructure < variableDep) {
                            functionStructure = variableDep;
                        }
                    }
                }
                switch (functionStructure) {
                    case mc::FFDep::L:
                        _structure.jacProperties[jacFuncs][iVars] = std::make_pair(participatingVars, LINEAR);
                        break;
                    case mc::FFDep::B:
                    case mc::FFDep::Q:
                    case mc::FFDep::P:
                    case mc::FFDep::R:
                    case mc::FFDep::N:
                    case mc::FFDep::D:
                    default:
                        _structure.jacProperties[jacFuncs][iVars] = std::make_pair(participatingVars, NONLINEAR);
                        break;
                }
                jacIndex++;
            }
        }

        delete[] jacobian;
    }
    if (allFunctionsLinear) {
        _structure.nnonZeroHessian = 0;
        _structure.nonZeroHessianIRow.clear();
        _structure.nonZeroHessianJCol.clear();
    }
    else {
        _determine_sparsity_hessian();
    }
}


/////////////////////////////////////////////////////////////////////////
// sets sparsity information for the Jacobian of constraints
void
UpperBoundingSolver::_determine_sparsity_jacobian()
{

    // Count the non-zeros in Jacobian
    _structure.nnonZeroJac = 0;
    for (size_t i = 1; i < 1 + _nineq + _nineqSquash + _neq; i++) {
        _structure.nnonZeroJac += (*_constraintProperties)[i].nparticipatingVariables;
    }

    _structure.nonZeroJacIRow.clear();
    _structure.nonZeroJacJCol.clear();
    _structure.nonZeroJacIRow.resize(_structure.nnonZeroJac);
    _structure.nonZeroJacJCol.resize(_structure.nnonZeroJac);
    // Ordering is obj, ineq, squash ineq, eq
    unsigned int consIndex = 0;
    unsigned nObj          = 1;
    for (size_t i = nObj; i < _constraintProperties->size(); i++) {
        for (unsigned int j = 0; j < (*_constraintProperties)[i].nparticipatingVariables; j++) {
            _structure.nonZeroJacIRow[consIndex] = i - nObj;
            _structure.nonZeroJacJCol[consIndex] = (*_constraintProperties)[i].participatingVariables[j];
            consIndex++;
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// sets sparsity information
void
UpperBoundingSolver::_determine_sparsity_hessian()
{

    // Structure in triplet format: https://www.coin-or.org/Ipopt/documentation/node38.html
    _structure.nnonZeroHessian = 0;
    _structure.nonZeroHessianIRow.clear();
    _structure.nonZeroHessianJCol.clear();

    // Count the non-zeros in Lagrangian Hessian
    std::set<std::pair<unsigned, unsigned>> hessianEntries;
    for (unsigned int iFunc = 0; iFunc < _structure.jacProperties.size(); iFunc++) {
        for (unsigned int iVar = 0; iVar < _structure.jacProperties[iFunc].size(); iVar++) {
            for (unsigned int j = 0; j < _structure.jacProperties[iFunc][iVar].first.size(); j++) {
                if (_structure.jacProperties[iFunc][iVar].first[j] <= iVar) {    // Lower triangular matrix
                    hessianEntries.insert(std::make_pair(iVar, _structure.jacProperties[iFunc][iVar].first[j]));
                }
            }
        }
    }
    for (auto it = hessianEntries.begin(); it != hessianEntries.end(); ++it) {
        _structure.nonZeroHessianIRow.push_back((*it).first);
        _structure.nonZeroHessianJCol.push_back((*it).second);
        _structure.nnonZeroHessian++;
    }
}

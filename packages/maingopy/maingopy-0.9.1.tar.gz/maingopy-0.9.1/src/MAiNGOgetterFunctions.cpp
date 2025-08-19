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

#include "MAiNGO.h"
#include "MAiNGOException.h"
#include "bab.h"


using namespace maingo;


/////////////////////////////////////////////////////////////////////////
// returns the value of the objective at solution point
double
MAiNGO::get_objective_value() const
{
    if ((_maingoStatus != GLOBALLY_OPTIMAL) && (_maingoStatus != FEASIBLE_POINT)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying objective value. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    return _solutionValue;
}


/////////////////////////////////////////////////////////////////////////
// returns the solution point
std::vector<double>
MAiNGO::get_solution_point() const
{
    if (_solutionPoint.empty()) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying solution point. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    std::vector<double> solutionPoint;
    unsigned removed = 0;
    for (unsigned i = 0; i < _nvarOriginal; ++i) {
        if (_removedVariables[i]) {
            // If the variable has been removed from the optimization problem, simply return the middle point of the original interval
            solutionPoint.push_back(0.5*(_originalVariables[i].get_lower_bound() + _originalVariables[i].get_upper_bound()));
            removed++;
        }
        else {
            // Otherwise simply return the value of the variable at solution point
            solutionPoint.push_back(_solutionPoint[i - removed]);
        }
    }
    return solutionPoint;
}


/////////////////////////////////////////////////////////////////////////
// returns the solution time
double
MAiNGO::get_cpu_solution_time() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying solution time. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    return _solutionTime;
}


/////////////////////////////////////////////////////////////////////////
// returns the solution time
double
MAiNGO::get_wallclock_solution_time() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying solution time. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    return _solutionTimeWallClock;
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the number of iterations
double
MAiNGO::get_iterations() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying number of iterations. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    if (_myBaB) {
        return _myBaB->get_iterations();
    }
    else {
        return 0;
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the maximum number of nodes in memory
double
MAiNGO::get_max_nodes_in_memory() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying number of nodes in memory. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    if (_myBaB) {
        return _myBaB->get_max_nodes_in_memory();
    }
    else {
        return 1;
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning number of UBD problems solved
double
MAiNGO::get_UBP_count() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying UBP count. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    if (_myBaB) {
        return _myBaB->get_UBP_count();
    }
    else {
        return 1;
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning number of LBD problems solved
double
MAiNGO::get_LBP_count() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying LBP count. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    if (_myBaB) {
        return _myBaB->get_LBP_count();
    }
    else {
        return 0;
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the final LBD
double
MAiNGO::get_final_LBD() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying final LBD. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    if (_myBaB) {
        return _myBaB->get_final_LBD();
    }
    else {
        return _solutionValue;    // In case of an LP, MIP, QP, or MIQP, we take the solution to be exact for now...
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the final absolute gap
double
MAiNGO::get_final_abs_gap() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying final absolute gap. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    if (_myBaB) {
        return _myBaB->get_final_abs_gap();
    }
    else {
        return 0;
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the final relative gap
double
MAiNGO::get_final_rel_gap() const
{
    if ((_maingoStatus == NOT_SOLVED_YET)) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying final relative gap. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }
    if (_myBaB) {
        return _myBaB->get_final_rel_gap();
    }
    else {
        return 0;
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the current MAiNGO status
RETCODE
MAiNGO::get_status() const
{
    return _maingoStatus;
}
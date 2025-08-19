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


namespace maingo {


/**
* @enum RETCODE
* @brief Enum for representing the return codes returned by MAiNGO after the solve() function was called.
*/
enum RETCODE {
    GLOBALLY_OPTIMAL = 0,     /*!< found solution is globally optimal */
    INFEASIBLE,               /*!< the given problem is infeasible */
    FEASIBLE_POINT,           /*!< the returned solution is feasible */
    NO_FEASIBLE_POINT_FOUND,  /*!< no feasible point was found */
    BOUND_TARGETS,            /*!< reached user-defined target for either lower or upper bound */
    NOT_SOLVED_YET,           /*!< problem has not been solved yet */
    JUST_A_WORKER_DONT_ASK_ME /*!< dummy status for workers in parallel version */
};

/** 
* @enum SUBSOLVER_RETCODE
* @brief Enum for representing the return codes returned by the different sub-solvers (UpperBoundingSolver, LowerBoundingSolver).
*/
enum SUBSOLVER_RETCODE {
    SUBSOLVER_INFEASIBLE = 0, /*!< no feasible point was found, or the problem was proven to be infeasible. */
    SUBSOLVER_FEASIBLE,       /*!< returned solution is feasible. */
};

/** 
* @enum TIGHTENING_RETCODE
* @brief Enum for representing the return codes returned by LowerBoundingSolvers when solving OBBT or constraint propagation
*/
enum TIGHTENING_RETCODE {
    TIGHTENING_INFEASIBLE = 0, /*!< the problem was found to be infeasible during bound tightening */
    TIGHTENING_UNCHANGED,      /*!< no progress was made in bound tightening */
    TIGHTENING_CHANGED         /*!< the bounds were successfully tightened */
};


namespace lbp {


/** 
* @enum LINEARIZATION_RETCODE
* @brief Enum for representing the return codes returned by the different linearization techniques.
*/
enum LINEARIZATION_RETCODE {
    LINEARIZATION_INFEASIBLE = 0, /*!< the problem was found to be infeasible during linearization */
    LINEARIZATION_OPTIMAL,        /*!< solved final LP during linearization */
    LINEARIZATION_UNKNOWN         /*!< the solver did not solve the final LP problem yet */
};

/** 
* @enum LP_RETCODE
* @brief Enum for representing the return codes returned when a linear program is solved.
*/
enum LP_RETCODE {
    LP_INFEASIBLE = 0, /*!< the linear program was found to be infeasible */
    LP_OPTIMAL,        /*!< solved LP to optimality */
    LP_UNKNOWN         /*!< solved LP to unknown status  */
};


}    // end namespace lbp


}    // end namespace maingo
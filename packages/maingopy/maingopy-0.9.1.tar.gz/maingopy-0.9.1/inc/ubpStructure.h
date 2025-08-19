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

#include "constraint.h"

#include <utility>
#include <vector>


namespace maingo {


namespace ubp {


/**
* @struct UbpStructure
* @brief Struct for storing structure information for the upper bounding solver.
*/
struct UbpStructure {

    //For information on sparsity structure see https://www.coin-or.org/Ipopt/documentation/node38.html
    unsigned nnonZeroJac;                                                                            /*!< number of non zeros in Jacobian (w/o objective) */
    unsigned nnonZeroHessian;                                                                        /*!< number of non zeros in Hessian of Lagrangian */
    std::vector<unsigned> nonZeroJacIRow;                                                            /*!< vector holding sparsity information of Jacobian of constraints */
    std::vector<unsigned> nonZeroJacJCol;                                                            /*!< vector holding sparsity information of Jacobian of constraints */
    std::vector<unsigned> nonZeroHessianIRow;                                                        /*!< vector holding sparsity information of Hessian of Lagrangian */
    std::vector<unsigned> nonZeroHessianJCol;                                                        /*!< vector holding sparsity information of Jacobian of constraints */
    std::vector<std::vector<std::pair<std::vector<unsigned>, CONSTRAINT_DEPENDENCY>>> jacProperties; /*!< Jaocobian properties implemented as vector for each function holding a vector for each variable (derivative w.r.t. this variable) holding the number of participating variables */
};


}    // end namespace ubp


}    // end namespace maingo
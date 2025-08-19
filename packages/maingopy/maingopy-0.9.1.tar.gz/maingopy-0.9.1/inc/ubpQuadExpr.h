/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * @file ubpQuadExpr.h
 *
 * @brief File containing declaration of structure UbpQuadExpr used to compute
 *        coefficients of linear and quadratic terms in (MIQ)Ps.
 *
 **********************************************************************************/

#define LAZYQUAD

#pragma once

#include "MAiNGOException.h"

#include "mcop.hpp"
#ifdef LAZYQUAD
#include "ubpLazyQuadExpr.h"
namespace maingo {
namespace ubp {
using UbpQuadExpr = LazyQuadExpr;
}
}    // namespace maingo
#else
#include <vector>
#endif

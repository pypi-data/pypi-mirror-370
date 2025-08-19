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

// Pre-processor variable for specific additional output in MAiNGO useful for debugging
#undef MAiNGO_DEBUG_MODE

// Pre-processor variable enabling infeasibility, optimality and feasibility checks for the lower bounding LP
#define LP__OPTIMALITY_CHECK

// Pre-processor variable enabling writing of files for the above checks
#undef LP__WRITE_CHECK_FILES
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
	* @brief Function for querying CPU time of the process
	*/
double get_cpu_time();

/**
	* @brief Function for querying wall clock time of the process
	*/
double get_wall_time();

}    // namespace maingo
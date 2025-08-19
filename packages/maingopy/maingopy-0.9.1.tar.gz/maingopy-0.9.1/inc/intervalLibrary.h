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


#include "mcfilib.hpp"

/**
	*  @typedef filib::interval<double,filib::rounding_strategy::native_switched,filib::interval_mode::i_mode_extended> I
	*
	*  @brief A type definition for an Interval variable using FILIB++ library which handles infinity properly and does not abort the program
	*/
typedef filib::interval<double, filib::rounding_strategy::native_switched, filib::interval_mode::i_mode_extended> I;


#include "ffunc.hpp"
#include "mccormick.hpp"
#include "vmccormick.hpp"

/**
*  @typedef mc::McCormick<I> MC
*
*  @brief A type definition for a McCormick variable
*/
typedef mc::McCormick<I> MC;

/**
*  @typedef mc::vMcCormick<I> vMC
*
*  @brief A type definition for a vector McCormick variable
*/
typedef mc::vMcCormick<I> vMC;
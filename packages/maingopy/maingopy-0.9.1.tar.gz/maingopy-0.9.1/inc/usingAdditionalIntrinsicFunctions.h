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


// Using declarations of all additional functions defined in MC++ for a comfortable use of these functions in the model
using mc::acoth;
using mc::acquisition_function;
using mc::arh;
using mc::bounding_func;
using mc::bstep;
using mc::centerline_deficit;
using mc::cost_function;
using mc::coth;
using mc::covariance_function;
using mc::enthalpy_of_vaporization;
using mc::euclidean_norm_2d;
using mc::expx_times_y;
using mc::fabsx_times_x;
using mc::fstep;
using mc::gaussian_probability_density_function;
using mc::iapws;
using mc::ideal_gas_enthalpy;
using mc::lb_func;
using mc::lmtd;
using mc::mc_print;
using mc::neg;
using mc::nrtl_dGtau;
using mc::nrtl_dtau;
using mc::nrtl_G;
using mc::nrtl_Gdtau;
using mc::nrtl_Gtau;
using mc::nrtl_tau;
using mc::p_sat_ethanol_schroeder;
using mc::pos;
using mc::power_curve;
using mc::regnormal;
using mc::rho_liq_sat_ethanol_schroeder;
using mc::rho_vap_sat_ethanol_schroeder;
using mc::rlmtd;
using mc::saturation_temperature;
using mc::sqr;
using mc::squash_node;
using mc::single_neuron;
using mc::sum_div;
using mc::ub_func;
using mc::vapor_pressure;
using mc::wake_deficit;
using mc::wake_profile;
using mc::xexpax;
using mc::xlog;
using mc::xlog_sum;
using std::max;
using std::min;
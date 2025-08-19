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

#include "ffunc.hpp"

inline mc::FFVar
xlogx(const mc::FFVar& Var)
{
    return mc::xlog(Var);
}

inline mc::FFVar
xexpy(const mc::FFVar& y, const mc::FFVar& x)
{
    return mc::expx_times_y(x, y);
}

inline mc::FFVar
norm2(const mc::FFVar& Var1, const mc::FFVar& Var2)
{
    return mc::euclidean_norm_2d(Var1, Var2);
}

inline mc::FFVar
xabsx(const mc::FFVar& Var)
{
    return mc::fabsx_times_x(Var);
}

inline mc::FFVar
squash(const mc::FFVar& Var, const double lb, const double ub)
{
    return mc::squash_node(Var, lb, ub);
}

inline mc::FFVar
single_NN(const std::vector<mc::FFVar>& Var, const std::vector<double>& w, const double b, const int type)
{
    return mc::single_neuron(Var, w, b, type);
}

inline mc::FFVar
ext_antoine_psat(const mc::FFVar& T, const double p1, const double p2, const double p3, const double p4,
                 const double p5, const double p6, const double p7)
{
    return mc::vapor_pressure(T, 1, p1, p2, p3, p4, p5, p6, p7);
}

inline mc::FFVar
ext_antoine_psat(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 7);
    return mc::vapor_pressure(T, 1, p[0], p[1], p[2], p[3], p[4], p[5], p[6]);
}

inline mc::FFVar
antoine_psat(const mc::FFVar& T, const double p1, const double p2, const double p3)
{
    return mc::vapor_pressure(T, 2, p1, p2, p3);
}

inline mc::FFVar
antoine_psat(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 3);
    return mc::vapor_pressure(T, 2, p[0], p[1], p[2]);
}

inline mc::FFVar
wagner_psat(const mc::FFVar& Var, const double p1, const double p2, const double p3, const double p4, const double Tc, const double p6)
{
    return mc::vapor_pressure(Var, 3, p1, p2, p3, p4, Tc, p6);
}

inline mc::FFVar
wagner_psat(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 6);
    return mc::vapor_pressure(T, 3, p[0], p[1], p[2], p[3], p[4], p[5]);
}

inline mc::FFVar
ik_cape_psat(const mc::FFVar& T, const double p1, const double p2, const double p3, const double p4,
             const double p5, const double p6, const double p7, const double p8, const double p9, const double p10)
{

    return mc::vapor_pressure(T, 4, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10);
}

inline mc::FFVar
ik_cape_psat(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 10);
    return mc::vapor_pressure(T, 4, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9]);
}

inline mc::FFVar
antoine_tsat(const mc::FFVar& T, const double p1, const double p2, const double p3)
{
    return mc::saturation_temperature(T, 2, p1, p2, p3);
}

inline mc::FFVar
antoine_tsat(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 3);
    return mc::saturation_temperature(T, 2, p[0], p[1], p[2]);
}

inline mc::FFVar
aspen_hig(const mc::FFVar& T, const double T0, const double p1, const double p2, const double p3, const double p4,
          const double p5, const double p6)
{
    return mc::ideal_gas_enthalpy(T, T0, 1, p1, p2, p3, p4, p5, p6);
}

inline mc::FFVar
aspen_hig(const mc::FFVar& T, const double T0, const std::vector<double> p)
{
    assert(p.size() == 6);
    return mc::ideal_gas_enthalpy(T, T0, 1, p[0], p[1], p[2], p[3], p[4], p[5]);
}

inline mc::FFVar
nasa9_hig(const mc::FFVar& T, const double T0, const double p1, const double p2, const double p3, const double p4,
          const double p5, const double p6, const double p7)
{
    return mc::ideal_gas_enthalpy(T, T0, 2, p1, p2, p3, p4, p5, p6, p7);
}

inline mc::FFVar
nasa9_hig(const mc::FFVar& T, const double T0, const std::vector<double> p)
{
    assert(p.size() == 7);
    return mc::ideal_gas_enthalpy(T, T0, 2, p[0], p[1], p[2], p[3], p[4], p[5], p[6]);
}

inline mc::FFVar
dippr107_hig(const mc::FFVar& T, const double T0, const double p1, const double p2, const double p3, const double p4,
             const double p5)
{
    return mc::ideal_gas_enthalpy(T, T0, 3, p1, p2, p3, p4, p5);
}

inline mc::FFVar
dippr107_hig(const mc::FFVar& T, const double T0, const std::vector<double> p)
{
    assert(p.size() == 5);
    return mc::ideal_gas_enthalpy(T, T0, 3, p[0], p[1], p[2], p[3], p[4]);
}

inline mc::FFVar
dippr127_hig(const mc::FFVar& T, const double T0, const double p1, const double p2, const double p3, const double p4,
             const double p5, const double p6, const double p7)
{
    return mc::ideal_gas_enthalpy(T, T0, 4, p1, p2, p3, p4, p5, p6, p7);
}

inline mc::FFVar
dippr127_hig(const mc::FFVar& T, const double T0, const std::vector<double> p)
{
    assert(p.size() == 7);
    return mc::ideal_gas_enthalpy(T, T0, 4, p[0], p[1], p[2], p[3], p[4], p[5], p[6]);
}

inline mc::FFVar
watson_dhvap(const mc::FFVar& T, const double Tc, const double a, const double b, const double T1,
             const double dHT1)
{
    return mc::enthalpy_of_vaporization(T, 1, Tc, a, b, T1, dHT1);
}

inline mc::FFVar
watson_dhvap(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 5);
    return mc::enthalpy_of_vaporization(T, 1, p[0], p[1], p[2], p[3], p[4]);
}

inline mc::FFVar
dippr106_dhvap(const mc::FFVar& T, const double Tc, const double p1, const double p2, const double p3,
               const double p4, const double p5)
{
    return mc::enthalpy_of_vaporization(T, 2, Tc, p1, p2, p3, p4, p5);
}

inline mc::FFVar
dippr106_dhvap(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 6);
    return mc::enthalpy_of_vaporization(T, 2, p[0], p[1], p[2], p[3], p[4], p[5]);
}


inline mc::FFVar
nrtl_tau(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 4);
    return mc::nrtl_tau(T, p[0], p[1], p[2], p[3]);
}

inline mc::FFVar
nrtl_dtau(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 3);
    return mc::nrtl_dtau(T, p[0], p[1], p[2]);
}

inline mc::FFVar
nrtl_g(const mc::FFVar& T, const double a, const double b, const double e, const double f, const double alpha)
{
    return mc::nrtl_G(T, a, b, e, f, alpha);
}

inline mc::FFVar
nrtl_g(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 5);
    return mc::nrtl_G(T, p[0], p[1], p[2], p[3], p[4]);
}

inline mc::FFVar
nrtl_gtau(const mc::FFVar& T, const double a, const double b, const double e, const double f, const double alpha)
{
    return mc::nrtl_Gtau(T, a, b, e, f, alpha);
}

inline mc::FFVar
nrtl_gtau(const mc::FFVar& T, const std::vector<double> p)
{
    assert(p.size() == 5);
    return mc::nrtl_Gtau(T, p[0], p[1], p[2], p[3], p[4]);
}

inline mc::FFVar
nrtl_gdtau(const mc::FFVar& Var, const double a, const double b, const double e, const double f, const double alpha)
{
    return mc::nrtl_Gdtau(Var, a, b, e, f, alpha);
}

inline mc::FFVar
nrtl_gdtau(const mc::FFVar& Var, const std::vector<double> p)
{
    assert(p.size() == 5);
    return mc::nrtl_Gdtau(Var, p[0], p[1], p[2], p[3], p[4]);
}

inline mc::FFVar
nrtl_dgtau(const mc::FFVar& Var, const double a, const double b, const double e, const double f, const double alpha)
{
    return mc::nrtl_dGtau(Var, a, b, e, f, alpha);
}

inline mc::FFVar
nrtl_dgtau(const mc::FFVar& Var, const std::vector<double> p)
{
    assert(p.size() == 5);
    return mc::nrtl_dGtau(Var, p[0], p[1], p[2], p[3], p[4]);
}

inline mc::FFVar
schroeder_ethanol_p(const mc::FFVar& Var)
{
    return mc::p_sat_ethanol_schroeder(Var);
}

inline mc::FFVar
schroeder_ethanol_rhovap(const mc::FFVar& Var)
{
    return mc::rho_vap_sat_ethanol_schroeder(Var);
}

inline mc::FFVar
schroeder_ethanol_rholiq(const mc::FFVar& Var)
{
    return mc::rho_liq_sat_ethanol_schroeder(Var);
}

inline mc::FFVar
cost_turton(const mc::FFVar& Var, const double p1, const double p2, const double p3)
{
    return mc::cost_function(Var, 1, p1, p2, p3);
}

inline mc::FFVar
cost_turton(const mc::FFVar& Var, const std::vector<double> p)
{
    assert(p.size() == 3);
    return mc::cost_function(Var, 1, p[0], p[1], p[2]);
}

inline mc::FFVar
covar_matern_1(const mc::FFVar& Var)
{
    return mc::covariance_function(Var, 1);
}

inline mc::FFVar
covar_matern_3(const mc::FFVar& Var)
{
    return mc::covariance_function(Var, 2);
}

inline mc::FFVar
covar_matern_5(const mc::FFVar& Var)
{
    return mc::covariance_function(Var, 3);
}

inline mc::FFVar
covar_sqrexp(const mc::FFVar& Var)
{
    return mc::covariance_function(Var, 4);
}

inline mc::FFVar
af_lcb(const mc::FFVar& Var1, const mc::FFVar& Var2, const double kappa)
{
    return mc::acquisition_function(Var1, Var2, 1, kappa);
}

inline mc::FFVar
af_ei(const mc::FFVar& Var1, const mc::FFVar& Var2, const double fmin)
{
    return mc::acquisition_function(Var1, Var2, 2, fmin);
}

inline mc::FFVar
af_pi(const mc::FFVar& Var1, const mc::FFVar& Var2, const double fmin)
{
    return mc::acquisition_function(Var1, Var2, 3, fmin);
}

inline mc::FFVar
gpdf(const mc::FFVar& Var)
{
    return mc::gaussian_probability_density_function(Var);
}
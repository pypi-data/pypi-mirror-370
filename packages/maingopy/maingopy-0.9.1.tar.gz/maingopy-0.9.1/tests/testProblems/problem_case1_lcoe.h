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

#include "MAiNGOmodel.h"
#include "libraries/Ideal2pStream.h"
#include "libraries/IdealGasStream.h"
#include "libraries/IdealLiquidStream.h"
//Case Study I minimizing LCOE
//dobo Paper: Deterministic global optimization of process flowsheets in a reduced space using McCormick relaxations

using U = mc::FFVar;
using namespace maingo;


//////////////////////////////////////////////////////////////////////////
// Model class:
class Model_case1_lcoe: public MAiNGOmodel {
  public:
    Model_case1_lcoe();
    EvaluationContainer evaluate(const std::vector<U>& x);
    std::vector<OptimizationVariable> get_variables();
    std::vector<double> get_initial_point();

  private:
    // Specify constant Model parameters here:
    const double p0, vif, etap, etat, deltahv, cpig, cif, R, A, B, C, Tmax, mcp, TGin, TGout, deltaTap, xmin, p1, kEco, kEvap, kSH, kCond, k1A, k2A, k3A, c1A, c2A, c3A, FmA, B1A, B2A, Tcin, Tcout;
    const double Inv_GT, Work_GT, Fuel_heat, Fuel_cost, f_phi, f_annu, Teq, Varcost;
    double T0;
    U zero, Amin, eps, deltaTmin;
    // Declare Model variables here if desired:
    IdealLiquidStream S1, S2, S3;
    IdealGasStream S4, S5;
    Ideal2pStream S6, S6s;
};


//////////////////////////////////////////////////////////////////////////
// free function for providing initialization data to the Branch-and-Bound solver
std::vector<OptimizationVariable>
Model_case1_lcoe::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(3, 100), "p2"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(5, 100), "mdot"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_case1_lcoe::get_initial_point()
{

    //here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    //initialPoint.push_back(3);
    //initialPoint.push_back(-3);

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// Constructor for the Model
Model_case1_lcoe::Model_case1_lcoe():
    p0(10e-3), vif(1e-3), etap(0.8), etat(0.9), deltahv(2480), cpig(2.08), cif(4.18), R(0.462), A(3.55959), B(643.748), C(-198.043), Tmax(873), mcp(200), TGin(900), TGout(448), deltaTmin(15), deltaTap(10), xmin(0.85), p1(0.2),
    kEco(0.06), kEvap(0.06), kSH(0.03), kCond(0.35), k1A(4.3247), k2A(-0.303), k3A(0.1634), c1A(0.03881), c2A(-0.11272), c3A(0.08183), FmA(2.75), B1A(1.63), B2A(1.66), Tcin(298), Tcout(303),
    Inv_GT(22.7176e6), Work_GT(69676), Fuel_heat(182359), Fuel_cost(14), f_phi(1.06), f_annu(0.1875), Teq(4000), Varcost(4), Amin(10), eps(1e-16), zero(0)
{
    // Initialize data if necessary:
    T0 = B / (A - log(p0) / log(10.0)) - C;
    IdealFluid water(cpig, cif, R, vif, A, B, C, deltahv, deltahv / T0);
    S1  = IdealLiquidStream(water, p0, T0);
    S2  = IdealLiquidStream(water, p0, T0);
    S3  = IdealLiquidStream(water, p0, T0);
    S4  = IdealGasStream(water, p0, T0);
    S5  = IdealGasStream(water, p0, T0);
    S6  = Ideal2pStream(water, p0, T0);
    S6s = Ideal2pStream(water, p0, T0);
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the Model
maingo::EvaluationContainer
Model_case1_lcoe::evaluate(const std::vector<U>& currentPoint)
{    // <-- Specify Model equations
    // Rename inputs
    U p2   = currentPoint[0];
    U mdot = currentPoint[1];

    // Model
    // Condenser outlet
    S1.set_px(p1);
    // Feedwater Pump
    U wp        = vif * (p2 - p1) * 100 / etap;
    U Work_Pump = mdot * wp;
    Work_Pump   = max(eps, Work_Pump);
    S2.set_ph(p2, (S1.get_h() + wp));
    // Boiler
    // Overall balance
    U Qzu = mcp * (TGin - TGout);
    S5.set_ph(p2, (S2.get_h() + Qzu / mdot));
    // Superheater
    S4.set_px(p2);
    U Q_SH = mdot * (S5.get_h() - S4.get_h());
    U TG2  = TGin - Q_SH / mcp;
    // Evaporator
    S3.set_pT(p2, (S2.get_Ts() - deltaTap));
    U Q_Eco  = mdot * (S3.get_h() - S2.get_h());
    U TG3    = TGout + Q_Eco / mcp;
    U Q_Evap = Qzu - Q_SH - Q_Eco;
    // Turbine
    S6s.set_ps(p1, S5.get_s());
    U wt        = etat * (S5.get_h() - S6s.get_h());
    U Work_Turb = mdot * wt;
    Work_Turb   = max(eps, Work_Turb);
    S6.set_ph(p1, (S5.get_h() - wt));
    U Work_net = Work_Turb - Work_Pump;
    Work_net   = max(eps, Work_net);
    U eta_ST   = Work_net / Qzu;
    // Condenser
    U Q_Cond = mdot * (S6.get_h() - S1.get_h());

    // Investment cost
    // Condenser
    U dT1 = S6.get_T() - Tcout;
    U dT2 = S1.get_T() - Tcin;
    dT1   = max(deltaTmin, dT1) + zero * mdot;
    dT2   = max(deltaTmin, dT2) + zero * mdot;
    //U LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
    U LMTD     = lmtd(dT1, dT2);
    U A_Cond   = Q_Cond / (kCond * LMTD);
    A_Cond     = max(0.9 * Amin, A_Cond) + zero * mdot;
    U Cp0      = pow(10., k1A + k2A * log(A_Cond) / log(10.0) + k3A * pow(log(A_Cond) / log(10.0), 2));
    U Fp       = 1.0;
    U Inv_Cond = 1.18 * (B1A + B2A * FmA * Fp) * Cp0;
    // Pump
    U Inv_Pump = 3540 * pow(Work_Pump, 0.71);
    // Turbine incl. generator
    U Inv_Turb = 6000 * pow(Work_Turb, 0.7) + 60 * pow(Work_Turb, 0.95);
    // Economizer
    dT1 = TGout - S2.get_T();
    dT2 = TG3 - S3.get_T();
    dT1 = max(deltaTmin, dT1) + zero * mdot;
    dT2 = max(deltaTmin, dT2) + zero * mdot;
    //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
    LMTD      = lmtd(dT1, dT2);
    U A_Eco   = Q_Eco / (kEco * LMTD);
    A_Eco     = max(0.9 * Amin, A_Eco) + zero * mdot;
    Cp0       = pow(10., k1A + k2A * log(A_Eco) / log(10.0) + k3A * pow(log(A_Eco) / log(10.0), 2));
    Fp        = pow(10., c1A + c2A * log(p2) / log(10.0) + c3A * pow(log(p2) / log(10.0), 2));
    U Inv_Eco = 1.18 * (B1A + B2A * FmA * Fp) * Cp0;
    // Evaporator
    dT1 = TG3 - S4.get_T();
    dT2 = TG2 - S4.get_T();
    dT1 = max(deltaTmin, dT1) + zero * mdot;
    dT2 = max(deltaTmin, dT2) + zero * mdot;
    //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
    LMTD       = lmtd(dT1, dT2);
    U A_Evap   = Q_Evap / (kEvap * LMTD);
    A_Evap     = max(0.9 * Amin, A_Evap) + zero * mdot;
    Cp0        = pow(10., k1A + k2A * log(A_Evap) / log(10.0) + k3A * pow(log(A_Evap) / log(10.0), 2));
    U Inv_Evap = 1.18 * (B1A + B2A * FmA * Fp) * Cp0;
    // Superheater
    dT1 = dT2;
    dT2 = TGin - S5.get_T();
    dT1 = max(deltaTmin, dT1) + zero * mdot;
    dT2 = max(deltaTmin, dT2) + zero * mdot;
    //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
    LMTD     = lmtd(dT1, dT2);
    U A_SH   = Q_SH / (kSH * LMTD);
    A_SH     = max(0.9 * Amin, A_SH) + zero * mdot;
    Cp0      = pow(10., k1A + k2A * log(A_SH) / log(10.0) + k3A * pow(log(A_SH) / log(10.0), 2));
    U Inv_SH = 1.18 * (B1A + B2A * FmA * Fp) * Cp0;
    // Cycle
    U Inv = Inv_Cond + Inv_Pump + Inv_Eco + Inv_Evap + Inv_SH + Inv_Turb;

    // Combined Cycle Plant
    U Work_Total = Work_net + Work_GT;
    U eta_CC     = Work_Total / Fuel_heat;
    U Inv_Total  = Inv + Inv_GT;
    U CAPEX      = Inv_Total * f_phi * f_annu / (Work_Total / 1000 * Teq);
    U OPEX       = Fuel_cost / eta_CC;
    U LCOE       = CAPEX + OPEX + Varcost;


    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective:
#ifndef HAVE_GROWING_DATASETS
    result.objective = LCOE;
#else
    result.objective_per_data.push_back(LCOE);
#endif
    // Inequalities (<=0):
    result.ineq.push_back((S5.get_T() - Tmax) / 100);
    result.ineq.push_back((S4.get_Ts() + deltaTmin - TG3) / 100);
    result.ineq.push_back((S5.get_hSatVap() - S5.get_h()) / 1000);
    result.ineq.push_back(xmin - S6.get_x());
    result.ineq.push_back(S6.get_x() - 1.0);
    result.ineq.push_back((Amin - A_Cond) / 10);
    result.ineq.push_back((Amin - A_Eco) / 10);
    result.ineq.push_back((Amin - A_Evap) / 10);
    result.ineq.push_back((Amin - A_SH) / 10);
    // Equalities (=0):
    // Additional Output:


    return result;
}

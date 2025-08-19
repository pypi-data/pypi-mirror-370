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

using U = mc::FFVar;

//////////////////////////////////////////////////////////////////////////
// Model class:
class Model_case2_lcoe: public maingo::MAiNGOmodel {
  public:
    Model_case2_lcoe();
    EvaluationContainer evaluate(const std::vector<U>& currentPoint);
    std::vector<maingo::OptimizationVariable> get_variables();
    std::vector<double> get_initial_point();

  private:
    // Specify constant Model parameters here:
    const double p0, vif, etap, etat, deltahv, cpig, cif, R, A, B, C, Tmax, mcp, TGin, TGout, deltaTap, xmin, p1, kEco, kEvap, kSH, kCond, k1A, k2A, k3A, c1A, c2A, c3A, FmA, B1A, B2A, k1B, k2B, k3B, FmB, B1B, B2B, Tcin, Tcout;
    const double Inv_GT, Work_GT, Fuel_heat, Fuel_cost, f_phi, f_annu, Teq, Varcost, Vmin;
    double T0;
    U eps, zero, Amin, deltaTmin;
    // Declare Model variables here if desired:
    IdealFluid water;
    IdealLiquidStream S1, S2, S3, S4, S5;
    IdealGasStream S6, S7;
    Ideal2pStream S8, S8s, S9, S9s;
};

//////////////////////////////////////////////////////////////////////////
// Free function for providing initialization data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_case2_lcoe::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.2, 5), "p2"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(3, 100), "p4"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(5, 100), "mdot"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(2480, 3750), "h7"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.01, 0.2), "k"));

    return variables;
}

//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_case2_lcoe::get_initial_point()
{

    //here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    //initialPoint.push_back(3);
    //initialPoint.push_back(-3);

    return initialPoint;
}

//////////////////////////////////////////////////////////////////////////
// Constructor for the Model
Model_case2_lcoe::Model_case2_lcoe():
    p0(10e-3), vif(1e-3), etap(0.8), etat(0.9), deltahv(2480), cpig(2.08), cif(4.18), R(0.462), A(3.55959), B(643.748), C(-198.043), Tmax(873), mcp(200),
    TGin(900), TGout(423), deltaTmin(15), deltaTap(10), xmin(0.85), p1(0.05), eps(1e-12), zero(0), kEco(0.06), kEvap(0.06), kSH(0.03), kCond(0.35),
    k1A(4.3247), k2A(-0.303), k3A(0.1634), c1A(0.03881), c2A(-0.11272), c3A(0.08183), FmA(2.75), B1A(1.63), B2A(1.66), k1B(3.5565), k2B(0.3776), k3B(0.0905),
    FmB(1), B1B(1.49), B2B(1.52), Tcin(298), Tcout(303), Inv_GT(22.7176e6), Work_GT(69676), Fuel_heat(182359), Fuel_cost(14), f_phi(1.06), f_annu(0.1875),
    Teq(4000), Varcost(4), Amin(10), Vmin(1)
{
    // Initialize data if necessary:
    T0    = B / (A - log(p0) / log(10.0)) - C;
    water = IdealFluid(cpig, cif, R, vif, A, B, C, deltahv, deltahv / T0);
    S1    = IdealLiquidStream(water, p0, T0);
    S2    = IdealLiquidStream(water, p0, T0);
    S3    = IdealLiquidStream(water, p0, T0);
    S4    = IdealLiquidStream(water, p0, T0);
    S5    = IdealLiquidStream(water, p0, T0);
    S6    = IdealGasStream(water, p0, T0);
    S7    = IdealGasStream(water, p0, T0);
    S8    = Ideal2pStream(water, p0, T0);
    S8s   = Ideal2pStream(water, p0, T0);
    S9    = Ideal2pStream(water, p0, T0);
    S9s   = Ideal2pStream(water, p0, T0);
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the Model
maingo::EvaluationContainer
Model_case2_lcoe::evaluate(const std::vector<U>& currentPoint)
{
    // Rename inputs
    U p2   = currentPoint[0];
    U p4   = currentPoint[1];
    U mdot = currentPoint[2];
    U h7   = currentPoint[3];
    U k    = currentPoint[4];


    // Model
    // Turbines:
    // Inlet:
    S7.set_ph(p4, h7);
    // Turbine 1 (bleed):
    S8s.set_ps(p2, S7.get_s());
    U wt8 = etat * (S7.get_h() - S8s.get_h());
    S8.set_ph(p2, (S7.get_h() - wt8));
    // Turbine 2 (main):
    S9s.set_ps(p1, S7.get_s());
    U wt9 = etat * (S7.get_h() - S9s.get_h());
    S9.set_ph(p1, (S7.get_h() - wt9));
    // Feedwater line
    // Condensate pump
    S1.set_px(p1);
    U wp1 = vif * (p2 - p1) * 100 / etap;
    S2.set_ph(p2, (S1.get_h() + wp1));
    // Deaerator
    S3.set_ph(p2, (k * S8.get_h() + (1 - k) * S2.get_h()));
    // Feedwater pump
    U wp2 = vif * (p4 - p2) * 100 / etap;
    S4.set_ph(p4, (S3.get_h() + wp2));
    // Boiler
    // Superheater
    S6.set_px(p4);
    U Q_SH = mdot * (S7.get_h() - S6.get_h());
    Q_SH   = max(eps, Q_SH);
    U TG2  = TGin - Q_SH / mcp;
    // Evaporator
    S5.set_pT(p4, S4.get_Ts() - deltaTap);
    U Q_Evap = mdot * (S6.get_h() - S5.get_h());
    Q_Evap   = max(eps, Q_Evap);
    U TG3    = TG2 - Q_Evap / mcp;
    // Eco
    U Q_Eco = mdot * (S5.get_h() - S4.get_h());
    Q_Eco   = max(eps, Q_Eco);
    U TGout = TG3 - Q_Eco / mcp;
    // Condenser
    U Q_Cond = mdot * (1 - k) * (S9.get_h() - S1.get_h());

    U Work_Pump1 = mdot * (1 - k) * wp1;
    Work_Pump1   = max(eps, Work_Pump1);
    U Work_Pump2 = mdot * wp2;
    Work_Pump2   = max(eps, Work_Pump2);
    U Work_Turb8 = mdot * k * wt8;
    Work_Turb8   = max(eps, Work_Turb8);
    U Work_Turb9 = mdot * (1 - k) * wt9;
    Work_Turb9   = max(eps, Work_Turb9);
    U Work_net   = Work_Turb8 + Work_Turb9 - Work_Pump1 - Work_Pump2;
    Work_net     = max(eps, Work_net);
    U Qzu        = Q_Eco + Q_Evap + Q_SH;
    U eta        = Work_net / Qzu;


    // Investment cost
    // Condenser
    U dT1 = S9.get_T() - Tcout;
    U dT2 = S1.get_T() - Tcin;
    dT1   = max(deltaTmin, dT1) + zero * mdot;
    dT2   = max(deltaTmin, dT2) + zero * mdot;
    //U LMTDa = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
    U LMTDa  = lmtd(dT1, dT2);
    U A_Cond = Q_Cond / (kCond * LMTDa);
    //U RLMTDa = rlmtd(dT1,dT2);
    //U A_Cond = Q_Cond / kCond * RLMTDa;
    A_Cond = max(0.9 * Amin, A_Cond);
    // U Cp0a = pow(10.,k1A+k2A*log(A_Cond)/log(10.0)+k3A*pow(log(A_Cond)/log(10.0),2));
    //U Cp0a = pow(10.,k1A+log(A_Cond)/log(10.0)*(k2A+k3A*log(A_Cond)/log(10.0)));
    U Cp0a     = cost_function(A_Cond, 1, k1A, k2A, k3A);
    U Fpa      = 1.0;
    U Inv_Cond = 1.18 * (B1A + B2A * FmA * Fpa) * Cp0a;
    // Pumps
    U Inv_Pump1 = 3540 * pow(Work_Pump1, 0.71);
    U Inv_Pump2 = 3540 * pow(Work_Pump2, 0.71);
    // Turbines incl. generator
    U Inv_Turb = 6000 * pow(Work_Turb8 + Work_Turb9, 0.7);
    U Inv_Gen  = 60 * pow(Work_Turb8 + Work_Turb9, 0.95);
    // Economizer
    dT1 = TGout - S4.get_T();
    dT2 = TG3 - S5.get_T();
    dT1 = max(deltaTmin, dT1);
    dT2 = max(deltaTmin, dT2);
    //U LMTDb = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
    U LMTDb = lmtd(dT1, dT2);
    U A_Eco = Q_Eco / (kEco * LMTDb);
    //U RLMTDb = rlmtd(dT1,dT2);
    //U A_Eco = Q_Eco / kEco * RLMTDb;
    A_Eco = max(0.9 * Amin, A_Eco) + zero * mdot;
    // U Cp0b = pow(10.,k1A+k2A*log(A_Eco)/log(10.0)+k3A*pow(log(A_Eco)/log(10.0),2));
    //U Cp0b = pow(10.,k1A+log(A_Eco)/log(10.0)*(k2A+k3A*log(A_Eco)/log(10.0)));
    U Cp0b = cost_function(A_Eco, 1, k1A, k2A, k3A);
    // U Fpb = pow(10.,c1A+c2A*log(p4)/log(10.0)+c3A*pow(log(p4)/log(10.0),2));
    // U Fpb = pow(10.,c1A+log(p4)/log(10.0)*(c2A+c3A*log(p4)/log(10.0)));
    U Fpb     = cost_function(p4, 1, c1A, c2A, c3A);
    U Inv_Eco = 1.18 * (B1A + B2A * FmA * Fpb) * Cp0b;
    // Evaporator
    dT1 = TG3 - S6.get_T();
    dT2 = TG2 - S6.get_T();
    dT1 = max(deltaTmin, dT1) + zero * mdot;
    dT2 = max(deltaTmin, dT2) + zero * mdot;
    //U LMTDc = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
    U LMTDc  = lmtd(dT1, dT2);
    U A_Evap = Q_Evap / (kEvap * LMTDc);
    //U RLMTDc = rlmtd(dT1,dT2);
    //U A_Evap = Q_Evap / kEvap * RLMTDc;
    A_Evap = max(0.9 * Amin, A_Evap);
    // U Cp0c = pow(10.,k1A+k2A*log(A_Evap)/log(10.0)+k3A*pow(log(A_Evap)/log(10.0),2));
    //U Cp0c = pow(10.,k1A+log(A_Evap)/log(10.0)*(k2A+k3A*log(A_Evap)/log(10.0)));
    U Cp0c     = cost_function(A_Evap, 1, k1A, k2A, k3A);
    U Inv_Evap = 1.18 * (B1A + B2A * FmA * Fpb) * Cp0c;
    // Superheater
    dT1 = dT2;
    dT2 = TGin - S7.get_T();
    dT1 = max(deltaTmin, dT1) + zero * mdot;
    dT2 = max(deltaTmin, dT2) + zero * mdot;
    //U LMTDd = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
    U LMTDd = lmtd(dT1, dT2);
    U A_SH  = Q_SH / (kSH * LMTDd);
    //U RLMTDd = rlmtd(dT1,dT2);
    //U A_SH = Q_SH / kSH * RLMTDd;
    A_SH = max(0.9 * Amin, A_SH) + zero * mdot;
    // U Cp0d = pow(10.,k1A+k2A*log(A_SH)/log(10.0)+k3A*pow(log(A_SH)/log(10.0),2));
    //U Cp0d = pow(10.,k1A+log(A_SH)/log(10.0)*(k2A+k3A*log(A_SH)/log(10.0)));
    U Cp0d   = cost_function(A_SH, 1, k1A, k2A, k3A);
    U Inv_SH = 1.18 * (B1A + B2A * FmA * Fpb) * Cp0d;
    // Deaerator
    U V_Dae = 1.5 * 600 * mdot * vif;
    // U Cp0DAE = pow(10.,k1B+k2B*log(V_Dae)/log(10.0)+k3B*pow(log(V_Dae)/log(10.0),2));
    //U Cp0DAE = pow(10.,k1B+log(V_Dae)/log(10.0)*(k2B+k3B*log(V_Dae)/log(10.0)));
    U Cp0DAE  = cost_function(V_Dae, 1, k1B, k2B, k3B);
    U FpDAE   = 1.25;
    U Inv_Dae = 1.18 * (B1B + B2B * FmB * FpDAE) * Cp0DAE;
    // Cycle
    U Inv = Inv_Cond + Inv_Pump1 + Inv_Dae + Inv_Pump2 + Inv_Eco + Inv_Evap + Inv_SH + Inv_Turb + Inv_Gen;

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
#endif    // HAVE_GROWING_DATASETS
    // Inequalities (<=0):
    result.ineq.push_back((S7.get_hSatVap() - S7.get_h()) / 1000);
    result.ineq.push_back((S5.get_Ts() + deltaTmin - TG3) / 100);
    result.ineq.push_back((S4.get_T() + deltaTmin - TGout) / 100);
    result.ineq.push_back((S7.get_T() - Tmax) / 100);
    result.ineq.push_back(xmin - S9.get_x());
    result.ineq.push_back(S8.get_x() - 1);
    result.ineq.push_back((p2 - p4) / 100);

    result.ineq.push_back((Amin - A_Cond) / 10);
    result.ineq.push_back((Amin - A_Eco) / 10);
    result.ineq.push_back((Amin - A_Evap) / 10);
    result.ineq.push_back((Amin - A_SH) / 10);
    result.ineq.push_back(Vmin - V_Dae);
    // Equalities
    result.eq.push_back((S3.get_h() - S3.get_hSatLiq()) / 100);

    // Additional Output:
    result.output.push_back(OutputVariable("x9", S9.get_x()));


    return result;
}

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
class Model_case3_wnet: public maingo::MAiNGOmodel {
  public:
    Model_case3_wnet();
    EvaluationContainer evaluate(const std::vector<U>& currentPoint);
    std::vector<maingo::OptimizationVariable> get_variables();
    std::vector<double> get_initial_point();

  private:
    // Specify constant Model parameters here:
    const double p0, vif, etap, etat, deltahv, cpig, cif, R, A, B, C, Tmax, mcp, TGin, deltaTap, xmin, p1, kEco, kEvap, kSH, kCond, k1A, k2A, k3A, c1A, c2A, c3A, FmA, B1A, B2A, k1B, k2B, k3B, FmB, B1B, B2B, Tcin, Tcout;
    const double Inv_GT, Work_GT, Fuel_heat, Fuel_cost, f_phi, f_annu, Teq, Varcost, Vmin;
    double T0;
    U eps, zero, Amin, deltaTmin;
    // Declare Model variables here if desired:
    IdealLiquidStream S1, S2, S3, S4, S5, S8, S9;
    IdealGasStream S6, S7, S10, S11, S12, S12s, S13;
    Ideal2pStream S14, S14s, S15, S15s;
};

//////////////////////////////////////////////////////////////////////////
// Free function for providing initialization data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_case3_wnet::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.2, 3), "p2"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(3, 15), "p4"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(10, 100), "p8"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(5, 100), "mdot"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(2480, 3750), "h7"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(2480, 3750), "h11"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.05, 0.5), "kLP"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.01, 0.2), "kBl"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_case3_wnet::get_initial_point()
{

    //here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    //initialPoint.push_back(3);
    //initialPoint.push_back(-3);

    return initialPoint;
}

//////////////////////////////////////////////////////////////////////////
// Constructor for the Model
Model_case3_wnet::Model_case3_wnet():
    p0(10e-3), vif(1e-3), etap(0.8), etat(0.9), deltahv(2480), cpig(2.08), cif(4.18), R(0.462), A(3.55959), B(643.748), C(-198.043), Tmax(873), mcp(200), TGin(900), deltaTmin(15), deltaTap(10), xmin(0.85), p1(0.05), eps(1e-16), zero(0),
    kEco(0.06), kEvap(0.06), kSH(0.03), kCond(0.35), k1A(4.3247), k2A(-0.303), k3A(0.1634), c1A(0.03881), c2A(-0.11272), c3A(0.08183), FmA(2.75), B1A(1.63), B2A(1.66), k1B(3.5565), k2B(0.3776), k3B(0.0905), FmB(1), B1B(1.49), B2B(1.52), Tcin(298), Tcout(303),
    Inv_GT(22.7176e6), Work_GT(69676), Fuel_heat(182359), Fuel_cost(14), f_phi(1.06), f_annu(0.1875), Teq(4000), Varcost(4), Amin(10), Vmin(1)
{
    // Initialize data if necessary:
    T0 = B / (A - log(p0) / log(10.0)) - C;
    IdealFluid water(cpig, cif, R, vif, A, B, C, deltahv, deltahv / T0);
    S1   = IdealLiquidStream(water, p0, T0);
    S2   = IdealLiquidStream(water, p0, T0);
    S3   = IdealLiquidStream(water, p0, T0);
    S4   = IdealLiquidStream(water, p0, T0);
    S5   = IdealLiquidStream(water, p0, T0);
    S8   = IdealLiquidStream(water, p0, T0);
    S9   = IdealLiquidStream(water, p0, T0);
    S6   = IdealGasStream(water, p0, T0);
    S7   = IdealGasStream(water, p0, T0);
    S10  = IdealGasStream(water, p0, T0);
    S11  = IdealGasStream(water, p0, T0);
    S12  = IdealGasStream(water, p0, T0);
    S12s = IdealGasStream(water, p0, T0);
    S13  = IdealGasStream(water, p0, T0);
    S14  = Ideal2pStream(water, p0, T0);
    S14s = Ideal2pStream(water, p0, T0);
    S15  = Ideal2pStream(water, p0, T0);
    S15s = Ideal2pStream(water, p0, T0);
    // <-- Reserve memory for required number of constraints:
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the Model
maingo::EvaluationContainer
Model_case3_wnet::evaluate(const std::vector<U>& currentPoint)
{    // <-- Specify Model equations
     // Rename inputs
    U p2   = currentPoint[0];
    U p4   = currentPoint[1];
    U p8   = currentPoint[2];
    U mdot = currentPoint[3];
    U h7   = currentPoint[4];
    U h11  = currentPoint[5];
    U kLP  = currentPoint[6];
    U kBl  = currentPoint[7];


    // Model
    U mLP    = mdot * kLP;
    U mHP    = mdot * (1 - kLP);
    U mBleed = mdot * kBl;
    U mMain  = mdot * (1 - kBl);
    // HP Turbine
    S11.set_ph(p8, h11);
    S12s.set_ps(p4, S11.get_s());
    U wt12        = etat * (S11.get_h() - S12s.get_h());
    U Work_Turb12 = mHP * wt12;
    Work_Turb12   = max(Work_Turb12, eps);
    S12.set_ph(p4, (S11.get_h() - wt12));
    // LP Turbine
    //Inlet
    S7.set_ph(p4, h7);
    S13.set_ph(p4, (kLP * S7.get_h() + (1 - kLP) * S12.get_h()));
    // Bleed
    S14s.set_ps(p2, S13.get_s());
    U wt14        = etat * (S13.get_h() - S14s.get_h());
    U Work_Turb14 = mBleed * wt14;
    Work_Turb14   = max(Work_Turb14, eps);
    S14.set_ph(p2, (S13.get_h() - wt14));
    // Main
    S15s.set_ps(p1, S13.get_s());
    U wt15        = etat * (S13.get_h() - S15s.get_h());
    U Work_Turb15 = mMain * wt15;
    Work_Turb15   = max(Work_Turb15, eps);
    S15.set_ph(p1, (S13.get_h() - wt15));
    // Feedwater line
    // Condenser
    S1.set_px(p1);
    U Q_Cond = mMain * (S15.get_h() - S1.get_h());
    // Condensate pump
    U wp2        = vif * (p2 - p1) * 100 / etap;
    U Work_Pump2 = mMain * wp2;
    S2.set_ph(p2, (S1.get_h() + wp2));
    // Deaerator
    S3.set_ph(p2, (kBl * S14.get_h() + (1 - kBl) * S2.get_h()));
    // LP pump
    U wp4        = vif * (p4 - p2) * 100 / etap;
    U Work_Pump4 = mdot * wp4;
    Work_Pump4   = max(Work_Pump4, eps);
    S4.set_ph(p4, (S3.get_h() + wp4));
    // HP pump
    S5.set_pT(p4, (S4.get_Ts() - deltaTap));
    U wp8        = vif * (p8 - p4) * 100 / etap;
    U Work_Pump8 = mHP * wp8;
    Work_Pump8   = max(Work_Pump8, eps);
    S8.set_ph(p8, (S5.get_h() + wp8));
    // Boiler
    // HP Superheater
    S10.set_px(p8);
    U Q_HPSH = mHP * (S11.get_h() - S10.get_h());
    Q_HPSH   = max(Q_HPSH, eps);
    U TG2    = TGin - Q_HPSH / mcp;
    // HP Evaporator
    S9.set_pT(p8, S10.get_Ts() - deltaTap);
    U Q_HPEV = mHP * (S10.get_h() - S9.get_h());
    Q_HPEV   = max(Q_HPEV, eps);
    U TG3    = TG2 - Q_HPEV / mcp;
    // LP Superheater
    S6.set_px(p4);
    U Q_LPSH = mLP * (S7.get_h() - S6.get_h());
    Q_LPSH   = max(Q_LPSH, eps);
    U TG4    = TG3 - Q_LPSH / mcp;
    // HP Eco
    U Q_HPEC = mHP * (S9.get_h() - S8.get_h());
    Q_HPEC   = max(Q_HPEC, eps);
    U TG5    = TG4 - Q_HPEC / mcp;
    // LP Evaporator
    U Q_LPEV = mLP * (S6.get_h() - S5.get_h());
    Q_LPEV   = max(Q_LPEV, eps);
    U TG6    = TG5 - Q_LPEV / mcp;
    // LP Eco
    U Q_LPEC = mdot * (S5.get_h() - S4.get_h());
    Q_LPEC   = max(Q_LPEC, eps);
    U TG7    = TG6 - Q_LPEC / mcp;

    U Work_net = Work_Turb12 + Work_Turb14 + Work_Turb15 - Work_Pump2 - Work_Pump4 - Work_Pump8;
    U Qzu      = Q_LPEC + Q_LPEV + Q_LPSH + Q_HPEC + Q_HPEV + Q_HPSH;
    U eta      = Work_net / Qzu;


    // Investment cost
    // Condenser
    /* U dT1 = S15.get_T()-Tcout;
        U dT2 = S1.get_T()-Tcin;
        dT1 = max(deltaTmin,dT1)+zero*mdot;
        dT2 = max(deltaTmin,dT2)+zero*mdot;
        //U LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
        //U LMTD = lmtd(dT1,dT2);
        //U A_Cond = Q_Cond / (kCond * LMTD);
        U RLMTD = rlmtd(dT1,dT2);
        U A_Cond = Q_Cond /kCond * RLMTD;
        A_Cond = max(0.9*Amin,A_Cond);
        // U Cp0 = pow(10,k1A+k2A*log(A_Cond)/log(10.0)+k3A*pow(log(A_Cond)/log(10.0),2));
        U Cp0 = cost_function(A_Cond,1,k1A,k2A,k3A);
        U Fp = 1.0;
        U Inv_Cond = 1.18 * (B1A+B2A*FmA*Fp) * Cp0;
        // Pumps
        U Inv_Pump2 = 3540*pow(Work_Pump2,0.71);
        U Inv_Pump4 = 3540*pow(Work_Pump4,0.71);
        U Inv_Pump8 = 3540*pow(Work_Pump8,0.71);
        // Turbines incl. generator
        U Inv_TurbLP = 6000*pow(Work_Turb14+Work_Turb15,0.7);
        U Inv_TurbHP = 6000*pow(Work_Turb12,0.7);
        U Inv_Gen = 60*pow(Work_Turb12+Work_Turb14+Work_Turb15,0.95);
        // LP-Economizer
        dT1 = TG7 - S4.get_T();
        dT2 = TG6 - S5.get_T();
        dT1 = max(deltaTmin,dT1)+zero*mdot;
        dT2 = max(deltaTmin,dT2)+zero*mdot;
        //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
        //LMTD = lmtd(dT1,dT2);
        //U A_LPEC = Q_LPEC / (kEco * LMTD);
        RLMTD = rlmtd(dT1,dT2);
        U A_LPEC = Q_LPEC /kEco * RLMTD;
        A_LPEC = max(0.9*Amin,A_LPEC);
        // Cp0 = pow(10,k1A+k2A*log(A_LPEC)/log(10.0)+k3A*pow(log(A_LPEC)/log(10.0),2));
        Cp0 = cost_function(A_LPEC,1,k1A,k2A,k3A);
        // Fp = pow(10,c1A+c2A*log(p4)/log(10.0)+c3A*pow(log(p4)/log(10.0),2));
        Fp = cost_function(p4,1,c1A,c2A,c3A);
        U Inv_LPEC = 1.18 * (B1A+B2A*FmA*Fp) * Cp0;
        // LP-Evaporator
        dT1 = TG6 - S6.get_Ts();
        dT2 = TG5 - S6.get_Ts();
        dT1 = max(deltaTmin,dT1)+zero*mdot;
        dT2 = max(deltaTmin,dT2)+zero*mdot;
        //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
        //LMTD = lmtd(dT1,dT2);
        //U A_LPEV = Q_LPEV / (kEvap * LMTD);
        RLMTD = rlmtd(dT1,dT2);
        U A_LPEV = Q_LPEV /kEvap * RLMTD;
        A_LPEV = max(0.9*Amin,A_LPEV);
        // Cp0 = pow(10,k1A+k2A*log(A_LPEV)/log(10.0)+k3A*pow(log(A_LPEV)/log(10.0),2));
        Cp0 = cost_function(A_LPEV,1,k1A,k2A,k3A);
        U Inv_LPEV = 1.18 * (B1A+B2A*FmA*Fp) * Cp0;
        // LP - Superheater
        dT1 = TG4 - S6.get_T();
        dT2 = TG3 - S7.get_T();
        dT1 = max(deltaTmin,dT1)+zero*mdot;
        dT2 = max(deltaTmin,dT2)+zero*mdot;
        //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
        //LMTD = lmtd(dT1,dT2);
        //U A_LPSH = Q_LPSH / (kSH * LMTD);
        RLMTD = rlmtd(dT1,dT2);
        U A_LPSH = Q_LPSH /kSH * RLMTD;
        A_LPSH = max(0.9*Amin,A_LPSH);
        // Cp0 = pow(10,k1A+k2A*log(A_LPSH)/log(10.0)+k3A*pow(log(A_LPSH)/log(10.0),2));
        Cp0 = cost_function(A_LPSH,1,k1A,k2A,k3A);
        U Inv_LPSH = 1.18 * (B1A+B2A*FmA*Fp) * Cp0;
        // HP-Economizer
        dT1 = TG5 - S8.get_T();
        dT2 = TG4 - S9.get_T();
        dT1 = max(deltaTmin,dT1)+zero*mdot;
        dT2 = max(deltaTmin,dT2)+zero*mdot;
        //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
        //LMTD = lmtd(dT1,dT2);
        //U A_HPEC = Q_HPEC / (kEco * LMTD);
        RLMTD = rlmtd(dT1,dT2);
        U A_HPEC = Q_HPEC /kEco * RLMTD;
        A_HPEC = max(0.9*Amin,A_HPEC);
        // Cp0 = pow(10,k1A+k2A*log(A_HPEC)/log(10.0)+k3A*pow(log(A_HPEC)/log(10.0),2));
        Cp0 = cost_function(A_HPEC,1,k1A,k2A,k3A);
        // Fp = pow(10,c1A+c2A*log(p8)/log(10.0)+c3A*pow(log(p8)/log(10.0),2));
        Fp = cost_function(p8,1,c1A,c2A,c3A);
        U Inv_HPEC = 1.18 * (B1A+B2A*FmA*Fp) * Cp0;
        // HP-Evaporator
        dT1 = TG3 - S10.get_Ts();
        dT2 = TG2 - S10.get_Ts();
        dT1 = max(deltaTmin,dT1)+zero*mdot;
        dT2 = max(deltaTmin,dT2)+zero*mdot;
        //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
        //LMTD = lmtd(dT1,dT2);
        //U A_HPEV = Q_HPEV / (kEvap * LMTD);
        RLMTD = rlmtd(dT1,dT2);
        U A_HPEV = Q_HPEV /kEvap * RLMTD;
        A_HPEV = max(0.9*Amin,A_HPEV);
        // Cp0 = pow(10,k1A+k2A*log(A_HPEV)/log(10.0)+k3A*pow(log(A_HPEV)/log(10.0),2));
        Cp0 = cost_function(A_HPEV,1,k1A,k2A,k3A);
        U Inv_HPEV = 1.18 * (B1A+B2A*FmA*Fp) * Cp0;
        // HP - Superheater
        dT1 = TG2 - S10.get_T();
        dT2 = TGin - S11.get_T();
        dT1 = max(deltaTmin,dT1)+zero*mdot;
        dT2 = max(deltaTmin,dT2)+zero*mdot;
        //LMTD = pow(dT1*dT2*(dT1+dT2)/2,0.33333333333333);
        //LMTD = lmtd(dT1,dT2);
        //U A_HPSH = Q_HPSH / (kSH * LMTD);
        RLMTD = rlmtd(dT1,dT2);
        U A_HPSH = Q_HPSH / kSH * RLMTD;
        A_HPSH = max(0.9*Amin,A_HPSH);
        // Cp0 = pow(10,k1A+k2A*log(A_HPSH)/log(10.0)+k3A*pow(log(A_HPSH)/log(10.0),2));
        Cp0 = cost_function(A_HPSH,1,k1A,k2A,k3A);
        U Inv_HPSH = 1.18 * (B1A+B2A*FmA*Fp) * Cp0;
        // Deaerator
        U V_Dae = 1.5 * 600 * mdot * vif;
        // Cp0 = pow(10,k1B+k2B*log(V_Dae)/log(10.0)+k3B*pow(log(V_Dae)/log(10.0),2));
        Cp0 = cost_function(V_Dae,1,k1B,k2B,k3B);
        Fp = 1.25;
        U Inv_Dae = 1.18 * (B1B+B2B*FmB*Fp) * Cp0;
        // Cycle
        U Inv = Inv_Cond + Inv_Pump2 + Inv_Dae + Inv_Pump4 + Inv_LPEC + Inv_LPEV + Inv_LPSH + Inv_Pump8 + Inv_HPEC + Inv_HPEV + Inv_HPSH + Inv_TurbLP + Inv_TurbHP + Inv_Gen;

        // Combined Cycle Plant
        U Work_Total = Work_net + Work_GT;
        U eta_CC = Work_Total / Fuel_heat;
        U Inv_Total = Inv + Inv_GT;
        U CAPEX = Inv_Total*f_phi*f_annu/(Work_Total/1000*Teq);
        U OPEX = Fuel_cost/eta_CC;
        U LCOE = CAPEX + OPEX  + Varcost; */

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */

    // Objective:
#ifndef HAVE_GROWING_DATASETS
    // result.objective = LCOE;
    result.objective = -Work_net;
#else
    result.objective_per_data.push_back(-Work_net);
#endif
    // Inequalities (<=0):
    result.ineq.push_back(((S7.get_hSatVap() - S7.get_h()) / 1000));
    result.ineq.push_back(((S11.get_hSatVap() - S11.get_h()) / 1000));
    result.ineq.push_back(((S7.get_T() - Tmax) / 100));
    result.ineq.push_back(((S11.get_T() - Tmax) / 100));
    result.ineq.push_back((xmin - S15.get_x()));
    result.ineq.push_back((S14.get_x() - 1.0));
    result.ineq.push_back(((S12s.get_hSatVap() - S12s.get_h()) / 1000));
    result.ineq.push_back(((S10.get_Ts() + deltaTmin - TG3) / 100));
    result.ineq.push_back(((S7.get_T() + deltaTmin - TG3) / 100));
    result.ineq.push_back(((S9.get_T() + deltaTmin - TG4) / 100));
    result.ineq.push_back(((S6.get_Ts() + deltaTmin - TG6) / 100));
    result.ineq.push_back(((S4.get_T() + deltaTmin - TG7) / 100));
    result.ineq.push_back(((p2 - p4) / 100));
    result.ineq.push_back(((p4 - p8) / 100));

    // result.ineq[14] = ((Amin-A_LPEC)/10);
    // result.ineq[15] = ((Amin-A_LPEV)/10);
    // result.ineq[16] = ((Amin-A_LPSH)/10);
    // result.ineq[17] = ((Amin-A_HPEC)/10);
    // result.ineq[18] = ((Amin-A_HPEV)/10);
    // result.ineq[19] = ((Amin-A_HPSH)/10);
    // result.ineq[20] = ((Amin-A_Cond)/10);
    // result.ineq[21] = (Vmin-V_Dae);
    // Equalities
    result.eq.push_back(((S3.get_h() - S3.get_hSatLiq()) / 100));
    // Additional Output:

    return result;
}

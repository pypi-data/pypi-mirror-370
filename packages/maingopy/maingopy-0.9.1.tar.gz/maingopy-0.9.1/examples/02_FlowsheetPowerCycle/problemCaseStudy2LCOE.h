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
#include "Thermo/IdealFluidModel.h"
#include "Thermo/IdealFluidProperties.h"

#include <memory>


/**
* @class Model
* @brief Class defining the actual model
*/
class Model: public maingo::MAiNGOmodel {

  public:
    /**
        * @brief Default constructor
        */
    Model();

    /**
        * @brief Main function used to evaluate the model and construct a directed acyclic graph
        *
        * @param[in] optVars is the optimization variables vector
        */
    maingo::EvaluationContainer evaluate(const std::vector<Var>& optVars);

    /**
        * @brief Function for getting optimization variables data
        */
    std::vector<maingo::OptimizationVariable> get_variables();

    /**
        * @brief Function for getting initial point data
        */
    std::vector<double> get_initial_point();

  private:
    /**
       * @name Constant model parameters initialized by the default constructor
       */
    /**@{*/
    const double eta_p, eta_t, mcpG, TGin, TGout, Tmax, dTap, dTmin, xmin, Amin, Vmin;
    const double kEco, kEvap, kSH, kCond, k1A, k2A, k3A, c1A, c2A, c3A, FmA, B1A, B2A, k1B, k2B, k3B, FmB, B1B, B2B, Tcin, Tcout;
    const double InvGT, WorkGT, FuelHeat, FuelPrice, fPhi, fAnnu, Teq, Varcost;
    /**@}*/

    /**
       * @name Thermodynamic model (implemented in the IdealFluidModel specialization of the ThermoModel class)
       */
    /**@{*/
    const thermo::IdealFluidModel thermoModel;
    /**@}*/
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Variable type is continuous per default
    // Branching priority is set to 1 per default
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(0.2, 5), /*Variable name*/ "p2"));
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(3, 100), /*Variable name*/ "p4"));
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(5, 100), /*Variable name*/ "mdot"));
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(2480, 3750), /*Variable name*/ "h7"));
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(0.01, 0.2), /*Variable name*/ "k"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model::Model():
    eta_p(0.8), eta_t(0.9), mcpG(200), TGin(900), TGout(448), Tmax(873.15), dTap(10), dTmin(15), xmin(0.85), Amin(10), Vmin(1),
    kEco(0.06), kEvap(0.06), kSH(0.03), kCond(0.35), k1A(4.3247), k2A(-0.303), k3A(0.1634),
    c1A(0.03881), c2A(-0.11272), c3A(0.08183), FmA(2.75), B1A(1.63), B2A(1.66), k1B(3.5565), k2B(0.3776), k3B(0.0905),
    FmB(1), B1B(1.49), B2B(1.52), Tcin(298), Tcout(303),
    InvGT(22.7176e6), WorkGT(69676), FuelHeat(182359), FuelPrice(14), fPhi(1.06), fAnnu(0.1875), Teq(4000), Varcost(4),
    thermoModel(thermo::IdealFluidProperties("Water", 2.08, 4.18, 0.462, 0.001, 3.55959, 643.748, -198.043, 2480., 313.8336))
{
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    // Currently not providing any initial point
    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// evaluate the model
maingo::EvaluationContainer
Model::evaluate(const std::vector<Var>& optVars)
{
    // Rename inputs, these are the only real optimization variables
    Var p2     = optVars[0];
    Var p4     = optVars[1];
    Var mdot   = optVars[2];
    Var h7     = optVars[3];
    Var k      = optVars[4];
    Var mBleed = mdot * k;
    Var mMain  = mdot * (1. - k);

    // Model in a reduced-space formulation
    maingo::EvaluationContainer result;
    // Turbines:
    // Inlet:
    Var p7 = p4;
    result.ineq.push_back(
        /* constraint residual; inequalities are always given as g(x)<=0;
									   they should be scaled to be on the order of 1 such that all constraints are fulfilled to the same accuracy*/
        (thermoModel.get_hvap_p(p7) - h7) / 1e3,
        /* optionally, constraints can be given a name that will appear in the MAiNGO_res.txt file written by MAiNGO*/
        "hvap(p7)<=h7");
    Var T7 = thermoModel.get_T_vap_ph(p7, h7);
    result.ineq.push_back((T7 - Tmax) / 1e2, "T7<=Tmax");
    Var s7 = thermoModel.get_s_vap_ph(p7, h7);
    // Turbine 1 (bleed):
    Var p8    = p2;
    Var s8iso = s7;
    result.ineq.push_back((thermoModel.get_sliq_p(p8) - s8iso) / 1e0, "sliq(p8)<=s8iso");
    result.ineq.push_back((s8iso - thermoModel.get_svap_p(p8)) / 1e0, "s8iso<=svap(p8)");
    Var h8iso         = thermoModel.get_h_twophase_ps(p8, s8iso);
    Var wtBleed       = eta_t * (h7 - h8iso);
    Var WorkTurbBleed = mBleed * wtBleed;
    Var h8            = h7 * (1. - eta_t) + eta_t * h8iso;
    result.ineq.push_back((thermoModel.get_hliq_p(p8) - h8) / 1e2, "hliq(p8)<=h8");
    result.ineq.push_back((h8 - thermoModel.get_hvap_p(p8)) / 1e3, "h8<=hvap(p8)");
    Var x8 = thermoModel.get_x_ph(p8, h8);
    Var T8 = thermoModel.get_Ts_p(p8);
    // Turbine 2 (main):
    Var p1    = 0.05;    // Fixed condenser pressure
    Var p9    = p1;
    Var s9iso = s7;
    result.ineq.push_back((thermoModel.get_sliq_p(p9) - s9iso) / 1e0, "sliq(p9)<=s9iso");
    result.ineq.push_back((s9iso - thermoModel.get_svap_p(p9)) / 1e0, "s9iso<=svap(p9)");
    Var h9iso        = thermoModel.get_h_twophase_ps(p9, s9iso);
    Var wtMain       = eta_t * (h7 - h9iso);
    Var WorkTurbMain = mMain * wtMain;
    Var h9           = h7 * (1. - eta_t) + eta_t * h9iso;
    result.ineq.push_back((thermoModel.get_hliq_p(p9) - h9) / 1e2, "hliq(p9)<=h9");
    result.ineq.push_back((h9 - thermoModel.get_hvap_p(p9)) / 1e3, "h9<=hvap(p9)");
    Var T9    = thermoModel.get_Ts_p(p9);
    Var x9    = thermoModel.get_x_ph(p9, h9);
    Var h9liq = thermoModel.get_hliq_p(p9);
    Var h9vap = thermoModel.get_hvap_p(p9);
    result.ineq.push_back((xmin * h9vap - h9 + h9liq * (1 - xmin)) / 1e1, "xmin<=x9");
    // Feedwater line
    // Condenser
    Var T1    = thermoModel.get_Ts_p(p1);
    Var h1    = thermoModel.get_hliq_p(p1);
    Var s1    = thermoModel.get_sliq_p(p1);
    Var QCond = mMain * (h9 - h1);
    // Condensate pump
    Var s2iso        = s1;
    Var h2iso        = thermoModel.get_h_liq_ps(p2, s2iso);
    Var wpCond       = (h2iso - h1) / eta_p;
    Var WorkPumpCond = mMain * wpCond;
    Var h2           = h1 * (1. - 1. / eta_p) + h2iso / eta_p;
    Var T2           = thermoModel.get_T_liq_ph(p2, h2);
    // Deaerator
    Var p3 = p2;
    Var h3 = thermoModel.get_hliq_p(p3);
    result.eq.push_back((mBleed * (h3 - h8) + mMain * (h3 - h2)) / 1e3, "Deaerator energy balance");
    Var s3 = thermoModel.get_sliq_p(p3);
    Var T3 = thermoModel.get_Ts_p(p3);
    // Feedwater pump
    result.ineq.push_back((p2 - p4) / 1e0, "p2<=p4");
    Var s4iso        = s3;
    Var h4iso        = thermoModel.get_h_liq_ps(p4, s4iso);
    Var wpFeed       = (h4iso - h3) / eta_p;
    Var WorkPumpFeed = mdot * wpFeed;
    Var h4           = h3 * (1. - 1. / eta_p) + h4iso / eta_p;
    result.ineq.push_back((h4 - thermoModel.get_hliq_p(p4)) / 1e2, "h4<=hliq(p4)");
    Var T4 = thermoModel.get_T_liq_ph(p4, h4);
    // Boiler
    // Superheater
    Var p6  = p4;
    Var T6  = thermoModel.get_Ts_p(p6);
    Var h6  = thermoModel.get_hvap_p(p6);
    Var QSH = mdot * (h7 - h6);
    Var TG2 = TGin - QSH / mcpG;
    // Evaporator
    Var p5    = p4;
    Var T5    = thermoModel.get_Ts_p(p5) - dTap;
    Var h5    = thermoModel.get_h_liq_pT(p5, T5);
    Var QEvap = mdot * (h6 - h5);
    Var TG3   = TGin - mdot * (h7 - h5) / mcpG;
    result.ineq.push_back((dTmin - (TG3 - T6)) / 1e1, "Pinch: Evaporator, cold end");
    // Eco
    Var QEco  = mdot * (h5 - h4);
    Var TGout = TGin - mdot * (h7 - h4) / mcpG;
    result.ineq.push_back((dTmin - (TGout - T4)) / 1e1, "Pinch: Economizer, cold end");
    // Overall
    Var WorkNet = mBleed * (wtBleed - wpFeed) + mMain * (wtMain - wpCond - wpFeed);
    Var Qzu     = mdot * (h7 - h4);
    Var eta     = WorkNet / Qzu;
    // Combined Cycle Power Plant
    Var WorkTotal = WorkNet + WorkGT;
    result.ineq.push_back((WorkGT - WorkTotal) / 1e5, "WorkGT<=WorkTotal");
    WorkTotal = max(WorkTotal, WorkGT);
    Var etaCC = WorkTotal / FuelHeat;

    // Investment cost
    // Condenser
    Var dT1   = T9 - Tcout;
    Var dT2   = T1 - Tcin;
    Var rLMTD = rlmtd(dT1, dT2);
    Var ACond = rLMTD * QCond / kCond;
    result.ineq.push_back((Amin - ACond) / 1e1, "Amin<=ACond");
    ACond       = max(Amin, ACond);
    Var Cp0     = cost_function(ACond, 1, k1A, k2A, k3A);
    Var Fp      = 1.0;
    Var InvCond = 1.18 * (B1A + B2A * FmA * Fp) * Cp0;
    // Pumps
    result.ineq.push_back((1e-3 - WorkPumpCond) / 1e3, "0.001<=WorkPumpCond");
    result.ineq.push_back((1e-3 - WorkPumpFeed) / 1e3, "0.001<=WorkPumpFeed");
    Var InvPumpCond = 3540. * pow(max(WorkPumpCond, 1e-3), 0.71);
    Var InvPumpFeed = 3540. * pow(max(WorkPumpFeed, 1e-3), 0.71);
    // Turbines incl. generator
    result.ineq.push_back((1e-3 - WorkTurbBleed) / 1e5, "0.001<=WorkTurbBleed");
    result.ineq.push_back((1e-3 - WorkTurbMain) / 1e5, "0.001<=WorkTurbMain");
    Var InvTurb = 6000. * pow(max(WorkTurbBleed + WorkTurbMain, 1e-3), 0.7) + 60. * pow(max(WorkTurbBleed + WorkTurbMain, 1e-3), 0.95);
    // Economizer
    dT1      = TGout - T4;
    dT2      = TG3 - T5;
    dT1      = max(dTmin, dT1);
    dT2      = max(dTmin, dT2);
    rLMTD    = rlmtd(dT1, dT2);
    Var AEco = rLMTD * QEco / kEco;
    result.ineq.push_back((Amin - AEco) / 1e1, "Amin<=AEvo");
    AEco       = max(Amin, AEco);
    Cp0        = cost_function(AEco, 1, k1A, k2A, k3A);
    Fp         = cost_function(p4, 1, c1A, c2A, c3A);
    Var InvEco = 1.18 * (B1A + B2A * FmA * Fp) * Cp0;
    // Evaporator
    dT1       = TG3 - T6;
    dT2       = TG2 - T6;
    dT1       = max(dTmin, dT1);
    dT2       = max(dTmin, dT2);
    rLMTD     = rlmtd(dT1, dT2);
    Var AEvap = rLMTD * QEvap / kEvap;
    result.ineq.push_back((Amin - AEvap) / 1e1, "Amin<=AEvap");
    AEvap       = max(Amin, AEvap);
    Cp0         = cost_function(AEvap, 1, k1A, k2A, k3A);
    Var InvEvap = 1.18 * (B1A + B2A * FmA * Fp) * Cp0;
    // Superheater
    dT1     = dT2;
    dT2     = TGin - T7;
    dT1     = max(dTmin, dT1);
    dT2     = max(dTmin, dT2);
    rLMTD   = rlmtd(dT1, dT2);
    Var ASH = rLMTD * QSH / kSH;
    result.ineq.push_back((Amin - ASH) / 1e1, "Amin<=ASH");
    ASH       = max(Amin, ASH);
    Cp0       = cost_function(ASH, 1, k1A, k2A, k3A);
    Var InvSH = 1.18 * (B1A + B2A * FmA * Fp) * Cp0;
    // Deaerator
    Var VDae = 1.5 * 600 * mdot * 0.001;
    result.ineq.push_back((Vmin - VDae) / 1e0, "Vmin");
    Var Cp0DAE = cost_function(VDae, 1, k1B, k2B, k3B);
    Var FpDAE  = 1.25;
    Var InvDae = 1.18 * (B1B + B2B * FmB * FpDAE) * Cp0DAE;
    // Cycle
    Var Inv = InvCond + InvPumpCond + InvPumpFeed + InvEco + InvEvap + InvSH + InvTurb + InvDae;

    // Combined Cycle Plant
    Var InvTotal = Inv + InvGT;
    Var LCOE     = (InvTotal * fPhi * fAnnu * 1000 / Teq + FuelPrice * FuelHeat) / WorkTotal + Varcost;

    // Objective:
    result.objective = LCOE;

    // More output
    result.output.emplace_back("T1 [C]", T1 - 273.15);
    result.output.emplace_back("T2 [C]", T2 - 273.15);
    result.output.emplace_back("T3 [C]", T3 - 273.15);
    result.output.emplace_back("T4 [C]", T4 - 273.15);
    result.output.emplace_back("T5 [C]", T5 - 273.15);
    result.output.emplace_back("T6 [C]", T6 - 273.15);
    result.output.emplace_back("T7 [C]", T7 - 273.15);
    result.output.emplace_back("T8 [C]", T8 - 273.15);
    result.output.emplace_back("T9 [C]", T9 - 273.15);
    result.output.emplace_back("x8", x8);
    result.output.emplace_back("x9", x9);
    result.output.emplace_back("TG1 [C]", TGin - 273.15);
    result.output.emplace_back("TG2 [C]", TG2 - 273.15);
    result.output.emplace_back("TG3 [C]", TG3 - 273.15);
    result.output.emplace_back("TG4 [C]", TGout - 273.15);
    result.output.emplace_back("Work Steam Cycle [kW]", WorkNet);
    result.output.emplace_back("eta [-]", eta);
    result.output.emplace_back("etaCC [-]", etaCC);

    return result;
}
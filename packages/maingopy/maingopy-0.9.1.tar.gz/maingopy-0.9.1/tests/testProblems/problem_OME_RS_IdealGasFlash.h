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
#include "libraries/SubcriticalComponent.h"


using Var = mc::FFVar;


//////////////////////////////////////////////////////////////////////////
// Model class to be passed to MAiNGO
class Model_OME_RS_IdealGasFlash: public maingo::MAiNGOmodel {

  public:
    Model_OME_RS_IdealGasFlash();
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars);
    std::vector<maingo::OptimizationVariable> get_variables();


  private:
    // Constant model parameters:
    double F, Tf, pf;
    std::vector<double> z;
    unsigned int ncomp;
    // Declaration of model variables:
    std::vector<SubcriticalComponent<Var>> components;
    std::vector<Var> ps, hig, deltahv, dhpliq, x, y, K;
    Var psi, hl, hv, Q, V, L, VbF, T, p, hf;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_OME_RS_IdealGasFlash::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "V/F"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(318, 523), "T"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.1, 1), "p"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x-0"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x-1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x-2"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x-3"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x-4"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x-5"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x-6"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x-7"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_OME_RS_IdealGasFlash::Model_OME_RS_IdealGasFlash()
{

    // Initialize data if necessary:
    // Pure component models:
    components.push_back(SubcriticalComponent<Var>("OME3", 136.147, 603.4, -1, -1, -1, -1));
    components.push_back(SubcriticalComponent<Var>("OME4", 166.173, 646.9, -1, -1, -1, -1));
    components.push_back(SubcriticalComponent<Var>("OME5", 196.199, 683.7, -1, -1, -1, -1));
    components.push_back(SubcriticalComponent<Var>("OME6", 226.225, 714.8, -1, -1, -1, -1));
    components.push_back(SubcriticalComponent<Var>("OME7", 256.251, 743.0, -1, -1, -1, -1));
    components.push_back(SubcriticalComponent<Var>("OME8", 286.277, 769.2, -1, -1, -1, -1));
    components.push_back(SubcriticalComponent<Var>("OME9", 316.303, 794.6, -1, -1, -1, -1));
    components.push_back(SubcriticalComponent<Var>("OME10", 346.329, 819.9, -1, -1, -1, -1));
    ncomp = components.size();
    ps.resize(ncomp);
    hig.resize(ncomp);
    deltahv.resize(ncomp);
    dhpliq.resize(ncomp);
    x.resize(ncomp);
    y.resize(ncomp);
    z.resize(ncomp);
    K.resize(ncomp);
    // Pure component property parameters
    // Extended Antoine [bar,K]
    components[0].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{63.682, -8042.31, 0, 0, -7.4100, 0, 1});
    components[1].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{81.214, -10017.28, 0, 0, -9.7511, 0, 1});
    components[2].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{86.939, -11323.17, 0, 0, -10.3994, 0, 1});
    components[3].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{93.494, -12720.0, 0, 0, -11.1491, 0, 1});
    components[4].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{99.812, -14090.9, 0, 0, -11.8697, 0, 1});
    components[5].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{106.13, -15462, 0, 0, -12.5903, 0, 1});
    components[6].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{112.448, -16833, 0, 0, -13.3109, 0, 1});
    components[7].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{118.766, -18204, 0, 0, -14.0315, 0, 1});
    // DIPPR106 [kJ/kmol,K]
    components[0].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{58.545 * 1000, 0.29380, 0, 0, 0});
    components[1].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{72.458 * 1000, 0.36130, 0, 0, 0});
    components[2].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{81.911 * 1000, 0.35950, 0, 0, 0});
    components[3].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{92.022 * 1000, 0.35810, 0, 0, 0});
    components[4].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{101.940 * 1000, 0.35750, 0, 0, 0});
    components[5].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{111.860 * 1000, 0.35800, 0, 0, 0});
    components[6].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{121.760 * 1000, 0.36000, 0, 0, 0});
    components[7].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{131.660 * 1000, 0.36360, 0, 0, 0});
    // Heat capacity - DIPPR107 [kJ/kmolK,K]
    components[0].set_heat_capacity_model(PureComponent<Var>::CPIG_DIPPR107, std::vector<double>{112.74, 277.19, -769.63, 0, 0});
    components[1].set_heat_capacity_model(PureComponent<Var>::CPIG_DIPPR107, std::vector<double>{130.39, 338.31, -758.08, 0, 0});
    components[2].set_heat_capacity_model(PureComponent<Var>::CPIG_DIPPR107, std::vector<double>{147.95, 399.59, -750.07, 0, 0});
    components[3].set_heat_capacity_model(PureComponent<Var>::CPIG_DIPPR107, std::vector<double>{165.45, 460.97, -744.20, 0, 0});
    components[4].set_heat_capacity_model(PureComponent<Var>::CPIG_DIPPR107, std::vector<double>{182.91, 522.41, -739.71, 0, 0});
    components[5].set_heat_capacity_model(PureComponent<Var>::CPIG_DIPPR107, std::vector<double>{200.34, 583.89, -736.16, 0, 0});
    components[6].set_heat_capacity_model(PureComponent<Var>::CPIG_DIPPR107, std::vector<double>{217.75, 645.40, -733.29, 0, 0});
    components[7].set_heat_capacity_model(PureComponent<Var>::CPIG_DIPPR107, std::vector<double>{235.15, 706.94, -730.91, 0, 0});


    // Feed:
    F    = 1;                                                     // [kmol/s]
    Tf   = 458;                                                   // [K]
    pf   = 1;                                                     // [bar]
    z[0] = 0.30;                                                  // OME3
    z[1] = 0.24;                                                  // OME4
    z[2] = 0.17;                                                  // OME5
    z[3] = 0.11;                                                  // OME6
    z[4] = 0.08;                                                  // OME7
    z[5] = 0.05;                                                  // OME8
    z[6] = 0.03;                                                  // OME9
    z[7] = 1 - z[0] - z[1] - z[2] - z[3] - z[4] - z[5] - z[6];    // OME10
    hf   = 0;                                                     // kJ/kmol
    for (unsigned int i = 0; i < ncomp; i++) {
        Var deltahvfi = components[i].calculate_vaporization_enthalpy_conv(Tf);
        Var higfi     = components[i].calculate_ideal_gas_enthalpy_conv(Tf);
        hf += z[i] * (higfi - deltahvfi);
    }
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_OME_RS_IdealGasFlash::evaluate(const std::vector<Var> &optVars)
{


    // Rename / prepare inputs
    VbF = optVars[0];
    T   = optVars[1];
    p   = optVars[2];
    for (size_t i = 0; i < ncomp; ++i) {
        x[i] = optVars[3 + i];
    }


    // Model
    // FLASH:
    // 1. Overall mass balance
    V = F * VbF;
    L = F - V;
    // 2. Calculate phase equilibrium residual & enthalpies
    psi = 0, hl = 0, hv = 0;
    Var sumX(0), sumY(0);
    // Var tmpQ(0);
    for (unsigned i = 0; i < ncomp; i++) {
        // Phase equilibrium
        ps[i]      = components[i].calculate_vapor_pressure_conv(T);
        hig[i]     = components[i].calculate_ideal_gas_enthalpy_conv(T);
        deltahv[i] = components[i].calculate_vaporization_enthalpy_conv(T);
        K[i]       = ps[i] / p;
        psi += x[i];
        sumX += x[i];
        y[i] = K[i] * x[i];
        psi -= y[i];
        sumY += y[i];
        // Enthalpies
        hv += y[i] * hig[i];
        hl += x[i] * (hig[i] - deltahv[i]);
    }
    // 3. Energy balance:
    Q = V * hv + L * hl - F * hf;

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective:
#ifndef HAVE_GROWING_DATASETS
    result.objective = -V * (y[0] + y[1] + y[2]);
#else
    result.objective_per_data.push_back(-V * (y[0] + y[1] + y[2]));
#endif
    // Inequalities (<=0):
    result.ineq.push_back((0.98 - (y[0] + y[1] + y[2])) / 1.0);
    // Equalities (=0):
    result.eq.push_back(psi / 1.0);
    result.eq.push_back((0 - Q) / 1);
    for (size_t i = 0; i < ncomp; ++i) {
        result.eq.push_back(((F * z[i]) - (V * y[i] + L * x[i])) / 1.0);
    }

    result.eqRelaxationOnly.push_back((1.0 - sumX) / 1.0);
    result.eqRelaxationOnly.push_back((1.0 - sumY) / 1.0);
    // result.eq.push_back( (1.0-sumX)/1.0 );
    // result.eq.push_back( (1.0-sumY)/1.0 );

    // Additional Output:
    result.output.push_back(maingo::OutputVariable("L", L));
    result.output.push_back(maingo::OutputVariable("V", V));
    result.output.push_back(maingo::OutputVariable("psi", psi));
    result.output.push_back(maingo::OutputVariable("VbF", VbF));
    result.output.push_back(maingo::OutputVariable("x[0]", x[0]));
    result.output.push_back(maingo::OutputVariable("x[1]", x[1]));
    result.output.push_back(maingo::OutputVariable("x[2]", x[2]));
    result.output.push_back(maingo::OutputVariable("x[3]", x[3]));
    result.output.push_back(maingo::OutputVariable("x[4]", x[4]));
    result.output.push_back(maingo::OutputVariable("x[5]", x[5]));
    result.output.push_back(maingo::OutputVariable("x[6]", x[6]));
    result.output.push_back(maingo::OutputVariable("x[7]", x[7]));
    result.output.push_back(maingo::OutputVariable("y[0]", y[0]));
    result.output.push_back(maingo::OutputVariable("y[1]", y[1]));
    result.output.push_back(maingo::OutputVariable("y[2]", y[2]));
    result.output.push_back(maingo::OutputVariable("y[3]", y[3]));
    result.output.push_back(maingo::OutputVariable("y[4]", y[4]));
    result.output.push_back(maingo::OutputVariable("y[5]", y[5]));
    result.output.push_back(maingo::OutputVariable("y[6]", y[6]));
    result.output.push_back(maingo::OutputVariable("y[7]", y[7]));
    result.output.push_back(maingo::OutputVariable("Mole fraction of OME3-5 in vapor:", y[0] + y[1] + y[2]));
    result.output.push_back(maingo::OutputVariable("Fraction of OME3-5 recovered:", V * (y[0] + y[1] + y[2]) / (F * (z[0] + z[1] + z[2]))));
    result.output.push_back(maingo::OutputVariable("Q [kW]", Q));

    return result;
}

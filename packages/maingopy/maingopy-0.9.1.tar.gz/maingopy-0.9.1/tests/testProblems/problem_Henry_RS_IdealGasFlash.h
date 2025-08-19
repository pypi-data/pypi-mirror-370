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
#include "libraries/HenryComponent.h"
#include "libraries/SubcriticalComponent.h"


using Var = mc::FFVar;


//////////////////////////////////////////////////////////////////////////
// Model class to be passed to MAiNGO
class Model_Henry_RS_IdealGasFlash: public maingo::MAiNGOmodel {

  public:
    Model_Henry_RS_IdealGasFlash();
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars);
    std::vector<maingo::OptimizationVariable> get_variables();


  private:
    // Specify constant model parameters here:
    double F, Tf, pf;
    std::vector<double> z;
    size_t ncompSubcritical, ncompHenry, ncomp;
    std::vector<SubcriticalComponent<Var>> componentsSubcritical;
    std::vector<HenryComponent<Var>> componentsHenry;
    // Declare model variables here if desired:
    std::vector<Var> ps, hig, deltahv, deltahsol, x, y, henry, K;
    Var psi, hl, hv, Q, V, L, VbF, T, p, hf, sumX, sumY;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_Henry_RS_IdealGasFlash::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "V/F-1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(300, 512), "T-1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1, 66.5), "p-1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "xH2-1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "xCO2-1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "xCO-1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "xMeOH-1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "xH2O-1"));
    return variables;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_Henry_RS_IdealGasFlash::Model_Henry_RS_IdealGasFlash()
{

    // Initialize data if necessary:
    // Component models:
    componentsHenry.push_back(HenryComponent<Var>("H2", 2.01588, 273.15 - 252.76, 13.13, 64.147, 0, -1));
    componentsHenry.push_back(HenryComponent<Var>("CO2", 44.0098, 273.15 + 31.06, 73.83, 94, -393.510, -1));
    componentsHenry.push_back(HenryComponent<Var>("CO", 28.0104, 273.15 - 140.23, 34.99, 94.4, -110.530, -1));
    componentsSubcritical.push_back(SubcriticalComponent<Var>("MeOH", 32.04, 512.5, 80.84, 117, -200.940, -1));
    componentsSubcritical.push_back(SubcriticalComponent<Var>("Water", 18.0154, 647.096, 220.64, 55.9472, -241.818, -1));
    ncompHenry       = componentsHenry.size();
    ncompSubcritical = componentsSubcritical.size();
    ncomp            = ncompSubcritical + ncompHenry;

    // Henry component property parameters
    // H2
    componentsHenry[0].set_henry_model(HenryComponent<Var>::HENRY_ASPEN);
    componentsHenry[0].add_henry_parameters(std::vector<double>{3, -61.4347, 1867.4, 12.643, -0.027187, 0});
    componentsHenry[0].add_henry_parameters(std::vector<double>{4, 180.066, -6993.51, -26.3119, 0.0150431, 0});
    componentsHenry[0].set_solvent_mixing_rule(HenryComponent<Var>::MIX_ASPEN, std::vector<double>{117, 55.9472});
    componentsHenry[0].set_heat_capacity_model(HenryComponent<Var>::CPIG_DIPPR107, std::vector<double>{27.617, 9.56, 2466, 3.76, 567.6});
    // CO2
    componentsHenry[1].set_henry_model(HenryComponent<Var>::HENRY_ASPEN);
    componentsHenry[1].add_henry_parameters(std::vector<double>{3, 15.4699, -3426.7, 1.5108, -0.025451, 0});
    componentsHenry[1].add_henry_parameters(std::vector<double>{4, 159.865, -8741.55, -21.669, 0.00110259, 0});
    componentsHenry[1].set_solvent_mixing_rule(HenryComponent<Var>::MIX_ASPEN, std::vector<double>{117, 55.9472});
    componentsHenry[1].set_heat_capacity_model(HenryComponent<Var>::CPIG_DIPPR107, std::vector<double>{29.37, 34.54, 1428, 26.4, 588});
    // CO
    componentsHenry[2].set_henry_model(HenryComponent<Var>::HENRY_ASPEN);
    componentsHenry[2].add_henry_parameters(std::vector<double>{3, 4.21187, 1144.4, 0, 0, 0});
    componentsHenry[2].add_henry_parameters(std::vector<double>{4, 171.775, -8296.75, -23.3372, 0, 0});
    componentsHenry[2].set_solvent_mixing_rule(HenryComponent<Var>::MIX_ASPEN, std::vector<double>{117, 55.9472});
    componentsHenry[2].set_heat_capacity_model(HenryComponent<Var>::CPIG_DIPPR107, std::vector<double>{29.108, 8.773, 3085.1, 8.4553, 1538.2});
    // Subcritical component property parameters
    // Extended Antoine
    componentsSubcritical[0].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{71.2051, -6904.5, 0.0, 0.0, -8.8622, 7.4664e-6, 2});
    componentsSubcritical[1].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{62.1361, -7258.2, 0.0, 0.0, -7.3037, 4.1653e-6, 2});
    // Enthalpy of vaporization
    componentsSubcritical[0].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{32615, -1.0407, 1.8695, -0.60801, 0});
    componentsSubcritical[1].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{56600, 0.61204, -0.6257, 0.3988, 0});
    // Heat capacity
    componentsSubcritical[0].set_heat_capacity_model(SubcriticalComponent<Var>::CPIG_DIPPR107, std::vector<double>{39.252, 87.9, 1916.5, 53.654, 896.7});
    componentsSubcritical[1].set_heat_capacity_model(SubcriticalComponent<Var>::CPIG_DIPPR107, std::vector<double>{33.363, 26.79, 2610.5, 8.896, 1169});


    // Resizing
    ps.resize(ncomp);
    hig.resize(ncomp);
    deltahv.resize(ncomp);
    deltahsol.resize(ncomp);
    x.resize(ncomp);
    y.resize(ncomp);
    z.resize(ncomp);
    henry.resize(ncomp);
    K.resize(ncomp);


    // Feed:
    F    = 1;                                // [kmol/s]
    Tf   = 250 + 273.15;                     // [K]
    pf   = 66.5;                             // [bar]
    z[0] = 0.644;                            // H2
    z[1] = 0.195;                            // CO2
    z[2] = 0.025;                            // CO
    z[3] = 0.072;                            // MeOH
    z[4] = 1 - z[0] - z[1] - z[2] - z[3];    // H2O

    hf = 0;    // kJ/kmol
    for (size_t i = 0; i < ncompHenry; ++i) {
        Var higfi = componentsHenry[i].calculate_ideal_gas_enthalpy_conv(Tf);
        hf += z[i] * higfi;
    }
    for (size_t i = 0; i < ncompSubcritical; ++i) {
        Var higfi = componentsSubcritical[i].calculate_ideal_gas_enthalpy_conv(Tf);
        hf += z[i + ncompHenry] * higfi;
    }
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_Henry_RS_IdealGasFlash::evaluate(const std::vector<Var> &optVars)
{

    // Rename / prepare inputs

    VbF = optVars[0];
    T   = optVars[1];
    p   = optVars[2];
    for (size_t i = 0; i < ncomp; ++i) {
        x[i] = optVars[3 + i];
    }

    // Model
    // FLASH 1:
    // 1. Overall mass balance
    V = F * VbF;
    L = F - V;
    // 2. Calculate phase equilibrium residual & enthalpies
    psi = 0, hl = 0, hv = 0, sumX = 0, sumY = 0;
    for (size_t i = 0; i < ncompHenry; ++i) {

        // Phase equilibrium
        henry[i] = componentsHenry[i].calculate_henry_mixed(T, x);
        K[i]     = henry[i] / p;
        y[i]     = K[i] * x[i];
        sumX += x[i];
        sumY += y[i];
        psi += x[i] - y[i];
        // Enthalpies
        hig[i]       = componentsHenry[i].calculate_ideal_gas_enthalpy_conv(T);
        deltahsol[i] = componentsHenry[i].calculate_solution_enthalpy_mixed(T, x);
        hv += y[i] * hig[i];
        hl += x[i] * (hig[i] - deltahsol[i]);
    }
    for (unsigned i = 0; i < ncompSubcritical; i++) {

        // Phase equilibrium
        ps[i + ncompHenry] = componentsSubcritical[i].calculate_vapor_pressure_conv(T);
        K[i + ncompHenry]  = ps[i + ncompHenry] / p;
        y[i + ncompHenry]  = K[i + ncompHenry] * x[i + ncompHenry];
        sumX += x[i + ncompHenry];
        sumY += y[i + ncompHenry];
        psi += x[i + ncompHenry] - y[i + ncompHenry];
        // Enthalpies
        hig[i + ncompHenry]     = componentsSubcritical[i].calculate_ideal_gas_enthalpy_conv(T);
        deltahv[i + ncompHenry] = componentsSubcritical[i].calculate_vaporization_enthalpy_conv(T);
        hv += y[i + ncompHenry] * hig[i + ncompHenry];
        hl += x[i + ncompHenry] * (hig[i + ncompHenry] - deltahv[i + ncompHenry]);
    }

    // 3. Energy balance:
    Q = V * hv + L * hl - F * hf;


    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective:
#ifndef HAVE_GROWING_DATASETS
    result.objective = -L * x[3] / (F * z[3]);
    // result.objective = V*y[3]/(F*z[3]);
#else
    result.objective_per_data.push_back(-L * x[3] / (F * z[3]));
#endif

    // // Inequalities (<=0):
    result.ineq.push_back((x[1] - 0.01) / 1e-2);

    // // Equalities (=0):
    for (size_t i = 0; i < ncomp; ++i) {
        result.eq.push_back((z[i] - (VbF * y[i] + (1 - VbF) * x[i])) / 1.0);
    }
    result.eq.push_back((psi - 0.0) / 1.0);

    result.eqRelaxationOnly.push_back((sumX - 1.0) / 1.0);
    result.eqRelaxationOnly.push_back((sumY - 1.0) / 1.0);

    // Additional Output:
    result.output.push_back(maingo::OutputVariable("L", L));
    result.output.push_back(maingo::OutputVariable("V", V));
    result.output.push_back(maingo::OutputVariable("psi", psi));
    result.output.push_back(maingo::OutputVariable("x[0]", x[0]));
    result.output.push_back(maingo::OutputVariable("x[1]", x[1]));
    result.output.push_back(maingo::OutputVariable("x[2]", x[2]));
    result.output.push_back(maingo::OutputVariable("x[3]", x[3]));
    result.output.push_back(maingo::OutputVariable("x[4]", x[4]));
    result.output.push_back(maingo::OutputVariable("y[0]", y[0]));
    result.output.push_back(maingo::OutputVariable("y[1]", y[1]));
    result.output.push_back(maingo::OutputVariable("y[2]", y[2]));
    result.output.push_back(maingo::OutputVariable("y[3]", y[3]));
    result.output.push_back(maingo::OutputVariable("y[4]", y[4]));
    result.output.push_back(maingo::OutputVariable("henry[0]", henry[0]));
    result.output.push_back(maingo::OutputVariable("henry[1]", henry[1]));
    result.output.push_back(maingo::OutputVariable("henry[2]", henry[2]));
    result.output.push_back(maingo::OutputVariable("Fraction of MeOH lost", (V * y[3]) / (F * z[3])));
    result.output.push_back(maingo::OutputVariable("hf", hf));
    result.output.push_back(maingo::OutputVariable("hl", hl));
    result.output.push_back(maingo::OutputVariable("hv", hv));
    result.output.push_back(maingo::OutputVariable("Q", Q));

    return result;
}

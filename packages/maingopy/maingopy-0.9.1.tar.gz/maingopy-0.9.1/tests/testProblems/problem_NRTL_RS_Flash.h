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
#include "libraries/NRTL.h"
#include "libraries/SubcriticalComponent.h"

#define USENRTL


using Var = mc::FFVar;


//////////////////////////////////////////////////////////////////////////
// Model class to be passed to MAiNGO
class Model_NRTL_RS_Flash: public maingo::MAiNGOmodel {

  public:
    Model_NRTL_RS_Flash();
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars);
    std::vector<maingo::OptimizationVariable> get_variables();


  private:
    // Constant model parameters:
    double F, Tf, pf;
    std::vector<double> z;
    unsigned int ncomp;
    std::vector<std::vector<double>> aNRTL, bNRTL, cNRTL;
    // Declaration of model variables:
    std::vector<SubcriticalComponent<Var>> components;
    std::vector<Var> ps, hig, deltahv, x, y, gamma, K;
    Var psi, hl, hv, Q, V, L, HE, VbF, T, p, hf, sumX, sumY;
    NRTL NRTLmodel;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_NRTL_RS_Flash::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "V/F"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(200, 298), "T"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1, 15), "p"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "xMeOH"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "xH2O"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "xDME"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "yMeOH"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "yH2O"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1e-6, 1), "yDME"));
    // std::cout << "#variables: " << variables.size() << std::endl;

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_NRTL_RS_Flash::Model_NRTL_RS_Flash()
{

    // Initialize data if necessary:
    // Pure component models:
    components.push_back(SubcriticalComponent<Var>("MeOH", 32.04, 512.5, 80.84, 117, -200.93, -1));
    components.push_back(SubcriticalComponent<Var>("Water", 18.0154, 647.1, 220.64, 56, -241.818, -1));
    components.push_back(SubcriticalComponent<Var>("DME", 46.07, 400.1, 54.0, 164, -184.1, -1));
    // Pure component property parameters
    // Extended Antoine
    components[0].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{71.2051, -6904.5, 0.0, 0.0, -8.8622, 7.4664e-6, 2});
    components[1].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{62.1361, -7258.2, 0.0, 0.0, -7.3037, 4.1653e-6, 2});
    components[2].set_vapor_pressure_model(SubcriticalComponent<Var>::PVAP_XANTOINE, std::vector<double>{51.72, -4020, 0.0, 0.0, -6.546, 9.44e-6, 2});
    // Enthalpy of vaporization
    components[0].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{32615, -1.0407, 1.8695, -0.60801, 0});
    components[1].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{56600, 0.61204, -0.6257, 0.3988, 0});
    components[2].set_enthalpy_of_vaporization_model(SubcriticalComponent<Var>::DHVAP_DIPPR106, std::vector<double>{26377, -0.072806, 0.54324, -0.13977, 0});
    // Heat capacity
    components[0].set_heat_capacity_model(SubcriticalComponent<Var>::CPIG_DIPPR107, std::vector<double>{39.252, 87.9, 1916.5, 53.654, 896.7});
    components[1].set_heat_capacity_model(SubcriticalComponent<Var>::CPIG_DIPPR107, std::vector<double>{33.363, 26.79, 2610.5, 8.896, 1169});
    components[2].set_heat_capacity_model(SubcriticalComponent<Var>::CPIG_DIPPR107, std::vector<double>{57.431, 94.494, 895.51, 65.065, 2467.4});
    ncomp = components.size();
    ps.resize(ncomp);
    hig.resize(ncomp);
    deltahv.resize(ncomp);
    x.resize(ncomp);
    y.resize(ncomp);
    z.resize(ncomp);
    K.resize(ncomp);
    // NRTL Parameters; 0: MeOH, 1: H2O, 2: DME
    NRTLpars tmpNRTLpars;
    std::vector<std::vector<double>> tmpMatrix(ncomp, std::vector<double>(ncomp, 0.0));
    tmpNRTLpars.a       = tmpMatrix;
    tmpNRTLpars.b       = tmpMatrix;
    tmpNRTLpars.c       = tmpMatrix;
    tmpNRTLpars.d       = tmpMatrix;
    tmpNRTLpars.e       = tmpMatrix;
    tmpNRTLpars.f       = tmpMatrix;
    tmpNRTLpars.a[0][1] = -0.693;
    tmpNRTLpars.a[1][0] = 2.7322;
    tmpNRTLpars.a[0][2] = 0.0;
    tmpNRTLpars.a[2][0] = 0.0;
    tmpNRTLpars.a[1][2] = 3.59543;
    tmpNRTLpars.a[2][1] = -0.223052;

    tmpNRTLpars.b[0][1] = 172.987;
    tmpNRTLpars.b[1][0] = -617.269;
    tmpNRTLpars.b[0][2] = 653.006;
    tmpNRTLpars.b[2][0] = -18.9372;
    tmpNRTLpars.b[1][2] = -550.5;
    tmpNRTLpars.b[2][1] = 611.456;

    tmpNRTLpars.c[0][1] = 0.3;
    tmpNRTLpars.c[1][0] = 0.3;
    tmpNRTLpars.c[0][2] = 0.2951;
    tmpNRTLpars.c[2][0] = 0.2951;
    tmpNRTLpars.c[1][2] = 0.362916;
    tmpNRTLpars.c[2][1] = 0.362916;
    NRTLmodel.setPars<Var>(tmpNRTLpars);

    // Feed:
    F    = 1;                  // [kmol/s]
    Tf   = 72 + 273.15;        // [K]
    pf   = 15;                 // [bar]
    z[0] = 0.1668;             // MeOH
    z[2] = 0.4161;             // DME
    z[1] = 1 - z[0] - z[2];    // H2O
    hf   = 0.;
    for (unsigned int i = 0; i < ncomp; i++) {
        Var higfi     = components[i].calculate_ideal_gas_enthalpy_conv(Tf);
        Var deltahvfi = components[i].calculate_vaporization_enthalpy_conv(Tf);
        hf += z[i] * (higfi - deltahvfi);
    }
#ifdef USENRTL
    hf += NRTLmodel.calculateHE<double>(Tf, z);
#endif
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_NRTL_RS_Flash::evaluate(const std::vector<Var> &optVars)
{


    // Rename / prepare inputs
    VbF = optVars[0];
    T   = optVars[1];
    p   = optVars[2];
    for (size_t i = 0; i < ncomp; ++i) {
        x[i] = optVars[3 + i];
    }
    for (size_t i = 0; i < ncomp; ++i) {
        y[i] = optVars[3 + ncomp + i];
    }


    // Model
    // FLASH:
    // 1. Overall mass balance
    V = F * VbF;
    L = F - V;
    // 2. Calculate phase equilibrium residual & enthalpies
#ifdef USENRTL
    gamma = NRTLmodel.calculateGamma<Var>(T, x);
    HE    = NRTLmodel.calculateHE<Var>(T, x);
#endif
    psi = 0, hl = 0, hv = 0, sumX = 0, sumY = 0;
    for (unsigned i = 0; i < ncomp; i++) {
        // Phase equilibrium
        ps[i] = components[i].calculate_vapor_pressure_conv(T);
#ifdef USENRTL
        K[i] = gamma[i] * ps[i] / p;
#else
        K[i] = ps[i] / p;
#endif
        psi += y[i] - x[i];
        sumX += x[i];
        sumY += y[i];
        // Enthalpies
        hig[i]     = components[i].calculate_ideal_gas_enthalpy_conv(T);
        deltahv[i] = components[i].calculate_vaporization_enthalpy_conv(T);
        hv += y[i] * hig[i];
        hl += x[i] * (hig[i] - deltahv[i]);
    }
#ifdef USENRTL
    hl += HE;
#endif
    // 3. Energy balance:
    Q = V * hv + L * hl - F * hf;

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective:
#ifndef HAVE_GROWING_DATASETS
    result.objective = -Q;
#else
    result.objective_per_data.push_back(-Q);
#endif
    // Inequalities (<=0):
    result.ineq.push_back((0.99 - y[2]) / 1.0);
    // Equalities (=0):
    for (unsigned int i = 0; i < ncomp; i++) {
        result.eq.push_back((F * z[i] - (V * y[i] + L * x[i])) / 1.0);
        result.eq.push_back((y[i] - (K[i] * x[i])) / 1.0);
    }
    result.eq.push_back((psi - 0.0) / 1.0);

    result.eqRelaxationOnly.push_back(sumX - 1.0);
    result.eqRelaxationOnly.push_back(sumY - 1.0);

    // Additional Output:
    result.output.push_back(maingo::OutputVariable("L", L));
    result.output.push_back(maingo::OutputVariable("V", V));
    result.output.push_back(maingo::OutputVariable("psi", psi));
    result.output.push_back(maingo::OutputVariable("sumX", sumX));
    result.output.push_back(maingo::OutputVariable("sumY", sumY));
    result.output.push_back(maingo::OutputVariable("Fraction of DME lost", L * x[2] / (F * z[2])));
    result.output.push_back(maingo::OutputVariable("Q [kW]", Q));
    result.output.push_back(maingo::OutputVariable("ps[0]", ps[0]));
    result.output.push_back(maingo::OutputVariable("ps[1]", ps[1]));
    result.output.push_back(maingo::OutputVariable("ps[2]", ps[2]));
    result.output.push_back(maingo::OutputVariable("hf", hf));
    result.output.push_back(maingo::OutputVariable("hv", hv));
    result.output.push_back(maingo::OutputVariable("hl", hl));
    result.output.push_back(maingo::OutputVariable("hig[0]", hig[0]));
    result.output.push_back(maingo::OutputVariable("hig[1]", hig[1]));
    result.output.push_back(maingo::OutputVariable("hig[2]", hig[2]));
    result.output.push_back(maingo::OutputVariable("deltahv[0]", deltahv[0]));
    result.output.push_back(maingo::OutputVariable("deltahv[1]", deltahv[1]));
    result.output.push_back(maingo::OutputVariable("deltahv[2]", deltahv[2]));

    // std::cout << "#ineq: " << result.ineq.size() << std::endl;
    // std::cout << "#eq: " << result.eq.size() << std::endl;

    return result;
}

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

#include <algorithm>
#include <iterator>     // std::advance
#include <utility>      // std::pair

#include "MAiNGOmodel.h"
#include "MAiNGOException.h"


using Var = mc::FFVar;
using NamedVar = std::pair<Var, std::string>;

namespace maingo {

/**
  * @brief Class defining the abstract TwoStageModel to be specialized by the user
  * In contrast to the typical specialization of a maingo::MAiNGOmodel the specialization does not require
  * overriding the evaluate method, but instead the four functions specifying objective and constraints:
  * - f1_func : first stage objective function
  * - f2_func : second stage objective function
  * - g1_func : first stage constraints vector
  * - g2_func : second stage constraints vector
  */
class TwoStageModel: public MAiNGOmodel {

  public:
    typedef const std::vector<Var> & Varview;
    typedef const std::vector<double> & Valview;
  
  private:
    /**
     * @brief validation for w. It must contain at least one entry and the sum of all entries needs to be 1
     *
     * @param[in] w weights of the considered scenarios
     */
    Valview _validate(Valview w) const {
      if ( w.size() == 0 ) {
        throw std::invalid_argument("w must have at least one entry!");
      }
      double sum = 0;
      for (auto & weight : w)
        sum += weight;
      if (!mc::isequal(sum, 1., 1e-6, 1e-6)) {
        throw std::invalid_argument("The sum of weight entries in w must be equal to 1, but is "
                                    + std::to_string(sum) + " instead!");
      }
      return w;
    };
  
    /**
     * @brief validation for data. It must be the same length as w and all entries must be of the same length.
     *
     * @param[in] data a vector the same length as w. Each entry is a vector of parameter values for the corresponding scenario.
     */
    const std::vector<std::vector<double>> &_validate(const std::vector<std::vector<double>> &data) const {
      if ( data.size() != Ns ) {
        throw std::invalid_argument("w and data must have the same length! "
                                    "Have " + std::to_string(w.size())
                                    + " and " + std::to_string(data.size()) + "!");
      }
      if ( Ns > 1 ) {
        auto len = data[0].size();
        for (auto & data_s : data)
          if ( data_s.size() != len )
            throw std::invalid_argument("All entries of data must have same length!");
      }
      return data;
    };

  public:
    const unsigned int Nx;  // Number of first stage variables
    const unsigned int Ny;  // Number of second stage variables / scenario
    const unsigned int Ns;  // number of scenarios

    unsigned int Nineq1;         // number of first stage ineq
    unsigned int Nsquash1;       // number of first stage squash
    unsigned int Neq1;           // number of first stage eq
    unsigned int NineqRelOnly1;  // number of first stage ineqRelOnly
    unsigned int NeqRelOnly1;    // number of first stage eqRelOnly

    unsigned int Nineq2;         // number of second stage ineq
    unsigned int Nsquash2;       // number of second stage squash
    unsigned int Neq2;           // number of second stage eq
    unsigned int NineqRelOnly2;  // number of second stage ineqRelOnly
    unsigned int NeqRelOnly2;    // number of second stage eqRelOnly

    // weights for the considered scenarios
    const std::vector<double> w;
    // vectors of parameter values for each scenario
    const std::vector<std::vector<double>> data;

    /**
     * @brief Constructor for uniformly weighted scenarios
     *
     * @param[in] Nx number of first-stage variables
     * @param[in] Ny number of second-stage variables
     * @param[in] data |S| vectors with parameters values
     */
    TwoStageModel(
      const unsigned int Nx,
      const unsigned int Ny,
      const std::vector<std::vector<double>> &data
    ): Nx(Nx), Ny(Ny), data{_validate(data)}, w(data.size(), 1.0 / data.size()), Ns{static_cast<unsigned int>(data.size())} {}

    /**
     * @brief Generic constructor
     *
     * @param[in] Nx number of first-stage variables
     * @param[in] Ny number of second-stage variables
     * @param[in] data |S| vectors with parameters values
     * @param[in] w weights for the considered |S| scenarios
     */
    TwoStageModel(
      const unsigned int Nx, 
      const unsigned int Ny,
      const std::vector<std::vector<double>> &data,
      Valview w
    ): Nx(Nx), Ny(Ny), data{_validate(data)}, w{_validate(w)}, Ns{static_cast<unsigned int>(w.size())} {}

    /**
     * @brief The first stage objective function
     */
    virtual Var f1_func(Varview x) {
      return 0;
    }

    /**
     * @brief The second stage objective function
     */
    virtual Var f2_func(Varview x, Varview ys, Valview ps) {
      return 0;
    };

    /**
     * @brief The vector of first stage constraints
     */
    virtual std::vector<std::vector<NamedVar>> g1_func(Varview x) {
      return {
        {},  // ineq
        {},  // squash
        {},  // eq
        {},  // ineqRelOnly
        {},  // eqRelOnly
      };
    }

    /**
     * @brief The vector of second stage constraints
     */
    virtual std::vector<std::vector<NamedVar>> g2_func(Varview x, Varview ys, Valview ps) {
      return {
        {},  // ineq
        {},  // squash
        {},  // eq
        {},  // ineqRelOnly
        {},  // eqRelOnly
      };
    }
  
    /**
     * @brief Main function that can be used as a callback by external code to update FFVars
     *
     * @param[in] optVars is the optimization variables vector
     */
    virtual void _update(Varview optVars) {
    }

    /**
     * @brief Main function used to evaluate the model and construct a directed acyclic graph
     *
     * @param[in] optVars is the optimization variables vector
     */
    maingo::EvaluationContainer evaluate(Varview optVars){

      _update(optVars);

      if (optVars.size() != Nx + Ns * Ny) {
        throw MAiNGOException("You seem to have specified a redundant variable that is removed before preprocessing (check console output).\nWe can currently not handle this case, please reformulate your problem so that all variables appear in at least one constraint or the objective!");
      }

      // Prepare output
      maingo::EvaluationContainer result;

      std::vector<Var> x = std::vector<Var>();
      x.reserve(Nx);
	  x.insert(x.begin(), optVars.begin(), optVars.begin() + Nx);

      // TODO: The moves currently don't do anything, as there's no move assignment implemented!
      Var f1 = std::move(f1_func(x));
      auto obj(f1);

      result.output.push_back(maingo::OutputVariable(f1, "f1"));

      std::vector<std::vector<NamedVar>> g1 = g1_func(x);
      auto & g1_ineq = g1[0];
      auto & g1_squash = g1[1];
      auto & g1_eq = g1[2];
      auto & g1_ineqRO = g1[3];
      auto & g1_eqRO = g1[4];

      Nineq1 = g1_ineq.size();
      Nsquash1 = g1_squash.size();
      Neq1 = g1_eq.size();
      NineqRelOnly1 = g1_ineqRO.size();
      NeqRelOnly1 = g1_eqRO.size();

      // TODO: result.ineq is NOT actually a vector... bad docstring!
      // result.ineq.insert(result.ineq.end(), g1.begin(), g1.end());
      for (auto i = 0; i < g1_ineq.size(); i++) {
        const auto &lhs = g1_ineq[i];
        result.ineq.push_back(lhs.first, lhs.second);
      }
      for (auto i = 0; i < g1_squash.size(); i++) {
        const auto &lhs = g1_squash[i];
        result.ineqSquash.push_back(lhs.first, lhs.second);
      }
      for (auto i = 0; i < g1_eq.size(); i++) {
        const auto &lhs = g1_eq[i];
        result.eq.push_back(lhs.first, lhs.second);
      }
      for (auto i = 0; i < g1_ineqRO.size(); i++) {
        const auto &lhs = g1_ineqRO[i];
        result.ineqRelaxationOnly.push_back(lhs.first, lhs.second);
      }
      for (auto i = 0; i < g1_eqRO.size(); i++) {
        const auto &lhs = g1_eqRO[i];
        result.eqRelaxationOnly.push_back(lhs.first, lhs.second);
      }

      for (unsigned int s = 0; s < Ns; s++) {
        auto s_string = std::to_string(s + 1);

        const auto &result_s = evaluate(optVars, s);

        auto & f2s = result_s.objective.value[0];
        obj += w[s] * f2s;
        
        result.output.push_back(maingo::OutputVariable(f2s, "f2_" + s_string));
    
        auto & g2s_ineq = result_s.ineq.value;
        auto & g2s_ineq_names = result_s.ineq.name;
        auto & g2s_squash = result_s.ineqSquash.value;
        auto & g2s_squash_names = result_s.ineqSquash.name;
        auto & g2s_eq = result_s.eq.value;
        auto & g2s_eq_names = result_s.eq.name;
        auto & g2s_ineqRO = result_s.ineqRelaxationOnly.value;
        auto & g2s_ineqRO_names = result_s.ineqRelaxationOnly.name;
        auto & g2s_eqRO = result_s.eqRelaxationOnly.value;
        auto & g2s_eqRO_names = result_s.eqRelaxationOnly.name;

        // TODO: result.ineq is NOT actually a vector... bad docstring!
        // result.ineq.insert(result.ineq.end(), g1.begin(), g1.end());
        for (auto i = 0; i < g2s_ineq.size(); i++) {
          result.ineq.push_back(g2s_ineq[i], g2s_ineq_names[i] + '_' + s_string);
        }
        for (auto i = 0; i < g2s_squash.size(); i++) {
          result.ineqSquash.push_back(g2s_squash[i], g2s_squash_names[i] + '_' + s_string);
        }
        for (auto i = 0; i < g2s_eq.size(); i++) {
          result.eq.push_back(g2s_eq[i], g2s_eq_names[i] + '_' + s_string);
        }
        for (auto i = 0; i < g2s_ineqRO.size(); i++) {
          result.ineqRelaxationOnly.push_back(g2s_ineqRO[i], g2s_ineqRO_names[i] + '_' + s_string);
        }
        for (auto i = 0; i < g2s_eqRO.size(); i++) {
          result.eqRelaxationOnly.push_back(g2s_eqRO[i], g2s_eqRO_names[i] + '_' + s_string);
        }

        if (s == 0) {  // NOTE: we assume subproblems to have equal structure, so we only need to do this once
          Nineq2 = g2s_ineq.size();
          Nsquash2 = g2s_squash.size();
          Neq2 = g2s_eq.size();
          NineqRelOnly2 = g2s_ineqRO.size();
          NeqRelOnly2 = g2s_eqRO.size();
        }
      }
      result.objective = obj;

      return result;
    };

    /**
     * @brief Main function used to evaluate the model and construct a directed acyclic graph
     *
     * @param[in] optVars is the vector of all variables
     * @param[in] s is the scenario index
     */
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars, unsigned int s){

      // Prepare output
      maingo::EvaluationContainer result_s;

      std::vector<Var> x = std::vector<Var>();
      x.reserve(Nx);
      x.insert(x.begin(), optVars.begin(), optVars.begin() + Nx);
    
      std::vector<Var> ys = std::vector<Var>();
      ys.reserve(Ny);
      ys.insert(ys.begin(), optVars.begin() + Nx + s * Ny, optVars.begin() + Nx + (s + 1) * Ny); 
      
      Valview ps = data[s];

      auto f2s = f2_func(x, ys, ps);

      result_s.objective = f2s;
      auto s_string = std::to_string(s);
      result_s.output.push_back(maingo::OutputVariable(f2s, "f2_" + s_string));

      auto g2s = g2_func(x, ys, ps);
      auto & g2s_ineq = g2s[0];
      auto & g2s_squash = g2s[1];
      auto & g2s_eq = g2s[2];
      auto & g2s_ineqRO = g2s[3];
      auto & g2s_eqRO = g2s[4];

      // TODO: result.ineq is NOT actually a vector... bad docstring!
      // result.ineq.insert(result.ineq.end(), g1.begin(), g1.end());
      for (auto i = 0; i < g2s_ineq.size(); i++) {
        result_s.ineq.push_back(g2s_ineq[i].first, g2s_ineq[i].second);
      }
      for (auto i = 0; i < g2s_squash.size(); i++) {
        result_s.ineqSquash.push_back(g2s_squash[i].first, g2s_squash[i].second);
      }
      for (auto i = 0; i < g2s_eq.size(); i++) {
        result_s.eq.push_back(g2s_eq[i].first, g2s_eq[i].second);
      }
      for (auto i = 0; i < g2s_ineqRO.size(); i++) {
        result_s.ineqRelaxationOnly.push_back(g2s_ineqRO[i].first, g2s_ineqRO[i].second);
      }
      for (auto i = 0; i < g2s_eqRO.size(); i++) {
        result_s.eqRelaxationOnly.push_back(g2s_eqRO[i].first, g2s_eqRO[i].second);
      }

      return result_s;
    };
  };
};
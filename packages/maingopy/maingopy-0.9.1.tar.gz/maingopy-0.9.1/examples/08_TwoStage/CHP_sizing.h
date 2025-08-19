// A simplified example problem of CHP sizing for demonstrating two-stage structure
// We need to size a heat-controlled CHP for the satisfaction of heat and power demands, expressed
// through multiple scenarios with different probabilities.
// First stage decisions are the nominal size and second stage decision is the relative load.
// From the relative load the required fuel and thus the operational costs can be calculated.

// Author Marco Langiu
#include "TwoStageModel.h"
#include "MAiNGO.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>


/**
 * @brief Uncertain data for the CHP sizing problem
 * heat and electricity demands
 */
std::vector<std::vector<double>> example_data = {
// Qdot_dem, P_dem
  {0.000000, 1.951245},
  {0.000000, 0.900772},
  {0.000000, 1.853530},
  {0.665121, 0.454477},
  {0.965798, 1.645523},
  {1.141710, 1.572129},
  {1.160934, 0.877757},
  {1.287897, 1.394736}
};

/**
 * @brief Vertex form of a * x^2 + b * x + c
 */
Var vertex_form(const Var &x, double a, double b, double c) {
    return c - pow(b, 2) / (4 * a) + a * pow(x + b / (2 * a), 2);
}


/**
 * @brief Example for user defined TwoStageModel
 */
struct CHP_sizing_problem : maingo::TwoStageModel {

  CHP_sizing_problem() : TwoStageModel(1, 1, example_data) {
    std::cout << "CHP sizing model with " << example_data.size() << " scenarios" << std::endl;

    std::map<std::string, double CHP_sizing_problem::*> members;
    members["Qdot_nom_ref"] = &CHP_sizing_problem::Qdot_nom_ref;
    members["c_ref"] = &CHP_sizing_problem::c_ref;
    members["M"] = &CHP_sizing_problem::M;
    members["c_m"] = &CHP_sizing_problem::c_m;
    members["Qdot_rel_min"] = &CHP_sizing_problem::Qdot_rel_min;
    members["Qdot_nom_min"] = &CHP_sizing_problem::Qdot_nom_min;
    members["Qdot_nom_max"] = &CHP_sizing_problem::Qdot_nom_max;
    members["n"] = &CHP_sizing_problem::n;
    members["i"] = &CHP_sizing_problem::i;
    members["T_OP"] = &CHP_sizing_problem::T_OP;
    members["p_gas"] = &CHP_sizing_problem::p_gas;
    members["p_el_buy"] = &CHP_sizing_problem::p_el_buy;
    members["p_el_sell"] = &CHP_sizing_problem::p_el_sell;

    std::ifstream file;
    file.open("CHP_data.txt");
    if (file.is_open()) {
        std::string line;
        std::string word;
        double number;
        bool firstLine = true;
        while (std::getline(file, line)) {    // Read file line by line
            if (firstLine) {
                // Check for BOM in UTF 8, BOM is ALWAYS at the beginning of a file -- NOTE: We only correctly handle UTF 8 setting files!
                if (line.length() >= 3) {
                    if (line[0] == (char)0XEF && line[1] == (char)0XBB && line[2] == (char)0XBF) {
                        line.erase(0, 3);
                    }
                }
                firstLine = false;
            }
            // If the line is not a comment, proceed (\r is for carriage return)
            if ((line.find_first_not_of(' ') != std::string::npos) && !line.empty() && line[0] != '#' && line[0] != '\r') {
                std::istringstream iss(line);    // This allows access to line as real std::string
                iss >> word;
                iss >> number;
                this->*(members[word]) = number;
            }
        }
      std::cout << "Found CHP_data.txt file, using values:\n";
    }
    else {    // File not found
      std::cout << "No CHP_data.txt file found, using default values:\n";
    }
    for (const auto & elem : members) {
      std::cout << elem.first << " = " << this->*(elem.second) << std::endl;
    }
    std::cout << std::endl;
    file.close();

    Qdot_eps   = 0.001 * Qdot_nom_max;
    Qdot_mean  = (Qdot_nom_min + Qdot_nom_max) / 2;
    af = (pow(1 + i, n) * i) / (pow(1 + i, n) - 1);  // annuity factor
  };

  double Qdot_nom_ref = 1;     // [MW], reference nominal power
  double c_ref        = 1.3e6; // [€], reference cost
  double M            = 0.9;   // [-], cost exponent
  double c_m          = 0.05;  // [-], maintenance coefficient, (fraction of investment cost)
  double Qdot_rel_min = 0.5;   // [-] minimum output part load
  double Qdot_nom_min = 0.5;   // [MW], minimum nominal power
  double Qdot_nom_max = 2.3;   // [MW], maximum nominal power
  double Qdot_eps;
  double Qdot_mean;
  
  double n = 30;   // lifetime in years
  double i = 0.05; // annualization interst rate
  double af;       // annuity factor

  double T_OP      = 6000; // [h / a]
  double p_gas     = 80;   // [€ / Mwh]
  double p_el_buy  = 250;  // [€ / Mwh]
  double p_el_sell = 100;  // [€ / Mwh]

  /**
   * @brief Compute the nominal thermal efficiency of the CHP
   */
  Var eff_th_nom(const Var &Qdot_nom) {
      return 0.498 - 3.55e-2 * Qdot_nom;
  }

  /**
   * @brief Compute the nominal electrical efficiency of the CHP
   */
  Var eff_el_nom(const Var &Qdot_nom) {
      return 0.372 + 3.55e-2 * Qdot_nom;
  }

  /**
   * @brief Compute the relative thermal efficiency of the CHP
   */
  Var eff_th_rel(const Var &Qdot_rel) {
      return vertex_form(Qdot_rel, -0.0768, -0.0199, 1.0960);
  }

  /**
   * @brief Compute the relative electrical efficiency of the CHP
   */
  Var eff_el_rel(const Var &Qdot_rel) {
      return vertex_form(Qdot_rel, -0.2611, 0.6743, 0.5868);
  }

  /**
   * @brief Compute the thermal efficiency of the CHP
   */
  Var eff_th(const Var &Qdot_nom, const Var &Qdot_rel) {
      return eff_th_nom(Qdot_nom) * eff_th_rel(Qdot_rel);
  }

  /**
   * @brief Compute the electrical efficiency of the CHP
   */
  Var eff_el(const Var &Qdot_nom, const Var &Qdot_rel) {
      return eff_el_nom(Qdot_nom) * eff_el_rel(Qdot_rel);
  }

  /**
   * @brief Function for getting the (Nx + Ns * Ny) optimization variables
   */
  std::vector<maingo::OptimizationVariable> get_variables() {
    std::vector<maingo::OptimizationVariable> variables;
    // Using branching priority ratio of 16:1
    std::string name = "Qdot_nom";
    variables.push_back({{Qdot_nom_min, Qdot_nom_max}, 16, name});
    for (auto s = 0; s < Ns; ++s) {
      name = "Qdot_rel_" + std::to_string(s);
      variables.push_back({{0, 1}, 1, name});
    }

    for (auto &var : variables) {
      std::cout << "  " << var.get_name() << " " << var.get_branching_priority() << std::endl;
    }
    std::cout << std::endl;
    return variables;
  };

  std::vector<double> get_initial_point() {
      return {
          // Optimal solution obtained from dense sampling with 1000 points in each variable domain
          1.671171171171171,
          1,
          0.6346346346346347,
          1,
          0.5005005005005005,
          1,
          0.9669669669669669,
          0.6946946946946947,
          0.8838838838838838,
        };
  }

  /**
   * @brief Annualized investment cost in million euros/a
   */
  Var f1_func(Varview x) {
    const Var & Qdot_nom = x[0];
    // investment cost of the component
    Var ic = std::move(c_ref * pow(Qdot_nom / Qdot_nom_ref, M));
    // fixed cost of the component
    Var fc = std::move(c_m * ic);

    return 1e-6 * (af * ic + fc);
  }

  /**
   * @brief Annual operating cost in million euros/a
   */
  Var f2_func(Varview x, Varview y, Valview p) {
    auto Qdot_nom = x[0];
    auto Qdot_rel     = y[0];
    auto Qdot_dem     = p[0];
    auto P_dem        = p[1];
    
    auto Qdot_out = Qdot_nom * Qdot_rel;

    auto Edot_in = Qdot_out / eff_th(Qdot_nom, Qdot_rel);
    auto P_out = Edot_in * eff_el(Qdot_nom, Qdot_rel);
    
    // When allowing an electric heater
    // auto Qdot_supplied_via_electricity = max(0, Qdot_dem - Qdot_out);
    // Otherwise
    auto Qdot_supplied_via_electricity = 0;

    auto P_grid = P_dem - P_out + Qdot_supplied_via_electricity;

    // Total variable cost = purchase for gas
    // + purchase for missing elextricity
    // or compensation (negative cost) for selling excess electricity
    return 1e-6 * (
        p_gas * Edot_in
        + p_el_buy * max(0, P_grid)
        - p_el_sell * max(0, -P_grid)
    ) * T_OP;
  }

  /**
   * @brief The vector of second stage constraints
   */
  std::vector<std::vector<std::pair<Var, std::string>>> g2_func(Varview x, Varview y, Valview p) {
    auto & Qdot_nom        = x[0];
    auto & Qdot_rel        = y[0];
    auto min_partload_viol = vertex_form(Qdot_rel, -1, Qdot_rel_min + Qdot_eps, -Qdot_rel_min * Qdot_eps);

    // If not using heater
    auto Qdot_out      = Qdot_nom * Qdot_rel;
    auto & Qdot_dem    = p[0];
    auto dem_violation = Qdot_dem - Qdot_out;

    return {
      {
        {min_partload_viol, "Minimum part load violation"},
        {dem_violation, "Heat demand satisfaction"},
      },  // ineq
      {},  // squash
      {},  // eq
      {},  // ineqRelOnly
      {},  // eqRelOnly
    };
  }

};

using Model = CHP_sizing_problem;
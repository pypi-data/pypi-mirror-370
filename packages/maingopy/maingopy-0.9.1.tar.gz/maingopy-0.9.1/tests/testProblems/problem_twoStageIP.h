/**
 * Example 1 from the paper:
 * Carøe, C. C. & Schultz, R.
 * Dual decomposition in stochastic integer programming 
 * Oper. Res. Lett., Elsevier, 1999, 24, 37-45
 * DOI: 10.1016/S0167-6377(98)00050-9
 */
#include "TwoStageModel.h"
#include "MAiNGO.h"

#include <fstream>
#include <sstream>
#include <string>

/**
 * @brief Example for a two-stage integer programming problem
 */
struct TwoStageIP_problem : maingo::TwoStageModel {

  TwoStageIP_problem() : TwoStageModel(
    2, // Nx
    4, // Ny
    { /** NOTE: In the original example the data consists of all combinations of two values from 5 to 15 in steps of 0.5 */
    // xi1, xi2
      { 5,  5},
      { 5, 15},
      {15,  5},
      {15, 15}
    }
  ) {};

  /**
   * @brief Function for getting the (Nx + Ns * Ny) optimization variables
   */
  std::vector<maingo::OptimizationVariable> get_variables() {
    std::vector<maingo::OptimizationVariable> variables;
    // Using branching priority ratio of 16:1
    std::string name = "x_1";
    variables.push_back({{0, 5}, maingo::VT_INTEGER, 1, name});
    name = "x_2";
    variables.push_back({{0, 5}, maingo::VT_INTEGER, 1, name});
    for (auto s = 0; s < Ns; ++s) {
      name = "y_1_" + std::to_string(s);
      variables.push_back({{0, 1}, maingo::VT_BINARY, 1, name});

      name = "y_2_" + std::to_string(s);
      variables.push_back({{0, 1}, maingo::VT_BINARY, 1, name});

      name = "y_3_" + std::to_string(s);
      variables.push_back({{0, 1}, maingo::VT_BINARY, 1, name});

      name = "y_4_" + std::to_string(s);
      variables.push_back({{0, 1}, maingo::VT_BINARY, 1, name});
    }

    return variables;
  };

  std::vector<double> get_initial_point() {
      return {
          0, 4,       // first stage
          0, 0, 0, 0, // second stage, scenario 1
          0, 0, 0, 0, // second stage, scenario 2
          0, 0, 0, 0, // second stage, scenario 3
          0, 0, 0, 0  // second stage, scenario 4
        };
  }

  Var f1_func(Varview x) {
    const Var &x1 = x[0];
    const Var &x2 = x[1];
    return - (3/2 * x1 + 4 * x2);
  }

  Var f2_func(Varview x, Varview y, Valview p) {
    const Var &y1 = y[0];
    const Var &y2 = y[1];
    const Var &y3 = y[2];
    const Var &y4 = y[3];
    return - (16 * y1 + 19 * y2 + 23 * y3 + 28 * y4);
  }

  std::vector<std::vector<std::pair<Var, std::string>>> g1_func(Varview x) {
      const Var &x1 = x[0];
      const Var &x2 = x[1];
      return {
          {{x1 - x2, "dummy constraint inactive at the global solution"}}, // ineq
          {},                                                              // squash
          {},                                                              // eq
          {},                                                              // ineqRelOnly
          {},                                                              // eqRelOnly
      };
  }

  std::vector<std::vector<std::pair<Var, std::string>>> g2_func(Varview x, Varview y, Valview p) {
    const Var &x1     = x[0];
    const Var &x2     = x[1];
    const Var &y1     = y[0];
    const Var &y2     = y[1];
    const Var &y3     = y[2];
    const Var &y4     = y[3];
    const double &xi1 = p[0];
    const double &xi2 = p[1];
    return {
      {
        {x1 + 2 * y1 + 3 * y2 + 4 * y3 + 5 * y4 - xi1, "con_1"},
        {x2 + 6 * y1 + 1 * y2 + 3 * y3 + 2 * y4 - xi2, "con_2"},
      },  // ineq
      {},  // squash
      {},  // eq
      {},  // ineqRelOnly
      {},  // eqRelOnly
    };
  }

};
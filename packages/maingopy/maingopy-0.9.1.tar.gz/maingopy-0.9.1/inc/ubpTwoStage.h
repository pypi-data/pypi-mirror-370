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

#include "MAiNGOException.h"
#include "logger.h"
#include "ubp.h"
#include "ubpClp.h"
#include "ubpIpopt.h"
#include "ubpNLopt.h"

#ifdef HAVE_CPLEX    // If CMake has found CPLEX ,this pre-processor variable is defined
  #include "ubpCplex.h"
#endif

#ifdef HAVE_KNITRO    // If CMake has found KNITRO, this pre-processor variable is defined
  #include "ubpKnitro.h"
#endif

#include "ubpDagObj.h"

#include "TwoStageModel.h"

namespace maingo {


namespace ubp {


/**
* @class UbpTwoStage
* @brief Wrapper for handling the upper-bounding problems of two stage (stochastic) programming problems
*
* This class constructs one upper-bounding subproblem solver per scenario and delegates solve calls to these subproblem solvers.
*/
template<class subsolver_class>
class UbsTwoStage: public subsolver_class {
  std::shared_ptr<maingo::TwoStageModel> _TwoStageModel;
  std::vector<std::shared_ptr<UpperBoundingSolver>> _subsolvers;

  mc::FFSubgraph _g1_subgraph;
  std::vector<Var> _firstStageIneqEq;

public:
  
  std::vector<std::vector<babBase::OptimizationVariable>> RP_opt_variables;
  std::vector<mc::FFGraph> RP_DAGs;
  std::vector<std::vector<mc::FFVar>> RP_DAG_variables;
  std::vector<std::vector<mc::FFVar>> RP_DAG_x;
  std::vector<std::vector<mc::FFVar>> RP_DAG_y;
  std::vector<std::vector<mc::FFVar>> RP_DAG_functions;
  std::vector<std::shared_ptr<std::vector<Constraint>>> RP_constraint_properties;

  /**
  * @brief Constructor, stores information on the problem and initializes the local-subsolvers used
  *
  * @param[in] twoStageModel is the pointer to the TwoStageModel opbject
  * @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
  * @param[in] DAGvars are the variables corresponding to the DAG
  * @param[in] DAGfunctions are the functions corresponding to the DAG
  * @param[in] variables is a vector containing the initial optimization variables defined in problem.h
  * @param[in] nineqIn is the number of inequality constraints
  * @param[in] neqIn is the number of equality constraints
  * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
  * @param[in] settingsIn is a pointer to the MAiNGO settings
  * @param[in] loggerIn is a pointer to the MAiNGO logger object
  * @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
  * @param[in] useIn communicates what the solver is to be used for
  */
  UbsTwoStage(const std::shared_ptr<maingo::TwoStageModel> twoStageModel,
              mc::FFGraph &DAG,
              const std::vector<mc::FFVar> &DAGvars,
              const std::vector<mc::FFVar> &DAGfunctions,
              const std::vector<babBase::OptimizationVariable> &variables,
              const unsigned nineqIn,
              const unsigned neqIn,
              const unsigned nineqSquashIn,
              std::shared_ptr<Settings> settingsIn,
              std::shared_ptr<Logger> loggerIn,
              std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn,
              UpperBoundingSolver::UBS_USE useIn) :
  subsolver_class(DAG, DAGvars, DAGfunctions, variables,
                  nineqIn, neqIn, nineqSquashIn,
                  settingsIn, loggerIn, constraintPropertiesIn, useIn),
  _TwoStageModel(twoStageModel) {
    // Creating empty containers for each scenario
    RP_opt_variables.resize(_TwoStageModel->Ns);
    RP_DAGs = std::vector<mc::FFGraph>(_TwoStageModel->Ns);  // one new DAG per scenario for RP subproblems
    RP_DAG_variables.resize(_TwoStageModel->Ns);
    RP_DAG_x.resize(_TwoStageModel->Ns);
    RP_DAG_y.resize(_TwoStageModel->Ns);
    RP_DAG_functions.resize(_TwoStageModel->Ns);

    // Filling the containers above
    #ifdef _OPENMP
      #pragma omp parallel for
    #endif
    for (int s = 0; s < _TwoStageModel->Ns; ++s) {
      RP_opt_variables[s].reserve(_TwoStageModel->Nx + _TwoStageModel->Ny);
      RP_DAG_variables[s].reserve(_TwoStageModel->Nx + _TwoStageModel->Ny);

      for (unsigned ix = 0; ix < _TwoStageModel->Nx; ++ix) {
        RP_opt_variables[s].push_back(variables[ix]);
        RP_DAG_variables[s].emplace_back(&RP_DAGs[s]);
        RP_DAG_x[s].push_back(RP_DAG_variables[s].back());
      }
    
      for (unsigned iy = 0; iy < _TwoStageModel->Ny; ++iy) {
        RP_opt_variables[s].push_back(variables[_TwoStageModel->Nx + s * _TwoStageModel->Ny + iy]);
        RP_DAG_variables[s].emplace_back(&RP_DAGs[s]);
        RP_DAG_y[s].push_back(RP_DAG_variables[s].back());
      }
    }
    
    std::vector<std::vector<std::vector<NamedVar>>> g2;
    g2.reserve(_TwoStageModel->Ns);
    // This loop might need to happen sequentially, since _TwoStageModel may not be thread-safe (e.g. when defined via the Python API)
    for (int s = 0; s < _TwoStageModel->Ns; ++s) {
      RP_DAG_functions[s].emplace_back(
        _TwoStageModel->f2_func(RP_DAG_x[s], RP_DAG_y[s], _TwoStageModel->data[s])
      );
      g2.emplace_back(_TwoStageModel->g2_func(RP_DAG_x[s], RP_DAG_y[s], _TwoStageModel->data[s]));
    }

    RP_constraint_properties = std::vector<std::shared_ptr<std::vector<Constraint>>>(_TwoStageModel->Ns);
    _subsolvers.resize(_TwoStageModel->Ns);
    #ifdef _OPENMP
      #pragma omp parallel for
    #endif
    for (int s = 0; s < _TwoStageModel->Ns; ++s) {

      RP_constraint_properties[s] = std::make_shared<std::vector<Constraint>>();
      _prepare_constraints(std::to_string(s), RP_constraint_properties[s], RP_DAG_functions[s], g2[s]);
      _subsolvers[s] = ubp::make_ubp_solver(
        RP_DAGs[s],                   // different since DAGs are different, but are only dummy objects
        RP_DAG_variables[s],          // [x_1, ..., x_Nx, y_s_1, ..., y_s_Ny]
        RP_DAG_functions[s],          // separated in advance
        RP_opt_variables[s],
        /*_TwoStageModel->Nineq1 + */_TwoStageModel->Nineq2, 
        /*_TwoStageModel->Neq1 + */_TwoStageModel->Neq2,
        /*_TwoStageModel->Nsquash1 + */_TwoStageModel->Nsquash2,
        settingsIn,
        loggerIn,                       // might get noisy with verbose output when solving in parallel...
        RP_constraint_properties[s],  // here we need to think about how to handle x as constant
        useIn,
        false
      );
    }

    // Create subgraph of g1 for efficient evauation
    std::vector<std::vector<NamedVar>> g1 = _TwoStageModel->g1_func(this->_DAGobj->vars);
    _firstStageIneqEq.reserve(_TwoStageModel->Nineq1 + _TwoStageModel->Nsquash1 + _TwoStageModel->Neq1);
    for (auto j : {0, 1, 2})  // positions of ineq, squash, and eq constraints in g1
      for (auto i = 0; i < g1[j].size(); i++)
        _firstStageIneqEq.push_back(g1[j][i].first);
    _g1_subgraph = this->_DAGobj->DAG.subgraph(_firstStageIneqEq.size(), _firstStageIneqEq.data());
  }

private:

  /**
   * @brief Function for preparing the constraints for the subproblem solver
   */
  inline void _prepare_constraints(
    const std::string &s_string,
    std::shared_ptr<std::vector<Constraint>> &RP_constraint_properties_s,
    std::vector<mc::FFVar> &RP_DAG_functions_s,
    std::vector<std::vector<NamedVar>> &g2_s
  ) {
    unsigned indexOriginal = 0, indexNonconstant = 0;

    RP_constraint_properties_s->emplace_back(
      CONSTRAINT_TYPE::OBJ,
      indexOriginal++,
      0,
      indexNonconstant++,
      0,
      "f2_" + s_string);

    maingo::CONSTRAINT_TYPE ct[3] = {
      maingo::CONSTRAINT_TYPE::INEQ,
      maingo::CONSTRAINT_TYPE::INEQ_SQUASH,
      maingo::CONSTRAINT_TYPE::EQ
    };

    unsigned indexType[3]            = {0, 0, 0};
    unsigned indexTypeNonconstant[3] = {0, 0, 0};
    std::string type[3] {"ineq", "ineg_squash", "eq"};
    for (unsigned i = 0; i < 3; ++i) { // g2RPs_ineq, g2RPs_squash, g2RPs_eq
      for (auto & func : g2_s[i]) {
        RP_DAG_functions_s.push_back(func.first);
        RP_constraint_properties_s->emplace_back(
          ct[i],
          indexOriginal++,
          indexType[i],
          indexNonconstant++,
          indexTypeNonconstant[i]++,
          type[i] + '_' + s_string + '_' + std::to_string(indexType[i]++));
      }
    }

    // Now that we assembled all functions for scenario s, we analyze their properties

    // Get dependency sets of all functions
    unsigned size = RP_DAG_functions_s.size();
    std::vector<std::map<int, int>> func_dep(size);
    for (unsigned int i = 0; i < size; i++) {
        func_dep[i] = RP_DAG_functions_s[i].dep().dep();
    }

    // Loop over all functions
    unsigned indexLinear = 0, indexNonlinear = 0;
    for (unsigned int i = 0; i < size; i++) {
      mc::FFDep::TYPE functionStructure = mc::FFDep::L;
      std::vector<unsigned> participatingVars;
      for (unsigned int j = 0; j < UpperBoundingSolver::_nvar; j++) {    // TODO: Only X and ys
        auto ito = func_dep[i].find(j);
        // Count all participating variables
        if (ito != func_dep[i].end()) {
          participatingVars.push_back(j);
          mc::FFDep::TYPE variableDep = (mc::FFDep::TYPE)(ito->second);
          // Update function type
          if (functionStructure < variableDep) {
            functionStructure = variableDep;
          }
        }
      }

      Constraint & func        = (*RP_constraint_properties_s)[i];
      func.indexNonconstantUBP = i;

      // determine dependency
      func.nparticipatingVariables = participatingVars.size();
      func.participatingVariables  = participatingVars;
      switch (functionStructure) {
        case mc::FFDep::L:
          func.dependency     = LINEAR;
          func.indexLinear    = indexLinear++;
          break;
        case mc::FFDep::B:
          func.dependency        = BILINEAR;
          func.indexNonlinear    = indexNonlinear++;
          break;
        case mc::FFDep::Q:
          func.dependency        = QUADRATIC;
          func.indexNonlinear    = indexNonlinear++;
          break;
        case mc::FFDep::P:
          func.dependency        = POLYNOMIAL;
          func.indexNonlinear    = indexNonlinear++;
          break;
        case mc::FFDep::R:
          func.dependency        = RATIONAL;
          func.indexNonlinear    = indexNonlinear++;
          break;
        case mc::FFDep::N:
        case mc::FFDep::D:
        default:
          func.dependency        = NONLINEAR;
          func.indexNonlinear    = indexNonlinear++;
          break;
      }
      func.convexity       = CONV_NONE;
      func.monotonicity    = MON_NONE;
    }
  }

  /**
  * @brief Function for actually solving the NLP sub-problem.
  *
  * @param[in] lowerVarBounds is the vector containing the lower bounds on the variables within the current node
  * @param[in] upperVarBounds is the vector containing the upper bounds on the variables within the current node
  * @param[out] objectiveValue is the objective value obtained for the solution point of the upper bounding problem (need not be a local optimum!)
  * @param[in,out] solutionPoint is the point at which objectiveValue was achieved (can in principle be any point within the current node!); it is also used for communicating the initial point (usually the LBP solution point)
  * @return Return code, either SUBSOLVER_FEASIBLE or SUBSOLVER_INFEASIBLE, indicating whether the returned solutionPoint (!!) is feasible or not
  */
  SUBSOLVER_RETCODE _solve_nlp(
    const std::vector<double> &lowerVarBounds,
    const std::vector<double> &upperVarBounds,
    double &objectiveValue,
    std::vector<double> &solutionPoint
  ) {

    /** NOTE: Shortcut indicating that no NLP is solved */
    if (subsolver_class::_maingoSettings->UBP_solverBab == UBP_SOLVER_EVAL)
      return SUBSOLVER_INFEASIBLE;

    // fix first stage variables
    std::vector<double> firstStageValues;
    for (unsigned i = 0; i <  _TwoStageModel->Nx; i++) {
      double x_i = solutionPoint[i];
      firstStageValues.push_back(x_i);
    }

    // Test feasibility of first stage constraints for given point
    std::vector<double> g1_result(_firstStageIneqEq.size());
    this->_DAGobj->DAG.eval(_g1_subgraph, _firstStageIneqEq.size(), _firstStageIneqEq.data(), g1_result.data(),
                            _TwoStageModel->Nx, this->_DAGobj->vars.data(), firstStageValues.data());

    // inequalities
    for (unsigned int i = 0; i < _TwoStageModel->Nineq1; i++) {
      if (g1_result[i] > UpperBoundingSolver::_maingoSettings->deltaIneq) {
        objectiveValue = INFINITY;
        return SUBSOLVER_INFEASIBLE;
      }
    }
    // squash Inequalities
    for (unsigned int i = _TwoStageModel->Nineq1; i < _TwoStageModel->Nineq1 + _TwoStageModel->Nsquash1; i++) {
      if (g1_result[i] > 0) {
        objectiveValue = INFINITY;
        return SUBSOLVER_INFEASIBLE;
      }
    }
    // equalities
    for (unsigned int i = _TwoStageModel->Nineq1 + _TwoStageModel->Nsquash1; i < _TwoStageModel->Nineq1 + _TwoStageModel->Nsquash1 + _TwoStageModel->Neq1; i++) {
      if (std::fabs(g1_result[i]) > UpperBoundingSolver::_maingoSettings->deltaEq) {
        objectiveValue = INFINITY;
        return SUBSOLVER_INFEASIBLE;
      }
    }

    bool infeasible = false;
    #ifdef _OPENMP
      #pragma omp parallel for
    #endif
    for (auto s = 0; s < _TwoStageModel->Ns; s++) {
      // Fix values of first stage variables
      std::vector<double> lowerVarBounds_s, upperVarBounds_s;
      for (auto &vec : {&lowerVarBounds_s, &upperVarBounds_s}) {
        vec->reserve(_TwoStageModel->Nx + _TwoStageModel->Ny);
        vec->insert(vec->end(), firstStageValues.begin(), firstStageValues.end());
      }
      // Add remaining bounds
      auto ys_begin = _TwoStageModel->Nx + s * _TwoStageModel->Ny;
      auto ys_end = ys_begin + _TwoStageModel->Ny;
      lowerVarBounds_s.insert(lowerVarBounds_s.end(),
                              lowerVarBounds.begin() + ys_begin,
                              lowerVarBounds.begin() + ys_end);
      upperVarBounds_s.insert(upperVarBounds_s.end(),
                              upperVarBounds.begin() + ys_begin,
                              upperVarBounds.begin() + ys_end);

      double objectiveValue_s = INFINITY;
      std::vector<double> solutionPoint_s;
      solutionPoint_s.insert(solutionPoint_s.end(), solutionPoint.begin(), solutionPoint.begin() + _TwoStageModel->Nx);
      solutionPoint_s.insert(solutionPoint_s.end(), solutionPoint.begin() + ys_begin, solutionPoint.begin() + ys_end);

      // Solve subproblems
      auto SUBSOLVER_RETCODE_s = _subsolvers[s]->_solve_nlp(
        lowerVarBounds_s,
        upperVarBounds_s,
        objectiveValue_s,
        solutionPoint_s
      );
      
      if (SUBSOLVER_RETCODE_s == SUBSOLVER_INFEASIBLE){
        infeasible = true;
      }
      // Update solutionPoint 
      std::copy(solutionPoint_s.begin() + _TwoStageModel->Nx, solutionPoint_s.end(), solutionPoint.begin() + ys_begin);
    }

    if (infeasible) {
      return SUBSOLVER_INFEASIBLE;
    }

    // Check if point returned by local solver is actually feasible. If it is, the objective function value will be stored as well.
    return subsolver_class::check_feasibility(solutionPoint, objectiveValue);
  }
};


/**
* @brief Factory function for initializing different TwoStage upper bounding solver wrappers
*
* @param[in] twoStageModel is the pointer to the TwoStageModel opbject
* @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
* @param[in] DAGvars are the variables corresponding to the DAG
* @param[in] DAGfunctions are the functions corresponding to the DAG
* @param[in] variables is a vector containing the initial optimization variables defined in problem.h
* @param[in] nineqIn is the number of inequality constraints
* @param[in] neqIn is the number of equality
* @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
* @param[in] settingsIn is a pointer to the MAiNGO settings
* @param[in] loggerIn is a pointer to the MAiNGO logger object
* @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
* @param[in] useIn is an ennum specifying the use of the UpperBoundingSolver (preprocessing of B&B)
*/
std::shared_ptr<UpperBoundingSolver> make_ubpTwoStage_solver(
  const std::shared_ptr<maingo::TwoStageModel> twoStageModel,
  mc::FFGraph &DAG,
  const std::vector<mc::FFVar> &DAGvars,
  const std::vector<mc::FFVar> &DAGfunctions,
  const std::vector<babBase::OptimizationVariable> &variables,
  const unsigned nineqIn,
  const unsigned neqIn,
  const unsigned nineqSquashIn,
  std::shared_ptr<Settings> settingsIn,
  std::shared_ptr<Logger> loggerIn,
  std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn,
  UpperBoundingSolver::UBS_USE useIn){
  UBP_SOLVER desiredSolver;
  std::string useDescription;
  switch (useIn) {
    case ubp::UpperBoundingSolver::USE_PRE:
      useDescription = "Two-stage multistart";
      desiredSolver  = settingsIn->UBP_solverPreprocessing;
      break;
    case ubp::UpperBoundingSolver::USE_BAB:
      useDescription = "Two-stage upper bounding";
      desiredSolver  = settingsIn->UBP_solverBab;
      break;
    default:
      throw MAiNGOException("  Error in UbsTwoStage Factory: unknown intended use for upper bounding solver.");  // GCOVR_EXCL_LINE
  }

  switch (desiredSolver) {
    case UBP_SOLVER_EVAL: {
      loggerIn->print_message("      " + useDescription + ": Function evaluation\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UpperBoundingSolver>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
    }
    case UBP_SOLVER_COBYLA: {
      loggerIn->print_message("      " + useDescription + ": COBYLA\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UbpNLopt>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
    }
    case UBP_SOLVER_BOBYQA: {
      loggerIn->print_message("      " + useDescription + ": BOBYQA\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UbpNLopt>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
    }
    case UBP_SOLVER_LBFGS: {
      loggerIn->print_message("      " + useDescription + ": LBFGS\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UbpNLopt>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
    }
    case UBP_SOLVER_SLSQP: {
      loggerIn->print_message("      " + useDescription + ": SLSQP\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UbpNLopt>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
    }
    case UBP_SOLVER_IPOPT: {
      loggerIn->print_message("      " + useDescription + ": IPOPT\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UbpIpopt>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
    }
    case UBP_SOLVER_KNITRO: {
#ifdef HAVE_KNITRO
      loggerIn->print_message("      " + useDescription + ": KNITRO\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UbpKnitro>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
#else
      throw MAiNGOException("  Error in UbsTwoStage Factory: Cannot use upper bounding strategy UBP_SOLVER_KNITRO: Your MAiNGO build does not contain KNITRO.");  // GCOVR_EXCL_LINE
#endif
    }
    case UBP_SOLVER_CPLEX: {
#ifdef HAVE_CPLEX
      loggerIn->print_message("      " + useDescription + ": CPLEX\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UbpCplex>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
#else
      throw MAiNGOException("  Error in UbsTwoStage Factory: Cannot use upper bounding strategy UBP_SOLVER_CPLEX: Your MAiNGO build does not contain CPLEX.");
#endif
    }
    case UBP_SOLVER_CLP: {
      loggerIn->print_message("      " + useDescription + ": CLP\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<UbsTwoStage<UbpClp>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
    }
    default:
    {  // GCOVR_EXCL_START
      std::ostringstream errmsg;
      errmsg << "  Error in UbsTwoStage Factory: Unknown upper bounding strategy: " << desiredSolver << std::endl;
      throw MAiNGOException("  Error in UbsTwoStage Factory: Unknown upper bounding strategy: " + std::to_string(desiredSolver));
    }
    // GCOVR_EXCL_STOP
  }
}


}    // end namespace ubp


}    // end namespace maingo
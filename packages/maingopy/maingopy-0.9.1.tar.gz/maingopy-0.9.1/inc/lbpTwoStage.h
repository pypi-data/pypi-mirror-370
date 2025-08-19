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

#include <map>

#include "instrumentor.h"

#include "babTree.h"

#include "logger.h"

#include "lbp.h"
#include "lbpClp.h"
#include "lbpInterval.h"
#include "lbpSubinterval.h"

#include "siblingResults.h"

#ifdef HAVE_CPLEX    // If Cmake has found CPLEX this pre-processor variable is set
  #include "lbpCplex.h"
#endif

#ifdef HAVE_GUROBI    // If Cmake has found Gurobi this pre-processor variable is set
    #include "lbpGurobi.h"
#endif

#ifdef _OPENMP   // If Cmake has found OpenMP this pre-processor variable is set
  #include <omp.h>
#endif

#include "TwoStageModel.h"

namespace maingo {

namespace lbp {

/**
 * @class LbpTwoStage
 * @brief Wrapper for handling the lower-bounding problems of two stage (stochastic) programming problems
 *
 * This class constructs one lower-bounding sub-problem solver per scenario and delegates solve calls to these subproblem solvers.
 */
template<class subsolver_class>
class LbpTwoStage : public subsolver_class {

  public:
    /**
     * @brief Constructor, stores information on the problem and initializes the sub-solver instances.
     *
     * @param[in] twoStageModel is the pointer to the TwoStageModel opbject
     * @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
     * @param[in] DAGvars are the variables corresponding to the DAG
     * @param[in] DAGfunctions are the functions corresponding to the DAG
     * @param[in] variables is a vector containing the initial optimization variables defined in problem.h
     * @param[in] nineqIn is the number of inequality constraints
     * @param[in] neqIn is the number of equality
     * @param[in] nineqRelaxationOnlyIn is the number of inequality for use only in the relaxed problem
     * @param[in] neqRelaxationOnlyIn is the number of equality constraints for use only in the relaxed problem
     * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
     * @param[in] settingsIn is a pointer to the MAiNGO settings
     * @param[in] loggerIn is a pointer to the MAiNGO logger object
     * @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
     */
    LbpTwoStage(const std::shared_ptr<maingo::TwoStageModel> twoStageModel,
                mc::FFGraph &DAG,
                const std::vector<mc::FFVar> &DAGvars,
                const std::vector<mc::FFVar> &DAGfunctions,
                const std::vector<babBase::OptimizationVariable> &variables,
                const std::vector<bool> &variableIsLinear,
                const unsigned nineqIn,
                const unsigned neqIn,
                const unsigned nineqRelaxationOnlyIn,
                const unsigned neqRelaxationOnlyIn,
                const unsigned nineqSquashIn,
                std::shared_ptr<Settings> settingsIn,
                std::shared_ptr<Logger> loggerIn,
                std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn):
        subsolver_class(DAG, DAGvars, DAGfunctions, variables, variableIsLinear,
                        nineqIn, neqIn, nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn,
                        settingsIn, loggerIn, constraintPropertiesIn),
        _TwoStageModel(twoStageModel), _No(2 << (twoStageModel->Ns - 1))
    {

        PROFILE_FUNCTION()

        _subproblemSolutions.resize(_TwoStageModel->Ns);
        _subproblemBounds.reserve(  // enough space for storing serialized sibling results
            1 * twoStageModel->Ns                                                    // parentSubproblemBounds
            + 2 * twoStageModel->Ns                                                  // objectiveBounds for both siblings
            + 2 * twoStageModel->Ns * (twoStageModel->Nx + twoStageModel->Ny)        // lower bounding solutions for both siblings
            + 2 * 2 * twoStageModel->Ns * (twoStageModel->Nx + twoStageModel->Ny)    // lower and upper bounds for all scenario subproblems of both siblings
        );
        _subproblemBounds.resize(_TwoStageModel->Ns);
        _subproblemDualInfo.resize(_TwoStageModel->Ns);

        LowerBoundingSolver::_lowerVarBounds.resize(LowerBoundingSolver::_nvar);
        LowerBoundingSolver::_upperVarBounds.resize(LowerBoundingSolver::_nvar);

        // Creating empty containers for each scenario
        SP_opt_variables.resize(_TwoStageModel->Ns);
        SP_DAGs = std::vector<mc::FFGraph>(_TwoStageModel->Ns);
        SP_DAG_variables.resize(_TwoStageModel->Ns);
        SP_DAG_x.resize(_TwoStageModel->Ns);
        SP_DAG_y.resize(_TwoStageModel->Ns);
        SP_DAG_functions.resize(_TwoStageModel->Ns);
        _subNodes.reserve(_TwoStageModel->Ns);

      // Filling the containers above
      #ifdef _OPENMP
        #pragma omp parallel for
      #endif
      for (int s = 0; s < _TwoStageModel->Ns; ++s) {
        PROFILE_SCOPE("LBS variable creation")

        _subproblemSolutions[s].reserve(_TwoStageModel->Nx + _TwoStageModel->Ny);
        _subproblemDualInfo[s].multipliers.reserve(_TwoStageModel->Nx + _TwoStageModel->Ny);

        SP_opt_variables[s].reserve(_TwoStageModel->Nx + _TwoStageModel->Ny);
        SP_DAG_variables[s].reserve(_TwoStageModel->Nx + _TwoStageModel->Ny);

        for (unsigned ix = 0; ix < _TwoStageModel->Nx; ++ix) {
          SP_opt_variables[s].push_back(variables[ix]);
          SP_DAG_variables[s].emplace_back(&SP_DAGs[s]);
          SP_DAG_x[s].push_back(SP_DAG_variables[s].back());
        }
      
        for (unsigned iy = 0; iy < _TwoStageModel->Ny; ++iy) {
          SP_opt_variables[s].push_back(variables[_TwoStageModel->Nx + s * _TwoStageModel->Ny + iy]);
          SP_DAG_variables[s].emplace_back(&SP_DAGs[s]);
          SP_DAG_y[s].push_back(SP_DAG_variables[s].back());
        }
      }
      std::vector<std::vector<std::vector<NamedVar>>> g1, g2;
      g1.reserve(_TwoStageModel->Ns);
      g2.reserve(_TwoStageModel->Ns);
      // This loop might need to happen sequentially, since _TwoStageModel may not be thread-safe (e.g. when defined via the Python API)
      for (int s = 0; s < _TwoStageModel->Ns; ++s) {
        PROFILE_SCOPE("LBS function evaluation")

        SP_DAG_functions[s].emplace_back(
          _TwoStageModel->f1_func(SP_DAG_x[s])
          + _TwoStageModel->f2_func(SP_DAG_x[s], SP_DAG_y[s], _TwoStageModel->data[s])
        );
        g1.emplace_back(_TwoStageModel->g1_func(SP_DAG_x[s]));
        g2.emplace_back(_TwoStageModel->g2_func(SP_DAG_x[s], SP_DAG_y[s], _TwoStageModel->data[s]));
      }

      SP_constraint_properties = std::vector<std::shared_ptr<std::vector<Constraint>>>(_TwoStageModel->Ns);
      _subsolvers.resize(_TwoStageModel->Ns);
      #ifdef _OPENMP
        #pragma omp parallel for
      #endif
      for (int s = 0; s < _TwoStageModel->Ns; ++s) {
        PROFILE_SCOPE("LBS constraint property creation")

        SP_constraint_properties[s] = std::make_shared<std::vector<Constraint>>();
        _prepare_constraints(std::to_string(s), SP_constraint_properties[s], SP_DAG_functions[s], g1[s], g2[s]);
        _subsolvers[s] = lbp::make_lbp_solver(
            SP_DAGs[s],
            SP_DAG_variables[s],  // [x_1, ..., x_Nx, y_s_1, ..., y_s_Ny]
            SP_DAG_functions[s],  // [f1+f2s, g1_1, ... g1_n, g2s_1, ..., g2s_m]
            SP_opt_variables[s],
            variableIsLinear,
            _TwoStageModel->Nineq1 + _TwoStageModel->Nineq2,
            _TwoStageModel->Neq1 + _TwoStageModel->Neq2,
            _TwoStageModel->NineqRelOnly1 + _TwoStageModel->NineqRelOnly2,
            _TwoStageModel->NeqRelOnly1 + _TwoStageModel->NeqRelOnly2,
            _TwoStageModel->Nsquash1 + _TwoStageModel->Nsquash2,
            settingsIn,
            LowerBoundingSolver::_logger,  // might get noisy with verbose output when solving in parallel...
            SP_constraint_properties[s],
            false
          );
      }
    }

    std::vector<mc::FFGraph> SP_DAGs;  // DAGs corresponding to subgraphs of single-scenario SP subproblems
    std::vector<std::vector<mc::FFVar>> SP_DAG_variables;  // copies of all variables
    std::vector<std::vector<mc::FFVar>> SP_DAG_functions;  // copies of FFVar objects representing objective and constraints for subproblems
    std::vector<std::vector<babBase::OptimizationVariable>> SP_opt_variables;
    std::vector<std::shared_ptr<std::vector<Constraint>>> SP_constraint_properties;  // Revised constraint properties
    // TODO: Do we really need these? --> Currently yes, due to the _TwoStageModel interface
    std::vector<std::vector<mc::FFVar>> SP_DAG_x;  // copies of first-stage variables from SP_DAG_variables
    std::vector<std::vector<mc::FFVar>> SP_DAG_y;  // copies of second-stage variables from SP_DAG_variables

    /**
     * @brief Function called by the B&B solver to heuristically activate more scaling in the LBS
     */
    void activate_more_scaling() override {
      for (auto & ss : _subsolvers) {
        ss->activate_more_scaling();
      }
    }

    /**
     * @brief Function called by B&B solver for optimality-based range reduction (cf., e.g., Gleixner et al., J. Glob. Optim. 67 (2017) 731)
     *
     * @param[in,out] currentNode is the B&B node for which the lower bounding problem should be solved; if OBBT is successful in tightening bounds, currentNode will be modified accordingly
     * @param[in] currentUBD is the current upper bounds (i.e., incumbent objective value); It is used for the objective function cut if reductionType==OBBT_FEASOPT
     * @param[in] reductionType determines whether OBBT should include only feasibility or also optimality (i.e., an objective function cut f_cv<=currentUBD)
     * @return Return code, see enum TIGHTENING_RETCODE
     */
    TIGHTENING_RETCODE solve_OBBT(babBase::BabNode &currentNode, const double currentUBD, const OBBT reductionType, const bool includeLinearVars) override {
      PROFILE_FUNCTION()

      if (currentNode.get_parent_ID() > 0 && LowerBoundingSolver::_maingoSettings->TS_parallelOBBT) {
        // use OBBT based on scenario subproblems
        return solve_parallel_OBBT(currentNode, currentUBD, reductionType, includeLinearVars);
      }

      /** NOTE: We cannot just do the straightforward thing below, because
       *        calls to the virtual functions from lbp will be redirected to
       *        the overridden functions in this class instead of the
       *        subsolver_class
       */
      // use OBBT based on deterministic equivalent
      // return subsolver_class::solve_OBBT(currentNode, currentUBD, reductionType);

      if ((reductionType == OBBT_FEAS) && LowerBoundingSolver::_onlyBoxConstraints)
      {
        return TIGHTENING_UNCHANGED;
      }

      std::vector<double> lowerVarBounds(currentNode.get_lower_bounds()), upperVarBounds(currentNode.get_upper_bounds());
      std::vector<double> originalWidth(LowerBoundingSolver::_nvar);
      for (size_t i = 0; i < LowerBoundingSolver::_nvar; ++i) {
        originalWidth[i] = upperVarBounds[i] - lowerVarBounds[i];
      }
      bool nodeChanged = false;
      // Update the LP for the current node (i.e., modify bounds and update coefficients and RHS)
      LINEARIZATION_RETCODE linStatus;
      try {
        PROFILE_SCOPE("OBBT_update_LP")
        linStatus = subsolver_class::_update_LP(currentNode);
      }
      catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while modifying the lower bounding LP for OBBT.", e, currentNode);
      }
      catch (...) {
        throw MAiNGOException("  Unknown error while modifying the lower bounding LP for OBBT.", currentNode);
      }
      // GCOVR_EXCL_STOP

      bool foundInfeasible = false;
      if (linStatus == LINEARIZATION_INFEASIBLE) {
        LowerBoundingSolver::_logger->print_message("  OBBT linearization status: Infeasible", VERB_ALL, LBP_VERBOSITY);

#ifdef MAiNGO_DEBUG_MODE
        if (_contains_incumbent(currentNode)) {
          const  bool reallyInfeasible = subsolver_class::_check_if_LP_really_infeasible();
          if (reallyInfeasible) {
  #ifdef LP__WRITE_CHECK_FILES
            _write_LP_to_file("solve_OBBT_infeas_at_linearization_with_incumbent_in_node");
  #endif
            if (currentNode.get_ID() == 0) {
              return TIGHTENING_INFEASIBLE;    // For the root node, we immediately want to report this false infeasibility claim since we want to completeley disable OBBT based on this information.
            }
            std::ostringstream outstr;
            outstr << "  Warning: Node with id " << currentNode.get_ID() << " declared infeasible by linearization technique in OBBT although it contains the incumbent. Skipping OBBT..." << std::endl;
            LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
          }
          else {
            LowerBoundingSolver::_logger->print_message("  Found node to not actually be infeasible. Problem seems to be difficult numerically. Skipping OBBT...", VERB_ALL, LBP_VERBOSITY);
          }
          return TIGHTENING_UNCHANGED;
        }
#endif  // MAiNGO_DEBUG_MODE
          foundInfeasible = true;
  #ifdef LP__OPTIMALITY_CHECK
          if (subsolver_class::_check_infeasibility(currentNode) == SUBSOLVER_FEASIBLE) {
            foundInfeasible = false;
          }
  #endif
      }

      // Only do OBBT if the LP was not found to be infeasible during the linearization
      if (!foundInfeasible) {
        // Prepare OBBT
        std::list<unsigned> toTreatMax, toTreatMin;
        std::vector<double> lastPoint(LowerBoundingSolver::_nvar);
        for (unsigned ivar = 0; ivar < LowerBoundingSolver::_nvar; ivar++) {    // Note that we also treat auxiliaries (if any are added)
          if (!LowerBoundingSolver::_variableIsLinear[ivar] || includeLinearVars) {
            toTreatMax.push_back(ivar);
            toTreatMin.push_back(ivar);
          }
          lastPoint[ivar] = 0.5 * (lowerVarBounds[ivar] + upperVarBounds[ivar]);
        }
        // Modify treatment of objective function
        switch (reductionType) {
          case OBBT_FEAS:    // Feasibility-based only
          {
            // Objective function is not needed in this case --> "deactivate" objective linearizations
            subsolver_class::_deactivate_objective_function_for_OBBT();
            break;
          }
          case OBBT_FEASOPT:    // including both feasibility and optimality
          {
            // Modify objective: remove eta and establish proper ubd
            subsolver_class::_modify_LP_for_feasopt_OBBT(currentUBD, toTreatMax, toTreatMin);
            break;
          }
          default:
          {  // GCOVR_EXCL_START
            std::ostringstream errmsg;
            errmsg << "  Unknown OBBT range reduction type: " << reductionType;
            throw MAiNGOException(errmsg.str(), currentNode);
          }
          // GCOVR_EXCL_STOP
        }

        // Loop over variable bounds until all variable bounds have either been treated by OBBT or filtered
        unsigned OBBTcnt  = 0;
        bool foundRelFeas = false;
        while ((toTreatMax.size() + toTreatMin.size()) > 0) {
          PROFILE_SCOPE("OBBT_loop")

          OBBTcnt++;
          // Select next candidate lower bound
          std::list<unsigned>::iterator tmpIt = toTreatMin.begin(), nextMinIt = toTreatMin.begin();
          double smallestDistanceMin = LowerBoundingSolver::_maingoSettings->infinity;
          if (foundRelFeas == true) {
            // Get minimum difference between last point and one lower variable bound, and use last point for trivial filtering (cf. Gleixner et al., J. Global Optim 67 (2017) 731)
            while (tmpIt != toTreatMin.end()) {
              double tmpDistance = (lastPoint[*tmpIt] - lowerVarBounds[*tmpIt]);
              double diameter    = upperVarBounds[*tmpIt] - lowerVarBounds[*tmpIt];
              if ((diameter < LowerBoundingSolver::_computationTol) || (tmpDistance <= diameter * LowerBoundingSolver::_maingoSettings->LBP_obbtMinImprovement)) {
                tmpIt = toTreatMin.erase(tmpIt);
              }
              else {
                if (tmpDistance < smallestDistanceMin) {
                  smallestDistanceMin = tmpDistance;
                  nextMinIt           = tmpIt;
                }
                tmpIt++;
              }
            }
          }
          else {
            // If no feasible (in relaxation) point was found, no need to search for the closest bound (first lower bound will be considered, if one exists)
            if (!toTreatMin.empty()) {
              smallestDistanceMin = 0;    // If there are still lower bounds to be treated, these get priority
            }
          }

          // Select next candidate upper bound
          std::list<unsigned>::iterator nextMaxIt = toTreatMax.begin();
          tmpIt                                   = toTreatMax.begin();
          double smallestDistanceMax              = LowerBoundingSolver::_maingoSettings->infinity;
          if (foundRelFeas == true) {
            // Get minimum difference between last point and one upper variable bound and use last point for trivial filtering (cf. Gleixner et al., J. Global Optim 67 (2017) 731)
            while (tmpIt != toTreatMax.end()) {
              double tmpDistance = (upperVarBounds[*tmpIt] - lastPoint[*tmpIt]);
              double diameter    = upperVarBounds[*tmpIt] - lowerVarBounds[*tmpIt];
              if ((diameter < LowerBoundingSolver::_computationTol) || (tmpDistance <= diameter * LowerBoundingSolver::_maingoSettings->LBP_obbtMinImprovement)) {
                tmpIt = toTreatMax.erase(tmpIt);
              }
              else {
                if (tmpDistance < smallestDistanceMax) {
                  smallestDistanceMax = tmpDistance;
                  nextMaxIt           = tmpIt;
                }
                tmpIt++;
              }
            }
          }
          else {
            // If no feasible (in relaxation) point was found, no need to search for the closest bound (first upper bound will be considered, if one exists)
            if (!toTreatMax.empty()) {
              smallestDistanceMax = 0.5;    // If there are still upper bounds to be treated, these should be considered (smallestDistanceMax<infinity), but lower bounds get priority (just to ensure reproducibility)
            }
          }

          // If the last variables left just got erased, there is nothing left to do:
          if ((smallestDistanceMax >= LowerBoundingSolver::_maingoSettings->infinity) && (smallestDistanceMin >= LowerBoundingSolver::_maingoSettings->infinity)) {
            break;
          }

          // Depending on which one is better (max or min), prepare OBBT
          unsigned iVar;                            // Index of the variable to be modified
          std::vector<double> *boundVector;         // Pointer to the bound vector to be modified
          std::vector<double> *otherBoundVector;    // Pointer to the bound vector that is not to be modified in the current run
          int optimizationSense;                    // 1: minimize, -1: maximize
          if (smallestDistanceMin <= smallestDistanceMax) {
            iVar = *nextMinIt;
            toTreatMin.erase(nextMinIt);
            boundVector       = &lowerVarBounds;
            otherBoundVector  = &upperVarBounds;
            optimizationSense = 1;    // 1 = minimize
          }
          else {
            iVar = *nextMaxIt;
            toTreatMax.erase(nextMaxIt);
            boundVector       = &upperVarBounds;
            otherBoundVector  = &lowerVarBounds;
            optimizationSense = -1;    // -1 = maximize
          }

          // Conduct OBBT: solve LP and update bound
          subsolver_class::_set_optimization_sense_of_variable(iVar, optimizationSense);    // Depending on whether we want to change upper or lower bound, use +1 or -1 as coefficient
          {
            PROFILE_SCOPE("OBBT_solve_LP")
            LowerBoundingSolver::_LPstatus = subsolver_class::_solve_LP(currentNode);
          }
          if (LowerBoundingSolver::_LPstatus == LP_INFEASIBLE) {

#ifdef MAiNGO_DEBUG_MODE
            if (_contains_incumbent(currentNode)) {
                const bool reallyInfeasible = _check_if_LP_really_infeasible();
                if (reallyInfeasible) {
  #ifdef LP__WRITE_CHECK_FILES
                _write_LP_to_file("solve_OBBT_infeas_with_incumbent_in_node");
  #endif
                if (currentNode.get_ID() == 0) {
                  subsolver_class::_restore_LP_coefficients_after_OBBT();
                  return TIGHTENING_INFEASIBLE;    // For the root node, we immediately want to report this false infeasibility claim since we want to completeley disable OBBT based on this information.
                }
                std::ostringstream outstr;
                outstr << "  Warning: Node with id " << currentNode.get_ID() << " declared infeasible by OBBT although it contains the incumbent. Skipping OBBT..." << std::endl;
                LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                break;
              }
              else {
                std::ostringstream outstr;
                outstr << "  Warning: Node with id " << currentNode.get_ID() << " is numerically sensitive in OBBT for bound " << iVar << " with sense " << optimizationSense << ". Skipping this bound..." << std::endl;
                LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                subsolver_class::_set_optimization_sense_of_variable(iVar, 0);
                continue;
              }
            }    // end of if (_contains_incumbent(currentNode))
#endif  // MAiNGO_DEBUG_MODE
            foundInfeasible = true;
#ifdef LP__OPTIMALITY_CHECK
            if (subsolver_class::_check_infeasibility(currentNode) == SUBSOLVER_FEASIBLE) {
              foundInfeasible = false;
              break;
            }
#endif
            LowerBoundingSolver::_logger->print_message("  OBBT status: " + std::to_string(LowerBoundingSolver::_LPstatus), VERB_ALL, LBP_VERBOSITY);

            break;
          }    // end of if(_LPstatus == LP_INFEASIBLE)
          else if (LowerBoundingSolver::_LPstatus != LP_OPTIMAL) {  // LP_UNKNOWN
            std::ostringstream outstr;
            outstr << "  Warning: No optimal solution found in OBBT. Status: " << LowerBoundingSolver::_LPstatus << ". Skipping OBBT..." << std::endl;
            LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
            break;
          }
          else {  // LP_OPTIMAL

            // Process solution: solution point to be used as "last point" in the next round
            std::vector<double> tmpPoint(LowerBoundingSolver::_nvar);
            double dummy = 0;
            try {
              subsolver_class::_get_solution_point(tmpPoint, dummy);
            }
            catch (std::exception &e) {  // GCOVR_EXCL_START
              std::ostringstream outstr;
              outstr << "  Warning: Variables at solution of OBBT could be not obtained by LP solver: " << e.what() << std::endl;
              LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
              subsolver_class::_set_optimization_sense_of_variable(iVar, 0);
              continue;
            }
            // GCOVR_EXCL_STOP
  #ifdef LP__OPTIMALITY_CHECK
            if (subsolver_class::_check_feasibility(tmpPoint) == SUBSOLVER_INFEASIBLE) {
              subsolver_class::_set_optimization_sense_of_variable(iVar, 0);
              continue;
            }
  #endif
            foundRelFeas = true;
            lastPoint    = tmpPoint;

            // Make sure the new bound makes sense and does not violate variable bounds
            double objectiveValue = subsolver_class::_get_objective_value_solver();

            if (!(objectiveValue >= (-LowerBoundingSolver::_maingoSettings->infinity))) {  // GCOVR_EXCL_START
              std::ostringstream outstr;
              outstr << "  Warning: Objective obtained from LP solver in OBBT is out of bounds (" << objectiveValue << ") although LP solution status is optimal. Skipping this bound." << std::endl;
              LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
              subsolver_class::_set_optimization_sense_of_variable(iVar, 0);
              continue;
            }
            // GCOVR_EXCL_STOP

            double newBound = optimizationSense * objectiveValue;    // Again depending on whether we want to change upper or lower bound, need to account for sign

#ifdef MAiNGO_DEBUG_MODE
            if (_contains_incumbent(currentNode)) {
              if (optimizationSense > 0) {    // Lower bound
                if (iVar < LowerBoundingSolver::_incumbent.size()) {
                  if (LowerBoundingSolver::_incumbent[iVar] < newBound) {
                    // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                    if (!mc::isequal(LowerBoundingSolver::_incumbent[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
#ifdef LP__WRITE_CHECK_FILES
                      subsolver_class::_write_LP_to_file("solve_OBBT_bound_infeas_with_incumbent_in_node");
#endif
                      std::ostringstream outstr;
                      outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and OBBT computed a lower bound for variable " << iVar << " which cuts off the incumbent. " << std::endl
                            << "           Correcting this bound and skipping OBBT... " << std::endl;
                      LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                    }
                    // We skip the bound, even if the bound is within computational tolerances
                    break;
                  }
                }
              }
              else {    // Upper bound
                if (iVar < LowerBoundingSolver::_incumbent.size()) {
                  if (LowerBoundingSolver::_incumbent[iVar] > newBound) {
                    // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                    if (!mc::isequal(LowerBoundingSolver::_incumbent[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                      std::ostringstream outstr;
                      outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and OBBT computed an upper bound for variable " << iVar << " which cuts off the incumbent. " << std::endl
                             << "           Correcting this bound and skipping OBBT... " << std::endl;
                      LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                    }
                    // We skip the bound, even if the bound is within computational tolerances
                    break;
                  }
                }
              }
            }
#endif  // MAiNGO_DEBUG_MODE

            double remainingWidth = optimizationSense * (*otherBoundVector)[iVar] - optimizationSense * newBound;
            if (remainingWidth < -LowerBoundingSolver::_computationTol) {
              if (LowerBoundingSolver::_originalVariables[iVar].get_variable_type() >= babBase::enums::VT_BINARY /* this includes VT_INTEGER */) {
                // The problem is found to be infeasible, since, e.g., lb of variable 1 was tightened to 3.2 and was then set to 4. Later on ub of variable 1 is tightened to 3.6 and thus set to 3,
                // meaning that this node is infeasible
                // This could be extended to saving the old lb value 3.2 and checking if it does not cross the new ub value 3.6
                subsolver_class::_restore_LP_coefficients_after_OBBT();
                return TIGHTENING_INFEASIBLE;
              }
              // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
              if (!mc::isequal(optimizationSense * newBound, optimizationSense * (*otherBoundVector)[iVar], LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                std::ostringstream outstr;
                outstr << "  Warning: Bounds crossover for variable " << iVar << " during OBBT with optimizationSense " << optimizationSense << ":" << std::endl;
                if (optimizationSense > 0) {
                  outstr << std::setprecision(16) << "  Lower Bound = " << newBound << " > " << std::setprecision(16) << (*otherBoundVector)[iVar] << " = Upper Bound. Skipping this bound." << std::endl;
                }
                else {
                  outstr << std::setprecision(16) << "  Upper Bound = " << newBound << " < " << std::setprecision(16) << (*otherBoundVector)[iVar] << " = Lower Bound. Skipping this bound." << std::endl;
                }
                LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
              }
              subsolver_class::_set_optimization_sense_of_variable(iVar, 0);
              continue;
            }
            else {

              // Update bound
              if (remainingWidth < LowerBoundingSolver::_computationTol) {
                // Can't surely set bounds equal, there is the possibility that we make the LP infeasible although it isn't !
                // (*boundVector)[iVar] = (*otherBoundVector)[iVar];
              }
              else {
                switch (LowerBoundingSolver::_originalVariables[iVar].get_variable_type()) {
                  case babBase::enums::VT_CONTINUOUS:
                    // Only update bounds if difference is larger than tolerance
                    if (!mc::isequal((*boundVector)[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                      nodeChanged          = true;
                      (*boundVector)[iVar] = newBound;
                    }
                    break;
                  case babBase::enums::VT_BINARY:
                    // Round bounds to ensure binary values
                    if (optimizationSense > 0) {    // Lower bound
                      if (!mc::isequal(newBound, 0, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                        nodeChanged          = true;
                        (*boundVector)[iVar] = 1;
                      }
                      // Integer bounds crossing => node is infeasible
                      if ((*boundVector)[iVar] > upperVarBounds[iVar]) {
                        subsolver_class::_restore_LP_coefficients_after_OBBT();
                        return TIGHTENING_INFEASIBLE;
                      }
                    }
                    else {    // Upper bound
                      if (!mc::isequal(newBound, 1, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                        nodeChanged          = true;
                        (*boundVector)[iVar] = 0;
                      }
                      // Integer bounds crossing => node is infeasible
                      if ((*boundVector)[iVar] < lowerVarBounds[iVar]) {
                        subsolver_class::_restore_LP_coefficients_after_OBBT();
                        return TIGHTENING_INFEASIBLE;
                      }
                    }
                    break;
                  case babBase::enums::VT_INTEGER:
                    // Round bounds to ensure integer values
                    if (optimizationSense > 0) {    // Lower bound
                      if (!mc::isequal(newBound, std::floor(newBound), LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                        newBound = std::ceil(newBound);
                      }
                      else {
                        newBound = std::floor(newBound);
                      }
                      if (!mc::isequal((*boundVector)[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                        nodeChanged          = true;
                        (*boundVector)[iVar] = newBound;
                      }
                      // Integer bounds crossing => node is infeasible
                      if ((*boundVector)[iVar] > upperVarBounds[iVar]) {
                        subsolver_class::_restore_LP_coefficients_after_OBBT();
                        return TIGHTENING_INFEASIBLE;
                      }
                    }
                    else {    // Upper bound
                      if (!mc::isequal(newBound, std::ceil(newBound), LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                        newBound = std::floor(newBound);
                      }
                      else {
                        newBound = std::ceil(newBound);
                      }
                      if (!mc::isequal((*boundVector)[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                        nodeChanged          = true;
                        (*boundVector)[iVar] = newBound;
                      }
                      // Integer bounds crossing => node is infeasible
                      if ((*boundVector)[iVar] < lowerVarBounds[iVar]) {
                        subsolver_class::_restore_LP_coefficients_after_OBBT();
                        return TIGHTENING_INFEASIBLE;
                      }
                    }
                    break;
                  default:
                    throw MAiNGOException("  Error while solving OBBT: Unknown variable type.");  // GCOVR_EXCL_LINE
                    break;
                }  // end switch
              }
            }
            // Restore objective coefficient
            subsolver_class::_set_optimization_sense_of_variable(iVar, 0);
          }
        }    // End of OBBT while loop
      }        // End of if(!foundInfeasible)

      // Restore proper objective function and restore LP solver options
      subsolver_class::_restore_LP_coefficients_after_OBBT();

      // Return appropriate return code and possibly update currentNode with new bounds
      if (foundInfeasible) {
        return TIGHTENING_INFEASIBLE;
      }
      else {
        if (!nodeChanged) {
          return TIGHTENING_UNCHANGED;
        }
        else {
          currentNode = babBase::BabNode(currentNode, lowerVarBounds, upperVarBounds);
          return TIGHTENING_CHANGED;
        }  // End of if (!nodeChanged)
      }  // End of if (foundInfeasible)
    }  // End of solveOBBT()


    /**
     * @brief Function called by B&B solver for parallel optimality-based range reduction (cf., e.g., Gleixner et al., J. Glob. Optim. 67 (2017) 731)
     *
     * @param[in,out] currentNode is the B&B node for which the lower bounding problem should be solved; if OBBT is successful in tightening bounds, currentNode will be modified accordingly
     * @param[in] currentUBD is the current upper bounds (i.e., incumbent objective value); It is used for the objective function cut if reductionType==OBBT_FEASOPT
     * @param[in] reductionType determines whether OBBT should include only feasibility or also optimality (i.e., an objective function cut f_cv<=currentUBD)
     * @return Return code, see enum TIGHTENING_RETCODE
     */
    TIGHTENING_RETCODE solve_parallel_OBBT(babBase::BabNode &currentNode, const double currentUBD, const OBBT reductionType, const bool includeLinearVars) {
      PROFILE_FUNCTION()

      if ((reductionType == OBBT_FEAS) && LowerBoundingSolver::_onlyBoxConstraints) {
        return TIGHTENING_UNCHANGED;
      }

      std::vector<double> lowerVarBounds(currentNode.get_lower_bounds()), upperVarBounds(currentNode.get_upper_bounds());
      std::vector<double> originalWidth(LowerBoundingSolver::_nvar);
      for (size_t i = 0; i < LowerBoundingSolver::_nvar; i++) {
        originalWidth[i] = upperVarBounds[i] - lowerVarBounds[i];
      }

      // Update the LP for the current node (i.e., modify bounds and update coefficients and RHS)
      LINEARIZATION_RETCODE linStatus;
      try {
        PROFILE_SCOPE("OBBT_update_LP")
        linStatus = _update_LP(currentNode);
      }
      catch (std::exception &e) {  // GCOVR_EXCL_START
        throw MAiNGOException("  Error while modifying the lower bounding LP for OBBT.", e, currentNode);
      }
      catch (...) {
        throw MAiNGOException("  Unknown error while modifying the lower bounding LP for OBBT.", currentNode);
      }
      // GCOVR_EXCL_STOP

      bool foundInfeasible = false;
      if (linStatus == LINEARIZATION_INFEASIBLE) {
          LowerBoundingSolver::_logger->print_message("  OBBT linearization status: Infeasible", VERB_ALL, LBP_VERBOSITY);

#ifdef MAiNGO_DEBUG_MODE
        if (_contains_incumbent(currentNode)) {
            const bool reallyInfeasible = _check_if_LP_really_infeasible();
          if (reallyInfeasible) {
  #ifdef LP__WRITE_CHECK_FILES
            _write_LP_to_file("solve_OBBT_infeas_at_linearization_with_incumbent_in_node");
  #endif
            if (currentNode.get_ID() == 0) {
              return TIGHTENING_INFEASIBLE;    // For the root node, we immediately want to report this false infeasibility claim since we want to completeley disable OBBT based on this information.
            }
            std::ostringstream outstr;
            outstr << "  Warning: Node with id " << currentNode.get_ID() << " declared infeasible by linearization technique in OBBT although it contains the incumbent. Skipping OBBT..." << std::endl;
            LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
          }
          else {
            LowerBoundingSolver::_logger->print_message("  Found node to not actually be infeasible. Problem seems to be difficult numerically. Skipping OBBT...", VERB_NORMAL, LBP_VERBOSITY);
          }
          return TIGHTENING_UNCHANGED;
        }
#endif  // MAiNGO_DEBUG_MODE

          foundInfeasible = true;
  #ifdef LP__OPTIMALITY_CHECK
          if (_check_infeasibility(currentNode) == SUBSOLVER_FEASIBLE) {
            foundInfeasible = false;
          }
  #endif
      }

      bool nodeChanged = false;
      // Only do OBBT if the LP was not found to be infeasible during the linearization
      if (!foundInfeasible) {
        // Prepare OBBT
        std::list<unsigned> toTreatMax, toTreatMin;
        // minimum and maximum values encountered to be feasible in the relaxation, used for filtering
        // initialized with the respective opposite bounds of the current node
        std::vector<double> min_vals = upperVarBounds;
        std::vector<double> max_vals = lowerVarBounds;
        // pOBBT is done in the space of the subproblem variables, i.e., only for Nx + Ny variables
        for (unsigned ivar = 0; ivar < (int)(_TwoStageModel->Nx + _TwoStageModel->Ny); ivar++) {    // Note that we also treat auxiliaries (if any are added)
          if (!LowerBoundingSolver::_variableIsLinear[ivar] || includeLinearVars) {
            toTreatMax.push_back(ivar);
            toTreatMin.push_back(ivar);
          }
        }
        // Modify treatment of objective function
        switch (reductionType) {
          case OBBT_FEAS:    // Feasibility-based only
          {
            // Objective function is not needed in this case --> "deactivate" objective linearizations
            for (auto & ss : _subsolvers) {
              ss->_deactivate_objective_function_for_OBBT();
            }
            break;
          }
          case OBBT_FEASOPT:    // including both feasibility and optimality
          {
            for (unsigned int s = 0; s < _TwoStageModel->Ns; s++) {
              double scenarioUBD = _calculate_scenario_UBD(s, currentUBD);
              // Modify objective: remove eta and establish proper ubd 
              _subsolvers[s]->_modify_LP_for_feasopt_OBBT(scenarioUBD, toTreatMax, toTreatMin);
            }
            break;
          }
          default:
          {  // GCOVR_EXCL_START
            std::ostringstream errmsg;
            errmsg << "  Unknown OBBT range reduction type: " << reductionType;
            throw MAiNGOException(errmsg.str(), currentNode);
          }
          // GCOVR_EXCL_STOP
        }
        // Loop over variable bounds until all variable bounds have either been treated by OBBT or filtered
        unsigned OBBTcnt  = 0;
        bool foundRelFeas = false;
        while ((toTreatMax.size() + toTreatMin.size()) > 0) {
          PROFILE_SCOPE("OBBT_loop")

          OBBTcnt++;
          // Select next candidate lower bound
          std::list<unsigned>::iterator tmpIt = toTreatMin.begin(), nextMinIt = toTreatMin.begin();
          double smallestDistanceMin = LowerBoundingSolver::_maingoSettings->infinity;
          if (foundRelFeas == true) {
            // Get minimum difference between last point and one lower variable bound, and use last point for trivial filtering (cf. Gleixner et al., J. Global Optim 67 (2017) 731)
            while (tmpIt != toTreatMin.end()) {
              double tmpDistance = (min_vals[*tmpIt] - lowerVarBounds[*tmpIt]);
              double diameter    = upperVarBounds[*tmpIt] - lowerVarBounds[*tmpIt];
              if ((diameter < LowerBoundingSolver::_computationTol) || (tmpDistance <= diameter * LowerBoundingSolver::_maingoSettings->LBP_obbtMinImprovement)) {
                tmpIt = toTreatMin.erase(tmpIt);
              }
              else {
                if (tmpDistance < smallestDistanceMin) {
                  smallestDistanceMin = tmpDistance;
                  nextMinIt           = tmpIt;
                }
                tmpIt++;
              }
            }
          }
          else {
            // If no feasible (in relaxation) point was found, no need to search for the closest bound (first lower bound will be considered, if one exists)
            if (!toTreatMin.empty()) {
              smallestDistanceMin = 0;    // If there are still lower bounds to be treated, these get priority
            }
          }

          // Select next candidate upper bound
          std::list<unsigned>::iterator nextMaxIt = toTreatMax.begin();
          tmpIt                                   = toTreatMax.begin();
          double smallestDistanceMax              = LowerBoundingSolver::_maingoSettings->infinity;
          if (foundRelFeas == true) {
            // Get minimum difference between last point and one upper variable bound and use last point for trivial filtering (cf. Gleixner et al., J. Global Optim 67 (2017) 731)
            while (tmpIt != toTreatMax.end()) {
              double tmpDistance = (upperVarBounds[*tmpIt] - max_vals[*tmpIt]);
              double diameter    = upperVarBounds[*tmpIt] - lowerVarBounds[*tmpIt];
              if ((diameter < LowerBoundingSolver::_computationTol) || (tmpDistance <= diameter * LowerBoundingSolver::_maingoSettings->LBP_obbtMinImprovement)) {
                tmpIt = toTreatMax.erase(tmpIt);
              }
              else {
                if (tmpDistance < smallestDistanceMax) {
                  smallestDistanceMax = tmpDistance;
                  nextMaxIt           = tmpIt;
                }
                tmpIt++;
              }
            }
          }
          else {
            // If no feasible (in relaxation) point was found, no need to search for the closest bound (first upper bound will be considered, if one exists)
            if (!toTreatMax.empty()) {
              smallestDistanceMax = 0.5;    // If there are still upper bounds to be treated, these should be considered (smallestDistanceMax<infinity), but lower bounds get priority (just to ensure reproducibility)
            }
          }

          // If the last variables left just got erased, there is nothing left to do:
          if ((smallestDistanceMax >= LowerBoundingSolver::_maingoSettings->infinity) && (smallestDistanceMin >= LowerBoundingSolver::_maingoSettings->infinity)) {
            break;
          }

          // Depending on which one is better (max or min), prepare OBBT
          unsigned iVar;                            // Index of the variable to be modified
          std::vector<double> *boundVector;         // Pointer to the bound vector to be modified
          std::vector<double> *otherBoundVector;    // Pointer to the bound vector that is not to be modified in the current run
          int optimizationSense;                    // 1: minimize, -1: maximize
          if (smallestDistanceMin <= smallestDistanceMax) {
            iVar = *nextMinIt;
            toTreatMin.erase(nextMinIt);
            boundVector       = &lowerVarBounds;
            otherBoundVector  = &upperVarBounds;
            optimizationSense = 1;    // 1 = minimize
          }
          else {
            iVar = *nextMaxIt;
            toTreatMax.erase(nextMaxIt);
            boundVector       = &upperVarBounds;
            otherBoundVector  = &lowerVarBounds;
            optimizationSense = -1;    // -1 = maximize
          }

          // Conduct OBBT: solve LP and update bound
          int iyVar = iVar - _TwoStageModel->Nx;  // Index offset by number of variables in first stage
          for (int s = 0; s < _TwoStageModel->Ns; s++) {
            _subsolvers[s]->_set_optimization_sense_of_variable(iVar, optimizationSense);
          }
          _solve_subproblem_LPs(currentNode, "OBBT"); // updates LowerBoundingSolver::_LPstatus

          if (LowerBoundingSolver::_LPstatus == LP_INFEASIBLE) {  /** NOTE: This infeasibility can also occur due to the objective cut (i.e., the node is dominated), not only because the node is infeasible! */
            std::ostringstream outstr;
            outstr << "  LP Obbt status: Infeasible" << std::endl;
            LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_ALL, LBP_VERBOSITY);

#ifdef MAiNGO_DEBUG_MODE
            if (_contains_incumbent(currentNode)) {
              const bool reallyInfeasible = _check_if_LP_really_infeasible();
              if (reallyInfeasible) {
  #ifdef LP__WRITE_CHECK_FILES
                _write_LP_to_file("solve_OBBT_infeas_with_incumbent_in_node");
  #endif
                // For the root node, we immediately want to report this false infeasibility claim since we want to completeley disable OBBT based on this information.
                if (currentNode.get_ID() == 0) {
                  _restore_LP_coefficients_after_OBBT();
                  return TIGHTENING_INFEASIBLE;
                }
                std::ostringstream outstr;
                outstr << "  Warning: Node with id " << currentNode.get_ID() << " declared infeasible by OBBT although it contains the incumbent. Skipping OBBT..." << std::endl;
                LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                break;
              }
              else {
                std::ostringstream outstr;
                outstr << "  Warning: Node with id " << currentNode.get_ID() << " is numerically sensitive in OBBT for bound " << iVar << " with sense " << optimizationSense << ". Skipping this bound..." << std::endl;
                LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                
                for (int s = 0; s < _TwoStageModel->Ns; s++) {
                  _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
                };
                continue;
              }
            }    // end of if (_contains_incumbent(currentNode))
#endif  // MAiNGO_DEBUG_MODE
            foundInfeasible = true;
#ifdef LP__OPTIMALITY_CHECK
            if (_check_infeasibility(currentNode) == SUBSOLVER_FEASIBLE) {
              foundInfeasible = false;
              break;
            }
#endif
            outstr.str("");
            outstr.clear();
            outstr << "  OBBT status: " << LowerBoundingSolver::_LPstatus << std::endl;
            LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_ALL, LBP_VERBOSITY);

            break;
          }    // end of if(_LPstatus == LP_INFEASIBLE)
          else if (LowerBoundingSolver::_LPstatus != LP_OPTIMAL) {  // LP_UNKNOWN // GCOVR_EXCL_START
            std::ostringstream outstr;
            outstr << "  Warning: No optimal solution found in OBBT. Status: " << LowerBoundingSolver::_LPstatus << ". Skipping OBBT..." << std::endl;
            LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
            break;
          }
          // GCOVR_EXCL_STOP
          else {  // LP_OPTIMAL

            // New point to be used for filtering
            try {
              for (int s = 0; s < _TwoStageModel->Ns; s++) {
                // write directly to private members _subproblemSolutions and _subproblemDualInfo
                auto & solution_s = _subproblemSolutions[s];
                auto & obj_s = _subproblemDualInfo[s].lpLowerBound;
                _subsolvers[s]->_get_solution_point(solution_s, obj_s);

                for (int i = 0; i < (int)(_TwoStageModel->Nx + _TwoStageModel->Ny); i++) {
                  if (solution_s[i] < min_vals[i]) {
                    min_vals[i] = solution_s[i];
                  }
                  if (solution_s[i] > max_vals[i]) {
                    max_vals[i] = solution_s[i];
                  }
                }
              }
            }
            catch (std::exception &e) {  // GCOVR_EXCL_START
              std::ostringstream outstr;
              outstr << "  Warning: Variables at solution of OBBT could be not obtained by LP solver: " << e.what() << std::endl;
              LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
              for (int s = 0; s < _TwoStageModel->Ns; s++) {
                _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
              };
              continue;
            }
            // GCOVR_EXCL_STOP
  #ifdef LP__OPTIMALITY_CHECK
            if (_check_feasibility({} /* UNUSED */) == SUBSOLVER_INFEASIBLE) {
              for (int s = 0; s < _TwoStageModel->Ns; s++) {
                _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
              };
              continue;
            }
  #endif
            foundRelFeas = true;  // This activates filtering

            // Make sure the new bound makes sense and does not violate variable bounds
            std::vector<double> objectiveValues(_TwoStageModel->Ns);
            for (int s = 0; s < _TwoStageModel->Ns; s++) {
              objectiveValues[s] = _subsolvers[s]->_get_objective_value_solver();
            }
            if (iyVar < 0) { // x variable, aggregate objective value
              double objectiveValue;
              if (optimizationSense > 0) { // Lower bound, take the maximum
                objectiveValue = *std::max_element(objectiveValues.begin(), objectiveValues.end());
              }
              else { // Upper bound, take the minimum
                objectiveValue = *std::min_element(objectiveValues.begin(), objectiveValues.end());
              }

              if (!(objectiveValue >= (-LowerBoundingSolver::_maingoSettings->infinity))) { // GCOVR_EXCL_START
                std::ostringstream outstr;
                outstr << "  Warning: Objective obtained from LP solver in OBBT is out of bounds (" << objectiveValue << ") although LP solution status is optimal. Skipping this bound." << std::endl;
                LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                for (int s = 0; s < _TwoStageModel->Ns; s++) {
                  _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
                }
                
                continue;
              }
              // GCOVR_EXCL_STOP

              double newBound = optimizationSense * objectiveValue;    // Again depending on whether we want to change upper or lower bound, need to account for sign
#ifdef MAiNGO_DEBUG_MODE
              if (_contains_incumbent(currentNode)) {
                if (optimizationSense > 0) {    // Lower bound
                  if (iVar < LowerBoundingSolver::_incumbent.size()) {
                    if (LowerBoundingSolver::_incumbent[iVar] < newBound) {
                      // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                      if (!mc::isequal(LowerBoundingSolver::_incumbent[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
  #ifdef LP__WRITE_CHECK_FILES
                        // x variable, write all subproblems
                        for (int s = 0; s < _TwoStageModel->Ns; s++) {
                            _subsolvers[s]->_write_LP_to_file("solve_OBBT_bound_infeas_with_incumbent_in_node_" + std::to_string(s));
                        }
  #endif
                        std::ostringstream outstr;
                        outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and OBBT computed a lower bound for variable " << iVar << " which cuts off the incumbent. " << std::endl
                              << "           Correcting this bound and skipping OBBT... " << std::endl;
                        LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                      }
                      // We skip the bound, even if the bound is within computational tolerances
                      break;
                    }
                  }
                }
                else {    // Upper bound
                  if (iVar < LowerBoundingSolver::_incumbent.size()) {
                    if (LowerBoundingSolver::_incumbent[iVar] > newBound) {
                      // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                      if (!mc::isequal(LowerBoundingSolver::_incumbent[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                        std::ostringstream outstr;
                        outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and OBBT computed an upper bound for variable " << iVar << " which cuts off the incumbent. " << std::endl
                                << "           Correcting this bound and skipping OBBT... " << std::endl;
                        LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                      }
                      // We skip the bound, even if the bound is within computational tolerances
                      break;
                    }
                  }
                }
              }
#endif  // MAiNGO_DEBUG_MODE

              double remainingWidth = optimizationSense * (*otherBoundVector)[iVar] - optimizationSense * newBound;
              if (remainingWidth < -LowerBoundingSolver::_computationTol) {
                // unlike in standard OBBT even for continuous variables this is not an indication of an error but of infeasibility, since we aggregate first-stage variable domains over all scenarios
                _restore_LP_coefficients_after_OBBT();
                return TIGHTENING_INFEASIBLE;
              }
              else {

                // Update bound
                if (remainingWidth < LowerBoundingSolver::_computationTol) {
                  // Can't safely set bounds equal, there is the possibility that we make the LP infeasible although it isn't !
                  // (*boundVector)[iVar] = (*otherBoundVector)[iVar];
                }
                else {
                  switch (LowerBoundingSolver::_originalVariables[iVar].get_variable_type()) {
                    case babBase::enums::VT_CONTINUOUS:
                      // Only update bounds if difference is larger than tolerance
                      if (!mc::isequal((*boundVector)[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                        nodeChanged          = true;
                        (*boundVector)[iVar] = newBound;
                      }
                      break;
                    case babBase::enums::VT_BINARY:
                      // Round bounds to ensure binary values
                      if (optimizationSense > 0) {    // Lower bound
                        if (!mc::isequal(newBound, 0, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                          nodeChanged          = true;
                          (*boundVector)[iVar] = 1;
                        }
                        // Integer bounds crossing => node is infeasible
                        if ((*boundVector)[iVar] > upperVarBounds[iVar]) {
                          _restore_LP_coefficients_after_OBBT();
                          return TIGHTENING_INFEASIBLE;
                        }
                      }
                      else {    // Upper bound
                        if (!mc::isequal(newBound, 1, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                          nodeChanged          = true;
                          (*boundVector)[iVar] = 0;
                        }
                        // Integer bounds crossing => node is infeasible
                        if ((*boundVector)[iVar] < lowerVarBounds[iVar]) {
                          _restore_LP_coefficients_after_OBBT();
                          return TIGHTENING_INFEASIBLE;
                        }
                      }
                      break;
                    case babBase::enums::VT_INTEGER:
                      // Round bounds to ensure integer values
                      if (optimizationSense > 0) {    // Lower bound
                        if (!mc::isequal(newBound, std::floor(newBound), LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                          newBound = std::ceil(newBound);
                        }
                        else {
                          newBound = std::floor(newBound);
                        }
                        if (!mc::isequal((*boundVector)[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                          nodeChanged          = true;
                          (*boundVector)[iVar] = newBound;
                        }
                        // Integer bounds crossing => node is infeasible
                        if ((*boundVector)[iVar] > upperVarBounds[iVar]) {
                          _restore_LP_coefficients_after_OBBT();
                          return TIGHTENING_INFEASIBLE;
                        }
                      }
                      else {    // Upper bound
                        if (!mc::isequal(newBound, std::ceil(newBound), LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                          newBound = std::floor(newBound);
                        }
                        else {
                          newBound = std::ceil(newBound);
                        }
                        if (!mc::isequal((*boundVector)[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                          nodeChanged          = true;
                          (*boundVector)[iVar] = newBound;
                        }
                        // Integer bounds crossing => node is infeasible
                        if ((*boundVector)[iVar] < lowerVarBounds[iVar]) {
                          _restore_LP_coefficients_after_OBBT();
                          return TIGHTENING_INFEASIBLE;
                        }
                      }
                      break;
                    default:
                      throw MAiNGOException("  Error while solving OBBT: Unknown variable type.");  // GCOVR_EXCL_LINE
                      break;
                  }  // end switch
                }
              }
              // Restore objective coefficient for x variable, restore coefficient in all subproblems
              for (int s = 0; s < _TwoStageModel->Ns; s++) {
                _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
              }
            } // end if (x variable)
            else { // y variable, use all objective values
              bool obj_out_of_bounds = false;
              bool return_infeasible = false;

              #ifdef _OPENMP
                #pragma omp parallel for
              #endif
              for (int s = 0; s < _TwoStageModel->Ns; s++) {
                if (!(objectiveValues[s] >= (-LowerBoundingSolver::_maingoSettings->infinity))) {  // GCOVR_EXCL_START
                  std::ostringstream outstr;
                  outstr << "  Warning: Objective obtained from LP solver in OBBT is out of bounds (" << objectiveValues[s] << ") although LP solution status is optimal. Skipping this bound." << std::endl;
                  LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                  obj_out_of_bounds = true;
                  
                  // break;
                  continue;
                }  // GCOVR_EXCL_STOP

                double newBound = optimizationSense * objectiveValues[s];    // Again depending on whether we want to change upper or lower bound, need to account for sign

#ifdef MAiNGO_DEBUG_MODE
                if (_contains_incumbent(currentNode)) {
                  if (optimizationSense > 0) {    // Lower bound
                    if (iVar < _subsolvers[s]->_incumbent.size()) {
                      if (_subsolvers[s]->_incumbent[iVar] < newBound) {
                        // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                        if (!mc::isequal(_subsolvers[s]->_incumbent[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
    #ifdef LP__WRITE_CHECK_FILES
                          // y variable, write only the corresponding subproblem
                          _subsolvers[s]->_write_LP_to_file("solve_OBBT_bound_infeas_with_incumbent_in_node" + std::to_string(s));
    #endif
                          std::ostringstream outstr;
                          outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and OBBT computed a lower bound for variable " << iVar << " which cuts off the incumbent. " << std::endl
                                << "           Correcting this bound and skipping OBBT... " << std::endl;
                          LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                        }
                        // We skip the bound, even if the bound is within computational tolerances
                        // break;
                        continue;
                      }
                    }
                  }
                  else {    // Upper bound
                    if (iVar < _subsolvers[s]->_incumbent.size()) {
                      if (_subsolvers[s]->_incumbent[iVar] > newBound) {
                        // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                        if (!mc::isequal(_subsolvers[s]->_incumbent[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                          std::ostringstream outstr;
                          outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and OBBT computed an upper bound for variable " << iVar << " which cuts off the incumbent. " << std::endl
                                  << "           Correcting this bound and skipping OBBT... " << std::endl;
                          LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                        }
                        // We skip the bound, even if the bound is within computational tolerances
                        //break;
                        continue;
                      }
                    }
                  }
                }
#endif  // MAiNGO_DEBUG_MODE

                int iTotalVar = _TwoStageModel->Nx + _TwoStageModel->Ny * s + iyVar;

                double remainingWidth = optimizationSense * (*otherBoundVector)[iTotalVar] - optimizationSense * newBound;
                if (remainingWidth < -LowerBoundingSolver::_computationTol) {
                  if (LowerBoundingSolver::_originalVariables[iTotalVar].get_variable_type() >= babBase::enums::VT_BINARY /* this includes VT_INTEGER */) {
                    // The problem is found to be infeasible, since, e.g., lb of variable 1 was tightened to 3.2 and was then set to 4. Later on ub of variable 1 is tightened to 3.6 and thus set to 3,
                    // meaning that this node is infeasible
                    // This could be extended to saving the old lb value 3.2 and checking if it does not cross the new ub value 3.6
                    _subsolvers[s]->_restore_LP_coefficients_after_OBBT();
                   
                    // return TIGHTENING_INFEASIBLE;
                    return_infeasible = true;
                    continue;
                  }
                  // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                  if (!mc::isequal(optimizationSense * newBound, optimizationSense * (*otherBoundVector)[iTotalVar], LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                    std::ostringstream outstr;
                    outstr << "  Warning: Bounds crossover for variable " << iTotalVar << " during OBBT with optimizationSense " << optimizationSense << ":" << std::endl;
                    if (optimizationSense > 0) {
                      outstr << std::setprecision(16) << "  Lower Bound = " << newBound << " > " << std::setprecision(16) << (*otherBoundVector)[iTotalVar] << " = Upper Bound. Skipping this bound." << std::endl;
                    }
                    else {
                      outstr << std::setprecision(16) << "  Upper Bound = " << newBound << " < " << std::setprecision(16) << (*otherBoundVector)[iTotalVar] << " = Lower Bound. Skipping this bound." << std::endl;
                    }
                    LowerBoundingSolver::_logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                  }
                  _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
                  continue;
                }
                else {

                  // Update bound
                  if (remainingWidth < LowerBoundingSolver::_computationTol) {
                    // Can't safely set bounds equal, there is the possibility that we make the LP infeasible although it isn't !
                    // (*boundVector)[iVar] = (*otherBoundVector)[iVar];
                  }
                  else {
                    switch (LowerBoundingSolver::_originalVariables[iTotalVar].get_variable_type()) {
                      case babBase::enums::VT_CONTINUOUS:
                        // Only update bounds if difference is larger than tolerance
                        if (!mc::isequal((*boundVector)[iTotalVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                          nodeChanged          = true;
                          (*boundVector)[iTotalVar] = newBound;
                        }
                        break;
                      case babBase::enums::VT_BINARY:
                        // Round bounds to ensure binary values
                        if (optimizationSense > 0) {    // Lower bound
                          if (!mc::isequal(newBound, 0, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                            nodeChanged          = true;
                            (*boundVector)[iTotalVar] = 1;
                          }
                          // Integer bounds crossing => node is infeasible
                          if ((*boundVector)[iTotalVar] > upperVarBounds[iTotalVar]) {
                            _subsolvers[s]->_restore_LP_coefficients_after_OBBT();
                            // return TIGHTENING_INFEASIBLE;
                            return_infeasible = true;
                            continue;
                          }
                        }
                        else {    // Upper bound
                          if (!mc::isequal(newBound, 1, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                            nodeChanged          = true;
                            (*boundVector)[iTotalVar] = 0;
                          }
                          // Integer bounds crossing => node is infeasible
                          if ((*boundVector)[iTotalVar] < lowerVarBounds[iTotalVar]) {
                            _subsolvers[s]->_restore_LP_coefficients_after_OBBT();
                            // return TIGHTENING_INFEASIBLE;
                            return_infeasible = true;
                            continue;
                          }
                        }
                        break;
                      case babBase::enums::VT_INTEGER:
                        // Round bounds to ensure integer values
                        if (optimizationSense > 0) {    // Lower bound
                          if (!mc::isequal(newBound, std::floor(newBound), LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                            newBound = std::ceil(newBound);
                          }
                          else {
                            newBound = std::floor(newBound);
                          }
                          if (!mc::isequal((*boundVector)[iTotalVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                            nodeChanged          = true;
                            (*boundVector)[iTotalVar] = newBound;
                          }
                          // Integer bounds crossing => node is infeasible
                          if ((*boundVector)[iTotalVar] > upperVarBounds[iTotalVar]) {
                            _subsolvers[s]->_restore_LP_coefficients_after_OBBT();
                            // return TIGHTENING_INFEASIBLE;
                            return_infeasible = true;
                            continue;
                          }
                        }
                        else {    // Upper bound
                          if (!mc::isequal(newBound, std::ceil(newBound), LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                            newBound = std::floor(newBound);
                          }
                          else {
                            newBound = std::ceil(newBound);
                          }
                          if (!mc::isequal((*boundVector)[iVar], newBound, LowerBoundingSolver::_computationTol, LowerBoundingSolver::_computationTol)) {
                            nodeChanged          = true;
                            (*boundVector)[iVar] = newBound;
                          }
                          // Integer bounds crossing => node is infeasible
                          if ((*boundVector)[iTotalVar] < lowerVarBounds[iTotalVar]) {
                            _subsolvers[s]->_restore_LP_coefficients_after_OBBT();
                            // return TIGHTENING_INFEASIBLE;
                            return_infeasible = true;
                            continue;
                          }
                        }
                        break;
                      default:
                        throw MAiNGOException("  Error while solving OBBT: Unknown variable type.");
                        break;
                    }  // end switch
                  }
                }

                // Restore objective coefficient
                _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
              }
              
              if (return_infeasible) {
                return TIGHTENING_INFEASIBLE;
              }
              if (obj_out_of_bounds) {  // GCOVR_EXCL_START
                for (int s = 0; s < _TwoStageModel->Ns; s++) {
                  _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
                };
                
                continue;  // with next iteration of OBBT loop
              } // GCOVR_EXCL_STOP
            }
          }
        }  // End of OBBT while loop
      }  // End of if(!foundInfeasible)

      // Restore proper objective function and restore LP solver options
      _restore_LP_coefficients_after_OBBT();

      // Return appropriate return code and possibly update currentNode with new bounds
      if (foundInfeasible) {
        return TIGHTENING_INFEASIBLE;
      }
      else {
        if (!nodeChanged) {
          return TIGHTENING_UNCHANGED;
        }
        else {
          currentNode = babBase::BabNode(currentNode, lowerVarBounds, upperVarBounds);
          return TIGHTENING_CHANGED;
        }  // End of if (!nodeChanged)
      }  // End of if (foundInfeasible)
    } // End of solveOBBT()

    /**
     * @brief Check the need for options for the preprocessor.
     * 
     * @param[in] rootNode is the root node of the B&B tree
    */
    void preprocessor_check_options(const babBase::BabNode &rootNode) override {
      PROFILE_FUNCTION()

      // NOTE: bounds for root node are currently the same for all second stage variables.
      //       if that remains like this, we can reuse the linearization point if necessary.
      std::vector<std::vector<double>> lowerVarBounds_s, upperVarBounds_s, linearizationPoint_s(_TwoStageModel->Ns, std::vector<double>(_TwoStageModel->Nx + _TwoStageModel->Ny));
      std::vector<double> lowerVarBounds(rootNode.get_lower_bounds());
      std::vector<double> upperVarBounds(rootNode.get_upper_bounds());
      std::tie(lowerVarBounds_s, upperVarBounds_s) = _split_bounds(lowerVarBounds, upperVarBounds);

      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        for (unsigned i = 0; i < _TwoStageModel->Nx + _TwoStageModel->Ny; i++) {
          linearizationPoint_s[s][i] = 0.5 * (lowerVarBounds_s[s][i] + upperVarBounds_s[s][i]);
        }
      }

      LowerBoundingSolver::preprocessor_check_options(rootNode);
      #ifdef _OPENMP
        #pragma omp parallel for
      #endif
      for (int s = 0; s < _TwoStageModel->Ns; s++) {

        auto & ss = _subsolvers[s];

        // Set relNodeTol
        ss->_maingoSettings->relNodeTol = std::min(ss->_maingoSettings->deltaIneq, std::min(ss->_maingoSettings->deltaEq, ss->_maingoSettings->relNodeTol));

        // Currently the evaluation is used only to possibly detect interval and McCormick exceptions,
        // since this is already checked in LowerBoundingSolver::preprocessor_check_options(rootNode),
        // we don't need to repeat this here!

        int _nvar = _TwoStageModel->Nx + _TwoStageModel->Ny;
        for (unsigned int i = 0; i < _nvar; i++) {
          ss->_DAGobj->McPoint[i] = MC(I(lowerVarBounds_s[s][i], upperVarBounds_s[s][i]), linearizationPoint_s[s][i]);
          ss->_DAGobj->McPoint[i].sub(_nvar, i);
        }

        if (ss->_maingoSettings->LBP_subgradientIntervals) {
          // Compute improved relaxations at mid point
          bool oldSetting                 = MC::options.SUB_INT_HEUR_USE;
          MC::options.SUB_INT_HEUR_USE    = true;
          MC::subHeur.originalLowerBounds = &lowerVarBounds_s[s];
          MC::subHeur.originalUpperBounds = &upperVarBounds_s[s];
          MC::subHeur.referencePoint      = &linearizationPoint_s[s];

          ss->_DAGobj->DAG.eval(ss->_DAGobj->subgraph, ss->_DAGobj->MCarray, ss->_DAGobj->functions.size(), ss->_DAGobj->functions.data(), ss->_DAGobj->resultRelaxation.data(), ss->_nvar, ss->_DAGobj->vars.data(), ss->_DAGobj->McPoint.data());
          MC::options.SUB_INT_HEUR_USE        = oldSetting;
          MC::subHeur.usePrecomputedIntervals = false;
          MC::subHeur.reset_iterator();
        }
        else {
          ss->_DAGobj->DAG.eval(ss->_DAGobj->subgraph, ss->_DAGobj->MCarray, ss->_DAGobj->functions.size(), ss->_DAGobj->functions.data(), ss->_DAGobj->resultRelaxation.data(), ss->_nvar, ss->_DAGobj->vars.data(), ss->_DAGobj->McPoint.data());
        }

        if (ss->_maingoSettings->LBP_addAuxiliaryVars && !ss->_maingoSettings->BAB_constraintPropagation) {
          ss->_logger->print_message("        The option BAB_constraintPropagation has to be 1 when using option LBP_addAuxiliaryVars. Setting it to 1.\n", VERB_NORMAL, LBP_VERBOSITY);
          ss->_maingoSettings->BAB_constraintPropagation = true;
        }

        // Check whether the options can be applied with respect to the used solver
        ss->_turn_off_specific_options();
      }
    }

    /**
     * @brief Solve the subproblems of the siblings.
     * 
     * @param[in,out] siblingResults The struct storing the results of the sibling iteration.
     * @param[in] ubd The best known upper bound.
     * @param[in] obbtType The type of OBBT.
     */
    void solve_sibling_subproblems(
      lbp::SiblingResults &siblingResults,
      double ubd,
      int obbtType
    ) {

      // Create subnodes for each sibling
      for (unsigned int j : {0, 1}) {
        std::tie(siblingResults.lowerBounds[j], siblingResults.upperBounds[j]) = 
          _split_bounds(siblingResults.siblings[j].get_lower_bounds(),
                        siblingResults.siblings[j].get_upper_bounds());
        for (int s = 0; s < _TwoStageModel->Ns; s++) {
          siblingResults.siblingSubNodes[s][j].set_lower_bound(siblingResults.lowerBounds[j][s]);
          siblingResults.siblingSubNodes[s][j].set_upper_bound(siblingResults.upperBounds[j][s]);
        }
      }

      // Fake _subNodes for parent node with appropriate bounds
      _subNodes.clear();
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        _subNodes.emplace_back(siblingResults.siblings[0],
                               siblingResults.siblingSubNodes[s][0].get_lower_bounds(),
                               siblingResults.siblingSubNodes[s][1].get_upper_bounds());
      }

      /** 
       * Scenario upper bounds based on the parent's subproblem bounds, valid for both siblings.
       * Note that scenarioUBDs we could calculate based on siblingResults.subproblemBounds[i])
       * are only valid for the node represented by sibling i.
       * Since we want to re-use the sibling domains resulting from range reduction,
       * we may only fathom by dominance if this fathoming is valid for all possible  orthants,
       * i.e., only when we can fathom based on the the parent's subproblem bounds.
       */
      std::vector<double> scenarioUBD(_TwoStageModel->Ns, 0.0);
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        scenarioUBD[s] = _calculate_scenario_UBD(s, ubd);
      }

      /**
       * Each of the following range reduction loops works as follows:
       * - For all s
       *   - Tighten the bounds of the subnode for scenario s of each sibling.
       *   - Create the union of domains for that scenario.
       *     (Note that if both sibling domains can be tightened, the union is a valid tightening of the parent domain.)
       * Since the x values must be feasible for all scenarios, the intersection of the x part of the scenario union of domains is a valid tightening of the parent domain for x.
       * If these tightenings result in an empty domain the parent can be fathomed, updated lower bounds 
       */
      bool parent_fathomed = false;
      /** Retcodes (< 1 means fathomed, > 0 means potentially feasible)
       *  -1 == fathomed by value dominance
       *  0 == fathomed by infeasibility
       *  1 == potentially feasible, unchanged variable bounds
       *  2 == potentially feasible, changed variable bounds
       */
      std::vector<std::array<int, 2>> retcodes({_TwoStageModel->Ns, {{1, 1}}});

      // CP
      #ifdef _OPENMP
        #pragma omp parallel for
      #endif
      for (int s = 0; s < _TwoStageModel->Ns; s++) { if (!parent_fathomed) { // only execute if we're not fathomed
        for (unsigned int j : {0, 1}) {
          retcodes[s][j] = static_cast<int>(
            _subsolvers[s]->do_constraint_propagation(
              siblingResults.siblingSubNodes[s][j],
              scenarioUBD[s]
            )
          );
        }
        if (siblingResults.infeasible_after_parent_tightening(s, _subNodes[s], retcodes[s])) {
            parent_fathomed = true;
        }
      }}
      if (parent_fathomed) {
        return;
      }

      if (siblingResults.infeasible_after_sibling_tightening(_subNodes, retcodes)) {
        return;
      }

      if (obbtType != -1) {
        // OBBT
        #ifdef _OPENMP
          #pragma omp parallel for
        #endif
        for (int s = 0; s < _TwoStageModel->Ns; s++) { if (!parent_fathomed) { // only execute if we're not fathomed
          for (unsigned int j : {0, 1}) {
            if (retcodes[s][j] > 0) {
              retcodes[s][j] = static_cast<int>(
                _subsolvers[s]->solve_OBBT(
                  siblingResults.siblingSubNodes[s][j],
                  scenarioUBD[s],
                  static_cast<OBBT>(obbtType)
                )
              );
            }
          }
          if (siblingResults.infeasible_after_parent_tightening(s, _subNodes[s], retcodes[s])) {
            parent_fathomed = true;
          }
        }}
        if (parent_fathomed) {
          return;
        }

        if (siblingResults.infeasible_after_sibling_tightening(_subNodes, retcodes)) {
          return;
        }
      }

      auto _fathom_by_domination = [&](int s, int j) {
        if (scenarioUBD[s] < siblingResults.objectiveBounds[j][s]) {
          /**
           * This scenario is dominated, i.e., the sibling can be fathomed by value dominance.
           * As with infeasibility of a subproblem, the parent can only be fathomed if the scenario subproblem of the other sibling is also fathomed.
           * We handle this domination as an infeasibility for ease of implementation, as it has the same implications.
           */
          siblingResults.solutions[j][s].clear();
          retcodes[s][j] = -1;
          if ((retcodes[s][0] < 1) && (retcodes[s][1] < 1)) {
            // siblingResults.converged = true;
            return true;
          }
        }
        return false;
      };

      // If we got here we will solve the sibling nodes; we count each sibling as one LB solve
      siblingResults.nAddedLBSolves = 2;

      // Lower bounding
      #ifdef _OPENMP
        #pragma omp parallel for
      #endif
      for (int s = 0; s < _TwoStageModel->Ns; s++) { if (!parent_fathomed) { // only execute if we're not fathomed
        for (unsigned int j : {0, 1}) {
          if (retcodes[s][j] > 0) {
            retcodes[s][j] = static_cast<int>(
              _subsolvers[s]->solve_LBP(
                siblingResults.siblingSubNodes[s][j],
                siblingResults.objectiveBounds[j][s],
                siblingResults.solutions[j][s],
                siblingResults.dualInfo[j][s]
              )
            );
            if (_fathom_by_domination(s, j)) { // early exit from loop
              parent_fathomed = true;
            }
          }
        }
        if ((retcodes[s][0] < 1) && (retcodes[s][1] < 1)) {
          parent_fathomed = true;
        }
      }}
      if (parent_fathomed) {
        return;
      }

      // We can update the subproblem bounds for the parent, the parentPruningScore and the scenarioUBD using the tightened objectiveBounds...
      siblingResults.update_parent_pruning_score(_subproblemBounds);
      // ... and check for domination again
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        scenarioUBD[s] = _calculate_scenario_UBD(s, ubd);
        for (int j = 0; j < 2; j++) {
          if (_fathom_by_domination(s, j)) {
            return;
          }
        }
      }

      /**
       * NOTE: In contrast to first-stage iterations, upper bounding is performed after DBBT.
       *       This allows to keep the necessary callbacks that need to be set up to a minimum.
       */

      // DBBT
      #ifdef _OPENMP
        #pragma omp parallel for
      #endif
      for (int s = 0; s < _TwoStageModel->Ns; s++) { if (!parent_fathomed) { // only execute if we're not fathomed
        for (unsigned int j : {0, 1}) {
          // disaggregated DBBT for subproblems
          if (retcodes[s][j] > 0) {
            retcodes[s][j] = static_cast<int>(
              _subsolvers[s]->do_dbbt_and_probing(
                siblingResults.siblingSubNodes[s][j],
                siblingResults.solutions[j][s],
                siblingResults.dualInfo[j][s],
                scenarioUBD[s]
              )
            );
          }
        }
        if (siblingResults.infeasible_after_parent_tightening(s, _subNodes[s], retcodes[s])) {
          parent_fathomed = true;
        }
      }}
      if (parent_fathomed) {
        return;
      }

      if (!siblingResults.infeasible_after_sibling_tightening(_subNodes, retcodes)) {
        // Extract results and store in siblingResults
        siblingResults.tighten_parent_objective_and_variable_bounds(retcodes);
        siblingResults.feasible = true;
      }
    }

    /**
     * @brief Prepares and executes disaggregated DBBT and probing.
     * 
     * @param[in] currentNode is the node for which DBBT and probing are executed.
     * @param[in] UNUSED_LBPSOLUTION is unused, instead we use _subproblemSolutions
     * @param[in] UNUSED_DUALINFO is unused, instead we use _subproblemDualInfo
     * @param[in] currentUBD is the best known upper bound
     */
    TIGHTENING_RETCODE
    do_dbbt_and_probing(
      babBase::BabNode &currentNode,
      const std::vector<double> &UNUSED_LBPSOLUTION,
      const LbpDualInfo &UNUSED_DUALINFO,
      const double currentUBD
    ) override {
      std::vector<TIGHTENING_RETCODE> retcodes(_TwoStageModel->Ns, TIGHTENING_UNCHANGED);
      #ifdef _OPENMP
        #pragma omp parallel for
      #endif
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        if (_subproblemDualInfo[s].multipliers.size() == 0) {
          continue;
        }
        double scenarioUBD = _calculate_scenario_UBD(s, currentUBD);
        retcodes[s] = _subsolvers[s]->do_dbbt_and_probing(_subNodes[s], _subproblemSolutions[s], _subproblemDualInfo[s], scenarioUBD);
      }
      // Node is infeasible if DBBT finds any subproblem to be infeasible

      // Size Nx + Ny * Ns
      auto &LB                   = currentNode.get_lower_bounds();
      auto &UB                   = currentNode.get_upper_bounds();
      TIGHTENING_RETCODE retcode = TIGHTENING_UNCHANGED;
      for (unsigned int s = 0; s < _TwoStageModel->Ns; s++) {
        if (retcodes[s] == TIGHTENING_INFEASIBLE) {
          return TIGHTENING_INFEASIBLE;
        }

        if (retcodes[s] == TIGHTENING_CHANGED) {
          if (retcode != TIGHTENING_INFEASIBLE) {
            retcode = TIGHTENING_CHANGED;
          }

          // Size Nx + Ny
          auto const &LBs = _subNodes[s].get_lower_bounds();
          auto const &UBs = _subNodes[s].get_upper_bounds();
          // Use best bounds for first-stage variables
          for (unsigned int ix = 0; ix < _TwoStageModel->Nx; ix++) {
            currentNode.set_lower_bound(ix, std::max(LBs[ix], LB[ix]));
            currentNode.set_upper_bound(ix, std::min(UBs[ix], UB[ix]));
            // If the subproblems require any first-stage variable to be in subdomains that do not intersect, the node is infeasible
            if (LB[ix] > UB[ix]) {
              return TIGHTENING_INFEASIBLE;
            }
          }
          // Update the second-stage variables associated to the current scenario
          for (unsigned int iy = 0; iy < _TwoStageModel->Ny; ++iy) {
            auto isp = _TwoStageModel->Nx + iy;
            auto i   = isp + s * _TwoStageModel->Ny;
            currentNode.set_lower_bound(i, LBs[isp]);
            currentNode.set_upper_bound(i, UBs[isp]);
          }
        }
      }
      return retcode;
    }

    void
    update_incumbent_LBP(const std::vector<double> &incumbentBAB) override {
      LowerBoundingSolver::_incumbent = incumbentBAB;
      std::vector<double> incumbent_s(_TwoStageModel->Nx + _TwoStageModel->Ny);
      for (unsigned int i = 0; i < _TwoStageModel->Nx; i++) {
        incumbent_s[i] = incumbentBAB[i];
      }
      for (unsigned int s = 0; s < _TwoStageModel->Ns; s++) {
        for (unsigned int i = 0; i < _TwoStageModel->Ny; i++) {
          incumbent_s[_TwoStageModel->Nx + i] = incumbentBAB[_TwoStageModel->Nx + s * _TwoStageModel->Ny + i];
        }
        _subsolvers[s]->update_incumbent_LBP(incumbent_s);
      }
    }

  protected:
    /**
     * @brief Delegates calls for computing linearization points and modifying the LP coefficients to the subproblem solvers
     *
     * @param[in] currentNode is current node of the branch-and-bound tree
     * @return returns a LINEARIZATION_RETCODE defining whether the final problem was already solved/proven infeasible during linearization
     */
    LINEARIZATION_RETCODE _update_LP(const babBase::BabNode &currentNode) override {
      _subNodes.clear();
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        _subNodes.push_back(currentNode);
      }
      _set_variable_bounds(currentNode.get_lower_bounds(), currentNode.get_upper_bounds());

      return _update_subproblem_LPs();
    }  // GCOVR_EXCL_LINE

    /**
      * @brief Function for setting the bounds of variables
      *
      * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
      * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
      */
    void _set_variable_bounds(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds) override {
      // PROFILE_FUNCTION()

      std::vector<std::vector<double>> LBs, UBs;
      std::tie(LBs, UBs) = _split_bounds(lowerVarBounds, upperVarBounds);

      // #ifdef _OPENMP
      //   #pragma omp parallel for
      // #endif
      for (unsigned int s = 0; s < _TwoStageModel->Ns; s++) {
        // PROFILE_SCOPE("_set_variable_bounds_s")

        _subsolvers[s]->_set_variable_bounds(LBs[s], UBs[s]);

        // NOTE: you'd expect this to be done in the subsolvers, but if they don't take care of it we get problems later!
        _subsolvers[s]->_lowerVarBounds = LBs[s];
        _subsolvers[s]->_upperVarBounds = UBs[s];
      }
      subsolver_class::_set_variable_bounds(lowerVarBounds, upperVarBounds);
    }

    /**
     * @brief Function for solving the currently constructed linear program.
     *
     * @param[in] currentNode is the currentNode, needed for throwing exceptions or obtaining the lower and upper bounds of variables
     */
    LP_RETCODE _solve_LP(const babBase::BabNode &currentNode) override {
      // NOTE: this function should only be called by LowerBoundingSolver::solve_LBP
      PROFILE_SCOPE("LBP_solve_LP")

      _solve_subproblem_LPs(currentNode, "LBP"); // updates LowerBoundingSolver::_LPstatus

      if (LowerBoundingSolver::_LPstatus == LP_OPTIMAL) {
        for (int s = 0; s < _TwoStageModel->Ns; s++) {
          _subproblemBounds[s] = std::max(_subsolvers[s]->_get_objective_value(), _subsolvers[s]->_DAGobj->validIntervalLowerBound);
        }
      }

      return LowerBoundingSolver::_LPstatus;
    }

    /**
     * @brief Function for updating the linear relaxations of the subproblems.
     *
     * @param[in] prefix is a prefix for communicating the calling scope to profiling
     */
    LINEARIZATION_RETCODE _update_subproblem_LPs(const std::string prefix = "") {
      // The overall retcode is:
      // - infeasible if any subproblems are infeasible
      // - unknown if any subproblem is unknown and none are infeasible
      // - optimal if all subproblem retcodes are optimal
      LINEARIZATION_RETCODE retcode = LINEARIZATION_OPTIMAL, overall_retcode = LINEARIZATION_OPTIMAL;
      #ifdef _OPENMP
        std::vector<LINEARIZATION_RETCODE> retcodes(_TwoStageModel->Ns, LINEARIZATION_OPTIMAL);
        #pragma omp parallel for
      #endif
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        PROFILE_SCOPE(prefix + "_update_LP_s")  // update the LP relaxation of the subproblem s
        _subNodes[s].set_lower_bound(_subsolvers[s]->_lowerVarBounds);
        _subNodes[s].set_upper_bound(_subsolvers[s]->_upperVarBounds);
        #ifdef _OPENMP
          retcodes[s] = _subsolvers[s]->_update_LP(_subNodes[s]);
        #else
          retcode = _subsolvers[s]->_update_LP(_subNodes[s]);
          
          if (retcode == LINEARIZATION_INFEASIBLE)
            return LINEARIZATION_INFEASIBLE;
          else if (retcode == LINEARIZATION_UNKNOWN)
            overall_retcode = LINEARIZATION_UNKNOWN;
        #endif
      }

      #ifdef _OPENMP
        for (auto && ret : retcodes) {
          if (ret == LINEARIZATION_INFEASIBLE) {
            return LINEARIZATION_INFEASIBLE;
          }
          else if (ret == LINEARIZATION_UNKNOWN)
            overall_retcode = LINEARIZATION_UNKNOWN;
        }
      #endif
      
      if (retcode == LINEARIZATION_INFEASIBLE)
          return LINEARIZATION_INFEASIBLE;
      else if ((retcode == LINEARIZATION_UNKNOWN) || (overall_retcode == LINEARIZATION_UNKNOWN))
        return LINEARIZATION_UNKNOWN;

      // This can only happen for Kelley linearization points, we need to update the subproblem bounds as this won't happen via _solve_LP
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
          _subproblemBounds[s] = std::max(_subsolvers[s]->_get_objective_value(), _subsolvers[s]->_DAGobj->validIntervalLowerBound);
      }
      return LINEARIZATION_OPTIMAL;
    }

    /**
     * @brief Function for solving the currently constructed linear relaxations of the subproblems.
     *
     * @param[in] currentNode is the currentNode, needed for throwing exceptions or obtaining the lower and upper bounds of variables
     * @param[in] prefix is a prefix for communicating the calling scope to profiling
     */
    void _solve_subproblem_LPs(const babBase::BabNode &currentNode, const std::string prefix = "") {
      LowerBoundingSolver::_LPstatus = LP_OPTIMAL;
      #ifdef _OPENMP
        #pragma omp parallel for
        for (int s = 0; s < _TwoStageModel->Ns; s++) {
          PROFILE_SCOPE(prefix + "_solve_LP_s")
          _subsolvers[s]->_LPstatus = _subsolvers[s]->_solve_LP(_subNodes[s]);

          if (LowerBoundingSolver::_LPstatus == LP_OPTIMAL && _subsolvers[s]->_LPstatus != LP_OPTIMAL) {
            LowerBoundingSolver::_LPstatus = _subsolvers[s]->_LPstatus;
          }
        }
      #else
        _early_return_solve_subproblem_LPs(currentNode, prefix);
      #endif
    }

    /**
     * @brief Function for solving the currently constructed linear relaxations of the subproblems allowing for an early return if one subproblem is found to be infeasible.
     *
     * @param[in] currentNode is the currentNode, needed for throwing exceptions or obtaining the lower and upper bounds of variables
     * @param[in] prefix is a prefix for communicating the calling scope to profiling
     */
    void _early_return_solve_subproblem_LPs(const babBase::BabNode &currentNode, const std::string prefix = "") {
      LowerBoundingSolver::_LPstatus = LP_UNKNOWN;
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        PROFILE_SCOPE(prefix + "_solve_LP_s")
        LowerBoundingSolver::_LPstatus = _subsolvers[s]->_LPstatus = _subsolvers[s]->_solve_LP(_subNodes[s]);
        if (LowerBoundingSolver::_LPstatus != LP_OPTIMAL) {
          return;  // early return if any subproblem has infeasible or unknown return status
        }
      }
    }

    /**
     * @brief Function returning the current status of the last solved set of linear programs.
     *
     * @return Returns the current status of the last solved set of linear programs.
     */
    LP_RETCODE _get_LP_status() override {
      // The overall retcode is:
      // - infeasible if any subproblems are infeasible
      // - unknown if any subproblem is unknown and none are infeasible
      // - optimal if all subproblem retcodes are optimal
      LP_RETCODE retcode = LP_OPTIMAL, overall_retcode = LP_OPTIMAL;
      for (unsigned int s = 0; s < _TwoStageModel->Ns; s++) {
          retcode = _subsolvers[s]->_get_LP_status();
          
          if (retcode == LP_INFEASIBLE)
            return LP_INFEASIBLE;
          else if (retcode == LP_UNKNOWN)
            overall_retcode = LP_UNKNOWN;
      }

      return overall_retcode;
    };

    /**
     * @brief Function for setting the solution to the solution point of the lastly solved LP.
     *
     * @param[in] solution is modified to hold the solution point of the lastly solved LP
     * @param[in] etaVal is modified to hold the value of eta variable of the lastly solved LP
     */
    void _get_solution_point(std::vector<double> &solution, double &obj) override {

      solution.resize(_TwoStageModel->Nx + _TwoStageModel->Ns * _TwoStageModel->Ny);
      for (unsigned int s = 0; s < _TwoStageModel->Ns; s++) {
        auto & solution_s = _subproblemSolutions[s];
        /** TODO: Can we drop one of these lines setting _subproblemDualInfo[s].lpLowerBound? */
        _subsolvers[s]->_get_solution_point(solution_s, _subproblemDualInfo[s].lpLowerBound);
        _subproblemDualInfo[s].lpLowerBound = _subsolvers[s]->_get_objective_value();

        // average over first-stage variable values
        for (unsigned int i = 0; i < _TwoStageModel->Nx; i++) {
          solution[i] += _TwoStageModel->w[s] * solution_s[i];
        }
        // assign correct element in overall variable vector
        for (unsigned int i = 0; i < _TwoStageModel->Ny; i++) {
          solution[_TwoStageModel->Nx + s * _TwoStageModel->Ny + i] = solution_s[_TwoStageModel->Nx + i];
        }
        // objective is weighted average over subproblem objectives
        /** NOTE: Obj corresponds to the LP bound, the better of LP and interval bound will be used as the node bound */
        obj += _TwoStageModel->w[s] * _subproblemDualInfo[s].lpLowerBound;
      }

      // alternatively set subsolver_class::_lowerVarBounds and subsolver_class::_upperVarBounds in _set_variable_bounds
      auto lb        = _subsolvers[0]->_lowerVarBounds;
      auto ub        = _subsolvers[0]->_upperVarBounds;
      // Find the s for which xs is closest to the mean over the xs in the l2 norm
      int s_opt      = -1;
      double minDist = subsolver_class::_maingoSettings->infinity;
      for (unsigned int s = 0; s < _TwoStageModel->Ns; s++) {
        double sumSquaredRelDists = 0., dist, initGap, relDist;
        for (unsigned int i = 0; i < _TwoStageModel->Nx; i++) {
          dist                = _subproblemSolutions[s][i] - solution[i];
          initGap             = subsolver_class::_originalVariables[i].get_upper_bound() - subsolver_class::_originalVariables[i].get_lower_bound();
          relDist             = (initGap > 0) ? (dist / initGap) : 0.;
          sumSquaredRelDists += std::pow(relDist, 2);
        }
        if (sumSquaredRelDists < minDist) {
          minDist = sumSquaredRelDists;
          s_opt   = s;
          if (sumSquaredRelDists == 0) {
            break;
          }
        }
      }
      // Update the solution point
      for (unsigned int i = 0; i < _TwoStageModel->Nx; i++) {
        solution[i] = _subproblemSolutions[s_opt][i];
      }
    }

    /**
     * @brief Function returning the objective value of the lastly solved LP.
     *
     * @return Returns the objective value of the lastly solved LP.
     */
    double _get_objective_value_solver() override {
      double res = 0;
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        res += _TwoStageModel->w[s] * _subsolvers[s]->_get_objective_value_solver();
      }
      return res;
    }

    /**
     * @brief Function for updating the multipliers from the lastly solved subproblem LPs.
     * 
     * The multipliers passed by LowerBoundingSolver::solve_LBP are not used
     * when solving subproblems, instead we use internally stored multipliers
     * in subproblemDualInfo. However since BranchAndBound::_postprocess_node
     * tests for the size of multipliers we need to use dummy values.
     *
     * @param[out] dummy_multipliers is sized appropriately but not used.
     */
    void _get_multipliers(std::vector<double> &dummy_multipliers) override {
      dummy_multipliers.resize(_TwoStageModel->Nx + _TwoStageModel->Ns * _TwoStageModel->Ny);
      for (unsigned s = 0; s < _TwoStageModel->Ns; s++) {
        _subsolvers[s]->_get_multipliers(_subproblemDualInfo[s].multipliers);
      }
    }

    /**
     * @brief Function for restoring proper coefficients and options in the LP after OBBT.
     */
    void _restore_LP_coefficients_after_OBBT() override {
      for (int s = 0; s < (int)_TwoStageModel->Ns; s++) {
        _subsolvers[s]->_restore_LP_coefficients_after_OBBT();
      }
    }

    /**
     * @brief Virtual function for fixing a variable to one of its bounds.
     *
     * @param[in] iVar is the number of variable which will be fixed.
     * @param[in] fixToLowerBound describes whether the variable shall be fixed to its lower or upper bound.
     */
    void _fix_variable(const unsigned &iVar, const bool fixToLowerBound) override {
  
      LowerBoundingSolver::_fix_variable(iVar, fixToLowerBound);

      if (iVar < _TwoStageModel->Nx) {
        for (unsigned s = 0; s < _TwoStageModel->Ns; s++)
          _subsolvers[s]->_fix_variable(iVar, fixToLowerBound);
        return;
      }

      // For second-stage variables indices wrap-around
      int s = (iVar - _TwoStageModel->Nx) / _TwoStageModel->Ny;
      int i_s = _TwoStageModel->Nx + (iVar - _TwoStageModel->Nx) % _TwoStageModel->Nx;
      _subsolvers[s]->_fix_variable(i_s, fixToLowerBound);
    };

    /**
     * @brief Function for checking if the current linear program is really infeasible by, e.g., resolving it with different algorithms.
     * 
     * @return Returns true if the linear program is indeed infeasible, false if and optimal solution was found
     */
    bool _check_if_LP_really_infeasible() override {
      // if any subproblem is infeasible, the main one is, too!
      for (auto & ss : _subsolvers) {
        if (ss->_check_if_LP_really_infeasible())
          return true;
      }
      return false;
    }

#ifdef LP__OPTIMALITY_CHECK
    /**
     * @brief Function for checking if the solution point returned is really infeasible
     *
     * @param[in] currentNode is holding the current node in the branch-and-bound tree
     * @return Returns whether the problem was confirmed to be infeasible or not
     */
    SUBSOLVER_RETCODE _check_infeasibility(const babBase::BabNode &currentNode) override {
      // The overall retcode is:
      // - infeasible if any subproblems are infeasible
      // - feasible if all subproblem retcodes are feasible
      for (unsigned s = 0; s < _TwoStageModel->Ns; s++) {
        // Infeasibility check may only be performed if the subproblem is not optimal
        if (_subsolvers[s]->_get_LP_status() == LP_OPTIMAL) {
          continue;
        }
        auto retcode = _subsolvers[s]->_check_infeasibility(_subNodes[s]);

        if (retcode == SUBSOLVER_INFEASIBLE)
          return SUBSOLVER_INFEASIBLE;
      }
      return SUBSOLVER_FEASIBLE;
    }


    // void _print_check_feasibility(const std::shared_ptr<Logger> logger, const VERB verbosity, const std::vector<double> &solution, const std::vector<std::vector<double>> rhs, const std::string name, const double value, const unsigned i, unsigned k, const unsigned nvar);

    /**
     * @brief Function for checking if the solution point returned by CPLEX solver is really feasible
     *
     * @param[in] UNUSED_SOLUTION for matching the signature only
     * @return Returns whether the given solution was confirmed to be feasible or not
     */
    SUBSOLVER_RETCODE _check_feasibility(const std::vector<double> &UNUSED_SOLUTION) override
    {
      // NOTE: Since we need to check feasibility with the subsolvers used for obtaining the solution and the first stage variables might differ, we use the previously computed solution instead of the passed one!
      // FIXME: Even though right now this is save as calls to _check_feasibility are always preceeded by _get_solution_point, this approach should get a sanity check.
      // std::vector<double> solution_s;
      // double dummy;

      for (unsigned s = 0; s < _TwoStageModel->Ns; s++) {

        // _subsolvers[s]->_get_solution_point(solution_s, dummy);
        auto & solution_s = _subproblemSolutions[s];

        auto retcode = _subsolvers[s]->_check_feasibility(solution_s);

        if (retcode == SUBSOLVER_INFEASIBLE)
          return SUBSOLVER_INFEASIBLE;
      }
      return SUBSOLVER_FEASIBLE;
    }

    /**
     * @brief Function for checking if the solution point is really optimal. Uses stored data for subproblems instead of the passed data.
     *
     * @param[in] UNUSED_CURRENT_NODE is holding the current node in the branch-and-bound tree
     * @param[in] UNUSED_LBD is the value of the solution point to check
     * @param[in] UNUSED_SOLUTION is holding the solution point to check
     * @param[in] UNUSED_ETAVAL is holding the value of eta at the solution point
     * @param[in] UNUSED_MULTIPLIERS is holding the dual multipliers of the solution
     * @return Returns whether the given solution was confirmed to be optimal or not
     */
    SUBSOLVER_RETCODE _check_optimality(const babBase::BabNode &UNUSED_CURRENT_NODE, const double UNUSED_LBD, const std::vector<double> &UNUSED_SOLUTION, const double UNUSED_ETAVAL, const std::vector<double> &UNUSED_MULTIPLIERS) override {
      for (unsigned s = 0; s < _TwoStageModel->Ns; s++) {
        auto &obj_s = _subproblemDualInfo[s].lpLowerBound;
        auto &solution_s = _subproblemSolutions[s];
        auto &multipliers_s = _subproblemDualInfo[s].multipliers;
        if (_subsolvers[s]->_check_optimality(_subNodes[s], obj_s, solution_s, obj_s, multipliers_s) == SUBSOLVER_INFEASIBLE)
          return SUBSOLVER_INFEASIBLE;
      }
      return SUBSOLVER_FEASIBLE;
    }

#endif

  private:

    std::shared_ptr<maingo::TwoStageModel> _TwoStageModel;
    std::vector<std::shared_ptr<LowerBoundingSolver>> _subsolvers;
    std::vector<std::vector<double>> _subproblemSolutions;  // handle for storing the last group of solution points obtained using subsolvers
  public:
    std::vector<double> _subproblemBounds;  // handle for storing the last group of bounds on SP subproblems (the better of LP objective and interval arithmetic bound) to generate upper bounds for OBBT
  private:
    std::vector<LbpDualInfo> _subproblemDualInfo; // handle for dualInfo associated to the lower bounding subproblems
    std::vector<double> _last_incumbent;
    bool _update_for_OBBT = false;  // if using default OBBT the update of the 'normal' lower bounding problem is required instead of the parallel subproblems

    std::vector<babBase::BabNode> _subNodes;  // the current node representation of the subproblems
    unsigned int _No;  // Number of orthant nodes created by second-stage branching.

    /**
     * @brief prepare constraints for the subproblems
     */
    inline void _prepare_constraints(
      const std::string &s_string,
      std::shared_ptr<std::vector<Constraint>> &SP_constraint_properties_s,
      std::vector<mc::FFVar> &SP_DAG_functions_s,
      std::vector<std::vector<NamedVar>> g1_s,
      std::vector<std::vector<NamedVar>> g2_s
    ) {
      unsigned indexOriginal = 0, indexNonconstant = 0;

      SP_constraint_properties_s->emplace_back(
          CONSTRAINT_TYPE::OBJ,
          indexOriginal++,
          0,
          indexNonconstant++,
          0,
          "f1 + f2_" + s_string);

      maingo::CONSTRAINT_TYPE ct[5] = {
        maingo::CONSTRAINT_TYPE::INEQ,
        maingo::CONSTRAINT_TYPE::INEQ_SQUASH,
        maingo::CONSTRAINT_TYPE::EQ,
        maingo::CONSTRAINT_TYPE::INEQ_REL_ONLY,
        maingo::CONSTRAINT_TYPE::EQ_REL_ONLY
      };

      unsigned indexType[5]            = {0, 0, 0, 0, 0};
      unsigned indexTypeNonconstant[5] = {0, 0, 0, 0, 0};
      std::string type[5]{"ineq", "ineg_squash", "eq", "ineqRO", "eqRO"};
      for (unsigned i = 0; i < 5; i++) {
        for (auto &func : g1_s[i]) {
          SP_DAG_functions_s.push_back(func.first);
          SP_constraint_properties_s->emplace_back(
              ct[i],
              indexOriginal++,
              indexType[i],
              indexNonconstant++,
              indexTypeNonconstant[i]++,
              type[i] + '_' + s_string + '_' + std::to_string(indexType[i]++));
        }
        for (auto &func : g2_s[i]) {
          SP_DAG_functions_s.push_back(func.first);
          SP_constraint_properties_s->emplace_back(
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
      unsigned size = SP_DAG_functions_s.size();
      std::vector<std::map<int, int>> func_dep(size);
      for (unsigned int i = 0; i < size; i++) {
        func_dep[i] = SP_DAG_functions_s[i].dep().dep();
      }

      // Loop over all functions
      unsigned indexLinear = 0, indexNonlinear = 0;
      for (unsigned int i = 0; i < size; i++) {
        mc::FFDep::TYPE functionStructure = mc::FFDep::L;
        std::vector<unsigned> participatingVars;
        for (unsigned int j = 0; j < LowerBoundingSolver::_nvar; j++) { // TODO: Only X and ys
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

        Constraint &func         = (*SP_constraint_properties_s)[i];
        func.indexNonconstantUBP = i;

        // determine dependency
        func.nparticipatingVariables = participatingVars.size();
        func.participatingVariables  = participatingVars;
        switch (functionStructure) {
          case mc::FFDep::L:
            func.dependency  = LINEAR;
            func.indexLinear = indexLinear++;
            break;
          case mc::FFDep::B:
            func.dependency     = BILINEAR;
            func.indexNonlinear = indexNonlinear++;
            break;
          case mc::FFDep::Q:
            func.dependency     = QUADRATIC;
            func.indexNonlinear = indexNonlinear++;
            break;
          case mc::FFDep::P:
            func.dependency     = POLYNOMIAL;
            func.indexNonlinear = indexNonlinear++;
            break;
          case mc::FFDep::R:
            func.dependency     = RATIONAL;
            func.indexNonlinear = indexNonlinear++;
            break;
          case mc::FFDep::N:
          case mc::FFDep::D:
          default:
            func.dependency     = NONLINEAR;
            func.indexNonlinear = indexNonlinear++;
            break;
        }
        func.convexity    = CONV_NONE;
        func.monotonicity = MON_NONE;
      }
    }

    /**
     * @brief Function for calculating scenario-specific upper bounds to be used as cutoffs on OBBT and DBBT.
     */
    inline double _calculate_scenario_UBD(unsigned int s, double currentUBD) {
      // Since we know that
      //   sum_{s}(_TwoStageModel->w[s] * subproblem_bound[s]) = localLB ≤ currentUBD
      // we can use the following cutoff for the subproblem s:
      //   ( currentUBD - sum_{q ≠ s}( _TwoStageModel->w[q] * subproblem_bound[q]) ) / _TwoStageModel->w[s]
      //   = ( currentUBD - (localLB - _TwoStageModel->w[s] * subproblem_bound[s]) ) / _TwoStageModel->w[s]
      //   = ( currentUBD - localLB ) / _TwoStageModel->w[s] + subproblem_bound[s] )
      // however, since we do OBBT before solving the LBPs, the only bounds we can use are those from the parent node

      // The complement lower bound is the node's local lower bound minus the current scenario's weighted bound
      double complement_LBD_s = 0.;
      for (int s_prime = 0; s_prime < _TwoStageModel->Ns; s_prime++) {
        if (s_prime != s)
          complement_LBD_s += _TwoStageModel->w[s_prime] * _subproblemBounds[s_prime];
      }
      return (currentUBD - complement_LBD_s) / _TwoStageModel->w[s];
    }

    inline void _reset_optimization_sense(int iyVar, int iVar, int iy, int is) {
      PROFILE_FUNCTION()

      if (iyVar < 0) {    // x variable, reset all subproblems
        // #pragma omp parallel for
        for (int s = 0; s < _TwoStageModel->Ns; s++) {
          _subsolvers[s]->_set_optimization_sense_of_variable(iVar, 0);
        }
      }
      else {    // y variable, reset the corresponding subproblem
        _subsolvers[is]->_set_optimization_sense_of_variable(_TwoStageModel->Nx + iy, 0);
      }
    }

    /**
     * @brief Split bound vectors into Ns subvectors for subproblem solvers.
     *
     * @param[in] vec is the vector to be split
     */
    inline std::pair<std::vector<std::vector<double>>, std::vector<std::vector<double>>> _split_bounds(const std::vector<double> LB, const std::vector<double> UB) {
      std::vector<std::vector<double>> LBs(_TwoStageModel->Ns, std::vector<double>(_TwoStageModel->Nx + _TwoStageModel->Ny));
      std::vector<std::vector<double>> UBs(_TwoStageModel->Ns, std::vector<double>(_TwoStageModel->Nx + _TwoStageModel->Ny));
      for (int s = 0; s < _TwoStageModel->Ns; s++) {
        for (unsigned i = 0; i < _TwoStageModel->Nx; i++) {
          LBs[s][i] = LB[i];
          UBs[s][i] = UB[i];
        }
        for (unsigned i = 0; i < _TwoStageModel->Ny; i++) {
          LBs[s][_TwoStageModel->Nx + i] = LB[_TwoStageModel->Nx + s * _TwoStageModel->Ny + i];
          UBs[s][_TwoStageModel->Nx + i] = UB[_TwoStageModel->Nx + s * _TwoStageModel->Ny + i];
        }
      }
      return {LBs, UBs};
    }
};


/**
 * @brief Factory function for initializing different TwoStage lower bounding solver wrappers
 *
 * @param[in] twoStageModel is the pointer to the TwoStageModel opbject
 * @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
 * @param[in] DAGvars are the variables corresponding to the DAG
 * @param[in] DAGfunctions are the functions corresponding to the DAG
 * @param[in] variables is a vector containing the initial optimization variables defined in problem.h
 * @param[in] nineqIn is the number of inequality constraints
 * @param[in] neqIn is the number of equality
 * @param[in] nineqRelaxationOnlyIn is the number of inequality for use only in the relaxed problem
 * @param[in] neqRelaxationOnlyIn is the number of equality constraints for use only in the relaxed problem
 * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
 * @param[in] settingsIn is a pointer to the MAiNGO settings
 * @param[in] loggerIn is a pointer to the MAiNGO logger object
 * @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
 */
std::shared_ptr<LowerBoundingSolver> make_two_stage_lbp_solver(
  const std::shared_ptr<maingo::TwoStageModel> twoStageModel,
  mc::FFGraph &DAG,
  const std::vector<mc::FFVar> &DAGvars,
  const std::vector<mc::FFVar> &DAGfunctions,
  const std::vector<babBase::OptimizationVariable> &variables,
  const std::vector<bool> &_variableIsLinear,
  const unsigned nineqIn,
  const unsigned neqIn,
  const unsigned nineqRelaxationOnlyIn,
  const unsigned neqRelaxationOnlyIn,
  const unsigned nineqSquashIn,
  std::shared_ptr<Settings> settingsIn,
  std::shared_ptr<Logger> loggerIn,
  std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn){
  PROFILE_FUNCTION()

  switch (settingsIn->LBP_solver) {
    case LBP_SOLVER_MAiNGO: {
      loggerIn->print_message("      Two-stage lower bounding: MAiNGO internal solver (McCormick relaxations for objective, intervals for constraints)\n",
                              VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<LbpTwoStage<LowerBoundingSolver>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, _variableIsLinear, nineqIn, neqIn,
                                                                nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
    }
    case LBP_SOLVER_INTERVAL: {
      loggerIn->print_message("      Two-stage lower bounding: Interval extensions\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<LbpTwoStage<LbpInterval>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, _variableIsLinear, nineqIn, neqIn,
                                                        nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
    }
    case LBP_SOLVER_CPLEX: {
#ifdef HAVE_CPLEX
      loggerIn->print_message("      Two-stage lower bounding: CPLEX\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<LbpTwoStage<LbpCplex>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, _variableIsLinear, nineqIn, neqIn,
                                                     nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
#else
      throw MAiNGOException("  Error in LbpTwoStage: Cannot use lower bounding strategy LBP_SOLVER_CPLEX: Your MAiNGO build does not contain CPLEX.");
#endif
    }
    case LBP_SOLVER_GUROBI: {
#ifdef HAVE_GUROBI
        loggerIn->print_message("      Two-stage lower bounding: Gurobi\n", VERB_NORMAL, BAB_VERBOSITY);
        return std::make_shared<LbpTwoStage<LbpGurobi>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, _variableIsLinear, nineqIn, neqIn,
                                                     nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
#else
        throw MAiNGOException("  Error in LbpTwoStage: Cannot use lower bounding strategy LBP_SOLVER_GUROBI: Your MAiNGO build does not contain Gurobi.");
#endif
    }
    case LBP_SOLVER_CLP: {
      loggerIn->print_message("      Two-stage lower bounding: CLP\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<LbpTwoStage<LbpClp>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, _variableIsLinear, nineqIn, neqIn,
                                                   nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
    }
    case LBP_SOLVER_SUBDOMAIN: {
      loggerIn->print_message("      Two-stage lower bounding: Interval extensions (or Centered form) with subintervals\n", VERB_NORMAL, BAB_VERBOSITY);
      return std::make_shared<LbpTwoStage<LbpSubinterval>>(twoStageModel, DAG, DAGvars, DAGfunctions, variables, _variableIsLinear, nineqIn, neqIn,
                                                        nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
    }
    default:
    {  // GCOVR_EXCL_START
      std::ostringstream errmsg;
      errmsg << "  Error in LbpTwoStage Factory: Unknown lower bounding solver: " << settingsIn->LBP_solver;
      throw MAiNGOException(errmsg.str());
    }
    // GCOVR_EXCL_STOP
  }
}


}    // end of namespace lbp


}    // end of namespace maingo
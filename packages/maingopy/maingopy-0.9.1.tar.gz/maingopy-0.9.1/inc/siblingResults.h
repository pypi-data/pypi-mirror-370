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

#include "lbp.h"

#include <vector>
#include <array>

namespace babBase {

class BabNode;

}  // namespace babBase


using babBase::BabNode;

namespace maingo {

namespace lbp {

/**
 * @brief Struct for storing results of a sibling iteration
 */
struct SiblingResults {
  const unsigned int Nx;
  const unsigned int Ny;
  const unsigned int Ns;
  const std::vector<double> &w;
  bool feasible;  // set to true only if each scenario is determined to be feasible in at least one sibling by lower bounding
  bool converged;  // set to true only if parent is converged
  bool foundNewFeasiblePoint;  // set to true only if point is found
  unsigned int nAddedLBSolves = 0;
  std::vector<double> ubpSolutionPoint;
  double ubpObjectiveValue;
  double parentPruningScore;  // updated based on minimum sibling pruning score
  std::vector<double> parentObjectiveBounds;
  std::array<BabNode, 2> siblings;
  std::vector<std::array<babBase::BabNode, 2>> siblingSubNodes;
  std::array<std::vector<double>, 2> objectiveBounds;
  std::array<std::vector<LbpDualInfo>, 2> dualInfo;
  std::array<std::vector<std::vector<double>>, 2> solutions;
  std::array<std::vector<std::vector<double>>, 2> lowerBounds;
  std::array<std::vector<std::vector<double>>, 2> upperBounds;

  SiblingResults(std::vector<double> &w, unsigned int Nx, unsigned int Ny):
      Nx(Nx), Ny(Ny), Ns(w.size()), w(w),
      parentObjectiveBounds(Ns, std::numeric_limits<double>::infinity()),
      objectiveBounds({{std::vector<double>(Ns, std::numeric_limits<double>::infinity()),
                        std::vector<double>(Ns, std::numeric_limits<double>::infinity())}}),
      solutions({{std::vector<std::vector<double>>(Ns),
                  std::vector<std::vector<double>>(Ns)}}),
      lowerBounds({{std::vector<std::vector<double>>(Ns, std::vector<double>(Nx + Ny, std::numeric_limits<double>::infinity())),
                    std::vector<std::vector<double>>(Ns, std::vector<double>(Nx + Ny, std::numeric_limits<double>::infinity()))}}),
      upperBounds({{std::vector<std::vector<double>>(Ns, std::vector<double>(Nx + Ny, -std::numeric_limits<double>::infinity())),
                    std::vector<std::vector<double>>(Ns, std::vector<double>(Nx + Ny, -std::numeric_limits<double>::infinity()))}})
      {};

  void reset(BabNode &&lowerSibling, BabNode &&upperSibling, std::vector<double> &parentSubproblemBounds) {
    feasible = false;
    converged = false;
    foundNewFeasiblePoint = false;
    nAddedLBSolves = 0;
    ubpObjectiveValue = std::numeric_limits<double>::infinity();
    parentPruningScore = lowerSibling.get_pruning_score();

    if (parentSubproblemBounds.size() == Ns) {
        // We have one set of bounds
        parentObjectiveBounds = parentSubproblemBounds;
    }
    else {
        /** The parent was an orthant node.
         *  We have two sets of bounds:
         *  1) The first Ns values are subproblem bounds based on the original parent subproblem bounds and are used to compute strong branching scores.
         *  2) The remaining values are subproblem bounds based on the tightened parent subproblem bounds and are used to compute scenario upper bounds and pruning scores.
         */
        parentObjectiveBounds.assign(parentSubproblemBounds.begin() + Ns, parentSubproblemBounds.end());
        parentSubproblemBounds.resize(Ns);
    }
    objectiveBounds[0] = parentSubproblemBounds;
    objectiveBounds[1] = parentSubproblemBounds;

    siblings = {lowerSibling, upperSibling};
    siblingSubNodes = {Ns, {{siblings[0], siblings[1]}}};
    dualInfo = {{std::vector<LbpDualInfo>(Ns),
                 std::vector<LbpDualInfo>(Ns)}};
    solutions = {{std::vector<std::vector<double>>(Ns),
                 std::vector<std::vector<double>>(Ns)}};
    lowerBounds = {{std::vector<std::vector<double>>(Ns, std::vector<double>(Nx + Ny, std::numeric_limits<double>::infinity())),
                   std::vector<std::vector<double>>(Ns, std::vector<double>(Nx + Ny, std::numeric_limits<double>::infinity()))}};
    upperBounds = {{std::vector<std::vector<double>>(Ns, std::vector<double>(Nx + Ny, -std::numeric_limits<double>::infinity())),
                   std::vector<std::vector<double>>(Ns, std::vector<double>(Nx + Ny, -std::numeric_limits<double>::infinity()))}};
    ubpSolutionPoint.reserve(Nx + Ns * Ny);
    ubpSolutionPoint = {};
  };

  const std::vector<double> & get_parent_lower_bounds() const {
      return siblings[0].get_lower_bounds();
  }

  const double & get_parent_lower_bound(unsigned int j) const {
      return siblings[0].get_lower_bound(j);
  }

  void set_parent_lower_bound(unsigned int j, double value) {
      siblings[0].set_lower_bound(j, value);
  }

  const std::vector<double> & get_parent_upper_bounds() const {
      return siblings[1].get_upper_bounds();
  }

  const double & get_parent_upper_bound(unsigned int j) const {
      return siblings[1].get_upper_bound(j);
  }

  void set_parent_upper_bound(unsigned int j, double value) {
      siblings[1].set_upper_bound(j, value);
  }

  /**
   * @brief Check if the parent is infeasible after updating the variable domains for given scenario subproblem with the unions of variable domains for the corresponding sibling subproblems.
   * 
   * @param s Scenario index
   * @param parentSubNode Node representing the parent subproblem
   * @param retcodes Return codes for the sibling subproblems
   * 
   * @returns true if the parent node is infeasible
   */
  bool infeasible_after_parent_tightening(int s, babBase::BabNode & parentSubNode, const std::array<int, 2> &retcodes) {
    // shorthands
    auto ssn0 = siblingSubNodes[s][0];
    auto ssn1 = siblingSubNodes[s][1];
    // First check whether the subproblem of one sibling is infeasible, if so only the other siblings data is relevant.
    if (retcodes[0] < 1) {  // scenario subproblem for sibling 0 is infeasible
      if (retcodes[1] < 1) {
        // both siblings are infeasible, so is the parent
        return true;
      }
      // only use data of sibling 1, independent of whether tightening changed
      for (int i = 0; i < Nx + Ny; ++i) {
        parentSubNode.set_lower_bound(i, ssn1.get_lower_bound(i));
        parentSubNode.set_upper_bound(i, ssn1.get_upper_bound(i));
      }
    }
    // We know scenario subproblem for sibling 0 is feasible
    else if (retcodes[1] < 1) {  // scenario subproblem for sibling 1 is infeasible
      // only use data of sibling 0, independent of whether tightening changed
      for (int i = 0; i < Nx + Ny; ++i) {
        parentSubNode.set_lower_bound(i, ssn0.get_lower_bound(i));
        parentSubNode.set_upper_bound(i, ssn0.get_upper_bound(i));
      }
    }
    // Both sibling subproblems are feasible, so we consider the union of the sibling domains
    else if ((retcodes[0] == 2) || (retcodes[1] == 2)) {  // at least one sibling was tightened
      for (int i = 0; i < Nx + Ny; ++i) {
        // if both siblings were tightened, the union over both siblings is a valid tightening of the parent bounds
        parentSubNode.set_lower_bound(i, std::min(ssn0.get_lower_bound(i), ssn1.get_lower_bound(i)));
        parentSubNode.set_upper_bound(i, std::max(ssn0.get_upper_bound(i), ssn1.get_upper_bound(i)));
      }
    }
    return false;
  }

  /**
   * @brief Check if the parent is infeasible after updating all variable domains with intersections of x-domains and unions of y-domains from the sibling subproblems.
   * 
   * @param parentSubNodes parent subproblem nodes, assumed to contain unions of sibling domains
   * @param retcodes Return codes for the sibling subproblems
   * 
   * @returns true if the parent node is infeasible
   */
  bool infeasible_after_sibling_tightening(std::vector<babBase::BabNode> &parentSubNodes, std::vector <std::array<int, 2>> & retcodes) {
    // Compute intersection over all scenarios of sibling domains for x
    // Since the resulting x domain is also valid for the parent node, we store it directly
    // in the parent bounds (which are just the lower/upper bound of the lower/upper sibling).
    for (int s = 0; s < Ns; ++s) {
      for (int i = 0; i < Nx; ++i) {
        // Update x domain of parent with the intersecion of unions of x domains over all scenarios
        set_parent_lower_bound(i, std::max(get_parent_lower_bound(i), parentSubNodes[s].get_lower_bound(i)));
        set_parent_upper_bound(i, std::min(get_parent_upper_bound(i), parentSubNodes[s].get_upper_bound(i)));
        if (get_parent_lower_bound(i) > get_parent_upper_bound(i)) // x domain of parent node is empty
          return true; // parent (and both siblings) infeasible
      }
      for (int i = 0; i < Ny; ++i) {  // Update y domain of parent with the unions of y domains over all scenarios
        set_parent_lower_bound(Nx + s * Ny + i, parentSubNodes[s].get_lower_bound(Nx + i));
        set_parent_upper_bound(Nx + s * Ny + i, parentSubNodes[s].get_upper_bound(Nx + i));
      }
    }

    // intersect the parent and sibling subproblem domains with the valid subdomain for x
    for (int s = 0; s < Ns; s++) {
      // intersect parent subproblem domains with the parent domains
      for (int i = 0; i < Nx; ++i) {
        parentSubNodes[s].set_lower_bound(i, 
          std::max(get_parent_lower_bound(i), parentSubNodes[s].get_lower_bound(i))
        );
        parentSubNodes[s].set_upper_bound(i, 
          std::min(get_parent_upper_bound(i), parentSubNodes[s].get_upper_bound(i))
        );
      }

      // intersect sibling subproblem domains with the parent domains
      for (int j = 0; j < 2; ++j) {
        if (retcodes[s][j] > 0) {
          for (int i = 0; i < Nx; ++i) {
            siblingSubNodes[s][j].set_lower_bound(i,
              std::max(get_parent_lower_bound(i), siblingSubNodes[s][j].get_lower_bound(i))
            );
            siblingSubNodes[s][j].set_upper_bound(i,
              std::min(get_parent_upper_bound(i), siblingSubNodes[s][j].get_upper_bound(i))
            );
            if (siblingSubNodes[s][j].get_lower_bound(i) > siblingSubNodes[s][j].get_upper_bound(i)) {
              retcodes[s][j] = 0;
              // If other sibling is also infeasible, parent is infeasible
              int j_other = (j == 0) ? 1 : 0;
              if (retcodes[s][j_other] < 1) {
                return true;
              }
            }
          }
        }
      }
    }
    return false;
  }

  /**
   * @brief Tighten parent objective bounds and variable domains based on sibling results
   * 
   * This method assumes that the parent node is not dominated, i.e., for each scenario, at most one sibling subproblem is dominated. 
   * 
   * @param retcodes Return codes for the sibling subproblems
   */
  void tighten_parent_objective_and_variable_bounds(const std::vector <std::array<int, 2>> & retcodes) {
    #ifdef _OPENMP
      #pragma omp parallel for
    #endif
    for (int s = 0; s < Ns; ++s) {
      // Objective: The lower bound from both siblings is a valid (and possibly tighter) lower bound for the parent
      if (retcodes[s][0] < 1) {
        this->parentObjectiveBounds[s] = objectiveBounds[1][s];
      }
      else if (retcodes[s][1] < 1) {
        this->parentObjectiveBounds[s] = objectiveBounds[0][s];
      }
      /** NOTE: Eventhough it would be a valid tightening, the following is detrimental.
       *        It would skew the strong branching score calculation and result in poor candidate selection.
       *        This in turn will cause excessive branching on some second-stage variables and thus it
       *        will result in frequent termination due to reaching minimum node size.
       * else {
       *   this->parentObjectiveBounds[s] = std::min(objectiveBounds[0][s], objectiveBounds[1][s]);
       * }
       */

      // Variables: We expect the bounds in subNodes to be tightened variable domains with consistent x subdomains
      for (unsigned int j : {0, 1}) {
        if (retcodes[s][j] > 0) {
          this->lowerBounds[j][s] = siblingSubNodes[s][j].get_lower_bounds();
          this->upperBounds[j][s] = siblingSubNodes[s][j].get_upper_bounds();
        }
      }
    }
  }

  /**
   * @brief Function for updating the parent pruning score to the minimum of all orthant nodes
   */
  void update_parent_pruning_score(std::vector <double> &parentSubproblemBounds) {
    parentPruningScore = 0;
    for (int s = 0; s < Ns; s++) {
      if (solutions[0][s].size() == 0) {
        if (solutions[1][s].size() == 0)
          return;
        objectiveBounds[0][s] = std::numeric_limits<double>::infinity();
        parentSubproblemBounds[s] = objectiveBounds[1][s];
        parentPruningScore += w[s] * objectiveBounds[1][s];
      }
      else if (solutions[1][s].size() == 0) {
        objectiveBounds[1][s] = std::numeric_limits<double>::infinity();
        parentSubproblemBounds[s]  = objectiveBounds[0][s];
        parentPruningScore += w[s] * objectiveBounds[0][s];
      }
      else {
        parentSubproblemBounds[s] = std::min(objectiveBounds[0][s], objectiveBounds[1][s]);
        parentPruningScore += w[s] * std::min(objectiveBounds[0][s], objectiveBounds[1][s]);
      }
    }
  }

  /**
   * @brief Function to calculate size of serializedSiblingResults
   * 
   * The serialization consists of a concatenation of:
   * - subproblem objective bounds for the parent
   * - subproblem objective bounds for the lower sibling
   * - subproblem objective bounds for the upper sibling
   * - lower bounding solutions for the lower sibling
   * - lower bounding solutions for the upper sibling
   * - lower bounds for the lower sibling
   * - lower bounds for the upper sibling
   * - upper bounds for the lower sibling
   * - upper bounds for the upper sibling
   * 
   * @returns serializedSiblingResultsSize
   */
  static size_t getSerializedSiblingResultsSize(int Nx, int Ny, int Ns) {
      return (
          1 * Ns                      // parentSubproblemBounds
          + 2 * Ns                    // objectiveBounds for both siblings
          + 2 * Ns * (Nx + Ny)        // lower bounding solutions for both siblings
          + 2 * 2 * Ns * (Nx + Ny)    // lower and upper bounds for all scenario subproblems of both siblings
      );
  }

  /**
   * @brief Function for serializig SiblingResults data to a single double vector
   * 
   * The serialization consists of a concatenation of:
   * - subproblem objective bounds for the parent
   * - subproblem objective bounds for the lower sibling
   * - subproblem objective bounds for the upper sibling
   * - lower bounding solutions for the lower sibling
   * - lower bounding solutions for the upper sibling
   * - lower bounds for the lower sibling
   * - lower bounds for the upper sibling
   * - upper bounds for the lower sibling
   * - upper bounds for the upper sibling
   * 
   * @param[out] serializedSiblingResults The serialized data
   * @param[in] fathomed_subproblems indicating which subproblems have been fathomed
   * 
   * NOTE: fathomed_subproblems uses int8_t instead of bool because due to its special implementation std::vector<bool> cannot be sent directly via MPI
   */
  void serialize(std::vector<double> &serializedSiblingResults, std::vector<int8_t> &fathomed_subproblems) const {
    fathomed_subproblems.resize(2 * Ns, false);
    serializedSiblingResults.reserve(getSerializedSiblingResultsSize(Nx, Ny, Ns));
    serializedSiblingResults.insert(serializedSiblingResults.end(), parentObjectiveBounds.begin(), parentObjectiveBounds.end());
    serializedSiblingResults.insert(serializedSiblingResults.end(), objectiveBounds[0].begin(), objectiveBounds[0].end());
    serializedSiblingResults.insert(serializedSiblingResults.end(), objectiveBounds[1].begin(), objectiveBounds[1].end());
    for (int j = 0; j < 2; ++j) {
      for (int s = 0; s < Ns; ++s) {
        if (solutions[j][s].size() == 0) {
          fathomed_subproblems[j * Ns + s] = true;
        }
        else {
          serializedSiblingResults.insert(serializedSiblingResults.end(), solutions[j][s].begin(), solutions[j][s].end());
        }
      }
    }
    for (int j = 0; j < 2; ++j) {
        for (int s = 0; s < Ns; ++s) {
            serializedSiblingResults.insert(serializedSiblingResults.end(), lowerBounds[j][s].begin(), lowerBounds[j][s].end());
        }
    }
    for (int j = 0; j < 2; ++j) {
        for (int s = 0; s < Ns; ++s) {
            serializedSiblingResults.insert(serializedSiblingResults.end(), upperBounds[j][s].begin(), upperBounds[j][s].end());
        }
    }
  }

  /**
   * @brief Function for updating the state of SiblingResults with serializedSiblingResults
   * 
   * @param[in] lowerSibling The lower sibling node
   * @param[in] upperSibling The upper sibling node
   * @param[in] serializedSiblingResults The serialized data to be stored
   * @param[in] fathomed_subproblems indicating which subproblems have been fathomed
   */
  void deserialize(const babBase::BabNode &lowerSibling, const babBase::BabNode &upperSibling,
                   std::vector<double> &serializedSiblingResults, const std::vector<int8_t> &fathomed_subproblems){
    siblings = {lowerSibling, upperSibling};
    auto it = serializedSiblingResults.begin();
    parentObjectiveBounds.assign(it, it + Ns);
    it += Ns;
    objectiveBounds[0].assign(it, it + Ns);
    it += Ns;
    objectiveBounds[1].assign(it, it + Ns);
    it += Ns;
    for (int j = 0; j < 2; ++j) {
      for (int s = 0; s < Ns; ++s) {
        if (fathomed_subproblems[j * Ns + s]) {
          solutions[j][s] = {};
        }
        else {
          solutions[j][s].assign(it, it + Nx + Ny);
        }
        it += Nx + Ny;
      }
    }
    for (int j = 0; j < 2; ++j) {
      for (int s = 0; s < Ns; ++s) {
        lowerBounds[j][s].assign(it, it + Nx + Ny);
        it += Nx + Ny;
      }
    }
    for (int j = 0; j < 2; ++j) {
      for (int s = 0; s < Ns; ++s) {
        upperBounds[j][s].assign(it, it + Nx + Ny);
        it += Nx + Ny;
      }
    }
    // clip to subproblem objective bounds for the parent
    serializedSiblingResults.resize(Ns);
    // Recompute parent pruning score
    parentPruningScore = 0;
    for (int s = 0; s < Ns; s++) {
        if (solutions[0][s].size() == 0) {
            parentPruningScore += w[s] * objectiveBounds[1][s];
        }
        else if (solutions[1][s].size() == 0) {
            parentPruningScore += w[s] * objectiveBounds[0][s];
        }
        else {
            parentPruningScore += w[s] * std::min(objectiveBounds[0][s], objectiveBounds[1][s]);
        }
    }
  }
};

}    // namespace lbp

}    // namespace maingo
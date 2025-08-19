/**********************************************************************************
 * Copyright (c) 2019-2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "babBrancher.h"
#include <map>


using namespace babBase;


////////////////////////////////////////////////////////////////////////////////////////
// Constructor for brancher class
Brancher::Brancher(const std::vector<OptimizationVariable>& variables, const std::string& dotfile):
    _globalOptimizationVariables(variables), _internalBranchAndBoundTree(dotfile), _Nx(0), _Ny(0)
{
    _branching_function = &Brancher::_default_branching;
    set_branching_dimension_selection_strategy(enums::BV::BV_PSCOSTS);
    _node_score_calculating_function = low_pruning_score_first;
    _pseudocosts_down                = std::vector<double>(variables.size(), 0);
    _pseudocosts_up                  = _pseudocosts_down;
    _number_of_trials_down           = std::vector<int>(variables.size(), 0);
    _number_of_trials_up             = _number_of_trials_down;
}


////////////////////////////////////////////////////////////////////////////////////////
// Set new branching dimension selection strategy
void
Brancher::set_branching_dimension_selection_strategy(const enums::BV branchingVarStratSelection)
{
    switch (branchingVarStratSelection) {
        case enums::BV_ABSDIAM:
            // Search for largest delta p and select that variable to branch on
            _select_branching_dimension = select_branching_dimension_absdiam;
            break;
        case enums::BV_RELDIAM:
            _select_branching_dimension = select_branching_dimension_reldiam;
            break;
        case enums::BV_PSCOSTS:
            using namespace std::placeholders;    // for _1, _2, _3
            _select_branching_dimension = std::bind(&Brancher::_select_branching_dimension_pseudo_costs, this, _1, _2, _3, _4);
            break;
        default:
            throw(BranchAndBoundBaseException("Error in bab - branching variable selection"));
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// Set the node selection strategy
void
Brancher::set_node_selection_strategy(const enums::NS nodeSelectionStratType)
{
    _internalBranchAndBoundTree.set_node_selection_strategy(nodeSelectionStratType);
}


////////////////////////////////////////////////////////////////////////////////////////
// Set the function for calculating node scores
void
Brancher::set_node_selection_score_function(
    std::function<double(const BabNode&, const std::vector<OptimizationVariable>&)> newNodeScoreFunction)
{
    _node_score_calculating_function = newNodeScoreFunction;
}


////////////////////////////////////////////////////////////////////////////////////////
// Registers the changes made to a node during processing to extract information for branching heuristics.
void
Brancher::register_node_change(const int Id, const BabNode& nodeAfterProcessing)
{

    auto it = std::find_if(_nodesWaitingForResponse.begin(), _nodesWaitingForResponse.end(), [Id](const std::tuple<unsigned, double, BranchingHistoryInfo>& s) { return (std::get<0>(s) == Id); });
    // here pseudocosts could be calculated by calling _update_branching_scores
    // it points to the nodeBeforeChanges
    if (it != _nodesWaitingForResponse.end()) {
        BranchingHistoryInfo info                             = std::move(std::get<2>(*it));
        int variableInd                                       = info.branchVar;
        BranchingHistoryInfo::BranchStatus branchingDirection = info.branchStatus;
        if ((branchingDirection != BranchingHistoryInfo::BranchStatus::wasNotBranched)) {
            double originalPruningScore            = std::get<1>(*it);
            double originalLowerBound              = info.parentLowerBound;
            double originalUpperBound              = info.parentUpperBound;
            double originalRelaxationSolutionPoint = info.relaxationSolutionPointForBranchingVariable;

            double branchingPoint = _calculate_branching_point(originalLowerBound, originalUpperBound, originalRelaxationSolutionPoint);
            double dminus, dplus;
            std::tie(dminus, dplus) = calculate_pseudocost_multipliers_minus_and_plus(_globalOptimizationVariables[variableInd].get_variable_type(), originalLowerBound, originalUpperBound, branchingPoint, originalRelaxationSolutionPoint);

            if (branchingDirection == BranchingHistoryInfo::BranchStatus::wasBranchedUp)    // we have one observation what happened after branching up
            {
                int K                = _number_of_trials_up[variableInd];
                double oldPseudocost = _pseudocosts_up[variableInd];
                if (K == 0)
                    oldPseudocost = 0;
                _pseudocosts_up[variableInd]      = (K * oldPseudocost + (nodeAfterProcessing.get_pruning_score() - originalPruningScore) / (dplus) / (this->get_pruning_score_threshold() - originalPruningScore)) / (K + 1);
                _number_of_trials_up[variableInd] = K + 1;
            }
            else {
                int K                = _number_of_trials_down[variableInd];
                double oldPseudocost = _pseudocosts_down[variableInd];
                if (K == 0)
                    oldPseudocost = 0;

                _pseudocosts_down[variableInd]      = (K * oldPseudocost + (nodeAfterProcessing.get_pruning_score() - originalPruningScore) / (dminus) / (this->get_pruning_score_threshold() - originalPruningScore)) / (K + 1);
                _number_of_trials_down[variableInd] = K + 1;
            }
        }
        _nodesWaitingForResponse.erase(it);
    }
    else {
        throw BranchAndBoundBaseException("Registered Id not found, called with node:", nodeAfterProcessing);
    }
}

void Brancher::register_node_status(const BabNode &n, const enums::NodeStatus s) {
    _internalBranchAndBoundTree.register_node_status(n, s);
}

////////////////////////////////////////////////////////////////////////////////////////
// Inserts the root node into the tree.
void
Brancher::insert_root_node(const BabNode& rootNode)
{
    _internalBranchAndBoundTree.add_node(this->_create_node_with_info_from_node(rootNode, 0, BranchingHistoryInfo::BranchStatus::wasNotBranched, 0, 0, 0));
}


////////////////////////////////////////////////////////////////////////////////////////
// Function that branches on a node and (normally) adds two new children to the BranchAndBoundTree.
/** NOTE: the values passed in for the relaxationSolutionObjValue argument are not necessarily the objective values from the LP relaxation!
 * They may have also be obtained via interval arithmetic!
 * In any case, this argument is currently never used.
 */
std::pair<bool /*isFixed*/, bool /*canBeConsideredFixed*/>
Brancher::branch_on_node(BabNode& parentNode,
                         const std::vector<double>& relaxationSolutionPoint,
                         double relaxationSolutionObjValue,
                         double relNodeSizeTol)
{
    std::vector<double> parentLowerBounds = parentNode.get_lower_bounds();
    std::vector<double> parentUpperBounds = parentNode.get_upper_bounds();
    bool nodeIsFixed                      = false;
    bool nodeCanBeThreatedAsFixed         = false;

    {
        std::vector<double> boundDifference;
        std::vector<double> relBoundDifference;
        boundDifference.reserve(parentLowerBounds.size());
        std::transform(parentLowerBounds.begin(), parentLowerBounds.end(), parentUpperBounds.begin(), std::back_inserter(boundDifference), [](double a, double b) { return b - a; });
        //   no gap between upper and lower (   upper>  lower )  left
        nodeIsFixed = std::none_of(boundDifference.begin(), boundDifference.end(), [](double val) { return val > 0.0; });


        for (size_t i = 0; i < boundDifference.size(); ++i) {
            // need to account for the case where a variable was initially already fixed
            double init_gap = _globalOptimizationVariables[i].get_upper_bound() - _globalOptimizationVariables[i].get_lower_bound();
            relBoundDifference.push_back((init_gap > 0) ? (boundDifference[i] / init_gap) : 0.);
        }
        //  if all dimensions have a relative ( to the original bounds)  gap between the bounds smaller than the given tolerance
        nodeCanBeThreatedAsFixed = std::none_of(relBoundDifference.begin(), relBoundDifference.end(), [relNodeSizeTol](double relSizeOfDimension) { return relSizeOfDimension > relNodeSizeTol; });
    }
    if (nodeIsFixed)    // Only happens for pure integer problems
    {
        // The node has been fixed, e.g. by probing.
        // Is readded to the tree, because it may need to be solved one more time.
        // all but the first argument are
        _internalBranchAndBoundTree.add_node(this->_create_node_with_info_from_node(parentNode, 0, BranchingHistoryInfo::BranchStatus::wasNotBranched, 0, 0, 0));
    }
    else if (nodeCanBeThreatedAsFixed)    // May also happen for problems with continuous variables if the node becomes too small due to excessive branching
    {
        // logged outside
    }
    else {
        unsigned int branchVar;
        double branchVarValue;
        _set_branching_variable_and_value(parentNode, relaxationSolutionPoint, relaxationSolutionObjValue,
                                          branchVar, branchVarValue);
        (this->*_branching_function)(parentNode, branchVar, branchVarValue, relaxationSolutionPoint);
    }
    return std::make_pair(nodeIsFixed, nodeCanBeThreatedAsFixed);
}

void
Brancher::_set_branching_variable_and_value(const BabNode& parentNode,
                                            const std::vector<double>& relaxationSolutionPoint,
                                            double relaxationSolutionObjValue,
                                            unsigned& branchVar,
                                            double& branchVarValue) {
    branchVar = _select_branching_dimension(
        parentNode, relaxationSolutionPoint, relaxationSolutionObjValue, this->_globalOptimizationVariables);
    branchVarValue = _get_relaxation_solution_value(parentNode, relaxationSolutionPoint, branchVar);
}

double Brancher::_get_relaxation_solution_value(const BabNode& parentNode,
                                                const std::vector<double>& relaxationSolutionPoint,
                                                unsigned & branchVar) {
  const std::vector<double> & parentLowerBounds(parentNode.get_lower_bounds()), parentUpperBounds(parentNode.get_upper_bounds());
  if (relaxationSolutionPoint.size() != parentLowerBounds.size()) {
    return 0.5 * (parentLowerBounds[branchVar] + parentUpperBounds[branchVar]);
  }
  else {
    return relaxationSolutionPoint[branchVar];
  }
}

std::vector<double> Brancher::_get_relaxation_solution_values(const BabNode & parentNode,
                                                              const std::vector<double> & relaxationSolutionPoint,
                                                              const std::vector<unsigned> & branchVars) {
  const std::vector<double> parentLowerBounds(parentNode.get_lower_bounds()), parentUpperBounds(parentNode.get_upper_bounds());
  std::vector<double> branchVarValues = {};
  branchVarValues.reserve(branchVars.size());
  for (auto branchVar : branchVars) {
    if (relaxationSolutionPoint.size() != parentLowerBounds.size()) {
      branchVarValues.push_back(0.5 * (parentLowerBounds[branchVar] + parentUpperBounds[branchVar]));
    }
    else {
      branchVarValues.push_back(relaxationSolutionPoint[branchVar]);
    }
  }
  return branchVarValues;
}

void Brancher::_default_branching(const BabNode& parentNode,
                                  unsigned int branchVar,
                                  double branchVarValue,
                                  const std::vector<double>& __unused) {
  std::pair<BabNodeWithInfo, BabNodeWithInfo> children = _create_children(branchVar, parentNode, branchVarValue);
}

void Brancher::_two_stage_branching(const BabNode& parentNode,
                                    unsigned int branchVar,
                                    double branchVarValue,
                                    const std::vector<double>& relaxationSolutionPoint) {
  if (branchVar < _Nx) {
    _default_branching(parentNode, branchVar, branchVarValue);
    return;
  }
  // Branching on Ns second-stage variables
  unsigned _Ns = (parentNode.get_lower_bounds().size() - _Nx) / _Ny;
  int iyVar = branchVar - _Nx;
  int iy = iyVar % _Ny;
  // int is = iyVar / _Ny;
  std::vector<unsigned> branchVars = {};
  branchVars.reserve(_Ns);
  for (unsigned s = 0; s < _Ns; s++) {
    unsigned branchVar_s = _Nx + s * _Ny + iy;
    branchVars.push_back(branchVar_s);
  }

  std::vector<double> branchVarValues;
  branchVarValues = _get_relaxation_solution_values(parentNode, relaxationSolutionPoint, branchVars);
  _setup_siblings(parentNode, branchVars, branchVarValues);
}

bool
Brancher::find_sibling(const BabNode &node, BabNode &sibling) {
  if (_internalBranchAndBoundTree._sibling_map.size() == 0) {
    return false;
  }
  auto it = _internalBranchAndBoundTree._sibling_map.find(node.get_ID());
  bool res = (it != _internalBranchAndBoundTree._sibling_map.end());
  if (res) {
    sibling = it->second;
    _internalBranchAndBoundTree._sibling_map.erase(it);
  }
  return res;
}

void
Brancher::multisect_parent_node(
  const double parentPruningScore,
  const std::vector<double> & parentObjectiveBounds,
  const std::array<BabNode, 2> & siblings,
  const std::array<std::vector<double>, 2> & objectiveBounds,
  const std::array<std::vector<std::vector<double>>, 2> & subproblemSolutions,
  const std::array<std::vector<std::vector<double>>, 2> & subproblemLowerBounds,
  const std::array<std::vector<std::vector<double>>, 2> & subproblemUpperBounds,
  unsigned int & _nNodesFathomed,
  double & _bestLbdFathomed,
  const std::function<bool(unsigned int, double)> &dominance_test,
  const std::function <
    void(
      babBase::BabNode &orthantNode,
      const std::vector<unsigned int> &bits,
      const std::array<std::vector<double>, 2> &objectiveBounds
    )
  > &postprocess_orthant,
  const double relNodeSizeTol
) {
  unsigned Id = siblings[0].get_ID();
  unsigned Ns = parentObjectiveBounds.size();

  /** Recover branched variables */
  auto it = std::find_if(_nodesWaitingForResponse.begin(), _nodesWaitingForResponse.end(),
                         [Id](const std::tuple<unsigned, double, BranchingHistoryInfo>& nodeData) { return (std::get<0>(nodeData) == Id); });
  std::vector<unsigned int> branchVars;
  branchVars.reserve(Ns);
  if (it != _nodesWaitingForResponse.end()) {
    branchVars.push_back(std::get<2>(*it).branchVar);  /** NOTE: We have set the first second stage variable to be the branching variable in _setup_siblings! */
    /** TODO: If necessary, we can update the pseudocosts as in register_node_change here! */
    _nodesWaitingForResponse.erase(it);
  }
  else {
    std::ostringstream oss;
    oss << "Node " << Id << " was not found in the list of nodes waiting for response!";
    throw std::runtime_error(oss.str());
  }
  for (int s = 1; s < Ns; s++) {
    branchVars.push_back(branchVars[s-1] + _Ny);
  }

  /** 
   * Decide on which of the second-stage variables we should actually branch.
   * If for any scenario the subproblems of both siblings are infeasible, the
   * parent node is infeasible and we continue without doing any further work.
   * If for any scenario the subproblem of exactly one sibling is infeasible,
   * we branch on the corresponding second-stage variable, but only create the
   * feasible orthants resulting from the subproblem of the feasible sibling
   * subproblem.
   * For the remaining scenarios we compute strong-branching scores and then
   * select the k best ones, where k is min(k_max_user, k_alpha), where
   * k_max_user is a user-given constant, and k_alpha is the number of
   * scenarios with a score of at least alpha * 100% of the best finite one.
   */
  
  // Get map from indices of partially feasible branchings to the sibling for
  // which the subproblem is feasible
  std::map<unsigned int, bool> infeasibleIndices; 
  for (int s = 0; s < Ns; s++) {
    if (subproblemSolutions[0][s].size() == 0) {
      if (subproblemSolutions[1][s].size() == 0) {
        return; /** Both subproblems are infeasible, so the parent node is infeasible! */
      }
      else {
        infeasibleIndices[s] = 1;
      }
    }
    else if (subproblemSolutions[1][s].size() == 0) {
      infeasibleIndices[s] = 0;
    }
  }
  int k_inf = infeasibleIndices.size();

  // Handles for parent bounds
  auto & parentLB = siblings[0].get_lower_bounds();
  auto & parentUB = siblings[1].get_upper_bounds();

  // Use the data from sibling (bit = 0 or 1) or parent (bit = 2) for the orthant
  auto update_orthant_data = [&](
    std::vector<double> &lb, std::vector<double> &ub, std::vector<double> &bp,
    double & pruningScore, unsigned int bit, unsigned int s
  ) {
    if (bit == 2) {
      // parent data, don't update bounds, contribution to bp is just midpoint
      for (unsigned int i = 0; i < _Nx; ++i) {
        bp[i] += 0.5 * (parentLB[i] + parentUB[i]) * _w[s];
      }
      for (unsigned int i = 0; i < _Ny; ++i) {
        auto isp                   = _Nx + i;
        auto ifp                   = isp + s * _Ny;
        bp[ifp] = 0.5 * (parentLB[isp] + parentUB[isp]);
      }
      // We can use the tighter of the two sibling bounds for pruning score calculation
      pruningScore += std::min(objectiveBounds[0][s], objectiveBounds[1][s]) * _w[s];
    }
    else {  // sibling data (note that actual branching point is currently always midpoint!)
      auto& lbs = subproblemLowerBounds[bit][s];
      auto& ubs = subproblemUpperBounds[bit][s];
      for (unsigned int i = 0; i < _Nx; ++i) {
        lb[i] = std::max(lb[i], lbs[i]);
        ub[i] = std::min(ub[i], ubs[i]);
        if (ub[i] < lb[i]) {
          return 0; /** The orthant is infeasible! */
        }
        // bp[i] += subproblemSolutions[bit][s][i] * _w[s];
        bp[i] += 0.5 * (lbs[i] + ubs[i]) * _w[s];
      }
      for (unsigned int i = 0; i < _Ny; ++i) {
        auto isp = _Nx + i;
        auto ifp = isp + s * _Ny;
        lb[ifp] = lbs[isp];
        ub[ifp] = ubs[isp];
        // bp[ifp] = subproblemSolutions[bit][s][isp];
        bp[ifp] = 0.5 * (lbs[isp] + ubs[isp]);
      }
      pruningScore += objectiveBounds[bit][s] * _w[s];
    }
    return 1; /** The orthant is feasible! */
  };

  if (k_inf == Ns) {
    std::vector<double> olb(parentLB), oub(parentUB), orthantBranchingPoint(oub.size());
    double pruningScore = 0;

    for (const auto & pair : infeasibleIndices) {
      const unsigned int& s = pair.first;
      const bool& bit       = pair.second;
      bool feasible = update_orthant_data(olb, oub, orthantBranchingPoint, pruningScore, bit, s);
      if (!feasible) {  // the last orthant is also infeasible, so is the parent node
        _internalBranchAndBoundTree.register_infeasible(siblings[0].get_parent_ID());
        _nNodesFathomed++;
        return;
      }
    }
    // instead of 2^Ns nodes we only get one, the rest are fathomed by infeasibility
    _nNodesFathomed += (1 << Ns) - 1;

    std::vector<std::pair<unsigned int, double>> branchPoints(Ns);
    for (unsigned int s = 0; s < Ns; ++s) {
      branchPoints[s] = std::make_pair(branchVars[s], orthantBranchingPoint[branchVars[s]]);
    }
    unsigned int o_id = _internalBranchAndBoundTree.get_valid_id();
    _internalBranchAndBoundTree.register_open(o_id);
    _internalBranchAndBoundTree.register_branching(siblings[0].get_parent_ID(), parentPruningScore, branchPoints, {o_id});

    // Check if pruningScore proves that the orthant cannot contain a better point
    pruningScore = std::max(pruningScore, parentPruningScore);
    if (dominance_test(o_id, pruningScore)) {    // Ok, fathomed by value dominance
      _internalBranchAndBoundTree.register_dominated(o_id, pruningScore);
      _nNodesFathomed++;
      _bestLbdFathomed = std::min(_bestLbdFathomed, pruningScore);
      return;
    }

    auto orthantNode = BabNode(pruningScore, olb, oub,
                               siblings[0].get_index_dataset(),
                               siblings[0].get_parent_ID(),
                               o_id,
                               siblings[0].get_depth(),
                               siblings[0].get_augment_data());
    std::vector<unsigned int> bits(Ns);
    for (const auto & pair : infeasibleIndices) {
      const unsigned int& s = pair.first;
      const bool& bit       = pair.second;
      bits[s] = bit;
    }

    postprocess_orthant(orthantNode, bits, objectiveBounds);

    // try branching orthant
    bool nodeReachedMinRelNodeSize                   = false;
    std::tie(std::ignore, nodeReachedMinRelNodeSize) = branch_on_node(
        orthantNode, orthantBranchingPoint, orthantNode.get_pruning_score(), relNodeSizeTol);
    if (nodeReachedMinRelNodeSize) {
      _nNodesFathomed++;
      _bestLbdFathomed = std::min(_bestLbdFathomed, orthantNode.get_pruning_score());
    }

    return;
  }

  // Get the strong-branching scores for the remaining scenarios
  std::map<unsigned int, double> strongBranchingScores;
  // iterator to first infeasible scenario 
  auto inf_iter = infeasibleIndices.begin();
  double eps = 1e-6;
  for (int s = 0; s < Ns; s++) {
    if (inf_iter != infeasibleIndices.end() && inf_iter->first == s) {
      inf_iter++;
      continue;
    }
    double delta_d = objectiveBounds[0][s] - parentObjectiveBounds[s];
    double delta_u = objectiveBounds[1][s] - parentObjectiveBounds[s];
    strongBranchingScores[s] = std::max(delta_d, eps) * std::max(delta_u, eps);
  }
  // maximum over strongBranchingScores
  double maxScore = std::max_element(
    strongBranchingScores.begin(),
    strongBranchingScores.end(),
    [](const std::pair<unsigned int, double> & p1, const std::pair<unsigned int, double>& p2) {
        return p1.second < p2.second;
    }
  )->second;

  if (maxScore <= std::pow(eps, 2)) {
    // Ensure the variable instance with the longest edge is branched on finitely by switching to relative width based scores if strong branching scores are too low.
    for (auto& p : strongBranchingScores) {
      unsigned int s           = p.first;
      unsigned int i           = branchVars[s];
      double gap               = parentUB[i] - parentLB[i];
      double initGap           = _globalOptimizationVariables[i].get_upper_bound() - _globalOptimizationVariables[i].get_lower_bound();
      double relSizeDim        = (initGap > 0) ? (gap / initGap) : 0.;
      strongBranchingScores[s] = relSizeDim;
    }
  }

  // sort keys of strongBranchingScores from highest to lowest score
  std::vector<unsigned int> branchedScenarioIndices;
  branchedScenarioIndices.reserve(strongBranchingScores.size());
  for (const auto& entry : strongBranchingScores) {
    branchedScenarioIndices.emplace_back(entry.first);
  }
  std::sort(branchedScenarioIndices.begin(), branchedScenarioIndices.end(),
            [&strongBranchingScores](int a, int b) { return strongBranchingScores[a] > strongBranchingScores[b]; });

  // determine the k best scenarios
  unsigned int k_max = std::min(_k_max, (unsigned int)branchedScenarioIndices.size()), k = 1;
  for (auto& i : branchedScenarioIndices) {
    if ((k == k_max) || (strongBranchingScores[branchedScenarioIndices[k]] < _alpha * strongBranchingScores[branchedScenarioIndices[0]])) {
      break;
    }
    k++;
  }
  branchedScenarioIndices.resize(k);
  std::sort(branchedScenarioIndices.begin(), branchedScenarioIndices.end());
  int numCombinations = 1 << k; // == 2^k

  /** 
   * Generate proto-orthant data which does not change, i.e., scenarios that are:
   * - in infeasibleIndices (i.e., scenarios that are partially infeasible) contain the feasible sibling's data
   * - neither in infeasibleIndices, nor in branchedScenarioIndices (i.e., scenarios that are not branched) contain the parent's data
   */
  std::vector<double> protoLB(parentLB), protoUB(parentUB), protoBranchingPoint(protoUB.size());
  double protoPruningScore = 0;
  std::vector<unsigned int> protoBits(Ns, 3); // unused value 3 for debugging
  for (int s = 0; s < Ns; s++) {
    if (infeasibleIndices.find(s) != infeasibleIndices.end()) {
      auto bit = infeasibleIndices[s];
      protoBits[s] = bit; // scenario is branched; use feasible sibling data
      bool feasible = update_orthant_data(protoLB, protoLB, protoBranchingPoint, protoPruningScore, bit, s);
      if (!feasible) {  // the tightened parent bounds turn out to be infeasible
        _internalBranchAndBoundTree.register_infeasible(siblings[0].get_parent_ID());
        _nNodesFathomed++;
        return;
      }
    }
    else if (
      std::find(
        branchedScenarioIndices.begin(),
        branchedScenarioIndices.end(), s)
        == branchedScenarioIndices.end()
    ) {
      protoBits[s] = 2; // scenario is not branched; use parent data
      bool feasible = update_orthant_data(protoLB, protoUB, protoBranchingPoint, protoPruningScore, 2, s);
      if (!feasible) {  // the tightened parent bounds turn out to be infeasible
        _internalBranchAndBoundTree.register_infeasible(siblings[0].get_parent_ID());
        _nNodesFathomed++;
        return;
      }
    }
  }

  // generate all undominated, feasible orthants
  int o_id = 0;
  std::vector<unsigned int> orthantNodeIds(numCombinations);

  for (int o = 0; o < numCombinations; ++o) {
    o_id = _internalBranchAndBoundTree.get_valid_id();
    orthantNodeIds[o] = o_id;
    _internalBranchAndBoundTree.register_open(o_id);

    // compute the remaining variable bounds
    std::vector<double> olb(protoLB), oub(protoUB), orthantBranchingPoint(protoBranchingPoint);
    double pruningScore = protoPruningScore;
    std::vector<unsigned int> bits(protoBits);

    bool feasible = true;
    for (unsigned int i = 0; i < branchedScenarioIndices.size(); ++i) { // use left or right sibling

      // The second-stage variable for this scenario is branched, so we either use the 
      // left or the right sibling, depending on the value of the bit in position b_i
      auto bit = get_bit(o, i);
      auto s = branchedScenarioIndices[i];
      bits[s] = bit;
      feasible = update_orthant_data(olb, oub, orthantBranchingPoint, pruningScore, bit, s);
      if (!feasible) {
        break;
      }
    }
    if (!feasible) {
      _internalBranchAndBoundTree.register_infeasible(o_id);
      _nNodesFathomed++;
      continue;
    }

    // Check if pruningScore proves that the orthant cannot contain a better point
    pruningScore = std::max(pruningScore, parentPruningScore);
    if (dominance_test(o_id, pruningScore)) {    // Ok, fathomed by value dominance
      _internalBranchAndBoundTree.register_dominated(o_id, pruningScore);
      _nNodesFathomed++;
      _bestLbdFathomed = std::min(_bestLbdFathomed, pruningScore);
      continue;
    }

    /** Node is neither infeasible, nor dominated, so we create it.
     *  As the orthant nodes are already in a processed state, they
     *  don't need to be added to the _internalBranchAndBoundTree.
     *  Instead, we directly branch on them and add the resulting children.
     */
    auto orthantNode = BabNode(pruningScore, olb, oub,
                               siblings[0].get_index_dataset(),
                               siblings[0].get_parent_ID(),
                               o_id,
                               siblings[0].get_depth(),
                               siblings[0].get_augment_data()                               
                               );

    postprocess_orthant(orthantNode, bits, objectiveBounds);

    // try branching orthant
    bool nodeReachedMinRelNodeSize = false;
    std::tie(std::ignore, nodeReachedMinRelNodeSize) = branch_on_node(
        orthantNode, orthantBranchingPoint, orthantNode.get_pruning_score(), relNodeSizeTol);
    if (nodeReachedMinRelNodeSize) {
      _nNodesFathomed++;
      _bestLbdFathomed = std::min(_bestLbdFathomed, orthantNode.get_pruning_score());
    }
  }

  std::vector<unsigned int> actuallybranchedVars;
  actuallybranchedVars.reserve(infeasibleIndices.size() + branchedScenarioIndices.size());
  // Add infeasibleIndices to branchedScenarioIndices
  for (auto& i : infeasibleIndices) {
    actuallybranchedVars.push_back(branchVars[i.first]);
  }
  // Add branchedScenarioIndices
  for (auto& i : branchedScenarioIndices) {
    actuallybranchedVars.push_back(branchVars[i]);
  }

  std::vector<std::pair<unsigned int, double>> branchPoints(actuallybranchedVars.size());
  for (unsigned int i = 0; i < actuallybranchedVars.size(); ++i) {
    auto & var = actuallybranchedVars[i];
    branchPoints[i] = std::make_pair(var, 0.5 * (parentLB[var] + parentUB[var]));
  }
  _internalBranchAndBoundTree.register_branching(siblings[0].get_parent_ID(), parentPruningScore, branchPoints, orthantNodeIds);
}


#ifdef BABBASE_HAVE_GROWING_DATASETS
/////////////////////////////////////////////////////////////////////////////////////////////////
// Function for creating one child from parent node and adding it to BaB tree
void
Brancher::add_node_with_new_data_index(const BabNode& parentNode, const unsigned int newDataIndex)
{
    // Mainly copy of parent node, with new index of dataset and marked as augmented
    BabNode child = BabNode(parentNode.get_pruning_score(), parentNode.get_lower_bounds(), parentNode.get_upper_bounds(), newDataIndex, parentNode.get_ID(), _internalBranchAndBoundTree.get_valid_id(), parentNode.get_depth() + 1, true);

    _internalBranchAndBoundTree.add_node_anyway(this->_create_node_with_info_from_node(child, 0, BranchingHistoryInfo::BranchStatus::wasNotBranched, 0, 0, 0));
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// Passing newThreshold to respective BabTree function (heuristic B&B algorithm with growing datasets)
void
Brancher::update_nodes_for_postprocessing(const double newThreshold)
{
    _internalBranchAndBoundTree.update_nodes_for_postprocessing(newThreshold);
}
#endif // BABBASE_HAVE_GROWING_DATASETS


/////////////////////////////////////////////////////////////////////////////////////////////////
// Helper function for getting all nodes created during strong branching
std::vector<BabNode>
Brancher::get_all_nodes_from_strong_branching(const BabNode& parentNode, const std::vector<double>& relaxationSolutionPoint)
{
    std::vector<BabNode> returnedNodes;
    returnedNodes.reserve(parentNode.get_upper_bounds().size());  // this seems strange, shouldn't it be 2 * parentNode.get_upper_bounds().size() for strong branching?
    for (unsigned i = 0; i < parentNode.get_upper_bounds().size(); i++) {
        unsigned branchVar = i;
        double branchVariableRelaxSolutionPoint;
        if (relaxationSolutionPoint.size() != parentNode.get_upper_bounds().size()) {
            branchVariableRelaxSolutionPoint = 0.5 * (parentNode.get_lower_bounds()[branchVar] + parentNode.get_upper_bounds()[branchVar]);
        }
        else {
            branchVariableRelaxSolutionPoint = relaxationSolutionPoint[branchVar];
        }
        std::pair<BabNodeWithInfo, BabNodeWithInfo> children = _create_children(branchVar, parentNode, branchVariableRelaxSolutionPoint);
        const BabNodeWithInfo& left                          = children.first;
        this->_nodesWaitingForResponse.push_back(std::make_tuple(left.get_ID(), left.get_pruning_score(), left.branchingInfo));
        const BabNodeWithInfo& right = children.second;
        this->_nodesWaitingForResponse.push_back(std::make_tuple(right.get_ID(), right.get_pruning_score(), right.branchingInfo));
        returnedNodes.push_back(std::move(children.first.node));
        returnedNodes.push_back(std::move(children.second.node));
    }
    return returnedNodes;
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// Helper function for creating nodes from parent node once branch variable has been decided
std::pair<BabNodeWithInfo, BabNodeWithInfo>
Brancher::_create_children(unsigned branchVar, const BabNode& parentNode, double branchVariableRelaxSolutionPoint)
{
    // Child nodes inherit dataset of parent node
    const unsigned int parentIndexDataset = parentNode.get_index_dataset();

    // Simple rule for now, split dimension at midpoint
    const std::vector<double>& parentLowerBounds = parentNode.get_lower_bounds();
    const std::vector<double>& parentUpperBounds = parentNode.get_upper_bounds();

    std::vector<double> leftChildUpperBounds(parentUpperBounds);
    std::vector<double> rightChildLowerBounds(parentLowerBounds);
    double branchPoint = _calculate_branching_point(parentLowerBounds[branchVar], parentUpperBounds[branchVar], branchVariableRelaxSolutionPoint);

    enums::VT varType(this->_globalOptimizationVariables[branchVar].get_variable_type());
    switch (varType) {
        case enums::VT_CONTINUOUS:
            leftChildUpperBounds[branchVar]  = branchPoint;
            rightChildLowerBounds[branchVar] = branchPoint;
            break;
        case enums::VT_BINARY:
        case enums::VT_INTEGER:
            // round down continuous-valued upper bounds
            leftChildUpperBounds[branchVar]  = floor(branchPoint);
            rightChildLowerBounds[branchVar] = floor(branchPoint) + 1;
            break;
        default:
            throw(BranchAndBoundBaseException("Error in bab - creating branch nodes: unknown variable type"));
            break;
    }

    BabNode leftChild                  = BabNode(parentNode.get_pruning_score(), parentLowerBounds, leftChildUpperBounds, parentIndexDataset,
                                                 parentNode.get_ID(), _internalBranchAndBoundTree.get_valid_id(),
                                                 parentNode.get_depth() + 1, parentNode.get_augment_data());
    BabNode rightChild                 = BabNode(parentNode.get_pruning_score(), rightChildLowerBounds, parentUpperBounds, parentIndexDataset,
                                                 parentNode.get_ID(), _internalBranchAndBoundTree.get_valid_id(),
                                                 parentNode.get_depth() + 1, parentNode.get_augment_data());
    BabNodeWithInfo leftChildWithInfo  = this->_create_node_with_info_from_node(leftChild, branchVar, BranchingHistoryInfo::BranchStatus::wasBranchedDown, branchVariableRelaxSolutionPoint, parentLowerBounds[branchVar], parentUpperBounds[branchVar]);
    BabNodeWithInfo rightChildWithInfo = this->_create_node_with_info_from_node(rightChild, branchVar, BranchingHistoryInfo::BranchStatus::wasBranchedUp, branchVariableRelaxSolutionPoint, parentLowerBounds[branchVar], parentUpperBounds[branchVar]);

    _internalBranchAndBoundTree.add_node(leftChildWithInfo);
    _internalBranchAndBoundTree.add_node(rightChildWithInfo);
    _internalBranchAndBoundTree.register_branching(parentNode.get_ID(), parentNode.get_pruning_score(), {std::make_pair((unsigned int)branchVar, branchPoint)}, {(unsigned int)leftChild.get_ID(), (unsigned int)rightChild.get_ID()});

    return std::make_pair(leftChildWithInfo, rightChildWithInfo);
}

void
Brancher::_setup_siblings(const BabNode & parentNode, const std::vector<unsigned> & branchVars, const std::vector<double> & branchVarValues) {
    const std::vector<double> & parentLowerBounds = parentNode.get_lower_bounds();
    const std::vector<double> & parentUpperBounds = parentNode.get_upper_bounds();

    std::vector<double> lowerSiblingUpperBounds(parentUpperBounds);
    std::vector<double> upperSiblingLowerBounds(parentLowerBounds);

    unsigned _Ns = (parentLowerBounds.size() - _Nx) / _Ny;
    unsigned lim = _Nx;
    std::vector<std::pair<unsigned int, double>> branchPoints(branchVars.size());
    for (unsigned s = 0; s < _Ns; s++) {
      const unsigned int & branchVar = branchVars[s];
      const double & branchVarValue = branchVarValues[s];
      // Ensure that we branch on second stage variables for different scenarios
      assert (lim <= branchVar && branchVar < lim + _Ny);
      lim += _Ny;

      double branchPoint = _calculate_branching_point(parentLowerBounds[branchVar], parentUpperBounds[branchVar], branchVarValue);
      branchPoints[s]    = std::make_pair(branchVar, branchPoint);
      enums::VT varType(this->_globalOptimizationVariables[branchVar].get_variable_type());
      switch (varType) {
        case enums::VT_CONTINUOUS:
          lowerSiblingUpperBounds[branchVar] = branchPoint;
          upperSiblingLowerBounds[branchVar] = branchPoint;
          break;
        case enums::VT_BINARY:
        case enums::VT_INTEGER:
          // round lower continuous-valued upper bounds
          lowerSiblingUpperBounds[branchVar] = floor(branchPoint);
          upperSiblingLowerBounds[branchVar] = floor(branchPoint + 0.5);
          break;
        default:
          throw(BranchAndBoundBaseException("Error in bab - creating sibling nodes: unknown variable type"));
      }
    }

    BabNode lowerSibling = BabNode(parentNode.get_pruning_score(), parentLowerBounds, lowerSiblingUpperBounds, parentNode.get_index_dataset(),
                                   parentNode.get_ID(), _internalBranchAndBoundTree.get_valid_id(),
                                   parentNode.get_depth() + 1, parentNode.get_augment_data());
    BabNode upperSibling = BabNode(parentNode.get_pruning_score(), upperSiblingLowerBounds, parentUpperBounds, parentNode.get_index_dataset(),
                                   parentNode.get_ID(), _internalBranchAndBoundTree.get_valid_id(),
                                   parentNode.get_depth() + 1, parentNode.get_augment_data());

    /** NOTE: Here we only make a BabNodeWithInfo for one of the sibling nodes
     *        (arbitrarily the one corresponding to the lower orthant).
     *        The other one can be accessed via the _sibling_map later on.
     *        While we effectively branch on Ns variables simultaneously,
     *        the current implementation of BranchingHistoryInfo only allows for
     *        branching on one variable at a time.
     *        As a proxy, we use the second-stage variable corresponding to the
     *        first scenario here.
     */
    auto dummyBranchVar = branchVars[0];
    auto dummyBranchVarValue = branchVarValues[0];
    BabNodeWithInfo dummyNode = this->_create_node_with_info_from_node(
      lowerSibling, dummyBranchVar,
      BranchingHistoryInfo::BranchStatus::wasBranchedDown,
      dummyBranchVarValue,
      parentLowerBounds[dummyBranchVar], parentUpperBounds[dummyBranchVar]
    );

    _internalBranchAndBoundTree.add_node(dummyNode);
    _internalBranchAndBoundTree.register_branching(parentNode.get_ID(), parentNode.get_pruning_score(), branchPoints, {(unsigned int)lowerSibling.get_ID(), (unsigned int)upperSibling.get_ID()});

    _internalBranchAndBoundTree._sibling_map[lowerSibling.get_ID()] = std::move(upperSibling);
}

////////////////////////////////////////////////////////////////////////////////////////
// Creates a node with added information.
BabNodeWithInfo
Brancher::_create_node_with_info_from_node(const BabNode normalNode, unsigned branchVariable, BranchingHistoryInfo::BranchStatus branchStatus, double variableRelaxationSolutionPoint, double parentLowerBound, double parentUpperBound) const
{
    double nodeSelectionScore = _node_score_calculating_function(normalNode, this->_globalOptimizationVariables);

    BabNodeWithInfo nodeWithInfo(normalNode, nodeSelectionScore);
    nodeWithInfo.branchingInfo.branchVar                                   = branchVariable;
    nodeWithInfo.branchingInfo.branchStatus                                = branchStatus;
    nodeWithInfo.branchingInfo.parentLowerBound                            = parentLowerBound;
    nodeWithInfo.branchingInfo.parentUpperBound                            = parentUpperBound;
    nodeWithInfo.branchingInfo.relaxationSolutionPointForBranchingVariable = variableRelaxationSolutionPoint;
    return nodeWithInfo;
}


////////////////////////////////////////////////////////////////////////////////////////
// Decreases the pruning score threshold to the supplied value.
double
Brancher::decrease_pruning_score_threshold_to(const double newThreshold)
{
    if (_internalBranchAndBoundTree.get_pruning_score_threshold() > newThreshold) {
        return this->_internalBranchAndBoundTree.set_pruning_score_threshold(newThreshold);
    }
    else {
        return std::numeric_limits<double>::infinity();
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// Returns the next BabNode to process according to the node selection strategy and node selection scores.
BabNode
Brancher::get_next_node()
{
    BabNodeWithInfo next = _internalBranchAndBoundTree.pop_next_node();

    this->_nodesWaitingForResponse.push_back(std::make_tuple(next.get_ID(), next.get_pruning_score(), next.branchingInfo));
    return std::move(next);
}


////////////////////////////////////////////////////////////////////////////////////////
// When the domain of a variable is branched on, this function decides at which point it is branched (only makes a difference for continous variables).
double
Brancher::_calculate_branching_point(double lowerBound, double upperBound, double relaxationValue) const
{
        return 0.5 * (lowerBound + upperBound);
}


////////////////////////////////////////////////////////////////////////////////////////
// Function for selecting the variable to branch on by choosing the one with the largest diameter
unsigned
babBase::select_branching_dimension_absdiam(const BabNode& parentNode,
                                            const std::vector<double>& relaxationSolutionPoint,
                                            const double relaxationSolutionObjValue,
                                            const std::vector<OptimizationVariable>& globalOptimizationVars)
{
    std::vector<double> lowerVarBounds = parentNode.get_lower_bounds();
    std::vector<double> upperVarBounds = parentNode.get_upper_bounds();
    unsigned branchVar                 = 0;
    double deltaBounds(0);
    double branchDimDistanceOfSolutionPointFromBounds = 0.0;

    for (unsigned i = 0; i < lowerVarBounds.size(); ++i) {
        double distanceOfSolutionPointFromBounds = 0.5;
        if (relaxationSolutionPoint.size() == lowerVarBounds.size()) {
            distanceOfSolutionPointFromBounds = relative_distance_to_closest_bound(relaxationSolutionPoint[i], lowerVarBounds[i], upperVarBounds[i], globalOptimizationVars[i]);
        }
        double scaledAbsoluteDiameter = (upperVarBounds[i] - lowerVarBounds[i]) * globalOptimizationVars[i].get_branching_priority();
        if ((scaledAbsoluteDiameter > deltaBounds) || (scaledAbsoluteDiameter == deltaBounds && distanceOfSolutionPointFromBounds > branchDimDistanceOfSolutionPointFromBounds)) {
            deltaBounds                                = scaledAbsoluteDiameter;
            branchVar                                  = i;
            branchDimDistanceOfSolutionPointFromBounds = distanceOfSolutionPointFromBounds;
        }
    }
    assert(deltaBounds > 0.0);    // make sure if statement was not always false (!)

    return branchVar;
}


////////////////////////////////////////////////////////////////////////////////////////
// Function for selecting the variable to branch on by choosing the one with the largest diameter relative to the original one
unsigned
babBase::select_branching_dimension_reldiam(const BabNode& parentNode,
                                            const std::vector<double>& relaxationSolutionPoint,
                                            const double relaxationSolutionObjValue,
                                            const std::vector<OptimizationVariable>& globalOptimizationVars)
{
    double deltaBounds(0);
    double relSizeDim(0);
    double branchDimDistanceOfSolutionPointFromBounds = 0.0;
    unsigned branchVar                                = 0;
    std::vector<double> lowerVarBounds                = parentNode.get_lower_bounds();
    std::vector<double> upperVarBounds                = parentNode.get_upper_bounds();
    for (unsigned i = 0; i < lowerVarBounds.size(); ++i) {
        // need to account for the case where a variable was initially already fixed
        double gap = upperVarBounds[i] - lowerVarBounds[i];
        double init_gap = globalOptimizationVars[i].get_upper_bound() - globalOptimizationVars[i].get_lower_bound();
        relSizeDim = (init_gap > 0) ? gap / init_gap : 0.;
        // TODO: relNodeSize = std::max(relSizeDim, relNodeSize); Need to add need toBranch Case
        double tmpdeltap(relSizeDim * globalOptimizationVars[i].get_branching_priority());
        double distanceOfSolutionPointFromBounds = 0.5;
        if (relaxationSolutionPoint.size() == lowerVarBounds.size()) {
            distanceOfSolutionPointFromBounds = relative_distance_to_closest_bound(relaxationSolutionPoint[i], lowerVarBounds[i], upperVarBounds[i], globalOptimizationVars[i]);
        }
        if ((tmpdeltap > deltaBounds) || (tmpdeltap == deltaBounds && distanceOfSolutionPointFromBounds > branchDimDistanceOfSolutionPointFromBounds)) {
            deltaBounds                                = tmpdeltap;
            branchVar                                  = i;
            branchDimDistanceOfSolutionPointFromBounds = distanceOfSolutionPointFromBounds;
        }
    }
    assert(deltaBounds > 0.0);    // make sure if statement was not always false (!)
    return branchVar;
}


////////////////////////////////////////////////////////////////////////////////////////
// How to select the dimension in which to branch when using pseudo costs
unsigned
Brancher::_select_branching_dimension_pseudo_costs(const BabNode& parentNode,
                                                   const std::vector<double>& relaxationSolutionPoint,
                                                   const double relaxationSolutionObjValue,
                                                   const std::vector<OptimizationVariable>& globalOptimizationVars) const
{
    // After: Branching and Bounds Tightening Techniques for Non-Convex MINLP from Pietro Belotti et. al

    double alpha                         = 0.15;
    unsigned bestVariableToBranchOnIndex = 0;
    double bestScore                     = 0;
    double dbest;
    for (unsigned variableIndex = 0; variableIndex < globalOptimizationVars.size(); variableIndex++) {

        double delta_i_minus = 0;
        double delta_i_plus  = 0;

        double relaxationSolutionPointAtVariableIndex;
        if (relaxationSolutionPoint.size() != parentNode.get_upper_bounds().size()) {
            relaxationSolutionPointAtVariableIndex = 0.5 * (parentNode.get_lower_bounds()[variableIndex] + parentNode.get_upper_bounds()[variableIndex]);
        }
        else {
            relaxationSolutionPointAtVariableIndex = relaxationSolutionPoint[variableIndex];
        }

        double branchingPoint = _calculate_branching_point(parentNode.get_lower_bounds()[variableIndex], parentNode.get_upper_bounds()[variableIndex], relaxationSolutionPointAtVariableIndex);

        std::tie(delta_i_minus, delta_i_plus) = calculate_pseudocost_multipliers_minus_and_plus(globalOptimizationVars[variableIndex].get_variable_type(), parentNode.get_lower_bounds()[variableIndex], parentNode.get_upper_bounds()[variableIndex], branchingPoint, relaxationSolutionPointAtVariableIndex);

        double estimatedImprovementUp   = _pseudocosts_up[variableIndex] * (delta_i_plus);
        double estimatedImprovementDown = _pseudocosts_down[variableIndex] * (delta_i_minus);

        //double score = globalOptimizationVars[variableIndex].get_branching_priority()*( alpha * std::max(estimatedImprovementUp, estimatedImprovementDown) + (1 - alpha)*std::min(estimatedImprovementUp, estimatedImprovementDown));
        double score = globalOptimizationVars[variableIndex].get_branching_priority() * ((std::max(estimatedImprovementUp, estimatedImprovementDown) + 1.0e-6) * (std::min(estimatedImprovementUp, estimatedImprovementDown) + 1.0e-6));
        if (score > bestScore) {
            bestScore                   = score;
            bestVariableToBranchOnIndex = variableIndex;
            dbest                       = delta_i_plus;
        }
        if (variableIndex == 0) {
            //std::cout << " 0 score " << score << " d" << delta_i_plus<< std::endl;
        }
    }
    //std::cout << "Branching on variable: " << bestVariableToBranchOnIndex << " with score of " << bestScore << "d: "<<dbest<<std::endl;
    // if(bestVariableToBranchOnIndex==0) std::cout << "Branching on variable: " << bestVariableToBranchOnIndex << " with score of " << bestScore << "d: " << dbest << std::endl;
    return bestVariableToBranchOnIndex;
}

//////////////////////////////////////////////////////////
// Calculate the multiplier for calculation of pseudocosts, the definition of the multipliers is for integer variables the change caused by rounding the relaxation solution point up or down
// For continous variables we follow the rb-int-br-rev strategy from Branching and Bounds Tightening Techniques for Non-Convex MINLP from Pietro Belotti et. al
std::pair<double, double>
babBase::calculate_pseudocost_multipliers_minus_and_plus(enums::VT varType, double lowerBound, double upperBound, double branchingPoint, double relaxationSolutionPoint)
{
    double delta_i_minus = 0;
    double delta_i_plus  = 0;
    if (varType == enums::VT_CONTINUOUS) {
        // using rb-int-br-rev for now
        delta_i_minus = upperBound - branchingPoint;
        delta_i_plus  = branchingPoint - lowerBound;
    }
    else {
        delta_i_minus = relaxationSolutionPoint - std::floor(relaxationSolutionPoint);
        delta_i_plus  = std::ceil(relaxationSolutionPoint) - relaxationSolutionPoint;
    }
    return std::make_pair(delta_i_minus, delta_i_plus);
}


////////////////////////////////////////////////////////////////////////////////////////
// Compute distance to closest bound
double
babBase::relative_distance_to_closest_bound(double pointValue, double bound1, double bound2, const babBase::OptimizationVariable& variable)
{
    return std::min(std::abs((pointValue - bound1) / (variable.get_upper_bound() - variable.get_lower_bound())),
                    std::abs((pointValue - bound2) / (variable.get_upper_bound() - variable.get_lower_bound())));
}


////////////////////////////////////////////////////////////////////////////////////////
// Auxiliary function for extracting the node with the lowest pruning score
double
babBase::low_pruning_score_first(const BabNode& candidate, const std::vector<OptimizationVariable>& globalVars)
{
    return -candidate.get_pruning_score();
}


////////////////////////////////////////////////////////////////////////////////////////
// Auxiliary function for extracting the node with the lowest id (i.e., oldest node)
double
babBase::low_id_first(const BabNode& candidate, const std::vector<OptimizationVariable>& globalVars)
{
    return -candidate.get_ID();
}


////////////////////////////////////////////////////////////////////////////////////////
// Auxiliary function for extracting the node with the highest id (i.e., newest node)
double
babBase::high_id_first(const BabNode& candidate, const std::vector<OptimizationVariable>& globalVars)
{
    return candidate.get_ID();
}
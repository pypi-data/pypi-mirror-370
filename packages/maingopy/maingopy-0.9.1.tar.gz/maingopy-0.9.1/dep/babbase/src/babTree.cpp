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

#include "babTree.h"


using namespace babBase;


////////////////////////////////////////////////////////////////////////////////////////
// Constructor of BabTree
BabTree::BabTree(const std::string& dotfile):
    _pruningScoreThreshold(std::numeric_limits<double>::infinity()), _nodesLeft(0), _sibling_map()
{

    _relPruningTol = 0.0;
    _absPruningTol = 0.0;
    _nodeVector.reserve(10000);
    this->set_node_selection_strategy(enums::NS_BESTBOUND);
    this->_Id = 1;
    
    if (dotfile.empty())
        _output_file = nullptr;
    else {
        _output_file = new std::ofstream();
        _output_file->open(dotfile);
        *_output_file << "digraph G {\n";
        _iter = 0;
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// Function for adding node to Bab Tree
// ensure:_nodeVector.begin() points on node with largest nodeSelectionScore, _nodesLeft has increased by 1, node with pruningScore>=pruningThreshold is not added
// no const reference for move see for reasoning https://www.codesynthesis.com/~boris/blog/2012/06/19/efficient-argument-passing-cxx11-part1/
void
BabTree::add_node(BabNodeWithInfo node)
{
  auto& pruningScoreThreshold = this->_pruningScoreThreshold;
  auto& relPruningTol         = this->_relPruningTol;
  auto& absPruningTol         = this->_absPruningTol;
  auto canBePruned            = [pruningScoreThreshold, relPruningTol, absPruningTol](const BabNodeWithInfo& node) { return babBase::larger_or_equal_within_rel_and_abs_tolerance(node.get_pruning_score(), pruningScoreThreshold, relPruningTol, absPruningTol); };
  if (!canBePruned(node)) {
    _nodeVector.emplace_back(node);
    //ensure that maximalValue is at the top, heap invariant
    std::push_heap(_nodeVector.begin(), _nodeVector.end(), NodePriorityComparator());
    _nodesLeft++;
    register_node_status(node.node, enums::NodeStatus::OPEN);
	}
}


#ifdef BABBASE_HAVE_GROWING_DATASETS
////////////////////////////////////////////////////////////////////////////////////////
// Function for adding node to Bab Tree independent of its pruning score
// Note: MAiNGO with growing datasets may need to add nodes which could only be pruned based on a reduced dataset
void
BabTree::add_node_anyway(BabNodeWithInfo node)
{
    _nodeVector.emplace_back(node);
    //ensure that maximalValue is at the top, heap invariant
    std::push_heap(_nodeVector.begin(), _nodeVector.end(), NodePriorityComparator());
    _nodesLeft++;
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// Function for replacing nodes with largest pruning scores by nodes which can be pruned based on a
// smaller pruning score in node vector for postprocessing (heuristic B&B algorithm with growing datasets)
void
BabTree::update_nodes_for_postprocessing(const double newThreshold)
{
    // Auxiliary lambda function for sorting nodes w.r.t. their pruning score
    auto smallerLBD = [](const babBase::BabNode& node1, const babBase::BabNode& node2) { return (node1.get_pruning_score() < node2.get_pruning_score()); };

    // Find element of list with largest pruning score
    auto itMaxScore = std::max_element(_nodesPostprocessing.begin(), _nodesPostprocessing.end(), smallerLBD);
    auto idxMaxScore = std::distance(_nodesPostprocessing.begin(), itMaxScore);

    // Check all nodes which will be pruned based on a reduced dataset
    for (auto &activeNode : _nodeVector) {
        if ((activeNode.node.get_index_dataset() > 0)
            && (larger_or_equal_within_rel_and_abs_tolerance(activeNode.node.get_pruning_score(), newThreshold, _relPruningTol, _absPruningTol)))
        {
            if (_nodesPostprocessing.size() < _nNodesMaxPostprocessing) {
                // If maximum number of nodes in list not reached yet: just append
                _nodesPostprocessing.push_back(activeNode.node);

                // Update iterator to largest element if first node added or if newly added node increases maximum score
                if ((_nodesPostprocessing.size() < 2)
                    || (_nodesPostprocessing[idxMaxScore].get_pruning_score() < (_nodesPostprocessing.back()).get_pruning_score())) {
                    idxMaxScore = _nodesPostprocessing.size()-1;
                }
            }
            else {
                // Else: Overwrite max_element in node list if pruning score of newly found node is smaller
                if (activeNode.node.get_pruning_score() < _nodesPostprocessing[idxMaxScore].get_pruning_score()) {
                    _nodesPostprocessing[idxMaxScore] = activeNode.node;

                    // Update maxGap
                    // Note that multiple nodes may have the same pruning score.
                    // Thus, the largest pruning score in the list may remain constant.
                    itMaxScore = std::max_element(_nodesPostprocessing.begin(), _nodesPostprocessing.end(), smallerLBD);
                    idxMaxScore = std::distance(_nodesPostprocessing.begin(), itMaxScore);
                }
            }
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// Function for for sorting nodesPostprocessing w.r.t. their pruning score (smallest first)
// Used in heuristic B&B algorithm with growing datasets
void
BabTree::sort_nodes_for_postprocessing()
{
    auto smallerLBD = [](const babBase::BabNode& node1, const babBase::BabNode& node2) { return (node1.get_pruning_score() < node2.get_pruning_score()); };
    std::sort(_nodesPostprocessing.begin(), _nodesPostprocessing.end(), smallerLBD);
}
#endif // BABBASE_HAVE_GROWING_DATASETS


///////////////////////////////////////////////////////////////////////////////////////
// Delete an element from the heap while keeping heap invariant intact
void
BabTree::delete_element(std::vector<BabNodeWithInfo>::iterator targetNodeIt)
{
    _nodeVector.erase(targetNodeIt);
    //first entry that no longer fullfills heap property
    std::vector<BabNodeWithInfo>::iterator it = std::is_heap_until(_nodeVector.begin(), _nodeVector.end(), NodePriorityComparator());
    //push each element that is in the last part of the vector that does not fullfill heap property on again.
    for (auto iterator = it; iterator != _nodeVector.end(); iterator++)
        std::push_heap(_nodeVector.begin(), it + 1, NodePriorityComparator());
}


///////////////////////////////////////////////////////////////////////////////////////
// Return the node according to the node selection strategy and removes it from the tree
BabNodeWithInfo
BabTree::pop_next_node()
{
    //this check might have sigificant overhead and be unnecessary since this
    //function should only be called from Brancher which already checks.
    //-> dont promise this check
    if (this->_nodeVector.empty()) {
        throw(BranchAndBoundBaseException("pop_next_node called on empty tree"));
    }

    //get nextNode according to _select_node
    // the selection function is not allowed to change _nodeVector and can thus only return a const_iterator
    std::vector<BabNodeWithInfo>::const_iterator selectedNodeIt = (this->_select_node)(_nodeVector);

    // we have full access to _nodeVector, so we create a iterator that points to the same selected element cf. http://www.aristeia.com/Papers/CUJ_June_2001.pdf
    std::vector<BabNodeWithInfo>::iterator privateSelectedNodeIt = _nodeVector.begin();
    // set private pointer to same location as outside pointer
    std::advance(privateSelectedNodeIt, std::distance<std::vector<BabNodeWithInfo>::const_iterator>(privateSelectedNodeIt, selectedNodeIt));

    // extract the selected Node efficiently, leaving behind an 'empty' node
    BabNodeWithInfo nextNode = std::move(*selectedNodeIt);

    //delete that 'empty' node
    // are we deleting the first element of a heap ? (efficient)
    if (selectedNodeIt == _nodeVector.begin()) {
        //move largest element to the back, while keeping the heap invariant for the rest of the vector
        std::pop_heap(_nodeVector.begin(), _nodeVector.end(), NodePriorityComparator());
        //remove said element
        _nodeVector.pop_back();
    }
    //deleting other element of the heap (less efficient) (still O(log(n))
    else {
        delete_element(privateSelectedNodeIt);
    }
    _nodesLeft--;
    _iter++;
    return nextNode;
}


///////////////////////////////////////////////////////////////////////////////////////
// Find node with lowest pruning score
double
BabTree::get_lowest_pruning_score() const
{
    if (!_nodeVector.empty()) {
        return std::min_element(_nodeVector.begin(), _nodeVector.end(), PruningScoreComparator())->get_pruning_score();
    }
    else {
        return std::numeric_limits<double>::infinity();
    }
}


///////////////////////////////////////////////////////////////////////////////////////
// Find node with lowest pruning score and calculate the difference
double
BabTree::get_pruning_score_gap() const
{
    return _pruningScoreThreshold - get_lowest_pruning_score();
};


///////////////////////////////////////////////////////////////////////////////////////
// Set new threshold for pruning (e.g., new upper bound)
double
BabTree::set_pruning_score_threshold(const double newThreshold)
{
    _pruningScoreThreshold = newThreshold;
    return _fathom_nodes_exceeding_pruning_threshold(newThreshold, _relPruningTol, _absPruningTol);
}


///////////////////////////////////////////////////////////////////////////////////////
// Find nodes with pruning score exceeding the pruning score threshold and remove them from the tree
double
BabTree::_fathom_nodes_exceeding_pruning_threshold(const double newThreshold, double relTol, double absTol)
{
    double minPruningScorePruned = std::numeric_limits<double>::infinity();
    if (!_nodeVector.empty()) {
        //possibly more performant when using unstable_remove_if or partition (e.g. when first element is pruned)
        size_t oldNumberOfNodes                                                = _nodeVector.size();
        auto canBePruned                                                       = [newThreshold, relTol, absTol](const BabNodeWithInfo& node) { return babBase::larger_or_equal_within_rel_and_abs_tolerance(node.get_pruning_score(), newThreshold, relTol, absTol); };
        std::vector<babBase::BabNodeWithInfo>::iterator startOfNodesToBePruned = std::partition(_nodeVector.begin(), _nodeVector.end(), std::not1(std::function<bool(const BabNodeWithInfo&)>(canBePruned)));
        if (startOfNodesToBePruned != _nodeVector.end()) {
            minPruningScorePruned = std::min_element(startOfNodesToBePruned, _nodeVector.end(), PruningScoreComparator())->get_pruning_score();
        }
        for (auto node_it = startOfNodesToBePruned; node_it != _nodeVector.end(); ++node_it) {
            register_node_status(*node_it, enums::NodeStatus::DOMINATED);
            inform_about_fathoming(*node_it);

            auto it = _sibling_map.find((*node_it).get_ID());
            if (it != _sibling_map.end()) {
                // ensure the upper sibling is also registered as fathomed
                inform_about_fathoming(it->second);
                _sibling_map.erase(it);
            }
        }
        _nodeVector.erase(startOfNodesToBePruned, _nodeVector.end());
        std::make_heap(_nodeVector.begin(), _nodeVector.end(), NodePriorityComparator());
        _nodesLeft = _nodesLeft - (oldNumberOfNodes - _nodeVector.size());
    }
    return minPruningScorePruned;
}

void
BabTree::attach_fathom_observer(std::shared_ptr<FathomObserver> observer) {
    _fathomObservers.push_back(observer);
}

void
BabTree::inform_about_fathoming(const BabNode& n) {
    for (auto& l : _fathomObservers) {
        l->observe_fathoming(n);
    }
}

///////////////////////////////////////////////////////////////////////////////////////
// Update the node selection strategy
void
BabTree::set_node_selection_strategy(enums::NS nodeSelectionStrategyType)
{
    switch (nodeSelectionStrategyType) {
        case enums::NS_BESTBOUND:

            _select_node = select_node_highest_priority;
            break;
        case enums::NS_DEPTHFIRST:
            _select_node = select_node_depthfirst;
            break;
        case enums::NS_BREADTHFIRST:
            _select_node = select_node_breadthfirst;
            break;
        default:
            throw(BranchAndBoundBaseException("  Error in babBase::BabTree - node selection"));
    }
};

void BabTree::register_node_status(const BabNode & n, const enums::NodeStatus s) {
    if (_output_file == nullptr)
      return;
    const int Id = n.get_ID();
    switch (s){
      case enums::NodeStatus::OPEN:
        register_open(Id);
        break;
      case enums::NodeStatus::DOMINATED:
        register_dominated(Id, n.get_pruning_score());
        break;
      case enums::NodeStatus::INFEASIBLE:
        register_infeasible(Id);
        break;
      default:  // Other cases are handled elsewhere
        break;
    }
}

void BabTree::register_open(int Id) {
  if (_output_file == nullptr)
    return;
  (*_output_file) << "  " << Id << "[shape=record,color=blue,label=\"" << Id << "|o\"]\n";
}

void BabTree::register_dominated(int Id, double pruningScore) {
  if (_output_file == nullptr)
    return;
  (*_output_file) << "  " << Id << "[color=red,label=\"" << Id << "|{{d|" << _iter << "}|" << _pruningScoreThreshold << "|" << pruningScore << "}\"]\n";
}

void BabTree::register_infeasible(int Id) {
  if (_output_file == nullptr)
    return;
  (*_output_file) << "  " << Id << "[color=red,label=\"" << Id << "|{i|" << _iter << "}\"]\n";
}

void BabTree::register_branching(int Id, double pruningScore, const std::vector<std::pair<unsigned int, double>> & branchVars, const std::vector<unsigned int> & children) {
  if (_output_file == nullptr)
    return;
  (*_output_file) << "  " << Id << "[color=green,label=\"" << Id << "|{{b|" << _iter << "}| ";
  for (int i = 0; i < branchVars.size(); ++i) {
    (*_output_file) << ' ' << branchVars[i].first << " @ " << branchVars[i].second;
    if (i < branchVars.size() - 1)
      (*_output_file) << ",";
  }
  (*_output_file) << "|"
                  << _pruningScoreThreshold << "|" << pruningScore << "}\"]\n";
  (*_output_file) << "  " << Id << " -> {";
  if (children.size() > 0) {
    (*_output_file) << children[0];
  }
  for(unsigned i = 1; i < children.size(); i++) {
    (*_output_file) << ", " << children[i];
  }
  (*_output_file) << "}\n";
}


/************************

//Outside of BabTree

*************************/


///////////////////////////////////////////////////////////////////////////////////////
//Returns the node with the highest priority
std::vector<BabNodeWithInfo>::const_iterator
babBase::select_node_highest_priority(const std::vector<BabNodeWithInfo>& nodeVectorIN)
{
    return nodeVectorIN.begin();
};


///////////////////////////////////////////////////////////////////////////////////////
//Returns the node added most recently to the tree
std::vector<BabNodeWithInfo>::const_iterator
babBase::select_node_depthfirst(const std::vector<BabNodeWithInfo>& nodeVectorIN)
{

    //compare based on ID
    const auto compareForId = [](BabNodeWithInfo a, BabNodeWithInfo b) { return a.get_ID() < b.get_ID(); };
    //get iterator on node with largest ID
    auto selectedNodeIterator = std::max_element(nodeVectorIN.begin(), nodeVectorIN.end(), compareForId);
    return selectedNodeIterator;
}


///////////////////////////////////////////////////////////////////////////////////////
//Returns the node added least recently to the tree
std::vector<BabNodeWithInfo>::const_iterator
babBase::select_node_breadthfirst(const std::vector<BabNodeWithInfo>& nodeVectorIN)
{

    // compare based on ID
    const auto compareForId = [](BabNodeWithInfo a, BabNodeWithInfo b) { return a.get_ID() < b.get_ID(); };
    // get iterator on node with lowest ID
    auto selectedNodeIterator = std::min_element(nodeVectorIN.begin(), nodeVectorIN.end(), compareForId);
    //create copy of node to return
    return selectedNodeIterator;
}

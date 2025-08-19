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

#pragma once

#include "babException.h"
#include "babNode.h"
#include "babUtils.h"

#include <algorithm>
#include <cassert>
#include <fstream>
#include <limits>
#include <memory>
#include <unordered_map>
#include <utility>


namespace babBase {


/**
 * @struct BranchingHistoryInfo
 * @brief Struct for collecting all information that must be saved about a node, so that after it is retrieved from the tree and processed, pseudocosts can be calculated.
 */
struct BranchingHistoryInfo {
    /**
     * @enum BranchStatus
     * @brief Enum for distinguishing a branching status
     */
    enum class BranchStatus {
        wasBranchedUp = 1,
        wasBranchedDown,
        wasNotBranched    // this last case happens e.g. for fixed nodes that are only readded to the tree
    } branchStatus;       /*!< Object storing the branch status*/

    int branchVar = -1; /*!<  The variable that was branched on in the parent node*/

    double relaxationSolutionPointForBranchingVariable; /*!< The point where the solution of the relaxation was found in that variable*/
    double parentLowerBound;                            /*!< The lower bound of the parent node in that variable*/
    double parentUpperBound;                            /*!< The upper bound of the parent node in that variable*/
};
/**
 * @class BabNodeWithInfo
 * @brief This class represents an node in the B&B-Tree with additional information attached
 *  that is used in selecting nodes or branching variables.
 *
 *  Currently additional information over the BabNode class are the node selection score, that can be
 *  used to order the selection of the nodes from the B&B-Tree and the information which variable was branched
 *  when the node was created. Additionally it is saved whether the branching was up or down.
 *  The last two pieces of information are used to attribute changes to branching decisions. (e.g. in register_node_change in Brancher)
 *  Currently this class is only used internally in the BabTree class and when communicating with the Brancher class.
 *  Efficient way to convert to BabNode are provided.
 */
class BabNodeWithInfo {

  public:
    /**
     * @brief Constructor
     *
     * @param[in] nodeIn is a normal BabNode to be copied
     * @param[in] selScoreIn is the selection score to be used for this bab node
     */
    BabNodeWithInfo(const BabNode nodeIn, double selScoreIn):
        node(nodeIn), _nodeSelectionScore(selScoreIn) {}

    BabNode node; /*!< Not without info*/

    /**
     * @brief Conversion Operator only callable from l-values
     */
    operator BabNode const &() const& { return node; }

    /**
     * @brief Conversion Operator only callable from r-values
     */
    operator BabNode&&() && { return std::move(node); }    //note the ref-qualifiers

    /**
     * @brief Returns the node selection score of the node
     */
    double get_node_selection_score() const { return _nodeSelectionScore; }

    /**
     * @brief Sets the node selection score of the node
     */
    void set_node_selection_score(double newScore) { _nodeSelectionScore = newScore; }

    /**
     * @brief Returns the pruning score of the node
     */
    double get_pruning_score() const { return node.get_pruning_score(); }

    /**
     * @brief Returns the ID of the node
     */
    unsigned get_ID() const { return node.get_ID(); };

    /**
     * @brief Object storing the branching history
     *
     *  Currently no getter and setter for these, as a nontrivial implementation seems
     *  unlikely unless it changed the returned types
     */
    BranchingHistoryInfo branchingInfo;

  private:
    double _nodeSelectionScore; /*!<  The selection score assigned to this node can be used to decide which node to process next*/
};

/**
 * @class FathomObserver
 * @brief Interface for classes that want to be notified when a node is fathomed. 
 */
struct FathomObserver {
    FathomObserver()                                                 = default;
    virtual ~FathomObserver()                                        = default;
    virtual void observe_fathoming(const BabNode& n) = 0;
};

/**
 * @class BabTree
 * @brief Represents the B&B-Tree, manages the way nodes are saved and retrieved and pruned.
 *
 *  The BabTree class is meant to be used to abstract the storage and node selection implementation.
 *  It makes sure that nodes are returned according to the node selection strategy. The default returns
 *  the node with the highest node selection score.
 *  Another invariant is that nodes whose pruning score exceeds the set pruning score threshold are never keept inside the tree.
 *  A added node that violates that invariant is immediately discarded and nodes already in the tree will be deleted when the pruning
 *  score threshold is lowered below there pruning score.
 *  The BabTree class is also in charge of giving out valid IDs as to keep them unique. IDs of Nodes added to the tree
 *  should therefore be retrieved from the tree.
 */
class BabTree {
  public:
    /**
     * @brief Default constructor for BabTree, threshold set to INF
     */
    BabTree(const std::string& dotfile=std::string());
    // Virtual Destructor for the case of inheritance.
    virtual ~BabTree(){
      if (_output_file) { // If an output file was created in the constructor, close it.
        (*_output_file) << "}\n";
        _output_file->close();
        delete _output_file;
        }
    };
    // Because of the previous definition, the compiler will not autogenarate the other constructors. So we tell it to:
    BabTree(const BabTree&)       = default;       /*!< Default copy constructor*/
    BabTree& operator=(BabTree&)  = default;  /*!< Default assignment*/
    BabTree(BabTree&&)            = default;  /*!< Default r-value constructor*/
    BabTree& operator=(BabTree&&) = default; /*!< Default r-value assignment*/

    /**
     * @brief Returns the number of nodes left in the tree. The private member _nodesLeft is used instead of nodeVector.size() so that places which change the
     * number of nodes in the tree are easier to search in case this needs to be logged at a later date.
     */
    size_t get_nodes_left() const
    {
        assert(_nodesLeft == _nodeVector.size());
        return _nodesLeft;
    };

    /**
     * @brief Returns a valid Id for the next node.
     * @return  Returns an Id different from all previous returned.
     * @note  Not ready for parallel use
     */
    unsigned get_valid_id() { return ++_Id; };    //increment should be declared atomic for parallel use!

    /**
     * @brief Add node to the list of nodes to process.
     */
    void add_node(BabNodeWithInfo node);

#ifdef BABBASE_HAVE_GROWING_DATASETS
    /**
     * @brief Add node to the list of nodes to process without checking pruning score.
     */
    void add_node_anyway(BabNodeWithInfo node);

    /**
     * @brief Replace nodes with largest pruning scores by nodes which can be pruned based on a smaller pruning score in node vector for postprocessing (heuristic B&B algorithm with growing datasets)
     *
     * @param[in] newThreshold the new threshold for pruning
     *
     */
    void update_nodes_for_postprocessing(const double newThreshold);

    /**
     * @brief Function for sorting nodesPostprocessing w.r.t. their pruning score (smallest first)
     */
    void sort_nodes_for_postprocessing();

    /**
     * @brief Getter function for next node from nodesPostprocessing (heuristic B&B algorithm with growing datasets)
     *
     * @param[in] idxNextNode is the index of the next node to be processed
     * @return Returns the node to be processed next in postprocessing
     *
     */
    BabNode get_next_node_for_postprocessing(const unsigned int idxNextNode) { return _nodesPostprocessing[idxNextNode]; };

    /**
     * @brief Function for getting the number of nodes tracked for postprocessing (heuristic B&B algorithm with growing datasets)
     *
     */
    size_t get_nodes_tracked_for_postprocessing() { return _nodesPostprocessing.size(); };
#endif // BABBASE_HAVE_GROWING_DATASETS

    /**
     * @brief Return the node according to the node selection strategy and removes it from the tree
     * @pre Tree is not empty. Can be checked  by get_nodes_left()!=0.
     * @note No check of the precondition is guaranteed. Violating it results in undefined behavior.
     */
    BabNodeWithInfo pop_next_node();

    /**
     * @brief Return the lowest pruning score. Returns infinity if tree is empty.
     */
    double get_lowest_pruning_score() const;

    /**
     * @brief Query the largest gap between the pruning threshold and the the pruning scores of the nodes. Returns -infinity if tree is empty.
     * _pruningScoreThreshold-lowest pruning score of all nodes left in the tree. If pruningScore = nodeSelectionScore, this could be done much more efficently.
     *
     */
    double get_pruning_score_gap() const;

    /**
     * @brief Update the pruning score threshold, e.g. after a new incumbent has been found, also fathom now fathomable nodes in tree
     * @return The lowest pruning score of all pruned nodes
     */
    double set_pruning_score_threshold(const double newThreshold);

    /**
     * @brief Query the the pruning score threshold
     */
    double get_pruning_score_threshold() const { return _pruningScoreThreshold; }

    /**
     * @brief Enables pruning of nodes even when they have pruning scores slightly below the threshold.
     *
     *        Takes only effect at next call to set_pruning_score_threshold or when nodes are added
     * @param[in] relTol relativeTolerance
     * @param[in] absTol absoluteTolerance (relative to pruningScoreThreshold)
     */
    void enable_pruning_with_rel_and_abs_tolerance(const double relTol, const double absTol)
    {
        _relPruningTol = relTol;
        _absPruningTol = absTol;
    };

    /**
     * @brief Allows to set the node selection strategy. Default is to return the node with largest node selection score.
     *
     * This should be used to set other strategies when the goal is to change the strategy during the algorithm.
     * For a permanent strategy, it is much more efficient to give the nodes a corresponding node selection priority.
     */
    void set_node_selection_strategy(enums::NS nodeSelectionStrategyType);

    void register_node_status(const BabNode & n, const enums::NodeStatus s);
    void register_open(int Id);
    void register_dominated(int Id, double pruningScore);
    void register_infeasible(int Id);
    void register_branching(int Id, double pruningScore, const std::vector<std::pair<unsigned int, double>> & branchVars, const std::vector<unsigned int> & children);
    void attach_fathom_observer(std::shared_ptr<FathomObserver> observer);
    void inform_about_fathoming(const BabNode& n);

    std::unordered_map<int, BabNode> _sibling_map; /*!< Map of sibling nodes */

  private:
    /**
     * @brief Removes a node from the tree
     */
    void delete_element(std::vector<BabNodeWithInfo>::iterator targetNodeIt);

    /**
     * @brief Removes all nodes from the tree having a pruning score greater than  (or within the tolerances of) pruning threshold
     * @param[in] newThreshold the new threshold to enforce
     * @param[in] relTol Relative tolerance to the new threshold. Describes by which fraction pruning score can be lower than the new threshold and still lead to fathoming
     * @param[in] absTol Absolute value by which pruning score can be lower than the new threshold and still lead to fathoming
     * @return return the lowest pruning score that still lead to fathoming
     */
    double _fathom_nodes_exceeding_pruning_threshold(const double newThreshold, const double relTol, const double absTol);

    std::vector<std::shared_ptr<FathomObserver>> _fathomObservers;

    double _pruningScoreThreshold; /*!< Represents the lowest known upper bound. Every node with a pruning score above this treshold will be pruned. */

    double _relPruningTol = 0.0; /*!< Relative tolerance applied to the pruning process, nodes with pruning score > PT - |PT|* _relativePruningTol will be also pruned (PT= _pruningScoreThreshhold). */
    double _absPruningTol = 0.0; /*!< Absolute tolerance applied to the pruning process, nodes with pruning score > PT - _absPruningTol will be also pruned. */

    size_t _nodesLeft; /*!< Number of nodes left in the tree */
    unsigned _Id;      /*!< Node id */
    
    std::ofstream * _output_file;
    int _iter;

    // Function has to accept a vector of BabNodes and return a const_iterator to the selected node. No assumption can be made about the ordering of the passed vector, except that the .front() entry is the one with the largest nodeSelectionScore
    std::function<std::vector<BabNodeWithInfo>::const_iterator(const std::vector<BabNodeWithInfo>& nodeVectorIN)> _select_node; /*!< Saved function that is used to select the next node to process. */
    std::vector<BabNodeWithInfo> _nodeVector;                                                                                   /*!<  Internal storage of the nodes, currently maintained as a heap of node selection score. The node with the highest nodeSelectionScore will be ensured to be at front of _nodeVector*/

#ifdef BABBASE_HAVE_GROWING_DATASETS
    unsigned _nNodesMaxPostprocessing = 100;   /*!< hard-coding maximum number of nodes saved for post-processing (only relevant for heuristic B&B algorithm with growing datasets) */
    std::vector<BabNode> _nodesPostprocessing; /*!< pruned nodes with lowest pruning score saved for post-processing (only relevant for heuristic B&B algorithm with growing datasets) */
#endif // BABBASE_HAVE_GROWING_DATASETS
};


/** @brief Returns the node with the highest priority*/
std::vector<BabNodeWithInfo>::const_iterator select_node_highest_priority(const std::vector<BabNodeWithInfo>& nodeVectorIN);

/** @brief Returns the node added least recently to the tree */
std::vector<BabNodeWithInfo>::const_iterator select_node_breadthfirst(const std::vector<BabNodeWithInfo>& nodeVectorIN);

/** @brief Returns the node added most recently to the tree */
std::vector<BabNodeWithInfo>::const_iterator select_node_depthfirst(const std::vector<BabNodeWithInfo>& nodeVectorIN);

/**
 * @struct NodePriorityComparator
 * @brief Functor for comparing node priorities.
 *
 * The default is maxHeap, we will keep this convention. The node with the highest nodeSelectionScore will be ensured to be at top of _nodeVector
 * Returns true if priority of a < b
 */
struct NodePriorityComparator {

    /**
     * @brief () operator for comparing
     *
     * @param[in] a is the left object
     * @param[in] b is the right object
     * @return true if a is lesser than b
     */
    bool operator()(const BabNodeWithInfo& a, const BabNodeWithInfo& b) const
    {
        if (a.get_node_selection_score() == b.get_node_selection_score())
            return a.get_ID() > b.get_ID();
        return a.get_node_selection_score() < b.get_node_selection_score();
    };
};


/**
 * @struct PruningScoreComparator
 * @brief Functor for comparing pruning scores.
 *
 * The default is maxHeap, we will keep this convention. The node with the highest pruning score will be ensured to be at top of _nodeVector
 * Returns true if priority of a < b
 */
struct PruningScoreComparator {

    /**
     * @brief () opeartor for comparing
     *
     * @param[in] a is the left object
     * @param[in] b is the right object
     * @return true if a is lesser than b
     */
    bool operator()(const BabNodeWithInfo& a, const BabNodeWithInfo& b) const
    {
        if (a.get_pruning_score() == b.get_pruning_score())
            return a.get_ID() > b.get_ID();
        return a.get_pruning_score() < b.get_pruning_score();
    };
};

}    //end namespace babBase
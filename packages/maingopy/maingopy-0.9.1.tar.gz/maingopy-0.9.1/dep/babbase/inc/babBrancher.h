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
#include "babOptVar.h"
#include "babTree.h"
#include "babUtils.h"

#include <functional>
#include <array>

// Forward declaration of LbpDualInfo
namespace maingo {
  namespace lbp {
    struct LbpDualInfo;
  }
}


namespace babBase {


/**
 * @class Brancher
 * @brief This class contains the logic for branching on nodes in the B&B-Tree and selecting nodes to be processed.
 *
 * The Brancher class is meant to be used to manage the nodes of the branch and bound tree.
 * Internally nodes are associated with two  properties, their pruning score and their selection score.
 * The pruning score usually represents the lower bound (minimization) and is used to exclude nodes from the tree.
 * No nodes are kept in the tree with a pruning score exceeding pruning_score_threshold (and possibly also below pruning_score_threshold by no more than the relative and absolute tolerances).
 * The selection score is used to decide the next node to be processed. With default settings, the node with the HIGHEST selection score is selected.
 * How selection scores are calculated can be customized with set_node_selection_score_function. By default the node with the smallest pruning score has the highest selection score.
 * For efficiency depth first search or breadth first search can be selected by using set_node_selection_strategy in which case selection scores are ignored.
 *
 * The next node to process can be extracted by calling get_next_node().
 * After the node is processed, the user is expected to call register_node_change() with the processed node, which
 * will allow collecting information for certain branching heuristics.
 * To branch on a node, this node is passed to branch_on_node() which normaly will add two new children to the B&B-Tree.
 * Currently, the branching decision is dependant on the current incumbent point. The brancher can be informed about a new incumbent point with set_new_incumbent_point().
 * The brancher also needs to be informed of new pruning score threshold which might represent upper bounds by calling decrease_pruning_score_threshold_to.
 */
class Brancher {

  public:
    /**
     * @brief Constructor
     */
    Brancher(const std::vector<OptimizationVariable>& variables, const std::string& dotfile=std::string());
    // Virtual Destructor for the case of inheritance. However, the compiler now will not autogenarate the other constructors. So we tell it to:
    virtual ~Brancher()       = default;
    Brancher(const Brancher&) = default;       /*!< Default copy constructor*/
    Brancher& operator=(Brancher&) = default;  /*!< Default assignment*/
    Brancher(Brancher&&)           = default;  /*!< Default r-value copy*/
    Brancher& operator=(Brancher&&) = default; /*!< Default r-value assignment*/

    /**
     * @brief Setup the use of _two_stage_branching.
     * 
     * @param[in] Nx Number of first-stage variables.
     * @param[in] Ny Number of second-stage variables.
     * @param[in] w Vector of weights for the second-stage variables.
     * @param[in] fathomObserver Pointer to the lower bounding solver or null.
     * @param[in] alpha Strong branching score threshold.
     * @param[in] k_max Base 2 log of the maximum number of nodes generated during multi section branching.
     */
    void setup_two_stage_branching(
      unsigned Nx, unsigned Ny, const std::vector<double>& w,
      const std::shared_ptr<babBase::FathomObserver>& fathomObserver,
      double alpha,
      unsigned int k_max
    )
    {
        _Nx                 = Nx;
        _Ny                 = Ny;
        _w                  = w;
        _branching_function = &Brancher::_two_stage_branching;
        _internalBranchAndBoundTree.attach_fathom_observer(fathomObserver);
        _alpha = alpha;
        _k_max = k_max;
    }

    /**
     * @brief Select a strategy for choosing a variable/dimension to branch on.
     * Currently selecting the dimension with largest absolute or relative diameter is implemented
     */
    void set_branching_dimension_selection_strategy(const enums::BV branchingVarStratSelection);

    /**
     * @brief Select the node selection strategy. Default is to select the node with highest node selection score.
     *
     *  It is easier but less efficient to select the other two provided options depth-first and breadth first via this
     *  function instead of selecting a different node selection score function with set_node_selection_score_function.
     *  However, this function may also be called during the search.
     */
    void set_node_selection_strategy(const enums::NS nodeSelectionStratType);

    /**
     * @brief Change the scoring function for the selection score of nodes.
     *
     * Currently only new nodes are scored with the new scoring function, meaning that this function is not suitable to change between
     * different node selection strategies (e.g. lowest-pruning score to depth-first) during the search. For this us set_node_selection_strategy.
     * @param newNodeScoreFunction Functor or function pointer or reference to function describing how selection scores should be calculated
     */
    void set_node_selection_score_function(std::function<double(const BabNode&, const std::vector<OptimizationVariable>&)> newNodeScoreFunction);

    /**
     * @brief Registers the changes made to a node during processing to extract information for branching heuristics.
     *
     * Internally keeps track of all nodes given out for processing for which no change has been registered.
     * This enables nodes to be processed in parallel or out of order.
     * If the Id is invalid (not found in the list of nodes given out for processing), an BranchAndBoundBaseExeception will be thrown.
     * If the Id is found on the list, it will be removed from that list after the function call.
     * @param Id is the ID of the node that was received with get_next_node()
     * @param nodeAfterProcessing is the node after processing. The ID member of this node is ignored.
     * @throws A BranchAndBoundBaseExeception if passed Id is invalid
     */
    void register_node_change(const int Id, const BabNode& nodeAfterProcessing);

    void register_node_status(const BabNode & n, const babBase::enums::NodeStatus s);

    /**
     * @brief Inserts the root node into the tree.
     * @param rootNode Node to be placed at the root. IDs are handled by BabTree and thus the ID member of rootNode will be replaced.
     * @pre   The tree is empty. Can be checked by get_nodes_in_tree()==0.
     */
    void insert_root_node(const BabNode& rootNode);

    /**
     * @brief Function that branches on a node and (normally) adds two new children to the BranchAndBoundTree.
     *
     * It uses the branching strategy from _select_branching_dimension to decide which variable to branch on.
     * relNodeSizeTol may be specified to not branch on nodes where all dimensions have a smaller size relative to the original bounds.
     * In this case, if all optimization variables are integer, the node is added to the tree unchanged to be processed/ solved a final time,
     *                otherwise the node is discarded.
     *
     * @param[in] parentNode Node to be branched on. Pruning Score is forwarded to children nodes.
     * @param[in] relaxationSolutionPoint  The solution point of the relaxed problem for the parent node.
     * @param[in] relaxationSolutionObjValue The objective function vaule corresponding to relaxationSolutionPoint.
     * @param[in] relNodeSizeTol The relative tolerance for bound differences (relative to the original bounds).
     * @return pair<isFixed, canBeConsideredFixed>
     * isFixed is true if all variables are fixed which should only happen for pure integer problems. In this case parentNode is simply added to the tree.
     * canBeConsideredFixed is true if all variables are fixed up to the relNodeSizeTol.  In this case parentNode is discarded.
     * @post Either both returned bools (isFixed and canBeConsideredFixed) are false, or two new nodes are added to the tree with the same pruning score as parentNode.
     */
    std::pair<bool /*isFixed*/, bool /*canBeConsideredFixed*/> branch_on_node(BabNode& parentNode, const std::vector<double>& relaxationSolutionPoint, double relaxationSolutionObjValue, double relNodeSizeTol = 0.0);

	  /**
	   * @brief Function that adds a node to the internal tree. This is intended to be used when nodes that were assigned to other managers are moved
	   * among multiple branch and bound trees.
	   */
	  void add_node(const BabNode& newNode) {
	  	// check to see if this is valid for donated nodes
	  	_internalBranchAndBoundTree.add_node(this->_create_node_with_info_from_node(newNode, 0, BranchingHistoryInfo::BranchStatus::wasNotBranched, 0, 0, 0));
	  }

#ifdef BABBASE_HAVE_GROWING_DATASETS
    /**
     * @brief Function for creating one child from parent node and adding it to BaB tree
     *
     * Note: Used in MAiNGO with growing datasets to get a node with the new dataset
     *
     * @param[in] parentNode is the node to be cloned except for index of dataset
     * @param[in] newDataIndex is the index of the dataset used for the new node
     */
    void add_node_with_new_data_index(const BabNode& parentNode, const unsigned int newDataIndex);

    /**
     * @brief Passing newThreshold to respective BabTree function (heuristic B&B algorithm with growing datasets)
     *
     * @param[in] newThreshold is the new threshold for pruning
     *
     */
    void update_nodes_for_postprocessing(const double newThreshold);

    /**
     * @brief Function for calling respective function of BabTree
     */
    void sort_nodes_for_postprocessing() { _internalBranchAndBoundTree.sort_nodes_for_postprocessing(); };

    /**
     * @brief Function for calling respective function of BabTree
     *
     * @param[in] idxNextNode is the index of the next node to be processed
     * @return Returns the node to be processed next in postprocessing
     *
     */
    BabNode get_next_node_for_postprocessing(const unsigned int idxNextNode) { return _internalBranchAndBoundTree.get_next_node_for_postprocessing(idxNextNode); };

    /**
     * @brief Function for calling respective function of BabTree
     *
     * @return Returns the number of nodes tracked for postprocessing (heuristic B&B algorithm with growing datasets)
     *
     */
    size_t get_nodes_tracked_for_postprocessing() { return _internalBranchAndBoundTree.get_nodes_tracked_for_postprocessing(); };
#endif    // BABBASE_HAVE_GROWING_DATASETS

    /**
     * @brief Returns the number of nodes in the tree.
     */
    size_t get_nodes_in_tree() const { return this->_internalBranchAndBoundTree.get_nodes_left(); }

    /**
     * @brief Returns the next BabNode to process according to the node selection strategy and node selection scores.
     * @pre  Tree is not empty. Can be checked with get_nodes_in_tree()>0
     * @throws A BranchAndBoundBaseException if the precondition is not fullfilled.
     */
    BabNode get_next_node();

    /**
     * @brief Returns the lowest pruning score of all nodes in the tree
     */
    double get_lowest_pruning_score() const { return this->_internalBranchAndBoundTree.get_lowest_pruning_score(); };

    /**
     * @brief Returns the difference between lowest pruning score in the tree and the pruning score threshold.
     */
    double get_pruning_score_gap() const { return this->_internalBranchAndBoundTree.get_pruning_score_gap(); }

    /**
     * @brief Decreases the pruning score threshold to the supplied value. Nodes with pruning score exceeding the new threshold are fathomed.
     * @return the lowest pruning score that lead to fathoming
     */
    double decrease_pruning_score_threshold_to(const double newThreshold);

    /**
     * @brief Returns the pruning score threshold
     * @return pruning_score_threshold No nodes with pruning score exceeding this value will be keept in the tree. Often represents lowest known upper bound.
     */
    double get_pruning_score_threshold() const { return _internalBranchAndBoundTree.get_pruning_score_threshold(); }

    /**
     * @brief Enables pruning of nodes even when they have pruning scores slightly below the threshold
     * @param[in] relTol relativeTolerance
     * @param[in] absTol absoluteTolerance (relative to pruningScoreThreshold)
     */
    void enable_pruning_with_rel_and_abs_tolerance(const double relTol, const double absTol) { _internalBranchAndBoundTree.enable_pruning_with_rel_and_abs_tolerance(relTol, absTol); };

    /**
     * @brief Branches once on all variables and does not add the nodes to the tree, but returns them immediately.
     */
    std::vector<BabNode> get_all_nodes_from_strong_branching(const BabNode& parentNode, const std::vector<double>& relaxationSolutionPoint);

    /**
     * @brief Checks if the node has a sibling and if yes fills the sibling array.
     * 
     * @param[in] node The node to check for siblings.
     * @param[out] node The (upper) sibling node of the (lower sibling) node, if the two nodes are siblings.
     * @return true if the node has a sibling, false otherwise.
     */
    bool find_sibling(const BabNode& node, BabNode& sibling);

    /**
     * @brief Get nodes solutions and objective values for feasible, undominated orthants from two processed sibling nodes.
     * 
     * @param[in] parentPruningScore The pruning score of the parent node.
     * @param[in] parentSubproblemBounds The bounds for subproblems of the parent node.
     * @param[in] siblings The sibling array.
     * @param[in] objectiveBounds The bounds of the subproblems.
     * @param[in] subproblemSolutions The solutions of the subproblems.
     * @param[out] _nNodesFathomed The count of fathomed nodes.
     * @param[out] _bestOrthantLbdFathomed The best lower bound of fathomed nodes.
     * @param[in] dominance_test The callback for testing dominance.
     * @param[in] postprocess_orthant The callback for postprocessing orthants.
     * @param[in] relNodeSizeTol The relative node size tolerance.
     */
    void
    multisect_parent_node(
      const double parentPruningScore,
      const std::vector<double>& parentSubproblemBounds,
      const std::array<BabNode, 2>& siblings,
      const std::array<std::vector<double>, 2>& objectiveBounds,
      const std::array<std::vector<std::vector<double>>, 2>& subproblemSolutions,
      const std::array<std::vector<std::vector<double>>, 2>& subproblemLowerBounds,
      const std::array<std::vector<std::vector<double>>, 2>& subproblemUpperBounds,
      unsigned int& _nNodesFathomed,
      double& _bestOrthantLbdFathomed,
      const std::function<bool(unsigned int orthantID, double orthantPruningScore)>& dominance_test,
      const std::function<
        void(
          babBase::BabNode& orthantNode,
          const std::vector<unsigned int>& bits,
          const std::array<std::vector<double>, 2>& objectiveBounds
        )>& postprocess_orthant,
      const double relNodeSizeTol
    );

     /**
     * @brief Helper function to get the bit at a position from the binary representation of a number.
     * 
     * Used for acessing the correct variable and subproblem bounds associated to different orthants during the creation of nodes fom siblings.
     * @param number: the number to get the bit from
     * @param position: the position of the bit to get
     * @return: the bit at the given position
     */
     inline size_t get_bit(const unsigned number, const unsigned position) {
        return number >> position & 1;
    }

  private:
    /**
     * @brief Creates a node with added information.
     *
     *  Added information is the node selection score, the variable last branched on  and if it was branched up or down.
     *  Additionally, what the value of this variable was at the relaxation solution and what bounds the parent node had on that variable.
     *  The node selection score is calculated immediately.
     *  @returns A BabNodeWithInfo with all fields from BabNode copied.
     */
    BabNodeWithInfo _create_node_with_info_from_node(BabNode normalNode, unsigned branchVariable, BranchingHistoryInfo::BranchStatus branchStatus, double variableRelaxationSolutionPoint, double parentLowerBound, double parentUpperBound) const;


    /**
     * @brief calculates the branching point. Currently 0.5*(lb + ub);
     */
    double _calculate_branching_point(double lowerBound, double upperBound, double relaxationValue) const;

    /**
     * @brief Partitions the parentNode into two child nodes.
     * @param[in] parentNode Node to be branched on.
     * @param[in] branchVar Variable to branch on.
     * @param[in] branchVarValue Value to branch on.
     * @param[in] __unused Unused, just to comply with signature of _branching_function.
     */
    void _default_branching(const BabNode& parentNode,
                            unsigned int branchVar,
                            double branchVarValue,
                            const std::vector<double>& __unused={});

    /** Partitions the parentNode in two or more child nodes.
     * 
     * If branchVar is a first-stage variable, default branching is used.
     * If branchVar is a second-stage variable, the corresponding second-stage variable from each scenario is also selected for branching.
     * The Ns partitions of the parentNode domain result in a total of 2 ** Ns new nodes.
     * Bounds for all of these nodes can be obtained by processing only two of them, as the processing is done via the solution of reoccurring subproblems.
     * Contrary to the default branching, the created nodes are immediately processed and those that warrant further seach are branched again, this time on the first-stage variables.
     * This results into up to 2 ** (Ns + 1) new nodes being added to the branch and bound tree.
     * 
     * @param[in] parentNode Node to be branched on.
     * @param[in] branchVar Variable to branch on.
     * @param[in] branchVarValue Value to branch on.
     * @param[in] relaxationSolutionPoint The relaxation solution point.
     */ 
    void _two_stage_branching(const BabNode& parentNode,
                              unsigned int branchVar,
                              double branchVarValue,
                              const std::vector<double>& relaxationSolutionPoint);

    /**
     * @brief Creation of the two sibling nodes for second-stage branching.
     * 
     * Each sibling node contains bounding information corresponding to either branching down or up on a particular second-stage variable from each scenario.
     * The first and second sibling node thus respectively represent the lower and upper orthant from the partition induced by branching the parent domain on the second-stage variables in branchVars.
     * Considered individually, the two siblings thus cover only 2 out of 2 ^ Ns orthants making up the parent domain.
     * However, the two groups of Ns subproblems that are solved when obtaining bounds on each of the two sibling nodes are complementary in the sense that any combination made by selecting a subproblem from one of the two groups for each scenario, gives the required information to calculate the bounds on one orthant of the partitioned parent domain.
     * In other words, the combined information that can be obtained from the two sibling nodes covers all 2 ^ Ns orthants.
     * 
     * @param[in] parentNode The parent node.
     * @param[in] branchVars The second-stage variables to be branched on.
     * @param[in] branchVarValues The values of the branchVars in the last solution of the relaxation.
     */
    void _setup_siblings(const BabNode & parentNode, const std::vector<unsigned> & branchVars, const std::vector<double> & branchVarValues);

    /**
     * @brief Function for selecting the variable to branch on and identifying a its value in the last solution.
     * 
     * The selected branching variable is returned in `branchVar` and its value in the last solution in `branchVarValue`.
     * If available, the branchVarValue is the respective entry in the relaxationSolutionPoint; otherwise it is the midpoint of the bounds of the parent node.
     * 
     * @param[in] parentNode is the node thas should be branched on
     * @param[in] relaxationSolutionPoint is the vector of the solution point for the relaxed problem in the parentNode node
     * @param[in] relaxationSolutionObjValue is the objective function value corresponding to relaxationSolutionPoint
     * @param[out] branchVar is the index of the variable to branch on
     * @param[out] branchVarValue is the representative value for the variable to branch on (not necessarily the branching point!)
     */
    void _set_branching_variable_and_value(const BabNode& parentNode,
                                           const std::vector<double>& relaxationSolutionPoint,
                                           double relaxationSolutionObjValue,
                                           unsigned& branchVar,
                                           double& branchVarValue);
    
    /**
     * @brief Identify the value of branchVar in the last solution.
     * 
     * If available, the value is the respective entry in the relaxationSolutionPoint;
     * otherwise it is the midpoint of the bounds of the parent node.
     * 
     * @param[in] parentNode Node to be branched on.
     * @param[in] relaxationSolutionPoint  The solution point of the relaxed problem for the parent node.
     * @param[in] branchVar The variable to branch on.
     */
     double _get_relaxation_solution_value(const BabNode & parentNode,
                                                     const std::vector<double> & relaxationSolutionPoint,
                                                     unsigned & branchVar);
     
    /**
     * @brief Identify the values for each variable in branchVars from the last solution.
     * 
     * If available, the values are the respective entries in the relaxationSolutionPoint;
     * otherwise they are the midpoints of the respective bounds from the parent node.
     * 
     * @param[in] parentNode Node to be branched on.
     * @param[in] relaxationSolutionPoint  The solution point of the relaxed problem for the parent node.
     * @param[in] branchVars The variables to branch on.
     */
    std::vector<double> _get_relaxation_solution_values(const BabNode & parentNode,
                                                        const std::vector<double> & relaxationSolutionPoint,
                                                        const std::vector<unsigned> & branchVars);

    /**
     *  @brief Helper function for creating nodes from parent node once branch variable has been decided
     */
    std::pair<BabNodeWithInfo, BabNodeWithInfo> _create_children(unsigned branchVar, const BabNode& parentNode, double branchVariableRelaxSolutionPoint);

    /**
     * @brief Function for selecting the variable to branch on by choosing the one with the largest pseudocost
     * @param[in] parentNode is the node thas should be branched on.
     * @param[in] relaxationSolutionPoint is the vector of the solution point for the relaxed problem in the parentNode node
     * @param[in] relaxationSolutionObjValue is the objective function value corresponding to relaxationSolutionPoint
     * @param[in] globalOptimizationVars is the vector of original optimization variables
     * @return branchVar is the index of the variable to branch on
     */
    unsigned _select_branching_dimension_pseudo_costs(const BabNode& parentNode, const std::vector<double>& relaxationSolutionPoint, const double relaxationSolutionObjValue, const std::vector<OptimizationVariable>& globalOptimizationVars) const;


    std::function<double(const BabNode&, const std::vector<OptimizationVariable>&)> _node_score_calculating_function;                                                                                                                       /*!< Saved function to calculate the node selection score of a node */
    std::function<unsigned(const BabNode& parentNode, const std::vector<double>& relaxationSolutionPoint, double relaxationSolutionObjValue, const std::vector<OptimizationVariable>& globalOptimizationVars)> _select_branching_dimension; /*!< Function for selecting the branching variable */
    typedef void (Brancher::*Branching_function)(const BabNode& parentNode, unsigned int branchingVar, double branchVarValue, const std::vector<double>& relaxationSolutionPoint);                                     /*!< Type definition for branching functions*/
    Branching_function _branching_function;                                                                                                                                                                                                 /*!< Pointer to the branching function*/
    BabTree _internalBranchAndBoundTree;                                                                                                                                                                                                    /*!< BranchAndBoundTree managing the nodes and their sorting*/
    std::vector<OptimizationVariable> _globalOptimizationVariables;                                                                                                                                                                         /*!< Saves the global/original bounds and types of variables and their global branching score components*/
    std::vector<double> _pseudocosts_up;                                                                                                                                                                                                    /*!< The pseudocosts for branching up on each of the variables*/
    std::vector<double> _pseudocosts_down;                                                                                                                                                                                                  /*!< The pseudocosts for branching down on each of the variables*/
    std::vector<int> _number_of_trials_up;                                                                                                                                                                                                  /*!< The number of times the pseudo cost for branching up has been updated. Used to incrementally calculate the average*/
    std::vector<int> _number_of_trials_down;                                                                                                                                                                                                /*!< The number of times the pseudo cost for branching down has been updated. Used to incrementally calculate the average*/
    std::vector<std::tuple<unsigned /* id*/, double /*parentPruningScore*/, BranchingHistoryInfo>> _nodesWaitingForResponse;                                                                                                                /*!< Nodes that have been handed to the client code but for which no change has been registered yet*/
    unsigned _Nx;                                                                                                                                                                                                                           /*!< Number of first-stage variables*/
    unsigned _Ny;                                                                                                                                                                                                                           /*!< Number of second-stage variables*/
    std::vector<double> _w;                                                                                                                                                                                                                 /*!< Scenario weights*/
    double _alpha;                                                                                                                                                                                                                          /*!< Strong branching score threshold for two-stage branching*/
    unsigned int _k_max;                                                                                                                                                                                                                    /*!< Base 2 log of the maximum number of nodes generated during multi section branching*/
};

/**
 * @brief Function for selecting the variable to branch on by choosing the one with the largest diameter
 * @param[in] parentNode is the node thas should be branched on.
 * @param[in] relaxationSolutionPoint is the vector of the solution point for the relaxed problem in the parentNode node
 * @param[in] relaxationSolutionObjValue is the objective function value corresponding to relaxationSolutionPoint
 * @param[in] globalOptimizationVars is the vector of original optimization variables
 * @return branchVar is the index of the variable to branch on
 */
unsigned select_branching_dimension_absdiam(const BabNode& parentNode, const std::vector<double>& relaxationSolutionPoint, const double relaxationSolutionObjValue, const std::vector<OptimizationVariable>& globalOptimizationVars);

/**
 * @brief Function for selecting the variable to branch on by choosing the one with the largest diameter relative to the original one
 * @param[in] parentNode is the node thas should be branched on.
 * @param[in] relaxationSolutionPoint is the vector of the solution point for the relaxed problem in the parentNode node
 * @param[in] relaxationSolutionObjValue is the objective function value corresponding to relaxationSolutionPoint
 * @param[in] globalOptimizationVars is the vector of original optimization variables
 * @return branchVar is the index of the variable to branch on
 */
unsigned select_branching_dimension_reldiam(const BabNode& parentNode, const std::vector<double>& relaxationSolutionPoint, const double relaxationSolutionObjValue, const std::vector<OptimizationVariable>& globalOptimizationVars);

/**
 * @brief Helper function for tiebracking in branching (akin to most fractional although this is only as good as random)
 */
double relative_distance_to_closest_bound(double pointValue, double bound1, double bound2, const babBase::OptimizationVariable& variable);

/**
 * @brief Function for BFS or lowPruning Score First (default), possible choice for calculating the node selection score
 */
double low_pruning_score_first(const BabNode& candidate, const std::vector<OptimizationVariable>& globalVars);
/**
 * @brief Function for Breadth-First-Search  possible choice for calculating the node selection score
 */
double low_id_first(const BabNode& candidate, const std::vector<OptimizationVariable>& globalVars);

/**
 * @brief Function for DFS, possible choice for calculating the node selection score
 */
double high_id_first(const BabNode& candidate, const std::vector<OptimizationVariable>& globalVars);
/**
 * @brief  Calculate the multiplier for calculation of pseudocosts
 */
std::pair<double, double> calculate_pseudocost_multipliers_minus_and_plus(enums::VT varType, double lowerBound, double upperBound, double branchingPoint, double relaxationSolutionPoint);


}    //end namespace babBase

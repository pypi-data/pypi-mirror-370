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

#include "babOptVar.h"
#include "babUtils.h"

#include <limits>
#include <string>
#include <set>


namespace babBase {


/**
 * @class BabNode
 * @brief Class representing a node in the Branch-and-Bound tree
 *
 * A BabNode is characterized by a vector containing the configuration for optimization variables (bounds etc.) in this node, as well as an ID (both private members).
 * It also contains a pruning score and a flag that indicates whether it holds the incumbent.
 */
class BabNode {

  public:
    /**
     * @brief Constructor for initializing a BabNode using separate vectors containing the bounds.
     *
     * @param[in] pruningScoreIn is the score of the node with respect to its pruning rule, a pruning score higher than a certain threshold will lead to pruning of the node
     * @param[in] lbdsIn is a vector containing the lower bounds on the optimization variables for this node
     * @param[in] ubdsIn is a vector containing the upper bounds on the optimization variables for this node
     * @param[in] indexDatasetIn is the ID associated with the dataset of this node
     * @param[in] pidIn is the ID of the parent of this node
     * @param[in] idIn is the ID to be associated with this node
     * @param[in] depthIn is the depth of the node in the tree
     * @param[in] augmentData tells whether dataset of this node is augmented in current iteration (see growing datasets)
     */
    BabNode(
        double pruningScoreIn,
        const std::vector<double>& lbdsIn,
        const std::vector<double>& ubdsIn,
        const unsigned int indexDatasetIn,
        const int pidIn,
        const int idIn,
        const unsigned depthIn,
        const bool augmentData
    ):
        _pruningScore(pruningScoreIn),
        _lowerBounds(lbdsIn),
        _upperBounds(ubdsIn),
        _indexDataset(indexDatasetIn),
        _parentidNumber(pidIn),
        _idNumber(idIn),
        _depth(depthIn),
        _augmentData(augmentData) {}

    /**
     * @brief Constructor for initializing the root node using a vector of OptimizationVariable (each of which contains a Bounds object).
     *
     * @param[in] pruningScoreIn is the score of the node with respect to its pruning rule, a pruning score higher than a certain threshold will lead to pruning of the node
     * @param[in] variablesIn is a vector containing the optimization variables
     */
    BabNode(
        double pruningScoreIn,
        const std::vector<OptimizationVariable>& variablesIn
    ):
        _pruningScore(pruningScoreIn),
        _indexDataset(0),
        _parentidNumber(-1),
        _idNumber(0),
        _depth(0),
        _augmentData(false)
    {
        size_t nVar = variablesIn.size();
        _lowerBounds.resize(nVar);
        _upperBounds.resize(nVar);
        for (size_t iVar = 0; iVar < nVar; iVar++) {
            _lowerBounds[iVar] = variablesIn[iVar].get_lower_bound();
            _upperBounds[iVar] = variablesIn[iVar].get_upper_bound();
        }
    }

    /**
     * @brief Constructor for initializing a BabNode using a given node and vectors containing the bounds.
     *
     * @param[in] babNodeIn is the node upon which the new node is based
     * @param[in] lbdsIn is a vector containing the lower bounds on the optimization variables for this node
     * @param[in] ubdsIn is a vector containing the upper bounds on the optimization variables for this node
     */
    BabNode(const BabNode& babNodeIn, const std::vector<double>& lbdsIn, const std::vector<double>& ubdsIn):
        _pruningScore(babNodeIn.get_pruning_score()), _lowerBounds(lbdsIn), _upperBounds(ubdsIn), _indexDataset(babNodeIn.get_index_dataset()), _parentidNumber(babNodeIn.get_parent_ID()), _idNumber(babNodeIn.get_ID()), _depth(babNodeIn.get_depth()), _augmentData(babNodeIn.get_augment_data()) {}


    /**
     * @brief Default constructor
     */
    BabNode():
        _pruningScore(std::numeric_limits<double>::infinity()), _depth(0), _indexDataset(0), _parentidNumber(-1), _idNumber(0), _augmentData(false) {}

    /**
     * @brief Function for querying the pruning score within this node
     */
    double get_pruning_score() const { return _pruningScore; }

    /**
     * @brief Function for setting the pruning score within this node
     */
    void set_pruning_score(double pruningScoreIn) { _pruningScore = pruningScoreIn; }

    /**
     * @brief Function for querying the lower bounds on the optimization variables within this node.
     */
    const std::vector<double> & get_lower_bounds() const { return _lowerBounds; }

    /**
     * @brief Function for querying the upper bounds on the optimization variables within this node.
     */
    const std::vector<double> & get_upper_bounds() const { return _upperBounds; }

    /**
     * @brief Function for querying the lower bounds on the optimization variables within this node.
     */
    const double & get_lower_bound(unsigned int i) const { return _lowerBounds[i]; }

    /**
     * @brief Function for querying the upper bounds on the optimization variables within this node.
     */
    const double & get_upper_bound(unsigned int i) const { return _upperBounds[i]; }

    /**
     * @brief Function for querying the parent node's ID.
     */
    int get_parent_ID() const { return _parentidNumber; };

    /**
     * @brief Function for querying the index of the dataset of this node
     */
    unsigned int get_index_dataset() const { return _indexDataset; }

    /**
     * @brief Function for querying the node ID.
     */
    int get_ID() const { return _idNumber; };

    /**
     * @brief Function for querying the node depth.
     */
    int get_depth() const { return _depth; };
 
    /**
     * @brief Function obtaining information whether dataset of node had been augmented (see growing datasets)
     */
    bool get_augment_data() const { return _augmentData; }

    /**
     * @brief Function for setting the whole upper bound vector
     */
    void set_upper_bound(const std::vector<double> upperBounds) { _upperBounds = upperBounds; }

    /**
     * @brief Function for setting the whole upper bound vector
     */
    void set_upper_bound(const unsigned iVar, const double value) { _upperBounds[iVar] = value; }

    /**
     * @brief Function for setting the whole lower bound vector
     */
    void set_lower_bound(const std::vector<double> lowerBounds) { _lowerBounds = lowerBounds; }

    /**
     * @brief Function for setting the whole lower bound vector
     */
    void set_lower_bound(const unsigned iVar, const double value) { _lowerBounds[iVar] = value; }

#ifdef BABBASE_HAVE_GROWING_DATASETS
    /**
    * @brief Function for setting the index of the dataset of this node
    */
    void set_index_dataset(const unsigned int indexDataset) { _indexDataset = indexDataset; }

    /**
    * @brief Function for setting information whether dataset of node is augmented (see growing datasets)
    */
    void set_augment_data(const bool augmentData) { _augmentData = augmentData; }
#endif // BABBASE_HAVE_GROWING_DATASETS

    /**
     * @brief Overloaded operator for easier output.
     *        Definition of this operator is in bab.cpp.
     */
    friend std::ostream& operator<<(std::ostream& out, const BabNode& node);

  private:
    /**
     * @name Internal variables of a B&B node
     */
    /**@{*/
    std::vector<double> _lowerBounds; /*!< Lower bounds on optimization variables within this node */
    std::vector<double> _upperBounds; /*!< Upper bounds on optimization variables within this node */
    unsigned int _indexDataset;       /*!< Index of dataset considered within this node */
    int _parentidNumber;              /*!< Parents Node ID */
    int _idNumber;                    /*!< Node ID */
    unsigned _depth;                  /*!< Depth of this node in the B&B tree */
    double _pruningScore;             /*!< PruningScore: if PruningScore is higher than a PruningThreshold, the node will be fathomed by and from the BAB-Tree*/
    bool _augmentData;                /*!< Variable telling whether dataset of this node is augmented in current iteration (see growing datasets)*/
    /**@}*/
};

/**
 * @brief operator << overloaded for BabNode for easier output
 *
 * @param[out] out is the outstream to be written to
 * @param[in] node is the B&B node to be printed
 */
inline std::ostream&
operator<<(std::ostream& out, const BabNode& node)
{
    std::string str;
    out << "BabNode id: " << node.get_ID() << ", pruning score: " << node.get_pruning_score() << ", dataset id: " << node.get_index_dataset() << "\n";
    for (unsigned int i = 0; i < node.get_lower_bounds().size(); i++) {
        out << "lb[" << i << "]: " << std::setprecision(16) << node.get_lower_bounds()[i] << " .. " << node.get_upper_bounds()[i] << " :[" << i << "]ub\n";
    }
    return out;
}


namespace enums {
    /**
     * @enum NodeStatus
     * @brief Enum for representing the status of a node.
     */
    enum class NodeStatus {
        OPEN = 0,  /*To be processed*/
        BRANCHED,  /*Branched on (currently unused) */
        DOMINATED, /*Fathomed by value dominance*/
        INFEASIBLE /*Fathomed by infeasibility*/
    };
}

}    // end namespace babBase

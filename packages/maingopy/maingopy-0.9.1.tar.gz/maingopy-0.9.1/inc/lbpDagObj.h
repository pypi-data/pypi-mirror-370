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

#include "constraint.h"
#include "intervalLibrary.h"
#include "settings.h"

#include "babOptVar.h"

#include <memory>
#include <utility>
#include <vector>


namespace maingo {


namespace lbp {


/**
* @struct DagObj
* @brief Struct for storing all needed Directed acyclic Graph objects for the upper bounding solver.
*
* Contains all objects, copies and variables for the usage of the DAG.
* Further information on DAG can be found in ffunc.hpp of MC++.
*
*/
struct DagObj {
    // Internal variables for the DAG
    mc::FFGraph DAG;                   /*!< the actual DAG */
    std::vector<mc::FFVar> vars;       /*!< DAG variables */
    mc::FFSubgraph subgraph;           /*!< subgraph holding the list of operations in the DAG */
    std::vector<mc::FFVar> functions;  /*!< vector of all functions in the DAG */
    std::vector<mc::FFVar> resultVars; /*!< vector holding evaluated FFVar Objects to not lose pointers */
    std::vector<MC> resultRelaxation;  /*!< vector holding resulting McCormick relaxations of possibly not all functions at some linearization point */
    std::vector<MC> McPoint;           /*!< McCormick Point at the reference point given by the linearization heuristic used  */
    std::vector<MC> MCarray;           /*!< dummy vector of MC objects for faster evaluation */
    bool intervals_already_computed;   /*!< auxiliary bool to avoid multiple evaluation when more than one linearization point is computed */

    // Variables for interval constraint propagation
    std::vector<I> intervalArray;       /*!< dummy interval vector for faster evaluation */
    std::vector<I> constraintIntervals; /*!< vector holding the bounding intervals for objective (-1e51, UB), (rel only) ineq constraints (-1e51, 0), (rel only) eq constraints (0, 0) */
    std::vector<I> currentIntervals;    /*!< vector holding the variable intervals */

    // Vectors holding operations of every function in the DAG (not all at once)
    std::vector<std::vector<mc::FFVar>> functionsObj;                /*!< vector holding function(s) for the objective */
    std::vector<std::vector<mc::FFVar>> functionsIneq;               /*!< vector holding functions for the inequalities */
    std::vector<std::vector<mc::FFVar>> functionsEq;                 /*!< vector holding functions for the equalities */
    std::vector<std::vector<mc::FFVar>> functionsIneqRelaxationOnly; /*!< vector holding functions for the relaxation only inequalities */
    std::vector<std::vector<mc::FFVar>> functionsEqRelaxationOnly;   /*!< vector holding functions for the relaxation only equalities */
    std::vector<std::vector<mc::FFVar>> functionsIneqSquash;         /*!< vector holding functions for the squash inequalities */
    std::vector<mc::FFSubgraph> subgraphObj;                         /*!< subgraph holding the list of operations of the objective function(s) */
    std::vector<mc::FFSubgraph> subgraphIneq;                        /*!< subgraph holding the list of operations of the inequalities */
    std::vector<mc::FFSubgraph> subgraphEq;                          /*!< subgraph holding the list of operations of the equalities */
    std::vector<mc::FFSubgraph> subgraphIneqRelaxationOnly;          /*!< subgraph holding the list of operations of the relaxation only inequalities */
    std::vector<mc::FFSubgraph> subgraphEqRelaxationOnly;            /*!< subgraph holding the list of operations of the relaxation only equalities */
    std::vector<mc::FFSubgraph> subgraphIneqSquash;                  /*!< subgraph holding the list of operations of the squash inequalities */

#ifdef HAVE_GROWING_DATASETS
    //Additional variables for MAiNGO with growing datasets
    bool useMse;                                                             /*!< whether to use mean squared error or summed squared error as the objective function */
    unsigned int indexFirstData;                                             /*!< position of the first objective per data in MAiNGO::_DAGfunctions */
    std::shared_ptr<std::vector<unsigned int>> datasets;                     /*!< pointer to a vector containing the size of all available datasets */
    std::shared_ptr<std::set<unsigned int>> datasetResampled;                /*!< pointer to resampled initial dataset */
    std::vector<std::shared_ptr<mc::FFSubgraph>> storedSubgraph;             /*!< vector containing pointers to subgraph of all previously used datasets. Note: position in this vector = index of dataset */
    std::vector<std::shared_ptr<mc::FFSubgraph>> storedSubgraphObj;          /*!< vector containing pointers to subgraphObj of all previously used datasets. Note: position in this vector = index of dataset */
    std::vector<std::vector<mc::FFVar>> storedFunctions;                     /*!< vector containing functions of all previously used datasets. Note: position in this vector = index of dataset */
    std::vector<std::vector<mc::FFVar>> storedFunctionsObj;                  /*!< vector containing functionsObj of all previously used datasets. Note: position in this vector = index of dataset */
    std::vector<std::shared_ptr<mc::FFSubgraph>> storedSubgraphCompl;        /*!< vector containing pointers to subgraph of all previously used complementary datasets. Note: position in this vector = index of corresponding reduced dataset - 1 */
    std::vector<std::shared_ptr<mc::FFSubgraph>> storedSubgraphObjCompl;     /*!< vector containing pointers to subgraphObj of all previously used complementary datasets. Note: position in this vector = index of corresponding reduced dataset - 1 */
    std::vector<std::vector<mc::FFVar>> storedFunctionsCompl;                /*!< vector containing functions of all previously used complementary datasets. Note: position in this vector = index of corresponding reduced dataset - 1 */
    std::vector<std::vector<mc::FFVar>> storedFunctionsObjCompl;             /*!< vector containing functionsObj of all previously used complementary datasets. Note: position in this vector = index of corresponding reduced dataset - 1 */
    std::vector<std::shared_ptr<mc::FFSubgraph>> storedSubgraphResampled;    /*!< pointer to subgraph of resampled initial dataset. Note: used vector with one element such that MC++ iterators are not corrupted when leaving space of DagObj */
    std::vector<std::shared_ptr<mc::FFSubgraph>> storedSubgraphObjResampled; /*!< pointer to subgraphObj of resampled initial dataset. Note: used vector with one element such that MC++ iterators are not corrupted when leaving space of DagObj  */
    std::vector<mc::FFVar> storedFunctionsResampled;                         /*!< functions of resampled initial dataset */
    std::vector<mc::FFVar> storedFunctionsObjResampled;                      /*!< functionsObj of resampled initial dataset */
#endif // HAVE_GROWING_DATASETS

    MC infinityMC;                  /*!< dummy MC object holding all zeros and infinity */
    double validIntervalLowerBound; /*!< variable holding a valid interval lower bound of the objective function */

    std::vector<std::vector<double>> simplexPoints; /*!< vector holding n+1 simplex points normalized to [-1,1] + the first point is always the mid point 0; the points are row-wise for later vMcCormick usage */
    std::vector<std::vector<double>> scaledPoints;  /*!< vector used to hold points scaled from [-1,1] to [lowerBound,upperBound] */
    std::vector<vMC> vMcPoint;                      /*!< vector McCormick Point at the reference point given by the linearization heuristic used */
    std::vector<vMC> vMCarray;                      /*!< dummy vector of vMC objects for faster evaluation */
    mc::FFSubgraph subgraphNonlinear;               /*!< subgraph holding the list of operations of nonlinear functions in the DAG */
    mc::FFSubgraph subgraphLinear;                  /*!< subgraph holding the list of operations of linear functions in the DAG */
    std::vector<mc::FFVar> functionsNonlinear;      /*!< vector of all nonlinear functions in the DAG */
    std::vector<mc::FFVar> functionsLinear;         /*!< vector of all linear functions in the DAG */
    std::vector<vMC> resultRelaxationVMCNonlinear;  /*!< vector holding resulting vector McCormick relaxations of all nonlinear functions at some linearization point */
    std::vector<MC> resultRelaxationNonlinear;      /*!< vector holding resulting McCormick relaxations of all linear functions at some linearization point */
    std::vector<MC> resultRelaxationLinear;         /*!< vector holding resulting McCormick relaxations of all linear functions at some linearization point */
    std::vector<unsigned> chosenLinPoints;          /*!< vector holding indices of linearization points chosen from simplexPoints */
    std::vector<bool> objRowFilled;                 /*!< vector holding bools whether a LP row of an objective has been filled. This is needed for proper handling in OBBT */

    std::shared_ptr<std::vector<Constraint>> _constraintProperties; /*!< pointer to constraint properties determined by MAiNGO */

    /**
            * @brief Constructor
            */
    DagObj(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
           const std::vector<babBase::OptimizationVariable> &variables, const unsigned nineq, const unsigned neq,
           const unsigned nineqRelaxationOnly, const unsigned neqRelaxationOnly, const unsigned nineqSquash,
           std::shared_ptr<Settings> settings, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn);

    /**
            * @brief Function for additional stuff neeeded when using vector McCormick
            */
    void initialize_vMcCormick();

#ifdef HAVE_GROWING_DATASETS
    /**
    * @brief Function for adding subgraph corresponding to a new reduced dataset
    *
    * @param[in] indexDataset is the index number of the reduced dataset to be used
    */
    void add_subgraph_for_new_dataset(const unsigned int indexDataset);

    /**
    * @brief Function for adding subgraph corresponding to complementary set of reduced dataset
    *
    * @param[in] indexDataset is the index number of the reduced dataset to be used
    */
    void add_subgraph_for_complementary_dataset(const unsigned int indexDataset);

    /**
	* @brief Function for changing objective in dependence of a (reduced) dataset
	*
	* @param[in] indexDataset is the index number of the (reduced) dataset to be used
	*/
    void change_growing_objective(const int indexDataset);

    /**
    * @brief Function for changing objective to resampled initial dataset
    */
    void change_growing_objective_for_resampling();
#endif    //HAVE_GROWING_DATASETS
};


}    // end namespace lbp


}    // end namespace maingo
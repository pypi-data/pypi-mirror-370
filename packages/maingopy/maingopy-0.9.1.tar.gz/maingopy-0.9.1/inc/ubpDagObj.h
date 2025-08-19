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
#include "settings.h"

#include "fadiff.h"
#include "ffunc.hpp"

#include <utility>
#include <vector>


namespace maingo {


namespace ubp {


/**
* @struct DagObj
* @brief Struct for storing all needed Directed acyclic Graph objects for the upper bounding solver.
*
* Contains all objects, copies and variables for the usage of the DAG.
* Further information on DAG can be found in ffunc.hpp of MC++.
*/
struct DagObj {
    /**
	* @name Internal variables for the upper bounding DAG
	*/
    /**@{*/
    mc::FFGraph DAG;                   /*!< the actual DAG */
    std::vector<mc::FFVar> vars;       /*!< DAG variables */
    mc::FFSubgraph subgraph;           /*!< subgraph holding list of operations in the DAG */
    std::vector<mc::FFVar> functions;  /*!< list of all functions in the DAG */
    std::vector<mc::FFVar> resultVars; /*!< vector holding evaluated FFVar Objects to not lose pointers */

    std::vector<fadbad::F<double>> adPoint;                /*!< vector holding FADBAD values for original variables at reference point */
    std::vector<fadbad::F<double>> fadbadArray;            /*!< dummy vector of FADBAD objects for faster evaluation */
    std::vector<fadbad::F<double>> resultAD;               /*!< vector holding FADBAD values of all functions at reference point */
    std::vector<fadbad::F<double>> resultADobj;            /*!< vector holding FADBAD values of objective function at reference point */
    std::vector<fadbad::F<double>> resultADineq;           /*!< vector holding FADBAD values of inequalities at reference point */
    std::vector<fadbad::F<double>> resultADeq;             /*!< vector holding FADBAD values of equalities at reference point */
    std::vector<fadbad::F<double>> resultADineqSquash;     /*!< vector holding FADBAD values of squash inequalities at reference point */
    std::vector<fadbad::F<double>> resultADineqSquashIneq; /*!< vector holding FADBAD values of normal and squash inequalities at reference point */
    std::vector<fadbad::F<double>> resultADineqEq;         /*!< vector holding FADBAD values of inequalities and equalities at reference point */

    std::vector<fadbad::F<fadbad::F<double>>> resultAD2ndOrder;    /*!< vector holding second order FADBAD values of all functions at reference point*/
    std::vector<fadbad::F<fadbad::F<double>>> fadbadArray2ndOrder; /*!< dummy vector of second order FADBAD objects for faster evaluation */
    std::vector<fadbad::F<fadbad::F<double>>> adPoint2ndOrder;     /*!< vector holding second order FADBAD values for original variables at reference point */

    std::vector<double> doublePoint;                /*!< vector holding double values for original variables at reference point */
    std::vector<double> doubleArray;                /*!< dummy vector of double objects for faster evaluation */
    std::vector<double> resultDouble;               /*!< vector holding double values of all functions at point */
    std::vector<double> resultDoubleObj;            /*!< vector holding double values of objective function at reference point */
    std::vector<double> resultDoubleIneq;           /*!< vector holding double values of inequalities at reference point */
    std::vector<double> resultDoubleEq;             /*!< vector holding double values of equalities at reference point */
    std::vector<double> resultDoubleIneqSquash;     /*!< vector holding double values of squash inequalities at reference point */
    std::vector<double> resultDoubleIneqSquashIneq; /*!< vector holding double values of normal and squash inequalities at reference point */
    std::vector<double> resultDoubleIneqEq;         /*!< vector holding double values of (squash) inequalities and equalities at reference point */

    std::vector<mc::FFVar> functionsObj;            /*!< vector holding function(s) for the objective */
    std::vector<mc::FFVar> functionsIneq;           /*!< vector holding functions for the inequalities */
    std::vector<mc::FFVar> functionsEq;             /*!< vector holding functions for the equalities */
    std::vector<mc::FFVar> functionsIneqSquash;     /*!< vector holding functions for the squash inequalities */
    std::vector<mc::FFVar> functionsIneqSquashIneq; /*!< vector holding functions for the normal and squash inequalities*/
    std::vector<mc::FFVar> functionsIneqEq;         /*!< vector holding functions for the (squash) inequalities and equalities */
    mc::FFSubgraph subgraphObj;                     /*!< subgraph holding the list of operations of the objective function(s) */
    mc::FFSubgraph subgraphIneq;                    /*!< subgraph holding the list of operations of the inequalities */
    mc::FFSubgraph subgraphEq;                      /*!< subgraph holding the list of operations of the equalities */
    mc::FFSubgraph subgraphIneqSquash;              /*!< subgraph holding the list of operations of the squash inequalities */
    mc::FFSubgraph subgraphIneqSquashIneq;          /*!< subgraph holding the list of operations of the normal and squash inequalities */
    mc::FFSubgraph subgraphIneqEq;                  /*!< subgraph holding the list of operations of the (squash) inequalities & equalities */

#ifdef HAVE_GROWING_DATASETS
    bool useMse;                                                    /*!< whether to use mean squared error or summed squared error as the objective function */
    unsigned int indexFirstData;                                    /*!< position of the first objective per data in MAiNGO::_DAGfunctions */
    std::shared_ptr<std::vector<unsigned int>> datasets;            /*!< pointer to a vector containing the size of all available datasets */
    std::vector<std::shared_ptr<mc::FFSubgraph>> storedSubgraph;    /*!< vector containing pointers to subgraph of all previously used datasets. Note: position in this vector = index of dataset */
    std::vector<std::shared_ptr<mc::FFSubgraph>> storedSubgraphObj; /*!< vector containing pointers to subgraphObj of all previously used datasets. Note: position in this vector = index of dataset */
    std::vector<std::vector<mc::FFVar>> storedFunctions;            /*!< vector containing functions of all previously used datasets. Note: position in this vector = index of dataset */
    std::vector<std::vector<mc::FFVar>> storedFunctionsObj;         /*!< vector containing functionsObj of all previously used datasets. Note: position in this vector = index of dataset */
#endif    // HAVE_GROWING_DATASETS

    std::shared_ptr<Settings> maingoSettings; /*!< pointer to settings file, used for exception handling */
    std::shared_ptr<Logger> logger;           /*!< pointer to logger, used for exception handling */
    bool warningFlag;                         /*!< flag indicating whether the user already got a warning triggered by an exception in mc::fadbad, used to avoid excessive output */
    /**@}*/

    /**
	* @brief Constructor
	*
	* @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
	* @param[in] DAGvars are the variables corresponding to the DAG
	* @param[in] DAGfunctions are the functions corresponding to the DAG
	* @param[in] variables is a vector containing the initial optimization variables defined in problem.h
	* @param[in] nineq is the number of inequality constraints
	* @param[in] neq is the number of equality constraints
	* @param[in] nineqSquash is the number of squash inequality constraints which are to be used only if the squash node has been used
	* @param[in] constraintProperties is a pointer to the constraint properties determined by MAiNGO
	* @param[in] settingsIn is a pointer to MAiNGO settings used
	* @param[in] loggerIn is a pointer to the MAiNGO logger
	*/
    DagObj(mc::FFGraph& DAG, const std::vector<mc::FFVar>& DAGvars, const std::vector<mc::FFVar>& DAGfunctions,
           const std::vector<babBase::OptimizationVariable>& variables, const unsigned nineq, const unsigned neq,
           const unsigned nineqSquash, std::shared_ptr<std::vector<Constraint>> constraintProperties, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn):
        maingoSettings(settingsIn),
        logger(loggerIn)
    {
        const unsigned nvar = variables.size();
        const unsigned nobj = 1;

        // Copy DAG for upper bounding solver
        for (unsigned int i = 0; i < nvar; i++) {
            mc::FFVar Y;                      // Create a new DAG variable
            this->vars.push_back(Y);          // Add the new DAG variable to the vars vector
            this->vars[i].set(&this->DAG);    // Add the new DAG variable to the DAG
        }
        this->resultVars.resize(DAGfunctions.size());

        DAG.eval(DAGfunctions.size(), DAGfunctions.data(), this->resultVars.data(), nvar, DAGvars.data(), this->vars.data());    // Get functions and write them to resultVars
        this->functions.resize(1 + nineq + neq + nineqSquash);
        // Note that the constraints in constraintProperties are in a different order than in MAiNGO.cpp!
        // Here it is obj, ineq, squash ineq, eq
        for (size_t i = 0; i < constraintProperties->size(); i++) {
            unsigned index = (*constraintProperties)[i].indexNonconstant;
            switch ((*constraintProperties)[i].type) {
                case OBJ:
                    this->functions[i] = this->resultVars[index];
                    break;
                case INEQ:
                    this->functions[i] = this->resultVars[index];
                    break;
                case INEQ_SQUASH:
                    this->functions[i] = this->resultVars[index];
                    break;
                case EQ:
                    this->functions[i] = this->resultVars[index];
                    break;
                case INEQ_REL_ONLY:
                case EQ_REL_ONLY:
                default:    // In upper bounding solver, we don't use relaxation only constraints
                    break;
            }
        }

        // Get the list of operations used in the DAG
        // It is needed for the call of proper DAG functions
#ifndef HAVE_GROWING_DATASETS
        this->subgraph = this->DAG.subgraph(this->functions.size(), this->functions.data());
#else
        storedFunctions.clear();
        storedFunctions.push_back(this->functions);

        storedSubgraph.clear();
        auto pointerToSubgraph = std::make_shared<mc::FFSubgraph>(this->DAG.subgraph(this->functions.size(), this->functions.data()));
        storedSubgraph.push_back(pointerToSubgraph);
        this->subgraph = *storedSubgraph[0];
#endif    // HAVE_GROWING_DATASETS

        // Get operations of each function in the DAG
        this->functionsObj.resize(nobj);
        this->functionsIneq.resize(nineq);
        this->functionsEq.resize(neq);
        this->functionsIneqSquash.resize(nineqSquash);
        this->functionsIneqSquashIneq.resize(nineq + nineqSquash);
        this->functionsIneqEq.resize(nineq + neq + nineqSquash);
        // Get each function, let's do it in one loop
        // Think of the order obj, ineq, squash ineq, eq which is different from the original one in MAiNGO.cpp
        for (size_t i = 0; i < constraintProperties->size(); i++) {
            unsigned index     = (*constraintProperties)[i].indexNonconstantUBP;
            unsigned indexType = (*constraintProperties)[i].indexTypeNonconstant;
            switch ((*constraintProperties)[i].type) {
                case OBJ:
                    this->functionsObj[i] = this->functions[index];
                    break;
                case INEQ:
                    this->functionsIneq[indexType]           = this->functions[index];
                    this->functionsIneqSquashIneq[indexType] = this->functions[index];
                    this->functionsIneqEq[indexType]         = this->functions[index];
                    break;
                case INEQ_SQUASH:
                    this->functionsIneqSquash[indexType]             = this->functions[index];
                    this->functionsIneqSquashIneq[indexType + nineq] = this->functions[index];
                    this->functionsIneqEq[indexType + nineq]         = this->functions[index];
                    break;
                case EQ:
                    this->functionsEq[indexType]                           = this->functions[index];
                    this->functionsIneqEq[indexType + nineq + nineqSquash] = this->functions[index];    // all inequalities first
                    break;
                case INEQ_REL_ONLY:
                case EQ_REL_ONLY:
                default:    // In upper bounding solver, we don't use relaxation only constraints
                    break;
            }
        }

        // Get operations of each function
#ifndef HAVE_GROWING_DATASETS
        this->subgraphObj = this->DAG.subgraph(this->functionsObj.size(), this->functionsObj.data());
#else
        storedFunctionsObj.clear();
        storedFunctionsObj.push_back(this->functionsObj);

        storedSubgraphObj.clear();
        auto pointerToSubgraphObj = std::make_shared<mc::FFSubgraph>(this->DAG.subgraph(this->functionsObj.size(), this->functionsObj.data()));
        storedSubgraphObj.push_back(pointerToSubgraphObj);
        this->subgraphObj = *storedSubgraphObj[0];
#endif    // HAVE_GROWING_DATASETS

        this->subgraphIneq           = this->DAG.subgraph(this->functionsIneq.size(), this->functionsIneq.data());
        this->subgraphEq             = this->DAG.subgraph(this->functionsEq.size(), this->functionsEq.data());
        this->subgraphIneqSquash     = this->DAG.subgraph(this->functionsIneqSquash.size(), this->functionsIneqSquash.data());
        this->subgraphIneqSquashIneq = this->DAG.subgraph(this->functionsIneqSquashIneq.size(), this->functionsIneqSquashIneq.data());
        this->subgraphIneqEq         = this->DAG.subgraph(this->functionsIneqEq.size(), this->functionsIneqEq.data());

        // Allocate memory for the corresponding vectors
        this->adPoint.resize(nvar);
        this->fadbadArray.resize(this->subgraph.l_op.size());
        this->doublePoint.resize(nvar);
        this->doubleArray.resize(this->subgraph.l_op.size());
        this->resultAD.resize(this->functions.size());
        this->resultADobj.resize(this->functionsObj.size());
        this->resultADineq.resize(this->functionsIneq.size());
        this->resultADeq.resize(this->functionsEq.size());
        this->resultADineqEq.resize(this->functionsIneqEq.size());
        this->resultADineqSquash.resize(this->functionsIneqSquash.size());
        this->resultADineqSquashIneq.resize(this->functionsIneqSquashIneq.size());
        this->resultDouble.resize(this->functions.size());
        this->resultDoubleObj.resize(this->functionsObj.size());
        this->resultDoubleIneq.resize(this->functionsIneq.size());
        this->resultDoubleEq.resize(this->functionsEq.size());
        this->resultDoubleIneqSquash.resize(this->functionsIneqSquash.size());
        this->resultDoubleIneqSquashIneq.resize(this->functionsIneqSquashIneq.size());
        this->resultDoubleIneqEq.resize(this->functionsIneqEq.size());
        this->adPoint2ndOrder.resize(nvar);
        this->fadbadArray2ndOrder.resize(this->subgraph.l_op.size());
        this->resultAD2ndOrder.resize(this->functions.size());

        this->warningFlag = false;
    }

#ifdef HAVE_GROWING_DATASETS
    /**
    * @brief Function for adding a subgraph corresponding to a new reduced dataset
    *
    * @param[in] indexDataset is the index number of the reduced dataset to be used
    */
    void add_subgraph_for_new_dataset(const unsigned int indexDataset)
    {
        mc::FFVar obj = 0;
        for (auto idxDataPoint = 0; idxDataPoint < (*datasets)[indexDataset]; idxDataPoint++) {
            obj += resultVars[idxDataPoint + indexFirstData];
        }
        if (useMse) {// Use mean of summed objective per data as objective
            functions[0]    = obj / (*datasets)[indexDataset];
            functionsObj[0] = obj / (*datasets)[indexDataset];
        }
        else {// Use sum of objective per data as objective
            functions[0]    = obj;
            functionsObj[0] = obj;
        }

        // Build new subgraphs
        storedFunctions.push_back(functions);
        auto pointerToSubgraph = std::make_shared<mc::FFSubgraph>(DAG.subgraph(functions.size(), functions.data()));
        storedSubgraph.push_back(pointerToSubgraph);

        storedFunctionsObj.push_back(functionsObj);
        auto pointerToSubgraphObj = std::make_shared<mc::FFSubgraph>(DAG.subgraph(functionsObj.size(), functionsObj.data()));
        storedSubgraphObj.push_back(pointerToSubgraphObj);
    }

    /**
    * @brief Function for changing objective in dependence of a (reduced) dataset
    *
    * @param[in] indexDataset is the index number of the (reduced) dataset to be used
    */
    void change_growing_objective(const unsigned int indexDataset)
    {
        // Build subgraphs if necessary
        if (indexDataset >= storedSubgraphObj.size()) {
            // If we do not have a subgraph for each dataset until the new dataset: build it
            // In parallel version (and only there), we may jump over datasets if they have already been processed by another node
            for (auto idx = storedSubgraphObj.size(); idx <= indexDataset; idx++) {
                add_subgraph_for_new_dataset(idx);
            }

        }

        // Update subgraphs
        subgraph  = *storedSubgraph[indexDataset];
        functions = storedFunctions[indexDataset];

        subgraphObj  = *storedSubgraphObj[indexDataset];
        functionsObj = storedFunctionsObj[indexDataset];
    }
#endif    //HAVE_GROWING_DATASETS
};


}    // end namespace ubp


}    // end namespace maingo
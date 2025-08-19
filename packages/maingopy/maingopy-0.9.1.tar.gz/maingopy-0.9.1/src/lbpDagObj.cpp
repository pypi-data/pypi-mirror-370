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

#include "lbpDagObj.h"
#include "MAiNGOException.h"

#include <iterator>

namespace maingo {


namespace lbp {


///////////////////////////////////////////////////////////////
// constructor
DagObj::DagObj(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
               const std::vector<babBase::OptimizationVariable> &variables, const unsigned nineq, const unsigned neq, const unsigned nineqRelaxationOnly,
               const unsigned neqRelaxationOnly, const unsigned nineqSquash, std::shared_ptr<Settings> settings, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn):
    _constraintProperties(constraintPropertiesIn)
{
    const unsigned nvar = variables.size();

    // Copy DAG for LowerBoundingSolver
    for (unsigned int i = 0; i < nvar; i++) {
        mc::FFVar Y;                      // Create a new DAG variable
        this->vars.push_back(Y);          // Add the new DAG variable to the vars vector
        this->vars[i].set(&this->DAG);    // Add the new DAG variable to the DAG
    }
    this->resultVars.resize(DAGfunctions.size());
    DAG.eval(DAGfunctions.size(), DAGfunctions.data(), this->resultVars.data(), nvar, DAGvars.data(), this->vars.data());    // Get functions and write them to resultVars
    for (unsigned int i = 0; i < 1 + nineq + neq + nineqRelaxationOnly + neqRelaxationOnly + nineqSquash; i++) {             // Do not track obj_per_data and output var's
        this->functions.push_back(this->resultVars[i]);                                                                      // Get functions
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
    this->functionsObj.clear();
    this->functionsIneq.clear();
    this->functionsEq.clear();
    this->functionsIneqRelaxationOnly.clear();
    this->functionsEqRelaxationOnly.clear();
    this->functionsIneqSquash.resize(nineq);
    this->functionsObj.resize(1);
    this->functionsIneq.resize(nineq);
    this->functionsEq.resize(neq);
    this->functionsIneqRelaxationOnly.resize(nineqRelaxationOnly);
    this->functionsEqRelaxationOnly.resize(neqRelaxationOnly);
    this->functionsIneqSquash.resize(nineqSquash);
    // Get each function, let's do it in one loop
    for (unsigned int i = 0; i < this->functions.size(); i++) {
        unsigned indexType = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].type) {
            case OBJ:
                this->functionsObj[indexType].push_back(this->functions[i]);
                break;
            case INEQ:
                this->functionsIneq[indexType].push_back(this->functions[i]);
                break;
            case EQ:
                this->functionsEq[indexType].push_back(this->functions[i]);
                break;
            case INEQ_REL_ONLY:
                this->functionsIneqRelaxationOnly[indexType].push_back(this->functions[i]);
                break;
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                this->functionsEqRelaxationOnly[indexType].push_back(this->functions[i]);
                break;    // Auxiliary relaxation only equalities are handled the same way as rel only eqs
            case INEQ_SQUASH:
                this->functionsIneqSquash[indexType].push_back(this->functions[i]);
                break;
            default:
                break;
        }
    }
    // Get subgraph of each function
    this->subgraphObj.clear();
    this->subgraphIneq.clear();
    this->subgraphEq.clear();
    this->subgraphIneqRelaxationOnly.clear();
    this->subgraphEqRelaxationOnly.clear();
    this->subgraphIneqSquash.clear();
    this->subgraphObj.resize(1);
    this->subgraphIneq.resize(nineq);
    this->subgraphEq.resize(neq);
    this->subgraphIneqRelaxationOnly.resize(nineqRelaxationOnly);
    this->subgraphEqRelaxationOnly.resize(neqRelaxationOnly);
    this->subgraphIneqSquash.resize(nineqSquash);
#ifdef HAVE_GROWING_DATASETS
    std::shared_ptr<mc::FFSubgraph> pointerToSubgraphObj;
#endif    // HAVE_GROWING_DATASETS

    for (unsigned int i = 0; i < this->functions.size(); i++) {
        unsigned indexType = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].type) {
            case OBJ:
#ifndef HAVE_GROWING_DATASETS
                this->subgraphObj[indexType] = this->DAG.subgraph(this->functionsObj[indexType].size(), this->functionsObj[indexType].data());
#else
                storedFunctionsObj.clear();
                storedFunctionsObj.push_back(this->functionsObj[indexType]);
                storedSubgraphObj.clear();
                pointerToSubgraphObj = std::make_shared<mc::FFSubgraph>(this->DAG.subgraph(this->functionsObj[indexType].size(), this->functionsObj[indexType].data()));
                storedSubgraphObj.push_back(pointerToSubgraphObj);
                this->subgraphObj[indexType] = *storedSubgraphObj[0];
#endif    // HAVE_GROWING_DATASETS
                break;
            case INEQ:
                this->subgraphIneq[indexType] = this->DAG.subgraph(this->functionsIneq[indexType].size(), this->functionsIneq[indexType].data());
                break;
            case EQ:
                this->subgraphEq[indexType] = this->DAG.subgraph(this->functionsEq[indexType].size(), this->functionsEq[indexType].data());
                break;
            case INEQ_REL_ONLY:
                this->subgraphIneqRelaxationOnly[indexType] = this->DAG.subgraph(this->functionsIneqRelaxationOnly[indexType].size(), this->functionsIneqRelaxationOnly[indexType].data());
                break;
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                this->subgraphEqRelaxationOnly[indexType] = this->DAG.subgraph(this->functionsEqRelaxationOnly[indexType].size(), this->functionsEqRelaxationOnly[indexType].data());
                break;
            case INEQ_SQUASH:
                this->subgraphIneqSquash[indexType] = this->DAG.subgraph(this->functionsIneqSquash[indexType].size(), this->functionsIneqSquash[indexType].data());
                break;
            default:
                break;
        }
    }

    // Allocate memory for the corresponding vectors (in dependence on LBP_linpoints) and also set settings
    // We use these always, e.g., for option check
    this->McPoint.resize(nvar);
    this->MCarray.resize(this->subgraph.l_op.size());
    this->resultRelaxation.resize(this->functions.size());

    // Objects needed for heuristics
    this->intervals_already_computed = false;
    this->intervalArray.resize(2 * this->subgraph.l_op.size());    // It is double the size, since it is used for forward and backward propagation
    this->constraintIntervals.resize(this->functions.size());
    this->currentIntervals.resize(nvar);

    // Compute a McCormick object with correct dimensions and everything is 0, this object is needed to properly reset the LP in Kelley's algorithm
    this->infinityMC = MC(I(0, 1), settings->infinity);
    this->infinityMC.sub(nvar);
    this->intervals_already_computed = false;
    validIntervalLowerBound          = -settings->infinity;
}


/////////////////////////////////////////////////////////////////////////
// function for initializing additional stuff needed when using vector-McCormick
void
DagObj::initialize_vMcCormick()
{

    this->functionsNonlinear.clear();
    this->functionsLinear.clear();
    this->vMcPoint.resize(this->vars.size());

    // Get linear and nonlinear functions
    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        if ((*_constraintProperties)[i].dependency > LINEAR) {
            this->functionsNonlinear.push_back(this->functions[i]);
        }
        else {
            this->functionsLinear.push_back(this->functions[i]);
        }
    }
    this->subgraphNonlinear = this->DAG.subgraph(this->functionsNonlinear.size(), this->functionsNonlinear.data());
    this->subgraphLinear    = this->DAG.subgraph(this->functionsLinear.size(), this->functionsLinear.data());
    this->resultRelaxationVMCNonlinear.resize(this->functionsNonlinear.size());
    this->resultRelaxationNonlinear.resize(this->functionsNonlinear.size());
    this->resultRelaxationLinear.resize(this->functionsLinear.size());
    this->vMCarray.resize(this->subgraphNonlinear.l_op.size());
}


#ifdef HAVE_GROWING_DATASETS
/////////////////////////////////////////////////////////////////////////
// function for adding subgraph corresponding to a new reduced dataset
void
DagObj::add_subgraph_for_new_dataset(const unsigned int indexDataset)
{
    mc::FFVar obj = 0;
    for (auto idxDataPoint = 0; idxDataPoint < (*datasets)[indexDataset]; idxDataPoint++) {
        obj += resultVars[idxDataPoint + indexFirstData];
    }
    if (useMse) {// Use mean of summed objective per data as objective
        functions[0]       = obj / (*datasets)[indexDataset];
        functionsObj[0][0] = obj / (*datasets)[indexDataset];
    }
    else {// Use sum of objective per data as objective
        functions[0]       = obj;
        functionsObj[0][0] = obj;
    }

    // Build new subgraphs
    storedFunctions.push_back(functions);
    auto pointerToSubgraph = std::make_shared<mc::FFSubgraph>(DAG.subgraph(functions.size(), functions.data()));
    storedSubgraph.push_back(pointerToSubgraph);

    storedFunctionsObj.push_back(functionsObj[0]);
    auto pointerToSubgraphObj = std::make_shared<mc::FFSubgraph>(DAG.subgraph(functionsObj[0].size(), functionsObj[0].data()));
    storedSubgraphObj.push_back(pointerToSubgraphObj);
}


/////////////////////////////////////////////////////////////////////////
// function for adding subgraph corresponding to complementary set of reduced dataset
void
DagObj::add_subgraph_for_complementary_dataset(const unsigned int indexDataset)
{
    mc::FFVar obj = 0;
    for (auto idxDataPoint = (*datasets)[indexDataset]; idxDataPoint < (*datasets)[0]; idxDataPoint++) {
        obj += resultVars[idxDataPoint + indexFirstData];
    }
    if (useMse) {// Use mean of summed objective per data as objective
        functions[0]       = obj / ((*datasets)[0] - (*datasets)[indexDataset]);
        functionsObj[0][0] = obj / ((*datasets)[0] - (*datasets)[indexDataset]);
    }
    else {// Use sum of objective per data as objective
        functions[0]       = obj;
        functionsObj[0][0] = obj;
    }

    // Build new subgraphs
    storedFunctionsCompl.push_back(functions);
    auto pointerToSubgraph = std::make_shared<mc::FFSubgraph>(DAG.subgraph(functions.size(), functions.data()));
    storedSubgraphCompl.push_back(pointerToSubgraph);

    storedFunctionsObjCompl.push_back(functionsObj[0]);
    auto pointerToSubgraphObj = std::make_shared<mc::FFSubgraph>(DAG.subgraph(functionsObj[0].size(), functionsObj[0].data()));
    storedSubgraphObjCompl.push_back(pointerToSubgraphObj);
}


/////////////////////////////////////////////////////////////////////////
// function for changing objective in dependence of a (reduced) dataset
void
DagObj::change_growing_objective(const int indexDataset)
{
    if (indexDataset >= 0) {// Change to full or reduced data set
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

        subgraphObj[0]  = *storedSubgraphObj[indexDataset];
        functionsObj[0] = storedFunctionsObj[indexDataset];
    }
    else {// Change to complementary set of reduced dataset
        // negative sign just means to use complementary set; complementary set of full dataset is empty
        unsigned int indexDatasetTransformed = -indexDataset - 1;

        if (indexDatasetTransformed < 0) {
            std::ostringstream errmsg;
            errmsg << "  Error in LowerBoundingSolver - change of objective: calling complementary set of full dataset, i.e., an empty set. " << std::endl;
            throw MAiNGOException(errmsg.str());
        }

        // Build subgraphs if necessary
        if (indexDatasetTransformed >= storedSubgraphObjCompl.size()) {
            // E.g., with augmentation rule VALSCAL it is possible to jump over a complementary dataset
            // As an alternative to building potentially unused subgraphs, we could safe empty subgraphs (if MC++ allows) and test for it in the argument of this if-statement
            for (auto i = storedSubgraphObjCompl.size(); i <= indexDatasetTransformed; i++) {
                add_subgraph_for_complementary_dataset(i+1); // Reversion of index transformation: 0 < -indexDataset = indexDatasetTransformed + 1
            }
        }

        // Update subgraphs
        subgraph  = *storedSubgraphCompl[indexDatasetTransformed];
        functions = storedFunctionsCompl[indexDatasetTransformed];

        subgraphObj[0]  = *storedSubgraphObjCompl[indexDatasetTransformed];
        functionsObj[0] = storedFunctionsObjCompl[indexDatasetTransformed];
    }
}

/////////////////////////////////////////////////////////////////////////
// function for changing objective to resampled initial dataset
void
DagObj::change_growing_objective_for_resampling()
{
    if (storedSubgraphResampled.size() == 0) {// Subgraph for resampled dataset not built yet
        if ((*datasetResampled).size() == 0) {
            std::ostringstream errmsg;
            errmsg << "  Error in LowerBoundingSolver - change of objective for resampling: datasetResampled is empty. " << std::endl;
            throw MAiNGOException(errmsg.str());
        }

        mc::FFVar obj = 0;
        for (auto idxDataPoint : (*datasetResampled)) {
            obj += resultVars[idxDataPoint + indexFirstData];
        }
        if (useMse) {// Use mean of summed objective per data as objective
            functions[0] = obj / (*datasetResampled).size();
            functionsObj[0][0] = obj / (*datasetResampled).size();
        }
        else {// Use sum of objective per data as objective
            functions[0] = obj;
            functionsObj[0][0] = obj;
        }

        // Build new subgraphs
        storedFunctionsResampled = functions;
        auto pointerToSubgraph   = std::make_shared<mc::FFSubgraph>(DAG.subgraph(functions.size(), functions.data()));
        storedSubgraphResampled.push_back(pointerToSubgraph);
        subgraph                 = *storedSubgraphResampled[0];

        storedFunctionsObjResampled = functionsObj[0];
        auto pointerToSubgraphObj   = std::make_shared<mc::FFSubgraph>(DAG.subgraph(functionsObj[0].size(), functionsObj[0].data()));
        storedSubgraphObjResampled.push_back(pointerToSubgraph);
        subgraphObj[0]              = *storedSubgraphObjResampled[0];
    }
    else {
        // Update subgraphs
        subgraph  = *storedSubgraphResampled[0];
        functions = storedFunctionsResampled;

        subgraphObj[0]  = *storedSubgraphObjResampled[0];
        functionsObj[0] = storedFunctionsObjResampled;
    }
}
#endif    //HAVE_GROWING_DATASETS


}    // end namespace lbp


}    // end namespace maingo
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

#include "MAiNGOmodel.h"


/**
*  @namespace maingo
*  @brief namespace holding all essentials of MAiNGO
*/
namespace maingo {


/**
* @class MAiNGOmodelEpsCon
* @brief This class is the base class for implementing bi-objective problems
*
* This class is used to derive a Model class in problem.h, where the user can implement their actual model.
*/
class MAiNGOmodelEpsCon: public MAiNGOmodel {

  public:
    /**
      * @brief Destructor
      */
    virtual ~MAiNGOmodelEpsCon() {} 

    /**
      * @brief Virtual function which has to be implemented by the user in order to enable evaluation of the model
      *
      * @param[in] optVars is a vector holding the optimization variables
      */
    virtual EvaluationContainer evaluate_user_model(const std::vector<Var> &optVars) = 0;

    /**
      * @brief Virtual function which has to be implemented by the user in order to enable getting data on optimization variables
      */
    virtual std::vector<OptimizationVariable> get_variables() = 0;

    /**
      * @brief Virtual function which has to be implemented by the user in order to enable evaluation of the model
      *
      * @param[in] optVars is a vector holding the optimization variables
      */
    EvaluationContainer evaluate(const std::vector<Var> &optVars) final;

    /**
      * @brief Virtual function which has to be implemented by the user in order to enable getting data on the initial point
      */
    virtual std::vector<double> get_initial_point() { return std::vector<double>(); } // GCOVR_EXCL_LINE

    /**
      * @brief Function for changing the epsilon-parameters
      *
      * @param[in] epsilon is a vector holding the epsilon parameters
      */
    void set_epsilon(const std::vector<double> &epsilon)
    {
        _epsilon = epsilon;
    }

    /**
      * @brief Function for setting the objective index
      *
      * @param[in] objectiveIndex is the index of the objective to be minimized
      */
    void set_objective_index(const size_t objectiveIndex)
    {
        _objectiveIndex = objectiveIndex;
    }

    /**
      * @brief Function for setting the _singleObjective flag
      *
      * @param[in] singleObjective indicates whether the next problem should be considered as single-objective
      */
    void set_single_objective(bool singleObjective)
    {
        _singleObjective = singleObjective;
    }

  private:
    std::vector<double> _epsilon = {}; /*!< vector of epsilon parameters for use in the epsilon-constraint method */
    size_t _objectiveIndex = 0;        /*!< index of objective to be minimized during epsilon-constraint method. The other objective will be used in the epsilon-constraint */
    bool _singleObjective = true;      /*!< flag indicating whether the next problem should be considered as single-objective (for objective _objectiveIndex), or whether to use the epsilon constraint(s) */
};


}    // end namespace maingo
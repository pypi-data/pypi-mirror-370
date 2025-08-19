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
#include "program.h"

#include "symbol_table.hpp"

#include <unordered_map>


using Var = mc::FFVar;


namespace maingo {

/**
* @class AleModel
* @brief This class provides the interface for a program composed of ALE expressions
*/
class AleModel: public MAiNGOmodel {

  public:
    /**
	* @brief Main function used to evaluate the model and construct a directed acyclic graph
	*
	* @param[in] optVars is the optimization variables vector
	*/
    EvaluationContainer evaluate(const std::vector<Var>& optVars);

    /**
    * @brief Constructor taking a ALE-based Program and an ALE symbol_table
    *
    * @param[in] prog is the program to translate to MAiNGO
    * @param[in] symbols is the symbol_table used to resolve symbols used in prog
    */
    AleModel(Program prog, ale::symbol_table& symbols):
        _prog(prog), _symbols(symbols)
    {
        make_variables();
    };

    /**
	* @brief Function for getting optimization variables data
	*/
    std::vector<OptimizationVariable> get_variables();

    /**
	* @brief Function for getting optimization variable position data
	*/
    const std::unordered_map<std::string, int>& get_positions();

    /**
	* @brief Function for getting initial point data
	*/
    std::vector<double> get_initial_point();

    /**
	* @brief Function for populating _variables, _initials, and _positions
	*/
    void make_variables();

  private:
    Program _prog;               /*!< Container for ALE expressions*/
    ale::symbol_table& _symbols; /*!< Container for ALE symbols*/

    std::vector<OptimizationVariable> _variables;    /*!< OptimiztionVariables used in the model*/
    std::vector<double> _initials;                   /*!< Initial point for _variables*/
    std::unordered_map<std::string, int> _positions; /*!< Association of ALE symbol names to positions in _variables*/
};


}    // namespace maingo
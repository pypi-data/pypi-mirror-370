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

#include "babOptVar.h"

#include "symbol.hpp"


namespace maingo {


using namespace ale;


/**
* @brief Function for serializing index sequences
*
* @param[in] indexes is the array of indexes to serialize
*/
template <unsigned IDim>
std::string
var_indexes(size_t* indexes, char delimiter)
{
    return std::to_string(indexes[0] + 1) + delimiter + var_indexes<IDim - 1>(indexes + 1, delimiter);
}

/**
* @brief Function for serializing index sequences
*
* @param[in] indexes is the array of indexes to serialize
*/
template <>
inline std::string
var_indexes<1>(size_t* indexes, char delimiter)
{
    return std::to_string(indexes[0] + 1);
}

/**
* @brief Function for flattening indexed symbol names
*
* @param[in] base is the base name of the symbol
* @param[in] indexes is the array of indexes to flatten
*/
template <unsigned IDim>
std::string
var_name(std::string base, size_t* indexes, char delimiter)
{
    return base + delimiter + var_indexes<IDim>(indexes, delimiter);
}

/**
* @class VariableLister
* @brief Serializes a given symbol and lists it into a vector
*/
class VariableLister {
  public:
    /**
	* @brief Constructor
	*
	* @param[out] variables is the resulting vector of variables
	* @param[out] initials is the resulting vector of initial values
	* @param[out] positions maps symbol names to positions in the variable vector
	*/
    VariableLister(
        std::vector<OptimizationVariable>& variables,
        std::vector<double>& initials,
        std::unordered_map<std::string, int>& positions):
        _variables(variables),
        _initials(initials), _positions(positions)
    {
    }

    /**
	* @brief Dispatch function
	*
	* @param[in] sym is the symbol to be serialized
	*/
    void dispatch(base_symbol* sym)
    {
        if (sym) {
            return std::visit(*this, sym->get_base_variant());
        }
    }

    /**
	* @name Visit functions
	* @brief Specific visit implementations
	*/
    /**@{*/
    template <typename TType>
    void operator()(value_symbol<TType>* sym)
    {
    }


    template <unsigned IDim>
    void operator()(value_symbol<real<IDim>>* sym)
    {
        return std::visit(*this, sym->get_value_variant());
    }


    template <unsigned IDim>
    void operator()(parameter_symbol<real<IDim>>* sym)
    {
    }


    template <unsigned IDim>
    void operator()(expression_symbol<real<IDim>>* sym)
    {
    }


    template <unsigned IDim>
    void operator()(function_symbol<real<IDim>>* sym)
    {
    }

    template <unsigned IDim>
    void operator()(function_symbol<ale::index<IDim>>* sym)
    {
    }

    template <unsigned IDim>
    void operator()(function_symbol<boolean<IDim>>* sym)
    {
    }


    template <unsigned IDim>
    void operator()(variable_symbol<real<IDim>>* sym)
    {
        for (int i = 0; i < IDim; ++i) {
            if (sym->shape(i) == 0) {
                return;
            }
        }
        _positions[sym->m_name] = _variables.size();
        size_t indexes[IDim];
        for (int i = 0; i < IDim; ++i) {
            indexes[i] = 0;
        }
        while (indexes[0] < sym->shape(0)) {
            if (sym->lower()[indexes] == -std::numeric_limits<double>::infinity() || sym->upper()[indexes] == std::numeric_limits<double>::infinity()) {
                throw MAiNGOException("  Error: VariableLister -- Entry of variable " + sym->m_name + "[" + var_indexes<IDim>(indexes, ',') + "] is unbounded");
            }
            maingo::VT vartype = VT_CONTINUOUS;
            if (sym->integral()) {
                if (ceil(sym->lower()[indexes]) == 0 && floor(sym->upper()[indexes]) == 1) {
                    vartype = VT_BINARY;
                }
                else {
                    vartype = VT_INTEGER;
                }
            }
            double lower          = sym->lower()[indexes];
            double upper          = sym->upper()[indexes];
            double branching_prio = sym->prio()[indexes];
            if (std::isnan(branching_prio)) {
                branching_prio = 1;
            }
            else if (branching_prio < 0) {
                throw MAiNGOException("  Error: VariableLister -- Branching priority of variable entry " + sym->m_name + "[" + var_indexes<IDim>(indexes, ',') + "] is less than 0");
            }
            else if (static_cast<unsigned int>(branching_prio) != branching_prio) {
                std::cout << "  Warning: VariableLister -- Non-integer branching priority of variable entry " << sym->m_name << "[" + var_indexes<IDim>(indexes, ',')
                          << "].prio = " << branching_prio << ". Setting branching priority to " << static_cast<unsigned int>(branching_prio) << ".\n";
                branching_prio = static_cast<unsigned int>(branching_prio);
            }
            _variables.push_back(
                OptimizationVariable(
                    Bounds(lower, upper),
                    vartype,
                    branching_prio,
                    var_name<IDim>(sym->m_name, indexes, '_')));
            double initial = sym->init()[indexes];
            if (std::isnan(initial)) {
                initial = 0.5 * (lower + upper);
            }
            _initials.push_back(initial);
            for (int i = IDim - 1; i >= 0; --i) {
                if (++indexes[i] < sym->shape(i)) {
                    break;
                }
                else if (i != 0) {
                    indexes[i] = 0;
                }
            }
        }
    }


    void operator()(variable_symbol<real<0>>* sym)
    {
        if (sym->lower() == -std::numeric_limits<double>::infinity() || sym->upper() == std::numeric_limits<double>::infinity()) {
            throw MAiNGOException("  Error: VariableLister -- Variable " + sym->m_name + " is unbounded");
        }
        _positions[sym->m_name] = _variables.size();
        maingo::VT vartype      = VT_CONTINUOUS;
        if (sym->integral()) {
            if (ceil(sym->lower()) == 0 && floor(sym->upper()) == 1) {
                vartype = VT_BINARY;
            }
            else {
                vartype = VT_INTEGER;
            }
        }
        double lower          = sym->lower();
        double upper          = sym->upper();
        double branching_prio = sym->prio();
        if (std::isnan(branching_prio)) {
            branching_prio = 1;
        }
        else if (branching_prio < 0) {
            throw MAiNGOException("  Error: VariableLister -- Branching priority of variable " + sym->m_name + " is less than 0");
        }
        else if (static_cast<unsigned int>(branching_prio) != branching_prio) {
            std::cout << "  Warning: VariableLister -- Non-integer branching priority of variable " << sym->m_name
                      << ".prio = " << branching_prio << ". Setting branching priority to " << static_cast<unsigned int>(branching_prio) << ".\n";
            branching_prio = static_cast<unsigned int>(branching_prio);
        }
        _variables.push_back(
            OptimizationVariable(
                Bounds(lower, upper),
                vartype,
                branching_prio,
                sym->m_name));
        double initial = sym->init();
        if (std::isnan(initial)) {
            initial = 0.5 * (lower + upper);
        }
        _initials.push_back(initial);
    }
    /**@}*/

  private:
    std::vector<OptimizationVariable>& _variables;    /*!< Vector of MAiNGO variables*/
    std::vector<double>& _initials;                   /*!< Vector of initial values*/
    std::unordered_map<std::string, int>& _positions; /*!< Positions of symbols in the variable vector*/
};


}    // namespace maingo
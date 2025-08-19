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
#include "symbol_table.hpp"

#include "nrtlSubroutines.h"
#include "util/evaluator.hpp"
#include "util/visitor_utils.hpp"
#include <iterator>

#include "ffunc.hpp"


namespace maingo {


using namespace ale;
using namespace ale::util;
using Var = mc::FFVar;

/**
* @struct ConstraintContainer
* @brief Containter for constraint evaluation
*/
struct ConstraintContainer {
    std::vector<Var> eq;   /*!< Equality constraints*/
    std::vector<Var> ineq; /*!< Inequality constraints*/
};

/**
* @class MaingoEvaluator
* @brief Evaluates ALE expressions to Var
*/
class MaingoEvaluator {

  public:
    /**
    * @brief Constructor
    *
    * @param[in] symbols is the symbol_table for symbol lookup
    * @param[in] variables is the vecor of MAiNGO variables
    * @param[in] positions maps ALE symbol names to positions in the MAiNGO variable vector
    */
    MaingoEvaluator(
        symbol_table& symbols,
        const std::vector<Var>& variables,
        const std::unordered_map<std::string, int>& positions):
        _symbols(symbols),
        _variables(variables),
        _positions(positions)
    {
    }

    /**
    * @name Dispatch functions
    * @brief Functions dispatching to visit functions
    */
    /**@{*/
    Var dispatch(expression<real<0>>& expr)
    {
        return dispatch(expr.get());
    }

    template <unsigned IDim>
    tensor<Var, IDim> dispatch(expression<real<IDim>>& expr)
    {
        return dispatch(expr.get());
    }

    ConstraintContainer dispatch(expression<boolean<0>>& expr)
    {
        return dispatch(expr.get());
    }

    template <typename TReturn, typename TType>
    TReturn dispatch(value_node<TType>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Used unsupported dispatch");
    }

    template <unsigned IDim>
    typename ale::index<IDim>::ref_type dispatch(value_node<ale::index<IDim>>* node)
    {
        return util::evaluate_expression(node, _symbols);
    }

    int dispatch(value_node<ale::index<0>>* node)
    {
        return util::evaluate_expression(node, _symbols);
    }

    template <typename TType>
    typename set<TType, 0>::basic_type dispatch(value_node<set<TType, 0>>* node)
    {
        return util::evaluate_expression(node, _symbols);
    }


    template <unsigned IDim>
    tensor<Var, IDim> dispatch(value_node<real<IDim>>* node)
    {
        return std::visit(*this, node->get_variant());
    }


    Var dispatch(value_node<real<0>>* node)
    {
        return std::visit(*this, node->get_variant());
    }


    ConstraintContainer dispatch(value_node<boolean<0>>* node)
    {
        return std::visit(*this, node->get_variant());
    }

    template <unsigned IDim>
    tensor<Var, IDim> dispatch(value_symbol<real<IDim>>* sym)
    {
        return std::visit(*this, sym->get_value_variant());
    }

    Var dispatch(value_symbol<real<0>>* sym)
    {
        return std::visit(*this, sym->get_value_variant());
    }
    /**@}*/

    /**
    * @name Visit functions
    * @brief Specific visit implementations
    */
    /**@{*/
    template <unsigned IDim>
    tensor<Var, IDim> operator()(constant_node<real<IDim>>* node)
    {
        tensor<Var, IDim> result(node->value.shape());
        result.ref().assign(node->value);
        return result;
    }


    Var operator()(constant_node<real<0>>* node)
    {
        return node->value;
    }


    ConstraintContainer operator()(constant_node<boolean<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported general logical expression");
        return ConstraintContainer();
    }


    template <unsigned IDim>
    tensor<Var, IDim> operator()(parameter_node<real<IDim>>* node)
    {
        auto sym = _symbols.resolve<real<IDim>>(node->name);
        if (!sym) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Symbol " + node->name + " has unexpected type");
        }
        return dispatch(sym);
    }

    template <unsigned IDim>
    tensor<Var, IDim> operator()(attribute_node<real<IDim>>* node)
    {
        variable_symbol<real<IDim>>* sym = cast_variable_symbol<real<IDim>>(_symbols.resolve(node->variable_name));
        if (!sym) {
            throw std::invalid_argument("Error: MaingoEvaluator -- Symbol " + node->variable_name + " has unexpected type in attribute call.");
        }
        tensor<Var, IDim> result(sym->shape());
        switch (node->attribute) {
            case variable_attribute_type::INIT:
                result.ref().assign(sym->init());
                return result;
            case variable_attribute_type::LB:
                result.ref().assign(sym->lower());
                return result;
            case variable_attribute_type::UB:
                result.ref().assign(sym->upper());
                return result;
            case variable_attribute_type::PRIO:
                result.ref().assign(sym->prio());
                return result;
            default:
                throw std::invalid_argument("Error: MaingoEvaluator -- Symbol " + node->variable_name + " has unexpected attribute.");
        }
    }

    Var operator()(attribute_node<real<0>>* node)
    {
        variable_symbol<real<0>>* sym = cast_variable_symbol<real<0>>(_symbols.resolve(node->variable_name));
        if (!sym) {
            throw std::invalid_argument("Error: MaingoEvaluator -- Symbol " + node->variable_name + " has unexpected type in attribute call.");
        }
        switch (node->attribute) {
            case variable_attribute_type::INIT:
                return sym->init();
            case variable_attribute_type::LB:
                return sym->lower();
            case variable_attribute_type::UB:
                return sym->upper();
            case variable_attribute_type::PRIO:
                return sym->prio();
            default:
                throw std::invalid_argument("Error: MaingoEvaluator -- Symbol " + node->variable_name + " has unexpected attribute.");
        }
    }

    template <unsigned IDim>
    ConstraintContainer operator()(attribute_node<boolean<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported general logical expression");
        return ConstraintContainer();
    }

    Var operator()(parameter_node<real<0>>* node)
    {
        auto sym = _symbols.resolve<real<0>>(node->name);
        if (!sym) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Symbol " + node->name + " has unexpected type");
        }
        return dispatch(sym);
    }


    ConstraintContainer operator()(parameter_node<boolean<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported general logical expression");
        return ConstraintContainer();
    }


    template <unsigned IDim>
    tensor<Var, IDim> operator()(parameter_symbol<real<IDim>>* sym)
    {
        tensor<Var, IDim> result(sym->m_value.shape());
        result.ref().assign(sym->m_value);
        return result;
    }


    Var operator()(parameter_symbol<real<0>>* sym)
    {
        return sym->m_value;
    }


    template <unsigned IDim>
    tensor<Var, IDim> operator()(variable_symbol<real<IDim>>* sym)
    {
        tensor<Var, IDim> result(sym->shape());
        size_t indexes[IDim];
        for (int i = 0; i < IDim; ++i) {
            indexes[i] = 0;
        }
        int position = _positions.at(sym->m_name);
        while (indexes[0] < result.shape(0)) {
            result[indexes] = _variables[position];
            ++position;
            for (int i = IDim - 1; i >= 0; --i) {
                if (++indexes[i] < sym->shape(i)) {
                    break;
                }
                else if (i != 0) {
                    indexes[i] = 0;
                }
            }
        }
        return result;
    }


    Var operator()(variable_symbol<real<0>>* sym)
    {
        return _variables[_positions.at(sym->m_name)];
    }

    template <unsigned IDim>
    tensor<Var, IDim> operator()(expression_symbol<real<IDim>>* sym)
    {
        return dispatch(sym->m_value.get());
    }

    Var operator()(expression_symbol<real<0>>* sym)
    {
        return dispatch(sym->m_value.get());
    }


    ConstraintContainer operator()(expression_symbol<boolean<0>>* sym)
    {
        return dispatch(sym->m_value.get());
    }

    template <unsigned IDim>
    tensor<Var, IDim> dispatch(function_symbol<real<IDim>>* sym)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Used unsupported dispatch");
    }


    Var dispatch(function_symbol<real<0>>* sym)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Used unsupported dispatch");
    }
    template <unsigned IDim>
    std::string getBaseIdentifier(entry_node<real<IDim>>* node)
    {
        auto child_node = dynamic_cast<entry_node<real<IDim + 1>>*>(node->template get_child<0>());
        if (child_node == nullptr) {
            return expression_to_string(node->template get_child<0>());
        }
        return getBaseIdentifier(child_node);
    }

    std::string getBaseIdentifier(entry_node<real<LIBALE_MAX_DIM - 1>>* node)
    {
        return expression_to_string(node->template get_child<0>());
    }

    // non-terminal visits
    template <unsigned IDim>
    tensor<Var, IDim> operator()(entry_node<real<IDim>>* node)
    {
        auto tensor       = dispatch(node->template get_child<0>());
        auto access_index = dispatch(node->template get_child<1>());
        if (1 > access_index || access_index > tensor.shape(0)) {
            std::string name    = getBaseIdentifier(node);
            std::string err_msg = "Dimension access violation in tensor \"" + name + "\": index " + std::to_string(access_index) + " is out of bounds";
            size_t access_dim;
            std::vector<size_t> para_sizes;
            std::ostringstream sizes_str;
            try {
                para_sizes = get_parameter_shape(name, _symbols);
                access_dim = para_sizes.size() - IDim;
                if (!para_sizes.empty()) {
                    std::copy(para_sizes.begin(), para_sizes.end() - 1, std::ostream_iterator<size_t>(sizes_str, ", "));
                    sizes_str << para_sizes.back();
                }
                err_msg += " at access dimension " + std::to_string(access_dim) + ". tensor dimension is {" + sizes_str.str() + "}.";
            }
            catch (std::invalid_argument& e) {
                sizes_str << tensor.shape(0);
                err_msg += ". tensor dimension at access is {" + sizes_str.str() + "}.";
            }
            throw std::invalid_argument(err_msg);
        }
        return tensor[access_index - 1];
    }


    Var operator()(entry_node<real<0>>* node)
    {
        auto tensor       = dispatch(node->template get_child<0>());
        auto access_index = dispatch(node->template get_child<1>());
        if (1 > access_index || access_index > tensor.shape(0)) {
            std::string name    = getBaseIdentifier(node);
            std::string err_msg = "Dimension access violation in tensor \"" + name + "\": index " + std::to_string(access_index) + " is out of bounds";
            size_t access_dim;
            std::vector<size_t> para_sizes;
            std::ostringstream sizes_str;
            try {
                para_sizes = get_parameter_shape(name, _symbols);
                access_dim = para_sizes.size() - (tensor.shape().size() - 1);
                if (!para_sizes.empty()) {
                    std::copy(para_sizes.begin(), para_sizes.end() - 1, std::ostream_iterator<size_t>(sizes_str, ", "));
                    sizes_str << para_sizes.back();
                }
                err_msg += " at access dimension " + std::to_string(access_dim) + ". tensor dimension is {" + sizes_str.str() + "}.";
            }
            catch (std::invalid_argument& e) {
                sizes_str << tensor.shape(0);
                err_msg += ". tensor dimension at access is {" + sizes_str.str() + "}.";
            }
            throw std::invalid_argument(err_msg);
        }
        return tensor[access_index - 1];
    }

	ConstraintContainer	operator()(entry_node<boolean<0>>* node)
	{
		throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported general logical expression");
		return ConstraintContainer();
	}

    template <unsigned IDim>
    tensor<Var, IDim> operator()(function_node<real<IDim>>* node)
    {
        return evaluate_function(*this, node, _symbols);
    }

    Var operator()(function_node<real<0>>* node)
    {
        return evaluate_function(*this, node, _symbols);
    }

    ConstraintContainer operator()(function_node<boolean<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported function_node expression");
        return ConstraintContainer();
    }

    tensor<Var, 1> operator()(tensor_node<real<1>>* node)
    {
        size_t shape[1];
        std::vector<Var> entries;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {    //evaluate Var-children of tensor in their dimension (one lower)
            Var child = dispatch(it->get());
            entries.push_back(child);
        }
        shape[0]               = entries.size();
        tensor_ref<Var, 1> res = tensor<Var, 1>(shape).ref();    //put evaluated entries in result-tensor
        for (int i = 0; i < entries.size(); ++i) {
            res[i] = entries[i];
        }
        tensor<Var, 1> result(res.shape());
        result.ref().assign(res);
        return result;
    }

    template <unsigned IDim>
    tensor<Var, IDim> operator()(tensor_node<real<IDim>>* node)
    {
        size_t shape[IDim];
        for (int i = 0; i < IDim; ++i) {
            shape[i] = 0;
        }
        std::vector<tensor<Var, IDim - 1>> entries;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {    //evaluate 'children' of tensor in their dimension (one lower)
            tensor<Var, IDim - 1> child = dispatch(it->get());
            if (it == node->children.begin()) {
                for (int i = 1; i < IDim; ++i) {
                    shape[i] = child.shape(i - 1);
                }
            }
            if (it != node->children.begin()) {    //check for the right shape
                for (int i = 1; i < IDim; ++i) {
                    if (shape[i] != child.shape(i - 1)) {
                        throw std::invalid_argument("different shapes in tensor_node");
                    }
                }
            }
            entries.push_back(child);
        }
        shape[0]                  = entries.size();
        tensor_ref<Var, IDim> res = tensor<Var, IDim>(shape).ref();    //put evaluated entries in result-tensor
        for (int i = 0; i < entries.size(); ++i) {
            res[i].assign(entries[i]);
        }
        tensor<Var, IDim> result(res.shape());
        result.ref().assign(res);
        return result;
    }

    template <unsigned IDim>
    tensor<Var, 1> operator()(vector_node<real<IDim>>* node)
    {
        auto res = util::evaluate_expression(node, _symbols);
        tensor<Var, 1> result(res.shape());
        result.ref().assign(res);
        return result;
    }

    tensor<Var, 1> operator()(vector_node<real<0>>* node)
    {
        size_t dim[1]    = {1};
        using basic_type = typename real<0>::basic_type;
        Var child        = dispatch(node->template get_child<0>());
        std::array<size_t, 1> shape;
        shape[0] = 1;
        tensor<Var, 1> result(shape, child);
        return result;
    }

    template <unsigned IDim>
    tensor<Var, IDim> operator()(index_shift_node<real<IDim>>* node)
    {
        auto res = util::evaluate_expression(node, _symbols);
        tensor<Var, IDim> result(res.shape());
        result.ref().assign(res);
        return result;
    }


    Var operator()(index_to_real_node* node)
    {
        int value = dispatch(node->get_child<0>());
        return (double)value;
    }


    Var operator()(real_to_index_node* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported real_to_index_node");
    }


    Var operator()(round_node* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported round_node");
    }


    Var operator()(minus_node* node)
    {
        return -dispatch(node->get_child<0>());
    }


    Var operator()(inverse_node* node)
    {
        return 1 / dispatch(node->get_child<0>());
    }


    Var operator()(addition_node* node)
    {
        Var result = 0;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            result += dispatch(it->get());
        }
        return result;
    }

    
    
    Var operator()(single_neuron_node* node)
    {
        std::vector<Var> vars;
        std::vector<double> weights;
		double bias;
		int type;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            if (distance(node->children.begin(), it) < (int)(node->children.size() / 2 - 1)) {
                vars.emplace_back(dispatch(it->get()));
            }
			else if (distance(node->children.begin(), it) == (int)(node->children.size()) - 2) {
				bias = dispatch(it->get()).num().val();
			}
			else if (distance(node->children.begin(), it) == (int)(node->children.size()) - 1) {
				type = dispatch(it->get()).num().val();
			}
            else {
                if (!dispatch(it->get()).cst()) {
                    throw MAiNGOException("  MaingoEvaluator -- Error: The " + std::to_string(distance(node->children.begin(), it)) + "-th coefficient in single_neuron is not a constant");
                }
                weights.emplace_back(dispatch(it->get()).num().val());
            }
        }

        return mc::single_neuron(vars, weights, bias, type);
    }
    


    Var operator()(sum_div_node* node)
    {
        if (node->children.size() % 2 == 0) {
            throw MAiNGOException("  Error: MaingoEvaluator --  Called sum_div with even number of arguments");
        }
        if (node->children.size() < 3) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Called sum_div with less than 3 arguments");
        }
        std::vector<Var> vars;
        std::vector<double> coeff;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            if (distance(node->children.begin(), it) < (int)(node->children.size() / 2)) {
                vars.emplace_back(dispatch(it->get()));
            }
            else {
                if (!dispatch(it->get()).cst()) {
                    throw MAiNGOException("  MaingoEvaluator -- Error: The " + std::to_string(distance(node->children.begin(), it)) + "-th coefficient in sum_div is not a constant");
                }
                coeff.emplace_back(dispatch(it->get()).num().val());
            }
        }
        return mc::sum_div(vars, coeff);
    }


    Var operator()(xlog_sum_node* node)
    {
        if (!(node->children.size() % 2 == 0)) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Called xlog_sum with odd number of arguments");
        }
        if (node->children.size() < 2) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Called xlog_sum with less than 2 arguments");
        }
        std::vector<Var> vars;
        std::vector<double> coeff;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            if (distance(node->children.begin(), it) < (int)(node->children.size() / 2)) {
                vars.emplace_back(dispatch(it->get()));
            }
            else {
                if (!dispatch(it->get()).cst()) {
                    throw MAiNGOException("  Error: MaingoEvaluator -- The " + std::to_string(distance(node->children.begin(), it)) + "-th coefficient in xlog_sum is not a constant");
                }
                coeff.emplace_back(dispatch(it->get()).num().val());
            }
        }
        return mc::xlog_sum(vars, coeff);
    }


    Var operator()(multiplication_node* node)
    {
        Var result = 1;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            result *= dispatch(it->get());
        }
        return result;
    }


    Var operator()(exponentiation_node* node)
    {
        Var result = 1;
        for (auto it = node->children.rbegin(); it != node->children.rend(); ++it) {
            result = pow(dispatch(it->get()),
                         result);
        }
        return result;
    }


    Var operator()(min_node* node)
    {
        if (node->children.size() == 0) {
            throw MAiNGOException("  Error: MaingoEvaluator --  Called min without arguments");
        }
        auto it    = node->children.begin();
        Var result = dispatch(it->get());
        it++;
        for (; it != node->children.end(); ++it) {
            result = mc::min(dispatch(it->get()),
                             result);
        }
        return result;
    }


    Var operator()(max_node* node)
    {
        if (node->children.size() == 0) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Called max without arguments");
        }
        auto it    = node->children.begin();
        Var result = dispatch(it->get());
        it++;
        for (; it != node->children.end(); ++it) {
            result = mc::max(dispatch(it->get()),
                             result);
        }
        return result;
    }


    template <typename TType>
    Var operator()(set_min_node<TType>* node)
    {
        auto elements = dispatch(node->template get_child<0>());
        _symbols.push_scope();
        if (elements.begin() == elements.end()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Called set_min with empty set");
        }
        auto it = elements.begin();
        _symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
        Var result = dispatch(node->template get_child<1>());
        ++it;
        for (; it != elements.end(); ++it) {
            _symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            result = mc::min(dispatch(node->template get_child<1>()),
                             result);
        }
        _symbols.pop_scope();
        return result;
    }


    template <typename TType>
    Var operator()(set_max_node<TType>* node)
    {
        auto elements = dispatch(node->template get_child<0>());
        _symbols.push_scope();
        if (elements.begin() == elements.end()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Called set_max with empty set");
        }
        auto it = elements.begin();
        _symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
        Var result = dispatch(node->template get_child<1>());
        ++it;
        for (; it != elements.end(); ++it) {
            _symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            result = mc::max(dispatch(node->template get_child<1>()),
                             result);
        }
        _symbols.pop_scope();
        return result;
    }


    Var operator()(exp_node* node)
    {
        return exp(dispatch(node->get_child<0>()));
    }


    Var operator()(log_node* node)
    {
        return log(dispatch(node->get_child<0>()));
    }


    Var operator()(sqrt_node* node)
    {
        return sqrt(dispatch(node->get_child<0>()));
    }


    Var operator()(sin_node* node)
    {
        return sin(dispatch(node->get_child<0>()));
    }


    Var operator()(asin_node* node)
    {
        return asin(dispatch(node->get_child<0>()));
    }


    Var operator()(cos_node* node)
    {
        return cos(dispatch(node->get_child<0>()));
    }


    Var operator()(acos_node* node)
    {
        return acos(dispatch(node->get_child<0>()));
    }


    Var operator()(tan_node* node)
    {
        return tan(dispatch(node->get_child<0>()));
    }


    Var operator()(atan_node* node)
    {
        return atan(dispatch(node->get_child<0>()));
    }


    Var operator()(lmtd_node* node)
    {
        return mc::lmtd(dispatch(node->get_child<0>()),
                        dispatch(node->get_child<1>()));
    }


    Var operator()(xexpax_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in xexpax is not a constant");
        }
        return mc::xexpax(dispatch(node->get_child<0>()),
                          dispatch(node->get_child<1>()).num().val());
    }


    Var operator()(arh_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in arh is not a constant");
        }
        return mc::Op<mc::FFVar>::arh(dispatch(node->get_child<0>()),
                                      dispatch(node->get_child<1>()).num().val());
    }


    Var operator()(lb_func_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in lb_func is not a constant");
        }
        return mc::lb_func(dispatch(node->get_child<0>()),
                           dispatch(node->get_child<1>()).num().val());
    }


    Var operator()(ub_func_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in ub_func is not a constant");
        }
        return mc::ub_func(dispatch(node->get_child<0>()),
                           dispatch(node->get_child<1>()).num().val());
    }


    Var operator()(bounding_func_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in bounding_func is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in bounding_func is not a constant");
        }
        return mc::bounding_func(dispatch(node->get_child<0>()),
                                 dispatch(node->get_child<1>()).num().val(),
                                 dispatch(node->get_child<2>()).num().val());
    }


    Var operator()(ale::squash_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in squash_node is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in squash_node is not a constant");
        }
        return mc::squash_node(dispatch(node->get_child<0>()),
                               dispatch(node->get_child<1>()).num().val(),
                               dispatch(node->get_child<2>()).num().val());
    }


    Var operator()(ale::af_lcb_node* node)
    {
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in af_lcb_node is not a constant");
        }
        return mc::acquisition_function(dispatch(node->get_child<0>()),
                                        dispatch(node->get_child<1>()),
                                        1,
                                        dispatch(node->get_child<2>()).num().val());
    }


    Var operator()(ale::af_ei_node* node)
    {
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in af_ei_node is not a constant");
        }
        return mc::acquisition_function(dispatch(node->get_child<0>()),
                                        dispatch(node->get_child<1>()),
                                        2,
                                        dispatch(node->get_child<2>()).num().val());
    }


    Var operator()(ale::af_pi_node* node)
    {
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in af_pi_node is not a constant");
        }
        return mc::acquisition_function(dispatch(node->get_child<0>()),
                                        dispatch(node->get_child<1>()),
                                        3,
                                        dispatch(node->get_child<2>()).num().val());
    }


    Var operator()(ale::regnormal_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in regnormal_node is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in regnormal_node is not a constant");
        }
        return mc::regnormal(dispatch(node->get_child<0>()),
                             dispatch(node->get_child<1>()).num().val(),
                             dispatch(node->get_child<2>()).num().val());
    }


    Var operator()(ext_antoine_psat_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in ext_antoine_psat is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in ext_antoine_psat is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in ext_antoine_psat is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in ext_antoine_psat is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in ext_antoine_psat is not a constant");
        }
        if (!dispatch(node->get_child<6>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p6 in ext_antoine_psat is not a constant");
        }
        if (!dispatch(node->get_child<7>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p7 in ext_antoine_psat is not a constant");
        }
        // ext_antoine_psat = type 1
        return mc::vapor_pressure(dispatch(node->get_child<0>()),
                                  1,
                                  dispatch(node->get_child<1>()).num().val(),
                                  dispatch(node->get_child<2>()).num().val(),
                                  dispatch(node->get_child<3>()).num().val(),
                                  dispatch(node->get_child<4>()).num().val(),
                                  dispatch(node->get_child<5>()).num().val(),
                                  dispatch(node->get_child<6>()).num().val(),
                                  dispatch(node->get_child<7>()).num().val());
    }


    Var operator()(antoine_psat_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in antoine_psat is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in antoine_psat is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in antoine_psat is not a constant");
        }
        // antoine_psat = type 2
        return mc::vapor_pressure(dispatch(node->get_child<0>()),
                                  2,
                                  dispatch(node->get_child<1>()).num().val(),
                                  dispatch(node->get_child<2>()).num().val(),
                                  dispatch(node->get_child<3>()).num().val());
    }


    Var operator()(wagner_psat_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in wagner_psat is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in wagner_psat is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in wagner_psat is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in wagner_psat is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in wagner_psat is not a constant");
        }
        if (!dispatch(node->get_child<6>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p6 in wagner_psat is not a constant");
        }
        // wagner_psat = type 3
        return mc::vapor_pressure(dispatch(node->get_child<0>()),
                                  3,
                                  dispatch(node->get_child<1>()).num().val(),
                                  dispatch(node->get_child<2>()).num().val(),
                                  dispatch(node->get_child<3>()).num().val(),
                                  dispatch(node->get_child<4>()).num().val(),
                                  dispatch(node->get_child<5>()).num().val(),
                                  dispatch(node->get_child<6>()).num().val());
    }


    Var operator()(ik_cape_psat_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<6>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p6 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<7>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p7 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<8>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p8 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<9>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p9 in ik_cape_psat is not a constant");
        }
        if (!dispatch(node->get_child<10>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p10 in ik_cape_psat is not a constant");
        }
        // ik_cape_psat = type 4
        return mc::vapor_pressure(dispatch(node->get_child<0>()),
                                  4,
                                  dispatch(node->get_child<1>()).num().val(),
                                  dispatch(node->get_child<2>()).num().val(),
                                  dispatch(node->get_child<3>()).num().val(),
                                  dispatch(node->get_child<4>()).num().val(),
                                  dispatch(node->get_child<5>()).num().val(),
                                  dispatch(node->get_child<6>()).num().val(),
                                  dispatch(node->get_child<7>()).num().val(),
                                  dispatch(node->get_child<8>()).num().val(),
                                  dispatch(node->get_child<9>()).num().val(),
                                  dispatch(node->get_child<10>()).num().val());
    }


    Var operator()(aspen_hig_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in aspen_hig is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in aspen_hig is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in aspen_hig is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in aspen_hig is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in aspen_hig is not a constant");
        }
        if (!dispatch(node->get_child<6>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p6 in aspen_hig is not a constant");
        }
        if (!dispatch(node->get_child<7>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p7 in aspen_hig is not a constant");
        }
        // aspen_hig = type 1
        return mc::ideal_gas_enthalpy(dispatch(node->get_child<0>()),
                                      dispatch(node->get_child<1>()).num().val(),
                                      1,
                                      dispatch(node->get_child<2>()).num().val(),
                                      dispatch(node->get_child<3>()).num().val(),
                                      dispatch(node->get_child<4>()).num().val(),
                                      dispatch(node->get_child<5>()).num().val(),
                                      dispatch(node->get_child<6>()).num().val(),
                                      dispatch(node->get_child<7>()).num().val());
    }


    Var operator()(nasa9_hig_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in nasa9_hig is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in nasa9_hig is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in nasa9_hig is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in nasa9_hig is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in nasa9_hig is not a constant");
        }
        if (!dispatch(node->get_child<6>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p6 in nasa9_hig is not a constant");
        }
        if (!dispatch(node->get_child<7>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p7 in nasa9_hig is not a constant");
        }
        if (!dispatch(node->get_child<8>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p8 in nasa9_hig is not a constant");
        }
        // nasa9_hig = type 2
        return mc::ideal_gas_enthalpy(dispatch(node->get_child<0>()),
                                      dispatch(node->get_child<1>()).num().val(),
                                      2,
                                      dispatch(node->get_child<2>()).num().val(),
                                      dispatch(node->get_child<3>()).num().val(),
                                      dispatch(node->get_child<4>()).num().val(),
                                      dispatch(node->get_child<5>()).num().val(),
                                      dispatch(node->get_child<6>()).num().val(),
                                      dispatch(node->get_child<7>()).num().val(),
                                      dispatch(node->get_child<8>()).num().val());
    }


    Var operator()(dippr107_hig_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in dippr107_hig is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in dippr107_hig is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in dippr107_hig is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in dippr107_hig is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in dippr107_hig is not a constant");
        }
        if (!dispatch(node->get_child<6>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p6 in dippr107_hig is not a constant");
        }
        // dippr107_hig_node = type 3
        return mc::ideal_gas_enthalpy(dispatch(node->get_child<0>()),
                                      dispatch(node->get_child<1>()).num().val(),
                                      3,
                                      dispatch(node->get_child<2>()).num().val(),
                                      dispatch(node->get_child<3>()).num().val(),
                                      dispatch(node->get_child<4>()).num().val(),
                                      dispatch(node->get_child<5>()).num().val(),
                                      dispatch(node->get_child<6>()).num().val());
    }


    Var operator()(dippr127_hig_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in dippr127_hig is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in dippr127_hig is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in dippr127_hig is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in dippr127_hig is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in dippr127_hig is not a constant");
        }
        if (!dispatch(node->get_child<6>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p6 in dippr127_hig is not a constant");
        }
        if (!dispatch(node->get_child<7>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p7 in dippr127_hig is not a constant");
        }
        if (!dispatch(node->get_child<8>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p8 in dippr127_hig is not a constant");
        }
        // dippr127_hig = type 4
        return mc::ideal_gas_enthalpy(dispatch(node->get_child<0>()),
                                      dispatch(node->get_child<1>()).num().val(),
                                      4,
                                      dispatch(node->get_child<2>()).num().val(),
                                      dispatch(node->get_child<3>()).num().val(),
                                      dispatch(node->get_child<4>()).num().val(),
                                      dispatch(node->get_child<5>()).num().val(),
                                      dispatch(node->get_child<6>()).num().val(),
                                      dispatch(node->get_child<7>()).num().val(),
                                      dispatch(node->get_child<8>()).num().val());
    }


    Var operator()(antoine_tsat_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in antoine_tsat is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in antoine_tsat is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in antoine_tsat is not a constant");
        }
        // antoine_tsat = type 2
        return mc::saturation_temperature(dispatch(node->get_child<0>()),
                                          2,
                                          dispatch(node->get_child<1>()).num().val(),
                                          dispatch(node->get_child<2>()).num().val(),
                                          dispatch(node->get_child<3>()).num().val());
    }


    Var operator()(watson_dhvap_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in watson_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in watson_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in watson_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in watson_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in watson_dhvap is not a constant");
        }
        // watson_dhvap = type 1
        return mc::enthalpy_of_vaporization(dispatch(node->get_child<0>()),
                                            1,
                                            dispatch(node->get_child<1>()).num().val(),
                                            dispatch(node->get_child<2>()).num().val(),
                                            dispatch(node->get_child<3>()).num().val(),
                                            dispatch(node->get_child<4>()).num().val(),
                                            dispatch(node->get_child<5>()).num().val());
    }


    Var operator()(dippr106_dhvap_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in dippr106_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in dippr106_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in dippr106_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p4 in dippr106_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p5 in dippr106_dhvap is not a constant");
        }
        if (!dispatch(node->get_child<6>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p6 in dippr106_dhvap is not a constant");
        }
        // dippr106_dhvap = type 2
        return mc::enthalpy_of_vaporization(dispatch(node->get_child<0>()),
                                            2,
                                            dispatch(node->get_child<1>()).num().val(),
                                            dispatch(node->get_child<2>()).num().val(),
                                            dispatch(node->get_child<3>()).num().val(),
                                            dispatch(node->get_child<4>()).num().val(),
                                            dispatch(node->get_child<5>()).num().val(),
                                            dispatch(node->get_child<6>()).num().val());
    }


    Var operator()(cost_turton_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p1 in cost_turton is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p2 in cost_turton is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Parameter p3 in cost_turton is not a constant");
        }
        // cost_turton = type 1
        return mc::cost_function(dispatch(node->get_child<0>()),
                                 1,
                                 dispatch(node->get_child<1>()).num().val(),
                                 dispatch(node->get_child<2>()).num().val(),
                                 dispatch(node->get_child<3>()).num().val());
    }


    Var operator()(covar_matern_1_node* node)
    {
        // covar_matern_1 = type 1
        return mc::covariance_function(dispatch(node->get_child<0>()),
                                       1);
    }


    Var operator()(covar_matern_3_node* node)
    {
        // covar_matern_3 = type 2
        return mc::covariance_function(dispatch(node->get_child<0>()),
                                       2);
    }


    Var operator()(covar_matern_5_node* node)
    {
        // covar_matern_5 = type 3
        return mc::covariance_function(dispatch(node->get_child<0>()),
                                       3);
    }


    Var operator()(covar_sqrexp_node* node)
    {
        // covar_sqrexp = type 4
        return mc::covariance_function(dispatch(node->get_child<0>()),
                                       4);
    }


    Var operator()(gpdf_node* node)
    {
        return mc::gaussian_probability_density_function(dispatch(node->get_child<0>()));
    }


    Var operator()(nrtl_tau_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in nrtl_tau is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in nrtl_tau is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fourth argument in nrtl_tau is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fifth argument in nrtl_tau is not a constant");
        }
        return nrtl_subroutine_tau(dispatch(node->get_child<0>()),
                                   dispatch(node->get_child<1>()).num().val(),
                                   dispatch(node->get_child<2>()).num().val(),
                                   dispatch(node->get_child<3>()).num().val(),
                                   dispatch(node->get_child<4>()).num().val());
    }


    Var operator()(nrtl_dtau_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in nrtl_dtau is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in nrtl_dtau is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fourth argument in nrtl_dtau is not a constant");
        }
        return nrtl_subroutine_dtau(dispatch(node->get_child<0>()),
                                    dispatch(node->get_child<1>()).num().val(),
                                    dispatch(node->get_child<2>()).num().val(),
                                    dispatch(node->get_child<3>()).num().val());
    }


    Var operator()(nrtl_g_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in nrtl_g is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in nrtl_g is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fourth argument in nrtl_g is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fifth argument in nrtl_g is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Sixth argument in nrtl_g is not a constant");
        }
        return nrtl_subroutine_G(dispatch(node->get_child<0>()),
                                 dispatch(node->get_child<1>()).num().val(),
                                 dispatch(node->get_child<2>()).num().val(),
                                 dispatch(node->get_child<3>()).num().val(),
                                 dispatch(node->get_child<4>()).num().val(),
                                 dispatch(node->get_child<5>()).num().val());
    }


    Var operator()(nrtl_gtau_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in nrtl_gtau is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in nrtl_gtau is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fourth argument in nrtl_gtau is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fifth argument in nrtl_gtau is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Sixth argument in nrtl_gtau is not a constant");
        }
        return nrtl_subroutine_Gtau(dispatch(node->get_child<0>()),
                                    dispatch(node->get_child<1>()).num().val(),
                                    dispatch(node->get_child<2>()).num().val(),
                                    dispatch(node->get_child<3>()).num().val(),
                                    dispatch(node->get_child<4>()).num().val(),
                                    dispatch(node->get_child<5>()).num().val());
    }


    Var operator()(nrtl_gdtau_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in nrtl_gdtau is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in nrtl_gdtau is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fourth argument in nrtl_gdtau is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fifth argument in nrtl_gdtau is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Sixth argument in nrtl_gdtau is not a constant");
        }
        return nrtl_subroutine_Gdtau(dispatch(node->get_child<0>()),
                                     dispatch(node->get_child<1>()).num().val(),
                                     dispatch(node->get_child<2>()).num().val(),
                                     dispatch(node->get_child<3>()).num().val(),
                                     dispatch(node->get_child<4>()).num().val(),
                                     dispatch(node->get_child<5>()).num().val());
    }

    Var operator()(nrtl_dgtau_node* node)
    {
        if (!dispatch(node->get_child<1>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Second argument in nrtl_dgtau is not a constant");
        }
        if (!dispatch(node->get_child<2>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Third argument in nrtl_dgtau is not a constant");
        }
        if (!dispatch(node->get_child<3>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fourth argument in nrtl_dgtau is not a constant");
        }
        if (!dispatch(node->get_child<4>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Fifth argument in nrtl_dgtau is not a constant");
        }
        if (!dispatch(node->get_child<5>()).cst()) {
            throw MAiNGOException("  Error: MaingoEvaluator -- Sixth argument in nrtl_dgtau is not a constant");
        }
        return nrtl_subroutine_dGtau(dispatch(node->get_child<0>()),
                                     dispatch(node->get_child<1>()).num().val(),
                                     dispatch(node->get_child<2>()).num().val(),
                                     dispatch(node->get_child<3>()).num().val(),
                                     dispatch(node->get_child<4>()).num().val(),
                                     dispatch(node->get_child<5>()).num().val());
    }


    Var operator()(norm2_node* node)
    {
        return mc::euclidean_norm_2d(dispatch(node->get_child<0>()),
                                     dispatch(node->get_child<1>()));
    }


    Var operator()(abs_node* node)
    {
        return mc::fabs(dispatch(node->get_child<0>()));
    }


    Var operator()(xabsx_node* node)
    {
        return mc::fabsx_times_x(dispatch(node->get_child<0>()));
    }


    Var operator()(xlogx_node* node)
    {
        return mc::xlog(dispatch(node->get_child<0>()));
    }


    Var operator()(cosh_node* node)
    {
        return mc::cosh(dispatch(node->get_child<0>()));
    }


    Var operator()(sinh_node* node)
    {
        return mc::sinh(dispatch(node->get_child<0>()));
    }


    Var operator()(tanh_node* node)
    {
        return mc::tanh(dispatch(node->get_child<0>()));
    }


    Var operator()(coth_node* node)
    {
        return mc::coth(dispatch(node->get_child<0>()));
    }


    Var operator()(acosh_node* node)
    {
        return mc::Op<mc::FFVar>::acosh(dispatch(node->get_child<0>()));
    }


    Var operator()(asinh_node* node)
    {
        return mc::Op<mc::FFVar>::asinh(dispatch(node->get_child<0>()));
    }


    Var operator()(atanh_node* node)
    {
        return mc::Op<mc::FFVar>::atanh(dispatch(node->get_child<0>()));
    }


    Var operator()(acoth_node* node)
    {
        return mc::Op<mc::FFVar>::acoth(dispatch(node->get_child<0>()));
    }


    Var operator()(erf_node* node)
    {
        return mc::erf(dispatch(node->get_child<0>()));
    }


    Var operator()(erfc_node* node)
    {
        return mc::erfc(dispatch(node->get_child<0>()));
    }


    Var operator()(pos_node* node)
    {
        return mc::pos(dispatch(node->get_child<0>()));
    }


    Var operator()(neg_node* node)
    {
        return mc::neg(dispatch(node->get_child<0>()));
    }


    Var operator()(rlmtd_node* node)
    {
        return mc::rlmtd(dispatch(node->get_child<0>()),
                         dispatch(node->get_child<1>()));
    }


    Var operator()(xexpy_node* node)
    {
        return mc::expx_times_y(dispatch(node->get_child<1>()),
                                dispatch(node->get_child<0>()));
    }


    Var operator()(schroeder_ethanol_p_node* node)
    {
        return mc::p_sat_ethanol_schroeder(dispatch(node->get_child<0>()));
    }


    Var operator()(schroeder_ethanol_rhovap_node* node)
    {
        return mc::rho_vap_sat_ethanol_schroeder(dispatch(node->get_child<0>()));
    }


    Var operator()(schroeder_ethanol_rholiq_node* node)
    {
        return mc::rho_liq_sat_ethanol_schroeder(dispatch(node->get_child<0>()));
    }


    Var operator()(mid_node* node)
    {
        Var arg1 = dispatch(node->get_child<0>());
        Var arg2 = dispatch(node->get_child<1>());
        Var arg3 = dispatch(node->get_child<2>());
        return mc::min(mc::max(arg1, arg2), mc::min(mc::max(arg2, arg3), mc::max(arg3, arg1)));
    }


    template <typename TType>
    Var operator()(sum_node<TType>* node)
    {
        auto elements = dispatch(node->template get_child<0>());
        if (elements.begin() == elements.end()) {
            std::cout << "called sum with emtpy set (by convention equals 0)\n";
        }
        _symbols.push_scope();
        Var result = 0;
        for (auto it = elements.begin(); it != elements.end(); ++it) {
            _symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            result += dispatch(node->template get_child<1>());
        }
        _symbols.pop_scope();
        return result;
    }


    template <typename TType>
    Var operator()(product_node<TType>* node)
    {
        auto elements = dispatch(node->template get_child<0>());
        if (elements.begin() == elements.end()) {
            std::cout << "called product with emtpy set (by convention equals 1)\n";
        }
        _symbols.push_scope();
        Var result = 1;
        for (auto it = elements.begin(); it != elements.end(); ++it) {
            _symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            result *= dispatch(node->template get_child<1>());
        }
        _symbols.pop_scope();
        return result;
    }


    ConstraintContainer operator()(negation_node* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported negation expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(equal_node<real<0>>* node)
    {
        ConstraintContainer result;
        result.eq.push_back(dispatch(node->get_child<0>()) - dispatch(node->get_child<1>()));
        return result;
    }


    ConstraintContainer operator()(less_node<real<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported strict inequality expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(less_equal_node<real<0>>* node)
    {
        ConstraintContainer result;
        result.ineq.push_back(dispatch(node->get_child<0>()) - dispatch(node->get_child<1>()));
        return result;
    }


    ConstraintContainer operator()(greater_node<real<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported strict inequality expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(greater_equal_node<real<0>>* node)
    {
        ConstraintContainer result;
        result.ineq.push_back(dispatch(node->get_child<1>()) - dispatch(node->get_child<0>()));
        return result;
    }


    ConstraintContainer operator()(equal_node<ale::index<0>>* node)
    {
        throw MAiNGOException(" Error: MaingoEvaluator -- Evaluated unsupported index comparison expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(less_node<ale::index<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported index comparison expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(less_equal_node<ale::index<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported index comparison expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(greater_node<ale::index<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported index comparison expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(greater_equal_node<ale::index<0>>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported index comparison expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(disjunction_node* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported disjunction expression");
        return ConstraintContainer();
    }


    ConstraintContainer operator()(conjunction_node* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported conjunction expression");
        return ConstraintContainer();
    }

    template <typename TType>
    ConstraintContainer operator()(element_node<TType>* node)
    {
        throw MAiNGOException("  Error: MaingoEvaluator -- Evaluated unsupported general logical expression");
        return ConstraintContainer();
    };


    template <typename TType>
    ConstraintContainer operator()(forall_node<TType>* node)
    {
        ConstraintContainer result;
        auto elements = dispatch(node->template get_child<0>());
        _symbols.push_scope();
        for (auto it = elements.begin(); it != elements.end(); ++it) {
            _symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            auto cons = dispatch(node->template get_child<1>());
            result.eq.insert(result.eq.end(), cons.eq.begin(), cons.eq.end());
            result.ineq.insert(result.ineq.end(), cons.ineq.begin(), cons.ineq.end());
        }
        _symbols.pop_scope();
        return result;
    }
    /**@*/

  private:
    symbol_table& _symbols;                                 /*< symbol_table for symbol lookup*/
    const std::vector<Var>& _variables;                     /*< MAiNGO variable vector*/
    const std::unordered_map<std::string, int>& _positions; /*< ALE symbol positions in MAiNGO variable vector*/
};


}    // namespace maingo

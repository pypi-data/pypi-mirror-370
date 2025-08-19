/**********************************************************************************
 * Copyright (c) 2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "util/evaluator.hpp"

#include <cstddef>                       // for size_t
#include <algorithm>                      // for max, min, copy
#include <array>                          // for array
#include <cmath>                          // for abs, pow, exp, log, sqrt, tanh, erf, cosh, sinh, lround, trunc, acos, acosh, asin, asinh, atan, atanh, cos, erfc
#include <iostream>                       // for operator<<, ostringstream, basic_ostream, basic_ostream<>::__ostream_type, cout, ostream
#include <iterator>                       // for distance, ostream_iterator
#include <limits>                         // for numeric_limits
#include <list>                           // for operator!=, operator==, list, _List_iterator, _List_iterator<>::_Self, list<>::iterator
#include <tuple>                          // for tuple_element<>::type
#include <type_traits>                    // for conditional_t
#include <variant>                        // for variant, visit
#include <vector>                         // for vector
#include "config.hpp"                     // for LIBALE_MAX_DIM
#include "expression.hpp"                 // for expression
#include "node.hpp"                       // for value_node_ptr, nrtl_dgt_dx_node, nrtl_gamma_node, nrtl_lngamma_node, ik_cape_psat_node, nrtl_ge_node, nrtl...
#include "symbol.hpp"                     // for parameter_symbol, expression_symbol, value_symbol, variable_symbol
#include "symbol_table.hpp"               // for symbol_table
#include "util/expression_to_string.hpp"  // for expression_to_string
#include "util/expression_utils.hpp"      // for get_parameter_shape
#include "util/nrtl_subroutines.hpp"      // for nrtl_subroutine_G, nrtl_subroutine_Gtau, nrtl_subroutine_tau, nrtl_subroutine_gamma, nrtl_subroutine_Gdtau
#include "util/visitor_utils.hpp"         // for evaluate_function, evaluate_children_tuple, evaluate_children
#include <sstream>                        // for ostringstream   
#include <stdexcept>                      // for invalid_argument

#include "node.hpp"
#include "symbol_table.hpp"
#include "expression.hpp"



namespace ale::util {

class evaluation_visitor {
public:
    evaluation_visitor(symbol_table& symbols): symbols(symbols) {};

    // TODO: dispatches can be removed once everything works using evaluate_children
    // expression dispatch
    template <typename TType>
    owning_ref<TType> dispatch(expression<TType>& expr) {
        return dispatch(expr.get());
    }

    // value_node dispatch
    template <typename TType>
    owning_ref<TType> dispatch(value_node<TType>* node) {
        return std::visit(*this, node->get_variant());
    }

    // symbol dispatch
    template <typename TType>
    owning_ref<TType> dispatch(value_symbol<TType>* sym) {
        return std::visit(*this, sym->get_value_variant());
    }

    // terminal visits
    template <typename TType>
    owning_ref<TType> operator()(constant_node<TType>* node) {
        if constexpr (get_node_dimension<TType> == 0) {
            return node->value;
        } else {
            return basic_type<TType>{node->value};
        }
    }

    template <typename TType>
    owning_ref<TType> operator()(parameter_node<TType>* node) {
        auto sym = symbols.resolve<TType>(node->name);
        if (!sym) {
            throw std::invalid_argument("symbol " + node->name + " is ill-defined");
        }
        return dispatch(sym);
    }

    template <typename TType>
    owning_ref<TType> operator()(attribute_node<TType> *node) {
        if constexpr(is_real_node<TType>) {
            variable_symbol<real<TType::dim>> *sym = cast_variable_symbol<real<TType::dim>>(symbols.resolve(node->variable_name));
            if (!sym) {
                throw std::invalid_argument("symbol " + node->variable_name + " is ill-defined");
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
                throw std::invalid_argument("unknown attribute requested for symbol: " + node->variable_name);
            }
        } else {
            throw std::invalid_argument("Attribute requested from non-real symbol: " + node->variable_name);
        }
        throw std::invalid_argument("Inconsistent behavior");
    }

    // symbol visits
    template <typename TType>
    owning_ref<TType> operator()(parameter_symbol<TType>* sym) {
        if(sym->m_is_placeholder) {
            throw uninitializedParameterException(sym->m_name);
        }
        return sym->m_value;
    }

    template <typename TType>
    owning_ref<TType> operator()(variable_symbol<TType>* sym) {
        throw std::invalid_argument("cannot evaluate variable_symbol \"" + sym->m_name + "\"");
    }

    template <typename TType>
    owning_ref<TType> operator()(expression_symbol<TType>* sym) {
        return dispatch(sym->m_value.get());
    }

	template <typename base_ttype, unsigned IDim>
	std::string getBaseIdentifier(entry_node<tensor_type<base_ttype, IDim>>* node) {
		auto child_node = dynamic_cast<entry_node<real<IDim + 1>>*>(node->template get_child<0>());
		if (child_node == nullptr) {
			return expression_to_string(node->template get_child<0>());
		}
		return getBaseIdentifier(child_node);
	}

	template <typename base_ttype>
	std::string getBaseIdentifier(entry_node<tensor_type<base_ttype, LIBALE_MAX_DIM-1>>* node) {
		return expression_to_string(node->template get_child<0>());
	}

    // non-terminal visits
	template <typename base_ttype, unsigned IDim>
    owning_ref<tensor_type<base_ttype, IDim>> operator()(entry_node<tensor_type<base_ttype, IDim>>* node) {
        auto [tensor, access_index] = evaluate_children_tuple(*this, node);
        if (1 > access_index || access_index > tensor.shape(0)) {
            std::string name = getBaseIdentifier(node);
            std::string err_msg = "Dimension access violation in tensor \"" + name + "\": index " + std::to_string(access_index) + " is out of bounds";
            size_t access_dim;
            std::vector<size_t> para_sizes;
            std::ostringstream sizes_str;
            try {
                para_sizes = get_parameter_shape(name, symbols);
                access_dim = para_sizes.size() - (tensor.shape().size() - 1);
                if (!para_sizes.empty()) {
                    std::copy(para_sizes.begin(), para_sizes.end() - 1, std::ostream_iterator<size_t>(sizes_str, ", "));
                    sizes_str << para_sizes.back();
                }
                err_msg += " at access dimension " + std::to_string(access_dim) + ". tensor dimension is {" + sizes_str.str() + "}.";
            }
            catch (std::invalid_argument& ) {
                sizes_str << tensor.shape(0);
                err_msg += ". tensor dimension at access is {" + sizes_str.str() + "}.";
            }
            throw std::invalid_argument(err_msg);
        }
        return tensor[access_index - 1];
    }

    template <typename TType>
    owning_ref<TType> operator()(tensor_node<TType>* node)  {
        auto children = evaluate_children(*this, node);

        // construct the shape of the new tensor
        std::vector<size_t> shape(get_node_dimension<TType>, 0);
        if constexpr (get_node_dimension<TType> == 1) {
            // if the new tensor has dim=1 the shape will just be the number of children
            shape.at(0) = children.size();
        } else {
            // if children.size = 0 the shape is already correct
            if (children.size() > 0) {
                // copy shape of first child to shape vector (shifted to the right by one)
                auto child0_shape = children.at(0).shape();
                for (int i = 0; i < get_node_dimension<TType> - 1; ++i) {
                    shape.at(i + 1) = child0_shape.at(i);
                }

                // assert that shape of all children is equal
                for (const auto& child: children) {
                    for (int i = 0; i < get_node_dimension<TType> - 1; ++i) {
                        if (child0_shape.at(i) != child.shape(i)) {
                            throw std::invalid_argument("different shapes in tensor_node");
                        }
                    }
                }

                // set the shape of the first dimension
                shape.at(0) = children.size();
            }
        }

        // copy the children into the combined tensor
        basic_type<TType> new_tensor(shape.data());
        for (size_t i = 0; i < children.size(); ++i) {
            if constexpr (get_node_dimension<TType> == 1) {
                new_tensor[i] = children.at(i);
            } else {
                new_tensor[i].assign(children.at(i));
            }
        }

        return new_tensor;
    }

    template <typename TType>
    owning_ref<TType> operator()(index_shift_node<TType>* node) {
        auto child = dispatch(node->template get_child<0>());
        size_t shape_res[TType::dim];
        for (int i = 0; i < TType::dim - 1; ++i) {
            shape_res[i] = child.shape(i+1);
        }
        shape_res[TType::dim - 1] = child.shape(0);
        auto res = basic_type<TType>(shape_res).ref();

        size_t indexes_child[TType::dim];
        size_t indexes_res[TType::dim];
        for (int i = 0; i < TType::dim; ++i) {
            indexes_child[i] = 0;
            indexes_res[i] = 0;
        }
        //this does:
        //res[0,0,0]=child[0,0,0]
        //res[1,0,0]=child[0,1,0]
        //res[2,0,0]=child[0,2,0]
        //res[0,1,0]=child[0,0,1]
        //res[1,1,0]=child[0,1,1]
        //res[2,1,0]=child[0,2,1]
        //...
        //res[0,0,1]=child[1,0,0]
        //...
        while(indexes_res[TType::dim - 1] < res.shape(TType::dim - 1)) {
            res[indexes_res] = child[indexes_child];
            for (int i = 0; i < TType::dim; ++i) {
                if (++indexes_res[i] < res.shape(i)) {
                    ++indexes_child[ (i+1) % TType::dim ];
                    break;
                }
                else if (i != TType::dim - 1){
                    indexes_res[i] = 0;
                    indexes_child[(i+1) % TType::dim] = 0;
                }
            }
        }
        return res;
    }

    // non-terminal real node visits
    double operator()(minus_node* node) {
        return - dispatch(node->get_child<0>());
    }

    double operator()(inverse_node* node) {
        return 1 / dispatch(node->get_child<0>());
    }

    double operator()(addition_node* node) {
        double result = 0;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            result += dispatch(it->get());
        }
        return result;
    }

    double operator()(sum_div_node* node) {
        if (node->children.size() % 2 == 0) {
            throw std::invalid_argument("called sum_div with even number of arguments");
        }
        if (node->children.size() < 3) {
            throw std::invalid_argument("called sum_div with less than 3 arguments");
        }
        std::vector<double> vars;
        std::vector<double> coeff;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            if (!(dispatch(it->get()) > 0)) {
                throw std::invalid_argument("called sum_div with non-positive argument");
            }
            if (distance(node->children.begin(), it) < (int)(node->children.size() / 2)) {
                vars.emplace_back(dispatch(it->get()));
            }
            else {
                coeff.emplace_back(dispatch(it->get()));
            }
        }
        double partial = coeff[1] * vars[0];
        for (int i = 1; i < (int)(node->children.size() / 2); ++i) {
            partial += coeff[i + 1] * vars[i];
        }
        return (coeff[0] * vars[0]) / partial;
    }

    double operator()(xlog_sum_node* node) {
        if (!(node->children.size() % 2 == 0)) {
            throw std::invalid_argument("called xlog_sum with odd number of arguments");
        }
        if (node->children.size() < 2) {
            throw std::invalid_argument("called xlog_sum with less than 2 arguments");
        }
        std::vector<double> vars;
        std::vector<double> coeff;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            if (!(dispatch(it->get()) > 0)) {
                throw std::invalid_argument("called xlog_sum with non-positive argument");
            }
            if (distance(node->children.begin(), it) < (int)(node->children.size() / 2)) {
                vars.emplace_back(dispatch(it->get()));
            }
            else {
                coeff.emplace_back(dispatch(it->get()));
            }
        }
        double partial = 0;
        for (int i = 0; i < (int)(node->children.size() / 2); ++i) {
            partial += coeff[i] * vars[i];
        }
        return vars[0] * log(partial);
    }

    
    double operator()(single_neuron_node* node) {
        if (node->children.size() < 4) {
            throw std::invalid_argument("called single_neuron with less than 4 arguments");
        }
        std::vector<double> vars;
        std::vector<double> weights;
        double result;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            if (distance(node->children.begin(), it) < (int)(node->children.size() / 2 - 1)) {
                vars.emplace_back(dispatch(it->get()));
            }
            else if (distance(node->children.begin(), it) == (int)(node->children.size()) - 2) {
                result = dispatch(it->get());
            }
            else if (distance(node->children.begin(), it) != (int)(node->children.size()) - 1) {
                weights.emplace_back(dispatch(it->get()));
            }
        }
		
        for (int i = 0; i < (int)(node->children.size() / 2); ++i) {
            result += weights[i] * vars[i];
        }
        return tanh(result);
    }

    double operator()(nrtl_tau_node* node) {
        auto [t, a, b, e, f] = evaluate_children_tuple(*this, node);
        return nrtl_subroutine_tau(t,a,b,e,f);
    }

    double operator()(nrtl_g_node* node) {
        auto [t, a, b, e, f, alpha] = evaluate_children_tuple(*this, node);
        return nrtl_subroutine_G(t, a, b, e, f, alpha);
    }

    double operator()(nrtl_gtau_node* node) {
        auto [t, a, b, e, f, alpha] = evaluate_children_tuple(*this, node);
        return nrtl_subroutine_Gtau(t, a, b, e, f, alpha);
    }

    double operator()(nrtl_dtau_node* node) {
        auto [t, b, e, f] = evaluate_children_tuple(*this, node);
        return nrtl_subroutine_dtau(t, b, e, f);
    }

    double operator()(nrtl_gdtau_node* node) {
        auto [t, a, b, e, f, alpha] = evaluate_children_tuple(*this, node);
        return nrtl_subroutine_Gdtau(t, a, b, e, f, alpha);
    }

    double operator()(nrtl_dgtau_node* node) {
        auto [t, a, b, e, f, alpha] = evaluate_children_tuple(*this, node);
        return nrtl_subroutine_dGtau(t, a, b, e, f, alpha);
    }

    double operator()(multiplication_node* node) {
        double result = 1;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            result *= dispatch(it->get());
        }
        return result;
    }

    double operator()(exponentiation_node* node) {
        double result = 1;
        for (auto it = node->children.rbegin(); it != node->children.rend(); ++it) {
            result = pow(dispatch(it->get()), result);
        }
        return result;
    }

    double operator()(min_node* node) {
        double result = std::numeric_limits<double>::infinity();
        for (auto it = node->children.rbegin(); it != node->children.rend(); ++it) {
            result = std::min(result, dispatch(it->get()));
        }
        return result;
    }

    double operator()(max_node* node) {
        double result = - std::numeric_limits<double>::infinity();
        for (auto it = node->children.rbegin(); it != node->children.rend(); ++it) {
            result = std::max(result, dispatch(it->get()));
        }
        return result;
    }

    double operator()(exp_node* node) {
        return exp(dispatch(node->get_child<0>()));
    }

    double operator()(log_node* node) {
        return log(dispatch(node->get_child<0>()));
    }

    double operator()(sqrt_node* node) {
        return sqrt(dispatch(node->get_child<0>()));
    }

    double operator()(sin_node* node) {
        return sin(dispatch(node->get_child<0>()));
    }

    double operator()(asin_node* node) {
        return asin(dispatch(node->get_child<0>()));
    }
    double operator()(cos_node* node) {
        return cos(dispatch(node->get_child<0>()));
    }

    double operator()(acos_node* node) {
        return acos(dispatch(node->get_child<0>()));
    }

    double operator()(tan_node* node) {
        return tan(dispatch(node->get_child<0>()));
    }

    double operator()(atan_node* node) {
        return atan(dispatch(node->get_child<0>()));
    }

    double operator()(xlogx_node* node) {
        double x = dispatch(node->get_child<0>());
        return x*log(x);
    }

    double operator()(abs_node* node) {
        return std::abs(dispatch(node->get_child<0>()));
    }

    double operator()(xabsx_node* node) {
        return std::abs(dispatch(node->get_child<0>()))*dispatch(node->get_child<0>());
    }

    double operator()(cosh_node* node) {
        return cosh(dispatch(node->get_child<0>()));
    }

    double operator()(sinh_node* node) {
        return sinh(dispatch(node->get_child<0>()));
    }

    double operator()(tanh_node* node) {
        return tanh(dispatch(node->get_child<0>()));
    }

    double operator()(coth_node* node) {
        return cosh(dispatch(node->get_child<0>())) / sinh(dispatch(node->get_child<0>()));
    }

    double operator()(acosh_node* node) {
        return acosh(dispatch(node->get_child<0>()));
    }

    double operator()(asinh_node* node) {
        return asinh(dispatch(node->get_child<0>()));
    }

    double operator()(atanh_node* node) {
        return atanh(dispatch(node->get_child<0>()));
    }

    double operator()(acoth_node* node) {
        double x = dispatch(node->get_child<0>());
        return 0.5 * log((x+1)/(x-1));
    }

    double operator()(erf_node* node) {
        return erf(dispatch(node->get_child<0>()));
    }

    double operator()(erfc_node* node) {
        return erfc(dispatch(node->get_child<0>()));
    }

    double operator()(pos_node* node) {
        if (dispatch(node->get_child<0>()) <= 0) {
            throw std::invalid_argument("called pos_node with non-positive variable");
        }
        return dispatch(node->get_child<0>());
    }

    double operator()(neg_node* node) {
        if (dispatch(node->get_child<0>()) >= 0) {
            throw std::invalid_argument("called neg_node with positive variable");
        }
        return dispatch(node->get_child<0>());
    }

    double operator()(schroeder_ethanol_p_node* node) {
        double t = dispatch(node->get_child<0>());
        const double t_c_K = 514.71;
        const double n_Tsat_1 = -8.94161;
        const double n_Tsat_2 = 1.61761;
        const double n_Tsat_3 = -51.1428;
        const double n_Tsat_4 = 53.1360;
        const double k_Tsat_1 = 1.0;
        const double k_Tsat_2 = 1.5;
        const double k_Tsat_3 = 3.4;
        const double k_Tsat_4 = 3.7;
        const double p_c = 62.68;
        return p_c*(exp(t_c_K/t*(n_Tsat_1*pow((1-t/t_c_K),k_Tsat_1) + n_Tsat_2*pow((1-t/t_c_K),k_Tsat_2)
           + n_Tsat_3*pow((1-t/t_c_K),k_Tsat_3) + n_Tsat_4*pow((1-t/t_c_K),k_Tsat_4))));
    }

    double operator()(schroeder_ethanol_rhovap_node* node) {
        double t = dispatch(node->get_child<0>());
        const double t_c_K = 514.71;
        const double n_vap_1 = -1.75362;
        const double n_vap_2 = -10.5323;
        const double n_vap_3 = -37.6407;
        const double n_vap_4 = -129.762;
        const double k_vap_1 = 0.21;
        const double k_vap_2 = 1.1;
        const double k_vap_3 = 3.4;
        const double k_vap_4 = 10;
        const double rho_c = 273.195;
        return rho_c*(exp(n_vap_1*pow((1 - t/t_c_K),k_vap_1) + n_vap_2*pow((1 - t/t_c_K),k_vap_2)
            + n_vap_3*pow((1 - t/t_c_K),k_vap_3) + n_vap_4*pow((1 - t/t_c_K),k_vap_4)));
    }

    double operator()(schroeder_ethanol_rholiq_node* node) {
        double t = dispatch(node->get_child<0>());
        const double t_c_K = 514.71;
        const double n_liq_1 = 9.00921;
        const double n_liq_2 = -23.1668;
        const double n_liq_3 = 30.9092;
        const double n_liq_4 = -16.5459;
        const double n_liq_5 = 3.64294;
        const double k_liq_1 = 0.5;
        const double k_liq_2 = 0.8;
        const double k_liq_3 = 1.1;
        const double k_liq_4 = 1.5;
        const double k_liq_5 = 3.3;
        const double rho_c = 273.195;
        return rho_c*(1 + n_liq_1*pow((1 - t/t_c_K),k_liq_1) + n_liq_2*pow((1 - t/t_c_K),k_liq_2)
            + n_liq_3*pow((1 - t/t_c_K),k_liq_3) + n_liq_4*pow((1 - t/t_c_K),k_liq_4)
            + n_liq_5*pow((1 - t/t_c_K),k_liq_5));
    }

    double operator()(covar_matern_1_node* node) {
        double x = dispatch(node->get_child<0>());
        return exp(-sqrt(x));
    }

    double operator()(covar_matern_3_node* node) {
        double x = dispatch(node->get_child<0>());
        double tmp = sqrt(3)*sqrt(x);
        return exp(-tmp) + tmp*exp(-tmp);
    }

    double operator()(covar_matern_5_node* node) {
        double x = dispatch(node->get_child<0>());
        double tmp = sqrt(5)*sqrt(x);
        return exp(-tmp) + tmp*exp(-tmp) + 5./3.*x*exp(-tmp);
    }

    double operator()(covar_sqrexp_node* node) {
        double x = dispatch(node->get_child<0>());
        return exp(-0.5*x);
    }

    double operator()(gpdf_node* node) {
        double x = dispatch(node->get_child<0>());
        return 1./(sqrt(2*M_PI)) * exp(-pow(x,2)/2.);
    }

    double operator()(lmtd_node* node) {
        double dT1 = dispatch(node->get_child<0>());
        double dT2 = dispatch(node->get_child<1>());
        return (dT1-dT2) / log(dT1/dT2);
    }

    double operator()(rlmtd_node* node) {
        double dT1 = dispatch(node->get_child<0>());
        double dT2 = dispatch(node->get_child<1>());
        return log(dT1/dT2) / (dT1-dT2);
    }

    double operator()(xexpax_node* node) {
        double x = dispatch(node->get_child<0>());
        double a = dispatch(node->get_child<1>());
        return x * exp(a * x);
    }

    double operator()(arh_node* node) {
        return exp(-dispatch(node->get_child<1>())/dispatch(node->get_child<0>()));
    }

    double operator()(lb_func_node* node) {
        if (dispatch(node->get_child<0>()) < dispatch(node->get_child<1>())) {
            std::ostringstream errmsg;
            errmsg << "called Lb_func with values lower than " << dispatch(node->get_child<1>())
                << " in range.";
            throw std::invalid_argument(errmsg.str());
        }
        return dispatch(node->get_child<0>());
    }

    double operator()(ub_func_node* node) {
        if (dispatch(node->get_child<0>()) > dispatch(node->get_child<1>())) {
            std::ostringstream errmsg;
            errmsg << "called ub_func with values larger than " << dispatch(node->get_child<1>())
                << " in range.";
            throw std::invalid_argument(errmsg.str());
        }
        return dispatch(node->get_child<0>());
    }

    double operator()(xexpy_node* node) {
        return dispatch(node->get_child<0>())*exp(dispatch(node->get_child<1>()));
    }

    double operator()(mid_node* node) {
        double arg1 = dispatch(node->get_child<0>());
        double arg2 = dispatch(node->get_child<1>());
        double arg3 = dispatch(node->get_child<2>());
        return std::min(std::max(arg1, arg2), std::min(std::max(arg2, arg3), std::max(arg3, arg1)));
    }


    double operator()(squash_node* node) {
        double arg1 = dispatch(node->get_child<0>());
        double arg2 = dispatch(node->get_child<1>());
        double arg3 = dispatch(node->get_child<2>());
        return std::min(std::max(arg1, arg2), arg3);
    }
    double operator()(regnormal_node* node) {
        double x = dispatch(node->get_child<0>());
        double a = dispatch(node->get_child<1>());
        double b = dispatch(node->get_child<2>());
        return x / std::sqrt(a+b*std::pow(x,2));
    }
    double operator()(af_lcb_node* node) {
        double mu    = dispatch(node->get_child<0>());
        double sigma = dispatch(node->get_child<1>());
        double kappa = dispatch(node->get_child<2>());
        return mu - kappa*sigma;
    }
    double operator()(af_ei_node* node) {
        double mu    = dispatch(node->get_child<0>());
        double sigma = dispatch(node->get_child<1>());
        double fmin  = dispatch(node->get_child<2>());
        if(sigma == 0){
            return std::max(fmin-mu, 0.);
        }
        double x   = mu - fmin;
        double gcd = std::erf(1./std::sqrt(2)*(-x/sigma))/2.+0.5;
        double gpd = 1./(std::sqrt(2*M_PI)) * std::exp(-std::pow(-x/sigma,2)/2.);
        return (-x)*gcd + sigma*gpd;
    }
    double operator()(af_pi_node* node) {
        double mu    = dispatch(node->get_child<0>());
        double sigma = dispatch(node->get_child<1>());
        double fmin  = dispatch(node->get_child<2>());
        if(sigma == 0 && fmin <= mu){
            return 0;
        }
        if(sigma == 0 && fmin > mu){
            return 1;
        }
        double x   = mu - fmin;
        return std::erf(1./std::sqrt(2)*(-x/sigma))/2.+0.5;
    }

    double operator()(ext_antoine_psat_node* node) {
        double t  = dispatch(node->get_child<0>());
        double p1 = dispatch(node->get_child<1>());
        double p2 = dispatch(node->get_child<2>());
        double p3 = dispatch(node->get_child<3>());
        double p4 = dispatch(node->get_child<4>());
        double p5 = dispatch(node->get_child<5>());
        double p6 = dispatch(node->get_child<6>());
        double p7 = dispatch(node->get_child<7>());
        return std::exp(p1 + p2 / (t + p3) + t * p4 + p5 * std::log(t) + p6 * std::pow(t, p7));
    }

    double operator()(antoine_psat_node* node) {
        double t  = dispatch(node->get_child<0>());
        double p1 = dispatch(node->get_child<1>());
        double p2 = dispatch(node->get_child<2>());
        double p3 = dispatch(node->get_child<3>());
        return std::pow(10., p1 - p2 / (p3 + t));
    }

    double operator()(wagner_psat_node* node) {
        double t  = dispatch(node->get_child<0>());
        double p1 = dispatch(node->get_child<1>());
        double p2 = dispatch(node->get_child<2>());
        double p3 = dispatch(node->get_child<3>());
        double p4 = dispatch(node->get_child<4>());
        double p5 = dispatch(node->get_child<5>());
        double p6 = dispatch(node->get_child<6>());
        double Tr = t / p5;
        return p6 * std::exp((p1*(1 - Tr) + p2 * std::pow(1 - Tr, 1.5) + p3 * std::pow(1 - Tr, 2.5)
            + p4 * std::pow(1 - Tr, 5)) / Tr);
    }

    double operator()(ik_cape_psat_node* node) {
        double t  = dispatch(node->get_child<0>());
        double p1 = dispatch(node->get_child<1>());
        double p2 = dispatch(node->get_child<2>());
        double p3 = dispatch(node->get_child<3>());
        double p4 = dispatch(node->get_child<4>());
        double p5 = dispatch(node->get_child<5>());
        double p6 = dispatch(node->get_child<6>());
        double p7 = dispatch(node->get_child<7>());
        double p8 = dispatch(node->get_child<8>());
        double p9 = dispatch(node->get_child<9>());
        double p10 = dispatch(node->get_child<10>());
        return std::exp(p1 + p2 * t + p3 * std::pow(t, 2) + p4 * std::pow(t, 3) + p5 * std::pow(t, 4)
            + p6 * std::pow(t, 5) + p7 * std::pow(t, 6) + p8 * std::pow(t, 7) + p9 * std::pow(t, 8)
            + p10 * std::pow(t, 9));
    }

    double operator()(aspen_hig_node* node) {
        double t  = dispatch(node->get_child<0>());
        double t0 = dispatch(node->get_child<1>());
        double p1 = dispatch(node->get_child<2>());
        double p2 = dispatch(node->get_child<3>());
        double p3 = dispatch(node->get_child<4>());
        double p4 = dispatch(node->get_child<5>());
        double p5 = dispatch(node->get_child<6>());
        double p6 = dispatch(node->get_child<7>());
        return p1 * (t - t0) + p2 / 2 * (std::pow(t, 2) - std::pow(t0, 2)) + p3 / 3 * (std::pow(t, 3)
            - std::pow(t0, 3)) + p4 / 4 * (std::pow(t, 4) - std::pow(t0, 4)) + p5 / 5 * (std::pow(t, 5)
            - std::pow(t0, 5)) + p6 / 6 * (std::pow(t, 6) - std::pow(t0, 6));
    }

    double operator()(nasa9_hig_node* node) {
        double t  = dispatch(node->get_child<0>());
        double t0 = dispatch(node->get_child<1>());
        double p1 = dispatch(node->get_child<2>());
        double p2 = dispatch(node->get_child<3>());
        double p3 = dispatch(node->get_child<4>());
        double p4 = dispatch(node->get_child<5>());
        double p5 = dispatch(node->get_child<6>());
        double p6 = dispatch(node->get_child<7>());
        double p7 = dispatch(node->get_child<8>());
        return -p1 * (1 / t - 1 / t0) + p2 * std::log(t / t0) + p3 * (t - t0) + p4 / 2 * (std::pow(t, 2)
            - std::pow(t0, 2)) + p5 / 3 * (std::pow(t, 3) - std::pow(t0, 3)) + p6 / 4 * (std::pow(t, 4)
            - std::pow(t0, 4)) + p7 / 5 * (std::pow(t, 5) - std::pow(t0, 5));
    }

    double operator()(dippr107_hig_node* node) {
        double t  = dispatch(node->get_child<0>());
        double t0 = dispatch(node->get_child<1>());
        double p1 = dispatch(node->get_child<2>());
        double p2 = dispatch(node->get_child<3>());
        double p3 = dispatch(node->get_child<4>());
        double p4 = dispatch(node->get_child<5>());
        double p5 = dispatch(node->get_child<6>());
        return p1 * (t - t0) + p2 * p3*(1 / std::tanh(p3 / t) - 1 / std::tanh(p3 / t0))
            - p4 * p5*(std::tanh(p5 / t) - std::tanh(p5 / t0));
    }

    double operator()(dippr127_hig_node* node) {
        double t  = dispatch(node->get_child<0>());
        double t0 = dispatch(node->get_child<1>());
        double p1 = dispatch(node->get_child<2>());
        double p2 = dispatch(node->get_child<3>());
        double p3 = dispatch(node->get_child<4>());
        double p4 = dispatch(node->get_child<5>());
        double p5 = dispatch(node->get_child<6>());
        double p6 = dispatch(node->get_child<7>());
        double p7 = dispatch(node->get_child<8>());
        return p1 * (t - t0) + p2 * p3*(1 / (std::exp(p3 / t) - 1) - 1 / (std::exp(p3 / t0) - 1))
            + p4 * p5*(1 / (std::exp(p5 / t) - 1) - 1 / (std::exp(p5 / t0) - 1))
            + p6 * p7*(1 / (std::exp(p7 / t) - 1) - 1 / (std::exp(p7 / t0) - 1));
    }

    double operator()(antoine_tsat_node* node) {
        double t  = dispatch(node->get_child<0>());
        double p1 = dispatch(node->get_child<1>());
        double p2 = dispatch(node->get_child<2>());
        double p3 = dispatch(node->get_child<3>());
        return p2 / (p1 - std::log(t) / std::log(10.)) - p3;
    }

    double operator()(watson_dhvap_node* node) {
        double t  = dispatch(node->get_child<0>());
        double tc = dispatch(node->get_child<1>());
        double a = dispatch(node->get_child<2>());
        double b = dispatch(node->get_child<3>());
        double t1 = dispatch(node->get_child<4>());
        double dHT1 = dispatch(node->get_child<5>());
        double tr = 1 - t / tc;
        if (tr > 0) {
            return dHT1 * std::pow(tr / (1 - t1 / tc), a + b * tr);
        }
        else {
            return 0.;
        }
    }

    double operator()(dippr106_dhvap_node* node) {
        double t  = dispatch(node->get_child<0>());
        double tc = dispatch(node->get_child<1>());
        double p2 = dispatch(node->get_child<2>());
        double p3 = dispatch(node->get_child<3>());
        double p4 = dispatch(node->get_child<4>());
        double p5 = dispatch(node->get_child<5>());
        double p6 = dispatch(node->get_child<6>());
        double tr = t / tc;
        if (tr < 1) {
            return p2 * std::pow(1 - tr, p3 + p4 * tr + p5 * std::pow(tr, 2) + p6 * std::pow(tr, 3));
        }
        else {
            return 0.;
        }
    }

    double operator()(cost_turton_node* node) {
        double x  = dispatch(node->get_child<0>());
        double p1 = dispatch(node->get_child<1>());
        double p2 = dispatch(node->get_child<2>());
        double p3 = dispatch(node->get_child<3>());
        return std::pow(10., p1 + p2 * std::log(x) / std::log(10.) + p3 * std::pow(std::log(x)
            / std::log(10.), 2));
    }

    double operator()(norm2_node* node) {
        return std::sqrt(pow(dispatch(node->get_child<0>()),2) + pow(dispatch(node->get_child<1>()),2));
        }

    double operator()(bounding_func_node* node) {
        double x = dispatch(node->get_child<0>());
        double lb = dispatch(node->get_child<1>());
        double ub = dispatch(node->get_child<2>());
        if (lb > ub) {
            throw std::invalid_argument("lb > ub in bounding_func");
        }
        if (lb > x) {
            throw std::invalid_argument("lb > x in bounding_func");
        }
        if (x > ub) {
            throw std::invalid_argument("x > ub in bounding_func");
        }
        return x;
    }

    template <typename TType>
    owning_ref<TType> operator()(function_node<TType>* node) {
        return evaluate_function(*this, node, symbols);
    }

    template <typename TType>
    ref_type<tensor_type<atom_type<TType>, 1>> operator()(vector_node<TType>* node) {
        throw std::invalid_argument("vector_node should not be encountered in evaluator");
    }

    template <typename TType>
    double operator()(sum_node<TType>* node) {
        auto elements = dispatch(node->template get_child<0>());
#ifndef NDEBUG
        if (elements.begin() == elements.end()) {
            std::cout << "called sum with emtpy set (by convention equals 0)\n";
        }
#endif
        symbols.push_scope();
        double result = 0;
        for (auto it = elements.begin(); it != elements.end(); ++it) {
            symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            result += dispatch(node->template get_child<1>());
        }
        symbols.pop_scope();
        return result;
    }


    template <typename TType>
    double operator()(product_node<TType>* node) {
        auto elements = dispatch(node->template get_child<0>());
#ifndef NDEBUG
        if (elements.begin() == elements.end()) {
            std::cout << "called product with emtpy set (by convention equals 1)\n";
        }
#endif
        symbols.push_scope();
        double result = 1;
        for (auto it = elements.begin(); it != elements.end(); ++it) {
            symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            result *= dispatch(node->template get_child<1>());
        }
        symbols.pop_scope();
        return result;
    }


    template <typename TType>
    double operator()(set_min_node<TType>* node) {
        auto elements = dispatch(node->template get_child<0>());
        if (elements.begin() == elements.end()) {
            throw std::invalid_argument("called set_min with emtpy set");
        }
        symbols.push_scope();
        double result = std::numeric_limits<double>::infinity();
        for (auto it = elements.begin(); it != elements.end(); ++it) {
            symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            result = std::min(result, dispatch(node->template get_child<1>()));
        }
        symbols.pop_scope();
        return result;
    }

    template <typename TType>
    double operator()(set_max_node<TType>* node) {
        auto elements = dispatch(node->template get_child<0>());
        if (elements.begin() == elements.end()) {
            throw std::invalid_argument("called set_max with emtpy set");
        }
        symbols.push_scope();
        double result = - std::numeric_limits<double>::infinity();
        for (auto it = elements.begin(); it != elements.end(); ++it) {
            symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            result = std::max(result, dispatch(node->template get_child<1>()));
        }
        symbols.pop_scope();
        return result;
    }
    double operator() (round_node* node){
        return std::lround(dispatch(node->get_child<0>()));
    }
    double operator() (index_to_real_node* node){
      int value=dispatch(node->get_child<0>());
      return (double) value;
    }
    // non-terminal index node visits
    int operator()(index_minus_node* node) {
        return - dispatch(node->get_child<0>());
    }

    int operator() (real_to_index_node* node){
            double value=dispatch(node->get_child<0>());
            //check if convertible to integer
            if(value<0){
              throw std::invalid_argument("called real_to_index with value smaller than 0:"+std::to_string(value));
            }
            if(value>std::numeric_limits<int>::max()){
              throw std::invalid_argument("called real_to_index with value too big to represent as an integer: "+std::to_string(value));
            }
            if(value!=std::trunc(value))
            {
              throw std::invalid_argument("must call real_to_index with value exactly representable as integer. Passed: "+std::to_string(value));
            }
            return (int) value;
    }
    int operator()(index_addition_node* node) {
        int result = 0;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            result += dispatch(it->get());
        }
        return result;
    }

    int operator()(index_multiplication_node* node) {
        int result = 1;
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            result *= dispatch(it->get());
        }
        return result;
    }

    // non-terminal boolean node visits
    bool operator()(negation_node* node) {
        return ! dispatch(node->get_child<0>());
    }

    template <typename TType>
    bool operator()(equal_node<TType>* node) {
        return dispatch(node->template get_child<0>()) == dispatch(node->template get_child<1>());
    }

    template <typename TType>
    bool operator()(less_node<TType>* node) {
        return dispatch(node->template get_child<0>()) < dispatch(node->template get_child<1>());
    }

    template <typename TType>
    bool operator()(less_equal_node<TType>* node) {
        return dispatch(node->template get_child<0>()) <= dispatch(node->template get_child<1>());
    }

    template <typename TType>
    bool operator()(greater_node<TType>* node) {
        return dispatch(node->template get_child<0>()) > dispatch(node->template get_child<1>());
    }

    template <typename TType>
    bool operator()(greater_equal_node<TType>* node) {
        return dispatch(node->template get_child<0>()) >= dispatch(node->template get_child<1>());
    }

    bool operator()(disjunction_node* node) {
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            if (dispatch(it->get())) {
                return true;
            }
        }
        return false;
    }

    bool operator()(conjunction_node* node) {
        for (auto it = node->children.begin(); it != node->children.end(); ++it) {
            if (!dispatch(it->get())) {
                return false;
            }
        }
        return true;
    }

    template <typename TType>
    bool operator()(element_node<TType>* node) {
        auto [element, containing_set] = evaluate_children_tuple(*this, node);
        for (const auto& v: containing_set) {
            if (element == v) {
                return true;
            }
        }
        return false;
    }

    template <typename TType>
    bool operator()(forall_node<TType>* node) {
        auto elements = dispatch(node->template get_child<0>());
        symbols.push_scope();
        for (auto it = elements.begin(); it != elements.end(); ++it) {
            symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            if (!dispatch(node->template get_child<1>())) {
                symbols.pop_scope();
                return false;
            }
        }
        symbols.pop_scope();
        return true;
    }

    template <typename TType>
    owning_ref<set<TType, 0>> operator()(indicator_set_node<TType>* node) {
        auto elements = dispatch(node->template get_child<0>());
        symbols.push_scope();
        for (auto it = elements.begin(); it != elements.end();) {
            symbols.define(node->name, new parameter_symbol<TType>(node->name, *it));
            if (!dispatch(node->template get_child<1>())) {
                it = elements.erase(it);
            }
            else {
                ++it;
            }
        }
        symbols.pop_scope();
        return elements;
    }

    symbol_table& get_symbols() {
        return symbols;
    }
private:
    symbol_table& symbols;
};

#include "util/evaluator_forward_declarations.tpp"

template <typename TType>
owning_ref<TType> evaluate_expression(expression<TType>& expr, symbol_table& symbols) {
    return evaluate_expression(expr.get(), symbols);
}

template <typename TType>
owning_ref<TType> evaluate_expression(value_node<TType>* node, symbol_table& symbols) {
    evaluation_visitor eval(symbols);
    return eval.dispatch(node);
}

}//ale::util

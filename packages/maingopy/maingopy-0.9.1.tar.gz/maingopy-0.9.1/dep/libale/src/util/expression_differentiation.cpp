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
#include "expression_differentiation.hpp"

#include <array>                 // for array
#include <math.h>                // for sqrt, M_PI
#include <cstdlib>               // for size_t, rand
#include <functional>            // for reference_wrapper
#include <list>                  // for operator!=, list, _List_iterator, _List_iterator<>::_Self
#include <map>                   // for map
#include <memory>                // for operator!=, unique_ptr, allocator_traits<>::value_type, default_delete
#include <stdexcept>             // for invalid_argument
#include <variant>               // for variant
#include <vector>                // for vector
#include <typeinfo>              // for typeid

#include "expression_utils.hpp"  // for replace_parameters, get_parameter_shape, find_parameter
#include "node.hpp"
#include "symbol.hpp"            // for cast_function_symbol
#include "symbol_table.hpp"      // for symbol_table
#include "util/expression_to_string.hpp"
#include "util/expression_utils/expression_utils_get_shape.hpp"
#include "util/expression_utils/expression_utils_is_constant.hpp"
#include "util/expression_utils/expression_utils_replace_parameter.hpp"
#include "visitor_utils.hpp"     // for reset_value_node_ptr_variant, traverse_children, call_visitor, extract_function_arguments






namespace ale {

    // declare differentiate fuction for recursion
    template <unsigned IDim>
    void differentiate_value_node_ptr(value_node_ptr<real<IDim>>&, const std::string& name, const std::vector<size_t>&, symbol_table&);

    /**
     * Visitor to differentiate expression trees
     *
     * TODO: maybe use unique_ptrs
     */
    class expression_diff_visitor {
    public:
        // take root to the expression being differentiated and the other parameters (see differentiate_value_node_ptr)
        expression_diff_visitor(value_node_ptr_variant root, const std::string& name, const std::vector<size_t>& index, symbol_table& symbols):
                current_node(root), var_name(name), index(index), symbols(symbols) {}

        template <typename TNode>
        void operator()(TNode* node) {
            throw std::invalid_argument("Differentiation of node of type " + std::string(typeid(TNode).name()) + " not possible/implemented");
        }

        void operator()(index_to_real_node* node) {
            // check that node does not depend on var_name
            auto var_name_parameters = find_parameter(var_name, current_node);
            if (!var_name_parameters.empty()) {
                throw std::invalid_argument("cannot differentiate expression with index_to_real_node which depends on the variable being differentiated");
            }

            // derivative is zero
            auto* new_node = new constant_node<real<0>>(0);
            reset_value_node_ptr_variant(current_node, new_node);
        }

        void operator()(real_to_index_node* node) {
            throw std::invalid_argument("cannot differentiate real_to_index_node");
        }

        void operator()(addition_node* node) {
            traverse_children(*this, node, {}, current_node);
        }

        void operator()(minus_node* node) {
            traverse_children(*this, node, {}, current_node);
        }

        template <unsigned IDim>
        void operator()(tensor_node<real<IDim>>* node) {
            traverse_children(*this, node, {}, current_node);
        }

        template <typename IteratorType>
        void operator()(sum_node<IteratorType>* node) {
            differentiate_value_node_ptr(std::get<1>(node->children), var_name, index, symbols);
        }

        template <typename IteratorType>
        void operator()(product_node<IteratorType>* node) {
            // (f_1*...*f_n)'=f_1'*(f_2*...*f_n)+...+(f_1*...*f_(n-1))*f_n'
            // (product(j in M: f_j))' = sum(j in M: f_j'*product(i in M\{j}: f_i))

            // for other iteratortypes there is no way yet to check wether to elements are equal
            if constexpr (std::is_same_v<IteratorType, real<0>>) {
                // get a reference to the value_node_ptr of the set which is iterated
                auto set = std::get<0>(node->children);

                auto rand_string = std::to_string(std::rand());
                std::string outer_var_name = node->name + "__outer_diff_iterator_var" + rand_string;
                std::string indicator_var_name = node->name + "__indicator_diff_iterator_var" + rand_string;

                if (symbols.resolve(outer_var_name) != nullptr || symbols.resolve(indicator_var_name) != nullptr) {
                    throw std::invalid_argument("name of iteration variable already in use");
                }

                // construct M\{j}
                auto ind_var = new parameter_node<IteratorType>(indicator_var_name);
                auto outer_var = new parameter_node<IteratorType>(outer_var_name);
                auto ind_is_outer = new equal_node<IteratorType>(ind_var, outer_var);
                auto ind_is_not_outer = new negation_node(ind_is_outer);
                auto set_without_outer = new indicator_set_node<IteratorType>(indicator_var_name, set->clone(), ind_is_not_outer);

                // construct product(i in M\{j}: f_i)
                auto non_derivative_prod = new product_node<IteratorType>(node->name, set_without_outer, node->template get_child<1>()->clone());

                // construct f_j'
                auto f_prime = std::get<1>(node->children);
                differentiate_value_node_ptr(f_prime, var_name, index, symbols);

                std::map<std::string, ale::value_node_variant> arg_map;
                arg_map.insert_or_assign(node->name, new parameter_node<IteratorType>(outer_var_name));
                //only one arg_map entry (else would need to prevent interference as in evaluate_function)
                replace_parameters(f_prime, arg_map);

                // construct f_j'*product(i in M\{j}: f_i)
                auto expr = new multiplication_node();
                expr->add_child(non_derivative_prod);
                expr->add_child(f_prime.release());

                // construct sum(j in M: f_j'*product(i in M\{j}: f_i))
                auto sum = new sum_node<IteratorType>(outer_var_name, set.release(), expr);

                // replace the current node with the derivative
                reset_value_node_ptr_variant(current_node, sum);
            }
        }

        /**
         * helper function to apply chain rule: (f(g(x)))' = f'(g(x))*g'(x)
         *
         * where fprime should be f'(g(x))
         * and g should be g(x)
         */
        void reset_with_chain_rule(value_node<real<0>>* fprime, value_node_ptr<real<0>> g) {
            // differentiate g
            differentiate_value_node_ptr(g, var_name, index, symbols);

            // multiply them together
            auto res = new multiplication_node();
            res->add_child(fprime);
            res->add_child(g.release());

            // replace the current node with the result
            reset_value_node_ptr_variant(current_node, res);
        }

        // (1/g(x))'=-1/g(x)^2*g'(x)
        void operator()(inverse_node* node) {
            // g(x)^2
            auto prod = new multiplication_node();
            prod->add_child(node->template get_child<0>()->clone());
            prod->add_child(node->template get_child<0>()->clone());

            // -1/g(x)^2
            auto inv = new inverse_node(prod);
            auto neg_inv = new minus_node(inv);

            // apply chainrule with f'(g(x)) = -1/g(x)^2
            reset_with_chain_rule(neg_inv, std::get<0>(node->children));
        }

        void operator()(exp_node* node) {
            // f(x) := e^x
            // g(x) is the child stored in this node
            // f'(g(x)) = f(g(x)) (ie exp'(g(x)) = e^g(x)) so we can just clone this node
            reset_with_chain_rule(node->clone(), std::get<0>(node->children));
        }

        void operator()(log_node* node) {
            // compute log'(g(x)) which is 1/g(x)
            auto inv = new inverse_node(node->template get_child<0>()->clone());

            // apply chain rule
            reset_with_chain_rule(inv, std::get<0>(node->children));
        }

        void operator()(xlogx_node* node) {
            // compute xlogx'(g(x)) which is log(g(x)) + 1
            auto log = new log_node(node->template get_child<0>()->clone());

            auto fprime = new addition_node();
            fprime->add_child(log);
            fprime->add_child(new constant_node<real<0>>(1));

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(sqrt_node* node) {
            // compute sqrt'(g(x)) which is 1/(2 * sqrt(g(x)))
            auto g_sqrt = new sqrt_node(node->template get_child<0>()->clone());

            auto mul = new multiplication_node();
            mul->add_child(new constant_node<real<0>>(2));
            mul->add_child(g_sqrt);

            auto inv = new inverse_node(mul);

            // chain rule
            reset_with_chain_rule(inv, std::get<0>(node->children));
        }

        void operator()(sin_node* node) {
            // compute sin'(g(x)) which is cos(g(x))
            auto fprime = new cos_node(node->template get_child<0>()->clone());

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(asin_node* node) {
            // construct asin'(g(x)) = 1 / sqrt(1 - g(x)^2)
            auto g_sqr = new multiplication_node();
            g_sqr->add_child(node->template get_child<0>()->clone());
            g_sqr->add_child(node->template get_child<0>()->clone());

            auto neg_g_sqr = new minus_node(g_sqr);

            auto diff = new addition_node();
            diff->add_child(neg_g_sqr);
            diff->add_child(new constant_node<real<0>>(1));

            auto diff_sqrt = new sqrt_node(diff);

            auto fprime = new inverse_node(diff_sqrt);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(cos_node* node) {
            // compute cos'(g(x)) which is -sin(g(x))
            auto fprime_neg = new sin_node(node->template get_child<0>()->clone());
            auto fprime = new minus_node(fprime_neg);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(acos_node* node) {
            // construct acos'(g(x)) = - 1 / sqrt(1 - g(x)^2)
            auto g_sqr = new multiplication_node();
            g_sqr->add_child(node->template get_child<0>()->clone());
            g_sqr->add_child(node->template get_child<0>()->clone());

            auto neg_g_sqr = new minus_node(g_sqr);

            auto diff = new addition_node();
            diff->add_child(neg_g_sqr);
            diff->add_child(new constant_node<real<0>>(1));

            auto diff_sqrt = new sqrt_node(diff);

            auto neg_diff_sqrt = new minus_node(diff_sqrt);

            auto fprime = new inverse_node(neg_diff_sqrt);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(tan_node* node) {
            // compute tan'(g(x)) which is 1/cos^2(g(x))
            auto co = new cos_node(node->template get_child<0>()->clone());

            auto co_sqr = new multiplication_node();
            co_sqr->add_child(co);
            co_sqr->add_child(co->clone());

            auto fprime = new inverse_node(co_sqr);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(atan_node* node) {
            // construct atan'(g(x)) = 1 / (g(x)^2 + 1)
            auto g_sqr = new multiplication_node();
            g_sqr->add_child(node->template get_child<0>()->clone());
            g_sqr->add_child(node->template get_child<0>()->clone());

            auto sum = new addition_node();
            sum->add_child(g_sqr);
            sum->add_child(new constant_node<real<0>>(1));

            auto fprime = new inverse_node(sum);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(sinh_node* node) {
            // construct sinh'(g(x)) = cosh(g(x))
            auto fprime = new cosh_node(node->template get_child<0>()->clone());

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(cosh_node* node) {
            // construct cosh'(g(x)) = sinh(g(x))
            auto fprime = new sinh_node(node->template get_child<0>()->clone());

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(asinh_node* node) {
            // construct asinh'(g(x)) = 1 / sqrt(g(x)^2 + 1)
            auto g_sqr = new multiplication_node();
            g_sqr->add_child(node->template get_child<0>()->clone());
            g_sqr->add_child(node->template get_child<0>()->clone());

            auto sum = new addition_node();
            sum->add_child(g_sqr);
            sum->add_child(new constant_node<real<0>>(1));

            auto sum_sqrt = new sqrt_node(sum);

            auto fprime = new inverse_node(sum_sqrt);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(acosh_node* node) {
            // construct acosh'(g(x)) = 1 / (sqrt(g(x) - 1) * sqrt(g(x) + 1))

            auto diff = new addition_node();
            diff->add_child(node->template get_child<0>()->clone());
            diff->add_child(new constant_node<real<0>>(-1));

            auto sqrt_1 = new sqrt_node(diff);

            auto sum = new addition_node();
            sum->add_child(node->template get_child<0>()->clone());
            sum->add_child(new constant_node<real<0>>(1));

            auto sqrt_2 = new sqrt_node(sum);

            auto prod = new multiplication_node();
            prod->add_child(sqrt_1);
            prod->add_child(sqrt_2);

            auto fprime = new inverse_node(prod);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(tanh_node* node) {
            // construct tanh'(g(x)) = 1 / cosh^2(g(x))
            auto cosh = new cosh_node(node->template get_child<0>()->clone());

            auto cosh_sqr = new multiplication_node();
            cosh_sqr->add_child(cosh->clone());
            cosh_sqr->add_child(cosh);

            auto fprime = new inverse_node(cosh_sqr);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(atanh_node* node) {
            // construct atanh'(g(x)) = 1 / (1 - g(x)^2)
            auto g_sqr = new multiplication_node();
            g_sqr->add_child(node->template get_child<0>()->clone());
            g_sqr->add_child(node->template get_child<0>()->clone());

            auto neg_g_sqr = new minus_node(g_sqr);

            auto diff = new addition_node();
            diff->add_child(new constant_node<real<0>>(1));
            diff->add_child(neg_g_sqr);

            auto fprime = new inverse_node(diff);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(coth_node* node) {
            // construct coth'(g(x)) = - 1 / sinh^2(g(x))
            auto sinh = new sinh_node(node->template get_child<0>()->clone());

            auto sinh_sqr = new multiplication_node();
            sinh_sqr->add_child(sinh->clone());
            sinh_sqr->add_child(sinh);

            auto fprime_neg = new inverse_node(sinh_sqr);
            auto fprime = new minus_node(fprime_neg);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(acoth_node* node) {
            //construct acoth'(g(x)) = 1 / (1 - g^2(x))
            auto g_sqr = new multiplication_node();
            g_sqr->add_child(node->template get_child<0>()->clone());
            g_sqr->add_child(node->template get_child<0>()->clone());

            auto neg_g_sqr = new minus_node(g_sqr);

            auto diff = new addition_node();
            diff->add_child(neg_g_sqr);
            diff->add_child(new constant_node<real<0>>(1));

            auto fprime = new inverse_node(diff);

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(erf_node* node) {
            // compute erf'(g(x)) which is 2e^(-x^2)/sqrt(pi)
            auto sqr = new multiplication_node();
            sqr->add_child(node->template get_child<0>()->clone());
            sqr->add_child(node->template get_child<0>()->clone());

            auto sqr_neg = new minus_node(sqr);
            auto ex = new exp_node(sqr_neg);

            auto fprime = new multiplication_node();
            fprime->add_child(ex);
            fprime->add_child(new constant_node<real<0>>(2 / std::sqrt(M_PI)));

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        void operator()(erfc_node* node) {
            // compute erf'(g(x)) which is -2e^(-x^2)/sqrt(pi)
            auto sqr = new multiplication_node();
            sqr->add_child(node->template get_child<0>()->clone());
            sqr->add_child(node->template get_child<0>()->clone());

            auto sqr_neg = new minus_node(sqr);
            auto ex = new exp_node(sqr_neg);

            auto fprime = new multiplication_node();
            fprime->add_child(ex);
            fprime->add_child(new constant_node<real<0>>(- 2 / std::sqrt(M_PI)));

            // apply chain rule
            reset_with_chain_rule(fprime, std::get<0>(node->children));
        }

        template <unsigned IDim>
        void operator()(entry_node<real<IDim>>* node) {
            differentiate_value_node_ptr(std::get<0>(node->children), var_name, index, symbols);
        }

        template <unsigned IDim>
        void operator()(function_node<real<IDim>>* node) {
            auto* sym = cast_function_symbol<real<IDim>>(symbols.resolve(node->name));
            if (sym == nullptr) {
                throw std::invalid_argument("functionsymbol " + node->name + " is ill-defined");
            }

            std::map<std::string, value_node_variant> arg_map;
            auto args = extract_function_arguments(node);
            for (int i = 0; i < args.size(); ++i) {
                arg_map.emplace(sym->arg_names.at(i), args.at(i));
            }

            auto expr_copy = sym->expr;

            // when replacing the first argument with an expression, we may introduce a symbol which would be replaced by the second argument
            // thus we replace all arguments with special names
            // we only need to ensure that the names are unique from user given symbol names (our children nodes do not see these names)

            std::map<std::string, std::string> local_arg_names = {};
            std::map<std::string, value_node_variant> local_arg_map = {};
            // create map of keys of arg_map to unique names and map of unique names to values of arg_map
            int arg_pos = 1;
            for(const auto& elem: arg_map) {
                std::string arg_name = "__Arg_" + std::to_string(arg_pos++);
                local_arg_names.emplace(elem.first, arg_name);
                local_arg_map.emplace(arg_name, elem.second);
            }
            rename_parameters(expr_copy, local_arg_names);

            replace_parameters(expr_copy, local_arg_map);


            differentiate_value_node_ptr(expr_copy.get_root(), var_name, index, symbols);

            reset_value_node_ptr_variant(current_node, expr_copy.get_root().release());
        }

        void operator()(exponentiation_node* node) {
            // this node represents (a_0(x)^a_1(x))^...^a_n(x)
            // this derivative is calculated recursively by
            // f(x) := (a_0(x)^a_1(x))^...^a_(n-1)(x)
            // g(x) := a_n(x)
            // then (f(x)^g(x))'=f(x)^(g(x) - 1) * (g(x)*f'(x) + f(x)*log(f(x))*g'(x))

            if (node->children.size() == 0) {
                throw std::invalid_argument("encountered exponentiation node without children");
            }
            if (node->children.size() == 1) {
                differentiate_value_node_ptr(node->children.front(), var_name, index, symbols);
                reset_value_node_ptr_variant(current_node, node->children.front().release());

                return;
            }

            // copy a_n(x) and make node be f(x)
            auto g = value_node_ptr<real<0>>(node->children.back());
            node->children.pop_back();

            // check if g is constant
            auto exponents_value = get_subtree_value(g.get(), symbols);
            if (exponents_value) {
                // construct c * f ^ (c - 1)
                auto c = new constant_node<real<0>>(*exponents_value);
                auto c_m_1 = new constant_node<real<0>>(*exponents_value - 1);

                auto fc = new exponentiation_node();
                fc->add_child(node->clone());
                fc->add_child(c_m_1);

                auto f_prime = value_node_ptr<real<0>>(node->clone());
                differentiate_value_node_ptr(f_prime, var_name, index, symbols);

                auto res = new multiplication_node();
                res->add_child(c);
                res->add_child(fc);
                res->add_child(f_prime.release());

                reset_value_node_ptr_variant(current_node, res);

                return;
            }

            // f(x)^(g(x) - 1)
            auto g_min_1 = new addition_node();
            g_min_1->add_child(g->clone());
            g_min_1->add_child(new constant_node<real<0>>(-1));

            auto a = new exponentiation_node();
            a->add_child(node->clone());
            a->add_child(g_min_1);

            // f(x)*log(f(x))*g'(x)
            auto flogf = new xlogx_node(node->clone());

            auto g_prime = g;
            differentiate_value_node_ptr(g_prime, var_name, index, symbols);

            auto c = new multiplication_node();
            c->add_child(flogf);
            c->add_child(g_prime.release());

            // g(x)*f'(x)
            auto f_prime = value_node_ptr<real<0>>(node->clone());
            differentiate_value_node_ptr(f_prime, var_name, index, symbols);

            auto b = new multiplication_node();
            b->add_child(g.release());
            b->add_child(f_prime.release());

            // (g(x)*f'(x) + f(x)*log(f(x))*g'(x))
            auto second_term = new addition_node();
            second_term->add_child(b);
            second_term->add_child(c);

            // (f(x)^g(x))'
            auto result = new multiplication_node();
            result->add_child(a);
            result->add_child(second_term);

            reset_value_node_ptr_variant(current_node, result);
        }

        void operator()(multiplication_node* node) {
            // (f_1*...*f_n)'=f_1'*(f_2*...*f_n)+...+(f_1*...*f_(n-1))*f_n'

            // initialize sum
            auto sum = std::make_unique<addition_node>();

            // iterate over children
            for(const auto& f : node->children) {
                auto f_var = f->get_variant();
                //handle f_i = constant (not counting parameters as constant because we might diff wrt. to them)
                if(is_tree_constant(f.get(), symbols, /*count_parameters_as_constant*/ false))
                {
                    double val = util::evaluate_expression(f.get(), symbols);
                    // any factor is constant 0 => whole node is constant 0 => derivative is also 0
                    if(val == 0.0){
                        reset_value_node_ptr_variant(current_node, new constant_node<real<0>>(0));
                        return;
                    }
                    //else skip (df = 0)
                    continue;
                }
                else {
                    // copy f and differentiate it
                    auto df = f;
                    differentiate_value_node_ptr(df, var_name, index, symbols);
                    // initialize product with df
                    auto mult = std::make_unique<multiplication_node>();
                    mult->add_child(df.release());

                    // iterate over all other children and multiply them to df
                    for(auto& g : node->children) {
                        if(f != g) {
                            auto copy_g = g;
                            mult->add_child(copy_g.release());
                        }
                    }

                    // add product to sum
                    sum->add_child(mult.release());
                }
            }

            // replace the current node with the calculated differentiation
            reset_value_node_ptr_variant(current_node, sum.release());
        }

        void operator()(index_multiplication_node* node) {
            throw std::invalid_argument("not implemented");
        }

        //
        // leaf nodes
        //

        template <typename TType>
        void operator()(parameter_node<TType>* node) {
            // check wether this parameter is being differentiated
            if (node->name == var_name) {
                // check that parameter can be differentiated
                if constexpr (is_real_node<TType>) {
                    // differentiate f(x)=x or in general f(x)=x_index

                    // get shape of node
                    auto shape = get_parameter_shape(node->name, symbols);

                    if constexpr (get_node_dimension<TType> == 0) {
                        // f'(x)=1 -> replace current node with new constant one node
                        reset_value_node_ptr_variant(current_node, new constant_node<TType>(1));
                    } else {
                        // set the tensor to 1 at the index that is being differentiated
                        basic_type<TType> tmp(shape.data(), 0);
                        tmp[index.data()] = 1;

                        // create 0-tensor of correct shape
                        auto result = new constant_node<TType>(tmp);

                        // replace current node with new tensor
                        reset_value_node_ptr_variant(current_node, result);
                    }
                } else {
                    throw std::invalid_argument("Cannot differentiate index / set");
                }
            } else {
                // differentiate as if the parameter was a constant (should match operator()(constant_node)) -> f'=0
                // ignore sets and indexes
                if constexpr (is_real_node<TType>) {
                    if constexpr (get_node_dimension<TType> == 0) {
                        // replace current node with 0
                        reset_value_node_ptr_variant(current_node, new constant_node<TType>(0));
                    } else {
                        // get shape of node
                        auto shape = get_parameter_shape(node->name, symbols);

                        // get zero-tensor of correct shape and replace current node with it
                        reset_value_node_ptr_variant(current_node, new constant_node<TType>({shape.data(), 0}));
                    }
                }
            }
        }

        template <typename TType>
        void operator()(constant_node<TType>* node) {
            // ignore sets and indexes
            if constexpr (is_real_node<TType>) {
                if constexpr (get_node_dimension<TType> == 0) {
                    // replace current node with 0
                    reset_value_node_ptr_variant(current_node, new constant_node<TType>(0));
                } else {
                    // get shape of node
                    auto shape = node->value.shape();

                    // get zero-tensor of correct shape and replace current node with it
                    reset_value_node_ptr_variant(current_node, new constant_node<TType>({shape, 0}));
                }
            }
        }

    private:
        value_node_ptr_variant current_node;
        const std::string& var_name;
        const std::vector<size_t>& index;
        symbol_table& symbols;
    };

    class expression_diff_cleaning_visitor {
    public:
        // take root to the expression being differentiated and the other parameters (see differentiate_value_node_ptr)
        expression_diff_cleaning_visitor(value_node_ptr_variant root, symbol_table& symbols):
                current_node(root), symbols(symbols) {}

        template <typename TType>
        void operator()(value_node<TType>* node) {
            traverse_children(*this, node, symbols, current_node);
        }

        void operator()(multiplication_node* node) {
            for(const auto& f : node->children) {
                auto f_var = f->get_variant();
                ///if multiply with a constant zero whole expression is constant 0
                if(std::holds_alternative<constant_node<real<0>>*>(f_var)) {
                    constant_node<real<0>>* f_const = std::get<constant_node<real<0>>*>(f_var);
                    if(f_const->value == 0.0) {
                        //no need to look at any other children
                        reset_value_node_ptr_variant(current_node, new constant_node<real<0>>(0));
                        return;
                    }
                }
            }

            //traverse_children(*this, node, symbols, current_node);
        }

        

    private:
        value_node_ptr_variant current_node;
        symbol_table& symbols;
    };



    /**
     * differentiate tree starting at node wrt name[index] inplace
     */
    template <unsigned IDim>
    void differentiate_value_node_ptr(value_node_ptr<real<IDim>>& node, const std::string& name,
                                    const std::vector<size_t>& index, symbol_table& symbols) {


        // instantiate visitor

        std::vector<value_node_ptr_variant> val = find_parameter(name, node);
        //if const
        if(val.empty()) {
            if constexpr(IDim == 0) {
                // replace current node with 0
                reset_value_node_ptr_variant(node, new constant_node<real<0>>(0));
            } else {
                std::vector<size_t> shape = get_expression_shape(node, symbols);
                // get zero-tensor of correct shape and replace current node with it
                reset_value_node_ptr_variant(node, new constant_node<real<IDim>>({ shape.data(), 0 }));
            }
        } else {

            // copy node to differentiate
            expression_diff_visitor differ(node, name, index, symbols);

            // call the visitor starting at node
            call_visitor(differ, node);

            expression_diff_cleaning_visitor cleaner(node, symbols);
            call_visitor(cleaner, node);
        }
    }

    /**
     * Differentiate value_node_ptr with respect to all unspecified indexes.
     *
     * VarDim: dimension of the parameter being differentiated (cannot be deduced)
     */
    template <unsigned VarDim, unsigned IDim, size_t FixedDim>
    value_node_ptr<real<IDim + (VarDim - FixedDim)>> differentiate_expression(const value_node_ptr<real<IDim>>& expr, std::string variable_name, const std::array<size_t, FixedDim>& index, symbol_table& symbols) {
        if constexpr (VarDim == FixedDim) {  // no unspecified indexes
            auto expr_copy = expr;
            differentiate_value_node_ptr(expr_copy, variable_name, std::vector<size_t>(index.begin(), index.end()), symbols);
            return expr_copy;
        } else if (FixedDim < VarDim) {
            auto var_shape = get_parameter_shape(variable_name, symbols);

            // increase length of index
            std::array<size_t, FixedDim + 1> index_copy;
            std::copy_n(index.begin(), FixedDim, index_copy.begin());

            std::unique_ptr<tensor_node<real<IDim + (VarDim - FixedDim)>>> node{new tensor_node<real<IDim + (VarDim - FixedDim)>>()};
            for (int i = 0; i < var_shape.at(index.size()); ++i) {
                index_copy.at(index.size()) = i;

                auto expr_diff = differentiate_expression<VarDim>(expr, variable_name, index_copy, symbols);
                node->add_child(expr_diff.release());
            }

            return value_node_ptr<real<IDim + (VarDim - FixedDim)>>(node.release());
        } else {
            throw std::invalid_argument("tried to fix more dimensions than the variable has");
        }
    }

#include "util/differentiation_forward_declarations.tpp"



} // namespace ale

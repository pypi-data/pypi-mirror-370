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

#include "parser.hpp"

#include <algorithm>   // for copy_n
#include <array>       // for array
#include <iostream>    // for char_traits, endl, basic_ostream, cerr, istream, ostream
#include <iterator>    // for next
#include <map>         // for operator!=, _Rb_tree_const_iterator, _Rb_tree_const_iterator<>::_Self
#include <stdexcept>   // for invalid_argument
#include <tuple>       // for tuple_element<>::type
#include <type_traits> // for conditional_t
#include <utility>     // for move, operator<, operator==, pair, operator>
#include <variant>     // for variant

#include "symbol.hpp"                          // for value_symbol<>::variant, base_symbol::variant, function_symbol, parameter_symbol, value_symbol, varia...
#include "util/expression_differentiation.hpp" // for differentiate_expression
#include "util/visitor_utils.hpp"              // for call_visitor

using token_type = ale::token::token_type;

namespace ale {

parser::parser(std::istream &input, symbol_table &symbols) :
    lex(input), buf(lex), error_stream(std::cerr), symbols(symbols) {
    lex.reserve_keywords(
      { // fundamentals
        "real", "integer", "binary", "index", "boolean", "set", "in", "lb", "ub",
        "prio", "init", "true", "false", "as_index", "as_real",
        // functions
        "sum", "product", "min", "max", "mid", "forall", "exp", "log", "pow",
        "sqr", "sqrt", "abs", "inv", "sin", "asin", "cos", "acos", "tan", "atan",
        "sinh", "cosh", "tanh", "coth", "asinh", "acosh", "atanh", "acoth",
        "round", "diff",
        // special functions
        "arh", "xexpy", "xexpax", "xlogx", "xabsx", "erf", "erfc", "norm2",
        "sum_div", "xlog_sum", "single_neuron", "pos", "neg", "lb_func", "ub_func",
        "bounding_func", "squash", "regnormal", "lmtd", "rlmtd", "cost_turton",
        "covar_matern_1", "covar_matern_3", "covar_matern_5", "covar_sqrexp",
        "af_lcb", "af_ei", "af_pi", "gpdf", "nrtl_tau", "nrtl_dtau", "nrtl_g",
        "nrtl_gtau", "nrtl_gdtau", "nrtl_dgtau", "antoine_psat",
        "ext_antoine_psat", "wagner_psat", "ik_cape_psat", "antoine_tsat",
        "aspen_hig", "nasa9_hig", "dippr107_hig", "dippr127_hig", "watson_dhvap",
        "dippr106_dhvap", "schroeder_ethanol_p", "schroeder_ethanol_rhovap",
        "schroeder_ethanol_rholiq" });
}

void parser::forbid_expressions(std::vector<std::string> expressions) {
    forbidden_expressions.insert(forbidden_expressions.end(), expressions.begin(),
      expressions.end());
    lex.forbid_expressions(expressions);
}

void parser::forbid_keywords(std::vector<std::string> expressions) {
    forbidden_keywords.insert(forbidden_keywords.end(), expressions.begin(),
      expressions.end());
    lex.forbid_keywords(expressions);
}

// input handling
const token& parser::current() {
	
    const token& tok = buf.current();
	if(tok.type != token::ERROR)
	{	
		return tok;
	}
	else
	{
		report_lexical(tok);
		discard();
		token tok_ = buf.current();
		while (tok_.type == token::ERROR) {
			report_lexical(tok_);
			discard();
			tok_ = buf.current();
		}
		return buf.current();
	}
}

void parser::consume() { buf.consume(); }

void parser::discard() { buf.discard(); }

bool parser::check(token::token_type expect) {
    set_expected_token(expect);
    if(current().type != expect) {
        return false;
    }
    return true;
}

bool parser::match(token::token_type expect) {
    if(check(expect)) {
        buf.consume();
        return true;
    }
    return false;
}

bool parser::check_keyword(const std::string &expect) {
    set_expected_keyword(expect);
    if(current().type == token::KEYWORD) {
        if(current().lexeme == expect) {
            return true;
        }
    }
    return false;
}

bool parser::match_keyword(const std::string &expect) {
    if(check_keyword(expect)) {
        buf.consume();
        return true;
    }
    return false;
}

// TODO: implement check() without setting expected
void parser::recover() {
    while(current().type != token::SEMICOL && current().type != token::END) {
        consume();
    }
    consume();
    buf.clear();
}

void parser::init() { buf.mark(); }

bool parser::accept() {
    buf.unmark();
    return true;
}

bool parser::reject() {
    buf.backtrack();
    return false;
}

// parser rules
bool parser::match_addition(std::unique_ptr<value_node<real<0>>> &result) {
    return match_addition_impl(result);
}

bool parser::match_addition(std::unique_ptr<value_node<index<0>>> &result) {
    return match_addition_impl(result);
}

template <typename ResultType>
bool parser::match_addition_impl(
  std::unique_ptr<value_node<ResultType>> &result) {
    constexpr bool is_real_0 = std::is_same_v<ResultType, real<0>>;
    using result_minus_node = std::conditional_t<is_real_0, minus_node, index_minus_node>;
    using result_addition_node = std::conditional_t<is_real_0, addition_node, index_addition_node>;

    init();
    std::unique_ptr<value_node<ResultType>> child;
    if(match(token::MINUS)) {
        std::unique_ptr<value_node<ResultType>> mult;
        if(!match_multiplication(mult)) {
            return reject();
        }
        child.reset(new result_minus_node(mult.release()));
    } else if(!match_multiplication(child)) {
        return reject();
    }
    if(!check_any(token::PLUS, token::MINUS)) {
        result.reset(child.release());
        return accept();
    }
    auto parent = std::make_unique<result_addition_node>();
    parent->add_child(child.release());
    while(check_any(token::PLUS, token::MINUS)) {
        if(match(token::PLUS)) {
            if(!match_multiplication(child)) {
                return reject();
            }
            parent->add_child(child.release());
        } else if(match(token::MINUS)) {
            if(!match_multiplication(child)) {
                return reject();
            }
            auto minus = std::make_unique<result_minus_node>(child.release());
            parent->add_child(minus.release());
        }
    }
    result.reset(parent.release());
    return accept();
}

bool parser::match_multiplication(
  std::unique_ptr<value_node<real<0>>> &result) {
    init();
    std::unique_ptr<value_node<real<0>>> child;
    if(!match_exponentiation(child)) {
        return reject();
    }
    if(!check_any(token::STAR, token::SLASH)) {
        result.reset(child.release());
        return accept();
    }
    auto parent = std::make_unique<multiplication_node>();
    parent->add_child(child.release());
    while(check_any(token::STAR, token::SLASH)) {
        if(match(token::STAR)) {
            if(!match_exponentiation(child)) {
                return reject();
            }
            parent->add_child(child.release());
        } else if(match(token::SLASH)) {
            if(!match_exponentiation(child)) {
                return reject();
            }
            auto inverse = std::make_unique<inverse_node>(child.release());
            parent->add_child(inverse.release());
        }
    }
    result.reset(parent.release());
    return accept();
}

bool parser::match_multiplication(
  std::unique_ptr<value_node<index<0>>> &result) {
    init();
    std::unique_ptr<value_node<index<0>>> child;
    if(!match_primary(child)) {
        return reject();
    }
    if(!check(token::STAR)) {
        result.reset(child.release());
        return accept();
    }
    auto parent = std::make_unique<index_multiplication_node>();
    parent->add_child(child.release());
    while(match(token::STAR)) {
        if(!match_primary(child)) {
            return reject();
        }
        parent->add_child(child.release());
    }
    result.reset(parent.release());
    return accept();
}

bool parser::match_exponentiation(
  std::unique_ptr<value_node<real<0>>> &result) {
    init();
    std::unique_ptr<value_node<real<0>>> child;
    if(!match_primary(child)) {
        return reject();
    }
    if(!check(token::HAT)) {
        result.reset(child.release());
        return accept();
    }
    auto parent = std::make_unique<exponentiation_node>();
    parent->add_child(child.release());
    while(match(token::HAT)) {
        if(!match_primary(child)) {
            return reject();
        }
        parent->add_child(child.release());
    }
    result.reset(parent.release());
    return accept();
}

namespace helper {
    class pow_node : public value_node<real<0>>,
                     public kary_node<real<0>, real<0>> {
    public:
        pow_node(value_node<real<0>> *base, value_node<real<0>> *exponent) :
            kary_node<real<0>, real<0>>(base, exponent) { }

        var get_variant() override {
            throw std::invalid_argument("get_variant not implemented");
        }

        value_node<real<0>> *clone() override {
            throw std::invalid_argument("clone not implemented");
        }
    };

    class sqr_node : public value_node<real<0>>, public kary_node<real<0>> {
    public:
        sqr_node(value_node<real<0>> *base) :
            kary_node<real<0>>(base) { }

        var get_variant() override {
            throw std::invalid_argument("get_variant not implemented");
        }

        value_node<real<0>> *clone() override {
            throw std::invalid_argument("clone not implemented");
        }
    };
} // namespace helper

bool parser::match_pow(std::unique_ptr<value_node<real<0>>> &result) {
    if(match_internal_function<helper::pow_node>(result, "pow")) {
        auto node = dynamic_cast<helper::pow_node *>(result.get());
        auto [base, exponent] = node->children;

        auto exp_node = new exponentiation_node();
        exp_node->add_child(base.release());
        exp_node->add_child(exponent.release());

        result.reset(exp_node);

        return true;
    }

    return false;
}

bool parser::match_sqr(std::unique_ptr<value_node<real<0>>> &result) {
    if(match_internal_function<helper::sqr_node>(result, "sqr")) {
        auto node = dynamic_cast<helper::sqr_node *>(result.get());
        auto [base] = node->children;

        auto exp_node = new exponentiation_node();
        exp_node->add_child(base.release());
        exp_node->add_child(new constant_node<real<0>>(2));

        result.reset(exp_node);

        return true;
    }

    return false;
}

template <typename ResultType>
bool parser::match_any_internal_function(
  std::unique_ptr<value_node<ResultType>> &result) {
    if constexpr(std::is_same_v<ResultType, real<0>>) {
        return match_internal_function<index_to_real_node>(result, "as_real")

               // nary functions
               || match_internal_function<min_node>(result, "min") || match_internal_function<max_node>(result, "max") || match_internal_function<sum_div_node>(result, "sum_div") || match_internal_function<xlog_sum_node>(result, "xlog_sum") || match_internal_function<single_neuron_node>(result, "single_neuron")

               // unary functions
               || match_sqr(result) || match_internal_function<exp_node>(result, "exp") || match_internal_function<log_node>(result, "log") || match_internal_function<sqrt_node>(result, "sqrt") || match_internal_function<sin_node>(result, "sin") || match_internal_function<asin_node>(result, "asin") || match_internal_function<cos_node>(result, "cos") || match_internal_function<acos_node>(result, "acos") || match_internal_function<tan_node>(result, "tan") || match_internal_function<atan_node>(result, "atan") || match_internal_function<xlogx_node>(result, "xlogx") || match_internal_function<abs_node>(result, "abs") || match_internal_function<xabsx_node>(result, "xabsx") || match_internal_function<cosh_node>(result, "cosh") || match_internal_function<sinh_node>(result, "sinh") || match_internal_function<tanh_node>(result, "tanh") || match_internal_function<coth_node>(result, "coth") || match_internal_function<asinh_node>(result, "asinh") || match_internal_function<acosh_node>(result, "acosh") || match_internal_function<atanh_node>(result, "atanh") || match_internal_function<acoth_node>(result, "acoth") || match_internal_function<round_node>(result, "round") || match_internal_function<inverse_node>(result, "inv") || match_internal_function<erf_node>(result, "erf") || match_internal_function<erfc_node>(result, "erfc") || match_internal_function<pos_node>(result, "pos") || match_internal_function<neg_node>(result, "neg") || match_internal_function<schroeder_ethanol_p_node>(result, "schroeder_ethanol_p") || match_internal_function<schroeder_ethanol_rhovap_node>(result, "schroeder_ethanol_rhovap") || match_internal_function<schroeder_ethanol_rholiq_node>(result, "schroeder_ethanol_rholiq") || match_internal_function<covar_matern_1_node>(result, "covar_matern_1") || match_internal_function<covar_matern_3_node>(result, "covar_matern_3") || match_internal_function<covar_matern_5_node>(result, "covar_matern_5") || match_internal_function<covar_sqrexp_node>(result, "covar_sqrexp") || match_internal_function<gpdf_node>(result, "gpdf")

               // binary functions
               || match_pow(result) || match_internal_function<lmtd_node>(result, "lmtd") || match_internal_function<rlmtd_node>(result, "rlmtd") || match_internal_function<xexpax_node>(result, "xexpax") || match_internal_function<arh_node>(result, "arh") || match_internal_function<lb_func_node>(result, "lb_func") || match_internal_function<ub_func_node>(result, "ub_func") || match_internal_function<xexpy_node>(result, "xexpy") || match_internal_function<norm2_node>(result, "norm2")

               // ternary functions
               || match_internal_function<mid_node>(result, "mid") || match_internal_function<bounding_func_node>(result, "bounding_func") || match_internal_function<squash_node>(result, "squash") || match_internal_function<regnormal_node>(result, "regnormal") || match_internal_function<af_lcb_node>(result, "af_lcb") || match_internal_function<af_ei_node>(result, "af_ei") || match_internal_function<af_pi_node>(result, "af_pi")

               // quaternary functions
               || match_internal_function<nrtl_dtau_node>(result, "nrtl_dtau") || match_internal_function<antoine_psat_node>(result, "antoine_psat") || match_internal_function<antoine_tsat_node>(result, "antoine_tsat") || match_internal_function<cost_turton_node>(result, "cost_turton")

               // quinternary functions
               || match_internal_function<nrtl_tau_node>(result, "nrtl_tau")

               // senary functions
               || match_internal_function<nrtl_g_node>(result, "nrtl_g") || match_internal_function<nrtl_gtau_node>(result, "nrtl_gtau") || match_internal_function<nrtl_gdtau_node>(result, "nrtl_gdtau") || match_internal_function<nrtl_dgtau_node>(result, "nrtl_dgtau") || match_internal_function<watson_dhvap_node>(result, "watson_dhvap")

               // septenary functions
               || match_internal_function<dippr106_dhvap_node>(result,
                 "dippr106_dhvap")
               || match_internal_function<wagner_psat_node>(result, "wagner_psat") || match_internal_function<dippr107_hig_node>(result, "dippr107_hig")

               // octonary functions
               || match_internal_function<aspen_hig_node>(result, "aspen_hig") || match_internal_function<ext_antoine_psat_node>(result, "ext_antoine_psat")

               // novenary functions
               || match_internal_function<nasa9_hig_node>(result, "nasa9_hig") || match_internal_function<dippr127_hig_node>(result, "dippr127_hig")

               // udonary functions
               || match_internal_function<ik_cape_psat_node>(result, "ik_cape_psat");
    } else if constexpr(std::is_same_v<ResultType, index<0>>) {
        return match_internal_function<real_to_index_node>(result, "as_index");
    }
}

bool parser::match_disjunction(
  std::unique_ptr<value_node<boolean<0>>> &result) {
    init();
    std::unique_ptr<value_node<boolean<0>>> child;
    if(!match_conjunction(child)) {
        return reject();
    }
    if(!check(token::PIPE)) {
        result.reset(child.release());
        return accept();
    }
    auto parent = std::make_unique<disjunction_node>();
    parent->add_child(child.release());
    while(match(token::PIPE)) {
        if(!match_conjunction(child)) {
            return reject();
        }
        parent->add_child(child.release());
    }
    result.reset(parent.release());
    return accept();
}

bool parser::match_conjunction(
  std::unique_ptr<value_node<boolean<0>>> &result) {
    init();
    std::unique_ptr<value_node<boolean<0>>> child;
    if(!match_primary(child)) {
        return reject();
    }
    if(!check(token::AND)) {
        result.reset(child.release());
        return accept();
    }
    auto parent = std::make_unique<conjunction_node>();
    parent->add_child(child.release());
    while(match(token::AND)) {
        if(!match_primary(child)) {
            return reject();
        }
        parent->add_child(child.release());
    }
    result.reset(parent.release());
    return accept();
}

bool parser::match_negation(std::unique_ptr<value_node<boolean<0>>> &result) {
    init();
    if(!match(token::BANG)) {
        return reject();
    }
    std::unique_ptr<value_node<boolean<0>>> child;
    if(!match_primary(child)) {
        return reject();
    }
    result.reset(new negation_node(child.release()));
    return accept();
}

bool parser::match_literal(std::string &lit) {
    init();
    if(!check(token::LITERAL)) {
        return reject();
    }
    lit += current().lexeme;
    consume();
    return accept();
}

class symbol_check_visitor {
public:
    symbol_check_visitor(unsigned expected_dim) :
        expected_dim(expected_dim) { }

    template <typename TType>
    bool operator()(value_symbol<TType> *sym) {
        type_failure = true;
        return false;
    }

    template <typename TType>
    bool operator()(function_symbol<TType> *sym) {
        type_failure = true;
        return false;
    }

    template <typename TType>
    bool operator()(variable_symbol<TType> *sym) {
        return get_node_dimension<TType> == expected_dim;
    }

    template <typename TType>
    bool operator()(parameter_symbol<TType> *sym) {
        return get_node_dimension<TType> == expected_dim;
    }

    bool wrong_symbol_type() { return type_failure; }

private:
    unsigned expected_dim;
    bool type_failure = false;
};

template <unsigned VarDim, size_t FixedDim, unsigned IDimGrad>
bool parser::match_derivative_arguments(
  std::unique_ptr<value_node<real<IDimGrad>>> &result) {
    // new fallback point
    init();

    if constexpr(FixedDim > VarDim || (VarDim - FixedDim) > IDimGrad) {
        return reject();
    } else {
        // calculate the dimension the argument has to have such that the return
        // dimension matches IDimGrad
        constexpr int IDimArg = IDimGrad - (VarDim - FixedDim);

        // match the expression in the first argument
        std::unique_ptr<value_node<real<IDimArg>>> arg_expr;
        if(!match_value(arg_expr)) {
            return reject();
        }

        if(!match(token::COMMA)) {
            return reject();
        }

        // match name of variable being differentiated
        if(!check(token::IDENT)) {
            return reject();
        }
        std::string diff_var = current().lexeme;
        consume();

        // match fixed indexes
        std::array<size_t, FixedDim> fixed_index;
        if constexpr(FixedDim > 0) {
            if(!match(token::LBRACK)) {
                return reject();
            }

            for(int i = 0; i < FixedDim; ++i) {
                // match an index and store it
                base_index::basic_type value;
                if(!match_basic_or_evaluated<index<0>>(value)) {
                    return reject();
                }
                fixed_index.at(i) = value - 1;

                // match a comma except for the last position
                if(i < FixedDim - 1) {
                    if(!match(token::COMMA)) {
                        return reject();
                    }
                }
            }

            if(!match(token::RBRACK)) {
                return reject();
            }
        }

        // check that symbol dimension matches VarDim and it is not a function
        // symbol
        auto *sym = symbols.resolve(diff_var);
        symbol_check_visitor sym_checker(VarDim);
        if(!call_visitor(sym_checker, sym)) {
            if(sym_checker.wrong_symbol_type()) {
                set_semantic("ERROR: wrong type of symbol passed as second argument");
            }
            return reject();
        }

        // convert the expression to a value_node_ptr
        value_node_ptr<real<IDimArg>> arg_expr_value_ptr(arg_expr.release());
        // arg_expr_value_ptr.reset(arg_expr.release());

        // differentiate it and set the result
        auto result_value_ptr = differentiate_expression<VarDim>(
          arg_expr_value_ptr, diff_var, fixed_index, symbols);
        result.reset(result_value_ptr.release());
    }

    return accept();
}

template <unsigned VarDim, size_t FixedDim, unsigned IDimGrad>
bool parser::match_derivative_arguments_any(
  std::unique_ptr<value_node<real<IDimGrad>>> &result) {
    if(match_derivative_arguments<VarDim, FixedDim>(result)) {
        return true;
    }

    // recursive call (<2, 2>, <2, 1>, <2, 0>, <1, 2>, ...)
    if constexpr(FixedDim > 0) {
        return match_derivative_arguments_any<VarDim, FixedDim - 1>(result);
    } else if constexpr(VarDim > 0) {
        return match_derivative_arguments_any<VarDim - 1, LIBALE_MAX_DIM>(result);
    }

    return false;
}

template <typename TType>
bool parser::match_derivative(std::unique_ptr<value_node<TType>> &result) {
    // new fallback point
    init();

    if(!match_keyword("diff")) {
        return reject();
    }

    if(!match(token::LPAREN)) {
        return reject();
    }

    if(!match_derivative_arguments_any<LIBALE_MAX_DIM, LIBALE_MAX_DIM>(result)) {
        return reject();
    }

    if(!match(token::RPAREN)) {
        return reject();
    }
    return accept();
}

template <unsigned IDim>
bool parser::match_any_definition() {
    init();
    if(match_any_definition<IDim - 1>()) {
        return accept();
    }
    if(match_real_definition<IDim>()) {
        return accept();
    }
    if(match_integer_definition<IDim>()) {
        return accept();
    }
    if(match_binary_definition<IDim>()) {
        return accept();
    }
    if(match_definition<index<IDim>>()) {
        return accept();
    }
    if(match_definition<boolean<IDim>>()) {
        return accept();
    }
    if(match_set_definition<real<IDim>>()) {
        return accept();
    }
    if(match_set_definition<index<IDim>>()) {
        return accept();
    }
    if(match_set_definition<boolean<IDim>>()) {
        return accept();
    }
    if(match_any_function_definition<IDim>()) {
        return accept();
    }
    return reject();
}

template <>
inline bool parser::match_any_definition<0>() {
    init();
    if(match_real_definition<0>()) {
        return accept();
    }
    if(match_integer_definition<0>()) {
        return accept();
    }
    if(match_binary_definition<0>()) {
        return accept();
    }
    if(match_definition<index<0>>()) {
        return accept();
    }
    if(match_definition<boolean<0>>()) {
        return accept();
    }
    if(match_set_definition<real<0>>()) {
        return accept();
    }
    if(match_set_definition<index<0>>()) {
        return accept();
    }
    if(match_set_definition<boolean<0>>()) {
        return accept();
    }
    if(match_expr_definition<real<0>>()) {
        return accept();
    }
    if(match_expr_definition<index<0>>()) {
        return accept();
    }
    if(match_expr_definition<boolean<0>>()) {
        return accept();
    }
    if(match_any_function_definition<0>()) {
        return accept();
    }
    return reject();
}

// entry points
template <typename TType>
bool parser::match_expression(std::unique_ptr<value_node<TType>> &result) {
    init();
    if(!match_value(result)) {
        return reject();
    }
    if(!match_any(token::SEMICOL, token::END)) {
        return reject();
    }
    return accept();
}

template <typename TType>
bool parser::match_expression(std::unique_ptr<value_node<TType>> &result,
  std::string &lit) {
    init();
    if(!match_value(result)) {
        return reject();
    }
    if(!match_literal(lit)) {
        lit = "";
    }
    if(!match_any(token::SEMICOL, token::END)) {
        return reject();
    }
    return accept();
}

template <unsigned IDim>
bool parser::match_any_assignment() {
    init();
    if(match_any_assignment<IDim - 1>()) {
        return accept();
    }
    if(match_forall_assignment<IDim>()) {
        return accept();
    }
    if(match_assignment<real<IDim>>()) {
        return accept();
    }
    if(match_assignment<index<IDim>>()) {
        return accept();
    }
    if(match_assignment<boolean<IDim>>()) {
        return accept();
    }
    if(match_bound_assignment<IDim>()) {
        return accept();
    }
    if(match_init_assignment<IDim>()) {
        return accept();
    }
    if(match_prio_assignment<IDim>()) {
        return accept();
    }
    return reject();
}

template <>
inline bool parser::match_any_assignment<0>() {
    init();
    if(match_forall_assignment<0>()) {
        return accept();
    }
    if(match_assignment<real<0>>()) {
        return accept();
    }
    if(match_assignment<index<0>>()) {
        return accept();
    }
    if(match_assignment<boolean<0>>()) {
        return accept();
    }
    if(match_bound_assignment<0>()) {
        return accept();
    }
    if(match_init_assignment<0>()) {
        return accept();
    }
    if(match_prio_assignment<0>()) {
        return accept();
    }
    return reject();
}

template <unsigned IDim>
bool parser::match_any_function_definition() {
    init();
    if(match_function_definition<real<IDim>>()) {
        return accept();
    }
    if(match_function_definition<index<IDim>>()) {
        return accept();
    }
    if(match_function_definition<boolean<IDim>>()) {
        return accept();
    }
    return reject();
}

#include "parser_forward_declarations.tpp"

// error reporting
bool parser::fail() { return had_error; }

void parser::clear() { had_error = false; }

void parser::print_errors() {
    while(!errors.empty()) {
        error_stream << errors.front() << std::endl;
        errors.pop();
    }
}

void parser::set_expected_token(token::token_type type) {
    if(current().position < unexpected_token.position) {
        return;
    }
    if(current().position == unexpected_token.position) {
        expected.insert(token::string(type));
        return;
    }
    unexpected_token = current();
    expected.clear();
    expected.insert(token::string(type));
}

void parser::set_expected_keyword(std::string lexeme) {
    if(current().position < unexpected_token.position) {
        return;
    }
    if(current().position == unexpected_token.position) {
        expected.insert(lexeme);
        return;
    }
    unexpected_token = current();
    expected.clear();
    expected.insert(lexeme);
}

void parser::set_expected_symbol() {
    if(current().position > unexpected_symbol.position) {
        unexpected_symbol = current();
    }
}

void parser::set_semantic(std::string error) {
    if(current().position > semantic_token.position) {
        semantic_token = current();
        semantic_issue = error;
        semantic_issue += " on input ";
        semantic_issue += current().position_string();
    }
}

void parser::report_empty() {
    had_error = true;
    errors.push("ERROR: Empty input");
}

void parser::report_lexical(token tok) {
    had_error = true;
    std::string error = "ERROR: Unexpected character \"";
    error += tok.lexeme;
    error += "\" on input ";
    error += tok.position_string();
    errors.push(error);
}

void parser::report_internal(std::string e, token tok) {
    had_error = true;
    std::string error = "ERROR: Unexpected internal error \"";
    error += e;
    error += "\" on input ";
    error += tok.position_string();
    errors.push(error);
}

void parser::report_syntactical() {
    had_error = true;
    auto furthest = semantic_token.position;
    if(furthest < unexpected_symbol.position) {
        furthest = unexpected_symbol.position;
    }
    if(furthest < unexpected_token.position) {
        furthest = unexpected_token.position;
    }
    if(semantic_token.position == furthest) {
        errors.push(semantic_issue);
    } else if(unexpected_symbol.position == furthest) {
        std::string error;
        error += "ERROR: Unexpected symbol \"";
        error += unexpected_symbol.lexeme;
        error += "\" on input ";
        error += unexpected_symbol.position_string();
        errors.push(error);
    } else {
        std::string error;
        error += "ERROR: Unexpected token \"";
        if(unexpected_token.type == token::KEYWORD) {
            error += unexpected_token.lexeme;
        } else if(unexpected_token.type == token::FORBIDDEN_EXPRESSION) {
            error += token::string(unexpected_token.type) + ": " + unexpected_token.lexeme;
        } else if(unexpected_token.type == token::FORBIDDEN_KEYWORD) {
            error += token::string(unexpected_token.type) + ": " + unexpected_token.lexeme;
        } else {
            error += token::string(unexpected_token.type);
        }
        error += "\" on input ";
        error += unexpected_token.position_string() + ", ";
        error += "expected ";
        for(auto it = expected.begin(); it != expected.end(); ++it) {
            error += "\"" + *it + "\"";
            if(next(it) != expected.end()) {
                error += ", ";
            }
        }
        if(unexpected_token.type == token::FORBIDDEN_EXPRESSION) {
            error += "\n       List of reserved expressions: ";
            for(auto it = forbidden_expressions.begin();
                it != forbidden_expressions.end(); ++it) {
                error += "\"" + *it + "\"";
                if(next(it) != forbidden_expressions.end()) {
                    error += ", ";
                }
            }
        }
        if(unexpected_token.type == token::FORBIDDEN_KEYWORD) {
            error += "\n       List of reserved keywords: ";
            for(auto it = forbidden_keywords.begin(); it != forbidden_keywords.end();
                ++it) {
                error += "\"" + *it + "\"";
                if(next(it) != forbidden_keywords.end()) {
                    error += ", ";
                }
            }
        }
        errors.push(error);
    }
}

} // namespace ale

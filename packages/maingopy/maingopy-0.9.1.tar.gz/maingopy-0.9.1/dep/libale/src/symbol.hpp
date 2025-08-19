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

#pragma once

#include "value.hpp"
#include <limits>
#include <stdexcept>
#include <string>
#include <variant>

#include "expression.hpp"

namespace ale {

template <typename TType>
struct value_symbol;

template <typename TType>
struct function_symbol;

using value_symbol_types = typename combined_pack<
  pointer_pack_from_pack<value_symbol, real_types>::type,
  pointer_pack_from_pack<value_symbol, index_types>::type,
  pointer_pack_from_pack<value_symbol, boolean_types>::type,
  pointer_pack_from_pack<value_symbol, real_set_types>::type,
  pointer_pack_from_pack<value_symbol, index_set_types>::type,
  pointer_pack_from_pack<value_symbol, boolean_set_types>::type,
  pointer_pack_from_pack<function_symbol, real_types>::type,
  pointer_pack_from_pack<function_symbol, index_types>::type,
  pointer_pack_from_pack<function_symbol, boolean_types>::type>::type;

struct base_symbol {
    using variant = typename from_pack<std::variant, value_symbol_types>::type;
    virtual ~base_symbol() {};
    virtual variant get_base_variant() = 0;
    // virtual variant get_base_variant() const = 0;
    virtual base_symbol *clone() = 0;
    virtual base_symbol *clone() const = 0;
};

template <typename TType>
struct parameter_symbol;

template <typename TType>
class variable_symbol;

template <typename TType>
struct expression_symbol;

template <typename TType>
struct value_symbol : public base_symbol {
    base_symbol::variant get_base_variant() final {
        return static_cast<value_symbol<TType> *>(this);
    }
    using variant = std::variant<parameter_symbol<TType> *>;
    virtual variant get_value_variant() = 0;
};

template <unsigned IDim>
struct value_symbol<real<IDim>> : public base_symbol {
    base_symbol::variant get_base_variant() override {
        return static_cast<value_symbol<real<IDim>> *>(this);
    }
    using variant = std::variant<parameter_symbol<real<IDim>> *,
      variable_symbol<real<IDim>> *,
      expression_symbol<real<IDim>> *>;
    virtual variant get_value_variant() = 0;
};

// added for compatibility of VS19 V16.11.23 -- begin
// error C2908
template <>
struct value_symbol<index<0>>;

template <>
struct value_symbol<boolean<0>>;
// added for compatibility of VS19 V16.11.23 -- end

template <>
struct value_symbol<real<0>> : public base_symbol {
    base_symbol::variant get_base_variant() override {
        return static_cast<value_symbol<real<0>> *>(this);
    }
    using variant = std::variant<parameter_symbol<real<0>> *, variable_symbol<real<0>> *,
      expression_symbol<real<0>> *>;
    virtual variant get_value_variant() = 0;
};

template <>
struct value_symbol<index<0>> : public base_symbol {
    base_symbol::variant get_base_variant() {
        return static_cast<value_symbol<index<0>> *>(this);
    }
    using variant = std::variant<parameter_symbol<index<0>> *, expression_symbol<index<0>> *>;
    virtual variant get_value_variant() = 0;
};

template <>
struct value_symbol<boolean<0>> : public base_symbol {
    base_symbol::variant get_base_variant() {
        return static_cast<value_symbol<boolean<0>> *>(this);
    }
    using variant = std::variant<parameter_symbol<boolean<0>> *,
      expression_symbol<boolean<0>> *>;
    virtual variant get_value_variant() = 0;
};

template <template <typename> typename TSymbol, typename TType>
struct derived_value_symbol : value_symbol<TType> {
    typename value_symbol<TType>::variant get_value_variant() override {
        return static_cast<TSymbol<TType> *>(this);
    }
    base_symbol *clone() final {
        return new TSymbol<TType>(static_cast<TSymbol<TType> &>(*this));
    }
    base_symbol *clone() const final {
        return new TSymbol<TType>(static_cast<const TSymbol<TType> &>(*this));
    }
};

// cant use bool in parameter symbol constructor
enum class IsPlaceholderFlag { TRUE,
    FALSE };
template <typename TType>
struct parameter_symbol : derived_value_symbol<parameter_symbol, TType> {
    using basic_type = typename TType::basic_type;
    parameter_symbol(std::string name,
      IsPlaceholderFlag is_placeholder = IsPlaceholderFlag::FALSE) :
        m_name(name),
        m_value(),
        m_is_placeholder(is_placeholder == IsPlaceholderFlag::TRUE) { }
    parameter_symbol(std::string name, basic_type value) :
        m_name(name), m_value(value) { }

    std::string m_name;
    basic_type m_value; // setter getter here is difficult since we have access
                        // like m_value[1]=5;
    // is used in parser.tpp to mark parameter_symbols that are only defined
    // without being initialized and where the evaluator should fail when
    // encountering them
    bool m_is_placeholder = false; // evaluators should check and abort if a
                                   // placeholder is being evaluated.
};

struct is_placeholder_tag { };
template <typename TAtom, unsigned IDim>
struct parameter_symbol<tensor_type<TAtom, IDim>>
    : derived_value_symbol<parameter_symbol, tensor_type<TAtom, IDim>> {
    using basic_type = typename tensor_type<TAtom, IDim>::basic_type;
    parameter_symbol(std::string name,
      IsPlaceholderFlag is_placeholder = IsPlaceholderFlag::FALSE) :
        m_name(name),
        m_value(),
        m_is_placeholder(is_placeholder == IsPlaceholderFlag::TRUE) { }
    parameter_symbol(std::string name, size_t shape[IDim],
      IsPlaceholderFlag is_placeholder = IsPlaceholderFlag::FALSE) :
        m_name(name),
        m_value(shape),
        m_is_placeholder(is_placeholder == IsPlaceholderFlag::TRUE) { }
    parameter_symbol(std::string name, std::array<size_t, IDim> shape,
      IsPlaceholderFlag is_placeholder = IsPlaceholderFlag::FALSE) :
        m_name(name),
        m_value(shape),
        m_is_placeholder(is_placeholder == IsPlaceholderFlag::TRUE) { }
    explicit parameter_symbol(std::string name, basic_type value) :
        m_name(name), m_value(value) { }

    std::string m_name;
    basic_type m_value; // setter getter here is difficult since we have access
                        // like m_value[1]=5;
    // is used in parser.tpp to mark parameter_symbols that are only defined
    // without being initialized and where the evaluator should fail when
    // encountering them
    bool m_is_placeholder = false; // evaluators should check and abort if a
                                   // placeholder is being evaluated.
};

template <typename TType>
class variable_symbol : public derived_value_symbol<variable_symbol, TType> { };

template <unsigned IDim>
class variable_symbol<real<IDim>>
    : public derived_value_symbol<variable_symbol, real<IDim>> {
    using basic_type = typename real<IDim>::basic_type;
    using ref_type = typename real<IDim>::ref_type;
    using scalar_type = typename real<IDim>::atom_type::basic_type;

public:
    variable_symbol(std::string name, bool integral = false) :
        m_name(name), m_integral(integral), m_init(), m_prio(), m_lower(),
        m_upper() { }
    variable_symbol(std::string name, size_t shape[IDim], bool integral = false) :
        m_name(name), m_integral(integral),
        m_init(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(shape, -std::numeric_limits<scalar_type>::infinity()),
        m_upper(shape, std::numeric_limits<scalar_type>::infinity()) { }
    variable_symbol(std::string name, size_t shape[IDim], std::string comment,
      bool integral = false) :
        m_name(name),
        m_integral(integral), m_comment(comment),
        m_init(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(shape, -std::numeric_limits<scalar_type>::infinity()),
        m_upper(shape, std::numeric_limits<scalar_type>::infinity()) { }
    variable_symbol(std::string name, std::array<size_t, IDim> shape,
      bool integral = false) :
        m_name(name),
        m_integral(integral),
        m_init(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(shape, -std::numeric_limits<scalar_type>::infinity()),
        m_upper(shape, std::numeric_limits<scalar_type>::infinity()) { }
    variable_symbol(std::string name, std::array<size_t, IDim> shape,
      std::string comment, bool integral = false) :
        m_name(name),
        m_integral(integral), m_comment(comment),
        m_init(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(shape, -std::numeric_limits<scalar_type>::infinity()),
        m_upper(shape, std::numeric_limits<scalar_type>::infinity()) { }
    variable_symbol(std::string name, size_t shape[IDim], scalar_type init,
      bool integral = false) :
        m_name(name),
        m_integral(integral), m_init(shape, init),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(shape, -std::numeric_limits<scalar_type>::infinity()),
        m_upper(shape, std::numeric_limits<scalar_type>::infinity()) { }
    variable_symbol(std::string name, std::array<size_t, IDim> shape,
      scalar_type init, bool integral = false) :
        m_name(name),
        m_integral(integral), m_init(shape, init),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(shape, -std::numeric_limits<scalar_type>::infinity()),
        m_upper(shape, std::numeric_limits<scalar_type>::infinity()) { }
    variable_symbol(std::string name, size_t shape[IDim], scalar_type lower,
      scalar_type upper, bool integral = false) :
        m_name(name),
        m_integral(integral),
        m_init(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(shape, lower), m_upper(shape, upper) { }
    variable_symbol(std::string name, std::array<size_t, IDim> shape,
      scalar_type lower, scalar_type upper, bool integral = false) :
        m_name(name),
        m_integral(integral),
        m_init(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(shape, lower), m_upper(shape, upper) { }

    variable_symbol(std::string name, basic_type init, bool integral = false) :
        m_name(name), m_integral(integral), m_init(init),
        m_prio(shape, std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(init.shape(), -std::numeric_limits<scalar_type>::infinity()),
        m_upper(init.shape(), std::numeric_limits<scalar_type>::infinity()) { }
    variable_symbol(std::string name, basic_type lower, basic_type upper,
      bool integral = false) :
        m_name(name),
        m_integral(integral),
        m_init(lower.shape(), std::numeric_limits<scalar_type>::quiet_NaN()),
        m_prio(lower.shape(), std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(lower), m_upper(upper) {
        for(int i = 0; i < IDim; ++i) {
            if(m_lower.shape(i) != m_upper.shape(i)) {
                throw std::invalid_argument("Attempted to construct variable_symbol "
                                            "with differently shaped bounds");
            }
        }
    }
    variable_symbol(std::string name, basic_type lower, basic_type upper,
      std::string comment, bool integral = false) :
        m_name(name),
        m_integral(integral), m_comment(comment),
        m_init(lower.shape(), std::numeric_limits<scalar_type>::quiet_NaN()),
        m_prio(lower.shape(), std::numeric_limits<scalar_type>::quiet_NaN()),
        m_lower(lower), m_upper(upper) {
        for(int i = 0; i < IDim; ++i) {
            if(m_lower.shape(i) != m_upper.shape(i)) {
                throw std::invalid_argument("Attempted to construct variable_symbol "
                                            "with differently shaped bounds");
            }
        }
    }
    bool integral() { return m_integral; }

    ref_type init() { return m_init.ref(); }

    ref_type prio() { return m_prio.ref(); }

    ref_type lower() { return m_lower.ref(); }

    ref_type upper() { return m_upper.ref(); }

    std::string comment() { return m_comment; }

    const std::array<size_t, IDim> shape() const { return m_init.shape(); }

    const size_t shape(unsigned dim) const { return m_init.shape(dim); }

    void resize(std::array<size_t, IDim> shape) {
        m_init.resize(shape, std::numeric_limits<scalar_type>::quiet_NaN());
        m_prio.resize(shape, std::numeric_limits<scalar_type>::quiet_NaN());
        m_lower.resize(shape, -std::numeric_limits<scalar_type>::infinity());
        m_upper.resize(shape, std::numeric_limits<scalar_type>::infinity());
    }

    void resize(size_t shape[IDim]) {
        m_init.resize(shape, std::numeric_limits<scalar_type>::quiet_NaN());
        m_prio.resize(shape, std::numeric_limits<scalar_type>::quiet_NaN());
        m_lower.resize(shape, -std::numeric_limits<scalar_type>::infinity());
        m_upper.resize(shape, std::numeric_limits<scalar_type>::infinity());
    }

    std::string m_name;

private:
    bool m_integral;

    basic_type m_init;
    basic_type m_prio;
    basic_type m_lower;
    basic_type m_upper;
    std::string m_comment;
};

template <>
class variable_symbol<real<0>>
    : public derived_value_symbol<variable_symbol, real<0>> {
    using basic_type = typename real<0>::basic_type;

public:
    variable_symbol(std::string name, bool integral = false) :
        m_name(name), m_init(std::numeric_limits<basic_type>::quiet_NaN()),
        m_prio(std::numeric_limits<basic_type>::quiet_NaN()),
        m_lower(-std::numeric_limits<basic_type>::infinity()),
        m_upper(std::numeric_limits<basic_type>::infinity()),
        m_integral(integral) { }
    variable_symbol(std::string name, std::string comment, bool integral = false) :
        m_name(name), m_comment(comment),
        m_init(std::numeric_limits<basic_type>::quiet_NaN()),
        m_prio(std::numeric_limits<basic_type>::quiet_NaN()),
        m_lower(-std::numeric_limits<basic_type>::infinity()),
        m_upper(std::numeric_limits<basic_type>::infinity()),
        m_integral(integral) { }
    variable_symbol(std::string name, size_t shape[0], bool integral = false) :
        variable_symbol(name, integral) { }
    variable_symbol(std::string name, std::array<size_t, 0> shape,
      bool integral = false) :
        variable_symbol(name, integral) { }
    variable_symbol(std::string name, basic_type init, bool integral = false) :
        m_name(name), m_integral(integral), m_init(init),
        m_prio(std::numeric_limits<basic_type>::quiet_NaN()),
        m_lower(-std::numeric_limits<basic_type>::infinity()),
        m_upper(std::numeric_limits<basic_type>::infinity()) { }
    variable_symbol(std::string name, basic_type lower, basic_type upper,
      bool integral = false) :
        m_name(name),
        m_integral(integral),
        m_init(std::numeric_limits<basic_type>::quiet_NaN()),
        m_prio(std::numeric_limits<basic_type>::quiet_NaN()), m_lower(lower),
        m_upper(upper) { }
    variable_symbol(std::string name, basic_type lower, basic_type upper,
      std::string comment, bool integral = false) :
        m_name(name),
        m_comment(comment), m_integral(integral),
        m_init(std::numeric_limits<basic_type>::quiet_NaN()),
        m_prio(std::numeric_limits<basic_type>::quiet_NaN()), m_lower(lower),
        m_upper(upper) { }
    bool integral() { return m_integral; }

    basic_type &init() { return m_init; }

    basic_type &prio() { return m_prio; }

    basic_type &lower() { return m_lower; }

    basic_type &upper() { return m_upper; }

    std::string comment() { return m_comment; }

    std::string m_name;

private:
    bool m_integral;
    std::string m_comment;
    basic_type m_init;
    basic_type m_prio;
    basic_type m_lower;
    basic_type m_upper;
};

template <typename TType>
struct expression_symbol : derived_value_symbol<expression_symbol, TType> {
    using basic_type = typename TType::basic_type;
    expression_symbol(std::string name, value_node<TType> *value) :
        m_name(name), m_value(value) { }
    std::string m_name;
    value_node_ptr<TType> m_value;
};

template <typename TType>
struct function_symbol : base_symbol {
    function_symbol(const std::string &name,
      const std::vector<std::string> &arg_names,
      const std::vector<size_t> &arg_dims,
      const std::vector<std::vector<size_t>> &arg_shapes,
      const std::vector<std::vector<size_t>> &arg_wildcards,
      const std::vector<size_t> &result_shape,
      const std::vector<size_t> &result_wildcards,
      value_node<TType> *exp) :
        m_name(name),
        arg_names(arg_names), arg_dims(arg_dims),
        arg_shapes(arg_shapes), arg_wildcards(arg_wildcards),
        result_shape(result_shape), result_wildcards(result_wildcards),
        expr(exp) { }

    using variant = std::variant<function_symbol<TType> *>;
    variant get_function_variant() {
        return static_cast<function_symbol<TType> *>(this);
    }
    base_symbol::variant get_base_variant() override {
        return static_cast<function_symbol<TType> *>(this);
    }
    base_symbol *clone() override {
        return new function_symbol<TType>(
          static_cast<function_symbol<TType> &>(*this));
    }
    base_symbol *clone() const override {
        return new function_symbol<TType>(
          static_cast<const function_symbol<TType> &>(*this));
    }

    std::string m_name;
    std::vector<std::string> arg_names;
    std::vector<size_t> arg_dims;
    std::vector<std::vector<size_t>> arg_shapes;
    std::vector<std::vector<size_t>> arg_wildcards;
    std::vector<size_t> result_shape;
    std::vector<size_t> result_wildcards;
    expression<TType> expr;
};

template <typename TType>
value_symbol<TType> *cast_value_symbol(base_symbol *sym) {
    if(sym == nullptr) {
        return nullptr;
    }

    auto value_variant = sym->get_base_variant();
    auto *value = std::get_if<value_symbol<TType> *>(&value_variant);
    if(value) {
        return *value;
    } else {
        return nullptr;
    }
}

template <typename TType>
class [[deprecated]] value_symbol_caster {
    [[deprecated]] value_symbol<TType> *dispatch(base_symbol *sym) {
        return cast_value_symbol<TType>(sym);
    }
};

template <typename TType>
function_symbol<TType> *cast_function_symbol(base_symbol *sym) {
    if(sym == nullptr) {
        return nullptr;
    }

    auto value_variant = sym->get_base_variant();
    auto *value = std::get_if<function_symbol<TType> *>(&value_variant);
    if(value) {
        return *value;
    } else {
        return nullptr;
    }
}

template <typename TType>
class [[deprecated]] function_symbol_caster {
    [[deprecated]] function_symbol<TType> *dispatch(base_symbol *sym) {
        return cast_function_symbol<TType>(sym);
    }
};

template <typename TType>
parameter_symbol<TType> *cast_parameter_symbol(base_symbol *sym) {
    auto *value_sym = cast_value_symbol<TType>(sym);

    if(value_sym == nullptr) {
        return nullptr;
    }

    auto value_variant = value_sym->get_value_variant();
    auto *value = std::get_if<parameter_symbol<TType> *>(&value_variant);
    if(value) {
        return *value;
    } else {
        return nullptr;
    }
}

template <typename TType>
class [[deprecated]] parameter_symbol_caster {
    [[deprecated]] parameter_symbol<TType> *dispatch(base_symbol *sym) {
        return cast_parameter_symbol<TType>(sym);
    }
};

template <typename TType>
variable_symbol<TType> *cast_variable_symbol(base_symbol *sym) {
    auto *value_sym = cast_value_symbol<TType>(sym);

    if(value_sym == nullptr) {
        return nullptr;
    }

    auto value_variant = value_sym->get_value_variant();
    auto *value = std::get_if<variable_symbol<TType> *>(&value_variant);
    if(value) {
        return *value;
    } else {
        return nullptr;
    }
}

template <typename TType>
class [[deprecated]] variable_symbol_caster {
    [[deprecated]] value_symbol<TType> *dispatch(base_symbol *sym) {
        return cast_variable_symbol<TType>(sym);
    }
};

} // namespace ale

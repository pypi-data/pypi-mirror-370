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

#define LIBALE_MAX_DIM 4
#define LIBALE_MAX_SET_DIM 1

#if(LIBALE_MAX_DIM < 1 || LIBALE_MAX_DIM > 10)
#error LIBALE_MAX_DIM must be between 1 and 10
#endif

// INT REP BLOCKS -----------------------------

// when function f is passed, this block extends f with every number from 0-n
#define REP1_INT_0(f) f(0)
#define REP1_INT_1(f) REP1_INT_0(f) f(1)
#define REP1_INT_2(f) REP1_INT_1(f) f(2)
#define REP1_INT_3(f) REP1_INT_2(f) f(3)
#define REP1_INT_4(f) REP1_INT_3(f) f(4)
#define REP1_INT_5(f) REP1_INT_4(f) f(5)
#define REP1_INT_6(f) REP1_INT_5(f) f(6)
#define REP1_INT_7(f) REP1_INT_6(f) f(7)
#define REP1_INT_8(f) REP1_INT_7(f) f(8)
#define REP1_INT_9(f) REP1_INT_8(f) f(9)

// used to call block above
#define REP1_INT(n, gen) REP1_INT_(n, gen)
#define REP1_INT_(n, gen) REP1_INT_##n(gen)

// when function f and arguments x1...x_k is passed, this block extends f with
// x1...x_k and every number from 0-n
#define REP2_INT_0(f, ...) f(__VA_ARGS__, 0)
#define REP2_INT_1(f, ...) REP2_INT_0(f, __VA_ARGS__) f(__VA_ARGS__, 1)
#define REP2_INT_2(f, ...) REP2_INT_1(f, __VA_ARGS__) f(__VA_ARGS__, 2)
#define REP2_INT_3(f, ...) REP2_INT_2(f, __VA_ARGS__) f(__VA_ARGS__, 3)
#define REP2_INT_4(f, ...) REP2_INT_3(f, __VA_ARGS__) f(__VA_ARGS__, 4)
#define REP2_INT_5(f, ...) REP2_INT_4(f, __VA_ARGS__) f(__VA_ARGS__, 5)
#define REP2_INT_6(f, ...) REP2_INT_5(f, __VA_ARGS__) f(__VA_ARGS__, 6)
#define REP2_INT_7(f, ...) REP2_INT_6(f, __VA_ARGS__) f(__VA_ARGS__, 7)
#define REP2_INT_8(f, ...) REP2_INT_7(f, __VA_ARGS__) f(__VA_ARGS__, 8)
#define REP2_INT_9(f, ...) REP2_INT_8(f, __VA_ARGS__) f(__VA_ARGS__, 9)

// used to call block above
#define REP2_INT(n, gen, ...) REP2_INT_(n, gen, __VA_ARGS__)
#define REP2_INT_(n, gen, ...) REP2_INT_##n(gen, __VA_ARGS__)

// same functionality as block above (needed for triple permutation of numbers,
// because we cannot pass functions to themselves)
#define REP3_INT_0(f, ...) f(__VA_ARGS__, 0)
#define REP3_INT_1(f, ...) REP3_INT_0(f, __VA_ARGS__) f(__VA_ARGS__, 1)
#define REP3_INT_2(f, ...) REP3_INT_1(f, __VA_ARGS__) f(__VA_ARGS__, 2)
#define REP3_INT_3(f, ...) REP3_INT_2(f, __VA_ARGS__) f(__VA_ARGS__, 3)
#define REP3_INT_4(f, ...) REP3_INT_3(f, __VA_ARGS__) f(__VA_ARGS__, 4)
#define REP3_INT_5(f, ...) REP3_INT_4(f, __VA_ARGS__) f(__VA_ARGS__, 5)
#define REP3_INT_6(f, ...) REP3_INT_5(f, __VA_ARGS__) f(__VA_ARGS__, 6)
#define REP3_INT_7(f, ...) REP3_INT_6(f, __VA_ARGS__) f(__VA_ARGS__, 7)
#define REP3_INT_8(f, ...) REP3_INT_7(f, __VA_ARGS__) f(__VA_ARGS__, 8)
#define REP3_INT_9(f, ...) REP3_INT_8(f, __VA_ARGS__) f(__VA_ARGS__, 9)

// used to call block above
#define REP3_INT(n, gen, ...) REP3_INT_(n, gen, __VA_ARGS__)
#define REP3_INT_(n, gen, ...) REP3_INT_##n(gen, __VA_ARGS__)

// same functionality as the first block, excludes zero
#define REP4_INT_1(f) f(1)
#define REP4_INT_2(f) REP4_INT_1(f) f(2)
#define REP4_INT_3(f) REP4_INT_2(f) f(3)
#define REP4_INT_4(f) REP4_INT_3(f) f(4)
#define REP4_INT_5(f) REP4_INT_4(f) f(5)
#define REP4_INT_6(f) REP4_INT_5(f) f(6)
#define REP4_INT_7(f) REP4_INT_6(f) f(7)
#define REP4_INT_8(f) REP4_INT_7(f) f(8)
#define REP4_INT_9(f) REP4_INT_8(f) f(9)

// used to call block above
#define REP4_INT(n, gen) REP4_INT_(n, gen)
#define REP4_INT_(n, gen) REP4_INT_##n(gen)

// DEFINITION TEMPLATES ----------------------- // x = int, y = type, z =
// argument, xy = int+type, s = string

// types
#define TEMPLATE template
#define CONST const
#define GENBOOL bool
#define OWNING_REF(x) owning_ref<x>
#define UNIQUE_PTR_VALUE_NODE_1(x, y, s) std::unique_ptr<value_node<y<x>>> &s
#define UNIQUE_PTR_VALUE_NODE_2(xy, s) std::unique_ptr<value_node<xy>> &s
#define VALUE_NODE_PTR(x) value_node_ptr<x>
#define REAL real
#define INDEX index
#define BOOLEAN boolean
#define SET set

// functions
#define EVALUATE_EXPRESSION(z1, z2) evaluate_expression(z1, z2);
#define PARSER_MATCH_EXPRESSION(xy, z) parser::match_expression<xy>(z);
#define PARSER_MATCH_DERIVATIVE(xy, z) parser::match_derivative<xy>(z);
#define PARSER_MATCH_ANY_DEFINITION(x) parser::match_any_definition<x>();
#define PARSER_MATCH_ANY_ASSIGNMENT(x) parser::match_any_assignment<x>();
#define PARSER_MATCH_ANY_FUNCTION_DEFINITION(x) \
    parser::match_any_function_definition<x>();
#define DIFFERENTIATE_EXPRESSION(x, z1, z2, z3, z4) \
    differentiate_expression<x>(z1, z2, z3, z4);

// UTILITY -----------------------------------------

// used when using argument with comma inside; call this first to ensure that
// the macro takes the correct arguments
#define SINGLE_ARG(...) __VA_ARGS__

// GENERATORS --------------------------------------

// used to call f with numbers from 0 to n
#define GEN_INT(n, f) REP1_INT(n, f)
// used to call f with numbers from 1 to n
#define GEN_INT_N0(n, f) REP4_INT(n, f)
// used to call f with x and numbers from 0 to n
#define GEN_DOUBLEINT(n, f, x) REP2_INT(n, f, x)
// used to call f with x1,x2 and numbers from 0 to n
#define GEN_TRIPLEINT(n, f, x1, x2) REP3_INT(n, f, x1, x2)
// used to call f with real, boolean, index and x
#define GEN_TYPE(f, x) f(x, REAL) f(x, BOOLEAN) f(x, INDEX)
// used to call f with settypes of real, boolean, index with the dimensions
// x1,x2
#define GEN_SETTYPE(f, x1, x2) \
    f(SINGLE_ARG(SET<REAL<x1>, x2>)) f(SINGLE_ARG(SET<BOOLEAN<x1>, x2>)) \
      f(SINGLE_ARG(SET<INDEX<x1>, x2>))

/*
        HOW TO ADD AN EXPLICIT INSTANTIATION / FORWARD DECLARATION
        Example: new forward declaration for function: 'value_node_ptr<y<x1>>
   do_things(std::array<size_t, x2>);' for the class C

        1. Create a new file C_forward_declarations.tpp (if it does not exist
   yet for your class). Add the following to this file:
        1. Add subgenerator (n depending on last subgenerator, C depending on
   your class) call to the main generator:           #define GEN GEN_C_1 ...
   GEN_C_n
        2. Add template macro for the actual function as last subgenerator:
   #define GEN_C_n_3(y,x1,x2) VALUE_NODE_PTR(y<x1>) do_things(std::array<size_t,
   x2>);
        3. Depending on needed varying arguments, build the other subgenerators:
   #define GEN_C_n GEN_INT(LIBALE_MAX_DIM, GEN_C_n_1) a) If just one integer is
   needed, use: 'GEN_INT(LIBALE_MAX_DIM, GEN_x_m)'.
   #define GEN_C_n_1(x) GEN_DOUBLEINT(LIBALE_MAX_DIM, GEN_C_n_2, x) b) If two
   integers are needed, use:
   #define GEN_C_n_2(x1,x2) GEN_SETTYPE(GEN_C_n_3, x1, x2) 'GEN_n
   GEN_INT(LIBALE_MAX_DIM, GEN_n_1)' and 'GEN_n_1(x)
   GEN_DOUBLEINT(LIBALE_MAX_DIM, GEN_n_m, x)'. c) If three integers are needed,
   use: 'GEN_n GEN_INT(LIBALE_MAX_DIM, GEN_n_1)' and 'GEN_n_1(x)
   GEN_DOUBLEINT(LIBALE_MAX_DIM, GEN_n_2, x)' and 'GEN_n_2(x1, x2)
   GEN_TRIPLEINT(LIBALE_MAX_DIM, GEN_n_m, x1, x2)'. d) If types are needed, use:
   'GEN_n(x) GEN_TYPE(GEN_n_m, x)'. e) If set-types are needed, use: 'GEN_n(x)
   GEN_SETTYPE(GEN_n_m, x1, x2)'. f) If a combination is needed, all of the
   properties are compatibel. Generate needed number of integers first, then
   insert types: 'GEN_n GEN_INT(LIBALE_MAX_DIM, GEN_n_1) and GEN_n_1(x)
   GEN_TYPE(GEN_n_m, x) g) If anything else is needed (e.g. different types),
   such a generator must be created at the beginning of the subgenerator list of
   this file (config.hpp)
        4. Check if one of the subgenerators function receives an argument which
                includes a comma (e.g. 'set<real<0>, 1>'). If so, put
   'SINGLE_ARG(arg)' around the argument. Otherwise, the preprocessor will see
   the argument as two arguments nad fail.
        5. To test, compile with the following to generate preprocessor output:
                'g++ -E file_name.cpp -o res.i'
        6. Add documentation for newly written subgenerators.

*/

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

#include <fstream>          // for istream
#include <memory>          // for unique_ptr
#include <queue>           // for queue
#include <string>          // for string, basic_string
#include <utility>         // for pair
#include <vector>          // for vector

#include "config.hpp"      // for LIBALE_MAX_DIM
#include "expression.hpp"  // for expression
#include "helper.hpp"      // for ale
#include "node.hpp"        // for value_node
#include "parser.hpp"      // for parser
#include "token.hpp"       // for token, token::END, ale, token::SEMICOL
#include "value.hpp"       // for boolean, index, real

namespace ale { struct symbol_table; }
namespace ale::demo {

struct parse_result
{
  std::vector<std::pair<expression<real<0>>, std::string>> first;
  std::vector<std::pair<expression<index<0>>, std::string>> second;
  std::vector<std::pair<expression<boolean<0>>, std::string>> third;
};

using namespace ale;

class batch_parser : public parser {
public:
    using parser::parser;
    

    parse_result parse() {
        std::queue<std::string>().swap(errors);
        std::vector<std::pair<expression<real<0>>, std::string>> reals;
        std::vector<std::pair<expression<boolean<0>>, std::string>> booleans;
        std::vector<std::pair<expression<index<0>>, std::string>> indices;
        match(token::END);
        if (match(token::END)) {
            report_empty();
            recover();
        }
        while (!check(token::END)) {
            // ignore any spurious semicolons
            if (match(token::SEMICOL)) {
                continue;
            }
            if (match_any_definition<LIBALE_MAX_DIM>()) {
                continue;
            }
            if (match_any_assignment<LIBALE_MAX_DIM>()) {
                continue;
            }
            {
                std::unique_ptr<value_node<real<0>>> expr;
                std::string                          note;
                if (match_expression(expr, note))
                {
                    reals.emplace_back(expr.release(), note);
                    continue;
                }
            }
            {
                std::unique_ptr<value_node<index<0>>> expr;
                std::string                           note;
                if (match_expression(expr, note))
                {
                    indices.emplace_back(expr.release(), note);
                    continue;
                }
            }
            {
                std::unique_ptr<value_node<boolean<0>>> expr;
                std::string                             note;
                if (match_expression(expr, note))
                {
                    booleans.emplace_back(expr.release(), note);
                    continue;
                }
            }

            report_syntactical();
            recover();
        }
        print_errors();
        return parse_result{reals, indices, booleans};
    }
};



}

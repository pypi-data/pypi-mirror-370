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

#include <cstddef>          // for size_t
#include <initializer_list> // for initializer_list
#include <iostream>         // for istream
#include <regex>
#include <string> // for string, basic_string
#include <vector> // for vector

#include "token.hpp" // for token, token::token_type

namespace ale {

class lexer {
public:
    lexer(std::istream &);
    token next_token();
    void reserve_keywords(std::initializer_list<std::string>);
    void forbid_expressions(std::vector<std::string>);
    void forbid_keywords(std::vector<std::string>);

private:
    char peek(unsigned n = 1);
    void skip();
    void consume();
    bool check(char, unsigned n = 1);
    bool match(char);

    void skip_space();
    void skip_comment();
    token match_number();
    token match_ident();
    token match_literal();

    token make_token(token::token_type);

    std::istream &input;

    std::vector<std::string> keywords;
    std::vector<std::string> forbidden_expressions;
    std::vector<std::string> forbidden_keywords;

    std::string lexeme;
    size_t line;
    size_t col;
};

} // namespace ale

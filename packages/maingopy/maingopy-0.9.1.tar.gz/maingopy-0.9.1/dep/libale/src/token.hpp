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

#include <iostream>
#include <string>
#include <unordered_map>

#define LIBALE_TOKEN_LIST \
    LIBALE_TOKEN(PLUS, "+") \
    LIBALE_TOKEN(MINUS, "-") \
    LIBALE_TOKEN(STAR, "*") \
    LIBALE_TOKEN(SLASH, "/") \
    LIBALE_TOKEN(HAT, "^") \
    LIBALE_TOKEN(PIPE, "|") \
    LIBALE_TOKEN(AND, "&") \
    LIBALE_TOKEN(BANG, "!") \
    LIBALE_TOKEN(EQUAL, "=") \
    LIBALE_TOKEN(LPAREN, "(") \
    LIBALE_TOKEN(RPAREN, ")") \
    LIBALE_TOKEN(LBRACK, "[") \
    LIBALE_TOKEN(RBRACK, "]") \
    LIBALE_TOKEN(LBRACE, "{") \
    LIBALE_TOKEN(RBRACE, "}") \
    LIBALE_TOKEN(COMMA, ",") \
    LIBALE_TOKEN(SEMICOL, ";") \
    LIBALE_TOKEN(DOT, ".") \
    LIBALE_TOKEN(DOTS, "..") \
    LIBALE_TOKEN(COLON, ":") \
    LIBALE_TOKEN(DEFINE, ":=") \
    LIBALE_TOKEN(LESS, "<") \
    LIBALE_TOKEN(LEQUAL, "<=") \
    LIBALE_TOKEN(ASSIGN, "<-") \
    LIBALE_TOKEN(GREATER, ">") \
    LIBALE_TOKEN(GEQUAL, ">=") \
    LIBALE_TOKEN(INTEGER, "INTEGER") \
    LIBALE_TOKEN(NUMBER, "NUMBER") \
    LIBALE_TOKEN(IDENT, "IDENT") \
    LIBALE_TOKEN(END, "END") \
    LIBALE_TOKEN(ERROR, "ERROR") \
    LIBALE_TOKEN(NONE, "NONE") \
    LIBALE_TOKEN(LITERAL, "LITERAL") \
    LIBALE_TOKEN(KEYWORD, "KEYWORD") \
    LIBALE_TOKEN(FORBIDDEN_KEYWORD, "FORBIDDEN_KEYWORD") \
    LIBALE_TOKEN(FORBIDDEN_EXPRESSION, "FORBIDDEN_EXPRESSION")

namespace ale {

struct token {
    enum token_type {
#define LIBALE_TOKEN(name, string) name,
        LIBALE_TOKEN_LIST
#undef LIBALE_TOKEN
    };

    static std::string string(token_type type) {
        switch(type) {
#define LIBALE_TOKEN(name, string) \
    case name: \
        return string;
            LIBALE_TOKEN_LIST
#undef LIBALE_TOKEN
            default:
                return "";
        }
    }

    token() :
        type(NONE), lexeme(""), position(0, 0) {};
    token(token_type type, std::string lexeme, size_t line, size_t column) :
        type(type), lexeme(lexeme), position(line, column) {};

    void print() const {
        std::cout << "<";
        std::cout << string(type);
        std::cout << ",\"" << lexeme << "\",@(" << position.first << ","
                  << position.second << ")>" << std::endl;
    };

    std::string position_string() const {
        return "line " + std::to_string(position.first) + ", column " + std::to_string(position.second);
    }

    token_type type;
    std::string lexeme;
    std::pair<size_t, size_t> position;
};

} // namespace ale

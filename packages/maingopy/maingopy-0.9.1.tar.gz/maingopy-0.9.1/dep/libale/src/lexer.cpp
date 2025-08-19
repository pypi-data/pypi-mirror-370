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

#include "lexer.hpp"

#include <algorithm> // for find
#include <ctype.h>   // for isdigit, isalpha
#include <map>       // for map
#include <regex>     // for regex_search, match_results<>::_Unchecked, smatch, _NFA, regex
#include <sstream>   // for basic_stringbuf<>::int_type, basic_stringbuf<>::pos_type, basic_stringbuf<>::__streambuf_type
#include <stdio.h>   // for EOF

namespace ale {

lexer::lexer(std::istream &input) :
    input(input), line(1), col(1) { }

void lexer::reserve_keywords(std::initializer_list<std::string> keys) {
    keywords.insert(keywords.end(), keys);
}

void lexer::forbid_expressions(std::vector<std::string> expressions) {
    forbidden_expressions.insert(forbidden_expressions.end(), expressions.begin(),
      expressions.end());
}

void lexer::forbid_keywords(std::vector<std::string> keys) {
    forbidden_keywords.insert(forbidden_keywords.end(), keys.begin(), keys.end());
}

char lexer::peek(unsigned n) {
    auto pos = input.tellg();
    input.seekg(n - 1, std::ios_base::cur);
    int next = input.peek();
    input.seekg(pos);
    if(next == EOF) {
        return 0;
    }
    return static_cast<char>(next);
}

void lexer::skip() {
    input.get();
    col++;
}

void lexer::consume() { lexeme += static_cast<char>(input.get()); }

bool lexer::check(char expect, unsigned n) { return peek(n) == expect; }

bool lexer::match(char expect) {
    if(check(expect)) {
        consume();
        return true;
    }
    return false;
}

token lexer::make_token(token::token_type type) {
    token tok(type, lexeme, line, col);
    col += lexeme.length();
    lexeme = "";
    return tok;
}

token lexer::next_token() {
    while(char next = peek()) {
        switch(next) {
            case ' ':
            case '\r':
            case '\t':
            case '\n':
                skip_space();
                continue;
            case '#':
                skip();
                skip_comment();
                continue;
            case '\"':
                return match_literal();
                continue;
            case '+':
                consume();
                return make_token(token::PLUS);
            case '-':
                consume();
                return make_token(token::MINUS);
            case '*':
                consume();
                return make_token(token::STAR);
            case '/':
                consume();
                return make_token(token::SLASH);
            case '^':
                consume();
                return make_token(token::HAT);
            case '|':
                consume();
                return make_token(token::PIPE);
            case '&':
                consume();
                return make_token(token::AND);
            case '!':
                consume();
                return make_token(token::BANG);
            case '=':
                consume();
                return make_token(token::EQUAL);
            case '(':
                consume();
                return make_token(token::LPAREN);
            case ')':
                consume();
                return make_token(token::RPAREN);
            case '[':
                consume();
                return make_token(token::LBRACK);
            case ']':
                consume();
                return make_token(token::RBRACK);
            case '{':
                consume();
                return make_token(token::LBRACE);
            case '}':
                consume();
                return make_token(token::RBRACE);
            case ',':
                consume();
                return make_token(token::COMMA);
            case ';':
                consume();
                return make_token(token::SEMICOL);
            case '.':
                consume();
                return make_token(match('.') ? token::DOTS : token::DOT);
            case ':':
                consume();
                return make_token(match('=') ? token::DEFINE : token::COLON);
            case '<':
                consume();
                if(match('=')) {
                    return make_token(token::LEQUAL);
                }
                if(match('-')) {
                    return make_token(token::ASSIGN);
                }
                return make_token(token::LESS);
            case '>':
                consume();
                return make_token(match('=') ? token::GEQUAL : token::GREATER);
            default:
                if(!((int)next > 0 && (int)next < 255)) {
                    // isdigit throws meaningless error under windows in debug if special
                    // character is detected.
                    // -> Manually create error token for user-friendly error reporting
                    consume();
                    return make_token(token::ERROR);
                } else if(isdigit(next)) {
                    return match_number();
                } else if(isalpha(next)) {
                    return match_ident();
                }
                consume();
                return make_token(token::ERROR);
        }
    }
    return make_token(token::END);
}

void lexer::skip_space() {
    while(check(' ') || check('\r') || check('\t') || check('\n')) {
        if(check('\n')) {
            line++;
            col = 0;
        }
        skip();
    }
}

void lexer::skip_comment() {
    while(peek() != 0 && !check('\n')) {
        skip();
    }
}

token lexer::match_number() {
    while(isdigit(peek())) {
        consume();
    }
    if(check('.') && check('.', 2)) {
        return make_token(token::INTEGER);
    }
    if(!check('.') && !check('e') && !check('E')) {
        return make_token(token::INTEGER);
    }
    if(match('.')) {
        while(isdigit(peek())) {
            consume();
        }
    }
    if(match('e') || match('E')) {
        match('-') || match('+');
        if(isdigit(peek())) {
            consume();
        } else {
            return make_token(token::ERROR);
        }
        while(isdigit(peek())) {
            consume();
        }
    }
    return make_token(token::NUMBER);
}

token lexer::match_ident() {
    if(isalpha(peek())) {
        consume();
    } else {
        return make_token(token::ERROR);
    }
    while(isalpha(peek()) || isdigit(peek()) || peek() == '_') {
        consume();
    }
    // TODO: accept any capitalization

    for(auto it = forbidden_expressions.begin();
        it != forbidden_expressions.end(); ++it) {
        std::smatch match;
        std::regex_search(lexeme, match, std::regex(*it));
        if(!match.empty()) {
            return make_token(token::FORBIDDEN_EXPRESSION);
        }
    }

    if(std::find(forbidden_keywords.begin(), forbidden_keywords.end(), lexeme) != forbidden_keywords.end()) {
        return make_token(token::FORBIDDEN_KEYWORD);
    }

    if(std::find(keywords.begin(), keywords.end(), lexeme) != keywords.end()) {
        return make_token(token::KEYWORD);
    }
    return make_token(token::IDENT);
}

token lexer::match_literal() {
    skip();
    while((peek() != '\"') && (peek() != '\0')) {
        consume();
    }
    if(check('\"')) {
        auto tok = make_token(token::LITERAL);
        skip();
        return tok;
    }
    return make_token(token::ERROR);
}

} // namespace ale

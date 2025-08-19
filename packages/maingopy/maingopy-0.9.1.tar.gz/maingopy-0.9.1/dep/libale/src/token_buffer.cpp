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

#include "token_buffer.hpp"

namespace ale {

token_buffer::token_buffer(lexer &lex) :
    lex(lex) {
    tokens = {};
    next = tokens.begin();
    marks = {};
}

const token& token_buffer::current() {
    if(next == tokens.end()) {
        tokens.push_back(lex.next_token());
        next--;
    }
    return *next;
}

void token_buffer::consume() { next++; }

void token_buffer::discard() { next = tokens.erase(next); }

void token_buffer::mark() {
    current();
    marks.push(next);
}

void token_buffer::unmark() { marks.pop(); }

void token_buffer::backtrack() {
    next = marks.top();
    unmark();
}

void token_buffer::clear() {
    tokens.erase(tokens.begin(), next);
    next = tokens.begin();
}

void token_buffer::purge() {
    tokens.erase(tokens.begin(), tokens.end());
    next = tokens.begin();
}

} // namespace ale

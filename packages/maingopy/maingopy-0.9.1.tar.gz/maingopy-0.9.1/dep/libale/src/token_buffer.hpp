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

#include <list>  // for list<>::iterator, list
#include <stack> // for stack

#include "lexer.hpp" // for lexer
#include "token.hpp" // for token

namespace ale {

class token_buffer {
public:
    token_buffer(lexer &);

    const token& current();
    void consume();
    void discard();

    void mark();
    void unmark();
    void backtrack();

    void clear();
    void purge();

private:
    lexer &lex;
    std::list<token> tokens = {};
    std::list<token>::iterator next = tokens.begin();
    std::stack<std::list<token>::iterator> marks = {};
};

} // namespace ale

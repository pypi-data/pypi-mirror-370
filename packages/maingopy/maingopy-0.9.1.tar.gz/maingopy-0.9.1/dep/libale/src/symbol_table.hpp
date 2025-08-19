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

#include "symbol.hpp"
#include "symbol_printer.hpp"
#include "util/owner.hpp"

#include <list>
#include <memory>
#include <set>
#include <stack>
#include <unordered_map>

namespace ale {

class symbol_stack;

class symbol_scope {
public:
    ~symbol_scope();
    void push(symbol_stack *stk) { definitions.insert(stk); }

private:
    std::set<symbol_stack *> definitions;
};

class symbol_stack {
public:
    base_symbol *top() { return bindings.top().second.get(); }

    void push(gsl::owner<base_symbol*> sym, symbol_scope *scope) {
        if(bindings.size() > 0) {
            auto &bind = bindings.top();
            if(bind.first == scope) {
                bind.second.reset(sym);
                return;
            }
        }
        bindings.emplace(scope, sym);
        scope->push(this);
    }

    void pop() { bindings.pop(); }

    void print() {
        if(!bindings.empty()) {
            std::cout << symbol_to_string(top()) << std::endl;
        } else {
            std::cout << "no definition" << std::endl;
        }
    }

    bool empty() { return bindings.empty(); }

private:
    std::stack<std::pair<symbol_scope *, std::unique_ptr<base_symbol>>> bindings;
};

inline symbol_scope::~symbol_scope() {
    for(auto it = definitions.begin(); it != definitions.end(); ++it) {
        (*it)->pop();
    }
}

struct symbol_table {
public:
    symbol_table() { push_scope(); }

    void push_scope() { scope_stack.emplace(); }

    void pop_scope() {
        // cant pop global scope
        if(scope_stack.size() > 1) {
            scope_stack.pop();
        }
    }

    template <typename TType>
    void define(std::string name, gsl::owner<value_symbol<TType>*> sym) {
        auto it = symbol_store.find(name);
        if(it != symbol_store.end()) {
            it->second.push(sym, &scope_stack.top());
        } else {
            symbol_names.push_back(name);
            symbol_store[name].push(sym, &scope_stack.top());
        }
    }

    void define(std::string name, gsl::owner<base_symbol*> sym) {
        auto it = symbol_store.find(name);
        if(it != symbol_store.end()) {
            it->second.push(sym, &scope_stack.top());
        } else {
            symbol_names.push_back(name);
            symbol_store[name].push(sym, &scope_stack.top());
        }
    }

    template <typename TType>
    value_symbol<TType> *resolve(std::string name) {
        auto it = symbol_store.find(name);
        if(it == symbol_store.end()) {
            return nullptr;
        }
        if(it->second.empty()) {
            return nullptr;
        }
        return cast_value_symbol<TType>(it->second.top());
    }

    base_symbol *resolve(std::string name) {
        auto it = symbol_store.find(name);
        if(it == symbol_store.end()) {
            return nullptr;
        }
        if(it->second.empty()) {
            return nullptr;
        }
        return it->second.top();
    }

    void print_all() {
        std::vector<std::string> keys;
        keys.reserve(symbol_store.size());
        for(auto &it : symbol_store) {
            keys.push_back(it.first);
        }
        std::sort(keys.begin(), keys.end());

        for(auto &it : keys) {
            auto sym = symbol_store.find(it);
            std::cout << "symbol " << sym->first << ": ";
            sym->second.print();
        }
    }

    void print(std::vector<std::string> syms) {
        for(auto it = syms.begin(); it != syms.end(); ++it) {
            print(*it);
        }
    }

    void print(std::string syms) {
        std::cout << "symbol " << syms << ": ";
        auto sym = symbol_store.find(syms);
        if(sym == symbol_store.end()) {
            std::cout << "undefined\n";
        } else {
            sym->second.print();
        }
    }

    const std::list<std::string> &get_names() { return symbol_names; }

private:
    std::unordered_map<std::string, symbol_stack> symbol_store;
    std::stack<symbol_scope> scope_stack;
    std::list<std::string> symbol_names;
};

// Use this instead of calling push_scope and having to make sure to call
// pop_scope at every eary return. On construction pushes a scope that is popped
// at destruction. Impossible to pop twice.
struct scope_guard {
    scope_guard(symbol_table &sym) :
        scoped_symbols(sym) {
        scoped_symbols.push_scope();
    }
    bool enabled = true;
    ~scope_guard() { trigger(); }

    // if we do not want to pop scope at destruction
    void dismiss() { enabled = false; }
    // pops scope and deactivates the trigger
    void trigger() {
        if(enabled)
            scoped_symbols.pop_scope();
        dismiss();
    }
    symbol_table &scoped_symbols;
};

} // namespace ale

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


#include <exception>           // for exception
#include <iomanip>             // for left, operator<<, setw, boolalpha
#include <iostream>            // for operator<<, cout, ostream, basic_ostream

#include "main.hpp"
#include "symbol_table.hpp"    // for symbol_table
#include "util/evaluator.hpp"  // for evaluate_expression



int main(int argc, char **argv) {

    std::cout << "initializing\n";
    std::cout << std::boolalpha;
    ale::symbol_table symbols;
    std::ifstream input;


    if (argc == 1) {
        std::cout << "no input file passed\nsetting input file to input.txt\n";
        input = std::ifstream("input.txt", std::ios::binary);
    }
    else {
        if (argc > 2) {
            std::cout << "multiple input files passed\n"
                "ignoring any addtional arguments\n"
                "setting input file to " << argv[1] << '\n';
        }
        input = std::ifstream(argv[1], std::ios::binary);
    }

    ale::demo::batch_parser par(input, symbols);
    std::cout << '\n';

    std::cout << "parsing input\n";
    ale::demo::parse_result trees;
    try {
        trees = par.parse();
    
    }
    catch (std::exception& e) {
        std::cout << "ERROR: " << e.what() << std::endl;
    }
    par.print_errors();
    std::cout << '\n';


    std::cout << "printing defined symbols\n";
    symbols.print_all();
    std::cout << '\n';

    std::cout << "evaluating expressions\n";
    std::cout << "evaluating real expressions\n";
    bool eval_fail = false;
    for (auto it = trees.first.begin(); it != trees.first.end(); ++it) {
        try {
            auto expr_result = ale::util::evaluate_expression(it->first, symbols);
            std::cout << std::setw(100) << std::left << it->second << ": " << expr_result << '\n';
        }
        catch (const std::exception& e) {
            eval_fail = true;
            std::cout << "ERROR: " << e.what() << std::endl;
        }
    }
    std::cout << "\nevaluating index expressions\n";
    for (auto it = trees.second.begin(); it != trees.second.end(); ++it) {
        try {
            auto expr_result = ale::util::evaluate_expression(it->first, symbols);
            std::cout << std::setw(100) << std::left << it->second << std::left << ": " << expr_result << '\n';
        }
        catch (const std::exception& e) {
            eval_fail = true;
            std::cout << "ERROR: " << e.what() << std::endl;
        }
    }
    std::cout << "\nevaluating bool expressions\n";
    for (auto it = trees.third.begin(); it != trees.third.end(); ++it) {
        try {
            auto expr_result = ale::util::evaluate_expression(it->first, symbols);
            std::cout << std::setw(100) << std::left << it->second << std::left << ": " << expr_result << '\n';
        }
        catch (const std::exception& e) {
            eval_fail = true;
            std::cout << "ERROR: " << e.what() << std::endl;
        }
    }

    std::cout << '\n';

    std::cout << "finished execution\n";

    if (par.fail()) {
        std::cout << "warning: encountered error during parsing\n"
            << "         please see the output above\n";
            return -1;
    }
    if (eval_fail) {
        std::cout << "warning: encountered error during evaluation\n"
            << "         please see the output above\n";
        return -1;
    }

    return 0;

}

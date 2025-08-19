/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "programParser.h"


namespace maingo {


using ale::boolean;
using ale::real;
using ale::token;
using ale::value_node;

ProgramParser::ProgramParser(std::istream& input, ale::symbol_table& symbols):
    parser(input, symbols)
{
    lex.reserve_keywords(
        {"definitions", "objective", "objectivePerData", "constraints", "outputs",
         "relaxation", "only", "squashing"});
}

void
ProgramParser::parse(Program& prog)
{
    std::queue<std::string>().swap(errors);
    match(token::END);
    if (match(token::END)) {
        report_empty();
        recover();
    }
    while (!check(token::END)) {
        if (match_keyword("definitions")) {
            if (!match(token::COLON)) {
                report_syntactical();
                recover_block();
                continue;
            }
            parse_definitions();
            continue;
        }
        if (match_keyword("objective")) {
            if (!match(token::COLON)) {
                report_syntactical();
                recover_block();
                continue;
            }
            parse_objective(prog);
            continue;
        }

        if (match_keyword("objectivePerData")) {
            if (!match(token::COLON)) {
                report_syntactical();
                recover_block();
                continue;
            }
            parse_objective_per_data(prog);
            continue;
        }

        if (match_keyword("constraints")) {
            if (!match(token::COLON)) {
                report_syntactical();
                recover_block();
                continue;
            }
            parse_constraints(prog);
            continue;
        }

        if (match_keyword("relaxation")) {
            if (!match_keyword("only") || !match_keyword("constraints") || !match(token::COLON)) {
                report_syntactical();
                recover_block();
                continue;
            }
            parse_relaxations(prog);
            continue;
        }

        if (match_keyword("squashing")) {
            if (!match_keyword("constraints") || !match(token::COLON)) {
                report_syntactical();
                recover();
                continue;
            }
            parse_squashes(prog);
            continue;
        }

        if (match_keyword("outputs")) {
            if (!match(token::COLON)) {
                report_syntactical();
                recover_block();
                continue;
            }
            parse_outputs(prog);
            continue;
        }
        report_syntactical();
        recover();
    }
    print_errors();
}

void
ProgramParser::parse_definitions()
{
    while (!check(token::END) && !check_any_keyword("definitions", "objective", "objectivePerData", "constraints", "relaxation", "squashing", "outputs")) {
        if (match_any_definition<LIBALE_MAX_DIM>()) {
            continue;
        }
        if (match_any_assignment<LIBALE_MAX_DIM>()) {
            continue;
        }
        report_syntactical();
        recover();
    }
}

void
ProgramParser::parse_objective(Program& prog)
{
    std::unique_ptr<value_node<real<0>>> expr;
    std::string note;
    if (match_expression(expr, note)) {
        prog.mObjective.emplace_back(expr.release(), note);
        return;
    }
    report_syntactical();
    recover();
}

void
ProgramParser::parse_objective_per_data(Program& prog)
{
    while (!check(token::END) && !check_any_keyword("definitions", "objective", "objectivePerData", "constraints", "relaxation", "squashing", "outputs")) {
        std::unique_ptr<value_node<boolean<0>>> expr;
        std::string note;
        if (match_expression(expr, note)) {
            prog.mObjectivePerData.emplace_back(expr.release(), note);
            return;
        }
        report_syntactical();
        recover();
    }
}

void
ProgramParser::parse_constraints(Program& prog)
{
    while (!check(token::END) && !check_any_keyword("definitions", "objective", "objectivePerData", "constraints", "relaxation", "squashing", "outputs")) {
        std::unique_ptr<value_node<boolean<0>>> expr;
        std::string note;
        if (match_expression(expr, note)) {
            prog.mConstraints.emplace_back(expr.release(), note);
            continue;
        }
        report_syntactical();
        recover();
    }
}

void
ProgramParser::parse_relaxations(Program& prog)
{
    while (!check(token::END) && !check_any_keyword("definitions", "objective", "objectivePerData", "constraints", "relaxation", "squashing", "outputs")) {
        std::unique_ptr<value_node<boolean<0>>> expr;
        std::string note;
        if (match_expression(expr, note)) {
            prog.mRelaxations.emplace_back(expr.release(), note);
            continue;
        }
        report_syntactical();
        recover();
    }
}

void
ProgramParser::parse_squashes(Program& prog)
{
    while (!check(token::END) && !check_any_keyword("definitions", "objective", "objectivePerData", "constraints", "relaxation", "squashing", "outputs")) {
        std::unique_ptr<value_node<boolean<0>>> expr;
        std::string note;
        if (match_expression(expr, note)) {
            prog.mSquashes.emplace_back(expr.release(), note);
            continue;
        }
        report_syntactical();
        recover();
    }
}

void
ProgramParser::parse_outputs(Program& prog)
{
    while (!check(token::END) && !check_any_keyword("definitions", "objective", "objectivePerData", "constraints", "relaxation", "squashing", "outputs")) {
        std::unique_ptr<value_node<real<0>>> expr;
        std::string note;
        if (match_expression(expr, note)) {
            prog.mOutputs.emplace_back(expr.release(), note);
            continue;
        }
        report_syntactical();
        recover();
    }
}

void
ProgramParser::recover_block()
{
    while (current().type != token::END && !(current().type == token::KEYWORD && (current().lexeme == "definitions" || current().lexeme == "objective" || current().lexeme == "objectivePerData" || current().lexeme == "constraints" || current().lexeme == "relaxations" || current().lexeme == "squashing" || current().lexeme == "outputs"))) {
        consume();
    }
    buf.clear();
}


}    // namespace maingo
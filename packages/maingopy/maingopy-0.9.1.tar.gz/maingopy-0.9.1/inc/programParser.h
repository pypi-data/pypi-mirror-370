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

#pragma once

#include "program.h"

#include "parser.hpp"

namespace maingo {

/**
* @class ProgramParser
* @brief Parser specialization for parsing a maingo::Program
*/
class ProgramParser: private ale::parser {
  public:
    ProgramParser(std::istream&, ale::symbol_table&); /*!< Constructor taking and input and symbol_table for definitions*/

    void parse(Program&); /*!< Function to parse the input to maingo::Program*/

    using ale::parser::clear;
    using ale::parser::fail;
    using ale::parser::print_errors;

  private:
    void parse_definitions();                /*!< Function parsing a definition block*/
    void parse_objective(Program&);          /*!< Function parsing an objective block*/
    void parse_objective_per_data(Program&); /*!< Function parsing an objective per data block for MAiNGO with growing datasets*/
    void parse_constraints(Program&);        /*!< Function parsing a constraint block*/
    void parse_relaxations(Program&);        /*!< Function parsing a relaxation-only constraint block*/
    void parse_squashes(Program&);           /*!< Function parsing a squash constraint block*/
    void parse_outputs(Program&);            /*!< Function parsing an output block*/

    void recover_block(); /*!< Function to recover from an error in block syntax*/
};


}    // namespace maingo
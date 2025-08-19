/**********************************************************************************
 * Copyright (c) 2019-2024 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "constraint.h"


using namespace maingo;


/////////////////////////////////////////////////////////////////////////
Constraint::Constraint():
    name(""), constantValue(0), type(CONSTRAINT_TYPE::TYPE_UNKNOWN), convexity(CONSTRAINT_CONVEXITY::CONV_NONE),
    monotonicity(CONSTRAINT_MONOTONICITY::MON_NONE), dependency(CONSTRAINT_DEPENDENCY::DEP_UNKNOWN), isConstant(false),
    isFeasible(true), indexOriginal(0), indexNonconstant(0), indexNonconstantUBP(0), indexConstant(0), indexLinear(0), indexNonlinear(0),
    indexType(0), indexTypeNonconstant(0), indexTypeConstant(0), nparticipatingVariables(0) 
{}


/////////////////////////////////////////////////////////////////////////
Constraint::Constraint(const CONSTRAINT_TYPE typeIn, const unsigned indexOriginalIn, const unsigned indexTypeIn, const unsigned indexNonconstantIn,
                       const unsigned indexTypeNonconstantIn, const std::string& nameIn):
    name(nameIn),
    constantValue(0), type(typeIn), convexity(CONSTRAINT_CONVEXITY::CONV_NONE),
    monotonicity(CONSTRAINT_MONOTONICITY::MON_NONE), dependency(CONSTRAINT_DEPENDENCY::DEP_UNKNOWN), isConstant(false),
    isFeasible(true), indexOriginal(indexOriginalIn), indexNonconstant(indexNonconstantIn), indexNonconstantUBP(0), indexConstant(0),
    indexLinear(0), indexNonlinear(0), indexType(indexTypeIn), indexTypeNonconstant(indexTypeNonconstantIn), indexTypeConstant(0), nparticipatingVariables(0)
{
    if (name == "") {
        std::string str;
        switch (typeIn) {
            case OBJ:
                str = "obj" + std::to_string(indexTypeIn + 1);
                break;
            case INEQ:
                str = "ineq" + std::to_string(indexTypeIn + 1);
                break;
            case EQ:
                str = "eq" + std::to_string(indexTypeIn + 1);
                break;
            case INEQ_REL_ONLY:
                str = "relOnlyIneq" + std::to_string(indexTypeIn + 1);
                break;
            case EQ_REL_ONLY:
                str = "relOnlyEq" + std::to_string(indexTypeIn + 1);
                break;
            case INEQ_SQUASH:
                str = "squashIneq" + std::to_string(indexTypeIn + 1);
                break;
            case AUX_EQ_REL_ONLY:
                str = "auxRelOnlyEq" + std::to_string(indexTypeIn + 1);
                break;
            case OUTPUT:
                str = "output" + std::to_string(indexTypeIn + 1);
                break;
            default:
                str = "constraint" + std::to_string(indexTypeIn + 1);
                break;
        }
        name = str;
    }
}


/////////////////////////////////////////////////////////////////////////
Constraint::Constraint(const CONSTRAINT_TYPE typeIn, const unsigned indexOriginalIn, const unsigned indexTypeIn,
                       const unsigned indexConstantIn, const unsigned indexTypeConstantIn, const bool isConstantIn,
                       const bool isFeasibleIn, const double valueIn, const std::string& nameIn):
    name(nameIn), constantValue(valueIn), type(typeIn), convexity(CONSTRAINT_CONVEXITY::CONV_NONE),
    monotonicity(CONSTRAINT_MONOTONICITY::MON_NONE), dependency(CONSTRAINT_DEPENDENCY::DEP_UNKNOWN), isConstant(isConstantIn),
    isFeasible(isFeasibleIn), indexOriginal(indexOriginalIn), indexNonconstant(0), indexNonconstantUBP(0), indexConstant(indexConstantIn),
    indexLinear(0), indexNonlinear(0), indexType(indexTypeIn), indexTypeNonconstant(0), indexTypeConstant(indexTypeConstantIn), nparticipatingVariables(0)
{
    if (name == "") {
        std::string str;
        switch (typeIn) {
            case OBJ:
                str = "obj" + std::to_string(indexTypeIn + 1);
                break;
            case INEQ:
                str = "ineq" + std::to_string(indexTypeIn + 1);
                break;
            case EQ:
                str = "eq" + std::to_string(indexTypeIn + 1);
                break;
            case INEQ_REL_ONLY:
                str = "relOnlyIneq" + std::to_string(indexTypeIn + 1);
                break;
            case EQ_REL_ONLY:
                str = "relOnlyEq" + std::to_string(indexTypeIn + 1);
                break;
            case INEQ_SQUASH:
                str = "squashIneq" + std::to_string(indexTypeIn + 1);
                break;
            case AUX_EQ_REL_ONLY:
                str = "auxRelOnlyEq" + std::to_string(indexTypeIn + 1);
                break;
            case OUTPUT:
                str = "output" + std::to_string(indexTypeIn + 1);
                break;
            default:
                str = "constraint" + std::to_string(indexTypeIn + 1);
                break;
        }
        name = str;
    }
}
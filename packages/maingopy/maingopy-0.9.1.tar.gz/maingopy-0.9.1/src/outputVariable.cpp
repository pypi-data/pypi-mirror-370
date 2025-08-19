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

#include "outputVariable.h"


using namespace maingo;


/////////////////////////////////////////////////////////////////////////
OutputVariable::OutputVariable(const std::string descriptionIn, const mc::FFVar valueIn):
    description(descriptionIn), value(valueIn)
{}


/////////////////////////////////////////////////////////////////////////
OutputVariable:: OutputVariable(const mc::FFVar valueIn, const std::string descriptionIn):
        value(valueIn), description(descriptionIn)
{}


/////////////////////////////////////////////////////////////////////////
OutputVariable::OutputVariable(const std::tuple<mc::FFVar, std::string> tupleIn):
        value(std::get<0>(tupleIn)), description(std::get<1>(tupleIn))
{}


/////////////////////////////////////////////////////////////////////////
OutputVariable::OutputVariable(const std::tuple<std::string, mc::FFVar> tupleIn):
        value(std::get<1>(tupleIn)), description(std::get<0>(tupleIn))
{}
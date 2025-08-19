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

#include <vector>  // for vector

namespace ale {

    using VarType = std::vector<std::vector<double>>; 

    //the parameters are a, b, c, d, e, f and alpha, for further info, see ASPEN help
    VarType nrtl_subroutine_tau(double t, VarType a, VarType b, VarType e, VarType f);
    double nrtl_subroutine_tau(double t, double a, double b, double e, double f);
    VarType nrtl_subroutine_G(double t, VarType tau, VarType c, VarType d);
    double nrtl_subroutine_G(double t, double a, double b, double e, double f, double alpha);
    VarType nrtl_subroutine_Gtau(VarType G, VarType tau);
    double nrtl_subroutine_Gtau(double t, double a, double b, double e, double f, double alpha);
    double nrtl_subroutine_dtau(double t, double b, double e, double f);
    VarType nrtl_subroutine_Gdtau(double t, VarType G, VarType b, VarType e, VarType f);
    double nrtl_subroutine_Gdtau(double t, double a, double b, double e, double f, double alpha);
    double nrtl_subroutine_dGtau(double t, double a, double b, double e, double f, double alpha);

}

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

#include <string>


namespace thermo {


/**
* @class IdealFluidProperties
* @brief Struct storing all parameters needed to model an ideal fluid with constant heat capacities and using the Antoine equation for saturation pressure
*/
struct IdealFluidProperties {

    const std::string name; /*!< Name of the fluid */

    const double cpig;   /*!< Heat capacity ideal gas                   [kJ/kg*K] */
    const double cif;    /*!< Heat capacity ideal fluid                 [kJ/kg*K] */
    const double Rm;     /*!< Specific gas constant                     [kJ/kg*K] */
    const double vif;    /*!< Specific volume ideal fluid               [m^3/kg]  */
    const double A;      /*!< Parameter for Antoine equation (in bar,K) [-]       */
    const double B;      /*!< Parameter for Antoine equation (in bar,K) [K]       */
    const double C;      /*!< Parameter for Antoine equation (in bar,K) [K]       */
    const double deltaH; /*!< Evaporation enthalpy                      [kJ/kg]   */
    const double T0;     /*!< Reference temperature for evaporation     [K]       */

    /**
        * @brief Constructor accepting parameter inputs
        */
    IdealFluidProperties(const std::string nameIn, const double cpigIn, const double cifIn, const double RmIn, const double vifIn, const double AIn,
                         const double BIn, const double CIn, const double deltaHIn, const double T0in):
        name(nameIn),
        cpig(cpigIn), cif(cifIn), Rm(RmIn), vif(vifIn), A(AIn), B(BIn), C(CIn), deltaH(deltaHIn), T0(T0in) {}
};


}    // end namespace thermo
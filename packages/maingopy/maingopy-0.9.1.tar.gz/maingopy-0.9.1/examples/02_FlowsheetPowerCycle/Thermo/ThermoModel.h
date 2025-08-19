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

#include "ffunc.hpp"

#include <string>


namespace thermo {


/**
* @class ThermoModel
* @brief Abstract base class for thermo models for steam power cycles
*/
class ThermoModel {

  public:
    using Var = mc::FFVar;

    virtual ~ThermoModel() {} /*!< destructor */

    virtual Var get_h_liq_pT(const Var &p, const Var &T) const      = 0; /*!< liquid phase enthalpy as a function of pressure and temperature */
    virtual Var get_T_liq_ph(const Var &p, const Var &h) const      = 0; /*!< liquid phase temperature as a function of pressure and enthalpy */
    virtual Var get_s_liq_pT(const Var &p, const Var &T) const      = 0; /*!< liquid phase entropy as a function of pressure and temperature */
    virtual Var get_T_liq_ps(const Var &p, const Var &s) const      = 0; /*!< liquid phase temperature as a function of pressure and entropy */
    virtual Var get_h_liq_ps(const Var &p, const Var &s) const      = 0; /*!< liquid phase enthalpy as a function of pressure and entropy */
    virtual Var get_s_liq_ph(const Var &p, const Var &h) const      = 0; /*!< liquid phase entropy as a function of pressure and enthalpy */
    virtual Var get_h_vap_pT(const Var &p, const Var &T) const      = 0; /*!< vapor phase enthalpy as a function of pressure and temperature */
    virtual Var get_T_vap_ph(const Var &p, const Var &h) const      = 0; /*!< vapor phase temperature as a function of pressure and enthalpy */
    virtual Var get_s_vap_pT(const Var &p, const Var &T) const      = 0; /*!< vapor phase entropy as a function of pressure and temperature */
    virtual Var get_T_vap_ps(const Var &p, const Var &s) const      = 0; /*!< vapor phase temperature as a function of pressure and entropy */
    virtual Var get_h_vap_ps(const Var &p, const Var &s) const      = 0; /*!< vapor phase enthalpy as a function of pressure and entropy */
    virtual Var get_s_vap_ph(const Var &p, const Var &h) const      = 0; /*!< vapor phase entropy as a function of pressure and enthalpy */
    virtual Var get_h_px(const Var &p, const Var &x) const          = 0; /*!< saturation temperature as a function of pressure */
    virtual Var get_h_Tx(const Var &T, const Var &x) const          = 0; /*!< saturation pressure as a function of temperature */
    virtual Var get_s_px(const Var &p, const Var &x) const          = 0; /*!< saturated liquid enthalpy as a function of pressure */
    virtual Var get_s_Tx(const Var &T, const Var &x) const          = 0; /*!< saturated vapor enthalpy as a function of pressure */
    virtual Var get_x_ph(const Var &p, const Var &h) const          = 0; /*!< saturated liquid entropy as a function of pressure */
    virtual Var get_x_ps(const Var &p, const Var &s) const          = 0; /*!< saturated vapor entropy as a function of pressure */
    virtual Var get_Ts_p(const Var &p) const                        = 0; /*!< saturation temperature as a function of pressure */
    virtual Var get_ps_T(const Var &T) const                        = 0; /*!< saturation pressure as a function of temperature */
    virtual Var get_hliq_p(const Var &p) const                      = 0; /*!< saturated liquid enthalpy as a function of pressure */
    virtual Var get_hvap_p(const Var &p) const                      = 0; /*!< saturated vapor enthalpy as a function of pressure */
    virtual Var get_hliq_T(const Var &T) const                      = 0; /*!< saturated liquid entropy as a function of pressure */
    virtual Var get_hvap_T(const Var &T) const                      = 0; /*!< saturated vapor entropy as a function of pressure */
    virtual Var get_sliq_p(const Var &p) const                      = 0; /*!< saturated liquid enthalpy as a function of temperature */
    virtual Var get_svap_p(const Var &p) const                      = 0; /*!< saturated vapor enthalpy as a function of temperature */
    virtual Var get_sliq_T(const Var &T) const                      = 0; /*!< saturated liquid entropy as a function of temperature */
    virtual Var get_svap_T(const Var &T) const                      = 0; /*!< saturated vapor entropy as a function of temperature */
    virtual Var get_h_twophase_ps(const Var &p, const Var &s) const = 0; /*!< two-phase enthalpy as a function of pressure and entropy */
    virtual Var get_s_twophase_ph(const Var &p, const Var &h) const = 0; /*!< two-phase entropy as a function of pressure and enthalpy */
};


}    // end namespace thermo
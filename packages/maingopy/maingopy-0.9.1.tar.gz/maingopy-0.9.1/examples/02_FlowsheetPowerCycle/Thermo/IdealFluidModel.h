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

#include "IdealFluidProperties.h"
#include "ThermoModel.h"

#include <cmath>
#include <memory>


namespace thermo {


using std::exp;
using std::log;
using std::max;


/**
* @class IdealFluidModel
* @brief Class for ideal thermodynamic model for steam power cycles
*/
class IdealFluidModel: public ThermoModel {

  public:
    IdealFluidModel(const IdealFluidProperties fluidProperties); /*!< constructor */

    Var get_h_liq_pT(const Var &p, const Var &T) const;      /*!< liquid phase enthalpy as a function of pressure and temperature */
    Var get_T_liq_ph(const Var &p, const Var &h) const;      /*!< liquid phase temperature as a function of pressure and enthalpy */
    Var get_s_liq_pT(const Var &p, const Var &T) const;      /*!< liquid phase entropy as a function of pressure and temperature */
    Var get_T_liq_ps(const Var &p, const Var &s) const;      /*!< liquid phase temperature as a function of pressure and entropy */
    Var get_h_liq_ps(const Var &p, const Var &s) const;      /*!< liquid phase enthalpy as a function of pressure and entropy */
    Var get_s_liq_ph(const Var &p, const Var &h) const;      /*!< liquid phase entropy as a function of pressure and enthalpy */
    Var get_h_vap_pT(const Var &p, const Var &T) const;      /*!< vapor phase enthalpy as a function of pressure and temperature */
    Var get_T_vap_ph(const Var &p, const Var &h) const;      /*!< vapor phase temperature as a function of pressure and enthalpy */
    Var get_s_vap_pT(const Var &p, const Var &T) const;      /*!< vapor phase entropy as a function of pressure and temperature */
    Var get_T_vap_ps(const Var &p, const Var &s) const;      /*!< vapor phase temperature as a function of pressure and entropy */
    Var get_h_vap_ps(const Var &p, const Var &s) const;      /*!< vapor phase enthalpy as a function of pressure and entropy */
    Var get_s_vap_ph(const Var &p, const Var &h) const;      /*!< vapor phase entropy as a function of pressure and enthalpy */
    Var get_Ts_p(const Var &p) const;                        /*!< saturation temperature as a function of pressure */
    Var get_ps_T(const Var &T) const;                        /*!< saturation pressure as a function of temperature */
    Var get_hliq_p(const Var &p) const;                      /*!< saturated liquid enthalpy as a function of pressure */
    Var get_hvap_p(const Var &p) const;                      /*!< saturated vapor enthalpy as a function of pressure */
    Var get_sliq_p(const Var &p) const;                      /*!< saturated liquid entropy as a function of pressure */
    Var get_svap_p(const Var &p) const;                      /*!< saturated vapor entropy as a function of pressure */
    Var get_hliq_T(const Var &T) const;                      /*!< saturated liquid enthalpy as a function of temperature */
    Var get_hvap_T(const Var &T) const;                      /*!< saturated vapor enthalpy as a function of temperature */
    Var get_sliq_T(const Var &T) const;                      /*!< saturated liquid entropy as a function of temperature */
    Var get_svap_T(const Var &T) const;                      /*!< saturated vapor entropy as a function of temperature */
    Var get_h_px(const Var &p, const Var &x) const;          /*!< enthalpy as a function of pressure and vapor quality */
    Var get_h_Tx(const Var &T, const Var &x) const;          /*!< enthalpy as a function of temperature and vapor quality */
    Var get_s_px(const Var &p, const Var &x) const;          /*!< entropy as a function of pressure and vapor quality */
    Var get_s_Tx(const Var &T, const Var &x) const;          /*!< entropy as a function of temperature and vapor quality */
    Var get_x_ph(const Var &p, const Var &h) const;          /*!< vapor quality as a function of pressure and enthalpy */
    Var get_x_ps(const Var &p, const Var &s) const;          /*!< vapor quality as a function of pressure and entropy */
    Var get_h_twophase_ps(const Var &p, const Var &s) const; /*!< two-phase enthalpy as a function of pressure and entropy */
    Var get_s_twophase_ph(const Var &p, const Var &h) const; /*!< two-phase entropy as a function of pressure and enthalpy */

  private:
    const IdealFluidProperties _fluidProperties; /*!< Struct holding all parameters for the model */
    Var _p0;                                     /*!< Reference pressure [bar]*/
};


IdealFluidModel::IdealFluidModel(const IdealFluidProperties fluidProperties):
    ThermoModel(), _fluidProperties(fluidProperties)
{
    _p0 = get_ps_T(_fluidProperties.T0);
}


IdealFluidModel::Var
IdealFluidModel::get_h_liq_pT(const Var &p, const Var &T) const
{
    return _fluidProperties.cif * (T - _fluidProperties.T0) + 1e2 * _fluidProperties.vif * (p - _p0);
}


IdealFluidModel::Var
IdealFluidModel::get_T_liq_ph(const Var &p, const Var &h) const
{
    return max(_fluidProperties.T0 + (h - 1e2 * _fluidProperties.vif * (p - _p0)) / _fluidProperties.cif, 1e-3);
}


IdealFluidModel::Var
IdealFluidModel::get_s_liq_pT(const Var &p, const Var &T) const
{
    return _fluidProperties.cif * log(T / _fluidProperties.T0);
}


IdealFluidModel::Var
IdealFluidModel::get_T_liq_ps(const Var &p, const Var &s) const
{
    return max(_fluidProperties.T0 * exp(s / _fluidProperties.cif), 1e-3);
}


IdealFluidModel::Var
IdealFluidModel::get_h_liq_ps(const Var &p, const Var &s) const
{
    Var T = get_T_liq_ps(p, s);
    return get_h_liq_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_s_liq_ph(const Var &p, const Var &h) const
{
    Var T = get_T_liq_ph(p, h);
    return get_s_liq_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_h_vap_pT(const Var &p, const Var &T) const
{
    return _fluidProperties.deltaH + _fluidProperties.cpig * (T - _fluidProperties.T0);
}


IdealFluidModel::Var
IdealFluidModel::get_T_vap_ph(const Var &p, const Var &h) const
{
    return max(_fluidProperties.T0 + (h - _fluidProperties.deltaH) / _fluidProperties.cpig, 1e-3);
}


IdealFluidModel::Var
IdealFluidModel::get_s_vap_pT(const Var &p, const Var &T) const
{
    return _fluidProperties.deltaH / _fluidProperties.T0 + _fluidProperties.cpig * log(T / _fluidProperties.T0) - _fluidProperties.Rm * log(p / _p0);
}


IdealFluidModel::Var
IdealFluidModel::get_T_vap_ps(const Var &p, const Var &s) const
{
    return max(_fluidProperties.T0 * exp((s - _fluidProperties.deltaH / _fluidProperties.T0 + _fluidProperties.Rm * log(p / _p0)) / _fluidProperties.cpig), 1e-3);
}


IdealFluidModel::Var
IdealFluidModel::get_h_vap_ps(const Var &p, const Var &s) const
{
    Var T = get_T_vap_ps(p, s);
    return get_h_vap_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_s_vap_ph(const Var &p, const Var &h) const
{
    Var T = get_T_vap_ph(p, h);
    return get_s_vap_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_Ts_p(const Var &p) const
{
    return saturation_temperature(p, 2, _fluidProperties.A, _fluidProperties.B, _fluidProperties.C);
}


IdealFluidModel::Var
IdealFluidModel::get_ps_T(const Var &T) const
{
    return vapor_pressure(T, 2, _fluidProperties.A, _fluidProperties.B, _fluidProperties.C);
}


IdealFluidModel::Var
IdealFluidModel::get_hliq_p(const Var &p) const
{
    Var T = get_Ts_p(p);
    return get_h_liq_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_hvap_p(const Var &p) const
{
    Var T = get_Ts_p(p);
    return get_h_vap_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_sliq_p(const Var &p) const
{
    Var T = get_Ts_p(p);
    return get_s_liq_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_svap_p(const Var &p) const
{
    Var T = get_Ts_p(p);
    return get_s_vap_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_hliq_T(const Var &T) const
{
    Var p = get_ps_T(T);
    return get_h_liq_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_hvap_T(const Var &T) const
{
    Var p = get_ps_T(T);
    return get_h_vap_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_sliq_T(const Var &T) const
{
    Var p = get_ps_T(T);
    return get_s_liq_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_svap_T(const Var &T) const
{
    Var p = get_ps_T(T);
    return get_s_vap_pT(p, T);
}


IdealFluidModel::Var
IdealFluidModel::get_h_px(const Var &p, const Var &x) const
{
    Var hliq = get_hliq_p(p);
    Var hvap = get_hvap_p(p);
    return x * hvap + (1 - x) * hliq;
}


IdealFluidModel::Var
IdealFluidModel::get_h_Tx(const Var &T, const Var &x) const
{
    Var hliq = get_hliq_T(T);
    Var hvap = get_hvap_T(T);
    return x * hvap + (1 - x) * hliq;
}


IdealFluidModel::Var
IdealFluidModel::get_s_px(const Var &p, const Var &x) const
{
    Var sliq = get_sliq_p(p);
    Var svap = get_svap_p(p);
    return x * svap + (1 - x) * sliq;
}


IdealFluidModel::Var
IdealFluidModel::get_s_Tx(const Var &T, const Var &x) const
{
    Var sliq = get_sliq_T(T);
    Var svap = get_svap_T(T);
    return x * svap + (1 - x) * sliq;
}


IdealFluidModel::Var
IdealFluidModel::get_x_ph(const Var &p, const Var &h) const
{
    Var hliq = get_hliq_p(p);
    Var hvap = get_hvap_p(p);
    return (h - hliq) / (hvap - hliq);
}


IdealFluidModel::Var
IdealFluidModel::get_x_ps(const Var &p, const Var &s) const
{
    Var sliq = get_sliq_p(p);
    Var svap = get_svap_p(p);
    return (s - sliq) / (svap - sliq);
}


IdealFluidModel::Var
IdealFluidModel::get_h_twophase_ps(const Var &p, const Var &s) const
{
    Var x = get_x_ps(p, s);
    return get_h_px(p, x);
}


IdealFluidModel::Var
IdealFluidModel::get_s_twophase_ph(const Var &p, const Var &h) const
{
    Var x = get_x_ph(p, h);
    return get_s_px(p, x);
}


}    // end namespace thermo
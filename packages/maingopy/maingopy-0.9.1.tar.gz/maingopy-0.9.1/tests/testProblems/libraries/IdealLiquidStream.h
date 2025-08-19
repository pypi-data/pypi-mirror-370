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

#ifndef IDEALLIQUIDSTREAM_H_
#define IDEALLIQUIDSTREAM_H_


#include "usingAdditionalIntrinsicFunctions.h"

#include "IdealFluid.h"

using T = mc::FFVar;

//Can calculate h,s,x out of p,t,h,s,x under using the functions of an ideal model
class IdealLiquidStream {
  private:
    //variables
    T _p;          //[bar]
    T _t;          //[K]
    T _h;          //[kJ/kg]
    T _s;          //[kJ/kg*K]
    T _ts;         //[K]
    T _hsatliq;    //[kJ/kg]
    //auxiliaries
    IdealFluid _fluid;
    DefinedStateVars _isVarDefined;
    ST _stateType;
    T _eps;
    T _p0;    //[bar] Pressure of reference state
    T _t0;    //[K] Temperature of reference state


    //functions for thermodynamic properties (h_pT == h(p,T))
    //enthalpy ideal liquid
    T hif_pT(T p, T t)
    {
        T hifResult = _fluid.cif * (t - _t0) + _fluid.vif * (p - _p0) * 1.0e2;
        return hifResult;
    }
    //entropy ideal liquid
    T sif_T(T t)
    {
        T sifResult = _fluid.cif * log(t / _t0);
        return sifResult;
    }
    //temperature (calculated from s)
    T t_sif(T s)
    {
        T tResult = _t0 * exp(s / _fluid.cif);
        return max(_eps, tResult);
    }
    //temperature (calculated from h)
    T t_hifp(T p, T h)
    {
        T tResult = (h - _fluid.vif * (p - _p0) * 1.0e2) / _fluid.cif + _t0;
        return max(_eps, tResult);
    }
    //Antoine equations
    T Ts_ps(T p)
    {
        //T tsResult = _fluid.B/(_fluid.A - (log(p)/log(10.0))) - _fluid.C;
        T tsResult = saturation_temperature(p, 2, _fluid.A, _fluid.B, _fluid.C);
        return tsResult;
    }

  public:
    // constructor
    IdealLiquidStream(IdealFluid fluid, T p0, T t0):
        _fluid(fluid),
        _p0(p0),
        _t0(t0)
    {
        _isVarDefined.setAllFalse();
        _stateType = ST_undefined;
        _eps       = 1e-8;
    }
    IdealLiquidStream() {}
    IdealLiquidStream(const IdealLiquidStream &theStream)
    {
        *this = theStream;
    }
    IdealLiquidStream &operator=(const IdealLiquidStream &theStream)
    {
        if (this != &theStream) {
            _p            = theStream._p;
            _t            = theStream._t;
            _h            = theStream._h;
            _s            = theStream._s;
            _ts           = theStream._ts;
            _hsatliq      = theStream._hsatliq;
            _fluid        = theStream._fluid;
            _p0           = theStream._p0;
            _t0           = theStream._t0;
            _eps          = theStream._eps;
            _stateType    = theStream._stateType;
            _isVarDefined = theStream._isVarDefined;
        }
        return *this;
    }
    //setter methods
    void set_pT(T p, T t)
    {
        _isVarDefined.setAllFalse();
        _p               = p;
        _t               = t;
        _ts              = Ts_ps(_p);
        _isVarDefined.p  = true;
        _isVarDefined.t  = true;
        _isVarDefined.ts = true;
        _stateType       = ST_pT;
    }
    void set_ph(T p, T h)
    {
        _isVarDefined.setAllFalse();
        _p               = p;
        _h               = h;
        _ts              = Ts_ps(_p);
        _isVarDefined.p  = true;
        _isVarDefined.h  = true;
        _isVarDefined.ts = true;
        _stateType       = ST_ph;
    }
    void set_ps(T p, T s)
    {
        _isVarDefined.setAllFalse();
        _p               = p;
        _s               = s;
        _ts              = Ts_ps(_p);
        _isVarDefined.p  = true;
        _isVarDefined.s  = true;
        _isVarDefined.ts = true;
        _stateType       = ST_ps;
    }
    void set_px(T p)
    {
        _isVarDefined.setAllFalse();
        _p                    = p;
        _ts                   = Ts_ps(_p);
        _t                    = _ts;
        _hsatliq              = hif_pT(_p, _ts);
        _isVarDefined.p       = true;
        _isVarDefined.t       = true;
        _isVarDefined.ts      = true;
        _isVarDefined.hsatliq = true;
        _stateType            = ST_px;
    }
    //getter methods
    T get_h()
    {
        if (!_isVarDefined.h) {
            _isVarDefined.h = true;
            switch (_stateType) {
                case ST_undefined:
                    std::cerr << "Error querying enthalpy of IdealStream: State not fully defined.";
                    throw(-1);
                case ST_pT:
                    _h = hif_pT(_p, _t);
                    return _h;
                case ST_ps:
                    _t              = t_sif(_s);
                    _isVarDefined.t = true;
                    _h              = hif_pT(_p, _t);
                    return _h;
                case ST_px:
                    _h = hif_pT(_p, _ts);
                    return _h;
                case ST_ph:
                    return _h;
                default:
                    std::cerr << "Fatal error: No StateType defined in IdealStream.";
                    throw(-1);
            }
        }
        else {
            return _h;
        }
    }
    T get_s()
    {
        if (!_isVarDefined.s) {
            _isVarDefined.s = true;
            switch (_stateType) {
                case ST_undefined:
                    std::cerr << "Error querying enthalpy of IdealStream: State not fully defined.";
                    throw(-1);
                case ST_pT:
                    _s = sif_T(_t);
                    return _s;
                case ST_ps:
                    return _s;
                case ST_px:
                    _s = sif_T(_ts);
                    return _s;
                case ST_ph:
                    _t              = t_hifp(_p, _h);
                    _isVarDefined.t = true;
                    _s              = sif_T(_t);
                    return _s;
                default:
                    std::cerr << "Fatal error: No StateType defined in IdealStream.";
                    throw(-1);
            }
        }
        else {
            return _s;
        }
    }
    T get_T()
    {
        if (!_isVarDefined.t) {
            _isVarDefined.t = true;
            switch (_stateType) {
                case ST_undefined:
                    std::cerr << "Error querying enthalpy of IdealStream: State not fully defined.";
                    throw(-1);
                case ST_pT:
                    return _t;
                case ST_ps:
                    _t = t_sif(_s);
                    return _t;
                case ST_px:
                    return _ts;
                case ST_ph:
                    _t = t_hifp(_p, _h);
                    return _t;
                default:
                    std::cerr << "Fatal error: No StateType defined in IdealStream.";
                    throw(-1);
            }
        }
        else {
            return _t;
        }
    }
    T get_Ts()
    {
        return _ts;
    }
    T get_hSatLiq()
    {
        if (!_isVarDefined.hsatliq) {
            _isVarDefined.hsatliq = true;
            _hsatliq              = hif_pT(_p, _ts);
            return _hsatliq;
        }
        else {
            return _hsatliq;
        }
    }
};

#endif /* IDEALLIQUIDSTREAM_H_ */

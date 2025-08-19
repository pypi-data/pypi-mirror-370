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

#ifndef IDEAL2PSTREAM_H_
#define IDEAL2PSTREAM_H_

#include "IdealFluid.h"

using T = mc::FFVar;

//Can calculate h,s,x out of p,t,h,s,x under using the functions of an ideal model
class Ideal2pStream {
  private:
    //variables
    T _p;          //[bar]
    T _h;          //[kJ/kg]
    T _s;          //[kJ/kg*K]
    T _x;          //[-]
    T _ts;         //[K]
    T _hsatliq;    //[kJ/kg]
    T _hsatvap;    //[kJ/kg]
    T _ssatliq;    //[kJ/kgK]
    T _ssatvap;    //[kJ/kgK]
    //auxiliaries
    IdealFluid _fluid;
    DefinedStateVars _isVarDefined;
    ST _stateType;
    T _eps;
    T _p0;    //[bar] Pressure of reference state
    T _t0;    //[K] Temperature of reference state


    //functions for thermodynamic properties (h_pT == h(p,T))
    //enthalpy ideal gas
    T hig_T(T t)
    {
        T higResult = _fluid.cpig * (t - _t0) + _fluid.deltaH;
        return higResult;
    }
    //enthalpy ideal liquid
    T hif_pT(T p, T t)
    {
        T hifResult = _fluid.cif * (t - _t0) + _fluid.vif * (p - _p0) * 1e2;
        return hifResult;
    }
    //enthalpy in the 2-phase area
    T hs_x(T x)
    {
        T hsResult = (1 - x) * _hsatliq + x * _hsatvap;
        return hsResult;
    }
    //entropy ideal gas
    T sig_pT(T p, T t)
    {
        T sigResult = _fluid.cpig * log(t / _t0) - _fluid.Rm * log(p / _p0) + _fluid.deltaS;
        return sigResult;
    }
    //entropy ideal liquid
    T sif_T(T t)
    {
        T sifResult = _fluid.cif * log(t / _t0);
        return sifResult;
    }
    //entropy in the 2-phase area
    T ss_x(T x)
    {
        T ssResult = (1 - x) * _ssatliq + x * _ssatvap;
        return ssResult;
    }
    //amount-of-substance fraction
    T x_h(T h)
    {
        T xResult = (h - _hsatliq) / (_hsatvap - _hsatliq);
        return xResult;
    }
    T x_s(T s)
    {
        T xResult = (s - _ssatliq) / (_ssatvap - _ssatliq);
        return xResult;
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
    Ideal2pStream(IdealFluid fluid, T p0, T t0):
        _fluid(fluid),
        _p0(p0),
        _t0(t0)
    {
        _isVarDefined.setAllFalse();
        _stateType = ST_undefined;
        _eps       = 1e-8;
    }
    Ideal2pStream() {}
    Ideal2pStream(const Ideal2pStream &theStream)
    {
        *this = theStream;
    }
    Ideal2pStream &operator=(const Ideal2pStream &theStream)
    {
        if (this != &theStream) {
            _p            = theStream._p;
            _h            = theStream._h;
            _s            = theStream._s;
            _x            = theStream._x;
            _ts           = theStream._ts;
            _hsatliq      = theStream._hsatliq;
            _hsatvap      = theStream._hsatvap;
            _ssatliq      = theStream._ssatliq;
            _ssatvap      = theStream._ssatvap;
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
    void set_ph(T p, T h)
    {
        _isVarDefined.setAllFalse();
        _p                    = p;
        _h                    = h;
        _ts                   = Ts_ps(_p);
        _hsatliq              = hif_pT(_p, _ts);
        _hsatvap              = hig_T(_ts);
        _ssatliq              = sif_T(_ts);
        _ssatvap              = sig_pT(_p, _ts);
        _isVarDefined.p       = true;
        _isVarDefined.h       = true;
        _isVarDefined.ts      = true;
        _isVarDefined.hsatliq = true;
        _isVarDefined.hsatvap = true;
        _isVarDefined.ssatliq = true;
        _isVarDefined.ssatvap = true;
        _stateType            = ST_ph;
    }
    void set_ps(T p, T s)
    {
        _isVarDefined.setAllFalse();
        _p                    = p;
        _s                    = s;
        _ts                   = Ts_ps(_p);
        _hsatliq              = hif_pT(_p, _ts);
        _hsatvap              = hig_T(_ts);
        _ssatliq              = sif_T(_ts);
        _ssatvap              = sig_pT(_p, _ts);
        _isVarDefined.p       = true;
        _isVarDefined.s       = true;
        _isVarDefined.ts      = true;
        _isVarDefined.hsatliq = true;
        _isVarDefined.hsatvap = true;
        _isVarDefined.ssatliq = true;
        _isVarDefined.ssatvap = true;
        _stateType            = ST_ps;
    }
    void set_px(T p, T x)
    {
        _isVarDefined.setAllFalse();
        _p                    = p;
        _x                    = x;
        _ts                   = Ts_ps(_p);
        _hsatliq              = hif_pT(_p, _ts);
        _hsatvap              = hig_T(_ts);
        _ssatliq              = sif_T(_ts);
        _ssatvap              = sig_pT(_p, _ts);
        _isVarDefined.p       = true;
        _isVarDefined.x       = true;
        _isVarDefined.ts      = true;
        _isVarDefined.hsatliq = true;
        _isVarDefined.hsatvap = true;
        _isVarDefined.ssatliq = true;
        _isVarDefined.ssatvap = true;
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
                case ST_ps:
                    if (!_isVarDefined.x) {
                        _x              = x_s(_s);
                        _isVarDefined.x = true;
                    }
                    _h = hs_x(_x);
                    return _h;
                case ST_px:
                    _h = hs_x(_x);
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
                case ST_ps:
                    return _s;
                case ST_px:
                    _s = ss_x(_x);
                    return _s;
                case ST_ph:
                    if (!_isVarDefined.x) {
                        _x              = x_h(_h);
                        _isVarDefined.x = true;
                    }
                    _s = ss_x(_x);
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
    T get_x()
    {
        if (!_isVarDefined.x) {
            _isVarDefined.x = true;
            switch (_stateType) {
                case ST_undefined:
                    std::cerr << "Error querying enthalpy of IdealStream: State not fully defined.";
                    throw(-1);
                case ST_ps:
                    _x = x_s(_s);
                    return _x;
                case ST_px:
                    return _x;
                case ST_ph:
                    _x = x_h(_h);
                    return _x;
                default:
                    std::cerr << "Fatal error: No StateType defined in IdealStream.";
                    throw(-1);
            }
        }
        else {
            return _x;
        }
    }
    T get_T()
    {
        return _ts;
    }
    T get_Ts()
    {
        return _ts;
    }
    T get_hSatLiq()
    {
        return _hsatliq;
    }
    T get_hSatVap()
    {
        return _hsatvap;
    }
};

#endif /* IDEAL2PSTREAM_H_ */

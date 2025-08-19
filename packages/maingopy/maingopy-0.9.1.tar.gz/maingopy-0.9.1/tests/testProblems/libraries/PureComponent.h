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


#ifndef PURECOMPONENT_H_
#define PURECOMPONENT_H_

#include "usingAdditionalIntrinsicFunctions.h"


/**
* @class PureComponent
* @brief Class representing a pure chemical component.
*
* It stores all necessary parameters and contains functions for computing temperature- (and possibly pressure-)dependent pure component properties using different models.
* The models to be used can be selected through the set functions using the respective enums.
*/
template <typename U>
class PureComponent {

  public:
    /** 
    * @enum CPIG
    * @brief Enum for selecting the ideal gas heat capacity model to be used.
    */
    enum CPIG {
        CPIG_UNDEF = 0,
        CPIG_ASPEN,       //!< cpig = C0 + C1*T + C2*T^2 + C3*T^3 + C4*T^4 + C5*T^5
        CPIG_NASA,        //!< cpig = R*(C0/T^2 + C1/T + C2 + C3*T + C4*T^2 + C5*T^3 + C6*T^4)
        CPIG_DIPPR107,    //!< cpig = C0 + C1*((C2/T)/sinh(C2/T))^2 + C3*((C4/T)/cosh(C4/T))^2
        CPIG_DIPPR127     //!< cpig = C0 + C1*(C2/T)^2*exp(C2/T)/(exp(C2/T)-1)^2 + C3*(C4/T)^2*exp(C24T)/(exp(C4/T)-1)^2 + C5*(C6/T)^2*exp(C6/T)/(exp(C6/T)-1)^2
    };


    /**
    * @brief Constructor. Requires all necessary constant property paremeters as arguments.
    * @param[in] nameIn is the component name.
    * @param[in] mwIn is the molecular weight in kg/kmol.
    * @param[in] tcIn is the critical temperature in K.
    * @param[in] pcIn is the critical pressure in bar.
    * @param[in] vcIn is the critical volume in cm^3/mol.
    * @param[in] dh0In is the enthalpy of formation at 298.15 K in kJ/mol
    * @param[in] dg0In is the Gibbs free energy of formation at 298.15 K in kJ/mol
    */
    PureComponent(const std::string nameIn, const double mwIn, const double tcIn, const double pcIn, const double vcIn, const double dh0In, const double dg0In):
        _name(nameIn), _MW(mwIn), _Tc(tcIn), _pc(pcIn), _vc(vcIn), _dh0(dh0In), _dg0(dg0In), _pref(1.0), _Tref(298.15), _R(83.144598), _cpigModel(CPIG_UNDEF) {}


    /**
    * @brief Function for computing the pure component ideal gas enthalpy at a given temperature.
    * @param[in] T is the temperature in K.
    * @return Ideal gas enthalpy in kJ/kmol
    */
    U calculate_ideal_gas_enthalpy(const U &T) const;


    /**
    * @brief Function for computing the pure component ideal gas enthalpy at a given temperature using the envelope implemented in MC++ ASSUMING THAT IT IS MONOTONICALLY INCREASING AND CONVEX!
    * @param[in] T is the temperature in K.
    * @return Ideal gas enthalpy in kJ/kmol
    */
    U calculate_ideal_gas_enthalpy_conv(const U &T) const;


    /**
    * @brief Function for computing the pure component ideal gas entropy at a given temperature and pressure. 
    * @param[in] T is the temperature in K.
    * @param[in] p is the pressure in bar.
    * @return Ideal gas entropy in kJ/(kmol K)
    */
    U calculate_ideal_gas_entropy(const U &T, const U &p) const;


    /**
    * @brief Function for computing the pure component ideal gas Gibbs free energy at a given temperature and pressure.
    * @param[in] T is the temperature in K.
    * @param[in] p is the pressure in bar.
    * @return Ideal gas Gibbs free energy in kJ/kmol
    */
    U calculate_gibbs_free_energy(const U &T, const U &p) const;


    /**
    * @brief Functions for selecting the property models to be used.
    * @param[in] modelId is an enumerator specifying the model.
    * @param[in] parameters is a vector containing the required parameter values.
    */
    void set_heat_capacity_model(CPIG modelId, const std::vector<double> &parameters);

    /**
    * @brief Function for querying the molecular weight
    * @return Molecular weight in kg/kmol
    */
    double get_MW() const { return _MW; }

    /**
    * @brief Function for querying the critical volume
    * @return Molecular weight in cm^3/mol
    */
    double get_vcrit() const { return _vc; }


    /**
    * @brief Function for querying the standard enthalpy of formation
    * @return Standard enthalpy of formation in kJ/kmol
    */
    double get_dh0() const { return _dh0 * 1000; }

    /**
    * @brief Function for querying the Gibbs free energy of formation
    * @return Gibbs free energy of formation in kJ/kmol
    */
    double get_dg0() const { return _dg0 * 1000; }

  protected:
    const std::string _name; /*!< Name of the component                                          */
    const double _MW;        /*!< Molecular weight                           [kg/kmol]           */
    const double _Tc;        /*!< Critical temperature                       [K]                 */
    const double _pc;        /*!< Critical pressure                          [bar]               */
    const double _vc;        /*!< Critical volume                            [cm^3/mol]          */
    const double _dh0;       /*!< Standard enthalpy of formation             [kJ/mol]            */
    const double _dg0;       /*!< Standard Gibbs free energy of formation    [kJ/mol]            */

    const double _pref; /*!< Reference pressure                         [bar]               */
    const double _Tref; /*!< Reference temperature                      [K]                 */
    const double _R;    /*!< Universal gas constant                     [cm^3*bar/(mol*K)]  */

    std::vector<double> _paramsCpig; /*!< Pointer to heat capacity parameters   [K, kJ/(kmol K)]    */

    CPIG _cpigModel; /*!< Enumerator storing which ideal gas heat capacity model is used            */

  private:
    PureComponent() {}
};


template <typename U>
U
PureComponent<U>::calculate_ideal_gas_enthalpy(const U &T) const
{
    if (_paramsCpig.size() != 7) {
        throw(std::runtime_error("Pure component enthalpy queried before a heat capacity model was specified."));
    }

    switch (_cpigModel) {
        case CPIG_ASPEN:
            return _dh0 * 1000 + _paramsCpig[0] * (T - _Tref) + _paramsCpig[1] / 2 * (pow(T, 2) - pow(_Tref, 2.)) + _paramsCpig[2] / 3 * (pow(T, 3) - pow(_Tref, 3.)) + _paramsCpig[3] / 4 * (pow(T, 4) - pow(_Tref, 4.)) + _paramsCpig[4] / 5 * (pow(T, 5) - pow(_Tref, 5.)) + _paramsCpig[5] / 6 * (pow(T, 6) - pow(_Tref, 6.));
        case CPIG_NASA:
            return _dh0 * 1000 + 0.1 * _R * (-_paramsCpig[0] * (1 / T - 1 / _Tref) + _paramsCpig[1] * log(T / _Tref) + _paramsCpig[2] * (T - _Tref) + _paramsCpig[3] / 2 * (pow(T, 2) - pow(_Tref, 2.)) + _paramsCpig[4] / 3 * (pow(T, 3) - pow(_Tref, 3.)) + _paramsCpig[5] / 4 * (pow(T, 4) - pow(_Tref, 4.)) + _paramsCpig[6] / 5 * (pow(T, 5) - pow(_Tref, 5.)));
        case CPIG_DIPPR107: {
            // The DIPPR107 model is symmetric w.r.t. the sign of _paramsCpig[2] and _paramsCpig[4]. If for some reason one of them is negative, we just switch the sign to be able to use the standard integrated for
            U term1;
            if (std::fabs(_paramsCpig[2]) < mc::machprec()) {
                term1 = _paramsCpig[1] * (T - _Tref);    // The limit of x*coth(x/T) for x->0 is T
            }
            else {
                term1 = _paramsCpig[1] * std::fabs(_paramsCpig[2]) * (coth(std::fabs(_paramsCpig[2]) / T) - coth(std::fabs(_paramsCpig[2]) / _Tref));
            }
            return _dh0 * 1000 + _paramsCpig[0] * (T - _Tref) + term1 - _paramsCpig[3] * std::fabs(_paramsCpig[4]) * (tanh(std::fabs(_paramsCpig[4]) / T) - tanh(std::fabs(_paramsCpig[4]) / _Tref));
        }
        case CPIG_DIPPR127: {
            U term1, term2, term3;
            if (std::fabs(_paramsCpig[2]) < mc::machprec()) {
                term1 = _paramsCpig[1] * (T - _Tref);    // The limit of x/(exp(x/T)-1) for x->0 is T
            }
            else {
                term1 = _paramsCpig[1] * _paramsCpig[2] * (1 / (exp(_paramsCpig[2] / T) - 1) - 1 / (exp(_paramsCpig[2] / _Tref) - 1));
            }
            if (std::fabs(_paramsCpig[4]) < mc::machprec()) {
                term2 = _paramsCpig[3] * (T - _Tref);    // The limit of x/(exp(x/T)-1) for x->0 is T
            }
            else {
                term2 = _paramsCpig[3] * _paramsCpig[4] * (1 / (exp(_paramsCpig[4] / T) - 1) - 1 / (exp(_paramsCpig[4] / _Tref) - 1));
            }
            if (std::fabs(_paramsCpig[6]) < mc::machprec()) {
                term3 = _paramsCpig[5] * (T - _Tref);    // The limit of x/(exp(x/T)-1) for x->0 is T
            }
            else {
                term3 = _paramsCpig[5] * _paramsCpig[6] * (1 / (exp(_paramsCpig[6] / T) - 1) - 1 / (exp(_paramsCpig[6] / _Tref) - 1));
            }
            return _dh0 * 1000 + _paramsCpig[0] * (T - _Tref) + term1 + term2 + term3;
        }
        case CPIG_UNDEF:
            throw(std::runtime_error("Error: No ideal gas heat capacity model specified."));
        default:
            throw(std::runtime_error("Error: Unknown ideal gas heat capacity model."));
    }
}


template <typename U>
U
PureComponent<U>::calculate_ideal_gas_enthalpy_conv(const U &T) const
{
    U result{_dh0 * 1000};

    switch (_cpigModel) {
        case CPIG_ASPEN:
            return result + aspen_hig(T, _Tref, _paramsCpig[0], _paramsCpig[1], _paramsCpig[2], _paramsCpig[3], _paramsCpig[4], _paramsCpig[5]);
        case CPIG_NASA:
            return result + nasa9_hig(T, _Tref, _paramsCpig[0], _paramsCpig[1], _paramsCpig[2], _paramsCpig[3], _paramsCpig[4], _paramsCpig[5], _paramsCpig[6]);
        case CPIG_DIPPR107:
            return result + dippr107_hig(T, _Tref, _paramsCpig[0], _paramsCpig[1], _paramsCpig[2], _paramsCpig[3], _paramsCpig[4]);
        case CPIG_DIPPR127:
            return result + dippr127_hig(T, _Tref, _paramsCpig[0], _paramsCpig[1], _paramsCpig[2], _paramsCpig[3], _paramsCpig[4], _paramsCpig[5], _paramsCpig[6]);
        case CPIG_UNDEF:
            throw(std::runtime_error("Error: No ideal gas heat capacity model specified."));
        default:
            throw(std::runtime_error("Error: Unknown ideal gas heat capacity model."));
    }
}


template <typename U>
U
PureComponent<U>::calculate_ideal_gas_entropy(const U &T, const U &p) const
{
    if (_paramsCpig.size() != 7) {
        throw(std::runtime_error("Pure component entropy queried before a heat capacity model was specified."));
    }

    switch (_cpigModel) {
        case CPIG_ASPEN:
            return 1000 * (_dh0 - _dg0) / _Tref + _paramsCpig[0] * log(T / _Tref) + _paramsCpig[1] * (T - _Tref) + _paramsCpig[2] / 2 * (pow(T, 2) - pow(_Tref, 2.)) + _paramsCpig[3] / 3 * (pow(T, 3) - pow(_Tref, 3.)) + _paramsCpig[4] / 4 * (pow(T, 4) - pow(_Tref, 4.)) + _paramsCpig[5] / 5 * (pow(T, 5) - pow(_Tref, 5.)) - 0.1 * _R * log(p / _pref);
        case CPIG_NASA:
            return 1000 * (_dh0 - _dg0) / _Tref + 0.1 * _R * (-_paramsCpig[0] / 2 * (1 / pow(T, 2) - 1 / pow(_Tref, 2.)) - _paramsCpig[1] * (1 / T - 1 / _Tref) + _paramsCpig[2] * log(T / _Tref) + _paramsCpig[3] * (T - _Tref) + _paramsCpig[4] / 2 * (pow(T, 2) - pow(_Tref, 2.)) + _paramsCpig[5] / 3 * (pow(T, 3) - pow(_Tref, 3.)) + _paramsCpig[6] / 4 * (pow(T, 4) - pow(_Tref, 4.))) - 0.1 * _R * log(p / _pref);
        case CPIG_DIPPR107: {
            // The DIPPR107 model is symmetric w.r.t. the sign of _paramsCpig[2] and _paramsCpig[4]. If for some reason one of them is negative, we just switch the sign to be able to use the standard integrated for
            U CbT    = std::fabs(_paramsCpig[2]) / T;
            U CbTref = std::fabs(_paramsCpig[2]) / _Tref;
            U EbT    = std::fabs(_paramsCpig[4]) / T;
            U EbTref = std::fabs(_paramsCpig[4]) / _Tref;
            U term1;
            if (std::fabs(_paramsCpig[2]) < mc::machprec()) {
                term1 = _paramsCpig[1] * ((1. - log(sinh(CbT))) - (1. - log(sinh(CbTref))));    // The limit of x*coth(x) for x->0 is 1
            }
            else {
                term1 = _paramsCpig[1] * ((CbT * coth(CbT) - log(sinh(CbT))) - (CbTref * coth(CbTref) - log(sinh(CbTref))));
            }
            return 1000 * (_dh0 - _dg0) / _Tref + _paramsCpig[0] * log(T / _Tref) + term1 - _paramsCpig[3] * ((EbT * tanh(EbT) - log(cosh(EbT))) - (EbTref * tanh(EbTref) - log(cosh(EbTref)))) - 0.1 * _R * log(p / _pref);
        }
        case CPIG_DIPPR127: {
            // FIX!!!!
            // U term1, term2, term3;
            // if (std::fabs(_paramsCpig[2]) < mc::machprec()) {
            // term1 = _paramsCpig[1]*((T)-());
            // } else {
            // term1 = _paramsCpig[1]*((CbT/(exp(CbT)-1)-log(1-exp(-CbT))) - (CbTref/(exp(CbTref)-1)-log(1-exp(-CbTref))));
            // }
            // if (std::fabs(_paramsCpig[4]) < mc::machprec()) {
            // } else {
            // }
            // if (std::fabs(_paramsCpig[6]) < mc::machprec()) {
            // } else {
            // }
            U CbT    = _paramsCpig[2] / T;
            U CbTref = _paramsCpig[2] / _Tref;
            U EbT    = _paramsCpig[4] / T;
            U EbTref = _paramsCpig[4] / _Tref;
            U GbT    = _paramsCpig[6] / T;
            U GbTref = _paramsCpig[6] / _Tref;
            return 1000 * (_dh0 - _dg0) / _Tref + _paramsCpig[0] * log(T / _Tref) + +_paramsCpig[3] * ((EbT / (exp(EbT) - 1) - log(1 - exp(-EbT))) - (EbTref / (exp(EbTref) - 1) - log(1 - exp(-EbTref)))) + _paramsCpig[5] * ((GbT / (exp(GbT) - 1) - log(1 - exp(-GbT))) - (GbTref / (exp(GbTref) - 1) - log(1 - exp(-GbTref)))) - 0.1 * _R * log(p / _pref);
        }
        case CPIG_UNDEF:
            throw(std::runtime_error("Error: No ideal gas heat capacity model specified."));
        default:
            throw(std::runtime_error("Error: Unknown ideal gas heat capacity model."));
    }
}


template <typename U>
U
PureComponent<U>::calculate_gibbs_free_energy(const U &T, const U &p) const
{
    return calculate_ideal_gas_enthalpy(T) - T * calculate_ideal_gas_entropy(T, p);
}


template <typename U>
void
PureComponent<U>::set_heat_capacity_model(CPIG modelId, const std::vector<double> &parameters)
{
    switch (modelId) {
        case CPIG_ASPEN:
            if (parameters.size() != 6) {
                throw(std::runtime_error("Error: Aspen polynomial for ideal gas heat capacity initialized with wrong number of parameters."));
            }
            break;
        case CPIG_NASA:
            if (parameters.size() != 7) {
                throw(std::runtime_error("Error: NASA polynomial for ideal gas heat capacity initialized with wrong number of parameters."));
            }
            break;
        case CPIG_DIPPR107:
            if (parameters.size() != 5) {
                throw(std::runtime_error("Error: DIPPR equation 107 for ideal gas heat capacity initialized with wrong number of parameters."));
            }
            break;
        case CPIG_DIPPR127:
            if (parameters.size() != 7) {
                throw(std::runtime_error("Error: DIPPR equation 107 for ideal gas heat capacity  initialized with wrong number of parameters."));
            }
            break;
        default:
            throw(std::runtime_error("Error: Unknown ideal gas heat capacity model."));
    }
    _cpigModel  = modelId;
    _paramsCpig = parameters;
    while (_paramsCpig.size() < 7) {
        _paramsCpig.push_back(0.);
    }
}


#endif /* PURECOMPONENT_H_ */

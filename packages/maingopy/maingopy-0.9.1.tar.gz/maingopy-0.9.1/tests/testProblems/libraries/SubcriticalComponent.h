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


#ifndef SUBCRITICALCOMPONENT_H_
#define SUBCRITICALCOMPONENT_H_

#include "PureComponent.h"

#include "usingAdditionalIntrinsicFunctions.h"


/**
* @class SubcriticalComponent
* @brief Class representing a pure chemical component below (or only "somewhat" above) its critical point.
*
* It stores all necessary parameters and contains functions for computing temperature- (and possibly pressure-)dependent pure component properties using different models.
* The models to be used can be selected through the set functions using the respective enums.
*/
template <typename U>
class SubcriticalComponent: public PureComponent<U> {

  public:
    /** 
    * @enum PVAP
    * @brief Enum for selecting the vapor pressure model to be used.
    */
    enum PVAP {
        PVAP_UNDEF = 0,
        PVAP_XANTOINE,    //!< pvap = exp(C0 + C1/(T+C2) + C3*T + C4*ln(T) + C5*T^C6)
        PVAP_ANTOINE,     //!< pvap = 10^(C0 - C1/(T+C2))
        PVAP_WAGNER,      //!< pvap = pc * exp((C0*(1-T/Tc) + C1*(1-T/Tc)^1.5 + C2*(1-T/Tc)^2.5 + C3*(1-T/Tc)^5)/(T/Tc))
        PVAP_IKCAPE       //!< pvap = exp( C0 + C1*T + C2*T^2 + C3*T^3 + C4*T^4 + C5*T^5 + C6*T^6 + C7*T^7 + C8*T^8 + C9*T^9 )
    };

    /** 
    * @enum DHVAP
    * @brief Enum for selecting the model to be used for enthalpy of vaporization.
    */
    enum DHVAP {
        DHVAP_UNDEF = 0,
        DHVAP_WATSON,     //!< dhvap = C4 * ((1-T/Tc)/(1-C3/Tc)) ^ (C1 + C2*(1-T/Tc))
        DHVAP_DIPPR106    //!< dhvap = C1 * (1-T/Tc) ^ (C2+C3*T/Tc+C4*(T/Tc)^2+C5*(T/Tc)^3)
    };

    /** 
    * @enum VLIQ
    * @brief Enum for selecting the model to be used for liquid volume.
    */
    enum VLIQ {
        VLIQ_UNDEF = 0,
        VLIQ_CONSTANT,    //!< vliq = C0
        VLIQ_QUADRATIC    //!< vliq = C0 + C1*T + C2*T^2
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
    SubcriticalComponent(const std::string nameIn, const double mwIn, const double tcIn, const double pcIn, const double vcIn, const double dh0In, const double dg0In):
        PureComponent<U>(nameIn, mwIn, tcIn, pcIn, vcIn, dh0In, dg0In), _pvapModel(PVAP_UNDEF), _dhvapModel(DHVAP_UNDEF), _vliqModel(VLIQ_UNDEF) {}


    /**
    * @brief Function for computing the pure component vapor pressure at a given temperature.
    * @param[in] T is the temperature in K.
    * @return Vapor pressure in bar.
    */
    U calculate_vapor_pressure(const U &T) const;

    /**
    * @brief Function for computing the pure component vapor pressure at a given temperature using the envelope implemented in MC++ ASSUMING THAT IT IS MONOTONICALLY INCREASING AND CONVEX!
    * @param[in] T is the temperature in K.
    * @return Vapor pressure in bar.
    */
    U calculate_vapor_pressure_conv(const U &T) const;

    /**
    * @brief Function for computing the pure component enthalpy of vaporization at a given temperature.
    * @param[in] T is the temperature in K.
    * @return Enthalpy of vaporization in kJ/kmol
    */
    U calculate_vaporization_enthalpy(const U &T) const;

    /**
    * @brief Function for computing the pure component enthalpy of vaporization at a given temperature using the envelope implemented in MC++ ASSUMING THAT IT IS MONOTONICALLY DECREASING AND CONCAVE!
    * @param[in] T is the temperature in K.
    * @return Enthalpy of vaporization in kJ/kmol
    */
    U calculate_vaporization_enthalpy_conv(const U &T) const;

    /**
    * @brief Function for computing the pressure correction for the pure component liquid enthalpy at a given temperature and pressure. 
    * @param[in] T is the temperature in K.
    * @param[in] p is the actual pressure in bar.
    * @param[in] ps is the pressure from where correction should take place in bar.
    * @return Pressure correction for enthalpy in kJ/kmol
    */
    U calculate_liquid_enthalpy_pressure_correction(const U &T, const U &p, const U &ps) const;


    /**
    * @brief Function for computing the poynting factor at a given temperature and pressure. 
    * @param[in] T is the temperature in K.
    * @param[in] p is the actual pressure in bar.
    * @param[in] ps is the pressure from where correction should take place in bar.
    * @return Poynting factor
    */
    U calculate_poynting_factor(const U &T, const U &p, const U &ps) const;

    /**
    * @brief Functions for selecting the property models to be used.
    * @param[in] modelId is an enumerator specifying the model.
    * @param[in] parameters is a vector containing the required parameter values.
    */
    void set_vapor_pressure_model(PVAP modelId, const std::vector<double> &parameters);
    void set_enthalpy_of_vaporization_model(DHVAP modelId, const std::vector<double> &parameters);
    void set_liquid_volume_model(VLIQ modelId, const std::vector<double> &parameters);


  private:
    std::vector<double> _paramsPvap;  /*!< Pointer to vapor pressure parameters             [K, bar]        */
    std::vector<double> _paramsDhvap; /*!< Pointer to enthalpy of vaporization parameters   [K, kJ/kmol]    */
    std::vector<double> _paramsVliq;  /*!< Pointer to liquid volume parameters              [K, l/kmol]     */

    PVAP _pvapModel;   /*!< Enumerator storing which vapor pressure model is used            */
    DHVAP _dhvapModel; /*!< Enumerator storing which enthalpy of vaporization model is used  */
    VLIQ _vliqModel;   /*!< Enumerator storing which liquid volume model is used             */
};


template <typename U>
U
SubcriticalComponent<U>::calculate_vapor_pressure(const U &T) const
{
    if (_paramsPvap.size() != 10) {
        throw(std::runtime_error("Vapor pressure queried before a corresponding model was specified."));
    }

    switch (_pvapModel) {
        case PVAP_XANTOINE:
            return exp(_paramsPvap[0] + _paramsPvap[1] / (T + _paramsPvap[2]) + _paramsPvap[3] * T + _paramsPvap[4] * log(T) + _paramsPvap[5] * pow(T, _paramsPvap[6]));
        case PVAP_ANTOINE:
            return pow(10.0, _paramsPvap[0] - _paramsPvap[1] / (T + _paramsPvap[2]));
        case PVAP_WAGNER: {
            U Tr(T / PureComponent<U>::_Tc);
            return PureComponent<U>::_pc * exp((_paramsPvap[0] * (1 - Tr) + _paramsPvap[1] * pow(1 - Tr, 1.5) + _paramsPvap[2] * pow(1 - Tr, 2.5) + _paramsPvap[3] * pow(1 - Tr, 5)) / Tr);
        }
        case PVAP_IKCAPE:
            return exp(_paramsPvap[0] + _paramsPvap[1] * T + _paramsPvap[2] * pow(T, 2) + _paramsPvap[3] * pow(T, 3) + _paramsPvap[4] * pow(T, 4) + _paramsPvap[5] * pow(T, 5) + _paramsPvap[6] * pow(T, 6) + _paramsPvap[7] * pow(T, 7) + _paramsPvap[8] * pow(T, 8) + _paramsPvap[9] * pow(T, 9));
        case PVAP_UNDEF:
            throw(std::runtime_error("Error: No vapor pressure model specified."));
        default:
            throw(std::runtime_error("Error: Unknown vapor pressure model."));
    }
}


template <typename U>
U
SubcriticalComponent<U>::calculate_vapor_pressure_conv(const U &T) const
{
    switch (_pvapModel) {
        case PVAP_XANTOINE:
            return ext_antoine_psat(T, _paramsPvap[0], _paramsPvap[1], _paramsPvap[2], _paramsPvap[3], _paramsPvap[4], _paramsPvap[5], _paramsPvap[6]);
        case PVAP_ANTOINE:
            return antoine_psat(T, _paramsPvap[0], _paramsPvap[1], _paramsPvap[2]);
        case PVAP_WAGNER:
            return wagner_psat(T, _paramsPvap[0], _paramsPvap[1], _paramsPvap[2], _paramsPvap[3], _paramsPvap[4], _paramsPvap[5]);
        case PVAP_IKCAPE:
            return ik_cape_psat(T, _paramsPvap[0], _paramsPvap[1], _paramsPvap[2], _paramsPvap[3], _paramsPvap[4], _paramsPvap[5], _paramsPvap[6], _paramsPvap[7], _paramsPvap[8], _paramsPvap[9]);
        case PVAP_UNDEF:
            throw(std::runtime_error("Error: No vapor pressure model specified."));
        default:
            throw(std::runtime_error("Error: Unknown vapor pressure model."));
    }
}

template <typename U>
U
SubcriticalComponent<U>::calculate_vaporization_enthalpy(const U &T) const
{
    if (_paramsDhvap.size() != 6) {
        throw(std::runtime_error("Enthalpy of vaporization queried before a corresponding model was specified."));
    }

    U Tr = T / PureComponent<U>::_Tc;
    switch (_dhvapModel) {
        case DHVAP_WATSON:
            return _paramsDhvap[4] * pow(max(1 - Tr, mc::machprec()) / (1 - _paramsDhvap[3] / PureComponent<U>::_Tc), _paramsDhvap[1] + _paramsDhvap[2] * (1 - Tr));
        case DHVAP_DIPPR106:
            return _paramsDhvap[1] * pow(max(1 - Tr, mc::machprec()), _paramsDhvap[2] + _paramsDhvap[3] * Tr + _paramsDhvap[4] * pow(Tr, 2) + _paramsDhvap[5] * pow(Tr, 3));
        case DHVAP_UNDEF:
            throw(std::runtime_error("Error: No enthalpy of vaporization model specified."));
        default:
            throw(std::runtime_error("Error: Unknown enthalpy of vaporization model."));
    }
}


template <typename U>
U
SubcriticalComponent<U>::calculate_vaporization_enthalpy_conv(const U &T) const
{
    switch (_dhvapModel) {
        case DHVAP_WATSON:
            return watson_dhvap(T, _paramsDhvap[0], _paramsDhvap[1], _paramsDhvap[2], _paramsDhvap[3], _paramsDhvap[4]);
        case DHVAP_DIPPR106:
            return dippr106_dhvap(T, _paramsDhvap[0], _paramsDhvap[1], _paramsDhvap[2], _paramsDhvap[3], _paramsDhvap[4], _paramsDhvap[5]);
        case DHVAP_UNDEF:
            throw(std::runtime_error("Error: No enthalpy of vaporization model specified."));
        default:
            throw(std::runtime_error("Error: Unknown enthalpy of vaporization model."));
    }
}


template <typename U>
U
SubcriticalComponent<U>::calculate_liquid_enthalpy_pressure_correction(const U &T, const U &p, const U &ps) const
{
    if (_paramsVliq.size() != 3) {
        throw(std::runtime_error("Liquid enthalpy pressure correction queried before a liquid volume model was specified."));
    }

    switch (_vliqModel) {
        case VLIQ_CONSTANT:
            return 0.1 * _paramsVliq[0] * (p - ps);
        case VLIQ_QUADRATIC:
            return 0.1 * (_paramsVliq[0] - _paramsVliq[2] * pow(T, 2)) * (p - ps);
        case VLIQ_UNDEF:
            throw(std::runtime_error("Error: No liquid volume model specified."));
        default:
            throw(std::runtime_error("Error: Unknown liquid volume model."));
    }
}


template <typename U>
U
SubcriticalComponent<U>::calculate_poynting_factor(const U &T, const U &p, const U &ps) const
{
    if (_paramsVliq.size() != 3) {
        throw(std::runtime_error("Poynting factor queried before a liquid volume model was specified."));
    }

    switch (_vliqModel) {
        case VLIQ_CONSTANT:
            return exp(_paramsVliq[0] * (p - ps) / (PureComponent<U>::_R * T));
        case VLIQ_QUADRATIC:
            return exp((_paramsVliq[0] / T + _paramsVliq[1] + _paramsVliq[2] * T) * (p - ps) / PureComponent<U>::_R);
        case VLIQ_UNDEF:
            throw(std::runtime_error("Error: No liquid volume model specified."));
        default:
            throw(std::runtime_error("Error: Unknown liquid volume model."));
    }
}


template <typename U>
void
SubcriticalComponent<U>::set_vapor_pressure_model(PVAP modelId, const std::vector<double> &parameters)
{
    switch (modelId) {
        case PVAP_XANTOINE:
            if (parameters.size() != 7) {
                throw(std::runtime_error("Error: Extended Antoine equation initialized with wrong number of parameters."));
            }
            break;
        case PVAP_ANTOINE:
            if (parameters.size() != 3) {
                throw(std::runtime_error("Error: Antoine equation initialized with wrong number of parameters."));
            }
            break;
        case PVAP_WAGNER:
            if (parameters.size() != 5) {
                throw(std::runtime_error("Error: Wagner equation for vapor pressure initialized with wrong number of parameters."));
            }
            break;
        case PVAP_IKCAPE:
            if (parameters.size() != 10) {
                throw(std::runtime_error("Error: IK Cape equation for vapor pressure initialized with wrong number of parameters."));
            }
            break;
        default:
            throw(std::runtime_error("Error: Unknown vapor pressure model."));
    }
    _pvapModel  = modelId;
    _paramsPvap = parameters;
    if (modelId == PVAP_WAGNER) {
        _paramsPvap.push_back(PureComponent<U>::_Tc);
        _paramsPvap.push_back(PureComponent<U>::_pc);
    }
    while (_paramsPvap.size() < 10) {
        _paramsPvap.push_back(0.);
    }
}


template <typename U>
void
SubcriticalComponent<U>::set_enthalpy_of_vaporization_model(DHVAP modelId, const std::vector<double> &parameters)
{
    switch (modelId) {
        case DHVAP_WATSON:
            if (parameters.size() != 4) {
                throw(std::runtime_error("Error: Watson model for enthalpy of vaporization initialized with wrong number of parameters."));
            }
            break;
        case DHVAP_DIPPR106:
            if (parameters.size() != 5) {
                throw(std::runtime_error("Error: DIPPR equation 106 for enthalpy of vaporization initialized with wrong number of parameters."));
            }
            break;
        default:
            throw(std::runtime_error("Error: Unknown enthalpy of vaporization model."));
    }
    _dhvapModel  = modelId;
    _paramsDhvap = std::vector<double>{PureComponent<U>::_Tc};
    _paramsDhvap.insert(_paramsDhvap.end(), parameters.begin(), parameters.end());
    while (_paramsDhvap.size() < 6) {
        _paramsDhvap.push_back(0.);
    }
}


template <typename U>
void
SubcriticalComponent<U>::set_liquid_volume_model(VLIQ modelId, const std::vector<double> &parameters)
{
    switch (modelId) {
        case VLIQ_CONSTANT:
            if (parameters.size() != 1) {
                throw(std::runtime_error("Error: Constant liquid volume model initialized with wrong number of parameters."));
            }
            break;
        case VLIQ_QUADRATIC:
            if (parameters.size() != 3) {
                throw(std::runtime_error("Error: Quadratic liquid volume model initialized with wrong number of parameters."));
            }
            break;
        default:
            throw(std::runtime_error("Error: Unknown liquid volume model."));
    }

    _vliqModel  = modelId;
    _paramsVliq = parameters;
    while (_paramsVliq.size() < 3) {
        _paramsVliq.push_back(0.);
    }
}


#endif /* SUBCRITICALCOMPONENT_H_ */

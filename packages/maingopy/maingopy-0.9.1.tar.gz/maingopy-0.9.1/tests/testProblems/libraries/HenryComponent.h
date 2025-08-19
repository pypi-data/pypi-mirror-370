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


#ifndef HENRYCOMPONENT_H_
#define HENRYCOMPONENT_H_

#include "usingAdditionalIntrinsicFunctions.h"


#include "PureComponent.h"

/**
* @class HenryComponent
* @brief Class representing a Henry component.
*
* It stores all necessary parameters and contains functions for computing temperature- (and possibly pressure-)dependent properties using different models.
* The models to be used can be selected through the set functions using the respective enums.
*/
template <typename U>
class HenryComponent: public PureComponent<U> {

  public:
    /** 
	* @enum HENRY
	* @brief Enum for selecting the Henry's law constant model to be used.
	*/
    enum HENRY {
        HENRY_UNDEF = 0,
        HENRY_ASPEN    //!< H_iA = exp(C0 + C1/T + C2*ln(T) + C3*T + C4/T^2)
    };

    /** 
	* @enum VSOL
	* @brief Enum for selecting the infinite dilution volume model to be used.
	*/
    enum VSOL {
        VSOL_UNDEF = 0,
        VSOL_CONSTANT    //!< vsol = C0
    };

    /** 
	* @enum MIX
	* @brief Enum for selecting the solvent mixing rules to be used.
	*/
    enum MIX {
        MIX_UNDEF = 0,
        MIX_MOLEFRAC,       //!< ln(H_i) = sum_A x_A * ln(H_iA)
        MIX_NORMOLEFRAC,    //!< ln(H_i) = sum_A y_A * ln(H_iA),    y_A := x_A /(sum_{B in Solvents} x_B)
        MIX_ASPEN           //!< ln(H_i) = sum_A w_A* * ln(H_iA),   w_A := x_A*vc_A^2/3 /(sum_{B in Solvents} x_B*vc_B^2/3), 	vc_i: critical volume of solvent
    };


    /**
	* @brief Constructor. Requires all necessary constant property parameters as arguments.
	* @param[in] nameIn is the component name.
	* @param[in] mwIn is the molecular weight in kg/kmol.
	* @param[in] tcIn is the critical temperature in K.
	* @param[in] pcIn is the critical pressure in bar.
	* @param[in] vcIn is the critical volume in cm^3/mol.
	* @param[in] dh0In is the enthalpy of formation at 298.15 K in kJ/mol
	* @param[in] dg0In is the Gibbs free energy of formation at 298.15 K in kJ/mol
	*/
    HenryComponent(const std::string nameIn, const double mwIn, const double tcIn, const double pcIn, const double vcIn, const double dh0In, const double dg0In):
        PureComponent<U>(nameIn, mwIn, tcIn, pcIn, vcIn, dh0In, dg0In), _maxLnH(std::log(1.0e12)), _minLnH(std::log(1.0e-12)), _henryModel(HENRY_UNDEF), _vsolModel(VSOL_UNDEF), _mixingRule(MIX_UNDEF) {}


    /**
	* @brief Function for computing the Henry's law constant in a single solvent at a given temperature (and the solvent's vapor pressure, i.e., neglecting the influence of pressure).
	* @param[in] T is the temperature in K.
	* @param[in] iSolvent is the index of the solvent (in the full components vector).
	* @return Henry's law constant in bar
	*/
    U calculate_henry_single(const U &T, const int iSolvent) const;
    U calculate_henry_single_log(const U &T, const int iSolvent) const;

    /**
	* @brief Function for computing the Henry's law constant in a single solvent at a given temperature and pressure.
	* @param[in] T is the temperature in K.
	* @param[in] p is the pressure in bar.
	* @param[in] ps is the solvents vapor pressure in bar.
	* @param[in] iSolvent is the index of the solvent (in the full components vector).
	* @return Henry's law constant in bar
	*/
    U calculate_henry_single(const U &T, const U &p, const U &ps, const int iSolvent) const;


    /**
	* @brief Function for computing the Henry's law constant in mixed solvents at a given temperature and solvent composition (neglecting the influence of pressure).
	* @param[in] T is the temperature in K.
	* @param[in] x is the vector containing the liquid mole fractions (only the ones of the subcritical components for which Henry coefficients are given will be used).
	* @return Henry's law constant in bar
	*/
    U calculate_henry_mixed(const U &T, const std::vector<U> &x) const;

    /**
	* @brief Function for computing the Henry's law constant in a single solvent at a given temperature, pressure, and solvent composition.
	* @param[in] T is the temperature in K.
	* @param[in] p is the pressure in bar.
	* @param[in] ps is the vector containing the solvents' vapor pressures in bar.
	* @param[in] x is the vector containing the liquid mole fractions (only the ones of the subcritical components for which Henry coefficients are given will be used).
	* @return Henry's law constant in bar
	*/
    U calculate_henry_mixed(const U &T, const U &p, const std::vector<U> &ps, const std::vector<U> &x) const;


    /**
	* @brief Function for computing the Henry's law constant divided by the infinite dilution activity coefficient in mixed solvents at a given temperature and composition (neglecting the influence of pressure).
	* @param[in] T is the temperature in K.
	* @param[in] gammaInf is the vector containing the natural logarithms of the infinite dilution activity coefficients in the different solvents.
	* @param[in] x is the vector containing the liquid mole fractions (only the ones of the subcritical components for which Henry coefficients are given will be used).
	* @return Henry's law constant in bar
	*/
    U calculate_henry_by_gamma_mixed(const U &T, const std::vector<U> &logGammaInf, const std::vector<U> &x) const;

    /**
	* @brief Function for computing the Henry's law constant in a single solvent at a given temperature and pressure (using the solvent's vapor pressure).
	* @param[in] T is the temperature in K.
	* @param[in] p is the pressure in bar.
	* @param[in] ps is the vector containing the solvents' vapor pressures in bar.
	* @param[in] gammaInf is the vector containing the natural logarithms of the infinite dilution activity coefficients in the different solvents.
	* @param[in] x is the vector containing the liquid mole fractions (only the ones of the subcritical components for which Henry coefficients are given will be used).
	* @return Henry's law constant in bar
	*/
    U calculate_henry_by_gamma_mixed(const U &T, const U &p, const std::vector<U> &ps, const std::vector<U> &logGammaInf, const std::vector<U> &x) const;


    /**
	* @brief Function for computing the enthalpy of solution in a single solvent at a given temperature (and the solvent's vapor pressure).
	* @param[in] T is the temperature in K.
	* @param[in] iSolvent is the index of the solvent (in the full components vector).
	* @return enthalpy of solution in kJ/kmol
	*/
    U calculate_solution_enthalpy_single(const U &T, const int iSolvent) const;

    /**
	* @brief Function for computing the enthalpy of solution in mixed solvents at a given temperature and solvent composition (neglecting the influence of pressure).
	* @param[in] T is the temperature in K.
	* @param[in] x is the vector containing the liquid mole fractions (only the ones of the subcritical components for which Henry coefficients are given will be used).
	* @return enthalpy of solution in kJ/kmol
	*/
    U calculate_solution_enthalpy_mixed(const U &T, const std::vector<U> &x) const;


    /**
	* @brief Functions for selecting the property models to be used.
	* @param[in] modelId is an enumerator specifying the model.
	*/
    void set_henry_model(const HENRY modelId);
    void set_solute_volume_model(const VSOL modelId);
    void set_solvent_mixing_rule(const MIX ruleId, const std::vector<double> &parameters = std::vector<double>());

    /**
	* @brief Functions for adding parameter values.
	* @param[in] parameters is a vector containing the required parameter values.
	*/
    void add_henry_parameters(const std::vector<double> &parameters);
    void add_volume_parameters(const std::vector<double> &parameters);

  private:
    const double _minLnH; /*!< Minimum value for natural logarithm of Henry's law constant (to avoid underflow)	*/
    const double _maxLnH; /*!< Minimum value for natural logarithm of Henry's law constant (to avoid overflow)	*/

    std::vector<std::vector<double>> _paramsHenry; /*!< Pointer to vector containing Henry parameters (at solvent vapor pressure); entry 0 is index of solvent			[K, bar] 		*/
    std::vector<std::vector<double>> _paramsVsol;  /*!< Pointer to vector containing parameters for infinite dilution volume model; entry 0 is index of solvent		[K, cm^3/mol] 	*/
    std::vector<double> _paramsMixAspen;           /*!< Pointer to vector containing parameters for Aspen solvent mixing rule, i.e., critical volumes of solvents 		[cm^3/mol]		*/

    HENRY _henryModel; /*!< Enumerator storing which Henry's law constant model is used					*/
    VSOL _vsolModel;   /*!< Enumerator storing which infinite dilution volume model is used				*/
    MIX _mixingRule;   /*!< Enumerator storing which solvent mixing rule is used							*/

    U _get_log_henry_single(const U &T, const int iSolventOnly) const;
    U _get_log_pressure_correction(const U &T, const U &p, const U &ps, const int iSolventOnly) const;
    U _get_dhsol_single(const U &T, const int iSolventOnly) const;
};


// ------------ Henry's constant ------------
template <typename U>
U
HenryComponent<U>::calculate_henry_single(const U &T, const int iSolvent) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters given."));
    }

    for (size_t i = 0; i < _paramsHenry.size(); ++i) {
        if (_paramsHenry[i][0] == iSolvent) {
            return exp(_get_log_henry_single(T, i));
        }
    }

    throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters found for desired solvent."));
}
template <typename U>
U
HenryComponent<U>::calculate_henry_single_log(const U &T, const int iSolvent) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters given."));
    }

    for (size_t i = 0; i < _paramsHenry.size(); ++i) {
        if (_paramsHenry[i][0] == iSolvent) {
            return _get_log_henry_single(T, i);
        }
    }

    throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters found for desired solvent."));
}


template <typename U>
U
HenryComponent<U>::calculate_henry_single(const U &T, const U &p, const U &ps, const int iSolvent) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters given."));
    }
    if (_paramsVsol.empty()) {
        throw(std::runtime_error("Error computing pressure correction for Henry's law constant: No infinite dilution volume parameters given."));
    }
    if (_paramsHenry.size() != _paramsVsol.size()) {
        throw(std::runtime_error("Error computing pressure correction for Henry's law constant: Dimension of Henry parameters and infinite dilution volume parameters don't match."));
    }

    for (size_t i = 0; i < _paramsHenry.size(); ++i) {
        if (_paramsHenry[i][0] == iSolvent) {
            U henryAtPs(exp(_get_log_henry_single(T, i)));
            U pressureCorrection(exp(_get_log_pressure_correction(T, p, ps, i)));
            return henryAtPs * pressureCorrection;
        }
    }

    throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters found for desired solvent."));
}


template <typename U>
U
HenryComponent<U>::calculate_henry_mixed(const U &T, const std::vector<U> &x) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters given."));
    }


    U lnH(0.);
    switch (_mixingRule) {
        case MIX_MOLEFRAC: {
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U lnHi(_get_log_henry_single(T, i));
                lnH += x[_paramsHenry[i][0]] * lnHi;
            }
            return exp(lnH);
        }
        case MIX_NORMOLEFRAC: {
            U sumXsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                sumXsolv += x[_paramsHenry[i][0]];
                U lnHi(_get_log_henry_single(T, i));
                lnH += x[_paramsHenry[i][0]] * lnHi;
            }
            return exp(bounding_func(lnH / (sumXsolv), _minLnH, _maxLnH));
        }
        case MIX_ASPEN: {
            U sumWsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U wSolv(x[_paramsHenry[i][0]] * _paramsMixAspen[i]);
                sumWsolv += wSolv;
                U lnHi(_get_log_henry_single(T, i));
                lnH += wSolv * lnHi;
            }
            return exp(bounding_func(lnH / (sumWsolv), _minLnH, _maxLnH));
        }
        case MIX_UNDEF:
            throw(std::runtime_error("Error: No solute mixing rule specified."));

        default:
            throw(std::runtime_error("Error: Unknown solute mixing rule."));
    }
}


template <typename U>
U
HenryComponent<U>::calculate_henry_mixed(const U &T, const U &p, const std::vector<U> &ps, const std::vector<U> &x) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters given."));
    }
    if (_paramsVsol.empty()) {
        throw(std::runtime_error("Error computing pressure correction for Henry's law constant: No infinite dilution volume parameters given."));
    }
    if (_paramsHenry.size() != _paramsVsol.size()) {
        throw(std::runtime_error("Error computing pressure correction for Henry's law constant: Dimension of Henry parameters and infinite dilution volume parameters don't match."));
    }

    U lnH(0.);
    switch (_mixingRule) {
        case MIX_MOLEFRAC: {
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U logHiAtPsi(_get_log_henry_single(T, i));
                U logPressureCorrection(_get_log_pressure_correction(T, p, ps[_paramsHenry[i][0]], i));
                lnH += x[_paramsHenry[i][0]] * (logHiAtPsi + logPressureCorrection);
            }
            return exp(lnH);
        }
        case MIX_NORMOLEFRAC: {
            U sumXsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                sumXsolv += x[_paramsHenry[i][0]];
                U logHiAtPsi(_get_log_henry_single(T, i));
                U logPressureCorrection(_get_log_pressure_correction(T, p, ps[_paramsHenry[i][0]], i));
                lnH += x[_paramsHenry[i][0]] * (logHiAtPsi + logPressureCorrection);
            }
            return exp(bounding_func(lnH / (sumXsolv), _minLnH, _maxLnH));
        }
        case MIX_ASPEN: {
            U sumWsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U wSolv(x[_paramsHenry[i][0]] * _paramsMixAspen[i]);
                sumWsolv += wSolv;
                U logHiAtPsi(_get_log_henry_single(T, i));
                U logPressureCorrection(_get_log_pressure_correction(T, p, ps[_paramsHenry[i][0]], i));
                lnH += wSolv * (logHiAtPsi + logPressureCorrection);
            }
            return exp(bounding_func(lnH / (sumWsolv), _minLnH, _maxLnH));
        }
        case MIX_UNDEF:
            throw(std::runtime_error("Error: No solute mixing rule specified."));

        default:
            throw(std::runtime_error("Error: Unknown solute mixing rule."));
    }
}


template <typename U>
U
HenryComponent<U>::calculate_henry_by_gamma_mixed(const U &T, const std::vector<U> &logGammaInf, const std::vector<U> &x) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters given."));
    }
    if (logGammaInf.size() != _paramsHenry.size()) {
        throw(std::runtime_error("Error computin Henry's law constant: Dimension fo infinite dilution activity coefficient vector inconsistent with number of solvents."));
    }

    U lnHbyGammaInf(0.);
    switch (_mixingRule) {
        case MIX_MOLEFRAC: {
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U lnHi(_get_log_henry_single(T, i));
                lnHbyGammaInf += x[_paramsHenry[i][0]] * (lnHi - logGammaInf[i]);
            }
            return exp(bounding_func(lnHbyGammaInf, _minLnH, _maxLnH));
        }
        case MIX_NORMOLEFRAC: {
            U sumXsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                sumXsolv += x[_paramsHenry[i][0]];
                U lnHi(_get_log_henry_single(T, i));
                lnHbyGammaInf += x[_paramsHenry[i][0]] * (lnHi - logGammaInf[i]);
            }
            return exp(bounding_func(lnHbyGammaInf / (sumXsolv), _minLnH, _maxLnH));
        }
        case MIX_ASPEN: {
            U sumWsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U wSolv(x[_paramsHenry[i][0]] * _paramsMixAspen[i]);
                sumWsolv += wSolv;
                U lnHi(_get_log_henry_single(T, i));
                lnHbyGammaInf += wSolv * (lnHi - logGammaInf[i]);
            }
            return exp(bounding_func(lnHbyGammaInf / (sumWsolv), _minLnH, _maxLnH));
        }
        case MIX_UNDEF:
            throw(std::runtime_error("Error: No solute mixing rule specified."));

        default:
            throw(std::runtime_error("Error: Unknown solute mixing rule."));
    }
}


template <typename U>
U
HenryComponent<U>::calculate_henry_by_gamma_mixed(const U &T, const U &p, const std::vector<U> &ps, const std::vector<U> &logGammaInf, const std::vector<U> &x) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters given."));
    }
    if (logGammaInf.size() != _paramsHenry.size()) {
        throw(std::runtime_error("Error computin Henry's law constant: Dimension fo infinite dilution activity coefficient vector inconsistent with number of solvents."));
    }
    if (_paramsHenry.size() != _paramsVsol.size()) {
        throw(std::runtime_error("Error computing pressure correction for Henry's law constant: Dimension of Henry parameters and infinite dilution volume parameters don't match."));
    }

    U lnHbyGammaInf(0.);
    switch (_mixingRule) {
        case MIX_MOLEFRAC: {
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U logHiAtPsi(_get_log_henry_single(T, i));
                U logPressureCorrection(_get_log_pressure_correction(T, p, ps[_paramsHenry[i][0]], i));
                lnHbyGammaInf += x[_paramsHenry[i][0]] * (logHiAtPsi + logPressureCorrection - logGammaInf[i]);
            }
            return exp(bounding_func(lnHbyGammaInf, _minLnH, _maxLnH));
        }
        case MIX_NORMOLEFRAC: {
            U sumXsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                sumXsolv += x[_paramsHenry[i][0]];
                U logHiAtPsi(_get_log_henry_single(T, i));
                U logPressureCorrection(_get_log_pressure_correction(T, p, ps[_paramsHenry[i][0]], i));
                lnHbyGammaInf += x[_paramsHenry[i][0]] * (logHiAtPsi + logPressureCorrection - logGammaInf[i]);
            }
            return exp(bounding_func(lnHbyGammaInf / (sumXsolv), _minLnH, _maxLnH));
        }
        case MIX_ASPEN: {
            U sumWsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U wSolv(x[_paramsHenry[i][0]] * _paramsMixAspen[i]);
                sumWsolv += wSolv;
                U logHiAtPsi(_get_log_henry_single(T, i));
                U logPressureCorrection(_get_log_pressure_correction(T, p, ps[_paramsHenry[i][0]], i));
                lnHbyGammaInf += wSolv * (logHiAtPsi + logPressureCorrection - logGammaInf[i]);
            }
            return exp(bounding_func(lnHbyGammaInf / (sumWsolv), _minLnH, _maxLnH));
        }
        case MIX_UNDEF:
            throw(std::runtime_error("Error: No solute mixing rule specified."));

        default:
            throw(std::runtime_error("Error: Unknown solute mixing rule."));
    }
}


// ------------ Enthalpy of solution ------------
template <typename U>
U
HenryComponent<U>::calculate_solution_enthalpy_single(const U &T, const int iSolvent) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing solution enthalpy: No Henry parameters given."));
    }

    for (size_t i = 0; i < _paramsHenry.size(); ++i) {
        if (_paramsHenry[i][0] == iSolvent) {
            return _get_dhsol_single(T, i);
        }
    }

    throw(std::runtime_error("Error computing solution enthalpy: No Henry parameters found for desired solvent."));
}

template <typename U>
U
HenryComponent<U>::calculate_solution_enthalpy_mixed(const U &T, const std::vector<U> &x) const
{

    if (_paramsHenry.empty()) {
        throw(std::runtime_error("Error computing Henry's law constant: No Henry parameters given."));
    }

    U dHsol(0.);
    switch (_mixingRule) {
        case MIX_MOLEFRAC: {
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                dHsol += x[_paramsHenry[i][0]] * _get_dhsol_single(T, i);
            }
            return dHsol;
        }
        case MIX_NORMOLEFRAC: {
            U sumXsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                sumXsolv += x[_paramsHenry[i][0]];
                dHsol += x[_paramsHenry[i][0]] * _get_dhsol_single(T, i);
            }
            return dHsol / (sumXsolv);
        }
        case MIX_ASPEN: {
            U sumWsolv(0.);
            for (size_t i = 0; i < _paramsHenry.size(); ++i) {
                U wSolv(x[_paramsHenry[i][0]] * _paramsMixAspen[i]);
                sumWsolv += wSolv;
                dHsol += wSolv * _get_dhsol_single(T, i);
            }
            return dHsol / (sumWsolv);
        }
        case MIX_UNDEF:
            throw(std::runtime_error("Error: No solute mixing rule specified."));

        default:
            throw(std::runtime_error("Error: Unknown solute mixing rule."));
    }
}


// ------------ Model selection ------------
template <typename U>
void
HenryComponent<U>::set_henry_model(HENRY modelId)
{

    switch (modelId) {
        case HENRY_ASPEN:
            break;
        default:
            throw(std::runtime_error("Error: Unknown Henry's law constant model."));
    }
    _henryModel = modelId;
    _paramsHenry.clear();
}


template <typename U>
void
HenryComponent<U>::set_solute_volume_model(VSOL modelId)
{

    switch (modelId) {
        case VSOL_CONSTANT:
            break;
        default:
            throw(std::runtime_error("Error: Unknown infinite dilution volume."));
    }

    _vsolModel = modelId;
    _paramsVsol.clear();
}


template <typename U>
void
HenryComponent<U>::set_solvent_mixing_rule(MIX ruleId, const std::vector<double> &parameters)
{

    switch (ruleId) {
        case MIX_MOLEFRAC:
            break;

        case MIX_NORMOLEFRAC:
            break;

        case MIX_ASPEN:
            if (parameters.empty()) {
                throw(std::runtime_error("Error setting solvent mixing rule MIX_ASPEN: No vector of solvent critical volumes given."));
            }
            _paramsMixAspen = parameters;
            for (size_t i = 0; i < _paramsMixAspen.size(); ++i) {
                if (_paramsMixAspen[i] <= 0) {
                    throw(std::runtime_error("Error setting solvent mixing rule MIX_ASPEN: Negative solvent critical volumes given."));
                }
                _paramsMixAspen[i] = pow(_paramsMixAspen[i], 2.0 / 3.0);
            }
            break;

        default:
            throw(std::runtime_error("Error: Unknown solvent mixing rule."));
    }
    _mixingRule = ruleId;
}


template <typename U>
void
HenryComponent<U>::add_henry_parameters(const std::vector<double> &parameters)
{

    switch (_henryModel) {
        case HENRY_ASPEN:
            if (parameters.size() != 6) {
                throw(std::runtime_error("Error adding Henry's law constant parameters: Wrong number of parameters."));
            }
            break;
        case HENRY_UNDEF:
            throw(std::runtime_error("Error adding Henry's law constant parameters: No Henry's law model specified."));
        default:
            throw(std::runtime_error("Error adding Henry's law constant parameters: Unknown Henry's law constant model."));
    }

    for (size_t i = 0; i < _paramsHenry.size(); ++i) {
        if (_paramsHenry[i][0] == parameters.at(0)) {
            throw(std::runtime_error("Error adding Henry's law constant parameters: Data for specified solvents already exists."));
        }
    }
    _paramsHenry.push_back(parameters);
}


template <typename U>
void
HenryComponent<U>::add_volume_parameters(const std::vector<double> &parameters)
{

    switch (_vsolModel) {
        case VSOL_CONSTANT:
            if (parameters.size() != 2) {
                throw(std::runtime_error("Error adding infinite dilution volume parameters: wrong number of parameters."));
            }
            break;
        case VSOL_UNDEF:
            throw(std::runtime_error("Error adding infinite dilution volume parameters: No infinite dilution volume model specified."));
        default:
            throw(std::runtime_error("Error adding infinite dilution volume parameters: Unknown infinite dilution  volume model."));
    }
    for (size_t i = 0; i < _paramsVsol.size(); ++i) {
        if (_paramsVsol[i][0] == parameters.at(0)) {
            throw(std::runtime_error("Error adding infinite dilution volume parameters: Data for specified solvents already exists."));
        }
    }
    _paramsVsol.push_back(parameters);
}


// ------------ Helper functions ------------

template <typename U>
U
HenryComponent<U>::_get_log_henry_single(const U &T, const int iSolventOnly) const
{

    switch (_henryModel) {
        case HENRY_ASPEN: {
            U lnHi(_paramsHenry[iSolventOnly][1] + _paramsHenry[iSolventOnly][2] / T + _paramsHenry[iSolventOnly][3] * log(T) + _paramsHenry[iSolventOnly][4] * T + _paramsHenry[iSolventOnly][5] / sqr(T));
            return bounding_func(lnHi, _minLnH, _maxLnH);
        }
        case HENRY_UNDEF:
            throw(std::runtime_error("Error: No Henry's law constant model specified."));

        default:
            throw(std::runtime_error("Error: Unknown Henry's law constant model."));
    }
}


template <typename U>
U
HenryComponent<U>::_get_log_pressure_correction(const U &T, const U &p, const U &ps, const int iSolventOnly) const
{

    switch (_vsolModel) {
        case VSOL_CONSTANT:
            return (_paramsVsol[iSolventOnly][1] / (PureComponent<U>::_R * T)) * (p - ps);

        case VSOL_UNDEF:
            throw(std::runtime_error("Error: No infinite dilution volume model specified."));

        default:
            throw(std::runtime_error("Error: Unknown infinite dilution volume model."));
    }
}


template <typename U>
U
HenryComponent<U>::_get_dhsol_single(const U &T, const int iSolventOnly) const
{

    switch (_henryModel) {
        case HENRY_ASPEN: {
            return PureComponent<U>::_R * (-_paramsHenry[iSolventOnly][2] + _paramsHenry[iSolventOnly][3] * T + _paramsHenry[iSolventOnly][4] * pow(T, 2) - 2 * _paramsHenry[iSolventOnly][5] / T);
        }
        case HENRY_UNDEF:
            throw(std::runtime_error("Error: No Henry's law constant model specified."));

        default:
            throw(std::runtime_error("Error: Unknown Henry's law constant model."));
    }
}

#endif /* HENRYCOMPONENT_H_ */

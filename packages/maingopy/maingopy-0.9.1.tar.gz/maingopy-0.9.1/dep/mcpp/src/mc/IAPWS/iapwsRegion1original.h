/**
 * @file iapwsRegion1original.h
 *
 * @brief File containing template implementation of region 1 of the IAPWS-IF97 model.
 *
 * Original model: Wagner, W.; Cooper, J. R.; Dittmann, A.; Kijima, J.; Kretzschmar, H.-J.; Kruse, A.; Mareš, R.; Oguchi, K.; Sato, H.; Stocker, I.; Sifner, O.; Takaishi, Y.; Tanishita, I.; Trubenbach, J. & Willkommen, T.:
 *                 The IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam. Journal of Engineering for Gas Turbines and Power -- Transactions of the ASME, 2000, 122, 150-182.
 *
 * Revised model used for this implementation: Revised Release on the IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam.
 *											   The International Association for the Properties of Water and Steam, Technical Report IAPWS R7-97(2012), 2012. http://www.iapws.org/relguide/IF97-Rev.html.
 *
 * ==============================================================================\n
 * © Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
 * ==============================================================================\n
 *
 * @author Dominik Bongartz, David Zanger, Alexander Mitsos
 * @date 15.08.2019
 *
 */

#pragma once

#include "iapwsData.h"
#include "iapwsAuxiliary.h"
#include "iapwsAuxiliaryDerivatives.h"


namespace iapws_if97 {


	namespace region1 {


		namespace original {


			/**
			* @name Forward equations (derived immediately from the basic equation g(p,T) for this region)
			*/
			/**@{*/

				/**
				* @brief Function for computing enthalpy as a function of pressure and temperature in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Specific enthalpy in kJ/kg
				*/
				template <typename U, typename V>
				auto get_h_pT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return constants::R * data::Tstar * auxiliary::gamma_tau(pi,tau);
				}

				/**
				* @brief Function for computing entropy as a function of pressure and temperature in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Specific entropy in kJ/(kg*K)
				*/
				template <typename U, typename V>
				auto get_s_pT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return constants::R * ( tau*auxiliary::gamma_tau(pi,tau) - auxiliary::gamma(pi,tau) );
				}

			/**@}*/


			/**
			* @name Backward equations (supplied by the IAPWS for this region)
			*/
			/**@{*/

				/**
				* @brief Function for computing temperature as a function of pressure and enthalpy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Temperature in K
				*/
				template <typename U, typename V>
				auto get_T_ph(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::theta_pi_eta(pi,eta);
				}

				/**
				* @brief Function for computing temperature as a function of pressure and entropy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Temperature in K
				*/
				template <typename U, typename V>
				auto get_T_ps(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBack;
					return data::TstarBack * auxiliary::theta_pi_sigma(pi,sigma);
				}

			/**@}*/


			namespace derivatives {


			/**
			* @name Derivatives of functions in region 1
			*/
			/**@{*/

				/**
				* @brief Function for computing the partial derivative of enthalpy w.r.t. temperature in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Partial derivative of specific enthalpy w.r.t. temperature in (kJ/kg)/K
				*/
				template <typename U, typename V>
				auto get_dh_pT_dT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return -constants::R * pow(tau,2) * auxiliary::derivatives::dgamma_tau_dtau(pi,tau);
				}

				/**
				* @brief Function for computing the partial derivative of enthalpy w.r.t. pressure in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa
				*/
				template <typename U, typename V>
				auto get_dh_pT_dp(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return constants::R * data::Tstar * auxiliary::derivatives::dgamma_tau_dpi(pi,tau) / data::pstar;
				}

				/**
				* @brief Function for computing the second partial derivative of enthalpy w.r.t. temperature in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Second partial derivative of specific enthalpy w.r.t. temperature in (kJ/kg)/K^2
				*/
				template <typename U, typename V>
				auto get_d2h_pT_dT2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return constants::R * ( (2.*pow(data::Tstar,2)/pow(T,3))*auxiliary::derivatives::dgamma_tau_dtau(pi,tau) + (pow(data::Tstar,3)/pow(T,4))*auxiliary::derivatives::d2gamma_tau_dtau2(pi,tau) );
				}

				/**
				* @brief Function for computing the second partial derivative of enthalpy w.r.t. pressure in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Second partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2h_pT_dp2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R * data::Tstar / pow(data::pstar,2)) * auxiliary::derivatives::d2gamma_tau_dpi2(pi,tau);
				}

				/**
				* @brief Function for computing the mixed second partial derivative of enthalpy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Mixed second partial derivative of specific enthalpy in (kJ/kg)/(K*MPa)
				*/
				template <typename U, typename V>
				auto get_d2h_pT_dpT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return -(constants::R * pow(tau,2) / data::pstar) * auxiliary::derivatives::d2gamma_tau_dpitau(pi,tau);
				}

				/**
				* @brief Function for computing the third partial derivative of enthalpy w.r.t. pressure in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Third partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa^3
				*/
				template <typename U, typename V>
				auto get_d3h_pT_dp3(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R * data::Tstar / pow(data::pstar,3)) * auxiliary::derivatives::d3gamma_tau_dpi3(pi,tau);
				}

				/**
				* @brief Function for computing a mixed third partial derivative of enthalpy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Mixed third partial derivative of specific enthalpy in (kJ/kg)/(K*MPa^2)
				*/
				template <typename U, typename V>
				auto get_d3h_pT_dp2T(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return -(constants::R * pow(tau,2) / pow(data::pstar,2)) * auxiliary::derivatives::d3gamma_tau_dpi2tau(pi,tau);
				}

				/**
				* @brief Function for computing a mixed third partial derivative of enthalpy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Mixed third partial derivative of specific enthalpy in (kJ/kg)/(K^2*MPa)
				*/
				template <typename U, typename V>
				auto get_d3h_pT_dpT2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R * pow(data::Tstar,3) / (pow(T,4)*data::pstar)) * auxiliary::derivatives::d3gamma_tau_dpitau2(pi,tau);
				}

				/**
				* @brief Function for computing the derivative of entropy w.r.t. pressure in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Partial derivative of specific entropy w.r.t. pressure in kJ/(kg*K*MPa)
				*/
				template <typename U, typename V>
				auto get_ds_pT_dp(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R / data::pstar) * ( tau*auxiliary::derivatives::dgamma_tau_dpi(pi,tau) - auxiliary::gamma_pi(pi,tau) );
				}

				/**
				* @brief Function for computing the derivative of entropy w.r.t. temperature in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Partial derivative of specific entropy w.r.t. temperature in kJ/(kg*K^2)
				*/
				template <typename U, typename V>
				auto get_ds_pT_dT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return -(constants::R * pow(data::Tstar,2) / pow(T,3)) * auxiliary::derivatives::dgamma_tau_dtau(pi,tau);
				}

				/**
				* @brief Function for computing the second partial derivative of entropy w.r.t. pressure in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Second partial derivative of specific entropy w.r.t. pressure in kJ/(kg*K*MPa^2)
				*/
				template <typename U, typename V>
				auto get_d2s_pT_dp2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R / pow(data::pstar,2)) * ( tau*auxiliary::derivatives::d2gamma_tau_dpi2(pi,tau) - auxiliary::derivatives::dgamma_pi_dpi(pi,tau) );
				}

				/**
				* @brief Function for computing the second partial derivative of entropy w.r.t. temperature in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Second partial derivative of specific entropy w.r.t. temperature in kJ/(kg*K^3)
				*/
				template <typename U, typename V>
				auto get_d2s_pT_dT2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (3.*constants::R*pow(data::Tstar,2) / pow(T,4)) * auxiliary::derivatives::dgamma_tau_dtau(pi,tau) + (constants::R*pow(data::Tstar,3) / pow(T,5)) * auxiliary::derivatives::d2gamma_tau_dtau2(pi,tau) ;
				}

				/**
				* @brief Function for computing the mixed second partial derivative of entropy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Mixed second partial derivative of specific entropy in kJ/(kg*K^2*Mpa)
				*/
				template <typename U, typename V>
				auto get_d2s_pT_dpT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return -(constants::R*pow(data::Tstar,2) / (data::pstar * pow(T,3))) * auxiliary::derivatives::d2gamma_tau_dpitau(pi,tau) ;
				}

				/**
				* @brief Function for computing the third partial derivative of entropy w.r.t. pressure in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Third partial derivative of specific entropy w.r.t. pressure in kJ/(kg*K*MPa^3)
				*/
				template <typename U, typename V>
				auto get_d3s_pT_dp3(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R / pow(data::pstar,3)) * ( tau*auxiliary::derivatives::d3gamma_tau_dpi3(pi,tau) - auxiliary::derivatives::d2gamma_pi_dpi2(pi,tau) );
				}

				/**
				* @brief Function for computing the mixed third partial derivative of entropy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Mixed third partial derivative of specific entropy in kJ/(kg*K^3*Mpa)
				*/
				template <typename U, typename V>
				auto get_d3s_pT_dpT2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R*pow(data::Tstar,3) / (data::pstar * pow(T,5))) * auxiliary::derivatives::d3gamma_tau_dpitau2(pi,tau) ;
				}

				/**
				* @brief Function for computing the third second partial derivative of entropy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Mixed third partial derivative of specific entropy in kJ/(kg*K^2*Mpa^2)
				*/
				template <typename U, typename V>
				auto get_d3s_pT_dp2T(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return -(constants::R*pow(data::Tstar,2) / (pow(data::pstar,2) * pow(T,3))) * auxiliary::derivatives::d3gamma_tau_dpi2tau(pi,tau) ;
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. pressure in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Partial derivative of temperature w.r.t. pressure in K/MPa
				*/
				template <typename U, typename V>
				auto get_dT_ph_dp(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::derivatives::dtheta_pi_eta_dpi(pi,eta) / data::pstarBack;
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. enthalpy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)
				*/
				template <typename U, typename V>
				auto get_dT_ph_dh(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::derivatives::dtheta_pi_eta_deta(pi,eta) / data::hstarBack;
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. pressure in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Second partial derivative of temperature w.r.t. pressure in K/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dp2(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::derivatives::d2theta_pi_eta_dpi2(pi,eta) / pow(data::pstarBack,2);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. enthalpy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Second partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)^2
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dh2(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::derivatives::d2theta_pi_eta_deta2(pi,eta) / pow(data::hstarBack,2);
				}

				/**
				* @brief Function for computing the mixed second partial derivative of temperature w.r.t. pressure & enthalpy in region 1.
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed second partial derivative of temperature w.r.t. pressure & enthalpy in K/(MPa*kJ/kg)
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dph(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::derivatives::d2theta_pi_eta_dpieta(pi,eta) / (data::hstarBack*data::pstarBack);
				}

			/**@}*/


			}	// end namespace derivatives


		}	// end namespace original


	}	// end namespace region1


}	// end namespace iapws_if97
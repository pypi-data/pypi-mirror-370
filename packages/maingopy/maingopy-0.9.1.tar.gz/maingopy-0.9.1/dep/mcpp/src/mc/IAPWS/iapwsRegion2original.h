/**
 * @file iapwsRegion2original.h
 *
 * @brief File containing template implementation of region 2 of the IAPWS-IF97 model.
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


	namespace region2 {


		namespace original {


			/**
			* @name Forward equations (derived immediately from the basic equation g(p,T) for this region)
			*/
			/**@{*/

				/**
				* @brief Function for computing enthalpy as a function of pressure and temperature in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Specific enthalpy in kJ/kg
				*/
				template <typename U, typename V>
				auto get_h_pT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return constants::R * data::Tstar * (auxiliary::gamma_0_tau(pi,tau) + auxiliary::gamma_r_tau(pi,tau));

				}

				/**
				* @brief Function for computing entropy as a function of pressure and temperature in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Specific entropy in kJ/(kg*K)
				*/
				template <typename U, typename V>
				auto get_s_pT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return constants::R * ( tau*(auxiliary::gamma_0_tau(pi,tau)+auxiliary::gamma_r_tau(pi,tau)) - (auxiliary::gamma_0(pi,tau) + auxiliary::gamma_r(pi,tau)) );
				}

			/**@}*/


			/**
			* @name Backward equations (supplied by the IAPWS for this region)
			*/
			/**@{*/

				/**
				* @brief Function for computing temperature as a function of pressure and enthalpy in region 2a (ie., p<=4MPa).
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Temperature in K
				*/
				template <typename U, typename V>
				auto get_T_ph_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::theta_pi_eta_a(pi,eta);
				}

				/**
				* @brief Function for computing temperature as a function of pressure and enthalpy in region 2b (ie., p>4MPa and h>=h_B2bc(p)).
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Temperature in K
				*/
				template <typename U, typename V>
				auto get_T_ph_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::theta_pi_eta_b(pi,eta);
				}

				/**
				* @brief Function for computing temperature as a function of pressure and enthalpy in region 2c (ie., p>4MPa and h<=h_B2bc(p)).
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Temperature in K
				*/
				template <typename U, typename V>
				auto get_T_ph_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return data::TstarBack * auxiliary::theta_pi_eta_c(pi,eta);
				}

				/**
				* @brief Function for computing temperature as a function of pressure and entropy in region 2a (ie., p<=4MPa).
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Temperature in K
				*/
				template <typename U, typename V>
				auto get_T_ps_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return data::TstarBack * auxiliary::theta_pi_sigma_a(pi,sigma);
				}

				/**
				* @brief Function for computing temperature as a function of pressure and entropy in region 2b (ie., p>4MPa and s>=5.85kJ/(kg*K)).
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Temperature in K
				*/
				template <typename U, typename V>
				auto get_T_ps_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return data::TstarBack * auxiliary::theta_pi_sigma_b(pi,sigma);
				}

				/**
				* @brief Function for computing temperature as a function of pressure and entropy in region 2c (ie., p>4MPa and s<=5.85kJ/(kg*K)).
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Temperature in K
				*/
				template <typename U, typename V>
				auto get_T_ps_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return data::TstarBack * auxiliary::theta_pi_sigma_c(pi,sigma);
				}

			/**@}*/



			/**
			* @name Boundary equations (auxiliary equations defining the boundary between region 2 and 3 as well as between region 2b and 2c)
			*/
			/**@{*/

				/**
				* @brief Function for computing pressure as a function of temperature for the boundary between regions 2 and 3.
				* @param[in] T Temperature in K
				* @return Pressure in MPa
				*/
				template <typename U>
				U get_b23_p_T(const U& T) {
					const U theta = T/data::Tstar23;
					return data::pstar23 * auxiliary::b23_pi_theta(theta);
				}

				/**
				* @brief Function for computing temperature as a function of pressure for the boundary between regions 2 and 3.
				* @param[in] p Pressure in MPa
				* @return Temperature in K
				*/
				template <typename U>
				U get_b23_T_p(const U& p) {
					const U pi = p/data::pstar23;
					return data::Tstar23 * auxiliary::b23_theta_pi(pi);
				}

				/**
				* @brief Function for computing pressure as a function of specific enthalpy for the boundary between regions 2b and 2c.
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Pressure in MPa
				*/
				template <typename U>
				U get_b2bc_p_h(const U& h) {
					const U eta = h/data::hstarBackBC;
					return data::pstarBack * auxiliary::b2bc_pi_eta(eta);
				}

				/**
				* @brief Function for computing specific enthalpy as a function of pressure for the boundary between regions 2b and 2c.
				* @param[in] p Pressure in MPa
				* @return Specific enthalpy in kJ/kg
				*/
				template <typename U>
				U get_b2bc_h_p(const U& p) {
					const U pi = p/data::pstarBack;
					return data::hstarBackBC * auxiliary::b2bc_eta_pi(pi);
				}

			/**@}*/


			namespace derivatives {


			/**
			* @name Derivatives of functions in region 2
			*/
			/**@{*/

				/**
				* @brief Function for computing the partial derivative of enthalpy w.r.t. temperature in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Partial derivative of specific enthalpy w.r.t. temperature in (kJ/kg)/K
				*/
				template <typename U, typename V>
				auto get_dh_pT_dT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return -constants::R * pow(tau,2) * (auxiliary::derivatives::dgamma_0_tau_dtau(pi,tau) + auxiliary::derivatives::dgamma_r_tau_dtau(pi,tau));
				}

				/**
				* @brief Function for computing the partial derivative of enthalpy w.r.t. pressure in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa
				*/
				template <typename U, typename V>
				auto get_dh_pT_dp(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R * data::Tstar / data::pstar) * auxiliary::derivatives::dgamma_r_tau_dpi(pi,tau);
				}

				/**
				* @brief Function for computing the second partial derivative of enthalpy w.r.t. temperature in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Second partial derivative of specific enthalpy w.r.t. temperature in (kJ/kg)/K^2
				*/
				template <typename U, typename V>
				auto get_d2h_pT_dT2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (2.*constants::R*pow(data::Tstar,2)/pow(T,3))*(auxiliary::derivatives::dgamma_0_tau_dtau(pi,tau) + auxiliary::derivatives::dgamma_r_tau_dtau(pi,tau))
							+ (constants::R*pow(data::Tstar,3)/pow(T,4))*(auxiliary::derivatives::d2gamma_0_tau_dtau2(pi,tau) + auxiliary::derivatives::d2gamma_r_tau_dtau2(pi,tau));
				}

				/**
				* @brief Function for computing the second partial derivative of enthalpy w.r.t. pressure in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Second partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2h_pT_dp2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R * data::Tstar / pow(data::pstar,2)) * auxiliary::derivatives::d2gamma_r_tau_dpi2(pi,tau);
				}

				/**
				* @brief Function for computing the mixed second partial derivative of enthalpy in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Mixed second partial derivative of specific enthalpyin (kJ/kg)/(MPa*K)
				*/
				template <typename U, typename V>
				auto get_d2h_pT_dpT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (-constants::R * pow(tau,2) / data::pstar) * auxiliary::derivatives::d2gamma_r_tau_dpitau(pi,tau);
				}

				/**
				* @brief Function for computing the partial derivative of entropy w.r.t. temperature in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Partial derivative of specific entropy w.r.t. temperature in (kJ/(kg*K))/K
				*/
				template <typename U, typename V>
				auto get_ds_pT_dT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return -(constants::R*pow(data::Tstar,2)/pow(T,3)) * (auxiliary::derivatives::dgamma_0_tau_dtau(pi,tau) + auxiliary::derivatives::dgamma_r_tau_dtau(pi,tau));
				}

				/**
				* @brief Function for computing the partial derivative of entropy w.r.t. pressure in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Partial derivative of specific entropy w.r.t. pressure in (kJ/(kg*K))/MPa
				*/
				template <typename U, typename V>
				auto get_ds_pT_dp(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R/data::pstar) * ( tau*auxiliary::derivatives::dgamma_r_tau_dpi(pi,tau) - (auxiliary::gamma_0_pi(pi) + auxiliary::gamma_r_pi(pi,tau)) );
				}

				/**
				* @brief Function for computing the second partial derivative of entropy w.r.t. temperature in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Second partial derivative of specific entropy w.r.t. temperature in (kJ/(kg*K))/K^2
				*/
				template <typename U, typename V>
				auto get_d2s_pT_dT2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (3.*constants::R*pow(data::Tstar,2)/pow(T,4))*(auxiliary::derivatives::dgamma_0_tau_dtau(pi,tau) + auxiliary::derivatives::dgamma_r_tau_dtau(pi,tau))
							+ (constants::R*pow(data::Tstar,3)/pow(T,5))*(auxiliary::derivatives::d2gamma_0_tau_dtau2(pi,tau) + auxiliary::derivatives::d2gamma_r_tau_dtau2(pi,tau));
				}

				/**
				* @brief Function for computing the second partial derivative of entropy w.r.t. pressure in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Second partial derivative of specific entropy w.r.t. pressure in (kJ/(kg*K))/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2s_pT_dp2(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (constants::R/pow(data::pstar,2)) * ( tau*auxiliary::derivatives::d2gamma_r_tau_dpi2(pi,tau) - ( auxiliary::derivatives::dgamma_0_pi_dpi(pi) + auxiliary::derivatives::dgamma_r_pi_dpi(pi,tau) ) );
				}

				/**
				* @brief Function for computing the mixed second partial derivative of entropy in region 2.
				* @param[in] p Pressure in MPa
				* @param[in] T Temperature in K
				* @return Mixed second partial derivative of specific entropy  in (kJ/(kg*K))/(MPa*K)
				*/
				template <typename U, typename V>
				auto get_d2s_pT_dpT(const U& p, const V& T) {
					const U pi = p/data::pstar;
					const V tau = data::Tstar/T;
					return (-constants::R*pow(data::Tstar,2)/(data::pstar*pow(T,3))) * auxiliary::derivatives::d2gamma_r_tau_dpitau(pi,tau);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. pressure in region 2a
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Partial derivative of temperature w.r.t. pressure in K/MPa
				*/
				template <typename U, typename V>
				auto get_dT_ph_dp_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/data::pstarBack) * auxiliary::derivatives::dtheta_pi_eta_dpi_a(pi,eta);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. enthalpy in region 2a
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)
				*/
				template <typename U, typename V>
				auto get_dT_ph_dh_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/data::hstarBack) * auxiliary::derivatives::dtheta_pi_eta_deta_a(pi,eta);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. pressure in region 2a
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Second partial derivative of temperature w.r.t. pressure in K/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dp2_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::pstarBack,2)) * auxiliary::derivatives::d2theta_pi_eta_dpi2_a(pi,eta);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. enthalpy in region 2a
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Second partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)^2
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dh2_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::hstarBack,2)) * auxiliary::derivatives::d2theta_pi_eta_deta2_a(pi,eta);
				}

				/**
				* @brief Function for computing the mixed second partial derivative of temperature in region 2a
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed second partial derivative of temperature in K/(MPa*kJ/kg)
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dph_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(data::pstarBack*data::hstarBack)) * auxiliary::derivatives::d2theta_pi_eta_dpieta_a(pi,eta);
				}

				/**
				* @brief Function for computing the third partial derivative of temperature w.r.t. enthalpy in region 2a
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Third partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)^3
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dh3_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::hstarBack,3)) * auxiliary::derivatives::d3theta_pi_eta_deta3_a(pi,eta);
				}

				/**
				* @brief Function for computing a mixed third partial derivative of temperature in region 2a
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed third partial derivative of temperature in K/(MPa^2*kJ/kg)
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dp2h_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(pow(data::pstarBack,2)*data::hstarBack)) * auxiliary::derivatives::d3theta_pi_eta_dpi2eta_a(pi,eta);
				}

				/**
				* @brief Function for computing a mixed third partial derivative of temperature in region 2a
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed third partial derivative of temperature in K/(MPa*(kJ/kg)^2)
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dph2_a(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(pow(data::hstarBack,2)*data::pstarBack)) * auxiliary::derivatives::d3theta_pi_eta_dpieta2_a(pi,eta);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. pressure in region 2b
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Partial derivative of temperature w.r.t. pressure in K/MPa
				*/
				template <typename U, typename V>
				auto get_dT_ph_dp_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/data::pstarBack) * auxiliary::derivatives::dtheta_pi_eta_dpi_b(pi,eta);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. enthalpy in region 2b
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)
				*/
				template <typename U, typename V>
				auto get_dT_ph_dh_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/data::hstarBack) * auxiliary::derivatives::dtheta_pi_eta_deta_b(pi,eta);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. pressure in region 2b
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Second partial derivative of temperature w.r.t. pressure in K/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dp2_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::pstarBack,2)) * auxiliary::derivatives::d2theta_pi_eta_dpi2_b(pi,eta);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. enthalpy in region 2b
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Second partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)^2
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dh2_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::hstarBack,2)) * auxiliary::derivatives::d2theta_pi_eta_deta2_b(pi,eta);
				}

				/**
				* @brief Function for computing the mixed second partial derivative of temperature in region 2b
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed second partial derivative of temperature in K/(MPa*kJ/kg)
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dph_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(data::hstarBack*data::hstarBack)) * auxiliary::derivatives::d2theta_pi_eta_dpieta_b(pi,eta);
				}

				/**
				* @brief Function for computing the third partial derivative of temperature w.r.t. enthalpy in region 2b
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Third partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)^3
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dh3_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::hstarBack,3)) * auxiliary::derivatives::d3theta_pi_eta_deta3_b(pi,eta);
				}

				/**
				* @brief Function for computing a mixed third partial derivative of temperature in region 2b
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed third partial derivative of temperature in K/(MPa^2*kJ/kg)
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dp2h_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(pow(data::pstarBack,2)*data::hstarBack)) * auxiliary::derivatives::d3theta_pi_eta_dpi2eta_b(pi,eta);
				}

				/**
				* @brief Function for computing a mixed third partial derivative of temperature in region 2b
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed third partial derivative of temperature in K/(MPa*(kJ/kg)^2)
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dph2_b(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(pow(data::hstarBack,2)*data::pstarBack)) * auxiliary::derivatives::d3theta_pi_eta_dpieta2_b(pi,eta);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. pressure in region 2c
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Partial derivative of temperature w.r.t. pressure in K/MPa
				*/
				template <typename U, typename V>
				auto get_dT_ph_dp_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/data::pstarBack) * auxiliary::derivatives::dtheta_pi_eta_dpi_c(pi,eta);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. enthalpy in region 2c
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)
				*/
				template <typename U, typename V>
				auto get_dT_ph_dh_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/data::hstarBack) * auxiliary::derivatives::dtheta_pi_eta_deta_c(pi,eta);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. pressure in region 2c
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Second partial derivative of temperature w.r.t. pressure in K/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dp2_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::pstarBack,2)) * auxiliary::derivatives::d2theta_pi_eta_dpi2_c(pi,eta);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. enthalpy in region 2c
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Second partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)^2
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dh2_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::hstarBack,2)) * auxiliary::derivatives::d2theta_pi_eta_deta2_c(pi,eta);
				}

				/**
				* @brief Function for computing the mixed second partial derivative of temperature in region 2c
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed second partial derivative of temperature in K/(MPa*kJ/kg)
				*/
				template <typename U, typename V>
				auto get_d2T_ph_dph_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(data::hstarBack*data::hstarBack)) * auxiliary::derivatives::d2theta_pi_eta_dpieta_c(pi,eta);
				}

				/**
				* @brief Function for computing the third partial derivative of temperature w.r.t. enthalpy in region 2c
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Third partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)^3
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dh3_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/pow(data::hstarBack,3)) * auxiliary::derivatives::d3theta_pi_eta_deta3_c(pi,eta);
				}

				/**
				* @brief Function for computing a mixed third partial derivative of temperature in region 2c
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed third partial derivative of temperature in K/(MPa^2*kJ/kg)
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dp2h_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(pow(data::pstarBack,2)*data::hstarBack)) * auxiliary::derivatives::d3theta_pi_eta_dpi2eta_c(pi,eta);
				}

				/**
				* @brief Function for computing a mixed third partial derivative of temperature in region 2c
				* @param[in] p Pressure in MPa
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Mixed third partial derivative of temperature in K/(MPa*(kJ/kg)^2)
				*/
				template <typename U, typename V>
				auto get_d3T_ph_dph2_c(const U& p, const V& h) {
					const U pi = p/data::pstarBack;
					const V eta = h/data::hstarBack;
					return (data::TstarBack/(pow(data::hstarBack,2)*data::pstarBack)) * auxiliary::derivatives::d3theta_pi_eta_dpieta2_c(pi,eta);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. pressure in region 2a (ie., p<=4MPa).
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Derivative of temperature w.r.t. pressure in K/MPa
				*/
				template <typename U, typename V>
				auto get_dT_ps_dp_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return (data::TstarBack/data::pstarBack) * auxiliary::derivatives::dtheta_pi_sigma_dpi_a(pi,sigma);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. entropy in region 2a (ie., p<=4MPa).
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_dT_ps_ds_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return (data::TstarBack/data::sstarBackA) * auxiliary::derivatives::dtheta_pi_sigma_dsigma_a(pi,sigma);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. pressure in region 2a (ie., p<=4MPa).
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Second derivative of temperature w.r.t. pressure in K/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2T_ps_dp2_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return (data::TstarBack/pow(data::pstarBack,2)) * auxiliary::derivatives::d2theta_pi_sigma_dpi2_a(pi,sigma);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. entropy in region 2a (ie., p<=4MPa).
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Second derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))^2
				*/
				template <typename U, typename V>
				auto get_d2T_ps_ds2_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return (data::TstarBack/pow(data::sstarBackA,2)) * auxiliary::derivatives::d2theta_pi_sigma_dsigma2_a(pi,sigma);
				}

				/**
				* @brief Function for computing the mixed second derivative of temperature in region 2a (ie., p<=4MPa).
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed second derivative of temperature in K/(MPa*kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_d2T_ps_dps_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return (data::TstarBack/(data::pstarBack*data::sstarBackA)) * auxiliary::derivatives::d2theta_pi_sigma_dpisigma_a(pi,sigma);
				}

				/**
				* @brief Function for computing the third partial derivative of temperature w.r.t. entropy in region 2a.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Third derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))^3
				*/
				template <typename U, typename V>
				auto get_d3T_ps_ds3_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return (data::TstarBack/pow(data::sstarBackA,3)) * auxiliary::derivatives::d3theta_pi_sigma_dsigma3_a(pi,sigma);
				}

				/**
				* @brief Function for computing a mixed third derivative of temperature in region 2a.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed third derivative of temperature in K/(MPa^2*kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_d3T_ps_dp2s_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return (data::TstarBack/(data::sstarBackA*pow(data::pstarBack,2))) * auxiliary::derivatives::d3theta_pi_sigma_dpi2sigma_a(pi,sigma);
				}

				/**
				* @brief Function for computing a mixed third derivative of temperature in region 2a.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed third derivative of temperature in K/(MPa*(kJ/(kg*K))^2)
				*/
				template <typename U, typename V>
				auto get_d3T_ps_dps2_a(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackA;
					return (data::TstarBack/(pow(data::sstarBackA,2)*data::pstarBack)) * auxiliary::derivatives::d3theta_pi_sigma_dpisigma2_a(pi,sigma);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. pressure in region 2b.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Derivative of temperature w.r.t. pressure in K/MPa
				*/
				template <typename U, typename V>
				auto get_dT_ps_dp_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return (data::TstarBack/data::pstarBack) * auxiliary::derivatives::dtheta_pi_sigma_dpi_b(pi,sigma);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. entropy in region 2b.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_dT_ps_ds_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return (data::TstarBack/data::sstarBackB) * auxiliary::derivatives::dtheta_pi_sigma_dsigma_b(pi,sigma);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. pressure in region 2b.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Second derivative of temperature w.r.t. pressure in K/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2T_ps_dp2_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return (data::TstarBack/pow(data::pstarBack,2)) * auxiliary::derivatives::d2theta_pi_sigma_dpi2_b(pi,sigma);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. entropy in region 2b.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Second derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))^2
				*/
				template <typename U, typename V>
				auto get_d2T_ps_ds2_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return (data::TstarBack/pow(data::sstarBackB,2)) * auxiliary::derivatives::d2theta_pi_sigma_dsigma2_b(pi,sigma);
				}

				/**
				* @brief Function for computing the mixed second derivative of temperature in region 2b.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed second derivative of temperature in K/(MPa*kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_d2T_ps_dps_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return (data::TstarBack/(data::sstarBackB*data::pstarBack)) * auxiliary::derivatives::d2theta_pi_sigma_dpisigma_b(pi,sigma);
				}

				/**
				* @brief Function for computing the third partial derivative of temperature w.r.t. entropy in region 2b.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Third derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))^3
				*/
				template <typename U, typename V>
				auto get_d3T_ps_ds3_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return (data::TstarBack/pow(data::sstarBackB,3)) * auxiliary::derivatives::d3theta_pi_sigma_dsigma3_b(pi,sigma);
				}

				/**
				* @brief Function for computing a mixed third derivative of temperature in region 2b.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed third derivative of temperature in K/(MPa^2*kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_d3T_ps_dp2s_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return (data::TstarBack/(data::sstarBackB*pow(data::pstarBack,2))) * auxiliary::derivatives::d3theta_pi_sigma_dpi2sigma_b(pi,sigma);
				}

				/**
				* @brief Function for computing a mixed third derivative of temperature in region 2b.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed third derivative of temperature in K/(MPa*(kJ/(kg*K))^2)
				*/
				template <typename U, typename V>
				auto get_d3T_ps_dps2_b(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackB;
					return (data::TstarBack/(pow(data::sstarBackB,2)*data::pstarBack)) * auxiliary::derivatives::d3theta_pi_sigma_dpisigma2_b(pi,sigma);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. pressure in region 2c.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Derivative of temperature w.r.t. pressure in K/MPa
				*/
				template <typename U, typename V>
				auto get_dT_ps_dp_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return (data::TstarBack/data::pstarBack) * auxiliary::derivatives::dtheta_pi_sigma_dpi_c(pi,sigma);
				}

				/**
				* @brief Function for computing the partial derivative of temperature w.r.t. entropy in region 2c.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_dT_ps_ds_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return (data::TstarBack/data::sstarBackC) * auxiliary::derivatives::dtheta_pi_sigma_dsigma_c(pi,sigma);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. pressure in region 2c.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Second derivative of temperature w.r.t. pressure in K/MPa^2
				*/
				template <typename U, typename V>
				auto get_d2T_ps_dp2_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return (data::TstarBack/pow(data::pstarBack,2)) * auxiliary::derivatives::d2theta_pi_sigma_dpi2_c(pi,sigma);
				}

				/**
				* @brief Function for computing the second partial derivative of temperature w.r.t. entropy in region 2c.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Second erivative of temperature w.r.t. entropy in K/(kJ/(kg*K))^2
				*/
				template <typename U, typename V>
				auto get_d2T_ps_ds2_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return (data::TstarBack/pow(data::sstarBackC,2)) * auxiliary::derivatives::d2theta_pi_sigma_dsigma2_c(pi,sigma);
				}

				/**
				* @brief Function for computing the mixed partial derivative of temperature in region 2c.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed derivative of temperature in K/(MPa*kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_d2T_ps_dps_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return (data::TstarBack/(data::sstarBackC*data::pstarBack)) * auxiliary::derivatives::d2theta_pi_sigma_dpisigma_c(pi,sigma);
				}

				/**
				* @brief Function for computing the third partial derivative of temperature w.r.t. entropy in region 2c.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Third derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))^3
				*/
				template <typename U, typename V>
				auto get_d3T_ps_ds3_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return (data::TstarBack/pow(data::sstarBackC,3)) * auxiliary::derivatives::d3theta_pi_sigma_dsigma3_c(pi,sigma);
				}

				/**
				* @brief Function for computing a mixed third derivative of temperature in region 2c.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed third derivative of temperature in K/(MPa^2*kJ/(kg*K))
				*/
				template <typename U, typename V>
				auto get_d3T_ps_dp2s_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return (data::TstarBack/(data::sstarBackC*pow(data::pstarBack,2))) * auxiliary::derivatives::d3theta_pi_sigma_dpi2sigma_c(pi,sigma);
				}

				/**
				* @brief Function for computing a mixed third derivative of temperature in region 2c.
				* @param[in] p Pressure in MPa
				* @param[in] s Specific entropy in kJ/(kg*K)
				* @return Mixed third derivative of temperature in K/(MPa*(kJ/(kg*K))^2)
				*/
				template <typename U, typename V>
				auto get_d3T_ps_dps2_c(const U& p, const V& s) {
					const U pi = p/data::pstarBack;
					const V sigma = s/data::sstarBackC;
					return (data::TstarBack/(pow(data::sstarBackC,2)*data::pstarBack)) * auxiliary::derivatives::d3theta_pi_sigma_dpisigma2_c(pi,sigma);
				}

				/**
				* @brief Function for computing the derivative of get_b23_p_T
				* @param[in] T Temperature in K
				* @return Derivative of pressure in MPa/K
				*/
				template <typename U>
				U get_b23_dp_dT(const U& T) {
					const U theta = T/data::Tstar23;
					return data::pstar23 * auxiliary::derivatives::b23_dpi_theta(theta);
				}

				/**
				* @brief Function for computing the derivative of get_b23_T_p
				* @param[in] p Pressure in MPa
				* @return Derivative of temperature in K/MPa
				*/
				template <typename U>
				U get_b23_dT_dp(const U& p) {
					const U pi = p/data::pstar23;
					return data::Tstar23 * auxiliary::derivatives::b23_dtheta_pi(pi);
				}

				/**
				* @brief Function for computing the derivative of get_b2bc_p_h
				* @param[in] h Specific enthalpy in kJ/kg
				* @return Derivative of pressure in MPa/(kJ/kg)
				*/
				template <typename U>
				U get_b2bc_dp_dh(const U& h) {
					const U eta = h/data::hstarBackBC;
					return data::pstarBack * auxiliary::derivatives::b2bc_dpi_eta(eta);
				}

				/**
				* @brief Function for computing the derivative of get_b2bc_h_p
				* @param[in] p Pressure in MPa
				* @return Derivative of specific enthalpy in (kJ/kg)/MPa
				*/
				template <typename U>
				U get_b2bc_dh_dp(const U& p) {
					const U pi = p/data::pstarBack;
					return data::hstarBackBC * auxiliary::derivatives::b2bc_deta_pi(pi);
				}

			/**@}*/


			}	// end namespace derivatives


		} // end namespace original


	}	// end namespace region2


}	// end namespace iapws_if97
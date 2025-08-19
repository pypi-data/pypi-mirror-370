/**
 * @file iapwsRegion1.h
 *
 * @brief File containing template implementation of region 1 of the IAPWS-IF97 model, augmented with the utility functions h(p,s) and s(p,h), and extended to provide more benign values outside of the original function domains.
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
 * @author Dominik Bongartz, Jaromail Najman, Alexander Mitsos
 * @date 15.08.2019
 *
 */

#pragma once

#include "iapwsData.h"
#include "iapwsAuxiliary.h"
#include "iapwsAuxiliaryDerivatives.h"
#include "iapwsRegion1original.h"
#include "iapwsRegion4original.h"


namespace iapws_if97 {


	namespace region1 {


		/**
		* @name Forward equations (derived immediately from the basic equation g(p,T) for this region)
		*/
		/**@{*/

			/**
			* @brief Function for computing enthalpy as a function of pressure and temperature in region 1 (original version before cutting at hmax).
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Specific enthalpy in kJ/kg
			*/
			template <typename U, typename V>
			auto get_h_pT_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::get_h_pT(p,T);
				} else {
					// Extrapolate linearly w.r.t from (ps(T),T)
					return original::get_h_pT(psat,T) + original::derivatives::get_dh_pT_dp(psat,T)*(p-psat);
				}
			}

			/**
			* @brief Function for computing enthalpy as a function of pressure and temperature in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Specific enthalpy in kJ/kg
			*/
			template <typename U, typename V>
			auto get_h_pT(const U&  p, const V&  T) {
				const auto h = get_h_pT_uncut(p,T);
				return min(h,(decltype(h))data::hmax);
			}

			/**
			* @brief Function for computing entropy as a function of pressure and temperature in region 1 (original version before cutting at smax)
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Specific entropy in kJ/(kg*K)
			*/
			template <typename U, typename V>
			auto get_s_pT_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::get_s_pT(p,T);
				} else {
					// Extrapolate linearly w.r.t from (ps(T),T)
					return original::get_s_pT(psat,T) + original::derivatives::get_ds_pT_dp(psat,T)*(p-psat);
				}
			}

			/**
			* @brief Function for computing entropy as a function of pressure and temperature in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Specific entropy in kJ/(kg*K)
			*/
			template <typename U, typename V>
			auto get_s_pT(const U&  p, const V&  T) {
				const auto s = get_s_pT_uncut(p,T);
				return min(s,(decltype(s))data::smax);
			}

		/**@}*/


		/**
		* @name Backward equations (supplied by the IAPWS for this region)
		*/
		/**@{*/

			/**
			* @brief Function for computing temperature as a function of pressure and enthalpy in region 1 (original version before cutting at Tmin and Tmax)
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Temperature in K
			*/
			template <typename U, typename V>
			auto get_T_ph_uncut(const U&  p, const V&  h) {
				if (p>=region2::data::pminB23) {
					return original::get_T_ph(p,h);
				} else {
					const U hmax = original::get_h_pT(p,region4::original::get_Ts_p(p));
					if (h<=hmax) {
						return original::get_T_ph(p,h);
					} else {
						return original::get_T_ph(p,hmax) + 0.1*(h-hmax);
					}
				}
			}

			/**
			* @brief Function for computing temperature as a function of pressure and enthalpy in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Temperature in K
			*/
			template <typename U, typename V>
			auto get_T_ph(const U&  p, const V&  h) {
				const auto T = get_T_ph_uncut(p,h);
				return max(min(T,(decltype(T))data::Tmax),(decltype(T))data::Tmin);
			}

			/**
			* @brief Function for computing temperature as a function of pressure and entropy in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] s Specific entropy in kJ/(kg*K)
			* @return Temperature in K
			*/
			template <typename U, typename V>
			auto get_T_ps(const U&  p, const V&  s) {
				auto T = original::get_T_ps(p,s);
				return max(min(T,(decltype(T))data::Tmax),(decltype(T))data::Tmin);
			}

		/**@}*/


		/**
		* @name Utility functions (derived from original IAPWS functions for this region)
		*/
		/**@{*/

			/**
			* @brief Function for computing enthalpy as a function of pressure and entropy in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] s Specific entropy in kJ/(kg*K)
			* @return Specific enthalpy in kJ/kg
			*/
			template <typename U, typename V>
			auto get_h_ps(const U&  p, const V&  s) {
				return get_h_pT(p,get_T_ps(p,s));
			}

			/**
			* @brief Function for computing entropy as a function of pressure and enthalpy in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Specific entropy in kJ/(kg*K)
			*/
			template <typename U, typename V>
			auto get_s_ph(const U&  p, const V&  h) {
				return get_s_pT(p,get_T_ph(p,h));
			}

		/**@}*/


		namespace derivatives {
			
		/**
		* @name Derivatives of functions in region 1
		*/
		/**@{*/

			/**
			* @brief Function for computing the partial derivative of enthalpy w.r.t. temperature in region 1
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Partial derivative of specific enthalpy w.r.t. temperature in (kJ/kg)/K
			*/
			template <typename U, typename V>
			auto get_dh_pT_dT_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::derivatives::get_dh_pT_dT(p,T);
				} else {
					const V dpsatdT = region4::original::derivatives::get_dps_dT(T);
					return original::derivatives::get_dh_pT_dT(psat,T) + (original::derivatives::get_d2h_pT_dpT(psat,T)+original::derivatives::get_d2h_pT_dp2(psat,T)*dpsatdT)*(p-psat);
				}
			}

			/**
			* @brief Function for computing the partial derivative of enthalpy w.r.t. pressure in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa
			*/
			template <typename U, typename V>
			auto get_dh_pT_dp_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::derivatives::get_dh_pT_dp(p,T);
				} else {
					return original::derivatives::get_dh_pT_dp(psat,T);
				}
			}

			/**
			* @brief Function for computing the second partial derivative of enthalpy w.r.t. temperature in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Second partial derivative of specific enthalpy w.r.t. temperature in (kJ/kg)/K^2
			*/
			template <typename U, typename V>
			auto get_d2h_pT_dT2_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::derivatives::get_d2h_pT_dT2(p,T);
				} else {
					const V ps = region4::original::get_ps_T(T);
					const V dpsdT = region4::original::derivatives::get_dps_dT(T);
					const V d2psdT2 = region4::original::derivatives::get_d2ps_dT2(T);
					return original::derivatives::get_d2h_pT_dT2(ps,T)
									   + (original::derivatives::get_d3h_pT_dpT2(ps,T) + 2.*original::derivatives::get_d3h_pT_dp2T(ps,T)*dpsdT + original::derivatives::get_d3h_pT_dp3(ps,T)*pow(dpsdT,2) + original::derivatives::get_d2h_pT_dp2(ps,T)*d2psdT2) * (p-ps)
									   - original::derivatives::get_d2h_pT_dp2(ps,T)*pow(dpsdT,2);
				}
			}

			/**
			* @brief Function for computing the second partial derivative of enthalpy w.r.t. pressure in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Second partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa^2
			*/
			template <typename U, typename V>
			auto get_d2h_pT_dp2_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::derivatives::get_d2h_pT_dp2(p,T);
				} else {
					return (decltype(original::derivatives::get_d2h_pT_dp2(psat,T)))0.;
				}
			}

			/**
			* @brief Function for computing the derivative of entropy w.r.t. pressure in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Partial derivative of specific entropy w.r.t. pressure in kJ/(kg*K*MPa)
			*/
			template <typename U, typename V>
			auto get_ds_pT_dp_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::derivatives::get_ds_pT_dp(p,T);
				} else {
					return original::derivatives::get_ds_pT_dp(psat,T);
				}
			}

			/**
			* @brief Function for computing the derivative of entropy w.r.t. temperature in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Partial derivative of specific entropy w.r.t. temperature in kJ/(kg*K^2)
			*/
			template <typename U, typename V>
			auto get_ds_pT_dT_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::derivatives::get_ds_pT_dT(p,T);
				} else {
					V dpsatdT = region4::original::derivatives::get_dps_dT(T);
					return original::derivatives::get_ds_pT_dT(psat,T)
						 + ( original::derivatives::get_d2s_pT_dpT(psat,T) + original::derivatives::get_d2s_pT_dp2(psat,T)*dpsatdT ) * (p-psat);
				}
			}

			/**
			* @brief Function for computing the second partial derivative of entropy w.r.t. pressure in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Second partial derivative of specific entropy w.r.t. pressure in kJ/(kg*K*MPa^2)
			*/
			template <typename U, typename V>
			auto get_d2s_pT_dp2_uncut(const U&  p, const V&  T) {
				const V psat = region4::original::get_ps_T(T);
				if (p >= psat) {
					return original::derivatives::get_d2s_pT_dT2(p,T);
				} else {
					return (decltype(original::derivatives::get_d2s_pT_dT2(p,T)))0.;
				}
			}

			/**
			* @brief Function for computing the partial derivative of temperature w.r.t. pressure in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Partial derivative of temperature w.r.t. pressure in K/MPa
			*/
			template <typename U, typename V>
			auto get_dT_ph_dp_uncut(const U&  p, const V&  h) {
				if (p>=region2::data::pminB23) {
					return original::derivatives::get_dT_ph_dp(p,h);
				} else {
					const U hmax = original::get_h_pT(p,region4::original::get_Ts_p(p));
					if (h<=hmax) {
						return original::derivatives::get_dT_ph_dp(p,h);
					} else {
						const U Ts = region4::original::get_Ts_p(p);
						const U dTsdp = region4::original::derivatives::get_dTs_dp(p);
						const U dhliqdp = original::derivatives::get_dh_pT_dp(p,Ts) + original::derivatives::get_dh_pT_dT(p,Ts)*dTsdp;
						return original::derivatives::get_dT_ph_dp(p,hmax) + (original::derivatives::get_dT_ph_dh(p,hmax)-0.1)*dhliqdp;
					}
				}
			}

			/**
			* @brief Function for computing the partial derivative of temperature w.r.t. enthalpy in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Partial derivative of temperature w.r.t. enthalpy in K/(kJ/kg)
			*/
			template <typename U, typename V>
			auto get_dT_ph_dh_uncut(const U&  p, const V&  h) {
				if (p>=region2::data::pminB23) {
					return original::derivatives::get_dT_ph_dh(p,h);
				} else {
					const U hmax = original::get_h_pT(p,region4::original::get_Ts_p(p));
					if (h<=hmax) {
						return original::derivatives::get_dT_ph_dh(p,h);
					} else {
						return (decltype(original::derivatives::get_dT_ph_dh(p,hmax)))0.1;
					}
				}
			}

			/**
			* @brief Function for computing the second partial derivative of temperature w.r.t. pressure in region 1.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Second partial derivative of temperature w.r.t. pressure in K/MPa^2
			*/
			template <typename U, typename V>
			auto get_d2T_ph_dp2_uncut(const U&  p, const V&  h) {
				if (p>=region2::data::pminB23) {
					return original::derivatives::get_d2T_ph_dp2(p,h);
				} else {
					const U hmax = original::get_h_pT(p,region4::original::get_Ts_p(p));
					if (h<=hmax) {
						return original::derivatives::get_d2T_ph_dp2(p,h);
					} else {
						const U Ts = region4::original::get_Ts_p(p);
						const U dTsdp = region4::original::derivatives::get_dTs_dp(p);
						const U d2Tsdp2 = region4::original::derivatives::get_d2Ts_dp2(p);
						const U dhliqdp = original::derivatives::get_dh_pT_dp(p,Ts) + original::derivatives::get_dh_pT_dT(p,Ts)*dTsdp;
						const U d2hliqdp2 = original::derivatives::get_d2h_pT_dp2(p,Ts) + 2.*original::derivatives::get_d2h_pT_dpT(p,Ts)*dTsdp + original::derivatives::get_d2h_pT_dT2(p,Ts)*pow(dTsdp,2) + original::derivatives::get_dh_pT_dT(p,Ts)*d2Tsdp2;
						return original::derivatives::get_d2T_ph_dp2(p,hmax)
								+ ( 2.*original::derivatives::get_d2T_ph_dph(p,hmax) + original::derivatives::get_d2T_ph_dh2(p,hmax)*dhliqdp ) * dhliqdp
								+ ( original::derivatives::get_dT_ph_dh(p,hmax) - 0.1 ) * d2hliqdp2;
					}
				}
			}

		/**@}*/
		

		}	// end namespace derivatives


	}	// end namespace region1


}	// end namespace iapws_if97
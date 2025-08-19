/**
 * @file iapwsRegion2.h
 *
 * @brief File containing template implementation of region 2 of the IAPWS-IF97 model, augmented with the utility functions h(p,s) and s(p,h), and extended to provide more benign values outside of the original function domains.
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
#include "iapwsRegion2original.h"
#include "iapwsRegion4original.h"


namespace iapws_if97 {


	namespace region2 {


		namespace auxiliary {
			
			
			/**
			* @brief Auxiliary function describing the boundary of the relaxed physical domain of region 2 for h(p,T)
			* @param[in] T Temperature in K
			* @return Pressure in MPa
			*/
			template <typename U>
			U plim_T(const U& T) {
				U plim;
				if (T<=data::Tplim) {
					plim = region4::original::get_ps_T(T);
				} else {
					plim = data::aPlim + data::bPlim*T + data::cPlim*pow(T,2) + data::dPlim*pow(T,3);
				}
				return plim;
			}

			/**
			* @brief Auxiliary function describing the boundary of the relaxed physical domain of region 2 for s(p,T)
			* @param[in] p Pressure in MPa
			* @return Temperature in K
			*/
			template <typename U>
			U Tlim_p(const U& p) {
				U Tlim;
				if (p<=data::pminB23) {
					Tlim = region4::original::get_Ts_p(p);
				} else {
					Tlim = data::aTlim + data::bTlim*p + data::cTlim*pow(p,2) + data::dTlim*pow(p,3);
				}
				return Tlim;
			}

			/**
			* @brief Auxiliary function describing the boundary of the relaxed physical domain of region 2 for T(p,h) above pminB23 (!)
			* @param[in] p Pressure in MPa
			* @return Enthalpy in kJ/kg
			*/
			template <typename U>
			U hlim_p(const U& p) {
				U hlim;
				if (p <= data::pminB23) {
					hlim = original::get_h_pT(p,region4::original::get_Ts_p(p));
				} else {
					hlim = data::aHlim + data::bHlim*p + data::cHlim*pow(p,2) + data::dHlim*exp(-pow((p-data::eHlim)/data::fHlim,2));
				}
				return hlim;
			}
			
			
		}	// end namespace auxiliary

		/**
		* @name Forward equations (derived immediately from the basic equation g(p,T) for this region)
		*/
		/**@{*/

			/**
			* @brief Function for computing enthalpy as a function of pressure and temperature in region 2 (original version before cutting at hmin).
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Specific enthalpy in kJ/kg
			*/
			template <typename U, typename V>
			auto get_h_pT_uncut(const U&  p, const V&  T) {
				const V plim = auxiliary::plim_T(T);
				if (p <= plim) {
					return original::get_h_pT(p,T);
				} else {
					return original::get_h_pT(plim,T) - (-59.+1.25*T/sqrt(plim))*(p-plim);
				}
			}

			/**
			* @brief Function for computing enthalpy as a function of pressure and temperature in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Specific enthalpy in kJ/kg
			*/
			template <typename U, typename V>
			auto get_h_pT(const U&  p, const V&  T) {
				const auto h = get_h_pT_uncut(p,T);
				return max(h,(decltype(h))data::hmin);
			}

			/**
			* @brief Function for computing entropy as a function of pressure and temperature in region 2 (original version before cutting at smin).
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Specific entropy in kJ/(kg*K)
			*/
			template <typename U, typename V>
			auto get_s_pT_uncut(const U&  p, const V&  T) {
				const V Tlim = auxiliary::Tlim_p(p);
				if (T >= Tlim) {
					return original::get_s_pT(p,T);
				} else {
					return original::get_s_pT(p,Tlim) + 0.003*(T-Tlim);
				}
			}

			/**
			* @brief Function for computing entropy as a function of pressure and temperature in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Specific entropy in kJ/(kg*K)
			*/
			template <typename U, typename V>
			auto get_s_pT(const U&  p, const V&  T) {
				const auto s = get_s_pT_uncut(p,T);
				return max(s,(decltype(s))data::smin);
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
			U get_b23_p_T(const U&  T) {
				if (T >= data::TB23hat) {
					return original::get_b23_p_T(T);
				} else {
					return data::pB23hat + data::kTB23*(T - data::TB23hat);
				}
			}

			/**
			* @brief Function for computing temperature as a function of pressure for the boundary between regions 2 and 3.
			* @param[in] p Pressure in MPa
			* @return Temperature in K
			*/
			template <typename U>
			U get_b23_T_p(const U&  p) {
				if (p >= data::pB23hat) {
					return original::get_b23_T_p(p);
				} else {
					return data::TB23hat + (p - data::pB23hat)/data::kTB23;
				}
			}

			/**
			* @brief Function for computing pressure as a function of specific enthalpy for the boundary between regions 2b and 2c.
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Pressure in MPa
			*/
			template <typename U>
			U get_b2bc_p_h(const U&  h) {
				if (h >= data::hminB2bc) {
					return original::get_b2bc_p_h(h);
				} else {
					return data::pmin + (h-data::hmin)/data::khB2bc;
				}
			}

			/**
			* @brief Function for computing specific enthalpy as a function of pressure for the boundary between regions 2b and 2c.
			* @param[in] p Pressure in MPa
			* @return Specific enthalpy in kJ/kg
			*/
			template <typename U>
			U get_b2bc_h_p(const U&  p) {
				if (p >= data::pminB2bc) {
					return original::get_b2bc_h_p(p);
				} else {
					return data::hmin + data::khB2bc*(p-data::pmin);
				}
			}

		/**@}*/


		/**
		* @name Utility functions (derived from original IAPWS functions for this region)
		*/
		/**@{*/

			/**
			* @brief Function for computing temperature as a function of pressure and enthalpy in region 2, using sub-regions a, b, and c (original version before cutting at Tmin and Tmax).
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Temperature in K
			*/
			template <typename U, typename V>
			auto get_T_ph_uncut(const U&  p, const V&  h) {
				const U hlim = auxiliary::hlim_p(p);
				if (p <= data::pminB) {			// could be in 2a or 4/1
					if ( h >= hlim ) {
						return original::get_T_ph_a(p,h);
					} else {
						return original::get_T_ph_a(p,hlim) + original::derivatives::get_dT_ph_dh_a(p,hlim)*(h-hlim);
					}
				}
				else if (p <= data::pminC) {	// could be in 2b or 4-1/2
					if ( h >= hlim ) {
						return original::get_T_ph_b(p,h);
					} else {
						return original::get_T_ph_b(p,hlim) + original::derivatives::get_dT_ph_dh_b(p,hlim)*(h-hlim);
					}
				}
				else {							// could be in 2b, 2c, 3 or 4-1/2
					if (h >= original::get_b2bc_h_p(p)) {
						return original::get_T_ph_b(p,h);
					} else {
						if ( h >= hlim ) {
							return original::get_T_ph_c(p,h);
						} else {
							return original::get_T_ph_c(p,hlim) + original::derivatives::get_dT_ph_dh_c(p,hlim)*(h-hlim);
						}
					}
				}
			}

			/**
			* @brief Function for computing temperature as a function of pressure and enthalpy in region 2, using sub-regions a, b, and c.
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
			* @brief Function for computing temperature as a function of pressure and entropy in region 2, using sub-regions a, b, and c (original version before cutting at Tmin and Tmax).
			* @param[in] p Pressure in MPa
			* @param[in] s Specific entropy in kJ/(kg*K)
			* @return Temperature in K
			*/
			template <typename U, typename V>
			auto get_T_ps_uncut(const U&  p, const V&  s) {
				const auto supper = original::get_s_pT(p,data::Tmax);
				const auto Ts = region4::original::get_Ts_p(min(p,(decltype(p))region4::data::pcrit));
				const auto slower = original::get_s_pT(p,Ts);
				if (p <= data::pminB) {		// could be in 2a, below, or above
					if (s<slower) {
						const auto slim = slower;
						return original::get_T_ps_a(p,slim) + original::derivatives::get_dT_ps_ds_a(p,slim)*(s-slim);
					} else if (s>supper) {
						const auto f = 165. - 0.125*(p-data::pmin);
						const auto slim = supper;
						return original::get_T_ps_a(p,slim) + original::derivatives::get_dT_ps_ds_a(p,slim)*(s-slim) + f*pow(s-slim,2);
					} else {
						return original::get_T_ps_a(p,s);
					}
				}
				else  if (p <= data::pminC) {	// could be in 2b, below, or above
					if (s<slower) {
						const auto slim = slower;
						return original::get_T_ps_b(p,slim) + original::derivatives::get_dT_ps_ds_b(p,slim)*(s-slim);
					} else if (s>supper) {
						const auto f = 165. - 0.125*(p-data::pmin);
						const auto slim = supper;
						return original::get_T_ps_b(p,slim) + original::derivatives::get_dT_ps_ds_b(p,slim)*(s-slim) + f*pow(s-slim,2);
					} else {
						return original::get_T_ps_b(p,s);
					}
				}
				else {									// could be in 2b, above, 2c, or below
					if (s <= data::smaxC) {	// could be in 2c or below
						if (s<slower) {
							const auto slim = slower;
							return original::get_T_ps_c(p,slim) + original::derivatives::get_dT_ps_ds_c(p,slim)*(s-slim);
						} else {
							return original::get_T_ps_c(p,s);
						}
					} else {							// could be in 2b or above
						if (s>supper) {
							const auto f = 165. - 0.125*(p-data::pmin);
							const auto slim = supper;
							return original::get_T_ps_b(p,slim) + original::derivatives::get_dT_ps_ds_b(p,slim)*(s-slim) + f*pow(s-slim,2);
						} else {
							return original::get_T_ps_b(p,s);
						}
					}
				}
			}

			/**
			* @brief Function for computing temperature as a function of pressure and entropy in region 2, using sub-regions a, b, and c.
			* @param[in] p Pressure in MPa
			* @param[in] s Specific entropy in kJ/(kg*K)
			* @return Temperature in K
			*/
			template <typename U, typename V>
			auto get_T_ps(const U&  p, const V&  s) {
				const auto T = get_T_ps_uncut(p,s);
				return max(min(T,(decltype(T))data::Tmax),(decltype(T))data::Tmin);
			}

			/**
			* @brief Function for computing enthalpy as a function of pressure and entropy in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] s Specific entropy in kJ/(kg*K)
			* @return Specific enthalpy in kJ/kg
			*/
			template <typename U, typename V>
			auto get_h_ps(const U&  p, const V&  s) {
				return get_h_pT(p,get_T_ps(p,s));
			}

			/**
			* @brief Function for computing entropy as a function of pressure and enthalpy in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Specific entropy in kJ/(kg*K)
			*/
			template <typename U, typename V>
			auto get_s_ph(const U&  p, const V&  h) {
				return get_s_pT(p,get_T_ph(p,h));
			}

		/**@}*/


		namespace auxiliary {
			
			
			namespace derivatives {
			

				/**
				* @brief Auxiliary function describing the derivative of the boundary of the relaxed physical domain of region 2
				* @param[in] T Temperature in K
				* @return Derivative of pressure in MPa/K
				*/
				template <typename U>
				U dplim_dT(const U& T) {
					U dplimdT;
					if (T<=data::Tplim) {
						dplimdT = region4::original::derivatives::get_dps_dT(T);
					} else {
						dplimdT = data::bPlim + 2.*data::cPlim*T + 3.*data::dPlim*pow(T,2);
					}
					return dplimdT;
				}

				/**
				* @brief Auxiliary function describing the second derivative of the boundary of the relaxed physical domain of region 2
				* @param[in] T Temperature in K
				* @return Second derivative of pressure in MPa/K^2
				*/
				template <typename U>
				U d2plim_dT2(const U& T) {
					U d2plimdT2;
					if (T<=data::Tplim) {
						d2plimdT2 = region4::original::derivatives::get_d2ps_dT2(T);
					} else {
						d2plimdT2 = 2.*data::cPlim + 6.*data::dPlim*T;
					}
					return d2plimdT2;
				}

				/**
				* @brief Auxiliary function describing the derivative of the boundary of the relaxed physical domain of region 2 for s(p,T)
				* @param[in] p Pressure in MPa
				* @return Derivative of temperature w.r.t. pressure in K/MPa
				*/
				template <typename U>
				U dTlim_dp(const U& p) {
					U dTlimdp;
					if (p<=data::pminB23) {
						dTlimdp = region4::original::derivatives::get_dTs_dp(p);
					} else {
						dTlimdp = data::bTlim + 2.*data::cTlim*p + 3.*data::dTlim*pow(p,2);
					}
					return dTlimdp;
				}

				/**
				* @brief Auxiliary function describing the second derivative of the boundary of the relaxed physical domain of region 2 for s(p,T)
				* @param[in] p Pressure in MPa
				* @return Second derivative of temperature w.r.t. pressure in K/MPa^2
				*/
				template <typename U>
				U d2Tlim_dp2(const U& p) {
					U d2Tlimdp2;
					if (p<=data::pminB23) {
						d2Tlimdp2 = region4::original::derivatives::get_d2Ts_dp2(p);
					} else {
						d2Tlimdp2 = 2.*data::cTlim + 6.*data::dTlim*p;
					}
					return d2Tlimdp2;
				}

				/**
				* @brief Auxiliary function describing the derivative of the boundary of the relaxed physical domain of region 2 for T(p,h) above pminB23 (!)
				* @param[in] p Pressure in MPa
				* @return Derivative of enthalpy w.r.t. presrue in (kJ/kg)/MPa
				*/
				template <typename U>
				U dhlim_dp(const U& p) {
					U dhlimdp;
					if (p <= data::pminB23) { 
						const U Ts = region4::original::get_Ts_p(p);
						const U dTsdp = region4::original::derivatives::get_dTs_dp(p);
						dhlimdp = original::derivatives::get_dh_pT_dp(p,Ts) + original::derivatives::get_dh_pT_dT(p,Ts)*dTsdp;
					} else {
						dhlimdp = data::bHlim + 2.*data::cHlim*p + data::dHlim*exp(-pow((p-data::eHlim)/data::fHlim,2)) * 2.*(data::eHlim-p)/pow(data::fHlim,2);
					}
					return dhlimdp;
				}
			
			
			}	// end namespace derivatives
			
			
		}	// end namespace auxiliary


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
			auto get_dh_pT_dT_uncut(const U&  p, const V&  T) {
				const V plim = auxiliary::plim_T(T);	// (relaxed) boundary of the physical (non-rectangular) domain of region 2
				if (p <= plim) {
					return original::derivatives::get_dh_pT_dT(p,T);
				} else {
					V dplimdT = auxiliary::derivatives::dplim_dT(T);
					return original::derivatives::get_dh_pT_dT(plim,T) + original::derivatives::get_dh_pT_dp(plim,T) * dplimdT
							- 1.25*((2*plim - T*dplimdT)/(2*pow(plim,1.5))) * (p-plim)
							+ (-59.+1.25*T/sqrt(plim)) * dplimdT;
				}
			}

			/**
			* @brief Function for computing the partial derivative of enthalpy w.r.t. pressure in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa
			*/
			template <typename U, typename V>
			auto get_dh_pT_dp_uncut(const U&  p, const V&  T) {
				const V plim = auxiliary::plim_T(T);	// (relaxed) boundary of the physical (non-rectangular) domain of region 2
				if (p <= plim) {
					return original::derivatives::get_dh_pT_dp(p,T);
				} else {
					return -(-59.+1.25*T/sqrt(plim));
				}
			}

			/**
			* @brief Function for computing the second partial derivative of enthalpy w.r.t. temperature in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Second partial derivative of specific enthalpy w.r.t. temperature in (kJ/kg)/K^2
			*/
			template <typename U, typename V>
			auto get_d2h_pT_dT2_uncut(const U&  p, const V&  T) {
				const V plim = auxiliary::plim_T(T);	// (relaxed) boundary of the physical (non-rectangular) domain of region 2
				if (p <= plim) {
					return original::derivatives::get_d2h_pT_dT2(p,T);
				} else {
					V dplimdT = auxiliary::derivatives::dplim_dT(T);
					V d2plimdT2 = auxiliary::derivatives::d2plim_dT2(T);
					return original::derivatives::get_d2h_pT_dT2(plim,T) + 2.*original::derivatives::get_d2h_pT_dpT(plim,T)*dplimdT
							+ original::derivatives::get_d2h_pT_dp2(plim,T)*pow(dplimdT,2) + original::derivatives::get_dh_pT_dp(plim,T) * d2plimdT2
						- 1.25*( ( (2.*dplimdT - dplimdT - T*d2plimdT2)*2.*pow(plim,1.5) - (2*plim - T*dplimdT)*3*pow(plim,0.5) ) / (4.*pow(plim,3)) ) * (p-plim)
						+ 2.*1.25*((2*plim - T*dplimdT)/(2*pow(plim,1.5)))*dplimdT + (-59.+1.25*T/sqrt(plim)) * d2plimdT2;
				}
			}

			/**
			* @brief Function for computing the second partial derivative of enthalpy w.r.t. pressure in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Second partial derivative of specific enthalpy w.r.t. pressure in (kJ/kg)/MPa^2
			*/
			template <typename U, typename V>
			auto get_d2h_pT_dp2_uncut(const U&  p, const V&  T) {
				const V plim = auxiliary::plim_T(T);	// (relaxed) boundary of the physical (non-rectangular) domain of region 2
				if (p <= plim) {
					return original::derivatives::get_d2h_pT_dp2(p,T);
				} else {
					return (decltype(original::derivatives::get_d2h_pT_dp2(p,T)))0.;
				}
			}

			/**
			* @brief Function for computing the mixed second partial derivative of enthalpy in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Mixed second partial derivative of specific enthalpyin (kJ/kg)/(MPa*K)
			*/
			template <typename U, typename V>
			auto get_d2h_pT_dpT_uncut(const U&  p, const V&  T) {
				const V plim = auxiliary::plim_T(T);	// (relaxed) boundary of the physical (non-rectangular) domain of region 2
				if (p <= plim) {
					return original::derivatives::get_d2h_pT_dpT(p,T);
				} else {
					V dplimdT = auxiliary::derivatives::dplim_dT(T);
					return - 1.25*((2*plim - T*dplimdT)/(2*pow(plim,1.5)));
				}
			}

			/**
			* @brief Function for computing the partial derivative of entropy w.r.t. temperature in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Partial derivative of specific entropy w.r.t. temperature in (kJ/(kg*K))/K
			*/
			template <typename U, typename V>
			auto get_ds_pT_dT_uncut(const U&  p, const V&  T) {
				const V Tlim = auxiliary::Tlim_p(p);
				if (T >= Tlim) {
					return original::derivatives::get_ds_pT_dT(p,T);
				} else {
					return (decltype(original::derivatives::get_ds_pT_dT(p,Tlim)))0.003;
				}
			}

			/**
			* @brief Function for computing the partial derivative of entropy w.r.t. pressure in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Partial derivative of specific entropy w.r.t. pressure in (kJ/(kg*K))/MPa
			*/
			template <typename U, typename V>
			auto get_ds_pT_dp_uncut(const U&  p, const V&  T) {
				const V Tlim = auxiliary::Tlim_p(p);
				if (T >= Tlim) {
					return original::derivatives::get_ds_pT_dp(p,T);
				} else {
					V dTlimdp = auxiliary::derivatives::dTlim_dp(p);
					return original::derivatives::get_ds_pT_dp(p,Tlim) + (original::derivatives::get_ds_pT_dT(p,Tlim) - 0.003)*dTlimdp;
				}
			}

			/**
			* @brief Function for computing the second partial derivative of entropy w.r.t. temperature in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Second partial derivative of specific entropy w.r.t. temperature in (kJ/(kg*K))/K^2
			*/
			template <typename U, typename V>
			auto get_d2s_pT_dT2_uncut(const U&  p, const V&  T) {
				const V Tlim = auxiliary::Tlim_p(p);
				if (T >= Tlim) {
					return original::derivatives::get_d2s_pT_dT2(p,T);
				} else {
					return (decltype(original::derivatives::get_d2s_pT_dT2(p,Tlim)))0.;
				}
			}

			/**
			* @brief Function for computing the second partial derivative of entropy w.r.t. pressure in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Second partial derivative of specific entropy w.r.t. pressure in (kJ/(kg*K))/MPa^2
			*/
			template <typename U, typename V>
			auto get_d2s_pT_dp2_uncut(const U&  p, const V&  T) {
				const V Tlim = auxiliary::Tlim_p(p);
				if (T >= Tlim) {
					return original::derivatives::get_d2s_pT_dp2(p,T);
				} else {
					const V dTlimdp = auxiliary::derivatives::dTlim_dp(p);
					const V d2Tlimdp2 = auxiliary::derivatives::d2Tlim_dp2(p);
					return original::derivatives::get_d2s_pT_dp2(p,Tlim)
							+ (2.*original::derivatives::get_d2s_pT_dpT(p,Tlim) + original::derivatives::get_d2s_pT_dT2(p,Tlim)*dTlimdp)*dTlimdp
							+ (original::derivatives::get_ds_pT_dT(p,Tlim) - 0.003)*d2Tlimdp2;
				}
			}

			/**
			* @brief Function for computing the mixed second partial derivative of entropy in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] T Temperature in K
			* @return Mixed second partial derivative of specific entropy  in (kJ/(kg*K))/(MPa*K)
			*/
			template <typename U, typename V>
			auto get_d2s_pT_dpT_uncut(const U&  p, const V&  T) {
				const V Tlim = auxiliary::Tlim_p(p);
				if (T >= Tlim) {
					return original::derivatives::get_d2s_pT_dpT(p,T);
				} else {
					return (decltype(original::derivatives::get_d2s_pT_dpT(p,Tlim)))0.;
				}
			}

			/**
			* @brief Function for computing the derivative of get_b23_p_T
			* @param[in] T Temperature in K
			* @return Derivative of pressure in MPa/K
			*/
			template <typename U>
			U get_b23_dp_dT(const U&  T) {
				if (T >= data::TB23hat) {
					return original::derivatives::get_b23_dp_dT(T);
				} else {
					return data::kTB23;
				}
			}

			/**
			* @brief Function for computing the derivative of get_b23_T_p
			* @param[in] p Pressure in MPa
			* @return Derivative of temperature in K/MPa
			*/
			template <typename U>
			U get_b23_dT_dp(const U&  p) {
				if (p >= data::pB23hat) {
					return original::derivatives::get_b23_dT_dp(p);
				} else {
					return 1. / data::kTB23;
				}
			}

			/**
			* @brief Function for computing the derivative of get_b2bc_p_h
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Derivative of pressure in MPa/(kJ/kg)
			*/
			template <typename U>
			U get_b2bc_dp_dh(const U&  h) {
				if (h >= data::hminB2bc) {
					return original::derivatives::get_b2bc_dp_dh(h);
				} else {
					return 1./data::khB2bc;
				}
			}

			/**
			* @brief Function for computing the derivative of get_b2bc_h_p
			* @param[in] p Pressure in MPa
			* @return Derivative of specific enthalpy in (kJ/kg)/MPa
			*/
			template <typename U>
			U get_b2bc_dh_dp(const U&  p) {
				if (p >= data::pminB2bc) {
					return original::derivatives::get_b2bc_dh_dp(p);
				} else {
					return data::khB2bc;
				}
			}

			/**
			* @brief Function for computing the derivative of temperature w.r.t. pressure in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Derivative of temperature w.r.t. pressure in K/MPa
			*/
			template <typename U, typename V>
			auto get_dT_ph_dp_uncut(const U&  p, const V&  h) {
				const U hlim = auxiliary::hlim_p(p);
				if (p <= data::pminB) {			// could be in 2a or 4/1
					if ( h >= hlim ) {
						return original::derivatives::get_dT_ph_dp_a(p,h);
					} else {
						const U dhlimdp = auxiliary::derivatives::dhlim_dp(p);
						const U dTdp = original::derivatives::get_dT_ph_dp_a(p,hlim);
						const U d2Tdph = original::derivatives::get_d2T_ph_dph_a(p,hlim);
						const U d2Tdh2 = original::derivatives::get_d2T_ph_dh2_a(p,hlim);
						return dTdp + (d2Tdph + d2Tdh2*dhlimdp)*(h-hlim);
					}
				}
				else if (p <= data::pminC) {	// could be in 2b or 4-1/2
					if ( h >= hlim ) {
						return original::derivatives::get_dT_ph_dp_b(p,h);
					} else {
						const U dhlimdp = auxiliary::derivatives::dhlim_dp(p);
						const U dTdp = original::derivatives::get_dT_ph_dp_b(p,hlim);
						const U d2Tdph = original::derivatives::get_d2T_ph_dph_b(p,hlim);
						const U d2Tdh2 = original::derivatives::get_d2T_ph_dh2_b(p,hlim);
						return dTdp + (d2Tdph + d2Tdh2*dhlimdp)*(h-hlim);
					}
				}
				else {							// could be in 2b, 2c, 3 or 4-1/2
					if (h >= original::get_b2bc_h_p(p)) {
						return original::derivatives::get_dT_ph_dp_b(p,h);
					} else {
						if ( h >= hlim ) {
							return original::derivatives::get_dT_ph_dp_c(p,h);
						} else {
							const U dhlimdp = auxiliary::derivatives::dhlim_dp(p);
							const U dTdp = original::derivatives::get_dT_ph_dp_c(p,hlim);
							const U d2Tdph = original::derivatives::get_d2T_ph_dph_c(p,hlim);
							const U d2Tdh2 = original::derivatives::get_d2T_ph_dh2_c(p,hlim);
							return dTdp + (d2Tdph + d2Tdh2*dhlimdp)*(h-hlim);
						}
					}
				}
			}

			/**
			* @brief Function for computing the derivative of temperature w.r.t. enthalpy in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific enthalpy in kJ/kg
			* @return Derivative of temperature w.r.t. enthalpy in K/(kJ/kg)
			*/
			template <typename U, typename V>
			auto get_dT_ph_dh_uncut(const U&  p, const V&  h) {
				const U hlim = auxiliary::hlim_p(p);
				if (p <= data::pminB) {			// could be in 2a or 4/1
					if ( h >= hlim ) {
						return original::derivatives::get_dT_ph_dh_a(p,h);
					} else {
						return original::derivatives::get_dT_ph_dh_a(p,hlim);
					}
				}
				else if (p <= data::pminC) {	// could be in 2b or 4-1/2
					if ( h >= hlim ) {
						return original::derivatives::get_dT_ph_dh_b(p,h);
					} else {
						return original::derivatives::get_dT_ph_dh_b(p,hlim);
					}
				}
				else {							// could be in 2b, 2c, 3 or 4-1/2
					if (h >= original::get_b2bc_h_p(p)) {
						return original::derivatives::get_dT_ph_dh_b(p,h);
					} else {
						if ( h >= hlim ) {
							return original::derivatives::get_dT_ph_dh_c(p,h);
						} else {
							return original::derivatives::get_dT_ph_dh_c(p,hlim);
						}
					}
				}
			}

			/**
			* @brief Function for computing the derivative of temperature w.r.t. pressure in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific entropy in kJ/(kg*K)
			* @return Derivative of temperature w.r.t. pressure in K/MPa
			*/
			template <typename U, typename V>
			auto get_dT_ps_dp_uncut(const U&  p, const V&  s) {
				const auto supper = original::get_s_pT(p,data::Tmax);
				const auto dsupperdp = original::derivatives::get_ds_pT_dp(p,data::Tmax);
				const auto Ts = region4::original::get_Ts_p(min(p,region4::data::pcrit));
				const auto dTsdp = region4::original::derivatives::get_dTs_dp(p);
				const auto slower = original::get_s_pT(p,Ts);
				const auto dslowerdp = original::derivatives::get_ds_pT_dp(p,Ts) + original::derivatives::get_ds_pT_dT(p,Ts)*dTsdp;
				if (p <= data::pminB) {		// could be in 2a, below, or above
					if (s<slower) {
						const auto slim = slower;
						const auto dslimdp = dslowerdp;
						const auto dTdp    = original::derivatives::get_dT_ps_dp_a(p,slim);
						const auto d2Tdps  = original::derivatives::get_d2T_ps_dps_a(p,slim);
						const auto d2Tds2  = original::derivatives::get_d2T_ps_ds2_a(p,slim);
						return dTdp + (d2Tdps+d2Tds2*dslimdp)*(s-slim);
					} else if (s>supper) {
						const auto f    = 165. - 0.125*(p-data::pmin);
						const auto dfdp = -0.125;
						const auto slim = supper;
						const auto dslimdp = dsupperdp;
						const auto dTdp    = original::derivatives::get_dT_ps_dp_a(p,slim);
						const auto d2Tdps  = original::derivatives::get_d2T_ps_dps_a(p,slim);
						const auto d2Tds2  = original::derivatives::get_d2T_ps_ds2_a(p,slim);
						return dTdp + (d2Tdps+d2Tds2*dslimdp)*(s-slim) + dfdp*pow(s-slim,2) - 2.*f*(s-slim)*dslimdp;
					} else {
						return original::derivatives::get_dT_ps_dp_a(p,s);
					}
				}
				else  if (p <= data::pminC) {	// could be in 2b, below, or above
					if (s<slower) {
						const auto slim = slower;
						const auto dslimdp = dslowerdp;
						const auto dTdp    = original::derivatives::get_dT_ps_dp_b(p,slim);
						const auto d2Tdps  = original::derivatives::get_d2T_ps_dps_b(p,slim);
						const auto d2Tds2  = original::derivatives::get_d2T_ps_ds2_b(p,slim);
						return dTdp + (d2Tdps+d2Tds2*dslimdp)*(s-slim);
					} else if (s>supper) {
						const auto f = 165. - 0.125*(p-data::pmin);
						const auto dfdp = -0.125;
						const auto slim = supper;
						const auto dslimdp = dsupperdp;
						const auto dTdp    = original::derivatives::get_dT_ps_dp_b(p,slim);
						const auto d2Tdps  = original::derivatives::get_d2T_ps_dps_b(p,slim);
						const auto d2Tds2  = original::derivatives::get_d2T_ps_ds2_b(p,slim);
						return dTdp + (d2Tdps+d2Tds2*dslimdp)*(s-slim) + dfdp*pow(s-slim,2) - 2.*f*(s-slim)*dslimdp;
					} else {
						return original::derivatives::get_dT_ps_dp_b(p,s);
					}
				}
				else {									// could be in 2b, above, 2c, or below
					if (s <= data::smaxC) {	// could be in 2c or below
						if (s<slower) {
							const auto slim = slower;
							const auto dslimdp = dslowerdp;
							const auto dTdp    = original::derivatives::get_dT_ps_dp_c(p,slim);
							const auto d2Tdps  = original::derivatives::get_d2T_ps_dps_c(p,slim);
							const auto d2Tds2  = original::derivatives::get_d2T_ps_ds2_c(p,slim);
							return dTdp + (d2Tdps+d2Tds2*dslimdp)*(s-slim);
						} else {
							return original::derivatives::get_dT_ps_dp_c(p,s);
						}
					} else {							// could be in 2b or above
						if (s>supper) {
							const auto f = 165. - 0.125*(p-data::pmin);
							const auto dfdp = -0.125;
							const auto slim = supper;
							const auto dslimdp = dsupperdp;
							const auto dTdp    = original::derivatives::get_dT_ps_dp_b(p,slim);
							const auto d2Tdps  = original::derivatives::get_d2T_ps_dps_b(p,slim);
							const auto d2Tds2  = original::derivatives::get_d2T_ps_ds2_b(p,slim);
							return dTdp + (d2Tdps+d2Tds2*dslimdp)*(s-slim) + dfdp*pow(s-slim,2) - 2.*f*(s-slim)*dslimdp;
						} else {
							return original::derivatives::get_dT_ps_dp_b(p,s);
						}
					}
				}
			}

			/**
			* @brief Function for computing the derivative of temperature w.r.t. entropy in region 2.
			* @param[in] p Pressure in MPa
			* @param[in] h Specific entropy in kJ/(kg*K)
			* @return Derivative of temperature w.r.t. entropy in K/(kJ/(kg*K))
			*/
			template <typename U, typename V>
			auto get_dT_ps_ds_uncut(const U&  p, const V&  s) {
				const auto supper = original::get_s_pT(p,data::Tmax);
				const auto Ts = region4::original::get_Ts_p(min(p,region4::data::pcrit));
				const auto slower = original::get_s_pT(p,Ts);
				if (p <= data::pminB) {		// could be in 2a, below, or above
					if (s<slower) {
						const auto slim = slower;
						return original::derivatives::get_dT_ps_ds_a(p,slim);
					} else if (s>supper) {
						const auto f = 165. - 0.125*(p-data::pmin);
						const auto slim = supper;
						return original::derivatives::get_dT_ps_ds_a(p,slim) + 2.*f*(s-slim);
					} else {
						return original::derivatives::get_dT_ps_ds_a(p,s);
					}
				}
				else  if (p <= data::pminC) {	// could be in 2b, below, or above
					if (s<slower) {
						const auto slim = slower;
						return original::derivatives::get_dT_ps_ds_b(p,slim);
					} else if (s>supper) {
						const auto f = 165. - 0.125*(p-data::pmin);
						const auto slim = supper;
						return original::derivatives::get_dT_ps_ds_b(p,slim) + 2.*f*(s-slim);
					} else {
						return original::derivatives::get_dT_ps_ds_b(p,s);
					}
				}
				else {									// could be in 2b, above, 2c, or below
					if (s <= data::smaxC) {	// could be in 2c or below
						if (s<slower) {
							const auto slim = slower;
							return original::derivatives::get_dT_ps_ds_c(p,slim);
						} else {
							return original::derivatives::get_dT_ps_ds_c(p,s);
						}
					} else {							// could be in 2b or above
						if (s>supper) {
							const auto f = 165. - 0.125*(p-data::pmin);
							const auto slim = supper;
							return original::derivatives::get_dT_ps_ds_b(p,slim) + 2.*f*(s-slim);
						} else {
							return original::derivatives::get_dT_ps_ds_b(p,s);
						}
					}
				}
			}

		/**@}*/


		}	// end namespace derivatives


	}	// end namespace region2


}	// end namespace iapws_if97
/**
 * @file iapwsRegion4.h
 *
 * @brief File containing template implementation of region 4 of the IAPWS-IF97 model, augmented with the some utility functions and divided into two subregions, and extended to provide more benigng values outside of the original function domains.
 *
 * Original model: Wagner, W.; Cooper, J. R.; Dittmann, A.; Kijima, J.; Kretzschmar, H.-J.; Kruse, A.; Mareš, R.; Oguchi, K.; Sato, H.; Stocker, I.; Sifner, O.; Takaishi, Y.; Tanishita, I.; Trubenbach, J. & Willkommen, T.:
 *                 The IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam. Journal of Engineering for Gas Turbines and Power -- Transactions of the ASME, 2000, 122, 150-182.
 *
 * Revised model used for this implementation: Revised Release on the IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam.
 *                                             The International Association for the Properties of Water and Steam, Technical Report IAPWS R7-97(2012), 2012. http://www.iapws.org/relguide/IF97-Rev.html.
 *
 * For ease of notation, we define the two subregions 4-1/2 and 4-3:
 *         If T<=623.15 (i.e., p<=16.5292) --> 4-1/2 (i.e., we use regions 1 and 2 for vapor and liquid phase, respectively)
 *         else --> 4-3 (i.e., we use region 3 for both vapor and liquid phase
 *
 * The additional utility functions that were added are hliq(p), hvap(p), hliq(T), hvap(T), sliq(p), svap(p), sliq(T), svap(T), h(p,x), h(T,x), s(p,x), s(T,x), x(p,h), x(p,s), h(p,s), and s(p,h).
 *
 * ==============================================================================\n
 * © Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
 * ==============================================================================\n
 *
 * @author Dominik Bongartz, Jaromil Najman, Alexander Mitsos
 * @date 15.08.2019
 *
 */


#pragma once

#include "iapwsData.h"
#include "iapwsAuxiliary.h"
#include "iapwsAuxiliaryDerivatives.h"


namespace iapws_if97 {


    namespace region4 {


        /**
        * @name Basic equation
        */
        /**@{*/

            /**
            * @brief Function for computing the saturation pressure as a function of temperature.
            * @param[in] T Temperature in K
            * @return Saturation pressure in MPa
            */
            template <typename U>
            U get_ps_T(const U& T) {
					if (T <= data::Tcrit) {
						return original::get_ps_T(T);
					} else {
						return data::psExtrA + data::psExtrB*T + data::psExtrC*pow(T,2);
					}
            }

        /**@}*/


        /**
        * @name Backward equation
        */
        /**@{*/

            /**
            * @brief Function for computing the saturation temperature as a function of pressure.
            * @param[in] p Pressure in MPa
            * @return Saturation temperature in K
            */
            template <typename U>
            U get_Ts_p(const U& p) {
					if (p <= data::pcrit) {
						return original::get_Ts_p(p);
					} else {
						return -data::psExtrB/(2.*data::psExtrC) + sqrt( pow(data::psExtrB/(2.*data::psExtrC),2) + (p-data::psExtrA)/data::psExtrC );
					}
            }

        /**@}*/


        /**
        * @name Utility functions (derived from original IAPWS functions for this region)
		*
		* These utility functions all involve calculations for saturated liquid and vapor states.
		* Depending on pressure (or temperature), these saturated liquid and vapor states may either be in regions 1/2, respectively, or 3.
		* We call these sub-regions 4-1/2 and 4-3.
		*
        */
        /**@{*/

            /**
            * @brief Function for computing saturated liquid enthalpy as a function of pressure in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @return Specific enthalpy in kJ/kg
            */
            template <typename U>
            auto get_hliq_p_12(const U& p) {
                return iapws_if97::region1::original::get_h_pT(p,original::get_Ts_p(p));
            }

            /**
            * @brief Function for computing saturated liquid enthalpy as a function of temperature in region 4-1/2.
            * @param[in] T Temperature in K
            * @return Specific enthalpy in kJ/kg
            */
            template <typename U>
            auto get_hliq_T_12(const U& T) {
                return iapws_if97::region1::original::get_h_pT(original::get_ps_T(T),T);
            }

            /**
            * @brief Function for computing saturated vapor enthalpy as a function of pressure in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @return Specific enthalpy in kJ/kg
            */
            template <typename U>
            auto get_hvap_p_12(const U& p) {
                return iapws_if97::region2::original::get_h_pT(p,original::get_Ts_p(p));
            }

            /**
            * @brief Function for computing saturated vapor enthalpy as a function of temperature in region 4-1/2.
            * @param[in] T Temperature in K
            * @return Specific enthalpy in kJ/kg
            */
            template <typename U>
            auto get_hvap_T_12(const U& T) {
                return iapws_if97::region2::original::get_h_pT(original::get_ps_T(T),T);
            }

            /**
            * @brief Function for computing saturated liquid entropy as a function of pressure in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @return Specific entropy in kJ/(kg*K)
            */
            template <typename U>
            auto get_sliq_p_12(const U& p) {
                return iapws_if97::region1::original::get_s_pT(p,original::get_Ts_p(p));
            }

            /**
            * @brief Function for computing saturated liquid entropy as a function of temperature in region 4-1/2.
            * @param[in] T Temperature in K
            * @return Specific entropy in kJ/(kg*K)
            */
            template <typename U>
            auto get_sliq_T_12(const U& T) {
                return iapws_if97::region1::original::get_s_pT(original::get_ps_T(T),T);
            }

            /**
            * @brief Function for computing saturated vapor entropy as a function of pressure in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @return Specific entropy in kJ/(kg*K)
            */
            template <typename U>
            auto get_svap_p_12(const U& p) {
                return iapws_if97::region2::original::get_s_pT(p,original::get_Ts_p(p));
            }

            /**
            * @brief Function for computing saturated vapor entropy as a function of temperature in region 4-1/2.
            * @param[in] T Temperature in K
            * @return Specific entropy in kJ/(kg*K)
            */
            template <typename U>
            auto get_svap_T_12(const U& T) {
                return iapws_if97::region2::original::get_s_pT(original::get_ps_T(T),T);
            }

            /**
            * @brief Function for computing enthalpy as a function of pressure and vapor quality in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @param[in] x Vapor quality (dimensionless)
            * @return Specific enthalpy in kJ/kg
            */
            template <typename U, typename V>
            auto get_h_px_12(const U& p, const V& x) {
                const U hliq(get_hliq_p_12(p));
                const U hvap(get_hvap_p_12(p));
                return x*hvap + (1.-x)*hliq;
            }

            /**
            * @brief Function for computing enthalpy as a function of temperature and vapor quality in region 4-1/2.
            * @param[in] T temperature in K
            * @param[in] x Vapor quality (dimensionless)
            * @return Specific enthalpy in kJ/kg
            */
            template <typename U, typename V>
            auto get_h_Tx_12(const U& T, const V& x) {
                const U hliq(get_hliq_T_12(T));
                const U hvap(get_hvap_T_12(T));
                return x*hvap + (1.-x)*hliq;
            }

            /**
            * @brief Function for computing entropy as a function of pressure and vapor quality in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @param[in] x Vapor quality (dimensionless)
            * @return Specific entropy in kJ/(kg*K)
            */
            template <typename U, typename V>
            auto get_s_px_12(const U& p, const V& x) {
                const U sliq(get_sliq_p_12(p));
                const U svap(get_svap_p_12(p));
                return x*svap + (1.-x)*sliq;
            }

            /**
            * @brief Function for computing entropy as a function of temperature and vapor quality in region 4-1/2.
            * @param[in] T temperature in K
            * @param[in] x Vapor quality (dimensionless)
            * @return Specific entropy in kJ/(kg*K)
            */
            template <typename U, typename V>
            auto get_s_Tx_12(const U& T, const V& x) {
                const U sliq(get_sliq_T_12(T));
                const U svap(get_svap_T_12(T));
                return x*svap + (1.-x)*sliq;
			}

            /**
            * @brief Function for computing vapor quality as a function of pressure and enthalpy in region 4-1/2 before cutting at xmax=1 and xmin=0
            * @param[in] p Pressure in MPa
            * @param[in] h Specific enthalpy in kJ/kg
            * @return Vapor quality (dimensionless)
            */
            template <typename U, typename V>
            auto get_x_ph_12_uncut(const U& p, const V& h) {
                const auto hliq(get_hliq_p_12(p));
                const auto hvap(get_hvap_p_12(p));
				return (h-hliq)/(hvap - hliq);
            }

            /**
            * @brief Function for computing vapor quality as a function of pressure and enthalpy in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @param[in] h Specific enthalpy in kJ/kg
            * @return Vapor quality (dimensionless)
            */
            template <typename U, typename V>
            auto get_x_ph_12(const U& p, const V& h) {
				const auto x(get_x_ph_12_uncut(p,h));
                return max(min(x,(decltype(x))1.),(decltype(x))0.);
            }

            /**
            * @brief Function for computing vapor quality as a function of pressure and entropy in region 4-1/2 before cutting at xmax=1 and xmin=0
            * @param[in] p Pressure in MPa
            * @param[in] s Specific entropy in kJ/(kg*K)
            * @return Vapor quality (dimensionless)
            */
            template <typename U, typename V>
            auto get_x_ps_12_uncut(const U& p, const V& s) {
                const auto sliq(get_sliq_p_12(p));
                const auto svap(get_svap_p_12(p));
                // auto deltas = svap - sliq;
                // deltas = max(deltas,(decltype(deltas))data::mindeltasvap12);
                return (s-sliq)/(svap - sliq);
            }

            /**
            * @brief Function for computing vapor quality as a function of pressure and entropy in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @param[in] s Specific entropy in kJ/(kg*K)
            * @return Vapor quality (dimensionless)
            */
            template <typename U, typename V>
            auto get_x_ps_12(const U& p, const V& s) {
                const auto x(get_x_ps_12_uncut(p,s));
                return min(max(x,(decltype(x))0.),(decltype(x))1.);
            }

            /**
            * @brief Function for computing enthalpy as a function of pressure and entropy in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @param[in] s Specific entropy in kJ/(kg*K)
            * @return Specific enthalpy in kJ/kg
            */
            template <typename U, typename V>
            auto get_h_ps_12(const U& p, const V& s) {
                return get_h_px_12(p,get_x_ps_12(p,s));
            }

            /**
            * @brief Function for computing entropy as a function of pressure and enthalpy in region 4-1/2.
            * @param[in] p Pressure in MPa
            * @param[in] h Specific enthalpy in kJ/kg
            * @return Specific entropy in kJ/(kg*K)
            */
            template <typename U, typename V>
            auto get_s_ph_12(const U& p, const V& h) {
                return get_s_px_12(p,get_x_ph_12(p,h));
            }


        /**@}*/


        namespace derivatives {


        /**
        * @name Derivatives of functions in region 4
        */
        /**@{*/

            /**
            * @brief Derivative of get_ps_T
            * @param[in] T Temperature in K
            * @return Derivative of saturation pressure in MPa/K
            */
            template <typename U>
            U get_dps_dT(const U& T) {
				if (T <= data::Tcrit) {
					return original::derivatives::get_dps_dT(T);
				} else {
					return data::psExtrB + 2.*data::psExtrC*T;
				}
            }

			/**
			* @brief Second derivative of get_ps_T
			* @param[in] T Temperature in K
			* @return Second derivative of saturation pressure in MPa/K^2
			*/
			template <typename U>
			U get_d2ps_dT2(const U& T) {
				if (T <= data::Tcrit) {
					return original::derivatives::get_dps_dT(T);
				} else {
					return 2.*data::psExtrC;
				}
			}

            /**
            * @brief Derivative of get_Ts_p
            * @param[in] p Pressure in MPa
            * @return Derivative of saturation temperature in K/MPa
            */
            template <typename U>
            U get_dTs_dp(const U& p) {
				if (p <= data::pcrit) {
					return original::derivatives::get_dTs_dp(p);
				} else {
					return 1. / ( 2. * data::psExtrC * sqrt( pow(data::psExtrB/(2.*data::psExtrC),2) + (p-data::psExtrA)/data::psExtrC ) );
				}
            }

            /**
            * @brief Second derivative of get_Ts_p
            * @param[in] p Pressure in MPa
            * @return Second derivative of saturation temperature in K/MPa^2
            */
            template <typename U>
            U get_d2Ts_dp2(const U& p) {
				if (p <= data::pcrit) {
					return original::derivatives::get_dTs_dp(p);
				} else {
					return -1. / ( 4. * pow(data::psExtrC,2) * pow( pow(data::psExtrB/(2.*data::psExtrC),2) + (p-data::psExtrA)/data::psExtrC , 1.5) );
				}
            }

            /**
            * @brief Derivative of get_hliq_p_12
            * @param[in] p Pressure in MPa
            * @return Derivative of saturated liquid enthalpy in (kJ/kg)/MPa
            */
            template <typename U>
            U get_dhliq_dp_12(const U& p) {
                const U Ts = original::get_Ts_p(p);
                return region1::original::derivatives::get_dh_pT_dp(p,Ts) + region1::original::derivatives::get_dh_pT_dT(p,Ts)*original::derivatives::get_dTs_dp(p);
            }

            /**
            * @brief Second derivative of get_hliq_p_12
            * @param[in] p Pressure in MPa
            * @return Second derivative of saturated liquid enthalpy in (kJ/kg)/MPa^2
            */
            template <typename U>
            U get_d2hliq_dp2_12(const U& p) {
                const U Ts = original::get_Ts_p(p);
                const U dTsdp = original::derivatives::get_dTs_dp(p);
                const U d2Tsdp2 = original::derivatives::get_d2Ts_dp2(p);
                return region1::original::derivatives::get_d2h_pT_dp2(p,Ts) + 2.*region1::original::derivatives::get_d2h_pT_dpT(p,Ts)*dTsdp + region1::original::derivatives::get_d2h_pT_dT2(p,Ts)*pow(dTsdp,2) + region1::original::derivatives::get_dh_pT_dT(p,Ts)*d2Tsdp2;
            }

            /**
            * @brief Derivative of get_hliq_T_12
            * @param[in] T Temperature in K
            * @return Derivative of saturated liquid enthalpy in (kJ/kg)/K
            */
            template <typename U>
            U get_dhliq_dT_12(const U& T) {
                const U ps = original::get_ps_T(T);
                return region1::original::derivatives::get_dh_pT_dT(ps,T) + region1::original::derivatives::get_dh_pT_dp(ps,T)*original::derivatives::get_dps_dT(T);
            }

            /**
            * @brief Second derivative of get_hliq_T_12
            * @param[in] T Temperature in K
            * @return Second derivative of saturated liquid enthalpy in (kJ/kg)/K^2
            */
            template <typename U>
            U get_d2hliq_dT2_12(const U& T) {
                const U ps = original::get_ps_T(T);
                const U dpsdT = original::derivatives::get_dps_dT(T);
                const U d2psdT2 = original::derivatives::get_d2ps_dT2(T);
                return region1::original::derivatives::get_d2h_pT_dT2(ps,T) + 2*region1::original::derivatives::get_d2h_pT_dpT(ps,T)*dpsdT + region1::original::derivatives::get_d2h_pT_dp2(ps,T)*pow(dpsdT,2) + region1::original::derivatives::get_dh_pT_dp(ps,T)*d2psdT2;
            }

            /**
            * @brief Derivative of get_hvap_p_12
            * @param[in] p Pressure in MPa
            * @return Derivative of saturated vapor enthalpy in (kJ/kg)/MPa
            */
            template <typename U>
            U get_dhvap_dp_12(const U& p) {
                const U Ts = original::get_Ts_p(p);
                return region2::original::derivatives::get_dh_pT_dp(p,Ts) + region2::original::derivatives::get_dh_pT_dT(p,Ts)*original::derivatives::get_dTs_dp(p);
            }

            /**
            * @brief Second derivative of get_hvap_p_12
            * @param[in] p Pressure in MPa
            * @return Second derivative of saturated vapor enthalpy in (kJ/kg)/MPa^2
            */
            template <typename U>
            U get_d2hvap_dp2_12(const U& p) {
                const U Ts = original::get_Ts_p(p);
                const U dTsdp = original::derivatives::get_dTs_dp(p);
                const U d2Tsdp2 = original::derivatives::get_d2Ts_dp2(p);
                return region2::original::derivatives::get_d2h_pT_dp2(p,Ts) + 2.*region2::original::derivatives::get_d2h_pT_dpT(p,Ts)*dTsdp + region2::original::derivatives::get_d2h_pT_dT2(p,Ts)*pow(dTsdp,2) + region2::original::derivatives::get_dh_pT_dT(p,Ts)*d2Tsdp2;
            }

            /**
            * @brief Derivative of get_hvap_T_12
            * @param[in] T Temperature in K
            * @return Derivative of saturated vapor enthalpy in (kJ/kg)/K
            */
            template <typename U>
            U get_dhvap_dT_12(const U& T) {
                const U ps = original::get_ps_T(T);
                return region2::original::derivatives::get_dh_pT_dT(ps,T) + region2::original::derivatives::get_dh_pT_dp(ps,T)*original::derivatives::get_dps_dT(T);
            }

            /**
            * @brief Second derivative of get_hvap_T_12
            * @param[in] T Temperature in K
            * @return Second derivative of saturated vapor enthalpy in (kJ/kg)/K
            */
            template <typename U>
            U get_d2hvap_dT2_12(const U& T) {
                const U ps = original::get_ps_T(T);
                const U dpsdT = original::derivatives::get_dps_dT(T);
                const U d2psdT2 = original::derivatives::get_d2ps_dT2(T);
                return region2::original::derivatives::get_d2h_pT_dT2(ps,T) + 2.*region2::original::derivatives::get_d2h_pT_dpT(ps,T)*dpsdT + region2::original::derivatives::get_d2h_pT_dp2(ps,T)*pow(dpsdT,2) + region2::original::derivatives::get_dh_pT_dp(ps,T)*d2psdT2;
            }

            /**
            * @brief Derivative of get_sliq_p_12
            * @param[in] p Pressure in MPa
            * @return Derivative of saturated liquid entropy in (kJ/kg*K)/MPa
            */
            template <typename U>
            U get_dsliq_dp_12(const U& p) {
                const U Ts = original::get_Ts_p(p);
                return region1::original::derivatives::get_ds_pT_dp(p,Ts) + region1::original::derivatives::get_ds_pT_dT(p,Ts)*original::derivatives::get_dTs_dp(p);
            }

			/**
            * @brief Second derivative of get_sliq_p_12
            * @param[in] p Pressure in MPa
            * @return Second derivative of saturated liquid entropy in (kJ/kg*K)/MPa^2
            */
            template <typename U>
            U get_d2sliq_dp2_12(const U& p) {
                const U Ts = original::get_Ts_p(p);
                const U dTsdp = original::derivatives::get_dTs_dp(p);
                const U d2Tsdp2 = original::derivatives::get_d2Ts_dp2(p);
                return region1::original::derivatives::get_d2s_pT_dp2(p,Ts) + 2.*region1::original::derivatives::get_d2s_pT_dpT(p,Ts)*dTsdp + region1::original::derivatives::get_d2s_pT_dT2(p,Ts)*pow(dTsdp,2) + region1::original::derivatives::get_ds_pT_dT(p,Ts)*d2Tsdp2;
            }

            /**
            * @brief Derivative of get_sliq_T_12
            * @param[in] T Temperature in K
            * @return Derivative of saturated liquid entropy in (kJ/kg*K)/K
            */
            template <typename U>
            U get_dsliq_dT_12(const U& T) {
                const U ps = original::get_ps_T(T);
                return region1::original::derivatives::get_ds_pT_dT(ps,T) + region1::original::derivatives::get_ds_pT_dp(ps,T)*original::derivatives::get_dps_dT(T);
            }

            /**
            * @brief Derivative of get_svap_T_12
            * @param[in] T Temperature in K
            * @return Derivative of saturated vapor entropy in (kJ/kg*K)/K
            */
            template <typename U>
            U get_dsvap_dT_12(const U& T) {
                const U ps = original::get_ps_T(T);
                return region2::original::derivatives::get_ds_pT_dT(ps,T) + region2::original::derivatives::get_ds_pT_dp(ps,T)*original::derivatives::get_dps_dT(T);
            }

            /**
            * @brief Second derivative of get_svap_T_12
            * @param[in] T Temperature in K
            * @return Second derivative of saturated vapor entropy in (kJ/kg*K)/K^2
            */
            template <typename U>
            U get_d2svap_dT2_12(const U& T) {
                const U ps = original::get_ps_T(T);
                const U dpsdT = original::derivatives::get_dps_dT(T);
                const U d2psdT2 = original::derivatives::get_d2ps_dT2(T);
                return region2::original::derivatives::get_d2s_pT_dT2(ps,T) + 2.*region2::original::derivatives::get_d2s_pT_dpT(ps,T)*dpsdT + region2::original::derivatives::get_d2s_pT_dp2(ps,T)*pow(dpsdT,2) + region2::original::derivatives::get_ds_pT_dp(ps,T)*d2psdT2;
            }

            /**
            * @brief Derivative of get_svap_p_12
            * @param[in] p Pressure in MPa
            * @return Derivative of saturated vapor entropy in (kJ/kg*K)/MPa
            */
            template <typename U>
            U get_dsvap_dp_12(const U& p) {
                const U Ts = original::get_Ts_p(p);
                return region2::original::derivatives::get_ds_pT_dp(p,Ts) + region2::original::derivatives::get_ds_pT_dT(p,Ts)*original::derivatives::get_dTs_dp(p);
            }

            /**
            * @brief Second derivative of get_svap_p_12
            * @param[in] p Pressure in MPa
            * @return Second derivative of saturated vapor entropy in (kJ/kg*K)/MPa^2
            */
            template <typename U>
            U get_d2svap_dp2_12(const U& p) {
                const U Ts = original::get_Ts_p(p);
                const U dTsdp = original::derivatives::get_dTs_dp(p);
                const U d2Tsdp2 = original::derivatives::get_d2Ts_dp2(p);
                return region2::original::derivatives::get_d2s_pT_dp2(p,Ts) + 2.*region2::original::derivatives::get_d2s_pT_dpT(p,Ts)*dTsdp + region2::original::derivatives::get_d2s_pT_dT2(p,Ts)*pow(dTsdp,2) + region2::original::derivatives::get_ds_pT_dT(p,Ts)*d2Tsdp2;
            }

            /**
            * @brief Partial derivative of get_x_ph_12_uncut w.r.t. p
            * @param[in] p Pressure in MPa
            * @param[in] h Specific enthalpy in kJ/kg
            * @return Partial derivative of vapor quality w.r.t. pressure in 1/MPa
            */
            template <typename U, typename V>
            auto get_dx_ph_dp_12_uncut(const U& p, const V& h) {
				const auto hliq(get_hliq_p_12(p));
				const auto hvap(get_hvap_p_12(p));
				const auto dhliqdp(get_dhliq_dp_12(p));
				const auto dhvapdp(get_dhvap_dp_12(p));
				return (hliq*dhvapdp-hvap*dhliqdp-h*(dhvapdp-dhliqdp))/pow(hvap-hliq,2);
            }

            /**
            * @brief Partial derivative of get_x_ph_12_uncut w.r.t. h
            * @param[in] p Pressure in MPa
            * @param[in] h Specific enthalpy in kJ/kg
            * @return Partial derivative of vapor quality w.r.t. enthalpy in 1/(kJ/kg)
            */
            template <typename U, typename V>
            auto get_dx_ph_dh_12_uncut(const U& p, const V& h) {
				return 1./(get_hvap_p_12(p)-get_hliq_p_12(p));
            }

            /**
            * @brief Second partial derivative of get_x_ph_12_uncut w.r.t. p
            * @param[in] p Pressure in MPa
            * @param[in] h Specific enthalpy in kJ/kg
            * @return Second partial derivative of vapor quality w.r.t. pressure in 1/MPa^2
            */
            template <typename U, typename V>
            auto get_d2x_ph_dp2_12_uncut(const U& p, const V& h) {
				const auto hliq(get_hliq_p_12(p));
				const auto hvap(get_hvap_p_12(p));
				const auto dhliqdp(get_dhliq_dp_12(p));
				const auto dhvapdp(get_dhvap_dp_12(p));
				const auto d2hliqdp2(get_d2hliq_dp2_12(p));
				const auto d2hvapdp2(get_d2hvap_dp2_12(p));
				return ((hliq*d2hvapdp2-hvap*d2hliqdp2-h*(d2hvapdp2-d2hliqdp2))*(hvap-hliq)-(hliq*dhvapdp-hvap*dhliqdp-h*(dhvapdp-dhliqdp))*2.*(hvap-hliq))/pow(hvap-hliq,3);
            }

        /**@}*/


        } // end namespace derivatives


    }   // end namespace region4


}   // end namespace iapws_if97
/**
 * @file iapwsRegion4original.h
 *
 * @brief File containing template implementation of region 4 of the IAPWS-IF97 model.
 *
 * Original model: Wagner, W.; Cooper, J. R.; Dittmann, A.; Kijima, J.; Kretzschmar, H.-J.; Kruse, A.; Mareš, R.; Oguchi, K.; Sato, H.; Stocker, I.; Sifner, O.; Takaishi, Y.; Tanishita, I.; Trubenbach, J. & Willkommen, T.:
 *                 The IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam. Journal of Engineering for Gas Turbines and Power -- Transactions of the ASME, 2000, 122, 150-182.
 *
 * Revised model used for this implementation: Revised Release on the IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam.
 *                                             The International Association for the Properties of Water and Steam, Technical Report IAPWS R7-97(2012), 2012. http://www.iapws.org/relguide/IF97-Rev.html.
 *
 * For ease of notation, we define the two subregions 4-1/2 and 4b:
 *         If T<=623.15 (i.e., p<=16.5292) --> 4-1/2 (i.e., we use regions 1 and 2 for vapor and liquid phase, respectively)
 *         else --> 4b (i.e., we use region 3 for both vapor and liquid phase
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
#include "iapwsRegion1original.h"
#include "iapwsRegion2original.h"


namespace iapws_if97 {


    namespace region4 {


		namespace original {


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
					const U theta = T/data::Tstar + data::parBasic.at(8)/(T/data::Tstar-data::parBasic.at(9));
					return data::pstar * (auxiliary::pi_theta(theta));
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
					const U beta = pow(p/data::pstar,0.25);
					return data::Tstar * (auxiliary::theta_beta(beta));
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
					const U theta = T/data::Tstar + data::parBasic.at(8)/(T/data::Tstar-data::parBasic.at(9));
					const U dtheta = 1/data::Tstar - data::parBasic.at(8)/(data::Tstar*pow(data::parBasic.at(9) - T/data::Tstar,2));
					return data::pstar * auxiliary::derivatives::dpi_theta(theta) * dtheta;
				}

				/**
				* @brief Second derivative of get_ps_T
				* @param[in] T Temperature in K
				* @return Second derivative of saturation pressure in MPa/K^2
				*/
				template <typename U>
				U get_d2ps_dT2(const U& T) {
					const U theta = T/data::Tstar + data::parBasic.at(8)/(T/data::Tstar-data::parBasic.at(9));
					const U dtheta = 1/data::Tstar - data::parBasic.at(8)/(data::Tstar*pow(data::parBasic.at(9) - T/data::Tstar,2));
					const U d2theta = -(2.*data::parBasic.at(8))/(pow(data::Tstar,2)*pow(data::parBasic.at(9) - T/data::Tstar,3));
					return data::pstar * ( auxiliary::derivatives::dpi_theta(theta)*d2theta + auxiliary::derivatives::d2pi_theta(theta)*pow(dtheta,2) );
				}

				/**
				* @brief Derivative of get_Ts_p
				* @param[in] p Pressure in MPa
				* @return Derivative of saturation temperature in K/MPa
				*/
				template <typename U>
				U get_dTs_dp(const U& p) {
					const U beta = pow(p/data::pstar,0.25);
					const U dbeta = 1./pos(4*data::pstar*pow(p/data::pstar,0.75));
					return data::Tstar * auxiliary::derivatives::dtheta_beta(beta) * dbeta;
				}

				/**
				* @brief Second derivative of get_Ts_p
				* @param[in] p Pressure in MPa
				* @return Second derivative of saturation temperature in K/MPa^2
				*/
				template <typename U>
				U get_d2Ts_dp2(const U& p) {
					const U beta = pow(p/data::pstar,0.25);
					const U dbeta = 1./pos(4*data::pstar*pow(p/data::pstar,0.75));
					const U d2beta = -3./pos(16.*pow(data::pstar,2)*pow(p/data::pstar,1.75));
					return data::Tstar * ( auxiliary::derivatives::dtheta_beta(beta)*d2beta + auxiliary::derivatives::d2theta_beta(beta)*pow(dbeta,2) );
				}
				
			/**@}*/


			} // end namespace derivatives


		} // end namespace original


    }   // end namespace region4


}   // end namespace iapws_if97
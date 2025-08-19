/**
 * @file iapwsAuxiliary.h
 *
 * @brief File containing template implementation of auxiliary functions of the IAPWS-IF97 model (not intended to be accessed by the user).
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

#include <vector>
#include <algorithm>
#include <cmath>


namespace iapws_if97 {


	// Making the std max/min visible within the iapws_if97 namespace
	inline double max(const double x, const double y) { return std::max(x,y); }
	inline double min(const double x, const double y) { return std::min(x,y); }

	// These functions (or, rather, the corresponding overloads for McCormick types) are used in MC++ for avoiding relaxations
	// crossing zero in cases the function itself is always positive / negative. The double version implemented in MC++ simply
	// returns x but has an additional sanity check whether the function value is actually >/<0. Repeating the double version
	// here to avoid the dependence on MC++. Since we know that herein we only used it in places where we are allowed to do so,
	// we skip the sanity check here. :-)
	inline double pos(const double x) { return x; }
	inline double neg(const double x) { return x; }


	namespace region1 {


		namespace auxiliary {


			/**
			* @brief Auxiliary function gamma needed for region 1 (corresponds to Gibbs free energy as a function of pressure and temperature)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] tau Inverse reduced temperature (Tstar/T)
			* @return Dimensionles quantitiy related to specific Gibbs free energy
			*/
			template <typename U, typename V>
			auto gamma(const U& pi, const V& tau) {
				const U myPi = 7.1 - pi;
				const V myTau = tau - 1.222;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
				auto result = d->n * pow(myPi,d->I) * pow(myTau,d->J);
				for( ++d; d!= data::parBasic.end(); ++d){
					result += d->n * pow(myPi,d->I) * pow(myTau,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function gamma_tau needed for region 1 (corresponds to derivative of gamma (cf. above) w.r.t. a reduced temperature)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] tau Inverse reduced temperature (Tstar/T)
			* @return Dimensionles quantitiy related to derivative of specific Gibbs free energy w.r.t. temperature
			*/
			template <typename U, typename V>
			auto gamma_tau(const U& pi, const V& tau) {
				const U myPi = 7.1 - pi;
				const V myTau = tau - 1.222;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
				auto result = d->n*pow(myPi,d->I)*((double)d->J)*pow(myTau,d->J - 1.);
				for( ++d; d!= data::parBasic.end(); ++d){
					result += d->n*pow(myPi,d->I)*((double)d->J)*pow(myTau,d->J - 1.);
				}
				return result;
			}

			/**
			* @brief Auxiliary function gamma_pi needed for region 1 (corresponds to derivative of gamma (cf. above) w.r.t. a reduced pressure)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] tau Inverse reduced temperature (Tstar/T)
			* @return Dimensionles quantitiy related to derivative of specific Gibbs free energy w.r.t. pressure
			*/
			template <typename U, typename V>
			auto gamma_pi(const U& pi, const V& tau) {
				const U myPi = 7.1 - pi;
				const V myTau = tau - 1.222;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
				auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*pow(myTau,d->J);
				for( ++d; d!= data::parBasic.end(); ++d){
					result += d->n*((double)d->I)*pow(myPi,d->I-1.)*pow(myTau,d->J);
				}
				return -1.*result;
			}

			/**
			* @brief Auxiliary function theta_pi_eta needed for region 1 (corresponds to temperature as a function of pressure and enthalpy)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] eta Reduced enthalpy (h/hstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U, typename V>
			auto theta_pi_eta(const U& pi, const V& eta) {
				const V myEta = eta + 1.;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTph.begin();
				auto result = d->n*pow(pi,d->I)*pow(myEta,d->J);
				for( ++d; d!= data::parBackwardTph.end(); ++d){
					result += d->n*pow(pi,d->I)*pow(myEta,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function theta_pi_sigma needed for region 1 (corresponds to temperature as a function of pressure and entropy)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] sigma Reduced entropy (h/sstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U, typename V>
			auto theta_pi_sigma(const U& pi, const V& sigma) {
				const V mySigma = sigma + 2.;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTps.begin();
				auto result = d->n*pow(pi,d->I)*pow(mySigma,d->J);
				for( ++d; d!= data::parBackwardTps.end(); ++d){
					if (d->I != 0) {
						result += d->n*pow(pi,d->I)*pow(mySigma, d->J);
					} else {
						result += d->n*pow(pi,d->I)*pow(mySigma,d->J);
					}
				}
				return result;
			}


		}	// end namespace auxiliary


	}	// end namespace region1


	namespace region2 {


		namespace auxiliary {


			/**
			* @brief Auxiliary function gamma_0 needed for region 2 (corresponds to the ideal-gas part of Gibbs free energy as a function of pressure and temperature)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] tau Inverse reduced temperature (Tstar/T)
			* @return Dimensionles quantitiy related to specific Gibbs free energy
			*/
			template <typename U, typename V>
			auto gamma_0(const U& pi, const V& tau) {
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic0.begin();
				auto result = log(pi) + d->n*pow(tau,d->J);
				for( ++d; d!= data::parBasic0.end(); ++d){
					result += d->n*pow(tau,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function gamma_0_tau needed for region 2 (corresponds to derivative of gamma_0 (cf. above) w.r.t. a reduced temperature)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] tau Inverse reduced temperature (Tstar/T)
			* @return Dimensionles quantitiy related to specific Gibbs free energy
			*/
			template <typename U, typename V>
			V gamma_0_tau(const U& pi, const V& tau) {
				V result = 0.;
				for(std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic0.begin(); d!= data::parBasic0.end(); ++d){
					result += d->n*((double)d->J)*pow(tau,d->J - 1.);
				}
				return result;
			}

			/**
			* @brief Auxiliary function gamma_0_pi needed for region 2 (corresponds to derivative of gamma_0 (cf. above) w.r.t. a reduced pressure)
			* @param[in] pi Reduced pressure (p/pstar)
			* @return Dimensionles quantitiy related to specific Gibbs free energy
			*/
			template <typename U>
			U gamma_0_pi(const U& pi) {
				return 1./pi;
			}

			/**
			* @brief Auxiliary function gamma_r needed for region 2 (corresponds to the residual part of Gibbs free energy as a function of pressure and temperature)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] tau Inverse reduced temperature (Tstar/T)
			* @return Dimensionles quantitiy related to specific Gibbs free energy
			*/
			template <typename U, typename V>
			auto gamma_r(const U& pi, const V& tau) {
				const V myTau = tau - 0.5;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
				auto result = d->n*pow(pi,d->I)*pow(myTau,d->J);
				for( ++d; d!= data::parBasicR.end(); ++d){
					result += d->n*pow(pi,d->I)*pow(myTau,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function gamma_r_tau needed for region 2 (corresponds to derivative of gamma_r (cf. above) w.r.t. a reduced temperature)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] tau Inverse reduced temperature (Tstar/T)
			* @return Dimensionles quantitiy related to specific Gibbs free energy
			*/
			template <typename U, typename V>
			auto gamma_r_tau(const U& pi, const V& tau) {
				const V myTau = tau - 0.5;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
				auto result = d->n*pow(pi,d->I)*((double)d->J)*pow(myTau,d->J - 1.);
				for( ++d; d!= data::parBasicR.end(); ++d){
					result += d->n*pow(pi,d->I)*((double)d->J)*pow(myTau,d->J - 1.);
				}
				return result;
			}

			/**
			* @brief Auxiliary function gamma_r_pi needed for region 2 (corresponds to derivative of gamma_r (cf. above) w.r.t. a reduced pressure)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] tau Inverse reduced temperature (Tstar/T)
			* @return Dimensionles quantitiy related to specific Gibbs free energy
			*/
			template <typename U, typename V>
			auto gamma_r_pi(const U& pi, const V& tau) {
				const V myTau = tau - 0.5;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
				auto result = d->n*((double)d->I)*pow(pi,d->I - 1.)*pow(myTau,d->J);
				for( ++d; d!= data::parBasicR.end(); ++d){
					result += d->n*((double)d->I)*pow(pi,d->I - 1.)*pow(myTau,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function theta_pi_eta_a needed for region 2a (corresponds to temperature as a function of pressure and enthalpy)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] eta Reduced enthalpy (h/hstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U, typename V>
			auto theta_pi_eta_a(const U& pi, const V& eta) {
				const V myEta = eta - 2.1;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
				auto result = d->n*pow(pi,d->I)*pow(myEta,d->J);
				for( ++d; d!= data::parBackwardTphA.end(); ++d){
					result += d->n*pow(pi,d->I)*pow(myEta,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function theta_pi_eta_b needed for region 2b (corresponds to temperature as a function of pressure and enthalpy)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] eta Reduced enthalpy (h/hstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U, typename V>
			auto theta_pi_eta_b(const U& pi, const V& eta) {
				const U myPi = pi - 2.;
				const V myEta = eta - 2.6;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
				auto result = d->n*pow(myPi,d->I)*pow(myEta,d->J);
				for( ++d; d!= data::parBackwardTphB.end(); ++d){
					result += d->n*pow(myPi,d->I)*pow(myEta,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function theta_pi_eta_c needed for region 2c (corresponds to temperature as a function of pressure and enthalpy)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] eta Reduced enthalpy (h/hstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U, typename V>
			auto theta_pi_eta_c(const U& pi, const V& eta) {
				const U myPi = pi + 25.;
				const V myEta = eta - 1.8;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
				auto result = d->n*pow(myPi,d->I)*pow(myEta,d->J);
				for( ++d; d!= data::parBackwardTphC.end(); ++d){
					result += d->n*pow(myPi,d->I)*pow(myEta,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function theta_pi_sigma_a needed for region 2a (corresponds to temperature as a function of pressure and entropy)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] sigma Reduced entropy (s/sstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U, typename V>
			auto theta_pi_sigma_a(const U& pi, const V& sigma) {
				const V mySigma = sigma - 2.;
				std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
				auto result = d->n*pow(pi,d->I)*pow(mySigma,d->J);
				for( ++d; d!= data::parBackwardTpsA.end(); ++d){
					result += d->n*pow(pi,d->I)*pow(mySigma,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function theta_pi_sigma_b needed for region 2b (corresponds to temperature as a function of pressure and entropy)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] sigma Reduced entropy (s/sstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U, typename V>
			auto theta_pi_sigma_b(const U& pi, const V& sigma) {
				const V mySigma = 10. - sigma;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
				auto result = d->n*pow(pi,d->I)*pow(mySigma,d->J);
				for( ++d; d!= data::parBackwardTpsB.end(); ++d){
					result += d->n*pow(pi,d->I)*pow(mySigma,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function theta_pi_sigma_c needed for region 2c (corresponds to temperature as a function of pressure and entropy)
			* @param[in] pi Reduced pressure (p/pstar)
			* @param[in] sigma Reduced entropy (s/sstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U, typename V>
			auto theta_pi_sigma_c(const U& pi, const V& sigma) {
				const V mySigma = 2. - sigma;
				std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
				auto result = d->n*pow(pi,d->I)*pow(mySigma,d->J);
				for( ++d; d!= data::parBackwardTpsC.end(); ++d){
					result += d->n*pow(pi,d->I)*pow(mySigma,d->J);
				}
				return result;
			}

			/**
			* @brief Auxiliary function describing the boundary between regions 2 and 3
			* @param[in] theta Reduced temperature (T/Tstar)
			* @return Reduced pressure (p/pstar)
			*/
			template <typename U>
			U b23_pi_theta(const U& theta) {
				return data::parB23.at(0) + data::parB23.at(1)*theta + data::parB23.at(2)*pow(theta,2);
			}

			/**
			* @brief Auxiliary function describing the boundary between regions 2 and 3
			* @param[in] pi Reduced pressure (p/pstar)
			* @return Reduced temperature (T/Tstar)
			*/
			template <typename U>
			U b23_theta_pi(const U& pi) {
				return data::parB23.at(3) + sqrt((pi-data::parB23.at(4))/data::parB23.at(2));
			}

			/**
			* @brief Auxiliary function describing the boundary between regions 2b and 2c
			* @param[in] eta Reduced enthalpy (h/hstar)
			* @return Reduced pressure (p/pstar)
			*/
			template <typename U>
			U b2bc_pi_eta(const U& eta) {
				return data::parBackwardB2BC.at(0) + data::parBackwardB2BC.at(1)*eta + data::parBackwardB2BC.at(2)*pow(eta,2);
			}

			/**
			* @brief Auxiliary function describing the boundary between regions 2b and 2c
			* @param[in] pi Reduced pressure (p/pstar)
			* @return Reduced enthalpy (h/hstar)
			*/
			template <typename U>
			U b2bc_eta_pi(const U& pi) {
				return data::parBackwardB2BC.at(3) + sqrt((pi-data::parBackwardB2BC.at(4))/data::parBackwardB2BC.at(2));
			}


		}	// end namespace auxiliary


	}	// end namespace region2


	namespace region4 {


		namespace auxiliary {


				/**
				* @brief Auxiliary function for computing saturation pressure as a function of temperature
				* @param[in] theta Quantity related to reduced temperature (T/Tstar)
				* @return Reduced pressure (p/pstar)
				*/
				template <typename U>
				U pi_theta(const U& theta) {
					const U A(                     pow(theta,2) + data::parBasic.at(0)*theta + data::parBasic.at(1));
					const U B(data::parBasic.at(2)*pow(theta,2) + data::parBasic.at(3)*theta + data::parBasic.at(4));
					const U C(data::parBasic.at(5)*pow(theta,2) + data::parBasic.at(6)*theta + data::parBasic.at(7));
					return pow(2.*C/pos(sqrt(pos(pow(B,2)-4.*A*C))-B),4);
				}

				/**
				* @brief Auxiliary function for computing saturation temperature as a function of pressure
				* @param[in] beta Quantity related to reduced pressure (p/pstar)
				* @return Reduced temperature (T/Tstar)
				*/
				template <typename U>
				U theta_beta(const U&  beta) {
					const U E(                     pow(beta,2) + data::parBasic.at(2)*beta + data::parBasic.at(5));
					const U F(data::parBasic.at(0)*pow(beta,2) + data::parBasic.at(3)*beta + data::parBasic.at(6));
					const U G(data::parBasic.at(1)*pow(beta,2) + data::parBasic.at(4)*beta + data::parBasic.at(7));
					const U D(2.*G/neg(-F-sqrt(pos(pow(F,2)-4.*E*G))));
					return 0.5*(data::parBasic.at(9) + D - sqrt(pos(pow(data::parBasic.at(9)+D,2)-4.*(data::parBasic.at(8)+data::parBasic.at(9)*D))));
				}


		}	// end namespace auxiliary


	}	// end namespace region4


}	// end namespace iapws_if97
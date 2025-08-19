/**
 * @file iapwsAuxiliaryDerivatives.h
 *
 * @brief File containing template implementation of auxiliary functions for derivatives of the IAPWS-IF97 model (not intended to be accessed by the user).
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

#include <vector>
#include <algorithm>


namespace iapws_if97 {


	namespace region1 {


		namespace auxiliary {


			namespace derivatives {


				/**
				* @brief Auxiliary function needed for the derivative of enthalpy w.r.t. temperature in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the derivative of enthalpy w.r.t. temperature
				*/
				template <typename U, typename V>
				auto dgamma_tau_dtau(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*pow(myPi,d->I)*((double)d->J)*((double)(d->J-1.))*pow(myTau,d->J - 2.);	// Need to compute first element separately to deduce return type
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*pow(myPi,d->I)*((double)d->J)*((double)(d->J-1.))*pow(myTau,d->J - 2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of enthalpy w.r.t. pressure in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the derivative of enthalpy w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dgamma_tau_dpi(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*pow(myTau,d->J - 1.);
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*pow(myTau,d->J - 1.);
					}
					return -1.*result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of enthalpy w.r.t. temperature in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the second derivative of enthalpy w.r.t. temperature
				*/
				template <typename U, typename V>
				auto d2gamma_tau_dtau2(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*pow(myPi,d->I)*((double)d->J)*((double)(d->J-1.))*((double)(d->J-2.))*pow(myTau,d->J - 3.);
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*pow(myPi,d->I)*((double)d->J)*((double)(d->J-1.))*((double)(d->J-2.))*pow(myTau,d->J - 3.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of enthalpy w.r.t. pressure in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the second derivative of enthalpy w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2gamma_tau_dpi2(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*((double)d->J)*pow(myTau,d->J - 1.);
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*((double)d->J)*pow(myTau,d->J - 1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of enthalpy in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to a mixed third derivative of enthalpy
				*/
				template <typename U, typename V>
				auto d2gamma_tau_dpitau(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myTau,d->J - 2.);
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myTau,d->J - 2.);
					}
					return -1.*result;
				}

				/**
				* @brief Auxiliary function needed for the third derivative of enthalpy w.r.t. pressure in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the third derivative of enthalpy w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d3gamma_tau_dpi3(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*((double)d->I-2.)*pow(myPi,d->I-3.)*((double)d->J)*pow(myTau,d->J - 1.);
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*((double)d->I-2.)*pow(myPi,d->I-3.)*((double)d->J)*pow(myTau,d->J - 1.);
					}
					return -1.*result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of enthalpy in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to a mixed third derivative of enthalpy
				*/
				template <typename U, typename V>
				auto d3gamma_tau_dpi2tau(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*((double)d->J)*((double)d->J-1.)*pow(myTau,d->J - 2.);
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*((double)d->J)*((double)d->J-1.)*pow(myTau,d->J - 2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of enthalpy in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to a mixed third derivative of enthalpy
				*/
				template <typename U, typename V>
				auto d3gamma_tau_dpitau2(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(myTau,d->J - 3.);
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(myTau,d->J - 3.);
					}
					return -1.*result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of entropy w.r.t. pressure in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the second derivative of enthalpy w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dgamma_pi_dpi(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*((double)d->I)*((double)(d->I-1.))*pow(myPi,d->I - 2.)*pow(myTau,d->J);	// Need to compute first element separately to deduce return type
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*((double)d->I)*((double)(d->I-1.))*pow(myPi,d->I - 2.)*pow(myTau,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of entropy w.r.t. pressure in the extension of region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the second derivative of enthalpy w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2gamma_pi_dpi2(const U& pi, const V& tau) {
					const U myPi = 7.1 - pi;
					const V myTau = tau - 1.222;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic.begin();
					auto result = d->n*((double)d->I)*((double)(d->I-1.))*((double)(d->I-2.))*pow(myPi,d->I - 3.)*pow(myTau,d->J);	// Need to compute first element separately to deduce return type
					for( ++d; d!= data::parBasic.end(); ++d){
						result += d->n*((double)d->I)*((double)(d->I-1.))*((double)(d->I-2.))*pow(myPi,d->I - 3.)*pow(myTau,d->J);
					}
					return -1.*result;
				}

				/**
				* @brief Auxiliary function needed for the partial derivative of temperature w.r.t. pressure in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensionles quantitiy related to the partial derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dtheta_pi_eta_dpi(const U& pi, const V& eta) {
					const V myEta = eta + 1.;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTph.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*pow(myEta,d->J);
					for( ++d; d!= data::parBackwardTph.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*pow(myEta,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the partial derivative of temperature w.r.t. specific enthalpy in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensionles quantitiy related to the partial derivative of temperature w.r.t. specific enthalpy
				*/
				template <typename U, typename V>
				auto dtheta_pi_eta_deta(const U& pi, const V& eta) {
					const V myEta = eta + 1.;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTph.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTph.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second partial derivative of temperature w.r.t. pressure in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensionles quantitiy related to the second partial derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_dpi2(const U& pi, const V& eta) {
					const V myEta = eta + 1.;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTph.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(myEta,d->J);
					for( ++d; d!= data::parBackwardTph.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(myEta,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second partial derivative of temperature w.r.t. specific enthalpy in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensionles quantitiy related to the second partial derivative of temperature w.r.t. specific enthalpy
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_deta2(const U& pi, const V& eta) {
					const V myEta = eta + 1.;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTph.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					for( ++d; d!= data::parBackwardTph.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third partial derivative of temperature w.r.t. pressure & enthalpy in region 1
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensionles quantitiy related to a mixed third partial derivative of temperature w.r.t. pressure & enthalpy
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_dpieta(const U& pi, const V& eta) {
					const V myEta = eta + 1.;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTph.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTph.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}


			}	// end namespace derivatives


		}	// end namespace auxiliary


	}	// end namespace region1


	namespace region2 {


		namespace auxiliary {


			namespace derivatives {


				/**
				* @brief Auxiliary function needed for the partial derivative of h w.r.t. T in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the partial derivative of h w.r.t. T
				*/
				template <typename U, typename V>
				V dgamma_0_tau_dtau(const U& pi, const V& tau) {
					V result = 0.;
					for(std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic0.begin(); d!= data::parBasic0.end(); ++d){
						result += d->n*((double)d->J)*(((double)d->J)-1.)*pow(tau,d->J - 2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second partial derivative of s w.r.t. p in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @return Dimensionles quantitiy related to the second partial derivative of s w.r.t. p
				*/
				template <typename U>
				U dgamma_0_pi_dpi(const U& pi) {
					return -1./pow(pi,2);
				}

				/**
				* @brief Auxiliary function needed for the partial derivative of h w.r.t. T in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the partial derivative of h w.r.t. T
				*/
				template <typename U, typename V>
				auto dgamma_r_tau_dtau(const U& pi, const V& tau) {
					const V myTau = tau - 0.5;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*(((double)d->J)-1.)*pow(myTau,d->J - 2.);
					for( ++d; d!= data::parBasicR.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*(((double)d->J)-1.)*pow(myTau,d->J - 2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second partial derivative of s w.r.t. p in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the second partial derivative of s w.r.t. p
				*/
				template <typename U, typename V>
				auto dgamma_r_pi_dpi(const U& pi, const V& tau) {
					const V myTau = tau - 0.5;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
					auto result = d->n*((double)d->I)*(((double)d->I)-1.)*pow(pi,d->I - 2.)*pow(myTau,d->J);
					for( ++d; d!= data::parBasicR.end(); ++d){
						result += d->n*((double)d->I)*(((double)d->I)-1.)*pow(pi,d->I - 2.)*pow(myTau,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the partial derivative of h w.r.t. p in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the partial derivative of h w.r.t. p
				*/
				template <typename U, typename V>
				auto dgamma_r_tau_dpi(const U& pi, const V& tau) {
					const V myTau = tau - 0.5;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(myTau,d->J - 1.);
					for( ++d; d!= data::parBasicR.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(myTau,d->J - 1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second partial derivative of h w.r.t. T in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the second partial derivative of h w.r.t. T
				*/
				template <typename U, typename V>
				V d2gamma_0_tau_dtau2(const U& pi, const V& tau) {
					V result = 0.;
					for(std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasic0.begin(); d!= data::parBasic0.end(); ++d){
						result += d->n*((double)d->J)*(((double)d->J)-1.)*(((double)d->J)-2.)*pow(tau,d->J - 3.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second partial derivative of h w.r.t. T in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the second partial derivative of h w.r.t. T
				*/
				template <typename U, typename V>
				auto d2gamma_r_tau_dtau2(const U& pi, const V& tau) {
					const V myTau = tau - 0.5;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*(((double)d->J)-1.)*(((double)d->J)-2.)*pow(myTau,d->J - 3.);
					for( ++d; d!= data::parBasicR.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*(((double)d->J)-1.)*(((double)d->J)-2.)*pow(myTau,d->J - 3.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second partial derivative of h w.r.t. p in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to the second partial derivative of h w.r.t. p
				*/
				template <typename U, typename V>
				auto d2gamma_r_tau_dpi2(const U& pi, const V& tau) {
					const V myTau = tau - 0.5;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(myTau,d->J - 1.);
					for( ++d; d!= data::parBasicR.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(myTau,d->J - 1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third partial derivative of h in region 2
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] tau Inverse reduced temperature (Tstar/T)
				* @return Dimensionles quantitiy related to a mixed third partial derivative of h
				*/
				template <typename U, typename V>
				auto d2gamma_r_tau_dpitau(const U& pi, const V& tau) {
					const V myTau = tau - 0.5;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBasicR.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myTau,d->J - 2.);
					for( ++d; d!= data::parBasicR.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myTau,d->J - 2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. pressure in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dtheta_pi_eta_dpi_a(const U& pi, const V& eta) {
					const V myEta = eta - 2.1;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*pow(myEta,d->J);
					for( ++d; d!= data::parBackwardTphA.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*pow(myEta,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. enthalpy in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto dtheta_pi_eta_deta_a(const U& pi, const V& eta) {
					const V myEta = eta - 2.1;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphA.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. pressure in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_dpi2_a(const U& pi, const V& eta) {
					const V myEta = eta - 2.1;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(myEta,d->J);
					for( ++d; d!= data::parBackwardTphA.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(myEta,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. enthalpy in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_deta2_a(const U& pi, const V& eta) {
					const V myEta = eta - 2.1;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					for( ++d; d!= data::parBackwardTphA.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_dpieta_a(const U& pi, const V& eta) {
					const V myEta = eta - 2.1;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphA.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the third derivative of temperature w.r.t. enthalpy in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the third derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_deta3_a(const U& pi, const V& eta) {
					const V myEta = eta - 2.1;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(myEta,d->J-3.);
					for( ++d; d!= data::parBackwardTphA.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(myEta,d->J-3.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to a mixed thid derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_dpi2eta_a(const U& pi, const V& eta) {
					const V myEta = eta - 2.1;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphA.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to a mixed thid derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_dpieta2_a(const U& pi, const V& eta) {
					const V myEta = eta - 2.1;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphA.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					for( ++d; d!= data::parBackwardTphA.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. pressure in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dtheta_pi_eta_dpi_b(const U& pi, const V& eta) {
					const U myPi = pi - 2.;
					const V myEta = eta - 2.6;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*pow(myEta,d->J);
					for( ++d; d!= data::parBackwardTphB.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*pow(myEta,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. enthalpy in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto dtheta_pi_eta_deta_b(const U& pi, const V& eta) {
					const U myPi = pi - 2.;
					const V myEta = eta - 2.6;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
					auto result = d->n*pow(myPi,d->I)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphB.end(); ++d){
						result += d->n*pow(myPi,d->I)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. pressure in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_dpi2_b(const U& pi, const V& eta) {
					const U myPi = pi - 2.;
					const V myEta = eta - 2.6;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*pow(myEta,d->J);
					for( ++d; d!= data::parBackwardTphB.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*pow(myEta,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. enthalpy in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_deta2_b(const U& pi, const V& eta) {
					const U myPi = pi - 2.;
					const V myEta = eta - 2.6;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
					auto result = d->n*pow(myPi,d->I)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					for( ++d; d!= data::parBackwardTphB.end(); ++d){
						result += d->n*pow(myPi,d->I)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_dpieta_b(const U& pi, const V& eta) {
					const U myPi = pi - 2.;
					const V myEta = eta - 2.6;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphB.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the third derivative of temperature w.r.t. enthalpy in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the third derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_deta3_b(const U& pi, const V& eta) {
					const U myPi = pi - 2.;
					const V myEta = eta - 2.6;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
					auto result = d->n*pow(myPi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(myEta,d->J-3.);
					for( ++d; d!= data::parBackwardTphB.end(); ++d){
						result += d->n*pow(myPi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(myEta,d->J-3.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_dpi2eta_b(const U& pi, const V& eta) {
					const U myPi = pi - 2.;
					const V myEta = eta - 2.6;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphB.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_dpieta2_b(const U& pi, const V& eta) {
					const U myPi = pi - 2.;
					const V myEta = eta - 2.6;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphB.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					for( ++d; d!= data::parBackwardTphB.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. pressure in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dtheta_pi_eta_dpi_c(const U& pi, const V& eta) {
					const U myPi = pi + 25.;
					const V myEta = eta - 1.8;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*pow(myEta,d->J);
					for( ++d; d!= data::parBackwardTphC.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*pow(myEta,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. enthalpy in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto dtheta_pi_eta_deta_c(const U& pi, const V& eta) {
					const U myPi = pi + 25.;
					const V myEta = eta - 1.8;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
					auto result = d->n*pow(myPi,d->I)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphC.end(); ++d){
						result += d->n*pow(myPi,d->I)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. pressure in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_dpi2_c(const U& pi, const V& eta) {
					const U myPi = pi + 25.;
					const V myEta = eta - 1.8;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*pow(myEta,d->J);
					for( ++d; d!= data::parBackwardTphC.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*pow(myEta,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. enthalpy in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_deta2_c(const U& pi, const V& eta) {
					const U myPi = pi + 25.;
					const V myEta = eta - 1.8;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
					auto result = d->n*pow(myPi,d->I)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					for( ++d; d!= data::parBackwardTphC.end(); ++d){
						result += d->n*pow(myPi,d->I)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the mixed second derivative of temperature in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the mixed second derivative of temperature
				*/
				template <typename U, typename V>
				auto d2theta_pi_eta_dpieta_c(const U& pi, const V& eta) {
					const U myPi = pi + 25.;
					const V myEta = eta - 1.8;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphC.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the third derivative of temperature w.r.t. enthalpy in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to the third derivative of temperature w.r.t. enthalpy
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_deta3_c(const U& pi, const V& eta) {
					const U myPi = pi + 25.;
					const V myEta = eta - 1.8;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
					auto result = d->n*pow(myPi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(myEta,d->J-3.);
					for( ++d; d!= data::parBackwardTphC.end(); ++d){
						result += d->n*pow(myPi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(myEta,d->J-3.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_dpi2eta_c(const U& pi, const V& eta) {
					const U myPi = pi + 25.;
					const V myEta = eta - 1.8;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*((double)d->J)*pow(myEta,d->J-1.);
					for( ++d; d!= data::parBackwardTphC.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(myPi,d->I-2.)*((double)d->J)*pow(myEta,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_eta_dpieta2_c(const U& pi, const V& eta) {
					const U myPi = pi + 25.;
					const V myEta = eta - 1.8;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTphC.begin();
					auto result = d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					for( ++d; d!= data::parBackwardTphC.end(); ++d){
						result += d->n*((double)d->I)*pow(myPi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(myEta,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. pressure in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dtheta_pi_sigma_dpi_a(const U& pi, const V& sigma) {
					const V mySigma = sigma - 2.;
					std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*pow(mySigma,d->J);
					for( ++d; d!= data::parBackwardTpsA.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*pow(mySigma,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. entropy in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto dtheta_pi_sigma_dsigma_a(const U& pi, const V& sigma) {
					const V mySigma = sigma - 2.;
					std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsA.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. pressure in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dpi2_a(const U& pi, const V& sigma) {
					const V mySigma = sigma - 2.;
					std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(mySigma,d->J);
					for( ++d; d!= data::parBackwardTpsA.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(mySigma,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. entropy in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dsigma2_a(const U& pi, const V& sigma) {
					const V mySigma = sigma - 2.;
					std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					for( ++d; d!= data::parBackwardTpsA.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the mixed second derivative of temperature in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the mixed second derivative of temperature
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dpisigma_a(const U& pi, const V& sigma) {
					const V mySigma = sigma - 2.;
					std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsA.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the third derivative of temperature w.r.t. entropy in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the third derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dsigma3_a(const U& pi, const V& sigma) {
					const V mySigma = sigma - 2.;
					std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(mySigma,d->J-3.);
					for( ++d; d!= data::parBackwardTpsA.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(mySigma,d->J-3.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dpi2sigma_a(const U& pi, const V& sigma) {
					const V mySigma = sigma - 2.;
					std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsA.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2a
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dpisigma2_a(const U& pi, const V& sigma) {
					const V mySigma = sigma - 2.;
					std::vector< DataTriple <double,int,double> >::const_iterator d=data::parBackwardTpsA.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					for( ++d; d!= data::parBackwardTpsA.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. pressure in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dtheta_pi_sigma_dpi_b(const U& pi, const V& sigma) {
					const V mySigma = 10. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*pow(mySigma,d->J);
					for( ++d; d!= data::parBackwardTpsB.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*pow(mySigma,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. entropy in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto dtheta_pi_sigma_dsigma_b(const U& pi, const V& sigma) {
					const V mySigma = 10. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsB.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return -result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. pressure in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dpi2_b(const U& pi, const V& sigma) {
					const V mySigma = 10. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(mySigma,d->J);
					for( ++d; d!= data::parBackwardTpsB.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(mySigma,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. entropy in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dsigma2_b(const U& pi, const V& sigma) {
					const V mySigma = 10. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					for( ++d; d!= data::parBackwardTpsB.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the mixed second derivative of temperature in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the mixed second derivative of temperature
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dpisigma_b(const U& pi, const V& sigma) {
					const V mySigma = 10. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsB.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return -result;
				}

				/**
				* @brief Auxiliary function needed for the third derivative of temperature w.r.t. entropy in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the third derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dsigma3_b(const U& pi, const V& sigma) {
					const V mySigma = 10. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(mySigma,d->J-3.);
					for( ++d; d!= data::parBackwardTpsB.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(mySigma,d->J-3.);
					}
					return -result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dpi2sigma_b(const U& pi, const V& sigma) {
					const V mySigma = 10. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsB.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return -result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2b
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dpisigma2_b(const U& pi, const V& sigma) {
					const V mySigma = 10. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsB.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					for( ++d; d!= data::parBackwardTpsB.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. pressure in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto dtheta_pi_sigma_dpi_c(const U& pi, const V& sigma) {
					const V mySigma = 2. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*pow(mySigma,d->J);
					for( ++d; d!= data::parBackwardTpsC.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*pow(mySigma,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the derivative of temperature w.r.t. entropy in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto dtheta_pi_sigma_dsigma_c(const U& pi, const V& sigma) {
					const V mySigma = 2. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsC.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return -result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. pressure in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. pressure
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dpi2_c(const U& pi, const V& sigma) {
					const V mySigma = 2. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(mySigma,d->J);
					for( ++d; d!= data::parBackwardTpsC.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*pow(mySigma,d->J);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the second derivative of temperature w.r.t. entropy in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the second derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dsigma2_c(const U& pi, const V& sigma) {
					const V mySigma = 2. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					for( ++d; d!= data::parBackwardTpsC.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function needed for the mixed second derivative of temperature in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the mixed second derivative of temperature
				*/
				template <typename U, typename V>
				auto d2theta_pi_sigma_dpisigma_c(const U& pi, const V& sigma) {
					const V mySigma = 2. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsC.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return -result;
				}

				/**
				* @brief Auxiliary function needed for the third derivative of temperature w.r.t. entropy in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to the third derivative of temperature w.r.t. entropy
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dsigma3_c(const U& pi, const V& sigma) {
					const V mySigma = 2. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
					auto result = d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(mySigma,d->J-3.);
					for( ++d; d!= data::parBackwardTpsC.end(); ++d){
						result += d->n*pow(pi,d->I)*((double)d->J)*((double)d->J-1.)*((double)d->J-2.)*pow(mySigma,d->J-3.);
					}
					return -result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dpi2sigma_c(const U& pi, const V& sigma) {
					const V mySigma = 2. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
					auto result = d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(mySigma,d->J-1.);
					for( ++d; d!= data::parBackwardTpsC.end(); ++d){
						result += d->n*((double)d->I)*((double)d->I-1.)*pow(pi,d->I-2.)*((double)d->J)*pow(mySigma,d->J-1.);
					}
					return -result;
				}

				/**
				* @brief Auxiliary function needed for a mixed third derivative of temperature in region 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @param[in] sigma Reduced entropy (s/sstar)
				* @return Dimensional quantitiy related to a mixed third derivative of temperature
				*/
				template <typename U, typename V>
				auto d3theta_pi_sigma_dpisigma2_c(const U& pi, const V& sigma) {
					const V mySigma = 2. - sigma;
					std::vector< DataTriple <int,int,double> >::const_iterator d=data::parBackwardTpsC.begin();
					auto result = d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					for( ++d; d!= data::parBackwardTpsC.end(); ++d){
						result += d->n*((double)d->I)*pow(pi,d->I-1.)*((double)d->J)*((double)d->J-1.)*pow(mySigma,d->J-2.);
					}
					return result;
				}

				/**
				* @brief Auxiliary function for the derivative of the boundary between regions 2 and 3
				* @param[in] theta Reduced temperature
				* @return Derivative of reduced pressure
				*/
				template <typename U>
				U b23_dpi_theta(const U& theta) {
					return data::parB23.at(1) + 2*data::parB23.at(2)*theta;
				}

				/**
				* @brief Auxiliary function for the derivative of the boundary between regions 2 and 3
				* @param[in] pi Reduced pressure
				* @return Derivative of reduced temperature
				*/
				template <typename U>
				U b23_dtheta_pi(const U& pi) {
					return 1. / ( 2.*sqrt(data::parB23.at(2)*(pi-data::parB23.at(4))) );
				}

				/**
				* @brief Auxiliary function for the derivative of the boundary between regions 2b and 2c
				* @param[in] eta Reduced enthalpy (h/hstar)
				* @return Derivative of reduced pressure (p/pstar)
				*/
				template <typename U>
				U b2bc_dpi_eta(const U& eta) {
				return data::parBackwardB2BC.at(1) + 2.*data::parBackwardB2BC.at(2)*eta;
				}

				/**
				* @brief Auxiliary function for the derivative of the boundary between regions 2b and 2c
				* @param[in] pi Reduced pressure (p/pstar)
				* @return Derivative of reduced enthalpy (h/hstar)
				*/
				template <typename U>
				U b2bc_deta_pi(const U& pi) {
					return 1./(2.*sqrt(data::parBackwardB2BC.at(2)*(pi-data::parBackwardB2BC.at(4))));
				}


			}	// end namespace derivatives


		}	// end namespace auxiliary


	}	// end namespace region2


	namespace region4 {


		namespace auxiliary {


			namespace derivatives {


				/**
				* @brief Auxiliary function for computing the derivative of saturation pressure as a function of temperature
				* @param[in] theta Quantity related to reduced temperature
				* @return Derivative of reduced pressure
				*/
				template <typename U>
				U dpi_theta(const U& theta) {
					const U A  (                     pow(theta,2) + data::parBasic.at(0)*theta + data::parBasic.at(1));
					const U B  (data::parBasic.at(2)*pow(theta,2) + data::parBasic.at(3)*theta + data::parBasic.at(4));
					const U C  (data::parBasic.at(5)*pow(theta,2) + data::parBasic.at(6)*theta + data::parBasic.at(7));
					const U dA (                     2.*theta + data::parBasic.at(0));
					const U dB (data::parBasic.at(2)*2.*theta + data::parBasic.at(3));
					const U dC (data::parBasic.at(5)*2.*theta + data::parBasic.at(6));
					const U tmp   (sqrt(pos(pow(B,2) - 4*A*C)));
					const U dpi_A ( -( 128.*pow(C,5)             / neg(pow(B - tmp,5)*tmp)                                            ));
					const U dpi_B (  (  64.*pow(C,4)*(B/tmp - 1) / neg(pow(B - tmp,5))                                                ));
					const U dpi_C (  (  64.*pow(C,3)             / pos(pow(B - tmp,4))      - 128.*A*pow(C,4)/neg(pow(B - tmp,5)*tmp) ));
					return dpi_A*dA + dpi_B*dB + dpi_C*dC;
				}

				/**
				* @brief Auxiliary function for computing the second derivative of saturation pressure as a function of temperature
				* @param[in] theta Quantity related to reduced temperature
				* @return Second derivative of reduced pressure
				*/
				template <typename U>
				U d2pi_theta(const U& theta) {
					const U A   (                     pow(theta,2) + data::parBasic.at(0)*theta + data::parBasic.at(1));
					const U B   (data::parBasic.at(2)*pow(theta,2) + data::parBasic.at(3)*theta + data::parBasic.at(4));
					const U C   (data::parBasic.at(5)*pow(theta,2) + data::parBasic.at(6)*theta + data::parBasic.at(7));
					const U dA  (                     2.*theta + data::parBasic.at(0));
					const U dB  (data::parBasic.at(2)*2.*theta + data::parBasic.at(3));
					const U dC  (data::parBasic.at(5)*2.*theta + data::parBasic.at(6));
					const U d2A (                     2.);
					const U d2B (data::parBasic.at(2)*2.);
					const U d2C (data::parBasic.at(5)*2.);
					const U tmp1   (pow(B,2) - 4*A*C);
					const U tmp2   (pos(sqrt(pos(tmp1))));
					const U tmp3	 (pos(pow(pos(tmp1),1.5)));
					const U dpi_A ( -( 128.*pow(C,5)             / neg(pow(B - tmp2,5)*tmp2)                                            ));
					const U dpi_B (  (  64.*pow(C,4)*(B/tmp2 - 1) / neg(pow(B - tmp2,5))                                                ));
					const U dpi_C (  (  64.*pow(C,3)             / pos(pow(B - tmp2,4))      - 128.*A*pow(C,4)/neg(pow(B - tmp2,5)*tmp2) ));
					const U d2pi_A2 ( (1280.*pow(C,6))/pos(pow(B - tmp2,6)*tmp1) - (256.*pow(C,6))/neg(pow(B - tmp2,5)*tmp3) );
					const U d2pi_B2 ( (320*pow(C,4)*pow(B/tmp2 - 1,2))/pos(pow(B - tmp2,6)) + (64.*pow(C,4)*(1./tmp2 - (1.*pow(B,2))/tmp3))/neg(pow(B - tmp2,5)) );
					const U d2pi_C2 ( (192*pow(C,2))/pos(pow(B - tmp2,4)) + (1280.*pow(A,2)*pow(C,4))/pos(pow(B - tmp2,6)*tmp1) - (1024.*A*pow(C,3))/neg(pow(B - tmp2,5)*tmp2) - (256.*pow(A,2)*pow(C,4))/neg(pow(B - tmp2,5)*tmp3));
					const U d2pi_AB ( (128.*B*pow(C,5))/neg(pow(B - tmp2,5)*tmp3) - (640.*pow(C,5)*(B/tmp2 - 1))/pos(pow(B - tmp2,6)*tmp2) );
					const U d2pi_AC ( (1280.*A*pow(C,5))/pos(pow(B - tmp2,6)*tmp1) - (256.*A*pow(C,5))/neg(pow(B - tmp2,5)*tmp3) - (640.*pow(C,4))/neg(pow(B - tmp2,5)*tmp2));
					const U d2pi_BC ( (256*pow(C,3)*(B/tmp2 - 1))/neg(pow(B - tmp2,5)) - (640.*A*pow(C,4)*(B/tmp2 - 1))/pos(pow(B - tmp2,6)*tmp2) + (128.*A*B*pow(C,4))/neg(pow(B - tmp2,5)*tmp3));
					return	 (dpi_A*d2A + dpi_B*d2B + dpi_C*d2C)
							+(d2pi_A2*pow(dA,2) + d2pi_B2*pow(dB,2) + d2pi_C2*pow(dC,2))
							+(2.*d2pi_AB*dA*dB + 2.*d2pi_AC*dA*dC + 2.*d2pi_BC*dB*dC);
				}

				/**
				* @brief Auxiliary function for computing the derivative of saturation temperature as a function of pressure
				* @param[in] beta Quantity related to reduced pressure
				* @return Derivative of reduced temperature
				*/
				template <typename U>
				U dtheta_beta(const U&  beta) {
					const U E (                     pow(beta,2) + data::parBasic.at(2)*beta + data::parBasic.at(5));
					const U F (data::parBasic.at(0)*pow(beta,2) + data::parBasic.at(3)*beta + data::parBasic.at(6));
					const U G (data::parBasic.at(1)*pow(beta,2) + data::parBasic.at(4)*beta + data::parBasic.at(7));
					const U dE(                     2.*beta + data::parBasic.at(2));
					const U dF(data::parBasic.at(0)*2.*beta + data::parBasic.at(3));
					const U dG(data::parBasic.at(1)*2.*beta + data::parBasic.at(4));
					const U tmp1( pos(sqrt(pos(pow(F,2)-4.*E*G))) );
					const U D(2.*G/neg(-F-tmp1));
					const U dD_E( -(4.*pow(G,2))/pos(tmp1*pow(F + tmp1,2)) );
					const U dD_F( (2.*G*(F/tmp1 + 1.))/pos(pow(F + tmp1,2)) );
					const U dD_G( - 2./pos(F + tmp1) - (4.*E*G)/pos(tmp1*pow(F + tmp1,2)) );
					const U dtheta_D ( 0.5*(data::parBasic.at(9) - D)/pos(sqrt(pos(pow(data::parBasic.at(9) + D,2) - 4.*data::parBasic.at(9)*D - 4.*data::parBasic.at(8)))) + 0.5 );
					return dtheta_D * ( dD_E*dE + dD_F*dF + dD_G*dG);
				}

				/**
				* @brief Auxiliary function for computing the second derivative of saturation temperature as a function of pressure
				* @param[in] beta Quantity related to reduced pressure
				* @return second derivative of reduced temperature
				*/
				template <typename U>
				U d2theta_beta(const U&  beta) {
					const U E  (                     pow(beta,2) + data::parBasic.at(2)*beta + data::parBasic.at(5));
					const U F  (data::parBasic.at(0)*pow(beta,2) + data::parBasic.at(3)*beta + data::parBasic.at(6));
					const U G  (data::parBasic.at(1)*pow(beta,2) + data::parBasic.at(4)*beta + data::parBasic.at(7));
					const U dE (                     2.*beta + data::parBasic.at(2));
					const U dF (data::parBasic.at(0)*2.*beta + data::parBasic.at(3));
					const U dG (data::parBasic.at(1)*2.*beta + data::parBasic.at(4));
					const U d2E(                     2.);
					const U d2F(data::parBasic.at(0)*2.);
					const U d2G(data::parBasic.at(1)*2.);
					const U tmp1( pos(pow(F,2)-4.*E*G) );
					const U tmp2( pos(sqrt(tmp1)) );
					const U D(2.*G/neg(-F-tmp2));
					const U dD_E( -(4.*pow(G,2))/pos(tmp2*pow(F + tmp2,2)) );
					const U dD_F( (2.*G*(F/tmp2 + 1.))/pos(pow(F + tmp2,2)) );
					const U dD_G( - 2./pos(F + tmp2) - (4.*E*G)/pos(tmp2*pow(F + tmp2,2)) );
					const U tmp3 ( pos(pow(tmp1,1.5)*pow(F+tmp2,2)) );
					const U d2D_E2( - 8.*pow(G,3)/tmp3 - 16.*pow(G,3)/pos(tmp1*pow(F+tmp2,3)) );
					const U d2D_F2( 2*G*(1./tmp2 - pow(F,2)/pos(pow(tmp1,1.5)))/pos(pow(F+tmp2,2)) - (4*G*pow(F/tmp2 + 1,2))/pos(pow(F+tmp2,3)) );
					const U d2D_G2( - 8.*E/pos(tmp2*pow(F+tmp2,2)) - 16.*pow(E,2)*G/pos(tmp1*pow(F+tmp2,3)) - 8.*pow(E,2)*G/tmp3 );
					const U d2D_EF( 8.*pow(G,2)*(F/tmp2 + 1)/pos(tmp2*pow(F+tmp2,3)) + 4.*F*pow(G,2)/tmp3 );
					const U d2D_EG( - 8.*G/pos(tmp2*pow(F+tmp2,2)) - 16.*E*pow(G,2)/pos(tmp1*pow(F+tmp2,3)) - 8.*E*pow(G,2)/tmp3 );
					const U d2D_FG( 2.*(F/tmp2 + 1)/pos(pow(F+tmp2,2)) + 8.*E*G*(F/tmp2 + 1)/pos(tmp2*pow(F+tmp2,3)) + 4.*E*F*G/tmp3 );
					const U dD_beta (        dD_E*dE        +     dD_F*dF        +    dD_G*dG );
					const U d2D_beta(  (     dD_E*d2E       +     dD_F*d2F       +    dD_G*d2G       )
									 + (   d2D_E2*pow(dE,2) +   d2D_F2*pow(dF,2) +  d2D_G2*pow(dG,2) )
									 + ( 2*d2D_EF*dE*dF     + 2*d2D_EG*dE*dG     + 2*d2D_FG*dF*dG    ) );
					const U dtheta_D ( 0.5*(data::parBasic.at(9) - D)/pos(sqrt(pos(pow(data::parBasic.at(9) + D,2) - 4.*data::parBasic.at(9)*D - 4.*data::parBasic.at(8)))) + 0.5 );
					const U d2theta_D ( 0.5*pow(data::parBasic.at(9) - D,2)/pos(pow(pos(pow(data::parBasic.at(9) + D,2) - 4.*data::parBasic.at(9)*D - 4.*data::parBasic.at(8)),1.5)) - 0.5/pos(sqrt(pos(pow(data::parBasic.at(9) + D,2) - 4.*data::parBasic.at(9)*D - 4.*data::parBasic.at(8)))) );
					return d2theta_D*pow(dD_beta,2) + dtheta_D*d2D_beta;
				}


			}	// end namespace derivatives


		}	// end namespace auxiliary


	}	// end namespace region4


}	// end namespace iapws_if97
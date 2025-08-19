/**
 * @file iapws.h
 *
 * @brief File serving as single include file for this implementation of the IAPWS-IF97 model. Also provides the double implementation (forwarding to the corresponding templates).
 *
 * Original model: Wagner, W.; Cooper, J. R.; Dittmann, A.; Kijima, J.; Kretzschmar, H.-J.; Kruse, A.; Mareš, R.; Oguchi, K.; Sato, H.; Stocker, I.; Sifner, O.; Takaishi, Y.; Tanishita, I.; Trubenbach, J. & Willkommen, T.:
 *                  The IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam. Journal of Engineering for Gas Turbines and Power -- Transactions of the ASME, 2000, 122, 150-182.
 *
 * Revised model used for this implementation: Revised Release on the IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam.
												The International Association for the Properties of Water and Steam, Technical Report IAPWS R7-97(2012), 2012. http://www.iapws.org/relguide/IF97-Rev.html.
 *
 * ==============================================================================\n
 * © Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
 * ==============================================================================\n
 *
 * @author Dominik Bongartz, Alexander Mitsos
 * @date 26.03.2019
 *
 */

#pragma once

#include "iapwsRegion1.h"
#include "iapwsRegion2.h"
#include "iapwsRegion4.h"

#include <stdexcept>
#include <string>


#undef LIVE_DANGEROUSLY
// #define LIVE_DANGEROUSLY


namespace mc {


	// 1d functions of IAPWS-IF97 model
	inline double iapws
	(const double x, const double type)
	{
		switch((int)type){
			case 11:	// region 1, h(p,T)
			case 12:	// region 1, s(p,T)
			case 13:	// region 1, T(p,h)
			case 14:	// region 1, T(p,s)
			case 15:	// region 1, h(p,s)
			case 16:	// region 1, s(p,h)
			case 21:	// region 2, h(p,T)
			case 22:	// region 2, s(p,T)
			case 23:	// region 2, T(p,h)
			case 24:	// region 2, T(p,s)
			case 25:	// region 2, h(p,s)
			case 26:	// region 2, s(p,h)
			case 43:	// region 4-1/2, h(p,x)
			case 44:	// region 4-1/2, h(T,x)
			case 45:	// region 4-1/2, s(p,x)
			case 46:	// region 4-1/2, s(T,x)
			case 47:	// region 4-1/2, x(p,h)
			case 48:	// region 4-1/2, x(p,s)
			case 49:	// region 4-1/2, h(p,s)
			case 410:	// region 4-1/2, s(p,h)
				throw std::runtime_error("\nmc::McCormick\t IAPWS called with one argument but a 2d type (" + std::to_string((int)type) + ")");
			case 29:	return iapws_if97::region2::get_b23_p_T(x); 		// region 2, boundary to 3, p(T)
			case 210:	return iapws_if97::region2::get_b23_T_p(x); 		// region 2, boundary to 3, T(p)
			case 211:	return iapws_if97::region2::get_b2bc_p_h(x); 		// region 2, boundary 2b/2c, p(h)
			case 212:	return iapws_if97::region2::get_b2bc_h_p(x); 		// region 2, boundary 2b/2c, h(p)
			case 41:	return iapws_if97::region4::get_ps_T(x); 			// region 4, p(T)
			case 42:	return iapws_if97::region4::get_Ts_p(x);			// region 4, T(p)
			case 411:	return iapws_if97::region4::get_hliq_p_12(x);		// region 4-1/2, hliq(p)
			case 412:	return iapws_if97::region4::get_hliq_T_12(x);		// region 4-1/2, hliq(T)
			case 413:	return iapws_if97::region4::get_hvap_p_12(x);		// region 4-1/2, hvap(p)
			case 414:	return iapws_if97::region4::get_hvap_T_12(x);		// region 4-1/2, hvap(T)
			case 415:	return iapws_if97::region4::get_sliq_p_12(x);		// region 4-1/2, sliq(p)
			case 416:	return iapws_if97::region4::get_sliq_T_12(x);		// region 4-1/2, sliq(T)
			case 417:	return iapws_if97::region4::get_svap_p_12(x);		// region 4-1/2, svap(p)
			case 418:	return iapws_if97::region4::get_svap_T_12(x);		// region 4-1/2, svap(T)
			default:
				throw std::runtime_error("\nmc::McCormick\t IAPWS called with unkown type (" + std::to_string((int)type) + ").");
		}
	}

	// 2d functions of IAPWS-IF97 model
	inline double iapws
	(const double x, const double y, const double type)
	{
		switch((int)type){
			// 2d functions:
			case 11:	return iapws_if97::region1::get_h_pT(x,y); 		// region 1, h(p,T)
			case 12:	return iapws_if97::region1::get_s_pT(x,y); 		// region 1, s(p,T)
			case 13:	return iapws_if97::region1::get_T_ph(x,y); 		// region 1, T(p,h)
			case 14:	return iapws_if97::region1::get_T_ps(x,y); 		// region 1, T(p,s)
			case 15:	return iapws_if97::region1::get_h_ps(x,y); 		// region 1, h(p,s)
			case 16:	return iapws_if97::region1::get_s_ph(x,y); 		// region 1, s(p,h)
			case 21:	return iapws_if97::region2::get_h_pT(x,y); 		// region 2, h(p,T)
			case 22:	return iapws_if97::region2::get_s_pT(x,y); 		// region 2, s(p,T)
			case 23:	return iapws_if97::region2::get_T_ph(x,y); 		// region 2, T(p,h)
			case 24:	return iapws_if97::region2::get_T_ps(x,y); 		// region 2, T(p,s)
			case 25:	return iapws_if97::region2::get_h_ps(x,y);		// region 2, h(p,s)
			case 26:	return iapws_if97::region2::get_s_ph(x,y); 		// region 2, s(p,h)
			case 43:	return iapws_if97::region4::get_h_px_12(x,y); 	// region 4-1/2, h(p,x)
			case 44:	return iapws_if97::region4::get_h_Tx_12(x,y); 	// region 4-1/2, h(T,x)
			case 45:	return iapws_if97::region4::get_s_px_12(x,y); 	// region 4-1/2, s(p,x)
			case 46:	return iapws_if97::region4::get_s_Tx_12(x,y); 	// region 4-1/2, s(T,x)
			case 47:	return iapws_if97::region4::get_x_ph_12(x,y); 	// region 4-1/2, x(p,h)
			case 48:	return iapws_if97::region4::get_x_ps_12(x,y); 	// region 4-1/2, x(p,s)
			case 49:	return iapws_if97::region4::get_h_ps_12(x,y); 	// region 4-1/2, h(p,s)
			case 410:	return iapws_if97::region4::get_s_ph_12(x,y); 	// region 4-1/2, s(p,h)
				// 1d functions:
			case 29:	// region 2, boundary to 3, p(T)
			case 210:	// region 2, boundary to 3, T(p)
			case 211:	// region 2, boundary 2b/2c, p(h)
			case 212:	// region 2, boundary 2b/2c, h(p)
			case 41:	// region 4, p(T)
			case 42:	// region 4, T(p)
			case 411:	// region 4-1/2, hliq(p)
			case 412:	// region 4-1/2, hliq(T)
			case 413:	// region 4-1/2, hvap(p)
			case 414:	// region 4-1/2, hvap(T)
			case 415:	// region 4-1/2, sliq(p)
			case 416:	// region 4-1/2, sliq(T)
			case 417:	// region 4-1/2, svap(p)
			case 418:	// region 4-1/2, svap(T)
				throw std::runtime_error("\nmc::McCormick\t IAPWS called with two arguments but a 1d type (" + std::to_string((int)type) + ")");
			default:
				throw std::runtime_error("\nmc::McCormick\t IAPWS called with unkown type (" + std::to_string((int)type) + ").");
		}
	}


}	// end namespace mc
/**
 * @file iapwsFilib.h
 *
 * @brief File containing implementation of interval bounds for the IAPWS-IF97 model in FILIB++ (within MC++).
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
 * @author Dominik Bongartz, Jaromil Najman, Alexander Mitsos
 * @date 15.08.2019
 *
 */

#pragma once

#include "mcfilib.hpp"

#include "iapws.h"


namespace filib {


	// 1d functions of IAPWS-IF97 model
	template < typename N, rounding_strategy K = native_switched, interval_mode E = i_mode_normal >
	interval<N,K,E> iapws(interval<N,K,E> const & x, const double type) {

		if(E) { if (x.isEmpty()) { return interval<N,K,E>::EMPTY(); } }

		namespace r1 = iapws_if97::region1;
		namespace r2 = iapws_if97::region2;
		namespace r4 = iapws_if97::region4;

		switch((int)type){
			// 2d functions:
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
				throw std::runtime_error("\nmc::Filib\t IAPWS called with one argument but a 2d type (" + std::to_string((int)type) + ")");
			// 1d functions:
			case 29:	// region 2, boundary to 3, p(T)
			{
				if (filib::inf(x)<r2::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, boundary between regions 2 and 3, p(T) with T<Tmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r2::data::Tmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, boundary between regions 2 and 3, p(T) with T>Tmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r2::get_b23_p_T(filib::inf(x)),r2::get_b23_p_T(filib::sup(x)));
			}
			case 210:	// region 2, boundary to 3, T(p)
			{
				if (filib::inf(x)<r2::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, boundary between regions 2 and 3, T(p) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r2::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, boundary between regions 2 and 3, T(p) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r2::get_b23_T_p(filib::inf(x)),r2::get_b23_T_p(filib::sup(x)));
			}
			case 211:	// region 2, boundary 2b/2c, p(h)
			{
				if (filib::inf(x)<r2::data::hmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, boundary between regions 2b and 2c, pB2bc(h) with h<hmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r2::data::hmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, boundary between regions 2b and 2c, pB2bc(h) with h>hmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r2::get_b2bc_p_h(filib::inf(x)),r2::get_b2bc_p_h(filib::sup(x)));
			}
			case 212:	// region 2, boundary 2b/2c, h(p)
			{
				if (filib::inf(x)<r2::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, boundary between regions 2b and 2c, hB2bc(p) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r2::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, boundary between regions 2b and 2c, hB2bc(p) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r2::get_b2bc_h_p(filib::inf(x)),r2::get_b2bc_h_p(filib::sup(x)));
			}
			case 41:	// region 4, p(T)
			{
				if (filib::inf(x)<r4::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4, p(T) with T<Tmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::Tmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4, p(T) with T>Tmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r4::get_ps_T(filib::inf(x)),r4::get_ps_T(filib::sup(x)));
			}
			case 42:	// region 4, T(p)
			{
				if (filib::inf(x)<r4::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4, T(p) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4, T(p) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r4::get_Ts_p(filib::inf(x)),r4::get_Ts_p(filib::sup(x)));
			}
			case 411:	// region 4-1/2, hliq(p)
			{
				if (filib::inf(x)<r4::data::pmin)    { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, hliq(p) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::pmax12) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, hliq(p) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r4::get_hliq_p_12(filib::inf(x)),r4::get_hliq_p_12(filib::sup(x)));
			}
			case 412:	// region 4-1/2, hliq(T)
			{
				if (filib::inf(x)<r4::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, hliq(T) with T<Tmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::Tmax12) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, hliq(T) with T>Tmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r4::get_hliq_T_12(filib::inf(x)),r4::get_hliq_T_12(filib::sup(x)));
			}
			case 413:	// region 4-1/2, hvap(p)
			{
				if (filib::inf(x)<r4::data::pmin  ) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, hvap(p) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::pmax12) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, hvap(p) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				double hLower, hUpper;
				if (filib::sup(x) <= r4::data::pmaxhvap12) {		// monotonically increasing
					hLower = r4::get_hvap_p_12(filib::inf(x));
					hUpper = r4::get_hvap_p_12(filib::sup(x));
				} else if (filib::inf(x) >= r4::data::pmaxhvap12) {	// monotonically decreasing
					hLower = r4::get_hvap_p_12(filib::sup(x));
					hUpper = r4::get_hvap_p_12(filib::inf(x));
				} else {											// not monotonic, but concave w/ max at pmaxhvap12
					hLower = std::min(r4::get_hvap_p_12(filib::inf(x)),r4::get_hvap_p_12(filib::sup(x)));
					hUpper = r4::get_hvap_p_12(r4::data::pmaxhvap12);
				}
				return interval<N,K,E>(hLower,hUpper);
			}
			case 414:	// region 4-1/2, hvap(T)
			{
				if (filib::inf(x)<r4::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, hvap(T) with T<Tmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::Tmax12) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, hvap(T) with T>Tmax in range: " + std::to_string(filib::sup(x))); }
				double hLower, hUpper;
				if (filib::sup(x) <= r4::data::Tmaxhvap12) {		// monotonically increasing
					hLower = r4::get_hvap_T_12(filib::inf(x));
					hUpper = r4::get_hvap_T_12(filib::sup(x));
				} else if (filib::inf(x) >= r4::data::Tmaxhvap12) {	// monotonically decreasing
					hLower = r4::get_hvap_T_12(filib::sup(x));
					hUpper = r4::get_hvap_T_12(filib::inf(x));
				} else {											// not monotonic, but concave w/ max at Tmaxhvap12
					hLower = std::min(r4::get_hvap_T_12(filib::inf(x)),r4::get_hvap_T_12(filib::sup(x)));
					hUpper = r4::get_hvap_T_12(r4::data::Tmaxhvap12);
				}
				return interval<N,K,E>(hLower,hUpper);
			}
			case 415:	// region 4-1/2, sliq(p)
			{
				if (filib::inf(x)<r4::data::pmin)    { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, sliq(p) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::pmax12) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, sliq(p) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r4::get_sliq_p_12(filib::inf(x)),r4::get_sliq_p_12(filib::sup(x)));
			}
			case 416:	// region 4-1/2, sliq(T)
			{
				if (filib::inf(x)<r4::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, sliq(T) with T<Tmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::Tmax12) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, sliq(T) with T>Tmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically increasing
				return interval<N,K,E>(r4::get_sliq_T_12(filib::inf(x)),r4::get_sliq_T_12(filib::sup(x)));
			}
			case 417:	// region 4-1/2, svap(p)
			{
				if (filib::inf(x)<r4::data::pmin)    { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, svap(p) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::pmax12) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, svap(p) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically decreasing
				return interval<N,K,E>(r4::get_svap_p_12(filib::sup(x)),r4::get_svap_p_12(filib::inf(x)));
			}
			case 418:	// region 4-1/2, svap(T)
			{
				if (filib::inf(x)<r4::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, svap(T) with T<Tmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::Tmax12) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, Region 4-1/2, svap(T) with T>Tmax in range: " + std::to_string(filib::sup(x))); }
				// monotonically decreasing
				return interval<N,K,E>(r4::get_svap_T_12(filib::sup(x)),r4::get_svap_T_12(filib::inf(x)));
			}
			default:
				throw std::runtime_error("\nmc::Filib\t IAPWS called with unkown type (" + std::to_string((int)type) + ").");
		}

	}


	// 2d functions of IAPWS-IF97 model
	template < typename N, rounding_strategy K = native_switched, interval_mode E = i_mode_normal >
	interval<N,K,E> iapws(interval<N,K,E> const & x, interval<N,K,E> const & y, const double type) {

		if(E) { if (x.isEmpty()) { return interval<N,K,E>::EMPTY(); } }

		namespace r1 = iapws_if97::region1;
		namespace r2 = iapws_if97::region2;
		namespace r4 = iapws_if97::region4;

		switch((int)type){
			// 2d functions:
			case 11:	// region 1, h(p,T)
			{
				if (filib::inf(x)<r1::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, h(p,T) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r1::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, h(p,T) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r1::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, h(p,T) with T<Tmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r1::data::Tmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, h(p,T) with T>Tmax in range: " + std::to_string(filib::sup(y))); }
				// Monotonically increasing w.r.t. T, but not necessarily p
				double hLower;
				if (filib::inf(y)<r1::data::TmaxDhdpGt0) {		// in this region (T<~510K), the function is also monotonically increasing w.r.t. p
					hLower = r1::get_h_pT(filib::inf(x),filib::inf(y));
				}
				else if (filib::inf(y)>r1::data::TminDhdpLt0) {	// in this region (T>~613K), the function is monotonically decreasing w.r.t. p
					hLower = r1::get_h_pT(filib::sup(x),filib::inf(y));
				}
				else {											// need to have a closer look
					// Need to distinguish multiple cases to account for piecewise definition of h (in particular, the extension for p<psat(T))
					// First, check sign of derivatives at both ends
					if (r1::derivatives::get_dh_pT_dp_uncut(filib::inf(x),filib::inf(y)) >= 0) {	// derivative is >=0 at pL (note that cutting at hmax does not change monotonicity!) => it is >=0 everywhere b/c of componentwise convexity
						hLower = r1::get_h_pT(filib::inf(x),filib::inf(y));
					} else {	// in this case, we already know that the minimum cannot lie in the extension, since it is linear in p and always at the lower end of the p interval
						if (r1::derivatives::get_dh_pT_dp_uncut(filib::sup(x),filib::inf(y)) <= 0) {// derivative is <=0 at pU (note that cutting at hmax does not change monotonicity!) => it is <=0 everywhere b/c of componentwise convexity
							hLower = r1::get_h_pT(filib::sup(x),filib::inf(y));
						} else {
							const double psat = r4::original::get_ps_T(filib::inf(y));
							interval<N,K,E> xPhysical(std::max(psat,filib::inf(x)),filib::sup(x));	// the part of the p interval that lies in the physical domain
							hLower = std::max( filib::inf(r1::original::get_h_pT(xPhysical,filib::inf(y))),
											   r1::data::hminAtTmaxDhdpGt0                			   		);
						}
					}
				}
				double hUpper;
				if (filib::sup(y)<r1::data::TmaxDhdpGt0) {			// increasing w.r.t. p
					hUpper = r1::get_h_pT(filib::sup(x),filib::sup(y));
				} else if (filib::sup(y)>r1::data::TminDhdpLt0) {	// decreasing w.r.t. p
					hUpper = r1::get_h_pT(filib::inf(x),filib::sup(y));
				} else {											// not monotonic, but since it is convex w.r.t. p, we know the maximum is at one of the corner points
					hUpper = std::max(	r1::get_h_pT(filib::sup(x),filib::sup(y)),
										r1::get_h_pT(filib::inf(x),filib::sup(y)) );
				}
				return interval<N,K,E>(	hLower,hUpper );
			}
			case 12:	// region 1, s(p,T)
			{
				if (filib::inf(x)<r1::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, s(p,T) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r1::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, s(p,T) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r1::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, s(p,T) with T<Tmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r1::data::Tmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, s(p,T) with T>Tmax in range: " + std::to_string(filib::sup(y))); }
				// Monotonically increasing w.r.t. T, but not necessarily p
				double sLower;
				if ( (filib::inf(y)>r1::data::TminDsdpLt0) || (filib::inf(x)>r1::data::pminDsdpLt0) ) {	// If temperature or pressure are high enough (>~277K or >~19MPa), we are decreasing in p
					sLower = r1::get_s_pT(filib::sup(x),filib::inf(y));
				} else {	// Since in this region we have d2s/dp2<=0, we know that the minimum is at one of the corners (pL,TL) or (pU,TL)
					sLower = std::min( r1::get_s_pT(filib::inf(x),filib::inf(y)),
									   r1::get_s_pT(filib::sup(x),filib::inf(y)) );
				}
				double sUpper;
				if ( (filib::sup(y)>r1::data::TminDsdpLt0) || (filib::inf(x)>r1::data::pminDsdpLt0) ) {	// If temperature or pressure are high enough (>~277K or >~19MPa), we are decreasing in p
					sUpper = r1::get_s_pT(filib::inf(x),filib::sup(y));
				} else {	// Here, we need to have a closer look
					// First, find boundary of the physical domain
					const double psat = r4::original::get_ps_T(filib::sup(y));
					if (filib::inf(x)>=psat) {		// completely in physical domain - need to use interval extensions w.r.t. p (=x)
						sUpper = filib::sup( r1::original::get_s_pT(x,filib::sup(y)) );
					}
					else if (filib::sup(x)>psat) {	// partially in both physical domain and extension
						interval<N,K,E> xPhysical( psat, filib::sup(x) );
						const double sUpperPhys = filib::sup( r1::original::get_s_pT(xPhysical,filib::sup(y)) );
						const double sUpperExt = std::max( r1::get_s_pT(filib::inf(x),filib::sup(y)),
														   r1::get_s_pT(psat         ,filib::sup(y)) );
						sUpper = std::max( sUpperPhys, sUpperExt );
					}
					else {							// completely in extension - here, the function is linear w.r.t. p and hence the max is at one of the corners (pL,TU) or (pU,TU)
						sUpper = std::max( r1::get_s_pT(filib::inf(x),filib::sup(y)),
										   r1::get_s_pT(filib::sup(x),filib::sup(y)) );
					}
				}
				return interval<N,K,E>(	sLower,sUpper );
			}
			case 13:	// region 1, T(p,h)
			{
				if (filib::inf(x)<r1::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, T(p,h) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r1::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, T(p,h) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r1::data::hmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, T(p,h) with h<hmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r1::data::hmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, T(p,h) with h>hmax in range: " + std::to_string(filib::sup(y))); }
				// Monotonically increasing w.r.t. h, but not necessarily p
				double Tlower;	// occurs at hL and some unknown p value
				if (filib::inf(y)>r1::data::hminDTdpLt0) {		// in this region, we are also increasing in p.
					Tlower = r1::get_T_ph(filib::inf(x),filib::inf(y));
				}
				else {									// in this region, the function may or may not be monotonic in p. However, since it is concave w.r.t. p, the minimum lies at either pL or pU.
					Tlower = std::min( r1::get_T_ph(filib::inf(x),filib::inf(y)),
									   r1::get_T_ph(filib::sup(x),filib::inf(y)) );
				}
				double Tupper;	// occurs at hU and some unknown p value
				if (filib::sup(y)>r1::data::hminDTdpLt0) {	// in this region, we are also increasing in p
					Tupper = r1::get_T_ph(filib::sup(x),filib::sup(y));
				}
				else {								// in this region, we need to have a closer look...
					bool completelyRelaxedPhysical = false;
					bool completelyExtension = false;
					bool inBothRegionsButPretendingToBeInRelaxedPhysical = false;	// If our domain contains parts of both the relaxed physical region and the extension, the maximum is
																					// either at their intersection or within the physical region. However, since we cannot analytially
																					// invert hliq(p) to find the p of this intersection, we cannot easily exploit this. Instead, we simply
																					// derive the upper bound from the original functional form (i.e., pretending that we still are in the
																					// (relaxed) physical region). This is valid since the extension is an underestimator of the original function
																					// for h<hminDTdpLt0 since dT/dp is greater in the extension than in the physical region.
					if (filib::inf(x) >= r2::data::pminB23) {
						completelyRelaxedPhysical = true;
					} else {
						if (filib::sup(y)<=r1::original::get_h_pT(filib::inf(x),r4::original::get_Ts_p(filib::inf(x)))) {
							completelyRelaxedPhysical = true;
						} else {
							if (filib::sup(x) < r2::data::pminB23) {
								if (filib::sup(y)>r1::original::get_h_pT(filib::sup(x),r4::original::get_Ts_p(filib::sup(x)))) {
									completelyExtension = true;
								} else {
									inBothRegionsButPretendingToBeInRelaxedPhysical = true;
								}
							} else {
								inBothRegionsButPretendingToBeInRelaxedPhysical = true;
							}
						}
					}
					if (completelyRelaxedPhysical || inBothRegionsButPretendingToBeInRelaxedPhysical) {	// in the relaxed physical domain, need to make another distinction w.r.t. the value of hU
						if (filib::sup(y)<r1::data::hmaxDTdpGt0) {		// here, we are decreasing w.r.t. p
							Tupper = r1::original::get_T_ph(filib::inf(x),filib::sup(y));
						} else {										// no monotonicity, need to rely on interval extensions w.r.t. p
							Tupper = std::min( filib::sup( r1::original::get_T_ph(x,filib::sup(y)) ),
											   r1::data::TmaxAtHminDTdpLt0 );
						}
					} else if (completelyExtension) {	// in the extension, we are increasing w.r.t. p
						Tupper = r1::get_T_ph(filib::sup(x),filib::sup(y));
					}

				}
				return interval<N,K,E>(	Tlower, Tupper );
			}
			case 14:	// region 1, T(p,s)
			{
				if (filib::inf(x)<r1::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, T(p,s) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r1::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, T(p,s) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r1::data::smin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, T(p,s) with s<smin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r1::data::smax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 1, T(p,s) with s>smax in range: " + std::to_string(filib::sup(y))); }
				interval<N,K,E> Torig = r1::original::get_T_ps(x,y);
				return interval<N,K,E>( std::min( std::max(filib::inf(Torig), r1::data::Tmin ), r1::data::Tmax),
										std::min( std::max(filib::sup(Torig), r1::data::Tmin ), r1::data::Tmax) );
			}
			case 15:	// region 1, h(p,s)
			{
				return iapws(x,iapws(x,y,14),11);	// h(p,T(p,s))
			}
			case 16:	// region 1, s(p,h)
			{
				return iapws(x,iapws(x,y,13),12);	// s(p,T(p,h))
			}
			case 21:	// region 2, h(p,T)
			{
				if (filib::inf(x)<r2::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, h(p,T) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r2::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, h(p,T) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r2::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, h(p,T) with T<Tmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r2::data::Tmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, h(p,T) with T>Tmax in range: " + std::to_string(filib::sup(y))); }
				// Monotonically increasing w.r.t. T and decreasing w.r.t. p
				return interval<N,K,E>(	r2::get_h_pT(filib::sup(x), filib::inf(y)),
										r2::get_h_pT(filib::inf(x), filib::sup(y)) );
			}
			case 22:	// region 2, s(p,T)
			{
				if (filib::inf(x)<r2::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, s(p,T) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r2::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, s(p,T) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r2::data::Tmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, s(p,T) with T<Tmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r2::data::Tmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, s(p,T) with T>Tmax in range: " + std::to_string(filib::sup(y))); }
				// Monotonically increasing w.r.t. T and decreasing w.r.t. p
				return interval<N,K,E>(	r2::get_s_pT(filib::sup(x), filib::inf(y)),
										r2::get_s_pT(filib::inf(x), filib::sup(y)) );
			}
			case 23:	// region 2, T(p,h)
			{
				if (filib::inf(x)<r2::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, T(p,h) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r2::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, T(p,h) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r2::data::hmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, T(p,h) with h<hmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r2::data::hmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, T(p,h) with h>hmax in range: " + std::to_string(filib::sup(y))); }
				// Monotonically increasing w.r.t. p and h
				return interval<N,K,E>(	r2::get_T_ph(filib::inf(x), filib::inf(y)),
										r2::get_T_ph(filib::sup(x), filib::sup(y)) );
			}
			case 24:	// region 2, T(p,s)
			{
				if (filib::inf(x)<r2::data::pmin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, T(p,s) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r2::data::pmax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, T(p,s) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r2::data::smin) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, T(p,s) with s<smin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r2::data::smax) { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 2, T(p,s) with s>smax in range: " + std::to_string(filib::sup(y))); }
				// Monotonically increasing w.r.t. p and s
				return interval<N,K,E>(	r2::get_T_ps(filib::inf(x), filib::inf(y)),
										r2::get_T_ps(filib::sup(x), filib::sup(y)) );
			}
			case 25:	// region 2, h(p,s)
			{
				return iapws(x,iapws(x,y,24),21);	// h(p,T(p,s))
			}
			case 26:	// region 2, s(p,h)
			{
				return iapws(x,iapws(x,y,23),22);	// s(p,T(p,h))
			}
			case 43: 	// region 4-1/2, h(p,x)
			{
				if (filib::inf(y)<0.) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, h(p,x) with x<xmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>1.) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, h(p,x) with x>xmax in range: " + std::to_string(filib::sup(y))); }
				interval<N,K,E> hcalc = y*iapws(x,413 /* r4-1/2, hvap(p) */) + (1.-y)*iapws(x,411 /* r4-1/2, hliq(p) */);
				return interval<N,K,E>( std::min( std::max(filib::inf(hcalc), r4::data::hmin12 ), r4::data::hmax12),
										std::min( std::max(filib::sup(hcalc), r4::data::hmin12 ), r4::data::hmax12) );
			}
			case 44: 	// region 4-1/2, h(T,x)
			{
				if (filib::inf(y)<0.) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, h(T,x) with x<xmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>1.) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, h(T,x) with x>xmax in range: " + std::to_string(filib::sup(y))); }
				interval<N,K,E> hcalc = y*iapws(x,414 /* r4-1/2, hvap(T) */) + (1.-y)*iapws(x,412 /* r4-1/2, hliq(T) */);
				return interval<N,K,E>( std::min( std::max(filib::inf(hcalc), r4::data::hmin12 ), r4::data::hmax12),
										std::min( std::max(filib::sup(hcalc), r4::data::hmin12 ), r4::data::hmax12) );
			}
			case 45: 	// region 4-1/2, s(p,x)
			{
				if (filib::inf(y)<0.) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, s(p,x) with x<xmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>1.) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, s(p,x) with x>xmax in range: " + std::to_string(filib::sup(y))); }
				interval<N,K,E> scalc = y*iapws(x,417 /* r4-1/2, svap(p) */) + (1.-y)*iapws(x,415 /* r4-1/2, sliq(p) */);
				return interval<N,K,E>( std::min( std::max(filib::inf(scalc), r4::data::smin12 ), r4::data::smax12),
										std::min( std::max(filib::sup(scalc), r4::data::smin12 ), r4::data::smax12) );
			}
			case 46: 	// region 4-1/2, s(T,x)
			{
				if (filib::inf(y)<0.) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, s(T,x) with x<xmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>1.) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, s(T,x) with x>xmax in range: " + std::to_string(filib::sup(y))); }
				interval<N,K,E> scalc = y*iapws(x,418 /* r4-1/2, svap(T) */) + (1.-y)*iapws(x,416 /* r4-1/2, sliq(T) */);
				return interval<N,K,E>( std::min( std::max(filib::inf(scalc), r4::data::smin12 ), r4::data::smax12),
										std::min( std::max(filib::sup(scalc), r4::data::smin12 ), r4::data::smax12) );
			}
			case 47: 	// region 4-1/2, x(p,h)
			{
				if (filib::inf(x)<r4::data::pmin) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, x(p,h) with p<pmin in range: " + std::to_string(filib::inf(x))); }
				if (filib::sup(x)>r4::data::pmax12)  { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, x(p,h) with p>pmax in range: " + std::to_string(filib::sup(x))); }
				if (filib::inf(y)<r4::data::hmin12)  { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, x(p,h) with h<hmin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r4::data::hmax12)  { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, x(p,h) with h>hmax in range: " + std::to_string(filib::sup(y))); }
				// x(p,h) is monotonically increasing in h, but not necessarily monotonic in p

				double xLower;	// the lower bound is attained at h^L, but an unkown value of p
				if ((filib::inf(y)<=r4::data::hmaxDx12hpdpLt0)||(filib::sup(x)<=r4::data::pmaxDx12hpdpLt0)) {	// if enthalpy or pressure are low enough, x(p,h) is decreasing in p
					xLower = r4::get_x_ph_12(filib::sup(x),filib::inf(y));
				} else {
					const double hliqpU = r4::get_hliq_p_12(filib::sup(x));
					const double hvappU = r4::get_hvap_p_12(filib::sup(x));
					const double dhliqdppU = r4::derivatives::get_dhliq_dp_12(filib::sup(x));
					const double dhvapdppU = r4::derivatives::get_dhvap_dp_12(filib::sup(x));
					const double numeratorDxDpAtpU = hliqpU*dhvapdppU-hvappU*dhliqdppU-filib::inf(y)*(dhvapdppU-dhliqdppU);
					if (numeratorDxDpAtpU<=0) {	// the function is componentwise convex here; if dxdp<=0 at pU, it is <=0 everywhere
						xLower = r4::get_x_ph_12(filib::sup(x),filib::inf(y));
					} else {
						const double hliqpL = r4::get_hliq_p_12(filib::inf(x));
						const double hvappL = r4::get_hvap_p_12(filib::inf(x));
						const double dhliqdppL = r4::derivatives::get_dhliq_dp_12(filib::inf(x));
						const double dhvapdppL = r4::derivatives::get_dhvap_dp_12(filib::inf(x));
						const double numeratorDxDpAtpL = hliqpL*dhvapdppL-hvappL*dhliqdppL-filib::inf(y)*(dhvapdppL-dhliqdppL);
						if (numeratorDxDpAtpL>=0) {	// the function is componentwise convex here; if dxdp>=0 at pL, it is >=0 everywhere
							xLower = r4::get_x_ph_12(filib::inf(x),filib::inf(y));
						} else {
							interval<N,K,E> hliq = iapws(x,411);
							interval<N,K,E> hvap = iapws(x,413);
							interval<N,K,E> hlowerInterval =(filib::inf(y)-hliq)/(hvap-hliq);
							xLower = std::max( filib::inf(hlowerInterval),
											   r4::get_x_ph_12(filib::sup(x),r4::data::hmaxDx12hpdpLt0) );
						}
					}
				}

				double xUpper;	// the lower bound is attained at h^U, but an unkown value of p
				if ((filib::sup(y)<=r4::data::hmaxDx12hpdpLt0)||(filib::sup(x)<=r4::data::pmaxDx12hpdpLt0)) {	// if enthalpy or pressure are low enough, x(p,h) is decreasing in p
					xUpper = r4::get_x_ph_12(filib::inf(x),filib::sup(y));
				}
				else {
					// In this region, the function is componentwise convex w.r.t. p at hU --> maximum is at a corner
					xUpper = std::max( r4::get_x_ph_12(filib::inf(x),filib::sup(y)),
									   r4::get_x_ph_12(filib::sup(x),filib::sup(y))  );
				}

				return interval<N,K,E>(	xLower, xUpper );
			}
			case 48: 	// region 4-1/2, x(p,s)
			{
				if (filib::inf(y)<r4::data::smin12) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, x(p,s) with s<smin in range: " + std::to_string(filib::inf(y))); }
				if (filib::sup(y)>r4::data::smax12) 	 { throw std::runtime_error("mc::Filib\t IAPWS-IF97, region 4-1/2, x(p,s) with s>smax in range: " + std::to_string(filib::sup(y))); }
				interval<N,K,E> sliq = iapws(x,415);	// region 4-1/2, sliq(p)
				interval<N,K,E> svap = iapws(x,417);	// region 4-1/2, svap(p)				
				return interval<N,K,E>(	std::max( std::min(filib::inf((filib::inf(y)-sliq)/max(svap-sliq,interval<N,K,E>(r4::data::mindeltasvap12))), 1.) ,0.),
										std::max( std::min(filib::sup((filib::sup(y)-sliq)/max(svap-sliq,interval<N,K,E>(r4::data::mindeltasvap12))), 1.) ,0.) );	// function is increasing in y(=s)
			}
			case 49: 	// region 4-1/2, h(p,s)
			{
				return iapws(x,iapws(x,y,48),43);	// h(p,x(p,s))
			}
			case 410:	// region 4-1/2, s(p,h)
			{
				return iapws(x,iapws(x,y,47),45);	// s(p,x(p,h))
			}
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
				throw std::runtime_error("\nmc::Filib\t IAPWS called with two arguments but a 1d type (" + std::to_string((int)type) + ")");
			default:
				throw std::runtime_error("\nmc::Filib\t IAPWS called with unkown type (" + std::to_string((int)type) + ").");
		}

	}


} // end namespace filib
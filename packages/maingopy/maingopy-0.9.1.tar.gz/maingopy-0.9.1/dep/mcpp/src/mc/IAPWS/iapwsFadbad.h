/**
 * @file iapwsFadbad.h
 * 
 * @brief File containing implementation of derivatives for the extended IAPWS-IF97 model in FILIB++ (within MC++).
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

#include "fadiff.h"

#include "iapws.h"


namespace iapws_if97 {
	
	
	namespace region2 {


		namespace auxiliary {
			
			
			template <typename U, unsigned int N>
			INLINE2 fadbad::FTypeName<U,N> plim_T(const fadbad::FTypeName<U,N>& T) {
				fadbad::FTypeName<U,N> plim;
				if (fadbad::Op<U>::myLe(T.val(),data::Tplim)) {
					plim = region4::original::get_ps_T(T);
				} else {
					plim = data::aPlim + data::bPlim*T + data::cPlim*pow(T,2) + data::dPlim*pow(T,3);	
				}
				return plim;
			}
			
			template <typename U, unsigned int N>
			INLINE2 fadbad::FTypeName<U,N> Tlim_p(const fadbad::FTypeName<U,N>& p) {
				fadbad::FTypeName<U,N> Tlim;
				if (fadbad::Op<U>::myLe(p.val(),data::pminB23)) {
					Tlim = region4::original::get_Ts_p(p);
				} else {
					Tlim = data::aTlim + data::bTlim*p + data::cTlim*pow(p,2) + data::dTlim*pow(p,3);	
				}
				return Tlim;
			}
			
			template <typename U, unsigned int N>
			INLINE2 fadbad::FTypeName<U,N> hlim_p(const fadbad::FTypeName<U,N>& p) {
				fadbad::FTypeName<U,N> hlim;
				if (fadbad::Op<U>::myLe(p.val(),data::pminB23)) {
					hlim = original::get_h_pT(p,region4::original::get_Ts_p(p));
				} else {
					hlim = data::aHlim + data::bHlim*p + data::cHlim*pow(p,2) + data::dHlim*exp(-pow((p-data::eHlim)/data::fHlim,2));
				}
				return hlim;
			}
			
			
		}	// end namespace auxiliary
	
	
	}	// end namespace region2	


}	// end namespace iapws_if97


namespace fadbad {

	// 1d functions of IAPWS-IF97 model
	template <typename T, unsigned int N>
	INLINE2 FTypeName<T,N> iapws(const FTypeName<T,N>& x, const double type)
	{
		namespace r1 = iapws_if97::region1;
		namespace r2 = iapws_if97::region2;
		namespace r4 = iapws_if97::region4;
		
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
				throw std::runtime_error("mc::Fadbad\t IAPWS called with one argument but a 2d type (" + std::to_string((int)type) + ")");
			case 29:	// region 2, boundary to 3, p(T)
			{
				if(Op<T>::myGe(x.val(), r2::data::TB23hat)){ 
					return r2::original::get_b23_p_T(x);
				} else {
					return r2::data::pB23hat + r2::data::kTB23*(x - r2::data::TB23hat);
				}
			}
			case 210:	// region 2, boundary to 3, T(p)
			{
				if(Op<T>::myGe(x.val(), r2::data::pB23hat)){ 
					return r2::original::get_b23_T_p(x);
				} else {
					return r2::data::TB23hat + (x - r2::data::pB23hat)/r2::data::kTB23;
				}
			}
			case 211:	// region 2, boundary 2b/2c, p(h) 
			{
				if(Op<T>::myGe(x.val(), r2::data::hminB2bc)){ 
					return r2::original::get_b2bc_p_h(x);
				} else {
					return r2::data::pmin + (x-r2::data::hmin)/r2::data::khB2bc;
				}
			}
			case 212:	// region 2, boundary 2b/2c, h(p)
			{
				if(Op<T>::myGe(x.val(), r2::data::pminB2bc)){ 
					return r2::original::get_b2bc_h_p(x);
				} else {
					return r2::data::hmin + r2::data::khB2bc*(x-r2::data::pmin);
				}
			}
			case 41:	// region 4, p(T)
			{
				if(Op<T>::myLe(x.val(), r4::data::Tcrit)){ 
					return r4::original::get_ps_T(x);
				} else {
					return r4::data::psExtrA + r4::data::psExtrB*x + r4::data::psExtrC*pow(x,2);
				}
			}
			case 42:	// region 4, T(p)
			{
				if(Op<T>::myLe(x.val(), r4::data::pcrit)){ 
					return r4::original::get_Ts_p(x);
				} else {
					return -r4::data::psExtrB/(2.*r4::data::psExtrC) + sqrt( std::pow(r4::data::psExtrB/(2.*r4::data::psExtrC),2) + (x-r4::data::psExtrA)/r4::data::psExtrC );
				}
			}
			case 411:	return r4::get_hliq_p_12(x);	// region 4-1/2, hliq(p)
			case 412:	return r4::get_hliq_T_12(x);	// region 4-1/2, hliq(T)
			case 413:	return r4::get_hvap_p_12(x);	// region 4-1/2, hvap(p)
			case 414:	return r4::get_hvap_T_12(x);	// region 4-1/2, hvap(T)
			case 415:	return r4::get_sliq_p_12(x);	// region 4-1/2, sliq(p)
			case 416:	return r4::get_sliq_T_12(x);	// region 4-1/2, sliq(T)
			case 417:	return r4::get_svap_p_12(x);	// region 4-1/2, svap(p)
			case 418:	return r4::get_svap_T_12(x);	// region 4-1/2, svap(T)
			default:
				throw std::runtime_error("mc::Fadbad\t IAPWS called with unkown type (" + std::to_string((int)type) + ").");
		} 
	}
	
	
	// 2d functions of IAPWS-IF97 model
	template <typename T, unsigned int N>
	INLINE2 FTypeName<T,N> iapws(const FTypeName<T,N>& x, const FTypeName<T,N>& y, const double type)
	{
		namespace r1 = iapws_if97::region1;
		namespace r2 = iapws_if97::region2;
		namespace r4 = iapws_if97::region4;
		
		switch((int)type){
			// 2d functions:
			case 11:	// region 1, h(p,T)
			{
				const FTypeName<T,N> psat = r4::original::get_ps_T(y);
				if (Op<T>::myGe(x.val(), psat.val())) {
					const FTypeName<T,N> h = r1::original::get_h_pT(x,y); 
					return min(h,(decltype(h))r1::data::hmax);
				} else { 
					const FTypeName<T,N> h = r1::original::get_h_pT(psat,y) + r1::original::derivatives::get_dh_pT_dp(psat,y)*(x-psat); ; 
					return min(h,(decltype(h))r1::data::hmax);
				}		
			}
			case 12:	// region 1, s(p,T)
			{
				const FTypeName<T,N> psat = r4::original::get_ps_T(y);
				if (Op<T>::myGe(x.val(), psat.val())) {
					const FTypeName<T,N> s = r1::original::get_s_pT(x,y); 
					return min(s,(decltype(s))r1::data::smax);
				} else { 
					const FTypeName<T,N> s = r1::original::get_s_pT(psat,y) + r1::original::derivatives::get_ds_pT_dp(psat,y)*(x-psat); ; 
					return min(s,(decltype(s))r1::data::smax);
				}		
			}
			case 13:	// region 1, T(p,h)
			{
				if (Op<T>::myGe(x.val(), r2::data::pminB23)) {
					const FTypeName<T,N> t = r1::original::get_T_ph(x,y);
					return max(min(t,(decltype(t))r1::data::Tmax),(decltype(t))r1::data::Tmin);
				} else {
					const FTypeName<T,N> hmax = r1::original::get_h_pT(x,r4::original::get_Ts_p(x));
					if (Op<T>::myLe(y.val(),hmax.val())) {
						const FTypeName<T,N> t = r1::original::get_T_ph(x,y);
						return max(min(t,(decltype(t))r1::data::Tmax),(decltype(t))r1::data::Tmin);
					} else {
						const FTypeName<T,N> t = r4::original::get_Ts_p(x) + 0.1*(y-hmax);
						return max(min(t,(decltype(t))r1::data::Tmax),(decltype(t))r1::data::Tmin);
					}
				}
			}
			case 14:	// region 1, T(p,s)
			{
				return r1::get_T_ps(x,y); 	// calling the version that already contains the max/min (not the original one!)	
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
				const FTypeName<T,N> plim = r2::auxiliary::plim_T(y);
				if (Op<T>::myLe(x.val(), plim.val())) {
					const FTypeName<T,N> h =  r2::original::get_h_pT(x,y);
					return max(h,(decltype(h))r2::data::hmin);
				} else {
					const FTypeName<T,N> h =  r2::original::get_h_pT(plim,y) - (-59.+1.25*y/(sqrt(plim)))*(x-plim);
					return max(h,(decltype(h))r2::data::hmin);
				}					
			}
			case 22:	// region 2, s(p,T)
			{
				const FTypeName<T,N> Tlim = r2::auxiliary::Tlim_p(x);
				if (Op<T>::myGe(y.val(), Tlim.val())) {
					const FTypeName<T,N> s = r2::original::get_s_pT(x,y);
					return max(s,(decltype(s))r2::data::smin);
				} else {
					const FTypeName<T,N> s = r2::original::get_s_pT(x,Tlim) + 0.003*(y-Tlim);
					return max(s,(decltype(s))r2::data::smin);
				}					
			}
			case 23:	// region 2, T(p,h)
			{
				const FTypeName<T,N> hlim = r2::auxiliary::hlim_p(x);
				if ( Op<T>::myLe(x.val(), r2::data::pminB) ) {		// could be in 2a or 4/1
					if ( Op<T>::myGe(y.val(),hlim.val()) ) {
						const auto t = r2::original::get_T_ph_a(x,y);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					} else {
						const auto t =  r2::original::get_T_ph_a(x,hlim) + r2::original::derivatives::get_dT_ph_dh_a(x,hlim)*(y-hlim);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					}
				} 
				else if ( Op<T>::myLe(x.val(), r2::data::pminC) ) {	// could be in 2b or 4-1/2
					if ( Op<T>::myGe(y.val(),hlim.val()) ) {
						const auto t = r2::original::get_T_ph_b(x,y);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					} else {
						const auto t =  r2::original::get_T_ph_b(x,hlim) + r2::original::derivatives::get_dT_ph_dh_b(x,hlim)*(y-hlim);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					}
				} 
				else {											// could be in 2b, 2c, 3 or 4-1/2
					const auto hlimB2bc = r2::original::get_b2bc_h_p(x);
					if ( Op<T>::myGe(y.val(), hlimB2bc.val()) ) {
						const auto t = r2::original::get_T_ph_b(x,y);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					} else {
						if ( Op<T>::myGe(y.val(),hlim.val()) ) {
							const auto t = r2::original::get_T_ph_c(x,y);
							return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
						} else {
							const auto t = r2::original::get_T_ph_c(x,hlim) + r2::original::derivatives::get_dT_ph_dh_c(x,hlim)*(y-hlim);
							return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
						}
					}
				}
			}
			case 24:	// region 2, T(p,s)
			{
				const FTypeName<T,N> supper = r2::original::get_s_pT(x,r2::data::Tmax);
				const FTypeName<T,N> Ts = r4::original::get_Ts_p(min(x,(decltype(x))r4::data::pcrit));
				const FTypeName<T,N> slower = r2::original::get_s_pT(x,Ts);
				if (Op<T>::myLe(x.val(),r2::data::pminB)) {			// could be in 2a, below, or above
					if (Op<T>::myLt(y.val(),slower.val())) { 
						const FTypeName<T,N> slim = slower;
						const FTypeName<T,N> t = r2::original::get_T_ps_a(x,slim) + r2::original::derivatives::get_dT_ps_ds_a(x,slim)*(y-slim);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					} else if (Op<T>::myGt(y.val(),supper.val())) {
						const FTypeName<T,N> f = 165. - 0.125*(x-r2::data::pmin);
						const FTypeName<T,N> slim = supper;
						const FTypeName<T,N> t = r2::original::get_T_ps_a(x,slim) + r2::original::derivatives::get_dT_ps_ds_a(x,slim)*(y-slim) + f*pow(y-slim,2);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					} else {
						const FTypeName<T,N> t = r2::original::get_T_ps_a(x,y);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					}
				}
				else if (Op<T>::myLe(x.val(),r2::data::pminC)) {	// could be in 2b, below, or above
					if (Op<T>::myLt(y.val(),slower.val())) { 
						const FTypeName<T,N> slim = slower;
						const FTypeName<T,N> t = r2::original::get_T_ps_b(x,slim) + r2::original::derivatives::get_dT_ps_ds_b(x,slim)*(y-slim);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					} else if (Op<T>::myGt(y.val(),supper.val())) {
						const FTypeName<T,N> f = 165. - 0.125*(x-r2::data::pmin);
						const FTypeName<T,N> slim = supper;
						const FTypeName<T,N> t = r2::original::get_T_ps_b(x,slim) + r2::original::derivatives::get_dT_ps_ds_b(x,slim)*(y-slim) + f*pow(y-slim,2);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					} else {
						const FTypeName<T,N> t = r2::original::get_T_ps_b(x,y);
						return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
					}
				}
				else {									// could be in 2b, above, 2c, or below
					if (Op<T>::myLe(y.val(),r2::data::smaxC)) {	// could be in 2c or below
						if (Op<T>::myLt(y.val(),slower.val())) {
							const FTypeName<T,N> slim = slower;
							const FTypeName<T,N> t = r2::original::get_T_ps_c(x,slim) + r2::original::derivatives::get_dT_ps_ds_c(x,slim)*(y-slim);
							return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
						} else {
							const FTypeName<T,N> t = r2::original::get_T_ps_c(x,y);
							return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
						}
					} else {							// could be in 2b or above
						if (Op<T>::myGt(y.val(),supper.val())) {
							const FTypeName<T,N> f = 165. - 0.125*(x-r2::data::pmin);
							const FTypeName<T,N> slim = supper;
							const FTypeName<T,N> t = r2::original::get_T_ps_b(x,slim) + r2::original::derivatives::get_dT_ps_ds_b(x,slim)*(y-slim) + f*pow(y-slim,2);
							return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
						} else {
							const FTypeName<T,N> t = r2::original::get_T_ps_b(x,y);
							return max(min(t,(decltype(t))r2::data::Tmax),(decltype(t))r2::data::Tmin);
						}
					} 
				}
			}
			case 25:	// region 2, h(p,s)
			{
				const FTypeName<T,N> sliq(r4::get_sliq_p_12(x));
				const FTypeName<T,N> hliq(r4::get_hliq_p_12(x));
				FTypeName<T,N> h;
				if (Op<T>::myGe(y.val(),sliq.val())) {
					const FTypeName<T,N> svap(r4::get_svap_p_12(x));
					const FTypeName<T,N> myx = (y-sliq)/(svap-sliq);
					const FTypeName<T,N> hvap(r4::get_hvap_p_12(x));
					h = myx*hliq + (1-myx)*hvap;
				} else {
					h = hliq;
				}
				return min(h,(decltype(h))r4::data::hmax12);
			}
			case 26:	// region 2, s(p,h)
			{
				return iapws(x,iapws(x,y,23),22);	// s(p,T(p,h))
			}
			case 43:	return r4::get_h_px_12(x,y); 	// region 4-1/2, h(p,x) 
			case 44:	return r4::get_h_Tx_12(x,y); 	// region 4-1/2, h(T,x)
			case 45:	return r4::get_s_px_12(x,y); 	// region 4-1/2, s(p,x)
			case 46:	return r4::get_s_Tx_12(x,y); 	// region 4-1/2, s(T,x)
			case 47:	return r4::get_x_ph_12(x,y);	// region 4-1/2, x(p,h)
			case 48:	return r4::get_x_ps_12(x,y); 	// region 4-1/2, x(p,s)
			case 49:	return r4::get_h_ps_12(x,y); 	// region 4-1/2, h(p,s)
			case 410: 	return r4::get_s_ph_12(x,y); 	// region 4-1/2, s(p,h)
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

	
} // end namespace fadbad

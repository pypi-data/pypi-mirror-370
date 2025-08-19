/**
 * @file iapwsInverse.h
 *
 * @brief File containing implementation of inverse functions of the functions in IAPWS-IF97 model in MC++ for the purpose of constraint propagation.
 *
 * Original model: Wagner, W.; Cooper, J. R.; Dittmann, A.; Kijima, J.; Kretzschmar, H.-J.; Kruse, A.; Mareš, R.; Oguchi, K.; Sato, H.; Stocker, I.; Sifner, O.; Takaishi, Y.; Tanishita, I.; Trubenbach, J. & Willkommen, T.:
 *                 The IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam. Journal of Engineering for Gas Turbines and Power -- Transactions of the ASME, 2000, 122, 150-182.
 *
 * Revised model used for this implementation: Revised Release on the IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam.
 *                                             The International Association for the Properties of Water and Steam, Technical Report IAPWS R7-97(2012), 2012. http://www.iapws.org/relguide/IF97-Rev.html.
 *
 * ==============================================================================\n
 * © Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
 * ==============================================================================\n
 *
 * @author Dominik Bongartz, Jaromil Najman, Alexander Mitsos
 * @date 27.08.2019
 *
 */

#pragma once

#include "iapws.h"


namespace mc {
	

	// 1d functions of IAPWS-IF97 model
	inline void 
	_compute_inverse_interval_iapws
	(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, const double type)
	{
		
		namespace r2 = iapws_if97::region2;
		namespace r4 = iapws_if97::region4;
		
		switch((int)type){
			case 11:		// region 1, h(p,T)
			case 12:		// region 1, s(p,T)
			case 13:		// region 1, T(p,h)
			case 14:		// region 1, T(p,s)
			case 15:		// region 1, h(p,s)
			case 16:		// region 1, s(p,h)
			case 21:		// region 2, h(p,T)
			case 22:		// region 2, s(p,T)
			case 23:		// region 2, T(p,h)
			case 24:		// region 2, T(p,s)
			case 25:		// region 2, h(p,s)
			case 26:		// region 2, s(p,h)
			case 43:		// region 4-1/2, h(p,x)
			case 44:		// region 4-1/2, h(T,x)
			case 45:		// region 4-1/2, s(p,x)
			case 46:		// region 4-1/2, s(T,x)
			case 47:		// region 4-1/2, x(p,h)
			case 48:		// region 4-1/2, x(p,s)
			case 49:		// region 4-1/2, h(p,s)
			case 410:	// region 4-1/2, s(p,h)
				throw std::runtime_error("\nmc::McCormick\t IAPWS inverse called with one argument but a 2d type (" + std::to_string((int)type) + ")");
			case 29:		// region 2, boundary to 3, p(T)
			{
				xL = r2::get_b23_T_p(bwdLowerBound);
				xU = r2::get_b23_T_p(bwdUpperBound);
				break;
			}
			case 210:	// region 2, boundary to 3, T(p)
			{
				xL = r2::get_b23_p_T(bwdLowerBound);
				xU = r2::get_b23_p_T(bwdUpperBound);
				break;
			}
			case 211:	// region 2, boundary 2b/2c, p(h)
			{
				xL = r2::get_b2bc_h_p(bwdLowerBound);
				xU = r2::get_b2bc_h_p(bwdUpperBound);
				break;
			}
			case 212:	// region 2, boundary 2b/2c, h(p)
			{
				xL = r2::get_b2bc_p_h(bwdLowerBound);
				xU = r2::get_b2bc_p_h(bwdUpperBound);
				break;
			}
			case 41:		// region 4, p(T)
			{
				xL = r4::get_Ts_p(bwdLowerBound);
				xU = r4::get_Ts_p(bwdUpperBound);
				break;
			}
			case 42:		// region 4, T(p)
			{
				xL = r4::get_ps_T(bwdLowerBound);
				xU = r4::get_ps_T(bwdUpperBound);
				break; 
			}
			case 411:	// region 4-1/2, hliq(p)
			{
				double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_hliq_p_12(x) - rusr[0]; };
				double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dhliq_dp_12(x); };
				double rusr = bwdLowerBound;
				xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				rusr = bwdUpperBound;
				xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				break;
			}
			case 412:	// region 4-1/2, hliq(T)
			{
				double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_hliq_T_12(x) - rusr[0]; };
				double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dhliq_dT_12(x); };
				double rusr = bwdLowerBound;
				xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				rusr = bwdUpperBound;
				xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				break;
			}
			case 413:	// return iapws_if97::region4::get_hvap_p_12(x);	// region 4-1/2, hvap(p)
			{
				if (fwdUpperBound<r4::data::pmaxhvap12) {	// monotonically increasing
					double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_hvap_p_12(x) - rusr[0]; };
					double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dhvap_dp_12(x); };
					double rusr = bwdLowerBound;
					xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
					rusr = bwdUpperBound;
					xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				} else if (fwdLowerBound>r4::data::pmaxhvap12) {	// monotonically decreasing
					double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_hvap_p_12(x) - rusr[0]; };
					double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dhvap_dp_12(x); };
					double rusr = bwdUpperBound;
					xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
					rusr = bwdLowerBound;
					xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				} else {	// no monotonicity, doing nothing
					xL = fwdLowerBound;
					xU = fwdUpperBound;
				}
				break;
			}
			case 414:	// return iapws_if97::region4::get_hvap_T_12(x);	// region 4-1/2, hvap(T)
			{
				if (fwdUpperBound<r4::data::Tmaxhvap12) {	// monotonically increasing
					double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_hvap_T_12(x) - rusr[0]; };
					double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dhvap_dT_12(x); };
					double rusr = bwdLowerBound;
					xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
					rusr = bwdUpperBound;
					xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				} else if (fwdLowerBound>r4::data::Tmaxhvap12) {	// monotonically decreasing
					double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_hvap_p_12(x) - rusr[0]; };
					double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dhvap_dp_12(x); };
					double rusr = bwdUpperBound;
					xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
					rusr = bwdLowerBound;
					xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				} else {	// no monotonicity, doing nothing
					xL = fwdLowerBound;
					xU = fwdUpperBound;
				}
				break;
			}
			case 415:	// region 4-1/2, sliq(p)
			{
				double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_sliq_p_12(x) - rusr[0]; };
				double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dsliq_dp_12(x); };
				double rusr = bwdLowerBound;
				xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				rusr = bwdUpperBound;
				xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				break;
			}
			case 416:	// region 4-1/2, sliq(T)
			{
				double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_sliq_T_12(x) - rusr[0]; };
				double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dsliq_dT_12(x); };
				double rusr = bwdLowerBound;
				xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				rusr = bwdUpperBound;
				xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				break;
			}
			case 417:	// region 4-1/2, svap(p)
			{
				double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_svap_p_12(x) - rusr[0]; };
				double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dsvap_dp_12(x); };
				double rusr = bwdUpperBound;
				xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				rusr = bwdLowerBound;
				xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				break;
			}
			case 418:	// region 4-1/2, svap(T)
			{
				double (*myfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::get_svap_T_12(x) - rusr[0]; };
				double (*mydfunc)(const double,const double*,const int*) = [](const double x, const double*rusr, const int* iusr){ return r4::derivatives::get_dsvap_dT_12(x); };
				double rusr = bwdUpperBound;
				xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				rusr = bwdLowerBound;
				xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, myfunc, mydfunc, &rusr);
				break;
			}
			default:
				throw std::runtime_error("\nmc::McCormick\t IAPWS inverse called with unkown type (" + std::to_string((int)type) + ").");
		}
		
	}


} // end namespace mc
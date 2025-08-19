// Copyright (C) 2009-2017 Benoit Chachuat, Imperial College London.
// All Rights Reserved.
// This code is published under the Eclipse Public License.

#ifndef MC__MCOP_HPP
#define MC__MCOP_HPP

#include <stdexcept>
#include <vector>

namespace mc
{

//! @brief C++ structure to allow usage of MC++ types for DAG evaluation and as template parameters in other MC++ types.
template <typename T> struct Op
{
  static T point( const double c ) { return T(c); } // { throw std::runtime_error("mc::Op<T>::point -- Function not overloaded"); }
  static T zeroone() { return T(0,1); }
  static void I(T& x, const T& y) { x = y; }
  static double l(const T& x) { return x.l(); }
  static double u(const T& x) { return x.u(); }
  static double abs (const T& x) { return abs(x);  }
  static double mid (const T& x) { return mid(x);  }
  static double diam(const T& x) { return diam(x); }
  static T inv (const T& x) { return inv(x);  }
  static T sqr (const T& x) { return sqr(x);  }
  static T sqrt(const T& x) { return sqrt(x); }
  static T exp (const T& x) { return exp(x);  }
  static T log (const T& x) { return log(x);  }
  static T xlog(const T& x) { return xlog(x); }
  static T fabsx_times_x(const T& x) { return fabsx_times_x(x); }
  static T xexpax(const T& x, const double a) { return xexpax(x,a); }
  static T centerline_deficit(const T& x, const double xLim, const double type) { return centerline_deficit(x,xLim,type); }
  static T wake_profile(const T& x, const double type) { return wake_profile(x,type); }
  static T wake_deficit(const T& x, const T& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static T power_curve(const T& x, const double type) { return power_curve(x,type); }
  static T lmtd(const T& x,const T& y) { return lmtd(x,y); }
  static T rlmtd(const T& x,const T& y) { return rlmtd(x,y); }
  static T mid(const T& x, const T& y, const double k) { return mid(x, y, k); }
  static T pinch(const T& Th, const T& Tc, const T& Tp) { return pinch(Th, Tc, Tp); } 
  static T euclidean_norm_2d(const T& x,const T& y) { return euclidean_norm_2d(x,y); }
  static T expx_times_y(const T& x,const T& y) { return expx_times_y(x,y); }
  static T vapor_pressure(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
							const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10); }
  static T ideal_gas_enthalpy(const T& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							  const double p7 = 0) { return ideal_gas_enthalpy(x,x0,type,p1,p2,p3,p4,p5,p6,p7);}
  static T saturation_temperature(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
								  const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}
  static T enthalpy_of_vaporization(const T& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { return enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6); }
  static T cost_function(const T& x, const double type, const double p1, const double p2, const double p3) { return cost_function(x,type,p1,p2,p3); }
  static T sum_div(const std::vector<T> &x, const std::vector<double> &coeff) { return sum_div(x,coeff); }
  static T xlog_sum(const std::vector<T> &x, const std::vector<double> &coeff) { return xlog_sum(x,coeff); }
  static T nrtl_tau(const T& x, const double a, const double b, const double e, const double f) { return nrtl_tau(x,a,b,e,f); }
  static T nrtl_dtau(const T& x, const double b, const double e, const double f) { return nrtl_dtau(x,b,e,f); }
  static T nrtl_G(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return nrtl_G(x,a,b,e,f,alpha); }
  static T nrtl_Gtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return nrtl_Gtau(x,a,b,e,f,alpha); }
  static T nrtl_Gdtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return nrtl_Gdtau(x,a,b,e,f,alpha); }
  static T nrtl_dGtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return nrtl_dGtau(x,a,b,e,f,alpha); }
  static T iapws(const T& x, const double type) { return iapws(x,type); }
  static T iapws(const T& x, const T& y, const double type) { return iapws(x,y,type); }
  static T p_sat_ethanol_schroeder(const T& x) { return p_sat_ethanol_schroeder(x); }
  static T rho_vap_sat_ethanol_schroeder(const T& x) { return rho_vap_sat_ethanol_schroeder(x); }
  static T rho_liq_sat_ethanol_schroeder(const T& x) { return rho_liq_sat_ethanol_schroeder(x); }
  static T covariance_function(const T& x, const double type) { return covariance_function(x,type); }
  static T acquisition_function(const T& x, const T& y, const double type, const double fmin) { return acquisition_function(x,y,type,fmin); }
  static T gaussian_probability_density_function(const T& x) { return gaussian_probability_density_function(x); }
  static T regnormal(const T& x, const double a, const double b) { return regnormal(x,a,b); }
  static T fabs(const T& x) { return fabs(x); }
  static T sin (const T& x) { return sin(x);  }
  static T cos (const T& x) { return cos(x);  }
  static T tan (const T& x) { return tan(x);  }
  static T asin(const T& x) { return asin(x); }
  static T acos(const T& x) { return acos(x); }
  static T atan(const T& x) { return atan(x); }
  static T sinh(const T& x) { return sinh(x); }
  static T cosh(const T& x) { return cosh(x); }
  static T tanh(const T& x) { return tanh(x); }
  static T coth(const T& x) { return coth(x); }
  static T asinh(const T& x) { return asinh(x); }
  static T acosh(const T& x) { return acosh(x); }
  static T atanh(const T& x) { return atanh(x); }
  static T acoth(const T& x) { return acoth(x); }
  static T erf (const T& x) { return erf(x);  }
  static T erfc(const T& x) { return erfc(x); }
  static T fstep(const T& x) { return fstep(x); }
  static T bstep(const T& x) { return bstep(x); }
  static T hull(const T& x, const T& y) { return hull(x,y); }
  static T min (const T& x, const T& y) { return min(x,y);  }
  static T max (const T& x, const T& y) { return max(x,y);  }
  static T pos (const T& x) { return pos(x);  }
  static T neg (const T& x) { return neg(x);  }
  static T lb_func (const T& x, const double lb) { return lb_func(x,lb);  }
  static T ub_func (const T& x, const double ub) { return ub_func(x,ub);  }
  static T bounding_func (const T& x, const double lb, const double ub) { return bounding_func(x,lb,ub);  }
  static T squash_node (const T& x, const double lb, const double ub) { return squash_node(x,lb,ub);  }
  static T single_neuron(const std::vector<T> &x, const std::vector<double> &w, const double b, const int type) { return single_neuron(x,w,b,type); }
  static T mc_print (const T& x, const int number) { return mc_print(x,number); }
  static T arh (const T& x, const double k) { return arh(x,k); }
  template <typename X, typename Y> static T pow(const X& x, const Y& y) { return pow(x,y); }
  static T cheb (const T& x, const unsigned n) { return cheb(x,n); }
  static T prod (const unsigned n, const T* x) { return prod(n,x); }
  static T monom (const unsigned n, const T* x, const unsigned* k) { return monom(n,x,k); }
  static bool inter(T& xIy, const T& x, const T& y) { return inter(xIy,x,y); }
  static bool eq(const T& x, const T& y) { return x==y; }
  static bool ne(const T& x, const T& y) { return x!=y; }
  static bool lt(const T& x, const T& y) { return x<y;  }
  static bool le(const T& x, const T& y) { return x<=y; }
  static bool gt(const T& x, const T& y) { return x>y;  }
  static bool ge(const T& x, const T& y) { return x>=y; }
};

}

#include <cmath>
#include "mcfunc.hpp"

namespace mc
{

//! @brief Specialization of the structure mc::Op to allow usage of doubles as a template parameter
template <> struct Op< double >
{
  static double point( const double c ) { return c; }
  static double zeroone() { throw std::runtime_error("mc::Op<double>::zeroone -- function not overloaded"); }
  static void I(double& x, const double& y) { x = y; }
  static double l(const double& x) { return x; }
  static double u(const double& x) { return x; }
  static double abs (const double& x) { return std::fabs(x);  }
  static double mid (const double& x) { return x;  }
  static double diam(const double& x) { return 0.; }
  static double inv (const double& x) { return mc::inv(x);  }
  static double sqr (const double& x) { return mc::sqr(x);  }
  static double sqrt(const double& x) { return std::sqrt(x); }
  static double exp (const double& x) { return std::exp(x);  }
  static double log (const double& x) { return std::log(x);  }
  static double xlog(const double& x) { return mc::xlog(x); }
  static double fabsx_times_x(const double& x) { return mc::fabsx_times_x(x); }
  static double xexpax(const double& x, const double a) { return mc::xexpax(x,a); }
  static double centerline_deficit(const double& x, const double xLim, const double type) { return mc::centerline_deficit(x,xLim,type); }
  static double wake_profile(const double& x, const double type) { return mc::wake_profile(x,type); }
  static double wake_deficit(const double& x, const double& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return mc::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static double power_curve(const double& x, const double type) { return mc::power_curve(x,type); }
  static double lmtd(const double& x,const double& y) { return mc::lmtd(x,y); }
  static double rlmtd(const double& x,const double& y) { return mc::rlmtd(x,y); }
  static double mid(const double& x, const double& y, const double k) { return mc::mid(x, y, k); }  
  static double pinch(const double& Th, const double& Tc, const double& Tp) { return mc::pinch(Th, Tc, Tp); }
  static double euclidean_norm_2d(const double& x,const double& y) { return mc::euclidean_norm_2d(x,y); }
  static double expx_times_y(const double& x,const double& y) { return mc::expx_times_y(x,y); }
  static double vapor_pressure(const double& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
								const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return mc::vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10); }
  static double ideal_gas_enthalpy(const double& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
								   const double p7 = 0) { return mc::ideal_gas_enthalpy(x,x0,type,p1,p2,p3,p4,p5,p6,p7); }
  static double saturation_temperature(const double& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
									   const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return mc::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}
  static double enthalpy_of_vaporization(const double& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { return mc::enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6); }
  static double cost_function(const double& x, const double type, const double p1, const double p2, const double p3) { return mc::cost_function(x,type,p1,p2,p3); }
  static double sum_div(const std::vector<double> &x, const std::vector<double> &coeff) { return mc::sum_div(x,coeff); }
  static double xlog_sum(const std::vector<double> &x, const std::vector<double> &coeff) { return mc::xlog_sum(x,coeff); }
  static double nrtl_tau(const double& x, const double a, const double b, const double e, const double f) { return mc::nrtl_tau(x,a,b,e,f); }
  static double nrtl_dtau(const double& x, const double b, const double e, const double f) { return mc::nrtl_dtau(x,b,e,f); }
  static double nrtl_G(const double& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_G(x,a,b,e,f,alpha); }
  static double nrtl_Gtau(const double& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_Gtau(x,a,b,e,f,alpha); }
  static double nrtl_Gdtau(const double& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_Gdtau(x,a,b,e,f,alpha); }
  static double nrtl_dGtau(const double& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_dGtau(x,a,b,e,f,alpha); }
  static double iapws(const double& x, const double type) { return mc::iapws(x,type); }
  static double iapws(const double& x, const double& y, const double type) { return mc::iapws(x,y,type); }
  static double p_sat_ethanol_schroeder(const double& x) { return mc::p_sat_ethanol_schroeder(x); }
  static double rho_vap_sat_ethanol_schroeder(const double& x) { return mc::rho_vap_sat_ethanol_schroeder(x); }
  static double rho_liq_sat_ethanol_schroeder(const double& x) { return mc::rho_liq_sat_ethanol_schroeder(x); }
  static double covariance_function(const double& x, const double type) { return mc::covariance_function(x,type); }
  static double acquisition_function(const double& x, const double& y, const double type, const double fmin) { return mc::acquisition_function(x,y,type,fmin); }
  static double gaussian_probability_density_function(const double& x) { return mc::gaussian_probability_density_function(x); }
  static double regnormal(const double& x, const double a, const double b) { return mc::regnormal(x,a,b); }
  static double fabs(const double& x) { return std::fabs(x); }
  static double sin (const double& x) { return std::sin(x);  }
  static double cos (const double& x) { return std::cos(x);  }
  static double tan (const double& x) { return std::tan(x);  }
  static double asin(const double& x) { return std::asin(x); }
  static double acos(const double& x) { return std::acos(x); }
  static double atan(const double& x) { return std::atan(x); }
  static double sinh(const double& x) { return std::sinh(x); }
  static double cosh(const double& x) { return std::cosh(x); }
  static double tanh(const double& x) { return std::tanh(x); }
  static double coth(const double& x) { return 1./std::tanh(x); }
  static double asinh(const double& x) { return std::asinh(x); }
  static double acosh(const double& x) { return std::acosh(x); }
  static double atanh(const double& x) { return std::atanh(x); }
  static double acoth(const double& x) { return 1./std::atanh(x); }
  static double erf (const double& x) { return std::erf(x);  }
  static double erfc(const double& x) { return std::erfc(x); }
  static double fstep(const double& x) { return mc::fstep(x); }
  static double bstep(const double& x) { return mc::bstep(x); }
  static double hull(const double& x, const double& y) { throw std::runtime_error("mc::Op<double>::hull -- function not overloaded"); }
  static double min (const double& x, const double& y) { return std::min(x,y);  }
  static double max (const double& x, const double& y) { return std::max(x,y);  }
  static double pos (const double& x) { return mc::pos(x);  }
  static double neg (const double& x) { return mc::neg(x);  }
  static double lb_func (const double& x, const double lb) { return mc::lb_func(x,lb);  }
  static double ub_func (const double& x, const double ub) { return mc::ub_func(x,ub);  }
  static double bounding_func (const double& x, const double lb, const double ub) { return mc::bounding_func(x,lb,ub);  }
  static double squash_node (const double& x, const double lb, const double ub) { return mc::squash_node(x,lb,ub);  }
  static double single_neuron(const std::vector<double> &x, const std::vector<double> &w, const double b, const int type) { return mc::single_neuron(x,w,b,type); }
  static double mc_print (const double& x, const int number) { return mc::mc_print(x,number); }
  static double arh (const double& x, const double k) { return mc::arh(x,k); }
  static double cheb (const double& x, const unsigned n) { return mc::cheb(x,n); }
  template <typename X, typename Y> static double pow(const X& x, const Y& y) { return std::pow(x,y); }
  static double prod (const unsigned n, const double* x) { return mc::prod(n,x); }
  static double monom (const unsigned n, const double* x, const unsigned* k) { return mc::monom(n,x,k); }
  static bool inter(double& xIy, const double& x, const double& y) { xIy = x; return true; }//{ throw std::runtime_error("mc::Op<double>::inter -- operation not permitted"); }
  static bool eq(const double& x, const double& y) { return x==y; }
  static bool ne(const double& x, const double& y) { return x!=y; }
  static bool lt(const double& x, const double& y) { return x<y;  }
  static bool le(const double& x, const double& y) { return x<=y; }
  static bool gt(const double& x, const double& y) { return x>y;  }
  static bool ge(const double& x, const double& y) { return x>=y; }
};

}
#endif

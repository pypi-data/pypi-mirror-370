// Copyright (C) 2009-2017 Benoit Chachuat, Imperial College London.
// All Rights Reserved.
// This code is published under the Eclipse Public License.

#ifndef MC__MCPROFIL_HPP
#define MC__MCPROFIL_HPP

#include "mcfunc.hpp"
#include "library_of_functions.hpp"
#include <Interval.h>
#include <Functions.h>
#include <Constants.h>

#include "fadbad.h"

namespace fadbad
{

//! @brief Specialization of the structure fadbad::Op for use of the type ::INTERVAL of <A href="http://www.ti3.tu-harburg.de/Software/PROFILEnglisch.html">PROFIL</A> as a template parameter of the classes fadbad::F, fadbad::B and fadbad::T of FADBAD++
template <> struct Op< ::INTERVAL >
{
  typedef double Base;
  typedef ::INTERVAL T;
  static Base myInteger( const int i ) { return Base(i); }
  static Base myZero() { return myInteger(0); }
  static Base myOne() { return myInteger(1);}
  static Base myTwo() { return myInteger(2); }
  static double myPI() { return mc::PI; }
  static T myPos( const T& x ) { return  x; }
  static T myNeg( const T& x ) { return -x; }
  template <typename U> static T& myCadd( T& x, const U& y ) { return x+=y; }
  template <typename U> static T& myCsub( T& x, const U& y ) { return x-=y; }
  template <typename U> static T& myCmul( T& x, const U& y ) { return x*=y; }
  template <typename U> static T& myCdiv( T& x, const U& y ) { return x/=y; }
  static T myInv( const T& x ) { return T(1.)/x; }
  static T mySqr( const T& x ) { return ::Sqr(x); }
  template <typename X> static T myPow( const X& x, const int n ) { return( (n>=3&&n%2)? ::Hull(::Power(Inf(x),n),::Power(Sup(x),n)): ::Power(x,n) ); }
  template <typename X, typename Y> static T myPow( const X& x, const Y& y ) { return ::Power(x,y); }
  //static T myCheb( const T& x, const unsigned n ) { return T(-1.,1.); }
  static T mySqrt( const T& x ) { return ::Sqrt( x ); }
  static T myLog( const T& x ) { return ::Log( x ); }
  static T myExp( const T& x ) { return ::Exp( x ); }
  static T mySin( const T& x ) { return ::Sin( x ); }
  static T myCos( const T& x ) { return ::Cos( x ); }
  static T myTan( const T& x ) { return ::Tan( x ); }
  static T myAsin( const T& x ) { return ::ArcSin( x ); }
  static T myAcos( const T& x ) { return ::ArcCos( x ); }
  static T myAtan( const T& x ) { return ::ArcTan( x ); }
  static T mySinh( const T& x ) { return ::Sinh( x ); }
  static T myCosh( const T& x ) { return ::Cosh( x ); }
  static T myTanh( const T& x ) { return ::Tanh( x ); }
  static bool myEq( const T& x, const T& y ) { return x==y; }
  static bool myNe( const T& x, const T& y ) { return x!=y; }
  static bool myLt( const T& x, const T& y ) { return x<y; }
  static bool myLe( const T& x, const T& y ) { return x<=y; }
  static bool myGt( const T& x, const T& y ) { return y<x; }
  static bool myGe( const T& x, const T& y ) { return y<=x; }
};

} // end namespace fadbad

#include "mcop.hpp"

namespace mc
{

//! @brief Specialization of the structure mc::Op for use of the type ::INTERVAL of <A href="http://www.ti3.tu-harburg.de/Software/PROFILEnglisch.html">PROFIL</A> as a template parameter in the other MC++ types
template <> struct Op< ::INTERVAL >
{
  typedef ::INTERVAL T;
  static T point( const double c ) { return T(c); }
  static T zeroone() { return T(0.,1.); }
  static void I(T& x, const T& y) { x = y; }
  static double l(const T& x) { return ::Inf(x); }
  static double u(const T& x) { return ::Sup(x); }
  static double abs (const T& x) { return ::Abs(x);  }
  static double mid (const T& x) { return ::Mid(x);  }
  static double diam(const T& x) { return ::Diam(x); }
  static T inv (const T& x) { return T(1.)/x;  }
  static T sqr (const T& x) { return ::Sqr(x);  }
  static T sqrt(const T& x) { if( ::Inf(x) < 0. ) throw std::runtime_error("negative square root"); return ::Sqrt(x); }
  static T root(const T& x, const int n) { return ::Root(x,n); }
  static T exp (const T& x) { return ::Exp(x);  }
  static T log (const T& x) { return ::Log(x);  }
  static T xlog(const T& x) { return T( ::Pred(mc::xlog(mc::mid(::Inf(x),::Sup(x),std::exp(-1.)))), ::Succ(std::max(mc::xlog(::Inf(x)),mc::xlog(::Sup(x)))) ); }
  static T fabsx_times_x(const T& x) { return T( ::Pred(mc::fabsx_times_x(::Inf(x))), ::Succ(mc::fabsx_times_x(::Sup(x)))); }
  static T xexpax(const T& x, const double a) 
  {  
    if(a==0){ return T(::Pred(::Inf(x)),::Succ(::Sup(x))); } // = x*exp(0*x) = x
	else if(a>0){ return T(::Pred(mc::xexpax(mc::mid(::Inf(x), ::Sup(x),-1./a),a)),::Succ(std::max(mc::xexpax(::Inf(x),a), mc::xexpax(::Sup(x),a)))); } // the extreme point -1/a is a minimum 
	else{ return T(::Pred(std::min(mc::xexpax(::Inf(x),a), mc::xexpax(::Sup(x),a))),::Succ(mc::xexpax(mc::mid(::Inf(x),::Sup(x),-1./a),a))); } // the extreme point -1/a is a maximum 
  }
  // !!THE RESULT IS NOT VERIFIED!!
  static T centerline_deficit(const T& x, const double xLim, const double type) 
  {  
    switch((int)type) {
      case 1:
      case 2:
        if (::Inf(x)>=1.) { // decreasing
          return T( ::Pred(mc::centerline_deficit(::Sup(x),xLim,type)),::Succ(mc::centerline_deficit(::Inf(x),xLim,type)) );
        } else if (::Sup(x)<=1.) {    // increasing
          return THE( ::Pred(mc::centerline_deficit(::Inf(x),xLim,type)), ::Succ(mc::centerline_deficit(::Sup(x),xLim,type)) );
        } else  {            // maximum at f(1)=1 and minimum at either end
          return T( ::Pred(std::min(mc::centerline_deficit(::Inf(x),xLim,type), mc::centerline_deficit(::Sup(x),xLim,type))), ::Succ(1.));
        }
      case 3:
      { 
        const double tmp = std::sqrt((9.*std::pow(xLim,3) - 69.*mc::sqr(xLim) + 175.*xLim - 175.)/std::pow(xLim - 1.,7));
        const double xmax = ( tmp*( 5.*xLim - 1. - 10.*mc::sqr(xLim) + 10.*std::pow(xLim,3) - 5.*std::pow(xLim,4) + std::pow(xLim,5) ) - 47*xLim + 4*xLim^2 + 3*xLim^3 + 70)
                  / (15.*(mc::sqr(xLim) - 4.*xLim + 5.));
        if (::Inf(x)>=xmax) {      // decreasing
          return T( ::Pred(mc::centerline_deficit(::Sup(x),xLim,type)), ::Succ(mc::centerline_deficit(::Inf(x),xLim,type)) );
        } else if (::Sup(x)<=xmax) { // increasing
          return T( ::Pred(mc::centerline_deficit(::Inf(x),xLim,type)), ::Succ(mc::centerline_deficit(::Sup(x),xLim,type)) );
        } else {              // maximum at xmax and minimum at either end
          return T( ::Pred(std::min(mc::centerline_deficit(::Inf(x),xLim,type),mc::centerline_deficit(::Sup(x),xLim,type))), ::Succ(mc::centerline_deficit(xmax,xLim,type)) );
        }
      }
      default:
          throw std::runtime_error("mc::McCormick\t centerline_deficit called with unkonw type.\n");
    }
  }
  static T wake_profile(const T& x, const double type) 
  {  
    if(::Inf(x)>=0.){ return T(::Pred(mc::wake_profile(::Sup(x),type)),::Succ(mc::wake_profile(::Inf(x),type))); } 
    else if(::Sup(x)<=0.){ return T(::Pred(mc::wake_profile(::Inf(x),type)),::Succ(mc::wake_profile(::Sup(x),type))); } 
    else { return T(::Pred(std::min(::Pred(mc::wake_profile(::Inf(x),type)),::Succ(mc::wake_profile(::Sup(x),type)))),::Succ(1.)); }
  }
  static T wake_deficit(const T& x, const T& r, const double a, const double alpha, const double rr, const double type1, const double type2)
    const double r0 = T(rr)*sqrt(T(1.-a)/T(1.-2.*a));
    const T Rwake = r0 + alpha*I1;
    return T(2.)*T(a)*centerline_deficit(Rwake/r0,1.-alpha*rr/r0,type1)*wake_profile(I2/Rwake,type2);
  }
  static T power_curve(const T& x, const double type) 
  {  
    return T(::Pred(mc::power_curve(::Inf(x),type)),::Succ(mc::power_curve(::Sup(x),type))); } 
  }
  static T lmtd(const T& x,const T& y) { return T( ::Pred(mc::lmtd(::Inf(x),::Inf(y))),::Succ(mc::lmtd(::Sup(x),::Sup(y))) ) ; }
  static T rlmtd(const T& x,const T& y) { return T( ::Pred(mc::rlmtd(::Sup(x),::Sup(y))),::Succ(mc::rlmtd(::Inf(x),::Inf(y))) ) ; }
  static T mid(const T& x, const T& y, const double k) { return T(::Pred(mc::mid(::Inf(x), ::Inf(y), k)), ::Succ(mc::mid(::Sup(x), ::Sup(y), k))); }
  static T pinch(const T& Th, const T& Tc, const T& Tp) { 
	  double l = std::min(mc::pinch(::Inf(Th), ::Sup(Tc), ::Sup(Tp)), mc::pinch(::Inf(Th), ::Sup(Tc), ::Inf(Tp)));
	  double u = std::max(mc::pinch(::Sup(Th), ::Inf(Tc), ::Sup(Tp)), mc::pinch(::Sup(Th), ::Inf(Tc), ::Inf(Tp)));
	  return T(::Pred(l), ::Succ(u)); 
  }
  static T euclidean_norm_2d(const T& x,const T& y) { 
		double minPointX = mc::mid(::Inf(x),::Sup(x),0.);
		double minPointY = mc::mid(::Inf(y),::Sup(y),0.);
		// max is one of the 4 corners
		std::vector<double> corners = { mc::euclidean_norm_2d(::Inf(x),::Inf(y)), mc::euclidean_norm_2d(::Inf(x),::Sup(y)),
		                                mc::euclidean_norm_2d(::Sup(x),::Inf(y)), mc::euclidean_norm_2d(::Sup(x),::Sup(y)) };
		unsigned cornerIndex = mc::argmax(4,corners.data());
		return T(::Pred(mc::euclidean_norm_2d(minPointX,minPointY)), ::Succ(corners[cornerIndex]));
  }
  static T expx_times_y(const T& x,const T& y) { return T( ::Pred(mc::expx_times_y(::Inf(x),::Inf(y))),::Succ(mc::expx_times_y(::Sup(x),::Sup(y))) ) ; }
  static T vapor_pressure(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
							const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return T( ::Pred( mc::vapor_pressure(::Inf(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10)), ::Succ( mc::vapor_pressure(::Sup(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10)) ); }  
  static T ideal_gas_enthalpy(const T& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							  const double p7 = 0) { return T( ::Pred( mc::ideal_gas_enthalpy(::Inf(x), x0,type,p1,p2,p3,p4,p5,p6,p7)), ::Succ( mc::ideal_gas_enthalpy(::Sup(x), x0,type,p1,p2,p3,p4,p5,p6,p7)) ); }
  static T saturation_temperature(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
								  const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return T( ::Pred( mc::saturation_temperature(::Inf(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10)), ::Succ( mc::saturation_temperature(::Sup(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10)) );}
  static T enthalpy_of_vaporization(const T& x, const double type, const double p1, const double p2, const double p3, const double p4,
									const double p5, const double p6 = 0) { return T( ::Pred( mc::enthalpy_of_vaporization(::Sup(x), type, p1,p2,p3,p4,p5,p6)), ::Succ( mc::enthalpy_of_vaporization(::Inf(x), type, p1,p2,p3,p4,p5,p6)) ); }  
  static T cost_function(const T& x, const double type, const double p1, const double p2, const double p3) // currently only Guthrie implemented
  { double min,max;
    MONOTONICITY monotonicity = get_monotonicity_cost_function(type, p1, p2, p3, ::Inf(x), ::Sup(x), min, max, true );
    switch(monotonicity){
		case MON_INCR:
			return T(mc::cost_function(::Inf(x),type,p1,p2,p3),mc::cost_function(::Sup(x),type,p1,p2,p3));
			break;
		case MON_DECR:
			return T(mc::cost_function(::Sup(x),type,p1,p2,p3),mc::cost_function(::Inf(x),type,p1,p2,p3));
			break;
		case MON_NONE:
			return T(min,max);
			break;
		default:
			return ::Exp((p1 + ::Log(x)/std::log(10.) * (p2 + p3*::Log(x)/std::log(10.)))*std::log(10.));
			break;
	}
  }
  static T nrtl_tau(const T& x, const double a, const double b, const double e, const double f) 
  { double min,max;
    MONOTONICITY monotonicity = get_monotonicity_nrtl_tau(a,b,e,f, ::Inf(x), ::Sup(x), min, max, true );
    switch(monotonicity){
		case MON_INCR:
			return T(mc::nrtl_tau(::Inf(x),a,b,e,f),mc::nrtl_tau(::Sup(x),a,b,e,f));
			break;
		case MON_DECR:
			return T(mc::nrtl_tau(::Sup(x),a,b,e,f),mc::nrtl_tau(::Inf(x),a,b,e,f));
			break;
		case MON_NONE:
			return T(min,max);
			break;
		default:
			return a + b/x + e * ::Log(x) + f*x;
			break;
	}
  }
  static T nrtl_dtau(const T& x, const double b, const double e, const double f) 
  { double min,max;
    MONOTONICITY monotonicity = get_monotonicity_nrtl_dtau(b,e,f, ::Inf(x), ::Sup(x), min, max, true );
    switch(monotonicity){
		case MON_INCR:
			return T(mc::nrtl_dtau(::Inf(x),b,e,f),mc::nrtl_dtau(::Sup(x),b,e,f));
			break;
		case MON_DECR:
			return T(mc::nrtl_dtau(::Sup(x),b,e,f),mc::nrtl_dtau(::Inf(x),b,e,f));
			break;
		case MON_NONE:
			return T(min,max);
			break;
		default:
			return -b/::Sqr(x) + e/x + f;
			break;
	}
  }
  static T nrtl_G(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return ::Exp(-alpha*nrtl_tau(x,a,b,e,f));} 
  static T nrtl_Gtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return xexpax(nrtl_tau(x,a,b,e,f),-alpha);}
  static T nrtl_Gdtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return nrtl_G(x,a,b,e,f,alpha)*nrtl_dtau(x,b,e,f);}
  static T nrtl_dGtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return -alpha*nrtl_Gtau(x,a,b,e,f,alpha)*nrtl_dtau(x,b,e,f);}
  static T iapws(const T& x, const double type) { throw std::runtime_error("Error: IAPWS-IF97 envelopes are not implemented for PROFIL."); }
  static T iapws(const T& x, const T& y, const double type) { throw std::runtime_error("Error: IAPWS-IF97 envelopes are not implemented for PROFIL."); }
  static T p_sat_ethanol_schroeder(const T& x) {  return T( ::Pred( mc::p_sat_ethanol_schroeder(::Inf(x))), ::Succ( mc::p_sat_ethanol_schroeder(::Sup(x))) ); }
  static T rho_vap_sat_ethanol_schroeder(const T& x) { return T( ::Pred( mc::rho_vap_sat_ethanol_schroeder(::Inf(x))), ::Succ( mc::rho_vap_sat_ethanol_schroeder(::Sup(x))) ); }
  static T rho_liq_sat_ethanol_schroeder(const T& x) { return T( ::Pred( mc::rho_liq_sat_ethanol_schroeder(::Sup(x))), ::Succ( mc::rho_liq_sat_ethanol_schroeder(::Inf(x))) ); }
  static T covariance_function(const T& x, const double type)
  { 
      if( ::Inf(x) < 0. ) throw std::runtime_error("mc::Profil\t Error in mcfilib.hpp. covariance_function with values <0.");
      return  T( ::Pred(mc::covariance_function(::Sup(x),type)), ::Succ(mc::covariance_function(::Inf(x),type)) );
  }
  static T acquisition_function(const T& x, const T& y, const double type, const double fmin)
  { 
      if (::Inf(y) < 0) {
			throw std::runtime_error("mc::Profil\t Error in mcfilib.hpp. acquisition_function with sigma values <0.");
		}
        switch((int)type){
			case 1: // lower confidence bound
			{
				return x - fmin*y;
			}
			case 2: // expected improvement
			{
				return T( ::Pred(mc::acquisition_function(::Sup(x), ::Inf(y), type, fmin)), ::Succ(mc::acquisition_function(::Inf(x), ::Sup(y), type, fmin)) );
			}
			case 3: // probability of improvement
			{
			  throw std::runtime_error("mc::Profil\t Probability of improvement acquisition function currently not implemented.\n");
			}
			default:
			  throw std::runtime_error("mc::Profil\t Acquisition function called with an unknown type.\n");
        }
  }
  static T gaussian_probability_density_function(const T& x)
  { 
      double minVal = std::min(mc::gaussian_probability_density_function(::Inf(x)),mc::gaussian_probability_density_function(::Sup(x)));
	  double maxVal;
	  if (::Inf(x) <= 0. && 0. <= ::Sup(x)) {
	  	  maxVal = mc::gaussian_probability_density_function(0.);
	  }
	  else{
	  	  maxVal = std::max(mc::gaussian_probability_density_function(::Inf(x)),mc::gaussian_probability_density_function(::Sup(x)));
	  }
	  
	  return T(::Pred(minVal), ::Succ(maxVal));
  }
  static T regnormal(const T& x, const double a, const double b) { return T( ::Pred( mc::regnormal(::Inf(x),a,b)), ::Succ( mc::regnormal(::Sup(x),a,b)) ); }
  static T fabs(const T& x) { return T(::Pred(mc::mid(::Inf(x),::Sup(x),0.)),::Succ(::Abs(x))); }
  static T sin (const T& x) { return ::Sin(x);  }
  static T cos (const T& x) { return ::Cos(x);  }
  static T tan (const T& x) { return ::Tan(x);  }
  static T asin(const T& x) { return ::ArcSin(x); }
  static T acos(const T& x) { return ::ArcCos(x); }
  static T atan(const T& x) { return ::ArcTan(x); }
  static T sinh(const T& x) { return ::Sinh(x); }
  static T cosh(const T& x) { return ::Cosh(x); }
  static T tanh(const T& x) { return ::Tanh(x); }
  static T coth(const T& x) { return ::Coth(x); }
  static T asinh(const T& x) { return ::Asinh(x); }
  static T acosh(const T& x) { return ::Acosh(x); }
  static T atanh(const T& x) { return ::Atanh(x); }
  static T acoth(const T& x) { return ::Acoth(x); }
  static T erf (const T& x) { return T(::Pred(std::erf(::Inf(x))),::Succ(std::erf(::Sup(x))));}
  static T erfc(const T& x) { return T(1.)- T(::Pred(std::erf(::Inf(x))),::Succ(std::erf(::Sup(x)))); }
  static T fstep(const T& x) { throw std::runtime_error("operation not permitted"); }
  static T bstep(const T& x) { throw std::runtime_error("operation not permitted"); }
  static T hull(const T& x, const T& y) { return ::Hull(x,y); }
  static T min (const T& x, const T& y) { return T( ::Pred(std::min(::Inf(x),::Inf(y))), ::Succ(std::min(::Sup(x),::Sup(y))) ); }
  static T max (const T& x, const T& y) { return T( ::Pred(std::max(::Inf(x),::Inf(y))), ::Succ(std::max(::Sup(x),::Sup(y))) ); }
  static T pos (const T& x ) { return T( ::Pred(std::max(::Inf(x),::Inf(T(mc::machprec())))), ::Succ(std::max(::Sup(x),::Sup(T(mc::machprec())))) ); }
  static T neg (const T& x ) { return T( ::Pred(std::min(::Inf(x),::Inf(T(-mc::machprec())))), ::Succ(std::min(::Sup(x),::Sup(T(-mc::machprec())))) ); }
  static T lb_func (const T& x, const double lb ) { return T( ::Pred(std::max(::Inf(x),::Inf(T(lb)))), ::Succ(std::max(::Sup(x),::Sup(T(lb)))) ); }
  static T ub_func (const T& x, const double ub ) { return T( ::Pred(std::min(::Inf(x),::Inf(T(ub)))), ::Succ(std::min(::Sup(x),::Sup(T(ub)))) ); }
  static T bounding_func (const T& x, const double lb, const double ub ) { return T( ::Pred(std::min(::Pred(std::max(::Inf(x),::Inf(T(lb)))),::Inf(T(ub)))), ::Succ(std::min(::Succ(std::max(::Sup(x),::Sup(T(lb)))),::Sup(T(ub)))) ); }
  static T squash_node (const T& x, const double lb, const double ub ) { return T( ::Pred(std::min(::Pred(std::max(::Inf(x),::Inf(T(lb)))),::Inf(T(ub)))), ::Succ(std::min(::Succ(std::max(::Sup(x),::Sup(T(lb)))),::Sup(T(ub)))) ); }
  static T single_neuron(const std::vector<T> &x, const std::vector<double> &w, const double b , const int type) 
  { 
    T min=b;
		T max=b; 
		for(unsigned int i=1; i<x.size;i++){
      if(w[i]>0){
			  min+=::Pred(w[i]*::Inf(x[i]));	
			  max+=::Succ(w[i]*::Sup(x[i]));	
      }
      else{
        min+=::Succ(w[i]*::Sup(x[i]));	
			  max+=::Pred(w[i]*::Inf(x[i]));	
      }
		}
    return T(tanh(min),tanh(max));
  }
  
  static T sum_div (const std::vector<T> &x, const std::vector<double> &coeff ) 
  {
		T min=0;
		T max=0; 
		for(unsigned int i=1; i<x.size;i++){
			min+=::Succ(coeff[i+1]*::Sup(x[i]));	
			max+=::Pred(coeff[i+1]*::Inf(x[i]));	
		}
		return T( ::Pred(::Inf(x[0]*coeff[0])/(coeff[1]*::Inf(x[1])+min)), ::Succ( ::Sup(x[0]*coeff[0])/(coeff[1]*::Sup(x[1])+max))); 
  }
  static T xlog_sum (const std::vector<T> &x, const std::vector<double> &coeff ) 
  {
	    	
		// Special case
		if(x.size()==1){
			double valL = ::Inf(x[0]) * std::log(coeff[0]*::Inf(x[0]));
			double valU = ::Sup(x[0]) * std::log(coeff[0]*::Sup(x[0]));
		    double m = mc::mid(::Inf(x[0]),::Sup(x[0]),std::exp(-1.)/coeff[0]);	
			return T( m*std::log(coeff[0]*m),std::max(valL,valU));
		}
		
		std::vector<double> corner1 = {::Inf(x[0])}; corner1.reserve(x.size());	
		std::vector<double> corner2 = {::Sup(x[0])}; corner2.reserve(x.size());
		std::vector<double> rusr = {coeff[0]}; rusr.reserve(x.size()+coeff.size());// used for root finding
		std::vector<double> minPoint(x.size());
		for(size_t i = 1; i<x.size();i++){
			corner1.push_back(::Sup(x[i]));
			corner2.push_back(::Sup(x[i]));
			rusr.push_back(coeff[i]);
			rusr.push_back(::Inf(x[i]));
			minPoint[i] = ::Inf(x[i]);
		}
		double upper = std::max(mc::xlog_sum(corner1,coeff), mc::xlog_sum(corner2,coeff));
		
		rusr.push_back(0.);
		int size = coeff.size();
		double zmin = _compute_root(::Inf(x[0]), ::Inf(x[0]), ::Sup(x[0]), xlog_sum_dfunc, xlog_sum_ddfunc, rusr.data(), &size);	
		minPoint[0] = mc::mid(::Inf(x[0]), ::Sup(x[0]), zmin);	
		double lower = mc::xlog_sum(minPoint, coeff);
		return T(lower,upper);
  }	 
  static T mc_print (const T& x, const int number ) { return T(::Pred(::Inf(x)),::Succ(::Sup(x))); }
  static T arh (const T& x, const double k) { return ::Exp(-k/x); }
  template <typename X> static T pow(const X& x, const int n) { return( (n>=3&&n%2)? ::Hull(::Power(Inf(x),n),::Power(Sup(x),n)): ::Power(x,n) ); }
  template <typename X, typename Y> static T pow(const X& x, const Y& y) { return ::Power(x,y); }
  static T cheb (const T& x, const unsigned n) { return T(-1.,1.); }
  static T prod (const unsigned int n, const T* x) { return n? x[0] * prod(n-1, x+1): 1.; }
  static T monom (const unsigned int n, const T* x, const unsigned* k) { return n? ::Power(x[0], k[0]) * monom(n-1, x+1, k+1): 1.; }
  static bool inter(T& xIy, const T& x, const T& y) { return ::Intersection(xIy,x,y); }
  static bool eq(const T& x, const T& y) { return x==y; }
  static bool ne(const T& x, const T& y) { return x!=y; }
  static bool lt(const T& x, const T& y) { return x<y;  }
  static bool le(const T& x, const T& y) { return x<=y; }
  static bool gt(const T& x, const T& y) { return y<x;  }
  static bool ge(const T& x, const T& y) { return y<=x; }
};

} // namespace mc

#endif

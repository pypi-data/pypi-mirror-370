// Copyright (C) 2009-2017 Benoit Chachuat, Imperial College London.
// All Rights Reserved.
// This code is published under the Eclipse Public License.

#ifndef MC__MCFILIB_HPP
#define MC__MCFILIB_HPP

#include "mcfunc.hpp"
#include "library_of_functions.hpp"
#include "library_of_inverse_functions.hpp"
#include "interval/interval.hpp"

#include "fadbad.h"

namespace fadbad
{

//! @brief Specialization of the structure fadbad::Op for use of the type filib::interval<double> of <A href="http://www.math.uni-wuppertal.de/~xsc/software/filib.html">FILIB++</A> as a template parameter of the classes fadbad::F, fadbad::B and fadbad::T of FADBAD++
template <> struct Op< filib::interval<double> >
{
  typedef double Base;
  typedef filib::interval<double> T;
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
  static T mySqr( const T& x ) { return filib::sqr(x); }
  template <typename X> static T myPow( const X& x, const int n ) { return filib::power(x,n); }
  template <typename X, typename Y> static T myPow( const X& x, const Y& y ) { return filib::pow(x,y); }
  static T mySqrt( const T& x ) { return filib::sqrt(x); }
  static T myLog( const T& x ) { return filib::log(x); }
  static T myExp( const T& x ) { return filib::exp(x); }
  static T mySin( const T& x ) { return filib::sin( x ); }
  static T myCos( const T& x ) { return filib::cos( x ); }
  static T myTan( const T& x ) { return filib::tan( x ); }
  static T myAsin( const T& x ) { return filib::asin( x ); }
  static T myAcos( const T& x ) { return filib::acos( x ); }
  static T myAtan( const T& x ) { return filib::atan( x ); }
  static T mySinh( const T& x ) { return filib::sinh( x ); }
  static T myCosh( const T& x ) { return filib::cosh( x ); }
  static T myTanh( const T& x ) { return filib::tanh( x ); }
  static bool myEq( const T& x, const T& y ) { return x.seq(y); }
  static bool myNe( const T& x, const T& y ) { return x.sne(y); }
  static bool myLt( const T& x, const T& y ) { return x.slt(y); }
  static bool myLe( const T& x, const T& y ) { return x.sle(y); }
  static bool myGt( const T& x, const T& y ) { return x.sgt(y); }
  static bool myGe( const T& x, const T& y ) { return x.sge(y); }

};

//! @brief Specialization of the structure fadbad::Op for use of the type filib::interval<double,filib::native_switched,filib::i_mode_extended> of <A href="http://www.math.uni-wuppertal.de/~xsc/software/filib.html">FILIB++</A> as a template parameter of the classes fadbad::F, fadbad::B and fadbad::T of FADBAD++
template <> struct Op< filib::interval<double,filib::native_switched,filib::i_mode_extended> >
{
  typedef double Base;
  typedef filib::interval<double,filib::native_switched,filib::i_mode_extended> T;
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
  static T mySqr( const T& x ) { return filib::sqr(x); }
  template <typename X> static T myPow( const X& x, const int n ) { return filib::power(x,n); }
  template <typename X, typename Y> static T myPow( const X& x, const Y& y ) { return filib::pow(x,y); }
  static T mySqrt( const T& x ) { return filib::sqrt(x); }
  static T myLog( const T& x ) { return filib::log(x); }
  static T myExp( const T& x ) { return filib::exp(x); }
  static T mySin( const T& x ) { return filib::sin( x ); }
  static T myCos( const T& x ) { return filib::cos( x ); }
  static T myTan( const T& x ) { return filib::tan( x ); }
  static T myAsin( const T& x ) { return filib::asin( x ); }
  static T myAcos( const T& x ) { return filib::acos( x ); }
  static T myAtan( const T& x ) { return filib::atan( x ); }
  static T mySinh( const T& x ) { return filib::sinh( x ); }
  static T myCosh( const T& x ) { return filib::cosh( x ); }
  static T myTanh( const T& x ) { return filib::tanh( x ); }
  static bool myEq( const T& x, const T& y ) { return x.seq(y); }
  static bool myNe( const T& x, const T& y ) { return x.sne(y); }
  static bool myLt( const T& x, const T& y ) { return x.slt(y); }
  static bool myLe( const T& x, const T& y ) { return x.sle(y); }
  static bool myGt( const T& x, const T& y ) { return x.sgt(y); }
  static bool myGe( const T& x, const T& y ) { return x.sge(y); }
};

} // end namespace fadbad


#include "mcop.hpp"


namespace filib {

	// added @AVT.SVT, 27.03.2019 - this is validated since it fowards to the filib internal version
	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N,K,E> pow(interval<N,K,E> const & x, int const & n) {
		return filib::power(x,n);
	}

	// added @AVT.SVT, 27.03.2019 - this is only validated in case inf(x)!=0.
	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N,K,E> pow(interval<N,K,E> const & x, double const & a) {
		if(E) {
			if (x.isEmpty()) {
				return interval<N,K,E>::EMPTY();
			}
		}
		if(a<0.){
			return interval<N,K,E>(1.0,1.0)/pow(x,-a);
		}
		if(a==0.){
			return interval<N,K,E>(1.0,1.0);
		}
		if(a==1.){
		  return x;
		}
		if(filib::inf(x)==0.){
		  return interval<N,K,E>(0,std::pow(filib::sup(x),a));
		}
		if(filib::inf(x)<0.){
		  throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. pow(x, double) with x < 0.");
		}
		return  filib::exp(a*filib::log(x));
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N,K,E> pos(interval<N,K,E> const & x) {
		return x.imax(mc::machprec());
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N,K,E> neg(interval<N,K,E> const & x) {
		return x.imin(-mc::machprec());
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N,K,E> max(interval<N,K,E> const & x, interval<N,K,E> const & y) {
		return x.imax(y);
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N,K,E> min(interval<N,K,E> const & x, interval<N,K,E> const & y) {
		return x.imin(y);
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> xexpax(interval<N,K,E> const & x, const double a) {
		if(a==0){ return interval<N,K,E>(filib::inf(x),filib::sup(x)); } // = x*exp(0*x) = x
		else if(a>0){ return interval<N,K,E>(mc::xexpax(mc::mid(filib::inf(x),filib::sup(x),-1./a),a),std::max(mc::xexpax(filib::inf(x),a), mc::xexpax(filib::sup(x),a))); } // the extreme point -1/a is a minimum
		else{ return interval<N,K,E>(std::min(mc::xexpax(filib::inf(x),a), mc::xexpax(filib::sup(x),a)),mc::xexpax(mc::mid(filib::inf(x),filib::sup(x),-1./a),a)); } // the extreme point -1/a is a maximum
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> centerline_deficit(interval<N,K,E> const & x, const double xLim, const double type) {
    	switch((int)type) {
    		case 1:
    		case 2:
    			if (filib::inf(x)>=1.) {	// decreasing
					return interval<N,K,E>(mc::centerline_deficit(filib::sup(x),xLim,type),mc::centerline_deficit(filib::inf(x),xLim,type));
    			} else if (filib::sup(x)<=1.) {		// increasing
					return interval<N,K,E>(mc::centerline_deficit(filib::inf(x),xLim,type),mc::centerline_deficit(filib::sup(x),xLim,type));
    			} else {						// maximum at f(1)=1 and minimum at either end
			  		return interval<N,K,E>( std::min(mc::centerline_deficit(filib::inf(x),xLim,type),mc::centerline_deficit(filib::sup(x),xLim,type)), 1. );
    			}
    		case 3:
    		{	
    			const double tmp = std::sqrt((9.*std::pow(xLim,3) - 69.*mc::sqr(xLim) + 175.*xLim - 175.)/std::pow(xLim - 1.,7));
    			const double xmax = ( tmp*( 5.*xLim - 1. - 10.*mc::sqr(xLim) + 10.*std::pow(xLim,3) - 5.*std::pow(xLim,4) + std::pow(xLim,5) ) - 47.*xLim + 4.*mc::sqr(xLim) + 3.*std::pow(xLim,3) + 70.)
    								/ (15.*(mc::sqr(xLim) - 4.*xLim + 5.));
				if (filib::inf(x)>=xmax) {			// decreasing
					return interval<N,K,E>(mc::centerline_deficit(filib::sup(x),xLim,type),mc::centerline_deficit(filib::inf(x),xLim,type));
			    } else if (filib::sup(x)<=xmax) {	// increasing
					return interval<N,K,E>(mc::centerline_deficit(filib::inf(x),xLim,type),mc::centerline_deficit(filib::sup(x),xLim,type));
				} else {							// maximum at xmax and minimum at either end
				  return interval<N,K,E>( std::min(mc::centerline_deficit(filib::inf(x),xLim,type),mc::centerline_deficit(filib::sup(x),xLim,type)), mc::centerline_deficit(xmax,xLim,type) );
				}
    		}
    		default:
      			throw std::runtime_error("mc::McCormick\t centerline_deficit called with unknown type.\n");
    	}
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> wake_profile(interval<N,K,E> const & x, const double type) {
		if(filib::inf(x)>=0.){
			return interval<N,K,E>(mc::wake_profile(filib::sup(x),type),mc::wake_profile(filib::inf(x),type));
		} else if (filib::sup(x)<=0.) {
			return interval<N,K,E>(mc::wake_profile(filib::inf(x),type),mc::wake_profile(filib::sup(x),type));
		} else {
		  return interval<N,K,E>( std::min(mc::wake_profile(filib::inf(x),type),mc::wake_profile(filib::sup(x),type)), 1. );
		}
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> wake_deficit(interval<N,K,E> const & x, interval<N,K,E> const & r, const double a, const double alpha, const double rr, const double type1, const double type2) {
		
    	// trivial case first:
    	if (filib::sup(x)<=-rr) {
    		return interval<N,K,E>(0.);
    	}

		const double r0 = rr*std::sqrt((1.-a)/(1.-2.*a));
		const double xLim = 1.-alpha*rr/r0;
    	switch((int)type2) {	// wake profile
    		case 1: // Jensen top hat
    		{
    			double fLower, fUpper;
    			switch((int)type1) {	// centerline deficit
		    		case 1:	// Original Jensen centerline deficit
		    		{
		    			if (filib::inf(r)>=0.) {		// decreasing w.r.t. r
		    				const double xMaxAtRmin = std::max(0.,(filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0);
			    			} else if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t. x
								fUpper = 0.;
			    			} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmin/r0);		
			    			}
		    				const double xMaxAtRmax = std::max(0.,(filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0);
			    			} else {
						  		fLower = 0.;
			    			}
		    			} else if (filib::sup(r)<=0.) {	// increasing w.r.t. r
		    				const double xMaxAtRmax = std::max(0.,(-filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0);
			    			} else if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t. x
								fUpper = 0.;
			    			} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmax/r0);		
			    			}
		    				const double  xMaxAtRmin= std::max(0.,(-filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0);
			    			} else {
						  		fLower = 0.;
			    			}
		    			} else {						// single max. w.r.t. r at 0
		    				if (filib::inf(x)>0.) {
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0);
		    				} else if (filib::sup(x)<0.) {
		    					fUpper = 0.;
		    				} else {
		    					fUpper = 2.*a;
		    				}
		    				const double rMaxAbs = std::max(filib::sup(r),-filib::inf(r));
		    				const double xMaxAtRmaxAbs= std::max(0.,(rMaxAbs-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmaxAbs) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0);
			    			} else {
						  		fLower = 0.;
			    			}
		    			}
		    			return interval<N,K,E>(fLower,fUpper);
		    		}
		    		case 2: // Continuous Jensen with linear interpolation
		    		{
		    			if (filib::inf(r)>=0.) {		// decreasing w.r.t. r
		    				const double xMaxAtRmin = std::max(0.,(filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0);
			    			} else if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t. x
								if (filib::sup(x)>=std::max(-rr,(filib::inf(r)-r0)/alpha)) {
									fUpper = 0. + (2.*a/rr)*(filib::sup(x)+rr);
								} else {
									fUpper = 0.;
								}
			    			} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmin/r0);		
			    			}
		    				const double xMaxAtRmax = std::max(0.,(filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0);
			    			} else if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t x
								if (filib::inf(x)>=std::max(-rr,(filib::sup(r)-r0)/alpha)) {
									fLower = 0. + (2.*a/rr)*(filib::inf(x)+rr);
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=std::max(-rr,(filib::sup(r)-r0)/alpha)) {
									fLower = std::min( 0. + (2.*a/rr)*(filib::inf(x)+rr),
													   2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0) );
								} else {
									fLower = 0.;
								}
			    			}
		    			} else if (filib::sup(r)<=0.) {	// increasing w.r.t. r
		    				const double xMaxAtRmax = std::max(0.,(-filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0);
			    			} else if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t. x
								if (filib::sup(x)>=std::max(-rr,(-filib::sup(r)-r0)/alpha)) {
									fUpper = 0. + (2.*a/rr)*(filib::sup(x)+rr);
								} else {
									fUpper = 0.;
								}
			    			} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmax/r0);		
			    			}
		    				const double  xMaxAtRmin= std::max(0.,(-filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0);
			    			}  else if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t x
								if (filib::inf(x)>=std::max(-rr,(-filib::inf(r)-r0)/alpha)) {
									fLower = 0. + (2.*a/rr)*(filib::inf(x)+rr);
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=std::max(-rr,(-filib::inf(r)-r0)/alpha)) {
									fLower = std::min( 0. + (2.*a/rr)*(filib::inf(x)+rr),
													   2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0) );
								} else {
									fLower = 0.;
								}
			    			}
		    			} else {						// single max. w.r.t. r at 0
		    				if (filib::inf(x)>0.) {
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0);
		    				} else if (filib::sup(x)<0.) {
		    					if (filib::sup(x)>=-rr) {
									fUpper = 0. + (2.*a/rr)*(filib::sup(x)+rr);
		    					} else {
			    					fUpper = 0.;
		    					}
		    				} else {
		    					fUpper = 2.*a;
		    				}
		    				const double rMaxAbs = std::max(filib::sup(r),-filib::inf(r));
		    				const double xMaxAtRmaxAbs= std::max(0.,(rMaxAbs-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmaxAbs) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0);
			    			} else if (filib::sup(x)<xMaxAtRmaxAbs) {// increasing w.r.t. x
								if (filib::inf(x)>=std::max(-rr,(rMaxAbs-r0)/alpha)) {
									fLower = 0. + (2.*a/rr)*(filib::inf(x)+rr);
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=std::max(-rr,(rMaxAbs-r0)/alpha)) {
									fLower = std::min( 0. + (2.*a/rr)*(filib::inf(x)+rr),
													   2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0) );
								} else {
									fLower = 0.;
								}
			    			}
		    			}
		    			return interval<N,K,E>(fLower,fUpper);
		    		}
		    		case 3:
		    		{
		    			const double xLim = 1.-alpha*rr/r0;
		    			const double tmp = std::sqrt((9.*std::pow(xLim,3) - 69.*mc::sqr(xLim) + 175.*xLim - 175.)/std::pow(xLim - 1.,7));
		    			const double xmax = ( tmp*( 5.*xLim - 1. - 10.*mc::sqr(xLim) + 10.*std::pow(xLim,3) - 5.*std::pow(xLim,4) + std::pow(xLim,5) ) - 47.*xLim + 4.*mc::sqr(xLim) + 3.*std::pow(xLim,3) + 70.)
		    								/ (15.*(mc::sqr(xLim) - 4.*xLim + 5.));
		    			if (filib::inf(r)>=0.) {		// decreasing w.r.t. r
		    				const double xMaxAtRmin = std::max(xmax,(filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fUpper = 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1);
			    			} else if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t. x
								if (filib::sup(x)>=std::max(-rr,(filib::inf(r)-r0)/alpha)) {
									fUpper = 2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1);
								} else {
									fUpper = 0.;
								}
			    			} else {
								fUpper = 2.*a*mc::centerline_deficit(1+alpha*xMaxAtRmin/r0,1.-alpha*rr/r0,type1);		
			    			}
		    				const double xMaxAtRmax = std::max(xmax,(filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fLower = 2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1);
			    			} else if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t x
								if (filib::inf(x)>=std::max(-rr,(filib::sup(r)-r0)/alpha)) {
									fLower = 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1);
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=std::max(-rr,(filib::sup(r)-r0)/alpha)) {
									fLower = std::min( 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1),
													   2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1) );
								} else {
									fLower = 0.;
								}
			    			}
		    			} else if (filib::sup(r)<=0.) {	// increasing w.r.t. r
		    				const double xMaxAtRmax = std::max(xmax,(-filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fUpper = 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1);
			    			} else if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t. x
								if (filib::sup(x)>=std::max(-rr,(-filib::sup(r)-r0)/alpha)) {
									fUpper = 2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1);
								} else {
									fUpper = 0.;
								}
			    			} else {
								fUpper = 2.*a*mc::centerline_deficit(1+alpha*xMaxAtRmax/r0,1.-alpha*rr/r0,type1);	
			    			}
		    				const double  xMaxAtRmin= std::max(xmax,(-filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fLower = 2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1);
			    			}  else if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t x
								if (filib::inf(x)>=std::max(-rr,(-filib::inf(r)-r0)/alpha)) {
									fLower = 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1);
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=std::max(-rr,(-filib::inf(r)-r0)/alpha)) {
									fLower = std::min( 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1),
													   2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1) );
								} else {
									fLower = 0.;
								}
			    			}
		    			} else {						// single max. w.r.t. r at 0
		    				if (filib::inf(x)>xmax) {
								fUpper = 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1);
		    				} else if (filib::sup(x)<xmax) {
		    					if (filib::sup(x)>=-rr) {
									fUpper = 2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1);
		    					} else {
			    					fUpper = 0.;
		    					}
		    				} else {
		    					fUpper = 2.*a;
		    				}
		    				const double rMaxAbs = std::max(filib::sup(r),-filib::inf(r));
		    				const double xMaxAtRmaxAbs= std::max(xmax,(rMaxAbs-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmaxAbs) {		// decreasing w.r.t. x
								fLower = 2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1);
			    			} else if (filib::sup(x)<xMaxAtRmaxAbs) {// increasing w.r.t. x
								if (filib::inf(x)>=std::max(-rr,(rMaxAbs-r0)/alpha)) {
									fLower = 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1);
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=std::max(-rr,(rMaxAbs-r0)/alpha)) {
									fLower = std::min( 2.*a*mc::centerline_deficit(1+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1),
													   2.*a*mc::centerline_deficit(1+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1) );
								} else {
									fLower = 0.;
								}
			    			}
		    			}
		    			return interval<N,K,E>(fLower,fUpper);
		    		}
		    		default:
		      			throw std::runtime_error("mc::McCormick\t wake_deficit called with unknown type for centerline_deficit.\n");

    			}
    		}
    		case 2: // Park Gauss profile
    		{
    			double fLower, fUpper;
    			switch((int)type1) {	// centerline deficit
		    		case 1:	// Original Jensen centerline deficit
		    		{
		    			if (filib::inf(r)>=0.) {		// decreasing w.r.t. r
		    				const double xMaxAtRmin = std::max(0.,(filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::inf(x))));
			    			} else if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t. x
			    				if (filib::sup(x)>=0.) {
									fUpper = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x))));
			    				} else {
			    					fUpper = 0.;
			    				}
			    			} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmin/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*xMaxAtRmin)));
			    			}
		    				const double xMaxAtRmax = std::max(0.,(filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x))));
			    			} else {
			    				if (filib::inf(x)>0.) {
									fLower = std::min(2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::inf(x)))),
													  2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x)))));
			    				} else {
			    					fLower = 0.;
			    				}
			    			}
		    			} else if (filib::sup(r)<=0.) {	// increasing w.r.t. r
		    				const double xMaxAtRmax = std::max(0.,(-filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::inf(x))));
			    			} else if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t. x
			    				if (filib::sup(x)>=0.) {
									fUpper = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x))));
			    				} else {
			    					fUpper = 0.;
			    				}
			    			} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmax/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*xMaxAtRmax)));	
			    			}
		    				const double  xMaxAtRmin= std::max(0.,(-filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x))));
			    			} else {
			    				if (filib::inf(x)>0.) {
									fLower = std::min(2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::inf(x)))),
													  2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x)))));
			    				} else {
			    					fLower = 0.;
			    				}
			    			}
		    			} else {						// single max. w.r.t. r at 0
		    				if (filib::inf(x)>0.) {
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*1.;
		    				} else if (filib::sup(x)<0.) {
		    					fUpper = 0.;
		    				} else {
		    					fUpper = 2.*a;
		    				}
		    				const double rMaxAbs = std::max(filib::sup(r),-filib::inf(r));
		    				const double xMaxAtRmaxAbs= std::max(0.,(rMaxAbs-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmaxAbs) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::sup(x))));
			    			} else {
			    				if (filib::inf(x)>0.) {
									fLower = std::min(2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::inf(x)))),
													  2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::sup(x)))));
			    				} else {
			    					fLower = 0.;
			    				}
			    			}
		    			}
		    			return interval<N,K,E>(fLower,fUpper);
		    		}
		    		case 2: // Continuous Jensen with linear interpolation
		    		{
		    			if (filib::inf(r)>=0.) {		// decreasing w.r.t. r
		    				const double xMaxAtRmin = std::max(0.,(filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::inf(x))));
			    			} else if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t. x
								if (filib::sup(x)>=-rr) {
									if (filib::sup(x)>=0.) {
										fUpper = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x))));
									} else {
										fUpper = (2.*a/rr)*(filib::sup(x)+rr)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x))));
									}
								} else {
									fUpper = 0.;
								}
			    			} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmin/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*xMaxAtRmin)));	
			    			}
		    				const double xMaxAtRmax = std::max(0.,(filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x))));
			    			} else if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t x
								if (filib::inf(x)>=-rr) {
									if (filib::inf(x)>=0.) {
										fLower = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::inf(x))));
									} else {
										fLower = (2.*a/rr)*(filib::inf(x)+rr)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::inf(x))));
									}
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=-rr) {
									fLower = std::min( 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x)))),
													   (2.*a/rr)*(filib::inf(x)+rr)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::inf(x)))) ) ;
								} else {
									fLower = 0.;
								}
			    			}
		    			} else if (filib::sup(r)<=0.) {	// increasing w.r.t. r
		    				const double xMaxAtRmax = std::max(0.,(-filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::inf(x))));
			    			} else if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t. x
								if (filib::sup(x)>=-rr) {
									if (filib::sup(x)>=0.) {
										fUpper = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x))));
									} else {
										fUpper = (2.*a/rr)*(filib::sup(x)+rr)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x))));
									}
								} else {
									fUpper = 0.;
								}
			    			} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmax/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*xMaxAtRmax)));		
			    			}
		    				const double  xMaxAtRmin= std::max(0.,(-filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x))));
			    			}  else if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t x
								if (filib::inf(x)>=-rr) {
									if (filib::inf(x)>=0.) {
										fLower = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::inf(x))));
									} else {
										fLower = (2.*a/rr)*(filib::inf(x)+rr)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::inf(x))));
									}
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=-rr) {
									fLower = std::min( 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x)))),
													   (2.*a/rr)*(filib::inf(x)+rr)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::inf(x)))) ) ;
								} else {
									fLower = 0.;
								}
			    			}
		    			} else {						// single max. w.r.t. r at 0
		    				if (filib::inf(x)>0.) {
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*1.;
		    				} else if (filib::sup(x)<0.) {
								if (filib::sup(x)>=-rr) {
									if (filib::sup(x)>=0.) {
										fUpper = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*1.;
									} else {
										fUpper = (2.*a/rr)*(filib::sup(x)+rr)*1.;
									}
								} else {
									fUpper = 0.;
								}
		    				} else {
		    					fUpper = 2.*a;
		    				}
		    				const double rMaxAbs = std::max(filib::sup(r),-filib::inf(r));
		    				const double xMaxAtRmaxAbs= std::max(0.,(rMaxAbs-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmaxAbs) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::sup(x))));
			    			} else if (filib::sup(x)<xMaxAtRmaxAbs) {// increasing w.r.t. x
								if (filib::inf(x)>=-rr) {
									if (filib::inf(x)>=0.) {
										fLower = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::inf(x))));
									} else {
										fLower = (2.*a/rr)*(filib::inf(x)+rr)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::inf(x))));
									}
								} else {
									fLower = 0.;
								}
			    			} else {
								if (filib::inf(x)>=-rr) {
									fLower = std::min( 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::sup(x)))),
													   (2.*a/rr)*(filib::inf(x)+rr)           *std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::inf(x)))) ) ;
								} else {
									fLower = 0.;
								}
			    			}
		    			}
		    			return interval<N,K,E>(fLower,fUpper);
		    		}
		    		case 3:
		    		{
		    			const double xLim = 1.-alpha*rr/r0;
		    			const double tmp = std::sqrt((9.*std::pow(xLim,3) - 69.*mc::sqr(xLim) + 175.*xLim - 175.)/std::pow(xLim - 1.,7));
		    			const double xmax = ( tmp*( 5.*xLim - 1. - 10.*mc::sqr(xLim) + 10.*std::pow(xLim,3) - 5.*std::pow(xLim,4) + std::pow(xLim,5) ) - 47.*xLim + 4.*mc::sqr(xLim) + 3.*std::pow(xLim,3) + 70.)
		    								/ (15.*(mc::sqr(xLim) - 4.*xLim + 5.));
		    			if (filib::inf(r)>=0.) {		// decreasing w.r.t. r
		    				const double xMaxAtRmin = std::max(0.,(filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::inf(x))));
			    			} else if (filib::inf(x)>=0.) {
								if (filib::sup(x)<xMaxAtRmin) {	// increasing w.r.t. x
									fUpper = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x))));
								} else {
									fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmin/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*xMaxAtRmin)));
								}
			    			} else {
				    			if ((filib::sup(x)<xMaxAtRmin)&&(filib::inf(r)>=r0)) {	// increasing w.r.t. x
									if (filib::sup(x)>=-rr) {
										fUpper = 2.*a*mc::centerline_deficit(1.+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x))));
									} else {
										fUpper = 0.;
									}
				    			} else {
									if (filib::sup(x)>=-rr) {
										fUpper = 2.*a*mc::centerline_deficit(1.+alpha*xmax/r0,1.-alpha*rr/r0,type1)*1.;
									} else {
										fUpper = 0.;
									}
				    			}
			    			}
		    				const double xMaxAtRmax = std::max(0.,(filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x))));
			    			} else {
								if (filib::inf(x)>=-rr) {
									fLower = std::min( 2.*a*mc::centerline_deficit(1.+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::inf(x)))),
													   2.*a*mc::centerline_deficit(1.+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x)))) ) ;
								} else {
									fLower = 0.;
								}
			    			}
		    			} else if (filib::sup(r)<=0.) {	// increasing w.r.t. r
		    				const double xMaxAtRmax = std::max(0.,(-filib::sup(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmax) {		// decreasing w.r.t. x
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::inf(x)))); 
			    			} else if (filib::inf(x)>=0.) {
								if (filib::sup(x)<xMaxAtRmax) {	// increasing w.r.t. x
									fUpper = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x))));
								} else {
									fUpper = 2.*a/mc::sqr(1.+alpha*xMaxAtRmax/r0)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*xMaxAtRmax)));
								}
			    			} else {
				    			if ((filib::sup(x)<xMaxAtRmax)&&(-filib::sup(r)>=r0)) {	// increasing w.r.t. x
									if (filib::sup(x)>=-rr) {
										fUpper = 2.*a*mc::centerline_deficit(1.+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1)*std::exp(-mc::sqr(filib::sup(r)/(r0+alpha*filib::sup(x))));
									} else {
										fUpper = 0.;
									}
				    			} else {
									if (filib::sup(x)>=-rr) {
										fUpper = 2.*a*mc::centerline_deficit(1.+alpha*xmax/r0,1.-alpha*rr/r0,type1)*1.;
									} else {
										fUpper = 0.;
									}
				    			}
			    			}
		    				const double  xMaxAtRmin= std::max(0.,(-filib::inf(r)-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmin) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x))));
			    			}  else {
								if (filib::inf(x)>=-rr) {
									fLower = std::min( 2.*a*mc::centerline_deficit(1.+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::inf(x)))),
													   2.*a*mc::centerline_deficit(1.+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1)*std::exp(-mc::sqr(filib::inf(r)/(r0+alpha*filib::sup(x)))) ) ;
								} else {
									fLower = 0.;
								}
			    			}
		    			} else {						// single max. w.r.t. r at 0
		    				if (filib::inf(x)>xmax) {
								fUpper = 2.*a/mc::sqr(1.+alpha*filib::inf(x)/r0)*1.;
		    				} else if (filib::sup(x)<xmax) {
								if (filib::sup(x)>=-rr) {
									fUpper = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*1.;
								} else {
									fUpper = 0.;
								}
		    				} else {
								fUpper = 2.*a/mc::sqr(1.+alpha*xmax/r0)*1.;
		    				}
		    				const double rMaxAbs = std::max(filib::sup(r),-filib::inf(r));
		    				const double xMaxAtRmaxAbs= std::max(0.,(rMaxAbs-r0)/alpha);
			    			if (filib::inf(x)>xMaxAtRmaxAbs) {		// decreasing w.r.t. x
								fLower = 2.*a/mc::sqr(1.+alpha*filib::sup(x)/r0)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::sup(x))));
			    			}  else {
								if (filib::inf(x)>=-rr) {
									fLower = std::min( 2.*a*mc::centerline_deficit(1.+alpha*filib::inf(x)/r0,1.-alpha*rr/r0,type1)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::inf(x)))),
													   2.*a*mc::centerline_deficit(1.+alpha*filib::sup(x)/r0,1.-alpha*rr/r0,type1)*std::exp(-mc::sqr(rMaxAbs/(r0+alpha*filib::sup(x)))) ) ;
								} else {
									fLower = 0.;
								}
			    			}
		    			}
		    			return interval<N,K,E>(fLower,fUpper);
		    		}
		    		default:
		      			throw std::runtime_error("mc::McCormick\t wake_deficit called with unknown type for centerline_deficit.\n");

    			}
    		}
    		default:
    			throw std::runtime_error("mc::McCormick\t wake_deficit called with unknown type for wake_deficit.\n");
    	}

	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> power_curve(interval<N,K,E> const & x, const double type) {
		return interval<N,K,E>(mc::power_curve(filib::inf(x),type),mc::power_curve(filib::sup(x),type));
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> lmtd(interval<N,K,E> const & x, interval<N,K,E> const & y) {
		if(filib::inf(x)<=0. || filib::inf(y)<=0.){
		  throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. lmtd(x, y) with values <=0.");
		}
		if(x.isInfinite() || y.isInfinite()){
			return interval<N,K,E>(mc::lmtd(filib::inf(x),filib::inf(y)), filib::primitive::POS_INFTY());
		}
		return interval<N,K,E>(mc::lmtd(filib::inf(x),filib::inf(y)),mc::lmtd(filib::sup(x),filib::sup(y)) ) ;
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> rlmtd(interval<N,K,E> const & x,  interval<N,K,E>const & y) {
	  if(filib::inf(x)<=0. || filib::inf(y)<=0.){
		  throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. rlmtd(x, y) with values <=0.");
	  }
	  return  interval<N,K,E>(mc::rlmtd(filib::sup(x),filib::sup(y)),mc::rlmtd(filib::inf(x),filib::inf(y)) ) ;
    }

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N, K, E> mid(interval<N, K, E> const & x, interval<N, K, E>const & y, const double k) {
		return  interval<N, K, E>(mc::mid(filib::inf(x), filib::inf(y), k), mc::mid(filib::sup(x), filib::sup(y), k));
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N, K, E> pinch(interval<N, K, E> const & Th, interval<N, K, E>const & Tc, interval<N, K, E>const & Tp) {
		double l = std::min(mc::pinch(filib::inf(Th), filib::sup(Tc), filib::sup(Tp)), mc::pinch(filib::inf(Th), filib::sup(Tc), filib::inf(Tp)));
		double u = std::max(mc::pinch(filib::sup(Th), filib::inf(Tc), filib::sup(Tp)), mc::pinch(filib::sup(Th), filib::inf(Tc), filib::inf(Tp)));
		return  interval<N, K, E>(l, u);
	}
	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> cost_function(interval<N,K,E> const & x, const double type, const double p1, const double p2, const double p3) // currently only Guthrie implemented
	{
		if(filib::inf(x)<=0.){
			  throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. cost_function with values <=0.");
		}
		double min = std::numeric_limits<double>::max(), max = -std::numeric_limits<double>::max();
		mc::MONOTONICITY monotonicity = mc::get_monotonicity_cost_function(type, p1, p2, p3, filib::inf(x), filib::sup(x), min, max, true );
		switch(monotonicity){
			case mc::MON_INCR:
				return interval<N,K,E>(mc::cost_function(filib::inf(x),type,p1,p2,p3),mc::cost_function(filib::sup(x),type,p1,p2,p3));
				break;
			case mc::MON_DECR:
				return interval<N,K,E>(mc::cost_function(filib::sup(x),type,p1,p2,p3),mc::cost_function(filib::inf(x),type,p1,p2,p3));
				break;
			case mc::MON_NONE:
				return interval<N,K,E>(min,max);
				break;
			default:
				return filib::exp((p1 + filib::log(x)/std::log(10.) * (p2 + p3*filib::log(x)/std::log(10.)))*std::log(10.));
				break;
		}
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> nrtl_tau(interval<N,K,E> const & x, const double a, const double b, const double e, const double f)
	{
		if(filib::inf(x)<=0.){
			  throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. nrtl_tau with values <=0.");
		}
		double min = std::numeric_limits<double>::max(), max = -std::numeric_limits<double>::max();
		mc::MONOTONICITY monotonicity = mc::get_monotonicity_nrtl_tau(a,b,e,f, filib::inf(x), filib::sup(x), min, max, true );
		switch(monotonicity){
			case mc::MON_INCR:
				return interval<N,K,E>(mc::nrtl_tau(filib::inf(x),a,b,e,f),mc::nrtl_tau(filib::sup(x),a,b,e,f));
				break;
			case mc::MON_DECR:
				return interval<N,K,E>(mc::nrtl_tau(filib::sup(x),a,b,e,f),mc::nrtl_tau(filib::inf(x),a,b,e,f));
				break;
			case mc::MON_NONE:
				return interval<N,K,E>(min,max);
				break;
			default:
				return a + b/x + e * filib::log(x) + f*x;
				break;
		}
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> nrtl_dtau(interval<N,K,E> const & x, const double b, const double e, const double f)
	{
		if(filib::inf(x)<=0.){
			  throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. nrtl_dtau with values <=0.");
		}
		double min = std::numeric_limits<double>::max(), max = -std::numeric_limits<double>::max();
		mc::MONOTONICITY monotonicity = mc::get_monotonicity_nrtl_dtau(b,e,f, filib::inf(x), filib::sup(x), min, max, true );
		switch(monotonicity){
			case mc::MON_INCR:
				return interval<N,K,E>(mc::nrtl_dtau(filib::inf(x),b,e,f),mc::nrtl_dtau(filib::sup(x),b,e,f));
				break;
			case mc::MON_DECR:
				return interval<N,K,E>(mc::nrtl_dtau(filib::sup(x),b,e,f),mc::nrtl_dtau(filib::inf(x),b,e,f));
				break;
			case mc::MON_NONE:
				return interval<N,K,E>(min,max);
				break;
			default:
				return -b/filib::sqr(x) + e/x + f;
				break;
		}
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N, K, E> single_neuron(const std::vector<interval<N,K,E>> &x, const std::vector<double> &w, const double b, const int type)
	{
	  std::vector<double> min(x.size());
	  std::vector<double> max(x.size());
	  for(unsigned int i=0; i<x.size();i++){
		if(x[i].isInfinite()){
		  throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. single_neuron with infinite values.");
		}

		if (w[i] >= 0.){
			min[i] = filib::inf(x[i]);
			max[i] = filib::sup(x[i]);
		}
		else {
		 	min[i] = filib::sup(x[i]);
		 	max[i] = filib::inf(x[i]);
	    }
	  }  

	  return interval<N,K,E>(mc::single_neuron(min,w,b,type),mc::single_neuron(max,w,b,type));
	}

    template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> sum_div (const std::vector<interval<N,K,E>> &x, const std::vector<double> &coeff )
	{
	  std::vector<double> min(x.size());
	  std::vector<double> max(x.size());
	  if(filib::inf(x[0])<=0. ){
		 throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. sum_div with values <=0.");
	  }
	  if(x[0].isInfinite()){
		 throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. sum_div with infinite values.");
	  }
	  min[0] = filib::inf(x[0]);
	  max[0] = filib::sup(x[0]);
	  for(unsigned int i=1; i<x.size();i++){
		   if(x[i].isInfinite()){
			 throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. sum_div with infinite values.");
		   }
		   min[i] = filib::sup(x[i]);
		   max[i] = filib::inf(x[i]);
		   if(filib::inf(x[i])<=0. ){
			 throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. sum_div with values <=0.");
		   }
	   }
	   return interval<N,K,E>(mc::sum_div(min,coeff),mc::sum_div(max,coeff));
  }

    template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> xlog_sum (const std::vector<interval<N,K,E>> &x, const std::vector<double> &coeff )
	{
		if(filib::inf(x[0])<=0. ){
			 throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. xlog_sum with values <=0.");
		}
		if(x[0].isInfinite()){
			 throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. xlog_sum with infinite values.");
		}
		// Special case
		if(x.size()==1){
			const double valL = filib::inf(x[0]) * std::log(coeff[0]*filib::inf(x[0]));
			const double valU = filib::sup(x[0]) * std::log(coeff[0]*filib::sup(x[0]));
		    const double m = mc::mid(filib::inf(x[0]),filib::sup(x[0]),std::exp(-1.)/coeff[0]);
			return interval<N,K,E>( m*std::log(coeff[0]*m),std::max(valL,valU));
		}

		std::vector<double> corner1 = {filib::inf(x[0])}; corner1.reserve(x.size());
		std::vector<double> corner2 = {filib::sup(x[0])}; corner2.reserve(x.size());
		std::vector<double> rusr = {coeff[0]}; rusr.reserve(x.size()+coeff.size());// used for root finding
		std::vector<double> minPoint(x.size());
		for(size_t i = 1; i<x.size();i++){
			corner1.push_back(filib::sup(x[i]));
			corner2.push_back(filib::sup(x[i]));
			rusr.push_back(coeff[i]);
			rusr.push_back(filib::inf(x[i]));
			minPoint[i] = filib::inf(x[i]);
			if(filib::inf(x[i])<=0. ){
				 throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. xlog_sum with values <=0.");
			}
			if(x[i].isInfinite()){
				 throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. xlog_sum with infinite values.");
			}
		}
		const double upper = std::max(mc::xlog_sum(corner1,coeff), mc::xlog_sum(corner2,coeff));

		rusr.push_back(0.); // We are looking for the root of the derivative
		const int size = rusr.size();
		const double zmin = mc::_compute_root(filib::inf(x[0]), filib::inf(x[0]), filib::sup(x[0]), mc::xlog_sum_dfunc, mc::xlog_sum_ddfunc, rusr.data(), &size);
		minPoint[0] = mc::mid(filib::inf(x[0]), filib::sup(x[0]), zmin);
		double lower = mc::xlog_sum(minPoint, coeff);
		return interval<N,K,E>(lower,upper);
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
    interval<N,K,E> euclidean_norm_2d (const interval<N,K,E> &x, const interval<N,K,E> &y)
	{
		const double minPointX = mc::mid(filib::inf(x),filib::sup(x),0.);
		const double minPointY = mc::mid(filib::inf(y),filib::sup(y),0.);
		// max is one of the 4 corners
		const std::vector<double> corners = { mc::euclidean_norm_2d(filib::inf(x),filib::inf(y)), mc::euclidean_norm_2d(filib::inf(x),filib::sup(y)),
		                                      mc::euclidean_norm_2d(filib::sup(x),filib::inf(y)), mc::euclidean_norm_2d(filib::sup(x),filib::sup(y)) };
		const unsigned cornerIndex = mc::argmax(4,corners.data());
		return interval<N,K,E>(mc::euclidean_norm_2d(minPointX,minPointY),corners[cornerIndex]);
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N, K, E> expx_times_y(const interval<N, K, E> &x, const interval<N, K, E> &y)
	{
		double minVal = 0;
		double maxVal = 0;
		if (filib::inf(y) < 0) {
			minVal = mc::expx_times_y(filib::sup(x), filib::inf(y));
		}
		else {
			minVal = mc::expx_times_y(filib::inf(x), filib::inf(y));
		}
		if (filib::sup(y) < 0) {
			maxVal = mc::expx_times_y(filib::inf(x), filib::sup(y));
		}
		else {
			maxVal = mc::expx_times_y(filib::sup(x), filib::sup(y));
		}
		return interval<N, K, E>(minVal, maxVal);
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N, K, E> covariance_function(const interval<N, K, E> &x, const double type)
	{
		if (filib::inf(x) < 0) {
			throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. covariance_function with values <0.");
		}

		return interval<N, K, E>( mc::covariance_function(filib::sup(x),type), mc::covariance_function(filib::inf(x),type) );
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N, K, E> acquisition_function(const interval<N, K, E> &x, const interval<N, K, E> &y, const double type, const double fmin)
	{
		if (filib::inf(y) < 0) {
			throw std::runtime_error("mc::Filib\t Error in mcfilib.hpp. acquisition_function with sigma values <0.");
		}
        switch((int)type){
			case 1: // lower confidence bound
			{
				return x - fmin*y;
			}
			case 2: // expected improvement
			{
				return interval<N, K, E>( mc::acquisition_function(filib::sup(x), filib::inf(y), type, fmin), mc::acquisition_function(filib::inf(x), filib::sup(y), type, fmin) );
			}
			case 3: // probability of improvement
			{
				// First the trivial case: sigma=0
				if (filib::sup(y)==0.) {
					if (filib::sup(x-fmin)<0.) {			// sigma=0, mu-fmin<0
						return interval<N, K, E>( 1., 1. );
					} else if (filib::inf(x-fmin)>=0.) { 	// sigma=0, mu-fmin>0
						return interval<N, K, E>( 0., 0. );
					} else { 								// sigma=0, 0 in [(mu-fmin)^L,(mu-fmin)^U]
						return interval<N, K, E>( 0., 1. );
					}
				}
				// Now the other trivial case: sigma>0 --> just use interval extensions of factorable representation
				if (filib::inf(y)>0.) {
					return mc::Op< interval<N, K, E> >::erf(1./std::sqrt(2)*((fmin-x)/y))/2.+0.5;
				}
				// What remains is the more complex one: sigma>=0
				double lower, upper;
				if (filib::inf(x-fmin)>=0.) {	// sigma>=0, mu-fmin>0 --> decreasing in x, inreasing in y
					lower = 0.;
					upper = std::erf(1./std::sqrt(2)*((fmin-filib::inf(x))/filib::sup(y)))/2.+0.5;
				} else if (filib::sup(x-fmin)<0.) {	// sigma>=0, mu-fmin<0 --> decreasing in x, decreasing in y
					lower = std::erf(1./std::sqrt(2)*((fmin-filib::sup(x))/filib::sup(y)))/2.+0.5;
					upper = 1.;
				} else {
					lower = 0.;
					upper = 1.;
				}
				return interval<N, K, E>( lower, upper );
			}
			default:
			  throw std::runtime_error("mc::Filib\t Acquisition function called with an unknown type.\n");
        }
	}

	template < typename N, rounding_strategy K = filib::native_switched, interval_mode E = filib::i_mode_extended>
	interval<N, K, E> gaussian_probability_density_function(const interval<N, K, E> &x)
	{
		double minVal = std::min(mc::gaussian_probability_density_function(filib::inf(x)),mc::gaussian_probability_density_function(filib::sup(x)));
		double maxVal;
		if (filib::inf(x) <= 0. && 0. <= filib::sup(x)) {
			maxVal = mc::gaussian_probability_density_function(0.);
		}
		else{
			maxVal = std::max(mc::gaussian_probability_density_function(filib::inf(x)),mc::gaussian_probability_density_function(filib::sup(x)));
		}

		return interval<N, K, E>(minVal, maxVal);
	}

} // end namespace filib


#include "IAPWS/iapwsFilib.h"

namespace mc
{

//! @brief Specialization of the structure mc::Op for use of the type filib::interval<double> of <A href="http://www.math.uni-wuppertal.de/~xsc/software/filib.html">FILIB++</A> as a template parameter in other MC++ types
template <> struct Op< filib::interval<double> >
{
  typedef filib::interval<double> T;
  static T point( const double c ) { return T(c); }
  static T zeroone() { return T(0.,1.); }
  static void I(T& x, const T& y) { x = y; }
  static double l(const T& x) { return filib::inf(x); }
  static double u(const T& x) { return filib::sup(x); }
  static double abs (const T& x) { return filib::mag(x);  }
  static double mid (const T& x) { return filib::mid(x);  }
  static double diam(const T& x) { return filib::diam(x); }
  static T inv (const T& x) { return T(1.)/x;  }
  static T sqr (const T& x) { return filib::sqr(x);  }
  static T sqrt(const T& x) {
	  if(x.inf()==0){ // this is done to avoid underflows -- filib returns e-324 numbers for sqrt(0)
		  return T(0, filib::sqrt(x).sup());
	  }
	  return filib::sqrt(x);
  }
  static T exp (const T& x) { return filib::exp(x);  }
  static T log (const T& x) { return filib::log(x);  }
  static T xlog(const T& x) { return T(mc::xlog(mc::mid(filib::inf(x),filib::sup(x),std::exp(-1.))), std::max(mc::xlog(filib::inf(x)), mc::xlog(filib::sup(x)))); }
  static T fabsx_times_x(const T& x) { return T( mc::fabsx_times_x(filib::inf(x)),mc::fabsx_times_x(filib::sup(x))); }
  static T xexpax(const T& x, const double a) { return filib::xexpax(x,a); }
  // !!THE RESULT IS NOT VERIFIED!!
  static T centerline_deficit(const T& x, const double xLim, const double type) { return filib::centerline_deficit(x,xLim,type); }
  static T wake_profile(const T& x, const double type) { return filib::wake_profile(x,type); }
  static T wake_deficit(const T& x, const T& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return filib::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static T power_curve(const T& x, const double type) { return filib::power_curve(x,type); }
  static T lmtd(const T& x,const T& y) { return filib::lmtd(x,y); }
  static T rlmtd(const T& x,const T& y) { return filib::rlmtd(x,y); }
  static T mid(const T& x, const T& y, const double k) { return filib::mid(x, y, k); } 
  static T pinch(const T& Th, const T& Tc, const T& Tp) { return filib::pinch(Th, Tc, Tp); }
  static T euclidean_norm_2d(const T& x,const T& y) { return filib::euclidean_norm_2d(x,y); }
  static T expx_times_y(const T& x,const T& y) { return filib::expx_times_y(x,y); }
  static T vapor_pressure(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
							const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return T( mc::vapor_pressure(filib::inf(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10), mc::vapor_pressure(filib::sup(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10) ); }
  static T ideal_gas_enthalpy(const T& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							  const double p7 = 0) { return T( mc::ideal_gas_enthalpy(filib::inf(x), x0,type,p1,p2,p3,p4,p5,p6,p7), mc::ideal_gas_enthalpy(filib::sup(x), x0,type,p1,p2,p3,p4,p5,p6,p7) ); }
  static T saturation_temperature(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
								  const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return T( mc::saturation_temperature(filib::inf(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10), mc::saturation_temperature(filib::sup(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10) );}
  static T enthalpy_of_vaporization(const T& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { return T( mc::enthalpy_of_vaporization(filib::sup(x), type,p1,p2,p3,p4,p5,p6), mc::enthalpy_of_vaporization(filib::inf(x), type,p1,p2,p3,p4,p5,p6) ); }
  static T cost_function(const T& x, const double type, const double p1, const double p2, const double p3) {return filib::cost_function(x, type, p1,p2,p3);} // currently only Guthrie implemented
  static T nrtl_tau(const T& x, const double a, const double b, const double e, const double f) { return filib::nrtl_tau(x,a,b,e,f); }
  static T nrtl_dtau(const T& x, const double b, const double e, const double f) { return filib::nrtl_dtau(x,b,e,f); }
  static T nrtl_G(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return filib::exp(-alpha*nrtl_tau(x,a,b,e,f));}
  static T nrtl_Gtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return xexpax(nrtl_tau(x,a,b,e,f),-alpha);}
  static T nrtl_Gdtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return nrtl_G(x,a,b,e,f,alpha)*nrtl_dtau(x,b,e,f);}
  static T nrtl_dGtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return -alpha*nrtl_Gtau(x,a,b,e,f,alpha)*nrtl_dtau(x,b,e,f);}
  static T iapws(const T& x, const double type) { return filib::iapws(x,type); }
  static T iapws(const T& x, const T& y, const double type) { return filib::iapws(x,y,type); }
  static T p_sat_ethanol_schroeder(const T& x) { return T( mc::p_sat_ethanol_schroeder(filib::inf(x)), mc::p_sat_ethanol_schroeder(filib::sup(x)) ); }
  static T rho_vap_sat_ethanol_schroeder(const T& x) { return T( mc::rho_vap_sat_ethanol_schroeder(filib::inf(x)), mc::rho_vap_sat_ethanol_schroeder(filib::sup(x)) ); }
  static T rho_liq_sat_ethanol_schroeder(const T& x) { return T( mc::rho_liq_sat_ethanol_schroeder(filib::sup(x)), mc::rho_liq_sat_ethanol_schroeder(filib::inf(x)) ); }
  static T covariance_function(const T& x, const double type) { return filib::covariance_function(x,type); }
  static T acquisition_function(const T& x, const T& y, const double type, const double fmin) { return filib::acquisition_function(x,y,type,fmin); }
  static T gaussian_probability_density_function(const T& x) { return filib::gaussian_probability_density_function(x); }
  static T regnormal(const T& x, const double a, const double b) { return T( mc::regnormal(filib::inf(x),a,b), mc::regnormal(filib::sup(x),a,b) ); }
  static T fabs(const T& x) { return filib::abs(x); }
  static T sin (const T& x) { return filib::sin(x);  }
  static T cos (const T& x) { return filib::cos(x);  }
  static T tan (const T& x) { return filib::tan(x);  }
  static T asin(const T& x) { return filib::asin(x); }
  static T acos(const T& x) { return filib::acos(x); }
  static T atan(const T& x) { return filib::atan(x); }
  static T sinh(const T& x) { return filib::sinh(x); }
  static T cosh(const T& x) { return filib::cosh(x); }
  static T tanh(const T& x) { return filib::tanh(x); }
  static T coth(const T& x) { return filib::coth(x); }
  static T asinh(const T& x) { return filib::asinh(x); }
  static T acosh(const T& x) { return filib::acosh(x); }
  static T atanh(const T& x) { return filib::atanh(x); }
  static T acoth(const T& x) { return filib::acoth(x); }
  static T erf (const T& x) { return T(std::erf(filib::inf(x)),std::erf(filib::sup(x))); }
  static T erfc(const T& x) { return T(1.)-T(std::erf(filib::inf(x)),std::erf(filib::sup(x))); }
  static T fstep(const T& x) { throw std::runtime_error("operation not permitted"); }
  static T bstep(const T& x) { throw std::runtime_error("operation not permitted"); }
  static T hull(const T& x, const T& y) { return x.hull(y); }
  static T min (const T& x, const T& y) { return filib::min(x,y); }
  static T max (const T& x, const T& y) { return filib::max(x,y); }
  static T pos (const T& x ) { return filib::pos(x); }
  static T neg (const T& x ) { return filib::neg(x); }
  static T lb_func (const T& x, const double lb ) { return x.imax(lb); }
  static T ub_func (const T& x, const double ub ) { return x.imin(ub); }
  static T bounding_func (const T& x, const double lb, const double ub ) { return (x.imax(lb)).imin(ub); }
  static T squash_node (const T& x, const double lb, const double ub ) { return (x.imax(lb)).imin(ub); }
  static T single_neuron(const std::vector<T> &x, const std::vector<double> &w, const double b , const int type) { return filib::single_neuron(x,w,b,type); }
  static T sum_div (const std::vector<T> &x, const std::vector<double> &coeff ) { return filib::sum_div(x,coeff); }
  static T xlog_sum (const std::vector<T> &x, const std::vector<double> &coeff ) { return filib::xlog_sum(x,coeff); }
  static T mc_print (const T& x, const int number ) { return T(filib::inf(x),filib::sup(x)); }
  static T arh (const T& x, const double k) { return filib::exp(-k/x); }
  static T cheb (const T& x, const unsigned n) { return T(-1.,1.); }
  template <typename X> static T pow(const X& x, const int n) { return filib::pow(x,n); } // defined above to avoid linker errors (added AVT.SVT, 27.03.2019)
  template <typename X> static T pow(const X& x, const double a) {
      if(x.inf()==0){ // this is done to avoid underflows -- filib returns e-324 numbers for pow(0,a)
		  return T(0, filib::pow(x,a).sup());
	  }
      return filib::pow(x,a);
  } // defined above to avoid linker errors (added AVT.SVT, 27.03.2019)
  template <typename X,typename Y> static T pow(const X& x, const Y& y) { return filib::pow(x,y); }
  static T prod (const unsigned int n, const T* x) { return n? x[0] * prod(n-1, x+1): 1.; }
  static T monom (const unsigned int n, const T* x, const unsigned* k) { return n? filib::power(x[0], k[0]) * monom(n-1, x+1, k+1): 1.; }
  static bool inter(T& xIy, const T& x, const T& y)
  {
    // xIy = x.intersect(y); // the intersect function is bugged in filib++ version 3.0.2. If i_mode=0 in filib then the result of intersect is incorrect
    // return true; // obviously we dont want to just return true every time
	if( (filib::inf(x) > filib::sup(y) && !isequal(filib::inf(x),filib::sup(y)))
	||  (filib::inf(y) > filib::sup(x) && !isequal(filib::inf(y),filib::sup(x))) ) return false;
	xIy = T(std::max( filib::inf(x), filib::inf(y) ), std::min(filib::sup(x),filib::sup(y)));
	return true;
  }
  static bool eq(const T& x, const T& y) { return x.seq(y); }
  static bool ne(const T& x, const T& y) { return x.sne(y); }
  static bool lt(const T& x, const T& y) { return x.slt(y); }
  static bool le(const T& x, const T& y) { return x.sle(y); }
  static bool gt(const T& x, const T& y) { return x.sgt(y); }
  static bool ge(const T& x, const T& y) { return x.sge(y); }
};

//! @brief Specialization of the structure mc::Op for use of the type filib::interval<double,filib::native_switched,filib::i_mode_extended> of <A href="http://www.math.uni-wuppertal.de/~xsc/software/filib.html">FILIB++</A> as a template parameter in other MC++ types
template <> struct Op< filib::interval<double,filib::native_switched,filib::i_mode_extended> >
{
  typedef filib::interval<double,filib::native_switched,filib::i_mode_extended> T;
  static T point( const double c ) { return T(c); }
  static T zeroone() { return T(0.,1.); }
  static void I(T& x, const T& y) { x = y; }
  static double l(const T& x) { return filib::inf(x); }
  static double u(const T& x) { return filib::sup(x); }
  static double abs (const T& x) { return filib::mag(x);  }
  static double mid (const T& x) { return filib::mid(x);  }
  static double diam(const T& x) { return filib::diam(x); }
  static T inv (const T& x) { return T(1.)/x;  }
  static T sqr (const T& x) { return filib::sqr(x);  }
  static T sqrt(const T& x) {
	  if(x.inf()==0){ // this is done to avoid underflows -- filib returns e-324 numbers for sqrt(0)
		  return T(0, filib::sqrt(x).sup());
	  }
	  return filib::sqrt(x);
  }
  static T exp (const T& x) { return filib::exp(x);  }
  static T log (const T& x) { return filib::log(x);  }
  static T xlog(const T& x) { return T( mc::xlog(mc::mid(filib::inf(x),filib::sup(x),std::exp(-1.))),std::max(mc::xlog(filib::inf(x)),mc::xlog(filib::sup(x)))); }
  static T fabsx_times_x(const T& x) { return T( mc::fabsx_times_x(filib::inf(x)),mc::fabsx_times_x(filib::sup(x))); }
  static T xexpax(const T& x, const double a) { return filib::xexpax(x,a); }
  // !!THE RESULT IS NOT VERIFIED!!
  static T centerline_deficit(const T& x, const double xLim, const double type) { return filib::centerline_deficit(x,xLim,type); }
  static T wake_profile(const T& x, const double type) { return filib::wake_profile(x,type); }
  static T wake_deficit(const T& x, const T& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return filib::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static T power_curve(const T& x, const double type) { return filib::power_curve(x,type); }
  static T lmtd(const T& x,const T& y) { return filib::lmtd(x,y); }
  static T rlmtd(const T& x,const T& y) { return filib::rlmtd(x,y); }
  static T mid(const T& x, const T& y, const double k) { return filib::mid(x, y, k); } 
  static T pinch(const T& Th, const T& Tc, const T& Tp) { return filib::pinch(Th, Tc, Tp); }
  static T euclidean_norm_2d(const T& x,const T& y) { return filib::euclidean_norm_2d(x,y); }
  static T expx_times_y(const T& x,const T& y) { return filib::expx_times_y(x, y); }
  static T vapor_pressure(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
							const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return T( mc::vapor_pressure(filib::inf(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10), mc::vapor_pressure(filib::sup(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10) ); }
  static T ideal_gas_enthalpy(const T& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							  const double p7 = 0) { return T( mc::ideal_gas_enthalpy(filib::inf(x), x0,type,p1,p2,p3,p4,p5,p6,p7), mc::ideal_gas_enthalpy(filib::sup(x), x0,type,p1,p2,p3,p4,p5,p6,p7) ); }
  static T saturation_temperature(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
								  const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return T( mc::saturation_temperature(filib::inf(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10), mc::saturation_temperature(filib::sup(x),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10) );}
  static T enthalpy_of_vaporization(const T& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { return T( mc::enthalpy_of_vaporization(filib::sup(x), type,p1,p2,p3,p4,p5,p6), mc::enthalpy_of_vaporization(filib::inf(x), type,p1,p2,p3,p4,p5,p6) ); }
  static T cost_function(const T& x, const double type, const double p1, const double p2, const double p3) {return filib::cost_function(x, type, p1,p2,p3);} // currently only Guthrie implemented
  static T nrtl_tau(const T& x, const double a, const double b, const double e, const double f) { return filib::nrtl_tau(x,a,b,e,f); }
  static T nrtl_dtau(const T& x, const double b, const double e, const double f) { return filib::nrtl_dtau(x,b,e,f); }
  static T nrtl_G(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return filib::exp(-alpha*nrtl_tau(x,a,b,e,f));}
  static T nrtl_Gtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return xexpax(nrtl_tau(x,a,b,e,f),-alpha);}
  static T nrtl_Gdtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return nrtl_G(x,a,b,e,f,alpha)*nrtl_dtau(x,b,e,f);}
  static T nrtl_dGtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return -alpha*nrtl_Gtau(x,a,b,e,f,alpha)*nrtl_dtau(x,b,e,f);}
  static T iapws(const T& x, const double type) { return filib::iapws(x,type); }
  static T iapws(const T& x, const T& y, const double type) { return filib::iapws(x,y,type); }
  static T p_sat_ethanol_schroeder(const T& x) { return T( mc::p_sat_ethanol_schroeder(filib::inf(x)), mc::p_sat_ethanol_schroeder(filib::sup(x)) ); }
  static T rho_vap_sat_ethanol_schroeder(const T& x) { return T( mc::rho_vap_sat_ethanol_schroeder(filib::inf(x)), mc::rho_vap_sat_ethanol_schroeder(filib::sup(x)) ); }
  static T rho_liq_sat_ethanol_schroeder(const T& x) { return T( mc::rho_liq_sat_ethanol_schroeder(filib::sup(x)), mc::rho_liq_sat_ethanol_schroeder(filib::inf(x)) ); }
  static T covariance_function(const T& x, const double type) { return filib::covariance_function(x,type); }
  static T acquisition_function(const T& x, const T& y, const double type, const double fmin) { return filib::acquisition_function(x,y,type,fmin); }
  static T gaussian_probability_density_function(const T& x) { return filib::gaussian_probability_density_function(x); }
  static T regnormal(const T& x, const double a, const double b) { return T( mc::regnormal(filib::inf(x),a,b), mc::regnormal(filib::sup(x),a,b) ); }
  static T fabs(const T& x) { return filib::abs(x); }
  static T sin (const T& x) { return filib::sin(x);  }
  static T cos (const T& x) { return filib::cos(x);  }
  static T tan (const T& x) { return filib::tan(x);  }
  static T asin(const T& x) { return filib::asin(x); }
  static T acos(const T& x) { return filib::acos(x); }
  static T atan(const T& x) { return filib::atan(x); }
  static T sinh(const T& x) { return filib::sinh(x); }
  static T cosh(const T& x) { return filib::cosh(x); }
  static T tanh(const T& x) { return filib::tanh(x); }
  static T coth(const T& x) { return filib::coth(x); }
  static T asinh(const T& x) { return filib::asinh(x); }
  static T acosh(const T& x) { return filib::acosh(x); }
  static T atanh(const T& x) { return filib::atanh(x); }
  static T acoth(const T& x) { return filib::acoth(x); }
  static T erf (const T& x) { return T(std::erf(filib::inf(x)),std::erf(filib::sup(x))); }
  static T erfc(const T& x) { return T(1.)-T(std::erf(filib::inf(x)),std::erf(filib::sup(x))); }
  static T fstep(const T& x) { throw std::runtime_error("operation not permitted"); }
  static T bstep(const T& x) { throw std::runtime_error("operation not permitted"); }
  static T hull(const T& x, const T& y) { return x.hull(y); }
  static T min (const T& x, const T& y) { return x.imin(y); }
  static T max (const T& x, const T& y) { return x.imax(y); }
  static T pos (const T& x ) { return x.imax(mc::machprec()); }
  static T neg (const T& x ) { return x.imin(-mc::machprec()); }
  static T lb_func (const T& x, const double lb ) { return x.imax(lb); }
  static T ub_func (const T& x, const double ub ) { return x.imin(ub); }
  static T bounding_func (const T& x, const double lb, const double ub ) { return (x.imax(lb)).imin(ub); }
  static T squash_node (const T& x, const double lb, const double ub ) { return (x.imax(lb)).imin(ub); }
  static T single_neuron(const std::vector<T> &x, const std::vector<double> &w, const double b ,const int type) { return filib::single_neuron(x,w,b,type); }
  static T sum_div (const std::vector<T> &x, const std::vector<double> &coeff ) { return filib::sum_div(x,coeff); }
  static T xlog_sum (const std::vector<T> &x, const std::vector<double> &coeff )  { return filib::xlog_sum(x,coeff); }
  static T mc_print (const T& x, const int number ) { return T(filib::inf(x),filib::sup(x)); }
  static T arh (const T& x, const double k) { return filib::exp(-k/x); }
  static T cheb (const T& x, const unsigned n) { return T(-1.,1.); }
  template <typename X> static T pow(const X& x, const int n) { return filib::pow(x,n); }  // defined above to avoid linker errors (added AVT.SVT, 27.03.2019)
  template <typename X> static T pow(const X& x, const double a) {
      if(x.inf()==0){ // this is done to avoid underflows -- filib returns e-324 numbers for pow(0,a)
		  return T(0, filib::pow(x,a).sup());
	  }
      return filib::pow(x,a);
  } // defined above to avoid linker errors (added AVT.SVT, 27.03.2019)
  template <typename X,typename Y> static T pow(const X& x, const Y& y) { return filib::pow(x,y); }
  static T prod (const unsigned int n, const T* x) { return n? x[0] * prod(n-1, x+1): 1.; }
  static T monom (const unsigned int n, const T* x, const unsigned* k) { return n? filib::power(x[0], k[0]) * monom(n-1, x+1, k+1): 1.; }
  static bool inter(T& xIy, const T& x, const T& y)
  {
    xIy = x.intersect(y);
    return !xIy.isEmpty();
  }
  static bool eq(const T& x, const T& y) { return x.seq(y); }
  static bool ne(const T& x, const T& y) { return x.sne(y); }
  static bool lt(const T& x, const T& y) { return x.slt(y); }
  static bool le(const T& x, const T& y) { return x.sle(y); }
  static bool gt(const T& x, const T& y) { return x.sgt(y); }
  static bool ge(const T& x, const T& y) { return x.sge(y); }
};

} // namespace mc

#endif

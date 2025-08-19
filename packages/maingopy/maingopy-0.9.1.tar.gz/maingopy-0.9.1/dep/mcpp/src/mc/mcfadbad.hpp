// Copyright (C) 2009-2017 Benoit Chachuat, Imperial College London.
// All Rights Reserved.
// This code is published under the Eclipse Public License.

#ifndef MC__MCFADBAD_HPP
#define MC__MCFADBAD_HPP

#include <iomanip>
#include "fadiff.h"
#include "mcfunc.hpp"

namespace fadbad
{

//! @brief Exceptions of mc::McCormick
  class Exceptions
  {
  public:
    //! @brief Enumeration type for McCormick exception handling
    enum TYPE{
      SQRT = 0,	//!< Square-root with nonpositive values in range
	  DPOW, //!< Power with negative double value in exponent
    };
    //! @brief Constructor for error <a>ierr</a>
    Exceptions( TYPE ierr ) : _ierr( ierr ){}
    //! @brief Inline function returning the error flag
    int ierr(){ return _ierr; }
    //! @brief Return error description
    std::string what(){
      switch( _ierr ){
      case SQRT:
        return "mc::mcFadbad\t Derivative of square root with 0 in range.";
	  case DPOW:
		return "mc::mcFadbad\t Derivative of x^a with x = 0 and a in (0,1).";
      }
      return "mc::mcFadbad\t Undocumented error.";
    }

  private:
    TYPE _ierr;
  };

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> pow2(const FTypeName<T,N>& a, const int b)
{
	FTypeName<T,N> c(Op<T>::myPow(a.val(),b));
	if (!a.depend()) return c;
	T tmp(b*Op<T>::myPow(a.val(),b-1));
	c.setDepend(a);
	for(unsigned int i=0;i<N;++i) c[i]=tmp*a[i];
	return c;
}

template <typename T >
INLINE2 FTypeName<T,0> pow2(const FTypeName<T,0>& a, const int b)
{
	FTypeName<T,0> c(Op<T>::myPow(a.val(),b));
	if (!a.depend()) return c;
	T tmp(b*Op<T>::myPow(a.val(),b-1));
	c.setDepend(a);
	for(unsigned int i=0;i<c.size();++i) c[i]=tmp*a[i];
	return c;
}

template <typename T>
INLINE2 T cheb(const T& a, const unsigned b)
{
  switch( b ){
    case 0: return Op<T>::myOne();
    case 1: return a;
    default: return Op<T>::myTwo() * a * cheb(a,b-1) - cheb(a,b-2); }
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> cheb(const FTypeName<T,N>& a, const unsigned b)
{
	FTypeName<T,N> c(cheb(a.val(),b));
	//FTypeName<T,N> c(Op<T>::myCheb(a.val(),b));
	if (!a.depend()) return c;
        // dTn/dx = n*Un-1(x)
        // Un-1(x) = 2*(T1(x)+T3(x)+...+Tn-1(x)) if n even
        //           2*(T0(x)+T2(x)+...+Tn-1(x))-1 if n odd
	T tmp(0.);
        if( b%2 ){ // odd case
          for( unsigned k=0; k<b; k+=2 ) tmp += cheb(a.val(),k);
          //for( unsigned k=0; k<b; k+=2 ) tmp += Op<T>::myCheb(a.val(),k);
          tmp *= 2.; tmp -= 1.;
        }
        else{ // even case
          for( unsigned k=1; k<b; k+=2 ) tmp += cheb(a.val(),k);
          //for( unsigned k=1; k<b; k+=2 ) tmp += Op<T>::myCheb(a.val(),k);
          tmp *= 2.;
        }
	c.setDepend(a);
	for(unsigned int i=0;i<N;++i) c[i]=tmp*a[i];
	return c;
}

template <typename T>
INLINE2 FTypeName<T,0> cheb(const FTypeName<T,0>& a, const unsigned b)
{
	FTypeName<T,0> c(cheb(a.val(),b));
	//FTypeName<T,0> c(Op<T>::myCheb(a.val(),b));
	if (!a.depend()) return c;
        // dTn/dx = n*Un-1(x)
        // Un-1(x) = 2*(T1(x)+T3(x)+...+Tn-1(x)) if n even
        //           2*(T0(x)+T2(x)+...+Tn-1(x))-1 if n odd
	T tmp(0.);
        if( b%2 ){ // odd case
          for( unsigned k=0; k<b; k+=2 ) tmp += cheb(a.val(),k);
          //for( unsigned k=0; k<b; k+=2 ) tmp += Op<T>::myCheb(a.val(),k);
          tmp *= 2.; tmp -= 1.;
        }
        else{ // even case
          for( unsigned k=1; k<b; k+=2 ) tmp += cheb(a.val(),k);
          //for( unsigned k=1; k<b; k+=2 ) tmp += Op<T>::myCheb(a.val(),k);
          tmp *= 2.;
        }
	c.setDepend(a);
	for(unsigned int i=0;i<c.size();++i) c[i]=tmp*a[i];
	return c;
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> fabs (const FTypeName<T,N>& a)
{
    if (Op<T>::myGt(a.val(), 0)) {
        return a;
    } else if (Op<T>::myLt(a.val(), 0)){
        return -a;
    } else  {
        return 0. * a;;
    }
}

template <typename T>
INLINE2 FTypeName<T,0> fabs (const FTypeName<T,0>& a)
{
    if (Op<T>::myGt(a.val(), 0)) {
        return a;
    } else if (Op<T>::myLt(a.val(), 0)){
        return -a;
    } else  {
        return 0. * a;;
    }
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> max (const FTypeName<T,N>& a, const FTypeName<T,N>& b)
{
    if (Op<T>::myGt(a.val(), b.val())) {
        return a;
    } else if (Op<T>::myLt(a.val(), b.val())){
        return b;
    } else  {
        return 0.5 * (a+b);
    }
}

template <typename T>
INLINE2 FTypeName<T,0> max (const FTypeName<T,0>& a, const FTypeName<T,0>& b)
{
    if (Op<T>::myGt(a.val(), b.val())) {
        return a;
    } else if (Op<T>::myLt(a.val(), b.val())){
        return b;
    } else  {
        return 0.5 * (a+b);
    }
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> min (const FTypeName<T,N>& a, const FTypeName<T,N>& b)
{
    if (Op<T>::myGt(a.val(), b.val())) {
        return b;
    } else if (Op<T>::myLt(a.val(), b.val())){
        return a;
    } else  {
        return 0.5 * (a+b);
    }
}

template <typename T>
INLINE2 FTypeName<T,0> min (const FTypeName<T,0>& a, const FTypeName<T,0>& b)
{
    if (Op<T>::myGt(a.val(), b.val())) {
        return b;
    } else if (Op<T>::myLt(a.val(), b.val())){
        return a;
    } else  {
        return 0.5 * (a+b);
    }
}

//this implementation is used for all AD types
template <typename T>
INLINE2 T xlog (const T& x)
{

    return x*Op<T>::myLog(x);
}

//this implementation is used for all AD types
template <typename T>
INLINE2 T tanh (const T& x)
{

    return Op<T>::myOne()-Op<T>::myTwo()/(Op<T>::myExp(Op<T>::myTwo()*x)+Op<T>::myOne());
}

//this implementation is used for all AD types
template <typename T>
INLINE2 T sinh (const T& x)
{

    return (Op<T>::myExp(x) - Op<T>::myExp(-x))/Op<T>::myTwo();
}

//this implementation is used for all AD types
template <typename T>
INLINE2 T cosh (const T& x)
{

    return (Op<T>::myExp(x) + Op<T>::myExp(-x))/Op<T>::myTwo();
}

//this implementation is used for all AD types
template <typename T>
INLINE2 T xexpax (const T& x, const double a)
{
    return x*Op<T>::myExp(a*x);
}

//this implementation is used for all AD types
template <typename T>
INLINE2 T expx_times_y (const T& x,const T& y)
{
    return Op<T>::myExp(x)*y;
}

//@AVT.SVT: 2024
template <typename T>
INLINE2 T single_neuron (const std::vector<T>& x, const std::vector<double>& w, const double b, const int type)
{
	T dummy = b;
	for(size_t i = 0; i<x.size();i++){
		dummy += w[i]*x[i];
	}
  return Op<T>::myOne()-Op<T>::myTwo()/(Op<T>::myExp(Op<T>::myTwo()*dummy)+Op<T>::myOne()); // tanh(dummy)
}

//@AVT.SVT: 11.07.2018
template <typename T>
INLINE2 T sum_div (const std::vector<T>& x, const std::vector<double>& coeff)
{
	T denom = coeff[1]*x[0];
	for(size_t i = 1; i<x.size();i++){
		denom += coeff[i+1]*x[i];
	}
	return coeff[0]*x[0]/denom;
}

//@AVT.SVT: 03.07.2019
template <typename T>
INLINE2 T xlog_sum (const std::vector<T>& x, const std::vector<double>& coeff)
{
	T dummy = 0.;
	for(size_t i = 0; i<x.size();i++){
		dummy += coeff[i]*x[i];
	}
	return x[0]*Op<T>::myLog(dummy);
}

//this implementation is used for all AD types
template <typename T>
INLINE2 T fabsx_times_x (const T& x)
{
    if(Op<T>::myGt(x.val(),Op<T>::myZero())){
      return Op<T>::myPow(x,2);
    }
	else{
      return -Op<T>::myPow(x,2);
	}
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> lmtd (const FTypeName<T,N>& a, const FTypeName<T,N>& b)
{
    if(Op<T>::myEq(a.val(), b.val())){
      FTypeName<T,N> c(a.val());
	  if (!a.depend() || !b.depend()) return c;
      c.setDepend(a,b);
       // Return function which has same first and second derivatives as lmtd on diagonal:
	  return (1./2.)*a - (1./12.)*a*log(a) + (1./12.)*a*log(b) + (1./2.)*b - (1./12.)*b*log(b) + (1./12.)*b*log(a);
    }
    return ((a-b)/(log(a)-log(b)));
}

template <typename T>
INLINE2 FTypeName<T,0> lmtd (const FTypeName<T,0>& a, const FTypeName<T,0>& b)
{
    if(Op<T>::myEq(a.val(), b.val())){
      FTypeName<T,0> c(a.val());
	  if (!a.depend() || !b.depend()) return c;
      c.setDepend(a,b);
       // Return function which has same first and second derivatives as lmtd on diagonal:
	  return (1./2.)*a - (1./12.)*a*log(a) + (1./12.)*a*log(b) + (1./2.)*b - (1./12.)*b*log(b) + (1./12.)*b*log(a);
    }
    return ((a-b)/(log(a)-log(b)));
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> rlmtd (const FTypeName<T,N>& a, const FTypeName<T,N>& b)
{
    if(Op<T>::myEq(a.val(), b.val())){
      FTypeName<T,N> c(1./a.val());
      if (!a.depend() || !b.depend()) return c;
      // Return function which has same first and second derivatives as rlmtd on diagonal:
	  return (4.0*a*b* sqrt(1.0 / pow(a*b, 3))) / 3.0 - 1.0 / (6.0 * b) - 1.0 / (6.0 * a);
    }
    return ((log(a)-log(b))/(a-b));
}

template <typename T>
INLINE2 FTypeName<T,0> rlmtd (const FTypeName<T,0>& a, const FTypeName<T,0>& b)
{
    if(Op<T>::myEq(a.val(), b.val())){
      FTypeName<T,0> c(1./a.val());
      if (!a.depend() || !b.depend()) return c;
      // Return function which has same first and second derivatives as rlmtd on diagonal:
	  return (4.0*a*b* sqrt(1.0 / pow(a*b, 3))) / 3.0 - 1.0 / (6.0 * b) - 1.0 / (6.0 * a);
    }
    return ((log(a)-log(b))/(a-b));
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T, N> mid(const FTypeName<T, N>& a, const FTypeName<T, N>& b, const double k)
{
	if ((Op<T>::myGe(a.val(), b.val()) && Op<T>::myGe(k, a.val())) || (Op<T>::myGe(a.val(), k) && Op<T>::myGe(b.val(), a.val()))) {
		return a;
	}
	else if ((Op<T>::myGe(b.val(), a.val()) && Op<T>::myGe(k, b.val())) || (Op<T>::myGe(b.val(), k) && Op<T>::myGe(a.val(), b.val()))) {
		return b;
	}
	else {
		FTypeName<T, N> c(k);
		c.setDepend(a, b);
		for (unsigned int i = 0; i < N; ++i) c[i] = 0;
		return c;
	}
}

template <typename T>
INLINE2 FTypeName<T, 0> mid(const FTypeName<T, 0>& a, const FTypeName<T, 0>& b, const double k)
{
	if ((Op<T>::myGe(a.val(), b.val()) && Op<T>::myGe(k, a.val())) || (Op<T>::myGe(a.val(), k) && Op<T>::myGe(b.val(), a.val()))) {
		return a;
	}
	else if ((Op<T>::myGe(b.val(), a.val()) && Op<T>::myGe(k, b.val())) || (Op<T>::myGe(b.val(), k) && Op<T>::myGe(a.val(), b.val()))) {
		return b;
	}
	else {
		FTypeName<T, 0> c(k);
		c.setDepend(a, b);
		for (unsigned int i = 0; i < c.size(); ++i) c[i] = 0;
		return c;
	}
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T, N> pinch(const FTypeName<T, N>& Th, const FTypeName<T, N>& Tc, const FTypeName<T, N>& Tp)
{
	if (Op<T>::myGe(Tp.val(), Th.val()) && Op<T>::myGe(Tp.val(), Tc.val())) {
		FTypeName<T, N> c(0);
		c.setDepend(Th, Tc);
		c.setDepend(Tc, Tp);
		for (unsigned int i = 0; i < N; ++i) c[i] = 0;
		return c;
	}
	else if (Op<T>::myGe(Th.val(), Tp.val()) && Op<T>::myGe(Tc.val(), Tp.val())) {
		return Th - Tc;
	}
	else if (Op<T>::myGe(Th.val(), Tc.val())) {
		return Th - Tp;
	}
	else {
		return Tp - Tc;
	}
}

template <typename T>
INLINE2 FTypeName<T, 0> pinch(const FTypeName<T, 0>& Th, const FTypeName<T, 0>& Tc, const FTypeName<T, 0>& Tp)
{
	if (Op<T>::myGe(Tp.val(), Th.val()) && Op<T>::myGe(Tp.val(), Tc.val())) {
		FTypeName<T, 0> c(0);
		c.setDepend(Th, Tc);
		c.setDepend(Tc, Tp);
		for (unsigned int i = 0; i < c.size(); ++i) c[i] = 0;
		return c;
	}
	else if (Op<T>::myGe(Th.val(), Tp.val()) && Op<T>::myGe(Tc.val(), Tp.val())) {
		return Th - Tc;
	}
	else if (Op<T>::myGe(Th.val(), Tc.val())) {
		return Th - Tp;
	}
	else {
		return Tp - Tc;
	}
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> euclidean_norm_2d (const FTypeName<T,N>& a, const FTypeName<T,N>& b)
{
    if(Op<T>::myEq(a.val(), 0)){ // Derivative is a/sqrt(a^2+b^2)
      FTypeName<T,N> c(a.val());
	  if (!a.depend() || !b.depend()) return c;
      c.setDepend(a,b);
	  return 0.;
    }
    return sqrt(sqr(a) + sqr(b));
}

template <typename T>
INLINE2 FTypeName<T,0> euclidean_norm_2d (const FTypeName<T,0>& a, const FTypeName<T,0>& b)
{
    if(Op<T>::myEq(a.val(), 0)){
      FTypeName<T,0> c(a.val());
	  if (!a.depend() || !b.depend()) return c;
      c.setDepend(a,b);
	  return 0.;
    }
    return sqrt(sqr(a) + sqr(b));
}

//@AVT.SVT: 27.06.2017
template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> pos (const FTypeName<T,N>& a)
{
    FTypeName<T,N> c(mc::machprec());
	return max(a,c);
}

template <typename T>
INLINE2 FTypeName<T,0> pos (const FTypeName<T,0>& a)
{
	FTypeName<T,0> c(mc::machprec());
	return max(a,c);
}

//@AVT.SVT: 25.07.2017
template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> neg (const FTypeName<T,N>& a)
{
    FTypeName<T,N> c(-mc::machprec());
	return min(a,c);
}

template <typename T>
INLINE2 FTypeName<T,0> neg (const FTypeName<T,0>& a)
{
	FTypeName<T,0> c(-mc::machprec());
	return min(a,c);
}

//@AVT.SVT: 28.09.2017
template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> lb_func (const FTypeName<T,N>& a, const double lb)
{
    FTypeName<T,N> c(lb);
	return max(a,c);
}

template <typename T>
INLINE2 FTypeName<T,0> lb_func (const FTypeName<T,0>& a, const double lb)
{
	FTypeName<T,0> c(lb);
	return max(a,c);
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> ub_func (const FTypeName<T,N>& a, const double ub)
{
    FTypeName<T,N> c(ub);
	return min(a,c);
}

template <typename T>
INLINE2 FTypeName<T,0> ub_func (const FTypeName<T,0>& a, const double ub)
{
	FTypeName<T,0> c(ub);
	return min(a,c);
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> bounding_func (const FTypeName<T,N>& a, const double lb, const double ub)
{
    FTypeName<T,N> c1(lb);
    FTypeName<T,N> c2(ub);
	return min(max(a,c1),c2);
}

template <typename T>
INLINE2 FTypeName<T,0> bounding_func (const FTypeName<T,0>& a, const double lb, const double ub)
{
	FTypeName<T,0> c1(lb);
	FTypeName<T,0> c2(ub);
	return min(max(a,c1),c2);
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> squash_node (const FTypeName<T,N>& a, const double lb, const double ub)
{
    FTypeName<T,N> c1(lb);
    FTypeName<T,N> c2(ub);
	return min(max(a,c1),c2);
	// return a;
}

template <typename T>
INLINE2 FTypeName<T,0> squash_node (const FTypeName<T,0>& a, const double lb, const double ub)
{
	FTypeName<T,0> c1(lb);
	FTypeName<T,0> c2(ub);
	return min(max(a,c1),c2);
	// return a;
}

template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> mc_print (const FTypeName<T,N>& a, const int number)
{
    std::cout << "FADBAD #" << number << ": " << a << std::endl;
	return a;
}

template <typename T>
INLINE2 FTypeName<T,0> mc_print (const FTypeName<T,0>& a, const int number)
{
	std::cout << "FADBAD #" << number << ": " << a << std::endl;
	return a;
}

//@AVT:SVT: 20.12.2018 added fadbad implementation of erf and erfc functions
template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> erf(const FTypeName<T,N>& a)
{
	const T& aval(a.val());
    FTypeName<T,N> c(erf(aval));
    if (!a.depend()) return c;
	c.setDepend(a);
	for(unsigned int i=0;i<N;++i) c[i]=a[i]* 2./std::sqrt(mc::PI)*Op<T>::myExp(-Op<T>::myPow(aval,2));
	return c;
}

template <typename T>
INLINE2 FTypeName<T,0> erf(const FTypeName<T,0>& a)
{
	const T& aval(a.val());
    FTypeName<T,0> c(erf(aval));
    if (!a.depend()) return c;
	c.setDepend(a);
	for(unsigned int i=0;i<c.size();++i) c[i]=a[i]* 2./std::sqrt(mc::PI)*Op<T>::myExp(-Op<T>::myPow(aval,2));
	return c;
}

// The double specialization of erf is needed since there is no myErf in fadbad
template <unsigned int N>
INLINE2 FTypeName<double,N> erf(const FTypeName<double,N>& a)
{
	const double& aval(a.val());
    FTypeName<double,N> c(std::erf(aval));
    if (!a.depend()) return c;
	c.setDepend(a);
	for(unsigned int i=0;i<N;++i) c[i]=a[i]* 2./std::sqrt(mc::PI)*std::exp(-std::pow(aval,2));
	return c;
}

INLINE2 FTypeName<double,0> erf(const FTypeName<double,0>& a)
{
	const double& aval(a.val());
    FTypeName<double,0> c(std::erf(aval));
    if (!a.depend()) return c;
	c.setDepend(a);
	for(unsigned int i=0;i<c.size();++i) c[i]=a[i]* 2./std::sqrt(mc::PI)*std::exp(-std::pow(aval,2));
	return c;
}


template <typename T>
INLINE2 T erfc (const T& x)
{

    return Op<T>::myOne() - erf(x);
}

//@AVT.SVT: 10.11.2017 added additional fadbad versions of our own functions to allow usage of DAG with fadbad
template <typename T>
INLINE2 T vapor_pressure(const T& x, const double type, const double p1, const double p2, const double p3, const double p4,
						 const double p5, const double p6, const double p7, const double p8, const double p9, const double p10)
{
   //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
    case 1: //Extended Antoine
      return Op<T>::myExp(p1+p2/(x+p3)+x*p4+p5*Op<T>::myLog(x)+p6*Op<T>::myPow(x,p7));
      break;

    case 2: //Antoine
      return Op<T>::myPow(10.,p1-p2/(p3+x));
      break;

    case 3: //Wagner
	  {
	  T Tr = x/p5;
      return p6*Op<T>::myExp((p1*(1-Tr)+p2*Op<T>::myPow(1-Tr,1.5)+p3*Op<T>::myPow(1-Tr,2.5)+p4*Op<T>::myPow(1-Tr,5))/Tr);
      break;
      }
    case 4: // IK-CAPE
      return Op<T>::myExp(p1+p2*x+p3*Op<T>::myPow(x,2)+p4*Op<T>::myPow(x,3)+p5*Op<T>::myPow(x,4)+p6*Op<T>::myPow(x,5)+p7*Op<T>::myPow(x,6)+p8*Op<T>::myPow(x,7)+p9*Op<T>::myPow(x,8)+p10*Op<T>::myPow(x,9));
      break;

    default:
      throw std::runtime_error("mc::McCormick\t Vapor Pressure called with an unknown type.");
      break;
  }
}

template <typename T>
INLINE2 T ideal_gas_enthalpy(const T& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4,
							 const double p5, const double p6 = 0, const double p7 = 0)
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
    case 1: // Aspen polynomial (implementing only the high-temperature version); the NASA 7-coefficient polynomial is equivalent with the last parameter equal to 0
      return p1*(x-x0) + p2/2*(Op<T>::myPow(x,2)-std::pow(x0,2)) + p3/3*(Op<T>::myPow(x,3)-std::pow(x0,3)) + p4/4*(Op<T>::myPow(x,4)-std::pow(x0,4)) + p5/5*(Op<T>::myPow(x,5)-std::pow(x0,5)) + p6/6*(Op<T>::myPow(x,6)-std::pow(x0,6));
      break;
    case 2: // NASA 9-coefficient polynomial
      return -p1*(1/x-1/x0) + p2*Op<T>::myLog(x/x0) + p3*(x-x0) + p4/2*(Op<T>::myPow(x,2)-std::pow(x0,2)) + p5/3*(Op<T>::myPow(x,3)-std::pow(x0,3)) + p6/4*(Op<T>::myPow(x,4)-std::pow(x0,4)) + p7/5*(Op<T>::myPow(x,5)-std::pow(x0,5));
      break;
    case 3: // DIPPR 107 equation
	{
	  // The DIPPR107 model is symmetric w.r.t. the sign of p3 and p5. If for some reason one of them is negative, we just switch the sign to be able to use the standard integrated for
	  T term1;
	  if (std::fabs(p3) < mc::machprec()) {
	  	term1 = p2*(x-x0); // The limit of p3/tanh(p3/x) for p3->0 is x
	  } else {
	  	term1 = p2*std::fabs(p3)*(1/tanh(std::fabs(p3)/x)-1/std::tanh(std::fabs(p3)/x0));
	  }
	  return p1*(x-x0) + term1 - p4*std::fabs(p5)*(tanh(std::fabs(p5)/x)-std::tanh(std::fabs(p5)/x0));
      break;
	}
    case 4: // DIPPR 127 equation
  	{
      T term1, term2, term3;
	  if (std::fabs(p3) < mc::machprec()) {
	  	term1 = p2*(x-x0);	// The limit of p3/(exp(p3/x)-1) for p3->0 is x
	  } else {
	  	term1 = p2*p3*(1/(Op<T>::myExp(p3/x)-1)-1/(std::exp(p3/x0)-1));
	  }
	  if (std::fabs(p5) < mc::machprec()) {
	  	term2 = p4*(x-x0);	// The limit of p5/(exp(p5/x)-1) for p5->0 is x
	  } else {
	  	term2 = p4*p5*(1/(Op<T>::myExp(p5/x)-1)-1/(std::exp(p5/x0)-1));
	  }
	  if (std::fabs(p7) < mc::machprec()) {
	  	term3 = p6*(x-x0);	// The limit of p7/(exp(p7/x)-1) for p7->0 is x
	  } else {
	  	term3 = p6*p7*(1/(Op<T>::myExp(p7/x)-1)-1/(std::exp(p7/x0)-1));
	  }
      return p1*(x-x0) + term1 + term2 + term3;
      break;
    }
    default:
      throw std::runtime_error("mc::McCormick\t Ideal Gas Enthalpy called with an unknown type.");
      break;
  }
}

template <typename T>
INLINE2 T saturation_temperature(const T& x, const double type, const double p1, const double p2, const double p3, const double p4,
								 const double p5, const double p6, const double p7, const double p8, const double p9, const double p10 )
{
  // moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
	case 1:
	{
		throw std::runtime_error("mc::McCormick\t Saturation Temperature type 1,3 or 4 is not allowed with type fadbad::F<mc::FFVar>.");
		break;
	}
	case 2:
		return p2/(p1-Op<T>::myLog(x)/std::log(10.))-p3;
		break;
	case 3:
	case 4:
	{
		throw std::runtime_error("mc::McCormick\t Saturation Temperature type 1,3 or 4 is not allowed with type fadbad::F<mc::FFVar>.");
		break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Saturation Temperature called with an unknown type.");
      break;
  }
}

template <typename T>
INLINE2 T enthalpy_of_vaporization(const T& x, const double type, const double p1, const double p2, const double p3, const double p4,
										   const double p5, const double p6 = 0 )
{
  // moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
    case 1: // Watson equation
	{
	  T tmp1 = 1-x/p1;	// this is 1-Tr
	  if (Op<T>::myGt(tmp1,Op<T>::myZero())) {
		  return p5 * Op<T>::myPow(tmp1/(1-p4/p1),p2+p3*tmp1);
	  } else {
		  return 0.;
	  }
	  break;
	}
	case 2: // DIPPR 106
	{
	  T Tr = x/p1;
	  if (Op<T>::myLt(Tr,Op<T>::myOne())) {
		return p2 * Op<T>::myPow(1-Tr,p3+p4*Tr+p5*Op<T>::myPow(Tr,2)+p6*Op<T>::myPow(Tr,3));
	  } else {
		return 0.;
	  }
	  break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Enthalpy of Vaporization called with an unknown type.");
      break;
  }
}

template <typename T>
INLINE2 T cost_function(const T& x, const double type, const double p1, const double p2, const double p3 )
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
    case 1: // Guthrie cost function
	{
	  return Op<T>::myPow( 10.,p1 + p2*Op<T>::myLog(x)/std::log(10.) + p3*Op<T>::myPow(Op<T>::myLog(x)/std::log(10.),2) );
	  break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Cost function called with an unknown type.");
      break;
  }
}


template <typename T, unsigned int N>
INLINE2 FTypeName<T,N> covariance_function(const FTypeName<T,N>& x, const double type )
{
	FTypeName<T,N> c(covariance_function(x.val(),type));
	if (!x.depend()) return c;
	c.setDepend(x);
	T tmp;
	switch((int)type){
		case 1: // matern 1/2
		{
			if (Op<T>::myEq(x.val(),Op<T>::myZero())) {
				throw std::runtime_error("mc::McCormick\t Covariance function matern 1/2 called with argument zero - derivative not defined.");
			}
			tmp = -Op<T>::myExp(-Op<T>::mySqrt(x.val()))/(2.*Op<T>::mySqrt(x.val()));
			break;
		}
		case 2: // matern 3/2
		{
			tmp = -1.5 * Op<T>::myExp(-Op<T>::mySqrt(3.*x.val()));
			break;
		}
		case 3: // matern 5/2
		{
			tmp = -5./6. * (1.+Op<T>::mySqrt(5.*x.val())) * Op<T>::myExp(-Op<T>::mySqrt(5.*x.val()));
			break;
		}
		case 4: // squared exponential
		{
			tmp = -0.5 * Op<T>::myExp(-0.5*x.val());
			break;
		}
		default:
			throw std::runtime_error("mc::McCormick\t Covariance function called with an unknown type.");
	}
	for(unsigned int i=0;i<N;++i) c[i]=tmp*x[i];
	return c;
}

template <typename T >
INLINE2 FTypeName<T,0> covariance_function(const FTypeName<T,0>& x, const double type)
{
	FTypeName<T,0> c(covariance_function(x.val(),type));
	if (!x.depend()) return c;
	c.setDepend(x);
	T tmp;
	switch((int)type){
		case 1: // matern 1/2
		{
			if (Op<T>::myEq(x.val(),Op<T>::myZero())) {
				throw std::runtime_error("mc::McCormick\t Covariance function matern 1/2 called with argument zero - derivative not defined.");
			}
			tmp = -Op<T>::myExp(-Op<T>::mySqrt(x.val()))/(2.*Op<T>::mySqrt(x.val()));
			break;
		}
		case 2: // matern 3/2
		{
			tmp = -1.5 * Op<T>::myExp(-Op<T>::mySqrt(3.*x.val()));
			break;
		}
		case 3: // matern 5/2
		{
			tmp = -5./6. * (1.+Op<T>::mySqrt(5.*x.val())) * Op<T>::myExp(-Op<T>::mySqrt(5.*x.val()));
			break;
		}
		case 4: // squared exponential
		{
			tmp = -0.5 * Op<T>::myExp(-0.5*x.val());
			break;
		}
		default:
			throw std::runtime_error("mc::McCormick\t Covariance function called with an unknown type.");
	}
	for(unsigned int i=0;i<c.size();++i) c[i]=tmp*x[i];
	return c;
}


template <unsigned int N>
INLINE2 FTypeName<double,N> covariance_function(const FTypeName<double,N>& x, const double type )
{
	FTypeName<double,N> c(mc::covariance_function(x.val(),type));
	if (!x.depend()) return c;
	c.setDepend(x);
	double tmp;
	switch((int)type){
		case 1: // matern 1/2
		{
			if (Op<double>::myEq(x.val(),Op<double>::myZero())) {
				throw std::runtime_error("mc::McCormick\t Covariance function matern 1/2 called with argument zero - derivative not defined.");
			}
			tmp = -Op<double>::myExp(-Op<double>::mySqrt(x.val()))/(2.*Op<double>::mySqrt(x.val()));
			break;
		}
		case 2: // matern 3/2
		{
			tmp = -1.5 * Op<double>::myExp(-Op<double>::mySqrt(3.*x.val()));
			break;
		}
		case 3: // matern 5/2
		{
			tmp = -5./6. * (1.+Op<double>::mySqrt(5.*x.val())) * Op<double>::myExp(-Op<double>::mySqrt(5.*x.val()));
			break;
		}
		case 4: // squared exponential
		{
			tmp = -0.5 * Op<double>::myExp(-0.5*x.val());
			break;
		}
		default:
			throw std::runtime_error("mc::McCormick\t Covariance function called with an unknown type.");
	}
	for(unsigned int i=0;i<N;++i) c[i]=tmp*x[i];
	return c;
}

INLINE2 FTypeName<double,0> covariance_function(const FTypeName<double,0>& x, const double type)
{
	FTypeName<double,0> c(mc::covariance_function(x.val(),type));
	if (!x.depend()) return c;
	c.setDepend(x);
	double tmp;
	switch((int)type){
		case 1: // matern 1/2
		{
			if (Op<double>::myEq(x.val(),Op<double>::myZero())) {
				throw std::runtime_error("mc::McCormick\t Covariance function matern 1/2 called with argument zero - derivative not defined.");
			}
			tmp = -Op<double>::myExp(-Op<double>::mySqrt(x.val()))/(2.*Op<double>::mySqrt(x.val()));
			break;
		}
		case 2: // matern 3/2
		{
			tmp = -1.5 * Op<double>::myExp(-Op<double>::mySqrt(3.*x.val()));
			break;
		}
		case 3: // matern 5/2
		{
			tmp = -5./6. * (1.+Op<double>::mySqrt(5.*x.val())) * Op<double>::myExp(-Op<double>::mySqrt(5.*x.val()));
			break;
		}
		case 4: // squared exponential
		{
			tmp = -0.5 * Op<double>::myExp(-0.5*x.val());
			break;
		}
		default:
			throw std::runtime_error("mc::McCormick\t Covariance function called with an unknown type.");
	}
	for(unsigned int i=0;i<c.size();++i) c[i]=tmp*x[i];
	return c;
}

template <typename T>
INLINE2 T acquisition_function(const T& mu, const T& sigma, const double type, const double fmin )
{
  switch((int)type){
    case 1: // lower confidence bound
	{
	  return mu - fmin*sigma;
	  break;
	}
    case 2: // expected improvement
	{
	  if (Op<T>::myEq(sigma,Op<T>::myZero())){
		  if(Op<T>::myLt(fmin-mu,Op<T>::myZero())){
			  return 0.;
		  }
		  else{
			  return fmin-mu;
		  }
	  }
	  return (fmin-mu)*(erf(1./std::sqrt(2)*(fmin-mu)/sigma)/2.+0.5) + sigma*gaussian_probability_density_function((fmin-mu)/sigma);
	  break;
	}
    case 3: // probability of improvement
	{
	  if (Op<T>::myEq(sigma,Op<T>::myZero())) {
		if (Op<T>::myGt(fmin,mu)){
			return 1.;
		} else {
			return 0.;
		}
	  }
	  return (erf(1./std::sqrt(2)*(fmin-mu)/sigma)/2.+0.5);
	  break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Acquisition function called with an unknown type.");
      break;
  }
}


template <typename T>
INLINE2 T gaussian_probability_density_function(const T& x)
{
   return 1./std::sqrt(2*mc::PI)* Op<T>::myExp(- Op<T>::mySqr(x)/2.);
}

//added AVT.SVT 05.02.2020
template <typename T>
INLINE2 T regnormal(const T& x, const double a, const double b)
{
   return x / Op<T>::mySqrt(a + b*Op<T>::mySqr(x));
}

//added AVT.SVT 23.11.2017
template <typename T>
INLINE2 T nrtl_tau(const T& x, const double a, const double b, const double e, const double f )
{
   return a+b/x + e*Op<T>::myLog(x) + f*x;
}

template <typename T>
INLINE2 T nrtl_dtau(const T& x, const double b, const double e, const double f )
{
  return f-b/Op<T>::myPow(x,2) + e/x;
}

//added AVT.SVT 23.11.2017
template <typename T>
INLINE2 T nrtl_G(const T& x, const double a, const double b, const double e, const double f, const double alpha)
{
	return Op<T>::myExp( -alpha * nrtl_tau(x,a,b,e,f));

}

template <typename T>
INLINE2 T der_nrtl_G(const T& x, const double a, const double b, const double e, const double f, const double alpha)
{
  //return -alpha*Op<T>::myExp( -alpha * (a+b/x + e*Op<T>::myLog(x) + f*x))*(f-b/Op<T>::myPow(x,2) + e/x);
  return -alpha * nrtl_G(x,a,b,e,f,alpha) * nrtl_dtau(x,b,e,f);
}

//added AVT.SVT 01.03.2018
template <typename T>
INLINE2 T nrtl_Gtau(const T& x, const double a, const double b, const double e, const double f, const double alpha )
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  //return Op<T>::myExp( -alpha * (a+b/x + e*Op<T>::myLog(x) + f*x))*(a+b/x + e*Op<T>::myLog(x) + f*x);
	return nrtl_G(x,a,b,e,f,alpha)*nrtl_tau(x,a,b,e,f);
}

//added AVT.SVT 22.03.2018
template <typename T>
INLINE2 T nrtl_Gdtau(const T& x, const double a, const double b, const double e, const double f, const double alpha)
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  //return Op<T>::myExp( -alpha*( a + b/x + e*Op<T>::myLog(x) + f*x ) )*(f - b/Op<T>::myPow(x,2) + e/x);
	return nrtl_G(x,a,b,e,f,alpha)*nrtl_dtau(x,b,e,f);

}

//added AVT.SVT 22.03.2018
template <typename T>
INLINE2 T nrtl_dGtau(const T& x, const double a, const double b, const double e, const double f, const double alpha)
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  //return -alpha*Op<T>::myExp( -alpha*( a + b/x + e*Op<T>::myLog(x) + f*x ) )*(f - b/Op<T>::myPow(x,2) + e/x)*(a + b/x + e*Op<T>::myLog(x) + f*x );
	return der_nrtl_G(x,a,b,e,f,alpha) * nrtl_tau(x,a,b,e,f);

}

template <typename T>
INLINE2 T p_sat_ethanol_schroeder (const T& x)
{
	const double _T_c_K = 514.71;
	const double _N_Tsat_1 = -8.94161;
	const double _N_Tsat_2 = 1.61761;
	const double _N_Tsat_3 = -51.1428;
	const double _N_Tsat_4 = 53.1360;
	const double _k_Tsat_1 = 1.0;
	const double _k_Tsat_2 = 1.5;
	const double _k_Tsat_3 = 3.4;
	const double _k_Tsat_4 = 3.7;
	const double _p_c = 62.68;

	return _p_c*(Op<T>::myExp(_T_c_K/x*(_N_Tsat_1*Op<T>::myPow((1-x/_T_c_K),_k_Tsat_1) + _N_Tsat_2*Op<T>::myPow((1-x/_T_c_K),_k_Tsat_2)
	       + _N_Tsat_3*Op<T>::myPow((1-x/_T_c_K),_k_Tsat_3) + _N_Tsat_4*Op<T>::myPow((1-x/_T_c_K),_k_Tsat_4))));
}

template <typename T>
INLINE2 T rho_vap_sat_ethanol_schroeder (const T& x)
{
	const double _T_c_K = 514.71;
	const double _N_vap_1 = -1.75362;
	const double _N_vap_2 = -10.5323;
	const double _N_vap_3 = -37.6407;
	const double _N_vap_4 = -129.762;
	const double _k_vap_1 = 0.21;
	const double _k_vap_2 = 1.1;
	const double _k_vap_3 = 3.4;
	const double _k_vap_4 = 10;
	const double _rho_c = 273.195;

	return _rho_c*(Op<T>::myExp(_N_vap_1*Op<T>::myPow((1 - x/_T_c_K),_k_vap_1) + _N_vap_2*Op<T>::myPow((1 - x/_T_c_K),_k_vap_2)
	       + _N_vap_3*Op<T>::myPow((1 - x/_T_c_K),_k_vap_3) + _N_vap_4*Op<T>::myPow((1 - x/_T_c_K),_k_vap_4)));
}

template <typename T>
INLINE2 T rho_liq_sat_ethanol_schroeder (const T& x)
{
	const double _T_c_K = 514.71;
	const double _N_liq_1=9.00921;
	const double _N_liq_2=-23.1668;
	const double _N_liq_3=30.9092;
	const double _N_liq_4=-16.5459;
	const double _N_liq_5=3.64294;
	const double _k_liq_1=0.5;
	const double _k_liq_2=0.8;
	const double _k_liq_3=1.1;
	const double _k_liq_4=1.5;
	const double _k_liq_5=3.3;
	const double _rho_c = 273.195;

	return _rho_c*(1 + _N_liq_1*Op<T>::myPow((1 - x/_T_c_K),_k_liq_1) + _N_liq_2*Op<T>::myPow((1 - x/_T_c_K),_k_liq_2)
	       + _N_liq_3*Op<T>::myPow((1 - x/_T_c_K),_k_liq_3) + _N_liq_4*Op<T>::myPow((1 - x/_T_c_K),_k_liq_4) + _N_liq_5*Op<T>::myPow((1 - x/_T_c_K),_k_liq_5));
}

template <typename T>
INLINE2 T centerline_deficit(const T& x, const double xLim, const double type)
{

  switch((int)type) {
    case 1:
      if (Op<T>::myGe(x,Op<T>::myOne())) {
        return 1./sqr(x);
      } else {
        return 0.;
      }
    case 2:
      if (Op<T>::myGe(x,Op<T>::myOne())) {
        return 1./sqr(x);
      } else if (Op<T>::myGt(x,Op<T>::myZero()+xLim)) {
        return (x-xLim)/(1.-xLim);
      } else {
        return 0.;
      }
    case 3:
      if (Op<T>::myGe(x,Op<T>::myOne())) {
        return 1./sqr(x);
      } else if (Op<T>::myGt(x,Op<T>::myZero()+xLim)) {
        const double tmp = ( -1. + xLim*(5. + xLim*(-10. + xLim*(10. + xLim*(-5. + xLim)))));
        const double p0 = (std::pow(xLim,3)*(21. + xLim*(-21. + xLim*6.))) / tmp;
        const double p1 =  -(mc::sqr(xLim)*(63. + xLim*(-28 + xLim*(-13. + xLim*8.)))) / tmp;
        const double p2 =  (xLim*(63. + xLim*(42. + xLim*(-60. + xLim*(12. + xLim*3))))) / tmp;
        const double p3 =  -(21. + xLim*(84. + xLim*(-42. + xLim*(-12. + xLim*9)))) / tmp;
        const double p4 =  (35. + xLim*(14. + xLim*(-28. + xLim*9.))) / tmp;
        const double p5 =  -(15. + xLim*(-12. + xLim*3.)) / tmp;
        return p0 + x*(p1 + x*(p2 + x*(p3 + x*(p4 + x*p5))));
      } else {
        return 0.;
      }
    default:
      throw std::runtime_error("mc::McCormick\t centerline_deficit called with unkonw type.\n");
  }

}

//this implementation is used for all AD types
template <typename T>
INLINE2 T wake_profile (const T& x, const double type)
{
  switch((int)type){
    case 1: // Jensen top hat
    {
      if (Op<T>::myLe(x.val(),Op<T>::myZero())) {
        if (Op<T>::myGe(x.val(),-Op<T>::myOne())) {
          return 1.;
        } else {
          return 0.;
        }
      } else {
        if (Op<T>::myLe(x.val(),Op<T>::myOne())) {
          return 1.;
        } else {
          return 0.;
        }
      }
    }
    case 2: // Park Gauss profile
    {
      return exp(-sqr(x));
    }
    default:
      throw std::runtime_error("mc::McCormick\t Wake_profile called with an unknown type.");
  }
}


template <typename T>
INLINE2 T wake_deficit(const T& x, const T& r, const double a, const double alpha, const double rr, const double type1, const double type2)
{
  if (Op<T>::myGt(x+rr,Op<T>::myZero())) {
    const double r0 = rr*std::sqrt((1.-a)/(1.-2.*a));
    const T Rwake = r0 + alpha*x;
    return 2.*a*centerline_deficit(Rwake/r0,1.-alpha*rr/r0,type1)*wake_profile(r/Rwake,type2);
  } else {
    return 0.;
  }
}


template <typename T>
INLINE2 T power_curve(const T& x, const double type)
{
  switch((int)type){
    case 1: // classical cubic power_curve
      if (Op<T>::myLt(x,Op<T>::myZero())) {
        return 0.;
      } else if (Op<T>::myGt(x,Op<T>::myOne())) {
        return 1.;
      } else {
        return pow(x,3);
      }
    case 2: // generalized power curve based on Enercon E-70 E4 according to Hau
      if (Op<T>::myLt(x,Op<T>::myZero())) {
        return 0.;
      } else if (Op<T>::myGt(x,Op<T>::myOne())) {
        return 1.;
      } else if (Op<T>::myLt(x-0.643650793650794,Op<T>::myZero())) {
        return sqr(x)*(1.378300020831773+x*0.158205207484756);
      } else {
        return 1.+pow(x-1.,3)*(18.670944034722282 + (x-1.)*28.407497538574532);
      }
    default:
      throw std::runtime_error("mc::McCormick\t power_curve called with an unknown type.");
  }
}


template <typename T, unsigned int N>
INLINE2 FTypeName<T, N> fstep(const FTypeName<T, N>& x)
{
    if (Op<T>::myGe(x.val(), 0.)) {
        FTypeName<T, N> c(1.);
        c.setDepend(x);
        for (unsigned int i = 0; i < N; ++i) c[i] = 0;
        return c;
    }
    else {
        FTypeName<T, N> c(0.);
        c.setDepend(x);
        for (unsigned int i = 0; i < N; ++i) c[i] = 0;
        return c;
    }
}


template <typename T>
INLINE2 FTypeName<T, 0> fstep(const FTypeName<T, 0>& x)
{
    if (Op<T>::myGe(x.val(), 0.)) {
        FTypeName<T, 0> c(1.);
        c.setDepend(x);
        for (unsigned int i = 0; i < c.size(); ++i) c[i] = 0;
        return c;
    }
    else {
        FTypeName<T, 0> c(0.);
        c.setDepend(x);
        for (unsigned int i = 0; i < c.size(); ++i) c[i] = 0;
        return c;
    }
}


template <typename T, unsigned int N>
INLINE2 FTypeName<T, N> bstep(const FTypeName<T, N>& x)
{
    if (Op<T>::myGe(x.val(), 0.)) {
        FTypeName<T, N> c(0.);
        c.setDepend(x);
        for (unsigned int i = 0; i < N; ++i) c[i] = 0;
        return c;
    }
    else {
        FTypeName<T, N> c(1.);
        c.setDepend(x);
        for (unsigned int i = 0; i < N; ++i) c[i] = 0;
        return c;
    }
}


template <typename T>
INLINE2 FTypeName<T, 0> bstep(const FTypeName<T, 0>& x)
{
    if (Op<T>::myGe(x.val(), 0.)) {
        FTypeName<T, 0> c(0.);
        c.setDepend(x);
        for (unsigned int i = 0; i < c.size(); ++i) c[i] = 0;
        return c;
    }
    else {
        FTypeName<T, 0> c(1.);
        c.setDepend(x);
        for (unsigned int i = 0; i < c.size(); ++i) c[i] = 0;
        return c;
    }
}




////////////////////////////////////////////////////////////////////////////////////////////////////////
//@AVT.SVT: 25.08.2017
template <typename T, unsigned int N> inline std::ostream&
operator<<
( std::ostream&out, const FTypeName<T,N>&a)
{
  unsigned int ndigits = 5;
  out << std::scientific << std::setprecision(ndigits) << std::right
      << a.val();
  if( a.depend() ){
    out << " (";
    for(unsigned int i=0;i<N-1;++i) out << std::setw(ndigits+7) << a[i] << ",";
    out << std::setw(ndigits+7) << a[N-1] << ")";
  }
  return out;
}

template <typename T> inline std::ostream&
operator<<
( std::ostream&out, const FTypeName<T,0>&a)
{
  unsigned int ndigits = 10;
  out << std::scientific << std::setprecision(ndigits) << std::right
      << a.val();
  if( a.depend() ){
    out << " (";
    for(unsigned int i=0;i<a.size()-1;++i) out << std::setw(ndigits+7) << a[i] << ",";
    out << std::setw(ndigits+7) << a[a.size()-1] << ")";
  }
  return out;
}


/////////////////////////////////////////////////////////////////////////////////////////////////////
} // end namespace fadbad

#include "tadiff.h"

namespace fadbad
{

template <typename U, int N>
struct TTypeNamePOW3 : public UnTTypeNameHV<U,N>
{
	int m_b;
	TTypeNamePOW3(const U& val, TTypeNameHV<U,N>* pOp, const int b):UnTTypeNameHV<U,N>(val,pOp),m_b(b){}
	TTypeNamePOW3(TTypeNameHV<U,N>* pOp, const int b):UnTTypeNameHV<U,N>(pOp),m_b(b){}
	unsigned int eval(const unsigned int k)
	{
		unsigned int l=this->opEval(k);
                if( m_b==0 ){
 			if (0==this->length()) { this->val(0)=Op<U>::myOne(); this->length()=1; }
			for(unsigned int i=this->length();i<l;++i) { this->val(i)=Op<U>::myZero(); }
                }
                else if( m_b==1 ){
			for(unsigned int i=this->length();i<l;++i) { this->val(i)=this->opVal(i); }
		}
                else if( m_b==2 ){
			if (0==this->length()) { this->val(0)=Op<U>::mySqr(this->opVal(0)); this->length()=1; }
			for(unsigned int i=this->length();i<l;++i)
			{
				this->val(i)=Op<U>::myZero();
				unsigned int m=(i+1)/2;
				for(unsigned int j=0;j<m;++j) Op<U>::myCadd(this->val(i), this->opVal(i-j)*this->opVal(j));
				Op<U>::myCmul(this->val(i), Op<U>::myTwo());
				if (0==i%2) Op<U>::myCadd(this->val(i), Op<U>::mySqr(this->opVal(m)));
			}
		}
		else if( m_b==3 ){
			if (0==this->length()) { this->val(0)=Op<U>::myPow(this->opVal(0),m_b); this->length()=1; }
			if (1<l && 1==this->length() ) { this->val(1)=Op<U>::myPow(this->opVal(0),m_b-1)
				*this->opVal(1)*Op<U>::myInteger(m_b); this->length()=2; }
			if (2<l && 2==this->length() ) { this->val(2)=Op<U>::myPow(this->opVal(0),m_b-2)
				*( this->opVal(0)*this->opVal(2) + Op<U>::myInteger(m_b-1)*Op<U>::mySqr(this->opVal(1)) )
				*Op<U>::myInteger(m_b); this->length()=3; }
			for(unsigned int i=this->length();i<l;++i)
                        {
                                this->val(i)=Op<U>::myZero();
				unsigned int m=(i+1)/2;
				for(unsigned int j=0;j<m;++j) Op<U>::myCadd(this->val(i), this->opVal(i-j)*this->opVal(j));
				Op<U>::myCmul(this->val(i), Op<U>::myTwo());
				if (0==i%2) Op<U>::myCadd(this->val(i), Op<U>::mySqr(this->opVal(m)));
                        }
			for(unsigned int i=l-1; i>=this->length();--i)
			{
				Op<U>::myCmul(this->val(i), this->opVal(0));
				for(unsigned int j=1;j<=i;++j) Op<U>::myCadd(this->val(i), this->val(i-j)*this->opVal(j));
			}
		}
                else{
			if (0==this->length()) { this->val(0)=Op<U>::myPow(this->opVal(0),m_b); this->length()=1; }
			for(unsigned int i=this->length();i<l;++i)
			{
				this->val(i)=Op<U>::myZero();
				for(unsigned int j=0;j<i;++j)
					Op<U>::myCadd(this->val(i), ( m_b - (m_b+Op<U>::myOne()) * Op<U>::myInteger(j) /
						Op<U>::myInteger(i) )*this->opVal(i-j)*this->val(j));
			}
                }
		return this->length()=l;
	}
private:
	void operator=(const TTypeNamePOW3<U,N>&){} // not allowed
};

template <typename U, int N>
TTypeName<U,N> pow(const TTypeName<U,N>& val, const int b)
{
	TTypeNameHV<U,N>* pHV=val.length()>0 ?
		new TTypeNamePOW3<U,N>(Op<U>::myPow(val.val(),b), val.getTTypeNameHV(), b):
		new TTypeNamePOW3<U,N>(val.getTTypeNameHV(), b);
	return TTypeName<U,N>(pHV);
}

} // end namespace fadbad

#include "badiff.h"

#include "mcop.hpp"

#include "IAPWS/iapwsFadbad.h"

namespace mc
{

//! @brief C++ structure for specialization of the mc::Op templated structure for use of the FADBAD type fadbad::F inside other MC++ types
template< typename U > struct Op< fadbad::F<U> >
{
  typedef fadbad::F<U> TU;
  static TU point( const double c ) { throw std::runtime_error("mc::Op<fadbad::F<U>>::point -- operation not permitted"); }
  static TU zeroone() { throw std::runtime_error("mc::Op<fadbad::F<U>>::zeroone -- operation not permitted"); }
  static void I(TU& x, const TU&y) { x = y; }
  static double l(const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::l -- operation not permitted"); }
  static double u(const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::u -- operation not permitted"); }
  static double abs (const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::abs -- operation not permitted"); }
  static double mid (const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::mid -- operation not permitted"); }
  static double diam(const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::diam -- operation not permitted"); }
  static TU inv (const TU& x) { return 1./x;  }
  static TU sqr (const TU& x) { return fadbad::sqr(x);  }
  static TU sqrt(const TU& x) {
	  if(x.val() == 0.){
		  throw std::runtime_error("mc::fadbad -- Derivative of sqrt(x) called with x=0. Proceeding...");
	  }
	  return fadbad::sqrt(x);
  }
  static TU exp (const TU& x) { return fadbad::exp(x);  }
  static TU log (const TU& x) { return fadbad::log(x);  }
  static TU xlog(const TU& x) { return x*fadbad::log(x); }
  static TU fabsx_times_x(const TU& x) { return fadbad::fabsx_times_x(x); }
  static TU xexpax(const TU& x, const double a) { return x*fadbad::exp(a*x); }
  static TU centerline_deficit(const TU& x, const double xLim, const double type) { return fadbad::centerline_deficit(x,xLim,type); }
  static TU wake_profile(const TU& x, const double type) { return fadbad::wake_profile(x,type); }
  static TU wake_deficit(const TU& x, const TU& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return fadbad::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static TU power_curve(const TU& x, const double type) { return fadbad::power_curve(x,type); }
  static TU expx_times_y(const TU& x, const TU& y) { return fadbad::exp(x)*y; }
  static TU lmtd(const TU& x, const TU& y)  { return fadbad::lmtd(x,y); }
  static TU rlmtd(const TU& x, const TU& y) { return fadbad::rlmtd(x,y); }
  static TU mid(const TU& x, const TU& y, const double k) { return fadbad::mid(x, y, k); }
  static TU pinch(const TU& Th, const TU& Tc, const TU& Tp) { return fadbad::pinch(Th, Tc, Tp); }
  static TU euclidean_norm_2d(const TU& x, const TU& y) { return fadbad::euclidean_norm_2d(x,y); }
  static TU vapor_pressure(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
						   const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return fadbad::vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10); }
  static TU ideal_gas_enthalpy(const TU& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							   const double p7 = 0) { return fadbad::ideal_gas_enthalpy(x,x0,type,p1,p2,p3,p4,p5,p6,p7);}
  static TU saturation_temperature(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
								   const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return fadbad::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10); }
  static TU enthalpy_of_vaporization(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { return fadbad::enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6);}
  static TU cost_function(const TU& x, const double type, const double p1, const double p2, const double p3) { return fadbad::cost_function(x,type,p1,p2,p3);}
  static TU sum_div(const std::vector<TU>& x, const std::vector<double>& coeff) { return fadbad::sum_div(x,coeff); }
  static TU xlog_sum(const std::vector<TU>& x, const std::vector<double>& coeff) { return fadbad::xlog_sum(x,coeff); }
  static TU nrtl_tau(const TU& x, const double a, const double b, const double e, const double f) { return fadbad::nrtl_tau(x,a,b,e,f); }
  static TU nrtl_dtau(const TU& x, const double b, const double e, const double f) { return fadbad::nrtl_dtau(x,b,e,f); }
  static TU nrtl_G(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { return fadbad::nrtl_G(x,a,b,e,f,alpha);}
  static TU nrtl_Gtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { return fadbad::nrtl_Gtau(x,a,b,e,f,alpha);}
  static TU nrtl_Gdtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { return fadbad::nrtl_Gdtau(x,a,b,e,f,alpha);}
  static TU nrtl_dGtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { return fadbad::nrtl_dGtau(x,a,b,e,f,alpha);}
  static TU iapws(const TU& x, const double type) { return fadbad::iapws(x,type); }
  static TU iapws(const TU& x, const TU& y, const double type) { return fadbad::iapws(x,y,type); }
  static TU p_sat_ethanol_schroeder(const TU& x) { return fadbad::p_sat_ethanol_schroeder(x);}
  static TU rho_vap_sat_ethanol_schroeder(const TU& x) { return fadbad::rho_vap_sat_ethanol_schroeder(x);}
  static TU rho_liq_sat_ethanol_schroeder(const TU& x) { return fadbad::rho_liq_sat_ethanol_schroeder(x);}
  static TU covariance_function(const TU& x, const double type) { return fadbad::covariance_function(x,type);}
  static TU acquisition_function(const TU& x, const TU& y, const double type, const double fmin) { return fadbad::acquisition_function(x,y,type,fmin);}
  static TU gaussian_probability_density_function(const TU& x) { return fadbad::gaussian_probability_density_function(x);}
  static TU regnormal(const TU& x, const double a, const double b) { return fadbad::regnormal(x,a,b);}
  static TU fabs(const TU& x) { /*throw std::runtime_error("mc::Op<fadbad::F<U>>::fabs -- operation not permitted");*/ return fadbad::fabs(x); }
  static TU sin (const TU& x) { return fadbad::sin(x);  }
  static TU cos (const TU& x) { return fadbad::cos(x);  }
  static TU tan (const TU& x) { return fadbad::tan(x);  }
  static TU asin(const TU& x) { return fadbad::asin(x); }
  static TU acos(const TU& x) { return fadbad::acos(x); }
  static TU atan(const TU& x) { return fadbad::atan(x); }
  static TU sinh(const TU& x) { return fadbad::sinh(x); }
  static TU cosh(const TU& x) { return fadbad::cosh(x); }
  static TU tanh(const TU& x) { return fadbad::tanh(x); }
  static TU coth(const TU& x) { return 1./fadbad::tanh(x); }
  static TU asinh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::asinh -- operation not permitted");}
  static TU acosh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::acosh -- operation not permitted");}
  static TU atanh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::atanh -- operation not permitted");}
  static TU acoth(const TU& x) { throw std::runtime_error("mc::Op<fadbad::F<U>>::acoth -- operation not permitted");}
  static TU erf (const TU& x) { return fadbad::erf(x); }
  static TU erfc(const TU& x) { return fadbad::erfc(x); }
  static TU fstep(const TU& x) { return fadbad::fstep(x); }
  static TU bstep(const TU& x) { return fadbad::bstep(x); }
  static TU hull(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::F<U>>::hull -- operation not permitted"); }
  static TU min (const TU& x, const TU& y) { return fadbad::min(x,y); }
  static TU max (const TU& x, const TU& y) { return fadbad::max(x,y); }
  static TU pos (const TU& x) { return fadbad::pos(x);  }
  static TU neg (const TU& x) { return fadbad::neg(x);  }
  static TU lb_func (const TU& x, const double lb) { return fadbad::lb_func(x,lb);  }
  static TU ub_func (const TU& x, const double ub) { return fadbad::ub_func(x,ub);  }
  static TU bounding_func (const TU& x, const double lb, const double ub) { return fadbad::bounding_func(x,lb,ub);  }
  static TU squash_node (const TU& x, const double lb, const double ub) { return fadbad::squash_node(x,lb,ub);  }
  static TU single_neuron(const std::vector<TU>& x, const std::vector<double>& w, const double b, const int type) { return fadbad::single_neuron(x,w,b,type); }
  static TU mc_print (const TU& x, const int number) { return fadbad::mc_print(x,number);  }
  static TU arh (const TU& x, const double k) { return fadbad::exp(-k/x); }
  static TU pow(const TU& x, const double y) {
      if(x.val()==0. && y <1.){
		  throw std::runtime_error("mc::fadbad -- Derivative of x^a called with x=0 and a in (0,1). Proceeding...");
	  }
	  return fadbad::pow(x,y);
  }
  template <typename X, typename Y> static TU pow(const X& x, const Y& y) { return fadbad::pow(x,y); }
  static TU cheb(const TU& x, const unsigned n) { return fadbad::cheb(x,n); }
  static TU prod (const unsigned n, const TU* x) { switch( n ){ case 0: return 1.; case 1: return x[0]; default: return x[0]*prod(n-1,x+1); } }
  static TU monom (const unsigned n, const TU* x, const unsigned* k) { switch( n ){ case 0: return 1.; case 1: return pow(x[0],(int)k[0]); default: return pow(x[0],(int)k[0])*monom(n-1,x+1,k+1); } }
  static bool inter(TU& xIy, const TU& x, const TU& y) { xIy = x; return true; }
  static bool eq(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::F<U>>::eq -- operation not permitted"); }
  static bool ne(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::F<U>>::ne -- operation not permitted"); }
  static bool lt(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::F<U>>::lt -- operation not permitted"); }
  static bool le(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::F<U>>::le -- operation not permitted"); }
  static bool gt(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::F<U>>::gt -- operation not permitted"); }
  static bool ge(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::F<U>>::ge -- operation not permitted"); }
};

//! @brief C++ structure for specialization of the mc::Op templated structure for use of the FADBAD type fadbad::B inside other MC++ types
template< typename U > struct Op< fadbad::B<U> >
{
  typedef fadbad::B<U> TU;
  static TU point( const double c ) { throw std::runtime_error("mc::Op<fadbad::B<U>>::point -- operation not permitted"); }
  static TU zeroone() { throw std::runtime_error("mc::Op<fadbad::B<U>>::zeroone -- operation not permitted"); }
  static void I(TU& x, const TU&y) { x = y; }
  static double l(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::l -- operation not permitted"); }
  static double u(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::u -- operation not permitted"); }
  static double abs (const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::abs -- operation not permitted"); }
  static double mid (const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::mid -- operation not permitted"); }
  static double diam(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::diam -- operation not permitted"); }
  static TU inv (const TU& x) { return 1./x;  }
  static TU sqr (const TU& x) { return fadbad::sqr(x);  }
  static TU sqrt(const TU& x) {
	  if(x.val() == 0.){
		  throw std::runtime_error("mc::fadbad -- Derivative of sqrt(x) called with x=0. Proceeding...");
	  }
	  return fadbad::sqrt(x);
  }
  static TU exp (const TU& x) { return fadbad::exp(x);  }
  static TU log (const TU& x) { return fadbad::log(x);  }
  static TU xlog(const TU& x) { return x*fadbad::log(x); }
  static TU fabsx_times_x(const TU& x) { return fadbad::fabsx_times_x(x); }
  static TU xexpax(const TU& x, const double a) { return x*fadbad::exp(a*x); }
  static TU centerline_deficit(const TU& x, const double xLim, const double type) { return fadbad::centerline_deficit(x,xLim,type); }
  static TU wake_profile(const TU& x, const double type) { return fadbad::wake_profile(x,type); }
  static TU wake_deficit(const TU& x, const TU& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return fadbad::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static TU power_curve(const TU& x, const double type) { return fadbad::power_curve(x,type); }
  static TU expx_times_y(const TU& x, const TU& y) { return fadbad::exp(x)*y; }
  static TU lmtd(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::lmtd -- operation not implemented"); }
  static TU rlmtd(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::rlmtd -- operation not implemented"); }
  static TU mid(const TU& x, const TU& y, const double k) { throw std::runtime_error("mc::Op<fadbad::B<U>>::mid -- operation not implemented"); } 
  static TU pinch(const TU& Th, const TU& Tc, const TU& Tp) { throw std::runtime_error("mc::Op<fadbad::B<U>>::pinch -- operation not implemented"); }
  static TU euclidean_norm_2d(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::euclidean_norm_2d -- operation not implemented"); }
  static TU vapor_pressure(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
							const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return fadbad::vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}
  static TU ideal_gas_enthalpy(const TU& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							   const double p7 = 0) { return fadbad::ideal_gas_enthalpy(x,x0,type,p1,p2,p3,p4,p5,p6,p7);}
  static TU saturation_temperature(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
									const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return fadbad::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}
  static TU enthalpy_of_vaporization(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { return fadbad::enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6);}
  static TU cost_function(const TU& x, const double type, const double p1, const double p2, const double p3) { return fadbad::cost_function(x,type,p1,p2,p3);}
  static TU sum_div(const std::vector<TU>& x, const std::vector<double>& coeff) { return fadbad::sum_div(x,coeff); }
  static TU xlog_sum(const std::vector<TU>& x, const std::vector<double>& coeff) { return fadbad::xlog_sum(x,coeff); }
  static TU nrtl_tau(const TU& x, const double a, const double b, const double e, const double f) { return fadbad::nrtl_tau(x,a,b,e,f); }
  static TU nrtl_dtau(const TU& x, const double b, const double e, const double f) { return fadbad::nrtl_dtau(x,b,e,f); }
  static TU nrtl_G(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { return fadbad::nrtl_G(x,a,b,e,f,alpha);}
  static TU nrtl_Gtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { return fadbad::nrtl_Gtau(x,a,b,e,f,alpha);}
  static TU nrtl_Gdtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { return fadbad::nrtl_Gdtau(x,a,b,e,f,alpha);}
  static TU nrtl_dGtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { return fadbad::nrtl_dGtau(x,a,b,e,f,alpha);}
  static TU iapws(const TU& x, const double type) { throw std::runtime_error("mc::Op<fadbad::B<U>>::iapws -- operation not permitted"); }
  static TU iapws(const TU& x, const TU& y, const double type) { throw std::runtime_error("mc::Op<fadbad::B<U>>::iapws -- operation not permitted"); }
  static TU p_sat_ethanol_schroeder(const TU& x) {return fadbad::p_sat_ethanol_schroeder(x);}
  static TU rho_vap_sat_ethanol_schroeder(const TU& x) {return fadbad::rho_vap_sat_ethanol_schroeder(x);}
  static TU rho_liq_sat_ethanol_schroeder(const TU& x) {return fadbad::rho_liq_sat_ethanol_schroeder(x);}
  static TU covariance_function(const TU& x, const double type) { throw std::runtime_error("mc::Op<fadbad::B<U>>::covariance_function -- operation not implemented");}
  static TU acquisition_function(const TU& x, const TU& y, const double type, const double fmin) { throw std::runtime_error("mc::Op<fadbad::B<U>>::acquisition_function -- operation not implemented");}
  static TU gaussian_probability_density_function(const TU& x) { return fadbad::gaussian_probability_density_function(x);}
  static TU regnormal(const TU& x, const double a, const double b) { return fadbad::regnormal(x,a,b);}
  static TU fabs(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::fabs -- operation not permitted"); }
  static TU sin (const TU& x) { return fadbad::sin(x);  }
  static TU cos (const TU& x) { return fadbad::cos(x);  }
  static TU tan (const TU& x) { return fadbad::tan(x);  }
  static TU asin(const TU& x) { return fadbad::asin(x); }
  static TU acos(const TU& x) { return fadbad::acos(x); }
  static TU atan(const TU& x) { return fadbad::atan(x); }
  static TU sinh(const TU& x) { return fadbad::sinh(x); }
  static TU cosh(const TU& x) { return fadbad::cosh(x); }
  static TU tanh(const TU& x) { return fadbad::tanh(x); }
  static TU coth(const TU& x) { return 1./fadbad::tanh(x);}
  static TU asinh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::asinh -- operation not permitted");}
  static TU acosh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::acosh -- operation not permitted");}
  static TU atanh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::atanh -- operation not permitted");}
  static TU acoth(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::acoth -- operation not permitted");}
  static TU erf (const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::erf -- operation not permitted"); }
  static TU erfc(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::erfc -- operation not permitted"); }
  static TU fstep(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::fstep -- operation not permitted"); }
  static TU bstep(const TU& x) { throw std::runtime_error("mc::Op<fadbad::B<U>>::bstep -- operation not permitted"); }
  static TU hull(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::hull -- operation not permitted"); }
  static TU min (const TU& x, const TU& y) {throw std::runtime_error("mc::Op<fadbad::B<U>>::min -- operation not permitted");}
  static TU max (const TU& x, const TU& y) {throw std::runtime_error("mc::Op<fadbad::B<U>>::max -- operation not permitted");}
  static TU pos (const TU& x) {throw std::runtime_error("mc::Op<fadbad::B<U>>::pos -- operation not permitted");}
  static TU neg (const TU& x) {throw std::runtime_error("mc::Op<fadbad::B<U>>::neg -- operation not permitted");}
  static TU lb_func (const TU& x, const double lb) {throw std::runtime_error("mc::Op<fadbad::B<U>>::lb_func -- operation not permitted");}
  static TU ub_func (const TU& x, const double ub) {throw std::runtime_error("mc::Op<fadbad::B<U>>::ub_func -- operation not permitted");}
  static TU bounding_func (const TU& x, const double lb, const double ub) {throw std::runtime_error("mc::Op<fadbad::B<U>>::bounding_func -- operation not permitted");}
  static TU squash_node (const TU& x, const double lb, const double ub) {throw std::runtime_error("mc::Op<fadbad::B<U>>::squash_node -- operation not permitted");}
  static TU single_neuron(const std::vector<TU>& x, const std::vector<double>& w, const double b, const int type) { return fadbad::single_neuron(x,w,b,type);}
  static TU mc_print (const TU& x, const int number) { throw std::runtime_error("mc::Op<fadbad::B<U>>::mc:print -- operation not permitted"); }
  static TU arh (const TU& x, const double k) { return fadbad::exp(-k/x); }
  static TU pow(const TU& x, const double y) {
      if(x.val()==0. && y <1.){
		  throw std::runtime_error("mc::fadbad -- Derivative of x^a called with x=0 and a in (0,1). Proceeding...");
	  }
	  return fadbad::pow(x,y);
  }
  template <typename X, typename Y> static TU pow(const X& x, const Y& y) { return fadbad::pow(x,y); }
  static TU cheb(const TU& x, const unsigned n) { throw std::runtime_error("mc::Op<fadbad::B<U>>::cheb -- operation not permitted"); }
  static TU prod (const unsigned n, const TU* x) { switch( n ){ case 0: return 1.; case 1: return x[0]; default: return x[0]*prod(n-1,x+1); } }
  static TU monom (const unsigned n, const TU* x, const unsigned* k) { switch( n ){ case 0: return 1.; case 1: return pow(x[0],(int)k[0]); default: return pow(x[0],(int)k[0])*monom(n-1,x+1,k+1); } }
  static bool inter(TU& xIy, const TU& x, const TU& y) { xIy = x; return true; }
  static bool eq(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::eq -- operation not permitted"); }
  static bool ne(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::ne -- operation not permitted"); }
  static bool lt(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::lt -- operation not permitted"); }
  static bool le(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::le -- operation not permitted"); }
  static bool gt(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::gt -- operation not permitted"); }
  static bool ge(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::B<U>>::ge -- operation not permitted"); }
};

//! @brief C++ structure for specialization of the mc::Op templated structure for use of the FADBAD type fadbad::T inside other MC++ types
template< typename U > struct Op< fadbad::T<U> >
{
  typedef fadbad::T<U> TU;
  static TU point( const double c ) { throw std::runtime_error("mc::Op<fadbad::T<U>>::point -- operation not permitted"); }
  static TU zeroone() { throw std::runtime_error("mc::Op<fadbad::T<U>>::zeroone -- operation not permitted"); }
  static void I(TU& x, const TU&y) { x = y; }
  static double l(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::l -- operation not permitted"); }
  static double u(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::u -- operation not permitted"); }
  static double abs (const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::abs -- operation not permitted"); }
  static double mid (const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::mid -- operation not permitted"); }
  static double diam(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::diam -- operation not permitted"); }
  static TU inv (const TU& x) { return 1./x;  }
  static TU sqr (const TU& x) { return fadbad::sqr(x);  }
  static TU sqrt(const TU& x) { return fadbad::sqrt(x); }
  static TU exp (const TU& x) { return fadbad::exp(x);  }
  static TU log (const TU& x) { return fadbad::log(x);  }
  static TU xlog(const TU& x) { return x*fadbad::log(x); }
  static TU fabsx_times_x(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::fabsx_times_x -- operation not permitted"); }
  static TU xexpax(const TU& x, const double a) { return x*fadbad::exp(a*x); }
  static TU centerline_deficit(const TU& x, const double xLim, const double type) { return fadbad::centerline_deficit(x,xLim,type); }
  static TU wake_profile(const TU& x, const double type) { return fadbad::wake_profile(x,type); }
  static TU wake_deficit(const TU& x, const TU& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return fadbad::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static TU power_curve(const TU& x, const double type) { return fadbad::power_curve(x,type); }
  static TU expx_times_y(const TU& x, const TU& y) { return fadbad::exp(x)*y; }
  static TU lmtd(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::lmtd -- operation not permitted"); }
  static TU rlmtd(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::rlmtd -- operation not permitted"); }
  static TU mid(const TU& x, const TU& y, const double k) { throw std::runtime_error("mc::Op<fadbad::T<U>>::mid -- operation not permitted"); }
  static TU pinch(const TU& Th, const TU& Tc, const TU& Tp) { throw std::runtime_error("mc::Op<fadbad::T<U>>::pinch -- operation not permitted"); }
  static TU euclidean_norm_2d(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::euclidean_norm_2d -- operation not permitted"); }
  static TU vapor_pressure(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
							const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { throw std::runtime_error("mc::Op<fadbad::T<U>>::vapor_pressure -- operation not permitted");}
  static TU ideal_gas_enthalpy(const TU& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							   const double p7 = 0) { throw std::runtime_error("mc::Op<fadbad::T<U>>::ideal_gas_enthalpy -- operation not permitted");}
  static TU saturation_temperature(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
									const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { throw std::runtime_error("mc::Op<fadbad::T<U>>::saturation_temperature -- operation not permitted");}
  static TU enthalpy_of_vaporization(const TU& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { throw std::runtime_error("mc::Op<fadbad::T<U>>::enthalpy_of_vaporization -- operation not permitted");}
  static TU cost_function(const TU& x, const double type, const double p1, const double p2, const double p3) { throw std::runtime_error("mc::Op<fadbad::T<U>>::cost_function -- operation not permitted");}
  static TU sum_div(const std::vector<TU>& x, const std::vector<double>& coeff) { throw std::runtime_error("mc::Op<fadbad::T<U>>::sum_div -- operation not permitted"); }
  static TU xlog_sum(const std::vector<TU>& x, const std::vector<double>& coeff) { throw std::runtime_error("mc::Op<fadbad::T<U>>::xlog_sum -- operation not permitted"); }
  static TU nrtl_tau(const TU& x, const double a, const double b, const double e, const double f) { throw std::runtime_error("mc::Op<fadbad::T<U>>::nrtl_tau -- operation not permitted");}
  static TU nrtl_dtau(const TU& x, const double b, const double e, const double f) { throw std::runtime_error("mc::Op<fadbad::T<U>>::nrtl_dtau -- operation not permitted"); }
  static TU nrtl_G(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { throw std::runtime_error("mc::Op<fadbad::T<U>>::nrtl_G -- operation not permitted");}
  static TU nrtl_Gtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { throw std::runtime_error("mc::Op<fadbad::T<U>>::nrtl_Gtau -- operation not permitted");}
  static TU nrtl_Gdtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { throw std::runtime_error("mc::Op<fadbad::T<U>>::nrtl_Gdtau -- operation not permitted");}
  static TU nrtl_dGtau(const TU& x, const double a, const double b, const double e, const double f, const double alpha) { throw std::runtime_error("mc::Op<fadbad::T<U>>::nrtl_dGtau -- operation not permitted");}
  static TU iapws(const TU& x, const double type) { throw std::runtime_error("mc::Op<fadbad::T<U>>::iapws -- operation not permitted"); }
  static TU iapws(const TU& x, const TU& y, const double type) { throw std::runtime_error("mc::Op<fadbad::T<U>>::iapws -- operation not permitted"); }
  static TU p_sat_ethanol_schroeder(const TU& x) {throw std::runtime_error("mc::Op<fadbad::T<U>>::p_sat_ethanol_schroeder -- operation not permitted");}
  static TU rho_vap_sat_ethanol_schroeder(const TU& x) {throw std::runtime_error("mc::Op<fadbad::T<U>>::rho_vap_sat_ethanol_schroeder -- operation not permitted");}
  static TU rho_liq_sat_ethanol_schroeder(const TU& x) {throw std::runtime_error("mc::Op<fadbad::T<U>>::rho_liq_sat_ethanol_schroeder -- operation not permitted");}
  static TU covariance_function(const TU& x, const double type) { throw std::runtime_error("mc::Op<fadbad::T<U>>::covariance_function -- operation not permitted");}
  static TU acquisition_function(const TU& x, const TU& y, const double type, const double fmin) { throw std::runtime_error("mc::Op<fadbad::T<U>>::acquisition_function -- operation not permitted");}
  static TU gaussian_probability_density_function(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::gaussian_probability_density_function -- operation not permitted");}
  static TU regnormal(const TU& x, const double a, const double b) { throw std::runtime_error("mc::Op<fadbad::T<U>>::regnormal -- operation not permitted");}
  static TU fabs(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::fabs -- operation not permitted"); }
  static TU sin (const TU& x) { return fadbad::sin(x);  }
  static TU cos (const TU& x) { return fadbad::cos(x);  }
  static TU tan (const TU& x) { return fadbad::tan(x);  }
  static TU asin(const TU& x) { return fadbad::asin(x); }
  static TU acos(const TU& x) { return fadbad::acos(x); }
  static TU atan(const TU& x) { return fadbad::atan(x); }
  static TU sinh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::sinh -- operation not permitted"); }
  static TU cosh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::cosh -- operation not permitted"); }
  static TU tanh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::tanh -- operation not permitted"); }
  static TU coth(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::coth -- operation not permitted"); }
  static TU asinh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::asinh -- operation not permitted");}
  static TU acosh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::acosh -- operation not permitted");}
  static TU atanh(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::atanh -- operation not permitted");}
  static TU acoth(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::acoth -- operation not permitted");}
  static TU erf (const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::erf -- operation not permitted"); }
  static TU erfc(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::erfc -- operation not permitted"); }
  static TU fstep(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::fstep -- operation not permitted"); }
  static TU bstep(const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::bstep -- operation not permitted"); }
  static TU hull(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::hull -- operation not permitted"); }
  static TU min (const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::min -- operation not permitted"); }
  static TU max (const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::max -- operation not permitted"); }
  static TU pos (const TU& x) { throw std::runtime_error("mc::Op<fadbad::T<U>>::pos -- operation not permitted"); }
  static TU neg (const TU& x) {throw std::runtime_error("mc::Op<fadbad::T<U>>::neg -- operation not permitted"); }
  static TU lb_func (const TU& x, const double lb) { throw std::runtime_error("mc::Op<fadbad::T<U>>::lb_func -- operation not permitted");  }
  static TU ub_func (const TU& x, const double ub) { throw std::runtime_error("mc::Op<fadbad::T<U>>::ub_func -- operation not permitted");  }
  static TU bounding_func (const TU& x, const double lb, const double ub) { throw std::runtime_error("mc::Op<fadbad::T<U>>::bounding_func -- operation not permitted");  }
  static TU squash_node (const TU& x, const double lb, const double ub) { throw std::runtime_error("mc::Op<fadbad::T<U>>::squash_node -- operation not permitted");  }
  static TU single_neuron(const std::vector<TU>& x, const std::vector<double>& w, const double b, const int type) { throw std::runtime_error("mc::Op<fadbad::T<U>>::single_neuron -- operation not permitted"); }
  static TU mc_print (const TU& x, const int number) { throw std::runtime_error("mc::Op<fadbad::T<U>>::mc_print -- operation not permitted");  }
  static TU arh (const TU& x, const double k) { return fadbad::exp(-k/x); }
  template <typename X, typename Y> static TU pow(const X& x, const Y& y) { return fadbad::pow(x,y); }
  static TU cheb(const TU& x, const unsigned n) { throw std::runtime_error("mc::Op<fadbad::T<U>>::cheb -- operation not permitted"); }
  static TU prod (const unsigned n, const TU* x) { switch( n ){ case 0: return 1.; case 1: return x[0]; default: return x[0]*prod(n-1,x+1); } }
  static TU monom (const unsigned n, const TU* x, const unsigned* k) { switch( n ){ case 0: return 1.; case 1: return pow(x[0],(int)k[0]); default: return pow(x[0],(int)k[0])*monom(n-1,x+1,k+1); } }
  static bool inter(TU& xIy, const TU& x, const TU& y) { xIy = x; return true; }
  static bool eq(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::eq -- operation not permitted"); }
  static bool ne(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::ne -- operation not permitted"); }
  static bool lt(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::lt -- operation not permitted"); }
  static bool le(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::le -- operation not permitted"); }
  static bool gt(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::gt -- operation not permitted"); }
  static bool ge(const TU& x, const TU& y) { throw std::runtime_error("mc::Op<fadbad::T<U>>::ge -- operation not permitted"); }
};

} // namespace mc

#endif

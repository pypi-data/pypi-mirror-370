/**
 * @file library_of_functions.hpp
 *
 * @brief File containing implementation of additional functions for MC++.
 *        When you are implementing a new function, you have to implement a double/Template version here and extend the following files accordingly:
 *        mccormick.hpp, mcop.hpp, mcfilib.hpp, mcprofil.hpp, interval.hpp, mcfadbad.hpp, ffunc.hpp, ffdep.hpp
 *
 * ==============================================================================\n
 * © Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
 * ==============================================================================\n
 *
 * @author Dominik Bongartz, Jaromil Najman, Alexander Mitsos
 * @date 17.05.2018
 *
 */

#ifndef MC__LIBRARY_OF_FUNCTIONS_HPP
#define MC__LIBRARY_OF_FUNCTIONS_HPP

#include <set>
#include <string>
#include <sstream>
#include <iomanip>

#include "numerics.hpp"
#include "IAPWS/iapws.h"


namespace mc{


inline double sqr
( const double x )
{
  // Return squared value
  return x*x;
}


inline double coth
( const double x )
{
  // Return squared value
  if ( std::fabs(x) < machprec())
    throw std::runtime_error("mc::McCormick\t Hyperbolic cotangent with zero in range.");
  return 1/std::tanh(x);
}

inline double acoth
( const double x )
{
  // Return squared value
  if ( std::fabs(x) < 1)
    throw std::runtime_error("mc::McCormick\t Area hyperbolic cotangent within [-1,1].");
  return 0.5*std::log((x+1)/(x-1));
}

//added AVT.SVT 07.06.2017
inline double lmtd
( const double x, const double y )
{
  if ( x <= 0. || y <= 0.)
    throw std::runtime_error("mc::McCormick\t LMTD with non-positive values in range (LMTD)");
  if( mc::isequal(x,y)){
    return x;
  }
  // Return lmtd(x,y) term
  return (x-y)/(std::log(x)-std::log(y));
}


inline double rlmtd
( const double x, const double y )
{
  if ( x <= 0. || y <= 0.)
    throw std::runtime_error("mc::McCormick\t RLMTD with non-positive values in range (rLMTD)");

  // Return rlmtd(x,y) term
  return 1./mc::lmtd(x,y);
}

//added AVT.SVT 09/2021
inline double pinch 
(const double Th, const double Tc, const double Tp)
{
	// return std::max(Th, Tp) - std::max(Tc, Tp);
	return std::max(Th - Tp, 0.) - std::max(Tc - Tp, 0.);
}

//added AVT.SVT 07.06.2017
inline double euclidean_norm_2d
( const double x, const double y )
{
  return std::sqrt(std::pow(x,2) + std::pow(y,2));
}

//added AVT.SVT 07.06.2017
inline double der_euclidean_norm_2d
( const double x, const double y )
{
  if(x == 0 ){
	  return 0;
  }
  return x/std::sqrt(std::pow(x,2)+std::pow(y,2));
}

inline double xlog
( const double x )
{
  if ( x < 0.)
	throw std::runtime_error("mc::McCormick\t Log with negative values in range (XLOG)");
  // Return x*log(x) term
  if( mc::isequal(x,0.) ) return 0.;

  return x*std::log( x );
}

inline double fabsx_times_x
( const double x )
{

  return std::fabs( x )*x;
}

inline double xexpax
( const double x, const double a )
{
  return x*std::exp( a*x );
}

//added AVT.SVT 27.06.2017
inline double pos
( const double x )
{
  if(x < machprec()){
	std::ostringstream errmsg;
	errmsg << "mc::McCormick\t Pos with values lower than " << std::setprecision(16) << machprec() << " in range.";
	throw std::runtime_error(errmsg.str());
  }

  return x;
}


//added AVT.SVT 25.07.2017
inline double neg
( const double x )
{
  if(x > -machprec()){
	std::ostringstream errmsg;
	errmsg << "mc::McCormick\t Neg with values larger than " << std::setprecision(16) << machprec() << " in range.";
	throw std::runtime_error(errmsg.str());
  }

  return x;
}

//added AVT.SVT 28.09.2017
inline double lb_func
( const double x, const double lb )
{
  if(x < lb){
	std::ostringstream errmsg;
	errmsg << "mc::McCormick\t Lb_func with values lower than " << std::setprecision(16) << lb << " in range.";
	throw std::runtime_error(errmsg.str());
  }
  return x;
}


inline double ub_func
( const double x, const double ub )
{
  if(x > ub){
	std::ostringstream errmsg;
	errmsg << "mc::McCormick\t Ub_func with values larger than " << std::setprecision(16) << ub << " in range.";
	throw std::runtime_error(errmsg.str());
  }
  return x;
}


inline double bounding_func
( const double x, const double lb, const double ub )
{
  return lb_func(ub_func(x,ub),lb);
}

inline double squash_node
( const double x, const double lb, const double ub )
{
  // Note that here we don't throw an exception but simply return the middle point (it could be any point except for the border points [due to feas tolerance]), if x is out of bounds
  // When using this function, the user has to make sure (through linear inequalities) that x is only feasible for [lb,ub]
  if(x<lb) return lb;
  if(x>ub) return ub;
  return x;
}

inline double single_neuron
( const std::vector<double> &x, const std::vector<double> &w, const double b, const int type)
{
  	double dummy = b;
	for(size_t i=0; i<x.size(); i++){
		dummy += w[i]*x[i];
	}
	return std::tanh(dummy);
}

inline double sum_div
( const std::vector<double> &x, const std::vector<double> &coeff)
{
	double dummy = 0;
	for(size_t i=1; i<x.size(); i++){
		dummy += coeff[i+1]*x[i];
	}
	return (coeff[0]*x[0]/(coeff[1]*x[0]+dummy));
}


inline double xlog_sum
( const std::vector<double> &x, const std::vector<double> &coeff)
{
  double dummy = 0;
  for(size_t i=0; i<x.size();i++){
	  dummy += coeff[i]*x[i];
  }
  return x[0]*std::log(dummy);
}

// This function computes the componentwise-convex underestimator of xlog_sum. It is used to construct a convex relaxation of xlog_sum.
// n has to be x.size()-1
inline double xlog_sum_componentwise_convex
( const std::vector<double> &x, const std::vector<double> &coeff, const std::vector<double> &intervalLowerBounds, const std::vector<double> &intervalUpperBounds, unsigned int n)
{
	if(n+1 > x.size()){
		std::ostringstream errmsg;
		errmsg << "mc::McCormick\t xlog_sum_componentwise_convex called with wrong n or size of x.";
		throw std::runtime_error(errmsg.str());
	}
	if(n>1){
		std::vector<double> pointL(x);
		std::vector<double> pointU(x);
		pointL[n] = intervalLowerBounds[n]; pointU[n] = intervalUpperBounds[n];

		if(isequal(pointL[n],pointU[n])){
			return mc::xlog_sum_componentwise_convex(pointL,coeff,intervalLowerBounds,intervalUpperBounds,n-1);
		}

		return mc::xlog_sum_componentwise_convex(pointL,coeff,intervalLowerBounds,intervalUpperBounds,n-1)
      		   + (mc::xlog_sum_componentwise_convex(pointU,coeff,intervalLowerBounds,intervalUpperBounds,n-1)
			     -mc::xlog_sum_componentwise_convex(pointL,coeff,intervalLowerBounds,intervalUpperBounds,n-1))/(pointU[n]-pointL[n])*(x[n]-pointL[n]);
	}

	std::vector<double> pointL(x);
	std::vector<double> pointU(x);
	pointL[1] = intervalLowerBounds[1]; pointU[1] = intervalUpperBounds[1];

	if(isequal(pointL[1],pointU[1])){
		return mc::xlog_sum(pointL,coeff);
	}

	return mc::xlog_sum(pointL,coeff) + (mc::xlog_sum(pointU,coeff)-mc::xlog_sum(pointL,coeff))/(pointU[1]-pointL[1])*(x[1]-pointL[1]);
}

// This function computes the componentwise-concave overestimator of xlog_sum. It is used to construct a concaveelaxation of xlog_sum.
inline double xlog_sum_componentwise_concave
( const std::vector<double> &x, const std::vector<double> &coeff, const std::vector<double> &intervalLowerBounds, const std::vector<double> &intervalUpperBounds)
{

	std::vector<double> pointL(x);
	std::vector<double> pointU(x);
	pointL[0] = intervalLowerBounds[0]; pointU[0] = intervalUpperBounds[0];

	return mc::xlog_sum(pointL,coeff) + (mc::xlog_sum(pointU,coeff)-mc::xlog_sum(pointL,coeff))/(pointU[0]-pointL[0])*(x[0]-pointL[0]);
}


inline double mc_print
(const double x, const int number)
{
	std::cout << "Double #" << number << ": " << x << std::endl;
	return x;
}


//added AVT.SVT 22.08.2017
//***Note that all functions are assumed to be convex and nondecreasing***
inline double vapor_pressure
(const double x, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
 const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
    case 1: //Extended Antoine
      return std::exp(p1+p2/(x+p3)+x*p4+p5*std::log(x)+p6*std::pow(x,p7));
      break;

    case 2: //Antoine
      return std::pow(10.,p1-p2/(p3+x));
      break;

    case 3: //Wagner
	  {
	  double Tr = x/p5;
      return p6*std::exp((p1*(1-Tr)+p2*std::pow(1-Tr,1.5)+p3*std::pow(1-Tr,2.5)+p4*std::pow(1-Tr,5))/Tr);
      break;
      }
    case 4: // IK-CAPE
      return std::exp(p1+p2*x+p3*std::pow(x,2)+p4*std::pow(x,3)+p5*std::pow(x,4)+p6*std::pow(x,5)+p7*std::pow(x,6)+p8*std::pow(x,7)+p9*std::pow(x,8)+p10*std::pow(x,9));
      break;

    default:
      throw std::runtime_error("mc::McCormick\t Vapor Pressure called with an unknown type.");
      break;
  }
}


//added AVT.SVT 22.08.2017
inline double der_vapor_pressure
(const double x, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
 const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{

  switch((int)type){
    case 1: //Extended Antoine
      return (std::exp(p1+p2/(x+p3)+x*p4+p5*std::log(x)+p6*std::pow(x,p7)))*(p4+p5/x-p2/std::pow(p3+x,2)+p6*p7*std::pow(x,p7-1));
      break;

    case 2: //Antoine
      return (std::pow(10.,p1-p2/(p3+x)))*(p2*std::log(10.))/(std::pow(p3+x,2));
      break;

    case 3: //Wagner
	  {
	  double Tr = x/p5;
      return -p6*(std::exp((p1*(1-Tr)+p2*std::pow(1-Tr,1.5)+p3*std::pow(1-Tr,2.5)+p4*std::pow(1-Tr,5))/(Tr)))
				*(1./x*(p1+2.5*p3*std::pow(Tr-1,1.5)-5*p4*std::pow(Tr-1,6)+1.5*p2*std::pow(1-Tr,0.5))+p5/std::pow(x,2)*(p2*std::pow(1-Tr,1.5)-p1*(Tr-1)-p3*std::pow(Tr-1,2.5)+p4*std::pow(Tr-1,5)));
      break;
      }
    case 4: // IK-CAPE
      return (std::exp(p1+p2*x+p3*std::pow(x,2)+p4*std::pow(x,3)+p5*std::pow(x,4)+p6*std::pow(x,5)+p7*std::pow(x,6)+p8*std::pow(x,7)+p9*std::pow(x,8)+p10*std::pow(x,9)))
			*(p2+2*p3*x+3*p4*std::pow(x,2)+4*p5*std::pow(x,3)+5*p6*std::pow(x,4)+6*p7*std::pow(x,5)+7*p8*std::pow(x,6)+8*p9*std::pow(x,7)+9*p10*std::pow(x,8));
      break;
    default:
      throw std::runtime_error("mc::McCormick\t Vapor Pressure called with an unknown type.");
      break;
  }
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
sattemp_func
( const double x, const double*rusr, const int*iusr )
{
  switch(*iusr){
	  case 1:
		return mc::vapor_pressure(x,*iusr,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6]) - rusr[10];
	  case 2:
		return mc::vapor_pressure(x,*iusr,rusr[0], rusr[1], rusr[2]) - rusr[10];
	  case 3:
		return mc::vapor_pressure(x,*iusr,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5]) - rusr[10];
	  case 4:
		return mc::vapor_pressure(x,*iusr,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6], rusr[7], rusr[8], rusr[9]) - rusr[10];
	  default:
		  throw std::runtime_error("mc::McCormick\t sattemp_func called with an unknown type.");
		  break;
  }
}


inline double
sattemp_dfunc
( const double x, const double*rusr, const int*iusr )
{
  switch(*iusr){
	  case 1:
		return mc::der_vapor_pressure(x,*iusr,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6]);
	  case 2:
		return mc::der_vapor_pressure(x,*iusr,rusr[0], rusr[1], rusr[2]);
	  case 3:
		return mc::der_vapor_pressure(x,*iusr,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5]);
	  case 4:
		return mc::der_vapor_pressure(x,*iusr,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6], rusr[7], rusr[8], rusr[9]);
	  default:
		  throw std::runtime_error("mc::McCormick\t sattemp_func called with an unknown type.");
		  break;
  }
}


//added AVT.SVT 01.09.2017
//***Note that all functions are assumed to be monotonically increasing and concave***
inline double saturation_temperature
(const double x, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
 const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
	case 1:
	case 3:
	case 4:
	{
		throw std::runtime_error("mc::McCormick\t Saturation Temperature called with an unsupported type. Currently only type 2 is supported");
		break;
	}
	case 2:
		return p2/(p1-std::log(x)/std::log(10.))-p3;
		break;
    default:
      throw std::runtime_error("mc::McCormick\t Saturation Temperature called with an unknown type.");
      break;
  }
}


inline double der_saturation_temperature
(const double x, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
 const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{

  switch((int)type){
	case 1:
		return 1./mc::der_vapor_pressure(mc::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6),type,p1,p2,p3,p4,p5,p6);
		break;
	case 2:
		return p2/( x * std::log(10.) * std::pow(p1 - std::log(x)/std::log(10.), 2) );
		break;
	case 3:
	case 4:
		return 1./mc::der_vapor_pressure(mc::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10),type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);
		break;
    default:
      throw std::runtime_error("mc::McCormick\t Saturation Temperature called with an unknown type.");
      break;
  }
}


//added AVT.SVT 01.09.2017
//***Note that all functions are are assumed to be convex and nondecreasing***
inline double ideal_gas_enthalpy
(const double x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4,
 const double p5, const double p6 = 0, const double p7 = 0 )
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
    case 1: // Aspen polynomial (implementing only the high-temperature version); the NASA 7-coefficient polynomial is equivalent with the last parameter equal to 0
      return p1*(x-x0) + p2/2*(std::pow(x,2)-std::pow(x0,2)) + p3/3*(std::pow(x,3)-std::pow(x0,3)) + p4/4*(std::pow(x,4)-std::pow(x0,4)) + p5/5*(std::pow(x,5)-std::pow(x0,5)) + p6/6*(std::pow(x,6)-std::pow(x0,6));
      break;
    case 2: // NASA 9-coefficient polynomial
      return -p1*(1/x-1/x0) + p2*std::log(x/x0) + p3*(x-x0) + p4/2*(std::pow(x,2)-std::pow(x0,2)) + p5/3*(std::pow(x,3)-std::pow(x0,3)) + p6/4*(std::pow(x,4)-std::pow(x0,4)) + p7/5*(std::pow(x,5)-std::pow(x0,5));
      break;
    case 3: // DIPPR 107 equation
    {
	  // The DIPPR107 model is symmetric w.r.t. the sign of p3 and p5. If for some reason one of them is negative, we just switch the sign to be able to use the standard integrated for
	  double term1;
	  if (std::fabs(p3) < mc::machprec()) {
	  	term1 = p2*(x-x0); // The limit of p3/tanh(p3/x) for p3->0 is x
	  } else {
	  	term1 = p2*std::fabs(p3)*(1/std::tanh(std::fabs(p3)/x)-1/std::tanh(std::fabs(p3)/x0));
	  }
	  return p1*(x-x0) + term1 - p4*std::fabs(p5)*(std::tanh(std::fabs(p5)/x)-std::tanh(std::fabs(p5)/x0));
      break;
	}
    case 4: // DIPPR 127 equation
	{
  	  double term1, term2, term3;
	  if (std::fabs(p3) < mc::machprec()) {
	  	term1 = p2*(x-x0);	// The limit of p3/(exp(p3/x)-1) for p3->0 is x
	  } else {
	  	term1 = p2*p3*(1/(std::exp(p3/x)-1)-1/(std::exp(p3/x0)-1));
	  }
	  if (std::fabs(p5) < mc::machprec()) {
	  	term2 = p4*(x-x0);	// The limit of p5/(exp(p5/x)-1) for p5->0 is x
	  } else {
	  	term2 = p4*p5*(1/(std::exp(p5/x)-1)-1/(std::exp(p5/x0)-1));
	  }
	  if (std::fabs(p7) < mc::machprec()) {
	  	term3 = p6*(x-x0);	// The limit of p7/(exp(p7/x)-1) for p7->0 is x
	  } else {
	  	term3 = p6*p7*(1/(std::exp(p7/x)-1)-1/(std::exp(p7/x0)-1));
	  }
      return p1*(x-x0) + term1 + term2 + term3;
      break;
    }
    default:
      throw std::runtime_error("mc::McCormick\t Ideal Gas Enthalpy called with an unknown type.");
      break;
  }
}


//added AVT.SVT 01.09.2017
inline double der_ideal_gas_enthalpy
(const double x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4,
 const double p5, const double p6 = 0, const double p7 = 0 )
{
  switch((int)type){
    case 1: // Aspen polynomial (implementing only the high-temperature version); the NASA "7"-coefficient polynomial is equivalent with the last parameter equal to 0
      return p1 + p2*x + p3*std::pow(x,2) + p4*std::pow(x,3) + p5*std::pow(x,4) + p6*std::pow(x,5);
      break;
    case 2: // NASA "9"-coefficient polynomial
      return p1/std::pow(x,2) + p2/x + p3 + p4*x + p5*std::pow(x,2) + p6*std::pow(x,3) + p7*std::pow(x,4);
      break;
    case 3: // DIPPR 107 equation
	{
	  // The DIPPR107 model is symmetric w.r.t. the sign of p3 and p5. If for some reason one of them is negative, we just switch the sign to be able to use the standard integrated for
	  double term1;
	  double tmp1(std::fabs(p3)/x);
	  double tmp2(std::fabs(p5)/x);
	  if (std::fabs(p3) < mc::machprec()) {
	  	term1 = p2;
	  } else {
	  	term1 = p2*std::pow(tmp1/std::sinh(tmp1),2);
	  }
      return p1 + term1 + p4*std::pow(tmp2/std::cosh(tmp2),2);
      break;
	}
    case 4: // DIPPR 127 equation
	{
	  double tmp1(p3/x);
	  double tmp2(p5/x);
	  double tmp3(p7/x);
	   double term1, term2, term3;
	  if (std::fabs(p3) < mc::machprec()) {
	  	term1 = p2;
	  } else {
	  	term1 = p2*(std::pow(tmp1,2)*std::exp(tmp1)/std::pow(std::exp(tmp1)-1,2));
	  }
	  if (std::fabs(p5) < mc::machprec()) {
	  	term2 = p4;
	  } else {
	  	term2 = p4*(std::pow(tmp2,2)*std::exp(tmp2)/std::pow(std::exp(tmp2)-1,2));
	  }
	  if (std::fabs(p7) < mc::machprec()) {
	  	term3 = p6;
	  } else {
	  	term3 = p6*(std::pow(tmp3,2)*std::exp(tmp3)/std::pow(std::exp(tmp3)-1,2));
	  }
      return p1 + term1 + term2 + term3;
      break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Ideal Gas Enthalpy called with an unknown type.");
      break;
  }
}


//added AVT.SVT 01.09.2017
//***Note that all functions are are assumed to be concave and nonincreasing *below p1* ***
inline double enthalpy_of_vaporization
(const double x, const double type, const double p1, const double p2, const double p3, const double p4,
 const double p5, const double p6 = 0)
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  switch((int)type){
    case 1: // Watson equation
	{
	  double tmp1 = 1-x/p1;	// this is 1-Tr
	  if (tmp1 > 0) {
		  return p5 * std::pow(tmp1/(1-p4/p1),p2+p3*tmp1);
	  } else {
		  return 0.;
	  }
	  break;
	}
	case 2: // DIPPR 106
	{
	  double Tr = x/p1;
	  if (Tr < 1) {
		return p2 * std::pow(1-Tr,p3+p4*Tr+p5*std::pow(Tr,2)+p6*std::pow(Tr,3));
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

//added AVT.SVT 01.09.2017
inline double der_enthalpy_of_vaporization
(const double x, const double type, const double p1, const double p2, const double p3, const double p4,
 const double p5, const double p6 = 0 )
{
  switch((int)type){
    case 1: // Watson equation
	{
	  double tmp1 = 1-x/p1;	// this is 1-Tr
	  if (tmp1 > 0) {
		return mc::enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6)/p1 * (-(p2+p3*tmp1)/tmp1 - p3*std::log(tmp1/(1-p4/p1)));
	  } else {
		  return 0.;
	  }
	  break;
	}
	case 2: // DIPPR 106
	{
	  double Tr = x/p1;
	  if (Tr < 1) {
		  return mc::enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6)/p1 * ( -(p3+p4*Tr+p5*std::pow(Tr,2)+p6*std::pow(Tr,3))/(1-Tr) + (p4+2*p5*Tr+3*p6*std::pow(Tr,2))*std::log(1-Tr) );
	  } else {
		  return 0;
	  }
	  break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Enthalpy of Vaporization called with an unknown type.");
      break;
  }
}


//added AVT.SVT 06.11.2017
inline double cost_function
(const double x, const double type, const double p1, const double p2, const double p3 )
{
  switch((int)type){
    case 1: // Guthrie cost function
	{
	  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
	  return std::pow( 10.,p1 + p2*std::log(x)/std::log(10.) + p3*std::pow(std::log(x)/std::log(10.),2) );
	  break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Cost function called with an unknown type.\n");
      break;
  }
}


//added AVT.SVT 06.11.2017
inline double der_cost_function
(const double x, const double type, const double p1, const double p2, const double p3 )
{
  switch((int)type){
    case 1: // Guthrie cost function
	{
	  return std::pow( 10.,p1 + p2*std::log(x)/std::log(10.) + p3*std::pow(std::log(x)/std::log(10.),2) ) *
             ( p2/x + 2*p3*std::log(x)/(x*std::log(10.)) );
	  break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Cost function called with an unknown type.");
      break;
  }
}

//added AVT.SVT 06.11.2017
inline double der2_cost_function
(const double x, const double type, const double p1, const double p2, const double p3 )
{
  switch((int)type){
    case 1: // Guthrie cost function
	{
	  return mc::cost_function(x,type,p1,p2,p3)*std::log(10.)
	         *(std::log(10.)*mc::sqr(p2/(x*std::log(10.)) + (2*p3*std::log(x))/(x*sqr(std::log(10.)))) - p2/(sqr(x)*std::log(10.)) + 2*p3/(sqr(x*std::log(10.))) - 2*p3*std::log(x)/(sqr(x*std::log(10.))));
	  break;
	}
    default:
      throw std::runtime_error("mc::McCormick\t Cost function called with an unknown type.");
      break;
  }
}

//needed for intervals of nrtl_tau, nrtl_dtau and cost_function
enum MONOTONICITY{
	  MON_NONE = 0,		//!< not increasing or decreasing
	  MON_INCR,			//!< increasing
	  MON_DECR			//!< decreasing
};

// function used for getting monotonicity (in the case in nonmonotonicity the min and max values) of cost functions for interval computations
inline MONOTONICITY
get_monotonicity_cost_function
(const double type, const double p1, const double p2, const double p3, const double l, const double u, double& min, double& max, bool computeMinMax)
{
	switch((int)type){
		case 1:
			// special case p3 = 0
			if(p3 == 0){
				if(p2 >= 0.){
					// increasing
					return MON_INCR;
				}
				else{
					// decreasing
					return MON_DECR;
				}
			}
			else{
				//we have exactly one root
				double root = std::exp(-p2*std::log(10.)/(2.0*p3));
				if( root <= l){ // left of the interval
					if(p3 >= 0. ){
						// increasing
						return MON_INCR;
					}
					else{
						// decreasing
						return MON_DECR;
					}
				}
				else if( root >= u){ // right of the interval
					if(p3 >= 0. ){
						//decreasing
						return MON_DECR;
					}
					else{
						//increasing
						return MON_INCR;
					}
				}

				if(computeMinMax){
					double extreme_point = std::exp(-p2*std::log(10.)/(2*p3));
					if(p3>0.){
						//minimum
						min = mc::cost_function(extreme_point,type,p1,p2,p3);
						if(mc::cost_function(l,type,p1,p2,p3)>mc::cost_function(u,type,p1,p2,p3)){
							max = mc::cost_function(l,type,p1,p2,p3);
						}else{
							max = mc::cost_function(u,type,p1,p2,p3);
						}
					}
					else if (p3<0.){
						max = mc::cost_function(extreme_point,type,p1,p2,p3);
						if(mc::cost_function(l,type,p1,p2,p3)<mc::cost_function(u,type,p1,p2,p3)){
							min = mc::cost_function(l,type,p1,p2,p3);
						}else{
							min = mc::cost_function(u,type,p1,p2,p3);
						}
					}
					else { // case p3 = 0
						if(mc::cost_function(l,type,p1,p2,p3)>mc::cost_function(u,type,p1,p2,p3)){
							max = mc::cost_function(l,type,p1,p2,p3);
							min = mc::cost_function(u,type,p1,p2,p3);
						}else{
							max = mc::cost_function(u,type,p1,p2,p3);
							min = mc::cost_function(l,type,p1,p2,p3);
						}
					}
				}
			}
			break;

		default:
		    throw std::runtime_error("mc::McCormick\t Cost function called with an unknown type.");
		    break;
	}
	return MON_NONE;
}

//added AVT.SVT 23.11.2017
inline double nrtl_tau
(const double x, const double a, const double b, const double e, const double f )
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  //nrtl tau given as a + b/T + e*ln(T) + f*T <-- see ASPEN
  return a+b/x + e*std::log(x) + f*x;
}


//added AVT.SVT 23.11.2017
inline double nrtl_dtau
(const double x, const double b, const double e, const double f )
{

  return f-b/std::pow(x,2) + e/x;
}

//added AVT.SVT 23.11.2017
inline double der2_nrtl_tau
(const double x, const double b, const double e )
{

  return 2*b/std::pow(x,3) - e/std::pow(x,2);
}

//added AVT.SVT 23.11.2017
inline double nrtl_G
(const double x, const double a, const double b, const double e, const double f, const double alpha )
{
  //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
  //alpha is c or alpha <-- see ASPEN
  //nrtl tau given as exp(-alpha*(a + b/T + e*ln(T) + f*T)) <-- see ASPEN
  return std::exp( -alpha*( a+b/x + e*std::log(x) + f*x) );
}


//added AVT.SVT 23.11.2017
inline double der_nrtl_G
(const double x, const double a, const double b, const double e, const double f, const double alpha )
{

  return -alpha * mc::nrtl_G(x,a,b,e,f,alpha) * mc::nrtl_dtau(x,b,e,f);
}


//added AVT.SVT 23.11.2017
inline double der2_nrtl_G
(const double x, const double a, const double b, const double e, const double f, const double alpha )
{

  // return std::pow(alpha,2) * std::exp( -alpha*( a+b/x + e*std::log(x) + f*x) ) * std::pow(( f-b/std::pow(x,2) + e/x),2)
		 // - alpha *std::exp( -alpha*( a+b/x + e*std::log(x) + f*x) )*(2*b/std::pow(x,3) - e/std::pow(x,2)) ;
	return std::pow(alpha,2) * mc::nrtl_G(x,a,b,e,f,alpha) * std::pow(mc::nrtl_dtau(x,b,e,f),2) - alpha * mc::nrtl_G(x,a,b,e,f,alpha) * mc::der2_nrtl_tau(x,b,e);
}


//added AVT.SVT 01.03.2018
inline double nrtl_Gtau
(const double x, const double a, const double b, const double e, const double f, const double alpha )
{
//the parameters are a,b,e,f and alpha, for further info, see ASPEN help
 //moved the check for number of parameters to ffunc.hpp, since we need to check the number only once, namely when the DAG is constructed
      return std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) ) * ( a + b/x + e*std::log(x) + f*x );

}

//derivative of G*tau
inline double der_nrtl_Gtau
(const double x, const double a, const double b, const double e, const double f, const double alpha  )
{
//the parameters are a,b,e,f and alpha, for further info, see ASPEN help
      return std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) ) * (  -b/std::pow(x,2) + e/x + f )
             *( 1.0 - alpha*( a + b/x + e*std::log(x) + f*x ) );

}

//second derivative of G*tau
inline double der2_nrtl_Gtau
(const double x, const double a, const double b, const double e, const double f, const double alpha  )
{
//the parameters are a,b,e,f and alpha, for further info, see ASPEN help
      return std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) ) *
             ( (  2.0*b/std::pow(x,3) - e/std::pow(x,2) ) * ( 1.0 - alpha*( a + b/x + e*std::log(x) + f*x ) )
              +( std::pow(f-b/std::pow(x,2)+e/x ,2) * (std::pow(alpha,2)*( a + b/x + e*std::log(x) + f*x ) -2*alpha  ) ) );

}

//nrtl function G * dtau/dT
inline double nrtl_Gdtau
(const double x, const double a, const double b, const double e, const double f, const double alpha)
{
  //the parameters are a,b,e,f and alpha, for further info, see ASPEN help
  return std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) )*(f - b/std::pow(x,2) + e/x);
}

//first derivative of G * dtau/dT
inline double der_nrtl_Gdtau
(const double x, const double a, const double b, const double e, const double f, const double alpha)
{
	//the parameters are a,b,e,f and alpha, for further info, see ASPEN help
	return  std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) )*(2.0*b/std::pow(x,3) - e/std::pow(x,2))
	  -alpha*std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) )*std::pow((f - b/std::pow(x,2) + e/x),2);
}

//second derivative of G * dtau/dT
inline double der2_nrtl_Gdtau
(const double x, const double a, const double b, const double e, const double f, const double alpha)
{
	//the parameters are a,b,e,f and alpha, for further info, see ASPEN help
	return  std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) )*( std::pow(alpha,2)*std::pow((f - b/std::pow(x,2) + e/x),3)
           -(6.0*b/std::pow(x,4) -2.0*e/std::pow(x,3)) - 3.0*alpha*(f - b/std::pow(x,2) + e/x)*(2.0*b/std::pow(x,3) - e/std::pow(x,2)) );
}

//nrtl dG/dT * tau function
inline double nrtl_dGtau
(const double x, const double a, const double b, const double e, const double f, const double alpha)
{
  //the parameters are a,b,e,f and alpha, for further info, see ASPEN help
  return -alpha*std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) )*(f - b/std::pow(x,2) + e/x)
	 *( a + b/x + e*std::log(x) + f*x );
}

//first derivative of dG/dT * tau
inline double der_nrtl_dGtau
(const double x, const double a, const double b, const double e, const double f, const double alpha)
{
  //the parameters are a,b,e,f and alpha, for further info, see ASPEN help
  return -alpha*std::exp( -alpha*( a + b/x + e*std::log(x) + f*x ) )*(
				  std::pow((f - b/std::pow(x,2) + e/x),2)
				  +(2.0*b/std::pow(x,3)-e/std::pow(x,2))*( a + b/x + e*std::log(x) + f*x )
				  -alpha*std::pow((f - b/std::pow(x,2) + e/x),2)*( a + b/x + e*std::log(x) + f*x ) );
}

//second derivative of dG/dT * tau
inline double der2_nrtl_dGtau
(const double x, const double a, const double b, const double e, const double f, const double alpha)
{
  //the parameters are a,b,e,f and alpha, for further info, see ASPEN help
  double s1 = ( a + b/x + e*std::log(x) + f*x );
  double s2 = (f - b/std::pow(x,2) + e/x);
  double s3 = (2.0*b/std::pow(x,3)-e/std::pow(x,2));

  return alpha*std::exp(-alpha*s1)*( s1*(6.0*b/std::pow(x,4)-2.0*e/std::pow(x,3)) - 3.0*s3*s2 + 2.0*alpha*std::pow(s2,3) -std::pow(alpha,2)*std::pow(s2,3)*s1
						+3.0*alpha*s3*s2*s1);
}

// function used for getting monotonicity (in the case in nonmonotonicity the min and max values) of nrtl_tau for interval computations
inline MONOTONICITY
get_monotonicity_nrtl_tau
(const double a, const double b, const double e, const double f, const double l, const double u, double& min, double& max, bool computeMinMax)
{
	// for further details, please refer to Najman, Bongartz & Mitsos 2019 Relaxations of thermodynamic property and costing models in process engineering
	if(f == 0. && e == 0.){
		if(b <= 0 ){ return MON_INCR;}else{ return MON_DECR;}
	}
	else if(f == 0.){
		double root = b/e;
		if(root <= 0){ // if it is not > 0, then do a simple corner check
			if(mc::nrtl_tau(l,a, b, e, f) < mc::nrtl_tau(u, a, b, e, f) ){ return MON_INCR;}else{ return MON_DECR;}
		}
		else if(root <= l ){ // left of the interval
			if(std::pow(e,3)/std::pow(b,2)>0 ){ return MON_INCR;}else{ return MON_DECR;} //check if its a minimum or maximum
		}
		else if(root >= u ){ // left of the interval
			if(std::pow(e,3)/std::pow(b,2)>0 ){ return MON_DECR;}else{ return MON_INCR;} //check if its a minimum or maximum
		}
		else { // the root lies in the interval and the function is not monotonic but we can still get tight interval bounds
			if (std::pow(e, 3) / std::pow(b, 2)>0) { //minimum
				min = mc::nrtl_tau(b / e, a, b, e, f);
				if (mc::nrtl_tau(l, a, b, e, f) <= mc::nrtl_tau(u, a, b, e, f)) {
					max = mc::nrtl_tau(u, a, b, e, f);
				}
				else {
					max = mc::nrtl_tau(l, a, b, e, f);
				}
			}
			else {	//maximum
				max = mc::nrtl_tau(b / e, a, b, e, f);
				if (mc::nrtl_tau(l, a, b, e, f) <= mc::nrtl_tau(u, a, b, e, f)) {
					min = mc::nrtl_tau(l, a, b, e, f);
				}
				else {
					min = mc::nrtl_tau(u, a, b, e, f);
				}
			}
			return MON_NONE;
		}
	}
	else{

	    double val = std::pow(e,2) +4.0*b*f;
        if(val < 0.){ // check of Assumption 1 we have no roots, so simply check corners
			if(mc::nrtl_tau(l,a,b,e,f) < mc::nrtl_tau(u,a,b,e,f) ){ return MON_INCR;} else{ return MON_DECR;}
		}
		else{
			//in this case, we have two roots with r1 < r2
			double r1 = std::min(-(e+std::sqrt(val ))/(2.0*f),-(e-std::sqrt(val ))/(2.0*f));
			double r2 = std::max(-(e+std::sqrt(val ))/(2.0*f),-(e-std::sqrt(val ))/(2.0*f));

			// if the right root does not lie in the valid domain T>0 then its second derivative is invalid for the following checks
			if(r2 <= 0. ){ // if it is not > 0, then do a simple corner check
				if(mc::nrtl_tau(l,a, b, e, f) < mc::nrtl_tau(u, a, b, e, f) ){ return MON_INCR;}else{ return MON_DECR;}
			}
			else{
				// note that checking only der2_nrtl_tau is cheaper than checking nrtl_tau twice when evaluating corner points
				// the right root does not lie in the interval and is left of the interval
				if(r2 <= l){
					if(mc::der2_nrtl_tau(r2,b,e) > 0. ){ return MON_INCR;}else{ return MON_DECR;} //check if its a minimum or maximum
				}
				// the left root does not lie in the interval and is right of the interval
				else if(r1 >= u){
					if(mc::der2_nrtl_tau(r1,b,e) > 0. ){ return MON_DECR;}else{ return MON_INCR;} //check if its a minimum or maximum
				}
				// both roots are outside the interval
				else if (r1 <= l && u <= r2){
					if(r1 <= 0.){		 // the smaller root can still be invalid
						if(mc::der2_nrtl_tau(r2,b,e) > 0. ){ return MON_DECR;}else{ return MON_INCR;} //check if its a minimum or maximum
					}
					else{
						if(mc::der2_nrtl_tau(r1,b,e) > 0. ){ return MON_INCR;}else{ return MON_DECR;} //check if its a minimum or maximum
					}
				}
				if(computeMinMax){
				    // at least one root lies within the interval bounds
					// we can still get tight interval bounds
					// check if left root lies in the interval bounds
					if(l<r1){
						// save value at root and root
						if(mc::der2_nrtl_tau(r1,b,e) > 0.){	// minimum
							min = mc::nrtl_tau(r1,a,b,e,f);
						}
						else{	// maximum
							max = mc::nrtl_tau(r1,a,b,e,f);
						}
					}
					// check if right root lies in the interval bounds
					if(r2<u){
						if(mc::der2_nrtl_tau(r2,b,e) > 0.){	// minimum
							min = mc::nrtl_tau(r2,a,b,e,f);
						}
						else{	// maximum
							max = mc::nrtl_tau(r2,a,b,e,f);
						}
					}

					if(mc::nrtl_tau(l,a,b,e,f) < min){ min = mc::nrtl_tau(l,a,b,e,f); }
					if(mc::nrtl_tau(u,a,b,e,f) < min){ min = mc::nrtl_tau(u,a,b,e,f); }
					if(mc::nrtl_tau(l,a,b,e,f) > max){ max = mc::nrtl_tau(l,a,b,e,f); }
					if(mc::nrtl_tau(u,a,b,e,f) > max){ max = mc::nrtl_tau(u,a,b,e,f); }
				}
			}
		}
	}

	return MON_NONE;
}

// function used for getting monotonicity (in the case in nonmonotonicity the min and max values) of nrtl_dtau for interval computations
inline MONOTONICITY
get_monotonicity_nrtl_dtau
(const double b, const double e, const double f, const double l, const double u, double& min, double& max, bool computeMinMax)
{
	// for further details, please refer to Najman, Bongartz & Mitsos 2019 Relaxations of thermodynamic property and costing models in process engineering
	if(b == 0. && e == 0.){
		if(mc::der2_nrtl_tau(l,b,e) >= 0 ){ return MON_INCR;}else{ return MON_DECR;}
	}
	else{
	    //in this case, we have one root
		double root = 2.0*b/e;
		if( root <= 0. ){ //if it is not > 0, then do a simple corner check
			if(mc::nrtl_dtau(l,b,e,f) < mc::nrtl_dtau(u,b,e,f) ){ return MON_INCR;}else{ return MON_DECR;}
		}
		else{
			if(root <= l){
				if( b<=0 ){ return MON_INCR;}else{ return MON_DECR;} //check if its a minimum or maximum, if b <= 0 then it's a minimum
			}
			else if(root >= u){
				if( b<=0 ){ return MON_DECR;}else{ return MON_INCR;} //check if its a minimum or maximum, if b <= 0 then it's a minimum
			}

			if(computeMinMax){
				if(b<=0){ // it's a minimum
					//lower bound and min point
					min = mc::nrtl_dtau(root,b,e,f);
					//upper bound and max point
					if(mc::nrtl_dtau(l,b,e,f) <= mc::nrtl_dtau(u,b,e,f)){
						max = mc::nrtl_dtau(u,b,e,f);
					}else{
						max = mc::nrtl_dtau(l,b,e,f);
					}
				}else{ // it is a maximum
					//lower bound and min point
					if(mc::nrtl_dtau(l,b,e,f) <= mc::nrtl_dtau(u,b,e,f)){
						min = mc::nrtl_dtau(l,b,e,f);
					}else{
						min = mc::nrtl_dtau(u,b,e,f);
					}
					//upper bound and max point
					max = mc::nrtl_dtau(root,b,e,f);
				}
			}
		}
	}
	return MON_NONE;
}

//added AVT.SVT 01.03.2018
inline double expx_times_y
(const double x, const double y)
{
  return std::exp(x)*y;
}

//the function is convex and increasing
inline double p_sat_ethanol_schroeder
(const double x)
{
	const double _T_c_K = 514.71;
	if(x>_T_c_K){
		throw std::runtime_error("mc::McCormick\t p_sat_ethanol_schroeder: No saturated state for overcritical temperature.");
	}
	if(x<0){
		throw std::runtime_error("mc::McCormick\t p_sat_ethanol_schroeder: Temperature can not be negative.");
	}
	const double _N_Tsat_1 = -8.94161;
	const double _N_Tsat_2 = 1.61761;
	const double _N_Tsat_3 = -51.1428;
	const double _N_Tsat_4 = 53.1360;
	const double _k_Tsat_1 = 1.0;
	const double _k_Tsat_2 = 1.5;
	const double _k_Tsat_3 = 3.4;
	const double _k_Tsat_4 = 3.7;
	const double _p_c = 62.68;

	return _p_c*(std::exp(_T_c_K/x*(_N_Tsat_1*std::pow((1-x/_T_c_K),_k_Tsat_1) + _N_Tsat_2*std::pow((1-x/_T_c_K),_k_Tsat_2) + _N_Tsat_3*std::pow((1-x/_T_c_K),_k_Tsat_3)
			+ _N_Tsat_4*std::pow((1-x/_T_c_K),_k_Tsat_4))));
}

inline double der_p_sat_ethanol_schroeder
(const double x)
{
	const double _T_c_K = 514.71;
	if(x>_T_c_K){
		throw std::runtime_error("mc::McCormick\t der_p_sat_ethanol_schroeder: No saturated state for overcritical temperature.");
	}
	if(x<0){
		throw std::runtime_error("mc::McCormick\t der_p_sat_ethanol_schroeder: Temperature can not be negative.");
	}
	const double _N_Tsat_1 = -8.94161;
	const double _N_Tsat_2 = 1.61761;
	const double _N_Tsat_3 = -51.1428;
	const double _N_Tsat_4 = 53.1360;
	const double _k_Tsat_1 = 1.0;
	const double _k_Tsat_2 = 1.5;
	const double _k_Tsat_3 = 3.4;
	const double _k_Tsat_4 = 3.7;
	const double _p_c = 62.68;

	return _p_c*(std::exp(_T_c_K/x*(_N_Tsat_1*std::pow((1-x/_T_c_K),_k_Tsat_1) + _N_Tsat_2*std::pow((1-x/_T_c_K),_k_Tsat_2) + _N_Tsat_3*std::pow((1-x/_T_c_K),_k_Tsat_3)
			+ _N_Tsat_4*std::pow((1-x/_T_c_K),_k_Tsat_4))))* ((-1/(x*(1-x/_T_c_K))) * (_N_Tsat_1*_k_Tsat_1*std::pow((1-x/_T_c_K),_k_Tsat_1) + _N_Tsat_2*_k_Tsat_2*std::pow((1-x/_T_c_K),_k_Tsat_2)
			+ _N_Tsat_3*_k_Tsat_3*std::pow((1-x/_T_c_K),_k_Tsat_3) + _N_Tsat_4*_k_Tsat_4*std::pow((1-x/_T_c_K),_k_Tsat_4)) - (_T_c_K/mc::sqr(x)) * (_N_Tsat_1*std::pow((1-x/_T_c_K),_k_Tsat_1)
			+ _N_Tsat_2*std::pow((1-x/_T_c_K),_k_Tsat_2) + _N_Tsat_3*std::pow((1-x/_T_c_K),_k_Tsat_3) + _N_Tsat_4*std::pow((1-x/_T_c_K),_k_Tsat_4)));
}

//the function is convex and increasing
inline double rho_vap_sat_ethanol_schroeder
(const double x)
{
	const double _T_c_K = 514.71;
	if(x>_T_c_K){
		throw std::runtime_error("mc::McCormick\t rho_vap_sat_ethanol_schroeder: No saturated state for overcritical temperature.");
	}
	if(x<0){
		throw std::runtime_error("mc::McCormick\t rho_vap_sat_ethanol_schroeder: Temperature can not be negative.");
	}
	const double _N_vap_1 = -1.75362;
	const double _N_vap_2 = -10.5323;
	const double _N_vap_3 = -37.6407;
	const double _N_vap_4 = -129.762;
	const double _k_vap_1 = 0.21;
	const double _k_vap_2 = 1.1;
	const double _k_vap_3 = 3.4;
	const double _k_vap_4 = 10;
	const double _rho_c = 273.195;

	return _rho_c*(std::exp(_N_vap_1*std::pow((1 - x/_T_c_K),_k_vap_1) + _N_vap_2*std::pow((1 - x/_T_c_K),_k_vap_2) + _N_vap_3*std::pow((1 - x/_T_c_K),_k_vap_3) + _N_vap_4*std::pow((1 - x/_T_c_K),_k_vap_4)));
}

inline double der_rho_vap_sat_ethanol_schroeder
(const double x)
{
	const double _T_c_K = 514.71;
	if(x>_T_c_K){
		throw std::runtime_error("mc::McCormick\t der_rho_vap_sat_ethanol_schroeder: No saturated state for overcritical temperature.");
	}
	if(x<0){
		throw std::runtime_error("mc::McCormick\t der_rho_vap_sat_ethanol_schroeder: Temperature can not be negative.");
	}
	const double _N_vap_1 = -1.75362;
	const double _N_vap_2 = -10.5323;
	const double _N_vap_3 = -37.6407;
	const double _N_vap_4 = -129.762;
	const double _k_vap_1 = 0.21;
	const double _k_vap_2 = 1.1;
	const double _k_vap_3 = 3.4;
	const double _k_vap_4 = 10;
	const double _rho_c = 273.195;

	return _rho_c*(std::exp(_N_vap_1*std::pow((1 - x/_T_c_K),_k_vap_1) + _N_vap_2*std::pow((1 - x/_T_c_K),_k_vap_2) + _N_vap_3*std::pow((1 - x/_T_c_K),_k_vap_3)
			+ _N_vap_4*std::pow((1 - x/_T_c_K),_k_vap_4)))* (1/(x-_T_c_K)) * (_N_vap_1*_k_vap_1*std::pow((1 - x/_T_c_K),_k_vap_1) + _N_vap_2*_k_vap_2*std::pow((1 - x/_T_c_K),_k_vap_2)
			+ _N_vap_3*_k_vap_3*std::pow((1 - x/_T_c_K),_k_vap_3) + _N_vap_4*_k_vap_4*std::pow((1 - x/_T_c_K),_k_vap_4));
}

//the function is concave and decreasing
inline double rho_liq_sat_ethanol_schroeder
(const double x)
{
	const double _T_c_K = 514.71;
	if(x>_T_c_K){
		throw std::runtime_error("mc::McCormick\t rho_liq_sat_ethanol_schroeder: No saturated state for overcritical temperature.");
	}
	if(x<0){
		throw std::runtime_error("mc::McCormick\t rho_liq_sat_ethanol_schroeder: Temperature can not be negative.");
	}
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

	return _rho_c*(1 + _N_liq_1*std::pow((1 - x/_T_c_K),_k_liq_1) + _N_liq_2*std::pow((1 - x/_T_c_K),_k_liq_2) + _N_liq_3*std::pow((1 - x/_T_c_K),_k_liq_3)
			+ _N_liq_4*std::pow((1 - x/_T_c_K),_k_liq_4) + _N_liq_5*std::pow((1 - x/_T_c_K),_k_liq_5));
}

inline double der_rho_liq_sat_ethanol_schroeder
(const double x)
{
	const double _T_c_K = 514.71;
	if(x>_T_c_K){
		throw std::runtime_error("mc::McCormick\t der_rho_liq_sat_ethanol_schroeder: No saturated state for overcritical temperature.");
	}
	if(x<0){
		throw std::runtime_error("mc::McCormick\t der_rho_liq_sat_ethanol_schroeder: Temperature can not be negative.");
	}
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

	return (_rho_c/(x-_T_c_K))*(_N_liq_1*_k_liq_1*std::pow((1 - x/_T_c_K),_k_liq_1) + _N_liq_2*_k_liq_2*std::pow((1 - x/_T_c_K),_k_liq_2) + _N_liq_3*_k_liq_3*std::pow((1 - x/_T_c_K),_k_liq_3)
			+ _N_liq_4*_k_liq_4*std::pow((1 - x/_T_c_K),_k_liq_4) + _N_liq_5*_k_liq_5*std::pow((1 - x/_T_c_K),_k_liq_5));
}

// the functions are convex and monotonically decreasing
inline double covariance_function
(const double x, const double type){

	if(x<0){
		  throw std::runtime_error("mc::McCormick\t Covariance function called with negative value x<0.\n");
	}

	if(x==0.){
		return 1;
	}

    switch((int)type){
		case 1: // matern 1/2
		{
		    return std::exp(-std::sqrt(x));
			break;
		}
		case 2: // matern 3/2
		{
			const double tmp = std::sqrt(3)*std::sqrt(x);
			return std::exp(-tmp) + tmp*std::exp(-tmp);
			break;
		}
		case 3: // matern 5/2
		{
			const double tmp = std::sqrt(5)*std::sqrt(x);
			return std::exp(-tmp) + tmp*std::exp(-tmp) + 5./3.*x*std::exp(-tmp);
			break;
		}
		case 4: // squared exponential
		{
			return std::exp(-0.5*x);
			break;
		}
		default:
		  throw std::runtime_error("mc::McCormick\t Covariance function called with an unknown type.\n");
		  break;
    }
}

// the functions are convex and monotonically decreasing
inline double der_covariance_function
(const double x, const double type){

	if(x<0){
		  throw std::runtime_error("mc::McCormick\t Derivative of covariance function called with negative value x<0.\n");
	}

    switch((int)type){
		case 1: // matern 1/2
		{
			if(x==0.){
				return -1e51;
			}
		    return -std::exp(-std::sqrt(x)) / (2. * std::sqrt(x));
			break;
		}
		case 2: // matern 3/2
		{
			return -3./2. * std::exp(-std::sqrt(3)*std::sqrt(x));
			break;
		}
		case 3: // matern 5/2
		{
			double tmp = std::sqrt(5)*std::sqrt(x);
			return -5./6. * std::exp(-tmp)*(tmp+1);
			break;
		}
		case 4: // squared exponential
		{
			return -0.5*std::exp(-0.5*x);
			break;
		}
		default:
		  throw std::runtime_error("mc::McCormick\t Derivative of covariance function called with an unknown type.\n");
		  break;
    }
}

inline double gaussian_cumulative_distribution
(const double x){
	return std::erf(1./std::sqrt(2)*x)/2.+0.5;
}

inline double gaussian_probability_density_function
(const double x){
	return 1./(std::sqrt(2*mc::PI)) * std::exp(-std::pow(x,2)/2.);
}

inline double der_gaussian_probability_density_function
(const double x){
	return  (-x)*mc::gaussian_probability_density_function(x);
}

inline double acquisition_function
(const double mu, const double sigma, const double type, const double fmin){

    if(sigma<0){
		  throw std::runtime_error("mc::McCormick\t Acquisition function called with sigma < 0.\n");
	}

    switch((int)type){
		case 1: // lower confidence bound
		{
		    return mu - fmin*sigma;
		}
		case 2: // expected improvement
		{
			if(sigma == 0){
				return std::max(fmin-mu, 0.);
			}
			const double x = mu - fmin;
			return (-x)*mc::gaussian_cumulative_distribution(-x/sigma) + sigma*mc::gaussian_probability_density_function(-x/sigma);
		}
		case 3: // probability of improvement
		{
		    if(sigma == 0 && fmin <= mu){
				return 0;
			}
			if(sigma == 0 && fmin > mu){
				return 1;
			}
		    const double x = mu - fmin;
			return mc::gaussian_cumulative_distribution(-x/sigma);
		}
		default:
		  throw std::runtime_error("mc::McCormick\t Acquisition function called with an unknown type.\n");
    }
}

inline double der_x_acquisition_function
(const double mu, const double sigma, const double type, const double fmin){

    if(sigma<0){
		  throw std::runtime_error("mc::McCormick\t Derivative of acquisition function w.r.t. x called with sigma < 0.\n");
	}

    switch((int)type){
		case 1: // lower confidence bound
		{
		    return 1;
		}
		case 2: // expected improvement
		{
			if(sigma == 0){
				if(fmin-mu>0){
					return -1;
				}else{
					return 0;
				}
			}
			const double x = mu - fmin;
			return -mc::gaussian_cumulative_distribution(-x/sigma);
		}
		case 3: // probability of improvement
		{
			if(sigma == 0){
				return 0;
			}
			const double x = mu - fmin;
		    return - std::exp(-std::pow(x,2) / (2*std::pow(sigma,2))) / (sigma*std::sqrt(2*mc::PI));
		}
		default:
		  throw std::runtime_error("mc::McCormick\t Derivative of acquisition function called with an unknown type.\n");
    }
}

inline double der_y_acquisition_function
(const double mu, const double sigma, const double type, const double fmin){

    if(sigma<0){
		  throw std::runtime_error("mc::McCormick\t Derivative of acquisition function w.r.t. y called with sigma < 0.\n");
	}

    switch((int)type){
		case 1: // lower confidence bound
		{
		    return -fmin;
		}
		case 2: // expected improvement
		{
			if(sigma == 0){
				return 0;
			}
			const double x = mu - fmin;
			return mc::gaussian_probability_density_function(-x/sigma);
		}
		case 3: // probability of improvement
		{
			if(sigma == 0){
				return 0;
			}
			double x = mu - fmin;
		    return std::exp(-std::pow(x,2) / (2*std::pow(sigma,2))) * x / (std::pow(sigma,2)*std::sqrt(2*mc::PI));
		}
		default:
		  throw std::runtime_error("mc::McCormick\t Derivative of acquisition function called with an unknown type.\n");
    }
}


inline double der_x2_acquisition_function
(const double mu, const double sigma, const double type, const double fmin){

    if(sigma<0){
		  throw std::runtime_error("mc::McCormick\t Second derivative of acquisition function w.r.t. x called with sigma < 0.\n");
	}

    switch((int)type){
		case 1: // lower confidence bound
		case 2: // expected improvement
		  throw std::runtime_error("mc::McCormick\t Second Derivative of acquisition function not implemented for types 1 and 2.\n");
		case 3: // probability of improvement
		{
			if(sigma == 0){
				return 0;
			}
			const double x = mu - fmin;
		    return (x*std::exp(-std::pow(x,2)/(2*std::pow(sigma,2)))) / (std::pow(sigma,3)*std::sqrt(2*mc::PI));
		}
		default:
		  throw std::runtime_error("mc::McCormick\t Second derivative of acquisition function called with an unknown type.\n");
    }
}


inline double der_y2_acquisition_function
(const double mu, const double sigma, const double type, const double fmin){

    if(sigma<0){
		  throw std::runtime_error("mc::McCormick\t Second derivative of acquisition function w.r.t. x called with sigma < 0.\n");
	}

    switch((int)type){
		case 1: // lower confidence bound
		case 2: // expected improvement
		  throw std::runtime_error("mc::McCormick\t Second Derivative of acquisition function not implemented for types 1 and 2.\n");
		case 3: // probability of improvement
		{
			if(sigma == 0){
				return 0;
			}
			const double x = mu - fmin;
		    return (x*(std::pow(x,2)-2*std::pow(sigma,2))*std::exp(-std::pow(x,2)/(2*std::pow(sigma,2)))) / (std::pow(sigma,5)*std::sqrt(2*mc::PI));
		}
		default:
		  throw std::runtime_error("mc::McCormick\t Second derivative of acquisition function called with an unknown type.\n");
    }
}


inline double regnormal
(const double x, const double a, const double b){

	if(a <= 0){
		  throw std::runtime_error("mc::McCormick\t Regnormal called with nonpositive value for a.\n");
	}
	if(b <= 0){
		  throw std::runtime_error("mc::McCormick\t Regnormal called with nonpositive value for b.\n");
	}

	return x / std::sqrt(a+ b*std::pow(x,2));
}


inline double der_regnormal
(const double x, const double a, const double b){

	if(a <= 0){
		  throw std::runtime_error("mc::McCormick\t Derivative of regnormal called with nonpositive value for a.\n");
	}
	if(b <= 0){
		  throw std::runtime_error("mc::McCormick\t Derivative of regnormal called with nonpositive value for b.\n");
	}

	return a / std::pow(a + b*std::pow(x,2),3./2.);
}


inline double centerline_deficit
(const double x, const double xLim, const double type){

	// Moved check for validity of parameters to ffunc.hpp - need to check only once when DAG is constructed
  switch((int)type) {
    case 1:
      if (x >= 1.) {
        return 1./sqr(x);
      } else {
        return 0.;
      }
    case 2:
      if (x >= 1.) {
        return 1./sqr(x);
      } else if (x>xLim) {
        return (x-xLim)/(1.-xLim);
      } else {
        return 0.;
      }
    case 3:
      if (x >= 1.) {
        return 1./sqr(x);
      } else if (x>xLim) {
        const double tmp = ( -1. + xLim*(5. + xLim*(-10. + xLim*(10. + xLim*(-5. + xLim)))));
        const double p0 = (std::pow(xLim,3)*(21. + xLim*(-21. + xLim*6.))) / tmp;
        const double p1 =  -(sqr(xLim)*(63. + xLim*(-28 + xLim*(-13. + xLim*8.)))) / tmp;
        const double p2 =  (xLim*(63. + xLim*(42. + xLim*(-60. + xLim*(12. + xLim*3))))) / tmp;
        const double p3 =  -(21. + xLim*(84. + xLim*(-42. + xLim*(-12. + xLim*9)))) / tmp;
        const double p4 =  (35. + xLim*(14. + xLim*(-28. + xLim*9.))) / tmp;
        const double p5 =  -(15. + xLim*(-12. + xLim*3.)) / tmp;
        /* broken numerically: 
          const double p0 = (3*(2*std::pow(xLim,5) - 7*std::pow(xLim,4) + 7*std::pow(xLim,3))) / (sqr(xLim - 1)*(std::pow(xLim,3) - 3*sqr(xLim) + 3*xLim - 1));
          const double p1 =  -(8*std::pow(xLim,5) - 13*std::pow(xLim,4) - 28*std::pow(xLim,3) + 63*sqr(xLim)) / (sqr(xLim - 1)*(std::pow(xLim,3) - 3*sqr(xLim) + 3*xLim - 1));
          const double p2 =  (3*(std::pow(xLim,5) + 4*std::pow(xLim,4) - 20*std::pow(xLim,3) + 14*sqr(xLim) + 21*xLim)) / (sqr(xLim-1.)*(std::pow(xLim,3) - 3*sqr(xLim) + 3*xLim - 1));
          const double p3 =  -(3*(3*std::pow(xLim,4) - 4*std::pow(xLim,3) - 14*sqr(xLim) + 28*xLim + 7)) / (sqr(xLim - 1.)*(std::pow(xLim,3) - 3*sqr(xLim) + 3*xLim - 1));
          const double p4 =  (9*std::pow(xLim,3) - 28*sqr(xLim) + 14*xLim + 35) / ((sqr(xLim) - 2*xLim + 1)*(std::pow(xLim,3) - 3*sqr(xLim) + 3*xLim - 1));
          const double p5 =  -(3*(sqr(xLim) - 4*xLim + 5)) / (std::pow(xLim,5) - 5*std::pow(xLim,4) + 10*std::pow(xLim,3) - 10*sqr(xLim) + 5*xLim - 1);
        */
        return p0 + x*(p1 + x*(p2 + x*(p3 + x*(p4 + x*p5))));
      } else {
        return 0.;
      }
    default:
      throw std::runtime_error("mc::McCormick\t centerline_deficit called with unkonw type.\n");
  }

}


inline double der_centerline_deficit
(const double x, const double xLim, const double type){

  switch((int)type) {
    case 1:
      if (x >= 1.) {
        return -2./std::pow(x,3);
      } else {
        return 0.;
      }
    case 2:
      if (x >= 1.) {
        return -2./std::pow(x,3);
      } else if (x>xLim) {
        return 1./(1.-xLim);
      } else {
        return 0.;
      }
    case 3:
      if (x >= 1.) {
        return -2./std::pow(x,3);
      } else if (x>xLim) {
        const double tmp = ( -1. + xLim*(5. + xLim*(-10. + xLim*(10. + xLim*(-5. + xLim)))));
        const double p0 = (std::pow(xLim,3)*(21. + xLim*(-21. + xLim*6.))) / tmp;
        const double p1 =  -(sqr(xLim)*(63. + xLim*(-28 + xLim*(-13. + xLim*8.)))) / tmp;
        const double p2 =  (xLim*(63. + xLim*(42. + xLim*(-60. + xLim*(12. + xLim*3))))) / tmp;
        const double p3 =  -(21. + xLim*(84. + xLim*(-42. + xLim*(-12. + xLim*9)))) / tmp;
        const double p4 =  (35. + xLim*(14. + xLim*(-28. + xLim*9.))) / tmp;
        const double p5 =  -(15. + xLim*(-12. + xLim*3.)) / tmp;
        return p1 + x*(2.*p2 + x*(3.*p3 + x*(4.*p4 + x*5.*p5)));
      } else {
        return 0.;
      }
    default:
      throw std::runtime_error("mc::McCormick\t der_centerline_deficit called with unkonw type.\n");
  }

}


inline double der2_centerline_deficit
(const double x, const double xLim, const double type){

  switch((int)type) {
    case 1:
    case 2:
      if (x >= 1.) {
        return 6./std::pow(x,4);
      } else {
        return 0.;
      }
    case 3:
      if (x >= 1.) {
        return 6./std::pow(x,4);
      } else if (x>xLim) {
        const double tmp = ( -1. + xLim*(5. + xLim*(-10. + xLim*(10. + xLim*(-5. + xLim)))));
        const double p0 = (std::pow(xLim,3)*(21. + xLim*(-21. + xLim*6.))) / tmp;
        const double p1 =  -(sqr(xLim)*(63. + xLim*(-28 + xLim*(-13. + xLim*8.)))) / tmp;
        const double p2 =  (xLim*(63. + xLim*(42. + xLim*(-60. + xLim*(12. + xLim*3))))) / tmp;
        const double p3 =  -(21. + xLim*(84. + xLim*(-42. + xLim*(-12. + xLim*9)))) / tmp;
        const double p4 =  (35. + xLim*(14. + xLim*(-28. + xLim*9.))) / tmp;
        const double p5 =  -(15. + xLim*(-12. + xLim*3.)) / tmp;
        return 2.*p2 + x*(6.*p3 + x*(12.*p4 + x*20.*p5));
      } else {
        return 0.;
      }
    default:
      throw std::runtime_error("mc::McCormick\t der2_centerline_deficit called with unkonw type.\n");
  }

}


inline double wake_profile
(const double x, const double type){
  
  switch((int)type){
    case 1: // Jensen top-hat profile
      return (std::fabs(x)<=1) ? 1. : 0.;
    case 2: // Park Gauss profile
      return std::exp(-sqr(x));
    default:
      throw std::runtime_error("mc::McCormick\t Wake_profile called with an unknown type.");
  }
}


inline double der_wake_profile
(const double x, const double type){
  
  switch((int)type){
    case 1: // Jensen top-hat - CAVE: function is not differentiable
      return 0.;
    case 2: // Park Gauss profile
    {
      return -2.*x*std::exp(-sqr(x));
    }
    default:
      throw std::runtime_error("mc::McCormick\t Wake_profile called with an unknown type.");
  }

}


inline double der2_wake_profile
(const double x, const double type){
  
  switch((int)type){
    case 1: // Jensen top-hat - CAVE: function is not differentiable
      return 0.;
    case 2: // Park Gauss profile
    {
      return (4.*sqr(x)-2.)*std::exp(-sqr(x));
    }
    default:
      throw std::runtime_error("mc::McCormick\t Wake_profile called with an unknown type.");
  }

}



inline double wake_deficit
(const double x, const double r, const double a, const double alpha, const double rr, const double type1, const double type2){
  
  
  if (x>-rr) {
    const double r0 = rr*std::sqrt((1.-a)/(1.-2.*a));
    const double Rwake = r0 + alpha*x;
    return 2.*a*centerline_deficit(Rwake/r0,1.-alpha*rr/r0,type1)*wake_profile(r/Rwake,type2);
  } else {
    return 0.;
  }

}


inline double power_curve
(const double x, const double type){
  
  switch((int)type){
    case 1: // classical cubic power curve
      if (x<=0.) {
        return 0.;
      } else if (x>=1.) {
        return 1.;
      } else {
        return std::pow(x,3);
      }      
    case 2: // generalized power curve based on Enercon E-70 E4 according to Hau
      if (x<=0.) {
        return 0.;
      } else if (x>=1.) {
        return 1.;
      } else if (x<=0.643650793650794) {
        return sqr(x)*(1.378300020831773+x*0.158205207484756);
      } else {
        return 1.+std::pow(x-1.,3)*(18.670944034722282 + (x-1.)*28.407497538574532);
      }  
    default:
      throw std::runtime_error("mc::McCormick\t power_curve called with an unknown type.");
  }

}


inline double der_power_curve
(const double x, const double type){
  
  switch((int)type){
    case 1: // classical cubic power curve
      if (x<=0.) {
        return 0.;
      } else if (x>=1.) {
        return 0.;
      } else {
        return 3.*sqr(x);
      }      
    case 2: // generalized power curve based on Enercon E-70 E4 according to Hau
      if (x<=0.) {
        return 0.;
      } else if (x>=1.) {
        return 0.;
      } else if (x<=0.643650793650794) {
        return x*(2.*1.378300020831773+3.*x*0.158205207484756);
      } else {
        return std::pow(x-1.,2)*(3.*18.670944034722282 + 4.*(x-1.)*28.407497538574532);
      }  
    default:
      throw std::runtime_error("mc::McCormick\t power_curve called with an unknown type.");
  }

}


inline double der2_power_curve
(const double x, const double type){
  
  switch((int)type){
    case 1: // classical cubic power curve
      if (x<=0.) {
        return 0.;
      } else if (x>=1.) {
        return 0.;
      } else {
        return 6.*x;
      }      
    case 2: // generalized power curve based on Enercon E-70 E4 according to Hau
      if (x<=0.) {
        return 0.;
      } else if (x>=1.) {
        return 0.;
      } else if (x<=0.643650793650794) {
        return (2.*1.378300020831773+6.*x*0.158205207484756);
      } else {
        return (x-1.)*(6.*18.670944034722282 + 12.*(x-1.)*28.407497538574532);
      }  
    default:
      throw std::runtime_error("mc::McCormick\t power_curve called with an unknown type.");
  }

}



} // end namespace mc


#endif
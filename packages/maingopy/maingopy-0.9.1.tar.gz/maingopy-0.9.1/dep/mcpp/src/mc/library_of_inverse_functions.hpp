
#ifndef MC__LIBRARY_OF_INVERSE_FUNCTIONS_HPP
#define MC__LIBRARY_OF_INVERSE_FUNCTIONS_HPP


#include "library_of_functions.hpp"
#include "numerics.hpp"

namespace mc{

inline double
_compute_root
( const double x0, const double xL, const double xU, numerics::puniv f,
  numerics::puniv df, const double*rusr, const int*iusr=0 )
{
    double res;
	try{
		res = numerics::newton(x0, xL, xU, f, df, rusr, iusr);
	}
	catch(std::runtime_error& e)
	{
		throw (e);
	}
	catch(...) {
		res = numerics::goldsect( xL, xU, f, rusr, iusr );
	}
	return res;
}

inline double
xlog_func
( const double x, const double*rusr, const int*iusr )
{
  //x*log(x) - *rusr = 0
  return x*std::log(x) - *rusr;
}


inline double
xlog_dfunc
( const double x, const double*rusr, const int*iusr )
{
  //log(x)+1
  return std::log(x) +1;
}


/**
* @brief Function for computing the inverse interval of xlog for contraint propagation (reval in DAG).
*        The function consists of two branches. The left branch (<1/exp(1)) is monotonically decreasing while the right branch (>1/exp(1)) is monotonically increasing.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of xlog
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of xlog
*/
inline void
_compute_inverse_interval_xlog
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	if( fwdLowerBound  >= std::exp(-1.0) ){
		// monotonically increasing part
		double rusrL = bwdLowerBound;
		xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xlog_func, xlog_dfunc, &rusrL);
		double rusrU = bwdUpperBound;
		xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, xlog_func, xlog_dfunc, &rusrU);
	}
	else if(fwdUpperBound <= std::exp(-1.0)){
		// monotonically decreasing part
		double rusrU = bwdUpperBound;
		xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xlog_func, xlog_dfunc, &rusrU);
		double rusrL = bwdLowerBound;
		xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, xlog_func, xlog_dfunc, &rusrL);
	}
	else if(bwdLowerBound > mc::xlog(fwdLowerBound) ){
		// we are fully on the right branch but before we got here, both branches were possible
		// we need this case to start newton for xL from the correct point
		double rusrL = bwdLowerBound;
		xL = _compute_root(fwdUpperBound, std::exp(-1.0), fwdUpperBound, xlog_func, xlog_dfunc, &rusrL);
		double rusrU = bwdUpperBound;
		xU = _compute_root(fwdUpperBound, std::exp(-1.0), fwdUpperBound, xlog_func, xlog_dfunc, &rusrU);
	}
	else if(bwdLowerBound > mc::xlog(fwdUpperBound) ){
		// we are fully on the left branch but before we got here, both branches were possible
		// we need this case to start newton for xU from the correct point
		double rusrL = bwdUpperBound;
		xL = _compute_root(fwdLowerBound, fwdLowerBound, std::exp(-1.0), xlog_func, xlog_dfunc, &rusrL);
		double rusrU = bwdLowerBound;
		xU = _compute_root(fwdLowerBound, fwdLowerBound, std::exp(-1.0), xlog_func, xlog_dfunc, &rusrU);
	}
    else{
		double rusr = bwdUpperBound;
		// now we know that we have two branches
		// the lower or upper bound can only be improved if we cut off something
		if(bwdUpperBound < mc::xlog(fwdLowerBound) ){
			xL =_compute_root(fwdLowerBound, fwdLowerBound, std::exp(-1.0), xlog_func, xlog_dfunc, &rusr);
		}
		if(bwdUpperBound < mc::xlog(fwdUpperBound) ){
			xU = _compute_root(fwdUpperBound,  std::exp(-1.0), fwdUpperBound, xlog_func, xlog_dfunc, &rusr);
		}
	}
}

/**
* @brief Function for computing the inverse interval of fabsx_times_x for contraint propagation (reval in DAG).
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of fabsx_times_x
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of fabsx_times_x
*/
inline void
_compute_inverse_interval_fabsx_times_x
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU)
{
	xU = bwdUpperBound>=0 ? std::sqrt(bwdUpperBound) : -std::sqrt(-bwdUpperBound);
	xL = bwdLowerBound>=0 ? std::sqrt(bwdLowerBound) : -std::sqrt(-bwdLowerBound);
}


// it is only w.r.t. to x
inline double
xlog_sum_func
( const double x, const double*rusr, const int*iusr )
{
  // rusr holds a1,b1,y1L/U,b2,y2L/U,..., value
  //   x*log(a1*x+b1*y1L+b2*y2L+...) - rusr[&iusr]
  unsigned int size = *iusr;
  double sum = rusr[0]*x;
  for(unsigned int i=1;i< size - 1;i+=2){
	  sum += rusr[i]*rusr[i+1];
  }
  return x*std::log(sum)-rusr[size-1];
}


inline double
xlog_sum_dfunc
( const double x, const double*rusr, const int*iusr )
{
  // rusr holds a1,b1,y1L/U,b2,y2L/U,..., value
  //    log(a1*x + b1*y1L+...) + a1*x/(a1*x + b1*y1L)
  // or log(a1*x + b1*y1U+...) + a1*x/(a1*x + b1*y1U)
  unsigned int size = *iusr;
  double sum = rusr[0]*x;
  for(unsigned int i=1;i< size - 1;i+=2){
	  sum += rusr[i]*rusr[i+1];
  }
  return std::log(sum) + rusr[0]*x/(sum);
}

// Second derivative w.r.t. to x needed for the computation of exact interval extensions
inline double
xlog_sum_ddfunc
( const double x, const double*rusr, const int*iusr )
{
  // rusr holds a1,b1,y1L/U,b2,y2L/U,..., value
  // 2*a1/(a1*x+b1*y1L+...) - a1^2*x/(a1*x+b1*y1L+...)^2 = a1*(a1*x+2*b1*y1L+2*b2*y2L+...)/(a1*x+2*b1*y1L+2*b2*y2L+...)^2
  // rusr holds a1,xL,b1,y1L,...,bn,ynL
  unsigned int size = *iusr;
  double sum1 = rusr[0]*x;
  double sum2 = rusr[0]*x;
  for(unsigned int i=1;i< size - 1;i+=2){
	  sum1 += 2*rusr[i]*rusr[i+1];
	  sum2 += rusr[i]*rusr[i+1];
  }
  return rusr[0]*sum1/std::pow(sum2,2);
}

/**
* @brief Function for computing the inverse interval of xlog_sum for x variable only for contraint propagation (reval in DAG).
*        For the backward upper bound we have to take a look at xlog_sum at yL while for the backward lower bound we look at xlog_sum at yU.
*        Both cases consist of two branches. The left branch (< root) is monotonically decreasing while the right branch (>root) is monotonically increasing.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of xlog_sum
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of xlog_sum
* @param[in] rusrL holds
* @param[in] upperIntervalBounds are the upper bounds of the forward propagation
*/
inline void
_compute_inverse_interval_xlog_sum
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU,
 std::vector<double> &rusrL, std::vector<double> &rusrU )
{

	// Using only backward upper bound first
	double xL1 = fwdLowerBound;
	double xU1 = fwdUpperBound;
	int size = rusrL.size();
	double rootL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xlog_sum_dfunc, xlog_sum_ddfunc, rusrL.data(), &size);
	if( fwdLowerBound  >= rootL ){
		// monotonically increasing part
		rusrL[size-1] = bwdUpperBound;
		xU1 = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, xlog_sum_func, xlog_sum_dfunc, rusrL.data(), &size);
	}
	else if(fwdUpperBound <= rootL){
		// monotonically decreasing part
		rusrL[size-1] = bwdUpperBound;
		xL1 = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xlog_sum_func, xlog_sum_dfunc, rusrL.data(), &size);
	}
	else{
		// now we know that we have two branches
		// the lower or upper bound can only be improved if we cut off something
		if(bwdUpperBound < xlog_sum_func(fwdLowerBound,rusrL.data(),&size) ){
			xL1 =_compute_root(fwdLowerBound, fwdLowerBound, rootL, xlog_sum_func, xlog_sum_dfunc, rusrL.data(), &size);
		}
		if(bwdUpperBound < xlog_sum_func(fwdUpperBound,rusrL.data(),&size) ){
			xU1 = _compute_root(fwdLowerBound,  rootL, fwdUpperBound, xlog_sum_func, xlog_sum_dfunc, rusrL.data(), &size);
		}
	}
	// Now using only backward lower bound
	double xL2 = fwdLowerBound;
	double xU2 = fwdUpperBound;
	double rootU = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xlog_sum_dfunc, xlog_sum_ddfunc, rusrU.data(), &size);
	if( fwdLowerBound  >= rootU ){
		// monotonically increasing part
		rusrU[size-1] = bwdLowerBound;
		xL2 = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xlog_sum_func, xlog_sum_dfunc, rusrU.data(), &size);
	}
	else if(fwdUpperBound <= rootU){
		// monotonically decreasing part
		rusrU[size-1] = bwdLowerBound;
		xU2 = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xlog_sum_func, xlog_sum_dfunc, rusrU.data(), &size);
	}
	else if(bwdLowerBound > xlog_sum_func(fwdLowerBound,rusrU.data(),&size) ){
		// we are fully on the right branch but before we got here, both branches were possible
		// we need this case to start newton for xL from the correct point
		rusrU[size-1] = bwdLowerBound;
		xL2 = _compute_root(fwdUpperBound, rootU, fwdUpperBound, xlog_sum_func, xlog_sum_dfunc, rusrU.data(), &size);
	}
	else if(bwdLowerBound > xlog_sum_func(fwdUpperBound,rusrU.data(),&size) ){
		// we are fully on the left branch but before we got here, both branches were possible
		// we need this case to start newton for xU from the correct point
		rusrU[size-1] = bwdLowerBound;
		xU2 = _compute_root(fwdLowerBound, fwdLowerBound, rootU, xlog_sum_func, xlog_sum_dfunc, rusrU.data(), &size);
	}
	xL = std::max(xL1,xL2);
	xU = std::min(xU1,xU2);
}


inline double
xexpax_func
( const double x, const double*rusr, const int*iusr )
{
  //x*exp(a*x) - *rusr = 0
  return x*std::exp(rusr[0]*x) - rusr[1];
}


inline double
xexpax_dfunc
( const double x, const double*rusr, const int*iusr )
{
  //exp(a*x) + a*x*exp(a*x)
  return std::exp(rusr[0]*x) + rusr[0]*x*std::exp(rusr[0]*x);
}


/**
* @brief Function for computing the inverse interval of xexpax for contraint propagation (reval in DAG).
*        The function consists of two branches. Each branch is monotonic. The monotonicity depends on the sign of a. The root of the function is at -1/a. It is a min if a>0 and a max otherwise.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of xexpax
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of xexpax
*/
inline void
_compute_inverse_interval_xexpax
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, const double a)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	if(a>=0){
		if( fwdLowerBound  >= -1./a ){
			// monotonically increasing part
			double rusrL[2] = {a,bwdLowerBound};
			xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrL);
			double rusrU[2] = {a,bwdUpperBound};
			xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrU);
		}
		else if(fwdUpperBound <= -1./a){
			// monotonically decreasing part
			double rusrU[2] = {a,bwdUpperBound};
			xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrU);
			double rusrL[2] = {a,bwdLowerBound};
			xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrL);
		}
		else if(bwdLowerBound > mc::xexpax(fwdLowerBound,a) ){
			// we are fully on the right branch but before we got here, both branches were possible
			// we need this case to start newton for xL from the correct point
			double rusrL[2] = {a,bwdLowerBound};
			xL = _compute_root(fwdUpperBound, -1./a, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrL);
			double rusrU[2] = {a,bwdUpperBound};
			xU = _compute_root(fwdUpperBound, -1./a, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrU);
		}
		else if(bwdLowerBound > mc::xexpax(fwdUpperBound,a) ){
			// we are fully on the left branch but before we got here, both branches were possible
			// we need this case to start newton for xU from the correct point
			double rusrL[2] = {a,bwdUpperBound};
			xL = _compute_root(fwdLowerBound, fwdLowerBound, -1./a, xexpax_func, xexpax_dfunc, rusrL);
			double rusrU[2] = {a,bwdLowerBound};
			xU = _compute_root(fwdLowerBound, fwdLowerBound, -1./a, xexpax_func, xexpax_dfunc, rusrU);
		}
		else{
			double rusr[2] = {a,bwdUpperBound};
			// now we know that we have two branches
			// the lower or upper bound can only be improved if we cut off something
			if(bwdUpperBound < mc::xexpax(fwdLowerBound,a) ){
				// we can improve the lower bound
				xL = _compute_root(fwdLowerBound, fwdLowerBound, -1./a, xexpax_func, xexpax_dfunc, rusr);
			}
			if(bwdUpperBound < mc::xexpax(fwdUpperBound,a) ){
				// we can improve the upper bound
				xU = _compute_root(fwdUpperBound,  -1./a, fwdUpperBound, xexpax_func, xexpax_dfunc, rusr);
			}
		}
	}
	else{
		if( fwdUpperBound  <= -1./a ){
			// monotonically increasing part
			double rusrL[2] = {a,bwdLowerBound};
			xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrL);
			double rusrU[2] = {a,bwdUpperBound};
			xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrU);
		}
		else if(fwdLowerBound >= -1./a){
			// monotonically decreasing part
			double rusrU[2] = {a,bwdUpperBound};
			xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrU);
			double rusrL[2] = {a,bwdLowerBound};
			xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrL);
		}
		else if(bwdUpperBound < mc::xexpax(fwdLowerBound,a) ){
			// we are fully on the right branch but before we got here, both branches were possible
			// we need this case to start newton for xL from the correct point
			double rusrL[2] = {a,bwdUpperBound};
			xL = _compute_root(fwdUpperBound, -1./a, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrL);
			double rusrU[2] = { a,bwdLowerBound};
			xU = _compute_root(fwdUpperBound, -1./a, fwdUpperBound, xexpax_func, xexpax_dfunc, rusrU);
		}
		else if(bwdUpperBound < mc::xexpax(fwdUpperBound,a) ){
			// we are fully on the left branch but before we got here, both branches were possible
			// we need this case to start newton for xU from the correct point
			double rusrL[2] = {a,bwdLowerBound};
			xL = _compute_root(fwdLowerBound, fwdLowerBound, -1./a, xexpax_func, xexpax_dfunc, rusrL);
			double rusrU[2] = {a,bwdUpperBound};
			xU = _compute_root(fwdLowerBound, fwdLowerBound, -1./a, xexpax_func, xexpax_dfunc, rusrU);
		}
		else{
			double rusr[2] = {a,bwdUpperBound};
			// now we know that we have two branches
			// the lower or upper bound can only be improved if we cut off something
			if(bwdLowerBound > mc::xexpax(fwdLowerBound,a) ){
				// we can improve the lower bound
				xL = _compute_root(fwdLowerBound, fwdLowerBound, -1./a, xexpax_func, xexpax_dfunc, rusr);
			}
			if(bwdLowerBound > mc::xexpax(fwdUpperBound,a) ){
				// we can improve the upper bound
				xU = _compute_root(fwdUpperBound,  -1./a, fwdUpperBound, xexpax_func, xexpax_dfunc, rusr);
			}
		}
	}
}


/**
* @brief Function for computing the inverse interval of centerline_deficit for contraint propagation (reval in DAG).
*        The function has a single maximum at x=0
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of centerline_deficit
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of centerline_deficit
*/
inline void
_compute_inverse_interval_centerline_deficit
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, const double xLim, const double type)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	
	if ( fwdLowerBound >= 1. ) {	// monotonically decreasing part: centerline_deficit(x) = 1/x^2

		xL = mc::isequal(bwdUpperBound,0.) ? fwdLowerBound : 1./std::sqrt(bwdUpperBound);
		xU = mc::isequal(bwdLowerBound,0.) ? fwdUpperBound : 1./std::sqrt(bwdLowerBound);

	} else if ( fwdUpperBound <= 1. ) {

		// Not changing anything

	} else {

		// First check if (potentially) improved upper bound "cuts away" either the positive or negative part
  		const double fAtFwdLowerBound = mc::centerline_deficit(fwdLowerBound,xLim,type);
		const double fAtFwdUpperBound = mc::centerline_deficit(fwdUpperBound,xLim,type);

		if (bwdUpperBound<fAtFwdLowerBound) {
			if (bwdUpperBound<=1.) {	// completely cutting away x<1 part --> now monotonically decreasing
				xL = mc::isequal(bwdUpperBound,0.) ? fwdLowerBound : 1./std::sqrt(bwdUpperBound);
				xU = mc::isequal(bwdLowerBound,0.) ? fwdUpperBound : 1./std::sqrt(bwdLowerBound);
			} else {	// not cutting away the x<0 part entirely; however, it cannot be much left of it anyways, so just leaving it
				xU = mc::isequal(bwdLowerBound,0.) ? fwdUpperBound : 1./std::sqrt(bwdLowerBound);
			}
		} else if (bwdUpperBound<fAtFwdUpperBound) {	// completely cutting away x>1 part
			xU = 1.;
		} else {	// not cutting away either half, only using backward lower bound
			if ((bwdLowerBound>fAtFwdUpperBound)&&(!mc::isequal(bwdLowerBound,0.))) {
				xU = 1./std::sqrt(bwdLowerBound);
			}
		}

	}
	
}


/**
* @brief Function for computing the inverse interval of wake_profile for contraint propagation (reval in DAG).
*        The function has a single maximum at x=0
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of wake_profile
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of wake_profile
*/
inline void
_compute_inverse_interval_wake_profile
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, const double type)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	
	switch((int)type) {
		case 1:
		{
			if ( fwdLowerBound >= -1. ) {	// monotonically decreasing part
				if (!mc::isequal(bwdLowerBound,0.)) {
					xU = std::min(fwdUpperBound,1.);
				}
				if (!mc::isequal(bwdUpperBound,1.)) {
					xL = std::max(fwdLowerBound,1.);
				} 
			} else if ( fwdUpperBound <= 1. ) {	// monotonically decreasing part 
				if (!mc::isequal(bwdLowerBound,0.)) {
					xL = std::max(fwdLowerBound,-1.);
				}
				if (!mc::isequal(bwdUpperBound,1.)) {
					xU = std::min(fwdUpperBound,-1.);
				} 
			} else {	// maximum at 0 - can only use the backward lower bound
				if (!mc::isequal(bwdLowerBound,0.)) {
					xL = -1.;
					xU = 1.;
				}
				
			}
			break;
		}
		case 2:
		{	
			if (fwdLowerBound >= 0.) { // monotonically decreasing part
				if (!mc::isequal(bwdLowerBound,0.)) {
					xU = std::sqrt(-std::log(bwdLowerBound));
				}
				if (!mc::isequal(bwdUpperBound,0.)) {
					xL = std::sqrt(-std::log(bwdUpperBound));
				}
			} else if (fwdUpperBound <= 0.) { // monotonically increasing part
				if (!mc::isequal(bwdLowerBound,0.)) {
					xL = -std::sqrt(-std::log(bwdLowerBound));
				}
				if (!mc::isequal(bwdUpperBound,0.)) {
					xU = -std::sqrt(-std::log(bwdUpperBound));
				}
			} else {	// maximum in interval: f(0)=1
				// First check if (potentially) improved upper bound "cuts away" either the positive or negative part
				const double fAtFwdLowerBound = std::exp(-sqr(fwdLowerBound));
				const double fAtFwdUpperBound = std::exp(-sqr(fwdUpperBound));
				if (bwdUpperBound<fAtFwdLowerBound) {	// completely cutting away x<0 part --> now monotonically decreasing
					if (!mc::isequal(bwdLowerBound,0.)) {
						xU = std::sqrt(-std::log(bwdLowerBound));
					}
					if (!mc::isequal(bwdUpperBound,0.)) {
						xL = std::sqrt(-std::log(bwdUpperBound));
					}
				} else if (bwdUpperBound<fAtFwdUpperBound) {	// completely cutting away x>0 part --> now monotonically increasing
					if (!mc::isequal(bwdLowerBound,0.)) {
						xL = -std::sqrt(-std::log(bwdLowerBound));
					}
					if (!mc::isequal(bwdUpperBound,0.)) {
						xU = -std::sqrt(-std::log(bwdUpperBound));
					}
				} else {	// not cutting away either half, only using backward lower bound
					if ((bwdLowerBound>fAtFwdLowerBound)&&(!mc::isequal(bwdLowerBound,0.))) {
						xL = -std::sqrt(-std::log(bwdLowerBound));
					}
					if ((bwdLowerBound>fAtFwdUpperBound)&&(!mc::isequal(bwdLowerBound,0.))) {
						xU = std::sqrt(-std::log(bwdLowerBound));
					}
				}
			}

			break;
		}
		default:
			break;
	}
	
	
}


/**
* @brief Function for computing the inverse interval of wake_deficit for contraint propagation (reval in DAG).
*
* @param[in] fwdLowerBound1 is the lower boundon x of the forward propagation
* @param[in] fwdUpperBound1 is the upper boundon x of the forward propagation
* @param[in] fwdLowerBound2 is the lower boundon r of the forward propagation
* @param[in] fwdUpperBound2 is the upper boundon r of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound on x obtained by the inverse interval computation of wake_deficit
* @param[in,out] xU is the upper bound on x obtained by the inverse interval computation of wake_deficit
* @param[in,out] rL is the lower bound on r obtained by the inverse interval computation of wake_deficit
* @param[in,out] rU is the upper bound on r obtained by the inverse interval computation of wake_deficit
*/
inline void
_compute_inverse_interval_wake_deficit
(const double fwdLowerBound1, const double fwdUpperBound1, const double fwdLowerBound2, const double fwdUpperBound2, const double bwdLowerBound, const double bwdUpperBound, 
	double& xL, double& xU, double& rL, double& rU, 
	const double a, const double alpha, const double rr, const double type1, const double type2)
{
	xL = fwdLowerBound1;
	xU = fwdUpperBound1;
	rL = fwdLowerBound2;
	rU = fwdUpperBound2;	
}


/**
* @brief Function for computing the inverse interval of power_curve for contraint propagation (reval in DAG).
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of power_curve
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of power_curve
*/
inline void
_compute_inverse_interval_power_curve
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, const double type)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	
	switch((int)type) {
		case 1:
			if (!mc::isequal(bwdLowerBound,0.)) {
				xL = std::pow(bwdLowerBound,1./3.);
			}
			if (!mc::isequal(bwdUpperBound,1.)) {
				xU = std::pow(bwdUpperBound,1./3.);
			} 
			break;
		case 2:
			break;
		default:
			break;
	}
	
	
}


// Note that lmtd is symmetrical
inline double
lmtd_func
( const double x, const double*rusr, const int*iusr )
{
  //lmtd(x,y)-*rusr = 0
  return mc::lmtd(x,rusr[0]) - rusr[1];
}

inline double
lmtdx_dfunc
( const double x, const double*rusr, const int*iusr )
{
  //derivative of lmtd
  if(mc::isequal(x,rusr[0])){
	  return 0.5;
  }
  return 1/(std::log(x)-std::log(rusr[0])) - (x-rusr[0])/(x*std::pow(std::log(x)-std::log(rusr[0]),2));
}

inline double
lmtdy_dfunc
( const double y, const double*rusr, const int*iusr )
{
  //derivative of lmtd
  if(mc::isequal(y,rusr[0])){
	  return 0.5;
  }
  return -1/(std::log(rusr[0])-std::log(y)) + (rusr[0]-y)/(y*std::pow(std::log(rusr[0])-std::log(y),2));
}

/**
* @brief Function for computing the inverse interval of lmtd for contraint propagation (reval in DAG).
*        We make use of monotonicity of the lmtd function. We can check corners and deduce whether an improvement in intervals is possible or not.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the x lower bound obtained by the inverse interval computation of lmtd
* @param[in,out] xU is the x upper bound obtained by the inverse interval computation of lmtd
* @param[in,out] yL is the y lower bound obtained by the inverse interval computation of lmtd
* @param[in,out] yU is the y upper bound obtained by the inverse interval computation of lmtd
*/
inline void
_compute_inverse_interval_lmtd
(const double xFwdLowerBound, const double xFwdUpperBound, const double yFwdLowerBound, const double yFwdUpperBound,
 const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double& yL, double& yU)
{
  xL = xFwdLowerBound;
  xU = xFwdUpperBound;
  yL = yFwdLowerBound;
  yU = yFwdUpperBound;
  // We can improve xU only if the correct corner is above the new upper bound
  if(mc::lmtd(xFwdUpperBound,yFwdLowerBound) > bwdUpperBound){
	  const double rusr[2] = {yFwdLowerBound,bwdUpperBound};
	  xU = _compute_root(xFwdUpperBound, xFwdLowerBound, xFwdUpperBound, lmtd_func, lmtdx_dfunc, rusr);
  }
  // We can improve xL only if the correct corner is above the new lower bound
  if(mc::lmtd(xFwdLowerBound,yFwdUpperBound) < bwdLowerBound){
	  const double rusr[2] = {yFwdUpperBound,bwdLowerBound};
	  xL = _compute_root(xFwdLowerBound, xFwdLowerBound, xFwdUpperBound, lmtd_func, lmtdx_dfunc, rusr);
  }
  // Analogously we can improve yL and yU
  // We can improve yU only if the correct corner is above the new upper bound
  if(mc::lmtd(xFwdLowerBound,yFwdUpperBound) > bwdUpperBound){
	  const double rusr[2] = {xFwdLowerBound,bwdUpperBound};
	  yU = _compute_root(yFwdUpperBound, yFwdLowerBound, yFwdUpperBound, lmtd_func, lmtdy_dfunc, rusr);
  }
  // We can improve yL only if the correct corner is above the new lower bound
  if(mc::lmtd(xFwdUpperBound,yFwdLowerBound) < bwdLowerBound){
	  const double rusr[2] = {xFwdUpperBound,bwdLowerBound};
	  yL = _compute_root(yFwdLowerBound, yFwdLowerBound, yFwdUpperBound, lmtd_func, lmtdy_dfunc, rusr);
  }
}

// Note that rlmtd is symmetrical
inline double
rlmtd_func
( const double x, const double*rusr, const int*iusr )
{
  //rlmtd(x,y)-*rusr = 0
  return mc::rlmtd(x,rusr[0]) - rusr[1];
}

inline double
rlmtdx_dfunc
( const double x, const double*rusr, const int*iusr )
{
  //derivative w.r.t. x of rlmtd
  if(mc::isequal(x,rusr[0])){
	  return -1/(2*std::pow(x,2));
  }
  return 1/(x*(x-rusr[0])) - (std::log(x)-std::log(rusr[0]))/std::pow(x-rusr[0],2);
}

inline double
rlmtdy_dfunc
( const double y, const double*rusr, const int*iusr )
{
  //derivative w.r.t. y of rlmtd
  if(mc::isequal(y,rusr[0])){
	  return -1/(2*std::pow(y,2));
  }
  return -1/(y*(rusr[0]-y)) + (std::log(rusr[0])-std::log(y))/std::pow(rusr[0]-y,2);
}

/**
* @brief Function for computing the inverse interval of rlmtd for contraint propagation (reval in DAG).
*        We make use of monotonicity of the rlmtd function. We can check corners and deduce whether an improvement in intervals is possible or not.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the x lower bound obtained by the inverse interval computation of rlmtd
* @param[in,out] xU is the x upper bound obtained by the inverse interval computation of rlmtd
* @param[in,out] yL is the y lower bound obtained by the inverse interval computation of rlmtd
* @param[in,out] yU is the y upper bound obtained by the inverse interval computation of rlmtd
*/
inline void
_compute_inverse_interval_rlmtd
(const double xFwdLowerBound, const double xFwdUpperBound, const double yFwdLowerBound, const double yFwdUpperBound,
 const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double& yL, double& yU)
{
  xL = xFwdLowerBound;
  xU = xFwdUpperBound;
  yL = yFwdLowerBound;
  yU = yFwdUpperBound;
  // We can improve xL only if the correct corner is above the new upper bound
  if(mc::rlmtd(xFwdLowerBound,yFwdUpperBound) > bwdUpperBound){
	  const double rusr[2] = {yFwdUpperBound,bwdUpperBound};
	  xL = _compute_root(xFwdLowerBound, xFwdLowerBound, xFwdUpperBound, rlmtd_func, rlmtdx_dfunc, rusr);
  }
  // We can improve xU only if the correct corner is above the new lower bound
  if(mc::rlmtd(xFwdUpperBound,yFwdLowerBound) < bwdLowerBound){
	  const double rusr[2] = {yFwdLowerBound,bwdLowerBound};
	  xU = _compute_root(xFwdUpperBound, xFwdLowerBound, xFwdUpperBound, rlmtd_func, rlmtdx_dfunc, rusr);
  }
  // Analogously we can improve yL and yU
  // We can improve yL only if the correct corner is above the new upper bound
  if(mc::rlmtd(xFwdUpperBound,yFwdLowerBound) > bwdUpperBound){
	  const double rusr[2] = {xFwdUpperBound,bwdUpperBound};
	  yL = _compute_root(yFwdLowerBound, yFwdLowerBound, yFwdUpperBound, rlmtd_func, rlmtdy_dfunc, rusr);
  }
  // We can improve yU only if the correct corner is above the new lower bound
  if(mc::rlmtd(xFwdLowerBound,yFwdUpperBound) < bwdLowerBound){
	  const double rusr[2] = {xFwdLowerBound,bwdLowerBound};
	  yU = _compute_root(yFwdUpperBound, yFwdLowerBound, yFwdUpperBound, rlmtd_func, rlmtdy_dfunc, rusr);
  }
}


inline double
erf_func
( const double x, const double*rusr, const int*iusr )
{
  //x*log(x) - *rusr = 0
  return std::erf(x) - *rusr;
}


inline double
erf_dfunc
( const double x, const double*rusr, const int*iusr )
{
  //log(x)+1 - *rusr = 0
  return 2/std::sqrt(mc::PI)*std::exp(std::pow(-x,2));
}


/**
* @brief Function for computing the inverse interval of erf for contraint propagation (reval in DAG).
*        erf is monotonically increasing.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of erf
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of erf
*/
inline void
_compute_inverse_interval_erf
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	// We can only tighten if we are in the (-1,1) range, meaning that -1 and 1 are not allowed to be in the range as sadly erf(100) already returns 1.
	// This if-clause is needed because when filib++ throws an exception, it terminates the whole program and we obviously don't want that...
	if (bwdLowerBound > -1) {
		double rusrL = bwdLowerBound;
		xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, erf_func, erf_dfunc, &rusrL);
	}
	if (bwdUpperBound < 1) {
		double rusrU = bwdUpperBound;
		xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, erf_func, erf_dfunc, &rusrU);
	}
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
idealgas_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::ideal_gas_enthalpy(x,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6], rusr[7], rusr[8]) - rusr[9];
}


inline double
idealgas_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_ideal_gas_enthalpy(x,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6], rusr[7], rusr[8]);
}


/**
* @brief Function for computing the inverse interval of ideal gas enthalpy for contraint propagation (reval in DAG).
*        The ideal gas enthalpy functions are assumed to be convex and nondecreasing.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of ideal gas enthalpy
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of ideal gas enthalpy
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_ideal_gas_enthalpy
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double* params)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	params[9] = bwdLowerBound;
	xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, idealgas_func, idealgas_dfunc,params);
	params[9] = bwdUpperBound;
	xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, idealgas_func, idealgas_dfunc, params);
}


inline double
vaporpressure_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::vapor_pressure(x,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6], rusr[7], rusr[8], rusr[9], rusr[10]) - rusr[11];
}


inline double
vaporpressure_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_vapor_pressure(x,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6], rusr[7], rusr[8], rusr[9], rusr[10]);
}


/**
* @brief Function for computing the inverse interval of vapor pressure for contraint propagation (reval in DAG).
*        The vapor pressure functions are assumed to be convex and nondecreasing.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of vapor pressure
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of vapor pressure
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_vapor_pressure
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double* params)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	params[11] = bwdLowerBound;
	xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, vaporpressure_func, vaporpressure_dfunc,params);
	params[11] = bwdUpperBound;
	xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, vaporpressure_func, vaporpressure_dfunc, params);
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
enthalpyvap_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::enthalpy_of_vaporization(x,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6]) - rusr[7];
}


inline double
enthalpyvap_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_enthalpy_of_vaporization(x,rusr[0], rusr[1], rusr[2], rusr[3], rusr[4], rusr[5], rusr[6]);
}


/**
* @brief Function for computing the inverse interval of enthalpy of vaporization for contraint propagation (reval in DAG).
*        The enthalpy of vaporization functions are assumed to be concave and nonincreasing.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of enthalpy of vaporization
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of enthalpy of vaporization
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_enthalpy_of_vaporization
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double* params)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	params[7] = bwdLowerBound;
	xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, enthalpyvap_func, enthalpyvap_dfunc,params);
	params[7] = bwdUpperBound;
	xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, enthalpyvap_func, enthalpyvap_dfunc, params);
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
costfunction_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::cost_function(x,rusr[0], rusr[1], rusr[2], rusr[3]) - rusr[4];
}


inline double
costfunction_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_cost_function(x,rusr[0], rusr[1], rusr[2], rusr[3]);
}


/**
* @brief Function for computing the inverse interval of cost functions for contraint propagation (reval in DAG).
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of cost function
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of cost function
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_cost_function
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double* params)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	double newtonWithLB = xL;
	double newtonWithUB = xU;
	params[4] = bwdLowerBound;
	newtonWithLB = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, costfunction_func, costfunction_dfunc, params);
	params[4] = bwdUpperBound;
	newtonWithUB = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, costfunction_func, costfunction_dfunc, params);

	double dummyL,dummyU;
	MONOTONICITY monotonicity = get_monotonicity_cost_function(params[0],params[1],params[2],params[3],fwdLowerBound,fwdUpperBound,dummyL,dummyU,false);

	// in the following we only improve intervals if we can detect monotonicity, since for most realistic domains and parameters cost_function is monotonic
	switch(monotonicity){
		case MON_INCR:
			xL = newtonWithLB;
			xU = newtonWithUB;
			break;
		case MON_DECR:
			xL = newtonWithUB;
			xU = newtonWithLB;
			break;
		case MON_NONE:
		{
			// no monotonicity, meaning that we have two branches
			// still need to distinguish if the root is a min or max
			double root = std::exp(-params[2]*std::log(10.)/(2*params[3]));
			if(params[3] >= 0.){ // minimum
				if(bwdLowerBound > mc::cost_function(fwdLowerBound,params[0],params[1],params[2],params[3]) ){
					// we are fully on the right branch but before we got here, both branches were possible
					// we need this case to start newton for xL from the correct point
					params[4] = bwdLowerBound;
					xL = _compute_root(fwdUpperBound, root, fwdUpperBound, costfunction_func, costfunction_dfunc, params);
					params[4] = bwdUpperBound;
					xU = _compute_root(fwdUpperBound, root, fwdUpperBound, costfunction_func, costfunction_dfunc, params);
				}
				else if(bwdLowerBound > mc::cost_function(fwdUpperBound,params[0],params[1],params[2],params[3]) ){
					// we are fully on the left branch but before we got here, both branches were possible
					// we need this case to start newton for xU from the correct point
					params[4] = bwdUpperBound;
					xL = _compute_root(fwdLowerBound, fwdLowerBound, root, costfunction_func, costfunction_dfunc, params);
					params[4] = bwdLowerBound;
					xU = _compute_root(fwdLowerBound, fwdLowerBound, root, costfunction_func, costfunction_dfunc, params);
				}
				else{
					params[4] = bwdUpperBound;
					// now we know that we have two branches
					// the lower or upper bound can only be improved if we cut off something
					if(bwdUpperBound < mc::cost_function(fwdLowerBound,params[0],params[1],params[2],params[3]) ){
						// we can improve the lower bound
						xL = _compute_root(fwdLowerBound, fwdLowerBound, root, costfunction_func, costfunction_dfunc, params);
					}
					if(bwdUpperBound < mc::cost_function(fwdUpperBound,params[0],params[1],params[2],params[3]) ){
						// we can improve the upper bound
						xU = _compute_root(fwdUpperBound, root, fwdUpperBound, costfunction_func, costfunction_dfunc, params);
					}
				}
			}
			else{ // the root is a maximum
				if(bwdUpperBound < mc::cost_function(fwdLowerBound,params[0],params[1],params[2],params[3]) ){
					// we are fully on the right branch but before we got here, both branches were possible
					// we need this case to start newton for xL from the correct point
					params[4] = bwdLowerBound;
					xU = _compute_root(fwdUpperBound, root, fwdUpperBound, costfunction_func, costfunction_dfunc, params);
					params[4] = bwdUpperBound;
					xL = _compute_root(fwdUpperBound, root, fwdUpperBound, costfunction_func, costfunction_dfunc, params);
				}
				else if(bwdUpperBound < mc::cost_function(fwdUpperBound,params[0],params[1],params[2],params[3]) ){
					// we are fully on the left branch but before we got here, both branches were possible
					// we need this case to start newton for xU from the correct point
					params[4] = bwdUpperBound;
					xU = _compute_root(fwdLowerBound, fwdLowerBound, root, costfunction_func, costfunction_dfunc, params);
					params[4] = bwdLowerBound;
					xL = _compute_root(fwdLowerBound, fwdLowerBound, root, costfunction_func, costfunction_dfunc, params);
				}
				else{
					params[4] = bwdUpperBound;
					// now we know that we have two branches
					// the lower or upper bound can only be improved if we cut off something
					if(bwdLowerBound > mc::cost_function(fwdLowerBound,params[0],params[1],params[2],params[3]) ){
						// we can improve the lower bound
						xL = _compute_root(fwdLowerBound, fwdLowerBound, root, costfunction_func, costfunction_dfunc, params);
					}
					if(bwdLowerBound > mc::cost_function(fwdUpperBound,params[0],params[1],params[2],params[3]) ){
						// we can improve the upper bound
						xU = _compute_root(fwdUpperBound, root, fwdUpperBound, costfunction_func, costfunction_dfunc, params);
					}
				}
			}
			break;
		}
	    default:
			break;
	}
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
nrtltau_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::nrtl_tau(x, rusr[0], rusr[1], rusr[2], rusr[3]) - rusr[4];
}


inline double
nrtltau_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::nrtl_dtau(x, rusr[1], rusr[2], rusr[3]);
}


/**
* @brief Function for computing the inverse interval of nrtl tau for contraint propagation (reval in DAG).
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of nrtl tau
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of nrtl tau
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_nrtl_tau
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double* params)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	double newtonWithLB = xL;
	double newtonWithUB = xU;
	params[4] = bwdLowerBound;
	newtonWithLB = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, nrtltau_func, nrtltau_dfunc,params);
	params[4] = bwdUpperBound;
	newtonWithUB = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, nrtltau_func, nrtltau_dfunc, params);

	double dummyL, dummyU; // in this case the range bounds are not needed
	MONOTONICITY monotonicity = get_monotonicity_nrtl_tau(params[0],params[1],params[2],params[3],fwdLowerBound,fwdUpperBound,dummyL,dummyU,/*do not compute range bounds*/false); // this can be found in mccormick.hpp

	// in the following we only improve intervals if we can detect monotonicity, since for most realistic domains and parameters nrtl_tau is monotonic
	switch(monotonicity){
		case MON_INCR:
			xL = newtonWithLB;
			xU = newtonWithUB;
			break;
		case MON_DECR:
			xL = newtonWithUB;
			xU = newtonWithLB;
			break;
		case MON_NONE:
	    default:
			break;
	}
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
nrtldtau_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::nrtl_dtau(x, rusr[0], rusr[1], rusr[2]) - rusr[3];
}


inline double
nrtldtau_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der2_nrtl_tau(x, rusr[0], rusr[1]);
}


/**
* @brief Function for computing the inverse interval of nrtl dtau for contraint propagation (reval in DAG).
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of nrtl dtau
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of nrtl dtau
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_nrtl_dtau
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double* params)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	double newtonWithLB = xL;
	double newtonWithUB = xU;
	params[3] = bwdLowerBound;
	newtonWithLB = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, nrtldtau_func, nrtldtau_dfunc,params);
	params[3] = bwdUpperBound;
	newtonWithUB = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, nrtldtau_func, nrtldtau_dfunc, params);

	double dummyL,dummyU;
	MONOTONICITY monotonicity = get_monotonicity_nrtl_dtau(params[0],params[1],params[2],fwdLowerBound,fwdUpperBound,dummyL,dummyU,false); // this can be found in mccormick.hpp

	// in the following we only improve intervals if we can detect monotonicity, since for most realistic domains and parameters nrtl_tau is monotonic
	switch(monotonicity){
		case MON_INCR:
			xL = newtonWithLB;
			xU = newtonWithUB;
			break;
		case MON_DECR:
			xL = newtonWithUB;
			xU = newtonWithLB;
			break;
		case MON_NONE:
	    default:
			break;
	}
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
psatethanolschroeder_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::p_sat_ethanol_schroeder(x) - *rusr;
}


inline double
psatethanolschroeder_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_p_sat_ethanol_schroeder(x);
}


/**
* @brief Function for computing the inverse interval of the p sat ethanol schroeder function for contraint propagation (reval in DAG).
*        This function is monotonically increasing
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of p sat ethanol schroeder
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of p sat ethanol schroeder
*/
inline void
_compute_inverse_interval_p_sat_ethanol_schroeder
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	double rusr = bwdLowerBound;
	xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, psatethanolschroeder_func, psatethanolschroeder_dfunc, &rusr);
	rusr = bwdUpperBound;
	xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, psatethanolschroeder_func, psatethanolschroeder_dfunc, &rusr);
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
rhovapsatethanolschroeder_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::rho_vap_sat_ethanol_schroeder(x) - *rusr;
}


inline double
rhovapsatethanolschroeder_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_rho_vap_sat_ethanol_schroeder(x);
}


/**
* @brief Function for computing the inverse interval of rho vap sat ethanol schroeder function for contraint propagation (reval in DAG).
*        This function is monotonically increasing
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of rho vap sat ethanol schroeder
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of rho vap sat ethanol schroeder
*/
inline void
_compute_inverse_interval_rho_vap_sat_ethanol_schroeder
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	double rusr = bwdLowerBound;
	xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, rhovapsatethanolschroeder_func, rhovapsatethanolschroeder_dfunc, &rusr);
	rusr = bwdUpperBound;
	xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, rhovapsatethanolschroeder_func, rhovapsatethanolschroeder_dfunc, &rusr);
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 13.09.2017
inline double
rholiqsatethanolschroeder_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::rho_liq_sat_ethanol_schroeder(x) - *rusr;
}


inline double
rholiqsatethanolschroeder_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_rho_liq_sat_ethanol_schroeder(x);
}


/**
* @brief Function for computing the inverse interval of rho liq sat ethanol schroeder function for contraint propagation (reval in DAG).
*        This function is monotonically decreasing.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of rho liq sat ethanol schroeder
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of rho liq sat ethanol schroeder
*/
inline void
_compute_inverse_interval_rho_liq_sat_ethanol_schroeder
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	double rusr = bwdLowerBound;
	xU = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, rholiqsatethanolschroeder_func, rholiqsatethanolschroeder_dfunc, &rusr);
	rusr = bwdUpperBound;
	xL = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, rholiqsatethanolschroeder_func, rholiqsatethanolschroeder_dfunc, &rusr);
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 03.02.2020
inline double
covariance_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::covariance_function(x,rusr[0]) - rusr[1];
}


inline double
covariance_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_covariance_function(x,rusr[0]);
}


/**
* @brief Function for computing the inverse interval of covariance functions for contraint propagation (reval in DAG).
*        The covariance functions are convex and nonincreasing.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of covariance
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of covariance
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_covariance_function
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double* params)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
    params[1] = bwdLowerBound;
	xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, covariance_func, covariance_dfunc, params);
	params[1] = bwdUpperBound;
	xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, covariance_func, covariance_dfunc, params);
}

// Note that acquiosition functions are not symmetrical
inline double
acquisitionx_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::acquisition_function(x,rusr[3],rusr[0],rusr[1]) - rusr[2];
}

// Note that lmtd is symmetrical
inline double
acquisitiony_func
( const double y, const double*rusr, const int*iusr )
{
  return mc::acquisition_function(rusr[3],y,rusr[0],rusr[1]) - rusr[2];
}

inline double
acquisitionx_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_x_acquisition_function(x,rusr[3],rusr[0],rusr[1]);
}

inline double
acquisitiony_dfunc
( const double y, const double*rusr, const int*iusr )
{
  return mc::der_y_acquisition_function(rusr[3],y,rusr[0],rusr[1]);
}

/**
* @brief Function for computing the inverse interval of acquisition functions for contraint propagation (reval in DAG).
*        We make use of monotonicity and convexity properties of the acquisition functions.
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the x lower bound obtained by the inverse interval computation of the acquisition function
* @param[in,out] xU is the x upper bound obtained by the inverse interval computation of the acquisition function
* @param[in,out] yL is the y lower bound obtained by the inverse interval computation of the acquisition function
* @param[in,out] yU is the y upper bound obtained by the inverse interval computation of the acquisition function
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_acquisition_function
(const double xFwdLowerBound, const double xFwdUpperBound, const double yFwdLowerBound, const double yFwdUpperBound,
 const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double& yL, double& yU, double* params)
{
  xL = xFwdLowerBound;
  xU = xFwdUpperBound;
  yL = yFwdLowerBound;
  yU = yFwdUpperBound;
  switch((int)params[0]){
	  case 1: // lower confidence bound
	      // [xL,xU] - fmin * [yL,yU] = [bwdL,bwdU], with fmin>0
	      xL = bwdLowerBound+params[1]*yFwdLowerBound;
		  xU = bwdUpperBound+params[1]*yFwdUpperBound;
		  yL = (xFwdLowerBound-bwdUpperBound)/params[1];
		  yU = (xFwdUpperBound-bwdLowerBound)/params[1];
	      break;
	  case 2: // expected improvement
	      // convex, decreasing in x, increasing in y
          // We can improve xL and xU only in a certain case
		  if(mc::acquisition_function(xFwdLowerBound,yFwdLowerBound,params[0],params[1]) > bwdUpperBound){
			  params[2] = bwdUpperBound;
			  params[3] = yFwdUpperBound;
			  xL = _compute_root(xFwdUpperBound, xFwdLowerBound, xFwdUpperBound, acquisitionx_func, acquisitionx_dfunc, params);
		  }
		  if(mc::acquisition_function(xFwdUpperBound,yFwdUpperBound,params[0],params[1]) < bwdLowerBound){
			  params[2] = bwdLowerBound;
			  params[3] = yFwdUpperBound;
			  xU = _compute_root(xFwdUpperBound, xFwdLowerBound, xFwdUpperBound, acquisitionx_func, acquisitionx_dfunc, params);
		  }
		  // Analogously we can improve yL and yU
		  // We can improve yU and yL only in a certain case
		  if(mc::acquisition_function(xFwdUpperBound,yFwdUpperBound,params[0],params[1]) > bwdUpperBound){
			  params[2] = bwdUpperBound;
			  params[3] = xFwdUpperBound;
			  yU = _compute_root(yFwdUpperBound, yFwdLowerBound, yFwdUpperBound, acquisitiony_func, acquisitiony_dfunc, params);
		  }
		  if(mc::acquisition_function(xFwdLowerBound,yFwdLowerBound,params[0],params[1]) < bwdLowerBound){
			  params[2] = bwdLowerBound;
			  params[3] = xFwdLowerBound;
			  yL = _compute_root(yFwdUpperBound, yFwdLowerBound, yFwdUpperBound, acquisitiony_func, acquisitiony_dfunc, params);
		  }
	      break;
	  case 3:
	      break;
	  default:
	      break;
  }
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 05.02.2020
inline double
gaussian_probability_density_function_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::gaussian_probability_density_function(x) - (*rusr);
}


inline double
gaussian_probability_density_function_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_gaussian_probability_density_function(x);
}


/**
* @brief Function for computing the inverse interval of the gausian probability density function for contraint propagation (reval in DAG).
*        This function is monotonically increasing
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of gausian probability density function
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of gausian probability density function
*/
inline void
_compute_inverse_interval_gaussian_probability_density_function
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	if(xU<=0.){ // monotonically increasing
		double rusr = bwdLowerBound;
		xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, gaussian_probability_density_function_func, gaussian_probability_density_function_dfunc, &rusr);
		rusr = bwdUpperBound;
		xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, gaussian_probability_density_function_func, gaussian_probability_density_function_dfunc, &rusr);
	}
    else if(xL >=0){ // monotonically decreasing
		double rusr = bwdLowerBound;
		xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, gaussian_probability_density_function_func, gaussian_probability_density_function_dfunc, &rusr);
		rusr = bwdUpperBound;
		xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, gaussian_probability_density_function_func, gaussian_probability_density_function_dfunc, &rusr);
	}
	else{
		double leftCorner  = mc::gaussian_probability_density_function(xL);
		double rightCorner = mc::gaussian_probability_density_function(xU);
		if(bwdLowerBound > leftCorner){
			double rusr = bwdLowerBound;
			xL = _compute_root(fwdLowerBound, fwdLowerBound, 0, gaussian_probability_density_function_func, gaussian_probability_density_function_dfunc, &rusr);
		}
		if(bwdLowerBound > rightCorner){
			double rusr = bwdLowerBound;
			xU = _compute_root(fwdUpperBound, 0, fwdUpperBound, gaussian_probability_density_function_func, gaussian_probability_density_function_dfunc, &rusr);
		}
		if(bwdUpperBound < leftCorner){
			double rusr = bwdUpperBound;
			xL = _compute_root(fwdUpperBound, 0, fwdUpperBound, gaussian_probability_density_function_func, gaussian_probability_density_function_dfunc, &rusr);
		}
		if(bwdUpperBound < rightCorner){
			double rusr = bwdUpperBound;
			xU = _compute_root(fwdLowerBound, fwdLowerBound, 0, gaussian_probability_density_function_func, gaussian_probability_density_function_dfunc, &rusr);

		}
	}
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// @AVT.SVT added 05.02.2020
inline double
regnormal_func
( const double x, const double*rusr, const int*iusr )
{
  return mc::regnormal(x,rusr[0],rusr[1]) - rusr[2];
}


inline double
regnormal_dfunc
( const double x, const double*rusr, const int*iusr )
{
  return mc::der_regnormal(x,rusr[0],rusr[1]);
}


/**
* @brief Function for computing the inverse interval of a specific nonlinear function for contraint propagation (reval in DAG).
*        This function is monotonically increasing
*
* @param[in] fwdLowerBound is the lower bound of the forward propagation
* @param[in] fwdUpperBound is the upper bound of the forward propagation
* @param[in] bwdLowerBound is the lower bound of the backward propagation
* @param[in] bwdUpperBound is the upper bound of the backward propagation
* @param[in,out] xL is the lower bound obtained by the inverse interval computation of regnormal
* @param[in,out] xU is the upper bound obtained by the inverse interval computation of regnormal
* @param[in] params are the parameters used to evaluate the function
*/
inline void
_compute_inverse_interval_regnormal
(const double fwdLowerBound, const double fwdUpperBound, const double bwdLowerBound, const double bwdUpperBound, double& xL, double& xU, double* params)
{
	xL = fwdLowerBound;
	xU = fwdUpperBound;
	params[2] = bwdLowerBound;
	xL = _compute_root(fwdLowerBound, fwdLowerBound, fwdUpperBound, regnormal_func, regnormal_dfunc, params);
	params[2] = bwdUpperBound;
	xU = _compute_root(fwdUpperBound, fwdLowerBound, fwdUpperBound, regnormal_func, regnormal_dfunc, params);
}


} // end namespace mc

#endif
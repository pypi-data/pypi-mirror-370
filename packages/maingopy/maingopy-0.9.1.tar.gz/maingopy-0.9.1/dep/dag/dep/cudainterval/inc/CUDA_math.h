
#ifndef CUDA_MATH
#define CUDA_MATH

#pragma once
#include <cuda_runtime.h>
#include "cuda_interval_lib.h"
#include "cuda_interval_rounded_arith.h"
// #include "cudaIntervalLibrary.h"

//#define MY_PI 3.14159265358979323846 /* pi */
#define MY_PI 3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679
#define MY_E 2.718281828459045 // e

#define USE_OUTWARD_ROUNDING true

namespace cudaMath {
	// ************************************ Helper functions for the interval-functions for the GPU ************************************************************ //
	/*
	Returns the quandrant of the input value x based on sin(x) and cos(x)
	1. Quadrant <=> x mod 2*Pi in [     0, pi/2  [
	2. Quadrant <=> x mod 2*Pi in [  pi/2, pi    [
	3. Quadrant <=> x mod 2*Pi in [    pi, 3/2*pi[
	4. Quadrant <=> x mod 2*Pi in [3/2*pi, 2*pi  [
	*/
	template <typename T> // no outward rounding used!
	__device__ int inline sin_cos_quand(T sinx, T cosx) {
		if (sinx >= 0 && cosx > 0) return 1;
		if (sinx > 0 && cosx <= 0) return 2;
		if (sinx <= 0 && cosx < 0) return 3;
		if (sinx < 0 && cosx >= 0) return 4;
	}

	/*
	Return the difference between the quadrants of the LB and UB
	*/
	__device__ int inline sin_cos_quand_dif(int LB_quand, int UB_quand) {
		if (LB_quand <= UB_quand) return UB_quand - LB_quand;
		else return UB_quand + 4 - LB_quand;
	}

	// ************************************ Intrinsic double-functions for the GPU ************************************************************ //
	template <typename T> __device__ bool inline isInteger(T x)
	{
		double tol = 1e-8;
		if (abs(x - (int)x) < tol) return true;
		return false;
	}
	template <typename T> __device__ bool inline isInInterval(T value, interval_gpu<T> interval)
	{
		if (value >= interval.lower() && value <= interval.upper())
			return true;
		return false;
	}
	template <typename T> __device__ T inline cos(T x) { return std::cos(x); }
	template <typename T> __device__ T inline sin(T x) { return std::sin(x); }
	template <typename T> __device__ T inline min(T x, T y) { return (x < y) ? x : y; }
	template <typename T> __device__ T inline max(T x, T y) { return (x > y) ? x : y; }
	template <typename T> __device__ T inline exp(T x) { return std::exp(x); }
	template <typename T> __device__ T inline log(T x) { return std::log(x); }
	template <typename T> __device__ T inline abs(T x) { return (x >= 0) ? x : -x; }
	template <typename T> __device__ T inline sqrt(T x) { return std::sqrt(x); }
	template <typename T> __device__ T inline sqrt_down(T x) { return __dsqrt_rd(x); }
	template <typename T> __device__ T inline sqrt_up(T x) { return __dsqrt_ru(x); }
	template <typename T> __device__ T inline sqr(T x) { return x * x; }
	template <typename T> __device__ T inline sqr_down(T x)
	{
		rounded_arith<T> rnd;
		return rnd.mul_down(x, x);
	}
	template <typename T> __device__ T inline sqr_up(T x)
	{
		rounded_arith<T> rnd;
		return rnd.mul_up(x, x);
	}
	template <typename T> __device__ T inline nth_root(T x, int n) { return pow(x, 1. / n); }
	template <typename T> __device__ T inline pow(T x, T exp) { return std::pow(x, exp); }
	template <typename T> __device__ T inline pow(T x, int exp) { return std::pow(x, (double)exp); }
	template <typename T> __device__ T inline pow_down(T x, int exp) {
		rounded_arith<T> rnd;
		T res(1);

		while (true) {
			if (exp & 1)
				res = rnd.mul_down(res, x);
			exp >>= 1;
			if (!exp)
				break;
			x = rnd.mul_down(x, x);
		}
		return res;
	}
	template <typename T> __device__ T inline pow_up(T x, int exp) 
	{
		rounded_arith<T> rnd;
		T res(1);

		while (true) {
			if (exp & 1)
				res = rnd.mul_up(res, x);
			exp >>= 1;
			if (!exp)
				break;
			x = rnd.mul_up(x, x);
		}
		return res;
	}
	template <typename T> __device__ T inline tanh(T x) { return std::tanh(x); }
	
	// ************************************ Intrinsic interval-functions for the GPU ************************************************************ //
	/* NOTE: 
	 * Outward rounding can be activated (see line 12) for the following interval-functions
	 * sqrt, sqr, pow
	 * 
	 * All other interval-function can not use outward rounding!
	 */
		
	template <typename T> __device__ interval_gpu<T> inline cos(interval_gpu<T> x) {
		T LB = x.lower(), UB = x.upper();
		T cos_LB = cos(LB), cos_UB = cos(UB);
		T sin_LB = sin(LB), sin_UB = sin(UB);
		// Interval is point
		if (UB == LB)
			return interval_gpu<T>(cos_LB);
		// Interval width larger than 2*pi
		else if (UB - LB >= 2 * MY_PI)
			return interval_gpu<T>(T(-1), T(1));
		else {
			int LB_quand = sin_cos_quand(sin_LB, cos_LB);
			int UB_quand = sin_cos_quand(sin_UB, cos_UB);
			int quand_diff = sin_cos_quand_dif(LB_quand, UB_quand);

			if (LB_quand == 1) {
				if (UB_quand == 2 || UB_quand == 1) return interval_gpu<T>(cos_UB, cos_LB);
				if (UB_quand == 3) return interval_gpu<T>(-1, cos_LB);
				if (UB_quand == 4) return interval_gpu<T>(-1, max(cos_LB, cos_UB));
			}
			if (LB_quand == 2) {
				if (UB_quand == 2) return interval_gpu<T>(cos_UB, cos_LB);
				if (UB_quand == 3) return interval_gpu<T>(-1, max(cos_LB, cos_UB));
				if (UB_quand == 4) return interval_gpu<T>(-1, cos_UB);
				if (UB_quand == 1) return interval_gpu<T>(-1, 1);
			}
			if (LB_quand == 3) {
				if (UB_quand == 4 || UB_quand == 3) return interval_gpu<T>(cos_LB, cos_UB);
				if (UB_quand == 1) return interval_gpu<T>(cos_LB, 1);
				if (UB_quand == 2) return interval_gpu<T>(min(cos_LB, cos_UB), 1);
			}
			if (LB_quand == 4) {
				if (UB_quand == 4) return interval_gpu<T>(cos_LB, cos_UB);
				if (UB_quand == 1) return interval_gpu<T>(min(cos_LB, cos_UB), 1);
				if (UB_quand == 2) return interval_gpu<T>(cos_UB, 1);
				if (UB_quand == 3) return interval_gpu<T>(-1, 1);
			}
		}
	} // no outward rounding used!
	template <typename T> __device__ interval_gpu<T> inline sin(interval_gpu<T> x) { return cos(x - interval_gpu<T>(MY_PI / 2)); }

	// Implementation based on https://mediatum.ub.tum.de/doc/1379696/file.pdf - Implementation of Interval Arithmetic in CORA 2016 - Matthias Althoff
	template <typename T> __device__ interval_gpu<T> inline _cos(interval_gpu<T> x)
	{	
		//		!!!!!!! FUNCTION IS NOT WORKING CORRECTLY !!!!!!!!!!!		(fmod does not work)
		interval_gpu<T> y = interval_gpu<T>(fmod(x.lower(), 2 * MY_PI), fmod(x.upper(), 2 * MY_PI));
		interval_gpu<T> Rc1 = interval_gpu<T>(0, MY_PI);
		interval_gpu<T> Rc2 = interval_gpu<T>(MY_PI, 2*MY_PI);

		if (x.upper() - x.lower() > 2 * MY_PI ||
			isInInterval(y.lower(), Rc1) && isInInterval(y.upper(), Rc1) && y.lower() > y.upper() ||
			isInInterval(y.lower(), Rc2) && isInInterval(y.upper(), Rc2) && y.lower() > y.upper())
			return interval_gpu<T>(-1, 1);

		if (isInInterval(y.lower(), Rc2) && isInInterval(y.upper(), Rc2) && y.lower() <= y.upper())
			return interval_gpu<T>(cos(y.lower()), cos(y.upper()));

		if (isInInterval(y.lower(), Rc2) && isInInterval(y.upper(), Rc1))
			return interval_gpu<T>(min(cos(y.lower()), cos(y.upper())), 1);

		if (isInInterval(y.lower(), Rc1) && isInInterval(y.upper(), Rc2))
			return interval_gpu<T>(-1, max(cos(y.lower()), cos(y.upper())));

		if (isInInterval(y.lower(), Rc1) && isInInterval(y.upper(), Rc1) && y.lower() <= y.upper())
			return interval_gpu<T>(cos(y.upper()), cos(y.lower()));
	}
	// Implementation based on https://mediatum.ub.tum.de/doc/1379696/file.pdf - Implementation of Interval Arithmetic in CORA 2016 - Matthias Althoff
	template <typename T> __device__ interval_gpu<T> inline _sin(interval_gpu<T> x)
	{
		//		!!!!!!! FUNCTION IS NOT WORKING CORRECTLY !!!!!!!!!!!		(fmod does not work)
		interval_gpu<T> y = interval_gpu<T>(fmod(x.lower(), 2 * MY_PI), fmod(x.upper(), 2 * MY_PI));
		interval_gpu<T> Rs1 = interval_gpu<T>(0, 0.5 * MY_PI);
		interval_gpu<T> Rs2 = interval_gpu<T>(0.5 * MY_PI, 1.5 * MY_PI);
		interval_gpu<T> Rs3 = interval_gpu<T>(1.5 * MY_PI, 2 * MY_PI);

		if (x.upper() - x.lower() >= 2 * MY_PI ||
			isInInterval(y.lower(), Rs1) && isInInterval(y.upper(), Rs1) && y.lower() > y.upper() ||
			isInInterval(y.lower(), Rs1) && isInInterval(y.upper(), Rs3) ||
			isInInterval(y.lower(), Rs2) && isInInterval(y.upper(), Rs2) && y.lower() > y.upper() ||
			isInInterval(y.lower(), Rs3) && isInInterval(y.upper(), Rs3) && y.lower() > y.upper())
			return interval_gpu<T>(-1, 1);

		if (isInInterval(y.lower(), Rs1) && isInInterval(y.upper(), Rs1) && y.lower() <= y.upper() ||
			isInInterval(y.lower(), Rs3) && isInInterval(y.upper(), Rs1))
			return interval_gpu<T>(sin(y.lower()), sin(y.upper()));

		if (isInInterval(y.lower(), Rs1) && isInInterval(y.upper(), Rs2) ||
			isInInterval(y.lower(), Rs3) && isInInterval(y.upper(), Rs2))
			return interval_gpu<T>(min(sin(y.lower()), sin(y.upper())), 1);

		if (isInInterval(y.lower(), Rs2) && isInInterval(y.upper(), Rs1) ||
			isInInterval(y.lower(), Rs2) && isInInterval(y.upper(), Rs3))
			return interval_gpu<T>(-1, max(sin(y.lower()), sin(y.upper())));

		if (isInInterval(y.lower(), Rs2) && isInInterval(y.upper(), Rs2) && y.lower() <= y.upper())
			return interval_gpu<T>(sin(y.lower()), sin(y.upper()));
	}
	template <typename T> __device__ interval_gpu<T> inline exp(interval_gpu<T> x) { return interval_gpu<T>(exp(x.lower()), exp(x.upper())); }
	template <typename T> __device__ interval_gpu<T> inline log(interval_gpu<T> x) 
	{ 
		if (x.lower() > 0)
			return interval_gpu<T>(log(x.lower()), log(x.upper())); 
		return interval_gpu<T>(-INFINITY, log(x.upper()));
	}
	template <typename T> __device__ interval_gpu<T> inline abs(interval_gpu<T> x) 
	{ 
		if(x.lower() >= 0)
			interval_gpu<T>(abs(x.lower()), abs(x.upper()));
		if(x.upper() <= 0)
			interval_gpu<T>(abs(x.upper()), abs(x.lower()));
		return interval_gpu<T>(0, abs(max(-x.lower(), x.upper()))); 
	}
	template <typename T> __device__ interval_gpu<T> inline abs_derivative(interval_gpu<T> x)
	{
		if (x.upper() < 0)
			return interval_gpu<T>(-1, -1);
		if (x.lower() < 0 && x.upper() == 0)
			return interval_gpu<T>(-1, 0);
		if(x.lower() == 0 && x.upper() == 0)
			return interval_gpu<T>(0, 0);
		if (x.lower() == 0 && x.upper() > 0)
			return interval_gpu<T>(0, 1);
		if (x.lower() > 0)
			return interval_gpu<T>(1, 1);
		//else: lower < 0, upper > 0?
	}
	template <typename T> __device__ interval_gpu<T> inline sqrt(interval_gpu<T> x) {
#if USE_OUTWARD_ROUNDING
		if (x.upper() >= 0) {
			if (x.lower() > 0)
				return interval_gpu<T>(sqrt_down(x.lower()), sqrt_up(x.upper()));
			else
				return interval_gpu<T>(0, sqrt_up(x.upper()));
		}
#else
		if (x.upper() >= 0) {
			if (x.lower() > 0)
				return interval_gpu<T>(sqrt(x.lower()), sqrt(x.upper()));
			else
				return interval_gpu<T>(0, sqrt(x.upper()));
		}
#endif // USE_OUTWARD_ROUNDING
		// TODO: Implement throw error when upper < 0;
	} 
	template <typename T> __device__ interval_gpu<T> inline sqr(interval_gpu<T> x)
	{
#if USE_OUTWARD_ROUNDING
		if (x.lower() >= 0)
			return interval_gpu<T>(sqr_down(x.lower()), sqr_up(x.upper()));
		if (x.upper() <= 0)
			return interval_gpu<T>(sqr_down(x.upper()), sqr_up(x.lower()));
		//if (x.lower() < 0 && x.upper() > 0)
		return interval_gpu<T>(0, sqr_up(max(-x.lower(), x.upper())));
#else
		if (x.lower() >= 0) 
			return interval_gpu<T>(sqr(x.lower()), sqr(x.upper()));
		if (x.upper() <= 0) 
			return interval_gpu<T>(sqr(x.upper()), sqr(x.lower()));
		//if (x.lower() < 0 && x.upper() > 0)
		return interval_gpu<T>(0, sqr(max(-x.lower(), x.upper())));
#endif // USE_OUTWARD_ROUNDING

		//if(abs(x.upper()) > abs(x.lower()))
		//	return interval_gpu<T>(sqr(x.lower()), sqr(x.upper()));
		//return interval_gpu<T>(sqr(x.upper()), sqr(x.lower()));
	}	
	template <typename T> __device__ interval_gpu<T> inline nth_root(interval_gpu<T> x, int n) { return interval_gpu<T>(nth_root(x.lower(), n), nth_root(x.upper(), n)); }
	template <typename T> __device__ interval_gpu<T> inline pow(interval_gpu<T> x, int y) 
	{
		T LB = x.lower(), UB = x.upper();

		if (y == 0) {
			return interval_gpu<T>(1., 1.);
		}
#if USE_OUTWARD_ROUNDING
		else if (y % 2 == 0) {	// Even exponents
			if (UB < 0)			// LB < 0
				return interval_gpu<T>(pow_down(UB, y), pow_up(LB, y));
			else if (LB > 0)	// UB > 0
				return interval_gpu<T>(pow_down(LB, y), pow_up(UB, y));
			else				// if (LB <= 0 && UB >= 0)
				return interval_gpu<T>(0., pow_up(max(-LB, UB), y));
		}
		else {					// Odd exponents
			return interval_gpu<T>(pow_down(LB, y), pow_up(UB, y));
		}
#else
		else if (y % 2 == 0) { // Even exponents
			if (LB < 0 && UB < 0)
				return interval_gpu<T>(pow(UB, y), pow(LB, y));
			else if (LB > 0 && UB > 0)
				return interval_gpu<T>(pow(LB, y), pow(UB, y));
			else
				return interval_gpu<T>(0., pow(max(-LB, UB), y));
		}
		else {// Odd exponents
			return interval_gpu<T>(pow(LB, y), pow(UB, y));
		}
#endif // USE_OUTWARD_ROUNDING
	}
	template <typename T> __device__ interval_gpu<T> inline pow(interval_gpu<T> x, double y)
	{
		if (isInteger(y))
			return pow(x, (int)y);
		else
			return interval_gpu<T>(pow(x.lower(), y), pow(x.upper(), y));
	}
	template <typename T> __device__ interval_gpu<T> inline pow(interval_gpu<T> x, interval_gpu<T> y)
	{
		double tol = 1e-8;
		if (abs(y.lower() - y.upper()) < tol)
			return pow(x, y.lower());

		//if (y.lower() <= 0)
		//	return exp(y * log(interval_gpu<T>(tol, x.upper())));	// !!! We are cutting of the negative part of the exponent. This can lead to wrong results.

		return exp(y * log(x));
	} // No outward rounding used !!!
	template <typename T> __device__ interval_gpu<T> inline tanh(interval_gpu<T> x) 
	{ 
		T LB = static_cast<T>(-1);
		T UB = static_cast<T>(1);
		// Outward rounding
		LB = std::nextafter(std::tanh(x.lower()), LB);
		UB = std::nextafter(std::tanh(x.upper()), UB);

		//double tol = 1e-1;
		//return I_gpu(tanh(x.lower() - tol), tanh(x.upper() + tol));
		//return I_gpu(std::tanh(x.lower()), std::tanh(x.upper())); 

		return interval_gpu<T>(LB, UB);
	} 
	template <typename T> __device__ interval_gpu<T> inline max(interval_gpu<T> x, interval_gpu<T> y)
	{
		T LB = max(x.lower(), y.lower());
		T UB = max(x.upper(), y.upper());

		return interval_gpu<T>(LB, UB);
	} 

	template<class T> inline __device__ __host__ interval_gpu<T> intersection(interval_gpu<T> const& interval1, interval_gpu<T> const& interval2)
	{
		T LB = max(interval1.lower(), interval2.lower());
		T UB = min(interval1.upper(), interval2.upper());
		return interval_gpu<T>(LB, UB);
	}
	template<class T> inline __device__ __host__ interval_gpu<T> intervalUnion(interval_gpu<T> const& interval1, interval_gpu<T> const& interval2)
	{
		T LB = min(interval1.lower(), interval2.lower());
		T UB = max(interval1.upper(), interval2.upper());
		return interval_gpu<T>(LB, UB);
	}
} // namespace cudaMath

// ************************************ Interval-operators for the GPU ************************************************************ //
template<class T> inline __device__	interval_gpu<T> operator/(interval_gpu<T> const& x, interval_gpu<T> const& y)
{
	/*rounded_arith<T> rnd;
	return interval_gpu<T>(rnd.sub_down(x.lower(), y.upper()),
		rnd.sub_up(x.upper(), y.lower()));*/
	return x * (1. / y);
}// no outward rounding used!
template<class T, typename K> inline __device__ interval_gpu<T> operator/(K const& x, interval_gpu<T> const& y)
{
	T y_LB = y.lower(), y_UB = y.upper();
	//if (y_LB == 0 && y_UB == 0) throw "ERROR: Invalid argument for / ";	TODO: Implement 1/0
	if (y_LB == 0 && y_UB > 0) return interval_gpu<T>(x / y_UB, INFINITY);
	if (y_LB < 0 && y_UB == 0) return interval_gpu<T>(-INFINITY, x / y_LB);
	if (y_LB < 0 && y_UB > 0) return interval_gpu<T>(-INFINITY, INFINITY);
	return interval_gpu<T>(x / y_UB, x / y_LB);
}// no outward rounding used!
template<class T, typename K> inline __device__	interval_gpu<T> operator*(K const& x, interval_gpu<T> const& y)
{
	return interval_gpu<T>(x) * y;
}
template<class T, typename K> inline __device__ interval_gpu<T> operator*(interval_gpu<T> const& x, K const& y)
{
	return x * interval_gpu<T>(y);
}
template<class T, typename K> inline __device__	interval_gpu<T> operator+(K const& x, interval_gpu<T> const& y) {
	return interval_gpu<T>(x) + y;
}
template<class T, typename K> inline __device__	interval_gpu<T> operator+(interval_gpu<T> const& x, K const& y) {
	return x + interval_gpu<T>(y);
}
template<class T, typename K> inline __device__	interval_gpu<T> operator-(K const& x, interval_gpu<T> const& y) {
	return interval_gpu<T>(x) - y;
}
template<class T, typename K> inline __device__	interval_gpu<T> operator-(interval_gpu<T> const& x, K const& y) {
	return x - interval_gpu<T>(y);
}
template<typename T, typename K> inline __device__ T operator^(T const& x, K const& y) { return cudaMath::pow(x, y); }


#endif // CUDA_MATH
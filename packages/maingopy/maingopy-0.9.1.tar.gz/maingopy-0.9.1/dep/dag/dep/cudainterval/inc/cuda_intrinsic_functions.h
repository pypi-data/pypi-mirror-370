
#ifndef  CUDA_INTRINSIC_FUNCTION_DECLARATION_CUH
#define  CUDA_INTRINSIC_FUNCTION_DECLARATION_CUH

#include <cuda_runtime.h>

// template<typename T> __device__ T next_after (T x, T y);
// __device__ float next_after (float x, float y) { return nextafterf(x, y); } 

// __device__ double next_after(double x, double y) { return nextafter(x, y); }

__device__ float __fadd_rd (float x, float y) ;

__device__ float __fadd_ru (float x, float y) ;

__device__ float __fdiv_rd (float x, float y);

__device__ float __fdiv_ru (float x, float y);

__device__ float __fmul_rd (float x, float y);

__device__ float __fmul_ru (float x, float y);

__device__ float __fsqrt_rd(float x);

__device__ float __fsqrt_ru(float x);

__device__ float __int_as_float(int x);

__device__ double __dadd_rd(double x, double y);

__device__ double __dadd_ru(double x, double y);

__device__ double __dmul_rd(double x, double y);

__device__ double __dmul_ru(double x, double y);

__device__ double __ddiv_rd(double x, double y);

__device__ double __ddiv_ru(double x, double y);

__device__ double __dsqrt_rd(double x);

__device__ double __dsqrt_ru(double x);

__device__ double __longlong_as_double(long long int x);

#endif /* end of include guard:  CUDA_INTRINSIC_FUNCTION_DECLARATION_CUH */
 /* end of include guard:  */
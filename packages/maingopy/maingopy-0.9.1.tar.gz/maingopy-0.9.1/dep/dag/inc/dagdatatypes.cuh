#ifndef DAGDATATYPES_CUH
#define DAGDATATYPES_CUH


#pragma once
#ifdef CUDA_INSTALLED
#include <cuda_runtime.h>
#include <cuda_interval_lib.h>
#include <cuda_interval_rounded_arith.h>

#define CUDA_ERROR_CHECK(call){ const cudaError_t error = call; if (error != cudaSuccess)	{	printf("\nError: %s \n  Line: %d \n", __FILE__, __LINE__);	printf("  Error-Code: %d \n  Reason: %s\n", error, cudaGetErrorString(error));	exit(1);}}

typedef interval_gpu<double> I_gpu;

namespace SVT_DAG {

	__device__ __host__
		double inline convert_to_double(I_gpu interval)
	{
		// TODO: Implement error check and control if interval.lower() == interval.upper()
		return (double)interval.lower();
	}
	__device__ __host__ double inline convert_to_double(double x) { return x; }

	__device__ __host__
		int inline convert_to_int(I_gpu interval)
	{
		// TODO: Implement error check and control if interval.lower() == interval.upper()
		return (int)interval.lower();
	}

	__device__ __host__ int inline convert_to_int(double value) { return (int)value; }
	__device__ __host__ int inline convert_to_int(int value) { return value; }

	template <typename T> T* copy_ptr_to_gpu(const T* oldPtr, int nElem)
	{
		T* newPtr;

		// Determine size of pointer content
		size_t bytes = nElem * sizeof(T);

		// Allocate memory on GPU
		cudaMalloc(&newPtr, bytes);

		// Copy data from CPU to GPU
		cudaMemcpy(newPtr, oldPtr, bytes, cudaMemcpyHostToDevice);

		return newPtr;
	}
} // namespace SVT_DAG
#endif // CUDA_INSTALLED
#endif // DAGDATATYPES_CUH
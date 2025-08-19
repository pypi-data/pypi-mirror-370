#ifndef BASEOPERATION_CUH
#define BASEOPERATION_CUH

#pragma once
#include "dagdatatypes.h"

#ifdef CUDA_INSTALLED
#include "operations.h"
//#include <unistd.h>

namespace SVT_DAG {

	// It is necessary to create object representing a function
	// directly in global memory of the GPU device for virtual
	// functions to work correctly, i.e. virtual function table
	// HAS to be on GPU as well.
	template <typename T>
	__global__ void create_concept_ptr_on_gpu(Concept** d_ptr_concept, const T specificOperation)
	{
		(*d_ptr_concept) = new Model<T>(specificOperation);
	}
	// No need for the explicit instantiation of create_concept_ptr_on_gpu, as this function
	// will be implicit instantiated during the initialization of BaseOperation
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Addition);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Subtraction);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Multiplication);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Division);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Exponential);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const PowerOperation);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const SquareRootOperation);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const SquareOperation);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Negative);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const TangensHyperbolicus);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Logarithmus);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const AbsoluteValue);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Cosinus);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Sinus);
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Inverse);                                                       
	// template __global__ void create_concept_ptr_on_gpu(Concept**, const Maximum);

	template <typename T>
	__host__
	Concept** BaseOperation::init_concept_ptr_on_GPU(const T& specificOperation)
	{
		//sleep(20);
		Concept** d_ptr_concept = NULL;

		CUDA_ERROR_CHECK(cudaMalloc(&d_ptr_concept, sizeof(Concept*)));

		create_concept_ptr_on_gpu << <1, 1 >> > (d_ptr_concept, specificOperation);

		//For test, can only catach the last API call error
		// cudaError errSync = cudaGetLastError();
		// printf("Sync error after launching the kernel function create_concept_ptr_on_gpu, name: %s\n", cudaGetErrorName(errSync));
		// printf("Sync error after launching the kernel function create_concept_ptr_on_gpu, content: %s\n", cudaGetErrorString(errSync));

		CUDA_ERROR_CHECK(cudaDeviceSynchronize());

		return d_ptr_concept;
	}
} // namespace SVT_DAG

#endif //CUDA_INSTALLED
#endif //BASEOPERATION_CUH
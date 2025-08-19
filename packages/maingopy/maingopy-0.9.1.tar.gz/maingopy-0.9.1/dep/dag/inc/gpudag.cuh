#ifndef GPUDAG_CUH
#define GPUDAG_CUH

#pragma once
#include "dagdatatypes.cuh"
#include "dagdatatypes.h"

#ifdef CUDA_INSTALLED
#include "dag.h"

struct testStruct{};

namespace SVT_DAG {

	namespace GpuDagFunctions {
		template <typename T>
		__global__ void copy_ptr_values_kernel(T* dst, T* src, int numberElements)
		{
			for (int i = 0; i < numberElements; i++) {
				dst[i] = src[i];
			}
		}
/*		__global__ void copy_ptr_values_kernel(DependentDagVar* dst, DependentDagVar* src, int numberElements)
		{
			for (int i = 0; i < numberElements; i++) {
				dst[i] = src[i];
			}
		}  */  
	}

	// Only for the evaluation on the GPU
	struct GpuDag {
		IndependentDagVar* d_independentVars = NULL;
		DependentDagVar* d_dependentVars = NULL;
		ConstantDagVar* d_constantVars = NULL;

		int numIndependentVars;
		int numDependentVars;
		int numConstantVars;
		int numVars;

		//I_gpu* dagVarValues = NULL;
		//I_gpu* valuesOfIndependentVariables = NULL;

		__device__ __host__ GpuDag()
		{
			this->numIndependentVars = 0;
			this->numDependentVars = 0;
			this->numConstantVars = 0;
			this->numVars = 0;
		}
		__device__ __host__ GpuDag(Dag& dag)
		{
			//d_independentVars = dag.d_independentVars;
			//d_dependentVars = dag.d_dependentVars;
			//d_constantVars = dag.d_constantVars;

			numIndependentVars = dag.numIndependentVars;
			numDependentVars = dag.numDependentVars;
			numConstantVars = dag.numConstantVars;
			numVars = dag.numVars;

			//// Allocate memory on GPU
			size_t bytesIndependentVars = numIndependentVars * sizeof(IndependentDagVar);
			size_t bytesDependentVars = numDependentVars * sizeof(DependentDagVar);
			size_t bytesConstantVars = numConstantVars * sizeof(ConstantDagVar);

			cudaMalloc(&d_independentVars, bytesIndependentVars);
			cudaMalloc(&d_dependentVars, bytesDependentVars);
			cudaMalloc(&d_constantVars, bytesConstantVars);

			// Copy values from Dag to GpuDag
			//copy_ptr_values(d_independentVars, dag.d_independentVars, numIndependentVars);
			//copy_ptr_values(d_dependentVars, dag.d_dependentVars, numDependentVars);
			//copy_ptr_values(d_constantVars, dag.d_constantVars, numConstantVars);
		}
		__device__ __host__ GpuDag(Dag* dag)
		{
#ifdef CUDA_INSTALLED
			d_independentVars = dag->d_independentVars;
			d_dependentVars = dag->d_dependentVars;
			d_constantVars = dag->d_constantVars;
#endif //CUDA_INSTALLED

			numIndependentVars = dag->numIndependentVars;
			numDependentVars = dag->numDependentVars;
			numConstantVars = dag->numConstantVars;
			numVars = dag->numVars;
		}

	private:
		template <typename T>
		void copy_ptr_values(T* dst, T* src, int numberElemnts)
		{
			GpuDagFunctions::copy_ptr_values_kernel << <1, 1 >> > (dst, src, numberElemnts);
			CUDA_ERROR_CHECK(cudaDeviceSynchronize());
		}
		//void copy_ptr_values(DependentDagVar* dst, DependentDagVar* src, int numberElements)
		//{
		//	// Construtct temporary dependent variable array with pointers to GPU
		//	DependentDagVar* h_dependentVars;
		//	h_dependentVars = (DependentDagVar*)malloc(numDependentVars * sizeof(DependentDagVar));
		//	for (int i = 0; i < numDependentVars; i++)
		//	{
		//		//BaseOperation* operation = copy_ptr_to_gpu(arrDependentVars[i].operation, 1);
		//		//const int* operandIds = copy_ptr_to_gpu(arrDependentVars[i].operandIds, arrDependentVars[i].numOperands);
		//		//h_dependentVars[i] = DependentDagVar(arrDependentVars[i].dagVarId, operation, operandIds, arrDependentVars[i].numOperands);
		//	}
		//}
	};

} // namespace SVT_DAG

#endif // CUDA_INSTALLED
#endif // GPUDAG_CUH
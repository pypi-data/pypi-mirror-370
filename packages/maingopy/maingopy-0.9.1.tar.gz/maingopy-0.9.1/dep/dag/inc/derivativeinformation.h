
#pragma once
#include "dag.h" 
#include "dagdatatypes.h"
#include "dagdatatypes.cuh"

namespace SVT_DAG {

	struct DerivativeInformation {
		// By now the function values on CPU are not used (CF on CPU is not implemented)
		I_cpu* functionValue_I_cpu;
		// By now the function derivative values on CPU are not used (CF on CPU is not implemented)
		I_cpu* derivativeValue_I_cpu;

		bool* isDependentOfIndependentVariable_CPU;
		int numIndependentVariables;

#ifdef CUDA_INSTALLED
		I_gpu* functionValue_I_gpu;
		I_gpu* functionValue_I_gpu_host;

		I_gpu* derivativeValue_I_gpu;
		I_gpu* derivativeValue_I_gpu_host;

		bool* isDependentOfIndependentVariable_GPU;
#endif // CUDA_INSTALLED
		// The memory used by DerivativeInformation objects are ponted by dag members
		// ~DerivativeInformation();
	
	};


	DerivativeInformation* get_derivativeInformation_vector_from_dag(Dag& dag, int numSubintervals);

} // namespace SVT_DAG
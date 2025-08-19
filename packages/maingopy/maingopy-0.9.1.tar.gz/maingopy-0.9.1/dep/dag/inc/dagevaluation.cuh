#ifndef DAGEVALUATION_CUH
#define DAGEVALUATION_CUH

#pragma once

#ifdef CUDA_INSTALLED
#include "dag.h"
#include "gpudag.cuh"
#include "derivativeinformation.h"

namespace SVT_DAG {

	// WARNING: Function does not check whether dag is synchronized (copied to GPU) or not
	template <typename dataType>
	__device__
	dataType*
	evaluate_on_gpu(Dag& dag, dataType* valuesOfIndependentVariables, dataType* dagVarValues)
	{ 
		for (int i = 0; i < dag.numIndependentVars; ++i)
		{
			dagVarValues[dag.d_independentVars[i].dagVarId] = valuesOfIndependentVariables[i];
		}

#pragma unroll
		for (int i = 0; i < dag.numConstantVars; i ++)
		{
			dagVarValues[dag.d_constantVars[i].dagVarId] = dag.d_constantVars[i].value;
		}

#pragma unroll
		for (int i = 0; i < dag.numDependentVars; ++i)
		{
			dagVarValues[dag.d_dependentVars[i].dagVarId] = dag.d_dependentVars[i].operation->evaluate_on_GPU(dagVarValues, dag.d_dependentVars[i].operandIds);
		}
	return dagVarValues;
	}

	template <typename dataType, typename T>
	__device__
		void
		evaluate_derivative_on_GPU(T& dag, dataType* valuesOfIndependentVariables, DerivativeInformation* dagVarValues)
	{		
		for (int i = 0; i < dag.numIndependentVars; ++i)
		{
			dagVarValues[dag.d_independentVars[i].dagVarId].functionValue_I_gpu[0] = valuesOfIndependentVariables[i];
		}		
		for (int i = 0; i < dag.numConstantVars; i++)
		{
			dagVarValues[dag.d_constantVars[i].dagVarId].functionValue_I_gpu[0] = dag.d_constantVars[i].value;
		}
		for (int i = 0; i < dag.numDependentVars; ++i)
		{
			dag.d_dependentVars[i].operation->evaluate_derivative_on_GPU(dagVarValues, dag.d_dependentVars[i].operandIds, dagVarValues[dag.d_dependentVars[i].dagVarId]);
		}
		//printf("\nDagVarValues:\n");
		//for (int i = 0; i < dag.numVars; i++) {
		//	printf(" dagVar[%2d]\n", i);
		//	printf("   val = [%f, %f]\n", dagVarValues[i].functionValue_I_gpu[0].lower(), dagVarValues[i].functionValue_I_gpu[0].upper());
		//	printf("   der = [%f, %f]\n", dagVarValues[i].derivativeValue_I_gpu[0].lower(), dagVarValues[i].derivativeValue_I_gpu[0].upper());
		//}
		//printf("\n");

	}
} // namespace SVT_DAG

#endif // CUDA_INSTALLED
#endif // DAGEVALUATION_CUH
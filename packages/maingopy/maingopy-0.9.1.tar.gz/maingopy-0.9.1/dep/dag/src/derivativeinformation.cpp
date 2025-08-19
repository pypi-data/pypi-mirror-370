
//#pragma once
#include "derivativeinformation.h"

namespace SVT_DAG {
	namespace DerivativeValueFunctions {
		void init_variable_dependencies_of_derivativeInformations(DerivativeInformation* derivativeInformations, Dag& dag)
		{
			int numDerivativeValues = dag.numIndependentVars;

			// Dependencies of independent variables
			for (int i = 0; i < dag.numIndependentVars; i++) {
				int positionOfDependencies = dag.independentVars[i].dagVarId * numDerivativeValues;
				bool* tmpIsDependentOfIndependentVariable = &derivativeInformations->isDependentOfIndependentVariable_CPU[positionOfDependencies];

				for (int j = 0; j < numDerivativeValues; j++)
					if (i == j) tmpIsDependentOfIndependentVariable[j] = true;
					else tmpIsDependentOfIndependentVariable[j] = false;

				derivativeInformations[dag.independentVars[i].dagVarId].isDependentOfIndependentVariable_CPU = tmpIsDependentOfIndependentVariable;
			}

			// Dependencies of constant variables
			for (int i = 0; i < dag.numConstantVars; i++) {
				int positionOfDependencies = dag.constantVars[i].dagVarId * numDerivativeValues;
				bool* tmpIsDependentOfIndependentVariable = &derivativeInformations->isDependentOfIndependentVariable_CPU[positionOfDependencies];

				for (int j = 0; j < numDerivativeValues; j++)
					tmpIsDependentOfIndependentVariable[j] = false;

				derivativeInformations[dag.constantVars[i].dagVarId].isDependentOfIndependentVariable_CPU = tmpIsDependentOfIndependentVariable;
			}

			// Dependencies of dependent variables
			for (int i = 0; i < dag.numDependentVars; i++) {
				int positionOfDependencies = dag.dependentVars[i].dagVarId * numDerivativeValues;
				bool* tmpIsDependentOfIndependentVariable = &derivativeInformations->isDependentOfIndependentVariable_CPU[positionOfDependencies];

				DependentDagVar currentVar = dag.dependentVars[i];

				for (int j = 0; j < numDerivativeValues; j++) {
					tmpIsDependentOfIndependentVariable[j] = false;

					for (int operand = 0; operand < currentVar.numOperands; operand++)
						if (derivativeInformations[currentVar.operandIds[operand]].isDependentOfIndependentVariable_CPU[j])
							tmpIsDependentOfIndependentVariable[j] = true;
				}

				derivativeInformations[dag.dependentVars[i].dagVarId].isDependentOfIndependentVariable_CPU = tmpIsDependentOfIndependentVariable; 
			}
		}
#ifdef CUDA_INSTALLED
		DerivativeInformation get_new_derivativeInformation_for_gpu(int numIndependentVars, int id, I_gpu* h_functionAndDerivativeValues, I_gpu* d_functionAndDerivativeValues,
			bool* isDependentOfIndependentVariable, bool* d_isDependentOfIndependentVariable) 
		{
			DerivativeInformation derivativeInformation;

			derivativeInformation.numIndependentVariables = numIndependentVars;

			derivativeInformation.functionValue_I_gpu = &d_functionAndDerivativeValues[id * (numIndependentVars + 1)];
			derivativeInformation.derivativeValue_I_gpu = &d_functionAndDerivativeValues[id * (numIndependentVars + 1) + 1];

			derivativeInformation.functionValue_I_gpu_host = &h_functionAndDerivativeValues[id * (numIndependentVars + 1)];
			derivativeInformation.derivativeValue_I_gpu_host = &h_functionAndDerivativeValues[id * (numIndependentVars + 1) + 1];

			derivativeInformation.isDependentOfIndependentVariable_CPU = &isDependentOfIndependentVariable[id * numIndependentVars];
			derivativeInformation.isDependentOfIndependentVariable_GPU = &d_isDependentOfIndependentVariable[id * numIndependentVars];

			return derivativeInformation;
		}

		void init_derivativeValues_for_independentDagVars_for_gpu(DerivativeInformation* derivativeInformations, Dag& dag, int subintervalId, I_gpu* h_functionAndDerivativeValues)
		{
			for (int independVar = 0; independVar < dag.numIndependentVars; independVar++) {

				int currentDagVarId = dag.independentVars[independVar].dagVarId;
				I_gpu* tmpDerivativeValues = derivativeInformations[currentDagVarId].derivativeValue_I_gpu_host;

				for (int derivative = 0; derivative < dag.numIndependentVars; derivative++) {

					if (independVar == derivative)
						tmpDerivativeValues[derivative] = I_gpu(1);
					else
						tmpDerivativeValues[derivative] = I_gpu(0);
				}
			}
		}

		void init_derivativeValues_for_constantDagVars_for_gpu(DerivativeInformation* derivativeInformations, Dag& dag, int subintervalId, I_gpu* h_functionAndDerivativeValues)
		{
			for (int constantVar = 0; constantVar < dag.numConstantVars; constantVar++) {
				int currentDagVarId = dag.constantVars[constantVar].dagVarId;
				I_gpu* tmpDerivativeValues = derivativeInformations[currentDagVarId].derivativeValue_I_gpu_host;

				for (int derivative = 0; derivative < dag.numIndependentVars; derivative++)
					tmpDerivativeValues[derivative] = I_gpu(0);
			}
		}

		DerivativeInformation* get_derivativeInformation_vector_from_dag_for_gpu(Dag& dag, int numSubintervals)
		{
			int numVars = dag.numVars;
			int numIndependentVars = dag.numIndependentVars;
			bool gpuUsedForLowerBounding = true;

			// Allocate memory for all derivativeInformation objects
			DerivativeInformation* derivativeInformations, * d_derivativeInformations;
			size_t bytesDerivativeValues = numVars * numSubintervals * sizeof(DerivativeInformation);
			derivativeInformations = (DerivativeInformation*)malloc(bytesDerivativeValues);

			// Allocate memory for functionValue and derivativeValues for the derivativeInformation objects
			size_t bytesFunctionAndDerivativeValues = numVars * numSubintervals * (numIndependentVars + 1) * sizeof(I_gpu);
			dag.h_functionAndDerivativeValues = (I_gpu*)malloc(bytesFunctionAndDerivativeValues);
			CUDA_ERROR_CHECK(cudaMalloc(&dag.d_functionAndDerivativeValues, bytesFunctionAndDerivativeValues));

			for (int i = 0; i < numVars * numSubintervals * (numIndependentVars + 1); i++)
				dag.h_functionAndDerivativeValues[i] = I_gpu(i);

			// Allocate memory for isDependentOfIndependentVariable_GPU for all derivativeInformation objects
			size_t bytesIsDependentOfIndependentVariable = numVars * numSubintervals * numIndependentVars * sizeof(bool);
			dag.isDependentOfIndependentVariable = (bool*)malloc(bytesIsDependentOfIndependentVariable);
			CUDA_ERROR_CHECK(cudaMalloc(&dag.d_isDependentOfIndependentVariable, bytesIsDependentOfIndependentVariable));

			for (int id = 0; id < numSubintervals * numVars; id++) 
				derivativeInformations[id] = get_new_derivativeInformation_for_gpu(numIndependentVars, id, dag.h_functionAndDerivativeValues, dag.d_functionAndDerivativeValues, 
																					dag.isDependentOfIndependentVariable, dag.d_isDependentOfIndependentVariable);
			

			for (int i = 0; i < numSubintervals; i++) {
				DerivativeInformation* currentInformation = &derivativeInformations[numVars * i];

				init_variable_dependencies_of_derivativeInformations(currentInformation, dag);				

				// Derivative values for independent and constant vars are know and can already be initialized
				init_derivativeValues_for_independentDagVars_for_gpu(currentInformation, dag, i, dag.h_functionAndDerivativeValues);
				init_derivativeValues_for_constantDagVars_for_gpu(currentInformation, dag, i, dag.h_functionAndDerivativeValues);
			}

			CUDA_ERROR_CHECK(cudaMemcpy(dag.d_isDependentOfIndependentVariable, dag.isDependentOfIndependentVariable, bytesIsDependentOfIndependentVariable, cudaMemcpyHostToDevice));
			CUDA_ERROR_CHECK(cudaMemcpy(dag.d_functionAndDerivativeValues, dag.h_functionAndDerivativeValues, bytesFunctionAndDerivativeValues, cudaMemcpyHostToDevice));

			cudaMalloc(&d_derivativeInformations, bytesDerivativeValues);
			cudaMemcpy(d_derivativeInformations, derivativeInformations, bytesDerivativeValues, cudaMemcpyHostToDevice);
			free(derivativeInformations);

			return d_derivativeInformations;
		}
#endif // CUDA_INSTALLED2

		DerivativeInformation get_new_derivativeInformation(int numIndependentVars, int id, I_cpu* functionAndDerivativeValues, bool* isDependentOfIndependentVariable) 
		{
			DerivativeInformation derivativeInformation;

			derivativeInformation.numIndependentVariables = numIndependentVars;

			derivativeInformation.functionValue_I_cpu = &functionAndDerivativeValues[id * (numIndependentVars + 1)];
			derivativeInformation.derivativeValue_I_cpu = &functionAndDerivativeValues[id * (numIndependentVars + 1) + 1];

			derivativeInformation.isDependentOfIndependentVariable_CPU = &isDependentOfIndependentVariable[id * numIndependentVars];

			return derivativeInformation;
		}

		void init_derivativeValues_for_independentDagVars(DerivativeInformation* derivativeInformations, Dag& dag, int subintervalId, I_cpu* functionAndDerivativeValues)
		{
			for (int independVar = 0; independVar < dag.numIndependentVars; independVar++) {

				int currentDagVarId = dag.independentVars[independVar].dagVarId;
				I_cpu* tmpDerivativeValues = derivativeInformations[currentDagVarId].derivativeValue_I_cpu;

				for (int derivative = 0; derivative < dag.numIndependentVars; derivative++) {

					if (independVar == derivative)
						tmpDerivativeValues[derivative] = I_cpu(1);
					else
						tmpDerivativeValues[derivative] = I_cpu(0);
				}
			}
		}

		void init_derivativeValues_for_constantDagVars(DerivativeInformation* derivativeInformations, Dag& dag, int subintervalId, I_cpu* functionAndDerivativeValues)
		{
			for (int constantVar = 0; constantVar < dag.numConstantVars; constantVar++) {
				int currentDagVarId = dag.constantVars[constantVar].dagVarId;
				I_cpu* tmpDerivativeValues = derivativeInformations[currentDagVarId].derivativeValue_I_cpu;

				for (int derivative = 0; derivative < dag.numIndependentVars; derivative++)
					tmpDerivativeValues[derivative] = I_cpu(0);
			}
		}

		DerivativeInformation* get_derivativeInformation_vector_from_dag_for_cpu(Dag& dag, int numSubintervals)
		{
			int numVars = dag.numVars;
			int numIndependentVars = dag.numIndependentVars;

			// Allocate memory for all derivativeInformation objects
			DerivativeInformation* derivativeInformations;
			derivativeInformations = new DerivativeInformation[numVars * numSubintervals];

			// Allocate memory for functionValue and derivativeValues for the derivativeInformation objects
			size_t bytesFunctionAndDerivativeValues = numVars * numSubintervals * (numIndependentVars + 1) * sizeof(I_cpu);
			dag.functionAndDerivativeValues = (I_cpu*)malloc(bytesFunctionAndDerivativeValues);

			for (int i = 0; i < numVars * numSubintervals * (numIndependentVars + 1); i++)
				dag.functionAndDerivativeValues[i] = I_cpu(i);

			// Allocate memory for isDependentOfIndependentVariable for all derivativeInformation objects
			size_t bytesIsDependentOfIndependentVariable = numVars * numSubintervals * numIndependentVars * sizeof(bool);
			dag.isDependentOfIndependentVariable = (bool*)malloc(bytesIsDependentOfIndependentVariable);


			for (int id = 0; id < numSubintervals * numVars; id++) 
				derivativeInformations[id] = get_new_derivativeInformation(numIndependentVars, id, dag.functionAndDerivativeValues, dag.isDependentOfIndependentVariable);
			

			for (int i = 0; i < numSubintervals; i++) {
				DerivativeInformation* currentInformation = &derivativeInformations[numVars * i];
				init_variable_dependencies_of_derivativeInformations(currentInformation, dag);				

				// Derivative values for independent and constant vars are know and can already be initialized
				init_derivativeValues_for_independentDagVars(currentInformation, dag, i, dag.functionAndDerivativeValues);
				init_derivativeValues_for_constantDagVars(currentInformation, dag, i, dag.functionAndDerivativeValues);
			}

			return derivativeInformations;
		}	
	
	}
	DerivativeInformation* get_derivativeInformation_vector_from_dag(Dag& dag, int numSubintervals)
	{
#ifdef CUDA_INSTALLED
		return DerivativeValueFunctions::get_derivativeInformation_vector_from_dag_for_gpu(dag, numSubintervals);
#else
		return DerivativeValueFunctions::get_derivativeInformation_vector_from_dag_for_cpu(dag, numSubintervals);
#endif
	}
} // namespace SVT_DAG
#pragma once
#include "subinterval_arithmetic_settings.cuh"
#include "dagConversion.h"

#include "interval/interval.hpp"

namespace cu
{
	// Define the sqr function for the sqr operation for double type
	// Used when contructing the cuda graph for centers (tangent<double>)
    inline __device__ double sqr(double x)
	{
		return x * x ; 
    	// return __dmul_rn(x, x);
	}
}

#include "cuinterval/cuinterval.h"
#include "cutangent/cutangent.cuh"
#include "cudaUtilities.h"

typedef filib::interval<double, filib::rounding_strategy::native_switched, filib::interval_mode::i_mode_extended> I_cpu;
typedef cu::interval<double> I_gpu; 

namespace SIA {	

	template <typename I>
	class subinterval_arithmetic_memory;

	/**
		* @brief Class for managing the results of the subinterval arithmetic.
		*		It can be used to access the interval bounds of objective function and constraints.
		*		Therefore, it is necessary to update to result after each iteration.
		*/
	template <typename I>
	class subinterval_arithmetic_result {

		enum FunctionType 
		{ 
			_OBJECTIVE = 0, 
			_INEQUALITY, 
			_EQUALITY	
		};

	
		std::vector<int> startFunctionIds;			// Vector containing the indices where the different function types (obj, ineq, eq) start in the vector containing all function values
		std::vector<int> numFunctionsPerType;		// Vector containing the numbers of functions per type
		std::vector<I_cpu> dagFunctionValues;		// Vector containing the values of all functions 

		std::vector<FunctionType> functionTypes = { _OBJECTIVE, _INEQUALITY, _EQUALITY };	// Vector containing the different function types (currently only obj, ineq & eq)

		int numSubintervals;						// Number of subintervals used for the subinterval arithmetic
		I_gpu* dagFunctionValuesOfSubintervals;		// Array on the GPU storing the function values of all subintervals
		int numDagFunctions;						// Number of DAG functions (objective + constraints)

	public:
		subinterval_arithmetic_result(subinterval_arithmetic_memory<I>* newMemory) { init(newMemory); }

		/**
			* @brief Function for updating the results. It constructs a convex hull of the function values over the interval bounds of each subinterval.
			*		This function should be call after each subinterval arithmetic iteration to update the results-object.
			*/
		void update()
		{
			for (auto& functionType : functionTypes) {
				int startFunctionId = startFunctionIds[functionType];

				for (int i = 0; i < numFunctionsPerType[functionType]; i++)
					dagFunctionValues[startFunctionId + i] = get_convex_hull_of_function_values((startFunctionId + i) * numSubintervals);
			}			
		}

#if USE_HARD_CODED_FUNCTION
		void set_obj_value(double objValue)
		{
			dagFunctionValues[0] = I_cpu(objValue);
		}
#endif // USE_HARD_CODED_FUNCTION

		/**
			* @brief Function to get the interval bounds of the id-th dag function. 
			*		The functions are sorted in the following order: 
			*			1) objective
			*			2) inequalities 
			*			3) equalities 
			* 
			* @param[in] id is the index of the dag function
			* return returns the interval bounds of the id-th dag function
			*/
		I_cpu get_bounds(int id) { return dagFunctionValues[id]; }
		std::vector<I_cpu> get_bounds() { return dagFunctionValues; }
		/**
			* @brief Function to get the interval bounds of the id-th objective function (normaly only one objective exists)
			*
			* @param[in] id is the index of the objective function
			* return returns the interval bounds of the id-th objective function
			*/
		I_cpu get_bounds_of_obj(int id) { return dagFunctionValues[startFunctionIds[_OBJECTIVE] + id]; }
		/**
			* @brief Function to get the interval bounds of the id-th inequality constraint
			*
			* @param[in] id is the index of the inequality constraint
			* return returns the interval bounds of the id-th inequality constraint
			*/
		I_cpu get_bounds_of_ineq(int id) { return dagFunctionValues[startFunctionIds[_INEQUALITY] + id]; }
		/**
			* @brief Function to get the interval bounds of the id-th equality constraint
			*
			* @param[in] id is the index of the equality constraint
			* return returns the interval bounds of the id-th equality constraint
			*/
		I_cpu get_bounds_of_eq(int id) { return dagFunctionValues[startFunctionIds[_EQUALITY] + id]; }

	private:
		subinterval_arithmetic_memory<I>* memory;		// Pointer to the memory object storing the pointers for the subinterval arithmetic

		void init(subinterval_arithmetic_memory<I>* newMemory)
		{
			memory = newMemory;	

			numSubintervals = memory->numSubintervals;
			dagFunctionValuesOfSubintervals = memory->dagFunctionValues;
			numDagFunctions = memory->numDagFunctions;
			
			startFunctionIds.push_back(0);
			startFunctionIds.push_back(startFunctionIds.back() + memory->dagInfo.numFunctionIdObj);
			startFunctionIds.push_back(startFunctionIds.back() + memory->dagInfo.numFunctionIdIneq);

			numFunctionsPerType.push_back(memory->dagInfo.numFunctionIdObj);
			numFunctionsPerType.push_back(memory->dagInfo.numFunctionIdIneq);
			numFunctionsPerType.push_back(memory->dagInfo.numFunctionIdEq);

			dagFunctionValues.resize(numDagFunctions);
		}

		/**
			* @brief Function for calculating the convex hull/union of the interval bounds of all subintervals for a DAG function (objective or constraint)
			* 
			* @param[in] functinId is the indice of the function for which the convex hull should be calculated
			* return returns the  convex hull/union of the interval bounds of all subintervalls 
			*/
		I_cpu get_convex_hull_of_function_values(int functionId)
		{
			double smallest_LB = INFINITY;
			double largest_UB = -INFINITY;
			for (int i = 0; i < numSubintervals; i++) {
				I_gpu functionValue = dagFunctionValuesOfSubintervals[functionId + i];
				if (smallest_LB > functionValue.lb)
					smallest_LB = functionValue.lb;

				if (largest_UB < functionValue.ub)
					largest_UB = functionValue.ub;
			}
			return I_cpu(smallest_LB, largest_UB);
		}
	};

	template <typename I>
	class subinterval_arithmetic_memory {
	public:
		I* inputDomain = NULL;				// Array on the CPU storing the current input domain (bounds of each optimization variable)
		I* d_inputDomain = NULL;			// Array on the GPU storing the current input domain (bounds of each optimization variable)
		I* d_subintervals = NULL;			// Array on the GPU storing the subintervals during the subinterval arithmetic

		int dim;							// Number of optimization variables
		int numSubintervals;				// Number of subintervals used in the subinterval arithmetic
		int intervalArithmetic;
		int iteration = 0;					// Counter for the number of iterations - only for printing some statistics

		int numBranchMoreDims;				// The number of dimensions to branch more subintervals
		bool adaptiveBranching;				// Whether to do the adaptive branching 
		double* dim_size = nullptr;			// The array used to store the size of input interval
		bool* branch_more_dims = nullptr;	// The array used to store the dimension to be branched more times
		bool* d_branch_more_dims = nullptr; // The array on GPU used to store the dimension to be branched more times
		size_t bytesBranchMoreDims;

		bool memory_allocated = false;		// Flag whether memory is allocated or not
		bool centered_form_used = false;	// Flag whether centered forms are used or not

		size_t bytesInputDomain;			// Number of bytes for storing the input domain
		size_t size_LB_subintervals;		// Number of bytes for storing the interval bounds of each subinterva

		// ****  Memory for using cuda graph  ***********************************************************************  
		DagConversionInformation dagInfo;
		cudaGraph_t cuDag;
		// cuda graph for centered form
		cudaGraph_t cuCenterDag;
		cudaGraphExec_t cuDagExec;
		std::vector<cuda_ctx> cudaContexts; // The stream which contains the cuda graph

		size_t bytes_dagVarValues;			// Bytes of the array storing the interval bounds of the dag variable values
		I* d_dagVarValues = NULL;			// Array on the GPU storing the interval bounds of the dag variable values
		I* dagVarValues = NULL;				// Array on the CPU storing the interval bounds of the dag variable values

		// ****  Memory for using centered form on GPU  *************************************************************
		cu::tangent<I>* deriv_dagFunctionValues = nullptr; // Array on the GPU storing the derivative as well as bounds for the interval variables
		cu::tangent<I>* deriv_variableValues = nullptr;
		cu::tangent<I>* deriv_dagVarValues = nullptr;
		cu::tangent<double>* centerFunctionValues = nullptr;
		cu::tangent<double>* centerDagVarValues = nullptr;
		cu::tangent<double>* centerValues = nullptr;
		I* constantVars = nullptr;

		// Size of the arraies for centered form.
		size_t size_deriv_dagFunctionValues;	
		size_t size_deriv_variableValues;
		size_t size_deriv_dagVarValues;		  
		size_t size_centerFunctionValues;
		size_t size_centerDagVarValues;
		size_t size_centerValues;
		size_t size_constantVars;

		int numDagFunctions;				// Number of DAG functions (objective + constraints)
		size_t bytesDagFunctionValues;		// Bytes of the array storing the interval bounds of the dag functions
		I* dagFunctionValues = NULL;		// Array on the CPU storing the interval bounds of the dag functions
		I* d_dagFunctionValues = NULL;		// Array on the GPU storing the interval bounds of the dag functions

		subinterval_arithmetic_result<I>* result;	// Result-object managing the dag function values on the CPU 

#if USE_HARD_CODED_FUNCTION
		//Pointers for using hard coded functions
		size_t bytesObjectiveValuesInterval;
		I_gpu* d_objectiveValuesInterval;
		I_gpu* objectiveValuesInterval;

		size_t bytesDerivativeValuesInterval;
		I_gpu* d_derivativeValuesInterval;

		size_t bytesObjectiveValuesDouble;
		double* d_objectiveValuesDouble;

		__device__ I_gpu* get_objectiveValuesInterval_GPU(int id) { return &d_objectiveValuesInterval[id]; }
		__device__ void save_objective_result_GPU(int id, I_gpu objectiveValue) { d_objectiveValuesInterval[id] = objectiveValue; }
		__device__ double* get_objectiveValuesDouble_GPU(int id) { return &d_objectiveValuesDouble[id]; }

		I_gpu* get_objectiveValuesInterval_CPU(int id) { return &objectiveValuesInterval[id]; }

		double get_min_obj_LB()
		{
			double min = INFINITY;

			for (int i = 0; i < numSubintervals; i++)
				if (min > LB_values_CPU[i]) min = LB_values_CPU[i];

			return min;
		}
#endif // USE_HARD_CODED_FUNCTION

		__device__ I* get_input_domain_GPU() { return d_inputDomain; }
		__host__   I* get_input_domain_CPU() { return inputDomain; }

		subinterval_arithmetic_memory() {}
		// modify the constructor to make it suitable for cuda graph
		subinterval_arithmetic_memory(int dim, int numSubintervals, int intervalArithmetic, const std::shared_ptr<DagObj> &dagObj, int numBranchMoreDims, bool adaptiveBranching) {
			// Potential improvement: using shared pointer?
			dagInfo = DagConversionInformation(dagObj->DAG, dagObj);
			init_function_ids_for_dag(dagInfo);

			init(dim, numSubintervals, numBranchMoreDims, adaptiveBranching);
			init_function_ids_and_values();

			if (intervalArithmetic == _CENTERED_FORM)
				init_deriv_memory();


			if (dagInfo.get_num_vars() != 0)
			{								
				int numVars = dagInfo.numDagVars;
				bytes_dagVarValues = numSubintervals * numVars * sizeof(I);				

				if (GPU_FOR_LB) {
					CUDA_CHECK(cudaMalloc(&d_dagVarValues, bytes_dagVarValues));
				}

				result = new subinterval_arithmetic_result<I>(this);

				// Initialize the cuda graph and its stream container
				CUDA_CHECK(cudaGraphCreate(&cuDag, 0));
				CUDA_CHECK(cudaGraphCreate(&cuCenterDag, 0));
				constexpr int n_streams = 1;
				cudaContexts.resize(n_streams); 
				for (auto &[buffer, stream] : cudaContexts) {
					CUDA_CHECK(cudaStreamCreateWithFlags(&stream, cudaStreamNonBlocking));
				}
			}

#if USE_HARD_CODED_FUNCTION
			bytesObjectiveValuesInterval = numSubintervals * sizeof(I_gpu);
			cudaMalloc(&d_objectiveValuesInterval, bytesObjectiveValuesInterval);
			objectiveValuesInterval = (I_gpu*)malloc(bytesObjectiveValuesInterval);

			bytesObjectiveValuesDouble = numSubintervals * sizeof(double);
			cudaMalloc(&d_objectiveValuesDouble, bytesObjectiveValuesDouble);
#endif
		
			memory_allocated = true;		
		}

		~subinterval_arithmetic_memory() {	
			clear();
		}

		/**
			* @brief Function for initializing the memory for the subinterval arithmetic
			* 
			* @param[in] dim is the number of optimization variables
			* @param[in] numSubintervals is the number of subinterval used in the subinterval arithmetic
			*/
		void init(int dim, int numSubintervals, int numBranchMoreDims, bool adaptiveBranching) {
			this->dim = dim;
			this->numSubintervals = numSubintervals;
			this->numBranchMoreDims = numBranchMoreDims;
			this->adaptiveBranching = adaptiveBranching;

			bytesInputDomain = dim * sizeof(I);
			size_LB_subintervals = dim * numSubintervals * sizeof(I);
			
			inputDomain = (I*)malloc(bytesInputDomain);
			
			if (adaptiveBranching){
				bytesBranchMoreDims = dim*sizeof(bool);
				dim_size = (double*)malloc(dim*sizeof(double));
				cudaHostAlloc(&branch_more_dims, bytesBranchMoreDims, cudaHostAllocDefault);
				cudaMalloc(&d_branch_more_dims, bytesBranchMoreDims);
			} 			
			
			// Allocate memory on GPU for GPU lower bounding
			if (GPU_FOR_LB) {
				cudaMalloc(&d_subintervals, size_LB_subintervals);
				cudaMalloc(&d_inputDomain, bytesInputDomain);
			}
		}

		void init_deriv_memory()
		{
			size_deriv_dagFunctionValues = numSubintervals * dim * numDagFunctions * sizeof(cu::tangent<I>);
			size_deriv_variableValues = numSubintervals * dim * dim * sizeof(cu::tangent<I>);
			size_centerFunctionValues = numSubintervals * numDagFunctions * sizeof(cu::tangent<double>);
			size_deriv_dagVarValues = numSubintervals * dim * dagInfo.numDagVars * sizeof(cu::tangent<I>);
			size_centerDagVarValues = numSubintervals * dagInfo.numDagVars * sizeof(cu::tangent<double>);
			size_centerValues = numSubintervals * dim * sizeof(cu::tangent<double>);
			size_constantVars = dagInfo.numDagVars * sizeof(I); // Way too larget for constant variables...

			cudaMalloc(&deriv_dagFunctionValues, size_deriv_dagFunctionValues);
			cudaMalloc(&deriv_variableValues, size_deriv_variableValues);
			cudaMalloc(&centerFunctionValues, size_centerFunctionValues);
			cudaMalloc(&deriv_dagVarValues, size_deriv_dagVarValues);
			cudaMalloc(&centerDagVarValues, size_centerDagVarValues);
			cudaMalloc(&centerValues, size_centerValues);
			constantVars = (I*)malloc(size_constantVars);

			centered_form_used = true;
		}
		
		/**
			* @brief Clearing the allocated memory and cuda resources. Currently not used and not tested.
			*/
		void clear() {
			if (memory_allocated) {
				delete result;
				free(inputDomain);
				free(dagFunctionValues);

				if (adaptiveBranching)
				{
					free(dim_size);
					cudaFreeHost(branch_more_dims);
					cudaFree(d_branch_more_dims);
				}

				if (GPU_FOR_LB) {
					cudaFree(d_subintervals);
					cudaFree(d_inputDomain);
					cudaFree(d_dagVarValues);
					cudaFree(d_dagFunctionValues);
				}

				if (centered_form_used) {
					cudaFree(deriv_dagFunctionValues);
					cudaFree(deriv_variableValues);
					cudaFree(centerFunctionValues);
					cudaFree(deriv_dagVarValues);
					cudaFree(centerDagVarValues);
					cudaFree(centerValues);
					free(constantVars);
				}


				cudaGraphExecDestroy(cuDagExec);
				cudaGraphDestroy(cuCenterDag);
				cudaGraphDestroy(cuDag);
				for (auto [buffer, stream] : cudaContexts) {
					cudaStreamDestroy(stream);
				}
			}
		}

		/**
			* @brief Function for copying the given input domain to GPU
			* 
			* @param[in] newInputDomain is the input domain that is copied to the GPU
			*/
		void copy_inputDomain_to_GPU(I_cpu* newInputDomain) 
		{ 
			for (int i = 0; i < dim; i++)
				// The gpu interval class is replaced by gpu interval struct
				inputDomain[i] = {newInputDomain[i].inf(), newInputDomain[i].sup()};
			CUDA_CHECK(cudaMemcpy(d_inputDomain, inputDomain, bytesInputDomain, cudaMemcpyHostToDevice)); 
		}

		// Function used to find largest branches
		void get_largest_dims_for_adaptive_branching() 
		{
			// Initialize arrays
			for (int i = 0; i < dim; i++) {
				if (i < numBranchMoreDims) 
					branch_more_dims[i] = true;
				else 
					branch_more_dims[i] = false;

				dim_size[i] = inputDomain[i].ub - inputDomain[i].lb;
			}

			// Search for largest dims
			for (int i = numBranchMoreDims; i < dim; i++) {
				for (int j = 0; j < i; j++) {
					if (branch_more_dims[j] && dim_size[i] > dim_size[j]) {
						branch_more_dims[j] = false;
						branch_more_dims[i] = true;
						break;
					}
				}
			}

			if (numBranchMoreDims > 1)
			{
				if (branch_more_dims[1] && dim_size[0] > dim_size[1]){
					branch_more_dims[1] = false;
					branch_more_dims[0] = true;
				}
			}

			CUDA_CHECK(cudaMemcpy(d_branch_more_dims, branch_more_dims, bytesBranchMoreDims, cudaMemcpyHostToDevice)); 
		}			

		/**
			* @brief Function for copying the values of the DAG functions (objective & constraints) from GPU to CPU. 
			*		This function also synchronizes the GPU (waiting for the GPU to finish its calculation)
			*/
		void copy_results_to_CPU() 
		{ 
			CUDA_CHECK(cudaDeviceSynchronize());
			// Update the DAG functions values in the result-object
			result->update();

#if USE_HARD_CODED_FUNCTION
			result->set_obj_value(get_min_obj_LB());
#endif // USE_HARD_CODED_FUNCTION
		}

	private:
		/**
			* @brief Function for initializing the indices of the DAG function (objective & constraints). 
			*		This is necessary for knowing which dag variable corresponse to which function of the optimization problem
			*/
		void init_function_ids_and_values()
		{
			numDagFunctions = (dagInfo.numFunctionIdObj + dagInfo.numFunctionIdIneq + dagInfo.numFunctionIdEq);
			bytesDagFunctionValues = numDagFunctions * numSubintervals * sizeof(I);
			dagFunctionValues = (I*)malloc(bytesDagFunctionValues);

			if (GPU_FOR_LB) {
				CUDA_CHECK(cudaMalloc(&d_dagFunctionValues, bytesDagFunctionValues));
			}
		}
	}; // class subinterval_arithmetic_memory

} // namespace subinterval_arithmetic
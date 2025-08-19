
#pragma once
#include "subinterval_arithmetic_settings.cuh"

//Dag parts on CPU
#include "dag.h"
#include "dagconversion.h"
#include "dagevaluation.h"

//Dag parts on GPU
#include "gpudag.cuh"
#include "dagevaluation.cuh"
#include "derivativeinformation.h"

using namespace SVT_DAG;

namespace subinterval_arithmetic {	

	template <typename I>
	class subinterval_arithmetic_memory;

	/**
		* @brief Class for managing the results of the subinterval arithmetic.
		*		It can be used to access the interval bounds of objective function and constraints.
		*		Therefore, it is necessary to update to result after each iteration.
		*/
	template <typename I>
	class Subinterval_arithmetic_result {

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
		I_gpu* dagFunctionValuesOfSubintervals;		// Array on the CPU storing the function values of all subintervals
		int numDagFunctions;						// Number of DAG functions (objective + constraints)

	public:
		Subinterval_arithmetic_result(subinterval_arithmetic_memory<I>* newMemory) { init(newMemory); }

		/**
			* @brief Function for updating the results. It constructs a convex hull of the function values over the interval bounds of each subinterval.
			*		This function should be call after each subinterval arithmetic iteration to update the results-object.
			*/
		void update()
		{
			for (auto& functionType : functionTypes) {
				int startFunctionId = startFunctionIds[functionType];

				for (int i = 0; i < numFunctionsPerType[functionType]; i++)
					dagFunctionValues[startFunctionId + i] = get_convex_hull_of_function_values(startFunctionId + i);
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
			startFunctionIds.push_back(startFunctionIds.back() + memory->dag.numDagVarIdObj);
			startFunctionIds.push_back(startFunctionIds.back() + memory->dag.numDagVarIdIneq);

			numFunctionsPerType.push_back(memory->dag.numDagVarIdObj);
			numFunctionsPerType.push_back(memory->dag.numDagVarIdIneq);
			numFunctionsPerType.push_back(memory->dag.numDagVarIdEq);

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
				I_gpu functionValue = dagFunctionValuesOfSubintervals[functionId + numDagFunctions * i];
				if (smallest_LB > functionValue.lower())
					smallest_LB = functionValue.lower();

				if (largest_UB < functionValue.upper())
					largest_UB = functionValue.upper();
			}
			return I_cpu(smallest_LB, largest_UB);
		}
	};

	template <typename I>
	class subinterval_arithmetic_memory {
	private: 
		I* inputDomain = NULL;				// Array on the CPU storing the current input domain (bounds of each optimization variable)
		I* d_inputDomain = NULL;			// Array on the GPU storing the current input domain (bounds of each optimization variable)
		I* d_subintervals = NULL;			// Array on the GPU storing the subintervals during the subinterval arithmetic

	public:
		int dim;							// Number of optimization variables
		int numSubintervals;				// Number of subintervals used in the subinterval arithmetic
		int intervalArithmetic;             // Interval Arithmetic strategy used for bounding
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
		size_t size_LB_subintervals;		// Number of bytes for storing the interval bounds of each subinterval


		// ****  Memory for using centered forms  **********************************************************************  
		I* d_f_arr = NULL;					// Array for storing the derivative values if centered forms are used
		double* center_arr = NULL;			// Array for storing the center pointed if centered forms are used
		size_t size_d_f_arr;				// Bytes of the array for the derivative values
		size_t size_center_arr;				// Bytes of the array for the center point
													
		size_t bytesDerivativeInformations;	// Bytes of the array storing all derivative informations of the DAG 
		DerivativeInformation* derivativeInformations_GPU = NULL;	// Array on the GPU for storing the derivative information of the DAG 

		size_t bytes_double_dagVarValues;	// Bytes fo the array storing the values of all dag variables values as doubles
		double* double_dagVarValues_CPU = NULL;	// Array on the CPU for storing the values of all dag variables values as doubles
		double* double_dagVarValues_GPU = NULL;	// Array on the GPU for storing the values of all dag variables values as doubles

		double* LB_values_CPU = NULL;		// Used for serial subinterval arithmetic on GPU
		size_t size_LB_values;				// Number of bytes for storing the LB values of each subinterval

		// ****  Memory for using DAG  **********************************************************************  
		Dag dag;							// DAG object on the CPU
		Dag* d_dag;							// Pointer to DAG object on the GPU

		size_t bytes_dagVarValues;			// Bytes of the array storing the interval bounds of the dag variable values
		I* dagVarValues = NULL;				// Array on the CPU storing the interval bounds of the dag variable values
		I* d_dagVarValues = NULL;			// Array on the GPU storing the interval bounds of the dag variable values

		int numDagFunctions;				// Number of DAG functions (objective + constraints)
		size_t bytesDagFunctionValues;		// Bytes of the array storing the interval bounds of the dag functions
		I* dagFunctionValues = NULL;		// Array on the CPU storing the interval bounds of the dag functions
		I* d_dagFunctionValues = NULL;		// Array on the GPU storing the interval bounds of the dag functions
		int* dagFunctionIds = NULL;			// Array on the CPU storing the dag variable indices for each dag function
		int* d_dagFunctionIds = NULL;		// Array on the GPU storing the dag variable indices for each dag function

		Subinterval_arithmetic_result<I>* result;	// Result-object managing the dag function values on the CPU 

#if USE_HARD_CODED_FUNCTION
		double* LB_values_GPU = NULL;		// Can be delete if Hardcoded-Function-Evaluation is not used any more

		//Pointers for using hard coded functions
		size_t bytesObjectiveValuesInterval;
		I_gpu* d_objectiveValuesInterval;
		I_gpu* objectiveValuesInterval;

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

		__host__   I* get_dagVarValues_CPU(int index) { return &dagVarValues[index * dag.numVars]; }
		__device__ I* get_dagVarValues_GPU(int index) { return &d_dagVarValues[index * dag.numVars]; }
		__host__   double* get_double_dagVarValues_CPU(int index) { return &double_dagVarValues_CPU[index * dag.numVars]; }
		__device__ double* get_double_dagVarValues_GPU(int index) { return &double_dagVarValues_GPU[index * dag.numVars]; }

		__device__ I* get_allocated_memory_for_subinterval(int index) { return &d_subintervals[index * dim]; }
		__device__ I* get_input_domain_GPU() { return d_inputDomain; }
		__host__   I* get_input_domain_CPU() { return inputDomain; }

		__device__ int get_index_of_objective_dagVarValue_GPU() { return d_dagFunctionIds[0]; }

		subinterval_arithmetic_memory(int dim, int numSubintervals, int intervalArithmetic, Dag _dag, int numBranchMoreDims, bool adaptiveBranching) {
			init(dim, intervalArithmetic, numSubintervals, numBranchMoreDims, adaptiveBranching);

			this->dag = _dag;

			if (dag.get_num_vars() != 0)
			{
				// Allocate memory for evaluation of the DAG
				dag.synchronize_var_vectors_and_var_arrays();
				dag.copy_to_gpu();
				int numVars = dag.numVars;

				bytes_dagVarValues = numSubintervals*	numVars * sizeof(I);				

				if (GPU_FOR_LB) {
					CUDA_ERROR_CHECK(cudaMalloc(&d_dagVarValues, bytes_dagVarValues));
				}
				else {
					dagVarValues = (I*)malloc(bytes_dagVarValues);
				}
				
				init_function_ids_and_values();
				result = new Subinterval_arithmetic_result<I>(this);
			}

			// If centered forms are used then additional memory for the derivative values needs to be allocated
			if (intervalArithmetic == _CENTERED_FORM)
				init_derivative(numSubintervals, dag);

#if USE_HARD_CODED_FUNCTION
			bytesObjectiveValuesInterval = numSubintervals * sizeof(I_gpu);
			cudaMalloc(&d_objectiveValuesInterval, bytesObjectiveValuesInterval);
			objectiveValuesInterval = (I_gpu*)malloc(bytesObjectiveValuesInterval);

			bytesObjectiveValuesDouble = numSubintervals * sizeof(double);
			cudaMalloc(&d_objectiveValuesDouble, bytesObjectiveValuesDouble);
#endif

			size_t bytes_dag = sizeof(Dag);
			CUDA_ERROR_CHECK(cudaMalloc(&d_dag, bytes_dag));
			CUDA_ERROR_CHECK(cudaMemcpy(d_dag, &dag, bytes_dag, cudaMemcpyHostToDevice));

			memory_allocated = true;
		}

		~subinterval_arithmetic_memory() {/*printf("The SIA memory destructor is called.");*/}

		/**
			* @brief Function for initializing the memory for the subinterval arithmetic
			* 
			* @param[in] dim is the number of optimization variables
			* @param[in] numSubintervals is the number of subinterval used in the subinterval arithmetic
			*/
		void init(int dim, int intervalArithmetic, int numSubintervals, int numBranchMoreDims, bool adaptiveBranching) {
			this->dim = dim;
			this->numSubintervals = numSubintervals;
			this->intervalArithmetic = intervalArithmetic;
			this->numBranchMoreDims = numBranchMoreDims;
			this->adaptiveBranching = adaptiveBranching;

			bytesInputDomain = dim * sizeof(I);
			size_LB_values = numSubintervals * sizeof(double);
			size_LB_subintervals = dim * numSubintervals * sizeof(I);

			LB_values_CPU = new double[numSubintervals];

#if USE_HARD_CODED_FUNCTION
			cudaMalloc(&LB_values_GPU, size_LB_values);
#endif

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

			// Allocate additional memory for centered form calculations
			if (intervalArithmetic == _CENTERED_FORM) {
				centered_form_used = true;
				// Calculate size for memory allocation
				size_d_f_arr = numSubintervals * dim * sizeof(I);
				size_center_arr = numSubintervals * dim * sizeof(double);

				// Allocate memory on GPU
				if (GPU_FOR_LB) {
					cudaMalloc(&d_f_arr, size_d_f_arr);
					cudaMalloc(&center_arr, size_center_arr);
				}
				// Allocate memory on CPU
				else {
					d_f_arr = (I*)malloc(size_d_f_arr);
					center_arr = (double*)malloc(size_center_arr);
				}
			}
		}
		
		/**
			* @brief Clearing the allocated memory. Currently not used and not tested.
			*/
		void clear() {
			// Call clear() function of dag, not implemented in the destructor of dag in case of multiple frees.
			dag.clear();

			if (memory_allocated) {
				free(inputDomain);
				free(dagFunctionValues);
				free(dagFunctionIds);

				delete[] LB_values_CPU;
				delete result;

#if USE_HARD_CODED_FUNCTION				
				free(objectiveValuesInterval);
				cudaFree(d_objectiveValuesInterval);
				cudaFree(LB_values_GPU);
#endif

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
					cudaFree(d_dag);
					cudaFree(d_dagFunctionIds);
					cudaFree(d_dagFunctionValues);
				}
				else {

					free(dagVarValues);
				}

				if (centered_form_used) {
					if (GPU_FOR_LB) {
						cudaFree(d_f_arr);
						cudaFree(center_arr);
						cudaFree(double_dagVarValues_GPU);
						cudaFree(derivativeInformations_GPU);

						dag.clear_derivatives();
					}
					else {
						free(d_f_arr);
						free(center_arr);
					}
					delete double_dagVarValues_CPU;
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
				inputDomain[i] = I(newInputDomain[i].inf(), newInputDomain[i].sup());
			CUDA_ERROR_CHECK(cudaMemcpy(d_inputDomain, inputDomain, bytesInputDomain, cudaMemcpyHostToDevice)); 
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

				dim_size[i] = inputDomain[i].upper() - inputDomain[i].lower();
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

			CUDA_ERROR_CHECK(cudaMemcpy(d_branch_more_dims, branch_more_dims, bytesBranchMoreDims, cudaMemcpyHostToDevice)); 
		}

		/**
			* @brief Function for copying the values of the DAG functions (objective & constraints) from GPU to CPU. 
			*		This function also synchronizes the GPU (waiting for the GPU to finish its calculation)
			*/
		void copy_results_to_CPU() 
		{ 
			CUDA_ERROR_CHECK(cudaDeviceSynchronize()); 
			CUDA_ERROR_CHECK(cudaMemcpy(dagFunctionValues, d_dagFunctionValues, bytesDagFunctionValues, cudaMemcpyDeviceToHost));

			// Update the DAG functions values in the result-object
			result->update();

#if USE_HARD_CODED_FUNCTION
			result->set_obj_value(get_min_obj_LB());
#endif // USE_HARD_CODED_FUNCTION
		}

	private:
		/**
			* @brief Auxilary function for allocating the memory for evaluating the derivative of the DAG
			* 
			* @param[in] numSubinterval is the number of subintervals used for the subinterval arithmetic
			* @param[in] dag ist the DAG used for the subinterval arithmetic
			*/
		void init_derivative(int numSubintervals, Dag& dag)
		{
			bytesDerivativeInformations = numSubintervals * dag.numVars * sizeof(DerivativeInformation);
			if (GPU_FOR_LB)
				derivativeInformations_GPU = get_derivativeInformation_vector_from_dag(dag, numSubintervals);

			if (GPU_FOR_LB) {
				bytes_double_dagVarValues = numSubintervals * dag.numVars * sizeof(double);
				cudaMalloc(&double_dagVarValues_GPU, bytes_double_dagVarValues);
			}
			double_dagVarValues_CPU = new double[numSubintervals * dag.numVars];
		}

		/**
			* @brief Function for initializing the indices of the DAG function (objective & constraints). 
			*		This is necessary for knowing which dag variable corresponse to which function of the optimization problem
			*/
		void init_function_ids_and_values()
		{
			numDagFunctions = (dag.numDagVarIdObj + dag.numDagVarIdIneq + dag.numDagVarIdEq);
			bytesDagFunctionValues = numDagFunctions * numSubintervals * sizeof(I);
			int bytesDagFunctionIds = numDagFunctions * sizeof(int);			

			dagFunctionValues = (I*)malloc(bytesDagFunctionValues);
			dagFunctionIds = (int*)malloc(bytesDagFunctionIds);

			if (GPU_FOR_LB) {
				CUDA_ERROR_CHECK(cudaMalloc(&d_dagFunctionIds, bytesDagFunctionIds));
				CUDA_ERROR_CHECK(cudaMalloc(&d_dagFunctionValues, bytesDagFunctionValues));
			}

			// Collect all dag function ids on the CPU
			int arrayPosition = 0;
			add_functionIds_to_dagFunctionIds(dag.dagVarIdObj, arrayPosition);
			add_functionIds_to_dagFunctionIds(dag.dagVarIdIneq, arrayPosition);
			add_functionIds_to_dagFunctionIds(dag.dagVarIdEq, arrayPosition);

			// Copy dag function ids to GPU
			CUDA_ERROR_CHECK(cudaMemcpy(d_dagFunctionIds, dagFunctionIds, bytesDagFunctionIds, cudaMemcpyHostToDevice));
		}

		/**
			* @brief Function for adding a given vector of function indices to the DAG function indices.
			* 
			* @param[in] functionIds are the function indices that should be added to the DAG
			* @param[in] currentPosition is the start position where the new function indices are added to the DAG function indices
			*/
		void add_functionIds_to_dagFunctionIds(std::vector<int> functionIds, int& currentPosition)
		{   
			for (int i = 0; i < functionIds.size(); i++) {
				dagFunctionIds[currentPosition + i] = functionIds[i];
			}
			currentPosition += functionIds.size();
		}

	}; // class subinterval_arithmetic_memory

} // namespace subinterval_arithmetic
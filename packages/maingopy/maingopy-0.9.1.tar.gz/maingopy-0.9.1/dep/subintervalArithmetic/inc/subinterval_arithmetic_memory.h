#pragma once
#include "subinterval_arithmetic_settings.h"

//Dag parts on CPU
#include "dag.h"
#include "dagconversion.h"
#include "dagevaluation.h"
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
		I_cpu* dagFunctionValuesOfSubintervals;		// Array on the CPU storing the function values of all subintervals
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
				I_cpu functionValue = dagFunctionValuesOfSubintervals[functionId + numDagFunctions * i];
				if (smallest_LB > functionValue.inf())
					smallest_LB = functionValue.inf();

				if (largest_UB < functionValue.sup())
					largest_UB = functionValue.sup();
			}
			return I_cpu(smallest_LB, largest_UB);
		}
	};

	template <typename I>
	class subinterval_arithmetic_memory {
	private: 
		I* _inputDomain = NULL;				// Array on the CPU storing the current input domain (bounds of each optimization variable)
		I* _subintervals = NULL;				// Array on the GPU storing the subintervals during the subinterval arithmetic

	public:
		int dim;							// Number of optimization variables
		int numSubintervals;				// Number of subintervals used in the subinterval arithmetic
		int intervalArithmetic;             // Interval Arithmetic strategy used for bounding
		int iteration = 0;					// Counter for the number of iterations - only for printing some statistics

		int numBranchMoreDims;				// The number of dimensions to branch more subintervals
		bool adaptiveBranching;				// Whether to do the adaptive branching 
		bool* largest_dims = nullptr;
		double* dim_size = nullptr;			// The array used to store the size of input interval
		bool* branch_more_dims = nullptr;	// The array used to store the dimension to be branched more times

		bool memory_allocated = false;		// Flag whether memory is allocated or not
		bool centered_form_used = false;	// Flag whether centered forms are used or not

		// ****  Memory for using centered forms  **********************************************************************  
		I* d_f_arr = NULL;					// Array for storing the derivative values if centered forms are used
		double* center_arr = NULL;			// Array for storing the center pointed if centered forms are used
		DerivativeInformation* derivativeInformations = NULL;	// Array on the CPU for storing the derivative information of the DAG 
		double* double_dagVarValues = NULL;	// Array on the CPU for storing the values of all dag variables values as doubles
		double* LB_values = NULL;		// Used for serial subinterval arithmetic on GPU

		// ****  Memory for using DAG  **********************************************************************  
		Dag dag;							// DAG object on the CPU
		I* dagVarValues = NULL;				// Array on the CPU storing the interval bounds of the dag variable values
		int numDagFunctions;				// Number of DAG functions (objective + constraints)
		I* dagFunctionValues = NULL;		// Array on the CPU storing the interval bounds of the dag functions
		int* dagFunctionIds = NULL;			// Array on the CPU storing the dag variable indices for each dag function

		Subinterval_arithmetic_result<I>* result;	// Result-object managing the dag function values on the CPU 

		I* get_dagVarValues(int index) { return &dagVarValues[index * dag.numVars]; }
		double* get_double_dagVarValues(int index) { return &double_dagVarValues[index * dag.numVars]; }

		I* get_allocated_memory_for_subinterval(int index) { return &_subintervals[index * dim]; }
		I* get_input_domain() { return _inputDomain; }
		int get_index_of_objective_dagVarValue() { return dagFunctionIds[0]; }

		// Constructors
		subinterval_arithmetic_memory() {}
		subinterval_arithmetic_memory(int dim, int numSubintervals, int intervalArithmetic, Dag dag, int numBranchMoreDims, bool adaptiveBranching) {
			init(dim, intervalArithmetic, numSubintervals, numBranchMoreDims, adaptiveBranching);

			this->dag = dag;

			if (dag.get_num_vars() != 0)
			{
				// Allocate memory for evaluation of the DAG
				dag.synchronize_var_vectors_and_var_arrays();
				int numVars = dag.numVars;
				dagVarValues = new I[numSubintervals * numVars];
				
				init_function_ids_and_values();
				result = new Subinterval_arithmetic_result<I>(this);
			}

			// If centered forms are used then additional memory for the derivative values needs to be allocated
			if (intervalArithmetic == _CENTERED_FORM)
				init_derivative(numSubintervals, dag);

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

			_subintervals = new I[dim * numSubintervals];
			LB_values = new double[numSubintervals];
			largest_dims = new bool[dim];	// TODO: Change to implementation without arrays
			dim_size = new double[dim];

			_inputDomain = new I[dim];

			if (adaptiveBranching){
				branch_more_dims = new bool[dim];
			} 

			// Allocate additional memory for centered form calculations
			if (intervalArithmetic == _CENTERED_FORM) {
				centered_form_used = true;
				// Calculate size for memory allocation
				d_f_arr = new I[numSubintervals * dim];
				center_arr = new double[numSubintervals * dim];
			}
		}

		void copy_domain_into_memory(I_cpu* newInputDomain){
			for (int i = 0; i < dim; i++)
			_inputDomain[i] = I(newInputDomain[i].inf(), newInputDomain[i].sup());
		}
		
		/**
			* @brief Clearing the allocated memory. Currently not used and not tested.
			*/
		void clear() {
			// Call clear() function of dag, not implemented in the destructor of dag in case of multiple frees.
			dag.clear();

			if (memory_allocated) {
				delete[] _inputDomain;
				delete[] dagFunctionValues;
				delete[] dagFunctionIds;

				delete[] LB_values;
				delete result;
				delete[] largest_dims;
				delete[] dim_size;

				if (adaptiveBranching)
				{
					delete[] branch_more_dims;
				}

				delete[] dagVarValues;

				if (centered_form_used) {
					delete[] derivativeInformations;
					delete[] d_f_arr;
					delete[] center_arr;
					delete[] double_dagVarValues;
					dag.clear_derivatives();
				}
			}
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

				dim_size[i] = _inputDomain[i].sup() - _inputDomain[i].inf();
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
		}

		/**
			* @brief Function for copying the values of the DAG functions (objective & constraints) from GPU to CPU. 
			*		This function also synchronizes the GPU (waiting for the GPU to finish its calculation)
			*/
		void update_results() 
		{ 
			// Update the DAG functions values in the result-object
			result->update();
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
			derivativeInformations = get_derivativeInformation_vector_from_dag(dag, numSubintervals);
			double_dagVarValues = new double[numSubintervals * dag.numVars];
		}

		/**
			* @brief Function for initializing the indices of the DAG function (objective & constraints). 
			*		This is necessary for knowing which dag variable corresponse to which function of the optimization problem
			*/
		void init_function_ids_and_values()
		{
			numDagFunctions = (dag.numDagVarIdObj + dag.numDagVarIdIneq + dag.numDagVarIdEq);

			dagFunctionValues = new I[numDagFunctions * numSubintervals];
			dagFunctionIds = new int[numDagFunctions];

			// Collect all dag function ids on the CPU
			int arrayPosition = 0;
			add_functionIds_to_dagFunctionIds(dag.dagVarIdObj, arrayPosition);
			add_functionIds_to_dagFunctionIds(dag.dagVarIdIneq, arrayPosition);
			add_functionIds_to_dagFunctionIds(dag.dagVarIdEq, arrayPosition);
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
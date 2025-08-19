#ifndef SUBINTERVAL_ARITHMETIC_CUH_
#define SUBINTERVAL_ARTIHMETIC_CUH_

#pragma once
#include "subinterval_arithmetic_settings.h"
#include "subinterval_arithmetic_memory.h"

#define CPU_INTERVAL_NaN -6.2774385622041925e+66

namespace subinterval_arithmetic {

	// Getter function for interval bounds
	inline double get_interval_LB(const I_cpu& interval) { return interval.inf(); }
	inline double get_interval_UB(const I_cpu& interval) { return interval.sup(); }

	// ************************** Help functions ************************
	
	/**
		* @brief Auxiliary function for calculating the minimum value of a array
		* 
		* @param[in] arr is the array with the values
		* @param[in] dim is the number of values in the array
		* @return returns the smallest value of the array
		*/
	template <typename T> 
    T get_arr_min(T* arr, const int& dim) {
		T min = INFINITY;
		for (int i = 0; i < dim; i++)
			if (arr[i] < min) min = arr[i];
		return min;
	}

	/**
		* @brief Auxiliary function for getting the id-th subinterval of a given interval.
		*			e.g. get_subinterval(0, 3, [0, 3]) will return the interval [0, 1]
		* 
		* @param[in] id determines which subinterval should be returned
		* @param[in] branch_fac determines in how many subintervals the interval should be splitted
		* @param[in] interval is the interval from which the subinterval is created
		* @return returns the id-th subinterval of the give interval
		*/
	template <typename I> 
    I get_subinterval(const int& id, const int& branch_fac, const I& interval) {
		double LB, UB, delta, new_LB, new_UB;
		LB = subinterval_arithmetic::get_interval_LB(interval);
		UB = subinterval_arithmetic::get_interval_UB(interval);
		delta = (UB - LB) / branch_fac;

		// Calc new lower bound
		new_LB = LB + delta * id;

		// Use original upper bound for last subinterval
		if (id == branch_fac) return I(new_LB, UB);

		// Calc new upper bound
		new_UB = new_LB + delta;

		// return subinterval
		return I(new_LB, new_UB);
	}

	// The core for going over every subinterval, only moving on one dimension once a time 
	inline	int get_exp_index(const int& index, const int& a, const int& i) {
		int temp = index / pow((float)a, (float)i);	// TODO: Check performance of pow with typecast to float vs own integer pow implemenation
		return temp % a;
	}

	/**
		* @brief Auxiliary function for determining the largest dimensions. (Search for multiple dimensions)
		* 
		* @param[in] interval is the input domain for which the largest dimension is to be determined
		* @param[in] largestDims stores the result. largest_dim[i] is true, if i is one of the largest dimensions. Otherwise it is false
		* @param[in] dim is the number of input dimensions
		* @param[in] branchDim is the number of largest dimensions to be determined 
		*/
	// Replaced by the one in SIA memory class
	template<typename I>
    void get_largest_dims(I* interval, double* dim_size, bool* largestDims, const int& dim, const int& branchDim) {
		// Initialize arrays
		for (int i = 0; i < dim; i++) {
			if (i < branchDim) largestDims[i] = true;
			else largestDims[i] = false;

			dim_size[i] = subinterval_arithmetic::get_interval_UB(interval[i]) - subinterval_arithmetic::get_interval_LB(interval[i]);
		}

		// Search for largest dims
		for (int i = branchDim; i < dim; i++) {
			for (int j = 0; j < i; j++) {
				if (largestDims[j] == true && dim_size[i] > dim_size[j]) {
					largestDims[j] = false;
					largestDims[i] = true;
					break;
				}
			}
		}
	}

	/**
		* @brief Auxiliary function for determining the largest dimension. (Search for one dimension)
		* 
		* @param[in] inputDomain is the input domain for which the largest dimension is to be determined
		* @param[in] dim is the number of input dimensions
		* return returns the index of the smallest dimension
		*/ 
	template <typename I> 
    int get_largest_dim(I* inputDomain, const int& dim) {
		int largestDim = -1;
		double largestWidth = 0;
		for (int i = 0; i < dim; i++) {
			double width_i = subinterval_arithmetic::get_interval_UB(inputDomain[i]) - subinterval_arithmetic::get_interval_LB(inputDomain[i]);
			if (width_i > largestWidth) {
				largestWidth = width_i;
				largestDim = i;
			}
		}
		return largestDim;
	}	

	// ************************** Branching strategies ************************

	/**
		* @brief Function for branching a given interval/input domain into a subinterval/subdomain by branching each dimension uniformaly
		*
		* @param[in] id is the thread id. This is needed for using right the GPU memory for this thread
		* @param[in] interval is a pointer to the input domain to be branched
		* @param[in] subinterval is a pointer to the allocated memory for the subdomain
		* @param[in] branch_fac
		* @param[in] dim is the number of dimensions of the input domain
		* @param[in] numBranchDims
		* @param[in] startID
		*/
	template <typename I>
	void branch_equaly_per_dim(const int& id, I* interval, I* subinterval, const int& branch_fac, const int& dim, const int& num_branch_dims, int startID = 0)
	{
		// Branch equaly on all dimensions
		for (int i = 0; i < dim; i++) {
			int index = subinterval_arithmetic::get_exp_index(id, branch_fac, i);
			subinterval[i + startID] = subinterval_arithmetic::get_subinterval(index, branch_fac, interval[i]);
		}
	}

	/**
		* @brief Function for branching a given interval/input domain into a subinterval/subdomain by uniformly branching at most dimensions as possible.
		*			If the input dimension is too high, not each dimension can be branched in each iteration because of the limited number of subintervals. 
		*			Then the largest dimensions are branched MIN_branching_per_dim times
		*
		* @param[in] id is the thread id. This is needed for using right the GPU memory for this thread
		* @param[in] interval is a pointer to the input domain to be branched
		* @param[in] subinterval is a pointer to the allocated memory for the subdomain
		* @param[in] branch_fac
		* @param[in] dim is the number of dimensions of the input domain
		* @param[in] numBranchDims
		* @param[in] startID
		*/
	template <typename I>
	void branch_as_many_dims_as_possible(const int& id, I* interval, I* subinterval, const int& branch_fac, const int& dim, const int& num_branch_dims, double* dim_size, bool* largest_dims, int startID = 0)
	{
		subinterval_arithmetic::get_largest_dims(interval, dim_size, largest_dims, dim, num_branch_dims);
		int iter_branch = 0;
		for (int i = 0; i < dim; i++) {
			if (largest_dims[i]) {
				int index = subinterval_arithmetic::get_exp_index(id, branch_fac, iter_branch);
				subinterval[i + startID] = subinterval_arithmetic::get_subinterval(index, branch_fac, interval[i]);
				iter_branch++;
			}
			else {
				subinterval[i + startID] = interval[i];
			}
		}
	}

// Update version 2, only do adaptive branching when pow(branch_fac, dim) < num_subintervals
	template <typename I> 
    void branch_adaptively(const int& id, I* interval, I* subinterval, const int& branch_fac, const int& dim, const int& num_branch_more_dims, bool* branch_more_dims)
	{
		int outer_id = id/pow(branch_fac + 1, num_branch_more_dims);
		int inner_iter_index = 0;	
		int outer_iter_index = 0;
		for (int i = 0; i < dim; i++) {
			if (branch_more_dims[i]){
				// Variable created within if statement could only impact within its own block, can not be used outside
				int inner_interval_index = subinterval_arithmetic::get_exp_index(id, branch_fac + 1, inner_iter_index);
				subinterval[i] = subinterval_arithmetic::get_subinterval(inner_interval_index, branch_fac + 1, interval[i]);
				inner_iter_index ++;
			} 
			else {
				int outer_interval_index = subinterval_arithmetic::get_exp_index(outer_id, branch_fac, outer_iter_index);
				subinterval[i] = subinterval_arithmetic::get_subinterval(outer_interval_index, branch_fac, interval[i]);
				outer_iter_index ++;
			}
		}	
	}

	/**
		* @brief Function for branching a given interval/input domain into a subinterval/subdomain by branching only on the largest dimension
		*
		* @param[in] id is the thread id. This is needed for using right the GPU memory for this thread
		* @param[in] interval is a pointer to the input domain to be branched
		* @param[in] subinterval is a pointer to the allocated memory for the subdomain
		* @param[in] branch_fac
		* @param[in] dim is the number of dimensions of the input domain
		* @param[in] numBranchDims
		* @param[in] startID
		*/
	template <typename I>
	void branch_on_largest_dim(const int& id, I* interval, I* subinterval, const int& branch_fac, const int& dim, int startID = 0)
	{
		int largest_dim = subinterval_arithmetic::get_largest_dim(interval, dim);
		for (int i = 0; i < dim; i++) {
			if (i == largest_dim) {
				subinterval[i + startID] = subinterval_arithmetic::get_subinterval(id, branch_fac, interval[i]);
			}
			else {
				subinterval[i + startID] = interval[i];
			}
		}
	}
	
	/**
		* @brief Function for branching a given interval/input domain into a subinterval/subdomain based on the selected subinterval branching strategy
		* 
		* @param[in] id is the thread id. This is needed for using right the GPU memory for this thread
		* @param[in] interval is a pointer to the input domain to be branched
		* @param[in] subinterval is a pointer to the allocated memory for the subdomain
		* @param[in] branch_fac
		* @param[in] dim is the number of dimensions of the input domain
		* @param[in] numBranchDims 
		* @param[in] startID
		*/
	template <typename I>
	inline void branch_interval_into_subinterval(const int& id, I* interval, I* subinterval, const int& branch_fac, const int& dim, const int& num_branch_dims, const int& branching_strategy, 
													const int& num_branch_more_dims, const bool& adaptive_branching, double* dim_size, bool* largest_dims, bool* branch_more_dims, int startID = 0) 
	{
		if (branch_fac == 1) {
			// Do not branch & just copy interval to subinterval
			for (int i = 0; i < dim; i++)
				subinterval[i + startID] = interval[i];
		}
		else {
			if (branching_strategy == _EQUALY_PER_DIM) {
				if (adaptive_branching){
					// branch_adaptively(id, interval, subinterval, branch_fac, dim, num_branch_dims, num_branch_more_dims);
					branch_adaptively(id, interval, subinterval, branch_fac, dim, num_branch_more_dims, branch_more_dims);
				}
				else if (num_branch_dims == dim) {
					branch_equaly_per_dim(id, interval, subinterval, branch_fac, dim, num_branch_dims, startID);
				}				
				else {
					branch_as_many_dims_as_possible(id, interval, subinterval, branch_fac, dim, num_branch_dims, dim_size, largest_dims, startID);
				}
			}
			else if (branching_strategy == _ON_LARGEST_DIM) {
				branch_on_largest_dim(id, interval, subinterval, branch_fac, dim, startID);
			}
		}
	}


	// ************************** Natural Interval Extension and Centered form **************************

	/**
		* @brief Auxiliary function for evaluating the dag on the GPU
		* 
		* @param[in] memory stores all pointers to the allocated GPU memory for the DAG evaluation
		* @param[in] subinterval is the input domain for the dag evaluation
		* @param[in] id is the thread id. This is needed for using right the GPU memory for this thread
		* return returns the interval bounds of the last dag variable. For a problem without constraints this is the objective function
		*/
	// For future use in MPI/OpenMP
	template <typename I> 
	inline void calc_natural_interval_extensions(subinterval_arithmetic_memory<I> &memory, I* subinterval, const int& id)
	{
		// Evaluate DAG at give subinterval
		I* dagVarValues = memory.get_dagVarValues(id);
		evaluate(memory.dag, subinterval, dagVarValues);		

		// Save bounds of the DAG functions (objective & constraints)
		int startPosition = id * memory.numDagFunctions;
		for (int i = 0; i < memory.numDagFunctions; i++) {
			memory.dagFunctionValues[startPosition + i] = dagVarValues[memory.dagFunctionIds[i]];
		}

		// Return last dagVarValue - without constraints this is the value of the objective function - return value is not used for regular implementation
		// return dagVarValues[memory.dag.numVars - 1];
	}

    /**
        * @brief Function for calculating the centered form of the given subinterval
        * 
        * @param[in] subinterval is the domain for which the centered form is calculated
        * @param[in] d_f is a pointer to the allocated memory for the derivative values 
        * @param[in] center is a pointer to the allocated memory for the center point 
        * @param[in] dim is the dimension of the given domain
        * @param[in] memory stores all pointers to the allocated GPU memory for the centered form calucation
        * @param[in] id is the thread id. This is needed for using right the GPU memory for this thread
        * return returns the interval bounds from the centered form calculation of the last DAG variable 
        */
	// For future use in MPI or OpenMP
    template <typename I>
    // inline I calc_centered_form(subinterval_arithmetic_memory<I>& memory, I* subinterval, int id, int centerStrategy)
	inline void calc_centered_form(subinterval_arithmetic_memory<I>& memory, I* subinterval, const int& id, const int& centerStrategy)
	{	
		int dim = memory.dim;
		I* d_f = &memory.d_f_arr[id * dim];
		double* center = &memory.center_arr[id * dim];

		I res;
		double f_c = 0;
		bool center_defined = true;

        // Calculate derivative
        DerivativeInformation* derivativeInformations = &memory.derivativeInformations[memory.dag.numVars * id];
        evaluate_derivative(memory.dag, subinterval, derivativeInformations);

        for (int i = 0; i < dim; i++)
            d_f[i] = derivativeInformations[memory.dagFunctionIds[0]].derivativeValue_I_cpu[i];

        // Calculate optimal center point
        for (int i = 0; i < dim; i++) {
            double LB_x_i = subinterval_arithmetic::get_interval_LB(subinterval[i]);
            double UB_x_i = subinterval_arithmetic::get_interval_UB(subinterval[i]);

#if USE_CORNER_POINT_AS_CENTER
            center[i] = LB_x_i;
#else
            if (centerStrategy == _ADVANCED){
                double LB_d_f_i = subinterval_arithmetic::get_interval_LB(d_f[i]);
                double UB_d_f_i = subinterval_arithmetic::get_interval_UB(d_f[i]);
                if (UB_d_f_i <= 0 && UB_d_f_i != CPU_INTERVAL_NaN)
                    center[i] = UB_x_i;
                else if (LB_d_f_i >= 0)
                    center[i] = LB_x_i;
                else if (LB_d_f_i != CPU_INTERVAL_NaN && UB_d_f_i != CPU_INTERVAL_NaN)
                    center[i] = (LB_d_f_i * LB_x_i - UB_d_f_i * UB_x_i) / (LB_d_f_i - UB_d_f_i);
                else
                    center_defined = false;
            }
            else {					
                center[i] = (UB_x_i + LB_x_i) / 2;
                if (isnan(center[i]))
                    center_defined = false;	
            }
#endif			
		}
			//printf(" %4d-th Center = [%f, %f]\n", id, center[0], center[1]);


		if (center_defined) {
            // Calculate centered optimal centered form		F(X,c) = f(c) + L(X,c) * (X - c)	with	L(X,c) = d_f(X)
            double* double_dagVarValues = memory.get_double_dagVarValues(id);
            // Evaluate DAG at center point
            evaluate(memory.dag, center, double_dagVarValues);

            // Calculate centered form for all DAG functions (objective & constraints)
            int startPosition = id * memory.numDagFunctions;
            for (int function = 0; function < memory.numDagFunctions; function++) {

                int functionId = memory.dagFunctionIds[function];
                f_c = double_dagVarValues[functionId];
                res = f_c;

                for (int i = 0; i < dim; i++) {
                    d_f[i] = derivativeInformations[functionId].derivativeValue_I_cpu[i];
                    res = res + d_f[i] * (subinterval[i] - center[i]);
                }		
                
                memory.dagFunctionValues[startPosition + function] = res;
            }
		}
		else {
            // If center point is not defined: fall back to natural interval extensions - results are already calculated during the derivative calculation
            int startPosition = id * memory.numDagFunctions;
            for (int function = 0; function < memory.numDagFunctions; function++) {

                int functionId = memory.dagFunctionIds[function];
                I_cpu functionValue = memory.derivativeInformations[functionId].functionValue_I_cpu[0];

                memory.dagFunctionValues[startPosition + function] = functionValue;
            }
		}
		// return res;
	}

	
	// ************************** Calculation of lower bounds for subintervals ************************
	/**
		* @brief Serial version of the GPU kernel for parallel calculation of multiple subinterval lower bounds.
		*			First, the subinterval of the original input domain is calulated according to the thread id
		*			Then, the interval bounds for the subinterval are calulated.
		*			Lastly, the final lower bound of the subinterval is stored in the memory object
		*
		* @param[in] memory stores all pointers to the allocated GPU memory for the subinterval arithmetic
		* @param[in] settings stores all settings and necessary information for the subinterval arithmetic
		*/
	// Serial imlementation of subinterval arithmetic
	template <typename I>
	void calc_LBs_serial(subinterval_arithmetic_memory<I>& memory, subinterval_arithmetic_settings& settings) {
		I* interval = memory.get_input_domain();
		I* subinterval = nullptr;

		int branch_fac = settings.get_branch_fac_per_dim();
		int dim = settings.get_dim();
		int num_branch_dims = settings.get_num_branch_dims();

		int branching_strategy = settings.get_branching_strategy();
		int num_branch_more_dims = settings.get_num_branch_more_dims();
		bool adaptive_branching = settings.get_adaptive_branching_flag();
		if (branching_strategy == _ON_LARGEST_DIM)
			branch_fac = settings.get_num_subintervals();

		double* dim_size = memory.dim_size;		
		bool* largest_dims = memory.largest_dims;
		bool* branch_more_dims = memory.branch_more_dims;
		
		for (int i = 0; i < memory.numSubintervals; i ++){
			subinterval = memory.get_allocated_memory_for_subinterval(i);
			branch_interval_into_subinterval(i, interval, subinterval, branch_fac, dim, num_branch_dims, branching_strategy, 
												num_branch_more_dims, adaptive_branching, dim_size, largest_dims, branch_more_dims);

			// Evaluate subinterval
			if (settings.get_interval_arithmetic() == _NATURAL_INTERVAL_EXTENSION) {
				calc_natural_interval_extensions(memory, subinterval, i);
			}
			if (settings.get_interval_arithmetic() == _CENTERED_FORM) {
				int centerStrategy = settings.get_center_strategy();
				calc_centered_form(memory, subinterval, i, centerStrategy);
			}
		}
		// memory.iteration++;
	}

	// ************************** Main function for calculating LB with subintervals ************************
	/**
		* @brief Function for starting the subinterval arithmetic for the current input domain in the memory object
		* 
		* @param[in] memory stores all pointers to the allocated GPU memory for the subinterval arithmetic
		* @param[in] settings stores all settings and necessary information for the subinterval arithmetic
		*/
	template <typename I> 
	void perform_subinterval_arithmetic_seriel(subinterval_arithmetic_memory<I>& memory, subinterval_arithmetic_settings& settings)
	{
		calc_LBs_serial(memory, settings);
		memory.iteration++;
	}

} // namespace subinterval_arithmetic
#endif // SUBINTERVAL_ARTIHMETIC_CUH_
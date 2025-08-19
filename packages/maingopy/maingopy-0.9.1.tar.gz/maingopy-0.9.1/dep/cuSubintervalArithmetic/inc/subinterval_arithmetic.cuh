#pragma once
#include "subinterval_arithmetic_settings.cuh"
#include "subinterval_arithmetic_memory.cuh"
#define CPU_INTERVAL_NaN -6.2774385622041925e+66

namespace SIA{

    // Helper functions for branching subintervals on GPU	
    __device__ inline double get_interval_LB(I_gpu interval) { return interval.lb; }
    __device__ inline double get_interval_UB(I_gpu interval) { return interval.ub; }   

	template <typename I>
	__device__
		int get_largest_dim(I* inputDomain, int dim) {
		int largestDim = -1;
		double largestWidth = 0;
		for (int i = 0; i < dim; i++) {
			double width_i = SIA::get_interval_UB(inputDomain[i]) - SIA::get_interval_LB(inputDomain[i]);
			if (width_i > largestWidth) {
				largestWidth = width_i;
				largestDim = i;
			}
		}
		return largestDim;
	}	 

    template<typename I>
	__device__
	void get_largest_dims(I* interval, bool* largestDims, int dim, int branchDim) 
    {
		double* dim_size = new double[dim];

		// Initialize arrays
		for (int i = 0; i < dim; i++) {
			if (i < branchDim) largestDims[i] = true;
			else largestDims[i] = false;

			dim_size[i] = SIA::get_interval_UB(interval[i]) - SIA::get_interval_LB(interval[i]);
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

		delete[] dim_size;
	}

    // Get the index of which subinterval should be chosen based on the id of thread.
	__device__
	inline	int get_exp_index(int index, int a, int i) 
    {
		int temp = index / pow((float)a, (float)i);	// TODO: Check performance of pow with typecast to float vs own integer pow implemenation
		return temp % a;
	}

    // Get the corresponding subinterval based on the given id
	template <typename I>
	__device__
    I get_subinterval(int id, int branch_fac, I interval) 
    {
		double LB, UB, delta, new_LB, new_UB;
		LB = SIA::get_interval_LB(interval);
		UB = SIA::get_interval_UB(interval);
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

    // Branch equaly on each dimension of the optimization variable(s)
	template <typename I>
	__device__
	void branch_equaly_per_dim(int id, I* interval, I* subinterval, int numSubintervals, int branch_fac, int dim, int num_branch_dims)
	//, int startID = 0
	{
		// Branch equaly on all dimensions
		for (int i = 0; i < dim; i++) {
			int index = SIA::get_exp_index(id, branch_fac, i);
			subinterval[numSubintervals * i + id] = SIA::get_subinterval(index, branch_fac, interval[i]);
			// + startID
		}
	}

    // Branch as many dimensions as possible
	template <typename I>
	__device__
	void branch_as_many_dims_as_possible(int id, I* interval, I* subinterval, int numSubintervals, int branch_fac, int dim, int num_branch_dims)
	//, int startID = 0
	{
		bool* largest_dims = new bool[dim];	// TODO: Change to implementation without arrays
		SIA::get_largest_dims(interval, largest_dims, dim, num_branch_dims);
		int iter_branch = 0;
		for (int i = 0; i < dim; i++) {
			if (largest_dims[i]) {
				int index = SIA::get_exp_index(id, branch_fac, iter_branch);
				subinterval[numSubintervals * i + id] = SIA::get_subinterval(index, branch_fac, interval[i]);
				// + startID
				iter_branch++;
			}
			else {
				subinterval[numSubintervals * i + id] = interval[i];
				// + startID
			}
		}
		delete[] largest_dims;
	}

	// Update version 2, only do adaptive branching when pow(branch_fac, dim) < num_subintervals
	template <typename I>
	__device__
	void branch_adaptively(int id, I* interval, I* subinterval, int num_subintervals, int branch_fac, int dim, int num_branch_more_dims, bool* branch_more_dims)
	{
		int outer_id = id/pow(branch_fac + 1, num_branch_more_dims);
		int inner_iter_index = 0;	
		int outer_iter_index = 0;
		for (int i = 0; i < dim; i++) {
			if (branch_more_dims[i]){
				int inner_interval_index = SIA::get_exp_index(id, branch_fac + 1, inner_iter_index);
				subinterval[num_subintervals * i + id] = SIA::get_subinterval(inner_interval_index, branch_fac + 1, interval[i]);
				inner_iter_index ++;
			} 
			else {
				int outer_interval_index = SIA::get_exp_index(outer_id, branch_fac, outer_iter_index);
				subinterval[num_subintervals * i + id] = SIA::get_subinterval(outer_interval_index, branch_fac, interval[i]);
				outer_iter_index ++;
			}
		}	
	}

    // Branch on the largest branch (with the largest width), the # of subintervals on this dimension is equal to the # of all subintervals needed 
	template <typename I>
	__device__
	void branch_on_largest_dim(int id, I* interval, I* subinterval, int numSubintervals, int dim)
	//, int startID = 0
	{
		// Specify the branch_fac as the number of subintervals
        int largest_dim = SIA::get_largest_dim(interval, dim);
		for (int i = 0; i < dim; i++) {
			if (i == largest_dim) {
				subinterval[numSubintervals * i + id] = SIA::get_subinterval(id, numSubintervals, interval[i]);
				// + startID
			}
			else {
				subinterval[numSubintervals * i + id] = interval[i];
				// + startID
			}
		}
	}

    // Kernel function for branching, added as a kernel of the cuda graph
	template <typename I>
	__global__ 
	void branch_interval_into_subinterval(I* interval, I* subinterval, int num_subintervals, int branch_fac, int dim, int num_branch_dims, int branching_strategy, 
											int num_branch_more_dims, bool adaptive_branching, bool* branch_more_dims) 
	// , int startID = 0
    {
		int id = threadIdx.x + blockDim.x * blockIdx.x;
		// Add guard for threads: the memory of subinterval is allocated according to numSubintervals, for thread id larger than numSubintervals,
		// the behavior could be undefined. 
        if (id < num_subintervals){
			if (branch_fac == 1) {
				// Do not branch & just copy interval to subinterval
				for (int i = 0; i < dim; i++)
					subinterval[i * num_subintervals + id] = interval[i];
					// + startID
			}
			else {
				if (branching_strategy == _EQUALY_PER_DIM) {
					if (adaptive_branching){
						branch_adaptively(id, interval, subinterval, num_subintervals, branch_fac, dim, num_branch_more_dims, branch_more_dims);
					}
					else if (num_branch_dims == dim) {
						branch_equaly_per_dim(id, interval, subinterval, num_subintervals, branch_fac, dim, num_branch_dims);
						//, startID
					}
					else {
						branch_as_many_dims_as_possible(id, interval, subinterval, num_subintervals, branch_fac, dim, num_branch_dims);
						//, startID
					}
				}
				else if (branching_strategy == _ON_LARGEST_DIM) {
					branch_on_largest_dim(id, interval, subinterval, num_subintervals, dim);
				}
			}
		}
	}

	template <typename I>
	__global__
	void initialize_derivatives(I* subinterval, cu::tangent<I>* deriv_subinterval, int numSubintervals, int dim)
	{
		int id = threadIdx.x + blockDim.x * blockIdx.x;
		if (id < numSubintervals){
			I initConst = {0.0, 0.0};
			I initActive = {1.0, 1.0};
			if (id < numSubintervals){
				for (int i = 0; i < dim; i ++){
					for (int j = 0; j < dim; j++){
						if (i == j)
							deriv_subinterval[i*numSubintervals*dim + id*dim + j] = cu::tangent<I>(subinterval[i*numSubintervals + id], initActive);
						else
							deriv_subinterval[i*numSubintervals*dim + id*dim + j] = cu::tangent<I>(subinterval[i*numSubintervals + id], initConst);
					}
				}
			}
		}
	} 

	template <typename I>
	__global__
	void get_center_values(cu::tangent<I>* functionValuesAndDerivs, cu::tangent<double>* centerValues, I* subintervals, int numSubintervals, int dim, int centerStrategy)
	{
		int id = threadIdx.x + blockDim.x * blockIdx.x;
		if (id < numSubintervals){
			if (centerStrategy == _SIMPLE){
				for (int i = 0; i < dim; i++){
					centerValues[i * numSubintervals +id] = cu::tangent<double>(mid(subintervals[i * numSubintervals + id]));
				}
			}
			else {
				for (int i = 0; i < dim; i++){
					double LB_derivObjFunction_i = derivative(functionValuesAndDerivs[id * dim + i]).lb;
					double UB_derivObjFunction_i = derivative(functionValuesAndDerivs[id * dim + i]).ub;
					double LB_x_i = subintervals[i * numSubintervals + id].lb;
					double UB_x_i = subintervals[i * numSubintervals + id].ub;
					if (UB_derivObjFunction_i <= 0)
						centerValues[i * numSubintervals + id] = cu::tangent<double>(UB_x_i);
					else if (LB_derivObjFunction_i >= 0)
						centerValues[i * numSubintervals + id] = cu::tangent<double>(LB_x_i);
					else
						centerValues[i * numSubintervals + id] = cu::tangent<double>((LB_derivObjFunction_i * LB_x_i - UB_derivObjFunction_i * UB_x_i)/(LB_derivObjFunction_i - UB_derivObjFunction_i));
				}
			}
		}
	}

	template <typename I>
	__global__
	void run_centered_form(cu::tangent<double>* centerFunctionValues, cu::tangent<I>* deriv_dagFunctionValues, cu::tangent<double>* centerValues, I* dagFunctionValues, I* subintervals, 
							int numSubintervals, int numDagFunctions, int dim)
	{
		int id = threadIdx.x + blockDim.x * blockIdx.x;
		double tempRes;
		I tempResInterval;
		if (id < numSubintervals){
			for (int i = 0; i < numDagFunctions; i ++){
				tempRes = value(centerFunctionValues[i * numSubintervals + id]);		
				tempResInterval.lb = tempRes;	
				tempResInterval.ub = tempRes;
				for (int j = 0; j < dim; j ++){
					tempResInterval = tempResInterval + derivative(deriv_dagFunctionValues[i * numSubintervals * dim + id * dim + j]) * (subintervals[j * numSubintervals + id] - value(centerValues[j * numSubintervals + id]));
				}
				dagFunctionValues[i * numSubintervals + id] = tempResInterval;
			}
		}
	}
}
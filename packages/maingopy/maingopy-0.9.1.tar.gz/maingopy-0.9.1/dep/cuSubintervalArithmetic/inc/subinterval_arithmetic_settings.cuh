#ifndef SUBINTERVAL_ARITHMETIC_SETTINGS_CUH_
#define SUBINTERVAL_ARITHMETIC_SETTINGS_CUH_

#pragma once
// *************************** Subinterval Aritmetic Settings **************************************
#define GPU_FOR_LB 1						// Settings for switching between GPU-parallel and CPU-serial implementation of the subinterval arithmetic. !!! CPU version is currently not working !!!

#define USE_HARD_CODED_FUNCTION 0			// Using hard coded functions or DAG for function evaluations
#define MULTIPLE_SUBDOMAINS_PER_THREAD 0	// Switch between using one or multiple subintervals per thread (0 = one subinterval per thread)

#define USE_CORNER_POINT_AS_CENTER 0		// Switch between optimal center points and corner point as center point (0 = optimal center point)

#define USE_HARD_CODED_ARRAYS 0				// Using hard coded arrays instead of dynamic arrays (register instead of global memory)

namespace SIA {

	enum branch_strategy { _EQUALY_PER_DIM, _ON_LARGEST_DIM };
	enum interval_arithmetic { _NATURAL_INTERVAL_EXTENSION, _CENTERED_FORM };
	enum center_sstrategy { _SIMPLE, _ADVANCED };

	/**
		* @brief Class for managing the settings of the subinterval arithmetic.
		*/
	class subinterval_arithmetic_settings {
	private:
		// Setting parameters
		int _numSubintervals;					// Number of subintervals during the subinterval arithemtic
		int _intervalArithmetic;
		int _branchingStrategy;
		int _centerStrategy;
		int _dim;

		// Parameters for uniform brancing
		int _branchFacPerDim;					// Number of branches on each dimension/variable
		int _numBranchDims;						// Number of dimensions/variables to branch on (If the numSubintervals < brachFacPerDim ^ dim then the uniformly branching can not branch on every dimension/variable)				
		int _minBranchFacPerDim;				// Minum number of branches on each dimension/variable 
		int _numBranchMoreDims;
		bool _adaptiveBranching = false;

		// Kernel parameters	
		int _numThreadsPerBlock;				// Number of cuda-threads per GPU-block used for the subinterval arithmetic
		int _numBlocks;							// Number of GPU blocks used for the subinterval arithmetic

		/**
			* @brief Calculates the largest integer numDims such that pow(_minBranchFacPerDim, _numDims) <= numBranches. 
			*		This is the maximal number of dimensions/variables that the subinterval arithmetic can branch one per iteration 
			*		and still branching at least _minBranchFacPerDim times on each dimension/variable.
			* 
			* @return returns the largest integer numDims such that pow(_minBranchFacPerDim, _numDims) <= numBranches
			*/
		int calc_max_numDims();

		// Returns the largest integer branch_per_dim, such that pow(branch_per_dim, dim) <= branch_fac
		/**
			* @brief Calculates the largest integer numDims such that pow(_branchPerDim, _numDims) <= _numSubintervals.
			*		This is the maximal number of branchings per dimension without exceeding the subinterval limit.
			*			E.g. if _dim = 2 and _numSubintervals = 20, then we can not create 20 subintervals by uniformly branching both dimesion. 
			*			We can create at most 4^2 = 16 subintervals, because if we branch 5 times on each dimension we would create 5 ^ 2 = 25 subintervals. 
			*
			* @return returns the largest integer numDims such that pow(_branchPerDim, _dim) <= _numSubintervals, which is the branching factor per dimension (_branchFacPerDim)
			*/
		int calc_branchFacPerDim();

	public:
		// Constructors
		subinterval_arithmetic_settings();
		subinterval_arithmetic_settings(int dim, int maxNumSubintervals, int intervalArithmetic, int branchingStrategy, int numThreadsPerBlock, int centerStrategy, int minBranchFacPerDim);

		// Destructor
		~subinterval_arithmetic_settings();

		// Getter
		__host__ __device__ int inline get_num_subintervals() { return _numSubintervals; }
		__host__ __device__ void inline set_num_subintervals(int new_num_subintervals) { _numSubintervals = new_num_subintervals; }
		__host__ __device__ int inline get_interval_arithmetic() { return _intervalArithmetic; }
		__host__ __device__ int inline get_branching_strategy() { return _branchingStrategy; }
		__host__ __device__ int inline get_center_strategy() {return _centerStrategy; }
		__host__ __device__ int inline get_num_branch_dims() { return _numBranchDims; }
		__host__ __device__ int inline get_branch_fac_per_dim() { return _branchFacPerDim; }
		__host__ __device__ int inline get_num_branch_more_dims() { return _numBranchMoreDims; }
		__host__ __device__ bool inline get_adaptive_branching_flag() { return _adaptiveBranching; }
		__host__ __device__ int inline get_dim() { return _dim; }
		__host__ __device__ int inline get_min_branch_fac_per_dim() { return _minBranchFacPerDim; }
		__host__ __device__ int inline get_num_threads() { return _numThreadsPerBlock; }
		__host__ __device__ int inline get_num_blocks() { return _numBlocks; }

	}; // class subinterval_arithmetic_settings

}

#endif // SUBINTERVAL_ARITHMETIC_SETTINGS_CUH_
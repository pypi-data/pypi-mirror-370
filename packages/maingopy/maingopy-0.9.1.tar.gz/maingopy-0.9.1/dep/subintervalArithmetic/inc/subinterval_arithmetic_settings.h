#ifndef SUBINTERVAL_ARITHMETIC_SETTINGS_CUH_
#define SUBINTERVAL_ARITHMETIC_SETTINGS_CUH_

// #pragma once
#include <dagdatatypes.h>

// *************************** Subinterval Aritmetic Settings **************************************
#define USE_CORNER_POINT_AS_CENTER 0		// Switch between optimal center points and corner point as center point (0 = optimal center point)

namespace subinterval_arithmetic {

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
		int _intervalArithmetic;                // The interval arithmetic used for boundsing (0 NIE, 1 CF)
		int _branchingStrategy;					// The branching strategy used for generating subintervals
		int _centerStrategy;
		int _dim;

		// Parameters for uniform brancing
		int _branchFacPerDim;					// Number of branches on each dimension/variable
		int _numBranchDims;						// Number of dimensions/variables to branch on (If the numSubintervals < brachFacPerDim ^ dim then the uniformly branching can not branch on every dimension/variable)				
		int _minBranchFacPerDim;				// Minum number of branches on each dimension/variable 
		int _numBranchMoreDims = 0;
		bool _adaptiveBranching = false;

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
		subinterval_arithmetic_settings(int dim, int maxNumSubintervals, int intervalArithmetic, int branchingStrategy, int centerStrategy, int minBranchFacPerDim);

		// Destructor
		~subinterval_arithmetic_settings();

		// Getter
		int inline get_num_subintervals() { return _numSubintervals; }
		void inline set_num_subintervals(int new_num_subintervals) { _numSubintervals = new_num_subintervals; }
		int inline get_interval_arithmetic() { return _intervalArithmetic; }
		int inline get_branching_strategy() { return _branchingStrategy; }
		int inline get_center_strategy() { return _centerStrategy; }
		int inline get_num_branch_dims() { return _numBranchDims; }
		int inline get_branch_fac_per_dim() { return _branchFacPerDim; }
		int inline get_num_branch_more_dims() { return _numBranchMoreDims; }
		bool inline get_adaptive_branching_flag() { return _adaptiveBranching; }
		int inline get_dim() { return _dim; }
		int inline get_min_branch_fac_per_dim() { return _minBranchFacPerDim; }

	}; // class subinterval_arithmetic_settings

}

#endif // SUBINTERVAL_ARITHMETIC_SETTINGS_CUH_
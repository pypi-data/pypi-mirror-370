
#include "subinterval_arithmetic_settings.cuh"

namespace subinterval_arithmetic {

	// Returns the largest integer num_dims, such that pow(MIN_BRANCH_PER_DIM, num_dims) <= num_branches
	int subinterval_arithmetic_settings::calc_max_numDims() {
		int max_num_dims = 0;
		int branch_fac = _minBranchFacPerDim;
		if (_numSubintervals < _minBranchFacPerDim){
			max_num_dims = 1;
			return max_num_dims;
		}
		else {
			for (int i = 1; i < _dim + 1; i++) {
				if (pow(branch_fac, i) > _numSubintervals) {
					max_num_dims = i - 1;
					return max_num_dims;
					//break;
				}
			}
		}
		return _dim;
	}

	// Only branch more when pow(branch_fac, dim) < numSubIntervals
	int subinterval_arithmetic_settings::calc_branchFacPerDim() {
		int tempBranchDim = 0;
		int branch_per_dim = 0;
		bool found_branch_per_dim = false;		

		while (!found_branch_per_dim) {
			tempBranchDim ++; 
			if (pow(tempBranchDim, _numBranchDims) > _numSubintervals) {
				found_branch_per_dim = true;
			}	
		}

		branch_per_dim = tempBranchDim - 1;

		// Get the new number of subintervals
		int new_num_subintervals = pow(branch_per_dim, _dim);
		if (new_num_subintervals < _numSubintervals){
			_numBranchMoreDims = _numBranchDims - 1;
			while (!_adaptiveBranching) {
		
				if (_numBranchMoreDims != 0){
					if (pow(tempBranchDim, _numBranchMoreDims)*pow(branch_per_dim, _numBranchDims - _numBranchMoreDims) < _numSubintervals + 1){
						_adaptiveBranching = true;
						new_num_subintervals = pow(tempBranchDim, _numBranchMoreDims)*pow(branch_per_dim, _numBranchDims - _numBranchMoreDims);
					}
					else
						_numBranchMoreDims --;
				}
				else {
					break;
				}
			}
		}
		
		// Reduce the number of threads to the new number of subintervals
		set_num_subintervals(new_num_subintervals);
		return branch_per_dim;
	}

	subinterval_arithmetic_settings::subinterval_arithmetic_settings() {}
	subinterval_arithmetic_settings::subinterval_arithmetic_settings(int dim, int maxNumSubintervals, int intervalArithmetic, int branchingStrategy, int numThreadsPerBlock, int centerStrategy, int minBranchFacPerDim) {
		_numSubintervals = maxNumSubintervals;
		_intervalArithmetic = intervalArithmetic;
		_branchingStrategy = branchingStrategy;
		_numThreadsPerBlock = numThreadsPerBlock;
		_centerStrategy = centerStrategy;
		_dim = dim;
		_minBranchFacPerDim = minBranchFacPerDim;

		_numBranchDims = calc_max_numDims();
		_branchFacPerDim = calc_branchFacPerDim();

		// Using maxPosibleSubintervals will lead to "zero-bounded" error. 
		// int maxPosibleSubintervals = pow(_branchFacPerDim, _dim);
		// if (maxPosibleSubintervals < _numSubintervals)
		// 	_numSubintervals = maxPosibleSubintervals;		

		if (_numSubintervals < _numThreadsPerBlock)
			_numThreadsPerBlock = _numSubintervals;

		// Calc number of GPU-blocks necessary to run enough threads
		_numBlocks = ceil(_numSubintervals * 1. / _numThreadsPerBlock);

	}
	subinterval_arithmetic_settings::~subinterval_arithmetic_settings() {}
}
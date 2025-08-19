# Example Problem Number 07 - Simple Problem with Growing Datasets

## About

This problem demonstrates the solution of a parameter estimation problem using growing datasets.
The problem to be solved is optimizing the slope of a linear function through the origin such that it fits the three data points (1,1), (1,0.6), and (1,0) best

    min  [(slope*1-1)^2 + (slope*1-0.6)^2 + (slope*1-0)^2]
    s.t. slope in [0,25]

To avoid MAiNGO passing this problem as a QP to CPLEX, we use sqroot(slope) as optimization variable and obtain

    min  [(x^2-1)^2 + (x^2-0.6)^2 + (x^2-0)^2]
    s.t. x in [0,5]
    
To solve the problem, you need to
* set compiler flag MAiNGO_use_growing_datasets to true
* include the file `problem_growingDatasets_simple.h` in your main file (e.g., `mainCppApi.cpp`)
* use an augmentation rule different from SCALING.
 
Note that augmentation rule SCALING can not trigger augmentation and, thus, does not lead to convergence for this model due to conflicting data points. In particular, one data point can be fitted perfectly, while there is a deviation between predictions and data when using at least two data points.
For more details refer to Example 1 of Sass et al. (Submitted in 2023)

The optimal slope for fitting all data points is slope = 0.533, i.e., x = 0.730.

## References

Sass, S., Mitsos, A., Bongartz, D., Bell, I. H., Nikolov, N., & Tsoukalas, A. (2023). A branch-and-bound algorithm with growing datasets for large-scale parameter estimation. *Submitted*
<!-- Sass, S., Mitsos, A., Bongartz, D., Bell, I. H., Nikolov, N., & Tsoukalas, A. (2023). [A branch-and-bound algorithm with growing datasets for large-scale parameter estimation](url to paper). *Journal* volume, firstPage–lastPage  -->
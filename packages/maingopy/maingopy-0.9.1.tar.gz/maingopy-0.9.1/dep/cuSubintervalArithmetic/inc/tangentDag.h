#pragma once

#include "cudaUtilities.h"

#include <cuinterval/interval.h>
#include <cutangent/tangent.h>

#include <vector>

namespace mc {
    class FFGraph;
    class FFVar;
} // namespace mc

//Use interval type to initialize tangent type then both the derivatives and values could be obtained.
void construct_mccormick_cuda_graph(const std::vector<cuda_ctx> &ctx, cudaGraph_t &cuda_graph, const mc::FFGraph &graph,
                                    cu::tangent<cu::interval<double>> *h_in,
                                    cu::tangent<cu::interval<double>> *h_out,
                                    cu::tangent<cu::interval<double>> *d_mccormick_bounds,
                                    const std::vector<mc::FFVar> &resultVars);

//#endif


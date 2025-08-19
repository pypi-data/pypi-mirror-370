#pragma once

#include "subinterval_arithmetic.cuh"
#include "cudaUtilities.h"
#include "../../../inc/MAiNGOException.h"

#pragma nv_diagnostic push
#pragma nv_diag_suppress 177 // variable was declared but not referenced warning
#pragma nv_diag_suppress 815 // nvcc is not happy with const value return types
#pragma nv_diagnostic pop

#include "ffunc.hpp"
#include <vector>

namespace SIA { //using namespace SIA;

    // TODO: Use XMacro to generate these kernels
    
    // Using stride loops within kernel to deal with high dimensional cases 
    template<typename T>
    __global__ void k_add(T *x, T *y, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x){
            res[i] = x[i] + y[i];
        }      
    }

    template<typename T>
    __global__ void k_sub(T *x, T *y, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x){
            res[i] = x[i] - y[i];
        }                
    }

    template<typename T>
    __global__ void k_mul(T *x, T *y, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = x[i] * y[i];
        }                
    }

    template<typename T>
    __global__ void k_div(T *x, T *y, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = x[i] / y[i];
        }
    }

    template<typename T>
    __global__ void k_scale(T *x, typename T::value_type y, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = y * x[i];
        }
    }

    template<typename T>
    __global__ void k_shift(T *x, typename T::value_type y, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = y + x[i];
        }
    }

    template<typename T>
    __global__ void k_neg(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = -x[i];
        }
    }

    template<typename T>
    __global__ void k_inv(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::recip(x[i]);
        }
    }

    template<typename T>
    __global__ void k_sqr(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::sqr(x[i]);
        }
    }

    template<typename T>
    __global__ void k_sqrt(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::sqrt(x[i]);
        }       
    }

    template<typename T>
    __global__ void k_sin(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::sin(x[i]);
        }         
    }

    template<typename T>
    __global__ void k_cos(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::cos(x[i]);
        }       
    }

    template<typename T>
    __global__ void k_exp(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::exp(x[i]);
        }        
    }

    template<typename T>
    __global__ void k_log(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::log(x[i]);
        }
    }

    template<typename T>
    __global__ void k_tanh(T *x, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::tanh(x[i]);
        }
    } 

    template<typename T>
    __global__ void k_ipow(T *x, int p, T *res, int n)
    {
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::pown(x[i], p);
        }
    }

    template<typename T>
    __global__ void k_dpow(T *x, double p, T *res, int n)
    {
        assert(int(p) == p && "currently only supports integer as exponent");
        for (int i = threadIdx.x + blockIdx.x * blockDim.x; i < n; i += gridDim.x * blockDim.x) 
        {
            res[i] = cu::pown(x[i], int(p));
        }
    }

    // n_instances: how many subintervals to process at the same time 
    // I: generally in type cu::interval
    template<typename I>
    void construct_cuda_graph(subinterval_arithmetic_memory<I> &memory, subinterval_arithmetic_settings &settings)
    {
        using Op = mc::FFOp;
        using Var = mc::FFVar;
        using node = cudaGraphNode_t;
        using T = I::value_type;

        auto n_vars = memory.dagInfo.dagObj->DAG.nvar();
        auto n_ops = n_vars + memory.dagInfo.dagObj->DAG.naux();

        int n = settings.get_num_subintervals();
        int n_derivs = n * n_vars;
        int n_threads_per_block = settings.get_num_threads();
        int n_blocks = settings.get_num_blocks();

        // Pointers for storing intermediate results
        // Potential improvement: replace with array in void * type 
        I *d_var_bound = nullptr;
        I *d_ops_bound = nullptr;
        cu::tangent<I> *deriv_var_bound = nullptr;
        cu::tangent<I> *deriv_ops_bound = nullptr; 

        std::vector<node> nodes(n_ops);
        std::vector<node> outNodes(memory.numDagFunctions);
        // keeps track of the dependencies between the nodes
        std::vector<node> deps;
        deps.reserve(2);

        // stores where the result of the operation at index i is stored in d_mccormick_bounds
        std::vector<int> d_res_locations(n_ops); 
        int next_free_slot = 0;
        
        cudaKernelNodeParams kernel_params {
            .func           = nullptr,
            .gridDim        = dim3(n_blocks, 1, 1),
            .blockDim       = dim3(n_threads_per_block, 1, 1),
            .sharedMemBytes = 0,
            .kernelParams   = nullptr,
            .extra          = nullptr
        };     

        // get the index of an operation (as stored in the graph)
        auto index = [](const Op *op) {
            return op->pres->id().second;
        };

        // get the type of a variable
        auto type = [](const Var *var) {
            return var->ops().first->type;
        };

        // get the unique index of an operation (adds offset to non-variables)
        auto unique_index = [&](const Var *var) {
            auto idx = index(var->ops().first);
            if (type(var) != Op::VAR) {
                idx += n_vars;
            }
            return idx;
        };

        // access the children of a variable
        auto children = [](const Var *var) {
            return var->ops().second;
        };

        // Add the branching node to branch, collect data directly from the data members of SIA memory  
        node branch;
        int branch_fac = settings.get_branch_fac_per_dim();
        int num_branch_dims = settings.get_num_branch_dims();
        int branching_strategy = settings.get_branching_strategy();
        int num_branch_more_dims = settings.get_num_branch_more_dims();
        bool adaptive_branching = settings.get_adaptive_branching_flag(); 
        kernel_params.func = (void *)branch_interval_into_subinterval<I>;
        void * branchParams[10] = {&memory.d_inputDomain, &memory.d_subintervals, &memory.numSubintervals, &branch_fac, &memory.dim, &num_branch_dims, 
                                    &branching_strategy, &num_branch_more_dims, &adaptive_branching, &memory.d_branch_more_dims};
        kernel_params.kernelParams = branchParams;
        CUDA_CHECK(cudaGraphAddKernelNode(&branch, memory.cuDag, nullptr, 0, &kernel_params));

        // Node used for initializing derivatives
        node initDeriv;
        void * derivInitParams[4] = { nullptr, nullptr, nullptr, nullptr };
        if (settings.get_interval_arithmetic() == _CENTERED_FORM)
        {
            derivInitParams[0] = &memory.d_subintervals;
            derivInitParams[1] = &memory.deriv_variableValues;
            derivInitParams[2] = &memory.numSubintervals;
            derivInitParams[3] = &memory.dim;

            kernel_params.func = (void *)initialize_derivatives<I>;
            kernel_params.kernelParams = derivInitParams;
            CUDA_CHECK(cudaGraphAddKernelNode(&initDeriv, memory.cuDag, &branch, 1, &kernel_params));
        }

        auto add_unary_op = [&](const Op *op, void *fn) {
            auto idx = index(op) + n_vars;

            auto operand = op->pops[0];
            auto operand_idx = unique_index(operand);

            deps.push_back(nodes[operand_idx]);

            int in_mem_idx = d_res_locations[operand_idx];
            int out_mem_idx;

            // Check if it is the only use of the input variable. This is the case if input variable 
            // has only one child (the current operation). If so, reuse the slot for the next output.
            if (children(operand).size() == 1 && unique_index(children(operand).back()->pres) == idx) {
                out_mem_idx = in_mem_idx;
            } else {
                out_mem_idx = next_free_slot;
                next_free_slot++;
            }
            d_res_locations[idx] = out_mem_idx;

            I *in = nullptr;
            I *out = nullptr;
            cu::tangent<I> *deriv_in = nullptr;
            cu::tangent<I> *deriv_out = nullptr;
            void *params[3] = { nullptr, nullptr, nullptr };

            if (settings.get_interval_arithmetic() == _CENTERED_FORM){
                deriv_in = &memory.deriv_dagVarValues[n * n_vars * in_mem_idx];
                deriv_out = &memory.deriv_dagVarValues[n * n_vars * out_mem_idx];
                params[0] = &deriv_in;
                params[1] = &deriv_out; 
                params[2] = &n_derivs;                
            }
            else {
                in = &memory.d_dagVarValues[n * in_mem_idx];
                out = &memory.d_dagVarValues[n * out_mem_idx];
                params[0] = &in;
                params[1] = &out; 
                params[2] = &n;              
            }

            kernel_params.func = fn;
            kernel_params.kernelParams = params;
            CUDA_CHECK(cudaGraphAddKernelNode(&nodes[idx], memory.cuDag, deps.data(), deps.size(), &kernel_params));
            deps.clear();
        };

        auto add_binary_op = [&](const Op *op, void *fn) {
            constexpr int mem_slot_unset = -1;
            constexpr int n_inputs = 2;
            auto idx = index(op) + n_vars;

            void *params[4] { nullptr, nullptr, nullptr, nullptr };
            void *ins[n_inputs];

            int mem_slot = mem_slot_unset;

            for (int i = 0; i < n_inputs; i++) {
                auto operand = op->pops[i];
                auto operand_type = type(operand);

                if (operand_type == Op::CNST) {
                    if (settings.get_interval_arithmetic() == _CENTERED_FORM){
                        // Constants should be interval type, otherwise will not call the corresponding reloaded operator 
                        double constVar = op->pops[i]->num().x;
                        I intervalConst = {constVar, constVar}; // NOTE: We currently assume that we deal with real values only (no ints)
                        auto constId = op->pops[i]->id();
                        memory.constantVars[constId.second + n_vars] = intervalConst;
                        params[i] = &memory.constantVars[constId.second + n_vars];
                    }
                    else {
                        params[i] = &op->pops[i]->num().x; // NOTE: We currently assume that we deal with real values only (no ints)
                    }
                } else {
                    auto operand_idx = unique_index(operand);
                    deps.push_back(nodes[operand_idx]);

                    // Check if it is the only use of the input variable. This is the case if input variable 
                    // has only one child (the current operation). If so, reuse the slot for the next output.
                    if (children(operand).size() == 1 && unique_index(children(operand).back()->pres) == idx) {
                        mem_slot = d_res_locations[operand_idx]; // immediate reuse of memory
                    }

                    auto in_mem_idx = d_res_locations[operand_idx];
                    if (settings.get_interval_arithmetic() == _CENTERED_FORM){
                        ins[i] = &memory.deriv_dagVarValues[n * n_vars * in_mem_idx];
                    }
                    else {
                        ins[i] = &memory.d_dagVarValues[n * in_mem_idx];
                    }
                    params[i] = &ins[i];
                }
            }
            
            int out_mem_idx;
            if (mem_slot == mem_slot_unset) { 
                out_mem_idx = next_free_slot;
                next_free_slot++;
            } else  { 
                out_mem_idx = mem_slot;
            }

            d_res_locations[idx] = out_mem_idx;

            I *out = nullptr;
            cu::tangent<I> *deriv_out = nullptr;

            if (settings.get_interval_arithmetic() == _CENTERED_FORM){
                deriv_out = &memory.deriv_dagVarValues[n * n_vars * out_mem_idx];
                params[2] = &deriv_out; 
                params[3] = &n_derivs;
            }
            else {
                out = &memory.d_dagVarValues[n * out_mem_idx];
                params[2] = &out;   
                params[3] = &n;            
            }
            kernel_params.func = fn;
            kernel_params.kernelParams = params;
            CUDA_CHECK(cudaGraphAddKernelNode(&nodes[idx], memory.cuDag, deps.data(), deps.size(), &kernel_params));
            deps.clear();
        };

        for (const Var *var : memory.dagInfo.dagObj->DAG.Vars()) {
            const Op* op = var->ops().first;

            switch (op->type) {
            case Op::CNST: {} break;
            case Op::VAR: {
                // Allocate the subinterval data to cuda nodes
                auto idx = index(op);
                auto slot_idx = next_free_slot;
                next_free_slot++;
                d_res_locations[idx] = slot_idx;
                // Copy data from different array if using centered form.
                if (settings.get_interval_arithmetic() == _CENTERED_FORM){
                    deriv_var_bound = &memory.deriv_variableValues[n * n_vars * slot_idx];
                    deriv_ops_bound = &memory.deriv_dagVarValues[n * n_vars * slot_idx];
                    CUDA_CHECK(cudaGraphAddMemcpyNode1D(&nodes[idx], memory.cuDag, &initDeriv, 1, 
                                                        deriv_ops_bound, deriv_var_bound, n * n_vars * sizeof(cu::tangent<I>), 
                                                        cudaMemcpyDeviceToDevice));
                }
                else {
                    d_var_bound = &memory.d_subintervals[n * slot_idx];
                    d_ops_bound = &memory.d_dagVarValues[n * slot_idx];
                    CUDA_CHECK(cudaGraphAddMemcpyNode1D(&nodes[idx], memory.cuDag, &branch, 1, 
                                                        d_ops_bound, d_var_bound, n * sizeof(I), 
                                                        cudaMemcpyDeviceToDevice));
                }
            } break;
            case Op::PLUS: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_binary_op(op, (void *)k_add<cu::tangent<I>>);
                else
                    add_binary_op(op, (void *)k_add<I>);
            } break;
            case Op::SHIFT: { // add var + const
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_binary_op(op, (void *)k_shift<cu::tangent<I>>);
                else
                    add_binary_op(op, (void *)k_shift<I>);
            } break;
            case Op::NEG: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_neg<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_neg<I>);
            } break;
            case Op::MINUS: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_binary_op(op, (void *)k_sub<cu::tangent<I>>);
                else
                    add_binary_op(op, (void *)k_sub<I>);
            } break;
            case Op::TIMES: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_binary_op(op, (void *)k_mul<cu::tangent<I>>);
                else
                    add_binary_op(op, (void *)k_mul<I>);
            } break;
            case Op::SCALE: { // mul var * const
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_binary_op(op, (void *)k_scale<cu::tangent<I>>);
                else
                    add_binary_op(op, (void *)k_scale<I>);
            } break;
            case Op::DIV: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_binary_op(op, (void *)k_div<cu::tangent<I>>);
                else
                    add_binary_op(op, (void *)k_div<I>);
            } break;
            case Op::INV: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_inv<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_inv<I>);
            } break;
            case Op::SQR: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_sqr<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_sqr<I>);
            } break;
            case Op::SQRT: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_sqrt<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_sqrt<I>);
            } break;
            // Add intrinsic function sin.
            case Op::SIN: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_sin<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_sin<I>);
            } break;
            case Op::COS: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_cos<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_cos<I>);
            } break;
            case Op::EXP: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_exp<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_exp<I>);
            } break;
            case Op::LOG: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_log<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_log<I>);
            } break;
            case Op::TANH: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_unary_op(op, (void *)k_tanh<cu::tangent<I>>);
                else
                    add_unary_op(op, (void *)k_tanh<I>);
            } break;
            case Op::IPOW: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_binary_op(op, (void *)k_ipow<cu::tangent<I>>);
                else
                    add_binary_op(op, (void *)k_ipow<I>);
            } break;
            case Op::DPOW: {
                if (settings.get_interval_arithmetic() == _CENTERED_FORM)
                    add_binary_op(op, (void *)k_dpow<cu::tangent<I>>);
                else
                    add_binary_op(op, (void *)k_dpow<I>);
            } break;
            default: {
                throw maingo::MAiNGOException("  Error in construction of cuda graph: Unknown op type: " + std::to_string(op->type));
            } break;
            }
        } 

        // Copy results back to host, to dagFunctionValues
        int i = 0;
        for (auto result_var : memory.dagInfo.dagObj->resultVars) {
            // auto result_var_idx = result_var.ops().first->pres->id().second + n_vars;
            auto result_var_idx = unique_index(&result_var);
            auto out_mem_idx = d_res_locations[result_var_idx];

            // node out;
            if (settings.get_interval_arithmetic() == _CENTERED_FORM){
                CUDA_CHECK(cudaGraphAddMemcpyNode1D(&outNodes[i], memory.cuDag, &nodes[result_var_idx], 1,
                                                    &memory.deriv_dagFunctionValues[n * n_vars * i], &memory.deriv_dagVarValues[n * n_vars * out_mem_idx], 
                                                    n * n_vars * sizeof(cu::tangent<I>), cudaMemcpyDeviceToDevice));
            }
            else{
                CUDA_CHECK(cudaGraphAddMemcpyNode1D(&outNodes[i], memory.cuDag, &nodes[result_var_idx], 1,
                                                    &memory.dagFunctionValues[n * i], &memory.d_dagVarValues[n * out_mem_idx], 
                                                    n * sizeof(I), cudaMemcpyDeviceToHost));
            }
            i++;
        }

        if (settings.get_interval_arithmetic() == _CENTERED_FORM){
            // Add node for allocating centers
            node center;
            int centerStrategy = settings.get_center_strategy();
            kernel_params.func = (void *)get_center_values<I>;
            void * centerParams[6] = { &memory.deriv_dagFunctionValues, &memory.centerValues, &memory.d_subintervals, &memory.numSubintervals, &memory.dim, &centerStrategy};
            kernel_params.kernelParams = centerParams;
            CUDA_CHECK(cudaGraphAddKernelNode(&center, memory.cuDag, outNodes.data(), outNodes.size(), &kernel_params));

            // Add node for running operations on center values
            node centerGraph;
            CUDA_CHECK(cudaGraphAddChildGraphNode(&centerGraph, memory.cuDag, &center, 1, memory.cuCenterDag));

            // Add node for finalize centered form
            node cform;
            kernel_params.func = (void *)run_centered_form<I>;
            void * cformParams[8] = { &memory.centerFunctionValues, &memory.deriv_dagFunctionValues, &memory.centerValues, &memory.d_dagFunctionValues, &memory.d_subintervals,
                                        &memory.numSubintervals, &memory.numDagFunctions, &memory.dim };
            kernel_params.kernelParams = cformParams;
            CUDA_CHECK(cudaGraphAddKernelNode(&cform, memory.cuDag, &centerGraph, 1, &kernel_params));

            // Copy centered form values back to CPU
            node out;
            CUDA_CHECK(cudaGraphAddMemcpyNode1D(&out, memory.cuDag, &cform, 1, memory.dagFunctionValues, memory.d_dagFunctionValues, 
                                                n*memory.numDagFunctions*sizeof(I), cudaMemcpyDeviceToHost));
        }
    }

    template<typename I>
    void construct_cuda_graph_for_centers(subinterval_arithmetic_memory<I> &memory, subinterval_arithmetic_settings &settings)
    {
        using Op = mc::FFOp;
        using Var = mc::FFVar;
        using node = cudaGraphNode_t;
        using T = I::value_type;

        auto n_vars = memory.dagInfo.dagObj->DAG.nvar();
        auto n_ops = n_vars + memory.dagInfo.dagObj->DAG.naux();

        int n = settings.get_num_subintervals();
        int n_threads_per_block = settings.get_num_threads();
        int n_blocks = settings.get_num_blocks();

        std::vector<node> nodes{n_ops};

        // keeps track of the dependencies between the nodes
        std::vector<node> deps;
        deps.reserve(2);

        // stores where the result of the operation at index i is stored in d_mccormick_bounds
        std::vector<int> d_res_locations(n_ops); 
        int next_free_slot = 0;
        
        cudaKernelNodeParams kernel_params {
            .func           = nullptr,
            .gridDim        = dim3(n_blocks, 1, 1),
            .blockDim       = dim3(n_threads_per_block, 1, 1),
            .sharedMemBytes = 0,
            .kernelParams   = nullptr,
            .extra          = nullptr
        }; 

        // get the index of an operation (as stored in the graph)
        auto index = [](const Op *op) {
            return op->pres->id().second;
        };

        // get the type of a variable
        auto type = [](const Var *var) {
            return var->ops().first->type;
        };

        // get the unique index of an operation (adds offset to non-variables)
        auto unique_index = [&](const Var *var) {
            auto idx = index(var->ops().first);
            if (type(var) != Op::VAR) {
                idx += n_vars;
            }
            return idx;
        };

        // access the children of a variable
        auto children = [](const Var *var) {
            return var->ops().second;
        };

        auto add_unary_op = [&](const Op *op, void *fn) {
            auto idx = index(op) + n_vars;
            auto operand = op->pops[0];
            auto operand_idx = unique_index(operand);

            deps.push_back(nodes[operand_idx]);

            int in_mem_idx = d_res_locations[operand_idx];
            int out_mem_idx;

            // Check if it is the only use of the input variable. This is the case if input variable 
            // has only one child (the current operation). If so, reuse the slot for the next output.
            if (children(operand).size() == 1 && unique_index(children(operand).back()->pres) == idx) {
                out_mem_idx = in_mem_idx;
            } else {
                out_mem_idx = next_free_slot;
                next_free_slot++;
            }
            d_res_locations[idx] = out_mem_idx;
            
            cu::tangent<double> *in = &memory.centerDagVarValues[n * in_mem_idx];
            cu::tangent<double> *out = &memory.centerDagVarValues[n * out_mem_idx];
            void *params[3] = { &in, &out, &n };

            kernel_params.func = fn;
            kernel_params.kernelParams = params;
            CUDA_CHECK(cudaGraphAddKernelNode(&nodes[idx], memory.cuCenterDag, deps.data(), deps.size(), &kernel_params));
            deps.clear();
        };

        auto add_binary_op = [&](const Op *op, void *fn) {
            constexpr int mem_slot_unset = -1;
            constexpr int n_inputs = 2;

            auto idx = index(op) + n_vars;

            void *params[4] { nullptr, nullptr, nullptr, &n };
            void *ins[n_inputs];

            int mem_slot = mem_slot_unset;

            for (int i = 0; i < n_inputs; i++) {
                auto operand = op->pops[i];
                auto operand_type = type(operand);

                if (operand_type == Op::CNST) {
                    params[i] = &op->pops[i]->num().x; // NOTE: We currently assume that we deal with real values only (no ints)
                } else {
                    auto operand_idx = unique_index(operand);
                    deps.push_back(nodes[operand_idx]);

                    // Check if it is the only use of the input variable. This is the case if input variable 
                    // has only one child (the current operation). If so, reuse the slot for the next output.
                    if (children(operand).size() == 1 && unique_index(children(operand).back()->pres) == idx) {
                        mem_slot = d_res_locations[operand_idx]; // immediate reuse of memory
                    }

                    auto in_mem_idx = d_res_locations[operand_idx];
                    ins[i] = &memory.centerDagVarValues[n * in_mem_idx];
                    params[i] = &ins[i];
                }
            }
            
            int out_mem_idx;
            if (mem_slot == mem_slot_unset) { 
                out_mem_idx = next_free_slot;
                next_free_slot++;
            } else  { 
            out_mem_idx = mem_slot;
            }

            d_res_locations[idx] = out_mem_idx;
            cu::tangent<double> *out = &memory.centerDagVarValues[n * out_mem_idx];
            params[2] = &out;
            kernel_params.func = fn;
            kernel_params.kernelParams = params;
            CUDA_CHECK(cudaGraphAddKernelNode(&nodes[idx], memory.cuCenterDag, deps.data(), deps.size(), &kernel_params));
            deps.clear();
        };

        for (const Var *var : memory.dagInfo.dagObj->DAG.Vars()) {
            const Op* op = var->ops().first;

            switch (op->type) {
            case Op::CNST: {} break;
            case Op::VAR: {
                // we need to copy the input bounds of the variables into the cuda graph on the device
                auto idx = index(op);
                auto slot_idx = next_free_slot;
                next_free_slot++;
                d_res_locations[idx] = slot_idx;
                cu::tangent<double> *input_variableCenters = &memory.centerValues[n * slot_idx];
                cu::tangent<double> *dag_variableCenters = &memory.centerDagVarValues[n * slot_idx];
                CUDA_CHECK(cudaGraphAddMemcpyNode1D(&nodes[idx], memory.cuCenterDag, NULL, 0, 
                                                    dag_variableCenters, input_variableCenters, n * sizeof(cu::tangent<double>), 
                                                    cudaMemcpyDeviceToDevice));
            } break;
            case Op::PLUS: {
                add_binary_op(op, (void *)k_add<cu::tangent<double>>);
            } break;
            case Op::SHIFT: { // add var + const
                add_binary_op(op, (void *)k_shift<cu::tangent<double>>);
            } break;
            case Op::NEG: {
                add_unary_op(op, (void *)k_neg<cu::tangent<double>>);
            } break;
            case Op::MINUS: {
                add_binary_op(op, (void *)k_sub<cu::tangent<double>>);
            } break;
            case Op::TIMES: {
                add_binary_op(op, (void *)k_mul<cu::tangent<double>>);
            } break;
            case Op::SCALE: { // mul var * const
                add_binary_op(op, (void *)k_scale<cu::tangent<double>>);
            } break;
            case Op::DIV: {
                add_binary_op(op, (void *)k_div<cu::tangent<double>>);
            } break;
            case Op::INV: {
                add_unary_op(op, (void *)k_inv<cu::tangent<double>>);
            } break;
            case Op::SQR: {
                add_unary_op(op, (void *)k_sqr<cu::tangent<double>>);
            } break;
            case Op::SQRT: {
                add_unary_op(op, (void *)k_sqrt<cu::tangent<double>>);
            } break;
            case Op::SIN: {
                add_unary_op(op, (void *)k_sin<cu::tangent<double>>);
            } break;
            case Op::COS: {
                add_unary_op(op, (void *)k_cos<cu::tangent<double>>);
            } break;
            case Op::EXP: {
                add_unary_op(op, (void *)k_exp<cu::tangent<double>>);
            } break;
            case Op::LOG: {
                add_unary_op(op, (void *)k_log<cu::tangent<double>>);
            } break;
            case Op::TANH: {
                add_unary_op(op, (void *)k_tanh<cu::tangent<double>>);
            } break;
            case Op::IPOW: {
                add_binary_op(op, (void *)k_ipow<cu::tangent<double>>);
            } break;
            case Op::DPOW: {
                add_binary_op(op, (void *)k_dpow<cu::tangent<double>>);
            } break;
            default: {
                throw maingo::MAiNGOException("  Error in construction of cuda graph: Unknown op type: " + std::to_string(op->type));
            } break;
            }
        }

        // Copy results back to host, to dagFunctionValues
        int i = 0;
        for (auto result_var : memory.dagInfo.dagObj->resultVars) {
            auto result_var_idx = unique_index(&result_var);
            auto out_mem_idx = d_res_locations[result_var_idx];

            node out;
            CUDA_CHECK(cudaGraphAddMemcpyNode1D(&out, memory.cuCenterDag, &nodes[result_var_idx], 1,
                                                &memory.centerFunctionValues[n * i], &memory.centerDagVarValues[n * out_mem_idx], 
                                                n * sizeof(cu::tangent<double>), cudaMemcpyDeviceToDevice));
            i++;
        }
    }

    // Main function for perfroming subinterval arithmetic
    template<typename I>
    void perform_subinterval_arithmetic(subinterval_arithmetic_memory<I> &memory, subinterval_arithmetic_settings &settings)
    {
        CUDA_CHECK(cudaGraphLaunch(memory.cuDagExec, memory.cudaContexts[0].stream));
        CUDA_CHECK(cudaStreamSynchronize(memory.cudaContexts[0].stream));       
    }
}
//#endif

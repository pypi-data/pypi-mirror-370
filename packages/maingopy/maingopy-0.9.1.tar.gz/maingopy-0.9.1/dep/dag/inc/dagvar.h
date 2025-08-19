#ifndef DAGVAR_H
#define DAGVAR_H

#pragma once
#include "dagdatatypes.h"
#include "dagdatatypes.cuh"
#include <vector>

namespace SVT_DAG {

    struct IndependentDagVar
    {
#ifdef CUDA_INSTALLED
        __device__ __host__
            IndependentDagVar() {}
#endif //CUDA_INSTALLED
        IndependentDagVar(const int dagVarIdIn)
            : dagVarId(dagVarIdIn)
        {}

#ifdef CUDA_INSTALLED
        __device__ __host__
#endif //CUDA_INSTALLED
            IndependentDagVar& operator= (IndependentDagVar const& o)
        {
            this->dagVarId = o.dagVarId;
            return *this;
        }

        int dagVarId{};
    };


    class BaseOperation;

    struct DependentDagVar
    {
#ifdef CUDA_INSTALLED
        __device__ __host__
            DependentDagVar() {}
#endif //CUDA_INSTALLED
        DependentDagVar(const int dagVarIdIn, BaseOperation* const operationIn, const int* const operandIdsIn, const int numOperandsIn)
            : dagVarId(dagVarIdIn), operation(operationIn), operandIds(operandIdsIn), numOperands(numOperandsIn)
        {}

#ifdef CUDA_INSTALLED
        __device__ __host__
#endif //CUDA_INSTALLED
            DependentDagVar& operator= (DependentDagVar const& o)
        {
            this->dagVarId = o.dagVarId;
            this->operation = o.operation;
            this->operandIds = o.operandIds;
            this->numOperands = o.numOperands;
            return *this;
        }

        int dagVarId{};

        BaseOperation* operation;
        const int* operandIds{};
        int numOperands;

    };

    struct ConstantDagVar
    {
#ifdef CUDA_INSTALLED
        __device__ __host__
            ConstantDagVar() {}
#endif //CUDA_INSTALLED
        template <typename T>
        ConstantDagVar(const int dagVarIdIn, const T valueIn)
            : dagVarId(dagVarIdIn)
        {
            value = convert_to_double(valueIn);
        }

#ifdef CUDA_INSTALLED
        __device__ __host__
#endif //CUDA_INSTALLED
            ConstantDagVar& operator= (ConstantDagVar const& o)
        {
            this->dagVarId = o.dagVarId;
            this->value = o.value;
            return *this;
        }

        int dagVarId{};

        double value;
    };

} // namespace SVT_DAG

#endif // DAGVAR_H
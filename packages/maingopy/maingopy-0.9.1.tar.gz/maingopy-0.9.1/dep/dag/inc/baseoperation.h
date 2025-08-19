#ifndef BASEOPERATION_H
#define BASEOPERATION_H

#pragma once

#include "dagdatatypes.h"
#ifdef CUDA_INSTALLED
#include "dagdatatypes.cuh"
#endif //CUDA_INSTALLED

#include <memory>
#include <vector>

namespace SVT_DAG {

    struct DerivativeInformation;

    // ******************************************** Concept ************************************************//
    struct Concept
    {
#ifdef CUDA_INSTALLED
        __device__ __host__ 
#endif // CUDA_INSTALLED          
        virtual ~Concept() {/*printf("The base destructor is called.");*/} // The destructor of base class will be called when the destructor of derived class is called.

        virtual void print() const = 0;
        virtual double evaluate(const std::vector<double>& operandValues, const int* const operandIndices) const = 0;
        virtual I_cpu  evaluate(const std::vector<I_cpu>& operandValues, const int* const operandIndices) const = 0;
        virtual double evaluate(const double* operandValues, const int* const operandIndices) const = 0;
        virtual I_cpu  evaluate(const I_cpu* operandValues, const int* const operandIndices) const = 0;
        virtual void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const = 0;

#ifdef CUDA_INSTALLED 
        __device__ virtual inline I_gpu evaluate_on_GPU(const I_gpu* operandValues, const int* const operandIndices) const = 0;
        __device__ virtual double evaluate_on_GPU(const double* operandValues, const int* const operandIndices) const = 0;

        __device__ virtual void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const = 0;
#endif // CUDA_INSTALLED
    };


    // ******************************************** Model ************************************************//
    template <typename T>
    struct Model : public Concept
    {
#ifdef CUDA_INSTALLED
        __device__ __host__
#endif // CUDA_INSTALLED
        Model(const T& specificOperation) : _specificOperation{ specificOperation } {}
#ifdef CUDA_INSTALLED
        __device__ __host__ 
#endif // CUDA_INSTALLED        
        ~Model() {/*printf("The derived class destructor is called.");*/} // The destructor should be on gpu as well when using delete to deallocate memory allocated with new

        void print() const override { _specificOperation.print(); }
        double evaluate(const std::vector<double>& operandValues, const int* const operandIndices) const override
        {
            return _specificOperation.evaluate(operandValues.data(), operandIndices);
        }
        I_cpu evaluate(const std::vector<I_cpu>& operandValues, const int* const operandIndices) const override
        {
            return _specificOperation.evaluate(operandValues.data(), operandIndices);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const override
        {
            return _specificOperation.evaluate(operandValues, operandIndices);
        }
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const override
        {
            return _specificOperation.evaluate(operandValues, operandIndices);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const override
        {
            _specificOperation.evaluate_derivative(operandValues, operandIndices, currentDagVar);
        }

#ifdef CUDA_INSTALLED
        __device__ inline I_gpu evaluate_on_GPU(const I_gpu* operandValues, const int* const operandIndices) const override
        {
            return _specificOperation.evaluate_on_GPU(operandValues, operandIndices);
        }
        __device__ double evaluate_on_GPU(const double* operandValues, const int* const operandIndices) const override
        {
            return _specificOperation.evaluate_on_GPU(operandValues, operandIndices);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const override
        {
            _specificOperation.evaluate_derivative_on_GPU(operandValues, operandIndices, currentDagVar);
        }
#endif // CUDA_INSTALLED

        T _specificOperation;
    };


    // ******************************************** BaseOperation ************************************************//
#ifdef CUDA_INSTALLED
    template <typename T>
    void swap(T*& a, T*& b)
    {
        T* temp = a;
        a = b;
        b = temp;
    }
#endif // CUDA_INSTALLED

    class BaseOperation
    {
    public:
        template < typename T >
            BaseOperation(const T& specificOperation)
            : _conceptPointerToSpecificOperation{ new Model<T>(specificOperation) }
        {
#ifdef CUDA_INSTALLED
            _d_conceptPointerToSpecificOperation = init_concept_ptr_on_GPU(specificOperation);
#endif // CUDA_INSTALLED
            //printf("The constructor of BaseOperation has been run.\n");
        }

            BaseOperation(const BaseOperation& otherOperation)
            : _conceptPointerToSpecificOperation{ otherOperation._conceptPointerToSpecificOperation }
        {
#ifdef CUDA_INSTALLED
            _d_conceptPointerToSpecificOperation = otherOperation._d_conceptPointerToSpecificOperation;
#endif // CUDA_INSTALLED
            //printf("The copy constructor has been run!\n");
        }

            ~BaseOperation();

            BaseOperation(BaseOperation&&) = default;
        BaseOperation& operator=(BaseOperation&&) = default;
        BaseOperation& operator=(const BaseOperation& otherOperation)
        {
            BaseOperation tmp(otherOperation);
            std::swap(_conceptPointerToSpecificOperation, tmp._conceptPointerToSpecificOperation);
#ifdef CUDA_INSTALLED
            swap(_d_conceptPointerToSpecificOperation, tmp._d_conceptPointerToSpecificOperation);
#endif // CUDA_INSTALLED
            return *this;
        }

        void print() const { _conceptPointerToSpecificOperation->print(); }
        template <typename dataType>
        dataType evaluate(const std::vector<dataType>& operandValues, const int* const operandIds) const
        {
            return _conceptPointerToSpecificOperation->evaluate(operandValues, operandIds);
        }
        template <typename dataType>
        dataType evaluate(const dataType* operandValues, const int* const operandIds) const
        {
            return _conceptPointerToSpecificOperation->evaluate(operandValues, operandIds);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIds, DerivativeInformation& currentDagVar) const
        {
            return _conceptPointerToSpecificOperation->evaluate_derivative(operandValues, operandIds, currentDagVar);
        }
#ifdef CUDA_INSTALLED
        template <typename T>
        __device__ T evaluate_on_GPU(const T* operandValues, const int* const operandIds) const
        {
            return (*_d_conceptPointerToSpecificOperation)->evaluate_on_GPU(operandValues, operandIds);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIds, DerivativeInformation& currentDagVar) const
        {
            return (*_d_conceptPointerToSpecificOperation)->evaluate_derivative_on_GPU(operandValues, operandIds, currentDagVar);
        }
#endif // CUDA_INSTALLED

    private:

        // Baseoperation class could be copied, however, unique ptr is not allowed to be copied.
        // std::unique_ptr<Concept> _conceptPointerToSpecificOperation;
        Concept* _conceptPointerToSpecificOperation = NULL;

#ifdef CUDA_INSTALLED
        Concept** _d_conceptPointerToSpecificOperation = NULL;

        template <typename T>
        __host__
        Concept** init_concept_ptr_on_GPU(const T& specificOperation);
#endif // CUDA_INSTALLED
    };

} // namespace SVT_DAG
#endif // BASEOPERATION_H
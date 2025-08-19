#ifndef OPERATIONS_H
#define OPERATIONS_H

#pragma once

#include "baseoperation.h"
#include "filibmath.h"
#include "derivativeinformation.h"

#ifdef CUDA_INSTALLED
#include "CUDA_math.h"  
#include "dagdatatypes.cuh"
#endif // CUDA_INSTALLED

#include <mcfilib.hpp>
#include <cmath>
#include <iostream>

//#define TEST_CHANGES false

namespace INTERVAL_POWER{

	bool inline isInteger(double x)
	{
		double tol = 1e-8;
		if (abs(x - (int)x) < tol) 
            return true;
		return false;
	}

	I_cpu inline pow(I_cpu x, int y) 
	{
		double LB = x.inf(), UB = x.sup();

		if (y == 0) {
			return I_cpu(1., 1.);
		}
		else if (y % 2 == 0) { // Even exponents
			if (LB < 0 && UB < 0)
				return I_cpu(std::pow(UB, y), std::pow(LB, y));
			else if (LB > 0 && UB > 0)
				return I_cpu(std::pow(LB, y), std::pow(UB, y));
			else
				return I_cpu(0., std::pow(std::max(-LB, UB), y));
		}
		else {// Odd exponents
			return I_cpu(std::pow(LB, y), std::pow(UB, y));
		}
	}
	I_cpu inline pow(I_cpu x, double y)
	{
		if (isInteger(y))
			return pow(x, (int)y);
		else
			return I_cpu(std::pow(x.inf(), y), std::pow(x.sup(), y));
	}
	I_cpu inline pow(I_cpu x, I_cpu y)
	{
		double tol = 1e-8;
		if (std::abs(y.inf() - y.sup()) < tol)
			return pow(x, y.inf());

		//if (y.lower() <= 0)
		//	return exp(y * log(interval_gpu<T>(tol, x.upper())));	// !!! We are cutting of the negative part of the exponent. This can lead to wrong results.

		return exp(y * log(x));
	} // No outward rounding used !!!
}

namespace SVT_DAG {

    // The helper function used to calculate the derivative of absolute function
	inline I_cpu abs_derivative(I_cpu const& x)
	{
		if (x.sup() < 0)
			return I_cpu(-1., -1.);
		if (x.inf() < 0 && x.sup() == 0)
			return I_cpu(-1., 0.);
		if (x.inf() == 0 && x.sup() == 0)
			return I_cpu(0., 0.);
		if (x.inf() == 0 && x.sup() > 0)
			return I_cpu(0., 1.);
		if (x.inf() > 0)
			return I_cpu(1., 1.);
		return I_cpu(-1., 1.);
	}

	inline I_cpu intervalUnion(I_cpu const& interval1, I_cpu const& interval2)
	{
		double LB = std::min(interval1.inf(), interval2.inf());
		double UB = std::max(interval1.sup(), interval2.sup());
		return I_cpu(LB, UB);
	}
    
    // The interval arithmetic provided by filib are used for I_cpu
    // For the arithmetic operations between a constant and an interval, the constant should be in double type
    struct Addition
    {
        template <typename T>
        T evaluate(const T* operandValues, const int* const operandIndices) const
        {
            return operandValues[operandIndices[0]] + operandValues[operandIndices[1]];
        }

        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];
            I_cpu g = operandValues[operandIndices[1]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = f + g;            

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];
                    I_cpu d_g = operandValues[operandIndices[1]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = d_f + d_g;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__ T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            // int index0 = operandIndices[0];
            // int index1 = operandIndices[1];
            return operandValues[operandIndices[0]] + operandValues[operandIndices[1]];
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];
            I_gpu g = operandValues[operandIndices[1]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = f + g;            

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];
                    I_gpu d_g = operandValues[operandIndices[1]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = d_f + d_g;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Addition"; }
    };
    //extern BaseOperation opAddition;


    struct Subtraction
    {
        template <typename T>
        T evaluate(const T* operandValues, const int* const operandIndices) const
        {
            return operandValues[operandIndices[0]] - operandValues[operandIndices[1]];
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];
            I_cpu g = operandValues[operandIndices[1]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = f - g;

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];
                    I_cpu d_g = operandValues[operandIndices[1]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = d_f - d_g;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__ T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return operandValues[operandIndices[0]] - operandValues[operandIndices[1]];
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];
            I_gpu g = operandValues[operandIndices[1]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = f - g;

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];
                    I_gpu d_g = operandValues[operandIndices[1]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = d_f - d_g;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Subtraction"; }
    };
    //extern BaseOperation opSubtraction;


    struct Multiplication
    {
        template <typename T>
        T evaluate(const T* operandValues, const int* const operandIndices) const
        {
            return operandValues[operandIndices[0]] * operandValues[operandIndices[1]];
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];
            I_cpu g = operandValues[operandIndices[1]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = f * g;

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];
                    I_cpu d_g = operandValues[operandIndices[1]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = f * d_g + d_f * g;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__ T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return operandValues[operandIndices[0]] * operandValues[operandIndices[1]];
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];
            I_gpu g = operandValues[operandIndices[1]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = f * g;

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];
                    I_gpu d_g = operandValues[operandIndices[1]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = f * d_g + d_f * g;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Multipliation"; }
    };
    //extern BaseOperation opMultiplication;


    struct Division
    {
        template <typename T>
        T evaluate(const T* operandValues, const int* const operandIndices) const
        {
            return operandValues[operandIndices[0]] / operandValues[operandIndices[1]];
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];
            I_cpu g = operandValues[operandIndices[1]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = f / g;

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];
                    I_cpu d_g = operandValues[operandIndices[1]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = (g * d_f - f * d_g) / sqr(g); // ToDO: Use sqr
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__ T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return operandValues[operandIndices[0]] / operandValues[operandIndices[1]];
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];
            I_gpu g = operandValues[operandIndices[1]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = f / g;

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];
                    I_gpu d_g = operandValues[operandIndices[1]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = (g * d_f - f * d_g) / cudaMath::sqr(g); // ToDO: Use sqr
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Division"; }
    };
    //extern BaseOperation opDivision;


    struct Exponential
    {
        template <typename T>
        T evaluate(const T* operandValues, const int* const operandIndices) const
        {
            return exp(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::exp(operandValues[operandIndices[0]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = exp(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = exp(f) * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::exp(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::exp(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = cudaMath::exp(f) * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Exponential"; }
    };
    //extern BaseOperation opExponential;


    struct PowerOperation
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return filib::pow(operandValues[operandIndices[0]], (operandValues[operandIndices[1]]));
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::pow(operandValues[operandIndices[0]], (operandValues[operandIndices[1]]));
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];
            I_cpu g = (operandValues[operandIndices[1]].functionValue_I_cpu[0]);

            currentDagVar.functionValue_I_cpu[0] = INTERVAL_POWER::pow(f, g);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = g * INTERVAL_POWER::pow(f, g - 1.) * d_f; 
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::pow(operandValues[operandIndices[0]], (operandValues[operandIndices[1]]));
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];
            I_gpu g = (operandValues[operandIndices[1]].functionValue_I_gpu[0]);

            currentDagVar.functionValue_I_gpu[0] = cudaMath::pow(f, g);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = g * cudaMath::pow(f, g - 1) * d_f; 
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = I_gpu(0.);
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Power"; }
    };
    //extern BaseOperation opPower;


    struct SquareRootOperation
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return sqrt(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::sqrt(operandValues[operandIndices[0]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = sqrt(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = 0.5 * d_f / sqrt(f);
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::sqrt(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::sqrt(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = 0.5 * d_f / cudaMath::sqrt(f);
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = I_gpu(0.);
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Square Root"; }
    };
    //extern BaseOperation opSquareRoot;



    struct SquareOperation
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return sqr(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return operandValues[operandIndices[0]] * operandValues[operandIndices[0]];
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = sqr(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = 2. * f * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::sqr(operandValues[operandIndices[0]]);
            //return operandValues[operandIndices[0]] * operandValues[operandIndices[0]];
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::sqr(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = 2 * f * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = I_gpu(0.);
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Square"; }
    };
    //extern BaseOperation opSquare;


    struct Negative
    {
        template <typename T>
        T evaluate(const T* operandValues, const int* const operandIndices) const
        {
            return -operandValues[operandIndices[0]];
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = -f;

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = -d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return -(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = -f;

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = -d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Negative"; }
    };

    //extern BaseOperation opNegative;

    
    struct TangensHyperbolicus
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return tanh(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::tanh(operandValues[operandIndices[0]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = tanh(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = (1. - sqr(tanh(f))) * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::tanh(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::tanh(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = (1 - cudaMath::sqr(cudaMath::tanh(f))) * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED
        inline void print() const { std::cout << "Tanh"; }
    };
    //extern BaseOperation opTangensHyperbolicus;



    struct AbsoluteValue
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return abs(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::abs(operandValues[operandIndices[0]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = abs(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    I_cpu absDerivative = abs_derivative(f);

                    currentDagVar.derivativeValue_I_cpu[i] = absDerivative * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::abs(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::abs(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    I_gpu absDerivative = cudaMath::abs_derivative(f);

                    currentDagVar.derivativeValue_I_gpu[i] = absDerivative * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED
        inline void print() const { std::cout << "Abs"; }
    };
    //extern BaseOperation opAbsoluteValue;



    struct Logarithmus
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return log(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::log(operandValues[operandIndices[0]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = log(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = d_f / f;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::log(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::log(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = d_f / f;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED
        inline void print() const { std::cout << "Log"; }
    };
    //extern BaseOperation opLogarithmus;


    struct Cosinus
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return cos(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::cos(operandValues[operandIndices[0]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = cos(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = -sin(f) * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::cos(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::cos(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = -cudaMath::sin(f) * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED
        inline void print() const { std::cout << "Cos"; }
    };
    //extern BaseOperation opCosinus;

    struct Sinus
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return sin(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::sin(operandValues[operandIndices[0]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = sin(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = cos(f) * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::sin(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::sin(f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = cudaMath::cos(f) * d_f;
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED
        inline void print() const { std::cout << "Sin"; }
    };
    //extern BaseOperation opSinus;


    struct Inverse
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return I_cpu(1,1)/(operandValues[operandIndices[0]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return 1/(operandValues[operandIndices[0]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = 1. / (f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];

                    currentDagVar.derivativeValue_I_cpu[i] = - d_f / sqr(f);
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return 1/(operandValues[operandIndices[0]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = 1 / (f);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];

                    currentDagVar.derivativeValue_I_gpu[i] = - d_f / cudaMath::sqr(f);
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = 0;
                }
            }
        }
#endif // CUDA_INSTALLED
        inline void print() const { std::cout << "Inverse"; }
    };
    //extern BaseOperation opInverse;



    struct Maximum
    {
        I_cpu evaluate(const I_cpu* operandValues, const int* const operandIndices) const
        {
            return filib::max(operandValues[operandIndices[0]], operandValues[operandIndices[1]]);
        }
        double evaluate(const double* operandValues, const int* const operandIndices) const
        {
            return std::max(operandValues[operandIndices[0]], operandValues[operandIndices[1]]);
        }
        void evaluate_derivative(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_cpu f = operandValues[operandIndices[0]].functionValue_I_cpu[0];
            I_cpu g = operandValues[operandIndices[1]].functionValue_I_cpu[0];

            currentDagVar.functionValue_I_cpu[0] = max(f, g);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_CPU[i]) {
                    I_cpu d_f = operandValues[operandIndices[0]].derivativeValue_I_cpu[i];
                    I_cpu d_g = operandValues[operandIndices[1]].derivativeValue_I_cpu[i];

                    if (f.inf() > g.sup())
                        currentDagVar.derivativeValue_I_cpu[i] = d_f;
                    else if (g.inf() > f.sup())
                        currentDagVar.derivativeValue_I_cpu[i] = d_g;
                    else 
                        currentDagVar.derivativeValue_I_cpu[i] = intervalUnion(d_f, d_g);
                }
                else {
                    currentDagVar.derivativeValue_I_cpu[i] = 0.;
                }
            }
        }

#ifdef CUDA_INSTALLED
        template <typename T>
        __device__
            T evaluate_on_GPU(const T* operandValues, const int* const operandIndices) const
        {
            return cudaMath::max(operandValues[operandIndices[0]], operandValues[operandIndices[1]]);
        }

        __device__ void evaluate_derivative_on_GPU(const DerivativeInformation* operandValues, const int* const operandIndices, DerivativeInformation& currentDagVar) const
        {
            I_gpu f = operandValues[operandIndices[0]].functionValue_I_gpu[0];
            I_gpu g = operandValues[operandIndices[1]].functionValue_I_gpu[0];

            currentDagVar.functionValue_I_gpu[0] = cudaMath::max(f, g);

            for (int i = 0; i < currentDagVar.numIndependentVariables; i++) {
                if (currentDagVar.isDependentOfIndependentVariable_GPU[i]) {
                    I_gpu d_f = operandValues[operandIndices[0]].derivativeValue_I_gpu[i];
                    I_gpu d_g = operandValues[operandIndices[1]].derivativeValue_I_gpu[i];

                    if (f.lower() > g.upper())
                        currentDagVar.derivativeValue_I_gpu[i] = d_f;
                    else if (g.lower() > f.upper())
                        currentDagVar.derivativeValue_I_gpu[i] = d_g;
                    else 
                        currentDagVar.derivativeValue_I_gpu[i] = cudaMath::intervalUnion(d_f, d_g);
                }
                else {
                    currentDagVar.derivativeValue_I_gpu[i] = I_gpu(0.);
                }
            }
        }
#endif // CUDA_INSTALLED

        inline void print() const { std::cout << "Maximum"; }
    };
    //extern BaseOperation opMaximum;
} // namespace SVT_DAG

#endif // OPERATIONS_H
/***********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file kernel.h
*
* @brief File containing declaration of kernel classes
*
**********************************************************************************/

#pragma once

#include <vector>
#include <memory>

namespace melon {
	namespace kernel {

		/**
		* @class Kernel
		* @brief Abstract parent class for kernel implementations
		*/
		template <typename T, typename V>
		class Kernel {
		public:

			// Deduces kernel return type, depending on template parameters
			using RET = decltype(std::declval<T>() + std::declval<V>());

			/**
			* @brief Destructor
			*/
			virtual ~Kernel() = default;

			/**
			*  @brief Function for evalualting the kernel for the points x1 and x2
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*
			*  @return returns the result of the kernel evaluation
			*/
			virtual RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2) = 0;
		};


		/**
		* @class Stationary Kernel
		* @brief Abstract parent class for stationary kernel implementations
		*/
		template <typename T, typename V>
		class StationaryKernel : public Kernel<T, V> {
		public:

			using typename Kernel<T, V> ::RET;

			/**
			*  @brief Calculates the quadratic distance between two points x1 and x2
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*/
			virtual RET _quadratic_distance(std::vector<T> x1, std::vector<V> x2) {
				RET distance = 0;

				for (size_t i = 0; i < x1.size(); i++) {		// i the demension of X and X_test
					distance += pow(x1.at(i) - x2.at(i), 2);
				}

				return distance;
			};

			/**
			*  @brief Function for evalualting the kernel for a given distance
			*
			*  @param[in] distance is a distance between two points for which the kernel is evaluated
			*
			*  @return returns the result of the kernel evaluation
			*/
			virtual RET evaluate_kernel(RET distance) = 0; // works only for stationary kernels

			/**
			*  @brief Function for calculating the distance used in the kernel (type of distance used can vary among kernels)
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*
			*  @return returns the distance used in the kernel
			*/
			virtual RET calculate_distance(std::vector<T> x1, std::vector<V> x2) = 0;
		};


		/**
		* @class KernelCompositeAdd
		* @brief Composite kernel which on evaluation adds the evaluation results of its subkernels
		*/
		template <typename T, typename V>
		class KernelCompositeAdd : public Kernel<T, V> {
		public:

			using typename Kernel<T, V> ::RET;

			/**
			*  @brief Function for adding another subkernel to the composite kernel
			*
			*  @param[in] kernel is the subkernel to be added
			*/
			void add(std::shared_ptr<Kernel<T, V>> kernel) { children.push_back(kernel); }

			/**
			*  @brief Function for evalualting the kernel
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*
			*  @return returns the result of the kernel evaluation
			*/
			RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2) {
				RET value = 0;
				for (auto kernel : children) {
					value += kernel->evaluate_kernel(x1, x2);
				}
				return value;
			}

		private:
			std::vector<std::shared_ptr<Kernel<T, V>>> children;   /*!< Vector containing the subkernels */
		};

		/**
		* @class KernelCompositeMultiply
		* @brief Composite kernel which on evaluation multiplies the evaluation results of its subkernels
		*/
		template <typename T, typename V>
		class KernelCompositeMultiply : public Kernel<T, V> {
		public:

			using typename Kernel<T, V> ::RET;

			/**
			*  @brief Function for adding another subkernel to the composite kernel
			*
			*  @param[in] kernel is the subkernel to be added
			*/
			void add(std::shared_ptr<Kernel<T, V>> kernel) { children.push_back(kernel); }

			/**
			*  @brief Function for evalualting the kernel
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*
			*  @return returns the result of the kernel evaluation
			*/
			RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2) {
				RET value = 1;
				for (auto kernel : children) {
					value *= kernel->k(x1, x2);
				}
				return value;
			}

		private:
			std::vector<std::shared_ptr<Kernel<T, V>>> children;       /*!< Vector containing the subkernels */
		};

		/**
		* @class KernelConstant
		* @brief Kernel which always returns a constant value
		*/
		template <typename T, typename V>
		class KernelConstant : public Kernel<T, V> {
		public:

			using typename Kernel<T, V> ::RET;

			/**
			*  @brief Constructor. Initializes the kernels return value to 1.
			*/
			KernelConstant() : _f(1) {};

			/**
			*  @brief Constructor.
			*
			*  @param[in] f is the value to be returned by the kernel
			*/
			KernelConstant(const T f) : _f(f) {};

			/**
			*  @brief Constructor.
			*
			*  @param[in] f is the value to be returned by the kernel
			*/
			KernelConstant(const V f) : _f(f) {};

			/**
			*  @brief Function for evalualting the kernel
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*
			*  @return returns the result of the kernel evaluation
			*/
			RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2) {
				return _f;
			}

		private:
			const RET _f;     /*!< Return value of the kernel*/
		};


		/**
		* @class KernelRBF
		* @brief Implementation of Radial Basis Function kernel
		*/
		template <typename T, typename V>
		class KernelRBF : public StationaryKernel<T, V> {
		public:

			using typename Kernel<T, V> ::RET;

			/**
			*  @brief Constructor.
			*
			*  @param[in] gamma is the value for the gamma parameter of the rbf kernel
			*/
			KernelRBF(const double gamma) : _gamma(gamma) {};


			/**
			*  @brief Function for evalualting the kernel
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*
			*  @return returns the result of the kernel evaluation
			*/
			RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2) override {

				RET distance = calculate_distance(x1, x2);
				return evaluate_kernel(distance);
			}

			/**
			*  @brief Function for calculating the distance used in the kernel (type of distance used can vary among kernels)
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*
			*  @return returns the distance used in the kernel
			*/
			RET calculate_distance(std::vector<T> x1, std::vector<V> x2) override {
				return this->_quadratic_distance(x1, x2);
			}

			/**
			*  @brief Function for evalualting the kernel for a given distance
			*
			*  @param[in] distance is a distance between two points for which the kernel is evaluated
			*
			*  @return returns the result of the kernel evaluation
			*/
			RET evaluate_kernel(RET distance) override {

				return exp(-_gamma * distance);

			}

		private:
			const double _gamma;
		};

	}

}

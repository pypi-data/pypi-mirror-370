/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file gp_data.h
*
* @brief File containing declaration of matern kernel classes
*
**********************************************************************************/

#pragma once

#include "kernel.h"

#define USE_TAYLORMADE_RELAXATIONS
//#undef USE_TAYLORMADE_RELAXATIONS

#ifdef USE_TAYLORMADE_RELAXATIONS
#include <ffunc.hpp>
#endif


namespace melon {
    namespace kernel {


#ifdef USE_TAYLORMADE_RELAXATIONS

        using mc::covariance_function;

        template <typename T> inline T
            covar_matern_1(const T& x) {
            return covariance_function(x, 1);
        }

        template <typename T> inline T
            covar_matern_3
            (const T& x) {
            return covariance_function(x, 2);
        }

        template <typename T> inline T
            covar_matern_5
            (const T& x) {
            return covariance_function(x, 3);
        }

        template <typename T> inline T
            covar_sqrexp
            (const T& x) {
            return covariance_function(x, 4);
        }

#endif
        /**
        * @struct KernelData
        * @brief struct containing kernel parameters
        */
        struct KernelData {
            double sf2;
            std::vector<double> ell;
        };

        /**
        * @class Matern
        * @brief Abstract parent class for matern kernels
        */
        template <typename T, typename V>
        class Matern : public StationaryKernel<T, V> {
        public:
            Matern();
            Matern(std::shared_ptr<const KernelData> data);

        protected:
            using typename Kernel<T, V>::RET;

            std::shared_ptr<const KernelData> _data;    /*!< KernelData object containing the kernel parameters */

			/**
			*  @brief Calculates the quadratic distance between two points x1 and x2
			*
			*  @param[in] x1 is a vector containing the first point
			*
			*  @param[in] x2 is a vector containing the second point
			*/
			RET _quadratic_distance(std::vector<T> x1, std::vector<V> x2) override {
				RET distance = 0;

				for (size_t i = 0; i < x1.size(); i++) {		// i the demension of X and X_test
					distance += pow(x1.at(i) - x2.at(i), 2) / pow(Matern<T, V>::_data->ell.at(i), 2);
				}

				return distance;
			};

            /**
            *  @brief Calculates the euclidian distance from the quadratic distance
            *
            *  @param[in] quadraticDistance is the quadraticDistance between two points which iis transformed into the euclidian distance
            */
            auto _euclidian_distance(RET quadraticDistance) {

                double const epsilon = 1e-16;
                // Small number to avoid gradient calculation of sqrt(x) function at x = 0. 
                // Otherwise this leads to longer computation time of IPOPT iterations in the preprocessing. (SLSQP works very quick with epsilon = 0).
                // In an example, epsilon =  1e-16 leads to an error of the prediction in the order of 1e-8. 
                // We accept this error.

                auto distance = quadraticDistance + epsilon;
                distance = sqrt(distance);

                return distance;
            };
        };

        /**
        * @class Matern12
        * @brief Class implementation of Matern12 kernel
        */
        template <typename T, typename V>
        class Matern12 : public Matern<T, V> {
        public:
            using Matern<T, V>::Matern;
            using typename Kernel<T, V>::RET;

            RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2);
            RET evaluate_kernel(RET distance);
            RET calculate_distance(std::vector<T> x1, std::vector<V> x2);
        };

        /**
        * @class Matern32
        * @brief Class implementation of Matern32 kernel
        */
        template <typename T, typename V>
        class Matern32 : public Matern<T, V> {
        public:
            using Matern<T, V>::Matern;
            using typename Kernel<T, V>::RET;

            RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2);
            RET evaluate_kernel(RET distance);
            RET calculate_distance(std::vector<T> x1, std::vector<V> x2);
        };

        /**
        * @class Matern52
        * @brief Class implementation of Matern52 kernel
        */
        template <typename T, typename V>
        class Matern52 : public Matern<T, V> {
        public:
            using Matern<T, V>::Matern;
            using typename Kernel<T, V>::RET;

            RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2);
            RET evaluate_kernel(RET distance);
            RET calculate_distance(std::vector<T> x1, std::vector<V> x2);
        };

        /**
        * @class MaternInf
        * @brief Class implementation of MaternInf kernel
        */
        template <typename T, typename V>
        class MaternInf : public Matern<T, V> {
        public:
            using Matern<T, V>::Matern;
            using typename Kernel<T, V>::RET;

            RET evaluate_kernel(std::vector<T> x1, std::vector<V> x2);
            RET evaluate_kernel(RET distance);
            RET calculate_distance(std::vector<T> x1, std::vector<V> x2);
        };

        /**
        * Implementation
        */

        template<typename T, typename V>
        Matern<T, V>::Matern() {}

        template<typename T, typename V>
        Matern<T, V>::Matern(std::shared_ptr<const KernelData> data) : Matern() {
            Matern<T, V>::_data = data;
        }


        // ---------------------------------------------------------------------------------
        // Matern1/2
        // ---------------------------------------------------------------------------------

        template<typename T, typename V>
        typename Matern12<T,V>::RET Matern12<T, V>::evaluate_kernel(RET distance) {

#ifdef USE_TAYLORMADE_RELAXATIONS
            return Matern<T, V>::_data->sf2 * covar_matern_1(distance);
#else
            RET euclidianDistance = sqrt(distance + 1e-16);
            return Matern<T, V>::_data->sf2 *  exp(-euclidianDistance);
#endif
        }

        template<typename T, typename V>
		typename Matern12<T, V>::RET Matern12<T, V>::evaluate_kernel(std::vector<T> x1, std::vector<V> x2) {
            RET distances = calculate_distance(x1, x2);
            return evaluate_kernel(distances);
        }

        template<typename T, typename V>
		typename Matern12<T, V>::RET Matern12<T, V>::calculate_distance(std::vector<T> x1, std::vector<V> x2) {
            return this->_quadratic_distance(x1, x2);
        }


        // ---------------------------------------------------------------------------------
        // Matern3/2
        // ---------------------------------------------------------------------------------

        template<typename T, typename V>
		typename Matern32<T, V>::RET Matern32<T, V>::evaluate_kernel(RET distance) {

#ifdef USE_TAYLORMADE_RELAXATIONS
            return Matern<T, V>::_data->sf2 * covar_matern_3(distance);
#else
            RET euclidianDistance = sqrt(distance + 1e-16);
            RET sqrtK = sqrt(3.0) * euclidianDistance;
            // we multiply the covariance function out because we found that it has tighter relaxations
            return Matern<T, V>::_data->sf2 * (exp(-sqrtK) + sqrtK * exp(-sqrtK));
#endif

        }


        template<typename T, typename V>
		typename Matern32<T, V>::RET Matern32<T, V>::evaluate_kernel(std::vector<T> x1, std::vector<V> x2) {
            RET distances = calculate_distance(x1, x2);
            return evaluate_kernel(distances);
        }

        template<typename T, typename V>
		typename Matern32<T, V>::RET Matern32<T, V>::calculate_distance(std::vector<T> x1, std::vector<V> x2) {
            return this->_quadratic_distance(x1, x2);
        }


        // ---------------------------------------------------------------------------------
        // Matern5/2
        // ---------------------------------------------------------------------------------

        template<typename T, typename V>
		typename Matern52<T, V>::RET Matern52<T, V>::evaluate_kernel(RET distance) {

#ifdef USE_TAYLORMADE_RELAXATIONS
            // use xexpax as envelope is implemented. return _data->sf2 * (1 + sqrtK) * exp(-sqrtK);
            return Matern<T, V>::_data->sf2 * covar_matern_5(distance);
#else
            RET euclidianDistance = sqrt(distance + 1e-16);
            RET sqrtK = sqrt(5.0) * euclidianDistance;
            RET sqrtK2_3 = 5. / 3. * distance;
            // we multiply the covariance function out because we found that it has tighter relaxations
            // return Matern<T, V>::_data->sf2 * (1 + sqrtK + sqrtK2_3) * exp(-sqrtK);
            return Matern<T, V>::_data->sf2 * (exp(-sqrtK) + sqrtK * exp(-sqrtK) + sqrtK2_3 * exp(-sqrtK));
#endif

        }

        template<typename T, typename V>
		typename Matern52<T, V>::RET Matern52<T, V>::evaluate_kernel(std::vector<T> x1, std::vector<V> x2) {
            RET distances = calculate_distance(x1, x2);
            return evaluate_kernel(distances);
        }

        template<typename T, typename V>
		typename Matern52<T, V>::RET Matern52<T, V>::calculate_distance(std::vector<T> x1, std::vector<V> x2) {
            return this->_quadratic_distance(x1, x2);
        }


        // ---------------------------------------------------------------------------------
        // MaternInf (squared exponential)
        // ---------------------------------------------------------------------------------

        template<typename T, typename V>
		typename MaternInf<T, V>::RET MaternInf<T, V>::evaluate_kernel(RET distance) {

#ifdef USE_TAYLORMADE_RELAXATIONS
            return Matern<T, V>::_data->sf2 * covar_sqrexp(distance);
#else
            return Matern<T, V>::_data->sf2 * exp(-0.5 * distance);
#endif

        }

        template<typename T, typename V>
		typename MaternInf<T, V>::RET MaternInf<T, V>::evaluate_kernel(std::vector<T> x1, std::vector<V> x2) {
            RET distances = calculate_distance(x1, x2);
            return evaluate_kernel(distances);
        }


        template<typename T, typename V>
		typename MaternInf<T, V>::RET MaternInf<T, V>::calculate_distance(std::vector<T> x1, std::vector<V> x2) {
            return this->_quadratic_distance(x1, x2);
        }
    }
}

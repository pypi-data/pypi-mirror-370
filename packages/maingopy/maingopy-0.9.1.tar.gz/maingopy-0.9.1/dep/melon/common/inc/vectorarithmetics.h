/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file vectorarithmetics.h
*
* @brief File containing overloaded vector functions for performing linear algebra operations.
*
**********************************************************************************/

#pragma once

#include <vector>		// std::vector
#include <numeric>		// std::inner_product
#include <algorithm>	// std::transform
#include <cassert>		// std::assert

namespace melon {
    /**
    *  @brief Overloaded operator for vector class allowing adding vectors
    *
    *  @param[in] v1 is the first summand vector
    *
    *  @param[in] v2 is the second summand vector
    *
    *  @return returns a vector res = v1 + v2
    */
    template <typename T, typename U>
    auto operator+(const std::vector<T> &v1, const std::vector<U> &v2) {
        assert(v1.size() == v2.size());
        std::vector<decltype(T(1) + U(1))> result;
        result.reserve(v1.size());
        std::transform(std::begin(v1), std::end(v1), std::begin(v2), std::back_inserter(result), [](T i, U j) { return i + j; });
        return result;
    };

    /**
    *  @brief Overloaded operator for vector class allowing adding scalars to vectors
    *
    *  @param[in] v is the summand vector
    *
    *  @param[in] s is the summand scalar
    *
    *  @return returns a vector res = v1 + v2
    */
    template <typename T, typename U>
    auto operator+(const std::vector<T> &v, const U s) {
        std::vector<decltype(T(1) + U(1))> result;
        result.reserve(v.size());
        std::transform(std::begin(v), std::end(v), std::back_inserter(result), [s](T i) {return i + s; });
        return result;
    }

    /**
    *  @brief Overloaded operator for vector class allowing substracting vectors
    *
    *  @param[in] v1 is the minuend vector
    *
    *  @param[in] v2 is the subtrahend vector
    *
    *  @return returns a result vector res = v1 - v2
    */
    template <typename T, typename U>
    auto operator-(std::vector<T> &v1, std::vector<U> &v2) {
        assert(v1.size() == v2.size());
        std::vector<decltype(v1.at(0) - v2.at(0))> result;
        result.reserve(v1.size());
        std::transform(std::begin(v1), std::end(v1), std::begin(v2), std::back_inserter(result), [](T i, U j) { return i - j; });
        return result;
    };

    /**
    *  @brief Overloaded operator for vector class allowing substracting scalars from vectors
    *
    *  @param[in] v is the minuend vector
    *
    *  @param[in] s is the subtrahend scalar
    *
    *  @return returns a result vector res = v1 - v2
    */
    template <typename T, typename U>
    auto operator-(const std::vector<T> &v, const U s) {
        std::vector<decltype(T(1) - U(1))> result;
        result.reserve(v.size());
        std::transform(std::begin(v), std::end(v), std::back_inserter(result), [s](T i) {return i - s; });
        return result;
    }

    /**
    *  @brief Overloaded operator for vector class allowing the calulation of a vector scalar product
    *
    *  @param[in] s is the scalar factor
    *
    *  @param[in] v is the factor vector
    *
    *  @return returns a result vector res = s*v
    */
    template <typename T, typename U>
    auto operator*(const T &s, const std::vector<U> &v) {
        std::vector<decltype(T(1) * U(1))> result;
        result.reserve(v.size());
        std::transform(std::begin(v), std::end(v), std::back_inserter(result), [s](U i) {return i * s; });
        return result;
    }

    /**
    *  @brief Overloaded operator for vector class allowing the calulation of a vector scalar product
    *
    *  @param[in] v is the factor vector
    *
    *  @param[in] s is the scalar factor
    *
    *  @return returns a result vector res = v*s
    */
    template <typename T, typename U>
    auto operator*(const std::vector<T> &v, const U &s) {
        std::vector<decltype(T(1) * U(1))> result;
        result.reserve(v.size());
        std::transform(std::begin(v), std::end(v), std::back_inserter(result), [s](T i) {return i * s; });
        return result;
    }

    /**
    *  @brief Overloaded operator for vector class allowing the calulation of a vector scalar division
    *
    *  @param[in] v is the dividend vector
    *
    *  @param[in] s is the scalar divisor
    *
    *  @return returns a result vector res = v/s
    */
    template <typename T, typename U>
    auto operator/(const std::vector<T>& v, const U& s) {
        std::vector<decltype(T(1) / U(1))> result;
        result.reserve(v.size());
        std::transform(std::begin(v), std::end(v), std::back_inserter(result), [s](T i) {return i / s; });
        return result;
    }

    /**
    *  @brief Overloaded operator for vector class allowing the calulation of dot product of two vectors
    *
    *  @param[in] v1 is the first vector
    *
    *  @param[in] v2 is the second vector
    *
    *  @return returns a result vector res = v1^T * v2
    */
    template <typename T, typename U>
    auto dot_product(const std::vector<T> &v1, const std::vector<U> &v2) {
        assert(v1.size() == v2.size());

        return std::inner_product(std::begin(v1), std::end(v1), std::begin(v2), T(0)*U(0));
    }

    /**
    *  @brief Overloaded operator for vector class allowing the calulation of a matrix vector product
    *
    *  @param[in] m is the matrix to be multiplied
    *
    *  @param[in] v ist the factor vector
    *
    *  @return returns a result vector res = m*v
    */
    template <typename T, typename U>
    auto operator*(const std::vector<std::vector<T>> &m, const std::vector<U> &v) {
        std::vector<decltype(T(1)*U(1))> result;
        result.reserve(v.size());
        std::transform(std::begin(m), std::end(m), std::back_inserter(result), [v](std::vector<T> m_i) {return dot_product(m_i, v); });

        return result;
    }

    /**
    *  @brief Overloaded operator for vector class allowing the calulation of a matrix matrix product
    *
    *  @param[in] m1 is the first matrix factor
    *
    *  @param[in] m2 is the second matrix factor
    *
    *  @return returns a result vector res = m*m
    */
    template <typename T, typename U>
    auto operator*(const std::vector<std::vector<T>> &m1, const std::vector<std::vector<U>> &m2) {
        assert(m1.at(0).size() == m2.size());
        std::vector<std::vector<decltype(T(1) * U(1))>> result;
        result.reserve(m1.size());
        std::transform(std::begin(m2), std::end(m2), std::back_inserter(result), [m1](std::vector<U> m_i) {return m1 * m_i; });

        return result;
    }

    /**
    *  @brief Overloaded operator for vector class allowing to transpose a matrix
    *
    *  @param[in] m is the matrix to be transposed
    *
    *  @return returns a result vector res = m^T
    */
    template <typename T>
    auto transpose(const std::vector<std::vector<T>> &m) {
        std::vector<std::vector<T>> result(m.at(0).size(), std::vector<T>(m.size()));
        for (std::vector<int>::size_type i = 0; i < m.size(); i++) {
            for (size_t j = 0; j < m[0].size(); j++) {
                result.at(j).at(i) = m.at(i).at(j);
            }
        }
        return result;
    }

    /**
    *  @brief Overloaded operator for vector class allowing to obtain a matrix diagonal
    *
    *  @param[in] m is the matrix of which the diagonal is obtained
    *
    *  @return returns a result vector res = diag(m)
    */
    template <typename T>
    auto diag(const std::vector<std::vector<T>> &m) {
        assert(m.size() == m.at(0).size());
        std::vector<T> result;
        for (size_t i = 0; i < m.size(); i++)
        {
            result.push_back(m.at(i).at(i));
        }
        return result;
    }
}

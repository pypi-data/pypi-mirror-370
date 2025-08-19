/**********************************************************************************
 * Copyright (c) 2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include <algorithm>
#include <array>
#include <stdexcept>
#include <vector>
#include <string>
#include <memory>

namespace ale {

namespace helper {
    template <typename T, size_t N, size_t... I>
    constexpr std::array<std::remove_cv_t<T>, N>
    to_array_impl(T a[N], std::index_sequence<I...>) {
        return { { a[I]... } };
    }
} // namespace helper

/**
 * Convert C-style array to std::array
 * This should already be a library function in C++20
 */
template <typename T, size_t N>
constexpr std::array<std::remove_cv_t<T>, N> to_array(T a[N]) {
    return ale::helper::to_array_impl<T, N>(a, std::make_index_sequence<N> {});
}

template <typename TType, unsigned IDim>
class tensor_ref;

template <typename TType, unsigned IDim>
class tensor_cref;

namespace helper {
    template <typename TType, unsigned IDim>
    class tensor_ref_base;
}

/**
 * Represents a tensor with elements of type TType and IDim dimensions.
 * This class only implements the most basic modifications and casts to
 * references.
 */
template <typename TType, unsigned IDim>
class tensor {
public:
    /**
   * Default initialize with shape {0, ..., 0}
   */
    tensor() { }

    /**
   * Initialize a tensor of given shape with init value.
   */
    tensor(const std::array<size_t, IDim> &shape, TType init = TType()) :
        m_shape(shape) {
        // calculate number of elements
        size_t size = 1;
        for(size_t i = 0; i < shape.size(); ++i) {
            size *= shape.at(i);
        }

        // initialize m_data
        m_data.reset(new TType[size]);
        ref().initialize(init);
    }

    /**
   * Initialize a tensor of given shape with init value.
   */
    tensor(size_t shape[IDim], TType init = TType()) :
        tensor(to_array<size_t, IDim>(shape), init) { }

    //
    // copy constructors
    //

    tensor(const tensor<TType, IDim> &other) :
        tensor(other.cref()) { }

    tensor(const tensor_ref<TType, IDim> &other) :
        tensor(tensor_cref { other }) { }

    tensor(const tensor_cref<TType, IDim> &other) {
        std::copy_n(other.shape().begin(), IDim, m_shape.begin());

        // calculate number of elements
        size_t size = 1;
        for(size_t i = 0; i < m_shape.size(); ++i) {
            size *= m_shape.at(i);
        }

        // initialize m_data
        m_data.reset(new TType[size]);
        ref().copy_initialize(other);
    }

    /**
   * Return the shape of the tensor
   */
    std::array<size_t, IDim> shape() const { return m_shape; }

    /**
   * Return the shape of the tensor at dimension dim
   */
    size_t shape(unsigned dim) const {
        if(dim >= IDim) {
            throw std::invalid_argument("Tensor access out of bounds.");
        }
        return shape()[dim];
    }

    /**
   * Resize the tensor keeping existing values and filling new entries with init
   */
    void resize(const std::array<size_t, IDim> &shape, TType init = TType()) {
        tensor<TType, IDim> temp(shape, init);
        temp.ref().copy_initialize(*this, init);
        swap(temp);
    }

    /**
   * Resize the tensor keeping existing values and filling new entries with init
   */
    void resize(size_t shape[IDim], TType init = TType()) {
        resize(to_array<size_t, IDim>(shape), init);
    }

    /**
   * Swap two tensors
   */
    void swap(tensor<TType, IDim> &other) {
        std::swap(m_shape, other.m_shape);
        std::swap(m_data, other.m_data);
    }

    //
    // overloaded access operators
    //

    std::conditional_t<IDim == 1, TType &, tensor_ref<TType, IDim - 1>>
    operator[](size_t index) {
        return ref()[index];
    }

    std::conditional_t<IDim == 1, const TType &, tensor_cref<TType, IDim - 1>>
    operator[](size_t index) const {
        return cref()[index];
    }

    TType &operator[](const size_t indexes[IDim]) { return ref()[indexes]; }

    const TType &operator[](const size_t indexes[IDim]) const {
        return cref()[indexes];
    }

    /**
   * Return a reference object to this tensor which is cheap to copy.
   */
    tensor_ref<TType, IDim> ref() { return tensor_ref<TType, IDim> { *this }; }

    /**
   * Return a const reference object to this tensor which is cheap to copy.
   */
    tensor_cref<TType, IDim> cref() const {
        return tensor_cref<TType, IDim> { *this };
    }

protected:
    std::shared_ptr<TType[]> m_data {};
    std::array<size_t, IDim> m_shape {};

    friend class ale::helper::tensor_ref_base<TType, IDim>;
};

namespace helper {
    /**
 * Implements common functions to tensor_ref and tensor_cref
 */
    template <typename TType, unsigned IDim>
    class tensor_ref_base {
    protected:
        /**
   * Initialize tensor_ref_base from tensor
   * Copies shape and data ptr and initializes fixed_indexes with empty vector
   */
        tensor_ref_base(const tensor<TType, IDim> &other) :
            m_data(other.m_data),
            m_shape(other.m_shape.begin(), other.m_shape.end()) { }

        /**
   * Initialize tensor_ref_base from an index and a tensor_ref_base of higher
   * dimension This copies the tensor_ref_base and appends the new index to the
   * fixed_indexes
   */
        tensor_ref_base(const tensor_ref_base<TType, IDim + 1> &other, size_t index) :
            m_data(other.m_data), m_shape(other.m_shape),
            m_fixed_indexes(other.m_fixed_indexes) {
            m_fixed_indexes.push_back(index);
        }

        /**
   * Return the shape of the tensor
   */
        std::array<size_t, IDim> shape() const {
            // return the last IDim entries of m_shape
            std::array<size_t, IDim> tmp;
            std::copy_n(m_shape.end() - IDim, IDim, tmp.begin());
            return tmp;
        }

        /**
   * Return the shape of the tensor at dimension dim
   */
        size_t shape(unsigned dim) const {
            if(dim >= IDim) {
                throw std::invalid_argument("Tensor access out of bounds.");
            }
            return shape()[dim];
        }

        /**
   * Get the number of elements in the tensor that this reference points to.
   */
        size_t get_size() const { return get_subsize(m_fixed_indexes.size()); }

        /**
   * Get a pointer to the start of the data that this reference points to.
   */
        TType *get_data_ptr() { return m_data.get() + get_offset(); }

        /**
   * Get a pointer to the start of the data that this reference points to.
   */
        const TType *get_data_ptr() const { return m_data.get() + get_offset(); }

    private:
        /**
   * Get the offset from the beginning of the tensors data to the beginning
   * of this subtensors data
   */
        size_t get_offset() const {
            size_t offset = 0;
            for(size_t i = 0; i < m_fixed_indexes.size(); ++i) {
                offset += get_subsize(i + 1) * m_fixed_indexes.at(i);
            }
            return offset;
        }

        /**
   * Get the number of elements in the tensor to which a reference with
   * k fixed indexes points
   */
        size_t get_subsize(size_t k) const {
            size_t size = 1;
            for(size_t i = k; i < m_shape.size(); ++i) {
                size *= m_shape.at(i);
            }
            return size;
        }

        std::shared_ptr<TType[]>
          m_data {};                    // points to the beginning of the tensors data
        std::vector<size_t> m_shape {}; // stores the full shape of the referenced
                                        // tensor (might be more than IDim)
        std::vector<size_t>
          m_fixed_indexes {}; // stores which subtensor this reference points to

        friend class tensor_ref_base<TType, IDim - 1>;
    };

} // namespace helper

/**
 * Constant reference to a tensor
 */
template <typename TType, unsigned IDim>
class tensor_cref : ale::helper::tensor_ref_base<TType, IDim> {
    using base = ale::helper::tensor_ref_base<TType, IDim>;

public:
    /**
   * Create const reference to a tensor
   */
    tensor_cref(const tensor<TType, IDim> &other) :
        base(other) { }

    /**
   * Create a const reference from a non-const reference
   */
    tensor_cref(const tensor_ref<TType, IDim> &other) :
        base(other) { }

    // expose shape function
    using base::shape;

    //
    // overloaded access operators
    //

    std::conditional_t<IDim == 1, const TType &, tensor_cref<TType, IDim - 1>>
    operator[](size_t index) const {
        if(index >= shape(0)) {
            throw std::invalid_argument("index out of bounds");
        }
        if constexpr(IDim == 1) {
            ;
            return get_data_ptr()[index];
        } else {
            return tensor_cref<TType, IDim - 1>(*this, index);
        }
    }

    const TType &operator[](const size_t indexes[IDim]) const {
        if constexpr(IDim == 1) {
            return (*this)[indexes[0]];
        } else {
            return (*this)[indexes[0]][indexes + 1];
        }
    }

private:
    tensor_cref(const tensor_cref<TType, IDim + 1> &other, size_t new_index) :
        base(other, new_index) { }

    using base::get_data_ptr;

    template <typename UType, unsigned JDim>
    friend class tensor_ref;

    friend class tensor_cref<TType, IDim + 1>;
    friend class tensor_cref<TType, IDim - 1>;
};

/**
 * Reference to a tensor
 * This class implements some ways to modify tensors
 */
template <typename TType, unsigned IDim>
class tensor_ref : ale::helper::tensor_ref_base<TType, IDim> {
    using base = ale::helper::tensor_ref_base<TType, IDim>;

public:
    /**
   * Create reference to a tensor
   */
    tensor_ref(const tensor<TType, IDim> &other) :
        base(other) { }

    // expose shape function
    using base::shape;

    /**
   * Copy values from a const reference. This method will throw an error if the
   * shapes of the tensors are not equal.
   */
    template <typename UType>
    void assign(const tensor_cref<UType, IDim> &other) {
        if(shape() != other.shape()) {
            throw std::invalid_argument(
              "tensors of unmatching shape cannot be assigned");
        }
        std::copy_n(other.get_data_ptr(), get_size(), get_data_ptr());
    }

    /**
   * Copy values from a reference. This method will throw an error if the shapes
   * of the tensors are not equal.
   */
    template <typename UType>
    void assign(const tensor_ref<UType, IDim> &other) {
        assign(tensor_cref { other });
    }

    /**
   * Copy values from another tensor. This method will throw an error if the
   * shapes of the tensors are not equal.
   */
    template <typename UType>
    void assign(const tensor<UType, IDim> &other) {
        assign(other.cref());
    }

    /**
   * Set each element of the tensor this reference points to the given value.
   */
    void initialize(TType init = TType()) {
        std::fill_n(get_data_ptr(), get_size(), init);
    }

    /**
   * Copy values from a const reference. In case the shapes do not match
   * the values will be ignored or filled with the init value.
   */
    void copy_initialize(const tensor_cref<TType, IDim> &other,
      TType init = TType()) {
        if(shape() == other.shape()) {
            // since the shapes match, use the more efficient assign
            assign(other);
        } else {
            auto min_shape = std::min(shape(0), other.shape(0));
            if constexpr(IDim == 1) {
                // copy first part of vector
                std::copy_n(other.get_data_ptr(), min_shape, get_data_ptr());

                // fill the rest with init value (if needed)
                auto remaining_shape = shape(0) - min_shape;
                std::fill_n(get_data_ptr() + min_shape, remaining_shape, init);
            } else {
                // copy first part of tensor
                for(size_t i = 0; i < min_shape; ++i) {
                    (*this)[i].copy_initialize(other[i], init);
                }

                // fill the rest with init value (if needed)
                for(size_t i = min_shape; i < shape(0); ++i) {
                    (*this)[i].initialize(init);
                }
            }
        }
    }

    /**
   * Copy values from a reference. In case the shapes do not match
   * the values will be ignored or filled with the init value.
   */
    void copy_initialize(const tensor_ref<TType, IDim> &other,
      TType init = TType()) {
        copy_initialize(tensor_cref { other }, init);
    }

    /**
   * Copy values from another tensor. In case the shapes do not match
   * the values will be ignored or filled with the init value.
   */
    void copy_initialize(const tensor<TType, IDim> &other, TType init = TType()) {
        copy_initialize(other.cref(), init);
    }

    //
    // overloaded access operators
    //

    std::conditional_t<IDim == 1, TType &, tensor_ref<TType, IDim - 1>>
    operator[](size_t index) {
        if(index >= shape(0)) {
            throw std::invalid_argument(
              "index " + std::to_string(index) + " out of bounds for shape = " + std::to_string(shape(0)));
        }
        if constexpr(IDim == 1) {
            ;
            return get_data_ptr()[index];
        } else {
            return tensor_ref<TType, IDim - 1>(*this, index);
        }
    }

    std::conditional_t<IDim == 1, const TType &, tensor_cref<TType, IDim - 1>>
    operator[](size_t index) const {
        return tensor_cref<TType, IDim> { *this }[index];
    }

    TType &operator[](const size_t indexes[IDim]) {
        if constexpr(IDim == 1) {
            return (*this)[indexes[0]];
        } else {
            return (*this)[indexes[0]][indexes + 1];
        }
    }

    const TType &operator[](const size_t indexes[IDim]) const {
        return tensor_cref<TType, IDim> { *this }[indexes];
    }

private:
    tensor_ref(const tensor_ref<TType, IDim + 1> &other, size_t new_index) :
        base(other, new_index) { }

    using base::get_data_ptr;
    using base::get_size;

    template <typename UType, unsigned JDim>
    friend class tensor_cref;

    friend class tensor_ref<TType, IDim + 1>;
    friend class tensor_ref<TType, IDim - 1>;
};

//
// utility functions
//

template <size_t IDim>
bool decrease_tensor_index(const std::array<size_t, IDim> &shape,
  std::vector<size_t> &index) {
    if(shape.size() != index.size()) {
        throw std::invalid_argument("sizes of shape and index do not match");
    }

    for(int i = IDim - 1; i >= 0; --i) {
        if(index.at(i) > 0) {
            index.at(i) -= 1;
            return true;
        }
        index.at(i) = shape.at(i) - 1;
    }

    return false;
}

template <size_t IDim>
bool increase_tensor_index(const std::array<size_t, IDim> &shape,
  std::vector<size_t> &index) {
    if(shape.size() != index.size()) {
        throw std::invalid_argument("sizes of shape and index do not match");
    }

    for(int i = IDim - 1; i >= 0; --i) {
        if(index.at(i) < shape.at(i) - 1) {
            index.at(i) += 1;
            return true;
        }
        index.at(i) = 0;
    }

    return false;
}

template <size_t IDim>
std::vector<size_t> last_tensor_index(const std::array<size_t, IDim> &shape) {
    std::vector<size_t> index;
    index.resize(shape.size());
    for(size_t i = 0; i < index.size(); ++i) {
        index.at(i) = shape.at(i) - 1;
    }
    return index;
}

template <size_t IDim>
std::array<size_t, IDim>
subsizes_of_shape(const std::array<size_t, IDim> &shape) {
    std::array<size_t, IDim> subsizes {};
    subsizes.at(IDim - 1) = 1;
    for(int i = static_cast<int>(IDim) - 2; i >= 0; --i) {
        subsizes.at(i) = shape.at(i + 1) * subsizes.at(i + 1);
    }

    return subsizes;
}

template <size_t IDim>
size_t tensor_num_elements(const std::array<size_t, IDim> &shape) {
    size_t num_elements = 1;
    for(size_t x : shape) {
        num_elements *= x;
    }
    return num_elements;
}

inline size_t tensor_num_elements(const std::vector<size_t> &shape) {
    size_t num_elements = 1;
    for(size_t x : shape) {
        num_elements *= x;
    }
    return num_elements;
}

} // namespace ale

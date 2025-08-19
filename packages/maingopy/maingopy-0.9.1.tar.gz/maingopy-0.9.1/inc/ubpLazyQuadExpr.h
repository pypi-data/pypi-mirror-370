/**********************************************************************************
 * Copyright (c) 2021 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "MAiNGOException.h"

#include "mcop.hpp"

#include <cassert>
#include <exception>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <sstream>
#include <vector>


///Overview: The goal of this module is to enable memory efficient assembly of sparse quadratic and linear expressions that are propagated through an MCPP DAG.
///           An linear expression is for example (c+a0x0+a1x1...+anxn). Often only a few coefficients ai are not zero.
///           The class LinExpr respresents a linear expression by only saving c and values and indices of nonzero coefficients ai.
///
///           Multiplying two linear expressions yields a quadratic expression.
///           Quadratic expressions can be represented by
///           (1): (c0+ax)*(c1+bx)=x.T*(a.T*b)*x + (c1*a+c2*b)*x + c0*c1 =x.T*Q*x+d*x+e
///           Avoiding a dense representation of the matrix Q saves memory in most cases. This is archieved with the class SparseMatrix.
///
///           The struct QuadExpr represents a full quadratic expression by combining an LinExpr part (representing d and e) and a SparseMatrix reprenting Q.
///           Higher orders (e.g. cubic ) are not supported and result in an exception.
///
///           Because the linear expressions are propagated through an MCPP DAG, every intermediate expression will normally be saved in the DAG with all coefficients.
///           This is useful for interval propagation, but here we are only interested in the final values.
///           The DAG is only used to enable an uniform model definition API.
///
///           To avoid the excessive memory usage, we evaluate the DAG with LazyQuadExpr.
///           This class does not save the results of the computation, but only the expression graph(recipe and original LinExpr objects needed to calculate the result), i.e., supports lazy evaluation.
///           The computation of the results can be triggered by calling an eval function.
///           The class also makes sure that no cubic or quartic expressions are formed.
///
///           The class LazyQuadExprTreeNode is the building block for the expression tree. If initialized with an LinExpr, it saves it to the heap and creates an shared pointer to it. Such LazyExprTreeNodes are leafs of the expression tree.
///           Nodes of higher level represent intermediate expressions and only contain the last arithmetic operation and shared pointers to the operands.
///           Example: (a+b)*c-> a,b,c are saved on the heap. d=a+b (saves PLUS and location of a and b) e=d*c(saves TIMES and location of d and e).
///
///           The reason for splitting LazyQuadExprTreeNode and LazyQuadExpr is that we do not want to call make_shared all the time, but want to make sure all LinExpr are saved only once.
///           Also and operator overloading is easier this way.


namespace maingo {
namespace ubp {


/**
 * @struct LinExpr
 * @brief A simple sparse vector class with an additional constant field. Represents c+a0*x0+a1*x1... where nonzero a0...an  and c are saved.
 *        This struct is used to avoid the need of propagating the IloExpr object resulting in HUGE RAM usage.
 *
 * The nonzero values and indices are stored in ascending index order.
 * Elementwise binary arithetic operations  are supported, which skip elements that are zero in both operands.
 * Elements can be efficently be appended.
 */
class LinExpr {
  public:
    /**
	  * @brief Default constructor, LinExpr only contains a constant term
	  */
    LinExpr(double scalar = 0.0):
        _constant(scalar)
    {
    }
    /** @brief Returns true if expression only contains a constant and no linear term*/
    bool is_scalar() const
    {
        return _values.empty() && _ids.empty();
    }
    /** @brief Getter for the constant term of the linear expression*/
    double& constant()
    {
        return _constant;
    }
    /** @brief Getter for the constant term of the linear expression*/
    double constant() const
    {
        return _constant;
    }
    /**
	* @brief Getter for elments in the sparse vector, corresponding to the linear part of the expression
	*
	* @param[in] index is the index of the value requested. Function returns a_index.
	*/
    double get_value(unsigned index) const
    {
        for (unsigned i = 0; i < _ids.size(); i++) {
            if (_ids[i] == index) {
                return _values[i];
            }
            if (_ids[i] > index)    //not found
            {
                break;
            }
        }
        return 0;
    }
    /**
	* @brief Setter for elments in the sparse vector, corresponding to the linear part of the expression
	*
	* @param[in] index is the index of the value to change. 
	* @param[in] value is the value that should be saved
	*/
    void set_value(unsigned index, double value)
    {
        //insert at the end if we know this is were the value belongs
        if (_ids.empty() || index > _ids.back()) {
            _ids.push_back(index);
            _values.push_back(value);
        }
        else {    //look if index is already saved
                  //if yes, replace value
            for (unsigned i = 0; i < _ids.size(); i++) {
                if (_ids[i] == index) {
                    _values[i] = value;
                }
                if (_ids[i] > index)    //not found, since _ids is sorted insert to keep _ids sorted
                {
                    std::vector<unsigned>::const_iterator it = _ids.begin() + i;
                    _ids.insert(it, value);
                    std::vector<double>::const_iterator it2 = _values.begin() + i;
                    _values.insert(it2, value);
                    break;
                }
            }
        }
    }
    /** @brief Getter for the ids of nonzero entries*/
    const std::vector<unsigned>& get_non_zero_ids() const
    {
        return _ids;
    }
    /** @brief Getter for the ids of nonzero entries*/
    const std::vector<double>& get_non_zero_values() const
    {
        return _values;
    }
    /** @brief  Function to print content of sparse linear expression*/
    std::string print() const
    {
        std::stringstream ss;

        for (unsigned i = 0; i < _ids.size(); i++) {
            ss << "(" << _ids[i] << "):" << _values[i] << ",";
        }
        ss << "(const):" << _constant << std::endl;
        return ss.str();
    }
    /**
	* @brief Helper function: apply a function f(unsigned id,double az,double bz) to all coefficients of a and b that are related to an index that occurs in either a or b.
	*
    * For example if we want to calculate ci=ai+bi, we must be careful, because a and b are saved as sparse vectors, i.e. the first entry in a.values does not correspond to a_0, but to a_{a._indices[0]}.
	* Assume that we want have a=(0):1,(3):4 and b=(3):1,(4):2, then this f will be called with f(0,1,0), f(3,4,1) and f(4,0,2), skipping over indices that are neither in a or b.
	* This function is an efficient alternative to writing both sparse vectors to full vectors apply a function that acts elementswise on both vectors and create a sparse vector from that.
    */
    //typedef void(*forallOperation)(int/*id*/,double&/*a.z*/,double&/*b.z*/);// necessary signature
    template <typename forallOperation>
    static void for_all_coeffs(forallOperation f, const LinExpr& a, const LinExpr& b)
    {
        int i1                             = 0;
        int i2                             = 0;
        const std::vector<unsigned>& a_ids = a._ids;
        const std::vector<unsigned>& b_ids = b._ids;
        //go from small id to large id through both id vectors
        //which are both sorted in ascending order
        //replace missing z[i] with zero if one of the vectors does not contain it
        while (i1 != a_ids.size() || i2 != b_ids.size()) {
            if (i1 == a_ids.size())    //no more in a
            {
                f(b._ids[i2], 0, b._values[i2]);
                i2++;
            }
            else if (i2 == b_ids.size())    //no more in b
            {
                f(a._ids[i1], a._values[i1], 0);
                i1++;
            }
            else if ((a_ids[i1] < b_ids[i2]))    // a.ids[i1] has the next ID, b does not have a coefficient for that id.
            {
                f(a._ids[i1], a._values[i1], 0);
                i1++;
            }
            else if ((a_ids[i1] > b_ids[i2]))    // b.ids[i2] has the next ID, a does not have a coefficient for that id
            {
                f(b._ids[i2], 0, b._values[i2]);
                i2++;
            }
            else    //(a._ids[i1]==b._ids[i2]) // current ID is contained in both id vectors
            {
                f(a._ids[i1], a._values[i1], b._values[i2]);
                i1++;
                i2++;
            }
        }
    }

    /**
     * @brief Helper function: apply a function + to all coefficients of a and b that are related to an index that occurs in either a or b.
     *
     * Added to decrease overhead because plus is called frequently
     */

    inline static void for_all_coeffs_plus(LinExpr& out, const LinExpr& a,
                                           const LinExpr& b)
    {
        int i1 = 0;
        int i2 = 0;
        // go from small id to large id through both id vectors
        // which are both sorted in ascending order
        // replace missing z[i] with zero if one of the vectors does not contain it
        while (i1 != a._ids.size() || i2 != b._ids.size()) {
            if (i1 == a._ids.size()) {    // no more in a
                out.set_value(b._ids[i2], 0 + b._values[i2]);
                i2++;
            }
            else if (i2 == b._ids.size()) {    // no more in b

                out.set_value(a._ids[i1], a._values[i1] + 0);
                i1++;
            }
            else if ((a._ids[i1] < b._ids[i2])) {    // a.ids[i1] has the next ID, b does not have a coefficient for that id.
                out.set_value(a._ids[i1], a._values[i1] + 0);
                i1++;
            }
            else if ((a._ids[i1] > b._ids[i2])) {    // b.ids[i2] has the next ID, a does not have a coefficient for that id
                out.set_value(b._ids[i2], 0 + b._values[i2]);
                i2++;
            }
            else {    //(a._ids[i1]==b._ids[i2]) // current ID is contained in both id vectors
                out.set_value(a._ids[i1], a._values[i1] + b._values[i2]);
                i1++;
                i2++;
            }
        }
    }

  protected:
    std::vector<double> _values; /*!< The linear coefficients saved in the vector*/

    std::vector<unsigned> _ids; /*!< Sorted list of all indices indentifing nonzero entries*/
    double _constant;           /*!< The constant term in linear (more exactly affine) expression*/
    friend LinExpr scale(const LinExpr& LHS, double scale);
    friend std::ostream& operator<<(std::ostream& os, const LinExpr& dt);
};


/** @brief  Function to print content of LinExpr*/
inline std::ostream&
operator<<(std::ostream& os, const LinExpr& dt)
{
    os << dt.print();
    return os;
}

/** @brief Helper function:do an elementwise binary operation on LHS and RHS and save result in returned variable*/
inline LinExpr
calculate_binary_operation_element_wise(const LinExpr& LHS, const LinExpr& RHS, const std::function<double(double, double)>& op)
{
    LinExpr Out(op(LHS.constant(), RHS.constant()));
    auto assingElementwiseOpToOut = [&Out, op](int id, double a, double b) {
        Out.set_value(id, op(a, b));
    };
    LinExpr::for_all_coeffs(assingElementwiseOpToOut, LHS, RHS);
    return Out;
}

/** @brief Operator+ for LinExpr: Elementwise addition */
inline LinExpr
operator+(const LinExpr& LHS, const LinExpr& RHS)
{
    LinExpr Out(LHS.constant() + RHS.constant());
    LinExpr::for_all_coeffs_plus(Out, LHS, RHS);
    return Out;
}

/** @brief Operator- for LinExpr: Elementwise subtraction */
inline LinExpr
operator-(const LinExpr& LHS, const LinExpr& RHS)
{
    return calculate_binary_operation_element_wise(LHS, RHS, std::minus<double>());
}

/** @brief Operator* for LinExpr: Elementwise  multiplication*/
inline LinExpr
operator*(const LinExpr& LHS, const LinExpr& RHS)
{
    return calculate_binary_operation_element_wise(LHS, RHS, std::multiplies<double>());
}

/** @brief Operator/ for LinExpr: Elementwise  division */
inline LinExpr
operator/(const LinExpr& LHS, const LinExpr& RHS)
{
    return calculate_binary_operation_element_wise(LHS, RHS, std::divides<double>());
}

/** @brief scale LinExpression by scalar*/
inline LinExpr
scale(const LinExpr& LHS, double scale)
{
    LinExpr result(LHS);
    result.constant() *= scale;

    for (double& val : result._values) {
        val *= scale;
    }

    return result;
}

/** @brief Operator* for LinExpr and scalar double : Elementwise  multiplication*/
inline LinExpr
operator*(const LinExpr& LHS, double scalar)
{
    return scale(LHS, scalar);
}

/** @brief Operator* for LinExpr and scalar double : Elementwise  multiplication*/
inline LinExpr
operator*(double scalar, const LinExpr& RHS)
{
    return scale(RHS, scalar);
}

/** @brief Operator/ for LinExpr and scalar double : Elementwise  division*/
inline LinExpr
operator/(const LinExpr& LHS, double divisor)
{
    return scale(LHS, 1 / divisor);
}


/**
* @struct  SparseMatrix
* @brief A simple  Sparse Matrix using directory of keys format.
*
* Elementwise operations (except division) are supported;
*/

class SparseMatrix {
  public:
    /**
	* @brief Default constructor
	* @param[in] nCols: number of columns of the matrix, unused in directory of key format.
	*/
    SparseMatrix(unsigned nCols = 0){};
    /**
	* @brief Getter for element of given row and column
	* @param[in] row is the row of the element requested
	* @param[in] col is the column of the element requested
	*/
    double get_element(unsigned row, unsigned col) const
    {
        if (row > get_number_of_rows()) {
            return 0;
        }
        else {
            auto it = _matrix.find(std::make_pair(row, col));
            if (it == _matrix.end())
                return 0;
            else
                return it->second;
        }
    }
    /**
	* @brief Setter for element of given row and column. Already set values are overridden.
	* @param[in] row is the row of the element to be changed
	* @param[in] col is the column of the element to be changed
	* @param[in] value is the value the element is to be changed to
	*/
    void setElement(unsigned row, unsigned col, double value)
    {
        _matrix[std::make_pair(row, col)] = value;
    }
    /* @brief Getter for a whole row of the matrix as a LinExpr object*/
    LinExpr getRow(unsigned row) const
    {
        LinExpr result;
        std::map<std::pair<unsigned, unsigned>, double>::const_iterator firstNonZeroElementInRowIt = _matrix.lower_bound(std::make_pair(row, 0));
        for (std::map<std::pair<unsigned, unsigned>, double>::const_iterator it = firstNonZeroElementInRowIt; it != _matrix.end() && it->first.first == row; it++) {
            result.set_value(it->first.second, it->second);
        }
        return result;
    }
    /* @brief Gets the number of rows saved in the matrix. There is at least one row with row id smaller than the number of rows*/
    unsigned get_number_of_rows() const
    {
        if (!_matrix.empty()) {
            unsigned highestCurrentRowIndex = _matrix.rbegin()->first.first;
            return highestCurrentRowIndex + 1;
        }
        else {
            return 0;
        }
    }
    /* @brief Append a row to the bottom of the sparse matrix*/
    void append_row(const LinExpr& row)
    {
        unsigned newRowIndex = get_number_of_rows();    // known row with highest index is get_number_of_rows-1;
        append_row(row, newRowIndex);
    }
    /* @brief Append a row to the matrix with a given row index, but leave empty rows between the previous last row and the newly added row.
	*
	*  Insetion is not allowed, i.e., can only append to the matrix not insert.
	*/
    void append_row(const LinExpr& row, unsigned rowNumber)
    {
        unsigned minNumber   = get_number_of_rows();    //we only allow appending, not replacing.
        unsigned nnz         = row.get_non_zero_ids().size();
        unsigned newRowIndex = rowNumber;
        if (newRowIndex < minNumber) { // GCOVR_EXCL_START
            throw MAiNGOException("Tried to append a row to a sparse matrix, but given row index lead to an insertion. Requested row index to append: " + std::to_string(rowNumber) + " index of last row already in matrix: " + std::to_string(minNumber - 1));
        }
        for (unsigned i = 0; i < nnz; i++) { // GCOVR_EXCL_STOP
            //efficently inserts at the end of the map!
            _matrix.insert(std::end(_matrix), std::make_pair(std::make_pair(newRowIndex, row.get_non_zero_ids()[i]), row.get_non_zero_values()[i]));
        }
    }
    /** @brief  Function to print content of sparse matrix*/
    std::string print() const
    {
        std::stringstream ss;
        if (!_matrix.empty()) {

            int previousRow = _matrix.begin()->first.first;
            ss << "\n";
            for (auto& t : _matrix) {
                unsigned row = t.first.first;
                unsigned col = t.first.second;
                double val   = t.second;
                if (row != previousRow) {
                    ss << "\n";
                    previousRow = row;
                }
                ss << "(" << row << "," << col << "): " << val << ",";
            }
        }
        ss << std::endl;
        return ss.str();
    }


  private:
    std::map<std::pair<unsigned, unsigned>, double> _matrix; /*!< sorted map saving the entries of the matrix, sorted first after rows, then after columns*/
    friend SparseMatrix scale(SparseMatrix LHS, double scalar);
    friend SparseMatrix add(SparseMatrix LHS, double scalar);
    friend std::ostream& operator<<(std::ostream& os, const SparseMatrix& dt);
};

/** @brief  Function to print content of sparse matrix*/
inline std::ostream&
operator<<(std::ostream& os, const SparseMatrix& dt)
{
    os << dt.print();
    return os;
}

/** @brief Operator+ for SparseMatrix: Elementwise addition*/
inline SparseMatrix
operator+(const SparseMatrix& LHS, const SparseMatrix& RHS)
{
    SparseMatrix result;
    unsigned maxRows = std::max(LHS.get_number_of_rows(), RHS.get_number_of_rows());
    for (unsigned i = 0; i < maxRows; i++) {
        result.append_row(LHS.getRow(i) + RHS.getRow(i), i);    //if both rows are empty, this will do nothing
    }
    return result;
}

/** @brief Operator- for SparseMatrix: Elementwise  subtraction */
inline SparseMatrix
operator-(const SparseMatrix& LHS, const SparseMatrix& RHS)
{
    SparseMatrix result;
    unsigned maxRows = std::max(LHS.get_number_of_rows(), RHS.get_number_of_rows());
    for (unsigned i = 0; i < maxRows; i++) {
        result.append_row(LHS.getRow(i) - RHS.getRow(i), i);
    }
    return result;
}

/** @brief Operator* for SparseMatrix: Elementwise  multiplication */
inline SparseMatrix
operator*(const SparseMatrix& LHS, const SparseMatrix& RHS)
{
    SparseMatrix result;
    unsigned maxRows = std::max(LHS.get_number_of_rows(), RHS.get_number_of_rows());
    for (unsigned i = 0; i < maxRows; i++) {
        result.append_row(LHS.getRow(i) * RHS.getRow(i), i);
    }
    return result;
}

/** @brief Operator+ for SparseMatrix and scalar: Elementwise addition*/
inline SparseMatrix
add(SparseMatrix LHS, double scalar)
{
    for (auto& p : LHS._matrix) {
        p.second += scalar;
    }
    return LHS;
}

/** @brief Operator* for SparseMatrix and scalar: Elementwise multiplication*/
inline SparseMatrix
scale(SparseMatrix LHS, double scale)
{
    for (auto& p : LHS._matrix) {
        p.second *= scale;
    }
    return LHS;
}

/** @brief Operator+ for SparseMatrix and scalar: Elementwise addition*/
inline SparseMatrix
operator+(const SparseMatrix& LHS, double scalar)
{
    return add(LHS, scalar);
}

/** @brief Operator+ for SparseMatrix and scalar: Elementwise addition*/
inline SparseMatrix
operator+(double scalar, const SparseMatrix& RHS)
{
    return add(RHS, scalar);
}

/** @brief Operator- for SparseMatrix and scalar: Elementwise subtraction */
inline SparseMatrix
operator-(const SparseMatrix& LHS, double scalar)
{
    return add(LHS, -scalar);
}

/** @brief Operator- for SparseMatrix: Elementwise negation*/
inline SparseMatrix
operator-(const SparseMatrix& LHS)
{
    return scale(LHS, -1.0);
}

/** @brief Operator- for SparseMatrix and scalar: Elementwise subtraction */
inline SparseMatrix
operator-(double scalar, const SparseMatrix& RHS)
{
    return scalar + (-RHS);
}

/** @brief Operator* for SparseMatrix and scalar: Elementwise multiplication*/
inline SparseMatrix
operator*(const SparseMatrix& LHS, double scalar)
{
    return scale(LHS, scalar);
}

/** @brief Operator* for SparseMatrix and scalar: Elementwise multiplication*/
inline SparseMatrix
operator*(double scalar, const SparseMatrix& RHS)
{
    return scale(RHS, scalar);
}

/**
* @struct  QuadExpr
* @brief General quadratic expression with a sparse matrix for the quadratic part and a sparse linear expression for the linear part (including a constant term)
*
* Elementwise operations (except division) are supported;
*/
struct QuadExpr {
    SparseMatrix quadraticPart;
    LinExpr linearPart;
};

/**
* @struct LazyQuadExprTreeNode
* @brief A class that represents a node of the expression tree.
*
*Saves the operation and pointers to its children, i.e., the nodes that the operation needs to be applied to  to calculate the expression the node represents.
*If this expression is a leaf node (an original operand for example a scalar) the operation type is identity
*This is outside LazyQuadExpr because we must make sure only shared_ptr to this class are held
*/
class LazyQuadExprTreeNode {
  public:
    /* @brief Types of operations that can be saved in the tree */
    enum class OperationType {
        PLUS,
        MINUS,
        TIMES,
        NEGATE,
        DIVISION_BY_SCALAR,
        IDENITY    //IDENITY means we ourselves have content in our linearContent member
    };
    /* @brief Order of expression*/
    enum class Order {
        SCALAR,      //only a constant
        LINEAR,      // a constant and linear terms
        QUADRATIC    // any expression with quadratic terms
    };
    /* @brief Returns true if expression contains quadratic terms*/
    bool is_quadratic() const
    {
        return _order == Order::QUADRATIC;
    }
    /* @brief Returns true if expression contains linear terms but no quadratic terms*/
    bool is_linear() const
    {
        return _order == Order::LINEAR;
    }
    /* @brief Returns true if expression contains only constants*/
    bool is_scalar() const
    {
        return _order == Order::SCALAR;
    }
    /**
	* @brief default constructor for LazyQuadExprTreeNode.
	*
	* @param[in] linExpr The linear expression this node is representing. The linear expression will be saved on the heap with a shader pointer
	*/
    LazyQuadExprTreeNode(LinExpr linExpr):
        _op(OperationType::IDENITY), _linearContent(std::make_shared<LinExpr>(linExpr)),
        _order(linExpr.is_scalar() ? Order::SCALAR : Order::LINEAR)
    {
    }
    /**
	* @brief default constructor for LazyQuadExprTreeNode given all members
	*/
    LazyQuadExprTreeNode(std::shared_ptr<LazyQuadExprTreeNode> LHS, std::shared_ptr<LazyQuadExprTreeNode> RHS, OperationType op, Order order = Order::LINEAR):
        _op(op), _leftChild(LHS), _rightChild(RHS), _order(order)
    {
    }

    /**
	* @brief Calculate the constant element of the quadratic expression, by going through the expression tree.
	*/
    double eval_element_constant() const
    {
        switch (_op) {
            case (OperationType::IDENITY):
                assert(_linearContent);    //IDENITY means the lazy element is a leaf and should have a linearContent saved
                return _linearContent->constant();
            case (OperationType::MINUS):
                return _leftChild->eval_element_constant() - _rightChild->eval_element_constant();
            case (OperationType::PLUS):
                return _leftChild->eval_element_constant() + _rightChild->eval_element_constant();
            case (OperationType::TIMES):
                return _leftChild->eval_element_constant() * _rightChild->eval_element_constant();
            case (OperationType::NEGATE):
                return -_leftChild->eval_element_constant();
            case (OperationType::DIVISION_BY_SCALAR):
                return _leftChild->eval_element_constant() / _rightChild->eval_element_constant();
        }
        assert(false);
        return std::numeric_limits<double>::quiet_NaN();
    }

    /**
	* @brief Calculate a specific linear element of the quadratic expression, by going through the expression tree.
	*/
    double eval_element_linear(unsigned index) const
    {
        if (this->is_scalar()) {
            return 0.0;
        }
        switch (_op) {
            case (OperationType::IDENITY):
                assert(_linearContent);    //IDENITY means the lazy element is a leaf and should have a linearContent saved
                return _linearContent->get_value(index);
            case (OperationType::MINUS):
                return _leftChild->eval_element_linear(index) - _rightChild->eval_element_linear(index);
            case (OperationType::PLUS):
                return _leftChild->eval_element_linear(index) + _rightChild->eval_element_linear(index);
            case (OperationType::TIMES):
                return _leftChild->eval_element_linear(index) * _rightChild->eval_element_constant() + _rightChild->eval_element_linear(index) * _leftChild->eval_element_constant();
            case (OperationType::DIVISION_BY_SCALAR):
                return _leftChild->eval_element_linear(index) / _rightChild->eval_element_constant();
            case (OperationType::NEGATE):
                return -_leftChild->eval_element_linear(index);
        }

        assert(false);
        return std::numeric_limits<double>::quiet_NaN();
    }
    /**
	* @brief Calculate a specific quadratic element of the quadratic expression, by going through the expression tree. 
	*
	* For evaluating the whole quadratic matrix, this method is more memory efficient, but much slower than using assemble_quadratic_expression_matrix_wise
	*/
    double eval_element_quadratic(unsigned row, unsigned col) const
    {
        if (_order != Order::QUADRATIC) {
            return 0.0;
        }
        else {
            switch (_op) {
                case (OperationType::MINUS):
                    return _leftChild->eval_element_quadratic(row, col) - _rightChild->eval_element_quadratic(row, col);
                case (OperationType::PLUS):
                    return _leftChild->eval_element_quadratic(row, col) + _rightChild->eval_element_quadratic(row, col);
                case (OperationType::NEGATE):
                    return -_leftChild->eval_element_quadratic(row, col);
                case (OperationType::TIMES): {
                    if (_leftChild->is_quadratic()) {
                        assert(_rightChild->is_scalar());
                        double left = _leftChild->eval_element_quadratic(row, col);
                        if (left == 0.0)
                            return 0.0;
                        else
                            return left * _rightChild->eval_element_constant();
                    }
                    else if (_rightChild->is_quadratic()) {
                        assert(_leftChild->is_scalar());
                        double right = _rightChild->eval_element_quadratic(row, col);
                        if (right == 0.0)
                            return 0.0;
                        else
                            return right * _leftChild->eval_element_constant();
                    }
                    else {
                        double left = _leftChild->eval_element_linear(row);
                        if (left == 0.0)
                            return 0.0;
                        else
                            return left * _rightChild->eval_element_linear(col);
                    }
                }
                case (OperationType::DIVISION_BY_SCALAR):
                    return _leftChild->eval_element_quadratic(row, col) / _rightChild->eval_element_constant();
                case (OperationType::IDENITY):
                    throw MAiNGOException(std::string("It should be impossible to create a lazy quadratic expression without creating it from linear expressions") + std::string("but the lazy quadratic expression tree still has an element that claims to be quadratic and an original expression."));
            }
        }
        assert(false);
        return std::numeric_limits<double>::quiet_NaN();
    }
    /**
	* @brief Calculate the whole quadratic expression (all elements of the quadratic matrix and the linear part, as well as the constant term) by going elementwise through the expression tree.
	*
	* When trivial,e.g., when calculating bij=aij*0 with aij jet unknown, evaluation of parts of the expression tree is avoided, but still many calculations well need to be repeated for the calculation of the elements.
	* The elmentwise calculation avoids building the full QuadExpr objects for the operants, e.g. for C=A+B we dont ever have full A and B in memory, but onyl a_ij b_ij, reducing the peak memory consumption. 
	* Most likely only worth the time penalty for extremly memory restricted problems.
	*/
    QuadExpr assemble_quadratic_expression_element_wise(unsigned nVariables) const
    {
        QuadExpr quadraticExpression;
        for (unsigned row = 0; row < nVariables; row++) {

            //The quadratic expression is the result of [a0 a1 a0].T x [b0 b1 b2] and is thus Q is not symmetric
            for (unsigned col = 0; col < nVariables; col++) {
                double element = eval_element_quadratic(row, col);
                if (element != 0.0) {
                    quadraticExpression.quadraticPart.setElement(row, col, element);
                }
            }
        }
        for (unsigned index = 0; index < nVariables; index++) {
            double element = eval_element_linear(index);
            if (element != 0.0) {
                quadraticExpression.linearPart.set_value(index, element);
            }
        }
        quadraticExpression.linearPart.constant() = eval_element_constant();
        return quadraticExpression;
    }

    /**
	* @brief Calculate the whole quadratic expression (all elements of the quadratic matrix and the linear part, as well as the constant term) by going through the expression tree. To save computations, operands are fully constructed.
	*
	*/
    QuadExpr assemble_quadratic_expression_matrix_wise(unsigned nVariables) const
    {
        QuadExpr result;

        {

            switch (_op) {
                case (OperationType::IDENITY): {
                    if (_order == Order::QUADRATIC) { // GCOVR_EXCL_START
                        throw MAiNGOException(std::string("It should be impossible to create a lazy quadratic expression without creating it from linear expressions") + std::string("but the lazy quadratic expression tree still has an element that claims to be quadratic and an original expression."));
                    }
                    result.linearPart = *_linearContent; // GCOVR_EXCL_STOP
                    return result;
                }
                case (OperationType::MINUS): {
                    QuadExpr left        = _leftChild->assemble_quadratic_expression_matrix_wise(nVariables);
                    QuadExpr right       = _rightChild->assemble_quadratic_expression_matrix_wise(nVariables);
                    result.linearPart    = left.linearPart - right.linearPart;
                    result.quadraticPart = left.quadraticPart - right.quadraticPart;
                    return result;
                }
                case (OperationType::PLUS): {
                    QuadExpr left        = _leftChild->assemble_quadratic_expression_matrix_wise(nVariables);
                    QuadExpr right       = _rightChild->assemble_quadratic_expression_matrix_wise(nVariables);
                    result.linearPart    = left.linearPart + right.linearPart;
                    result.quadraticPart = left.quadraticPart + right.quadraticPart;
                    return result;
                }
                case (OperationType::NEGATE): {
                    QuadExpr left        = _leftChild->assemble_quadratic_expression_matrix_wise(nVariables);
                    result.quadraticPart = left.quadraticPart * -1.0;
                    result.linearPart    = left.linearPart * -1.0;
                    return result;
                }
                case (OperationType::TIMES): {
                    if (_leftChild->is_quadratic()) {
                        assert(_rightChild->is_scalar());
                        QuadExpr right = _rightChild->assemble_quadratic_expression_matrix_wise(nVariables);
                        if (right.linearPart.constant() == 0.0)    //can stop early if one operand is full zero
                            return result;                         //Is still empty
                        QuadExpr left        = _leftChild->assemble_quadratic_expression_matrix_wise(nVariables);
                        result.linearPart    = left.linearPart * right.linearPart.constant();
                        result.quadraticPart = left.quadraticPart * right.linearPart.constant();
                    }
                    else if (_rightChild->is_quadratic()) {
                        assert(_leftChild->is_scalar());
                        QuadExpr left = _leftChild->assemble_quadratic_expression_matrix_wise(nVariables);
                        if (left.linearPart.constant() == 0.0)    //can stop early if one operand is pure zero
                            return result;                        //Is still empty
                        QuadExpr right       = _rightChild->assemble_quadratic_expression_matrix_wise(nVariables);
                        result.linearPart    = right.linearPart * left.linearPart.constant();
                        result.quadraticPart = right.quadraticPart * left.linearPart.constant();
                    }
                    else {
                        QuadExpr left                 = _leftChild->assemble_quadratic_expression_matrix_wise(nVariables);
                        QuadExpr right                = _rightChild->assemble_quadratic_expression_matrix_wise(nVariables);
                        result.linearPart             = left.linearPart * right.linearPart.constant() + right.linearPart * left.linearPart.constant();
                        result.linearPart.constant()  = left.linearPart.constant() * right.linearPart.constant();
                        std::vector<unsigned> indLeft = left.linearPart.get_non_zero_ids();
                        std::vector<double> valLeft   = left.linearPart.get_non_zero_values();
                        unsigned indexInIndLeft       = 0;
                        for (unsigned row = 0; row <= indLeft.back(); row++)    //indLeft is sorted, going from 0 to left.back means going through
                                                                                // all possible nonzero row indices. But only rows i with i in indLeft have any nonzero elements.
                        {
                            if (row == indLeft[indexInIndLeft])    //row is in left
                            {

                                result.quadraticPart.append_row(valLeft[indexInIndLeft] * right.linearPart, row);
                                indexInIndLeft++;
                            }
                        }
                    }
                    return result;
                }
                case (OperationType::DIVISION_BY_SCALAR): {
                    QuadExpr left     = _leftChild->assemble_quadratic_expression_matrix_wise(nVariables);
                    result.linearPart = left.linearPart / _rightChild->eval_element_constant();
                    return result;
                }
            }
        }
        assert(false);    //should be inpossible to reach since each case returns
        return result;
    }

  protected:
    OperationType _op; /*!< The operation saved in this node that needs to be applied to the children to generate the result*/


    //The operands used to calculate the current expression. this=_op(_leftChild,_rightChild)
    const std::shared_ptr<LazyQuadExprTreeNode> _leftChild;  /*!< left child of the current node in the expression tree: this=_op(_leftChild,_rightChild */
    const std::shared_ptr<LazyQuadExprTreeNode> _rightChild; /*!< right child of the current node in the expression tree: this=_op(_leftChild,_rightChild. If op_==NEGATE _rightChild is ignored */

    const std::shared_ptr<LinExpr> _linearContent; /*!<In the leafs of the expression tree, the original linear expressions is saved, is empty except when _Op=IDENITY */

    const Order _order; /*!< Saves if the expression is a scalar, linear or quadratic, to make sure no cubic or higher orders are calculated */
};

/** @brief Operator+ for LazyQuadExprTreeNode*/
inline std::shared_ptr<LazyQuadExprTreeNode>
operator+(std::shared_ptr<LazyQuadExprTreeNode> LHS, std::shared_ptr<LazyQuadExprTreeNode> RHS)
{
    LazyQuadExprTreeNode::Order order = LazyQuadExprTreeNode::Order::LINEAR;
    if (LHS->is_quadratic() || RHS->is_quadratic()) {
        order = LazyQuadExprTreeNode::Order::QUADRATIC;
    }
    else if (LHS->is_scalar() && RHS->is_scalar()) {
        order = LazyQuadExprTreeNode::Order::SCALAR;
    }

    return std::make_shared<LazyQuadExprTreeNode>(LHS, RHS, LazyQuadExprTreeNode::OperationType::PLUS, order);
}

/** @brief Operator- for LazyQuadExprTreeNode*/
inline std::shared_ptr<LazyQuadExprTreeNode>
operator-(std::shared_ptr<LazyQuadExprTreeNode> LHS, std::shared_ptr<LazyQuadExprTreeNode> RHS)
{
    LazyQuadExprTreeNode::Order order = LazyQuadExprTreeNode::Order::LINEAR;
    if (LHS->is_quadratic() || RHS->is_quadratic()) {
        order = LazyQuadExprTreeNode::Order::QUADRATIC;
    }
    else if (LHS->is_scalar() && RHS->is_scalar()) {
        order = LazyQuadExprTreeNode::Order::SCALAR;
    }

    return std::make_shared<LazyQuadExprTreeNode>(LHS, RHS, LazyQuadExprTreeNode::OperationType::MINUS, order);
}

/** @brief Operator- for LazyQuadExprTreeNode*/
inline std::shared_ptr<LazyQuadExprTreeNode>
operator-(std::shared_ptr<LazyQuadExprTreeNode> LHS)
{
    LazyQuadExprTreeNode::Order order = LazyQuadExprTreeNode::Order::SCALAR;
    if (LHS->is_linear())
        order = LazyQuadExprTreeNode::Order::LINEAR;
    else if (LHS->is_quadratic())
        order = LazyQuadExprTreeNode::Order::QUADRATIC;
    return std::make_shared<LazyQuadExprTreeNode>(LHS, LHS, LazyQuadExprTreeNode::OperationType::NEGATE, order);
}

/**
 *@brief Operator* for LazyQuadExprTreeNode
 *
 * Will throw if total order of the resulting expression would be higher than quadratic.
 */
inline std::shared_ptr<LazyQuadExprTreeNode>
operator*(std::shared_ptr<LazyQuadExprTreeNode> LHS, std::shared_ptr<LazyQuadExprTreeNode> RHS)
{
    bool resultMoreThanQuadratic = (LHS->is_quadratic() && !RHS->is_scalar()) || (RHS->is_quadratic() && !LHS->is_scalar());
    bool resultQuadratic         = (LHS->is_linear() && RHS->is_linear()) || (LHS->is_quadratic() && RHS->is_scalar()) || (LHS->is_scalar() && RHS->is_quadratic());
    bool resultScalar            = LHS->is_scalar() && RHS->is_scalar();
    LazyQuadExprTreeNode::Order resultOrder;
    if (resultMoreThanQuadratic) { // GCOVR_EXCL_START
        throw MAiNGOException(("Cant multiply already quadratic expressions to generate a quadratic expression"));
    }
    else if (resultQuadratic) { // GCOVR_EXCL_STOP
        resultOrder = LazyQuadExprTreeNode::Order::QUADRATIC;
    }
    else if (resultScalar) {
        resultOrder = LazyQuadExprTreeNode::Order::SCALAR;
    }
    else {
        resultOrder = LazyQuadExprTreeNode::Order::LINEAR;
    }
    return std::make_shared<LazyQuadExprTreeNode>(LHS, RHS, LazyQuadExprTreeNode::OperationType::TIMES, resultOrder);
}

/**
*@brief Operator/ for LazyQuadExprTreeNode
*
* Will throw if RHS is not a scalar.
*/
inline std::shared_ptr<LazyQuadExprTreeNode>
operator/(std::shared_ptr<LazyQuadExprTreeNode> LHS, std::shared_ptr<LazyQuadExprTreeNode> RHS)
{
    LazyQuadExprTreeNode::Order resultOrder = LazyQuadExprTreeNode::Order::SCALAR;
    if (!RHS->is_scalar()) { // GCOVR_EXCL_START
        throw MAiNGOException("Function 1/x not allowed in (MIQ)Ps.");
    }
    if (LHS->is_linear()) { // GCOVR_EXCL_STOP
        resultOrder = LazyQuadExprTreeNode::Order::LINEAR;
    }
    else if (LHS->is_quadratic()) {
        resultOrder = LazyQuadExprTreeNode::Order::QUADRATIC;
    }
    return std::make_shared<LazyQuadExprTreeNode>(LHS, RHS, LazyQuadExprTreeNode::OperationType::DIVISION_BY_SCALAR, resultOrder);
}

/**
* @struct LazyQuadExpr
* @brief A class can be used as in to generate quadratic expressions that can be lazily evaluated, which enables memory savings when evaluating in DAG.
*
* Lazy behavior is archieved by building a pointer structure on the heap that saves an expression tree. This class  encapsulates a node of an the expression tree. 
*/
class LazyQuadExpr {
  public:
    /**
	* @brief Constructor for LazyQuadExpr that represents a variable or an identity expression
	*
	* @param[in] numberVars Is the total number of variables (currently unused)
	* @param[in] active_index Is the index of the variable this expression represents. Should be smaller then numberVars;
	*/
    LazyQuadExpr(unsigned numberVars, unsigned active_index)
    {
        if (active_index >= numberVars) { // GCOVR_EXCL_START
            throw MAiNGOException("Tried to create an lazy quadratic expresion for a variable with an index that is inconsistent with the specified number of variables");
        }
        LinExpr lin(0.0); // GCOVR_EXCL_STOP
        lin.set_value(active_index, 1.0);
        _tree = std::make_shared<LazyQuadExprTreeNode>(lin);
    }
    /* @brief Constructor for LazyQuadExpr from a linear expression */
    LazyQuadExpr(LinExpr linExpr)
    {
        _tree = std::make_shared<LazyQuadExprTreeNode>(linExpr);
    }
    /* @brief Constructor for LazyQuadExpr from a scalar*/
    LazyQuadExpr(double scalar = 0.0)
    {
        _tree = std::make_shared<LazyQuadExprTreeNode>(LinExpr(scalar));
        /* @brief Constructor for LazyQuadExpr from a shared pointer to LazyQuadExprTreeNode, making them convertible to each other*/
    }
    LazyQuadExpr(std::shared_ptr<LazyQuadExprTreeNode> tree):
        _tree(tree) {}

    /* @brief Conversion for LazyQuadExpr to a shared pointer to LazyQuadExprTreeNode, making them convertible to each other*/
    operator std::shared_ptr<LazyQuadExprTreeNode>()
    {
        return _tree;
    }
    /*! @copydoc  LazyQuadExprTreeNode::assemble_quadratic_expression_element_wise()*/
    QuadExpr assemble_quadratic_expression_element_wise(unsigned numberVars) const
    {
        return _tree->assemble_quadratic_expression_element_wise(numberVars);
    }
    /*! @copydoc  LazyQuadExprTreeNode::assemble_quadratic_expression_matrix_wise()*/
    QuadExpr assemble_quadratic_expression_matrix_wise(unsigned numberVars) const
    {
        return _tree->assemble_quadratic_expression_matrix_wise(numberVars);
    }
    /*! @copydoc  LazyQuadExprTreeNode::eval_element_linear()*/
    double eval_element_linear(unsigned index) const
    {
        return _tree->eval_element_linear(index);
    }
    /*! @copydoc  LazyQuadExprTreeNode::eval_element_constant()*/
    double eval_element_constant() const
    {
        return _tree->eval_element_constant();
    }
    /*! @copydoc  LazyQuadExprTreeNode::eval_element_quadratic()*/
    double eval_element_quadratic(unsigned int row, unsigned int col) const
    {
        return _tree->eval_element_quadratic(row, col);
    }
    /** @brief Operator+= for LazyQuadExpr*/
    LazyQuadExpr& operator+=(const LazyQuadExpr& RHS)
    {
        _tree = _tree + RHS._tree;
        return *this;
    }
    /** @brief Operator*= for LazyQuadExpr*/
    LazyQuadExpr& operator*=(const LazyQuadExpr& RHS)
    {
        _tree = _tree * RHS._tree;
        return *this;
    }
    /** @brief Operator-= for LazyQuadExpr*/
    LazyQuadExpr& operator-=(const LazyQuadExpr& RHS)
    {
        _tree = _tree - RHS._tree;
        return *this;
    }
    /** @brief Operator/= for LazyQuadExpr for scalar RHS*/
    LazyQuadExpr& operator/=(double scalar)
    {
        //if RHS not scalar, this throws
        _tree = _tree / LazyQuadExpr(scalar)._tree;
        return *this;
    }

  private:
    std::shared_ptr<LazyQuadExprTreeNode> _tree; /*!< The root node to the expression tree that can be evaluated to compute the expression*/
    friend LazyQuadExpr operator+(const LazyQuadExpr&, const LazyQuadExpr&);
    friend LazyQuadExpr operator-(const LazyQuadExpr&, const LazyQuadExpr&);
    friend LazyQuadExpr operator*(const LazyQuadExpr&, const LazyQuadExpr&);
    friend LazyQuadExpr operator-(const LazyQuadExpr&);
    friend LazyQuadExpr operator+(const LazyQuadExpr&);
    friend LazyQuadExpr operator/(const LazyQuadExpr& LHS, double scalar);
};

/** @brief Operator+ for LazyQuadExpr*/
inline LazyQuadExpr
operator+(const LazyQuadExpr& LHS)
{
    return LazyQuadExpr(LHS._tree);
}

/** @brief Operator+ for LazyQuadExpr*/
inline LazyQuadExpr
operator+(const LazyQuadExpr& LHS, const LazyQuadExpr& RHS)
{
    return LazyQuadExpr(LHS._tree + RHS._tree);
}

/** @brief Operator- for LazyQuadExpr*/
inline LazyQuadExpr
operator-(const LazyQuadExpr& LHS, const LazyQuadExpr& RHS)
{
    return LazyQuadExpr(LHS._tree - RHS._tree);
}

/** @brief Operator* for LazyQuadExpr*/
inline LazyQuadExpr
operator*(const LazyQuadExpr& LHS, const LazyQuadExpr& RHS)
{
    return LazyQuadExpr(LHS._tree * RHS._tree);
}

/** @brief Operator- for LazyQuadExpr*/
inline LazyQuadExpr
operator-(const LazyQuadExpr& LHS)
{
    return LazyQuadExpr(-LHS._tree);
}

/** @brief Operator/ for LazyQuadExpr with scalar RHS*/
inline LazyQuadExpr
operator/(const LazyQuadExpr& LHS, double scalar)
{
    return LazyQuadExpr(LHS._tree / LazyQuadExpr(scalar)._tree);
}

/** @brief Operator/ for division of a double by an LazyQuadExpr */
inline LazyQuadExpr
operator/(const double in1, const LazyQuadExpr& in2)
{
    throw MAiNGOException("  Error: LazyQuadExpr -- function 1/x not allowed in (MIQ)Ps."); // GCOVR_EXCL_LINE
}

/** @brief Operator/ for division of an int by an LazyQuadExpr */
inline LazyQuadExpr
operator/(const int in1, const LazyQuadExpr& in2)
{
    throw MAiNGOException("  Error: LazyQuadExpr -- function 1/x not allowed in (MIQ)Ps."); // GCOVR_EXCL_LINE
}


}    // namespace ubp
}    // namespace maingo


namespace mc {


//! @brief Specialization of the structure mc::Op for use of the type UbpQuadExpr as a template parameter in other MC++ types
template <>
struct Op<maingo::ubp::LazyQuadExpr> {
    typedef maingo::ubp::LazyQuadExpr QE;        /*!< typedef for easier usage */
    static QE sqr(const QE& x) { return x * x; } /*!< x^2 */
    static QE pow(const QE& x, const int n)
    {
        if (n == 0) {
            return QE(1.0);
        }
        if (n == 1) {
            return x;
        }
        if (n == 2) {
            return x * x;
        }
        throw std::runtime_error("  Error: UbpQuadExpr -- function pow with n <> 0,1,2 not allowed in (MIQ)Ps.");
    } /*!< powers are allowed up to order 2 */
    static QE pow(const QE& x, const double a)
    {
        if (a == 0) {
            return QE(1.0);
        }
        if (a == 1) {
            return x;
        }
        if (a == 2) {
            return x * x;
        }
        throw std::runtime_error("  Error: UbpQuadExpr -- function pow with a <> 0,1,2 not allowed in (MIQ)Ps.");
    }                                                                                                                                                                         /*!< power are allowed up to order 2 */
        static QE pow(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function pow(x,y) not allowed in (MIQ)Ps."); }                            /*!< x^y is not allowed */
        static QE pow(const double x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function pow(a,y) not allowed in (MIQ)Ps."); }                         /*!< c^x is not allowed */
        static QE pow(const int x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function pow(n,y) not allowed in (MIQ)Ps."); }                            /*!< d^x is not allowed */
        static QE prod(const unsigned int n, const QE* x) { throw std::runtime_error("  Error: UbpQuadExpr -- function prod not allowed in (MIQ)Ps."); }                      /*!< prod could be allowed but is currently not implemented */
        static QE monom(const unsigned int n, const QE* x, const unsigned* k) { throw std::runtime_error("  Error: UbpQuadExpr -- function monom not allowed in (MIQ)Ps."); } /*!< monom could be allowed but is currently not implemented */
        static QE point(const double c) { throw std::runtime_error("  Error: UbpQuadExpr -- function point not allowed in (MIQ)Ps."); }                                       /*!< point is not needed at all */
        static QE zeroone() { throw std::runtime_error("  Error: UbpQuadExpr -- function zeroone not allowed in (MIQ)Ps."); }                                                 /*!< zeroone is not needed at all */
        static void I(QE& x, const QE& y) { x = y; }                                                                                                                          /*!< even thou I should be understood as interval, it is implemented here as assignment */
        static double l(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function l not allowed in (MIQ)Ps."); }                                              /*!< no lower bound given */
        static double u(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function u not allowed in (MIQ)Ps."); }                                              /*!< no upper bound given */
        static double abs(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function abs not allowed in (MIQ)Ps."); }                                          /*!< abs is not allowed */
        static double mid(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function mid not allowed in (MIQ)Ps."); }                                          /*!< mid not given */
        static double diam(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function diam not allowed in (MIQ)Ps."); }                                        /*!< diam not given */
        static QE inv(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function inv not allowed in (MIQ)Ps."); }                                              /*!< inv is not allowed */
        static QE sqrt(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function sqrt not allowed in (MIQ)Ps."); }                                            /*!< sqrt is not allowed */
        static QE exp(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function exp not allowed in (MIQ)Ps."); }                                              /*!< exp is not allowed */
        static QE log(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function log not allowed in (MIQ)Ps."); }                                              /*!< log is not allowed */
        static QE xlog(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function xlog not allowed in (MIQ)Ps."); }                                            /*!< xlog is not allowed */
        static QE fabsx_times_x(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function fabsx_times_x not allowed in (MIQ)Ps."); }                          /*!< x*|x| is not allowed */
        static QE xexpax(const QE& x, const double a) { throw std::runtime_error("  Error: UbpQuadExpr -- function xexpax not allowed in (MIQ)Ps."); }                        /*!< x*exp(a*x) is not allowed */
        static QE lmtd(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function lmtd not allowed in (MIQ)Ps."); }                               /*!< lmtd is not allowed */
        static QE rlmtd(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function rlmtd not allowed in (MIQ)Ps."); }                             /*!< rlmtd is not allowed */
        static QE mid(const QE& x, const QE& y, const double k) { throw std::runtime_error("  Error: UbpQuadExpr -- function mid not allowed in (MIQ)Ps."); }
        static QE pinch(const QE& Th, const QE& Tc, const QE& Tp) { throw std::runtime_error("  Error: UbpQuadExpr -- function pinch not allowed in (MIQ)Ps."); }
        static QE euclidean_norm_2d(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function euclidean_norm_2d not allowed in (MIQ)Ps."); }     /*!< euclidean is not allowed */
        static QE expx_times_y(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function expx_times_y not allowed in (MIQ)Ps."); }               /*!< exp(x)*y is not allowed */
        static QE vapor_pressure(const QE& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
                                 const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { throw std::runtime_error("  Error: UbpQuadExpr -- function vapor_pressure not allowed in (MIQ)Ps."); } /*!< no thermodynamic function is not allowed */
        static QE ideal_gas_enthalpy(const QE& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
                                     const double p7 = 0) { throw std::runtime_error("  Error: UbpQuadExpr -- function ideal_gas_enthalpy not allowed in (MIQ)Ps."); } /*!< no thermodynamic function is not allowed */
        static QE saturation_temperature(const QE& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
                                         const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { throw std::runtime_error("  Error: UbpQuadExpr -- function saturation_temperature not allowed in (MIQ)Ps."); }                                                          /*!< no thermodynamic function is not allowed */
        static QE enthalpy_of_vaporization(const QE& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { throw std::runtime_error("  Error: UbpQuadExpr -- function enthalpy_of_vaporization not allowed in (MIQ)Ps."); } /*!< no thermodynamic function is not allowed */
        static QE cost_function(const QE& x, const double type, const double p1, const double p2, const double p3) { throw std::runtime_error("  Error: UbpQuadExpr -- function cost_function not allowed in (MIQ)Ps."); }                                                                              /*!< no cost function function is not allowed */
        static QE nrtl_tau(const QE& x, const double a, const double b, const double e, const double f) { throw std::runtime_error("  Error: UbpQuadExpr -- function nrtl_tau not allowed in (MIQ)Ps."); }                                                                                              /*!< no thermodynamic function is not allowed */
        static QE nrtl_dtau(const QE& x, const double b, const double e, const double f) { throw std::runtime_error("  Error: UbpQuadExpr -- function nrtl_dtau not allowed in (MIQ)Ps."); }                                                                                                            /*!< no thermodynamic function is not allowed */
        static QE nrtl_G(const QE& x, const double a, const double b, const double e, const double f, const double alpha) { throw std::runtime_error("  Error: UbpQuadExpr -- function nrtl_G not allowed in (MIQ)Ps."); }                                                                              /*!< no thermodynamic function is not allowed */
        static QE nrtl_Gtau(const QE& x, const double a, const double b, const double e, const double f, const double alpha) { throw std::runtime_error("  Error: UbpQuadExpr -- function nrtl_Gtau not allowed in (MIQ)Ps."); }                                                                        /*!< no thermodynamic function is not allowed */
        static QE nrtl_Gdtau(const QE& x, const double a, const double b, const double e, const double f, const double alpha) { throw std::runtime_error("  Error: UbpQuadExpr -- function nrtl_Gdtau not allowed in (MIQ)Ps."); }                                                                      /*!< no thermodynamic function is not allowed */
        static QE nrtl_dGtau(const QE& x, const double a, const double b, const double e, const double f, const double alpha) { throw std::runtime_error("  Error: UbpQuadExpr -- function nrtl_dGtau not allowed in (MIQ)Ps."); }                                                                      /*!< no thermodynamic function is not allowed */
        static QE iapws(const QE& x, const double type) { throw std::runtime_error("  Error: UbpQuadExpr -- function iapws not allowed in (MIQ)Ps."); }                                                                                                                                                 /*!< no thermodynamic function is not allowed */
        static QE iapws(const QE& x, const QE& y, const double type) { throw std::runtime_error("  Error: UbpQuadExpr -- function iapws not allowed in (MIQ)Ps."); }                                                                                                                                    /*!< no thermodynamic function is not allowed */
        static QE p_sat_ethanol_schroeder(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function p_sat_ethanol_schroeder not allowed in (MIQ)Ps."); }                                                                                                                                /*!< no thermodynamic function is not allowed */
        static QE rho_vap_sat_ethanol_schroeder(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function rho_vap_sat_ethanol_schroeder not allowed in (MIQ)Ps."); }                                                                                                                    /*!< no thermodynamic function is not allowed */
        static QE rho_liq_sat_ethanol_schroeder(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function rho_liq_sat_ethanol_schroeder not allowed in (MIQ)Ps."); }                                                                                                                    /*!< no thermodynamic function is not allowed */
        static QE covariance_function(const QE& x, const double type) { throw std::runtime_error("  Error: UbpQuadExpr -- function covariance_function not allowed in (MIQ)Ps."); }                                                                                                                     /*!< no thermodynamic function is not allowed */
        static QE acquisition_function(const QE& x, const QE& y, const double type, const double fmin) { throw std::runtime_error("  Error: UbpQuadExpr -- function acquisition_function not allowed in (MIQ)Ps."); }                                                                                   /*!< no thermodynamic function is not allowed */
        static QE gaussian_probability_density_function(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function gaussian_probability_density_function not allowed in (MIQ)Ps."); }                                                                                                    /*!< no thermodynamic function is not allowed */
        static QE regnormal(const QE& x, const double a, const double b) { throw std::runtime_error("  Error: UbpQuadExpr -- function regnormal not allowed in (MIQ)Ps."); }                                                                                                                            /*!< no thermodynamic function is not allowed */
        static QE fabs(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function fabs not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< fabs function is not allowed */
        static QE sin(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function sin not allowed in (MIQ)Ps."); }                                                                                                                                                                        /*!< trigonometric function is not allowed */
        static QE cos(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function cos not allowed in (MIQ)Ps."); }                                                                                                                                                                        /*!< trigonometric function is not allowed */
        static QE tan(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function tan not allowed in (MIQ)Ps."); }                                                                                                                                                                        /*!< trigonometric function is not allowed */
        static QE asin(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function asin not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< trigonometric function is not allowed */
        static QE acos(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function acos not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< trigonometric function is not allowed */
        static QE atan(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function atan not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< trigonometric function is not allowed */
        static QE sinh(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function sinh not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< trigonometric function is not allowed */
        static QE cosh(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function cosh not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< trigonometric function is not allowed */
        static QE tanh(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function tanh not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< trigonometric function is not allowed */
        static QE coth(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function coth not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< trigonometric function is not allowed */
        static QE asinh(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function asinh not allowed in (MIQ)Ps."); }                                                                                                                                                                    /*!< trigonometric function is not allowed */
        static QE acosh(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function acosh not allowed in (MIQ)Ps."); }                                                                                                                                                                    /*!< trigonometric function is not allowed */
        static QE atanh(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function atanh not allowed in (MIQ)Ps."); }                                                                                                                                                                    /*!< trigonometric function is not allowed */
        static QE acoth(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function acoth not allowed in (MIQ)Ps."); }                                                                                                                                                                    /*!< trigonometric function is not allowed */
        static QE erf(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function erf not allowed in (MIQ)Ps."); }                                                                                                                                                                        /*!< erf function is not allowed */
        static QE erfc(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function erfc not allowed in (MIQ)Ps."); }                                                                                                                                                                      /*!< erfc function is not allowed */
        static QE fstep(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function fstep not allowed in (MIQ)Ps."); }                                                                                                                                                                    /*!< discontinuous function is not allowed */
        static QE bstep(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function bstep not allowed in (MIQ)Ps."); }                                                                                                                                                                    /*!< discontinuous function is not allowed */
        static QE hull(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function hull not allowed in (MIQ)Ps."); }                                                                                                                                                         /*!< hull is not given */
        static QE min(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function min not allowed in (MIQ)Ps."); }                                                                                                                                                           /*!< min function is not allowed */
        static QE max(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function max not allowed in (MIQ)Ps."); }                                                                                                                                                           /*!< max function is not allowed */
        static QE pos(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function pos not allowed in (MIQ)Ps."); }                                                                                                                                                                        /*!< pos function is not allowed */
        static QE neg(const QE& x) { throw std::runtime_error("  Error: UbpQuadExpr -- function neg not allowed in (MIQ)Ps."); }                                                                                                                                                                        /*!< neg function is not allowed */
        static QE lb_func(const QE& x, const double lb) { throw std::runtime_error("  Error: UbpQuadExpr -- function lb_func not allowed in (MIQ)Ps."); }                                                                                                                                               /*!< lb_func function is not allowed */
        static QE ub_func(const QE& x, const double ub) { throw std::runtime_error("  Error: UbpQuadExpr -- function ub_func not allowed in (MIQ)Ps."); }                                                                                                                                               /*!< ub_func function is not allowed */
        static QE bounding_func(const QE& x, const double lb, const double ub) { throw std::runtime_error("  Error: UbpQuadExpr -- function bounding_func not allowed in (MIQ)Ps."); }                                                                                                                  /*!< bounding_func function is not allowed */
        static QE squash_node(const QE& x, const double lb, const double ub) { throw std::runtime_error("  Error: UbpQuadExpr -- function squash_node not allowed in (MIQ)Ps."); }                                                                                                                      /*!< squash_node function is not allowed */
        static QE single_neuron(const std::vector<QE>& x, const std::vector<double>& w, const double b, const int type) { throw std::runtime_error("  Error: UbpQuadExpr -- function single_neuron not allowed in (MIQ)Ps."); }                                                                         /*!< single_neuron function is not allowed */
        static QE sum_div(const std::vector<QE>& x, const std::vector<double>& coeff) { throw std::runtime_error("  Error: UbpQuadExpr -- function sum_div not allowed in (MIQ)Ps."); }                                                                                                                 /*!< sum_div function is not allowed */
        static QE xlog_sum(const std::vector<QE>& x, const std::vector<double>& coeff) { throw std::runtime_error("  Error: UbpQuadExpr -- function xlog_sum not allowed in (MIQ)Ps."); }                                                                                                               /*!< xlog_sum function is not allowed */
        static QE mc_print(const QE& x, const int number) { throw std::runtime_error("  Error: UbpQuadExpr -- function mc_print not allowed in (MIQ)Ps."); }                                                                                                                                            /*!< printing function is not allowed */
        static QE arh(const QE& x, const double k) { throw std::runtime_error("  Error: UbpQuadExpr -- function arh not allowed in (MIQ)Ps."); }                                                                                                                                                        /*!< arh function is not allowed */
        static QE cheb(const QE& x, const unsigned n) { throw std::runtime_error("  Error: UbpQuadExpr -- function cheb not allowed in (MIQ)Ps."); }                                                                                                                                                    /*!< cheb function is not allowed */
        static bool inter(QE& xIy, const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function inter not allowed in (MIQ)Ps."); }                                                                                                                                            /*!< interior is not given */
        static bool eq(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function eq not allowed in (MIQ)Ps."); }                                                                                                                                                           /*!< compare function is not allowed */
        static bool ne(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function ne not allowed in (MIQ)Ps."); }                                                                                                                                                           /*!< compare function is not allowed */
        static bool lt(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function lt not allowed in (MIQ)Ps."); }                                                                                                                                                           /*!< compare function is not allowed */
        static bool le(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function le not allowed in (MIQ)Ps."); }                                                                                                                                                           /*!< compare function is not allowed */
        static bool gt(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function gt not allowed in (MIQ)Ps."); }                                                                                                                                                           /*!< compare function is not allowed */
        static bool ge(const QE& x, const QE& y) { throw std::runtime_error("  Error: UbpQuadExpr -- function ge not allowed in (MIQ)Ps."); }                                                                                                                                                           /*!< discontinuous function is not allowed */
        static QE centerline_deficit(const QE& x, const double xLim, const double type) { throw std::runtime_error("  Error: UbpQuadExpr -- function centerline_deficit not allowed in (MIQ)Ps."); }                                                                                                    /*!< discontinuous function is not allowed */
        static QE wake_profile(const QE& x, const double type) { throw std::runtime_error("  Error: UbpQuadExpr -- function wake_profile not allowed in (MIQ)Ps."); }                                                                                                                                   /*!< discontinuous function is not allowed */
        static QE wake_deficit(const QE& x, const QE& r, const double a, const double alpha, const double rr, const double type1, const double type2) { throw std::runtime_error("  Error: UbpQuadExpr -- function wake_deficit not allowed in (MIQ)Ps."); }                                            /*!< discontinuous function is not allowed */
        static QE power_curve(const QE& x, const double type) { throw std::runtime_error("  Error: UbpQuadExpr -- function power_curve not allowed in (MIQ)Ps."); }                                                                                                                                     /*!< compare function is not allowed */
    };


}    // namespace mc

/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "babBounds.h"

#include <iostream>
#include <limits>
#include <string>


/**
*   @namespace babBase
*   @brief namespace holding all essentials of the babBase submodule
*/
namespace babBase {


/**
    * @namespace babBase::enums
    * @brief namespace holding all enums used for branching and B&B reporting
    */
namespace enums {


/**
        * @enum VT
        * @brief Enum for representing the Variable Type of an optimization variable as specified by the user.
        */
enum VT {
    VT_CONTINUOUS = 0, /*!< This is a continuous (i.e., real) variable. */
    VT_BINARY,         /*!< This is a binary variable. */
    VT_INTEGER         /*!< This is an integer variable. */
};


}    //  end namespace enums


/**
    * @class OptimizationVariable
    * @brief Class for representing an optimization variable specified by the user
    *
    * An optimization variable is characterized by an upper and lower bound, a variable type (enums::VT, optional), a branching priority (BP, optional), and a name (optional), all of which are private members.
    * Once instantiated, it cannot be modified. Each optimization variable also contains a flag (_feasible) that indicates if the bounds are consistent (lower bound <= upper bound) and in case of integer variables, whether the interval contains an integer value
    */
class OptimizationVariable {


  public:
    /**
        * @brief Constructor for the case all three optional parameters are used.
        *
        * @param[in] variableBoundsIn is the Bounds object representing lower and upper bounds on the optimization variable
        * @param[in] variableType is the Variable Type of this variable
        * @param[in] branchingPriority is the Branching Priority of this variable
        * @param[in] nameIn is the name of this variable
        */
    OptimizationVariable(const Bounds &variableBoundsIn, const enums::VT variableType, const unsigned branchingPriority, const std::string nameIn):
        _bounds(variableBoundsIn), _userSpecifiedBounds(variableBoundsIn), _variableType(variableType),
        _branchingPriority(branchingPriority), _name(nameIn), _feasible(variableBoundsIn.are_consistent())
    {
        _round_and_check_discrete_bounds();
    }

    /**
        * @brief Constructor for the case only a variable type and a branching priority is specified in addition to the bounds. The variable name is empty
        *
        * @param[in] variableBoundsIn is the Bounds object representing lower and upper bounds on the optimization variable
        * @param[in] variableType is the Variable Type of this variable
        * @param[in] branchingPriority is the Branching Priority of this variable
        */
    OptimizationVariable(const Bounds &variableBoundsIn, const enums::VT variableType, const unsigned branchingPriority):
        _bounds(variableBoundsIn), _userSpecifiedBounds(variableBoundsIn), _variableType(variableType),
        _branchingPriority(branchingPriority), _name(), _feasible(variableBoundsIn.are_consistent())
    {
        _round_and_check_discrete_bounds();
    }

    /**
        * @brief Constructor for the case only a variable type and a name is specified in addition to the bounds. The variable is used for branching
        *
        * @param[in] variableBoundsIn is the Bounds object representing lower and upper bounds on the optimization variable
        * @param[in] variableType is the Variable Type of this variable
        * @param[in] nameIn is the name of this variable
        */
    OptimizationVariable(const Bounds &variableBoundsIn, const enums::VT variableType, const std::string nameIn):
        _bounds(variableBoundsIn), _userSpecifiedBounds(variableBoundsIn), _variableType(variableType),
        _branchingPriority(1), _name(nameIn), _feasible(variableBoundsIn.are_consistent())
    {
        _round_and_check_discrete_bounds();
    }

    /**
        * @brief Constructor for the case only a branching priority and a name is specified in addition to the bounds. The variable is assumed to be continuous
        *
        * @param[in] variableBoundsIn is the Bounds object representing lower and upper bounds on the optimization variable
        * @param[in] branchingPriority is the Branching Priority of this variable
        * @param[in] nameIn is the name of this variable
        */
    OptimizationVariable(const Bounds &variableBoundsIn, const unsigned branchingPriority, const std::string nameIn):
        _bounds(variableBoundsIn), _userSpecifiedBounds(variableBoundsIn), _variableType(enums::VT_CONTINUOUS),
        _branchingPriority(branchingPriority), _name(nameIn), _feasible(variableBoundsIn.are_consistent())
    {
    }

    /**
        * @brief Constructor for the case only a variable type is specified in addition to the bounds. The variable is used for branching, and the name is empty
        *
        * @param[in] variableBoundsIn is the Bounds object representing lower and upper bounds on the optimization variable
        * @param[in] variableType is the Variable Type of this variable
        */
    OptimizationVariable(const Bounds &variableBoundsIn, const enums::VT variableType):
        _bounds(variableBoundsIn), _userSpecifiedBounds(variableBoundsIn), _variableType(variableType),
        _branchingPriority(1), _name(), _feasible(variableBoundsIn.are_consistent())
    {
        _round_and_check_discrete_bounds();
    }

    /**
        * @brief Constructor for the case only a branching priority is specified in addition to the bounds. The variable is thus assumed to be continuous, and the name is empty
        *
        * @param[in] variableBoundsIn is the Bounds object representing lower and upper bounds on the optimization variable
        * @param[in] branchingPriority is the Branching Priority of this variable
        */
    OptimizationVariable(const Bounds &variableBoundsIn, const unsigned branchingPriority):
        _bounds(variableBoundsIn), _userSpecifiedBounds(variableBoundsIn), _variableType(enums::VT_CONTINUOUS),
        _branchingPriority(branchingPriority), _name(), _feasible(variableBoundsIn.are_consistent())
    {
    }

    /**
        * @brief Constructor for the case only a name is specified in addition to the bounds. The variable is thus assumed to be continuous, and it is used for branching
        *
        * @param[in] variableBoundsIn is the Bounds object representing lower and upper bounds on the optimization variable
        * @param[in] nameIn is the name of this variable
        */
    OptimizationVariable(const Bounds &variableBoundsIn, const std::string nameIn):
        _bounds(variableBoundsIn), _userSpecifiedBounds(variableBoundsIn), _variableType(enums::VT_CONTINUOUS),
        _branchingPriority(1), _name(nameIn), _feasible(variableBoundsIn.are_consistent())
    {
    }

    /**
        * @brief Minimal constructor requiring only the required information. The variable is thus assumed to be continuous, it is used for branching, and the name is empty
        *
        * @param[in] variableBoundsIn is the Bounds object representing lower and upper bounds on the optimization variable
        */
    OptimizationVariable(const Bounds &variableBoundsIn):
        _bounds(variableBoundsIn), _userSpecifiedBounds(variableBoundsIn), _variableType(enums::VT_CONTINUOUS),
        _branchingPriority(1), _name(), _feasible(variableBoundsIn.are_consistent())
    {
    }

    /**
        * @brief Constructor for the case only a variable type, branching priority and a variable name are specified. The variable bounds are not defined. This function currently just throws an exception, except in case of a binary variable.
        *
        * @param[in] variableType is the Variable Type of this variable
        * @param[in] branchingPriority is the Branching Priority of this variable
        * @param[in] nameIn is the name of this variable
        */
    OptimizationVariable(const enums::VT variableType, const unsigned branchingPriority, const std::string nameIn):
        _bounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
        _userSpecifiedBounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
        _variableType(variableType), _branchingPriority(branchingPriority), _name(nameIn)
    {
        _infer_and_set_bounds_or_throw();
    }

    /**
        * @brief Constructor for the case only a variable type and branching priority are specified. The variable bounds are not defined. This function currently just throws an exception, except in case of a binary variable.
        *
        * @param[in] variableType is the Variable Type of this variable
        * @param[in] branchingPriority is the Branching Priority of this variable
        */
    OptimizationVariable(const enums::VT variableType, const unsigned branchingPriority):
        _bounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
        _userSpecifiedBounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
        _variableType(variableType), _branchingPriority(branchingPriority), _name()
    {
        _infer_and_set_bounds_or_throw();
    }

    /**
        * @brief Constructor for the case only a variable type and a variable name are specified. The variable bounds are not defined. This function currently just throws an exception, except in case of a binary variable.
        *
        * @param[in] variableType is the Variable Type of this variable
        * @param[in] nameIn is the name of this variable
        */
    OptimizationVariable(const enums::VT variableType, const std::string nameIn):
        _bounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
        _userSpecifiedBounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
        _variableType(variableType), _branchingPriority(1), _name(nameIn)
    {
        _infer_and_set_bounds_or_throw();
    }

    /**
        * @brief Constructor for the case only a variable type is specified. The variable bounds are not defined. This function currently just throws an exception, except in case of a binary variable.
        *
        * @param[in] variableType is the Variable Type of this variable
        */
    OptimizationVariable(const enums::VT variableType):
        _bounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
        _userSpecifiedBounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
        _variableType(variableType), _branchingPriority(1), _name()
    {
        _infer_and_set_bounds_or_throw();
    }

    /**
        * @brief Constructor for the case only branching priority and a variable name arespecified. The variable bounds are not defined. This function currently just throws an exception.
        *
        * @param[in] branchingPriority is the Branching Priority of this variable
        * @param[in] nameIn is the name of this variable
        */
    OptimizationVariable(const unsigned branchingPriority, const std::string nameIn);

    /**
        * @brief Constructor for the case only a branching priority is specified. The variable bounds are not defined. This function currently just throws an exception.
        *
        * @param[in] branchingPriority is the Branching Priority of this variable
        */
    OptimizationVariable(const unsigned branchingPriority);

    /**
        * @brief Constructor for the case only a variable name is specified. The variable bounds are not defined. This function currently just throws an exception.
        *
        * @param[in] nameIn is the name of this variable
        */
    OptimizationVariable(const std::string nameIn);

    /**
        * @brief Default constructor The variable bounds are not defined. This function currently just throws an exception.
        */
    OptimizationVariable();

    /**
        * @brief Function for querying the branching priority.
        */
    void set_branching_priority(const unsigned priority) { _branchingPriority = priority; }

    /**
        * @brief Function for querying the lower variable bound.
        */
    double get_lower_bound() const { return _bounds.lower; }

    /**
        * @brief Function for querying the upper variable bound.
        */
    double get_upper_bound() const { return _bounds.upper; }

    /**
        * @brief Function for querying the lower variable bound as originally specified by the user.
        */
    double get_user_lower_bound() const { return _userSpecifiedBounds.lower; }

    /**
        * @brief Function for querying the upper variable bound as originally specified by the user.
        */
    double get_user_upper_bound() const { return _userSpecifiedBounds.upper; }

    /**
        * @brief Function for querying the midpoint of the variable range.
        */
    double get_mid() const { return 0.5 * (_bounds.lower + _bounds.upper); }

    /**
        * @brief Function for querying the variable name.
        */
    std::string get_name() const { return _name; }

    /**
        * @brief Function for querying the variable type.
        */
    enums::VT get_variable_type() const { return _variableType; }

    /**
        * @brief Function for querying the branching priority.
        */
    unsigned get_branching_priority() const { return _branchingPriority; }

    /**
        * @brief Function for querying whether the host set of the variable is non-empty
        */
    bool has_nonempty_host_set() const { return _feasible; }

    /**
        * @brief Function for querying whether the bounds have been modified (e.g., by rounding to integer values) compared to those specified by the user
        */
    bool bounds_changed_from_user_input() const { return ((_bounds != _userSpecifiedBounds) ? true : false); }

    /**
        * @brief operator << overloaded for Bounds for easier output
        *
        * @param[out] os is the outstream to be written to
        * @param[in] ov is an optimization variable to be written
        */
    friend std::ostream &operator<<(std::ostream &os, const OptimizationVariable &ov)
    {
        std::string typestring;
        std::string leftPara  = "{";
        std::string rightPara = "}";
        switch (ov.get_variable_type()) {
            case babBase::enums::VT_BINARY:
                typestring = "Binary";
                break;
            case babBase::enums::VT_CONTINUOUS:
                typestring = "Continous";
                leftPara   = "[";
                rightPara  = "]";
                break;
            case babBase::enums::VT_INTEGER:
                typestring = "Integer";
                break;
        }
        os << "Name: " << ov.get_name() << " " << typestring << " Bounds: " << leftPara << ov._bounds.lower << "," << ov._bounds.upper << rightPara;
        return os;
    };

  private:
    /**
        * @name Internal variables for storing information on the OptimizationVariable
        */
    /**@{*/
    Bounds _bounds;                    /*!< bounds on the optimization variable (potentially altered from the user-specified through rounding in case of discrete variables)*/
    Bounds _userSpecifiedBounds;       /*!< bounds on the optimization variable as specified by the user (i.e., before potential rounding in case of discrete variables)*/
    enums::VT _variableType;           /*!< optional: type of variable (default: enums::VT_CONTINUOUS) */
    unsigned _branchingPriority;       /*!< optional: whether this variable should be branched on (default: 1) */
    std::string _name;                 /*!< optional: name of the variable */
    bool _feasible;                    /*!< flag indicating whether the variable has a non-empty host set (upper bound >= lower bound; contains integer/binary values where approriate) */
    /**@}*/

    /**
        * @brief sanity check of user-given bounds on discrete variables
        *
        *   Rounds non-discrete bounds to discrete values and updates the private member _feasible depending on whether discrete ub < discrete lb.
        *
        */
    void _round_and_check_discrete_bounds();

    /**
        * @brief Auxiliary function for determining bounds in case the user did not specify any
        *
        *   Attemps to infer bounds from other information (e.g., variable type).
        *   If this is possible, the inferred bounds are stored in the corresponding member variables.
        *   If not, an exception is thrown.
        *
        */
    void _infer_and_set_bounds_or_throw();
};


}    // namespace babBase

/**********************************************************************************
 * Copyright (c) 2019-2024 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include <string>
#include <vector>


namespace maingo {


/**
* @enum PROBLEM_STRUCTURE
* @brief Enum for representing the problem structure.
*/
enum PROBLEM_STRUCTURE {
    LP = 0, /*!< linear program */
    MIP,    /*!< mixed-integer linear program */
    QP,     /*!< quadratically constrained program */
    MIQP,   /*!< mixed-integer quadratically constrained program */
    NLP,    /*!< non-linear program */
    DNLP,   /*!< non-smooth non-linear program */
    MINLP   /*!< mixed-integer non-linear program */
};

/**
* @enum CONSTRAINT_TYPE
* @brief Enum for representing the constraint type.
*/
enum CONSTRAINT_TYPE {
    OBJ = 0,         /*!< objective */
    INEQ,            /*!< inequality */
    EQ,              /*!< equality */
    INEQ_REL_ONLY,   /*!< relaxation only inequality */
    EQ_REL_ONLY,     /*!< relaxations only equality */
    INEQ_SQUASH,     /*!< squash inequality is meant to be used with the squash_node function. No tolerances are allowed for a squash inequality */
    AUX_EQ_REL_ONLY, /*!< auxiliary relaxation only equality */
    OUTPUT,          /*!< output function */
    TYPE_UNKNOWN     /*!< unknown function type */
};

/**
* @enum CONSTRAINT_CONVEXITY
* @brief Enum for representing the constraint convexity.
*/
enum CONSTRAINT_CONVEXITY {
    CONV_NONE = 0, /*!< the constraint has no specific convexity properties */
    CONVEX,        /*!< the constraint is convex */
    CONCAVE        /*!< the constraint is concave */
};

/**
* @enum CONSTRAINT_MONOTONICITY
* @brief Enum for representing the constraint monotonicity.
*/
enum CONSTRAINT_MONOTONICITY {
    MON_NONE = 0, /*!< the constraint has no specific monotonicity properties */
    INCR,         /*!< the constraint is monotonically increasing */
    DECR          /*!< the constraint is monotonically decreasing */
};

/**
* @enum CONSTRAINT_DEPENDENCY
* @brief Enum for representing the constraint dependency.
*        Note that the dependency is increasing meaning that linear is a subset of bilinear which is a subset of quadratic etc.
*/
enum CONSTRAINT_DEPENDENCY {
    DEP_UNKNOWN = 0, /*!< unknown dependency type */
    LINEAR,          /*!< linear */
    BILINEAR,        /*!< bilinear */
    QUADRATIC,       /*!< quadratic */
    POLYNOMIAL,      /*!< polynomial */
    RATIONAL,        /*!< rational */
    NONLINEAR        /*!< nonlinear */
};

/**
    * @struct Constraint
    * @brief Struct for storing information about constraints
    *
    * This struct stores constraint properties such as constraint type, convexity, monotonicity. It also stores several indices for easier access to the correct constraint such as
    * the index in the originalFunctions which was read in from the model, index in the constantFunctions vector, index in the nonConstantFunctions vector,
    * index among linear functions, and index among nonlinear function. Moreover, it holds the type of a constraint, e.g., linear, quadratic, bilinear etc., the number of participating
    * variables in the constraint, and the number of (non)linearly participating variables in the given constraint
    * This struct does not hold the FFVar value of the constraint.
    */
struct Constraint {

  public:
    /**
            * @brief Default conststructor
            */
    Constraint();

    /**
            * @brief Conststructor for non-constant constraints with a possible name
            */
    Constraint(const CONSTRAINT_TYPE typeIn, const unsigned indexOriginalIn, const unsigned indexTypeIn, const unsigned indexNonconstantIn,
               const unsigned indexTypeNonconstantIn, const std::string& nameIn = "");

    /**
            * @brief Conststructor for constant constraints with a possible name
            */
    Constraint(const CONSTRAINT_TYPE typeIn, const unsigned indexOriginalIn, const unsigned indexTypeIn, const unsigned indexConstantIn,
               const unsigned indexTypeConstantIn, const bool isConstantIn,
               const bool isFeasibleIn, const double valueIn, const std::string& nameIn = "");

    Constraint(const Constraint&)                         = default;
    Constraint(Constraint&&)                              = default;
    Constraint& operator=(const Constraint& constraintIn) = default;
    Constraint& operator=(Constraint&& constraintIn)      = default;
    ~Constraint()                                         = default;


    std::string name;                             /*!< Name of the constraint */
    double constantValue;                         /*!< Value of the constraint (only used if the constraint is constant) */
    unsigned nparticipatingVariables;             /*!< Number of different participating variables in the constraint */
    std::vector<unsigned> participatingVariables; /*!< Vector holding the indices of variables participating in the constraint */
    /**
            * @name Constraint properties
            */
    /**@{*/
    CONSTRAINT_TYPE type;                 /*!< Type of the constraint */
    CONSTRAINT_CONVEXITY convexity;       /*!< Convexity of the constraint */
    CONSTRAINT_MONOTONICITY monotonicity; /*!< Monotonicity of the constraint */
    CONSTRAINT_DEPENDENCY dependency;     /*!< Dependency of the constraint */
    bool isConstant;                      /*!< Constness of constraint */
    bool isFeasible;                      /*!< Flag whether the constraint is feasible (only used if the constraint is constant) */
    /**@}*/
    /**
            * @name Constraint indices
            */
    /**@{*/
    unsigned int indexOriginal;        /*!< Index of the constraint when read in by evaluate, 0 = obj, 1 - x ineq, x+1 - y eq etc. For outputs this is the original ordering of outputs when read in the first time*/
    unsigned int indexNonconstant;     /*!< Index of the constraint among non-constant constraints (objective is always non-constant!) */
    unsigned int indexNonconstantUBP;  /*!< Index of the constraint among non-constant constraints (objective is always non-constant!) for the UBS */
    unsigned int indexConstant;        /*!< Index of the constraint among constant constraints */
    unsigned int indexLinear;          /*!< Index of the constraint among linear constraints */
    unsigned int indexNonlinear;       /*!< Index of the constraint among nonlinear constraints */
    unsigned int indexType;            /*!< Index of the constraint among constraints of the same type */
    unsigned int indexTypeNonconstant; /*!< Index of the constraint among nonconstant constraints of the same type */
    unsigned int indexTypeConstant;    /*!< Index of the constraint among constant constraints of the same type */
                                       /**@}*/
};


}    // end namespace maingo
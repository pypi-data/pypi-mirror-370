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

#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <string>
#include <type_traits>


namespace babBase {


/**
 * @brief compares if two floating numbers are very close to each other from:https://en.cppreference.com/w/cpp/types/numeric_limits/epsilon
 *
 * @param[in] x first object
 * @param[in] y second object
 * @param[in] ulp units in last place
 */
template <class T>
typename std::enable_if<!std::numeric_limits<T>::is_integer, bool>::type
almost_equal(T x, T y, int ulp = 2)
{
    // the machine epsilon has to be scaled to the magnitude of the values used
    // and multiplied by the desired precision in ULPs (units in the last place)
    return std::abs(x - y) <= std::numeric_limits<T>::epsilon() * std::abs(x + y) * ulp
           // unless the result is subnormal
           || std::abs(x - y) < std::numeric_limits<T>::min();
}


/**
 * @brief Function for checking if LBD is larger than UBD, or smaller by not more than the specified tolerance
 *
 * @param[in] LBD is the lower bound
 * @param[in] UBD is the upper bound
 * @param[in] epsilonR is the relative tolerance
 * @param[in] epsilonA is the absolute tolerance
 */
inline bool
larger_or_equal_within_rel_and_abs_tolerance(const double LBD, const double UBD, const double epsilonR, const double epsilonA)
{
    bool absDone = (LBD >= (UBD - epsilonA));                // Done means that absolute criterion is met
    bool relDone = (LBD >= (UBD - fabs(UBD) * epsilonR));    // Done means that relative criterion is met
    bool done    = (absDone || relDone);                     // If either criterion is met we are done

    return done;
}


/**
 * @struct BabLog
 * @brief Struct storing logging information during B&B prodcedure
 */
struct BabLog {
    std::queue<double> time;       /*!< queue for storing CPU time for logging */
    std::queue<double> LBD;        /*!< queue for storing overall LBD for logging */
    std::queue<double> UBD;        /*!< queue for storing overall UBD for logging */
    std::queue<double> iters;      /*!< queue for storing number of iterations for logging */
    std::queue<double> nodeid;     /*!< queue for storing current node ID for logging */
    std::queue<double> curLB;      /*!< queue for storing current node lower bound for logging */
    std::queue<double> nodesLeft;  /*!< queue for storing number of nodes left for logging */
    std::queue<double> absGap;     /*!< queue for storing absolute optimality gap for logging */
    std::queue<double> relGap;     /*!< queue for storing relative optimality gap  for logging */
    std::string solutionStatus;    /*!< string storing information on the solution status */
    std::string logFileName;       /*!< string storing name of the log file */
    std::string csvIterationsName; /*!< string storing name of the csv iterations file */
    std::string csvGeneralName;    /*!< string storing name of the csv general file */
    bool reachedMinNodeSize;       /*!< bool for saving information if minimum node size has been reached within B&B */

    /**
     * @brief Clears all logging information
     */
    void clear()
    {
        time               = std::queue<double>();
        LBD                = std::queue<double>();
        UBD                = std::queue<double>();
        iters              = std::queue<double>();
        nodeid             = std::queue<double>();
        curLB              = std::queue<double>();
        nodesLeft          = std::queue<double>();
        absGap             = std::queue<double>();
        relGap             = std::queue<double>();
        solutionStatus     = "";
        reachedMinNodeSize = false;
        if (logFileName.empty()) {
            logFileName = "bab.log";
        }
        if (csvIterationsName.empty()) {
            csvIterationsName = "bab_Report_Iterations.csv";
        }
        if (csvGeneralName.empty()) {
            csvGeneralName = "bab_Report_General.csv";
        }
    }
};


namespace enums {


/**
 * @enum BAB_RETCODE
 * @brief Enum for representing the return codes returned by the B&B solver.
 */
enum BAB_RETCODE {
    GLOBALLY_OPTIMAL = 0, /*!< globally optimal solution found */
    INFEASIBLE,           /*!< problem is infeasible */
    GLOBAL_MIN_NODE_SIZE, /*!< reached minimum node size, user defined optimality tolerances could not be reached */
    MAX_TIME,             /*!< maximum time reached */
    MAX_ITERATIONS,       /*!< maximum number of iterations reached */
    MAX_NODES,            /*!< maximum number of nodes reached */
    FEASIBLE_POINT_ONLY,  /*!< user only requested a feasible point which has now been found */
    TARGET_UBD,           /*!< reached user-specified target upper bound */
    TARGET_LBD,           /*!< reached user-specified target lower bound */
    NOT_SOLVED_YET,       /*!< problem has not been solved yet */
	IS_WORKER			  /*!< this process is a worker */
};

/**
 * @enum NS
 * @brief Enum for selecting the Node Selection heuristic.
 */
enum NS {
    NS_BESTBOUND = 0, /*!< (=0): use node with lowest lower bound currently in the tree */
    NS_DEPTHFIRST,    /*!< (=1): use node with highest ID (i.e., the one created the most recently) */
    NS_BREADTHFIRST   /*!< (=2): use node with lower ID (i.e., the oldest one still in the tree) */
};

/**
 * @enum BV
 * @brief Enum for selecting the Branching Variable selection heuristic.
 */
enum BV {
    BV_ABSDIAM = 0, /*!< (=0): use dimension with largest absolute diameter */
    BV_RELDIAM,     /*!< (=1): use dimension with largest diameter relative to the original one */
    BV_PSCOSTS      /*!< (=2): use pseudo costs to select the next branching variable*/
};

/**
 * @enum iterationType
 * @brief Enum for selecting the iteration type.
*/
enum ITERATION_TYPE {
    NORMAL_ITERATION,
    SIBLING_ITERATION,
};

}    // end namespace enums


/**
 * @class OutVar
 * @brief Helper class that can be used to enforce the caller to explicitly state that the variable he passed may be changed
 *
 * Use as  int a=3; foo(out_par(a)); or foo(OutVar<int>(a));
 */
template <class T>
class OutVar {

  public:
    typedef T type; /*!< type of OutVar*/

    explicit OutVar(T& ref) noexcept:
        _ptr(std::addressof(ref)) {}                       /*!< Copy */
    OutVar(T&&)                    = delete;               /*!< Don't use r-value copy constructor */
    OutVar(const OutVar&) noexcept = default;              /*!< Use default copy constructor */
    OutVar& operator=(const OutVar& x) noexcept = default; /*!<  Use default assignment */

    operator T&() const noexcept { return *_ptr; } /*!<  Access via () */
    T& get() const noexcept { return *_ptr; }      /*!<  Get reference */

  private:
    T* _ptr; /*!< Pointer to object of type T */
};

/**
 * @brief Function for casting to OutVar<type T>
 *
 * @param[in] arr is the argument to be casted
 */
template <typename T>
OutVar<T>
out_par(T& arr)
{
    return OutVar<T>(arr);
}


}    // end namespace babBase
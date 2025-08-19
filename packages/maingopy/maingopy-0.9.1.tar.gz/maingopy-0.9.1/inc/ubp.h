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

#include "constraint.h"
#include "logger.h"
#include "mcForward.h"
#include "returnCodes.h"
#include "settings.h"
#include "ubpStructure.h"

#include "babNode.h"
#include "babUtils.h"

#include <memory>
#include <vector>


namespace maingo {


namespace ubp {


struct DagObj;

/**
* @class UpperBoundingSolver
* @brief Base class for wrappers for handling the upper bounding problems
*
* This is the base class for the upper bounding solvers that construct and solve upper bounding problems. The base class simply checks feasibility of the initial point (or midpoint if none is given).
* The derived classes mainly need to implement the solve method for solving the upper bounding problem, as well as the set_effort method for choosing between a high and low solution effort.
*
*/
class UpperBoundingSolver {

	template<class subsolver_class>
  friend class UbsTwoStage;

  public:
    /**
		* @enum UBS_USE
		* @brief Enum for communicating what the intended purpose of the solver is. This determines which settings are used.
		*/
    enum UBS_USE {
        USE_PRE = 0, /*!< (=0): used during pre-processing */
        USE_BAB      /*!< (=1): used in Branch-and-Bound */
    };

    /**
		* @brief Constructor, stores information on the problem and constructs an own copy of the directed acyclic graph
		*
		* @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
		* @param[in] DAGvars are the variables corresponding to the DAG
		* @param[in] DAGfunctions are the functions corresponding to the DAG
		* @param[in] variables is a vector containing the initial optimization variables defined in problem.h
		* @param[in] nineqIn is the number of inequality constraints
		* @param[in] neqIn is the number of equality constraints
        * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
		* @param[in] settingsIn is a pointer to the MAiNGO settings
		* @param[in] loggerIn is a pointer to the MAiNGO logger object
		* @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
		* @param[in] useIn communicates what the solver is to be used for
		*/
    UpperBoundingSolver(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
                        const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn);

    /**
		* @brief Virtual destructor, only needed to make sure the correct destructor of the derived classes is called
		*/
    virtual ~UpperBoundingSolver() {}

    /**
		* @brief Function called by B&B solver for solving the upper bounding problem on the current node. This calls the internal (protected) function solve_nlp that needs to be re-implemented by the derived classes
		*
		* @param[in] currentNode is the B&B node for which the lower bounding problem should be solved
		* @param[out] objectiveValue is the objective value obtained for the solution point of the upper bounding problem (need not be a local optimum!)
		* @param[in,out] solutionPoint is the point at which objectiveValue was achieved (can in principle be any point within the current node!); it is also used for communicating the initial point (usually the LBP solution point)
		* @return Return code, either SUBSOLVER_FEASIBLE or SUBSOLVER_INFEASIBLE, indicating whether the returned solutionPoint (!!) is feasible or not
		*/
    virtual SUBSOLVER_RETCODE solve(babBase::BabNode const &currentNode, double &objectiveValue, std::vector<double> &solutionPoint);

    /**
		* @brief Multistart heuristic for automatically solving the UBP from multiple starting points
		*
		* @param[in] currentNode is the B&B node for which the lower bounding problem should be solved
		* @param[out] objectiveValue is the objective value obtained for the solution point of the upper bounding problem (need not be a local optimum!)
		* @param[in,out] solutionPoint is the point at which objectiveValue was achieved (can in principle be any point within the current node!); it is also used for communicating the user-defined initial point (if any)
		* @param[out] feasible is a vector containing information about which multistart runs were successful in finding a feasible point (only used if corresponding setting PRE_printEveryLocalSerach is on)
		* @param[out] optimalObjectives is a vector containing the optimal objectives found (either all of them if PRE_printEveryLocalSerach is enabled, or only the ones with significant improvements)
		* @param[out] initialPointFeasible states whether or not the user-specified point was found to be feasible
		* @return Return code, either RETCODE_FEASIBLE or RETCODE_INFEASIBLE, indicating whether a feasible solution has been found
		*/
    SUBSOLVER_RETCODE multistart(babBase::BabNode const &currentNode, double &objectiveValue, std::vector<double> &solutionPoint, std::vector<SUBSOLVER_RETCODE> &feasible, std::vector<double> &optimalObjectives, bool &initialPointFeasible);

    /**
		* @brief Function for checking feasibility of a point
		*
		* @param[in] currentPoint is the point to be checked
		* @param[in] objectiveValue is the objective value of the current point
		*/
    SUBSOLVER_RETCODE check_feasibility(const std::vector<double> &currentPoint, double &objectiveValue) const;

#ifdef HAVE_GROWING_DATASETS
    /**
	* @brief Function for changing objective in dependence of a (reduced) dataset
	*
	* @param[in] indexDataset is the index number of the (reduced) dataset to be used
	*/
    void change_growing_objective(const unsigned int indexDataset);

    /**
    * @brief Function for passing position of data points to solver
    *
    * @param[in] datasets is a pointer to a vector containing the size of all available datasets
    * @param[in] indexFirstData is the position of the first objective per data in MAiNGO::_DAGfunctions
	*/
    void pass_data_position_to_solver(const std::shared_ptr<std::vector<unsigned int>> datasets, const unsigned int indexFirstData);

	/**
    * @brief Function for telling solver whether mean squared error or summed squared error is used as objective function
    *
    * @param[in] useMse is the boolean to be passed
	*/
    void pass_use_mse_to_solver(const bool useMse);
#endif    //HAVE_GROWING_DATASETS

  protected:
    /**
		* @brief Function for actually solving the NLP sub-problem. This needs to be re-defined in derived classes to call specific sub-solvers
		*
		* @param[in] lowerVarBounds is the vector containing the lower bounds on the variables within the current node
		* @param[in] upperVarBounds is the vector containing the upper bounds on the variables within the current node
		* @param[out] objectiveValue is the objective value obtained for the solution point of the upper bounding problem (need not be a local optimum!)
		* @param[in,out] solutionPoint is the point at which objectiveValue was achieved (can in principle be any point within the current node!); it is also used for communicating the initial point (usually the LBP solution point)
		* @return Return code, either SUBSOLVER_FEASIBLE or SUBSOLVER_INFEASIBLE, indicating whether the returned solutionPoint (!!) is feasible or not
		*/
    virtual SUBSOLVER_RETCODE _solve_nlp(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, double &objectiveValue, std::vector<double> &solutionPoint);

    /**
		* @name Functions for checking feasibility of a given point
		*/
    /**@{*/
    /**
		* @brief Function checking if inequality constraints are fulfilled
		*
		* @param[in] modelOutput holds the values of all constraints of the model
		*/
    SUBSOLVER_RETCODE _check_ineq(const std::vector<double> &modelOutput) const;

    /**
		* @brief Function checking if squash inequality constraints are fulfilled (no tolerance allowed)
		*
		* @param[in] modelOutput holds the values of all constraints of the model
		*/
    SUBSOLVER_RETCODE _check_ineq_squash(const std::vector<double> &modelOutput) const;

    /**
		* @brief Function checking if equality constraints are fulfilled
		*
		* @param[in] modelOutput holds the values of all constraints of the model
		*/
    SUBSOLVER_RETCODE _check_eq(const std::vector<double> &modelOutput) const;

    /**
		* @brief Function checking if bounds are fulfilled
		*
		* @param[in] currentPoint holds the values of the current point
		*/
    SUBSOLVER_RETCODE _check_bounds(const std::vector<double> &currentPoint) const;

    /**
		* @brief Function checking if discrete variables are indeed discrete
		*
		* @param[in] currentPoint holds the values of the current point
		*/
    SUBSOLVER_RETCODE _check_integrality(const std::vector<double> &currentPoint) const;
    /**@}*/

    /**
		* @brief Function for determining the number of variables participating in each function and the type of a function (linear, bilinear, quadratic, non-linear)
		*/
    void _determine_structure();

    /**
		* @brief Function for setting the information about the sparsity structure in the Jacobian
		*/
    void _determine_sparsity_jacobian();

    /**
		* @brief Function for determining the non-zero entries in the Hessian of the Lagrangian function
		*/
    void _determine_sparsity_hessian();

    /**
		* @brief Function for generating a point used in multistart
		*
		* @param[in] usedCenter is a flag indicating whether the mid point has already been used
		* @param[in] lowerVarBounds holds lower bounds of variables
		* @param[in] upperVarBounds holds upper bounds of variables
		*/
    std::vector<double> _generate_multistart_point(bool &usedCenter, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
        * @name Pointers to several objects. Note that these are NOT const, since if we want to resolve with MAiNGO, the pointers have to change
        */
    /**@{*/
    std::shared_ptr<Settings> _maingoSettings;                      /*!< pointer to object holding MAiNGO settings */
    std::shared_ptr<Logger> _logger;                                /*!< pointer to MAiNGO logger */
    std::shared_ptr<DagObj> _DAGobj;                                /*!< pointer to object containing DAG for upper bounding */
    UBS_USE _intendedUse;                                           /*!< object storing information about the intended use of this UpperBoundingSolver object */
    std::shared_ptr<std::vector<Constraint>> _constraintProperties; /*!< pointer to constraint properties determined by MAiNGO */
                                                                    /**@}*/

    /**
		* @name Internal variables for storing information on the problem
		*/
    /**@{*/
    unsigned _nvar;                                                /*!< number of variables */
    unsigned _nineq;                                               /*!< number of inequalities */
    unsigned _nineqSquash;                                         /*!< number of squash inequalities */
    unsigned _neq;                                                 /*!< number of equalities */
    std::vector<babBase::OptimizationVariable> _originalVariables; /*!< original variables (i.e., original upper and lower bounds, info on which variables are binary etc., cf. structs.h) */
    std::vector<double> _originalUpperBounds;                      /*!< vector of upper bounds for variables as specified in the problem definition */
    std::vector<double> _originalLowerBounds;                      /*!< vector of upper bounds for variables as specified in the problem definition */
    UbpStructure _structure;                                       /*!< struct storing information on the problem structure */
                                                                   /**@}*/


  private:
    UpperBoundingSolver(); /*!< Standard constructor prohibited */
    // Prevent use of default copy constructor and copy assignment operator by declaring them private:
    UpperBoundingSolver(const UpperBoundingSolver &);            /*!< default copy constructor declared private to prevent use */
    UpperBoundingSolver &operator=(const UpperBoundingSolver &); /*!< default assignment operator declared private to prevent use */
};

/**
* @brief Factory function for initializing different upper bounding solver wrappers
*
* @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
* @param[in] DAGvars are the variables corresponding to the DAG
* @param[in] DAGfunctions are the functions corresponding to the DAG
* @param[in] variables is a vector containing the initial optimization variables defined in problem.h
* @param[in] nineqIn is the number of inequality constraints
* @param[in] neqIn is the number of equality
* @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
* @param[in] settingsIn is a pointer to the MAiNGO settings
* @param[in] loggerIn is a pointer to the MAiNGO logger object
* @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
* @param[in] useIn communicates what the solver is to be used for
*/
std::shared_ptr<UpperBoundingSolver> make_ubp_solver(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
                                                     const std::vector<babBase::OptimizationVariable> &variables, const unsigned nineqIn, const unsigned neqIn,
                                                     const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn,
                                                     UpperBoundingSolver::UBS_USE useIn, bool printSolver = true);


}    // end namespace ubp


}    // end namespace maingo

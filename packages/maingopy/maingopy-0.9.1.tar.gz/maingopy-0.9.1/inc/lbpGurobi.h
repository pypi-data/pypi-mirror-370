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

#include "lbp.h"

#include "gurobi_c++.h"


namespace maingo {


namespace lbp {


/**
* @class LbpGurobi
* @brief Wrapper for handling the lower bounding problems by interfacing Gurobi
*
* This class constructs and solves lower bounding problems using Gurobi.
*
*/
class LbpGurobi : public LowerBoundingSolver {

  public:
    /**
        * @brief Constructor, stores information on the problem and initializes the Gurobi problem and solver instances.
        *
        * @param[in] DAG is the directed acyclic graph constructed in MAiNGO.cpp needed to construct an own DAG for the lower bounding solver
        * @param[in] DAGvars are the variables corresponding to the DAG
        * @param[in] DAGfunctions are the functions corresponding to the DAG
        * @param[in] variables is a vector containing the optimization variables
        * @param[in] variableIsLinear is a vector containing information about which variables occur only linearly
        * @param[in] nineqIn is the number of inequality constraints
        * @param[in] neqIn is the number of equality
        * @param[in] nineqRelaxationOnlyIn is the number of inequality for use only in the relaxed problem
        * @param[in] neqRelaxationOnlyIn is the number of equality constraints for use only in the relaxed problem
        * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
        * @param[in] settingsIn is a pointer to the MAiNGO settings
        * @param[in] loggerIn is a pointer to the MAiNGO logger object
		* @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
        */
    LbpGurobi(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
              const std::vector<babBase::OptimizationVariable> &variables, const std::vector<bool> &variableIsLinear, const unsigned nineqIn, const unsigned neqIn,
              const unsigned nineqRelaxationOnlyIn, const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn,
              std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn);

    /**
        * @brief Destructor
        */
    ~LbpGurobi();

    /**
        * @brief Function called by the B&B solver to heuristically activate more scaling in the LBS
        */
    void activate_more_scaling();

  protected:
    /**
        * @brief Function for setting the bounds of variables
        *
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        */
    void _set_variable_bounds(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds);

    /**
        * @brief Auxiliary function for updating LP objective, i.e., processing the linearization of the objective function
        *
        * @param[in] resultRelaxation is the McCormick object holding relaxation of objective iObj at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iObj is the number of the objective function
        */
    void _update_LP_obj(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                        const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iObj);

    /**
        * @brief Auxiliary function for updating LP inequalities, i.e., processing the linearization of the inequality
        *
        * @param[in] resultRelaxation is the McCormick object holding relaxation of inequality iIneq at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iIneq is the number of the inequality function
        */
    void _update_LP_ineq(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                         const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneq);

    /**
        * @brief Auxiliary function for updating LP equalities, i.e., processing the linearization of the equality
        *
        * @param[in] resultRelaxationCv is the McCormick object holding relaxation of equality iEq at linearizationPoint used for the convex part
        * @param[in] resultRelaxationCc is the McCormick object holding relaxation of equality iEq at linearizationPoint used for the concave part
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iEq is the number of the equality function
        */
    void _update_LP_eq(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                       const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEq);

    /**
        * @brief Auxiliary function for updating LP relaxation only inequalities, i.e., processing the linearization of the relaxation only inequality
        *
        * @param[in] resultRelaxation is the McCormick object holding relaxation of relaxation only inequality iIneqRelaxationOnly at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iIneqRelaxationOnly is the number of the relaxation only inequality function
        */
    void _update_LP_ineqRelaxationOnly(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                       const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqRelaxationOnly);

    /**
        * @brief Auxiliary function for updating LP relaxation only equalities, i.e., processing the linearization of the relaxation only equality
        *
        * @param[in] resultRelaxationCv is the McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the convex part
        * @param[in] resultRelaxationCc is the McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the concave part
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iEqRelaxationOnly is the number of the relaxation only equality function
        */
    void _update_LP_eqRelaxationOnly(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                     const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEqRelaxationOnly);

    /**
        * @brief Auxiliary function for updating LP squash inequalities, i.e., processing the linearization of the squash inequality
        *        No tolerances are allowed for squash inequalities!
        *
        * @param[in] resultRelaxation is the McCormick object holding relaxation of inequality iIneqSquash at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iLin is the number of the linearization point
        * @param[in] iIneqSquash is the number of the inequality function
        */
    void _update_LP_ineq_squash(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqSquash);

    /**
        * @brief Auxiliary function for updating LP objective, i.e., processing the linearization of the objective function for vector McCormick relaxations
        *
        * @param[in] resultRelaxationVMC is the vector McCormick object holding relaxation of objective iObj at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iObj is the number of the objective function
        */
    void _update_LP_obj(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                        const std::vector<double> &upperVarBounds, unsigned const &iObj);

    /**
        * @brief Auxiliary function for updating LP inequalities, i.e., processing the linearization of the inequality for vector McCormick relaxations
        *
        * @param[in] resultRelaxationVMC is the vector McCormick object holding relaxation of inequality iIneq at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iIneq is the number of the inequality function
        */
    void _update_LP_ineq(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                         const std::vector<double> &upperVarBounds, unsigned const &iIneq);

    /**
        * @brief Auxiliary function for updating LP equalities, i.e., processing the linearization of the equality for vector McCormick relaxations
        *
        * @param[in] resultRelaxationCvVMC is the vector McCormick object holding relaxation of equality iEq at linearizationPoint used for the convex part
        * @param[in] resultRelaxationCcVMC is the vector McCormick object holding relaxation of equality iEq at linearizationPoint used for the concave part
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iEq is the number of the equality function
        */
    void _update_LP_eq(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                       const std::vector<double> &upperVarBounds, unsigned const &iEq);

    /**
        * @brief Auxiliary function for updating LP relaxation only inequalities, i.e., processing the linearization of the relaxation only inequality for vector McCormick relaxations
        *
        * @param[in] resultRelaxationVMC is the vector McCormick object holding relaxation of relaxation only inequality iIneqRelaxationOnly at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iIneqRelaxationOnly is the number of the relaxation only inequality function
        */
    void _update_LP_ineqRelaxationOnly(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                       const std::vector<double> &upperVarBounds, unsigned const &iIneqRelaxationOnly);

    /**
        * @brief Auxiliary function for updating LP relaxation only equalities, i.e., processing the linearization of the relaxation only equality for vector McCormick relaxations
        *
        * @param[in] resultRelaxationCvVMC is the vector McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the convex part
        * @param[in] resultRelaxationCcVMC is the vector McCormick object holding relaxation of relaxation only equality iEqRelaxationOnly at linearizationPoint used for the concave part
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iEqRelaxationOnly is the number of the relaxation only equality function
        */
    void _update_LP_eqRelaxationOnly(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                     const std::vector<double> &upperVarBounds, unsigned const &iEqRelaxationOnly);

    /**
        * @brief Auxiliary function for updating LP squash inequalities, i.e., processing the linearization of the squash inequality for vector McCormick relaxations
        *        No tolerances are allowed for squash inequalities!
        *
        * @param[in] resultRelaxationVMC is the vector McCormick object holding relaxation of inequality iIneqSquash at linearizationPoint
        * @param[in] linearizationPoint is the vector holding the linearization point
        * @param[in] lowerVarBounds is the vector holding the lower bounds of the variables
        * @param[in] upperVarBounds is the vector holding the upper bounds of the variables
        * @param[in] iIneqSquash is the number of the inequality function
        */
    void _update_LP_ineq_squash(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                const std::vector<double> &upperVarBounds, unsigned const &iIneqSquash);

    /**
        * @brief Function for solving the currently constructed linear program.
        *
        * @param[in] currentNode is the currentNode, needed for throwing exceptions or obtaining the lower and upper bounds of variables
        */
    LP_RETCODE _solve_LP(const babBase::BabNode &currentNode);

    /**
        * @brief Function returning the current status of the lastly solved linear program.
        *
        * @return Returns the current status of the last solved linear program.
        */
    LP_RETCODE _get_LP_status();

    /**
        * @brief Function for setting the solution to the solution point of the lastly solved LP.
        *
        * @param[in] solution is modified to hold the solution point of the lastly solved LP
        * @param[in] etaVal is modified to hold the value of eta variable of the lastly solved LP
        */
    void _get_solution_point(std::vector<double> &solution, double &etaVal);

    /**
        * @brief Function returning the objective value of the lastly solved LP.
        *
        * @return Returns the objective value of the lastly solved LP.
        */
    double _get_objective_value_solver();

    /**
        * @brief Function for setting the multipliers of the lastly solved LP.
        *
        * @param[in] multipliers is modified to hold the reduced costs of the lastly solved LP
        */
    void _get_multipliers(std::vector<double> &multipliers);

    /**
        * @brief Function deactivating all objective rows in the LP for feasibility OBBT.
        */
    void _deactivate_objective_function_for_OBBT();

    /**
        * @brief Function modifying the LP for feasibility-optimality OBBT.
        *
        * @param[in] currentUBD is the current upper bound
        * @param[in,out] toTreatMax is the list holding variables indices for maximization
        * @param[in,out] toTreatMin is the list holding variables indices for minimization
        */
    void _modify_LP_for_feasopt_OBBT(const double &currentUBD, std::list<unsigned> &toTreatMax, std::list<unsigned> &toTreatMin);

    /**
        * @brief Function for setting the optimization sense of variable iVar in OBBT.
        *
        * @param[in] iVar is the number of variable of which the optimization sense will be changed.
        * @param[in] optimizationSense describes whether the variable shall be maximized or minimized 1: minimize, 0: ignore,  -1: maximize.
        */
    void _set_optimization_sense_of_variable(const unsigned &iVar, const int &optimizationSense);

    /**
        * @brief Function for fixing a variable to one of its bounds.
        *
        * @param[in] iVar is the number of variable which will be fixed.
        * @param[in] fixToLowerBound describes whether the variable shall be fixed to its lower or upper bound.
        */
    void _fix_variable(const unsigned &iVar, const bool fixToLowerBound);

    /**
        * @brief Function for restoring proper coefficients and options in the LP after OBBT.
        */
    void _restore_LP_coefficients_after_OBBT();

    /**
        * @brief Function for checking if the current linear program is really infeasible by, e.g., resolving it with different algorithms.
        *
        * @return Returns true if the linear program is indeed infeasible, false if and optimal solution was found
        */
    bool _check_if_LP_really_infeasible();

    /**
        * @brief Function for checking if a specific option has to be turned off for a given lower bounding solver. - empty for Gurobi
        */
    void _turn_off_specific_options() {};

#ifdef LP__OPTIMALITY_CHECK
    /**
        * @brief Function for checking if the solution point returned by Gurobi is really infeasible using Farkas' Lemma
        *
        * @param[in] currentNode is holding the current node in the branch-and-bound tree
        * @return Returns whether the problem was confirmed to be infeasible or not
        */
    SUBSOLVER_RETCODE _check_infeasibility(const babBase::BabNode &currentNode);

    /**
        * @brief helper function that connects _check_feasibility to  the logger
        */
    void _print_check_feasibility(const std::shared_ptr<Logger> logger, const VERB verbosity, const std::vector<double> &solution, const std::vector<std::vector<double>> rhs, const std::string name, const double value, const unsigned i, unsigned k, const unsigned nvar);

    /**
        * @brief Function for checking if the solution point returned by Gurobi solver is really feasible
        *
        * @param[in] solution is holding the solution point to check
        * @return Returns whether the given solution was confirmed to be feasible or not
        */
    SUBSOLVER_RETCODE _check_feasibility(const std::vector<double> &solution);

    /**
        * @brief Function for checking if the solution point returned by Gurobi solver is really optimal using strong duality
        *
        * @param[in] currentNode is holding the current node in the branch-and-bound tree
        * @param[in] newLBD is the value of the solution point to check
        * @param[in] solution is holding the solution point to check
        * @param[in] etaVal is holding the value of eta at the solution point
        * @param[in] multipliers is holding the dual multipliers of the solution
        * @return Returns whether the given solution was confirmed to be optimal or not
        */
    SUBSOLVER_RETCODE _check_optimality(const babBase::BabNode &currentNode, const double newLBD, const std::vector<double> &solution, const double etaVal, const std::vector<double> &multipliers);

#endif

#ifdef LP__WRITE_CHECK_FILES
    /**
        * @brief Function writing the current linear program to file
        *
        * @param[in] fileName is the name of the written file
        */
    virtual void _write_LP_to_file(const std::string &fileName);
#endif

  private:
    /**
        * @brief Function for taking care of memory management (either called from destructor or when an exception is thrown) - empty for Gurobi
        */
    void _terminate_gurobi() {};

    /**
        * @name Internal Gurobi variables
        */
    /**@{*/
    GRBEnv grbEnv;
    GRBModel grbModel;
    GRBLinExpr grbObj;
    std::vector<GRBVar> grbVars;
    GRBVar eta;
    std::vector<std::vector<GRBConstr>> linObj;
    std::vector<std::vector<GRBConstr>> linIneq;
    std::vector<std::vector<GRBConstr>> linEq1;
    std::vector<std::vector<GRBConstr>> linEq2;
    std::vector<std::vector<GRBConstr>> linIneqRelaxationOnly;
    std::vector<std::vector<GRBConstr>> linEqRelaxationOnly1;
    std::vector<std::vector<GRBConstr>> linEqRelaxationOnly2;
    std::vector<std::vector<GRBConstr>> linIneqSquash;
    double etaCoeff;
#ifdef LP__OPTIMALITY_CHECK
    std::vector<double> farkasVals;
    GRBConstr* farkasCons;
    std::vector<std::vector<double>> dualValsObj;                /*!< auxiliary variable for optimality check */
    std::vector<std::vector<double>> dualValsIneq;               /*!< auxiliary variable for optimality check */
    std::vector<std::vector<double>> dualValsEq1;                /*!< auxiliary variable for optimality check */
    std::vector<std::vector<double>> dualValsEq2;                /*!< auxiliary variable for optimality check */
    std::vector<std::vector<double>> dualValsIneqRelaxationOnly; /*!< auxiliary variable for optimality check */
    std::vector<std::vector<double>> dualValsEqRelaxationOnly1;  /*!< auxiliary variable for optimality check */
    std::vector<std::vector<double>> dualValsEqRelaxationOnly2;  /*!< auxiliary variable for optimality check */
    std::vector<std::vector<double>> dualValsIneqSquash;         /*!< auxiliary variable for optimality check */
#endif
    /**@}*/
};


}    // end of namespace lbp


}    // end of namespace maingo
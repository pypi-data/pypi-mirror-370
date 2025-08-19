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

#include "ubpStructure.h"

// Needed according to Ipopt Dll readme:
#define HAVE_CONFIG_H
#include "IpTNLP.hpp"

#include <memory>
#include <vector>


namespace maingo {


namespace ubp {


struct DagObj;

/**
* @class IpoptProblem
* @brief Class for representing problems to be solved by IpOpt, providing an interface to the problem definition in problem.h used by MC++
*
* This class is a specialization of the problem definition class within the Ipopt C++ API.
* It provides an interface between Ipopt and the problem definition in problem.h. by evaluating the Model equations and preparing the information required by Ipopt.
* An instance of this class is handed to Ipopt as an argument of its optimizeTNLP routine in ubp.cpp.
* For more information on the basic interface see  https://www.coin-or.org/Ipopt/documentation/node23.html.
*
*/
class IpoptProblem: public Ipopt::TNLP {

  public:
    /**
        * @brief Standard constructor
        */
    IpoptProblem();

    /**
        * @brief Constructor actually used in ubp.cpp. Initializes the corresponding members.
        *
        * @param[in] nvarIn is the number of optimization variables
        * @param[in] neqIn is the number of equality constraints
        * @param[in] nineqIn is the number of inequality constraints
        * @param[in] nineqSquashIn is the number of squash inequality constraints which are to be used only if the squash node has been used
        * @param[in] structureIn is a struct containing information on sparsity patterns of the Lagrangian and Hessian
        * @param[in] constraintPropertiesIn is a pointer to the constraint properties determined by MAiNGO
        * @param[in] dagObj is a pointer to the struct holding the DAG to be evaluated
        */
    IpoptProblem(unsigned nvarIn, unsigned neqIn, unsigned nineqIn, unsigned nineqSquashIn, UbpStructure* structureIn,
                 std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, std::shared_ptr<DagObj> dagObj);

    /** @brief Destructor */
    virtual ~IpoptProblem();

    /**
        * @brief Function called by Ipopt to get basic information on the problem
        *
        * @param[out] n is the number of optimization variables
        * @param[out] m is the total number of constraints (both equality and inequality)
        * @param[out] nnz_jac_g is the number of non-zero elements of the Jacobian of the constraints (assumed to be dense)
        * @param[out] nnz_h_lag is the number of non-zero elements of the Hessian of the Lagrangian (not used since BigMC currently only relies on BFGS)
        * @param[out] Index_style Information on indexing of arrays (using C-style indexing, i.e., starting with 0)
        */
    virtual bool get_nlp_info(Ipopt::Index& n, Ipopt::Index& m, Ipopt::Index& nnz_jac_g,
                              Ipopt::Index& nnz_h_lag, IndexStyleEnum& Index_style);

    /**
        * @brief Function called by Ipopt to get information on variables bounds
        * @param[in] n is the number of optimization variables
        * @param[in] m is the total number of constraints (both equality and inequality)
        * @param[out] x_l is a pointer to an array containing the lower bounds on the optimization variables
        * @param[out] x_u is a pointer to an array containing the upper bounds on the optimization variables
        * @param[out] g_l is a pointer to an array containing the lower bounds on the constraints (zero for equalities, and -2e19 for inequalities)
        * @param[out] g_u is a pointer to an array containing the upper bounds on the constraints (all zero)
        */
    virtual bool get_bounds_info(Ipopt::Index n, Ipopt::Number* x_l, Ipopt::Number* x_u,
                                 Ipopt::Index m, Ipopt::Number* g_l, Ipopt::Number* g_u);

    /**
        * @brief Function called by Ipopt to query the starting point for local search
        *
        * @param[in] n is the number of optimization variables
        * @param[in] m is the total number of constraints (both equality and inequality)
        * @param[in] init_x indicates that a starting point for x is required
        * @param[out] x is a pointer to an array containing the initial point
        * @param[in] init_z not used in MAiNGO implementation
        * @param[in] z_L not used in MAiNGO implementation
        * @param[in] z_U not used in MAiNGO implementation
        * @param[in] init_lambda not used in MAiNGO implementation
        * @param[in] lambda not used in MAiNGO implementation
        */
    virtual bool get_starting_point(Ipopt::Index n, bool init_x, Ipopt::Number* x,
                                    bool init_z, Ipopt::Number* z_L, Ipopt::Number* z_U,
                                    Ipopt::Index m, bool init_lambda,
                                    Ipopt::Number* lambda);
    /**
        * @brief Function called by Ipopt to evaluate the objective function
        *
        * @param[in] n is the number of optimization variables
        * @param[in] x is a pointer to an array containing the point at which the objective is to be evaluated
        * @param[in] new_x indicates whether the current x is different from the previous one handed to one of the evaluation functions
        * @param[out] obj_value is the value of the objective function at the current point
        */
    virtual bool eval_f(Ipopt::Index n, const Ipopt::Number* x, bool new_x, Ipopt::Number& obj_value);

    /**
        * @brief Function called by Ipopt to evaluate the gradient of the objective function
        *
        * @param[in] n is the number of optimization variables
        * @param[in] x is a pointer to an array containing the point at which the objective is to be evaluated
        * @param[in] new_x indicates whether the current x is different from the previous one handed to one of the evaluation functions
        * @param[out] grad_f is a pointer to an array containing the gradient of the objective function at the current point
        */
    virtual bool eval_grad_f(Ipopt::Index n, const Ipopt::Number* x, bool new_x, Ipopt::Number* grad_f);

    /**
        * @brief Function called by Ipopt to evaluate the constraints
        *
        * @param[in] n is the number of optimization variables
        * @param[in] x is a pointer to an array containing the point at which the objective is to be evaluated
        * @param[in] new_x indicates whether the current x is different from the previous one handed to one of the evaluation functions
        * @param[in] m is the total number of constraints (both equality and inequality)
        * @param[out] g is a pointer to an array containing the values of the constraints at the current point
        */
    virtual bool eval_g(Ipopt::Index n, const Ipopt::Number* x, bool new_x, Ipopt::Index m, Ipopt::Number* g);

    /**
        * @brief Function called by Ipopt to evaluate the constraints
        *
        * @param[in] n is the number of optimization variables
        * @param[in] x is a pointer to an array containing the point at which the objective is to be evaluated
        * @param[in] new_x indicates whether the current x is different from the previous one handed to one of the evaluation functions
        * @param[in] m is the total number of constraints (both equality and inequality)
        * @param[in] nele_jac is not documented in MAiNGO
        * @param[out] iRow is a pointer to an array containing the row indices according to the sparsity pattern (see  https://www.coin-or.org/Ipopt/documentation/node23.html).
        * @param[out] jCol is a pointer to an array containing the row indices according to the sparsity pattern (see  https://www.coin-or.org/Ipopt/documentation/node23.html).
        * @param[in,out] values is a pointer to an array containing the jacobian of the constraints at the current point. If the function is called with values==NULL, only information on the structure of the Jacobian is required.
        */
    virtual bool eval_jac_g(Ipopt::Index n, const Ipopt::Number* x, bool new_x,
                            Ipopt::Index m, Ipopt::Index nele_jac, Ipopt::Index* iRow, Ipopt::Index* jCol,
                            Ipopt::Number* values);

    /**
        * @brief Function called by Ipopt to evaluate the Hessian - not implemented, just throws an exception!
        *
        * @param[in] n not implemented
        * @param[in] x not implemented
        * @param[in] new_x not implemented
        * @param[in] obj_factor not implemented
        * @param[in] m not implemented
        * @param[in] lambda not implemented
        * @param[in] new_lambda not implemented
        * @param[in] nele_hess not implemented
        * @param[in] iRow not implemented
        * @param[in] jCol not implemented
        * @param[in] values not implemented
        */
    virtual bool eval_h(Ipopt::Index n, const Ipopt::Number* x, bool new_x,
                        Ipopt::Number obj_factor, Ipopt::Index m, const Ipopt::Number* lambda,
                        bool new_lambda, Ipopt::Index nele_hess, Ipopt::Index* iRow,
                        Ipopt::Index* jCol, Ipopt::Number* values);

    /**
        * @brief Function called by Ipopt to communicate the result of the local search
        *
        * @param[in] status Return code of Ipopt (not used since feasibility is checked in ubp.cpp and local optimality is not as important in this case).
        * @param[in] n is the number of optimization variables
        * @param[in] x is a pointer to an array containing the solution point of the local search
        * @param[in] obj_value is the objective function value at the solution point
        * @param[in] z_L not used
        * @param[in] z_U not used
        * @param[in] m not used
        * @param[in] g not used
        * @param[in] lambda not used
        * @param[in] ip_data not used
        * @param[in] ip_cq not used
        */
    virtual void finalize_solution(Ipopt::SolverReturn status,
                                   Ipopt::Index n, const Ipopt::Number* x, const Ipopt::Number* z_L, const Ipopt::Number* z_U,
                                   Ipopt::Index m, const Ipopt::Number* g, const Ipopt::Number* lambda,
                                   Ipopt::Number obj_value,
                                   const Ipopt::IpoptData* ip_data,
                                   Ipopt::IpoptCalculatedQuantities* ip_cq);

    /**
        * @brief Function called from the upper bounding wrapper to query the solution
        *
        * @param[out] sol_x is a vector containing the solution point
        * @return Objective value at solution point
        */
    double get_solution(std::vector<double>& sol_x);

    /**
        * @brief Function called from the upper bounding wrapper to specify the variable bounds and starting point
        *
        * @param[in] xL is a vector containing the lower bounds on the optimization variables
        * @param[in] xU is a vector containing the upper bounds on the optimization variables
        * @param[in] xStart is a vector containing the starting point to be used in local search
        */
    void set_bounds_and_starting_point(const std::vector<double>& xL, const std::vector<double>& xU, const std::vector<double>& xStart);

  private:
    std::shared_ptr<DagObj> _DAGobj; /*!< pointer to object containing DAG for upper bounding */

    /**
        * @name Internal IPOPT variables
        */
    /**@{*/
    Ipopt::Index _nvar;                                             /*!< number of variables */
    Ipopt::Index _nineq;                                            /*!< number of inequalities */
    Ipopt::Index _nineqSquash;                                      /*!< number of squash inequalities */
    Ipopt::Index _neq;                                              /*!< number of equalities */
    UbpStructure* _structure;                                       /*!< pointer to struct storing information on the problem structure */
    std::shared_ptr<std::vector<Constraint>> _constraintProperties; /*!< pointer to constraint properties determined by MAiNGO */
    double _solution_f;                                             /*!< solution value */
    std::vector<double> _xL;                                        /*!< vector holding lower bounds */
    std::vector<double> _xU;                                        /*!< vector holding upper bounds */
    std::vector<double> _xStart;                                    /*!< vector holding the initial point */
    std::vector<double> _solutionX;                                 /*!< vector holding the solution point */
    /**@}*/

    // Copy constructors made private
    IpoptProblem(const IpoptProblem&);            /*!< default copy constructor declared private to prevent use */
    IpoptProblem& operator=(const IpoptProblem&); /*!< default assignment operator declared private to prevent use */
};


}    // end namespace ubp


}    // end namespace maingo
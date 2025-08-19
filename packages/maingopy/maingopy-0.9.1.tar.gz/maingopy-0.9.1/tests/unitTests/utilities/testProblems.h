/**********************************************************************************
 * Copyright (c) 2021-2024 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "MAiNGOmodel.h"
#include "MAiNGOmodelEpsCon.h"


using Var = mc::FFVar;


class BasicModel1: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = optVars[0]*optVars[1];

        result.ineq.push_back(exp(optVars[0])-1.);
        result.ineqRelaxationOnly.push_back(optVars[0]);
        result.eq.push_back(optVars[0]);
        result.eqRelaxationOnly.push_back(optVars[0]);
        result.ineqSquash.push_back(optVars[0]);

        result.ineq.push_back(-0.5);
        result.ineqRelaxationOnly.push_back(-0.5);
        result.eq.push_back(0.0);
        result.eqRelaxationOnly.push_back(0.0);
        result.ineqSquash.push_back(-0.5);

        result.output.push_back(maingo::OutputVariable(optVars[0] + 41.5, "the answer"));
        result.output.push_back(maingo::OutputVariable(mc::FFVar(42.0), "still the answer"));
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER, "y"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "z1"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER, "z2"));
        return variables;
    }

  private:
};

class BasicModel2: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = pow(optVars[0],3);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "y"));
        return variables;
    }

  private:
};


class BasicBiobjectiveModel: public maingo::MAiNGOmodelEpsCon {
  public:
    BasicBiobjectiveModel(){}

    maingo::EvaluationContainer evaluate_user_model(const std::vector<Var> &optVars) {
        Var x = optVars.at(0);
        Var y = optVars.at(1);
        Var A1 = 0.5 * sin(1) - 2 * cos(1) + sin(2) - 1.5 * cos(2);
        Var A2 = 1.5 * sin(1) - cos(1) + 2 * sin(2) - 0.5 * cos(2);
        Var B1 = 0.5 * sin(x) - 2 * cos(x) + sin(y) - 1.5 * cos(y);
        Var B2 = 1.5 * sin(x) - cos(x) + 2 * sin(y) - 0.5 * cos(y);
        maingo::EvaluationContainer result;
        result.objective.push_back(1 + sqr(A1 - B1) + pow(A2 - B2, 2));
        result.objective.push_back(sqr(x + 3) + sqr(y + 1));
        return result;
    }

    std::vector<double> get_initial_point() {
        return {0., 0.};
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable( maingo::Bounds(-3.14, 3.14)));
        variables.push_back(maingo::OptimizationVariable( maingo::Bounds(-3.14, 3.14)));    
        return variables;
    }
};


class MultiobjectiveModelOneObjective: public maingo::MAiNGOmodelEpsCon {
  public:
    maingo::EvaluationContainer evaluate_user_model(const std::vector<Var> &optVars) {
        Var x = optVars.at(0);
        maingo::EvaluationContainer result;
        result.objective.push_back(x);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable( maingo::Bounds(-3.14, 3.14))); 
        return variables;
    }
};


class BasicLP: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = optVars[0];
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "y"));
        return variables;
    }
};


class InfeasibleLP: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = optVars[0];
        result.ineq.push_back(2 - optVars[0]);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        return variables;
    }
};


class BasicQP: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = sqr(optVars[0]);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        return variables;
    }
};


class BasicMIP: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = optVars[0];
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER, "y"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "z"));
        return variables;
    }
};


class BasicMIQP: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = sqr(optVars[0]);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER, "x"));
        return variables;
    }
};


class BasicNLP: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = pow(optVars[0],3);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        return variables;
    }
};


class BasicMINLP: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = pow(optVars[0],3);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER, "x"));
        return variables;
    }
};


class BasicDNLP: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = fabs(pow(optVars[0],3));
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        return variables;
    }
};


class BasicNLPcustomInitialPoint: public maingo::MAiNGOmodel {
  public:
    BasicNLPcustomInitialPoint(const std::vector<double> initialPoint): _initialPoint(initialPoint) {}

    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = pow(optVars[3],3);
        result.ineq.push_back(optVars[0] - 0.5, "ineq 1");
        result.ineq.push_back(optVars[2] - 1.5);
        result.ineq.push_back(-0.5);
        result.ineqRelaxationOnly.push_back(-0.5);
        result.ineqSquash.push_back(-0.5);
        result.eq.push_back(optVars[0] - 0.5, "eq 1");
        result.eq.push_back(optVars[1] - 1);
        result.eq.push_back(1e-10);
        result.eqRelaxationOnly.push_back(1e-10);
        result.output.push_back(maingo::OutputVariable(optVars[0] - 1.5, "out1"));
        result.output.push_back(maingo::OutputVariable(optVars[0] - 3.5, "out2"));
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "c1"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "b1"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER, "i1"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY));
        return variables;
    }

    std::vector<double> get_initial_point() {
        return _initialPoint;
    }
  private:
    std::vector<double> _initialPoint = {};
};


class ProblemInfeasibleBounds: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = pow(optVars[0],3);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(2, 1), maingo::VT_CONTINUOUS, "c1"));
        return variables;
    }
};


class ProblemConstantConstraintsInfeasible: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.objective = pow(optVars[0],3);
        result.ineq.push_back(0.5);
        result.ineqRelaxationOnly.push_back(1.5);
        result.ineqSquash.push_back(2.5);
        result.eq.push_back(0.5);
        result.eqRelaxationOnly.push_back(1.5);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1, 2), maingo::VT_CONTINUOUS, "c1"));
        return variables;
    }
};


class FeasibilityProblem: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        result.ineq.push_back(pow(optVars[0],3) - 1.5);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(1, 2), maingo::VT_CONTINUOUS, "c1"));
        return variables;
    }
};
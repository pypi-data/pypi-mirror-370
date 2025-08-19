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

#include "MAiNGO.h"
#include "MAiNGOException.h"

#include "utilities/testProblems.h"

#include <gtest/gtest.h>

#include <filesystem>



using maingo::MAiNGO;


class MAiNGOTestProblemRegular: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        maingo::EvaluationContainer result;
        Var x = optVars[0];
        Var y = optVars[1];
        result.objective = pow(x,3)*pow(y-0.5,5)*log(sqrt(exp(x)*(x-pow(x,3)))+1.5)*pow(x*y,5);
        result.ineq.push_back(pow(x,3) - y + 0.5);
        result.ineqRelaxationOnly.push_back(pow(x,3) - y + 0.4);
        result.output.push_back(maingo::OutputVariable(x*y - (x-x), "x*y"));
        result.output.push_back(maingo::OutputVariable(42, "the answer"));
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "y"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-2, 2), maingo::VT_BINARY, "z"));
        return variables;
    }

    std::vector<double> get_initial_point() override {
        return {0.5, 0.5, 0};
    }
};


class ProblemWithoutVariables: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        return maingo::EvaluationContainer();
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return std::vector<maingo::OptimizationVariable>();
    }
};


class ProblemThrowingException: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        throw std::runtime_error("Something went wrong during evaluation!");
        return maingo::EvaluationContainer();
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
};


class ProblemThrowingInteger: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        throw -1;
        return maingo::EvaluationContainer();
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
};


class ProblemConflictingBounds: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        return maingo::EvaluationContainer();
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(1, 0)) };
    }
};


class ProblemConstantConstraintInfeasible: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        maingo::EvaluationContainer result;
        result.ineq.push_back(0.5);
        result.ineq.push_back(-0.5);
        result.ineqRelaxationOnly.push_back(0.5);
        result.ineqRelaxationOnly.push_back(-0.5);
        result.ineqSquash.push_back(0.5);
        result.ineqSquash.push_back(-0.5);
        result.ineqSquash.push_back(optVars[0]);
        result.eq.push_back(0.5);
        result.eq.push_back(0.0);
        result.eqRelaxationOnly.push_back(0.5);
        result.eqRelaxationOnly.push_back(0.0);
        result.eq.push_back(optVars[0]);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
};


class ProblemNonconstantConstraintInfeasible: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        maingo::EvaluationContainer result;
        result.objective = pow(optVars[0], 3);
        result.ineq.push_back(2. - optVars[0]);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
};


class ProblemConstantObjective: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        maingo::EvaluationContainer result;
        result.objective = 42;
        result.ineq.push_back(0.5 - optVars[0]);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
};


class ProblemWithHiddenZero: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        maingo::EvaluationContainer result;
        Var x = optVars[0];
        result.objective = pow(x,3) + pow(x,3) -2*pow(x,3);
        result.eq.push_back(pow(x,3) + pow(x,3) -2*pow(x,3));
        result.eqRelaxationOnly.push_back(pow(x,3) + pow(x,3) -2*pow(x,3));
        result.ineq.push_back(pow(x,3) + pow(x,3) -2*pow(x,3));
        result.ineqRelaxationOnly.push_back(pow(x,3) + pow(x,3) -2*pow(x,3));
        result.ineqSquash.push_back(pow(x,3) + pow(x,3) -2*pow(x,3));
        result.eq.push_back(x);
        result.eqRelaxationOnly.push_back(x);
        result.ineq.push_back(x);
        result.ineqRelaxationOnly.push_back(x);
        result.ineqSquash.push_back(x);
        result.output.push_back(maingo::OutputVariable(pow(x,3) + pow(x,3) -2*pow(x,3), "hidden zero"));
        result.output.push_back(maingo::OutputVariable(pow(x,4) + pow(x,4) -2*pow(x,4), "another hidden zero"));
        result.output.push_back(maingo::OutputVariable(x, "no hidden zero"));
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
};


class ProblemAdjustableNumberOfRelaxationOnlyConstraintsInfeasible: public maingo::MAiNGOmodel {
  public:
    ProblemAdjustableNumberOfRelaxationOnlyConstraintsInfeasible(const size_t nineq, const size_t neq): _nineq(nineq), _neq(neq) {}

    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) override {
        maingo::EvaluationContainer result;
        result.objective = pow(optVars[0], 3);
        for (size_t iIneq = 0; iIneq < _nineq; iIneq++) {
            result.ineqRelaxationOnly.push_back(0.5 - optVars[0]);
        }
        for (size_t iEq = 0; iEq < _neq; iEq++) {
            result.eqRelaxationOnly.push_back(0.5 - optVars[0]);
        }
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
  private:
    size_t _nineq = 0;
    size_t _neq = 0;
};


class ProblemWithAdjustableNumberOfObjectives: public maingo::MAiNGOmodelEpsCon {
  public:
    ProblemWithAdjustableNumberOfObjectives(const size_t nobj) { _nobj = nobj;}

    maingo::EvaluationContainer evaluate_user_model(const std::vector<Var> &optVars) {
        Var x = optVars.at(0);
        maingo::EvaluationContainer result;
        for (size_t i = 0; i<_nobj; ++i) {
            result.objective.push_back(x);
        }
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable( maingo::Bounds(0, 1)));  
        return variables;
    }
  private:
    size_t _nobj = 0;
};


class BiObjectiveProblemThrowingException: public maingo::MAiNGOmodelEpsCon {
  public:
    maingo::EvaluationContainer evaluate_user_model(const std::vector<Var> &optVars) override {
        throw std::runtime_error("Something went wrong during evaluation!");
        return maingo::EvaluationContainer();
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
};


class InfeasibleBiObjectiveProblem: public maingo::MAiNGOmodelEpsCon {
  public:
    maingo::EvaluationContainer evaluate_user_model(const std::vector<Var> &optVars) override {
        Var x = optVars.at(0);
        maingo::EvaluationContainer result;
        result.objective.push_back(x);
        result.objective.push_back(x);
        result.ineq.push_back(2. - x);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() override {
        return { maingo::OptimizationVariable(maingo::Bounds(0, 1)) };
    }
};


///////////////////////////////////////////////////
TEST(TestMAiNGO, NoModelSet) {
    MAiNGO maingo;
    EXPECT_THROW(maingo.solve(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, ModelWithoutVariables) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemWithoutVariables>();
    EXPECT_THROW(MAiNGO maingo(model), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, ModelThrowsException) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemThrowingException>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.solve(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, ModelThrowsInteger) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemThrowingInteger>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.solve(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, InitialPointWrongSize) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>(10, 0.5));
    MAiNGO maingo;
    EXPECT_THROW(maingo.set_model(model), maingo::MAiNGOException);

    model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>(8, 0.5));
    EXPECT_THROW(maingo.set_model(model), maingo::MAiNGOException);

    model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>(9, 0.5));
    EXPECT_NO_THROW(maingo.set_model(model));

    model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>(0));
    EXPECT_NO_THROW(maingo.set_model(model));
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, RegularSolve) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<MAiNGOTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("LBP_addAuxiliaryVars", 1);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, RegularSolveInfeasible) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemNonconstantConstraintInfeasible>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::INFEASIBLE);

    maingo.set_option("BAB_constraintPropagation", 0);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::INFEASIBLE);

    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("BAB_constraintPropagation", 0);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::INFEASIBLE);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, TargetLowerBound) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<MAiNGOTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("UBP_solverBab", 0);
    maingo.set_option("targetLowerBound", -10);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::BOUND_TARGETS);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, NoFeasiblePointFound) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<MAiNGOTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("UBP_solverBab", 0);
    maingo.set_option("BAB_maxIterations", 0);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::NO_FEASIBLE_POINT_FOUND);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, TargetUpperBound) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<MAiNGOTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("targetUpperBound", 10);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::BOUND_TARGETS);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, ConflictingBounds) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemConflictingBounds>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::INFEASIBLE);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, ConstantConstraintsInfeasible) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemConstantConstraintInfeasible>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::INFEASIBLE);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, ConflictingRelaxationOnlyConstraints) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemAdjustableNumberOfRelaxationOnlyConstraintsInfeasible>(2, 2);
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_constraintPropagation", 0);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("BAB_alwaysDoObbt", 0);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    model = std::make_shared<ProblemAdjustableNumberOfRelaxationOnlyConstraintsInfeasible>(1, 1);
    maingo.set_model(model);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, ConstantObjective) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemConstantObjective>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, HiddenZero) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemWithHiddenZero>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, RegularSolveWithMultiobjectiveProblem) {
    std::shared_ptr<maingo::MAiNGOmodelEpsCon> model = std::make_shared<BasicBiobjectiveModel>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.solve(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, PureMultistart) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<MAiNGOTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("PRE_pureMultistart", 1);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::FEASIBLE_POINT);

    maingo.set_option("PRE_maxLocalSearches", 0);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::NO_FEASIBLE_POINT_FOUND);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    maingo.set_option("LBP_solver", 0);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 1);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 2);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 3);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveMIP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicMIP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    maingo.set_option("LBP_solver", 0);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 1);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 2);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 3);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveMIQP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicMIQP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    maingo.set_option("LBP_solver", 0);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 1);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 2);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    maingo.set_option("LBP_solver", 3);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveDNLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicDNLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveMINLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicMINLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, RegularSolveWithMultiobjectiveProblemConvertedToSingleObjective) {
    std::shared_ptr<maingo::MAiNGOmodelEpsCon> model = std::make_shared<BasicBiobjectiveModel>();
    model->set_epsilon(std::vector<double>{1., 0.});
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("epsilonA", 1e-9);
    maingo.set_option("epsilonR", 1e-9);
    EXPECT_NO_THROW(maingo.solve());
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
    EXPECT_DOUBLE_EQ(maingo.get_objective_value(), 1.);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveAndWriteModelToAleFile) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<MAiNGOTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("modelWritingLanguage", maingo::LANG_ALE);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_written_model.txt", errorCode);
    maingo.solve();
    EXPECT_EQ(std::filesystem::exists("MAiNGO_written_model.txt"), true);
    std::filesystem::remove("MAiNGO_written_model.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveAndWriteModelToGamsFile) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<MAiNGOTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("modelWritingLanguage", maingo::LANG_GAMS);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_written_model.gms", errorCode);
    maingo.solve();
    EXPECT_EQ(std::filesystem::exists("MAiNGO_written_model.gms"), true);
    std::filesystem::remove("MAiNGO_written_model.gms", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, NoModelSetEpsilonConstraint) {
    MAiNGO maingo;
    EXPECT_THROW(maingo.solve_epsilon_constraint(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveEpsilonConstraintWithSingleObjectiveProblem) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<MAiNGOTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.solve_epsilon_constraint(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveEpsilonConstraintWithWrongObjectiveNumber) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemWithAdjustableNumberOfObjectives>(0);
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.solve_epsilon_constraint(), maingo::MAiNGOException);

    model = std::make_shared<ProblemWithAdjustableNumberOfObjectives>(1);
    maingo.set_model(model);
    EXPECT_THROW(maingo.solve_epsilon_constraint(), maingo::MAiNGOException);

    model = std::make_shared<ProblemWithAdjustableNumberOfObjectives>(3);
    maingo.set_model(model);
    EXPECT_THROW(maingo.solve_epsilon_constraint(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, BiObjectiveProblemThrowsException) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BiObjectiveProblemThrowingException>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.solve_epsilon_constraint(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveEpsilonConstraint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicBiobjectiveModel>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("EC_nPoints", 3);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_epsilon_constraint_objective_values.csv", errorCode);
    std::filesystem::remove("MAiNGO_epsilon_constraint_solution_points.csv", errorCode);
    maingo.solve_epsilon_constraint();
    EXPECT_EQ(true, std::filesystem::exists("MAiNGO_epsilon_constraint_objective_values.csv"));
    EXPECT_EQ(true, std::filesystem::exists("MAiNGO_epsilon_constraint_solution_points.csv"));
    std::filesystem::remove("MAiNGO_epsilon_constraint_objective_values.csv", errorCode);
    std::filesystem::remove("MAiNGO_epsilon_constraint_solution_points.csv", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveEpsilonConstraintInfeasible) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<InfeasibleBiObjectiveProblem>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("EC_nPoints", 2);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_epsilon_constraint_objective_values.csv", errorCode);
    std::filesystem::remove("MAiNGO_epsilon_constraint_solution_points.csv", errorCode);
    maingo.solve_epsilon_constraint();
    EXPECT_EQ(maingo.get_status(), maingo::INFEASIBLE);
    EXPECT_EQ(true, std::filesystem::exists("MAiNGO_epsilon_constraint_objective_values.csv"));
    EXPECT_EQ(true, std::filesystem::exists("MAiNGO_epsilon_constraint_solution_points.csv"));
    std::filesystem::remove("MAiNGO_epsilon_constraint_objective_values.csv", errorCode);
    std::filesystem::remove("MAiNGO_epsilon_constraint_solution_points.csv", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGO, SolveEpsilonConstraintAndAskingToWriteModelToFile) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicBiobjectiveModel>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("modelWritingLanguage", maingo::LANG_GAMS);
    maingo.set_option("EC_nPoints", 2);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_epsilon_constraint_objective_values.csv", errorCode);
    std::filesystem::remove("MAiNGO_epsilon_constraint_solution_points.csv", errorCode);
    std::filesystem::remove("MAiNGO_written_model.gms", errorCode);

    maingo.solve_epsilon_constraint();
    EXPECT_EQ(true, std::filesystem::exists("MAiNGO_epsilon_constraint_objective_values.csv"));
    EXPECT_EQ(true, std::filesystem::exists("MAiNGO_epsilon_constraint_solution_points.csv"));
    std::filesystem::remove("MAiNGO_epsilon_constraint_objective_values.csv", errorCode);
    std::filesystem::remove("MAiNGO_epsilon_constraint_solution_points.csv", errorCode);

    EXPECT_EQ(false, std::filesystem::exists("MAiNGO_written_model.gms"));
    std::filesystem::remove("MAiNGO_written_model.gms", errorCode);
}
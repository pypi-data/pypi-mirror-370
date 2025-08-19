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

#include <gtest/gtest.h>
#include <fstream>


using maingo::MAiNGO;


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, epsilonA)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("epsilonA", 1e-4), true);
    EXPECT_EQ(maingo.get_option("epsilonA"), 1e-4);

    EXPECT_EQ(maingo.set_option("epsilonA", 1e-10), true);
    EXPECT_EQ(maingo.get_option("epsilonA"), 1e-9);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, epsilonR)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("epsilonR", 1e-4), true);
    EXPECT_EQ(maingo.get_option("epsilonR"), 1e-4);

    EXPECT_EQ(maingo.set_option("epsilonR", 1e-10), true);
    EXPECT_EQ(maingo.get_option("epsilonR"), 1e-9);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, deltaIneq)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("deltaIneq", 1e-4), true);
    EXPECT_EQ(maingo.get_option("deltaIneq"), 1e-4);

    EXPECT_EQ(maingo.set_option("deltaIneq", 1e-10), true);
    EXPECT_EQ(maingo.get_option("deltaIneq"), 1e-9);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, deltaEq)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("deltaEq", 1e-4), true);
    EXPECT_EQ(maingo.get_option("deltaEq"), 1e-4);

    EXPECT_EQ(maingo.set_option("deltaEq", 1e-10), true);
    EXPECT_EQ(maingo.get_option("deltaEq"), 1e-9);

}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, relNodeTol)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("relNodeTol", 1e-4), true);
    EXPECT_EQ(maingo.get_option("relNodeTol"), 1e-7);

    EXPECT_EQ(maingo.set_option("relNodeTol", 1e-8), true);
    EXPECT_EQ(maingo.get_option("relNodeTol"), 1e-8);

    EXPECT_EQ(maingo.set_option("relNodeTol", 1e-13), true);
    EXPECT_EQ(maingo.get_option("relNodeTol"), 1e-12);

    
    EXPECT_EQ(maingo.set_option("relNodeTol", 1e-4), true);
    EXPECT_EQ(maingo.set_option("deltaIneq", 1e-5), true);
    EXPECT_EQ(maingo.set_option("deltaEq", 1e-6), true);
    EXPECT_EQ(maingo.get_option("relNodeTol"), 1e-7);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_maxNodes)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_maxNodes", 1e3), true);
    EXPECT_EQ(maingo.get_option("BAB_maxNodes"), 1e3);

    EXPECT_EQ(maingo.set_option("BAB_maxNodes", -1), true);
    EXPECT_EQ(maingo.get_option("BAB_maxNodes"), std::numeric_limits<unsigned>::max());

    EXPECT_EQ(maingo.set_option("BAB_maxNodes", -42), true);
    EXPECT_EQ(maingo.get_option("BAB_maxNodes"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_maxIterations)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_maxIterations", 1e3), true);
    EXPECT_EQ(maingo.get_option("BAB_maxIterations"), 1e3);

    EXPECT_EQ(maingo.set_option("BAB_maxIterations", -1), true);
    EXPECT_EQ(maingo.get_option("BAB_maxIterations"), std::numeric_limits<unsigned>::max());

    EXPECT_EQ(maingo.set_option("BAB_maxIterations", -42), true);
    EXPECT_EQ(maingo.get_option("BAB_maxIterations"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, maxTime)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("maxTime", 1e3), true);
    EXPECT_EQ(maingo.get_option("maxTime"), 1e3);

    EXPECT_EQ(maingo.set_option("maxTime", -1), true);
    EXPECT_EQ(maingo.get_option("maxTime"), std::numeric_limits<unsigned>::max());

    EXPECT_EQ(maingo.set_option("maxTime", -10), true);
    EXPECT_EQ(maingo.get_option("maxTime"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, confirmTermination)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("confirmTermination", 0), true);
    EXPECT_EQ(maingo.get_option("confirmTermination"), 0);

    EXPECT_EQ(maingo.set_option("confirmTermination", 1), true);
    EXPECT_EQ(maingo.get_option("confirmTermination"), 1);

    EXPECT_EQ(maingo.set_option("confirmTermination", 2), true);
    EXPECT_EQ(maingo.get_option("confirmTermination"), 0);

    EXPECT_EQ(maingo.set_option("confirmTermination", 0.99), true);
    EXPECT_EQ(maingo.get_option("confirmTermination"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, terminateOnFeasiblePoint)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("terminateOnFeasiblePoint", 0), true);
    EXPECT_EQ(maingo.get_option("terminateOnFeasiblePoint"), 0);

    EXPECT_EQ(maingo.set_option("terminateOnFeasiblePoint", 1), true);
    EXPECT_EQ(maingo.get_option("terminateOnFeasiblePoint"), 1);

    EXPECT_EQ(maingo.set_option("terminateOnFeasiblePoint", 2), true);
    EXPECT_EQ(maingo.get_option("terminateOnFeasiblePoint"), 0);

    EXPECT_EQ(maingo.set_option("terminateOnFeasiblePoint", 0.99), true);
    EXPECT_EQ(maingo.get_option("terminateOnFeasiblePoint"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, targetLowerBound)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("targetLowerBound", 42.), true);
    EXPECT_EQ(maingo.get_option("targetLowerBound"), 42.);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, targetUpperBound)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("targetUpperBound", 42.), true);
    EXPECT_EQ(maingo.get_option("targetUpperBound"), 42.);
}
 

///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, PRE_maxLocalSearches)
{
 MAiNGO maingo;
 EXPECT_EQ(maingo.set_option("PRE_maxLocalSearches", 42), true);
 EXPECT_EQ(maingo.get_option("PRE_maxLocalSearches"), 42);

 EXPECT_EQ(maingo.set_option("PRE_maxLocalSearches", 42.5), true);
 EXPECT_EQ(maingo.get_option("PRE_maxLocalSearches"), (int)42.5);

 EXPECT_EQ(maingo.set_option("PRE_maxLocalSearches", -1), true);
 EXPECT_EQ(maingo.get_option("PRE_maxLocalSearches"), 0);
}
 

///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, PRE_obbtMaxRounds)
{
 MAiNGO maingo;
 EXPECT_EQ(maingo.set_option("PRE_obbtMaxRounds", 42), true);
 EXPECT_EQ(maingo.get_option("PRE_obbtMaxRounds"), 42);

 EXPECT_EQ(maingo.set_option("PRE_obbtMaxRounds", 42.5), true);
 EXPECT_EQ(maingo.get_option("PRE_obbtMaxRounds"), (int)42.5);

 EXPECT_EQ(maingo.set_option("PRE_obbtMaxRounds", -1), true);
 EXPECT_EQ(maingo.get_option("PRE_obbtMaxRounds"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, PRE_pureMultistart)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("PRE_pureMultistart", 0), true);
    EXPECT_EQ(maingo.get_option("PRE_pureMultistart"), 0);

    EXPECT_EQ(maingo.set_option("PRE_pureMultistart", 1), true);
    EXPECT_EQ(maingo.get_option("PRE_pureMultistart"), 1);

    EXPECT_EQ(maingo.set_option("PRE_pureMultistart", 2), true);
    EXPECT_EQ(maingo.get_option("PRE_pureMultistart"), 0);

    EXPECT_EQ(maingo.set_option("PRE_pureMultistart", 0.99), true);
    EXPECT_EQ(maingo.get_option("PRE_pureMultistart"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_nodeSelection)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_nodeSelection", 0), true);
    EXPECT_EQ(maingo.get_option("BAB_nodeSelection"), 0);

    EXPECT_EQ(maingo.set_option("BAB_nodeSelection", 1), true);
    EXPECT_EQ(maingo.get_option("BAB_nodeSelection"), 1);

    EXPECT_EQ(maingo.set_option("BAB_nodeSelection", 2), true);
    EXPECT_EQ(maingo.get_option("BAB_nodeSelection"), 2);

    EXPECT_EQ(maingo.set_option("BAB_nodeSelection", 0.5), true);
    EXPECT_EQ(maingo.get_option("BAB_nodeSelection"), 0);

    EXPECT_EQ(maingo.set_option("BAB_nodeSelection", 1.5), true);
    EXPECT_EQ(maingo.get_option("BAB_nodeSelection"), 0);

    EXPECT_EQ(maingo.set_option("BAB_nodeSelection", 3), true);
    EXPECT_EQ(maingo.get_option("BAB_nodeSelection"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_branchVariable)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_branchVariable", 0), true);
    EXPECT_EQ(maingo.get_option("BAB_branchVariable"), 0);

    EXPECT_EQ(maingo.set_option("BAB_branchVariable", 1), true);
    EXPECT_EQ(maingo.get_option("BAB_branchVariable"), 1);

    EXPECT_EQ(maingo.set_option("BAB_branchVariable", 2), true);
    EXPECT_EQ(maingo.get_option("BAB_branchVariable"), 0);

    EXPECT_EQ(maingo.set_option("BAB_branchVariable", 0.99), true);
    EXPECT_EQ(maingo.get_option("BAB_branchVariable"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_alwaysSolveObbt)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_alwaysSolveObbt", 0), true);
    EXPECT_EQ(maingo.get_option("BAB_alwaysSolveObbt"), 0);

    EXPECT_EQ(maingo.set_option("BAB_alwaysSolveObbt", 1), true);
    EXPECT_EQ(maingo.get_option("BAB_alwaysSolveObbt"), 1);

    EXPECT_EQ(maingo.set_option("BAB_alwaysSolveObbt", 2), true);
    EXPECT_EQ(maingo.get_option("BAB_alwaysSolveObbt"), 0);

    EXPECT_EQ(maingo.set_option("BAB_alwaysSolveObbt", 0.99), true);
    EXPECT_EQ(maingo.get_option("BAB_alwaysSolveObbt"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_obbtDecayCoefficient)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_obbtDecayCoefficient", 42.), true);
    EXPECT_EQ(maingo.get_option("BAB_obbtDecayCoefficient"), 42.);

    EXPECT_EQ(maingo.set_option("BAB_obbtDecayCoefficient", -1.), true);
    EXPECT_EQ(maingo.get_option("BAB_obbtDecayCoefficient"), 0.);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_probing)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_probing", 0), true);
    EXPECT_EQ(maingo.get_option("BAB_probing"), 0);

    EXPECT_EQ(maingo.set_option("BAB_probing", 1), true);
    EXPECT_EQ(maingo.get_option("BAB_probing"), 1);

    EXPECT_EQ(maingo.set_option("BAB_probing", 2), true);
    EXPECT_EQ(maingo.get_option("BAB_probing"), 0);

    EXPECT_EQ(maingo.set_option("BAB_probing", 0.99), true);
    EXPECT_EQ(maingo.get_option("BAB_probing"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_dbbt)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_dbbt", 0), true);
    EXPECT_EQ(maingo.get_option("BAB_dbbt"), 0);

    EXPECT_EQ(maingo.set_option("BAB_dbbt", 1), true);
    EXPECT_EQ(maingo.get_option("BAB_dbbt"), 1);

    EXPECT_EQ(maingo.set_option("BAB_dbbt", 2), true);
    EXPECT_EQ(maingo.get_option("BAB_dbbt"), 1);

    EXPECT_EQ(maingo.set_option("BAB_dbbt", 0.99), true);
    EXPECT_EQ(maingo.get_option("BAB_dbbt"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_constraintPropagation)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_constraintPropagation", 0), true);
    EXPECT_EQ(maingo.get_option("BAB_constraintPropagation"), 0);

    EXPECT_EQ(maingo.set_option("BAB_constraintPropagation", 1), true);
    EXPECT_EQ(maingo.get_option("BAB_constraintPropagation"), 1);

    EXPECT_EQ(maingo.set_option("BAB_constraintPropagation", 2), true);
    EXPECT_EQ(maingo.get_option("BAB_constraintPropagation"), 0);

    EXPECT_EQ(maingo.set_option("BAB_constraintPropagation", 0.99), true);
    EXPECT_EQ(maingo.get_option("BAB_constraintPropagation"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_solver)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_solver", 0), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 0);

    EXPECT_EQ(maingo.set_option("LBP_solver", 1), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 1);

#ifdef HAVE_CPLEX
    EXPECT_EQ(maingo.set_option("LBP_solver", 2), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 2);
#elif HAVE_GUROBI
    EXPECT_EQ(maingo.set_option("LBP_solver", 2), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 4);
#else
    EXPECT_EQ(maingo.set_option("LBP_solver", 2), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 3);
#endif

    EXPECT_EQ(maingo.set_option("LBP_solver", 3), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 3);

#ifdef HAVE_GUROBI
    EXPECT_EQ(maingo.set_option("LBP_solver", 4), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 4);
#elif HAVE_CPLEX
    EXPECT_EQ(maingo.set_option("LBP_solver", 4), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 2);
#else
    EXPECT_EQ(maingo.set_option("LBP_solver", 4), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 3);
#endif

    EXPECT_EQ(maingo.set_option("LBP_solver", 5), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 5);

#ifdef HAVE_CPLEX
    EXPECT_EQ(maingo.set_option("LBP_solver", 0.5), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 2);

    EXPECT_EQ(maingo.set_option("LBP_solver", 1.5), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 2);

    EXPECT_EQ(maingo.set_option("LBP_solver", 6), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 2);
#elif HAVE_GUROBI
    EXPECT_EQ(maingo.set_option("LBP_solver", 0.5), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 4);

    EXPECT_EQ(maingo.set_option("LBP_solver", 1.5), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 4);

    EXPECT_EQ(maingo.set_option("LBP_solver", 6), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 4);
#else
    EXPECT_EQ(maingo.set_option("LBP_solver", 0.5), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 3);

    EXPECT_EQ(maingo.set_option("LBP_solver", 1.5), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 3);

    EXPECT_EQ(maingo.set_option("LBP_solver", 6), true);
    EXPECT_EQ(maingo.get_option("LBP_solver"), 3);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_linPoints)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_linPoints", 0), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 0);

    EXPECT_EQ(maingo.set_option("LBP_linPoints", 1), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 1);

    EXPECT_EQ(maingo.set_option("LBP_linPoints", 2), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 2);

    EXPECT_EQ(maingo.set_option("LBP_linPoints", 3), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 3);

    EXPECT_EQ(maingo.set_option("LBP_linPoints", 4), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 4);

    EXPECT_EQ(maingo.set_option("LBP_linPoints", 5), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 5);

    EXPECT_EQ(maingo.set_option("LBP_linPoints", 0.5), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 0);

    EXPECT_EQ(maingo.set_option("LBP_linPoints", 1.5), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 0);

    EXPECT_EQ(maingo.set_option("LBP_linPoints", 6), true);
    EXPECT_EQ(maingo.get_option("LBP_linPoints"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_subgradientIntervals)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_subgradientIntervals", 0), true);
    EXPECT_EQ(maingo.get_option("LBP_subgradientIntervals"), 0);

    EXPECT_EQ(maingo.set_option("LBP_subgradientIntervals", 1), true);
    EXPECT_EQ(maingo.get_option("LBP_subgradientIntervals"), 1);

    EXPECT_EQ(maingo.set_option("LBP_subgradientIntervals", 2), true);
    EXPECT_EQ(maingo.get_option("LBP_subgradientIntervals"), 0);

    EXPECT_EQ(maingo.set_option("LBP_subgradientIntervals", 0.99), true);
    EXPECT_EQ(maingo.get_option("LBP_subgradientIntervals"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_obbtMinImprovement)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_obbtMinImprovement", 0.25), true);
    EXPECT_EQ(maingo.get_option("LBP_obbtMinImprovement"), 0.25);

    EXPECT_EQ(maingo.set_option("LBP_obbtMinImprovement", 0), true);
    EXPECT_EQ(maingo.get_option("LBP_obbtMinImprovement"), 0);

    EXPECT_EQ(maingo.set_option("LBP_obbtMinImprovement", 1), true);
    EXPECT_EQ(maingo.get_option("LBP_obbtMinImprovement"), 1);

    EXPECT_EQ(maingo.set_option("LBP_obbtMinImprovement", -0.5), true);
    EXPECT_EQ(maingo.get_option("LBP_obbtMinImprovement"), 0.5);

    EXPECT_EQ(maingo.set_option("LBP_obbtMinImprovement", 1.5), true);
    EXPECT_EQ(maingo.get_option("LBP_obbtMinImprovement"), 0.5);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_activateMoreScaling)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_activateMoreScaling", 1e3), true);
    EXPECT_EQ(maingo.get_option("LBP_activateMoreScaling"), 1e3);

    EXPECT_EQ(maingo.set_option("LBP_activateMoreScaling", 99), true);
    EXPECT_EQ(maingo.get_option("LBP_activateMoreScaling"), 10000);

    EXPECT_EQ(maingo.set_option("LBP_activateMoreScaling", 100001), true);
    EXPECT_EQ(maingo.get_option("LBP_activateMoreScaling"), 10000);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_addAuxiliaryVars)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_addAuxiliaryVars", 0), true);
    EXPECT_EQ(maingo.get_option("LBP_addAuxiliaryVars"), 0);

    EXPECT_EQ(maingo.set_option("LBP_addAuxiliaryVars", 1), true);
    EXPECT_EQ(maingo.get_option("LBP_addAuxiliaryVars"), 1);

    EXPECT_EQ(maingo.set_option("LBP_addAuxiliaryVars", 2), true);
    EXPECT_EQ(maingo.get_option("LBP_addAuxiliaryVars"), 0);

    EXPECT_EQ(maingo.set_option("LBP_addAuxiliaryVars", 0.99), true);
    EXPECT_EQ(maingo.get_option("LBP_addAuxiliaryVars"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_minFactorsForAux)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_minFactorsForAux", 4), true);
    EXPECT_EQ(maingo.get_option("LBP_minFactorsForAux"), 4);

    EXPECT_EQ(maingo.set_option("LBP_minFactorsForAux", 4.35), true);
    EXPECT_EQ(maingo.get_option("LBP_minFactorsForAux"), (int)4.35);

    EXPECT_EQ(maingo.set_option("LBP_minFactorsForAux", 1), true);
    EXPECT_EQ(maingo.get_option("LBP_minFactorsForAux"), 2);

    EXPECT_EQ(maingo.set_option("LBP_minFactorsForAux", -10), true);
    EXPECT_EQ(maingo.get_option("LBP_minFactorsForAux"), 2);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_maxNumberOfAddedFactors)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_maxNumberOfAddedFactors", 4), true);
    EXPECT_EQ(maingo.get_option("LBP_maxNumberOfAddedFactors"), 4);

    EXPECT_EQ(maingo.set_option("LBP_maxNumberOfAddedFactors", 4.35), true);
    EXPECT_EQ(maingo.get_option("LBP_maxNumberOfAddedFactors"), (int)4.35);

    EXPECT_EQ(maingo.set_option("LBP_maxNumberOfAddedFactors", 0.5), true);
    EXPECT_EQ(maingo.get_option("LBP_maxNumberOfAddedFactors"), 1);

    EXPECT_EQ(maingo.set_option("LBP_maxNumberOfAddedFactors", -10), true);
    EXPECT_EQ(maingo.get_option("LBP_maxNumberOfAddedFactors"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, MC_mvcompUse)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("MC_mvcompUse", 0), true);
    EXPECT_EQ(maingo.get_option("MC_mvcompUse"), 0);

    EXPECT_EQ(maingo.set_option("MC_mvcompUse", 1), true);
    EXPECT_EQ(maingo.get_option("MC_mvcompUse"), 1);

    EXPECT_EQ(maingo.set_option("MC_mvcompUse", 2), true);
    EXPECT_EQ(maingo.get_option("MC_mvcompUse"), 1);

    EXPECT_EQ(maingo.set_option("MC_mvcompUse", 0.99), true);
    EXPECT_EQ(maingo.get_option("MC_mvcompUse"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, MC_mvcompTol)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("MC_mvcompTol", 1e-10), true);
    EXPECT_EQ(maingo.get_option("MC_mvcompTol"), 1e-10);

    EXPECT_EQ(maingo.set_option("MC_mvcompTol", 1e-13), true);
    EXPECT_EQ(maingo.get_option("MC_mvcompTol"), 1e-12);

    EXPECT_EQ(maingo.set_option("MC_mvcompTol", 1e-8), true);
    EXPECT_EQ(maingo.get_option("MC_mvcompTol"), 1e-12);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, MC_envelTol)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("MC_envelTol", 1e-10), true);
    EXPECT_EQ(maingo.get_option("MC_envelTol"), 1e-10);

    EXPECT_EQ(maingo.set_option("MC_envelTol", 1e-13), true);
    EXPECT_EQ(maingo.get_option("MC_envelTol"), 1e-12);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UBP_solverPreprocessing)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 0), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 0);

    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 1), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 1);

    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 2), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 2);

    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 3), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 3);

    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 4), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 4);

    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 5), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 5);

#ifdef HAVE_KNITRO
    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 6), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 6);
#else
    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 6), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 5);
#endif

    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 0.5), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 5);

    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 1.5), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 5);

    EXPECT_EQ(maingo.set_option("UBP_solverPreprocessing", 7), true);
    EXPECT_EQ(maingo.get_option("UBP_solverPreprocessing"), 5);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UBP_maxStepsPreprocessing)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("UBP_maxStepsPreprocessing", 4), true);
    EXPECT_EQ(maingo.get_option("UBP_maxStepsPreprocessing"), 4);

    EXPECT_EQ(maingo.set_option("UBP_maxStepsPreprocessing", 4.35), true);
    EXPECT_EQ(maingo.get_option("UBP_maxStepsPreprocessing"), (int)4.35);

    EXPECT_EQ(maingo.set_option("UBP_maxStepsPreprocessing", 0.5), true);
    EXPECT_EQ(maingo.get_option("UBP_maxStepsPreprocessing"), 1);

    EXPECT_EQ(maingo.set_option("UBP_maxStepsPreprocessing", -10), true);
    EXPECT_EQ(maingo.get_option("UBP_maxStepsPreprocessing"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UBP_maxTimePreprocessing)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("UBP_maxTimePreprocessing", 4), true);
    EXPECT_EQ(maingo.get_option("UBP_maxTimePreprocessing"), 4);

    EXPECT_EQ(maingo.set_option("UBP_maxTimePreprocessing", 0.05), true);
    EXPECT_EQ(maingo.get_option("UBP_maxTimePreprocessing"), 0.1);

    EXPECT_EQ(maingo.set_option("UBP_maxTimePreprocessing", -10), true);
    EXPECT_EQ(maingo.get_option("UBP_maxTimePreprocessing"), 0.1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UBP_solverBab)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("UBP_solverBab", 0), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 0);

    EXPECT_EQ(maingo.set_option("UBP_solverBab", 1), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 1);

    EXPECT_EQ(maingo.set_option("UBP_solverBab", 2), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 2);

    EXPECT_EQ(maingo.set_option("UBP_solverBab", 3), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 3);

    EXPECT_EQ(maingo.set_option("UBP_solverBab", 4), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 4);

    EXPECT_EQ(maingo.set_option("UBP_solverBab", 5), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 5);

#ifdef HAVE_KNITRO
    EXPECT_EQ(maingo.set_option("UBP_solverBab", 6), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 6);
#else
    EXPECT_EQ(maingo.set_option("UBP_solverBab", 6), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 4);
#endif

    EXPECT_EQ(maingo.set_option("UBP_solverBab", 0.5), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 4);

    EXPECT_EQ(maingo.set_option("UBP_solverBab", 1.5), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 4);

    EXPECT_EQ(maingo.set_option("UBP_solverBab", 7), true);
    EXPECT_EQ(maingo.get_option("UBP_solverBab"), 4);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UBP_maxStepsBab)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("UBP_maxStepsBab", 4), true);
    EXPECT_EQ(maingo.get_option("UBP_maxStepsBab"), 4);

    EXPECT_EQ(maingo.set_option("UBP_maxStepsBab", 4.35), true);
    EXPECT_EQ(maingo.get_option("UBP_maxStepsBab"), (int)4.35);

    EXPECT_EQ(maingo.set_option("UBP_maxStepsBab", 0.5), true);
    EXPECT_EQ(maingo.get_option("UBP_maxStepsBab"), 1);

    EXPECT_EQ(maingo.set_option("UBP_maxStepsBab", -10), true);
    EXPECT_EQ(maingo.get_option("UBP_maxStepsBab"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UBP_maxTimeBab)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("UBP_maxTimeBab", 4), true);
    EXPECT_EQ(maingo.get_option("UBP_maxTimeBab"), 4);

    EXPECT_EQ(maingo.set_option("UBP_maxTimeBab", 0.05), true);
    EXPECT_EQ(maingo.get_option("UBP_maxTimeBab"), 0.1);

    EXPECT_EQ(maingo.set_option("UBP_maxTimeBab", -10), true);
    EXPECT_EQ(maingo.get_option("UBP_maxTimeBab"), 0.1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UBP_ignoreNodeBounds)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("UBP_ignoreNodeBounds", 0), true);
    EXPECT_EQ(maingo.get_option("UBP_ignoreNodeBounds"), 0);

    EXPECT_EQ(maingo.set_option("UBP_ignoreNodeBounds", 1), true);
    EXPECT_EQ(maingo.get_option("UBP_ignoreNodeBounds"), 1);

    EXPECT_EQ(maingo.set_option("UBP_ignoreNodeBounds", 2), true);
    EXPECT_EQ(maingo.get_option("UBP_ignoreNodeBounds"), 0);

    EXPECT_EQ(maingo.set_option("UBP_ignoreNodeBounds", 0.99), true);
    EXPECT_EQ(maingo.get_option("UBP_ignoreNodeBounds"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, EC_nPoints)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("EC_nPoints", 4), true);
    EXPECT_EQ(maingo.get_option("EC_nPoints"), 4);

    EXPECT_EQ(maingo.set_option("EC_nPoints", 4.35), true);
    EXPECT_EQ(maingo.get_option("EC_nPoints"), (int)4.35);

    EXPECT_EQ(maingo.set_option("EC_nPoints", 1), true);
    EXPECT_EQ(maingo.get_option("EC_nPoints"), 2);

    EXPECT_EQ(maingo.set_option("EC_nPoints", -10), true);
    EXPECT_EQ(maingo.get_option("EC_nPoints"), 2);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, LBP_verbosity)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("LBP_verbosity", 0), true);
    EXPECT_EQ(maingo.get_option("LBP_verbosity"), 0);

    EXPECT_EQ(maingo.set_option("LBP_verbosity", 1), true);
    EXPECT_EQ(maingo.get_option("LBP_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("LBP_verbosity", 2), true);
    EXPECT_EQ(maingo.get_option("LBP_verbosity"), 2);

    EXPECT_EQ(maingo.set_option("LBP_verbosity", 0.5), true);
    EXPECT_EQ(maingo.get_option("LBP_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("LBP_verbosity", 1.5), true);
    EXPECT_EQ(maingo.get_option("LBP_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("LBP_verbosity", 3), true);
    EXPECT_EQ(maingo.get_option("LBP_verbosity"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UBP_verbosity)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("UBP_verbosity", 0), true);
    EXPECT_EQ(maingo.get_option("UBP_verbosity"), 0);

    EXPECT_EQ(maingo.set_option("UBP_verbosity", 1), true);
    EXPECT_EQ(maingo.get_option("UBP_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("UBP_verbosity", 2), true);
    EXPECT_EQ(maingo.get_option("UBP_verbosity"), 2);

    EXPECT_EQ(maingo.set_option("UBP_verbosity", 0.5), true);
    EXPECT_EQ(maingo.get_option("UBP_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("UBP_verbosity", 1.5), true);
    EXPECT_EQ(maingo.get_option("UBP_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("UBP_verbosity", 3), true);
    EXPECT_EQ(maingo.get_option("UBP_verbosity"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_verbosity)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_verbosity", 0), true);
    EXPECT_EQ(maingo.get_option("BAB_verbosity"), 0);

    EXPECT_EQ(maingo.set_option("BAB_verbosity", 1), true);
    EXPECT_EQ(maingo.get_option("BAB_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("BAB_verbosity", 2), true);
    EXPECT_EQ(maingo.get_option("BAB_verbosity"), 2);

    EXPECT_EQ(maingo.set_option("BAB_verbosity", 0.5), true);
    EXPECT_EQ(maingo.get_option("BAB_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("BAB_verbosity", 1.5), true);
    EXPECT_EQ(maingo.get_option("BAB_verbosity"), 1);

    EXPECT_EQ(maingo.set_option("BAB_verbosity", 3), true);
    EXPECT_EQ(maingo.get_option("BAB_verbosity"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_printFreq)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_printFreq", 4), true);
    EXPECT_EQ(maingo.get_option("BAB_printFreq"), 4);

    EXPECT_EQ(maingo.set_option("BAB_printFreq", 4.35), true);
    EXPECT_EQ(maingo.get_option("BAB_printFreq"), (int)4.35);

    EXPECT_EQ(maingo.set_option("BAB_printFreq", 0.5), true);
    EXPECT_EQ(maingo.get_option("BAB_printFreq"), 1);

    EXPECT_EQ(maingo.set_option("BAB_printFreq", -10), true);
    EXPECT_EQ(maingo.get_option("BAB_printFreq"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, BAB_logFreq)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("BAB_logFreq", 4), true);
    EXPECT_EQ(maingo.get_option("BAB_logFreq"), 4);

    EXPECT_EQ(maingo.set_option("BAB_logFreq", 4.35), true);
    EXPECT_EQ(maingo.get_option("BAB_logFreq"), (int)4.35);

    EXPECT_EQ(maingo.set_option("BAB_logFreq", 0.5), true);
    EXPECT_EQ(maingo.get_option("BAB_logFreq"), 1);

    EXPECT_EQ(maingo.set_option("BAB_logFreq", -10), true);
    EXPECT_EQ(maingo.get_option("BAB_logFreq"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, loggingDestination)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("loggingDestination", 0), true);
    EXPECT_EQ(maingo.get_option("loggingDestination"), 0);

    EXPECT_EQ(maingo.set_option("loggingDestination", 1), true);
    EXPECT_EQ(maingo.get_option("loggingDestination"), 1);

    EXPECT_EQ(maingo.set_option("loggingDestination", 2), true);
    EXPECT_EQ(maingo.get_option("loggingDestination"), 2);

    EXPECT_EQ(maingo.set_option("loggingDestination", 3), true);
    EXPECT_EQ(maingo.get_option("loggingDestination"), 3);


    EXPECT_EQ(maingo.set_option("loggingDestination", 0.5), true);
    EXPECT_EQ(maingo.get_option("loggingDestination"), 3);

    EXPECT_EQ(maingo.set_option("loggingDestination", 1.5), true);
    EXPECT_EQ(maingo.get_option("loggingDestination"), 3);

    EXPECT_EQ(maingo.set_option("loggingDestination", 4), true);
    EXPECT_EQ(maingo.get_option("loggingDestination"), 3);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, writeCsv)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("writeCsv", 0), true);
    EXPECT_EQ(maingo.get_option("writeCsv"), 0);

    EXPECT_EQ(maingo.set_option("writeCsv", 1), true);
    EXPECT_EQ(maingo.get_option("writeCsv"), 1);

    EXPECT_EQ(maingo.set_option("writeCsv", 2), true);
    EXPECT_EQ(maingo.get_option("writeCsv"), 0);

    EXPECT_EQ(maingo.set_option("writeCsv", 0.99), true);
    EXPECT_EQ(maingo.get_option("writeCsv"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, writeJson)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("writeJson", 0), true);
    EXPECT_EQ(maingo.get_option("writeJson"), 0);

    EXPECT_EQ(maingo.set_option("writeJson", 1), true);
    EXPECT_EQ(maingo.get_option("writeJson"), 1);

    EXPECT_EQ(maingo.set_option("writeJson", 2), true);
    EXPECT_EQ(maingo.get_option("writeJson"), 0);

    EXPECT_EQ(maingo.set_option("writeJson", 0.99), true);
    EXPECT_EQ(maingo.get_option("writeJson"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, writeResultFile)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("writeResultFile", 0), true);
    EXPECT_EQ(maingo.get_option("writeResultFile"), 0);

    EXPECT_EQ(maingo.set_option("writeResultFile", 1), true);
    EXPECT_EQ(maingo.get_option("writeResultFile"), 1);

    EXPECT_EQ(maingo.set_option("writeResultFile", 2), true);
    EXPECT_EQ(maingo.get_option("writeResultFile"), 0);

    EXPECT_EQ(maingo.set_option("writeResultFile", 0.99), true);
    EXPECT_EQ(maingo.get_option("writeResultFile"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, writeToLogSec)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("writeToLogSec", 42.5), true);
    EXPECT_EQ(maingo.get_option("writeToLogSec"), 42);

    EXPECT_EQ(maingo.set_option("writeToLogSec", 4.2), true);
    EXPECT_EQ(maingo.get_option("writeToLogSec"), 1800);

    EXPECT_EQ(maingo.set_option("writeToLogSec", -10), true);
    EXPECT_EQ(maingo.get_option("writeToLogSec"), 1800);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, PRE_printEveryLocalSearch)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("PRE_printEveryLocalSearch", 0), true);
    EXPECT_EQ(maingo.get_option("PRE_printEveryLocalSearch"), 0);

    EXPECT_EQ(maingo.set_option("PRE_printEveryLocalSearch", 1), true);
    EXPECT_EQ(maingo.get_option("PRE_printEveryLocalSearch"), 1);

    EXPECT_EQ(maingo.set_option("PRE_printEveryLocalSearch", 2), true);
    EXPECT_EQ(maingo.get_option("PRE_printEveryLocalSearch"), 0);

    EXPECT_EQ(maingo.set_option("PRE_printEveryLocalSearch", 0.99), true);
    EXPECT_EQ(maingo.get_option("PRE_printEveryLocalSearch"), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, modelWritingLanguage)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("modelWritingLanguage", 0), true);
    EXPECT_EQ(maingo.get_option("modelWritingLanguage"), 0);

    EXPECT_EQ(maingo.set_option("modelWritingLanguage", 1), true);
    EXPECT_EQ(maingo.get_option("modelWritingLanguage"), 1);

    EXPECT_EQ(maingo.set_option("modelWritingLanguage", 2), true);
    EXPECT_EQ(maingo.get_option("modelWritingLanguage"), 2);


    EXPECT_EQ(maingo.set_option("modelWritingLanguage", 0.5), true);
    EXPECT_EQ(maingo.get_option("modelWritingLanguage"), 1);

    EXPECT_EQ(maingo.set_option("modelWritingLanguage", 1.5), true);
    EXPECT_EQ(maingo.get_option("modelWritingLanguage"), 1);

    EXPECT_EQ(maingo.set_option("modelWritingLanguage", 3), true);
    EXPECT_EQ(maingo.get_option("modelWritingLanguage"), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_approach)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_approach", 0), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);

    EXPECT_EQ(maingo.set_option("growing_approach", 1), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 1);

    EXPECT_EQ(maingo.set_option("growing_approach", 2), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 2);


    EXPECT_EQ(maingo.set_option("growing_approach", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);

    EXPECT_EQ(maingo.set_option("growing_approach", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);

    EXPECT_EQ(maingo.set_option("growing_approach", 3), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);
#else
    EXPECT_EQ(maingo.set_option("growing_approach", 0), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);

    EXPECT_EQ(maingo.set_option("growing_approach", 1), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);

    EXPECT_EQ(maingo.set_option("growing_approach", 2), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);

    EXPECT_EQ(maingo.set_option("growing_approach", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);

    EXPECT_EQ(maingo.set_option("growing_approach", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);

    EXPECT_EQ(maingo.set_option("growing_approach", 3), true);
    EXPECT_EQ(maingo.get_option("growing_approach"), 0);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_maxTimePostprocessing)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_maxTimePostprocessing", 1e3), true);
    EXPECT_EQ(maingo.get_option("growing_maxTimePostprocessing"), 1e3);


    EXPECT_EQ(maingo.set_option("growing_maxTimePostprocessing", -10), true);
    EXPECT_EQ(maingo.get_option("growing_maxTimePostprocessing"), 60);
#else
    EXPECT_EQ(maingo.set_option("growing_maxTimePostprocessing", 1e3), true);
    EXPECT_EQ(maingo.get_option("growing_maxTimePostprocessing"), 60);

    EXPECT_EQ(maingo.set_option("growing_maxTimePostprocessing", -10), true);
    EXPECT_EQ(maingo.get_option("growing_maxTimePostprocessing"), 60);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_useResampling)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_useResampling", 0), true);
    EXPECT_EQ(maingo.get_option("growing_useResampling"), 0);

    EXPECT_EQ(maingo.set_option("growing_useResampling", 1), true);
    EXPECT_EQ(maingo.get_option("growing_useResampling"), 1);


    EXPECT_EQ(maingo.set_option("growing_useResampling", 2), true);
    EXPECT_EQ(maingo.get_option("growing_useResampling"), 0);

    EXPECT_EQ(maingo.set_option("growing_useResampling", 0.99), true);
    EXPECT_EQ(maingo.get_option("growing_useResampling"), 0);
#else
    EXPECT_EQ(maingo.set_option("growing_useResampling", 0), true);
    EXPECT_EQ(maingo.get_option("growing_useResampling"), 0);

    EXPECT_EQ(maingo.set_option("growing_useResampling", 1), true);
    EXPECT_EQ(maingo.get_option("growing_useResampling"), 0);

    EXPECT_EQ(maingo.set_option("growing_useResampling", 2), true);
    EXPECT_EQ(maingo.get_option("growing_useResampling"), 0);

    EXPECT_EQ(maingo.set_option("growing_useResampling", 0.99), true);
    EXPECT_EQ(maingo.get_option("growing_useResampling"), 0);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_shuffleData)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_shuffleData", 0), true);
    EXPECT_EQ(maingo.get_option("growing_shuffleData"), 0);

    EXPECT_EQ(maingo.set_option("growing_shuffleData", 1), true);
    EXPECT_EQ(maingo.get_option("growing_shuffleData"), 1);


    EXPECT_EQ(maingo.set_option("growing_shuffleData", 2), true);
    EXPECT_EQ(maingo.get_option("growing_shuffleData"), 1);

    EXPECT_EQ(maingo.set_option("growing_shuffleData", 0.99), true);
    EXPECT_EQ(maingo.get_option("growing_shuffleData"), 1);
#else
    EXPECT_EQ(maingo.set_option("growing_shuffleData", 0), true);
    EXPECT_EQ(maingo.get_option("growing_shuffleData"), 1);

    EXPECT_EQ(maingo.set_option("growing_shuffleData", 1), true);
    EXPECT_EQ(maingo.get_option("growing_shuffleData"), 1);

    EXPECT_EQ(maingo.set_option("growing_shuffleData", 2), true);
    EXPECT_EQ(maingo.get_option("growing_shuffleData"), 1);

    EXPECT_EQ(maingo.set_option("growing_shuffleData", 0.99), true);
    EXPECT_EQ(maingo.get_option("growing_shuffleData"), 1);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_relativeSizing)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    std::ifstream sizingFile("growingDatasetsSizing.txt");
    if (sizingFile.good()) {
        // If mandatory file found
        EXPECT_EQ(maingo.set_option("growing_relativeSizing", 0), true);
        EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 0);

        // Test also for absent file
        auto ans = std::remove("growingDatasetsSizing.txt");
        if (ans == 0) {
            EXPECT_EQ(maingo.set_option("growing_relativeSizing", 0), true);
            EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);
        }
    }
    else {
        // If mandatory file missing
        EXPECT_EQ(maingo.set_option("growing_relativeSizing", 0), true);
        EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);

        // Test also for existing file
        std::ofstream{ "growingDatasetsSizing.txt" };
        EXPECT_EQ(maingo.set_option("growing_relativeSizing", 0), true);
        EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 0);
    }
    // Without file
    // With file

    EXPECT_EQ(maingo.set_option("growing_relativeSizing", 1), true);
    EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);


    EXPECT_EQ(maingo.set_option("growing_relativeSizing", 2), true);
    EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);

    EXPECT_EQ(maingo.set_option("growing_relativeSizing", 0.99), true);
    EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);
#else
    EXPECT_EQ(maingo.set_option("growing_relativeSizing", 0), true);
    EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);

    EXPECT_EQ(maingo.set_option("growing_relativeSizing", 1), true);
    EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);

    EXPECT_EQ(maingo.set_option("growing_relativeSizing", 2), true);
    EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);

    EXPECT_EQ(maingo.set_option("growing_relativeSizing", 0.99), true);
    EXPECT_EQ(maingo.get_option("growing_relativeSizing"), 1);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_maxSize)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_maxSize", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_maxSize"), 0.5);


    EXPECT_EQ(maingo.set_option("growing_maxSize", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_maxSize"), 0.9);

    EXPECT_EQ(maingo.set_option("growing_maxSize", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_maxSize"), 0.9);
#else
    EXPECT_EQ(maingo.set_option("growing_maxSize", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_maxSize"), 0.9);

    EXPECT_EQ(maingo.set_option("growing_maxSize", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_maxSize"), 0.9);

    EXPECT_EQ(maingo.set_option("growing_maxSize", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_maxSize"), 0.9);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_initPercentage)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_initPercentage", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_initPercentage"), 0.5);


    EXPECT_EQ(maingo.set_option("growing_initPercentage", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_initPercentage"), 0.1);

    EXPECT_EQ(maingo.set_option("growing_initPercentage", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_initPercentage"), 0.1);
#else
    EXPECT_EQ(maingo.set_option("growing_initPercentage", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_initPercentage"), 0.1);

    EXPECT_EQ(maingo.set_option("growing_initPercentage", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_initPercentage"), 0.1);

    EXPECT_EQ(maingo.set_option("growing_initPercentage", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_initPercentage"), 0.1);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_augmentPercentage)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_augmentPercentage", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentPercentage"), 0.5);


    EXPECT_EQ(maingo.set_option("growing_augmentPercentage", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentPercentage"), 0.25);

    EXPECT_EQ(maingo.set_option("growing_augmentPercentage", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentPercentage"), 0.25);
#else
    EXPECT_EQ(maingo.set_option("growing_augmentPercentage", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentPercentage"), 0.25);

    EXPECT_EQ(maingo.set_option("growing_augmentPercentage", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentPercentage"), 0.25);

    EXPECT_EQ(maingo.set_option("growing_augmentPercentage", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentPercentage"), 0.25);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_augmentRule)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_augmentRule", 0), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 0);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 1), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 1);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 2), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 2);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 3), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 3);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 4), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 4);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 5);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 6), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 6);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 7), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 7);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 8), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);


    EXPECT_EQ(maingo.set_option("growing_augmentRule", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);
#else
    EXPECT_EQ(maingo.set_option("growing_augmentRule", 0), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 1), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 2), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 3), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);
    
    EXPECT_EQ(maingo.set_option("growing_augmentRule", 4), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 6), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 7), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 8), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);

    EXPECT_EQ(maingo.set_option("growing_augmentRule", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentRule"), 8);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_augmentFreq)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_augmentFreq", 4.35), true);
    EXPECT_EQ(maingo.get_option("growing_augmentFreq"), (int)4.35);

    EXPECT_EQ(maingo.set_option("growing_augmentFreq", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentFreq"), 10);

    EXPECT_EQ(maingo.set_option("growing_augmentFreq", -1), true);
    EXPECT_EQ(maingo.get_option("growing_augmentFreq"), 10);
#else
    EXPECT_EQ(maingo.set_option("growing_augmentFreq", 4.35), true);
    EXPECT_EQ(maingo.get_option("growing_augmentFreq"), 10);

    EXPECT_EQ(maingo.set_option("growing_augmentFreq", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentFreq"), 10);

    EXPECT_EQ(maingo.set_option("growing_augmentFreq", -1), true);
    EXPECT_EQ(maingo.get_option("growing_augmentFreq"), 10);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_augmentWeight)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_augmentWeight", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentWeight"), 0.5);

    EXPECT_EQ(maingo.set_option("growing_augmentWeight", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentWeight"), 1.0);

    EXPECT_EQ(maingo.set_option("growing_augmentWeight", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentWeight"), 1.0);
#else
    EXPECT_EQ(maingo.set_option("growing_augmentWeight", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentWeight"), 1.0);

    EXPECT_EQ(maingo.set_option("growing_augmentWeight", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentWeight"), 1.0);

    EXPECT_EQ(maingo.set_option("growing_augmentWeight", 1.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentWeight"), 1.0);
#endif
}


///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, growing_augmentTol)
{
    MAiNGO maingo;
#ifdef HAVE_GROWING_DATASETS
    EXPECT_EQ(maingo.set_option("growing_augmentTol", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentTol"), 0.5);


    EXPECT_EQ(maingo.set_option("growing_augmentTol", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentTol"), 0.1);
#else
    EXPECT_EQ(maingo.set_option("growing_augmentTol", 0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentTol"), 0.1);

    EXPECT_EQ(maingo.set_option("growing_augmentTol", -0.5), true);
    EXPECT_EQ(maingo.get_option("growing_augmentTol"), 0.1);
#endif
}

///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, Num_subdomains)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("Num_subdomains", 256), true);
    EXPECT_EQ(maingo.get_option("Num_subdomains"), 256);

    EXPECT_EQ(maingo.set_option("Num_subdomains", 0), true);
    EXPECT_EQ(maingo.get_option("Num_subdomains"), 1024);
}

///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, Interval_arithmetic)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("Interval_arithmetic", 0), true);
    EXPECT_EQ(maingo.get_option("Interval_arithmetic"), 0);

    EXPECT_EQ(maingo.set_option("Interval_arithmetic", 2), true);
    EXPECT_EQ(maingo.get_option("Interval_arithmetic"), 1);
}

///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, Subinterval_branch_strategy)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("Subinterval_branch_strategy", 1), true);
    EXPECT_EQ(maingo.get_option("Subinterval_branch_strategy"), 1);

    EXPECT_EQ(maingo.set_option("Subinterval_branch_strategy", 2), true);
    EXPECT_EQ(maingo.get_option("Subinterval_branch_strategy"), 0);
}

///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, Center_strategy)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("Center_strategy", 1), true);
    EXPECT_EQ(maingo.get_option("Center_strategy"), 1);

    EXPECT_EQ(maingo.set_option("Center_strategy", 2), true);
    EXPECT_EQ(maingo.get_option("Center_strategy"), 0);
}

///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, MIN_branching_per_dim)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("MIN_branching_per_dim", 3), true);
    EXPECT_EQ(maingo.get_option("MIN_branching_per_dim"), 3);

    EXPECT_EQ(maingo.set_option("MIN_branching_per_dim", 0), true);
    EXPECT_EQ(maingo.get_option("MIN_branching_per_dim"), 2);
}

///////////////////////////////////////////////////
TEST(TestMAiNGOsetAndGetOption, UnknownOption)
{
    MAiNGO maingo;
    EXPECT_EQ(maingo.set_option("bogusOption", 0.5), false);
    EXPECT_THROW(maingo.get_option("bogusOption"), maingo::MAiNGOException);
}
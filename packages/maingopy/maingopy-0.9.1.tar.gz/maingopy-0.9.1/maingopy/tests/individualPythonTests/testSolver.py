from maingopy import *
import os
import re
import unittest

class Model(MAiNGOmodel):
    def __init__(self):
        MAiNGOmodel.__init__(self)

    def get_variables(self):
        variables = [OptimizationVariable(Bounds(0,1)),
                     OptimizationVariable(Bounds(2,3))  ]
        return variables

    def evaluate(self,vars):
        result = EvaluationContainer()
        result.obj = vars[0]*vars[1]
        result.ineq = [vars[0] - vars[1]]
        result.out = [OutputVariable("The answer", 42)]
        return result



class TestMAiNGO(unittest.TestCase):
    def test_RETCODE_enum(self):
        try:
            myRetCode = GLOBALLY_OPTIMAL
            myRetCode = INFEASIBLE
            myRetCode = FEASIBLE_POINT
            myRetCode = NO_FEASIBLE_POINT_FOUND
            myRetCode = BOUND_TARGETS
            myRetCode = NOT_SOLVED_YET
            myRetCode = JUST_A_WORKER_DONT_ASK_ME
        except:
            self.fail("Value of enum RETCODE not available")

    def test_VERB_enum(self):
        try:
            verbosity = VERB_NONE
            verbosity = VERB_NORMAL
            verbosity = VERB_ALL
        except:
            self.fail("Value of enum VERB not available")

    def test_LOGGING_DESTINATION_enum(self):
        try:
            verbosity = LOGGING_NONE
            verbosity = LOGGING_OUTSTREAM
            verbosity = LOGGING_FILE
            verbosity = LOGGING_FILE_AND_STREAM
        except:
            self.fail("Value of enum LOGGING_DESTINATION not available")

    def test_UBP_SOLVER_enum(self):
        try:
            ubpSolver = UBP_SOLVER_EVAL
            ubpSolver = UBP_SOLVER_COBYLA
            ubpSolver = UBP_SOLVER_BOBYQA
            ubpSolver = UBP_SOLVER_LBFGS
            ubpSolver = UBP_SOLVER_SLSQP
            ubpSolver = UBP_SOLVER_IPOPT
            ubpSolver = UBP_SOLVER_KNITRO
        except:
            self.fail("Value of enum UBP_SOLVER not available")

    def test_LBP_SOLVER_enum(self):
        try:
            lbpSolver = LBP_SOLVER_MAiNGO
            lbpSolver = LBP_SOLVER_INTERVAL
            lbpSolver = LBP_SOLVER_CPLEX
            lbpSolver = LBP_SOLVER_GUROBI
            lbpSolver = LBP_SOLVER_CLP
            lbpSolver = LBP_SOLVER_SUBDOMAIN
        except:
            self.fail("Value of enum LBP_SOLVER not available")

    def test_WRITING_LANGUAGE_enum(self):
        try:
            myLanguage = LANG_NONE
            myLanguage = LANG_ALE
            myLanguage = LANG_GAMS
        except:
            self.fail("Value of enum PARSING_LANGUAGE not available")

    def test_initialize_maingo(self):
        try:
            myMAiNGO = MAiNGO(Model())
        except:
            self.fail("Initialization of MAiNGO raised exception unexpectedly")

    def test_maingo_setters(self):
        myMAiNGO = MAiNGO(Model())
        try:
            myMAiNGO.set_model(Model())
            myMAiNGO.set_log_file_name("LogFileName.log")
            myMAiNGO.set_result_file_name("ResFileName.txt")
            myMAiNGO.set_solution_and_statistics_csv_file_name("solutionStatistics.csv")
            myMAiNGO.set_iterations_csv_file_name("Iterations.csv")
            myMAiNGO.set_json_file_name("JsonFileName.json")
        except:
            self.fail("Setter function of MAiNGO raised exception unexpectedly")

    def test_set_option(self):
        myMAiNGO = MAiNGO(Model())
        self.assertEqual(myMAiNGO.set_option("madeUpOptionThatDoesNotExist",42), False)
        with open('individualPythonTests/MAiNGOSettings.txt', 'r') as f:
            file_content = f.read()
        pattern = re.compile(r'(?:#.+\n)+#?\s*(\w+)\s+(\S+)')
        example_file_options = re.findall(pattern, file_content)
        for option, value in example_file_options:
            self.assertEqual(myMAiNGO.set_option(option, float(value)), True)

    def test_read_settings(self):
        myMAiNGO = MAiNGO(Model())
        try:
            myMAiNGO.read_settings("madeUpSettingsFileThatDoesNotExists.txt")
            myMAiNGO.read_settings("individualPythonTests/MAiNGOSettings.txt")
            myMAiNGO.read_settings()
        except:
            self.fail("read_settings function of MAiNGO raised exception unexpectedly")

    def test_write_to_other_language_via_function(self):
        if os.path.exists("tmpAleFile.txt"):
            self.fail("Error testing the writing of ALE file via function: tmpAleFile.txt already exists.")
        myModel = Model()
        myMAiNGO = MAiNGO(myModel)
        myMAiNGO.set_option("loggingDestination",LOGGING_NONE)
        myMAiNGO.set_option("writeResultFile",False)
        myMAiNGO.write_model_to_file_in_other_language(LANG_ALE, "tmpAleFile.txt")
        if not os.path.exists("tmpAleFile.txt"):
            self.fail("MAiNGO did not write ALE file via function.")
        os.remove("tmpAleFile.txt")

    def test_write_to_other_language_via_option(self):
        if os.path.exists("MAiNGO_written_model.txt"):
            self.fail("Error testing the writing of ALE file via option: MAiNGO_written_model.txt already exists.")
        myModel = Model()
        myMAiNGO = MAiNGO(myModel)
        myMAiNGO.set_option("loggingDestination",LOGGING_NONE)
        myMAiNGO.set_option("writeResultFile",False)
        myMAiNGO.set_option("modelWritingLanguage",LANG_ALE)
        myMAiNGO.set_option("PRE_pureMultistart",True)
        myMAiNGO.set_option("PRE_maxLocalSearches",0)
        myMAiNGO.solve()
        if not os.path.exists("MAiNGO_written_model.txt"):
            self.fail("MAiNGO did not write ALE file via option.")
        os.remove("MAiNGO_written_model.txt")

    def test_getters_before_solve(self):
        myModel = Model()
        myMAiNGO = MAiNGO(myModel)
        self.assertEqual(myMAiNGO.get_status(), NOT_SOLVED_YET)
        with self.assertRaises(Exception):
            myMAiNGO.get_additional_outputs_at_solution_point()
        with self.assertRaises(Exception):
            myMAiNGO.get_cpu_solution_time()
        with self.assertRaises(Exception):
            myMAiNGO.get_final_abs_gap()
        with self.assertRaises(Exception):
            myMAiNGO.get_final_LBD()
        with self.assertRaises(Exception):
            myMAiNGO.get_final_rel_gap()
        with self.assertRaises(Exception):
            myMAiNGO.get_iterations()
        with self.assertRaises(Exception):
            myMAiNGO.get_LBP_count()
        with self.assertRaises(Exception):
            myMAiNGO.get_max_nodes_in_memory()
        with self.assertRaises(Exception):
            myMAiNGO.get_model_at_solution_point()
        with self.assertRaises(Exception):
            myMAiNGO.get_objective_value()
        with self.assertRaises(Exception):
            myMAiNGO.get_solution_point()
        with self.assertRaises(Exception):
            myMAiNGO.get_UBP_count()
        with self.assertRaises(Exception):
            myMAiNGO.get_wallclock_solution_time()

    def test_model_evaluation_infeasible(self):
        myModel = Model()
        myMAiNGO = MAiNGO(myModel)
        result = myMAiNGO.evaluate_model_at_point([0.5, 0])
        self.assertEqual(result[1],False)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(result[0][0],0.5*0.)
        self.assertEqual(result[0][1],0.5-0.)

    def test_model_evaluation_feasible(self):
        myModel = Model()
        myMAiNGO = MAiNGO(myModel)
        result = myMAiNGO.evaluate_model_at_point([0.5, 2.5])
        self.assertEqual(result[1],True)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(result[0][0],0.5*2.5)
        self.assertEqual(result[0][1],0.5-2.5)

    def test_additional_outputs_evaluation_infeasible(self):
        myModel = Model()
        myMAiNGO = MAiNGO(myModel)
        result = myMAiNGO.evaluate_additional_outputs_at_point([0.5, 0])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("The answer", 42))

    def test_additional_outputs_evaluation_feasible(self):
        myModel = Model()
        myMAiNGO = MAiNGO(myModel)
        result = myMAiNGO.evaluate_additional_outputs_at_point([0.5, 2.5])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("The answer", 42))

    def test_solve_and_getters_after_solve(self):
        myModel = Model()
        myMAiNGO = MAiNGO(myModel)
        myMAiNGO.set_option("loggingDestination", LOGGING_NONE)
        myMAiNGO.set_option("writeResultFile", False)
        status = myMAiNGO.solve()
        self.assertEqual(status, GLOBALLY_OPTIMAL)

        try:
            myMAiNGO.get_cpu_solution_time()
            myMAiNGO.get_final_abs_gap()
            myMAiNGO.get_final_LBD()
            myMAiNGO.get_final_rel_gap()
            myMAiNGO.get_iterations()
            myMAiNGO.get_LBP_count()
            myMAiNGO.get_max_nodes_in_memory()
            myMAiNGO.get_UBP_count()
            myMAiNGO.get_wallclock_solution_time()
        except:
            self.fail("Getter function of MAiNGO raised exception unexpectedly when called after solve")

        self.assertAlmostEqual(myMAiNGO.get_objective_value(), 0, 4)
        solutionPoint = myMAiNGO.get_solution_point()
        self.assertEqual(len(solutionPoint), 2)
        self.assertAlmostEqual(solutionPoint[0], 0)

        evaluationResult = myMAiNGO.evaluate_model_at_solution_point()
        self.assertEqual(len(evaluationResult), 2)
        self.assertEqual(evaluationResult[0], myMAiNGO.get_objective_value())
        self.assertLessEqual(evaluationResult[1], 1e-6)

        additionalOutputs = myMAiNGO.evaluate_additional_outputs_at_solution_point()
        self.assertEqual(len(additionalOutputs), 1)
        self.assertEqual(additionalOutputs[0], ("The answer", 42))



# ----- Testing extension "B&B algorithm with growing datasets"

class ModelSimpleGrowing(MAiNGOmodel):
    def __init__(self):
        MAiNGOmodel.__init__(self)

    def get_variables(self):
        variables = [OptimizationVariable(Bounds(0,5))]
        return variables

    def evaluate(self,vars):
        inputValues = [ 1,1,1]
        outputValues = [1,0.6,0]
        result = EvaluationContainer()
        se = 0
        for i in range(3):
            predictedValue = sqr(vars[0])*inputValues[i]
            se_per_data = sqr(predictedValue - outputValues[i])
            se = se + se_per_data
            result.objData.append(se_per_data)
        result.obj = se
        result.out = [OutputVariable("slope", sqr(vars[0]))]
        return result



class TestMAiNGOgrowingDatasets(unittest.TestCase):
    def test_AUGMENTATION_RULE_enum(self):
        try:
            myRetCode = AUG_RULE_CONST
            myRetCode = AUG_RULE_SCALING
            myRetCode = AUG_RULE_OOS
            myRetCode = AUG_RULE_COMBI
            myRetCode = AUG_RULE_TOL
            myRetCode = AUG_RULE_SCALCST
            myRetCode = AUG_RULE_OOSCST
            myRetCode = AUG_RULE_COMBICST
            myRetCode = AUG_RULE_TOLCST
        except:
            self.fail("Value of enum AUG_RULE not available")

    def test_GROWING_APPROACH_enum(self):
        try:
            myRetCode = GROW_APPR_DETERMINISTIC
            myRetCode = GROW_APPR_SSEHEURISTIC
            myRetCode = GROW_APPR_MSEHEURISTIC
        except:
            self.fail("Value of enum GROWING_APPROACH not available")

    def test_initialize_maingo(self):
        try:
            myMAiNGO = MAiNGO(ModelSimpleGrowing())
        except:
            self.fail("Initialization of MAiNGO raised exception unexpectedly")

# ----- End of tests for growing datasets



if __name__ == '__main__':
    unittest.main()
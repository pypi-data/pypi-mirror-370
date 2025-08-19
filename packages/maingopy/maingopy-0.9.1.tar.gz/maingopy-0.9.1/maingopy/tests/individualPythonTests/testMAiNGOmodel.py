from maingopy import *
import unittest

class CompleteModel(MAiNGOmodel):
    def get_variables(self):
        variables = [OptimizationVariable(Bounds(0,1)),
                     OptimizationVariable(Bounds(2,3))  ]
        return variables
        
    def get_initial_point(self):
        return [0.5,
                2.5]

    def evaluate(self,vars):
        result = EvaluationContainer()
        result.obj = vars[0]*vars[1]
        result.ineq = [0.5 - vars[0],
                       2.5 - vars[1]]
        return result


class ModelMissingVariables(MAiNGOmodel):
    def get_initial_point(self):
        return [0.5,
                2.5]

    def evaluate(self,vars):
        result = EvaluationContainer()
        result.obj = vars[0]*vars[1]
        result.ineq = [0.5 - vars[0],
                       2.5 - vars[1]]
        return result
 

class ModelMissingEvaluate(MAiNGOmodel):
    def get_variables(self):
        variables = [OptimizationVariable(Bounds(0,1)),
                     OptimizationVariable(Bounds(2,3))  ]
        return variables
        
    def get_initial_point(self):
        return [0.5,
                2.5]


class ModelWithoutInitialPoint(MAiNGOmodel):
    def get_variables(self):
        variables = [OptimizationVariable(Bounds(0,1)),
                     OptimizationVariable(Bounds(2,3))  ]
        return variables

    def evaluate(self,vars):
        result = EvaluationContainer()
        result.obj = vars[0]*vars[1]
        result.ineq = [0.5 - vars[0],
                       2.5 - vars[1]]
        return result
        
            
class TestMAiNGOmodel(unittest.TestCase):
    def test_model_missing_variables(self):
        model = ModelMissingVariables()
        with self.assertRaises(Exception):
            model.get_variables()
    
    
    def test_model_missing_evaluate(self):
        model = ModelMissingEvaluate()
        with self.assertRaises(Exception):
            model.evaluate()
    
    
    def test_model_without_initial_point(self):
        model = ModelWithoutInitialPoint()
        initialPoint = model.get_initial_point()
        self.assertEqual(len(initialPoint), 0)


    def test_get_variables(self):
        model = CompleteModel()
        variables = model.get_variables()
        self.assertEqual(len(variables), 2)
        self.assertEqual(variables[0].get_lower_bound(), 0)
        self.assertEqual(variables[0].get_upper_bound(), 1)
        self.assertEqual(variables[1].get_lower_bound(), 2)
        self.assertEqual(variables[1].get_upper_bound(), 3)


    def test_get_initial_point(self):
        model = CompleteModel()
        initialPoint = model.get_initial_point()
        self.assertEqual(len(initialPoint), 2)
        self.assertEqual(initialPoint[0], 0.5)
        self.assertEqual(initialPoint[1], 2.5)
        

if __name__ == '__main__':
    unittest.main()
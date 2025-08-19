from maingopy import *
import unittest

class ModelEmptyVariables(MAiNGOmodel):
    def __init__(self):
        MAiNGOmodel.__init__(self)

    def get_variables(self):
        variables = []
        return variables

    def get_initial_point(self):
        return [0.5,
                2.5]

    def evaluate(self, vars):
        result = EvaluationContainer()
        result.obj = vars[0] * vars[1]
        result.ineq = [0.5 - vars[0],
                       2.5 - vars[1]]
        return result

class TestMAiNGOmodel(unittest.TestCase):
    def test_model_empty_variables(self):
        model = ModelEmptyVariables()
        with self.assertRaises(MAiNGOException):
            myModel = ModelEmptyVariables()
            myMAiNGO = MAiNGO(myModel)

if __name__ == '__main__':
    unittest.main()
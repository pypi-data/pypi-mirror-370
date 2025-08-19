from maingopy import *
import unittest

class TestEvaluationContainer(unittest.TestCase):

    def test_output_variable(self):
        myVar = FFVar()
        myDescription = "foo"
        try:
            myOutVar = OutputVariable(myVar,myDescription)
            myOutVar = OutputVariable(myDescription,myVar)
            myOutVar = OutputVariable((myDescription,myVar))
            myOutVar = OutputVariable((myVar,myDescription))
        except:
            self.fail("Initialization of OutputVariable raised exception unexpectedly")

        self.assertEqual(myOutVar.description, myDescription)
        self.assertEqual(myOutVar.value, myVar)


    def test_model_function(self):
        myVar = FFVar()
        myVarVector = [FFVar(), FFVar()]
        try:
            myModelFunc = ModelFunction()
            myModelFunc = ModelFunction(myVar)
            myModelFunc = ModelFunction(myVarVector)
            myModelFunc = ModelFunction(myVar,"x")
        except:
            self.fail("Initialization of ModelFunction raised exception unexpectedly")

        self.assertEqual(myModelFunc.name, ["x"])
        self.assertEqual(myModelFunc.value, [myVar])

        try:
            myModelFunc.push_back(myVar)
            myModelFunc.push_back(myVar,"x")
            myModelFunc.push_back(myVarVector)
            myModelFunc.push_back(myVarVector,"x")
        except:
            self.fail("Function push_back of ModelFunction raised exception unexpectedly")

        try:
            myModelFunc.clear()
        except:
            self.fail("Function clear of ModelFunction raised exception unexpectedly")


    def test_evaluation_container(self):
        try:
            myContainer = EvaluationContainer()
        except:
            self.fail("Initialization of EvaluationContainer raised exception unexpectedly")

        # Make sure all required members are exposed and the aliases work
        myModelFunc = ModelFunction([FFVar(), FFVar()])
        myContainer.objective = myModelFunc
        self.assertEqual(myContainer.obj, myModelFunc)
        myContainer.equalities = myModelFunc
        self.assertEqual(myContainer.eq, myModelFunc)
        myContainer.inequalities = myModelFunc
        self.assertEqual(myContainer.ineq, myModelFunc)
        myContainer.equalitiesRelaxationOnly = myModelFunc
        self.assertEqual(myContainer.eqRelaxationOnly, myModelFunc)
        self.assertEqual(myContainer.eqRO, myModelFunc)
        myContainer.inequalitiesRelaxationOnly = myModelFunc
        self.assertEqual(myContainer.ineqRelaxationOnly, myModelFunc)
        self.assertEqual(myContainer.ineqRO, myModelFunc)
        myContainer.inequalitiesSquash = myModelFunc
        self.assertEqual(myContainer.ineqSquash, myModelFunc)

        myOutVar = OutputVariable(FFVar(),"Foo")
        myContainer.output = [myOutVar]
        self.assertEqual(myContainer.out, [myOutVar])

        # Test implicit conversion of mc::FFVar and std::vector<mc::FFVar> to ModelFunction
        try:
            myContainer.objective = FFVar()
            myContainer.objective = [FFVar(), FFVar()]
        except:
            self.fail("Implicit conversion to ModelFunction raised exception unexpectedly")


if __name__ == '__main__':
    unittest.main()
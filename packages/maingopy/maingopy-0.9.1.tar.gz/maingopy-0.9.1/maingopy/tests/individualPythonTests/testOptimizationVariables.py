from maingopy import *
import unittest

class TestVariables(unittest.TestCase):


    def test_bound_initialization(self):
        try:
            myBounds = Bounds(-0.5,1.5)
            myBounds = Bounds(1.,0.)
        except:
            self.fail("Initialization of Bounds raised exception unexpectedly")


    def test_VT_enum(self):
        try:
            myVT = VT_CONTINUOUS
            myVT = VT_INTEGER
            myVT = VT_BINARY
        except:
            self.fail("Value of enum VT not avilable")


    def test_optimization_variable_initialization(self):
        myBounds = Bounds(-0.5,1.5)
        try:
            myVar = OptimizationVariable(myBounds, VT_CONTINUOUS, 5, "x")
            myVar = OptimizationVariable(myBounds, VT_CONTINUOUS, 5)
            myVar = OptimizationVariable(myBounds, VT_CONTINUOUS, "x")
            myVar = OptimizationVariable(myBounds, 5, "x")
            myVar = OptimizationVariable(myBounds, 5)
            myVar = OptimizationVariable(myBounds, "x")
            myVar = OptimizationVariable(myBounds)
            myVar = OptimizationVariable(VT_BINARY, 5, "x")
            myVar = OptimizationVariable(VT_BINARY, 5)
            myVar = OptimizationVariable(VT_BINARY, "x")
            myVar = OptimizationVariable(VT_BINARY)
        except:
            self.fail("Initialization of OptimizationVariable raised exception unexpectedly")

        with self.assertRaises(Exception):
            myVar = OptimizationVariable(myBounds, VT_CONTINUOUS, 5.5, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(myBounds, VT_CONTINUOUS, -5, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(myBounds, VT_CONTINUOUS, 5.5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(myBounds, VT_CONTINUOUS, -5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(myBounds, 5.5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(myBounds, -5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_INTEGER, 5, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_INTEGER, 5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_INTEGER, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_INTEGER)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_CONTINUOUS, 5, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_CONTINUOUS, 5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_CONTINUOUS, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_CONTINUOUS)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_BINARY, 5.5, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_BINARY, -5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_INTEGER, 5.5, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_INTEGER, -5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_CONTINUOUS, 5.5, "x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(VT_CONTINUOUS, -5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(5.5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(-5)
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(5,"x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(5.5,"x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable(-5,"x")
        with self.assertRaises(Exception):
            myVar = OptimizationVariable("x")


if __name__ == '__main__':
    unittest.main()
from maingopy import *


#####################################################
# Define a model
class ModelSimpleGrowing(MAiNGOmodel):
    def __init__(self):
        MAiNGOmodel.__init__(self)    
    
    def get_variables(self):
        variables = [OptimizationVariable(Bounds(0,5),VT_CONTINUOUS,"x")]
        return variables

    def evaluate(self, vars):

        x= vars[0]
        inputValues  = [1,1,1]
        outputValues = [1,0.6,0]
        result = EvaluationContainer()
        se = 0
        for i in range(3):
            predictedValue = sqr(x)*inputValues[i]
            se_per_data = sqr(predictedValue - outputValues[i])
            se = se + se_per_data
            result.objData.append(se_per_data)
        result.obj = se
        result.output = [OutputVariable("Optimal slope: ", sqr(x))]
        return result


#####################################################
# Work with the model
myModel = ModelSimpleGrowing()
myMAiNGO = MAiNGO(myModel)

myMAiNGO.set_option("growing_augmentRule", AUG_RULE_CONST)
myMAiNGO.set_option("growing_augmentFreq", 1)

maingoStatus = myMAiNGO.solve() 
# print(maingoStatus)
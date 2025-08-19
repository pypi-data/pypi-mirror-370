from pathlib import Path

from maingopy import *
from maingopy.melonpy import *

folderpath = Path(__file__).parent.resolve() / "modelData"


#%% Define model

class Model(MAiNGOmodel):

    def get_variables(self):
        return [OptimizationVariable(Bounds(0.0, 1.0), VT_CONTINUOUS, "x"),
                OptimizationVariable(Bounds(0.0, 1.0), VT_CONTINUOUS, "y")]

    def evaluate(self,vars):
        
        mf_gp = MulfilGp(folderpath.as_posix())
        
        mean_low = mf_gp.calculate_low_prediction_reduced_space(vars)
        std_low = sqrt(mf_gp.calculate_low_variance_reduced_space(vars))
        mean_high = mf_gp.calculate_high_prediction_reduced_space(vars)
        std_high = sqrt(mf_gp.calculate_high_variance_reduced_space(vars))

        result = EvaluationContainer()
        result.objective = mean_high
        
        result.output = [OutputVariable("mean_low", mean_low),
                         OutputVariable("std_low", std_low),
                         OutputVariable("mean_high", mean_high),
                         OutputVariable("std_high", std_high)]
                         
        return result
    
    
#%% Solve optimization problem

myModel = Model()
myMAiNGO = MAiNGO(myModel)
myMAiNGO.solve()

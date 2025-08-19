from maingopy import *
from maingopy.melonpy import *
from math import pi


#####################################################
# To define a model, we need to spcecialize the MAiNGOmodel class
class Model(MAiNGOmodel):
    def __init__(self):
        MAiNGOmodel.__init__(self)
        # Initialize feedforward neural network and load data from example csv file
        self.testNet = FeedForwardNet()
        self.filePath = ""
        self.netName = "myTestANN"
        self.testNet.load_model(self.filePath, self.netName, CSV)


    # We need to implement the get_variables functions for specifying the optimization varibles
    def get_variables(self):
        variables = [ OptimizationVariable(Bounds(-3,3), VT_CONTINUOUS, "x"),
                      OptimizationVariable(Bounds(-3,3), VT_CONTINUOUS, "y") ]
        return variables


    # We need to implement the evaluate function that computes the values of the objective and constraints from the variables.
    # Note that the variables in the 'vars' argument of this function do correspond to the optimization variables defined in the get_variables function.
    # However, they are different objects for technical reasons. The only mapping we have between them is the position in the list.
    # The results of the evaluation (i.e., objective and constraint values) need to be return in an EvaluationContainer
    def evaluate(self, vars):
        x = vars[0]
        y = vars[1]
        
        # Inputs to the ANN are the variables x and y
        annInputs = [x, y]
        
        # Evaluate the network (in reduced-space)
        # This returns a list, because the output of the network may be multidimensional
        annOutputs = self.testNet.calculate_prediction_reduced_space(annInputs)

        # Set the ANN output (only 1 in this case) as objective to be minimized
        result = EvaluationContainer()
        result.objective = annOutputs[0]

        return result


#####################################################
# To work with the problem, we first create an instance of the model.
myModel = Model()

# We then create an instance of MAiNGO, the solver, and hand it the model.
myMAiNGO = MAiNGO(myModel)

# Next, adjust settings as desired
# We can have MAiNGO read a settings file:
fileName = ""
myMAiNGO.read_settings(fileName) # If fileName is empty, MAiNGO will attempt to open MAiNGOSettings.txt
# We can also use the set_option function directly:
# myMAiNGO.set_option("maxTime", 100) # set CPU time limit to 100s
# myMAiNGO.set_option("loggingDestination", LOGGING_FILE) # write log to file only, not screen

# We can also customize file names for written output if desired
# myMAiNGO.set_log_file_name("my_log_file.log")
# myMAiNGO.set_option("writeJson", True)
# myMAiNGO.set_json_file_name("my_json_file.json")
# myMAiNGO.set_option("writeCsv", True)
# myMAiNGO.set_iterations_csv_file_name("iterations.csv")
# myMAiNGO.set_solution_and_statistics_csv_file_name("solution_and_statistics.csv")

# We can have MAiNGO write the current model to a file in a given modeling language.
# (As an alternative, this could also be done within the solve function of MAiNGO
# through the settings modelWritingLanguage, but with less options for customization)
# myMAiNGO.write_model_to_file_in_other_language(writingLanguage=LANG_GAMS, fileName="my_problem_file_MAiNGO.gms", solverName="SCIP", writeRelaxationOnly=False)

# Finally, we call the solve routine to solve the problem.
maingoStatus = myMAiNGO.solve()
# print(maingoStatus)
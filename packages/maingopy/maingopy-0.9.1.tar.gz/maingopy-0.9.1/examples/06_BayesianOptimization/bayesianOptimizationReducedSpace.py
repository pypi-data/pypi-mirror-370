from maingopy import *
from maingopy.melonpy import *
from math import pi


#####################################################
# To define a model, we need to specialize the MAiNGOmodel class
class Model(MAiNGOmodel):
    def __init__(self):
        MAiNGOmodel.__init__(self)
        # Initialize Gaussian Process and load data from example json file
        self.gp = GaussianProcess()
        self.filePath = ""
        self.netName = "testGP"
        self.gp.load_model(self.filePath, self.netName, JSON)


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
        
        # Inputs to the GP are the variables x and y
        gpInputs = [x, y]
        
        # Evaluate GaussianProcess (in reduced-space)
        mu = self.gp.calculate_prediction_reduced_space(gpInputs) # prediction of GP
        variance = self.gp.calculate_variance_reduced_space(gpInputs) # variance
        sigma = sqrt(variance) # standard deviation

        # Compute acquisition functions to be maximized for Bayesian optimiation
        # First, auxiliaries: read out current minimum of training data outputs as target, and fixed kappa for lower confidence bound
        fmin = self.gp.get_minimum_of_training_data_outputs()
        kappa = 2
        # Now, compute actual (most common) acquisition functions
        expectedImprovement = af_ei(mu, sigma, fmin)
        probabilityOfImprovement = af_pi(mu, sigma, fmin)
        lowerConfidenceBound = af_lcb(mu, sigma, kappa)
        

        # Set the desired acquisition function as objective function
        # Recall that MAiNGO always minimizes, so need to put "-" in front of objective to maximize!
        result = EvaluationContainer()
        result.objective = -expectedImprovement
        # result.objective = -probabilityOfImprovement
        # result.objective = -lowerConfidenceBound

        result.output = [ OutputVariable("mu", mu),
                          OutputVariable("sigma", sigma),
                          OutputVariable("fmin", fmin),
                          OutputVariable("expectedImprovement", expectedImprovement),
                          OutputVariable("probability of improvement", probabilityOfImprovement),
                          OutputVariable("lower confidence bound", lowerConfidenceBound) ]

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
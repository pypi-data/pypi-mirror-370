from maingopy import *
from math import pi
#only for the parallel version
if HAVE_MAiNGO_MPI():
    from mpi4py import MPI
    MPI.COMM_WORLD
    #mute multiple outputs
    buffer = muteWorker()

# Auxiliary class, just to highlight we can use other classes, functions, etc. in our models
class SomeExternalClass():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        
    def functionOne(self, x, y):
        return -self.p1 * sqrt( (sqr(x) + sqr(y))/2 )
        
    def functionTwo(self, x, y):
        return ( cos(self.p2*x) + cos(self.p2*y) ) / 2


#####################################################
# To define a model, we need to spcecialize the MAiNGOmodel class
class Model(MAiNGOmodel):
    def __init__(self):
        MAiNGOmodel.__init__(self) # Should be there for technical reasons
        self.a = 20
        self.ext = SomeExternalClass(0.2, pi)
    
    
    # We need to implement the get_variables functions for specifying the optimization variables
    def get_variables(self):
        # We need to return a list of OptimizationVariable objects.
        # To define an optimization variable, we typically need to specify bounds, and optionally a variable type, a branching priority, and a name 
        #
        # Variable bounds:
        #  Every optimization variable (except for binary variables, cf. below) requires finite lower and upper bounds.
        #
        # Variable type:
        #  There are three variable types in MAiNGO. VT_CONTINUOUS variables, VT_BINARY variables, and VT_INTEGER variables.
        #  Double type bounds for binaries and integers will be rounded up for lower bounds and rounded down for upper bounds.
        #
        # Branching priority:
        #  A branching priority 'n' means that we will branch log_2(n+1) times more often on that specific variable, n will be rounded down to the next integer meaning that a BP of 1.5 equals 1
        #  If you want to branch less on a specific variable just increase the branching priority of all other variables
        #  A branching priority of <1 means that MAiNGO will never branch on this specific variable. This may lead to non-convergence of the B&B algorithm
        #
        # Variable name:
        #  The name has to be of string type. All ASCII characters are allowed and variables are allowed to have the same name.
        #  MAiNGO outputs the variables in the same order as they are set in the variables list within this function.
        #
        variables = [OptimizationVariable(VT_BINARY, "x"),                     # A binary variable automatically has the bounds [0,1] - this is the only case where bounds are optional
                     OptimizationVariable(Bounds(-2,2), VT_CONTINUOUS, "y")  ] # The VT_CONTINUOUS specifies that this is a real variable. It could be omitted, since this is the default
        return variables

    # Optional: we can implement a function for specifying an initial guess for our optimization variables
    # If provided, MAiNGO will use this point for the first local search during pre-processing
    def get_initial_point(self):
        # If you choose to provide an initial point, you have to make sure that the size of the initialPoint equals the size of
        # the variables list returned by get_variables. Otherwise, MAiNGO will throw an exception.
        # The value of an initial point variable does not have to fit the type of the variable, e.g., it is allowed to set a double type value as an initial point for a binary variable
        initialPoint = [0, 1]
        return initialPoint


    # We need to implement the evaluate function that computes the values of the objective and constraints from the variables.
    # Note that the variables in the 'vars' argument of this function do correspond to the optimization variables defined in the get_variables function.
    # However, they are different objects for technical reasons. The only mapping we have between them is the position in the list.
    # The results of the evaluation (i.e., objective and constraint values) need to be returned in an EvaluationContainer
    def evaluate(self, vars):
        # Create copies of the variables with nicer names
        x = vars[0]
        y = vars[1]
        
        # Here, we can do (almost, see documentation) any kind of intermediate calculation.
        # Any variables defined here are intermediates that are not optimization variables.
        temp1 = self.ext.functionOne(x, y)
        temp2 = self.ext.functionTwo(x, y)
        
        # The objective and constraints are returned in an EvaluationContainer
        result = EvaluationContainer()
        
        # Example objective: the Ackley function
        result.objective = -self.a * exp(temp1) - exp(temp2) + self.a + exp(1)
        
        # Inequalities: need to return a list of constraint residuals g(x) for constraints of form g(x)<=0
        result.ineq = [x - 1] # This means: x-1 <= 0
        
        # Equalities: similarly, need to return a list of residuals h(x) for h(x)=0
        result.eq = [x**2 + y**2 - 1] # Circle equality with radius 1
       
       
        # Relaxation-only inequalities and equalities are used for lower bounding only.
        # None of the relaxation only (in)equalities are passed to the upper bounding solver.
        # Only for the best feasible point (if any) found during pre-processing and for the
        # final solution point, MAiNGO checks whether they satisfy relaxation-only
        # (in)equalities and warns the user if they do not.
        # IMPORTANT: You thus need to make sure yourself that any relaxation-only constraints
        #            are redundant with the "regular" constraints.
        #
        # Relaxation-only inequalities (<=0):
        # result.ineqRelaxationOnly = [y - 1];
        #
        # Relaxation-only equalities (=0):
        # result.eqRelaxationOnly = [y + x - 1]
       
        # Additional output can be used to access intermediate variables after a problem has been solved.
        result.output = [OutputVariable("Result of temp1: ", temp1)]

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

#only for the parallel version
if HAVE_MAiNGO_MPI():
    #wokers must be unmuted before solving model
    unmuteWorker(buffer)

# We can have MAiNGO write the current model to a file in a given modeling language.
# (As an alternative, this could also be done within the solve function of MAiNGO
# through the settings modelWritingLanguage, but with less options for customization)
# myMAiNGO.write_model_to_file_in_other_language(writingLanguage=LANG_GAMS, fileName="my_problem_file_MAiNGO.gms", solverName="SCIP", writeRelaxationOnly=False)
 
# Finally, we call the solve routine to solve the problem.
maingoStatus = myMAiNGO.solve() 
# print(maingoStatus)
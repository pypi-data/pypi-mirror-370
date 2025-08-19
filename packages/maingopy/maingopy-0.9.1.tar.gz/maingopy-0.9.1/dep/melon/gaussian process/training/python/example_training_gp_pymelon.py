##
#  @file example_training_of_ANN_with_pruning.py
#
#  @brief Training of artificial neural network in Keras with pruning and export to file that is readable by MeLOn.
#
# ==============================================================================\n
#   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
# ==============================================================================\n
#
#  @author Artur M. Schweidtmann, Linus Netze, and Alexander Mitsos
#  @date 18. February 2021
##

import utils
import numpy as np
import torch
import gpytorch
from pyDOE import lhs
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import time

from pymelon import *
from pymaingo import *

############################ SET PARAMETERS ############################ 

# Set parameters for generation of training data 
DX = 2 #input dims of data/GP
DY = 1
PROBLEM_LB = np.array([-3,-3]) #lower bound of inputs
PROBLEM_UB = np.array([3,3]) #upper bounds of inputs
N_TRAINING_POINTS = 20
test_func = lambda x: (
    3*(1-x[:,0])**2*np.exp(-(x[:,0]**2) - (x[:,1]+1)**2)
    - 10*(x[:,0]/5 - x[:,0]**3 - x[:,1]**5)*np.exp(-x[:,0]**2-x[:,1]**2)
    - 1/3*np.exp(-(x[:,0]+1)**2 - x[:,1]**2)
    )

# Set prameter for model
MATERN = 5

# Set parameter for training
N_TRAINING_ITER = 250 
#.settings.fast_computations(False, False, False)
#gpytorch.settings.fast_pred_samples(False)
#gpytorch.settings.lazily_evaluate_kernels(False)
#gpytorch.settings.cholesky_jitter(1e-4)

############################ GENERATE DATA ############################ 

# Generate sampling points using latin hypercube sampling
X = lhs(DX, samples=N_TRAINING_POINTS)

# Scale to bounds (lhs only yields values from 0 to 1)
X = PROBLEM_LB + (PROBLEM_UB - PROBLEM_LB)*X

y = test_func(X)

############################  SCALE DATA ############################ 

scaler = dict()

# scale inputs to [0 , 1]
scaler['input'] = MinMaxScaler(feature_range=(0,1 )) 
X_scaled = scaler['input'].fit_transform(X)
X_train = torch.from_numpy(X_scaled)

# scale outputs to zero mean and unit variance
scaler['output'] = StandardScaler()
y_scaled = scaler['output'].fit_transform(y.reshape(-1, 1)).squeeze()
y_train = torch.from_numpy(y_scaled)


############################  Define MODEL ############################ 

# A basic exact GP regression model (xompare gpytorch documentation: https://docs.gpytorch.ai/en/stable/examples/01_Exact_GPs/Simple_GP_Regression.html)
# Example from documentaion is extended by using a Matern instead of a radial basis function kernel.

class ExactGPModel(gpytorch.models.ExactGP): #definition of class
    def __init__(self, train_x, train_y, likelihood, matern): # def creates objects needed for forward
        super(ExactGPModel, self).__init__(train_x, train_y, likelihood)
        #super() returns a proxy class which inherits gpytorch.models.ExactGP, its parent
        #in short, we create a subclass by extending the parent
        self.mean_module = gpytorch.means.ConstantMean() # constant mean
        self.covar_module = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.MaternKernel(nu=matern/2, ard_num_dims = 2)
            )
        #self.covar_module = gpytorch.kernels.MaternKernel(nu=matern/2, ard_num_dims = 2) #matern class
        #we have flexible options for mean and covar module definition (i.e. with/without white noise, here or below
        
    def forward(self, x): #computes 
        mean_x = self.mean_module(x) #prior mean
        covar_x = self.covar_module(x)# + self.white_noise_module(x) #prior covariance matrix from kernels
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x) #multivar normal

# initialize likelihood and model
likelihood = gpytorch.likelihoods.GaussianLikelihood()
model = ExactGPModel(X_train, y_train, likelihood, matern=MATERN)

############################  TRAINING ############################ 

training_time = time.time()

# Find optimal model hyperparameters
model.train()
likelihood.train()

# Use the adam optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=0.1)  # Includes GaussianLikelihood parameters

# "Loss" for GPs - the marginal log likelihood
mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)

for i in range(N_TRAINING_ITER):
    # Zero gradients from previous iteration
    optimizer.zero_grad()
    # Output from model
    output = model(*model.train_inputs)
    # Calc loss and backprop gradients
    loss = -mll(output, model.train_targets)
    loss.backward()
    print('Iter %d/%d \n\tLoss:\t%s\n\tlengthscale:\t%s\n\tnoise:\t%s' % (
        i + 1, N_TRAINING_ITER, loss,
        model.covar_module.base_kernel.lengthscale,
        model.likelihood.noise
    ))
    optimizer.step()

training_time = training_time - time.time()

############################  GET MODEL OBJECT ############################ 
gp_model = utils.generate_melon_gp_object(model, X_train, y_train, MATERN, scaler)
utils.save_model_to_json(r"C:\Users\Linus\Documents\HiWi\SVT\MeLOn\myMeLOn\build", "testGP.json", model, X_train, y_train, MATERN, scaler)

############################  DEFINE OPTIMIZATION PROBLEM ############################ 

class Model(MAiNGOmodel):

    #####################################
    # This function defines the optimization variables in the problem. In the above (MI)NLP, this corresponds to the x \in X part.
    # A variable typically needs bounds to define the host set X and can optionally have a variable type (VT_CONTINUOUS, VT_INTEGER, VT_BINARY)
    # and a name (and a branching priority, which is an algorithmic parameter and usually not relevant).
    # Note that the name is used *only* in the screen or log output of MAiNGO. In particular, it can not be used for modelling...
    def get_variables(self):
        return [OptimizationVariable(Bounds(-3, 3), VT_CONTINUOUS, "x"),
                OptimizationVariable(Bounds(-3, 3), VT_CONTINUOUS, "y")  ]

    #####################################
    # This function essentially needs to implement the functions f(x), h(x), and g(x) in the aove (MI)NLP.
    # Unfortunaley, right now we cannot use the variable objects defined in the get_variables function above
    # directly for modeling (nor other variable types defined elsewhere) for technical reasons.
    # Instead, the "vars" list that MAiNGO hands to this evaluate function contains the same number of elements as the
    # list that we returned in the get_variables function, and it is only through their position in this list that we can
    # map the variables used herein to the ones we defined in get_variables.
    def evaluate(self,vars):
        
        # First read in GP parameters from file "fileName" at "filePath"
        gp = GaussianProcess()
        gp.load_model(gp_model)
        
        # Evaluate the Gaussian process
        # Input of the GP are the optimiation variables "vars", as defined in the "get_variables" function (cf. discussion above)
        mu = gp.calculate_prediction_reduced_space(vars)
        variance = gp.calculate_variance_reduced_space(vars)
        sigma = sqrt(variance)

        result = EvaluationContainer()
        result.objective = mu;
        
        # Optionally, we can define OutputVariables. These are things that we would like to have
        # evaluated at the optimal solution but that do not form part of the (MI)NLP itself.
        result.output = [ OutputVariable("mu ", mu),
                          OutputVariable("sigma: ", sigma) ]
        return result


############################  SOLVE OPTIMIZATION PROBLEM ############################ 

# To actually solve the problem, we instantiate a model, hand it to a MAiNGO instance.
myModel = Model()
myMAiNGO = MAiNGO(myModel)

# There are lots of settings regarding algorithmic details, subsolvers, and output.
# E.g., to disable screen output:
# myMAiNGO.set_option("outstreamVerbosity", 0)

# Actually solve the problem
myMAiNGO.solve()

# Query results
optimalObjective = myMAiNGO.get_objective_value()
print("\nOptimal objective value: {}".format(optimalObjective))
optimalSolutionPoint = myMAiNGO.get_solution_point()
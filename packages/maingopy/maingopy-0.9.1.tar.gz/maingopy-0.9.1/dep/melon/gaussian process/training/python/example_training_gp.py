##
#  @file example_training_gp.py
#
#  @brief Training of gaussian process in GPyTorch and export to file that is readable by MeLOn.
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

# Set output location
FILE_PATH = "./output"
FILE_NAME = "testGP.json"


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
        # self.mean_module = gpytorch.means.ZeroMean() # zero mean
        if matern == 999:
            self.covar_module = gpytorch.kernels.ScaleKernel(
                gpytorch.kernels.RBFKernel(ard_num_dims = DX)
                )
        else:
            self.covar_module = gpytorch.kernels.ScaleKernel(
                gpytorch.kernels.MaternKernel(nu=matern/2, ard_num_dims = DX)
                )
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

############################  SAVE MODEL IN JSON FILE ############################ 
utils.save_model_to_json(FILE_PATH, FILE_NAME, model, likelihood, X_train, y_train, MATERN, scaler)


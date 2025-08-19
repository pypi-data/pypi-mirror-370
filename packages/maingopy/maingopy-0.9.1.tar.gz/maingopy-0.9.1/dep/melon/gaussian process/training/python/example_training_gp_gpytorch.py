##
#  @file example_training_gp_gpytorch.py
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

from pathlib import Path
import utils
import numpy as np
import torch
import gpytorch
from scipy.stats import qmc
from sklearn.preprocessing import MinMaxScaler, StandardScaler

try:
    import melonpy
    MELONPY_IMPORT = True
except ModuleNotFoundError:
    MELONPY_IMPORT = False
    
    
#%% SET PARAMETERS

# Set parameters for generation of training data 
DIM_X = 2 # input dimension
X_LB = np.array([-3,-3]) # lower bound of inputs
X_UB = np.array([3,3]) # upper bounds of inputs
N_TRAINING_POINTS = 32
TEST_FUNC = lambda X: (
    3 * (1 - X[:,0])**2 * np.exp(-(X[:,0]**2) - (X[:,1] + 1)**2) -
    10 * (X[:,0]/5 - X[:,0]**3 - X[:,1]**5) * np.exp(-X[:,0]**2 - X[:,1]**2) -
    np.exp(-(X[:,0] + 1)**2 - X[:,1]**2) / 3)
SEED = 0

# Set kernel
MATERN = 5

# Set if to use fixed zero mean
ZERO_MEAN = False

# Set parameter for training
N_TRAINING_ITER = 250

# Set output location
FILEPATH = Path(__file__).parent.resolve() / "testGpGpytorch.json"

# Set test input
X_TEST = np.array([[1.5, -2]])


#%% GENERATE DATA

# Generate sampling points using latin hypercube sampling
sampler = qmc.LatinHypercube(d=DIM_X, rng=np.random.default_rng(SEED))
X = sampler.random(n=N_TRAINING_POINTS)

# Scale to bounds (sampler only yields values from 0 to 1)
X = X_LB + (X_UB - X_LB)*X

y = TEST_FUNC(X)


#%% SCALE DATA

scalers = dict()

# scale inputs to [0 , 1]
scalers['input'] = MinMaxScaler(feature_range=(0,1)) 
X_scaled = scalers['input'].fit_transform(X)
X_train = torch.from_numpy(X_scaled)

# scale outputs to zero mean and unit variance
scalers['output'] = StandardScaler()
y_scaled = scalers['output'].fit_transform(y.reshape(-1, 1)).squeeze()
y_train = torch.from_numpy(y_scaled)


#%% DEFINE MODEL

# A basic exact GP regression model
# Compare gpytorch documentation: https://docs.gpytorch.ai/en/stable/examples/01_Exact_GPs/Simple_GP_Regression.html
# Example from documentaion is extended by using a Matern instead of a radial basis function kernel.

class ExactGPModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood, matern):
        super(ExactGPModel, self).__init__(train_x, train_y, likelihood)
        
        if ZERO_MEAN:
            self.mean_module = gpytorch.means.ZeroMean()
        else:
            self.mean_module = gpytorch.means.ConstantMean() # constant mean

        if matern == 999:
            self.covar_module = \
                gpytorch.kernels.ScaleKernel(gpytorch.kernels.RBFKernel(ard_num_dims = DIM_X))
        else:
            self.covar_module = \
                gpytorch.kernels.ScaleKernel(gpytorch.kernels.MaternKernel(nu=matern/2, ard_num_dims = DIM_X))
        
    def forward(self, x): 
        mean_x = self.mean_module(x) # prior mean
        covar_x = self.covar_module(x) # prior covariance function from kernels
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

# initialize likelihood and model
likelihood_gpytorch = gpytorch.likelihoods.GaussianLikelihood()
model_gpytorch = ExactGPModel(X_train, y_train, likelihood_gpytorch, matern=MATERN)


#%% TRAINING

# Find optimal model hyperparameters
model_gpytorch.train()
likelihood_gpytorch.train()

# Use the adam optimizer
optimizer = torch.optim.Adam(model_gpytorch.parameters(), lr=0.1)  # Includes GaussianLikelihood parameters

# "Loss" for GPs - the marginal log likelihood
mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood_gpytorch, model_gpytorch)

for i in range(N_TRAINING_ITER):
    # Zero gradients from previous iteration
    optimizer.zero_grad()
    # Output from model
    output = model_gpytorch(*model_gpytorch.train_inputs)
    # Calc loss and backprop gradients
    loss = -mll(output, model_gpytorch.train_targets)
    loss.backward()
    print('Iter %d/%d \n\tLoss:\t%s\n\tlengthscale:\t%s\n\tnoise:\t%s' % (
        i + 1, N_TRAINING_ITER, loss,
        model_gpytorch.covar_module.base_kernel.lengthscale,
        model_gpytorch.likelihood.noise
    ))
    optimizer.step()


#%% SAVE MODEL IN JSON FILE

utils.save_gpytorch_model_to_json(
    FILEPATH, model_gpytorch, likelihood_gpytorch, X_train, y_train, MATERN, scalers)


#%% TEST

if MELONPY_IMPORT:

    # GPyTorch predictions

    model_gpytorch.eval()
    likelihood_gpytorch.eval()

    x_test_scaled = scalers['input'].transform(X_TEST)

    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        preds_gpytorch = model_gpytorch(torch.from_numpy(x_test_scaled))

    mean_gpytorch_scaled = preds_gpytorch.mean.numpy()
    var_gpytorch_scaled = preds_gpytorch.variance.numpy()

    mean_gpytorch = scalers['output'].inverse_transform(mean_gpytorch_scaled[np.newaxis, :])
    var_gpytorch = var_gpytorch_scaled * scalers['output'].var_.item()

    # MeLOn predictions

    model_melon = melonpy.GaussianProcessDouble(FILEPATH.parent.as_posix(), FILEPATH.name)
    mean_melon = model_melon.calculate_prediction_reduced_space(X_TEST.ravel())
    var_melon = model_melon.calculate_variance_reduced_space(X_TEST.ravel())

    # Printing

    print("\nTEST")
    print(f"Input: {X_TEST.ravel()}")
    print(f"GPyTorch mean: {mean_gpytorch.item()}")
    print(f"MeLOn mean: {mean_melon}")
    print(f"GPyTorch var: {var_gpytorch.item()}")
    print(f"MeLOn var: {var_melon}")

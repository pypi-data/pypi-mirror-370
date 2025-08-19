##
#  @file example_training_gp_gpy.py
#
#  @brief Training of gaussian process in GPy and export to file that is readable by MeLOn.
#
# ==============================================================================\n
#   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
# ==============================================================================\n
#
#  @author Luis Kutschat
#  @date 31. January 2025
##

from pathlib import Path
import utils
import numpy as np
import GPy
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

# Set if to use fixed zero noise
ZERO_NOISE = False

# Set number of optimization restarts
N_OPTIMIZATION_RESTARTS = 10

# Set output location
FILEPATH = Path(__file__).parent.resolve() / "testGpGpy.json"

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

# scale inputs to [0, 1]
scalers['input'] = MinMaxScaler(feature_range=(0,1)) 
X_train = scalers['input'].fit_transform(X)

# scale outputs to zero mean and unit variance
scalers['output'] = StandardScaler()
y_train = scalers['output'].fit_transform(y.reshape(-1, 1))


#%% DEFINE MODEL

mean_func = GPy.mappings.Constant(DIM_X, 1)
if ZERO_MEAN:
    mean_func.fix(0.0)
    
kernel_type = utils.int_to_kernel_type(MATERN)
kernel = kernel_type(DIM_X, ARD=True)

model_gpy = GPy.models.GPRegression(X_train, y_train, kernel, mean_function=mean_func)

if ZERO_NOISE:
    model_gpy.likelihood.fix(0.0)
    
    
#%% TRAINING

np.random.seed(SEED)    
model_gpy.optimize_restarts(N_OPTIMIZATION_RESTARTS, verbose=True, robust=True)


#%% SAVE MODEL IN JSON FILE

utils.save_gpy_model_to_json(FILEPATH, model_gpy, scalers)

#%% TEST

if MELONPY_IMPORT:

    # GPyTorch predictions
    
    x_test_scaled = scalers['input'].transform(X_TEST)
    
    mean_gpy_scaled, var_gpy_scaled = model_gpy.predict(x_test_scaled, include_likelihood=False)

    mean_gpy = scalers['output'].inverse_transform(mean_gpy_scaled)
    var_gpy = var_gpy_scaled * scalers['output'].var_.item()

    # MeLOn predictions

    model_melon = melonpy.GaussianProcessDouble(FILEPATH.parent.as_posix(), FILEPATH.name)
    mean_melon = model_melon.calculate_prediction_reduced_space(X_TEST.ravel())
    var_melon = model_melon.calculate_variance_reduced_space(X_TEST.ravel())

    # Printing

    print("\nTEST")
    print(f"Input: {X_TEST.ravel()}")
    print(f"GPy mean: {mean_gpy.item()}")
    print(f"MeLOn mean: {mean_melon}")
    print(f"GPy var: {var_gpy.item()}")
    print(f"MeLOn var: {var_melon}")

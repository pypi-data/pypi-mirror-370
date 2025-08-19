##
#  @file example_training_mulfilgp.py
#
#  @brief Training of a multifidelity Gaussian process in emukit and export to files that are readable by MeLOn.
#
# ==============================================================================\n
#   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
# ==============================================================================\n
#
#  @author Luis Kutschat
#  @date 21.01.2025
##

from pathlib import Path
import numpy as np
from scipy.stats import qmc
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from emukit.model_wrappers.gpy_model_wrappers import GPyMultiOutputWrapper
from emukit.multi_fidelity.convert_lists_to_array import convert_xy_lists_to_arrays
from emukit.multi_fidelity.models import GPyLinearMultiFidelityModel
from emukit.multi_fidelity.kernels import LinearMultiFidelityKernel

import utils
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
TEST_FUNC_LOW = lambda X: (
    3 * (1 - X[:,0])**2 * np.exp(-(X[:,0]**2) - (X[:,1] + 1)**2) -
    10 * (X[:,0]/5 - X[:,0]**3 - X[:,1]**5) * np.exp(-X[:,0]**2 - X[:,1]**2) -
    np.exp(-(X[:,0] + 1)**2 - X[:,1]**2) / 3)
TEST_FUNC_HIGH = lambda X: 1.1*TEST_FUNC_LOW(X) + 1.1
SEED = 0

# Set kernels
MATERN_LOW = 5
MATERN_HIGH = 1

# Set number of optimization restarts
N_OPTIMIZATION_RESTARTS = 10

# Set output location
FOLDERPATH = Path(__file__).parent.resolve() / "testMulfilGp"

# Set test input
X_TEST = np.array([[1.5, -2]])


#%% GENERATE DATA

# Generate sampling points using latin hypercube sampling
sampler = qmc.LatinHypercube(d=DIM_X, rng=np.random.default_rng(SEED))
X_low = sampler.random(n=N_TRAINING_POINTS)

# Scale to bounds (sampler only yields values from 0 to 1)
X_low = X_LB + (X_UB - X_LB)*X_low

y_low = TEST_FUNC_LOW(X_low)[:, np.newaxis]

# Use the first half of low inputs for high fidelity learning
X_high = X_low[:N_TRAINING_POINTS//2, :]
y_high = TEST_FUNC_HIGH(X_high)[:, np.newaxis]

# Prepare inputs and outputs for emukit
X_train, y_train = convert_xy_lists_to_arrays([X_low, X_high], [y_low, y_high])


#%% DEFINE MODEL

# Contrary to GPs, only zero prior mean and zero noise are supported
# Contrary to GPs, the emukit model is trained with non scaled inputs and outputs
    
kernel_type_low = utils.int_to_kernel_type(MATERN_LOW)
kernel_low = kernel_type_low(DIM_X, ARD=True)
kernel_type_high = utils.int_to_kernel_type(MATERN_HIGH)
kernel_high = kernel_type_high(DIM_X, ARD=True)
mf_kernel = LinearMultiFidelityKernel([kernel_low, kernel_high])

model_gpy = GPyLinearMultiFidelityModel(X_train, y_train, mf_kernel, 2)
model_gpy.likelihood.likelihoods_list[0].fix(0.0)
model_gpy.likelihood.likelihoods_list[1].fix(0.0)

model_emukit = GPyMultiOutputWrapper(model_gpy, 2, N_OPTIMIZATION_RESTARTS)


#%% TRAINING

np.random.seed(SEED)
model_emukit.optimize()


#%% CREATE SCALERS

scalers = dict()

scalers["input"] = MinMaxScaler(feature_range=(0,1))
scalers["input"].fit(X_train[:, :-1])

scalers["output_low"] = StandardScaler()
scalers["output_low"].fit(y_low)

scalers["output_high"] = StandardScaler()
scalers["output_high"].fit(y_high)


#%% SAVE MODEL IN JSON FILES

utils.save_emukit_model_to_json(FOLDERPATH, model_emukit, scalers)


#%% TEST

if MELONPY_IMPORT:

    # emukit predictions
    
    x_test_low = np.concatenate((X_TEST, [[0]]), 1)
    mean_emukit_low, var_emukit_low = model_emukit.predict(x_test_low)
    
    x_test_high = np.concatenate((X_TEST, [[1]]), 1)
    mean_emukit_high, var_emukit_high = model_emukit.predict(x_test_high)

    # MeLOn predictions

    model_melon = melonpy.MulfilGpDouble(FOLDERPATH.parent.as_posix(), FOLDERPATH.name)
    
    mean_melon_low = model_melon.calculate_low_prediction_reduced_space(X_TEST.ravel())
    var_melon_low = model_melon.calculate_low_variance_reduced_space(X_TEST.ravel())
    
    mean_melon_high = model_melon.calculate_high_prediction_reduced_space(X_TEST.ravel())
    var_melon_high = model_melon.calculate_high_variance_reduced_space(X_TEST.ravel())

    # Printing

    print("\nTEST")
    print(f"Input: {X_TEST.ravel()}")
    
    print(f"Emukit low mean: {mean_emukit_low.item()}")
    print(f"MeLOn low mean: {mean_melon_low}\n")
    
    print(f"Emukit low var: {var_emukit_low.item()}")
    print(f"MeLOn low var: {var_melon_low}\n")
    
    print(f"Emukit high mean: {mean_emukit_high.item()}")
    print(f"MeLOn high mean: {mean_melon_high}\n")
    
    print(f"Emukit high var: {var_emukit_high.item()}")
    print(f"MeLOn high var: {var_melon_high}\n")


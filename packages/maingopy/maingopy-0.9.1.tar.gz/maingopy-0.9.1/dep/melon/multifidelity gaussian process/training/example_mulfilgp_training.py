##
#  @file example_mulfilgp_training.py
#
#  @brief Training of a multifidelity GP in emukit and export to .json files that are readable by MeLOn
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
import GPy
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from emukit.model_wrappers.gpy_model_wrappers import GPyMultiOutputWrapper
from emukit.multi_fidelity.convert_lists_to_array import convert_xy_lists_to_arrays
from emukit.multi_fidelity.models import GPyLinearMultiFidelityModel
from emukit.multi_fidelity.kernels import LinearMultiFidelityKernel
import emukit.test_functions

import utils

np.random.seed(0)


#%% User configuration

folderpath = Path(__file__).parent.resolve() / "modelData"
n_training_inputs = 32
input_dim = 2
n_optimization_restarts = 10
low_fidelity_fun = lambda X: np.linalg.norm(X, axis=1)[:, np.newaxis] # emukit.test_functions.forrester.forrester_low(np.mean(X, 1)[:, np.newaxis])
high_fidelity_fun = lambda X: 1.1*low_fidelity_fun(X) + 0.1 # emukit.test_functions.forrester.forrester(np.mean(X, 1)[:, np.newaxis]) 


#%% Train multifidelity GP and save its data to .json files

# Create training data
    
X_low = np.random.rand(n_training_inputs, input_dim)
X_high = X_low[:n_training_inputs//2, :]
y_low = low_fidelity_fun(X_low)
y_high = high_fidelity_fun(X_high)

X, y = convert_xy_lists_to_arrays([X_low, X_high], [y_low, y_high])

# Create emukit model

kernel_low = GPy.kern.OU(input_dim, ARD = True)
kernel_high = GPy.kern.Matern32(input_dim, ARD = True)
mf_kernel = LinearMultiFidelityKernel([kernel_low, kernel_high])

mf_model_gpy = GPyLinearMultiFidelityModel(X, y, mf_kernel, 2)
mf_model_gpy.likelihood.likelihoods_list[0].fix(0.0)
mf_model_gpy.likelihood.likelihoods_list[1].fix(0.0)

mf_model_emukit = GPyMultiOutputWrapper(mf_model_gpy, 2, n_optimization_restarts)
mf_model_emukit.optimize()

# Create scalers

input_scaler = MinMaxScaler()
input_scaler.fit(np.concatenate((X_low, X_high), 0))
output_scaler_low = StandardScaler()
output_scaler_low.fit(y_low)
output_scaler_high = StandardScaler()
output_scaler_high.fit(y_high)

# Save data to .json files

utils.save_data_to_json(folderpath, mf_model_emukit, input_scaler, (output_scaler_low, output_scaler_high))

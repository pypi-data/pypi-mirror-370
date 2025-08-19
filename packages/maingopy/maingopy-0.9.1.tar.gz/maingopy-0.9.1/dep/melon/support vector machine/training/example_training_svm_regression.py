##
#  @file example_training.py
#
#  @brief Training of suppot vector regression model and export to file that is readable by MeLOn.
#
# ==============================================================================\n
#   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
# ==============================================================================\n
#
#  @author Linus Netze, Artur M. Schweidtmann and Alexander Mitsos
#  @date 28. March 2020
##

from pathlib import Path
import utils
from scipy.stats import qmc
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np

try:
    import melonpy
    MELONPY_IMPORT = True
except ModuleNotFoundError:
    MELONPY_IMPORT = False


#%% SET PARAMETERS

# Set parameters for generation of training data
DIM_X = 2
X_LB = np.array([-3,-3]) # lower bound of inputs
X_UB = np.array([3,3]) # upper bounds of inputs
N_TRAINING_POINTS = 32
TEST_FUNC = lambda X: (
    3 * (1 - X[:,0])**2 * np.exp(-(X[:,0]**2) - (X[:,1] + 1)**2) -
    10 * (X[:,0]/5 - X[:,0]**3 - X[:,1]**5) * np.exp(-X[:,0]**2 - X[:,1]**2) -
    np.exp(-(X[:,0] + 1)**2 - X[:,1]**2) / 3)
SEED = 0

# Set training parameters
KERNEL = 'rbf'
GAMMA = 'scale'
TOL = 1e-3
C = 1
EPSILON = 0.1

# Set output location
FILEPATH_OUT = Path(__file__).parent.resolve() / "testSvmRegression.json"

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

# scale inputs to [-1, 1]
scalers['input'] = MinMaxScaler(feature_range=(-1,1)) 
X_train = scalers['input'].fit_transform(X)

# scale outputs to zero mean and unit variance
scalers['output'] = StandardScaler()
y_train = scalers['output'].fit_transform(y.reshape(-1, 1))


#%% DEFINE MODEL

model_sklearn = SVR(kernel=KERNEL, gamma=GAMMA, tol=TOL, C=C, epsilon=EPSILON)

#%% TRAINING 

model_sklearn.fit(X_train, y_train)


#%% SAVE MODEL IN JSON FILE

utils.save_model_to_json(FILEPATH_OUT, model_sklearn, scalers)


#%% TEST

if MELONPY_IMPORT:

    # Sklearn predictions
    
    x_test_scaled = scalers["input"].transform(X_TEST)
    pred_sklearn_scaled = model_sklearn.predict(x_test_scaled)
    pred_sklearn = scalers["output"].inverse_transform(pred_sklearn_scaled[np.newaxis, :])

    # MeLOn predictions

    model_melon = melonpy.SupportVectorMachineOneClassDouble(FILEPATH_OUT.parent.as_posix(), FILEPATH_OUT.name)
    pred_melon = model_melon.calculate_prediction_reduced_space(X_TEST.ravel())

    # Printing

    print("\nTEST")
    print(f"Input: {X_TEST.ravel()}")
    print(f"Scikit-learn prediction: {pred_sklearn.item()}")
    print(f"MeLOn prediction: {pred_melon}")

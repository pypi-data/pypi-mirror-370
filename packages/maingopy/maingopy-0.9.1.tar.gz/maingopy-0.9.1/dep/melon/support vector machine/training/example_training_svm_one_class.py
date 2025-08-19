##
#  @file example_training.py
#
#  @brief Training of suppot vector outlier detection model and export to file that is readable by MeLOn.
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
from sklearn.svm import OneClassSVM
import numpy as np
import pandas as pd

try:
    import melonpy
    MELONPY_IMPORT = True
except ModuleNotFoundError:
    MELONPY_IMPORT = False


#%% SET PARAMETERS    

# Set training parameters
KERNEL = 'rbf'
GAMMA = 1/1.3**2
NU = 0.1
TOL = 1e-6

# Set training data location
FILEPATH_IN = Path(__file__).parent.resolve() / "banana_dataset.csv"

# Set output location
FILEPATH_OUT = Path(__file__).parent.resolve() / "testSvmOneClass.json"

# Set test input
X_TEST = np.array([[1.5, -2]])


#%% LOAD DATA
# Data can be downloaded from https://www.openml.org/d/1460

df = pd.read_csv(FILEPATH_IN, engine="python")
v1 = df["V1"].where(df["Class"]==1).dropna().values
v2 = df["V2"].where(df["Class"]==1).dropna().values
training_data = np.array([v1,v2]).transpose() 


#%% DEFINE MODEL

model_sklearn = OneClassSVM(gamma=GAMMA, kernel=KERNEL, nu=NU, tol=TOL)

#%% TRAINING 

model_sklearn.fit(training_data)


#%% SAVE MODEL IN JSON FILE

utils.save_model_to_json(FILEPATH_OUT, model_sklearn)


#%% TEST

if MELONPY_IMPORT:

    # Sklearn predictions
    
    pred_sklearn = model_sklearn.decision_function(X_TEST)

    # MeLOn predictions

    model_melon = melonpy.SupportVectorMachineOneClassDouble(FILEPATH_OUT.parent.as_posix(), FILEPATH_OUT.name)
    pred_melon = model_melon.calculate_prediction_reduced_space(X_TEST.ravel())

    # Printing

    print("\nTEST")
    print(f"Input: {X_TEST.ravel()}")
    print(f"Scikit-learn prediction: {pred_sklearn.item()}")
    print(f"MeLOn prediction: {pred_melon}")
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

import utils
from sklearn.svm import OneClassSVM
import numpy as np
import time
import os
import pandas as pd

############################ LOAD DATA ############################ 
df = pd.read_csv(os.path.join("data", "Input", "banana_dataset.csv"), engine= "python")
v1 = df["V1"].where(df["Class"]==1).dropna().values
v2 = df["V2"].where(df["Class"]==1).dropna().values
data = np.array([v1,v2]).transpose() 

############################ SET PARAMETERS ############################ 

# output filename
problem_name = "banana"
output_folder = "./data/Output/"
filename_out = output_folder + problem_name

# training parameters
kernel = 'rbf'
gamma = 1/1.3**2
nu=0.1
tol=1e-6

############################  BUILD MODEL ############################ 
clf = OneClassSVM(gamma=gamma, kernel=kernel , nu = nu, tol = tol)

############################  TRAINING ############################ 

training_time = time.time()

clf.fit(data)

training_time = training_time - time.time()

############################  SAVE MODEL ############################ 

# Save model to JSON
utils.save_model_to_json(filename_out, problem_name + '.json', clf)
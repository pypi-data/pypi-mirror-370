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
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np
import matplotlib.pyplot as plt
import time

############################ GENERATE DATA ############################ 
# Generate sample data
problem_name = "sin"

rng = np.random.default_rng(seed=42)

X = np.sort(5 * rng.random((40, 1)), axis=0)
y = np.sin(X).ravel()

# Add noise to targets
y[::5] += 3 * (0.5 - rng.random(8))

############################ SCALE DATA ############################ 
scaler = dict()

# scale inputs to [-1 , 1]
scaler['input'] = MinMaxScaler(feature_range=(-1,1 )) 
X_scaled = scaler['input'].fit_transform(X)

# scale outputs to zero mean and unit variance
scaler['output'] = StandardScaler()
y_scaled = scaler['output'].fit_transform(y.reshape(-1, 1)).ravel()

############################ SET PARAMETERS ############################ 

# output filename
output_folder = "./data/Output/"
filename_out = output_folder + problem_name

# training parameters
kernel = 'rbf'
gamma = 'scale'
tol = 1e-3
C = 1
epsilon = 0.1

############################  BUILD MODEL ############################ 
clf = SVR(kernel=kernel, gamma=gamma, tol=tol, C=C, epsilon=epsilon)

############################  TRAINING ############################ 

training_time = time.time()

clf.fit(X_scaled, y_scaled)

training_time = training_time - time.time()

############################  SAVE MODEL ############################ 

# Save model to XML
utils.save_model_to_json(filename_out, problem_name + '.json', clf,scaler)


########################### PLOT MODEL ##############################

y_pred = scaler['output'].inverse_transform(clf.predict(X_scaled)) 

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(15, 10), sharey=True)
axes.plot(X, y_pred, color='m', lw=2,
                label='SVR prediction')
axes.plot(X, np.sin(X).ravel(), color='b', lw=2,
                label='Original function')
axes.scatter(X[clf.support_], y[clf.support_], facecolor="none",
                    edgecolor='m', s=50,
                    label='Support vectors')
axes.scatter(X[np.setdiff1d(np.arange(len(X)), clf.support_)],
                    y[np.setdiff1d(np.arange(len(X)), clf.support_)],
                    facecolor="none", edgecolor="k", s=50,
                    label='other training data')
axes.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),
                ncol=1, fancybox=True, shadow=True)

fig.text(0.5, 0.04, 'data', ha='center', va='center')
fig.text(0.06, 0.5, 'target', ha='center', va='center', rotation='vertical')
fig.suptitle("Support Vector Regression", fontsize=14)
plt.show()

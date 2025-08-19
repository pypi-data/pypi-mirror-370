##
#  @file example_training_of_ANN_with_pruning.py
#
#  @brief Training of artificial neural network in Keras with pruning and export to file that is readable by MeLOn.
#
# ==============================================================================\n
#   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
# ==============================================================================\n
#
#  @author Artur M. Schweidtmann, Friedrich von Bülow, Jing Cui, Laurens Lueg, and Alexander Mitsos
#  @date 20. January 2020
##

import utils
import tensorflow as tf
import numpy as np
import time
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

############################ LOAD DATA ############################ 
# enter data set information
problem_name = "peaks"
# enter file name of training data - 
filename_data = "./data/peaks.csv"
# dimensionality of the data
input_dim = 2
output_dim = 1
# scale Input to [-1,1] range
scaleInput = True
# normalize Output to z-score
normalizeOutput = True

data = np.loadtxt(open(filename_data, "rb"), delimiter=",")
X = data[:, :-output_dim]
y = data[:, input_dim:]
X_norm = utils.scale(X, scaleInput)
y_norm = utils.normalize(y, normalizeOutput)
x_train, x_val, y_train, y_val = train_test_split(X_norm, y_norm, test_size=0.15)
n_train = x_train.shape[0]

############################ SET PARAMETERS ############################ 
# output filename
output_folder = "./data/Output/"
filename_out = output_folder + problem_name
# training parameters
network_layout = [10, 10]
activation_function = 'relu'
activation_function_out = 'linear'
learning_rate = 0.001
kernel_regularizer = tf.keras.regularizers.l2(l=0.0001)
# 'he_normal' for relu activation, 'glorot_uniform' for everything else
kernel_initializer = 'he_normal'
optimizer = 'adam'
epochs = 100
batch_size = 128
random_state = 1

############################  BUILD MODEL ############################ 

# Sequential class: Linear stack of layers.
model = tf.keras.Sequential()
# Create and add first layer
model.add(tf.keras.layers.Dense(network_layout[0],
                                name="input",
                                kernel_initializer=kernel_initializer,
                                kernel_regularizer=kernel_regularizer,
                                activation=activation_function,
                                input_dim=input_dim))
# Create and add all remaining layers
for neuron in network_layout[1:]:
    model.add(tf.keras.layers.Dense(neuron,
                                    kernel_initializer=kernel_initializer,
                                    kernel_regularizer=kernel_regularizer,
                                    activation=activation_function))
model.add(tf.keras.layers.Dense(output_dim, name="output",
                                kernel_initializer='glorot_uniform',
                                kernel_regularizer=kernel_regularizer,
                                activation=activation_function_out))

model.compile(loss='mse', optimizer=optimizer, metrics=['mse', 'mae'])
# Generate a table summarizing the model
model.summary()

############################  TRAINING ############################ 

training_time = time.time()

history = model.fit(x_train, y_train, validation_data=(x_val, y_val),
                    epochs=epochs, batch_size=batch_size, verbose=1)
training_time = training_time - time.time()

############################  SAVE MODEL ############################ 

# Save entire model to a HDF5 file
model.save(filename_out + '_model.h5')
# Save model to XML
utils.save_model_to_xml(filename_out + '.xml', model, X, y, scaleInput, normalizeOutput)
# plot predictions
y_pred = model.predict(X_norm)

############################ PLOT PREDICTIONS ############################ 
n_train = X_norm.shape[0]
n_rt = np.sqrt(n_train).astype(int)
X = np.zeros((n_rt, n_rt))
Y = np.zeros((n_rt, n_rt))
Z_true = np.zeros((n_rt, n_rt))
Z_pred = np.zeros((n_rt, n_rt))
for i in range(n_rt):
    for j in range(n_rt):
        X[i, j] = X_norm[i * n_rt + j, 0]
        Y[i, j] = X_norm[i * n_rt + j, 1]
        Z_true[i, j] = y_norm[i * n_rt + j]
        Z_pred[i, j] = y_pred[i * n_rt + j]

fig = plt.figure(figsize=plt.figaspect(0.4))
ax = fig.add_subplot(1, 2, 1, projection='3d')
cmap = plt.get_cmap('coolwarm')
ax.plot_surface(X, Y, Z_true, cmap=cmap)
ax.set_title('training data')

ax = fig.add_subplot(1, 2, 2, projection='3d')
ax.plot_wireframe(X, Y, Z_pred)
ax.set_title('learned function')
plt.show()

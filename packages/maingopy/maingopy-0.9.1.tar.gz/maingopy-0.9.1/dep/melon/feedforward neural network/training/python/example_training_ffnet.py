##
#  @file example_training_of_ANN.py
#
#  @brief Training of artificial neural network, optionally with pruning, in Keras and export to file that is readable by MeLOn.
#
# ==============================================================================\n
#   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
# ==============================================================================\n
#
#  @author Artur M. Schweidtmann, Friedrich von Bülow, Jing Cui, Laurens Lueg, and Alexander Mitsos
#  @date 20. January 2020
##

# Use Keras 2 (see 'TensorFlow + Keras 2 backwards compatibility' at https://keras.io/getting_started/)
# TensorFlow Model Optimization Toolkit still uses Keras 2 (see https://github.com/tensorflow/model-optimization/blob/master/tensorflow_model_optimization/python/core/keras/compat.py)
import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'

from pathlib import Path
import random
import utils
import tensorflow as tf
import tensorflow_model_optimization as tfmot
from scipy.stats import qmc
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

try:
    import melonpy
    MELONPY_IMPORT = True
except ModuleNotFoundError:
    MELONPY_IMPORT = False
    
#%% SET PARAMETERS

# Set parameters for generation of training data 
DIM_X = 2 # input dimension
DIM_Y = 1 # output dimension
X_LB = np.array([-3,-3]) # lower bound of inputs
X_UB = np.array([3,3]) # upper bounds of inputs
SCALE_INPUT = True # scale Input to [-1,1] range
SCALE_OUTPUT = True # normalize Output to z-score
VALIDATION_SIZE = 0.15
N_TRAINING_POINTS = 256
TEST_FUNC = lambda X: (
    3 * (1 - X[:,0])**2 * np.exp(-(X[:,0]**2) - (X[:,1] + 1)**2) -
    10 * (X[:,0]/5 - X[:,0]**3 - X[:,1]**5) * np.exp(-X[:,0]**2 - X[:,1]**2) -
    np.exp(-(X[:,0] + 1)**2 - X[:,1]**2) / 3)
SEED = 0

# Set network parameters
NETWORK_LAYOUT = [10, 10] # number of neurons for each layer
ACTIVATION_FUNCTION = 'relu'
ACTIVATION_FUNCTION_OUT = 'linear'
LEARNING_RATE = 0.001
KERNEL_REGULARIZER = tf.keras.regularizers.L2(l2=0.0001)
# 'he_normal' for relu activation, 'glorot_uniform' for everything else
KERNEL_INITIALIZER = 'he_normal'
KERNEL_INITIALIZER_OUT = 'glorot_uniform'
OPTIMIZER = 'adam'
N_EPOCHS = 100
SIZE_BATCH = 32

# Set pruning parameters
DO_PRUNING = True
INITIAL_SPARSITY = 0.0
FINAL_SPARSITY = 0.4
BEGIN_STEP = 30
FREQUENCY = 10

# Set output location
FILEPATH = Path(__file__).parent.resolve() / "testFfnet.xml"

# Set test input
X_TEST = np.array([[1.5, -2]])


#%% GENERATE DATA

# Generate sampling points using latin hypercube sampling
sampler = qmc.LatinHypercube(d=DIM_X, rng=np.random.default_rng(SEED))
X = sampler.random(n=N_TRAINING_POINTS)

# Scale to bounds (sampler only yields values from 0 to 1)
X = X_LB + (X_UB - X_LB)*X

y = TEST_FUNC(X)[:, np.newaxis]


#%% SCALE DATA

scalers = dict()

# scale inputs to [-1,1]
scalers['input'] = MinMaxScaler(feature_range=(-1,1)) 
scalers['input'].fit(X)
if SCALE_INPUT:
    X_scaled = scalers['input'].transform(X)
else:
    X_scaled = X

# scale outputs to zero mean and unit variance
scalers['output'] = StandardScaler()
scalers['output'].fit(y)
if SCALE_OUTPUT:
    y_scaled = scalers['output'].transform(y)
else:
    y_scaled = y

# split into training and validation data
X_train, X_val, y_train, y_val = train_test_split(
    X_scaled, y_scaled, test_size=VALIDATION_SIZE, random_state=SEED)


#%% DEFINE MODEL

# Set the seed
os.environ['PYTHONHASHSEED']=str(SEED)
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# Sequential class: Linear stack of layers.
model_keras = tf.keras.models.Sequential()

# Create and add input layer
layer = tf.keras.Input(shape=(DIM_X,))
model_keras.add(layer)

# Create and add all hidden layers
for neuron in NETWORK_LAYOUT:
    layer = tf.keras.layers.Dense(
        neuron,
        kernel_initializer=KERNEL_INITIALIZER,
        kernel_regularizer=KERNEL_REGULARIZER,
        activation=ACTIVATION_FUNCTION)
    model_keras.add(layer)
    
# Create and add output layer
layer = tf.keras.layers.Dense(
    DIM_Y,
    name="output",
    kernel_initializer=KERNEL_INITIALIZER_OUT,
    kernel_regularizer=KERNEL_REGULARIZER,
    activation=ACTIVATION_FUNCTION_OUT)
model_keras.add(layer)

# Do pruning if set
if DO_PRUNING:
    
    end_step = np.ceil(X_train.shape[0] / SIZE_BATCH).astype(np.int32) * N_EPOCHS  
    schedule = tfmot.sparsity.keras.PolynomialDecay(
        initial_sparsity=INITIAL_SPARSITY,
        final_sparsity=FINAL_SPARSITY,
        begin_step=BEGIN_STEP,
        end_step=end_step,
        frequency=FREQUENCY)
    pruning_params = {'pruning_schedule': schedule}

    model_keras = tfmot.sparsity.keras.prune_low_magnitude(model_keras, **pruning_params)
    
model_keras.compile(
    loss='mse', optimizer=OPTIMIZER, metrics=['mse', 'mae'])

# Generate a table summarizing the model
model_keras.summary()


#%% TRAINING

callbacks = list()
if DO_PRUNING:
    callbacks.append(tfmot.sparsity.keras.UpdatePruningStep())
    
history = model_keras.fit(
    X_train, y_train, validation_data=(X_val, y_val),
    epochs=N_EPOCHS, batch_size=SIZE_BATCH, verbose=1, callbacks=callbacks)


#%% SAVE MODEL IN XML FILE

if DO_PRUNING:
    model_keras = tfmot.sparsity.keras.strip_pruning(model_keras)
    
utils.save_model_to_xml(
    FILEPATH, model_keras, X, y,
    scalers, SCALE_INPUT, SCALE_OUTPUT)


#%% TEST

if MELONPY_IMPORT:

    # Keras prediction
    if SCALE_INPUT:
        x_test_scaled = scalers['input'].transform(X_TEST)
    else:
        x_test_scaled = X_TEST
        
    pred_keras_scaled = model_keras.predict(x_test_scaled)
    
    if SCALE_OUTPUT:
        pred_keras = scalers['output'].inverse_transform(pred_keras_scaled)
    else:
        pred_keras = pred_keras_scaled
    
    # MeLOn prediction
    model_melon = melonpy.FeedForwardNetDouble(
        FILEPATH.parent.as_posix(), FILEPATH.name,
        melonpy.MODEL_FILE_TYPE.XML)
    pred_melon = model_melon.calculate_prediction_reduced_space(X_TEST.ravel())

    # Printing
    print("\nTEST")
    print(f"Input: {X_TEST.ravel()}")
    print(f"Keras prediction: {pred_keras.item()}")
    print(f"MeLOn prediction: {pred_melon}")

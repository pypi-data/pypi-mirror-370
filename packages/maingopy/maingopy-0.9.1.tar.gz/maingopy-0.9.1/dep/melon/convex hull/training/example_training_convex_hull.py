##
#  @file example_training_convex_hull.py
#
#  @brief Creation of a convex hull and export to files that are readable by MeLOn.
#
# ==============================================================================\n
#   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
# ==============================================================================\n
#
#  @author Christian
#  @date 19.03.2020
##

from pathlib import Path
from scipy.stats import qmc
from scipy.spatial import ConvexHull
import numpy as np
import json

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
N_TRAINING_POINTS = 16
SEED = 0

# Set output location
FILEPATH = Path(__file__).parent.resolve() / "testConvexHull.json"

# Set test input
X_TEST = np.array([1.5, -2])


#%% GENERATE DATA

# Generate sampling points using latin hypercube sampling
sampler = qmc.LatinHypercube(d=DIM_X, rng=np.random.default_rng(SEED))
X = sampler.random(n=N_TRAINING_POINTS)

# Scale to bounds (sampler only yields values from 0 to 1)
X = X_LB + (X_UB - X_LB)*X
    
#%% DEFINE AND LEARN MODEL
model_scipy = ConvexHull(X)


#%% SAVE MODEL IN JSON FILE

A = model_scipy.equations[:,:DIM_X]
b = model_scipy.equations[:, DIM_X:]
data = {"A": [list(_A) for _A in A], "b": [_b[0] for _b in b]}

FILEPATH.touch(exist_ok=True)
with FILEPATH.open('w') as outfile:
    json.dump(data, outfile, indent=2)
    
    
#%% TEST

if MELONPY_IMPORT:
    
    # SciPy constraints
    
    constraints_scipy = (A @ X_TEST + b.ravel()).tolist()
    
    # MeLOn constraints
    
    model_melon = melonpy.ConvexHullDouble(FILEPATH.parent.as_posix(), FILEPATH.name)
    constraints_melon = model_melon.generate_constraints(X_TEST)
    
    # Printing
    print(f"Input: {X_TEST.tolist()}")
    print(f"SciPy constraints: {constraints_scipy}")
    print(f"MeLOn constraints: {constraints_melon}")
    
    
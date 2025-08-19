from pathlib import Path
import json

import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import GPy.kern
from emukit.model_wrappers.gpy_model_wrappers import GPyMultiOutputWrapper


def save_emukit_model_to_json(
    folderpath: Path, model: GPyMultiOutputWrapper, scalers: dict[str, MinMaxScaler | StandardScaler]) -> None:
    
    if not model.gpy_model.likelihood.likelihoods_list[0].is_fixed:
        raise Exception("mf_model.gpy_model.likelihood.likelihoods_list[0].is_fixed is not True.\n" +
                        "We currently support only noise of zero.")
    if not model.gpy_model.likelihood.likelihoods_list[1].is_fixed:
        raise Exception("mf_model.gpy_model.likelihood.likelihoods_list[1].is_fixed is not True.\n" +
                        "We currently support only noise of zero.")
    if model.gpy_model.likelihood.likelihoods_list[0].param_array[0] != 0.0:
        raise Exception("mf_model.gpy_model.likelihood.likelihoods_list[0].param_array[0] != 0.0.\n" +
                        "We currently support only noise of zero.")
    if model.gpy_model.likelihood.likelihoods_list[1].param_array[0] != 0.0:
        raise Exception("mf_model.gpy_model.likelihood.likelihoods_list[1].param_array[0] != 0.0.\n" +
                        "We currently support only noise of zero.")
    
    folderpath.mkdir(parents = True, exist_ok = True)
    
    # Low fidelity data
    scalers_low = {"input": scalers["input"], "output": scalers["output_low"]}
    data = create_level_gp_data(0, model, scalers_low)
    with (folderpath / "lowGpData.json").open("w") as outfile:
        json.dump(data, outfile, indent = 2)
        
    # High fidelity data
    scalers_high = {"input": scalers["input"], "output": scalers["output_high"]}
    data = create_level_gp_data(1, model, scalers_high)
    with (folderpath / "highGpData.json").open("w") as outfile:
        json.dump(data, outfile, indent = 2)
        
    # Rho
    data = dict()
    data["rho"] = model.gpy_model.kern.scaling_param[0]
    with (folderpath / "rho.json").open("w") as outfile:
        json.dump(data, outfile, indent = 2)
 
 
def load_scalers_from_json(filepath: Path) -> tuple[MinMaxScaler, StandardScaler]:
    
    with open(filepath, "r") as infile:
        data = json.load(infile)
    
    input_scaler = MinMaxScaler()
    input_scaler.scale_ = \
        (input_scaler.feature_range[1] - input_scaler.feature_range[0]) / \
            (np.array(data["problemUpperBound"]) - np.array(data["problemLowerBound"]))
    input_scaler.min_ = \
        input_scaler.feature_range[0] - np.array(data["problemLowerBound"]) * input_scaler.scale_
    
    output_scaler = StandardScaler()
    output_scaler.mean_ = np.array(data["meanOfOutput"])
    output_scaler.scale_ = np.array(data["stdOfOutput"])
    output_scaler.var_ = output_scaler.scale_**2
        
    return input_scaler, output_scaler


def load_gp_training_data_from_json(filepath: Path) -> tuple[np.array, np.array, np.array, np.array]:
    
    with open(filepath, "r") as infile:
        data = json.load(infile)
        
    X = np.array(data["X"])
    y = np.array(data["Y"]).reshape(-1, 1)
    K = np.array(data["K"])
    invK = np.array(data["invK"])
    
    return X, y, K, invK


def load_kernel_from_json(filepath: Path) -> GPy.kern.Kern:
    
    with open(filepath, "r") as infile:
        data = json.load(infile)
    
    input_dim = data["DX"]    
    variance = data["sf2"]
    lengthscale = np.array(data["ell"])
    kernel_type = int_to_kernel_type(data["matern"])
    
    return kernel_type(input_dim, variance, lengthscale, True)
    

def create_level_gp_data(
    level: int, model: GPyMultiOutputWrapper, scalers: dict[str, MinMaxScaler | StandardScaler]) -> dict:
    
    mask = model.X[:, -1] == level
    X = model.X[mask, :-1]
    y = model.Y[mask]
    X_scaled = scalers["input"].transform(X)
    y_scaled = scalers["output"].transform(y)
    
    data = dict()
    
    data["nX"] = X.shape[0]
    data["DX"] = X.shape[1]
    data["DY"] = 1
    
    data["X"] = X_scaled.tolist()
    data["Y"] = y_scaled.flatten().tolist()
    
    kernel = model.gpy_model.kern.kernels[level]
    noise = model.gpy_model.likelihood.likelihoods_list[level].variance
    if (noise.size == 1):
        noise = noise * np.ones((X.shape[0],))
    
    K = (kernel.K(X, X) + np.diag(noise)) / scalers["output"].var_.item()
    K_inv = np.linalg.inv(K)
    data["K"] = K.tolist()
    data["invK"] = K_inv.tolist()
    
    data["matern"] = kernel_type_to_int(kernel)
    data["sf2"] = kernel.variance[0] / scalers["output"].var_.item()
    data["ell"] = (scalers["input"].scale_ * kernel.lengthscale).tolist()
    
    data["meanfunction"] = scalers["output"].transform([[0]]).item()
    
    data["problemLowerBound"] = scalers["input"].data_min_.tolist()
    data["problemUpperBound"] = scalers["input"].data_max_.tolist()
    data["stdOfOutput"] = scalers["output"].scale_.item()
    data["meanOfOutput"] = scalers["output"].mean_.item()
    
    return data
    

def kernel_type_to_int(kernel: GPy.kern.Kern) -> int:
    
    if (isinstance(kernel, GPy.kern.RBF) or isinstance(kernel, GPy.kern.ExpQuad)): return 999
    if isinstance(kernel, GPy.kern.OU): return 1
    if isinstance(kernel, GPy.kern.Matern32): return 3
    if isinstance(kernel, GPy.kern.Matern52): return 5
    raise Exception(f"The given kernel ({type(kernel).__name__}) is not supported.")
    
    
def int_to_kernel_type(type: int) -> GPy.kern.Kern:
    
    if (type == 999): return GPy.kern.ExpQuad
    if (type == 1): return GPy.kern.OU
    if (type == 3): return GPy.kern.Matern32
    if (type == 5): return GPy.kern.Matern52
    raise Exception(f"The given type number ({type}) is not known.")
    
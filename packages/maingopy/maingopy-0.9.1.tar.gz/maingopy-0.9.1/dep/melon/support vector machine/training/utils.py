from pathlib import Path
import numpy as np
from sklearn.svm import SVR, OneClassSVM
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import json

def save_model_to_json(filepath: Path, model: SVR | OneClassSVM, scalers: dict[str, MinMaxScaler | StandardScaler] = dict()):

    data = dict()
    data["rho"] = model.intercept_.item()
    data["support_vectors"] = model.support_vectors_.tolist()
    data["dual_coefficients"] = model.dual_coef_.ravel().tolist()
    data["kernel_parameters"] = [model._gamma]
    data["kernel_function"] = model.kernel

    data["scaling"] = dict()
    
    if "input" in scalers:
        data["scaling"]["input"] = {
            "scaler": "MinMax",
            "min": scalers["input"].data_min_.tolist(),
            "max": scalers["input"].data_max_.tolist()}
    else:
        data["scaling"]["input"] = {"scaler": "Identity"}
        
    if "output" in scalers:
        data["scaling"]["output"] = {
            "scaler": "Standard",
            "mean": scalers["output"].mean_.tolist(),
            "stddev": scalers["output"].scale_.tolist()}
    else:
        data["scaling"]["output"] = {"scaler": "Identity"}
        
    filepath.touch(exist_ok=True)
    with filepath.open('w') as outfile:
        json.dump(data, outfile, indent=2)

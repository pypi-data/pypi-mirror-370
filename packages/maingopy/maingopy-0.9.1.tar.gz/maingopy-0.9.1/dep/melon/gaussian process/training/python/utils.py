from pathlib import Path
import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import gpytorch
from gpytorch.means import ConstantMean, ZeroMean
from gpytorch.likelihoods import GaussianLikelihood, FixedNoiseGaussianLikelihood
import GPy


def save_gpytorch_model_to_json(
    filepath: Path, GP_model: gpytorch.models.ExactGP, GP_likelihood: gpytorch.likelihoods.GaussianLikelihood,
    X: np.array, y:np.array, matern: int, scalers: dict[str, MinMaxScaler | StandardScaler]
    ):
    
    data = dict()
    
    data["nX"] = X.shape[0]
    data["DX"] = X.shape[1]
    data["DY"] = 1
    
    data["X"] = X.numpy().tolist()
    data["Y"] = y.numpy().tolist()
    
    noise = GP_likelihood.noise.detach().numpy()
    cov_mat = GP_model.covar_module(X).numpy()
    if isinstance(GP_likelihood, GaussianLikelihood):
        K_numpy = cov_mat + noise * np.eye(N=data["nX"])
    elif isinstance(GP_likelihood, FixedNoiseGaussianLikelihood):
        K_numpy = cov_mat + np.diag(noise)
    else:
        raise Exception(f'Likelihood {type(GP_likelihood)} currently not supported.') 

    data["K"] = K_numpy.tolist()
    data["invK"] = np.linalg.inv(K_numpy).tolist()
    
    data["matern"] = matern
    data["sf2"] = GP_model.covar_module.outputscale.detach().numpy().astype(float).item()
    data["ell"] = GP_model.covar_module.base_kernel.lengthscale.detach().numpy().flatten().tolist()
    
    if isinstance(GP_model.mean_module, ConstantMean):
        data["meanfunction"] = GP_model.mean_module.constant.detach().numpy().tolist()
    elif isinstance(GP_model.mean_module, ZeroMean):
        data["meanfunction"] = 0
    else: 
        raise Exception(f'GP uses {type(GP_model.mean_module)} as a mean function. '
                        'Currently only ConstantMean or ZeroMean are supported as mean modules.') 

    data["problemLowerBound"] = scalers['input'].data_min_.tolist()
    data["problemUpperBound"] = scalers['input'].data_max_.tolist()    
    data["stdOfOutput"] = scalers['output'].scale_.item()
    data["meanOfOutput"] = scalers['output'].mean_.item()

    filepath.touch(exist_ok=True)
    with filepath.open('w') as outfile:
        json.dump(data, outfile, indent=2)


def save_gpy_model_to_json(
    filepath: Path, GP_model: GPy.models.GPRegression, scalers: dict[str, MinMaxScaler | StandardScaler]):
    
    X = GP_model.X
    y = GP_model.Y
    
    data = dict()
    
    data["nX"] = X.shape[0]
    data["DX"] = X.shape[1]
    data["DY"] = 1
    
    data["X"] = X.tolist()
    data["Y"] = y.flatten().tolist()
    
    kernel = GP_model.kern
    noise = GP_model.likelihood.variance
    if (noise.size ==1):
        noise = noise * np.ones((data["nX"]))
    
    K = kernel.K(X, X) + np.diag(noise)
    K_inv = np.linalg.inv(K)
    data["K"] = K.tolist()
    data["invK"] = K_inv.tolist()
    
    data["matern"] = kernel_type_to_int(kernel)
    data["sf2"] = kernel.variance.item()
    if (kernel.lengthscale.size == 1):
        data["ell"] = (kernel.lengthscale.item() * np.ones((data["DX"],))).tolist()
    else:
        data["ell"] = kernel.lengthscale.tolist()
    
    mean_func = GP_model.mean_function
    if mean_func is None:
        data["meanfunction"] = 0.0
    elif isinstance(mean_func, GPy.mappings.constant.Constant):
        data["meanfunction"] = mean_func.C.item()
    else:
        raise Exception(f'Type of mean function ({type(mean_func)}) currently not supported.') 
    
    data["problemLowerBound"] = scalers["input"].data_min_.tolist()
    data["problemUpperBound"] = scalers["input"].data_max_.tolist()
    data["stdOfOutput"] = scalers["output"].scale_.item()
    data["meanOfOutput"] = scalers["output"].mean_.item()
    
    filepath.touch(exist_ok=True)
    with filepath.open('w') as outfile:
        json.dump(data, outfile, indent=2)


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
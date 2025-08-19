"""Generate random demands for the CHP sizing problem."""
import numpy as np


def random_demands(Ns, seed=42, /, Qdot_bounds=(0, 1.5), P_bounds=(0, 2)):
    """Generate Ns random demands for the CHP sizing problem.

    Parameters
    ----------
    Ns : int
        Number of scenarios.
    seed : int, optional
        Seed for the random number generator, by default 0
    Qdot_bounds, P_bounds : tuple, optional
        Bounds for the relative demands, by default (0, 1.5) and (0, 2)

    Returns
    -------
    demands : np.ndarray
        Demands for heat and power in each scenario.
    """
    rng = np.random.default_rng(seed)
    demands = rng.uniform(
        (Qdot_bounds[0], P_bounds[0]),
        (Qdot_bounds[1], P_bounds[1]),
        size=(Ns, 2)
    )
    # Sort the demands by combined demand
    # return demands[np.argsort(np.sum(demands, axis=1))]
    # Sort the demands by heat demand
    return demands[np.argsort(demands[:, 0])]

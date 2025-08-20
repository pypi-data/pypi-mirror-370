# Standard library imports
from __future__ import annotations
from typing import Optional, Union, Callable, Dict, List, Tuple, Any

# Third-party imports
import numpy as np
from scipy import stats 

# Local application imports
from random_allocation.comparisons.utils import search_function_with_bounds, FunctionType
from random_allocation.comparisons.structs import PrivacyParams, SchemeConfig, Direction

# ==================== Deterministic ====================
def Gaussian_delta(sigma: float,
                   epsilon: float,
                   ) -> float:
    """
    Calculate the privacy profile of the Gaussian mechanism for a given epsilon.

    Parameters:
    - sigma: The standard deviation of the Gaussian mechanism.
    - epsilon: The privacy parameter.
    """
    upper_cdfs = float(stats.norm.cdf(0.5 / sigma - sigma * epsilon))
    lower_log_cdfs = float(stats.norm.logcdf(-0.5 / sigma - sigma * epsilon))
    # Ensure the result is float by using explicit float conversion
    result = float(upper_cdfs - np.exp(epsilon + lower_log_cdfs))
    return result

def Gaussian_epsilon(sigma: float,
                     delta: float,
                     epsilon_tolerance: float = 1e-3,
                     ) -> float:
    """
    Calculate the epsilon privacy parameter of the Gaussian mechanism for a given delta.

    Parameters:
    - sigma: The standard deviation of the Gaussian mechanism.
    - delta: The privacy profile bound.
    - tolerance: The acceptable error margin.

    Returns:
    - The calculated epsilon value or infinity if not found.
    """
    # Assert invariants that should always be true
    assert sigma > 0, f"sigma must be positive, got {sigma}"
    assert 0 < delta < 1, f"delta must be between 0 and 1, got {delta}"
    
    # Compute the analytic upper bound for epsilon
    epsilon_upper_bound = 1/(2*sigma**2) + np.sqrt(2*np.log(sigma/(delta*np.sqrt(2/np.pi))))/sigma

    # Find the epsilon value using binary search
    optimization_func = lambda eps: Gaussian_delta(sigma=sigma, epsilon=eps)
    epsilon = search_function_with_bounds(func=optimization_func, y_target=delta, bounds=(0, epsilon_upper_bound),
                                          tolerance=epsilon_tolerance, function_type=FunctionType.DECREASING)
    return np.inf if epsilon is None else float(epsilon)

# ==================== Local ====================
def local_delta(params: PrivacyParams,
                config: SchemeConfig,
                direction: Direction = Direction.BOTH,
                ) -> float:
    """
    Calculate the privacy profile in case the index where each element is used is public (no amplification).

    Parameters:
    - params: PrivacyParams containing sigma, epsilon, num_selected, and num_epochs
    - config: Configuration parameters. Is used only for consistency.
    - direction: The direction of privacy. Can be ADD, REMOVE, or BOTH. Doesn't affect the result, and is used only for consistency.
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")

    if params.sampling_probability < 1.0:
        raise ValueError('Sampling probability must be 1.0 for local method')
        
    return Gaussian_delta(sigma=params.sigma/np.sqrt(params.num_selected*params.num_epochs), 
                         epsilon=params.epsilon)

def local_epsilon(params: PrivacyParams,
                  config: SchemeConfig,
                  direction: Direction = Direction.BOTH,
                  ) -> float:
    """
    Calculate the local epsilon value based on sigma, delta, number of selections, and epochs.

    Parameters:
    - params: PrivacyParams containing sigma, delta, num_selected, and num_epochs
    - config: Configuration parameters. Is used only for consistency.
    - direction: The direction of privacy. Can be ADD, REMOVE, or BOTH. Doesn't affect the result, and is used only for consistency.
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")

    if params.sampling_probability < 1.0:
        raise ValueError('Sampling probability must be 1.0 for local method')
    
    return Gaussian_epsilon(sigma=params.sigma/np.sqrt(params.num_selected*params.num_epochs), 
                           delta=params.delta, 
                           epsilon_tolerance=config.epsilon_tolerance)
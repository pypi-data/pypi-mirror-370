# Standard library imports
from typing import Callable

# Third-party imports
import numpy as np
from dp_accounting.pld.privacy_loss_distribution import PrivacyLossDistribution

# Local application imports
from random_allocation.comparisons.utils import search_function_with_bounds, FunctionType, BoundType
from random_allocation.other_schemes.poisson import Poisson_delta_PLD, Poisson_epsilon_PLD, Poisson_PLD
from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig, Direction
from random_allocation.random_allocation_scheme.random_allocation_utils import handle_directions

# Type aliases
NumericFunction = Callable[[float], float]

# ==================== Add ====================
def allocation_epsilon_decomposition_add(params: PrivacyParams, config: SchemeConfig) -> float:
    """Helper function to compute epsilon for the add direction in decomposition scheme"""
    if params.num_steps == 1:
        return float(np.inf)# will lead to lambda=1

    lambda_val = 1 - (1-1.0/params.num_steps)**params.num_steps
    Poisson_sampling_prob = params.sampling_probability/params.num_steps
    Poisson_PLD_obj = Poisson_PLD(
        sigma=params.sigma,
        num_steps=params.num_steps,
        num_epochs=params.num_epochs,
        sampling_prob=Poisson_sampling_prob,
        discretization=config.discretization,
        direction=Direction.ADD,
    )
    
    optimization_func = lambda eps: float(Poisson_PLD_obj.get_delta_for_epsilon(-np.log(1-lambda_val*(1-np.exp(-eps)))))
    
    epsilon = search_function_with_bounds(
        func=optimization_func, 
        y_target=params.delta, 
        bounds=(0, config.epsilon_upper_bound),
        tolerance=config.epsilon_tolerance, 
        function_type=FunctionType.DECREASING
    )
    
    if epsilon is None:
        return float(np.inf)
    
    lower_bound = max(0, (epsilon-config.epsilon_tolerance)/2)
    upper_bound = min((epsilon + config.epsilon_tolerance)*2, config.epsilon_upper_bound)
    
    optimization_func = lambda eps: allocation_delta_decomposition_add_from_PLD(
        epsilon=eps, 
        num_steps=params.num_steps,
        Poisson_PLD_obj=Poisson_PLD_obj
    )
    
    epsilon = search_function_with_bounds(
        func=optimization_func, 
        y_target=params.delta, 
        bounds=(lower_bound, upper_bound),
        tolerance=config.epsilon_tolerance, 
        function_type=FunctionType.DECREASING
    )
    return float(np.inf) if epsilon is None else float(epsilon)

def allocation_delta_decomposition_add_from_PLD(epsilon: float, num_steps: int, Poisson_PLD_obj: PrivacyLossDistribution) -> float:
    if num_steps == 1:
        return float(np.inf)# will lead to lambda=1

    lambda_val = 1 - (1-1.0/num_steps)**num_steps
    # use one of two identical formulas to avoid numerical instability
    if epsilon < 1:
        lambda_new = lambda_val / (lambda_val + np.exp(epsilon)*(1-lambda_val))
    else:
        lambda_new = lambda_val*np.exp(-epsilon) / (lambda_val*np.exp(-epsilon) + (1-lambda_val))
    
    epsilon_new = -np.log(1 - lambda_val * (1 - np.exp(-epsilon)))
    return float(min(Poisson_PLD_obj.get_delta_for_epsilon(epsilon_new)/lambda_new, 1.0))

def allocation_delta_decomposition_add(params: PrivacyParams, config: SchemeConfig) -> float:
    """Helper function to compute delta for the add direction in decomposition scheme"""
    Poisson_sampling_prob = params.sampling_probability / params.num_steps

    Poisson_PLD_obj = Poisson_PLD(
        sigma=params.sigma,
        num_steps=params.num_steps,
        num_epochs=params.num_epochs,
        sampling_prob=Poisson_sampling_prob,
        discretization=config.discretization,
        direction=Direction.ADD,
    )
    
    return allocation_delta_decomposition_add_from_PLD(
        epsilon=params.epsilon,
        num_steps=params.num_steps,
        Poisson_PLD_obj=Poisson_PLD_obj
    )

# ==================== Remove ====================
def allocation_epsilon_decomposition_remove(params: PrivacyParams, config: SchemeConfig) -> float:
    """Helper function to compute epsilon for the remove direction in decomposition scheme"""
    lambda_val = 1 - (1-1.0/params.num_steps)**params.num_steps
    delta_new = params.delta * lambda_val

    Poisson_sampling_prob = params.sampling_probability/params.num_steps
    Poisson_params = PrivacyParams(
        sigma=params.sigma, 
        delta=delta_new, 
        num_steps=params.num_steps, 
        num_selected=1, 
        num_epochs=params.num_epochs
    )

    epsilon_Poisson = Poisson_epsilon_PLD(params=Poisson_params, config=config, sampling_prob=Poisson_sampling_prob)

    factor = 1.0/lambda_val
    # use one of two identical formulas to avoid numerical instability
    if epsilon_Poisson < 1:
        amplified_epsilon = np.log(1+factor*(np.exp(epsilon_Poisson)-1))
    else:
        amplified_epsilon = epsilon_Poisson + np.log(factor + (1-factor)*np.exp(-epsilon_Poisson))
    return float(amplified_epsilon)

def allocation_delta_decomposition_remove(params: PrivacyParams, config: SchemeConfig) -> float:
    """Helper function to compute delta for the remove direction in decomposition scheme"""
    lambda_val = 1 - (1-1.0/params.num_steps)**params.num_steps

    # use one of two identical formulas to avoid numerical instability
    if params.epsilon < 1.0:
        epsilon_new = np.log(1+lambda_val*(np.exp(params.epsilon)-1))
    else:
        epsilon_new = params.epsilon + np.log(np.exp(-params.epsilon)+lambda_val*(1-np.exp(-params.epsilon)))

    Poisson_sampling_prob = params.sampling_probability/params.num_steps
    Poisson_params = PrivacyParams(
        sigma=params.sigma, 
        epsilon=epsilon_new, 
        num_steps=params.num_steps, 
        num_selected=1, 
        num_epochs=params.num_epochs
    )
    delta_Poisson = Poisson_delta_PLD(params=Poisson_params, config=config, sampling_prob=Poisson_sampling_prob)
    return float(delta_Poisson / lambda_val)

# ==================== Both ====================
def allocation_epsilon_decomposition(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute epsilon for the decomposition allocation scheme.
    
    Args:
        params: Privacy parameters (must include delta)
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Computed epsilon value
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")

    if params.num_epochs > 1 or params.num_selected > 1:
        raise ValueError('Allocation decomposition method only supports num_epochs=1 and num_selected=1')

    return handle_directions(params=params,
                             config=config,
                             direction=direction,
                             add_func=allocation_epsilon_decomposition_add,
                             remove_func=allocation_epsilon_decomposition_remove,
                             var_name="epsilon")

def allocation_delta_decomposition(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute delta for the decomposition allocation scheme.
    
    Args:
        params: Privacy parameters (must include epsilon)
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Computed delta value
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    
    if params.num_epochs > 1 or params.num_selected > 1:
        raise ValueError('Allocation decomposition method only supports num_epochs=1 and num_selected=1')

    return handle_directions(params=params,
                             config=config,
                             direction=direction,
                             add_func=allocation_delta_decomposition_add,
                             remove_func=allocation_delta_decomposition_remove,
                             var_name="delta")

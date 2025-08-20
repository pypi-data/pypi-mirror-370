# Standard library imports
from typing import Optional, Union, Callable, Dict, Any, List, Tuple

# Third-party imports
import numpy as np

# Local application imports
from random_allocation.random_allocation_scheme.Monte_Carlo_external import *
from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig, Direction
from random_allocation.comparisons.utils import search_function_with_bounds, FunctionType

def allocation_epsilon_lower_bound(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    # return 0.0
    """
    Compute a lower bound on epsilon for the allocation scheme.
    
    Args:
        params: Privacy parameters (must include delta)
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Lower bound on epsilon
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")
    
    if params.num_epochs > 1 or params.num_selected > 1:
        raise ValueError('Allocation lower bound only supports num_epochs=1 and num_selected=1')

    if params.sampling_probability < 1.0:
        raise ValueError('Sampling probability must be 1.0 for allocation lower bound')

    #find the epsilon that gives the delta using binary search    
    optimization_func = lambda eps: allocation_delta_lower_bound(
        PrivacyParams(
            sigma=params.sigma,
            epsilon=eps,
            num_steps=params.num_steps,
            num_epochs=params.num_epochs,
            num_selected=params.num_selected
        ),
        config=config,
        direction=direction
    )
    
    epsilon = search_function_with_bounds(
        func=optimization_func, 
        y_target=params.delta, 
        bounds=(config.epsilon_tolerance*2, config.epsilon_upper_bound),
        tolerance=config.epsilon_tolerance, 
        function_type=FunctionType.DECREASING
    )
    return epsilon if epsilon is not None else np.inf

def allocation_delta_lower_bound(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute a lower bound on delta for the allocation scheme.
    
    Args:
        params: Privacy parameters (must include epsilon)
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Lower bound on delta
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    
    if params.num_epochs > 1 or params.num_selected > 1:
        raise ValueError('Allocation lower bound only supports num_epochs=1 and num_selected=1')

    if params.sampling_probability < 1.0:
        raise ValueError('Sampling probability must be 1.0 for allocation lower bound')

    bnb_accountant = BnBAccountant()
    
    # Convert the return value to float to ensure type consistency
    result = bnb_accountant.get_deltas_lower_bound(
        params.sigma, 
        (params.epsilon), 
        params.num_steps, 
        params.num_epochs
    )[0]
    
    # Protected conversion: ensure delta is non-negative (delta >= 0 always)
    return float(max(result, 0.0))
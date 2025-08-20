# Standard library imports
from typing import Optional, Union, Callable, Dict, Any

# Third-party imports
import numpy as np

# Local application imports
from random_allocation.comparisons.utils import search_function_with_bounds, FunctionType
from random_allocation.other_schemes.shuffle_external import numericalanalysis
from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig, Direction
from random_allocation.other_schemes.local import local_epsilon

def shuffle_epsilon_analytic(params: PrivacyParams,
                             config: SchemeConfig,
                             direction: Direction = Direction.BOTH,
                             ) -> float:
    """
    Calculate the epsilon value for the shuffle scheme.
    
    Parameters:
    - params: Privacy parameters
    - config: Scheme configuration parameters
    - direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")
    
    if params.num_epochs > 1 or params.num_selected > 1:
        raise ValueError('Shuffle method only supports num_epochs=1 and num_selected=1')
    
    if params.sampling_probability < 1.0:
        raise ValueError('Sampling probability must be 1.0 for shuffle method')

    delta_split = 0.05    
    # Create temporary params for local_epsilon
    temp_params = PrivacyParams(
        sigma=params.sigma,
        delta=params.delta,
        epsilon=None,
        num_steps=params.num_steps,
        num_selected=params.num_selected,
        num_epochs=params.num_epochs
    )
    det_eps = local_epsilon(params=temp_params, config=config, direction=direction)
    
    # Create params for the local delta
    local_delta = params.delta*delta_split/(2*params.num_steps*(np.exp(2)+1)*(1+np.exp(2)/2))
    local_params = PrivacyParams(
        sigma=params.sigma,
        delta=local_delta,
        epsilon=None,
        num_steps=params.num_steps,
        num_selected=1,
        num_epochs=1
    )
    
    local_epsilon_val = local_epsilon(params=local_params, config=config, direction=direction)
    if local_epsilon_val is None or local_epsilon_val > 10:
        return float(det_eps) if det_eps is not None else float('inf')
    
    epsilon = numericalanalysis(
        n=params.num_steps, 
        epsorig=local_epsilon_val, 
        delta=params.delta*(1-delta_split), 
        num_iterations=params.num_epochs,
        step=config.shuffle_step, 
        upperbound=True
    )
    
    for _ in range(5):
        local_delta = params.delta/(2*params.num_steps*(np.exp(epsilon)+1)*(1+np.exp(local_epsilon_val)/2))
        local_params.delta = local_delta
        local_epsilon_val = local_epsilon(params=local_params, config=config, direction=direction)
        if local_epsilon_val is None:
            local_epsilon_val = float('inf')  # Use infinity for None values
            
        epsilon = numericalanalysis(
            n=params.num_steps, 
            epsorig=local_epsilon_val, 
            delta=params.delta*(1-delta_split),
            num_iterations=params.num_epochs, 
            step=config.shuffle_step, 
            upperbound=True
        )
        
        delta_bnd = params.delta*(1-delta_split)+local_delta*params.num_steps*(np.exp(epsilon)+1)*(1+np.exp(local_epsilon_val)/2)
        if delta_bnd < params.delta:
            break
    
    if epsilon > det_eps and det_eps is not None:
        return float(det_eps)
    
    # Return epsilon but ensure it's a float
    return float(epsilon)

def shuffle_delta_analytic(params: PrivacyParams,
                           config: SchemeConfig,
                           direction: Direction = Direction.BOTH,
                           ) -> float:
    """
    Calculate the delta value for the shuffle scheme.
    
    Parameters:
    - params: Privacy parameters
    - config: Scheme configuration parameters
    - direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    
    if params.num_epochs > 1 or params.num_selected > 1:
        raise ValueError('Shuffle method only supports num_epochs=1 and num_selected=1')
    
    if params.sampling_probability < 1.0:
        raise ValueError('Sampling probability must be 1.0 for shuffle method')
    
    result = search_function_with_bounds(
        func=lambda delta: shuffle_epsilon_analytic(params=PrivacyParams(
            sigma=params.sigma,
            num_steps=params.num_steps,
            num_selected=params.num_selected,
            num_epochs=params.num_epochs,
            epsilon=None,
            delta=delta
        ), config=config, direction=direction), 
        y_target=params.epsilon, 
        bounds=(config.delta_tolerance, 1-config.delta_tolerance),
        tolerance=config.delta_tolerance, 
        function_type=FunctionType.DECREASING
    )
    
    # Handle the case where search_function_with_bounds returns None
    return 1.0 if result is None else float(result)
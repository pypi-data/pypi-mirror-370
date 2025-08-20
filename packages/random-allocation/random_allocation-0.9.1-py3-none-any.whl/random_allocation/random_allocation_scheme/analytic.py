# Standard library imports

# Third-party imports
import numpy as np

# Local application imports
from random_allocation.comparisons.utils import search_function_with_bounds, FunctionType
from random_allocation.other_schemes.local import local_epsilon, Direction
from random_allocation.other_schemes.poisson import Poisson_epsilon_PLD
from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig

def sampling_prob_from_sigma(sigma: float,
                             delta: float,
                             num_steps: int,
                             num_selected: int,
                             local_delta: float,
                             direction: Direction = Direction.BOTH,
                             ) -> float:
    """
    Calculate the sampling probability for the given parameters.
    
    Args:
        sigma: Noise scale
        delta: Privacy parameter
        num_steps: Number of steps
        num_selected: Number of selected items
        local_delta: Delta parameter for local randomization
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
        
    Returns:
        Calculated sampling probability between 0 and 1
    """
    params = PrivacyParams(sigma=sigma, delta=local_delta, num_steps=num_steps, num_selected=num_selected, num_epochs=1)
    local_epsilon_val = local_epsilon(params=params, config=SchemeConfig(), direction=direction)
    if local_epsilon_val is None:
        return 1.0
    gamma = np.cosh(local_epsilon_val)*np.sqrt(2*num_selected*np.log(num_selected/delta)/num_steps)
    if gamma > 1 - num_selected/num_steps:
        return 1.0
    return float(np.clip(num_selected/(num_steps*(1.0-gamma)), 0, 1))

def allocation_epsilon_analytic(params: PrivacyParams,
                                config: SchemeConfig,
                                direction: Direction = Direction.BOTH,
                                ) -> float:
    """
    Compute epsilon for the analytic allocation scheme.
    
    Args:
        params: Privacy parameters
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Computed epsilon value or np.inf if conditions are not met
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")
        
    num_steps_per_round = int(np.ceil(params.num_steps/params.num_selected))
    num_rounds = int(np.ceil(params.num_steps/num_steps_per_round))

    local_delta_split = 0.99
    Poisson_delta_split = (1-local_delta_split)/2
    large_sampling_prob_delta_split = (1-local_delta_split)/2
    
    local_delta = params.delta*local_delta_split/(num_steps_per_round*num_rounds*params.num_epochs)
    Poisson_delta = params.delta*Poisson_delta_split
    large_sampling_prob_delta = params.delta*large_sampling_prob_delta_split/(num_rounds*params.num_epochs)
    
    sampling_prob = params.sampling_probability * \
                    sampling_prob_from_sigma(
                        sigma=params.sigma, 
                        delta=large_sampling_prob_delta, 
                        num_steps=num_steps_per_round,
                        num_selected=1, 
                        local_delta=local_delta,
                        direction=direction
                    )

    if sampling_prob > np.sqrt(1/num_steps_per_round):
        return float(np.inf)
        
    Poisson_params = PrivacyParams(
        sigma=params.sigma, 
        delta=Poisson_delta, 
        num_steps=num_steps_per_round, 
        num_selected=1, 
        num_epochs=num_rounds*params.num_epochs
    )
    epsilon = Poisson_epsilon_PLD(
        params=Poisson_params,
        config=config,
        sampling_prob=sampling_prob,
        direction=direction
    )
    
    return float(epsilon)

def allocation_delta_analytic(params: PrivacyParams,
                              config: SchemeConfig,
                              direction: Direction = Direction.BOTH,
                              ) -> float:
    """
    Compute delta for the analytic allocation scheme.
    
    Args:
        params: Privacy parameters
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
        
    Returns:
        Computed delta value
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    
    result = search_function_with_bounds(
        func=lambda delta: allocation_epsilon_analytic(params=PrivacyParams(
            sigma=params.sigma,
            num_steps=params.num_steps,
            num_selected=params.num_selected,
            num_epochs=params.num_epochs,
            sampling_probability=params.sampling_probability,
            epsilon=None,
            delta=delta
        ), config=config, direction=direction), 
        y_target=params.epsilon, 
        bounds=(2*config.delta_tolerance, 1-2*config.delta_tolerance),
        tolerance=config.delta_tolerance, 
        function_type=FunctionType.DECREASING
    )
    
    # Handle case where search function returns None
    return 1.0 if result is None else float(result)
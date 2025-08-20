# Standard library imports
from logging import config
from typing import Callable, List, Union, Optional, Tuple, Dict, Any, cast, Literal

# Third-party imports
import numpy as np
from numpy.typing import NDArray

# Local application imports
from random_allocation.random_allocation_scheme.direct import log_factorial_range, log_factorial
from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig, Direction, Verbosity
from random_allocation.random_allocation_scheme.random_allocation_utils import handle_directions, print_alpha

# Type alias for numpy float arrays
FloatArray = NDArray[np.float64]

# ==================== Add ====================
def allocation_RDP_DCO_add(sigma: float,
                           num_steps: int,
                           num_selected: int,
                           alpha: float,
                           ) -> float:
    """
    Compute an upper bound on RDP of the allocation mechanism (add direction)
    
    Args:
        sigma: Noise scale
        num_steps: Number of steps
        num_selected: Number of selected items
        alpha: Alpha order for RDP
    
    Returns:
        Upper bound on RDP
    """
    return float(alpha*num_selected**2/(2*sigma**2*num_steps) \
        + (alpha*num_selected*(num_steps-num_selected))/(2*sigma**2*num_steps*(alpha-1)) \
        - num_steps*np.log1p(alpha*(np.exp(num_selected*(num_steps-num_selected)/(sigma**2*num_steps**2))-1))/(2*(alpha-1)))

def allocation_epsilon_RDP_DCO_add(params: PrivacyParams, config: SchemeConfig) -> float:
    """
    Compute an upper bound on epsilon for the RDP-DCO allocation mechanism (add direction)

    Args:
        params: Privacy parameters
        config: Scheme configuration

    Returns:
        Upper bound on epsilon
    """
    alpha_orders = np.array(config.allocation_RDP_DCO_alpha_orders, dtype=np.float64)
    alpha_RDP = params.num_epochs * np.array([allocation_RDP_DCO_add(
        params.sigma, params.num_steps, params.num_selected, float(alpha))
        for alpha in alpha_orders])
    alpha_epsilons = np.maximum(0.0, alpha_RDP + np.log1p(-1/alpha_orders) - np.log(params.delta * alpha_orders)/(alpha_orders-1))
    used_alpha = float(alpha_orders[np.argmin(alpha_epsilons)])
    print_alpha(used_alpha, alpha_orders[0], alpha_orders[-1], config.verbosity, "add", params)
    return float(np.min(alpha_epsilons))

def allocation_delta_RDP_DCO_add(params: PrivacyParams, config: SchemeConfig) -> float:
    """
    Compute an upper bound on delta for the RDP-DCO allocation mechanism (add direction)

    Args:
        params: Privacy parameters
        config: Scheme configuration

    Returns:
        Upper bound on delta
    """
    # Compute RDP values
    alpha_orders = np.array(config.allocation_RDP_DCO_alpha_orders, dtype=np.float64)
    alpha_RDP = params.num_epochs * np.array([allocation_RDP_DCO_add(
        params.sigma, params.num_steps, params.num_selected, float(alpha))
        for alpha in alpha_orders])
    
    # Compute log(delta) directly to avoid overflow
    log_alpha_deltas = (alpha_orders-1) * (alpha_RDP - params.epsilon) + \
                        alpha_orders * np.log1p(-1/alpha_orders) - np.log(alpha_orders-1)
    
    # Find the minimum delta and corresponding alpha directly in log space
    min_log_delta_idx = np.argmin(log_alpha_deltas)
    used_alpha = float(alpha_orders[min_log_delta_idx])
    print_alpha(used_alpha, alpha_orders[0], alpha_orders[-1], config.verbosity, "add", params)
    
    # Protected conversion: ensure delta doesn't exceed 1.0
    return float(np.minimum(1.0, np.exp(log_alpha_deltas[min_log_delta_idx])))

# ==================== Remove ====================

def allocation_RDP_DCO_remove(sigma: float,
                              num_steps: int,
                              num_selected: int,
                              alpha: float,
                              ) -> float:
    """
    Compute an upper bound on RDP of the allocation mechanism based on alpha=2
    
    Args:
        sigma: Noise scale
        num_steps: Number of steps 
        num_selected: Number of selected items
        alpha: Alpha order for RDP
    
    Returns:
        Upper bound on RDP
    """
    log_terms_arr = np.array([log_factorial_range(n=num_selected, m=i) - log_factorial(n=i)
                              + log_factorial_range(n=num_steps-num_selected, m=num_selected-i) - log_factorial(n=num_selected-i)
                              + i*alpha/(2*sigma**2) for i in range(num_selected+1)])
    max_log_term = np.max(log_terms_arr)
    return float(max_log_term + np.log(np.sum(np.exp(log_terms_arr - max_log_term))) - 
                 log_factorial_range(n=num_steps, m=num_selected) + log_factorial(n=num_selected))

def allocation_epsilon_RDP_DCO_remove(params: PrivacyParams, config: SchemeConfig) -> float:
        """
        Compute an upper bound on epsilon for the RDP-DCO allocation mechanism (remove direction)
        Args:
        params: Privacy parameters
        config: Scheme configuration

        Returns:
            Upper bound on epsilon
        """
        alpha_orders = np.array(config.allocation_RDP_DCO_alpha_orders, dtype=np.float64)
        alpha_RDP = params.num_epochs * np.array([allocation_RDP_DCO_remove(
            params.sigma, params.num_steps, params.num_selected, float(alpha))
            for alpha in alpha_orders])
        alpha_epsilons = np.maximum(0.0, alpha_RDP + np.log1p(-1/alpha_orders) - np.log(params.delta * alpha_orders)/(alpha_orders-1))
        used_alpha = float(alpha_orders[np.argmin(alpha_epsilons)])
        print_alpha(used_alpha, alpha_orders[0], alpha_orders[-1], config.verbosity, "remove", params)
        return float(np.min(alpha_epsilons))

def allocation_delta_RDP_DCO_remove(params: PrivacyParams, config: SchemeConfig) -> float:
    """
    Compute an upper bound on delta for the RDP-DCO allocation mechanism (remove direction)
    
    Args:
        params: Privacy parameters
        config: Scheme configuration
    
    Returns:
        Upper bound on delta
    """
    # Compute RDP values
    alpha_orders = np.array(config.allocation_RDP_DCO_alpha_orders, dtype=np.float64)
    alpha_RDP = params.num_epochs * np.array([allocation_RDP_DCO_remove(
        params.sigma, params.num_steps, params.num_selected, float(alpha))
        for alpha in alpha_orders])
    
    # Compute log(delta) directly to avoid overflow
    log_alpha_deltas = (alpha_orders-1) * (alpha_RDP - params.epsilon) + \
                        alpha_orders * np.log1p(-1/alpha_orders) - np.log(alpha_orders-1)
    
    # Find the minimum delta and corresponding alpha directly in log space
    min_log_delta_idx = np.argmin(log_alpha_deltas)
    used_alpha = float(alpha_orders[min_log_delta_idx])
    print_alpha(used_alpha, alpha_orders[0], alpha_orders[-1], config.verbosity, "remove", params)
    
    # Protected conversion: ensure delta doesn't exceed 1.0
    return float(np.minimum(1.0, np.exp(log_alpha_deltas[min_log_delta_idx])))
    
# ==================== Both ====================
def allocation_epsilon_RDP_DCO(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute epsilon for the RDP-DCO allocation scheme.
    
    Args:
        params: Privacy parameters
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Computed epsilon value
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")
    
    if params.sampling_probability < 1.0:
        raise ValueError('Sampling probability must be 1.0 for allocation RDP_DCO method')

    # Use alpha_orders directly from config or generate if not provided
    if config.allocation_RDP_DCO_alpha_orders is not None:
        alpha_orders: NDArray[np.float64] = np.array(config.allocation_RDP_DCO_alpha_orders, dtype=np.float64)
        assert np.all(alpha_orders >= 2), f"All alpha values must be >= 2 for RDP_DCO. Found min value: {np.min(alpha_orders)}"
    else:
        alpha_orders = np.concatenate((np.arange(2, 202, dtype=np.float64), np.exp(np.linspace(np.log(202), np.log(10_000), 50))))
    config.allocation_RDP_DCO_alpha_orders = alpha_orders.tolist()

    return handle_directions(params=params,
                             config=config,
                             direction=direction,
                             add_func=allocation_epsilon_RDP_DCO_add,
                             remove_func=allocation_epsilon_RDP_DCO_remove,
                             var_name="epsilon")

def allocation_delta_RDP_DCO(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute delta for the RDP-DCO allocation scheme.
    
    Args:
        params: Privacy parameters
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
        
    Returns:
        Computed delta value
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    
    if params.sampling_probability < 1.0:
        raise ValueError('Sampling probability must be 1.0 for allocation RDP_DCO method')

    # Use alpha_orders directly from config or generate if not provided
    if config.allocation_RDP_DCO_alpha_orders is not None:
        alpha_orders: NDArray[np.float64] = np.array(config.allocation_RDP_DCO_alpha_orders, dtype=np.float64)
        assert np.all(alpha_orders >= 2), f"All alpha values must be >= 2 for RDP_DCO. Found min value: {np.min(alpha_orders)}"
    else:
        alpha_orders = np.concatenate((np.arange(2, 202, dtype=np.float64), np.exp(np.linspace(np.log(202), np.log(10_000), 50))))
    config.allocation_RDP_DCO_alpha_orders = alpha_orders.tolist()

    return handle_directions(params=params,
                             config=config,
                             direction=direction,
                             add_func=allocation_delta_RDP_DCO_add,
                             remove_func=allocation_delta_RDP_DCO_remove,
                             var_name="delta")

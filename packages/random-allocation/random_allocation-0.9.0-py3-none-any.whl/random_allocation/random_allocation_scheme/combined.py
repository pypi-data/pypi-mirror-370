# Standard library imports
from typing import List, Dict, Tuple, Optional, Union, Callable, Any, cast

# Third-party imports
import numpy as np

# Local application imports
from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig, Direction, Verbosity
from random_allocation.random_allocation_scheme.analytic import allocation_epsilon_analytic, allocation_delta_analytic
from random_allocation.random_allocation_scheme.direct import allocation_epsilon_direct, allocation_delta_direct
from random_allocation.random_allocation_scheme.recursive import allocation_epsilon_recursive, allocation_delta_recursive
from random_allocation.random_allocation_scheme.decomposition import allocation_epsilon_decomposition, allocation_delta_decomposition
from random_allocation.other_schemes.local import local_epsilon, local_delta
from random_allocation.random_allocation_scheme.random_allocation_utils import handle_directions

# ==================== Add ====================
def allocation_epsilon_combined_add(params: PrivacyParams, config: SchemeConfig) -> float:
    """
    Compute epsilon for the combined allocation scheme in the add direction.
    
    Args:
        params: Privacy parameters (must include delta)
        config: Scheme configuration parameters
    
    Returns:
        Computed epsilon value
    """
    
    epsilon_local_val = local_epsilon(params=params, config=config) if params.sampling_probability == 1.0 else float('inf')
    epsilon_analytic_val = allocation_epsilon_analytic(params=params, config=config, direction=Direction.ADD)
    # Direct allocation is only valid if sampling_probability == 1.0
    epsilon_direct_val = allocation_epsilon_direct(params=params, config=config, direction=Direction.ADD) if params.sampling_probability == 1.0 else float('inf')
    epsilon_recursive_val = allocation_epsilon_recursive(params=params, config=config, direction=Direction.ADD)
    # Only use decomposition if constraints are met (num_epochs=1 and num_selected=1)
    epsilon_decompose_val = allocation_epsilon_decomposition(params=params, config=config, direction=Direction.ADD) if params.num_epochs == 1 and params.num_selected == 1 else float('inf')

    return min(
        epsilon_local_val,
        epsilon_analytic_val,
        epsilon_decompose_val,
        epsilon_direct_val,
        epsilon_recursive_val
    )

def allocation_delta_combined_add(params: PrivacyParams, config: SchemeConfig) -> float:
    """
    Compute delta for the combined allocation scheme in the add direction.
    
    Args:
        params: Privacy parameters (must include epsilon)
        config: Scheme configuration parameters
    
    Returns:
        Computed delta value
    """
    
    delta_local_val = local_delta(params=params, config=config) if params.sampling_probability == 1.0 else 1.0    
    delta_analytic_val = allocation_delta_analytic(params=params, config=config, direction=Direction.ADD)
    # Direct allocation is only valid if sampling_probability == 1.0
    delta_direct_val = allocation_delta_direct(params=params, config=config, direction=Direction.ADD) if params.sampling_probability == 1.0 else 1.0
    delta_recursive_val = allocation_delta_recursive(params=params, config=config, direction=Direction.ADD)
    # Only use decomposition if constraints are met (num_epochs=1 and num_selected=1)
    delta_decompose_val = allocation_delta_decomposition(params=params, config=config, direction=Direction.ADD) if params.num_epochs == 1 and params.num_selected == 1 else 1.0

    return min(
        delta_local_val,
        delta_analytic_val,
        delta_decompose_val,
        delta_direct_val,
        delta_recursive_val
    )

# ==================== Remove ====================
def allocation_epsilon_combined_remove(params: PrivacyParams, config: SchemeConfig) -> float:
    """
    Compute epsilon for the combined allocation scheme in the remove direction.
    
    Args:
        params: Privacy parameters (must include delta)
        config: Scheme configuration parameters
    
    Returns:
        Computed epsilon value
    """
    
    epsilon_local_val = local_epsilon(params=params, config=config) if params.sampling_probability == 1.0 else float('inf')
    epsilon_analytic_val = allocation_epsilon_analytic(params=params, config=config, direction=Direction.REMOVE)
    # Direct allocation is only valid if sampling_probability == 1.0
    epsilon_direct_val = allocation_epsilon_direct(params=params, config=config, direction=Direction.REMOVE) if params.sampling_probability == 1.0 else float('inf')
    epsilon_recursive_val = allocation_epsilon_recursive(params=params, config=config, direction=Direction.REMOVE)
    # Only use decomposition if constraints are met (num_epochs=1 and num_selected=1)
    epsilon_decompose_val = allocation_epsilon_decomposition(params=params, config=config, direction=Direction.REMOVE) if params.num_epochs == 1 and params.num_selected == 1 else float('inf')

    return min(
        epsilon_local_val,
        epsilon_analytic_val,
        epsilon_decompose_val,
        epsilon_direct_val,
        epsilon_recursive_val
    )

def allocation_delta_combined_remove(params: PrivacyParams, config: SchemeConfig) -> float:
    """
    Compute delta for the combined allocation scheme in the remove direction.
    
    Args:
        params: Privacy parameters (must include epsilon)
        config: Scheme configuration parameters
    
    Returns:
        Computed delta value
    """
    
    delta_local_val = local_delta(params=params, config=config) if params.sampling_probability == 1.0 else 1.0
    delta_analytic_val = allocation_delta_analytic(params=params, config=config, direction=Direction.REMOVE)
    # Direct allocation is only valid if sampling_probability == 1.0
    delta_direct_val = allocation_delta_direct(params=params, config=config, direction=Direction.REMOVE) if params.sampling_probability == 1.0 else 1.0
    delta_recursive_val = allocation_delta_recursive(params=params, config=config, direction=Direction.REMOVE)
    # Only use decomposition if constraints are met (num_epochs=1 and num_selected=1)
    delta_decompose_val = allocation_delta_decomposition(params=params, config=config, direction=Direction.REMOVE) if params.num_epochs == 1 and params.num_selected == 1 else 1.0

    return min(
        delta_local_val,
        delta_analytic_val,
        delta_decompose_val,
        delta_direct_val,
        delta_recursive_val
    )

# ==================== Both ====================
def allocation_epsilon_combined(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute epsilon for the combined allocation scheme.
    This method uses the minimum of the various allocation methods.
    
    Args:
        params: Privacy parameters (must include delta)
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Computed epsilon value
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")

    return handle_directions(params=params,
                             config=config,
                             direction=direction,
                             add_func=allocation_epsilon_combined_add,
                             remove_func=allocation_epsilon_combined_remove,
                             var_name="epsilon")

def allocation_delta_combined(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute delta for the combined allocation scheme.
    
    Args:
        params: Privacy parameters (must include epsilon)
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Computed delta value
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    
    return handle_directions(params=params,
                             config=config,
                             direction=direction,
                             add_func=allocation_delta_combined_add,
                             remove_func=allocation_delta_combined_remove,
                             var_name="delta")

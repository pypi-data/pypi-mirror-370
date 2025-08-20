# Standard library imports
from typing import Callable

# Third-party imports
import numpy as np
from dp_accounting.pld import privacy_loss_distribution
from PLD_subsampling import scale_pld_infinity_mass 

# Local application imports
from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig, Direction
from random_allocation.comparisons.utils import search_function_with_bounds, FunctionType
from random_allocation.other_schemes.poisson import Poisson_epsilon_PLD, Poisson_delta_PLD, Poisson_PLD
from random_allocation.random_allocation_scheme.decomposition import allocation_delta_decomposition_add_from_PLD, allocation_delta_decomposition, allocation_epsilon_decomposition
from random_allocation.random_allocation_scheme.direct import allocation_delta_direct
# Type aliases
NumericFunction = Callable[[float], float]

def allocation_epsilon_recursive_inner(
    sigma: float, 
    delta: float, 
    num_steps: int, 
    num_epochs: int, 
    sampling_probability: float, 
    config: SchemeConfig, 
    optimization_func: NumericFunction, 
    direction: Direction
) -> float:
    epsilon = np.inf

    # Find a eps such that the the privacy profile of the random allocation in the add direction is bounded by delta/2
    # The bound used is based on the decomposition method
    eps_result = search_function_with_bounds(
        func=optimization_func, 
        y_target=delta/2, 
        bounds=(1e-5, 10),
        tolerance=1e-2, 
        function_type=FunctionType.DECREASING
    )

    # If we find a eps, we can compute the sampling probability
    if eps_result is not None:
        sampling_prob = sampling_probability*np.exp(2 * eps_result)/num_steps

        # if the induced sampling probability is small enough, we can compute the corresponding Poisson epsilon
        if sampling_prob <= np.sqrt(1/num_steps):
            params_Poisson = PrivacyParams(
                sigma=sigma,
                num_steps=num_steps,
                num_selected=1,
                num_epochs=num_epochs,
                epsilon=None,  
                delta=delta/2 
            )
            epsilon = float(Poisson_epsilon_PLD(params=params_Poisson,
                                              config=config,
                                              sampling_prob=sampling_prob,
                                              direction=direction))
    return epsilon

def allocation_epsilon_recursive(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute epsilon for the recursive allocation scheme.
    
    Args:
        params: Privacy parameters (must include delta)
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Computed epsilon value
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")
        
    num_steps_per_round = int(np.ceil(params.num_steps/params.num_selected))
    num_rounds = int(np.ceil(params.num_steps/num_steps_per_round))
    
    # We use the decomposition method to compute the tail bound, and we have to optimize over epsilon'.
    # Since recomputing the Poisson PLD is expensive, we re-implement the decomposition method for the add direction,
    # compute the PLD once, and optimize only over epsilon' to delta/2 conversion.
    tail_Poisson_PLD = Poisson_PLD(
        sigma=params.sigma, 
        num_steps=num_steps_per_round, 
        num_epochs=1, 
        sampling_prob=params.sampling_probability/num_steps_per_round, 
        discretization=config.discretization, 
        direction=Direction.ADD,
    )
    if direction != Direction.ADD:
        optimization_func = lambda eps: allocation_delta_decomposition_add_from_PLD(epsilon=eps, 
                                                                                    num_steps=num_steps_per_round, Poisson_PLD_obj=tail_Poisson_PLD) \
                                        * (np.exp(-eps)/(np.exp(eps) -1)) * num_rounds*params.num_epochs
        epsilon_remove = allocation_epsilon_recursive_inner(sigma=params.sigma, delta=params.delta,
                                                           num_steps=num_steps_per_round,
                                                           num_epochs=num_rounds*params.num_epochs,
                                                           sampling_probability=params.sampling_probability,
                                                           config=config,
                                                           optimization_func=optimization_func,
                                                           direction=Direction.REMOVE)

    if direction != Direction.REMOVE:
        optimization_func = lambda eps: allocation_delta_decomposition_add_from_PLD(epsilon=eps, 
                                                                                    num_steps=num_steps_per_round, Poisson_PLD_obj=tail_Poisson_PLD) \
                                        * (np.exp(eps)/(np.exp(eps) -1)) * num_rounds*params.num_epochs
        epsilon_add = allocation_epsilon_recursive_inner(sigma=params.sigma, delta=params.delta,
                                                         num_steps=num_steps_per_round,
                                                         num_epochs=num_rounds*params.num_epochs,
                                                         sampling_probability=params.sampling_probability,
                                                         config=config,
                                                         optimization_func=optimization_func,
                                                         direction=Direction.ADD)
    
    if direction == Direction.ADD:
        assert 'epsilon_add' in locals(), "Failed to compute epsilon_add"
        return float(epsilon_add)
    if direction == Direction.REMOVE:
        assert 'epsilon_remove' in locals(), "Failed to compute epsilon_remove"
        return float(epsilon_remove)
    
    # Both directions, return max of the two
    assert 'epsilon_add' in locals() and 'epsilon_remove' in locals(), "Failed to compute either epsilon_add or epsilon_remove"
    return float(max(epsilon_add, epsilon_remove))

def allocation_delta_recursive(params: PrivacyParams, config: SchemeConfig, direction: Direction = Direction.BOTH) -> float:
    """
    Compute delta for the recursive allocation scheme.
    
    Args:
        params: Privacy parameters (must include epsilon)
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        Computed delta value
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    
    num_steps_per_round = int(np.ceil(params.num_steps/params.num_selected))
    num_rounds = int(np.ceil(params.num_steps/num_steps_per_round))

    delta_add: float  # type annotation without initialization
    delta_remove: float  # type annotation without initialization

    gamma = min(params.epsilon/2, np.log(max(2.0, params.num_steps))/4)
    eta = min(np.exp(2*gamma)/params.num_steps, 1.0)
    params_gamma = PrivacyParams(
        sigma=params.sigma,
        num_steps=num_steps_per_round,
        num_selected=1,
        num_epochs=1,
        epsilon=gamma,
        delta=None
    )
    params_Poisson = PrivacyParams(
        sigma=params.sigma,
        num_steps=num_steps_per_round,
        num_selected=1,
        num_epochs=num_rounds*params.num_epochs,
        epsilon=params.epsilon,  
        delta=None, 
    )

    if direction != Direction.ADD:
        delta_add_decomposition = allocation_delta_decomposition(params=params_gamma, config=config, direction=Direction.ADD)
        delta_add_direct = allocation_delta_direct(params=params_gamma, config=config, direction=Direction.ADD) if params.sampling_probability == 1.0 else 1.0
        delta_remove = Poisson_delta_PLD(
            params=params_Poisson, 
            config=config, 
            sampling_prob=eta, 
            direction=Direction.REMOVE
        ) + 1/(np.exp(2*gamma)-np.exp(gamma)) * min(delta_add_decomposition, delta_add_direct)
        # Protected conversion: ensure delta doesn't exceed 1.0
        delta_remove = min(delta_remove, 1.0)
    
    if direction != Direction.REMOVE:
        if params.epsilon > 0.5:
            delta_add = allocation_delta_decomposition(params=params, config=config, direction=Direction.ADD)
        else:
            delta_add_decomposition = allocation_delta_decomposition(params=params_gamma, config=config, direction=Direction.ADD)
            delta_add_direct = allocation_delta_direct(params=params_gamma, config=config, direction=Direction.ADD) if params.sampling_probability == 1.0 else 1.0
            delta_add = Poisson_delta_PLD(
                params=params_Poisson, 
                config=config, 
                sampling_prob=eta, 
                direction=Direction.ADD
            ) + np.exp(gamma)/(np.exp(gamma)-1) * min(delta_add_decomposition, delta_add_direct)
            # Protected conversion: ensure delta doesn't exceed 1.0
            delta_add = min(delta_add, 1.0)

    if direction == Direction.ADD:
        assert 'delta_add' in locals(), "Failed to compute delta_add"
        return float(delta_add)
    if direction == Direction.REMOVE:
        assert 'delta_remove' in locals(), "Failed to compute delta_remove"
        return float(delta_remove)
    # Both directions, return max of the two
    assert 'delta_add' in locals() and 'delta_remove' in locals(), "Failed to compute either delta_add or delta_remove"
    return float(max(delta_add, delta_remove))


def allocation_PLD_recursive(params: PrivacyParams, config: SchemeConfig, delta: float) -> privacy_loss_distribution.PrivacyLossDistribution:
    num_steps_per_round = int(np.ceil(params.num_steps/params.num_selected))
    num_rounds = int(np.ceil(params.num_steps/num_steps_per_round))

    params_gamma = PrivacyParams(
        sigma=params.sigma,
        num_steps=num_steps_per_round,
        num_selected=1,
        num_epochs=1,
        epsilon=None,
        delta=delta/num_rounds
    )
    # gamma = min(allocation_epsilon_decomposition(params=params_gamma, config=config, direction=Direction.ADD), 1.0 - 1.0/num_steps_per_round)
    gamma = allocation_epsilon_decomposition(params=params_gamma, config=config, direction=Direction.ADD)
    print(f"gamma: {gamma}")
    gamma = min(gamma, 1.0 - 1.0/num_steps_per_round)
    eta = min(1.0, 1.0/((1-gamma)*num_steps_per_round))  # Clamp to [0, 1] to avoid numerical issues
    print(f"eta: {eta}")

    PoissonPLD = Poisson_PLD(
        sigma=params.sigma,
        num_steps=num_steps_per_round,
        num_epochs=num_rounds*params.num_epochs,
        sampling_prob=eta,
        discretization=config.discretization,
        direction=Direction.BOTH,
    )
    return scale_pld_infinity_mass(PoissonPLD, delta)

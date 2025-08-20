# Standard library imports
from typing import List, Optional, cast

# Third-party imports
from dp_accounting import pld, dp_event, rdp
import numpy as np
from numpy.typing import NDArray

# Local application imports
from random_allocation.comparisons.structs import PrivacyParams, SchemeConfig
from random_allocation.comparisons.structs import Direction, Verbosity


# ==================== PLD ====================
def create_zero_pmf(discretization: float) -> pld.privacy_loss_distribution.pld_pmf.PLDPmf:
    """
    Create a PMF that represents zero privacy loss.
    
    This creates a PMF with all probability mass at privacy loss = 0.
    When composed with itself, it remains a zero privacy loss distribution,
    which avoids numerical overflow issues during composition.
    
    Args:
        discretization: The discretization parameter for the PMF
        
    Returns:
        A PMF object representing zero privacy loss
    """
    # Create a PMF with all probability mass at privacy loss = 0
    # This is a true representation of zero privacy loss
    return pld.privacy_loss_distribution.pld_pmf.create_pmf(
        loss_probs={0: 1.0},  # All probability mass at privacy loss = 0
        discretization=discretization,
        infinity_mass=0.0,
        pessimistic_estimate=True
    )

def Poisson_PLD(sigma: float,
                num_steps: int,
                num_epochs: int,
                sampling_prob: float,
                discretization: float,
                direction: Direction,
                ) -> pld.privacy_loss_distribution.PrivacyLossDistribution:
    """
    Calculate the privacy loss distribution (PLD) for the Poisson scheme with the Gaussian mechanism.

    Parameters:
    - sigma: The standard deviation of the Gaussian mechanism.
    - num_steps: The number of steps in each epoch.
    - sampling_prob: The probability of sampling.
    - num_epochs: The number of epochs.
    - discretization: The discretization interval for the pld.
    - direction: The direction of the pld. Can be 'add', 'remove', or 'both'.
    """
    total_compositions = num_steps * num_epochs
    
    # Create the standard Gaussian PLD
    Gauss_PLD = pld.privacy_loss_distribution.from_gaussian_mechanism(
        standard_deviation=sigma,
        value_discretization_interval=discretization,
        pessimistic_estimate=True,
        sampling_prob=sampling_prob,
        use_connect_dots=True
    )
    
    # For "both" direction, just use the Gaussian PLD directly
    if direction == Direction.BOTH:
        return Gauss_PLD.self_compose(total_compositions)
    
    # For add or remove directions, use our zero privacy loss PMF
    # This PMF has all mass at privacy loss = 0, which is stable under composition
    zero_pmf = create_zero_pmf(discretization)
    
    # Create the appropriate PLD based on direction
    if direction == Direction.ADD:
        # For add direction, use zero_pmf for pmf_remove (no privacy loss when removing)
        PLD_single = pld.privacy_loss_distribution.PrivacyLossDistribution(
            pmf_remove=zero_pmf,
            pmf_add=Gauss_PLD._pmf_add
        )
    elif direction == Direction.REMOVE:
        # For remove direction, use zero_pmf for pmf_add (no privacy loss when adding)
        PLD_single = pld.privacy_loss_distribution.PrivacyLossDistribution(
            pmf_remove=Gauss_PLD._pmf_remove,
            pmf_add=zero_pmf
        )
    
    # Directly compose and return the PLD without any fallback mechanism
    return PLD_single.self_compose(total_compositions)

def Poisson_epsilon_PLD(params: PrivacyParams,
                        config: SchemeConfig,
                        sampling_prob: float = 0.0,
                        direction: Direction = Direction.BOTH,
                        ) -> float:
    """
    Calculate the epsilon value for the Poisson scheme with the Gaussian mechanism based on pld.

    Parameters:
    - params: Privacy parameters
    - config: Scheme configuration
    - sampling_prob: The probability of sampling
    - direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")
    if params.sampling_probability < 1.0:
        raise ValueError("Poisson PLD method only supports sampling_probability=1.0")

    if sampling_prob == 0.0:
        sampling_prob = params.num_selected / params.num_steps
    
    PLD = Poisson_PLD(
        sigma=params.sigma, 
        num_steps=params.num_steps, 
        num_epochs=params.num_epochs, 
        sampling_prob=sampling_prob,
        discretization=config.discretization, 
        direction=direction
    )
    return float(PLD.get_epsilon_for_delta(params.delta))

def Poisson_delta_PLD(params: PrivacyParams,
                      config: SchemeConfig,
                      sampling_prob: float = 0.0,
                      direction: Direction = Direction.BOTH,
                      ) -> float:
    """
    Calculate the delta value for the Poisson scheme with the Gaussian mechanism based on pld.

    Parameters:
    - params: Privacy parameters
    - config: Scheme configuration
    - sampling_prob: The probability of sampling
    - direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    if params.sampling_probability < 1.0:
        raise ValueError("Poisson PLD method only supports sampling_probability=1.0")

    if sampling_prob == 0.0:
        sampling_prob = params.num_selected / params.num_steps
    
    PLD = Poisson_PLD(
        sigma=params.sigma, 
        num_steps=params.num_steps, 
        num_epochs=params.num_epochs, 
        sampling_prob=sampling_prob,
        discretization=config.discretization, 
        direction=direction
    )
    return float(PLD.get_delta_for_epsilon(params.epsilon))


# ==================== RDP ====================
def Poisson_RDP(sigma: float,
                num_steps: int,
                num_epochs: int,
                sampling_prob: float,
                alpha_orders: Optional[List[float]] = None,
                ) -> rdp.RdpAccountant:
    """
    Create an RDP accountant for the Poisson scheme with the Gaussian mechanism.

    Parameters:
    - sigma: The standard deviation of the Gaussian mechanism.
    - num_steps: The number of steps in each epoch.
    - num_epochs: The number of epochs.
    - sampling_prob: The probability of sampling.
    - alpha_orders: The list of alpha orders for rdp. If None, defaults will be used by RdpAccountant.
    """
    accountant = rdp.RdpAccountant(alpha_orders)
    event = dp_event.PoissonSampledDpEvent(sampling_prob, dp_event.GaussianDpEvent(sigma))
    accountant.compose(event, int(num_steps*num_epochs))
    return accountant

def Poisson_delta_RDP(params: PrivacyParams,
                      config: SchemeConfig,
                      direction: Direction = Direction.BOTH,
                      ) -> float:
    """
    Calculate the delta value for the Poisson scheme with the Gaussian mechanism based on rdp.

    Parameters:
    - params: Privacy parameters
    - config: Scheme configuration
    - direction: The direction of privacy. Currently only BOTH is supported.
    """
    if params.epsilon is None:
        raise ValueError("Epsilon must be provided to compute delta")
    if params.sampling_probability < 1.0:
        raise ValueError("Poisson RDP method only supports sampling_probability=1.0")
    if direction != Direction.BOTH:
        raise ValueError("Poisson RDP only supports Direction.BOTH")
    
    sampling_prob = params.num_selected / params.num_steps
    
    accountant = Poisson_RDP(
        sigma=params.sigma, 
        num_steps=params.num_steps, 
        num_epochs=params.num_epochs, 
        sampling_prob=sampling_prob,
        alpha_orders=config.Poisson_alpha_orders
    )
    
    if config.verbosity == Verbosity.ALL:
        delta, used_alpha = accountant.get_delta_and_optimal_order(params.epsilon)
        print(f'sigma: {params.sigma}, num_steps: {params.num_steps}, num_epochs: {params.num_epochs}, '
              f'sampling_prob: {sampling_prob}, used_alpha: {used_alpha}')
        return float(delta)
    
    return float(accountant.get_delta(params.epsilon))

def Poisson_epsilon_RDP(params: PrivacyParams,
                        config: SchemeConfig,
                        sampling_prob: float = 0.0,
                        direction: Direction = Direction.BOTH,
                        ) -> float:
    """
    Calculate the epsilon value for the Poisson scheme with the Gaussian mechanism based on rdp.

    Parameters:
    - params: Privacy parameters
    - config: Scheme configuration
    - sampling_prob: The probability of sampling
    - direction: The direction of privacy. Currently only BOTH is supported.
    """
    if params.delta is None:
        raise ValueError("Delta must be provided to compute epsilon")
    if params.sampling_probability < 1.0:
        raise ValueError("Poisson RDP method only supports sampling_probability=1.0")
    if direction != Direction.BOTH:
        raise ValueError("Poisson RDP only supports Direction.BOTH")

    if sampling_prob == 0.0:
        sampling_prob = params.num_selected / params.num_steps
    
    accountant = Poisson_RDP(
        sigma=params.sigma, 
        num_steps=params.num_steps, 
        num_epochs=params.num_epochs, 
        sampling_prob=sampling_prob,
        alpha_orders=config.Poisson_alpha_orders
    )
    
    if config.verbosity == Verbosity.ALL:
        epsilon, used_alpha = accountant.get_epsilon_and_optimal_order(params.delta)
        print(f'sigma: {params.sigma}, num_steps: {params.num_steps}, num_epochs: {params.num_epochs}, '
              f'sampling_prob: {sampling_prob}, used_alpha: {used_alpha}')
        return float(epsilon)
    
    return float(accountant.get_epsilon(params.delta))
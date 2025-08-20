"""
Common definitions for privacy parameters, scheme configurations, and experiment configuration.
"""

# Standard library imports
from enum import Enum
from typing import Dict, List, Callable, Union

# Local application imports
from random_allocation.comparisons.structs import MethodFeatures
from random_allocation.other_schemes.local import *
from random_allocation.other_schemes.poisson import *
from random_allocation.other_schemes.shuffle import *
from random_allocation.random_allocation_scheme import *

# Type aliases
MethodName = str
FeatureName = str
FeatureValue = Union[str, Callable[..., float], None]
FeaturesDict = Dict[MethodName, FeatureValue]

#======================= Variables =======================
EPSILON: str = 'epsilon'
DELTA: str = 'delta'
SIGMA: str = 'sigma'
NUM_STEPS: str = 'num_steps'
NUM_SELECTED: str = 'num_selected'
NUM_EPOCHS: str = 'num_epochs'
VARIABLES: List[str] = [EPSILON, DELTA, SIGMA, NUM_STEPS, NUM_SELECTED, NUM_EPOCHS]

names_dict: Dict[str, str] = {
    EPSILON: r'\varepsilon',
    DELTA: r'\delta',
    SIGMA: r'\sigma',
    NUM_STEPS: r't',
    NUM_SELECTED: r'k',
    NUM_EPOCHS: r'E'
}

# ======================= Schemes =======================
LOCAL: str = 'Local'
POISSON: str = 'Poisson'
ALLOCATION: str = 'Allocation'
SHUFFLE: str = 'Shuffle'
LOWER_BOUND: str = 'Lower Bound'

colors_dict: Dict[str, str] = {LOCAL: '#FF0000', POISSON: '#2BB22C', ALLOCATION: '#157DED', SHUFFLE: '#FF00FF', LOWER_BOUND: '#FF7F00'}

# ======================= Computation =======================
ANALYTIC: str = 'Analytic'
MONTE_CARLO: str = 'Monte Carlo'
PLD: str = 'PLD'
RDP: str = 'RDP'
DECOMPOSITION: str = 'Decomposition'
INVERSE: str = 'Inverse'
COMBINED: str = 'Combined'
RECURSIVE: str = 'Recursive'

# ======================= Methods =======================
POISSON_PLD: str                 = f'{POISSON} ({PLD})'
POISSON_RDP: str                 = f'{POISSON} ({RDP})'
ALLOCATION_ANALYTIC: str         = f'{ALLOCATION} (Our - {ANALYTIC})'
ALLOCATION_DIRECT: str           = f'{ALLOCATION} (Our - Direct)'
ALLOCATION_RDP_DCO: str          = f'{ALLOCATION} (DCO25 - {RDP})'
ALLOCATION_DECOMPOSITION: str    = f'{ALLOCATION} (Our - {DECOMPOSITION})'
ALLOCATION_COMBINED: str         = f'{ALLOCATION} (Our - {COMBINED})'
ALLOCATION_RECURSIVE: str        = f'{ALLOCATION} (Our - {RECURSIVE})'
ALLOCATION_MONTE_CARLO: str      = f'{ALLOCATION} (CGHKKLMSZ24 - {MONTE_CARLO})'
ALLOCATION_LOWER_BOUND: str      = f'{ALLOCATION} (CGHKKLMSZ24 - {LOWER_BOUND})'


# ======================= Methods Features =======================

methods_dict: Dict[str, MethodFeatures] = {
    LOCAL: MethodFeatures(
        name=LOCAL,
        epsilon_calculator=local_epsilon,
        delta_calculator=local_delta,
        legend=r'$\varepsilon_{\mathcal{L}}$ - ' + LOCAL,
        marker='*',
        color=colors_dict[LOCAL]
    ),
    POISSON_PLD: MethodFeatures(
        name=POISSON_PLD,
        epsilon_calculator=Poisson_epsilon_PLD,
        delta_calculator=Poisson_delta_PLD,
        legend=r'$\varepsilon_{\mathcal{P}}$ - ' + POISSON_PLD,
        marker='x',
        color=colors_dict[POISSON]
    ),
    POISSON_RDP: MethodFeatures(
        name=POISSON_RDP,
        epsilon_calculator=Poisson_epsilon_RDP,
        delta_calculator=Poisson_delta_RDP,
        legend=r'$\varepsilon_{\mathcal{P}}$ - ' + POISSON_RDP,
        marker='v',
        color=colors_dict[POISSON]
    ),
    SHUFFLE: MethodFeatures(
        name=SHUFFLE,
        epsilon_calculator=shuffle_epsilon_analytic,
        delta_calculator=shuffle_delta_analytic,
        legend=r'$\varepsilon_{\mathcal{S}}$ - ' + SHUFFLE,
        marker='p',
        color=colors_dict[SHUFFLE]
    ),
    ALLOCATION_ANALYTIC: MethodFeatures(
        name=ALLOCATION_ANALYTIC,
        epsilon_calculator=allocation_epsilon_analytic,
        delta_calculator=allocation_delta_analytic,
        legend=r'$\varepsilon_{\mathcal{A}}$ - ' + ALLOCATION_ANALYTIC,
        marker='P',
        color=colors_dict[ALLOCATION]
    ),
    ALLOCATION_DIRECT: MethodFeatures(
        name=ALLOCATION_DIRECT,
        epsilon_calculator=allocation_epsilon_direct,
        delta_calculator=allocation_delta_direct,
        legend=r'$\varepsilon_{\mathcal{A}}$ - ' + ALLOCATION_DIRECT,
        marker='^',
        color=colors_dict[ALLOCATION]
    ),
    ALLOCATION_RDP_DCO: MethodFeatures(
        name=ALLOCATION_RDP_DCO,
        epsilon_calculator=allocation_epsilon_RDP_DCO,
        delta_calculator=allocation_delta_RDP_DCO,
        legend=r'$\varepsilon_{\mathcal{A}}$ - ' + ALLOCATION_RDP_DCO,
        marker='o',
        color=colors_dict[ALLOCATION]
    ),
    ALLOCATION_DECOMPOSITION: MethodFeatures(
        name=ALLOCATION_DECOMPOSITION,
        epsilon_calculator=allocation_epsilon_decomposition,
        delta_calculator=allocation_delta_decomposition,
        legend=r'$\varepsilon_{\mathcal{A}}$ - ' + ALLOCATION_DECOMPOSITION,
        marker='X',
        color=colors_dict[ALLOCATION]
    ),
    ALLOCATION_COMBINED: MethodFeatures(
        name=ALLOCATION_COMBINED,
        epsilon_calculator=allocation_epsilon_combined,
        delta_calculator=allocation_delta_combined,
        legend=r'$\varepsilon_{\mathcal{A}}$ - ' + ALLOCATION_COMBINED,
        marker='s',
        color=colors_dict[ALLOCATION]
    ),
    ALLOCATION_RECURSIVE: MethodFeatures(
        name=ALLOCATION_RECURSIVE,
        epsilon_calculator=allocation_epsilon_recursive,
        delta_calculator=allocation_delta_recursive,
        legend=r'$\varepsilon_{\mathcal{A}}$ - ' + ALLOCATION_RECURSIVE,
        marker='h',
        color=colors_dict[ALLOCATION]
    ),
    ALLOCATION_MONTE_CARLO: MethodFeatures(
        name=ALLOCATION_MONTE_CARLO,
        epsilon_calculator=None,
        delta_calculator=allocation_delta_MC,
        legend=r'$\varepsilon_{\mathcal{A}}$ - ' + ALLOCATION_MONTE_CARLO,
        marker='D',
        color=colors_dict[ALLOCATION]
    ),
    ALLOCATION_LOWER_BOUND: MethodFeatures(
        name=ALLOCATION_LOWER_BOUND,
        epsilon_calculator=allocation_epsilon_lower_bound,
        delta_calculator=allocation_delta_lower_bound,
        legend=r'$\varepsilon_{\mathcal{A}}$ - ' + ALLOCATION_LOWER_BOUND,
        marker='d',
        color=colors_dict[LOWER_BOUND]
    )
}

def get_features_for_methods(methods: List[MethodName], feature: FeatureName) -> Dict[MethodName, FeatureValue]:
    """
    Extract a specific feature for a list of methods using the global methods_dict.
    
    Args:
        methods: List of method keys
        feature: Name of the feature to extract
        
    Returns:
        Dictionary mapping method names to their feature values
    """
    try:
        return {method: getattr(methods_dict[method], feature) for method in methods}
    except KeyError as e:
        raise KeyError(f"Invalid method key: {e}")
    except AttributeError as e:
        raise AttributeError(f"Invalid feature name: {feature}")
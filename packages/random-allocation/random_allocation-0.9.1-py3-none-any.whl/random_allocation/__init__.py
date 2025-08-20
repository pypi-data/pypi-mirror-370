"""
Random Allocation for Differential Privacy

This package provides tools for analyzing and comparing different random allocation schemes
in the context of differential privacy.
"""

# Local application imports
from random_allocation.comparisons.experiments import run_experiment, PlotType
from random_allocation.comparisons.visualization import plot_comparison, plot_combined_data, plot_as_table
from random_allocation.comparisons.definitions import (
    ALLOCATION, ALLOCATION_ANALYTIC, ALLOCATION_DIRECT, ALLOCATION_DECOMPOSITION,
    EPSILON, DELTA, VARIABLES, methods_dict, names_dict, colors_dict
)
from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig
from random_allocation.random_allocation_scheme import (
    allocation_epsilon_analytic, allocation_delta_analytic,
    allocation_epsilon_direct, allocation_delta_direct,
    allocation_epsilon_RDP_DCO, allocation_delta_RDP_DCO,
    allocation_epsilon_decomposition, allocation_delta_decomposition
)

__all__ = [
    # Parameter and configuration classes
    'PrivacyParams',
    'SchemeConfig',
    
    # Experiment functions
    'run_experiment',
    'PlotType',
    
    # Plotting functions
    'plot_comparison',
    'plot_combined_data',
    'plot_as_table',
    
    # Constants and configurations
    'ALLOCATION',
    'ALLOCATION_ANALYTIC',
    'ALLOCATION_DIRECT',
    'ALLOCATION_DECOMPOSITION',
    'EPSILON',
    'DELTA',
    'VARIABLES',
    'methods_dict',
    'names_dict',
    'colors_dict',
    
    # Core allocation functions
    'allocation_epsilon_analytic',
    'allocation_delta_analytic',
    'allocation_epsilon_direct',
    'allocation_delta_direct',
    'allocation_epsilon_RDP_DCO',
    'allocation_delta_RDP_DCO',
    'allocation_epsilon_decomposition',
    'allocation_delta_decomposition'
]
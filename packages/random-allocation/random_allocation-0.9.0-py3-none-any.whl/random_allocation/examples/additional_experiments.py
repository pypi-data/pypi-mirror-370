#!/usr/bin/env python
# Standard library imports
import os
import sys
from typing import Dict, List, Union, Any, Callable, Tuple

# Add the correct project root directory to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party imports
import numpy as np
import matplotlib.pyplot as plt

# Local application imports
from random_allocation.comparisons.definitions import *
from random_allocation.comparisons.experiments import *
from random_allocation.comparisons.visualization import *
from random_allocation.examples.utility_comparison import (
    run_utility_experiments, plot_utility_comparison,
    save_utility_experiment_data, load_utility_experiment_data
)


# Configuration
READ_DATA: bool = False  # Set to True to try reading data from existing files first
SAVE_DATA: bool = True  # Set to True to save computed data to CSV files
SAVE_PLOTS: bool = True  # Set to True to save plots to files
SHOW_PLOTS: bool = False  # Set to True to display plots interactively


def run_experiment_1():
    """
    First experiment - Compare different schemes for the same parameters as the Chau et al. experiments
    """    
    SCL_8192_params_dict = {
        'x_var': SIGMA,
        'y_var': EPSILON,
        SIGMA: np.linspace(0.1, 0.5, 5),
        DELTA: 1e-7,
        NUM_STEPS: 1_563,
        NUM_SELECTED: 1,
        NUM_EPOCHS: 1
    }

    pCTR_8192_params_dict = {
        'x_var': SIGMA,
        'y_var': EPSILON,
        SIGMA: np.linspace(0.1, 0.5, 5),
        DELTA: 1e-7,
        NUM_STEPS: 4_492,
        NUM_SELECTED: 1,
        NUM_EPOCHS: 1
    }

    SCL_1024_params_dict = {
        'x_var': SIGMA,
        'y_var': EPSILON,
        SIGMA: np.linspace(0.1, 0.5, 5),
        DELTA: 1e-7,
        NUM_STEPS: 12_500,
        NUM_SELECTED: 1,
        NUM_EPOCHS: 1
    }

    pCTR_1024_params_dict = {
        'x_var': SIGMA,
        'y_var': EPSILON,
        SIGMA: np.linspace(0.1, 0.5, 5),
        DELTA: 1e-7,
        NUM_STEPS: 35_938,
        NUM_SELECTED: 1,
        NUM_EPOCHS: 1
    }

    config = SchemeConfig(allocation_direct_alpha_orders=[int(i) for i in np.arange(2, 61, dtype=int)])

    methods_all = [LOCAL, POISSON_PLD, ALLOCATION_DIRECT, ALLOCATION_RECURSIVE, ALLOCATION_DECOMPOSITION]

    visualization_config = {
        'log_x_axis': False, 
        'log_y_axis': True, 
        'format_x': lambda x, _: f'{x:.1f}'
    }

    print("Running experiment 1.1: Compare different schemes for varying sigma using the Criteo Sponsored Search Conversion Log dataset with expected batch size of 8192")
    SCL_8192_data = run_experiment(
        params_dict=SCL_8192_params_dict, 
        config=config, 
        methods=methods_all, 
        visualization_config=visualization_config, 
        experiment_name='Criteo SCL - 8192', 
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.BOTH
    )

    print("Running experiment 1.2: Compare different schemes for varying sigma using the Criteo Display Ads pCTR dataset with expected batch size of 8192")
    pCTR_8192_data = run_experiment(
        params_dict=pCTR_8192_params_dict, 
        config=config, 
        methods=methods_all, 
        visualization_config=visualization_config, 
        experiment_name='Criteo pCTR - 8192', 
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.BOTH
    )

    print("Running experiment 1.3: Compare different schemes for varying sigma using the Criteo Sponsored Search Conversion Log dataset with expected batch size of 1024")
    SCL_1024_data = run_experiment(
        params_dict=SCL_1024_params_dict, 
        config=config, 
        methods=methods_all, 
        visualization_config=visualization_config, 
        experiment_name='Criteo SCL - 1024', 
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.BOTH
    )

    print("Running experiment 1.4: Compare different schemes for varying sigma using the Criteo Display Ads pCTR dataset with expected batch size of 1024")
    pCTR_1024_data = run_experiment(
        params_dict=pCTR_1024_params_dict, 
        config=config, 
        methods=methods_all, 
        visualization_config=visualization_config, 
        experiment_name='Criteo pCTR - 1024', 
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.BOTH
    )

def run_experiment_2():
    """
    Second experiment - Monte Carlo comparison experiment for the same parameters as the Chau et al. experiments
    """
    print("Running experiment 2: Monte Carlo comparison experiment for the same parameters as the Chau et al. experiments")

    config = SchemeConfig(
        discretization=1e-4,
        allocation_direct_alpha_orders=[int(i) for i in np.arange(2, 61, dtype=int)],
        delta_tolerance=1e-15,
        epsilon_tolerance=1e-3,
        MC_use_order_stats=True,
        MC_use_mean=False,
        MC_conf_level=0.99,
        MC_sample_size=500_000,
        verbosity=Verbosity.NONE,
    )

    num_steps_arr = [35_938, 4_492, 12_500, 1_563]
    sigma_arr = [0.3, 0.4, 0.3, 0.4]
    epsilon_arr = [np.linspace(1, 10, 10),
                   np.linspace(1, 10, 10),
                   np.linspace(1, 10, 10),
                   np.linspace(1, 10, 10)]
    num_selected = 1
    num_epochs = 1
    experiment_name = 'MC_comparison_Chau_et_al'

    # Data handling logic for experiment 6
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    data_file = os.path.join(data_dir, experiment_name)

    # Try to load existing data if requested
    deltas_dict_arr = None
    epsilon_mat = None
    should_compute_data = True

    if READ_DATA:
        loaded_data = load_privacy_curves_data(data_file)
        if loaded_data is not None:
            deltas_dict_arr, epsilon_mat, _, _ = loaded_data
            should_compute_data = False

    # Compute data if needed (either we're not reading or loading failed)
    if should_compute_data:
        params_mat = [[PrivacyParams(num_steps=num_steps, sigma=sigma, epsilon=epsilon, 
                                   num_selected=num_selected, num_epochs=num_epochs) 
                     for epsilon in epsilon_arr] 
                    for num_steps, sigma, epsilon_arr in zip(num_steps_arr, sigma_arr, epsilon_arr)]
        
        # Calculate deltas for all methods
        deltas_dict_arr = [calc_all_methods_delta(params_arr, config) for params_arr in params_mat]
        epsilon_mat = epsilon_arr
        
        # Save data if requested
        if SAVE_DATA:
            save_privacy_curves_data(deltas_dict_arr, epsilon_mat, num_steps_arr, sigma_arr, data_file)

    # Create plot titles and figure
    subplot_titles = [f"$t$ = {num_steps:,}, $\\sigma$ = {sigma}" for num_steps, sigma in zip(num_steps_arr, sigma_arr)]
    fig = plot_privacy_curves(deltas_dict_arr, epsilon_mat, subplot_titles)

    if SAVE_PLOTS:
        plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        fig.savefig(os.path.join(plots_dir, 'MC_comparison_plot.png'))
    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close(fig)
        
    return fig

def main():
    """
    Run all experiments in sequence
    """
    print("Starting paper experiments...")
    run_experiment_1()
    run_experiment_2()
    print("All experiments completed successfully.")


if __name__ == "__main__":
    main()

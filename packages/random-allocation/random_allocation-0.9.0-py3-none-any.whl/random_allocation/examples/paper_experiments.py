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
    First experiment - Compare different schemes for varying sigma
    """
    print("Running experiment 1: Compare different schemes for varying sigma")
    
    params_dict = {
        'x_var': SIGMA,
        'y_var': EPSILON,
        SIGMA: np.exp(np.linspace(np.log(0.2), np.log(2), 20)),
        DELTA: 1e-10,
        NUM_STEPS: 100_000,
        NUM_SELECTED: 1,
        NUM_EPOCHS: 1
    }

    config = SchemeConfig(allocation_direct_alpha_orders=[int(i) for i in np.arange(2, 61, dtype=int)])

    methods_all = [LOCAL, SHUFFLE, POISSON_PLD, ALLOCATION_DIRECT, ALLOCATION_RECURSIVE, ALLOCATION_DECOMPOSITION]
    methods_add_rem = [LOCAL, POISSON_PLD, ALLOCATION_DIRECT, ALLOCATION_RECURSIVE, ALLOCATION_DECOMPOSITION]
    methods_several_select = [LOCAL, POISSON_PLD, ALLOCATION_DIRECT, ALLOCATION_RECURSIVE]

    visualization_config = {
        'log_x_axis': True, 
        'log_y_axis': True, 
        'format_x': lambda x, _: f'{x:.2f}'
    }

    data_both = run_experiment(
        params_dict=params_dict, 
        config=config, 
        methods=methods_all, 
        visualization_config=visualization_config, 
        experiment_name='main', 
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.BOTH
    )

    data_add = run_experiment(
        params_dict=params_dict, 
        config=config, 
        methods=methods_add_rem, 
        visualization_config=visualization_config, 
        experiment_name='main_add', 
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.ADD
    )

    data_rem = run_experiment(
        params_dict=params_dict, 
        config=config, 
        methods=methods_add_rem, 
        visualization_config=visualization_config, 
        experiment_name='main_remove',     
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.REMOVE
    )

    params_dict_several_select = {
        'x_var': SIGMA,
        'y_var': EPSILON,
        SIGMA: np.exp(np.linspace(np.log(0.5), np.log(4), 20)),
        DELTA: 1e-10,
        NUM_STEPS: 100_000,
        NUM_SELECTED: 10,
        NUM_EPOCHS: 1
    }

    data_several_select_add = run_experiment(
        params_dict=params_dict_several_select, 
        config=config, 
        methods=methods_several_select, 
        visualization_config=visualization_config, 
        experiment_name='main_several_select_add', 
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.ADD
    )

    data_several_select_rem = run_experiment(
        params_dict=params_dict_several_select, 
        config=config, 
        methods=methods_several_select, 
        visualization_config=visualization_config, 
        experiment_name='main_several_select_remove',     
        plot_type=PlotType.COMBINED,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.REMOVE
    )

def run_experiment_2():
    """
    Second experiment - Compare different schemes for varying number of epochs
    """
    print("Running experiment 2: Compare different schemes for varying number of epochs")
    
    params_dict = {
        'x_var': NUM_EPOCHS,
        'y_var': EPSILON,
        SIGMA: 1,
        DELTA: 1e-8,
        NUM_STEPS: 10_000,
        NUM_SELECTED: 1,
        NUM_EPOCHS: np.exp(np.linspace(np.log(1), np.log(1001), 10)).astype(int)
    }

    config = SchemeConfig(allocation_direct_alpha_orders=[int(i) for i in np.arange(2, 61, dtype=int)])

    methods = [POISSON_PLD, POISSON_RDP, ALLOCATION_DIRECT]

    visualization_config = {
        'log_x_axis': True, 
        'log_y_axis': False, 
        'format_x': lambda x, _: str(int(x))
    }

    data = run_experiment(
        params_dict=params_dict, 
        config=config, 
        methods=methods, 
        visualization_config=visualization_config, 
        experiment_name='multi_epoch', 
        plot_type=PlotType.COMPARISON,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.BOTH
    )


def run_experiment_3():
    """
    Third experiment - Compare different schemes for varying number of steps
    """
    print("Running experiment 3: Compare different schemes for varying number of steps")
    
    params_dict = {
        'x_var': NUM_STEPS,
        'y_var': EPSILON,
        SIGMA: 0.3,
        DELTA: 1e-4,
        NUM_STEPS: np.arange(25, 551, 50),
        NUM_SELECTED: 1,
        NUM_EPOCHS: 1
    }

    config = SchemeConfig(allocation_direct_alpha_orders=[int(i) for i in np.arange(2, 61, dtype=int)])

    methods = [POISSON_RDP, POISSON_PLD, ALLOCATION_DIRECT, ALLOCATION_DECOMPOSITION]

    visualization_config = {
        'log_x_axis': False, 
        'log_y_axis': False, 
        'format_x': lambda x, _: str(int(x))
    }

    data = run_experiment(
        params_dict=params_dict, 
        config=config, 
        methods=methods, 
        visualization_config=visualization_config, 
        experiment_name='RDP_domination', 
        plot_type=PlotType.COMPARISON,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.BOTH
    )


def run_experiment_4():
    """
    Fourth experiment - Compare different schemes for varying number of selected items
    """
    print("Running experiment 4: Compare different schemes for varying number of selected items")
    
    params_dict = {
        'x_var': NUM_SELECTED,
        'y_var': EPSILON,
        SIGMA: 0.6,
        DELTA: 1e-6,
        NUM_STEPS: 2**10,
        NUM_SELECTED: 2**np.arange(0, 7),
        NUM_EPOCHS: 1,
    }

    config = SchemeConfig(allocation_direct_alpha_orders=[int(i) for i in np.arange(2, 61, dtype=int)])

    methods = [POISSON_RDP, ALLOCATION_DIRECT, ALLOCATION_RDP_DCO]

    visualization_config = {
        'log_x_axis': True, 
        'log_y_axis': True, 
        'format_x': lambda x, _: str(int(x))
    }

    data = run_experiment(
        params_dict=params_dict,
        config=config,
        methods=methods,
        visualization_config=visualization_config,
        experiment_name='DCO_comp',
        plot_type=PlotType.COMPARISON,
        read_data=READ_DATA,
        save_data=SAVE_DATA,
        save_plots=SAVE_PLOTS,
        show_plots=SHOW_PLOTS,
        direction=Direction.BOTH
    )


def run_experiment_5():
    """
    Fifth experiment - Multi-plot experiment for multiple step values
    """
    print("Running experiment 5: Multi-plot experiment for multiple step values")
    
    config = SchemeConfig(allocation_direct_alpha_orders=[int(i) for i in np.arange(2, 61, dtype=int)])

    methods = [POISSON_PLD, ALLOCATION_RDP_DCO, ALLOCATION_COMBINED, ALLOCATION_LOWER_BOUND]

    visualization_config = {
        'log_x_axis': True, 
        'log_y_axis': False, 
        'format_x': lambda x, _: f'{x:.2f}'
    }

    # Define parameters for experiments with different steps values
    params_dict_list = [
        {
            'x_var': SIGMA,
            'y_var': EPSILON,
            SIGMA: np.exp(np.linspace(np.log(0.8), np.log(2.5), 10)),
            DELTA: 1e-10,
            NUM_STEPS: 100,
            NUM_SELECTED: 1,
            NUM_EPOCHS: 1
        },
        {
            'x_var': SIGMA,
            'y_var': EPSILON,
            SIGMA: np.exp(np.linspace(np.log(0.65), np.log(2), 10)),
            DELTA: 1e-10,
            NUM_STEPS: 1_000,
            NUM_SELECTED: 1,
            NUM_EPOCHS: 1
        },
        {
            'x_var': SIGMA,
            'y_var': EPSILON,
            SIGMA: np.exp(np.linspace(np.log(0.6), np.log(0.9), 10)),
            DELTA: 1e-10,
            NUM_STEPS: 10_000,
            NUM_SELECTED: 1,
            NUM_EPOCHS: 1
        }
    ]

    # Experiment names
    experiment_names = [
        'epsilon_vs_sigma_small_t',
        'epsilon_vs_sigma_mid_t',
        'epsilon_vs_sigma_large_t'
    ]

    # Run the three experiments
    data_list = []
    for params_dict, experiment_name in zip(params_dict_list, experiment_names):
        data = run_experiment(
            params_dict=params_dict,
            config=config,
            methods=methods,
            visualization_config=visualization_config,
            experiment_name=experiment_name,
            plot_type=PlotType.COMBINED,
            read_data=READ_DATA,
            save_data=SAVE_DATA,
            save_plots=False,  # Don't save individual plots
            show_plots=False,  # Don't show individual plots
            direction=Direction.BOTH
        )
        data_list.append(data)

    # Create titles based on the step values in each parameter dictionary
    titles = [f"$t$ = {params_dict[NUM_STEPS]:,}" for params_dict in params_dict_list]

    # Use the plot_multiple_data function to create a multi-subplot figure
    fig = plot_multiple_data(
        data_list=data_list,
        titles=titles,
        log_x_axis=True,
        log_y_axis=False,
        format_x=lambda x, _: f'{x:.2f}',
        plot_type='epsilon_vs_sigma_combined', 
        figsize=(20, 6),  # Width, height in inches
        grid_layout=(1, 3)  # 1 row, 3 columns
    )

    if SAVE_PLOTS:
        plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        fig.savefig(os.path.join(plots_dir, 'multi_range_plot.png'))
    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close(fig)


def run_experiment_6():
    """
    Sixth experiment - Monte Carlo comparison experiment
    """
    print("Running experiment 6: Monte Carlo comparison experiment")
    
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

    num_steps_arr = [100, 100, 10_000, 10_000]
    sigma_arr = [0.75, 0.5, 0.75, 0.5]
    epsilon_arr = [np.linspace(0.5, 4.0, 10),
                   np.linspace(0.5, 4.0, 10),
                   np.linspace(0.5, 4.0, 10),
                   np.linspace(0.5, 4.0, 10)]
    num_selected = 1
    num_epochs = 1
    experiment_name = 'MC_comparison'

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


def run_experiment_7():
    """
    Seventh experiment - Utility comparison between Poisson and Random Allocation schemes
    
    This experiment compares the utility (mean squared error) of Poisson and Random Allocation schemes
    under different privacy and dimensionality settings.
    """
    print("Running experiment 7: Utility comparison between Poisson and Random Allocation schemes")
    
    # Experiment parameters
    small_eps = 0.1
    large_eps = 1.0
    small_dim = 1
    large_dim = 1_000

    num_steps = 1_000
    num_experiments = 10_000 
    true_mean = 0.9
    delta = 1e-10
    # Use fewer sample size points for faster execution
    sample_size_arr = np.logspace(2, 5, num=7, dtype=int)

    # Visualization parameter
    num_std = 3
    
    # Data handling logic for utility experiment
    experiment_name = 'utility_comparison'
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    data_file = os.path.join(data_dir, experiment_name)
    
    # Try to load existing data if requested
    experiment_data_list = None
    should_compute_data = True
    titles = [
        r"$\varepsilon$ = " + f"{large_eps:.1f}" + r", $d$ = " + f"{small_dim:,}", 
        r"$\varepsilon$ = " + f"{small_eps:.1f}" + r", $d$ = " + f"{small_dim:,}", 
        r"$\varepsilon$ = " + f"{small_eps:.1f}" + r", $d$ = " + f"{large_dim:,}"
    ]
    epsilon_values = [large_eps, small_eps, small_eps]
    dimension_values = [small_dim, small_dim, large_dim]
    
    if READ_DATA:
        loaded_data = load_utility_experiment_data(data_file)
        if loaded_data is not None:
            experiment_data_list, sample_size_arr, titles, num_steps, num_experiments = loaded_data
            should_compute_data = False
            print("Loaded existing utility experiment data")

    # Compute data if needed
    if should_compute_data:
        print("Running utility experiment 1: large epsilon, small dimension...")
        large_eps_small_dim_data = run_utility_experiments(
            epsilon=large_eps,
            delta=delta,
            num_steps=num_steps,
            dimension=small_dim,
            true_mean=true_mean,
            num_experiments=num_experiments,
            sample_size_arr=sample_size_arr
        )

        print("Running utility experiment 2: small epsilon, small dimension...")
        small_eps_small_dim_data = run_utility_experiments(
            epsilon=small_eps,
            delta=delta,
            num_steps=num_steps,
            dimension=small_dim,
            true_mean=true_mean,
            num_experiments=num_experiments,
            sample_size_arr=sample_size_arr
        )

        print("Running utility experiment 3: small epsilon, large dimension...")
        small_eps_large_dim_data = run_utility_experiments(
            epsilon=small_eps,
            delta=delta,
            num_steps=num_steps,
            dimension=large_dim,
            true_mean=true_mean,
            num_experiments=num_experiments,
            sample_size_arr=sample_size_arr
        )

        experiment_data_list = [
            large_eps_small_dim_data, 
            small_eps_small_dim_data, 
            small_eps_large_dim_data
        ]
        
        # Save computed data if requested
        if SAVE_DATA:
            save_utility_experiment_data(
                experiment_data_list=experiment_data_list,
                sample_size_arr=sample_size_arr,
                titles=titles,
                num_steps=num_steps,
                epsilon_values=epsilon_values,
                delta=delta,
                dimension_values=dimension_values,
                true_mean=true_mean,
                num_experiments=num_experiments,
                experiment_name=data_file
            )
    
    # Create visualization with the experiment data
    fig = plot_utility_comparison(
        sample_size_arr=sample_size_arr,
        experiment_data_list=experiment_data_list,
        titles=titles,
        num_steps=num_steps,
        num_experiments=num_experiments,
        C=num_std
    )
    
    if SAVE_PLOTS:
        plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        # Save with moderate padding to ensure legend doesn't get cut off
        plt.savefig(os.path.join(plots_dir, 'privacy_utility_tradeoff_plot.png'), 
                   bbox_inches='tight', pad_inches=0.2)
    
    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close()


def main():
    """
    Run all experiments in sequence
    """
    print("Starting paper experiments...")
    run_experiment_1()
    run_experiment_2()
    run_experiment_3()
    run_experiment_4()
    run_experiment_5()    
    run_experiment_6()    
    run_experiment_7()    
    print("All experiments completed successfully.")


if __name__ == "__main__":
    main()

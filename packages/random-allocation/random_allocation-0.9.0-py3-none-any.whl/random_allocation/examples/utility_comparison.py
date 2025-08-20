import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import pandas as pd

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (random_allocation)
parent_dir = os.path.dirname(current_dir)

# Get the parent of parent directory (the project root)
project_root = os.path.dirname(parent_dir)

# Add the project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.append(project_root)
    print(f"Added {project_root} to sys.path")

from random_allocation.comparisons.utils import *
from random_allocation.comparisons.structs import *
from random_allocation.other_schemes.poisson import *
from random_allocation.random_allocation_scheme.recursive import *
from random_allocation.random_allocation_scheme.decomposition import *


def Poisson_mean_estimation_vectorized(data, num_steps, sigma):
    """
    Vectorized implementation of Poisson mean estimation.
    
    Args:
        data: Array of shape (num_experiments, sample_size) containing the data
        num_steps: Number of steps in the scheme
        sigma: Noise parameter
    """
    num_experiments, sample_size = data.shape
    sampling_probability = 1.0/num_steps
    # Generate participation counts for all experiments at once
    num_participations = np.random.binomial(num_steps, sampling_probability, size=(num_experiments, sample_size))
    # Calculate mean for each experiment
    sums = np.sum(num_participations * data, axis=1)
    # Add noise to each mean
    noise = np.random.normal(0, sigma*np.sqrt(num_steps), size=num_experiments)
    return (sums + noise)/sample_size


def Poisson_accuracy(sampling_func, sample_size, num_experiments, num_steps, sigma, true_mean):
    """
    Calculates the accuracy of Poisson scheme, returning mean and standard deviation of squared errors.
    
    Args:
        sampling_func: Function to generate sample data
        sample_size: Size of each sample
        num_experiments: Number of experiments to run
        num_steps: Number of steps in the scheme
        sigma: Noise parameter
        true_mean: True mean to compare against
        
    Returns:
        tuple: (mean_error, std_error)
    """
    data = sampling_func(sample_size, num_experiments)
    # Get estimates for all experiments at once
    estimates = Poisson_mean_estimation_vectorized(data, num_steps, sigma)
    # Calculate squared errors
    errors = (estimates - true_mean) ** 2
    return np.mean(errors), np.std(errors)

def Poisson_epsilon(num_steps, sigma, delta):
    params = PrivacyParams(
        sigma=sigma,
        num_steps=num_steps,
        num_selected=1,
        num_epochs=1,
        delta=delta,
    )
    config = SchemeConfig()
    return Poisson_epsilon_PLD(params, config, direction=Direction.BOTH)

def Poisson_sigma(num_steps, epsilon, delta, lower = 0.1, upper = 10):
    optimization_func = lambda sig: Poisson_epsilon(num_steps=num_steps, sigma=sig, delta=delta) 
    
    sigma = search_function_with_bounds(
        func=optimization_func, 
        y_target=epsilon,
        bounds=(lower, upper),
        tolerance=0.05,
        function_type=FunctionType.DECREASING
    )
    if sigma is None:
        lower_epsilon = Poisson_epsilon(num_steps=num_steps, sigma=upper, delta=delta)
        upper_epsilon = Poisson_epsilon(num_steps=num_steps, sigma=lower, delta=delta)
        print(f"Poisson_sigma: lower_epsilon={lower_epsilon}, upper_epsilon={upper_epsilon}, target_epsilon={epsilon}")
        return np.inf
    return sigma


def allocation_mean_estimation_vectorized(data, num_steps, sigma):
    """
    Vectorized implementation of Random Allocation mean estimation.
    
    Args:
        data: Array of shape (num_experiments, sample_size) containing the data
        num_steps: Number of steps in the scheme
        sigma: Noise parameter
    """
    # Calculate means for each experiment
    sums = np.sum(data, axis=1)
    # Add noise to each mean
    noise = np.random.normal(0, sigma*np.sqrt(num_steps), size=sums.shape)
    return (sums + noise) / data.shape[1]

def allocation_accuracy(sampling_func, sample_size, num_experiments, num_steps, sigma, true_mean):
    """
    Calculates the accuracy of Random Allocation scheme, returning mean and standard deviation of errors.
    
    Args:
        sampling_func: Function to generate sample data
        sample_size: Size of each sample
        num_experiments: Number of experiments to run
        num_steps: Number of steps in the scheme
        sigma: Noise parameter
        true_mean: True mean to compare against
        
    Returns:
        tuple: (mean_error, std_error)
    """
    data = sampling_func(sample_size, num_experiments)
    # Get estimates for all experiments at once using vectorized implementation
    estimates = allocation_mean_estimation_vectorized(data, num_steps, sigma)
    # Calculate squared errors
    errors = (estimates - true_mean) ** 2
    return np.mean(errors), np.std(errors)

def allocation_epsilon(num_steps, sigma, delta):
    params = PrivacyParams(
        sigma=sigma,
        num_steps=num_steps,
        num_selected=1,
        num_epochs=1,
        delta=delta,
    )
    config = SchemeConfig()
    return allocation_epsilon_recursive(params, config, direction=Direction.BOTH)

def allocation_sigma(num_steps, epsilon, delta, lower = 0.1, upper = 10):
    optimization_func = lambda sig: allocation_epsilon(num_steps=num_steps, sigma=sig, delta=delta)
    sigma = search_function_with_bounds(
        func=optimization_func, 
        y_target=epsilon,
        bounds=(lower, upper),
        tolerance=0.05,
        function_type=FunctionType.DECREASING
    )
    if sigma is None:
        lower_epsilon = allocation_epsilon(num_steps=num_steps, sigma=upper, delta=delta)
        upper_epsilon = allocation_epsilon(num_steps=num_steps, sigma=lower, delta=delta)
        print(f"Allocation_sigma: lower_epsilon={lower_epsilon}, upper_epsilon={upper_epsilon}, target_epsilon={epsilon}")
        return np.inf    
    return sigma

def run_utility_experiments(epsilon, delta, num_steps, dimension, true_mean, num_experiments, sample_size_arr):
    """
    Run a single experiment with given parameters and measure execution time for different stages.
    
    Args:
        epsilon: Privacy parameter epsilon
        delta: Privacy parameter delta
        num_steps: Number of steps in the privacy mechanism
        dimension: Dimension factor for noise scaling
        true_mean: True mean to compare against
        num_experiments: Number of experiments to run
        sample_size_arr: Array of sample sizes to test
        use_hardcoded_sigma: Whether to use hardcoded sigma values instead of calculating them
        hardcoded_poisson_sigma: Hardcoded sigma value for Poisson scheme (already scaled by sqrt(dimension))
        hardcoded_allocation_sigma: Hardcoded sigma value for allocation scheme (already scaled by sqrt(dimension))
    
    Returns:
        tuple: (experiment_data, sigma_calc_time, simulation_time)
    """
    # Calculate sigma values
    Poisson_sigma_val = Poisson_sigma(num_steps, epsilon, delta) * np.sqrt(dimension)
    allocation_sigma_val = allocation_sigma(num_steps, epsilon, delta) * np.sqrt(dimension)
    
    # Create sampling function
    sampling_func = lambda sample_size, num_experiments: np.random.binomial(1, true_mean, size=(num_experiments, sample_size))
    
    Poisson_accuracy_means = []
    Poisson_stds = []
    allocation_accuracy_means = []
    allocation_stds = []       
    for sample_size in sample_size_arr:
        # Calculate Poisson accuracy metrics using the updated function
        p_mean, p_std = Poisson_accuracy(
            sampling_func, sample_size, num_experiments, num_steps, Poisson_sigma_val, 
            true_mean
        )
        Poisson_accuracy_means.append(p_mean)
        Poisson_stds.append(p_std)
        
        # Calculate allocation accuracy metrics using the updated function
        a_mean, a_std = allocation_accuracy(
            sampling_func, sample_size, num_experiments, num_steps, allocation_sigma_val, 
            true_mean
        )
        allocation_accuracy_means.append(a_mean)
        allocation_stds.append(a_std)
    
    # Analytic approximation
    Poisson_accuracy_analytic = true_mean * (1 - true_mean) / sample_size_arr + true_mean / sample_size_arr + Poisson_sigma_val**2 * num_steps / sample_size_arr**2
    allocation_accuracy_analytic = true_mean * (1 - true_mean) / sample_size_arr + allocation_sigma_val**2 * num_steps / sample_size_arr**2

    return {
        'Poisson accuracy': np.array(Poisson_accuracy_means),
        'Poisson std': np.array(Poisson_stds),
        'Allocation accuracy': np.array(allocation_accuracy_means),
        'Allocation std': np.array(allocation_stds),
        'Poisson accuracy (analytic)': Poisson_accuracy_analytic,
        'Allocation accuracy (analytic)': allocation_accuracy_analytic,
        'Poisson sigma': Poisson_sigma_val,
        'Allocation sigma': allocation_sigma_val
    }

def plot_subplot_with_ci(ax, x_data, data, title, xlabel, ylabel, num_experiments, C=3, show_ci=True):
    """
    Create a subplot with confidence interval-based visualization of error distributions.
    Uses standard deviation and standard error for confidence intervals.
    
    Args:
        ax: Matplotlib axis to plot on
        x_data: Array of x values (sample sizes)
        data: Dictionary containing results data
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        num_experiments: Number of experiments run
        C: Multiplier for the confidence interval (standard error = std/sqrt(n))
        show_ci: Whether to display confidence interval bands (default: True)
    """
    # Colors for consistency
    Poisson_color = 'tab:blue'
    allocation_color = 'tab:orange'
    
    # Plot lines for experimental data (means)
    ax.plot(x_data, data['Poisson accuracy'], 'o', color=Poisson_color,
            label=f"Poisson (σ_scaled = {data['Poisson sigma']:.2f})")
    ax.plot(x_data, data['Allocation accuracy'], 's', color=allocation_color,
            label=f"Random allocation (σ_scaled = {data['Allocation sigma']:.2f})")
    
    # Calculate standard error from standard deviation
    std_error = lambda std: std / np.sqrt(num_experiments)
    
    # Only display confidence intervals if requested
    if show_ci:
        # Format CI for legend text - just "confidence interval" without repeating for each method
        ci_text = f"{C}σ confidence interval"
        
        # Always use pre-calculated standard deviations if available
        if 'Poisson std' in data:
            poisson_se = std_error(data['Poisson std'])
            ax.fill_between(
                x_data, 
                data['Poisson accuracy'] - C * poisson_se, 
                data['Poisson accuracy'] + C * poisson_se,
                alpha=0.3, color=Poisson_color, 
                label=f"Poisson {C}σ confidence interval"
            )
        else:
            print(f"Warning: No pre-calculated Poisson std available for {title}.")
            
        if 'Allocation std' in data:
            allocation_se = std_error(data['Allocation std'])
            ax.fill_between(
                x_data, 
                data['Allocation accuracy'] - C * allocation_se, 
                data['Allocation accuracy'] + C * allocation_se,
                alpha=0.3, color=allocation_color, 
                label=f"Random allocation {C}σ confidence interval"
            )
        else:
            print(f"Warning: No pre-calculated Allocation std available for {title}.")
    
    # Plot analytic approximations
    ax.plot(x_data, data['Poisson accuracy (analytic)'], '--', color=Poisson_color, 
            label="Poisson (analytic)")
    ax.plot(x_data, data['Allocation accuracy (analytic)'], '--', color=allocation_color, 
            label="Random allocation (analytic)")
    
    # Finalize plot formatting
    ax.set_title(title)
    ax.set_xlabel(xlabel, labelpad=3)  # Small padding to keep label close to axis
    ax.set_ylabel(ylabel)
    ax.set_xscale("log")
    ax.set_yscale("log")
    # Remove individual legends for each subplot - we'll add one common legend
    # ax.legend()
    ax.grid(True, alpha=0.3)


# Comprehensive plot function that creates the complete visualization
def plot_utility_comparison(sample_size_arr, experiment_data_list, titles, num_steps, num_experiments, C=3, show_ci=True):
    """
    Creates a comprehensive plot with subplots comparing Poisson and Random Allocation
    schemes using standard deviation-based confidence intervals.
    
    Args:
        sample_size_arr: Array of sample sizes 
        experiment_data_list: List of dictionaries containing results from experiments
        titles: List of titles for each subplot
        num_steps: Number of steps used in the experiment
        num_experiments: Number of experiments run
        C: Multiplier for the confidence interval (standard error = std/sqrt(n))
        show_ci: Whether to display confidence interval bands (default: True)
    """
    # Create figure and subplots
    fig, axs = plt.subplots(1, len(experiment_data_list), figsize=(20, 6))
    
    # Plot each experiment in its own subplot
    for i, (data, title) in enumerate(zip(experiment_data_list, titles)):
        plot_subplot_with_ci(
            axs[i], sample_size_arr, data, 
            title, "Sample Size", "Square Error", 
            num_experiments=num_experiments,
            C=C,
            show_ci=show_ci
        )

    # Create a better positioned legend with clearer organization
    handles, labels = axs[0].get_legend_handles_labels()
    
    # First reserve space for legend at the bottom
    plt.subplots_adjust(bottom=0.20)
    
    # Add a single legend below all subplots
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.01), 
               ncol=3, fontsize=16, frameon=True, framealpha=0.9)
    
    # Apply tight_layout with rect parameter to respect the space we reserved for the legend
    # The rect parameter specifies (left, bottom, right, top) fractions of the figure
    plt.tight_layout(rect=(0, 0.14, 1, 0.95))
    
    return fig

def save_utility_experiment_data(experiment_data_list, sample_size_arr, titles, num_steps, epsilon_values, delta, dimension_values, true_mean, num_experiments, experiment_name):
    """
    Save utility experiment data to files for future use.
    
    Args:
        experiment_data_list: List of dictionaries containing experiment results
        sample_size_arr: Array of sample sizes used in the experiments
        titles: List of titles for each experiment
        num_steps: Number of steps used in the experiment
        epsilon_values: List of epsilon values used in experiments
        delta: Delta value used in experiments
        dimension_values: List of dimension values used in experiments
        true_mean: True mean value used in experiments
        num_experiments: Number of experiments run
        experiment_name: Base name for the output files
    """
    # Create data directory if it doesn't exist
    data_dir = os.path.dirname(experiment_name)
    os.makedirs(data_dir, exist_ok=True)
    
    # Create metadata dictionary
    metadata = {
        'sample_sizes': sample_size_arr.tolist() if isinstance(sample_size_arr, np.ndarray) else sample_size_arr,
        'num_steps': num_steps,
        'epsilon_values': epsilon_values,
        'delta': delta,
        'dimension_values': dimension_values,
        'true_mean': true_mean,
        'num_experiments': num_experiments,
        'titles': titles,
        'experiments': []
    }
    
    # Add each experiment's data to metadata
    for i, data in enumerate(experiment_data_list):
        exp_data = {}
        # Convert numpy arrays to lists for JSON serialization
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                exp_data[key] = value.tolist()
            else:
                exp_data[key] = value
        metadata['experiments'].append(exp_data)
    
    # Save as JSON for complete data
    with open(f"{experiment_name}.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Also save as CSV files for each experiment
    for i, (data, title) in enumerate(zip(experiment_data_list, titles)):
        df_data = {'sample_size': sample_size_arr}
        
        # Add all result data
        for key, value in data.items():
            df_data[key] = value
        
        # Add experiment parameters
        df_data['title'] = [title] * len(sample_size_arr)
        df_data['num_steps'] = [num_steps] * len(sample_size_arr)
        if i < len(epsilon_values):
            df_data['epsilon'] = [epsilon_values[i]] * len(sample_size_arr)
        if i < len(dimension_values):
            df_data['dimension'] = [dimension_values[i]] * len(sample_size_arr)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(df_data)
        df.to_csv(f"{experiment_name}_{i}.csv", index=False)
    
    print(f"Saved utility experiment data to {experiment_name}")

def load_utility_experiment_data(experiment_name):
    """
    Load utility experiment data from previously saved files.
    
    Args:
        experiment_name: Base name for the input files
        
    Returns:
        Tuple containing (experiment_data_list, sample_size_arr, titles, num_steps, num_experiments)
        or None if the file doesn't exist
    """
    json_file = f"{experiment_name}.json"
    if not os.path.exists(json_file):
        print(f"No data found at {json_file}")
        return None
    
    print(f"Reading data from {json_file}")
    with open(json_file, 'r') as f:
        metadata = json.load(f)
    
    # Extract experiment parameters
    sample_size_arr = np.array(metadata['sample_sizes'])
    num_steps = metadata['num_steps']
    num_experiments = metadata['num_experiments']
    titles = metadata['titles']
    
    # Convert experiment data back from lists to numpy arrays
    experiment_data_list = []
    for exp_data in metadata['experiments']:
        data_dict = {}
        for key, value in exp_data.items():
            if isinstance(value, list):
                data_dict[key] = np.array(value)
            else:
                data_dict[key] = value
        experiment_data_list.append(data_dict)
    
    return experiment_data_list, sample_size_arr, titles, num_steps, num_experiments
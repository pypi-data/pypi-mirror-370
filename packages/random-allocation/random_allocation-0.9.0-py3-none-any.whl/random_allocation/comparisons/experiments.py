# Standard library imports
import copy
import inspect
import os
import time
from enum import Enum
from typing import Dict, Any, Callable, List, Tuple, Union, Optional, cast, Collection, Mapping, Literal

# Third-party imports
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

# Local application imports
from random_allocation.comparisons.definitions import *
from random_allocation.comparisons.visualization import plot_combined_data, plot_comparison, plot_as_table
from random_allocation.comparisons.data_handler import (
    save_experiment_data, load_experiment_data,
    calc_method_delta, calc_all_methods_delta,
    save_privacy_curves_data, load_privacy_curves_data
)

# Type aliases
ParamsDict = Dict[str, Any]
DataDict = Dict[str, Any]
MethodList = List[str]
XValues = List[Union[float, int]]
FormatterFunc = Callable[[float, int], str]
VisualizationConfig = Dict[str, Any]

class PlotType(Enum):
    COMPARISON = 1
    COMBINED = 2

def get_func_dict(methods: MethodList,
                  y_var: str
                  ) -> Dict[str, Optional[Callable[[Any, Any], float]]]:
    """
    Get the function dictionary for the given methods and y variable.
    
    Args:
        methods: List of method names to retrieve functions for
        y_var: The variable to compute (either 'epsilon' or 'delta')
        
    Returns:
        Dictionary mapping method names to their corresponding calculator functions
    """
    if y_var == EPSILON:
        return cast(Dict[str, Optional[Callable[[Any, Any], float]]], get_features_for_methods(methods, 'epsilon_calculator'))
    return cast(Dict[str, Optional[Callable[[Any, Any], float]]], get_features_for_methods(methods, 'delta_calculator'))

def clear_all_caches() -> None:
    """
    Clear all caches for all modules.
    """
    pass

def calc_experiment_data(params: PrivacyParams,
                         config: SchemeConfig,
                         methods: MethodList,
                         x_var: str,
                         x_values: XValues,
                         y_var: str,
                         direction: Direction = Direction.BOTH
                         ) -> DataDict:
    """
    Calculate data for the experiment.
    
    Args:
        params: Base privacy parameters
        config: Scheme configuration parameters
        methods: List of methods to use in the experiment
        x_var: The variable to vary (x-axis)
        x_values: Values for the x variable
        y_var: The variable to calculate (y-axis)
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
    
    Returns:
        A dictionary containing the experiment data
    """
    funcs_dict = get_func_dict(methods, y_var)
    
    # Initialize data dictionary to store results
    data: DataDict = {'y data': {}}
    
    # For each method
    for method in methods:
        # Skip if method not found in function dictionary
        if method not in funcs_dict or funcs_dict[method] is None:
            print(f"Warning: Method {method} not found in function dictionary or is None. Skipping...")
            continue
            
        # Use a more specific type annotation that includes expected parameters
        func = funcs_dict[method]
        assert func is not None, f"Function for method {method} should not be None at this point"
        
        start_time = time.time()
        print(f"Calculating {method}...")
        
        # List to store function results for each x value
        results: List[float] = []
        
        # Process each x value
        for x_value in x_values:
            # Make a copy of params to modify for this specific case
            param_copy = copy.copy(params)
            
            # Update the param with the current x_value for variable x_var
            setattr(param_copy, x_var, x_value)
            
            # Make sure we have the correct parameter set for the calculation
            # If we're calculating epsilon, we need delta to be provided (and vice versa)
            if y_var == 'epsilon':
                # We're calculating epsilon, so make sure delta is set and epsilon is None
                if param_copy.delta is None:
                    raise ValueError(f"Delta must be provided to compute epsilon")
                param_copy.epsilon = None
            elif y_var == 'delta':
                # We're calculating delta, so make sure epsilon is set and delta is None
                if param_copy.epsilon is None:
                    raise ValueError(f"Epsilon must be provided to compute delta")
                param_copy.delta = None
            
            # Call the function with the modified params and ensure result is a float
            # Use type ignore to bypass the unexpected keyword argument errors
            result = func(params=param_copy, config=config, direction=direction)  # type: ignore
            
            # Handle None or Optional return values by converting to float
            if result is None:
                # Default to 0.0 if None is returned, or raise an error if preferred
                result_float = 0.0
            else:
                result_float = float(result)
            
            results.append(result_float)
        
        data['y data'][method] = np.array(results)
        
        if data['y data'][method].ndim > 1:
            data['y data'][method + '- std'] = data['y data'][method][:,1]
            data['y data'][method] = data['y data'][method][:,0]
        
        end_time = time.time()
        print(f"Calculating {method} took {end_time - start_time:.3f} seconds")

    data['x name'] = names_dict[x_var]
    data['y name'] = names_dict[y_var]
    data['x data'] = x_values
    
    # Build title for the plot
    data['title'] = f"{names_dict[y_var]} as a function of {names_dict[x_var]} \n"
    
    for var in VARIABLES:
        if var != x_var and var != y_var:
            value = getattr(params, var, None)
            if value is not None:
                data[var] = value
                data['title'] += f"{names_dict[var]} = {value}, "
    
    return data

def save_experiment_plot(data: DataDict, methods: MethodList, experiment_name: str) -> None:
    """
    Save the experiment plot to a file.
    
    Args:
        data: The experiment data dictionary
        methods: List of methods used in the experiment
        experiment_name: Name of the experiment for the output file (full path)
    """
    # Create plots directory if it doesn't exist
    os.makedirs(os.path.dirname(experiment_name), exist_ok=True)
    
    # Create and save the plot using plot_comparison
    fig: Figure = plot_comparison(data)
    plt.savefig(f'{experiment_name}_plot.png')
    plt.close()

def run_experiment(
    params_dict: ParamsDict,
    config: SchemeConfig,
    methods: MethodList, 
    visualization_config: Optional[VisualizationConfig] = None,
    experiment_name: str = '',
    plot_type: PlotType = PlotType.COMPARISON,
    read_data: bool = False, 
    save_data: bool = True,
    save_plots: bool = False,
    show_plots: bool = True,
    direction: Direction = Direction.BOTH
) -> DataDict:
    """
    Run an experiment and handle its results.
    
    Args:
        params_dict: Dictionary containing experiment parameters
            Must contain 'x_var', 'y_var', and x_values
        config: A SchemeConfig object
        methods: List of methods to use in the experiment
        visualization_config: Additional keyword arguments for the plot function
        experiment_name: Name of the experiment for the output file
        plot_type: Type of plot to create (COMPARISON or COMBINED)
        read_data: Whether to try reading data from existing files before calculating
        save_data: Whether to save computed data to CSV files
        save_plots: Whether to save plots to files
        show_plots: Whether to display plots interactively
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
        
    Returns:
        The experiment data dictionary
    """
    # Clear all caches before running the experiment
    clear_all_caches()
    
    # Get the examples directory path
    examples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'examples')
    data_dir = os.path.join(examples_dir, 'data')
    data_file = os.path.join(data_dir, experiment_name)
    
    # Extract required parameters from params_dict without removing them
    x_var = params_dict.get('x_var')
    y_var = params_dict.get('y_var')
    
    if x_var is None or y_var is None:
        raise ValueError("params_dict must contain 'x_var' and 'y_var' keys")
    
    if x_var not in params_dict:
        raise ValueError(f"params_dict must contain values for '{x_var}'")
        
    x_values = cast(XValues, params_dict[x_var])
    
    # Create a PrivacyParams object with base values (excluding x_values)
    base_params = {k: v for k, v in params_dict.items() if not isinstance(v, (list, np.ndarray)) and k not in ['x_var', 'y_var']}
    
    # Use epsilon/delta from params_dict if present
    epsilon = base_params.get(EPSILON)
    delta = base_params.get(DELTA)
    
    # Create PrivacyParams object with initial values
    params = PrivacyParams(
        sigma=base_params.get(SIGMA, 1.0),
        num_steps=base_params.get(NUM_STEPS, 1),
        num_selected=base_params.get(NUM_SELECTED, 1),
        num_epochs=base_params.get(NUM_EPOCHS, 1),  # Changed default to 1
        epsilon=epsilon,
        delta=delta
    )

    # Data handling logic:
    # - If read_data is True: Try to read existing data first
    # - If calculation is needed and save_data is True: Save the calculated data
    data: DataDict
    
    if read_data:
        # Try to load existing data first
        loaded_data = load_experiment_data(data_file, methods)
        if loaded_data is not None:
            print(f"Loaded existing data for {experiment_name}")
            data = loaded_data
        else:
            print(f"Computing data for {experiment_name}")
            data = calc_experiment_data(params, config, methods, x_var, x_values, y_var, direction)
            if save_data:
                save_experiment_data(data, methods, data_file)
    else:
        # Always calculate new data
        print(f"Computing data for {experiment_name}")
        data = calc_experiment_data(params, config, methods, x_var, x_values, y_var, direction)
        if save_data:
            save_experiment_data(data, methods, data_file)
    
    # Plotting logic
    if visualization_config is None:
        visualization_config = {}
    
    # Create the appropriate plot based on plot_type
    if plot_type == PlotType.COMPARISON:
        # Use type: ignore to bypass incompatible argument type errors
        fig: Figure = plot_comparison(data, **visualization_config)  # type: ignore
    else:  # PlotType.COMBINED
        # Use type: ignore to bypass incompatible argument type errors
        fig = plot_combined_data(data, **visualization_config)  # type: ignore
    
    # Save the plot if requested
    if save_plots:
        plots_dir = os.path.join(examples_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        fig.savefig(os.path.join(plots_dir, f'{experiment_name}_plot.png'))
    
    # Show the plot if requested
    if show_plots:
        plt.show()
        plot_as_table(data)
    else:
        plt.close(fig)
        
    return data
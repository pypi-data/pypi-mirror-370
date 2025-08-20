"""
Data handling utilities for experiments.

This module provides functions for saving and loading experiment data
with full preservation of all information.
"""

import os
import json
from typing import Dict, List, Union, Any, Optional, Collection, cast, Callable, Tuple
import time
import numpy as np
import pandas as pd

# Local imports
from random_allocation.comparisons.definitions import Direction
from random_allocation.comparisons.structs import SchemeConfig, PrivacyParams
from random_allocation.other_schemes.poisson import Poisson_delta_PLD
from random_allocation.random_allocation_scheme.combined import allocation_delta_combined
from random_allocation.random_allocation_scheme.Monte_Carlo import Monte_Carlo_estimation, AdjacencyType

# Define type aliases locally to avoid circular imports
MethodList = List[str]
DataDict = Dict[str, Any]


def save_experiment_data(data: DataDict, methods: MethodList, experiment_name: str) -> None:
    """
    Save experiment data with complete information.
    
    Args:
        data: The experiment data dictionary
        methods: List of methods used in the experiment
        experiment_name: Name of the experiment for the output file (full path)
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(experiment_name), exist_ok=True)
    
    # Prepare data for saving
    save_data = {
        'x data': data['x data'].tolist() if isinstance(data['x data'], np.ndarray) else data['x data'],
        'x name': data.get('x name', ''),
        'y name': data.get('y name', ''),
        'title': data.get('title', ''),
        'y data': {}
    }
    
    # Process y data for each method
    for method in methods:
        if method in data['y data']:
            save_data['y data'][method] = data['y data'][method].tolist() if isinstance(data['y data'][method], np.ndarray) else data['y data'][method]
        
        # Save standard deviation data if available
        std_key = method + '- std'
        if std_key in data['y data']:
            save_data['y data'][std_key] = data['y data'][std_key].tolist() if isinstance(data['y data'][std_key], np.ndarray) else data['y data'][std_key]
    
    # Save any additional parameters stored in the data dict
    for key, value in data.items():
        if key not in ['x data', 'y data', 'x name', 'y name', 'title']:
            # Convert numpy arrays to lists for JSON serialization
            if isinstance(value, np.ndarray):
                save_data[key] = value.tolist()
            else:
                save_data[key] = value
    
    # Save as JSON for complete data preservation
    with open(f"{experiment_name}.json", 'w') as f:
        json.dump(save_data, f, indent=2)
    
    # Also save as CSV for compatibility
    df_data: Dict[str, Union[Collection[float], str]] = {'x': data['x data']}
    
    # Add y data for each method to the DataFrame
    for method in methods:
        if method in data['y data']:
            df_data[method] = data['y data'][method]
        
        std_key = method + '- std'
        if std_key in data['y data']:
            df_data[f"{method}_std"] = data['y data'][std_key]
    
    # Include additional metadata
    df_data['title'] = data.get('title', '')
    df_data['x name'] = data.get('x name', '')
    df_data['y name'] = data.get('y name', '')
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(df_data)
    df.to_csv(experiment_name, index=False)


def load_experiment_data(experiment_name: str, methods: MethodList) -> Optional[DataDict]:
    """
    Load experiment data with complete information.
    
    Args:
        experiment_name: Name of the experiment file (full path, without extension)
        methods: List of methods used in the experiment
    
    Returns:
        The loaded experiment data dictionary or None if file doesn't exist
    """
    # First try to load from JSON which has complete information
    json_file = f"{experiment_name}.json"
    if os.path.exists(json_file):
        print(f"Reading data from {json_file}")
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        
        # Convert loaded data to correct format
        data: DataDict = {
            'x data': np.array(loaded_data['x data']) if 'x data' in loaded_data else np.array([]),
            'y data': {},
            'x name': loaded_data.get('x name', ''),
            'y name': loaded_data.get('y name', ''),
            'title': loaded_data.get('title', '')
        }
        
        # Process y data
        if 'y data' in loaded_data:
            for method, values in loaded_data['y data'].items():
                data['y data'][method] = np.array(values)
        
        # Add any additional parameters
        for key, value in loaded_data.items():
            if key not in ['x data', 'y data', 'x name', 'y name', 'title']:
                # Convert list back to numpy array if needed
                if isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                    data[key] = np.array(value)
                else:
                    data[key] = value
        
        return data
    
    # Fallback to CSV if JSON doesn't exist
    csv_file = experiment_name
    if os.path.exists(csv_file):
        print(f"Reading data from {csv_file}")
        # Read the CSV and convert to expected DataDict format
        df = pd.read_csv(csv_file)
        
        csv_data: DataDict = {'y data': {}, 'x data': np.array(df['x'].tolist())}
        
        for method in methods:
            if method in df.columns:
                csv_data['y data'][method] = df[method].values
            if f"{method}_std" in df.columns:
                csv_data['y data'][method + '- std'] = df[f"{method}_std"].values
        
        # Extract metadata
        if 'title' in df.columns and not df.empty:
            csv_data['title'] = df['title'].iloc[0] 
        if 'x name' in df.columns and not df.empty:
            csv_data['x name'] = df['x name'].iloc[0]
        if 'y name' in df.columns and not df.empty:
            csv_data['y name'] = df['y name'].iloc[0]
        
        return csv_data
    
    # If neither file exists, return None
    return None

def calc_method_delta(name: str, func: Callable, params_arr: List[PrivacyParams], config: SchemeConfig, direction: Direction = Direction.BOTH) -> List[float]:
    """
    Calculate delta values for a specific method.
    
    Args:
        name: Name of the method
        func: Function to calculate delta
        params_arr: Array of PrivacyParams objects
        config: Scheme configuration parameters
        direction: The direction of privacy. Can be ADD, REMOVE, or BOTH.
        
    Returns:
        List of delta values for each set of parameters
    """
    time_start = time.perf_counter()
    results = [func(params=params, config=config, direction=direction) for params in params_arr]
    time_stop = time.perf_counter()
    print(f'{name} delta done in {time_stop - time_start: .0f} seconds')
    return results

def calc_all_methods_delta(params_arr: List[PrivacyParams], config: SchemeConfig) -> Dict[str, List[float]]:
    """
    Calculate delta values for all methods.
    
    Args:
        params_arr: Array of PrivacyParams objects
        config: Scheme configuration parameters
        
    Returns:
        Dictionary mapping method names to lists of delta values
    """
    print(f'Calculating deltas with sigma = {params_arr[0].sigma}, t = {params_arr[0].num_steps} for all methods...')
    deltas_dict = {}
    deltas_dict['Poisson'] = calc_method_delta('Poisson', Poisson_delta_PLD, params_arr, config, direction=Direction.BOTH)
    deltas_dict['allocation - Our'] = calc_method_delta('allocation - Our', allocation_delta_combined, params_arr, config, direction=Direction.BOTH)

    time_start = time.perf_counter()
    MC_dict_arr = [Monte_Carlo_estimation(params, config, adjacency_type=AdjacencyType.REMOVE) for params in params_arr]
    time_stop = time.perf_counter()
    deltas_dict['allocation - MC HP'] = [MC_dict['high prob'] for MC_dict in MC_dict_arr]
    deltas_dict['allocation - MC mean'] = [MC_dict['mean'] for MC_dict in MC_dict_arr]
    print(f'Monte Carlo estimation done in {time_stop - time_start: .0f} seconds')
    print(f'Calculation done for {len(deltas_dict)} methods')
    return deltas_dict

def save_privacy_curves_data(
    deltas_dict_arr: List[Dict[str, List[float]]], 
    epsilon_mat: List[np.ndarray], 
    num_steps_arr: List[int], 
    sigma_arr: List[float], 
    experiment_name: str
) -> None:
    """
    Save privacy curves data for multi-parameter experiments.
    
    Args:
        deltas_dict_arr: List of dictionaries mapping method names to delta values
        epsilon_mat: List of arrays of epsilon values
        num_steps_arr: List of number of steps values
        sigma_arr: List of sigma values
        experiment_name: Name of the experiment for the output file (full path)
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(experiment_name), exist_ok=True)
    
    # Prepare data for saving
    save_data = {
        'num_steps': num_steps_arr,
        'sigma': sigma_arr,
        'epsilon_values': [eps_arr.tolist() if isinstance(eps_arr, np.ndarray) else eps_arr for eps_arr in epsilon_mat],
        'deltas_data': []
    }
    
    # Convert each deltas_dict to a format suitable for JSON
    for deltas_dict in deltas_dict_arr:
        json_dict = {}
        for method, deltas in deltas_dict.items():
            json_dict[method] = deltas if not isinstance(deltas, np.ndarray) else deltas.tolist()
        save_data['deltas_data'].append(json_dict)
    
    # Save as JSON for complete data preservation
    with open(f"{experiment_name}.json", 'w') as f:
        json.dump(save_data, f, indent=2)
    
    # Also save as CSV for compatibility - one file per parameter combination
    for i, (num_steps, sigma, epsilon_arr, deltas_dict) in enumerate(zip(num_steps_arr, sigma_arr, epsilon_mat, deltas_dict_arr)):
        df_data = {'epsilon': epsilon_arr}
        
        # Add delta values for each method
        for method, deltas in deltas_dict.items():
            df_data[method] = deltas
        
        # Add parameter information
        df_data['num_steps'] = [num_steps] * len(epsilon_arr)
        df_data['sigma'] = [sigma] * len(epsilon_arr)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(df_data)
        df.to_csv(f"{experiment_name}_{i}.csv", index=False)
    
    print(f"Saved privacy curves data to {experiment_name}")

def load_privacy_curves_data(experiment_name: str) -> Optional[Tuple[List[Dict[str, np.ndarray]], List[np.ndarray], List[int], List[float]]]:
    """
    Load privacy curves data for multi-parameter experiments.
    
    Args:
        experiment_name: Name of the experiment file (full path, without extension)
    
    Returns:
        Tuple of (deltas_dict_arr, epsilon_mat, num_steps_arr, sigma_arr) or None if file doesn't exist
    """
    # Try to load from JSON which has complete information
    json_file = f"{experiment_name}.json"
    if os.path.exists(json_file):
        print(f"Reading data from {json_file}")
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        
        # Extract arrays from loaded data
        num_steps_arr = loaded_data.get('num_steps', [])
        sigma_arr = loaded_data.get('sigma', [])
        epsilon_mat = [np.array(eps_arr) for eps_arr in loaded_data.get('epsilon_values', [])]
        
        # Convert loaded deltas data to correct format
        deltas_dict_arr = []
        for json_dict in loaded_data.get('deltas_data', []):
            deltas_dict = {}
            for method, deltas in json_dict.items():
                deltas_dict[method] = np.array(deltas)
            deltas_dict_arr.append(deltas_dict)
        
        return deltas_dict_arr, epsilon_mat, num_steps_arr, sigma_arr
    
    # If file doesn't exist, return None
    print(f"No data found at {json_file}")
    return None
from logging import config
from typing import Optional, Callable

from random_allocation.comparisons.definitions import PrivacyParams, SchemeConfig, Direction
from random_allocation.comparisons.structs import Verbosity

def handle_directions(params: PrivacyParams,
                      config: SchemeConfig,
                      direction: Direction,
                      add_func: Callable,
                      remove_func: Callable,
                      var_name: str,
                      ) -> float:
    
    remove_val: Optional[float] = None
    if direction != Direction.ADD:
        remove_val = remove_func(params=params, config=config)

    add_val: Optional[float] = None
    if direction != Direction.REMOVE:
        add_val = add_func(params=params, config=config)

    if direction == Direction.ADD:
        assert add_val is not None, f"{var_name}_add should be defined"
        return add_val
    if direction == Direction.REMOVE:
        assert remove_val is not None, f"{var_name}_remove should be defined"
        return remove_val

    # Both directions - both should be defined
    assert add_val    is not None, f"{var_name}_add should be defined"
    assert remove_val is not None, f"{var_name}_remove should be defined"
    return float(max(remove_val, add_val))

def print_alpha(used_alpha: float, 
                min_alpha: float, 
                max_alpha: float, 
                verbosity: Verbosity,
                direction_name: str,
                params: PrivacyParams) -> None:
    # Check for potential alpha overflow or underflow
    if verbosity != Verbosity.NONE:
        if used_alpha == max_alpha:
            print(f'Potential alpha overflow in {direction_name} direction! used alpha: {used_alpha} which is the maximal alpha')
        if used_alpha == min_alpha:
            print(f'Potential alpha underflow in {direction_name} direction! used alpha: {used_alpha} which is the minimal alpha')

    # Print debug info if requested
    if verbosity == Verbosity.ALL:
        if params.epsilon is not None:
            print(f'Direction - {direction_name}: sigma: {params.sigma}, epsilon: {params.epsilon}, num_steps: {params.num_steps}, num_selected: {params.num_selected}, num_epochs: {params.num_epochs}, used_alpha: {used_alpha}')
        elif params.delta is not None:
            print(f'Direction - {direction_name}: sigma: {params.sigma}, delta: {params.delta}, num_steps: {params.num_steps}, num_selected: {params.num_selected}, num_epochs: {params.num_epochs}, used_alpha: {used_alpha}')

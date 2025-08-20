# Standard library imports
from enum import auto, Enum
import math
from typing import Callable, Dict, List, Optional, Tuple, Union, Any, cast, TypedDict, Protocol

# Third-party imports
import numpy as np
from scipy import integrate
from scipy.optimize import minimize_scalar, OptimizeResult
from scipy import optimize

# Import Verbosity enum from structs
from random_allocation.comparisons.structs import Verbosity

# Helper functions for verbosity handling

def _should_print_warning(verbosity: Verbosity) -> bool:
    """Check if warning messages should be printed at this verbosity level"""
    return verbosity in [Verbosity.WARNINGS, Verbosity.ALL]

def _should_print_info(verbosity: Verbosity) -> bool:
    """Check if info messages should be printed at this verbosity level"""
    return verbosity == Verbosity.ALL

# Type aliases
BoundsType = Optional[Tuple[float, float]]
NumericFunction = Callable[[float], float]

class FunctionType(Enum):
    """Enum for specifying the type of function.
    
    Values:
        INCREASING: Monotonically increasing function (f'(x) > 0 for all x)
        DECREASING: Monotonically decreasing function (f'(x) < 0 for all x)
        CONVEX: Convex function (f''(x) > 0 for all x)
        CONCAVE: Concave function (f''(x) < 0 for all x)
    """
    INCREASING = auto()
    DECREASING = auto()
    CONVEX = auto()
    CONCAVE = auto()

class BoundType(Enum):
    """Enum for specifying the desired bound type.
    
    Values:
        NONE: No specific bound guarantee needed
        UPPER: Guarantee f(x) ≤ y_target
        LOWER: Guarantee f(x) ≥ y_target
    """
    NONE = auto()       # No specific bound guarantee
    UPPER = auto()      # Guarantee f(x) ≤ y_target
    LOWER = auto()      # Guarantee f(x) ≥ y_target

def search_function(
    func: NumericFunction, 
    y_target: float, 
    verbosity: Verbosity,
    initial_guess: float = 0.0, 
    bounds: BoundsType = None, 
    tolerance: float = 1e-6, 
    function_type: FunctionType = FunctionType.INCREASING
) -> Optional[float]:
    """
    Find x such that func(x) = y_target for different types of functions.
    
    This function uses different optimization strategies based on the type of function:
    - For monotonic functions (increasing/decreasing): Uses bracketing methods
    - For non-monotonic functions (convex/concave): Tries root-finding first, then
      falls back to minimizing the squared difference if needed
    
    Args:
        func: Function to search (maps x -> y)
        y_target: Target y value we're searching for
        verbosity: Verbosity level for outputs (Verbosity enum)
        initial_guess: Initial guess for x (primarily used for convex/concave functions)
        bounds: Tuple of (x_min, x_max) defining search bounds
        tolerance: Acceptable tolerance for the result
        function_type: Type of function (FunctionType enum)
        
    Returns:
        x value such that func(x) ≈ y_target, or None if not found
    
    Raises:
        ValueError: If bounds are not provided for monotonic functions or if an invalid 
                   function_type is provided
        RuntimeError: If the optimization fails unexpectedly
    """    
    # Flag for whether to print warnings
    should_print_warning = _should_print_warning(verbosity)
    # Flag for whether to print info messages
    should_print_info = _should_print_info(verbosity)
    
    assert(tolerance > 0) 
    # Define objective function to find the root: f(x) - y_target = 0
    objective: NumericFunction = lambda x: func(x) - y_target
    
    # Handle monotonic functions (increasing or decreasing)
    if function_type in [FunctionType.INCREASING, FunctionType.DECREASING]:
        # Binary search approach requires bounds
        if bounds is None:
            if should_print_warning:
                print("[WARNING] Must provide bounds for monotonic function search")
            raise ValueError("Must provide bounds for monotonic function search")
        
        x_min, x_max = bounds
        
        # Validate bounds
        if x_min >= x_max:
            if should_print_warning:
                print(f"[WARNING] Lower bound must be less than upper bound, got {bounds}")
            raise ValueError(f"Lower bound must be less than upper bound, got {bounds}")
        
        try:
            # Evaluate function at bounds
            y_min: float = func(x_min)
            y_max: float = func(x_max)
            
            # Check if solution exists within bounds
            if function_type == FunctionType.INCREASING:
                # For increasing functions, we need y_min ≤ y_target ≤ y_max
                if y_target < y_min or y_target > y_max:
                    if should_print_warning:
                        print(f"[WARNING] Target value {y_target} is outside of function range [{y_min}, {y_max}] for increasing function")
                    return None
            else:  # FunctionType.DECLINING
                # For decreasing functions, we need y_min ≥ y_target ≥ y_max
                if y_target > y_min or y_target < y_max:
                    if should_print_warning:
                        print(f"[WARNING] Target value {y_target} is outside of function range [{y_max}, {y_min}] for decreasing function")
                    return None
            
            # Use scipy's root_scalar with bracket method
            try:
                root_result: optimize.RootResults = optimize.root_scalar(
                    objective, 
                    bracket=bounds, 
                    method='brentq', 
                    rtol=tolerance
                )
                if not root_result.converged and should_print_warning:
                    print(f"[WARNING] Root finding did not converge for y_target={y_target}")
                return root_result.root if root_result.converged else None
            except ValueError as e:
                # This can happen if the bracket doesn't contain a root despite our checks
                # This might indicate the function isn't truly monotonic
                if should_print_warning:
                    print(f"[WARNING] Root finding failed: {str(e)}. The function may not be monotonic as specified.")
                raise RuntimeError(f"Root finding failed: {str(e)}. The function may not be monotonic as specified.")
                
        except Exception as e:
            # Handle potential evaluation errors
            if should_print_warning:
                print(f"[WARNING] Error evaluating function: {str(e)}")
            raise RuntimeError(f"Error evaluating function: {str(e)}")
    
    # Handle non-monotonic functions (convex or concave)
    elif function_type in [FunctionType.CONVEX, FunctionType.CONCAVE]:
        # First try direct root finding, which is faster when it works
        try:
            if bounds:
                # If we have bounds, try bracketing method first
                try:
                    bracket_result: optimize.RootResults = optimize.root_scalar(
                        objective, 
                        bracket=bounds, 
                        method='brentq', 
                        rtol=tolerance
                    )
                    if bracket_result.converged:
                        return float(bracket_result.root)
                except ValueError:
                    # Bracketing failed, so there might not be a root within bounds
                    # or there might be multiple roots - continue to other methods
                    if should_print_warning:
                        print(f"[WARNING] Bracketing method failed for y_target={y_target} within bounds {bounds}")
                    pass
                    
            # Try Newton's method with initial guess but suppress derivative warnings
            try:
                # Use brent method instead of newton to avoid derivative issues
                # Newton can fail when derivative is zero at the initial point
                secant_result: optimize.RootResults = optimize.root_scalar(
                    objective, 
                    x0=initial_guess, 
                    method='secant',  # Changed from 'newton' to 'secant'
                    rtol=tolerance
                )
                if secant_result.converged:
                    return float(secant_result.root)
            except (ValueError, RuntimeError) as e:
                # Method failed, continue to minimization approach
                if should_print_warning:
                    print(f"[WARNING] Secant method failed for y_target={y_target}: {str(e)}")
                pass
                
            # Fall back to minimizing squared difference
            # This works even when there's no exact solution
            objective_squared: NumericFunction = lambda x: (func(x) - y_target)**2
            
            if bounds:
                min_result: OptimizeResult = minimize_scalar(
                    objective_squared, 
                    bounds=bounds, 
                    method='bounded', 
                    options={'xatol': tolerance}
                )
            else:
                min_scalar_result: OptimizeResult = minimize_scalar(
                    objective_squared, 
                    method='brent', 
                    options={'xtol': tolerance}
                )
                min_result = min_scalar_result
            
            # Check if our solution is good enough
            # Sometimes minimize_scalar finds a local minimum that's not close to y_target
            x_result: float = float(min_result.x)
            error = abs(func(x_result) - y_target)
            if error <= tolerance:
                return float(x_result)  # Explicitly cast to float to avoid returning Any
            else:
                # No suitable solution found
                if should_print_warning:
                    print(f"[WARNING] Failed to find solution: function value at x={x_result} is {func(x_result)}, " + 
                          f"which differs from target {y_target} by {error} (exceeds tolerance {tolerance})")
                return None
                
        except Exception as e:
            # Handle potential optimization errors
            if should_print_warning:
                print(f"[WARNING] Optimization failed: {str(e)}")
            raise RuntimeError(f"Optimization failed: {str(e)}")
    
    else:
        if should_print_warning:
            print(f"[WARNING] Invalid function_type: {function_type}. Must be a FunctionType enum.")
        raise ValueError(f"Invalid function_type: {function_type}. Must be a FunctionType enum.")


def adjust_for_sign(
    func: NumericFunction, 
    x_result: Optional[float], 
    y_target: float, 
    tolerance: float, 
    function_type: FunctionType, 
    bound_type: BoundType,
    verbosity: Verbosity
) -> Optional[float]:
    """
    Adjusts x_result to ensure a specific sign relationship between func(x) and y_target.
    
    This function uses mathematical transformations to simplify the problem:
    1. Decreasing functions → increasing functions with sign flip
    2. Concave functions → convex functions with sign flip 
    3. Lower bounds → upper bounds with appropriate transformations
    
    This reduces the number of cases from 8 combinations (4 function types × 2 bound types)
    to just 4 combinations (2 function types × 2 bound types), making the code simpler
    and more maintainable.
    
    Mathematical basis:
    - For decreasing f(x), working with -f(x) makes it increasing
    - For concave f(x), working with -f(x) makes it convex
    - When the function is flipped, the bound type must also be flipped
      (e.g., ensuring f(x) ≤ y becomes ensuring -f(x) ≥ -y)
    
    Args:
        func: Original function f(x)
        x_result: Initial x result to adjust (from search_function)
        y_target: Target y value that was searched for
        tolerance: Acceptable numerical tolerance
        function_type: Type of function (increasing, decreasing, convex, concave)
        bound_type: Type of bound to ensure (NONE, UPPER, LOWER)
        verbosity: Verbosity level for outputs (Verbosity enum)
        
    Returns:
        Adjusted x value ensuring the desired relationship with y_target,
        or None if x_result was None
        
    Raises:
        ValueError: If invalid function_type or bound_type is provided
        RuntimeError: If adjustment fails unexpectedly
    """
    # Flag for whether to print warnings
    should_print_warning = _should_print_warning(verbosity)
    # Flag for whether to print info messages
    should_print_info = _should_print_info(verbosity)
    
    # Input validation
    if not isinstance(function_type, FunctionType):
        if should_print_warning:
            print(f"[WARNING] function_type must be a FunctionType enum, got {type(function_type)}")
        raise ValueError(f"function_type must be a FunctionType enum, got {type(function_type)}")
    
    if not isinstance(bound_type, BoundType):
        if should_print_warning:
            print(f"[WARNING] bound_type must be a BoundType enum, got {type(bound_type)}")
        raise ValueError(f"bound_type must be a BoundType enum, got {type(bound_type)}")
    
    if tolerance <= 0:
        if should_print_warning:
            print(f"[WARNING] tolerance must be positive, got {tolerance}")
        raise ValueError(f"tolerance must be positive, got {tolerance}")
    
    # If no result or no bound requirement, return as is
    if x_result is None or bound_type == BoundType.NONE:
        if x_result is None and should_print_warning:
            print(f"[WARNING] No valid x_result provided to adjust_for_sign")
        return x_result
    
    # Transform the problem to reduce the number of cases:
    # - Convert decreasing to increasing by flipping the function
    # - Convert concave to convex by flipping the function
    # - Convert LOWER bound to UPPER bound by flipping the bound check
    
    transformed_func: NumericFunction = func
    transformed_y_target: float = y_target
    transformed_bound_type: BoundType = bound_type
    transformed_function_type: FunctionType = function_type
    
    # Apply transformations for decreasing and concave functions
    if function_type in [FunctionType.DECREASING, FunctionType.CONCAVE]:
        # Create a new function that flips the sign of the original
        transformed_func = lambda x: -func(x)
        transformed_y_target = -y_target
        
        # Function flipped, so invert bound type:
        # - UPPER bound (f(x) ≤ y) becomes LOWER bound (-f(x) ≥ -y)
        # - LOWER bound (f(x) ≥ y) becomes UPPER bound (-f(x) ≤ -y)
        transformed_bound_type = BoundType.LOWER if bound_type == BoundType.UPPER else BoundType.UPPER
        
        # Also update function type for clarity in the adjustment logic
        transformed_function_type = (FunctionType.INCREASING if function_type == FunctionType.DECREASING 
                                  else FunctionType.CONVEX)
        
        if should_print_info:
            print(f"[INFO] Transformed {function_type} function to {transformed_function_type} " +
                  f"and bound type {bound_type} to {transformed_bound_type}")
    
    try:
        # Check if we already satisfy the bound
        y_result: float = transformed_func(x_result)
        error: float = y_result - transformed_y_target
        
        # If bound is already satisfied, return as is
        if ((transformed_bound_type == BoundType.UPPER and error <= 0) or 
            (transformed_bound_type == BoundType.LOWER and error >= 0)):
            if should_print_info:
                print(f"[INFO] Bound already satisfied: f({x_result}) = {y_result}, target = {transformed_y_target}, " +
                      f"error = {error}, bound_type = {transformed_bound_type}")
            return x_result
        
        # Now we only need to handle INCREASING and CONVEX functions with UPPER and LOWER bounds
        if should_print_warning:
            print(f"[WARNING] Bound not satisfied: f({x_result}) = {y_result}, target = {transformed_y_target}, " +
                  f"error = {error}, bound_type = {transformed_bound_type}. Adjusting x...")
            
        adjustment_factor: float = tolerance
        max_iterations: int = 100
        iterations: int = 0
        
        # Iterative adjustment to satisfy the bound
        while iterations < max_iterations:
            iterations += 1
            
            if transformed_function_type == FunctionType.INCREASING:
                # For monotonically increasing functions:
                # - To satisfy y ≤ y_target (upper bound), decrease x
                # - To satisfy y ≥ y_target (lower bound), increase x
                if transformed_bound_type == BoundType.UPPER:
                    x_result -= adjustment_factor
                else:  # BoundType.LOWER
                    x_result += adjustment_factor
            else:  # CONVEX function
                # For convex functions (U-shape):
                # The direction depends on which side of the minimum we're on
                # We determine this by testing if moving left decreases the function value
                x_test: float = x_result - adjustment_factor
                y_test: float = transformed_func(x_test)
                
                if transformed_bound_type == BoundType.UPPER:
                    # Need to decrease function value to satisfy f(x) ≤ y_target
                    if y_test < y_result:  # Moving left decreases value
                        x_result = x_test
                    else:  # Moving right decreases value
                        x_result += adjustment_factor
                else:  # BoundType.LOWER
                    # Need to increase function value to satisfy f(x) ≥ y_target
                    if y_test > y_result:  # Moving left increases value
                        x_result = x_test
                    else:  # Moving right increases value
                        x_result += adjustment_factor
            
            # Check if we've achieved the desired relationship
            y_result = transformed_func(x_result)
            error = y_result - transformed_y_target
            
            if ((transformed_bound_type == BoundType.UPPER and error <= 0) or 
                (transformed_bound_type == BoundType.LOWER and error >= 0)):
                if should_print_info:
                    print(f"[INFO] Successfully adjusted x to {x_result} after {iterations} iterations, " +
                          f"giving f(x) = {y_result}, error = {error}")
                return x_result
            
            # Increase adjustment factor to converge faster (exponential growth)
            adjustment_factor *= 2
        
        # If we reach here, we hit the maximum iterations without converging
        # Log a warning, but still return our best approximation
        if should_print_warning:
            print(f"[WARNING] adjust_for_sign did not converge after {max_iterations} iterations. " +
                  f"Last x = {x_result}, f(x) = {y_result}, error = {error}, tolerance = {tolerance}")
        
        import warnings
        warnings.warn(
            f"adjust_for_sign did not converge after {max_iterations} iterations. " +
            f"Last error: {error}, tolerance: {tolerance}",
            RuntimeWarning
        )
        
        return x_result
        
    except Exception as e:
        # Handle potential function evaluation errors
        if should_print_warning:
            print(f"[WARNING] Error during adjustment: {str(e)}")
        raise RuntimeError(f"Error during adjustment: {str(e)}")


def search_function_with_bounds(func: NumericFunction,
                                y_target: float,
                                initial_guess: float = 0.0,
                                bounds: BoundsType = None,
                                tolerance: float = 1e-6,
                                function_type: FunctionType = FunctionType.INCREASING, 
                                bound_type: BoundType = BoundType.UPPER,
                                verbosity: Verbosity = Verbosity.NONE
                                ) -> Optional[float]:
    """
    Finds x such that func(x) = y_target with optional bound guarantees.
    
    This function combines two steps:
    1. Find an initial x such that func(x) ≈ y_target using `search_function`
    2. If needed, adjust x to ensure the specified bound relationship using `adjust_for_sign`
    
    The bound guarantees are useful in many scenarios:
    - For confidence intervals/bounds: use UPPER bound to ensure y ≤ y_target
    - For approximating inverse functions with safety guarantees
    - For optimization problems where overshooting may be problematic
    - For controlling numerical errors in one direction only
    
    Args:
        func: Function to search (maps x -> y)
        y_target: Target y value we're searching for
        initial_guess: Initial guess for x
        bounds: Tuple of (x_min, x_max) defining search bounds
        tolerance: Acceptable tolerance for the result
        function_type: Type of function (FunctionType enum)
        bound_type: Type of bound to ensure (BoundType enum)
        verbosity: Verbosity level for outputs (Verbosity enum)
        
    Returns:
        x value satisfying the desired relationship with y_target, or None if not found
        
    Raises:
        ValueError: If invalid inputs are provided
        RuntimeError: If the search or adjustment process fails unexpectedly
        
    Examples:
        # Find x where f(x) = 10, with guarantee that f(x) ≤ 10
        >>> result = search_function_with_bounds(f, 10, bound_type=BoundType.UPPER)
        
        # Find x where f(x) = 5 for a convex function, guaranteeing f(x) ≥ 5
        >>> result = search_function_with_bounds(f, 5, function_type=FunctionType.CONVEX, 
                                              bound_type=BoundType.LOWER)
    """
    
    # Flag for whether to print warnings
    should_print_warning = _should_print_warning(verbosity)
    # Flag for whether to print info messages
    should_print_info = _should_print_info(verbosity)
    
    # Input validation
    if not isinstance(function_type, FunctionType):
        if should_print_warning:
            print(f"[WARNING] function_type must be a FunctionType enum, got {type(function_type)}")
        raise ValueError(f"function_type must be a FunctionType enum, got {type(function_type)}")
    
    if not isinstance(bound_type, BoundType):
        if should_print_warning:
            print(f"[WARNING] bound_type must be a BoundType enum, got {type(bound_type)}")
        raise ValueError(f"bound_type must be a BoundType enum, got {type(bound_type)}")
    
    if tolerance <= 0:
        if should_print_warning:
            print(f"[WARNING] tolerance must be positive, got {tolerance}")
        raise ValueError(f"tolerance must be positive, got {tolerance}")
    
    if should_print_info:
        print(f"[INFO] search_function_with_bounds: target={y_target}, " +
              f"function_type={function_type}, bound_type={bound_type}, bounds={bounds}")
    
    # Step 1: Find an initial solution that approximates func(x) = y_target
    x_result: Optional[float] = search_function(
        func, y_target, verbosity, initial_guess, bounds, tolerance, function_type
    )
    
    # Handle the case where search_function returns None but we have bounds and a bound type requirement
    if x_result is None and bounds is not None and bound_type in [BoundType.UPPER, BoundType.LOWER]:
        x_min, x_max = bounds
        try:
            y_min = func(x_min)
            y_max = func(x_max)
            
            if should_print_info:
                print(f"[INFO] Checking boundary values since search_function returned None: " +
                      f"f({x_min})={y_min}, f({x_max})={y_max}, target={y_target}")
            
            # For UPPER bound, we need f(x) ≤ y_target
            if bound_type == BoundType.UPPER:
                if y_min <= y_target and y_max <= y_target:
                    # Both satisfy the bound, choose closest to target
                    if abs(y_min - y_target) <= abs(y_max - y_target):
                        x_result = x_min
                        if should_print_info:
                            print(f"[INFO] Both bounds satisfy UPPER bound. Choosing x_min={x_min} as it's closer to target")
                    else:
                        x_result = x_max
                        if should_print_info:
                            print(f"[INFO] Both bounds satisfy UPPER bound. Choosing x_max={x_max} as it's closer to target")
                elif y_min <= y_target:
                    x_result = x_min
                    if should_print_info:
                        print(f"[INFO] Lower bound satisfies UPPER bound requirement. Using x_min={x_min}")
                elif y_max <= y_target:
                    x_result = x_max
                    if should_print_info:
                        print(f"[INFO] Upper bound satisfies UPPER bound requirement. Using x_max={x_max}")
                else:
                    if should_print_warning:
                        print(f"[WARNING] Neither boundary value satisfies UPPER bound requirement")
            
            # For LOWER bound, we need f(x) ≥ y_target
            elif bound_type == BoundType.LOWER:
                if y_min >= y_target and y_max >= y_target:
                    # Both satisfy the bound, choose closest to target
                    if abs(y_min - y_target) <= abs(y_max - y_target):
                        x_result = x_min
                        if should_print_info:
                            print(f"[INFO] Both bounds satisfy LOWER bound. Choosing x_min={x_min} as it's closer to target")
                    else:
                        x_result = x_max
                        if should_print_info:
                            print(f"[INFO] Both bounds satisfy LOWER bound. Choosing x_max={x_max} as it's closer to target")
                elif y_min >= y_target:
                    x_result = x_min
                    if should_print_info:
                        print(f"[INFO] Lower bound satisfies LOWER bound requirement. Using x_min={x_min}")
                elif y_max >= y_target:
                    x_result = x_max
                    if should_print_info:
                        print(f"[INFO] Upper bound satisfies LOWER bound requirement. Using x_max={x_max}")
                else:
                    if should_print_warning:
                        print(f"[WARNING] Neither boundary value satisfies LOWER bound requirement")
        
        except Exception as e:
            if should_print_warning:
                print(f"[WARNING] Failed to evaluate boundary values: {str(e)}")
    
    # Print warning if still None
    if x_result is None and should_print_warning:
        print(f"[WARNING] search_function failed to find a solution for y_target={y_target}")
    
    # Step 2: If needed, adjust to ensure the desired sign relationship
    result = adjust_for_sign(
        func, x_result, y_target, tolerance, function_type, bound_type, verbosity
    )
    
    if result is None and should_print_warning:
        print(f"[WARNING] adjust_for_sign failed to adjust the solution for y_target={y_target}")
    elif should_print_info and result is not None:
        final_y = func(result)
        error = final_y - y_target
        print(f"[INFO] Final solution: x={result}, f(x)={final_y}, " +
              f"target={y_target}, error={error}, bound_type={bound_type}")
    
    return result
"""
Utility functions for slider controls and parameter management.

This module provides helper functions for automatically determining appropriate
slider configurations based on parameter ranges.
"""

import math
from typing import List, Union, Dict
import numpy as np



def calculate_slider_steps(min_values: List[float], max_values: List[float]) -> List[float]:
    """
    Calculate reasonable slider steps based on parameter ranges.
    
    This function analyzes the range of each parameter and suggests an appropriate
    step size that provides good granularity. The step sizes are the same as input
    steps to ensure consistent behavior between sliders and input fields:
    - Ranges < 100: step = 0.01
    - Ranges 100-999: step = 0.1  
    - Ranges 1000+: step = 1.0
    
    Args:
        min_values (List[float]): List of minimum values for each parameter
        max_values (List[float]): List of maximum values for each parameter
        
    Returns:
        List[float]: List of recommended step sizes for each parameter
        
    Raises:
        ValueError: If lists have different lengths or if any max < min
        
    Examples:
        >>> min_vals = [0, 0, 0, 0]
        >>> max_vals = [10, 100, 1000, 0.1]
        >>> steps = calculate_slider_steps(min_vals, max_vals)
        >>> steps
        [0.01, 0.1, 1.0, 0.01]
        
        >>> # Temperature range
        >>> steps = calculate_slider_steps([20], [100])
        >>> steps[0]
        0.01
    """
    if len(min_values) != len(max_values):
        raise ValueError("min_values and max_values must have the same length")
    
    steps = []
    
    for min_val, max_val in zip(min_values, max_values):
        if max_val < min_val:
            raise ValueError(f"max_value ({max_val}) cannot be less than min_value ({min_val})")
        
        # Calculate the range
        range_val = max_val - min_val
        
        if range_val == 0:
            # If no range, use a very small step
            steps.append(0.001)
            continue
        
        # Calculate step based on range magnitude
        step = _calculate_step_for_range(range_val)
        steps.append(step)
    
    return steps


def _calculate_step_for_range(range_val: float) -> float:
    """
    Calculate an appropriate step size for a given range.
    
    Uses the same step sizes as input steps to ensure sliders and inputs
    have consistent granularity:
    - Ranges < 100: step = 0.01
    - Ranges 100-999: step = 0.1
    - Ranges 1000+: step = 1.0
    
    Args:
        range_val (float): The range (max - min) for the parameter
        
    Returns:
        float: Recommended step size
    """
    if range_val <= 0:
        return 0.01
    
    # Use the same logic as input steps for consistency
    if range_val < 100:
        return 0.01
    elif range_val < 1000:
        return 0.1
    else:
        return 1.0


def _calculate_input_step_for_range(range_val: float) -> float:
    """
    Calculate an appropriate input step size for a given range.
    
    Input steps are finer than slider steps to allow more precise control:
    - Ranges < 100: input step = 0.01
    - Ranges 100-999: input step = 0.1
    - Ranges 1000+: input step = 1.0
    
    Args:
        range_val (float): The range (max - min) for the parameter
        
    Returns:
        float: Recommended input step size
    """
    if range_val < 100:
        return 0.01
    elif range_val < 1000:
        return 0.1
    else:
        return 1.0


def calculate_input_steps(min_values: List[float], max_values: List[float]) -> List[float]:
    """
    Calculate appropriate input step sizes based on parameter ranges.
    
    Input steps are typically finer than slider steps to allow precise adjustment.
    
    Args:
        min_values (List[float]): List of minimum values for each parameter
        max_values (List[float]): List of maximum values for each parameter
        
    Returns:
        List[float]: List of recommended input step sizes for each parameter
    """
    if len(min_values) != len(max_values):
        raise ValueError("min_values and max_values must have the same length")
    
    input_steps = []
    
    for min_val, max_val in zip(min_values, max_values):
        if max_val < min_val:
            raise ValueError(f"max_value ({max_val}) cannot be less than min_value ({min_val})")
        
        # Calculate the range
        range_val = max_val - min_val
        
        # Calculate input step based on range magnitude
        input_step = _calculate_input_step_for_range(range_val)
        input_steps.append(input_step)
    
    return input_steps


def _round_to_reasonable_precision(value: float) -> float:
    """
    Round a step value to a reasonable precision for UI display.
    
    Args:
        value (float): The step value to round
        
    Returns:
        float: Rounded step value
    """
    if value >= 1:
        # For values >= 1, round to reasonable whole numbers or simple decimals
        if value >= 10:
            return round(value)
        else:
            return round(value, 1)
    else:
        # For values < 1, determine appropriate decimal places
        magnitude = math.floor(math.log10(value))
        decimal_places = max(1, -magnitude + 1)
        return round(value, decimal_places)


def calculate_mark_intervals(min_values: List[float], max_values: List[float], 
                           target_marks: int = 5) -> List[float]:
    """
    Calculate mark intervals for sliders based on range magnitude.
    
    Creates marks at regular intervals that align with intuitive values:
    - Range < 1: marks on every 0.1 (interval = 0.1)
    - Range < 10: marks on every integer (interval = 1.0)  
    - Range < 100: marks on every multiple of 10 (interval = 10.0)
    - Range >= 100: marks on every multiple of 100 (interval = 100.0)
    
    Args:
        min_values (List[float]): List of minimum values for each parameter
        max_values (List[float]): List of maximum values for each parameter
        target_marks (int): Target number of marks to display (unused, kept for compatibility)
        
    Returns:
        List[float]: List of recommended mark intervals for each parameter
        
    Examples:
        >>> min_vals = [0, 0, 0, 0]
        >>> max_vals = [0.5, 5, 50, 500]
        >>> intervals = calculate_mark_intervals(min_vals, max_vals)
        >>> intervals
        [0.1, 1.0, 10.0, 100.0]
    """
    if len(min_values) != len(max_values):
        raise ValueError("min_values and max_values must have the same length")
    
    intervals = []
    
    for min_val, max_val in zip(min_values, max_values):
        range_val = max_val - min_val
        
        if range_val == 0:
            intervals.append(1.0)
            continue
        
        # Determine interval based on range magnitude
        # Also consider the number of marks to avoid overcrowding
        if range_val < 1:
            interval = 0.1  # Every 0.1 for very small ranges
        elif range_val < 10:
            interval = 1.0  # Every integer for ranges like 0-9.9
        elif range_val < 100:
            interval = 10.0  # Every multiple of 10
        else:
            interval = 100.0  # Every multiple of 100
        
        intervals.append(interval)
    
    return intervals


def create_slider_config(min_values: List[float], max_values: List[float],
                        property_values: List[float] = None) -> dict:
    """
    Create complete slider configurations with automatically calculated steps and marks.
    
    This is a convenience function that combines step and mark interval calculations
    to create ready-to-use slider configurations. If property values are provided,
    they will be validated and adjusted to align with the calculated slider grid.
    
    Args:
        min_values (List[float]): Minimum values for each slider
        max_values (List[float]): Maximum values for each slider
        property_values (List[float], optional): Current property values to validate
                                               against slider grid. If provided, values
                                               will be snapped to nearest valid step.
        
    Returns:
        dict: Configuration dictionary with keys:
            - 'min_vals' (List[float]): Minimum values for each slider (snapped to slider grid)
            - 'max_vals' (List[float]): Maximum values for each slider (snapped to slider grid)
            - 'step_vals' (List[float]): Calculated step values for each slider (same as input steps)
            - 'input_step_vals' (List[float]): Step values for inputs (same as slider steps)
            - 'mark_vals' (List[dict]): Mark positions for each slider (position → None mapping)
            - 'grid_slider_vals' (List[float], optional): Property values snapped to slider grid if provided
            - 'grid_input_vals' (List[float], optional): Property values snapped to input grid if provided
        
    Example:
        >>> config = create_slider_config(
        ...     min_values=[0, 20, 0],
        ...     max_values=[100, 80, 1000],
        ...     property_values=[23.7, 45.3, 567.8]
        ... )
        >>> config['step_vals']
        [0.01, 0.01, 1.0]
        >>> config['input_step_vals']
        [0.01, 0.01, 1.0]
        >>> config['grid_vals'][0]  # 23.7 snapped to grid
        23.7
    """
    # Validate inputs
    if len(min_values) != len(max_values):
        raise ValueError("min_values and max_values must have the same length")
    
    if property_values is not None and len(property_values) != len(min_values):
        raise ValueError("property_values must have the same length as min_values and max_values")
    
    # Calculate steps and mark intervals
    steps = calculate_slider_steps(min_values, max_values)  # Use the calculated steps directly
    
    input_steps = calculate_input_steps(min_values, max_values)  # Calculate input steps based on range
    
    # Snap min and max values to the slider grid
    grid_min_values = []
    grid_max_values = []
    for i, (min_val, max_val, step) in enumerate(zip(min_values, max_values, steps)):
        # For min value: round down to nearest grid point (floor)
        grid_min = min_val - (min_val % step) if min_val % step != 0 else min_val
        
        # For max value: round up to nearest grid point (ceil)
        if max_val % step == 0:
            grid_max = max_val
        else:
            grid_max = max_val + (step - (max_val % step))
        
        grid_min_values.append(grid_min)
        grid_max_values.append(grid_max)
    
    mark_intervals = calculate_mark_intervals(grid_min_values, grid_max_values)
    
    # Create mark dictionaries for each slider
    mark_vals = []
    grid_slider_vals = []
    grid_input_vals = []
    
    for i, (min_val, max_val, step, input_step, mark_interval) in enumerate(
        zip(grid_min_values, grid_max_values, steps, input_steps, mark_intervals)
    ):
        # Generate marks dictionary for this slider (positions only, no labels)
        marks = {}
        
        # Find the first mark position that's a multiple of mark_interval
        # Start from the nearest multiple of mark_interval >= min_val
        if mark_interval > 0:
            first_mark = math.ceil(min_val / mark_interval) * mark_interval
            current_mark = first_mark
            
            while current_mark <= max_val:
                # Round to avoid floating-point precision issues
                rounded_mark = round(current_mark, 10)  # Round to 10 decimal places
                marks[rounded_mark] = ''  # No label
                current_mark += mark_interval
                
                # Ensure we don't exceed max_val due to floating point precision
                if current_mark > max_val + mark_interval * 0.01:
                    break
        
        mark_vals.append(marks)
        
        # Handle property value if provided
        if property_values is not None:
            property_val = property_values[i]
            # Snap to both slider grid (coarser) and input grid (finer) without clamping to range
            slider_grid_value = snap_to_grid_no_clamp(property_val, min_val, step)
            input_grid_value = snap_to_grid_no_clamp(property_val, min_val, input_step)
            grid_slider_vals.append(slider_grid_value)
            grid_input_vals.append(input_grid_value)
    
    # Create the configuration dictionary
    config = {
        'min_vals': grid_min_values,
        'max_vals': grid_max_values,
        'step_vals': steps,
        'input_step_vals': input_steps,
        'mark_vals': mark_vals
    }
    
    # Add grid values if property values were provided
    if property_values is not None:
        config['grid_slider_vals'] = grid_slider_vals
        config['grid_input_vals'] = grid_input_vals
    
    return config


def create_range_slider_config(min_values: List[float], max_values: List[float],
                              lower_values: List[float] = None, 
                              upper_values: List[float] = None) -> dict:
    """
    Create complete range slider configurations with automatically calculated steps and marks.
    
    This is a convenience function that combines step and mark interval calculations
    to create ready-to-use range slider configurations. If lower and upper values are provided,
    they will be validated, adjusted to ensure proper ordering, and aligned with the 
    calculated slider grids.
    
    Args:
        min_values (List[float]): Minimum values for each range slider
        max_values (List[float]): Maximum values for each range slider
        lower_values (List[float], optional): Current lower bound values for each range slider.
                                            Will be snapped to grid and validated.
        upper_values (List[float], optional): Current upper bound values for each range slider.
                                            Will be snapped to grid and validated.
        
    Returns:
        dict: Complete configuration dictionary containing:
            - 'min_vals' (List[float]): Minimum values for each range slider (snapped to slider grid)
            - 'max_vals' (List[float]): Maximum values for each range slider (snapped to slider grid)
            - 'step_vals' (List[float]): Calculated step values for each range slider (same as input steps)
            - 'input_step_vals' (List[float]): Step values for inputs (same as slider steps)
            - 'mark_vals' (List[dict]): Mark positions for each range slider (position → '' mapping)
            - 'grid_slider_vals' (List[tuple], optional): Range values snapped to slider grid if provided [(lower, upper), ...]
            - 'grid_input_vals' (List[tuple], optional): Range values snapped to input grid if provided [(lower, upper), ...]
        
    Example:
        >>> config = create_range_slider_config(
        ...     min_values=[0, 20, 0],
        ...     max_values=[100, 80, 1000],
        ...     lower_values=[23.7, 45.3, 167.8],
        ...     upper_values=[67.2, 55.1, 834.5]
        ... )
        >>> config['step_vals']
        [0.01, 0.01, 1.0]
        >>> config['input_step_vals']
        [0.01, 0.01, 1.0]
        >>> config['grid_slider_vals'][0]  # (23.7, 67.2) snapped to slider grid
        (23.7, 67.2)
    """
    # Validate inputs
    if len(min_values) != len(max_values):
        raise ValueError("min_values and max_values must have the same length")
    
    if lower_values is not None and len(lower_values) != len(min_values):
        raise ValueError("lower_values must have the same length as min_values and max_values")
        
    if upper_values is not None and len(upper_values) != len(min_values):
        raise ValueError("upper_values must have the same length as min_values and max_values")
    
    # Both lower_values and upper_values must be provided together or not at all
    if (lower_values is None) != (upper_values is None):
        raise ValueError("lower_values and upper_values must both be provided or both be None")
    
    # Calculate steps and mark intervals
    steps = calculate_slider_steps(min_values, max_values)  # Use the calculated steps directly
    
    input_steps = calculate_input_steps(min_values, max_values)  # Calculate input steps based on range

    # Snap min and max values to the slider grid
    grid_min_values = []
    grid_max_values = []
    for i, (min_val, max_val, step) in enumerate(zip(min_values, max_values, steps)):
        # For min value: round down to nearest grid point (floor)
        grid_min = min_val - (min_val % step) if min_val % step != 0 else min_val
        
        # For max value: round up to nearest grid point (ceil)
        remainder = max_val % step
        grid_max = max_val + (step - remainder) if remainder != 0 else max_val
        
        grid_min_values.append(grid_min)
        grid_max_values.append(grid_max)

    mark_intervals = calculate_mark_intervals(grid_min_values, grid_max_values)
    
    # Generate marks for each slider
    mark_vals = []
    for min_val, max_val, interval in zip(grid_min_values, grid_max_values, mark_intervals):
        marks = {}
        
        # Find the first mark position that's a multiple of interval
        # Start from the nearest multiple of interval >= min_val
        if interval > 0:
            first_mark = math.ceil(min_val / interval) * interval
            current = first_mark
            
            while current <= max_val:
                # Round to avoid floating-point precision issues
                rounded_mark = round(current, 10)  # Round to 10 decimal places
                marks[rounded_mark] = ''  # Empty string for clean appearance
                current += interval
        
        mark_vals.append(marks)

    # Process property values if provided
    grid_slider_vals = []
    grid_input_vals = []
    
    if lower_values is not None and upper_values is not None:
        for i, (min_val, max_val, step, input_step, lower_val, upper_val) in enumerate(
            zip(grid_min_values, grid_max_values, steps, input_steps, lower_values, upper_values)
        ):
            # Ensure proper ordering of lower/upper values
            actual_lower = min(lower_val, upper_val)
            actual_upper = max(lower_val, upper_val)
            
            # Snap to grids
            lower_slider_grid = snap_to_grid_no_clamp(actual_lower, min_val, step)
            upper_slider_grid = snap_to_grid_no_clamp(actual_upper, min_val, step)
            lower_input_grid = snap_to_grid_no_clamp(actual_lower, min_val, input_step)
            upper_input_grid = snap_to_grid_no_clamp(actual_upper, min_val, input_step)
            
            # Store as tuples
            grid_slider_vals.append((lower_slider_grid, upper_slider_grid))
            grid_input_vals.append((lower_input_grid, upper_input_grid))

    # Create the configuration dictionary
    config = {
        'min_vals': grid_min_values,
        'max_vals': grid_max_values,
        'step_vals': steps,
        'input_step_vals': input_steps,
        'mark_vals': mark_vals
    }
    
    # Add grid values if property values were provided
    if lower_values is not None and upper_values is not None:
        config['grid_slider_vals'] = grid_slider_vals
        config['grid_input_vals'] = grid_input_vals
    
    return config


def snap_to_slider_grid(value: float, min_val: float, max_val: float, step: float) -> float:
    """
    Snap a value to the nearest valid position on a slider grid.
    
    This ensures that property values align with the discrete steps of a slider,
    preventing issues with values that fall between valid slider positions.
    
    Args:
        value (float): The value to snap to the grid
        min_val (float): Minimum value of the slider range
        max_val (float): Maximum value of the slider range
        step (float): Step size of the slider
        
    Returns:
        float: Value snapped to the nearest valid slider position
        
    Examples:
        >>> # Snap 23.7 to a slider with step 0.1
        >>> snap_to_slider_grid(23.7, 0, 100, 0.1)
        23.7
        
        >>> # Snap 23.75 to a slider with step 0.1 
        >>> snap_to_slider_grid(23.75, 0, 100, 0.1)
        23.8
        
        >>> # Clamp value outside range
        >>> snap_to_slider_grid(150, 0, 100, 1.0)
        100.0
    """
    # First clamp to range
    clamped_value = max(min_val, min(max_val, value))
    
    # Calculate offset from minimum
    offset = clamped_value - min_val
    
    # Round to nearest step
    num_steps = round(offset / step)
    
    # Calculate snapped value
    snapped_value = min_val + (num_steps * step)
    
    # Ensure we stay within bounds (floating point precision issues)
    snapped_value = max(min_val, min(max_val, snapped_value))
    
    # Round to appropriate precision based on step size
    if step >= 1:
        return round(snapped_value)
    else:
        decimal_places = max(0, -math.floor(math.log10(step)))
        return round(snapped_value, decimal_places)


def snap_to_grid_no_clamp(value: float, min_val: float, step: float) -> float:
    """
    Snap a value to the nearest grid position without clamping to range.
    
    This function snaps values to the grid defined by min_val and step,
    but does NOT clamp values to stay within a min/max range. This allows
    property values outside the slider range to maintain their relative
    position on the extended grid.
    
    Args:
        value (float): The value to snap to the grid
        min_val (float): Minimum value of the slider range (grid reference point)
        step (float): Step size of the grid
        
    Returns:
        float: Value snapped to the nearest valid grid position
        
    Examples:
        >>> # Snap value within range
        >>> snap_to_grid_no_clamp(23.75, 0, 0.1)
        23.8
        
        >>> # Snap value outside range (not clamped)
        >>> snap_to_grid_no_clamp(150.3, 0, 0.1)
        150.3
        
        >>> # Snap value below range (not clamped)
        >>> snap_to_grid_no_clamp(-5.67, 0, 0.1)
        -5.7
    """
    # Calculate offset from minimum (no clamping)
    offset = value - min_val
    
    # Round to nearest step
    num_steps = round(offset / step)
    
    # Calculate snapped value
    snapped_value = min_val + (num_steps * step)
    
    # Round to appropriate precision based on step size
    if step >= 1:
        return round(snapped_value)
    else:
        decimal_places = max(0, -math.floor(math.log10(step)))
        return round(snapped_value, decimal_places)


def format_slider_value(value: float, step: float) -> str:
    """
    Format a slider value for display based on the step size.
    
    Automatically determines appropriate decimal places based on the step size
    to avoid displaying unnecessary precision.
    
    Args:
        value (float): The value to format
        step (float): The step size of the slider
        
    Returns:
        str: Formatted value string
        
    Examples:
        >>> format_slider_value(123.456, 1.0)
        '123'
        >>> format_slider_value(123.456, 0.1)
        '123.5'
        >>> format_slider_value(123.456, 0.01)
        '123.46'
    """
    if step >= 1:
        return f"{value:.0f}"
    else:
        # Determine decimal places based on step size
        decimal_places = max(0, -math.floor(math.log10(step)))
        return f"{value:.{decimal_places}f}"


def are_slider_input_values_incompatible(
    slider_value: float, 
    input_value: float, 
    slider_step: float, 
    input_step: float
) -> bool:
    """
    Check if slider and input values are incompatible with each other.
    
    Two values are considered incompatible if there is no single original value
    that would snap to both the given slider grid value AND the given input grid value.
    This typically happens when the slider value and input value represent different
    original values that have been snapped to their respective grids.
    
    Args:
        slider_value (float): The value from the slider grid
        input_value (float): The value from the input grid  
        slider_step (float): Step size for the slider grid
        input_step (float): Step size for the input grid
        
    Returns:
        bool: True if the values are incompatible, False if they could represent
              the same original value snapped to different grids
              
    Examples:
        >>> # Compatible values: both could come from original value 12.36
        >>> are_slider_input_values_incompatible(12.4, 12.36, 0, 0.1, 0.01)
        False
        
        >>> # Incompatible values: no single value could snap to both
        >>> are_slider_input_values_incompatible(12.3, 12.36, 0, 0.1, 0.01) 
        True
        
        >>> # Compatible values: both could come from original value 12.35
        >>> are_slider_input_values_incompatible(12.4, 12.35, 0, 0.1, 0.01)
        False
    """
    # Calculate the range of original values that would snap to the slider_value
    slider_half_step = slider_step / 2.0
    slider_min_original = slider_value - slider_half_step
    slider_max_original = slider_value + slider_half_step
    
    # Calculate the range of original values that would snap to the input_value  
    input_half_step = input_step / 2.0
    input_min_original = input_value - input_half_step
    input_max_original = input_value + input_half_step
    
    # Check if the ranges overlap
    # If they overlap, there exists at least one original value that would snap to both
    overlap_start = max(slider_min_original, input_min_original)
    overlap_end = min(slider_max_original, input_max_original)
    
    # If overlap_start > overlap_end, there's no overlap (incompatible)
    # Use a small tolerance for floating-point comparison
    tolerance = 1e-12
    return overlap_start > overlap_end + tolerance



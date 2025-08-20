"""
Unit tests for SliderControls utility functions.
"""

import unittest
import math
from steer_core.Apps.Utils.SliderControls import (
    calculate_slider_steps, 
    calculate_mark_intervals, 
    create_slider_config,
    snap_to_slider_grid
)


class TestSliderControls(unittest.TestCase):
    """Test cases for slider control utility functions."""
    
    def test_calculate_slider_steps_basic(self):
        """Test basic step calculation functionality."""
        min_vals = [0, 0, 0]
        max_vals = [10, 100, 1000]
        steps = calculate_slider_steps(min_vals, max_vals)
        
        # Should have 3 steps
        self.assertEqual(len(steps), 3)
        
        # Steps should be reasonable for their ranges
        self.assertLessEqual(steps[0], 1.0)  # 10 range
        self.assertLessEqual(steps[1], 10.0)  # 100 range
        self.assertLessEqual(steps[2], 100.0)  # 1000 range
        
        # All steps should be positive
        for step in steps:
            self.assertGreater(step, 0)
    
    def test_calculate_slider_steps_edge_cases(self):
        """Test edge cases for step calculation."""
        # Zero range
        steps = calculate_slider_steps([5], [5])
        self.assertEqual(steps[0], 0.001)
        
        # Very small range
        steps = calculate_slider_steps([0], [0.001])
        self.assertGreater(steps[0], 0)
        self.assertLess(steps[0], 0.001)
        
        # Negative ranges
        steps = calculate_slider_steps([-100], [100])
        self.assertGreater(steps[0], 0)
    
    def test_calculate_slider_steps_validation(self):
        """Test input validation for step calculation."""
        # Mismatched lengths
        with self.assertRaises(ValueError):
            calculate_slider_steps([0, 1], [10])
        
        # Max < min
        with self.assertRaises(ValueError):
            calculate_slider_steps([10], [5])
    
    def test_calculate_mark_intervals(self):
        """Test mark interval calculation."""
        min_vals = [0, 0]
        max_vals = [100, 1000]
        intervals = calculate_mark_intervals(min_vals, max_vals)
        
        self.assertEqual(len(intervals), 2)
        
        # Intervals should be reasonable
        self.assertGreater(intervals[0], 0)
        self.assertGreater(intervals[1], 0)
        
        # Should be larger than steps for same ranges
        steps = calculate_slider_steps(min_vals, max_vals)
        for interval, step in zip(intervals, steps):
            self.assertGreaterEqual(interval, step)
    
    def test_create_slider_config(self):
        """Test complete slider configuration creation."""
        min_vals = [0, 20]
        max_vals = [100, 80]
        
        config = create_slider_config(min_vals, max_vals)
        
        # Check required keys
        required_keys = ['min_vals', 'max_vals', 'step_vals', 'input_step_vals', 'mark_vals']
        for key in required_keys:
            self.assertIn(key, config)
        
        # Check list lengths
        self.assertEqual(len(config['min_vals']), 2)
        self.assertEqual(len(config['max_vals']), 2)
        self.assertEqual(len(config['step_vals']), 2)
        self.assertEqual(len(config['input_step_vals']), 2)
        self.assertEqual(len(config['mark_vals']), 2)
        
        # Check values - min/max should be grid-snapped but close to originals
        # Grid-snapped min should be <= original min
        for i, (grid_min, orig_min) in enumerate(zip(config['min_vals'], min_vals)):
            self.assertLessEqual(grid_min, orig_min)
            self.assertAlmostEqual(grid_min, orig_min, delta=config['step_vals'][i])
            
        # Grid-snapped max should be >= original max  
        for i, (grid_max, orig_max) in enumerate(zip(config['max_vals'], max_vals)):
            self.assertGreaterEqual(grid_max, orig_max)
            self.assertAlmostEqual(grid_max, orig_max, delta=config['step_vals'][i])
        
        # Check that step values are positive
        for step in config['step_vals']:
            self.assertGreater(step, 0)
        
        # Check that input step values are positive and slider steps are 10x larger than input steps
        # Also check minimum step sizes: slider min 0.1, input min 0.01
        for i, (slider_step, input_step) in enumerate(zip(config['step_vals'], config['input_step_vals'])):
            self.assertGreater(input_step, 0)
            self.assertGreaterEqual(slider_step, 0.1)   # Minimum step size for sliders
            self.assertGreaterEqual(input_step, 0.01)   # Minimum step size for inputs
            # When both are above minimum, slider should be 10x larger than input
            if input_step > 0.01:
                self.assertAlmostEqual(slider_step, input_step * 10.0, places=10)
        
        # Check that mark_vals contains dictionaries
        for marks in config['mark_vals']:
            self.assertIsInstance(marks, dict)
            self.assertGreater(len(marks), 0)
    
    def test_create_slider_config_with_property_values(self):
        """Test slider configuration with property values snapping to grid."""
        min_vals = [0, 20]
        max_vals = [100, 80]
        property_vals = [23.7, 45.3]
        
        config = create_slider_config(min_vals, max_vals, property_vals)
        
        # Check that both grid value types are present
        self.assertIn('grid_slider_vals', config)
        self.assertIn('grid_input_vals', config)
        self.assertEqual(len(config['grid_slider_vals']), 2)
        self.assertEqual(len(config['grid_input_vals']), 2)
        
        # Grid values should be properly snapped to grid (note: no longer constrained to slider range)
        for i, (slider_grid_val, input_grid_val) in enumerate(zip(config['grid_slider_vals'], config['grid_input_vals'])):
            # Values should be snapped to their respective grids
            slider_step = config['step_vals'][i]
            input_step = config['input_step_vals'][i]
            
            # Check grid alignment (values should be on grid)
            slider_offset = (slider_grid_val - config['min_vals'][i]) % slider_step
            input_offset = (input_grid_val - config['min_vals'][i]) % input_step
            
            # Due to floating point precision, offset might be very close to 0 or step size
            self.assertTrue(abs(slider_offset) < 1e-10 or abs(slider_offset - slider_step) < 1e-10, 
                          f"Slider value not on grid: offset={slider_offset}")
            self.assertTrue(abs(input_offset) < 1e-10 or abs(input_offset - input_step) < 1e-10, 
                          f"Input value not on grid: offset={input_offset}")

    def test_create_slider_config_out_of_range_values(self):
        """Test that property values outside slider range are preserved (not clamped)."""
        min_vals = [0, 10]
        max_vals = [100, 50]
        # Property values outside the ranges
        property_vals = [150, 5]  # 150 > 100, 5 < 10
        
        config = create_slider_config(min_vals, max_vals, property_vals)
        
        # Values should be preserved (not clamped to range)
        self.assertEqual(config['grid_slider_vals'][0], 150.0)  # Not clamped to 100
        self.assertEqual(config['grid_slider_vals'][1], 5.0)    # Not clamped to 10
        self.assertEqual(config['grid_input_vals'][0], 150.0)   # Not clamped to 100 
        self.assertEqual(config['grid_input_vals'][1], 5.0)     # Not clamped to 10
        
        # Values should still be on grid
        for i, (slider_val, input_val) in enumerate(zip(config['grid_slider_vals'], config['grid_input_vals'])):
            slider_step = config['step_vals'][i]
            input_step = config['input_step_vals'][i]
            
            # Check grid alignment
            slider_offset = (slider_val - config['min_vals'][i]) % slider_step
            input_offset = (input_val - config['min_vals'][i]) % input_step
            
            # Due to floating point precision, offset might be very close to 0 or step size
            self.assertTrue(abs(slider_offset) < 1e-10 or abs(slider_offset - slider_step) < 1e-10)
            self.assertTrue(abs(input_offset) < 1e-10 or abs(input_offset - input_step) < 1e-10)
    
    def test_create_slider_config_validation(self):
        """Test validation for slider configuration creation."""
        # Mismatched lengths for min/max
        with self.assertRaises(ValueError):
            config = create_slider_config([0], [100, 200])
        
        # Wrong property values length
        with self.assertRaises(ValueError):
            config = create_slider_config([0], [100], [25, 50])
    
    def test_create_slider_config_marks(self):
        """Test that mark_vals are properly structured dictionaries with interval-based marks."""
        min_vals = [0, 10]
        max_vals = [100, 50]
        
        config = create_slider_config(min_vals, max_vals)
        
        # Check mark_vals structure
        self.assertEqual(len(config['mark_vals']), 2)
        
        for i, marks in enumerate(config['mark_vals']):
            self.assertIsInstance(marks, dict)
            
            # Check that all mark keys are floats and values are empty strings (no labels)
            for mark_pos, mark_label in marks.items():
                self.assertIsInstance(mark_pos, (int, float))
                self.assertEqual(mark_label, '')  # Empty string, no labels
                self.assertGreaterEqual(mark_pos, config['min_vals'][i])
                self.assertLessEqual(mark_pos, config['max_vals'][i])
        
        # Check that marks follow interval-based logic
        # First slider: range 0-100 (interval=100.0), should have marks at multiples of 100 within range
        marks1 = config['mark_vals'][0]
        # Range 100 gets interval 100.0, so marks should be at 0, 100
        expected_positions1 = [0.0, 100.0]
        self.assertEqual(sorted(marks1.keys()), expected_positions1)
        
        # Second slider: range 10-50 (range=40, interval=10.0), should have marks at multiples of 10 within range  
        marks2 = config['mark_vals'][1]
        expected_positions2 = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.assertEqual(sorted(marks2.keys()), expected_positions2)
    
    def test_snap_to_slider_grid(self):
        """Test snapping values to slider grid."""
        # Value already on grid
        result = snap_to_slider_grid(23.7, 0, 100, 0.1)
        self.assertAlmostEqual(result, 23.7, places=5)
        
        # Value between grid points
        result = snap_to_slider_grid(23.75, 0, 100, 0.1)
        self.assertAlmostEqual(result, 23.8, places=5)
        
        # Value below minimum
        result = snap_to_slider_grid(-10, 0, 100, 1.0)
        self.assertEqual(result, 0.0)
        
        # Value above maximum
        result = snap_to_slider_grid(150, 0, 100, 1.0)
        self.assertEqual(result, 100.0)
        # Integer step
        result = snap_to_slider_grid(23.7, 0, 100, 1.0)
        self.assertEqual(result, 24.0)
    
    def test_realistic_scenarios(self):
        """Test with realistic parameter scenarios."""
        # Temperature control scenario
        min_vals = [20, 0, 0.1]
        max_vals = [100, 50, 10.0]
        steps = calculate_slider_steps(min_vals, max_vals)
        
        # Temperature (80°C range) - should have fine control
        self.assertLessEqual(steps[0], 1.0)
        
        # Percentage (50% range) - should have reasonable control
        self.assertLessEqual(steps[1], 1.0)
        
        # Flow rate (9.9 L/min range) - should have fine control
        self.assertLessEqual(steps[2], 0.1)


if __name__ == '__main__':
    unittest.main()

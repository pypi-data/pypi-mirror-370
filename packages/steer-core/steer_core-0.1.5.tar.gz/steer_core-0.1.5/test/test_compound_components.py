"""
Unit tests for SliderWithTextInput component with built-in callback logic.

Tests cover component initialization, layout generation, callback registration,
and synchronization behavior.
"""

import unittest
from unittest.mock import Mock, patch
import dash
from dash import html, dcc
import numpy as np

# Import the component
from steer_core.Apps.Components.SliderComponents import SliderWithTextInput


class TestSliderWithTextInput(unittest.TestCase):
    """Test cases for SliderWithTextInput component."""
    
    def setUp(self):

        """Set up test fixtures."""

        self.test_id_base = {'type': 'test', 'index': 0}

        self.component = SliderWithTextInput(
            id_base=self.test_id_base,
            min_val=0.0,
            max_val=100.0,
            step=1.0,
            mark_interval=10.0,
            property_name='test_prop',
            title='Test Component',
            default_val=50.0
        )
    
    def test_initialization(self):
        """Test component initialization and attribute assignment."""
        self.assertEqual(self.component.id_base, self.test_id_base)
        self.assertEqual(self.component.min_val, 0.0)
        self.assertEqual(self.component.max_val, 100.0)
        self.assertEqual(self.component.step, 1.0)
        self.assertEqual(self.component.mark_interval, 10.0)
        self.assertEqual(self.component.property_name, 'test_prop')
        self.assertEqual(self.component.title, 'Test Component')
        self.assertEqual(self.component.default_val, 50.0)
        self.assertTrue(self.component.with_slider_titles)
        self.assertFalse(self.component.slider_disable)
        self.assertEqual(self.component.div_width, 'calc(90%)')
    
    def test_id_generation(self):
        """Test ID generation for component elements."""
        expected_slider_id = {
            **self.test_id_base,
            'subtype': 'slider',
            'property': 'test_prop'
        }
        expected_input_id = {
            **self.test_id_base,
            'subtype': 'input',
            'property': 'test_prop'
        }
        
        self.assertEqual(self.component.slider_id, expected_slider_id)
        self.assertEqual(self.component.input_id, expected_input_id)
    
    def test_make_id_method(self):
        """Test the _make_id private method."""
        result = self.component._make_id('custom_subtype')
        expected = {
            **self.test_id_base,
            'subtype': 'custom_subtype',
            'property': 'test_prop'
        }
        self.assertEqual(result, expected)
    
    def test_make_slider(self):
        """Test slider component creation."""
        slider = self.component._make_slider()
        
        self.assertIsInstance(slider, dcc.Slider)
        self.assertEqual(slider.id, self.component.slider_id)
        self.assertEqual(slider.min, 0.0)
        self.assertEqual(slider.max, 100.0)
        self.assertEqual(slider.value, 50.0)
        self.assertEqual(slider.step, 1.0)
        self.assertFalse(slider.disabled)
        self.assertEqual(slider.updatemode, 'mouseup')
        
        # Test marks generation
        expected_marks = {int(i): "" for i in np.arange(0.0, 110.0, 10.0)}
        self.assertEqual(slider.marks, expected_marks)
    
    def test_make_input(self):
        """Test input component creation."""
        input_comp = self.component._make_input()
        
        self.assertIsInstance(input_comp, dcc.Input)
        self.assertEqual(input_comp.id, self.component.input_id)
        self.assertEqual(input_comp.type, 'number')
        self.assertEqual(input_comp.value, 50.0)
        self.assertEqual(input_comp.step, 1.0)
        self.assertFalse(input_comp.disabled)
        self.assertEqual(input_comp.style, {'margin-left': '20px'})
    
    def test_call_method(self):
        """Test the __call__ method that generates the complete layout."""
        layout = self.component()
        
        self.assertIsInstance(layout, html.Div)
        self.assertEqual(len(layout.children), 5)  # P, Div, Input, Br, Br
        
        # Check title paragraph
        title_p = layout.children[0]
        self.assertIsInstance(title_p, html.P)
        self.assertEqual(title_p.children, 'Test Component')
    
    def test_call_method_without_title(self):
        """Test layout generation with titles disabled."""
        self.component.with_slider_titles = False
        layout = self.component()
        
        title_p = layout.children[0]
        self.assertEqual(title_p.children, "\u00A0")  # Non-breaking space
    
    def test_components_property(self):
        """Test the components property."""
        components = self.component.components
        
        expected = {
            'slider': self.component.slider_id,
            'input': self.component.input_id
        }
        self.assertEqual(components, expected)
    
    def test_validate_and_clamp_value(self):
        """Test value validation and clamping."""
        # Test normal value
        self.assertEqual(self.component._validate_and_clamp_value(50.0), 50.0)
        
        # Test value below minimum
        self.assertEqual(self.component._validate_and_clamp_value(-10.0), 0.0)
        
        # Test value above maximum
        self.assertEqual(self.component._validate_and_clamp_value(150.0), 100.0)
        
        # Test None value
        self.assertEqual(self.component._validate_and_clamp_value(None), 50.0)
        
        # Test invalid string
        self.assertEqual(self.component._validate_and_clamp_value("invalid"), 50.0)
    
    def test_validate_and_clamp_value_no_default(self):
        """Test value validation when no default value is set."""
        component = SliderWithTextInput(
            id_base=self.test_id_base,
            min_val=0.0,
            max_val=100.0,
            step=1.0,
            mark_interval=10.0,
            property_name='test_prop',
            title='Test Component',
            default_val=None
        )
        
        # Should return min_val when no default and invalid input
        self.assertEqual(component._validate_and_clamp_value(None), 0.0)
        self.assertEqual(component._validate_and_clamp_value("invalid"), 0.0)
    
        
    def test_no_automatic_callbacks(self):
        """Test that component no longer has automatic callback registration methods."""
        # These methods should no longer exist
        with self.assertRaises(AttributeError):
            self.component.register_callbacks()
        
        with self.assertRaises(AttributeError):
            self.component.register_clientside_callbacks()
        
        with self.assertRaises(AttributeError):
            SliderWithTextInput.with_sync(
                id_base=self.test_id_base,
                min_val=0.0,
                max_val=100.0,
                step=1.0,
                mark_interval=10.0,
                property_name='test',
                title='Test'
            )
            
        # Store methods should also no longer exist
        with self.assertRaises(AttributeError):
            self.component.get_store_input()
            
        with self.assertRaises(AttributeError):
            self.component.get_store_output()
            
        # Store ID should no longer exist
        with self.assertRaises(AttributeError):
            self.component.store_id
    
    def test_disabled_components(self):
        """Test component creation with disabled state."""
        disabled_component = SliderWithTextInput(
            id_base=self.test_id_base,
            min_val=0.0,
            max_val=100.0,
            step=1.0,
            mark_interval=10.0,
            property_name='disabled_test',
            title='Disabled Test',
            slider_disable=True
        )
        
        slider = disabled_component._make_slider()
        input_comp = disabled_component._make_input()
        
        self.assertTrue(slider.disabled)
        self.assertTrue(input_comp.disabled)
    
    def test_custom_div_width(self):
        """Test component with custom div width."""
        custom_component = SliderWithTextInput(
            id_base=self.test_id_base,
            min_val=0.0,
            max_val=100.0,
            step=1.0,
            mark_interval=10.0,
            property_name='width_test',
            title='Width Test',
            div_width='50%'
        )
        
        layout = custom_component()
        self.assertEqual(layout.style['width'], '50%')
    
    def test_get_value_inputs(self):
        """Test the get_value_inputs helper method."""
        inputs = self.component.get_value_inputs()
        
        # Should return a list with two Input objects
        self.assertEqual(len(inputs), 2)
        
        # Check slider input
        slider_input = inputs[0]
        self.assertEqual(slider_input.component_id, self.component.slider_id)
        self.assertEqual(slider_input.component_property, 'value')
        
        # Check input input
        input_input = inputs[1]
        self.assertEqual(input_input.component_id, self.component.input_id)
        self.assertEqual(input_input.component_property, 'value')
    
    def test_get_value_outputs(self):
        """Test the get_value_outputs helper method."""
        outputs = self.component.get_value_outputs()
        
        # Should return a list with two Output objects
        self.assertEqual(len(outputs), 2)
        
        # Check slider output
        slider_output = outputs[0]
        self.assertEqual(slider_output.component_id, self.component.slider_id)
        self.assertEqual(slider_output.component_property, 'value')
        
        # Check input output
        input_output = outputs[1]
        self.assertEqual(input_output.component_id, self.component.input_id)
        self.assertEqual(input_output.component_property, 'value')
    
    def test_get_pattern_matching_value_inputs(self):
        """Test the get_pattern_matching_value_inputs helper method."""
        inputs = self.component.get_pattern_matching_value_inputs('temperature')
        
        # Should return a list with two Input objects
        self.assertEqual(len(inputs), 2)
        
        # Check pattern structure
        slider_pattern = inputs[0].component_id
        self.assertEqual(slider_pattern['type'], 'parameter')
        self.assertEqual(slider_pattern['subtype'], 'slider')
        self.assertEqual(slider_pattern['property'], 'temperature')
        
        input_pattern = inputs[1].component_id
        self.assertEqual(input_pattern['type'], 'parameter')
        self.assertEqual(input_pattern['subtype'], 'input')
        self.assertEqual(input_pattern['property'], 'temperature')
    
    def test_get_pattern_matching_value_outputs(self):
        """Test the get_pattern_matching_value_outputs helper method."""
        outputs = self.component.get_pattern_matching_value_outputs('ALL')
        
        # Should return a list with two Output objects
        self.assertEqual(len(outputs), 2)
        
        # Check pattern structure
        slider_pattern = outputs[0].component_id
        self.assertEqual(slider_pattern['type'], 'parameter')
        self.assertEqual(slider_pattern['subtype'], 'slider')
        self.assertEqual(slider_pattern['property'], 'ALL')
        
        input_pattern = outputs[1].component_id
        self.assertEqual(input_pattern['type'], 'parameter')
        self.assertEqual(input_pattern['subtype'], 'input')
        self.assertEqual(input_pattern['property'], 'ALL')


class TestSliderWithTextInputIntegration(unittest.TestCase):
    """Integration tests for SliderWithTextInput component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = dash.Dash(__name__)
        self.component = SliderWithTextInput(
            id_base={'type': 'test', 'index': 0},
            min_val=0.0,
            max_val=100.0,
            step=1.0,
            mark_interval=10.0,
            property_name='integration_test',
            title='Integration Test Component'
        )
    
    def test_component_creation(self):
        """Test that component creates correctly without auto-sync."""
        self.assertIsInstance(self.component, SliderWithTextInput)
        self.assertEqual(self.component.min_val, 0.0)
        self.assertEqual(self.component.max_val, 100.0)
        self.assertEqual(self.component.property_name, 'integration_test')
    
    def test_component_layout_generation(self):
        """Test that the component generates proper layout."""
        layout = self.component()
        self.assertIsInstance(layout, html.Div)
        # Should have title, slider div, input, and two breaks
        self.assertEqual(len(layout.children), 5)


if __name__ == '__main__':
    unittest.main()

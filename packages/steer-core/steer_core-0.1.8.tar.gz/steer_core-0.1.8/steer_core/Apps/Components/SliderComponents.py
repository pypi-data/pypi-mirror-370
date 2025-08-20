import dash as ds
import numpy as np
from typing import Union
from dash import Input, Output


class SliderWithTextInput:
    """
    A custom Dash component that combines a slider and text input for synchronized value control.
    
    This component creates a user interface element consisting of a slider and a numeric input field
    that can be used together to set numeric values. The slider provides visual feedback and easy
    adjustment, while the text input allows for precise value entry. Both components are synchronized
    and share the same value constraints.
    
    The component is designed for use in Dash applications where users need to input numeric values
    within a specified range, with the flexibility of both visual (slider) and precise (text input)
    control methods.
    
    Attributes:
        id_base (dict): Base identifier dictionary used to construct unique IDs for child components
        min_val (float): Minimum allowed value for both slider and input
        max_val (float): Maximum allowed value for both slider and input
        default_val (Union[float, list[float], None]): Default value to display on initialization
        step (float): Step size for value increments/decrements
        mark_interval (float): Interval between tick marks on the slider
        property_name (str): Property identifier used in component ID construction
        title (str): Display title for the component
        with_slider_titles (bool): Whether to show the title above the slider
        div_width (str): CSS width specification for the container div
        slider_disable (bool): Whether the components should be disabled
        message (str): Optional message displayed between title and slider
        slider_id (dict): Computed ID for the slider component
        input_id (dict): Computed ID for the input component
    
    Example:
        >>> slider_component = SliderWithTextInput(
        ...     id_base={'type': 'parameter', 'index': 0},
        ...     min_val=0.0,
        ...     max_val=100.0,
        ...     step=1.0,
        ...     mark_interval=10.0,
        ...     property_name='temperature',
        ...     title='Temperature (°C)',
        ...     default_val=25.0,
        ...     message='Optimal range is 20-30°C'  # Optional message
        ... )
        >>> layout_element = slider_component()  # Returns Dash HTML Div component
    """

    def __init__(
        self,
        id_base: dict,
        min_val: float,
        max_val: float,
        step: float,
        mark_interval: float,
        property_name: str,
        title: str,
        default_val: Union[float, list[float]] = None,
        with_slider_titles: bool = True,
        slider_disable: bool = False,
        div_width: str = 'calc(90%)',
        message: str = None,
    ):
        """
        Initialize the SliderWithTextInput component.
        
        Args:
            id_base (dict): Base dictionary for generating component IDs. Should contain
                           identifying information that will be extended with component-specific
                           subtypes and properties.
            min_val (float): Minimum value that can be selected on the slider or entered
                           in the text input.
            max_val (float): Maximum value that can be selected on the slider or entered
                           in the text input.
            step (float): The granularity of value changes. Determines the smallest
                         increment/decrement possible.
            mark_interval (float): The spacing between tick marks displayed on the slider.
                                 Should be a multiple of step for best visual alignment.
            property_name (str): A string identifier for this specific property, used
                               in ID generation and callbacks.
            title (str): Human-readable title displayed above the component.
            default_val (Union[float, list[float]], optional): Initial value to display.
                        If None, defaults to min_val. Can be a single float or list
                        for compatibility with range sliders.
            with_slider_titles (bool, optional): If True, displays the title above
                                               the slider. If False, shows a non-breaking
                                               space to maintain layout. Defaults to True.
            slider_disable (bool, optional): If True, disables both slider and input
                                            interactions. Defaults to False.
            div_width (str, optional): CSS width specification for the container div.
                                     Defaults to 'calc(90%)'.
            message (str, optional): Optional message to display between the title
                                   and slider. If None, no message is displayed.
                                   Defaults to None.
        
        Raises:
            ValueError: If min_val >= max_val, or if step <= 0, or if mark_interval <= 0.
            TypeError: If default_val is provided but not numeric.
        """
        
        self.id_base = id_base
        self.min_val = min_val
        self.max_val = max_val
        self.default_val = default_val
        self.step = step
        self.mark_interval = mark_interval
        self.property_name = property_name
        self.title = title
        self.with_slider_titles = with_slider_titles
        self.div_width = div_width
        self.slider_disable = slider_disable
        self.message = message

        self.slider_id = self._make_id('slider')
        self.input_id = self._make_id('input')

    def _make_id(self, subtype: str):
        """
        Generate a unique ID dictionary for component sub-elements.
        
        Combines the base ID with component-specific subtype and property information
        to create unique identifiers for Dash callbacks and component references.
        
        Args:
            subtype (str): The specific component subtype (e.g., 'slider', 'input').
        
        Returns:
            dict: Complete ID dictionary containing base ID information plus subtype
                  and property specifications.
        
        Example:
            >>> component._make_id('slider')
            {'type': 'parameter', 'index': 0, 'subtype': 'slider', 'property': 'temperature'}
        """
        return {**self.id_base, 'subtype': subtype, 'property': self.property_name}

    def _make_slider(self):
        """
        Create and configure the Dash slider component.
        
        Generates a dcc.Slider with the specified range, step size, default value,
        and tick marks. The slider provides visual feedback for value selection
        and is synchronized with the text input component.
        
        Returns:
            dash.dcc.Slider: Configured slider component with ID, value constraints,
                           tick marks, and styling options.
        
        Note:
            - Tick marks are generated at intervals specified by mark_interval
            - updatemode is set to 'mouseup' to reduce callback frequency
            - The slider can be disabled via the slider_disable attribute
        """
        return ds.dcc.Slider(
            id=self.slider_id,
            min=self.min_val,
            max=self.max_val,
            value=self.default_val,
            step=self.step,
            disabled=self.slider_disable,
            marks={int(i): "" for i in np.arange(self.min_val, self.max_val + self.mark_interval, self.mark_interval)},
            updatemode='mouseup'
        )

    def _make_input(self):
        """
        Create and configure the Dash numeric input component.
        
        Generates a dcc.Input with number type for precise value entry.
        The input is synchronized with the slider and provides an alternative
        method for users to specify exact values.
        
        Returns:
            dash.dcc.Input: Configured numeric input component with ID, type,
                          value constraints, styling, and step specification.
        
        Note:
            - Input type is set to 'number' for numeric validation
            - Left margin styling provides visual alignment with slider
            - Step size matches the slider for consistent granularity
        """
        return ds.dcc.Input(
            id=self.input_id,
            type='number',
            value=self.default_val,
            style={'margin-left': '20px'},
            step=self.step,
            disabled=self.slider_disable
        )

    def __call__(self):
        """
        Generate the complete component layout as a callable object.
        
        Creates and returns a Dash HTML Div containing the title, optional message,
        slider, and input components arranged in a cohesive layout. This method allows
        the class instance to be used as a callable that returns the complete
        component structure.
        
        Returns:
            dash.html.Div: Complete component layout containing:
                - Title paragraph (conditional based on with_slider_titles)
                - Optional message paragraph (if message is provided)
                - Slider component in a styled container
                - Numeric input component
                - Spacing elements (line breaks)
        
        Note:
            - Title display is controlled by with_slider_titles attribute
            - When title is hidden, a non-breaking space maintains layout
            - Message is displayed only if provided during initialization
            - Negative bottom margin on slider container reduces spacing
            - Container width is controlled by div_width attribute
        """
        slider_title = self.title if self.with_slider_titles else "\u00A0"
        
        # Build the component list
        components = [
            ds.html.P(slider_title, style={'margin-left': '20px', 'margin-bottom': '0px'})
        ]
        
        # Add optional message if provided
        if self.message:
            components.append(
                ds.html.P(self.message, style={
                    'margin-left': '20px', 
                    'margin-bottom': '5px',
                    'margin-top': '2px',
                    'font-size': '0.9em',
                    'color': '#666666',
                    'font-style': 'italic'
                })
            )
        
        # Add slider, input, and breaks
        components.extend([
            ds.html.Div([self._make_slider()], style={'margin-bottom': '-18px'}),
            self._make_input(),
            ds.html.Br(), ds.html.Br()
        ])

        return ds.html.Div(components, style={'width': self.div_width, 'margin-left': '-20px'})

    @property
    def components(self):
        """
        Get a dictionary mapping component types to their IDs.
        
        Provides easy access to the IDs of the slider and input components
        for use in Dash callbacks and component interactions.
        
        Returns:
            dict: Dictionary with component type keys mapping to their ID dictionaries.
        
        Example:
            >>> component.components
            {
                'slider': {'type': 'parameter', 'subtype': 'slider', 'property': 'temperature'},
                'input': {'type': 'parameter', 'subtype': 'input', 'property': 'temperature'}
            }
        
        Note:
            This property is particularly useful for setting up Dash callbacks
            that need to reference the specific component IDs.
        """
        return {
            'slider': self.slider_id,
            'input': self.input_id
        }
    
    def get_value_inputs(self):
        """
        Get Input objects for listening to component value changes.
        
        Returns a list of Dash Input objects that can be used in callbacks to
        listen for value changes from either the slider or input components.
        
        Returns:
            list: List containing [Input(slider_id, 'value'), Input(input_id, 'value')]
            
        Example:
            >>> @app.callback(
            ...     Output('some-output', 'children'),
            ...     component.get_value_inputs()
            ... )
            ... def update_display(slider_val, input_val):
            ...     return f"Value: {slider_val or input_val}"
        """
        return [
            Input(self.slider_id, 'value'),
            Input(self.input_id, 'value')
        ]
    
    def get_value_outputs(self):
        """
        Get Output objects for updating component values.
        
        Returns a list of Dash Output objects that can be used in callbacks to
        update the values of both the slider and input components.
        
        Returns:
            list: List containing [Output(slider_id, 'value'), Output(input_id, 'value')]
            
        Example:
            >>> @app.callback(
            ...     component.get_value_outputs(),
            ...     [Input('some-input', 'value')]
            ... )
            ... def update_components(new_value):
            ...     return [new_value, new_value]
        """
        return [
            Output(self.slider_id, 'value'),
            Output(self.input_id, 'value')
        ]
    
    def get_pattern_matching_value_inputs(self, property_name='ALL'):
        """
        Get pattern-matching Input objects for listening to multiple component instances.
        
        Returns Input objects using pattern-matching to listen to all components
        with the specified property name, useful for multi-component callbacks.
        
        Args:
            property_name: The property to match. Use 'ALL' for all properties,
                          or specify a specific property name.
                          
        Returns:
            list: List containing pattern-matching Input objects
            
        Example:
            >>> @app.callback(
            ...     Output('summary', 'children'),
            ...     component.get_pattern_matching_value_inputs('ALL')
            ... )
            ... def update_summary(slider_values, input_values):
            ...     return f"Total sliders: {len(slider_values)}"
        """
        pattern = {'type': 'parameter', 'subtype': 'slider', 'property': property_name}
        input_pattern = {'type': 'parameter', 'subtype': 'input', 'property': property_name}
        
        return [
            Input(pattern, 'value'),
            Input(input_pattern, 'value')
        ]
    
    def get_pattern_matching_value_outputs(self, property_name='ALL'):
        """
        Get pattern-matching Output objects for updating multiple component instances.
        
        Returns Output objects using pattern-matching to update all components
        with the specified property name.
        
        Args:
            property_name: The property to match. Use 'ALL' for all properties,
                          or specify a specific property name.
                          
        Returns:
            list: List containing pattern-matching Output objects
            
        Example:
            >>> @app.callback(
            ...     component.get_pattern_matching_value_outputs('ALL'),
            ...     [Input('reset-button', 'n_clicks')]
            ... )
            ... def reset_all_components(n_clicks):
            ...     if n_clicks:
            ...         return [[0] * len(slider_values), [0] * len(input_values)]
            ...     return [dash.no_update, dash.no_update]
        """
        pattern = {'type': 'parameter', 'subtype': 'slider', 'property': property_name}
        input_pattern = {'type': 'parameter', 'subtype': 'input', 'property': property_name}
        
        return [
            Output(pattern, 'value'),
            Output(input_pattern, 'value')
        ]
    
    def _validate_and_clamp_value(self, value):
        """
        Validate and clamp a value to the component's valid range.
        
        Ensures that any input value is within the min_val to max_val range
        and handles None values appropriately.
        
        Args:
            value: The value to validate and clamp.
            
        Returns:
            float: The clamped value within the valid range, or the current
                   default_val if the input value is invalid.
        """
        if value is None:
            return self.default_val if self.default_val is not None else self.min_val
        
        try:
            numeric_value = float(value)
            return max(self.min_val, min(self.max_val, numeric_value))
        except (ValueError, TypeError):
            return self.default_val if self.default_val is not None else self.min_val


class SliderWithTextInputAndCheckbox(SliderWithTextInput):
    """
    A custom Dash component that extends SliderWithTextInput by adding a checkbox with a message.
    
    This component inherits all functionality from SliderWithTextInput and adds a checkbox
    positioned beneath the input field. The checkbox can be used to enable/disable features,
    toggle options, or provide additional control over the parameter being adjusted.
    
    The checkbox includes an associated message that describes its purpose or provides
    additional context for the user. The checkbox is larger than standard size and has
    proper spacing between the checkbox and its label text.
    
    Attributes:
        checkbox_message (str): The message displayed next to the checkbox
        checkbox_default (bool): Default checked state of the checkbox
        checkbox_id (dict): Computed ID for the checkbox component
    
    Note:
        The checkbox value is [True] when checked, [] when unchecked.
    
    Example:
        >>> slider_component = SliderWithTextInputAndCheckbox(
        ...     id_base={'type': 'parameter', 'index': 0},
        ...     min_val=0.0,
        ...     max_val=100.0,
        ...     step=1.0,
        ...     mark_interval=10.0,
        ...     property_name='temperature',
        ...     title='Temperature (°C)',
        ...     default_val=25.0,
        ...     checkbox_message='Use automatic temperature control',
        ...     checkbox_default=True
        ... )
        >>> layout_element = slider_component()  # Returns Dash HTML Div component
    """

    def __init__(
        self,
        id_base: dict,
        min_val: float,
        max_val: float,
        step: float,
        mark_interval: float,
        property_name: str,
        title: str,
        checkbox_message: str,
        default_val: Union[float, list[float]] = None,
        checkbox_default: bool = False,
        with_slider_titles: bool = True,
        slider_disable: bool = False,
        div_width: str = 'calc(90%)',
        message: str = None,
    ):
        """
        Initialize the SliderWithTextInputAndCheckbox component.
        
        Args:
            id_base (dict): Base dictionary for generating component IDs.
            min_val (float): Minimum value for the slider and input.
            max_val (float): Maximum value for the slider and input.
            step (float): Step size for value increments/decrements.
            mark_interval (float): Interval between tick marks on the slider.
            property_name (str): String identifier for this property.
            title (str): Title displayed above the component.
            checkbox_message (str): Message displayed next to the checkbox.
            default_val (Union[float, list[float]], optional): Initial value for slider/input.
            checkbox_default (bool, optional): Initial checked state of checkbox. Defaults to False.
            with_slider_titles (bool, optional): Whether to show title. Defaults to True.
            slider_disable (bool, optional): Whether to disable interactions. Defaults to False.
            div_width (str, optional): CSS width for container. Defaults to 'calc(90%)'.
            message (str, optional): Optional message between title and slider.
        """
        # Initialize parent class
        super().__init__(
            id_base=id_base,
            min_val=min_val,
            max_val=max_val,
            step=step,
            mark_interval=mark_interval,
            property_name=property_name,
            title=title,
            default_val=default_val,
            with_slider_titles=with_slider_titles,
            slider_disable=slider_disable,
            div_width=div_width,
            message=message,
        )
        
        # Add checkbox-specific attributes
        self.checkbox_message = checkbox_message
        self.checkbox_default = checkbox_default
        self.checkbox_id = self._make_id('checkbox')

    def _make_checkbox(self):
        """
        Create and configure the Dash checkbox component.
        
        Returns:
            dash.html.Div: Container with a larger checkbox and separated label text.
        """
        return ds.html.Div([
            ds.dcc.Checklist(
                id=self.checkbox_id,
                options=[{'label': '', 'value': True}],
                value=[True] if self.checkbox_default else [],
                style={
                    'display': 'inline-block',
                    'margin-right': '10px',
                    'transform': 'scale(1.3)',  # Make checkbox larger
                    'transform-origin': 'left top',  # Changed to 'top' for better alignment
                    'vertical-align': 'baseline'  # Use baseline alignment
                },
                labelStyle={'margin': '0px'}
            ),
            ds.html.Span(
                self.checkbox_message,
                style={
                    'display': 'inline-block',
                    'vertical-align': 'baseline',  # Match checkbox baseline
                    'margin-left': '5px',
                    'line-height': '1.3',  # Slightly higher line height
                    'margin-top': '-4px'  # Pull text up more aggressively
                }
            )
        ], style={'margin-left': '20px', 'margin-top': '10px', 'line-height': '1'})

    def __call__(self):
        """
        Generate the complete component layout including the checkbox.
        
        Creates and returns a Dash HTML Div containing the title, optional message,
        slider, input, and checkbox components arranged in a cohesive layout.
        
        Returns:
            dash.html.Div: Complete component layout containing all elements plus checkbox.
        """
        slider_title = self.title if self.with_slider_titles else "\u00A0"
        
        # Build the component list
        components = [
            ds.html.P(slider_title, style={'margin-left': '20px', 'margin-bottom': '0px'})
        ]
        
        # Add optional message if provided
        if self.message:
            components.append(
                ds.html.P(self.message, style={
                    'margin-left': '20px', 
                    'margin-bottom': '5px',
                    'margin-top': '2px',
                    'font-size': '0.9em',
                    'color': '#666666',
                    'font-style': 'italic'
                })
            )
        
        # Add slider and input
        components.extend([
            ds.html.Div([self._make_slider()], style={'margin-bottom': '-18px'}),
            self._make_input(),
        ])
        
        # Add checkbox beneath the input
        components.extend([
            self._make_checkbox(),
            ds.html.Br(), ds.html.Br()
        ])

        return ds.html.Div(components, style={'width': self.div_width, 'margin-left': '-20px'})

    @property
    def components(self):
        """
        Get a dictionary mapping component types to their IDs, including the checkbox.
        
        Returns:
            dict: Dictionary with component type keys mapping to their ID dictionaries.
        """
        return {
            'slider': self.slider_id,
            'input': self.input_id,
            'checkbox': self.checkbox_id
        }
    
    def get_checkbox_input(self):
        """
        Get Input object for listening to checkbox value changes.
        
        Returns:
            Input: Dash Input object for the checkbox component.
            
        Note:
            The checkbox value will be [True] when checked, [] when unchecked.
            
        Example:
            >>> @app.callback(
            ...     Output('some-output', 'children'),
            ...     component.get_checkbox_input()
            ... )
            ... def update_display(checkbox_value):
            ...     is_checked = True in (checkbox_value or [])
            ...     return f"Checkbox is {'checked' if is_checked else 'unchecked'}"
        """
        return Input(self.checkbox_id, 'value')
    
    def get_checkbox_output(self):
        """
        Get Output object for updating checkbox value.
        
        Returns:
            Output: Dash Output object for the checkbox component.
            
        Note:
            To check the checkbox, return [True]. To uncheck, return [].
            
        Example:
            >>> @app.callback(
            ...     component.get_checkbox_output(),
            ...     [Input('some-button', 'n_clicks')]
            ... )
            ... def toggle_checkbox(n_clicks):
            ...     if n_clicks and n_clicks % 2 == 1:
            ...         return [True]
            ...     return []
        """
        return Output(self.checkbox_id, 'value')
    
    def get_all_inputs(self):
        """
        Get Input objects for all component values (slider, input, and checkbox).
        
        Returns:
            list: List containing Input objects for slider, input, and checkbox.
            
        Note:
            The checkbox value will be [True] when checked, [] when unchecked.
            
        Example:
            >>> @app.callback(
            ...     Output('summary', 'children'),
            ...     component.get_all_inputs()
            ... )
            ... def update_summary(slider_val, input_val, checkbox_val):
            ...     is_checked = True in (checkbox_val or [])
            ...     value = slider_val or input_val
            ...     return f"Value: {value}, Option enabled: {is_checked}"
        """
        return [
            Input(self.slider_id, 'value'),
            Input(self.input_id, 'value'),
            Input(self.checkbox_id, 'value')
        ]


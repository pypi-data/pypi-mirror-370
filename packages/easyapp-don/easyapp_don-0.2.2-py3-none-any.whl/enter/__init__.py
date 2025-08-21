"""
This module provides three interactive input interface functions based on KivyMD: ent(), esent(), and fillent(). These functions create customizable GUI windows for user input collection with support for text labels, input fields, buttons, and theme customization.

1. ent()
   - Description: Creates a simple single-input interface with a text label, one input field, OK button, and Cancel button.
   - Functionality: Collects a single text input from the user and returns the interaction result (OK/Cancel/close action) along with the input text.
   - Parameters:
     - t (list, optional): Configuration for the title text. Format: [text_content, (x_position, y_position)] where positions are normalized (0-1 relative to screen). Defaults to ["Hello,easyapp_don-lazydonkey!", (0.5, 0.7)].
     - tie (str, optional): Title of the application window. Defaults to "EntEasyapp_don".
     - color (tuple, optional): Background color in RGBA format (values 0-1). Defaults to WHITE12.
     - theme (str, optional): Application theme style, must be "LIGHT" or "DARK". Defaults to LIGHT.
     - tip (dict, optional): Configuration for the close confirmation dialog. Format: {"txt": dialog_content, "tie": dialog_title, "ok": [ok_button_text, ok_color], "cal": [cancel_button_text, cancel_color]}. Defaults to a basic close confirmation.
     - ok (list, optional): OK button configuration. Format: [text, color, (width_ratio, height_ratio), (x_position, y_position), is_close_bool]. The last parameter indicates if the app closes on click. Defaults to ["Ok", BLUE8, (0.15, 0.05), (0.1, 0.1), True].
     - cal (list, optional): Cancel button configuration. Format: [text, color, (width_ratio, height_ratio), (x_position, y_position), is_close_bool]. The last parameter indicates if the app closes on click. Defaults to ["Cancel", GREY4, (0.15, 0.05), (0.9, 0.1), True].
     - e (list, optional): Input field configuration. Format: [hint_text, (width_ratio, height_ratio), (x_position, y_position)]. Defaults to ["Enter something.", (0.96, 0.05), (0.5, 0.5)].
   - Return: A list [action, input_text] where action is True (OK clicked), False (Cancel clicked), or None (window closed directly when tip is disabled); input_text is the user's input string.

2. esent()
   - Description: Creates an interface with multiple text labels and multiple input fields, along with OK and Cancel buttons.
   - Functionality: Collects multiple text inputs from the user through multiple input fields and returns the interaction result along with all input texts.
   - Parameters:
     - ts (list, optional): List of text label configurations. Each element format: [text_content, (x_position, y_position)] with normalized positions. Defaults to sample text labels.
     - es (list, optional): List of input field configurations. Each element format: [hint_text, (width_ratio, height_ratio), (x_position, y_position)]. Defaults to 3 sample input fields.
     - ok (list, optional): OK button configuration (same format as ent()). Defaults to ["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True].
     - cal (list, optional): Cancel button configuration (same format as ent()). Defaults to ["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True].
     - tie (str, optional): Window title. Defaults to "EsEntEasyapp_don".
     - theme (str, optional): Theme style ("LIGHT" or "DARK"). Defaults to LIGHT.
     - color (tuple, optional): Background color in RGBA. Defaults to WHITE12.
     - tip (dict, optional): Close confirmation dialog configuration (same format as ent()). Defaults to a basic close confirmation.
   - Return: A list [action, input_texts] where action is True/False/None (same as ent()); input_texts is a list of user input strings from all fields.

3. fillent()
   - Description: Creates an enhanced interface with text labels, multiple input fields, and custom fill buttons that maintain selection states.
   - Functionality: Collects user inputs through text fields and tracks selections from interactive fill buttons, returning the interaction result, button selections, and input texts.
   - Parameters:
     - ts (list, optional): Text label configurations (same format as esent()). Defaults to sample text labels.
     - fs (list, optional): List of fill button configurations. Each element format: [button_text, default_color, selected_color, (width_ratio, height_ratio), (x_position, y_position)]. Defaults to 3 sample buttons.
     - es (list, optional): Input field configurations (same format as esent()). Defaults to 3 sample input fields.
     - color (tuple, optional): Background color in RGBA. Defaults to WHITE12.
     - theme (str, optional): Theme style ("LIGHT" or "DARK"). Defaults to LIGHT.
     - tip (dict, optional): Close confirmation dialog configuration (same format as ent()). Defaults to a basic close confirmation.
     - ok (list, optional): OK button configuration (same format as ent()). Defaults to ["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True].
     - cal (list, optional): Cancel button configuration (same format as ent()). Defaults to ["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1)].
     - tie (str, optional): Window title. Defaults to "FillEntEasyapp_don".
   - Return: A list [action, button_selections, input_texts] where action is True/False/None (same as ent()); button_selections contains data from selected fill buttons; input_texts is a list of user input strings.

Note: To modify colors and themes, import color constants and theme utilities from 'easyapp_don.tools.colors' (e.g., WHITE12, BLUE8, LIGHT, DARK).
"""
__version__="0.2.2"
__author__="LvYanHua"
__all__=['Ent',
         'EsEnt',
         'FillEnt']
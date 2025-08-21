"""
easyapp_don.button - Interactive UI Components Library

This package provides a collection of interactive button components for building user interfaces,
including basic buttons, enhanced stateful buttons, and fillable/toggle buttons with various customization options.

All components support custom positioning, sizing, colors, and themes, and are built on KivyMD for cross-platform compatibility.
Colors and themes should be imported from `easyapp_don.tools.colors` (e.g., LIGHT, DARK, RED8, GREEN7).


1. Btn Component (Basic Interactive Button)
-------------------------------------------
A simple clickable button component for creating dialogs with customizable text, buttons, and styling.
Returns the index of the clicked button or None when closed.

Function: btn(t=None, tie="BtnEasyapp_don", theme=LIGHT, color=WHITE12, bs=None, tip=None) -> Optional[int]

Parameters:
- t: Configuration for the main display text.
  Format: ["text_content", (center_x, center_y)]
  - "text_content": String text to display (default: "Hello,easyapp_don!")
  - (center_x, center_y): Position coordinates (0-1 range, where (0.5, 0.5) is center; default: (0.5, 0.5))
  Type: list | None

- tie: Title of the window displayed in the title bar.
  Default: "BtnEasyapp_don"
  Type: str

- theme: Visual theme (light or dark mode). Must be LIGHT or DARK from `easyapp_don.tools.colors`.
  Default: LIGHT
  Type: str

- color: Background color of the main layout. Use colors from `easyapp_don.tools.colors`.
  Default: WHITE12
  Type: tuple

- bs: List of button configurations. Each button is defined as:
  ["button_text", button_color, (size_hint_x, size_hint_y), (center_x, center_y), close_on_click]
  - "button_text": String displayed on the button
  - button_color: Background color (from `easyapp_don.tools.colors`)
  - (size_hint_x, size_hint_y): Button dimensions relative to screen (0-1 range)
  - (center_x, center_y): Button position coordinates (0-1 range)
  - close_on_click: Boolean indicating if the window closes when clicked
  Default: Predefined 3-button set
  Type: list | None

- tip: Configuration for the close confirmation dialog (shown when window is closed).
  Format: {
    "txt": "Confirmation message text",
    "tie": "Dialog title",
    "ok": ["OK button text", button_color],
    "cal": ["Cancel button text", button_color]
  }
  Set to {} to disable confirmation.
  Default: Predefined close prompt
  Type: dict | None

Return Value:
- Integer index of the clicked button (0-based, according to `bs` order)
- None if the window is closed via the close button (after confirmation)
- None for buttons where `close_on_click` is False


2. EsBtn Component (Enhanced Stateful Button)
---------------------------------------------
An upgraded button component supporting multiple text elements and flexible button configurations.
Ideal for multistep interfaces or dialogs requiring multiple text prompts.

Function: esbtn(ts=None, tie="EsBtnEasyapp_don", color=WHITE12, theme=LIGHT, tip=None, bs=None) -> Optional[int]

Parameters:
- ts: List of text elements to display. Each element follows:
  ["text_content", (center_x, center_y)]
  - "text_content": String text to display
  - (center_x, center_y): Position coordinates (0-1 range)
  Default: Predefined 5-text set
  Type: list | None

- tie: Title of the window.
  Default: "EsBtnEasyapp_don"
  Type: str

- color: Background color of the main layout (from `easyapp_don.tools.colors`).
  Default: WHITE12
  Type: tuple

- theme: Visual theme (LIGHT or DARK from `easyapp_don.tools.colors`).
  Default: LIGHT
  Type: str

- tip: Close confirmation dialog configuration (same format as `btn()`'s `tip`).
  Default: Predefined close prompt
  Type: dict | None

- bs: List of button configurations (same format as `btn()`'s `bs`).
  Default: Predefined 3-button set
  Type: list | None

Return Value:
- Integer index of the clicked button (0-based)
- None if closed via window close button (after confirmation)


3. FillBtn Component (Fillable/Toggle Button)
---------------------------------------------
A specialized component with toggleable "fillable" buttons that maintain state, perfect for forms, surveys,
or any interface requiring selection tracking. Returns both the clicked button index and fillable states.

Function: fillbtn(ts=None, tie="FillBtnEasyapp_don", theme=LIGHT, color=WHITE12, tip=None, bs=None, fs=None) -> list

Parameters:
- ts: List of text elements (same format as `esbtn()`'s `ts`).
  Default: Predefined 5-text set
  Type: list | None

- tie: Title of the window.
  Default: "FillBtnEasyapp_don"
  Type: str

- theme: Visual theme (LIGHT or DARK from `easyapp_don.tools.colors`).
  Default: LIGHT
  Type: str

- color: Background color of the main layout (from `easyapp_don.tools.colors`).
  Default: WHITE12
  Type: tuple

- tip: Close confirmation dialog configuration (same format as `btn()`'s `tip`).
  Default: Predefined close prompt
  Type: dict | None

- bs: List of standard button configurations (same format as `btn()`'s `bs`).
  Default: Predefined 3-button set
  Type: list | None

- fs: List of fillable/toggle button configurations. Each is defined as:
  ["default_text", base_color, text_color, (size_hint_x, size_hint_y), (center_x, center_y)]
  - "default_text": Initial text displayed on the fillable button
  - base_color: Background color when not selected
  - text_color: Text color (or highlight color when selected)
  - (size_hint_x, size_hint_y): Dimensions relative to screen (0-1 range)
  - (center_x, center_y): Position coordinates (0-1 range)
  Default: Predefined 3-fillable-button set
  Type: list | None

Return Value:
- List with two elements:
  [clicked_button_index, [filled_button_indices]]
  - clicked_button_index: Index of the clicked standard button (from `bs`)
  - [filled_button_indices]: List of indices (0-based) of fillable buttons that were toggled/selected


Author: easyapp_don Development Team

License:
    This component is available for commercial use.
    Special offer: For free.

Privacy Policy:
    This component does not collect, store, or transmit any user privacy data.
    All interactions are processed locally within the application.
"""
__version__="0.2.2"
__author__="LvYanHua"
__all__=['Btn',
         'EsBtn',
         'FillBtn']
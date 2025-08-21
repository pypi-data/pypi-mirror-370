"""
```python
The `supermarket` module provides a set of user-friendly functions for quickly building interactive single-page and multi-page applications with rich UI elements, including text, images, buttons, input fields, and custom interactive components. It is built on top of KivyMD, offering a simplified interface for developers to create desktop and mobile applications without deep knowledge of GUI frameworks.

## Core Functions

### 1. `page()`
#### Purpose
Creates a single-page interactive application with customizable UI elements such as text, images, buttons, input fields, and interactive components (e.g., fillable buttons, image toggle buttons).

#### Functionality
- Generates a single window with a floating layout.
- Supports adding text labels, images, background images, buttons, input fields, fillable buttons (toggling color on click), and image toggle buttons (switching images on click).
- Handles user interactions (clicks, input) and returns results when the application is closed.
- Allows customization of theme (light/dark), background color, window title, and closing confirmation dialog.

#### Usage
```python
from easyapp_don.supermarket.one_pagebook import page

# Basic usage with default elements
result = page()

# Customized usage
result = page(
    ts=[["Welcome to My App", (0.5, 0.9)], ["User Input:", (0.2, 0.6)]],
    i=[["images/logo.png", (0.3, 0.3), (0.5, 0.7), 0.8]],
    es=[["Enter your name", (0.4, 0.05), (0.5, 0.5)]],
    bs=[["Submit", GREEN8, (0.2, 0.05), (0.5, 0.3)]],
    theme=DARK,
    tie="My Single-Page App"
)
```

#### Parameters
- `ts` (list, optional): List of text elements. Each element is a sublist `[text_content, (x_pos, y_pos)]`, where:
  - `text_content` (str): The text to display.
  - `(x_pos, y_pos)` (tuple of floats): Position in relative coordinates (0-1 for x and y axes, with (0.5, 0.5) as center).
  - Default: `[["Hello,easyapp_don!", (0.5, 0.95)], ["Text1", (0.1, 0.6)], ...]`
  - Example: `ts=[["Title", (0.5, 0.9)], ["Description", (0.5, 0.8)]]`

- `i` (list, optional): List of image elements. Each element is a sublist `[image_path, (width_ratio, height_ratio), (x_pos, y_pos), opacity]`, where:
  - `image_path` (str): Path to the image file.
  - `(width_ratio, height_ratio)` (tuple of floats): Size relative to the window (0-1).
  - `(x_pos, y_pos)` (tuple of floats): Position in relative coordinates.
  - `opacity` (float): Transparency (0-1, 1 = fully opaque).
  - Default: `[["images/easyapp_don.png", (1, 1), (0.5, 0.5), 0.6]]`
  - Example: `i=[["images/icon.png", (0.2, 0.2), (0.8, 0.9), 0.9]]`

- `bi` (list, optional): List of background image elements (similar to `i` but with a close interaction flag). Each element is `[image_path, (width_ratio, height_ratio), (x_pos, y_pos), opacity, is_close_button]`, where:
  - `is_close_button` (bool): If `True`, clicking the image triggers the app close dialog.
  - Default: `[["images/sky.png", (0.15, 0.1), (0.15, 0.3), 0.9, True], ...]`
  - Example: `bi=[["images/bg.png", (1, 1), (0.5, 0.5), 0.3, False]]`

- `es` (list, optional): List of input fields. Each element is `[hint_text, (width_ratio, height_ratio), (x_pos, y_pos)]`, where:
  - `hint_text` (str): Placeholder text for the input field.
  - Default: `[["Enter1", (0.2, 0.05), (0.15, 0.5)], ...]`
  - Example: `es=[["Email", (0.3, 0.05), (0.5, 0.4)]]`

- `bs` (list, optional): List of raised buttons. Each element is `[button_text, background_color, (width_ratio, height_ratio), (x_pos, y_pos)]`, where:
  - `background_color` (tuple): RGB/RGBA color tuple (e.g., `GREEN8` from `easyapp_don.tools.colors`).
  - Default: `[["Button0", RED8, (0.1, 0.05), (0.1, 0.05)], ...]`
  - Example: `bs=[["Save", BLUE8, (0.15, 0.05), (0.5, 0.2)]]`

- `fs` (list, optional): List of fillable buttons (toggle color on click). Each element is `[button_text, default_color, active_color, (width_ratio, height_ratio), (x_pos, y_pos)]`, where:
  - `default_color`/`active_color` (tuple): Colors for unclicked/clicked states.
  - Default: `[["a(0)", GREY4, RED1, (0.05, 0.05), (0.1, 0.8)], ...]`
  - Example: `fs=[["Agree", GREY4, GREEN8, (0.2, 0.05), (0.5, 0.6)]]`

- `fi` (list, optional): List of image toggle buttons (switch images on click). Each element is `[default_image_path, active_image_path, (width_ratio, height_ratio), (x_pos, y_pos)]`, where:
  - Images switch when clicked.
  - Default: `[["images/dinos.png", "images/gold.png", (0.05, 0.05), (0.1, 0.7)], ...]`
  - Example: `fi=[["images/off.png", "images/on.png", (0.1, 0.1), (0.8, 0.2)]]`

- `theme` (str, optional): App theme, either `LIGHT` or `DARK` (from `easyapp_don.tools.colors`). Default: `LIGHT`.

- `color` (tuple, optional): Background color of the page (RGB/RGBA tuple). Default: `WHITE12`.

- `tie` (str, optional): Window title. Default: `"OnePageEasyapp"`.

- `tip` (dict, optional): Configuration for the close confirmation dialog. Structure:
  - `"txt"` (str): Dialog message.
  - `"tie"` (str): Dialog title.
  - `"ok"` (list): `[button_text, button_color]` for confirmation.
  - `"cal"` (list): `[button_text, button_color]` for cancellation.
  - Default: `{"txt": "Close app?", "tie": "Tip", "ok": ["Yes", GREY4], "cal": ["No", BLUE8]}`


### 2. `pages()`
#### Purpose
Creates a multi-page application with navigation between pages (next/previous) and persistent state management across pages.

#### Functionality
- Manages a sequence of pages, each with its own UI elements (text, images, buttons, etc.).
- Supports navigation between pages via "Next" and "Previous" buttons.
- Preserves user input and interactions across page transitions.
- Returns aggregated results from all pages when the application is closed.

#### Usage
```python
from easyapp_don.supermarket.pagebooks import pages

# Define page configurations
page_configs = {
    "Page1": {
        "tie": "Introduction",
        "ts": [["Welcome to Multi-Page App", (0.5, 0.9)], ["Page 1/2", (0.5, 0.05)]],
        "bs": [["Next", BLUE8, (0.15, 0.05), (0.8, 0.1)]]
    },
    "Page2": {
        "tie": "User Info",
        "ts": [["Enter your details", (0.5, 0.9)], ["Page 2/2", (0.5, 0.05)]],
        "es": [["Name", (0.3, 0.05), (0.5, 0.5)]],
        "bs": [["Submit", GREEN8, (0.15, 0.05), (0.5, 0.3)]],
        "last": {"txt": "Previous", "color": GREY8, "size": (0.15, 0.05), "pos": (0.2, 0.1)}
    }
}

# Run multi-page app
results = pages(page_configs)
```

#### Parameters
- `page_configs` (dict, optional): A dictionary where keys are page names (e.g., "Page1") and values are page configurations. Each page configuration includes:
  - All parameters from `page()` (e.g., `ts`, `i`, `bs`, `theme`, etc.).
  - `last` (dict, optional): Configuration for the "Previous" button: `{"txt": str, "color": tuple, "size": tuple, "pos": tuple}`.
  - `next` (dict, optional): Configuration for the "Next" button (same structure as `last`).
  - Default: A pre-defined 3-page demo.

- Return: A dictionary with results from each page, including user inputs, button states, and interactions.


### 3. `img_pages()`
#### Purpose
Extends `pages()` with enhanced support for image-heavy multi-page applications, optimized for displaying and interacting with images (e.g., galleries, image-based quizzes).

#### Functionality
- Inherits all features of `pages()`.
- Adds specialized handling for high-resolution images, including lazy loading and aspect ratio preservation.
- Supports image-specific interactions (e.g., zoom, click-to-select images).
- Optimizes performance for applications with multiple large images.

#### Usage
```python
from easyapp_don.supermarket.imgbooks import img_pages

# Image-heavy page configs
image_page_configs = {
    "Gallery1": {
        "tie": "Nature Gallery",
        "i": [
            ["images/mountains.jpg", (0.4, 0.4), (0.3, 0.6), 1.0],
            ["images/ocean.jpg", (0.4, 0.4), (0.7, 0.6), 1.0]
        ],
        "bs": [["Next Gallery", BLUE8, (0.15, 0.05), (0.8, 0.1)]]
    },
    "Gallery2": {
        "tie": "City Gallery",
        "i": [
            ["images/skyscraper.jpg", (0.4, 0.4), (0.3, 0.6), 1.0],
            ["images/bridge.jpg", (0.4, 0.4), (0.7, 0.6), 1.0]
        ],
        "last": {"txt": "Previous", "color": GREY8, "size": (0.15, 0.05), "pos": (0.2, 0.1)}
    }
}

# Run image-focused multi-page app
image_results = img_pages(image_page_configs)
```

#### Parameters
- Inherits all parameters from `pages()`, with additional image-specific optimizations:
  - `i` and `bi` parameters are optimized for large images, with automatic downscaling if needed.
  - `fi` (image toggle buttons) support higher resolution swaps without performance loss.


## Privacy Policy
This module does not collect, store, or transmit any user personal information. All user inputs and interactions are processed locally within the application and are not shared with third parties. Users are responsible for ensuring compliance with relevant privacy regulations when handling sensitive data in their applications built using this module.


## License
This module is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, provided that the original copyright notice and this permission notice are included in all copies or substantial portions of the software. The software is provided "as is" without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.


## How to Use
1. **Installation**: Ensure `easyapp_don` is installed, including dependencies like KivyMD.
2. **Import Functions**: Use `from easyapp_don.supermarket.one_pagebook import page`, `from easyapp_don.supermarket.pagebooks import pages`, or `from easyapp_don.supermarket.imgbooks import img_pages` based on your needs.
3. **Configure UI Elements**: Define text, images, buttons, etc., using the parameter structures outlined above.
4. **Run the App**: Call the function with your configuration. The function returns a dictionary of user interactions when the app is closed.
5. **Process Results**: Use the returned results to handle user inputs, button clicks, and other interactions in your logic.
"""
__version__="0.2.1"
__author__="LvYanHua"
__all__=['imgbooks',
         'pagebooks',
         'one_pagebook',
         'tools']
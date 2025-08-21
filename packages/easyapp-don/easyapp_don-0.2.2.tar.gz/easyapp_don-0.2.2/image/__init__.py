"""
```
This module provides a set of functions for creating graphical interfaces with images, text, and interactive buttons using KivyMD. The core functions include img(), fill_img(), btn_img(), and fill_btn_img(), each offering different combinations of interactive elements.


## Core Functions

### 1. img()
- **Purpose**: Create a basic interface with images, text labels, and OK/Cancel buttons. Suitable for simple image display with basic user interactions.
- **Example**:
  ```python
  from easyapp_don.image import img
  # Basic usage
  result = img()
  # Customized usage
  result = img(
      i=[["images/sky.png", (1, 1), (0.5, 0.5), 0.8]],  # Display sky image
      ts=[["Welcome", (0.5, 0.9)]],  # Text at top center
      ok=["Confirm", "BLUE8", (0.2, 0.05), (0.3, 0.1), True],
      theme="DARK"
  )
  ```
- **Parameters**:
  - `ts`: List of text elements. Format: `[["text_content", (center_x, center_y)], ...]`
    Example: `[["Title", (0.5, 0.9)]]` (text at top center)
  - `ok`/`cal`: OK/Cancel button config. Format: `[text, color, (size_hint_x, size_hint_y), (center_x, center_y), close_on_click]`
    Example: `["OK", "GREEN6", (0.2, 0.05), (0.5, 0.1), True]`
  - `theme`: Interface theme ("LIGHT" or "DARK")
  - `color`: Background color (e.g., "WHITE12", "PINK10")
  - `tie`: Window title (default: "ImgEasyapp_don")
  - `tip`: Close confirmation dialog config. Format: `{"txt": message, "tie": title, "ok": [text, color], "cal": [text, color]}`. Use `{}` to disable.
  - `i`: Image config. Format: `[["image_path", (size_hint_x, size_hint_y), (center_x, center_y), opacity], ...]`
    Example: `[["images/logo.png", (0.3, 0.3), (0.5, 0.5), 1.0]]`


### 2. fill_img()
- **Purpose**: Extends img() with "fill buttons" that change color when clicked. Useful for selection/toggle scenarios.
- **Example**:
  ```python
  from easyapp_don.image import fill_img
  result = fill_img(
      fs=[["Option 1", "GREY4", "RED8", (0.2, 0.05), (0.5, 0.5)]],  # Button: grey → red when clicked
      ts=[["Select an option", (0.5, 0.9)]],
      theme="LIGHT"
  )
  ```
- **Parameters**:
  - `fs`: Fill button config. Format: `[["text", default_color, fill_color, (size_hint_x, size_hint_y), (center_x, center_y)], ...]`
    Example: `[["Click me", "GREY4", "BLUE8", (0.2, 0.05), (0.5, 0.5)]]`
  - Other parameters (`ts`, `ok`, `cal`, etc.) are the same as in img().


### 3. btn_img()
- **Purpose**: Extends img() with "image buttons" (clickable images). Ideal for interactions using visual elements.
- **Example**:
  ```python
  from easyapp_don.image import btn_img
  result = btn_img(
      bi=[["images/btn_icon.png", (0.15, 0.1), (0.5, 0.5), 0.9]],  # Image button
      i=[["images/bg.png", (1, 1), (0.5, 0.5), 0.6]],  # Background image
      tie="Image Button Demo"
  )
  ```
- **Parameters**:
  - `bi`: Image button config. Format: `[["image_path", (size_hint_x, size_hint_y), (center_x, center_y), opacity], ...]`
    Returns the index of the clicked image button (e.g., 0, 1).
  - Other parameters (`ts`, `ok`, `cal`, etc.) are the same as in img().


### 4. fill_btn_img()
- **Purpose**: Combines features of fill_img() (fill buttons) and btn_img() (image buttons), plus "toggle image buttons" (switch between two images when clicked).
- **Example**:
  ```python
  from easyapp_don.image import fill_btn_img
  result = fill_btn_img(
      fi=[["images/off.png", "images/on.png", (0.1, 0.1), (0.5, 0.6)]],  # Toggle image: off → on
      fs=[["Select", "GREY4", "GREEN6", (0.2, 0.05), (0.5, 0.4)]],  # Fill button
      bi=[["images/action.png", (0.15, 0.1), (0.5, 0.2), 1.0]],  # Image button
      theme="DARK"
  )
  ```
- **Parameters**:
  - `fi`: Toggle image button config. Format: `[["default_image", toggle_image, (size_hint_x, size_hint_y), (center_x, center_y)], ...]`
  - Other parameters (`ts`, `ok`, `cal`, `i`, `fs`, `bi`) are the same as in previous functions.


## General Notes

1. **Colors and Themes**:
   - Color parameters (e.g., "BLUE8", "GREY4") are imported from `easyapp_don.tools.colors`.
   - Theme parameters ("LIGHT"/"DARK") are imported from `easyapp_don.tools.Manner`.

2. **Size and Position**:
   - `size_hint` (e.g., `(0.2, 0.05)`): Defines element size as a proportion of the parent container (range: 0-1). 0.2 means 20% of the parent's width.
   - `pos_hint` (e.g., `(0.5, 0.5)`): Defines element position relative to the parent container (range: 0-1). (0.5, 0.5) centers the element.

3. **Image Files**:
   Copy the `images` folder (containing image assets) to the same directory as your code file. This prevents errors due to missing image files.
```
"""
__version__="0.2.2"
__author__="LvYanHua"
__all__=['Img',
         'FillImg',
         'ButtonImg',
         'FillButtonImg']
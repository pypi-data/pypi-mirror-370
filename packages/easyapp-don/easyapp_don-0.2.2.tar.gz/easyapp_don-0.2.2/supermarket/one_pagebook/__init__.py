"""
        Creates a customizable single-page interactive application using KivyMD, with configurable UI elements,
        and returns structured data about user interactions (clicks, inputs, and toggle states).

        This function abstracts the complexity of building a KivyMD app by allowing you to define UI components
        through simple parameter configurations. It runs the app, waits for user interaction (button clicks or app closure),
        then returns a detailed list of interaction results.

        KeyNotes:
        - The `theme` parameter values (`LIGHT`/`DARK`) can be imported from `easyapp_don.tools.colors`.
        - All color parameters (e.g., button colors, background color) should be imported from `easyapp_don.tools.colors`
          (no need to define custom RGBA tuples). Color variable names end with a number indicating shade depth
          (e.g., `RED1` = light red, `RED8` = dark red; `GREY4` = medium grey).

        :param ts: Configuration for text labels. Each element is a sublist with format:
            `["text_content", (center_x, center_y)]`
            - `text_content`: String text to display
            - `(center_x, center_y)`: Position on the page (0-1 range, (0.5, 0.5) is center)
            Example:
            ```python
            ts = [
                ["Welcome to My App", (0.5, 0.95)],  # Title at top-center
                ["Enter details below", (0.5, 0.85)]  # Subtitle below title
            ]
            ```
            Defaults to predefined text elements if None.

        :param tip: Configuration for the confirmation dialog when closing the app. Dictionary with keys:
            - `"txt"`: Dialog message (string)
            - `"tie"`: Dialog title (string)
            - `"ok"`: Sublist for confirm button: `["button_text", button_color]`
            - `"cal"`: Sublist for cancel button: `["button_text", button_color]`
            Example:
            ```python
            tip = {
                "txt": "Are you sure you want to exit?",
                "tie": "Exit Confirmation",
                "ok": ["Yes, Exit", RED6],
                "cal": ["Cancel", GREY4]
            }
            ```
            Defaults to a close confirmation dialog if None.

        :param color: Page background color. Should be a color variable from `easyapp_don.tools.colors`
            Example: `color = GREY2` (light grey background)
            Defaults to WHITE12.

        :param theme: App theme style (light or dark mode). Import `LIGHT` or `DARK` from `easyapp_don.tools.colors`
            Example:
            ```python
            from easyapp_don.tools.colors import DARK
            theme = DARK  # Uses dark mode theme
            ```
            Defaults to LIGHT.

        :param tie: Title of the application window (string)
            Example: `tie = "My Shopping List App"`
            Defaults to "OnePageEasyapp_don".

        :param i: Configuration for static (non-interactive) images. Each element is a sublist with format:
            `["image_path", (size_hint_x, size_hint_y), (center_x, center_y), opacity]`
            - `image_path`: Path to image file (e.g., `"images/logo.png"`)
            - `(size_hint_x, size_hint_y)`: Image size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            - `opacity`: Transparency (0 = fully transparent, 1 = fully opaque)
            Example:
            ```python
            i = [
                ["images/logo.png", (0.3, 0.2), (0.5, 0.7), 0.9],  # Semi-transparent logo
            ]
            ```
            Defaults to a predefined image if None.

        :param bi: Configuration for image-based buttons. These buttons have indices starting after the last index of `bs` buttons.
            Each element is a sublist with format:
            `["image_path", (size_hint_x, size_hint_y), (center_x, center_y), opacity, is_close_button]`
            - `image_path`: Path to button's image (e.g., `"images/settings.png"`)
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            - `opacity`: Image transparency (0-1 range)
            - `is_close_button`: Boolean indicating if clicking triggers app closure
            Example:
            ```python
            bi = [
                ["images/home_btn.png", (0.1, 0.1), (0.2, 0.3), 1.0, True],
            ]
            ```
            Defaults to predefined image buttons if None.

        :param fi: Configuration for image toggle buttons (toggle between two images). Each element is a sublist with format:
            `["image1_path", "image2_path", (size_hint_x, size_hint_y), (center_x, center_y)]`
            - `image1_path`: Default image path (e.g., `"images/unchecked.png"`)
            - `image2_path`: Toggled image path (e.g., `"images/checked.png"`)
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            Example:
            ```python
            fi = [
                ["images/off.png", "images/on.png", (0.08, 0.08), (0.3, 0.6)],
            ]
            ```
            Defaults to predefined image fill buttons if None.

        :param es: Configuration for text input fields. Each element is a sublist with format:
            `["hint_text", (size_hint_x, size_hint_y), (center_x, center_y)]`
            - `hint_text`: Gray placeholder text (e.g., "Enter your name")
            - `(size_hint_x, size_hint_y)`: Input field size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            Example:
            ```python
            es = [
                ["Username", (0.3, 0.05), (0.5, 0.6)],
                ["Age", (0.15, 0.05), (0.5, 0.5)]
            ]
            ```
            Defaults to predefined input fields if None.

        :param bs: Configuration for standard raised buttons. These buttons have indices starting from 0.
            Each element is a sublist with format:
            `["button_text", button_color, (size_hint_x, size_hint_y), (center_x, center_y)]`
            - `button_text`: String displayed on the button (e.g., "Submit")
            - `button_color`: Color from `easyapp_don.tools.colors` (e.g., `GREEN4`)
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            Example:
            ```python
            bs = [
                ["Submit", GREEN4, (0.2, 0.07), (0.3, 0.1)],  # Index 0
                ["Cancel", RED6, (0.2, 0.07), (0.7, 0.1)]     # Index 1
            ]
            ```
            Defaults to predefined buttons if None.

        :param fs: Configuration for color fill toggle buttons (toggle background color). Each element is a sublist with format:
            `["button_text", default_color, fill_color, (size_hint_x, size_hint_y), (center_x, center_y)]`
            - `button_text`: String displayed on the button (e.g., "Option A")
            - `default_color`: Initial background color (from `easyapp_don.tools.colors`)
            - `fill_color`: Toggled background color (from `easyapp_don.tools.colors`)
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            Example:
            ```python
            fs = [
                ["Red Team", GREY4, RED3, (0.15, 0.07), (0.25, 0.4)],
            ]
            ```
            Defaults to predefined fill buttons if None.

        :return: A list containing interaction results with structure:
            `[clicked_index, input_values, fs_states, fi_states]`
            - `clicked_index`: Index of clicked button (int) or None (app closed without clicking)
              - For `bs` buttons: Indices start at 0
              - For `bi` buttons: Indices start after last `bs` index
            - `input_values`: List of text values from `es` input fields
            - `fs_indexes`: List of states from `fs` toggle buttons
            - `fi_indexes`: List of states from `fi` image toggle buttons
    """
__version__="0.2.2"
__author__="LvYanHua"
__all__=['OnePagebook']
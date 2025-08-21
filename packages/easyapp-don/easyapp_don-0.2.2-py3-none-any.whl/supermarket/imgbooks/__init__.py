"""
        Create and run a multipage application with image support, enabling page navigation (previous, next, home),
        user interactions like button clicks, text input, and handling of various UI elements (labels, images, special buttons).
        It is built on top of KivyMD for the UI and provides a simplified way to set up a multipage structure
        compared to directly using lower - level Kivy/KivyMD APIs.

        :param ps: A dictionary that configures multiple aspects of the multipage application.
                   Each key in the dictionary represents a page name (not displayed as the title directly),
                   and the corresponding value is another dictionary with detailed page - specific settings.
                   These settings can include:
                   - "tie": The title of the page, which will be shown in the app's title bar.
                   - "ts": A list for text elements, where each element can be a simple text string (will be centered by default)
                           or a list with text and a (x, y) position tuple (ranging from 0 to 1, relative to the parent container).
                   - "fs": A list for fill buttons, each element can be a simplified form (just text, with other properties like color, size filled with defaults)
                           or a detailed list specifying text, initial color, clicked color, size (as a tuple), and position (as a tuple).
                   - "es": A list for text fields, each element can be a simple hint text (with default size and position)
                           or a detailed list with hint text, size (tuple), and position (tuple).
                   - "bs": A list for action buttons, each element can be a basic setup (text and color, with default size and position)
                           or a detailed list with text, color, size (tuple), and position (tuple). Clicking these buttons can trigger app termination with recorded results.
                   - "i": A list for images, each element can be a simple image path (with default size, position, and opacity)
                           or a detailed list with path, size (tuple), position (tuple), and opacity (float).
                   - "bi": A list for button - linked images, similar to regular images but can be associated with button - like press actions.
                   - "fi": A list for fill - image buttons, combining image display with fill - button - like interaction logic.
                   - "last": Configuration for the "previous page" navigation button, including text, color, size (tuple), and position (tuple).
                             This button is only visible if not on the first page.
                   - "next": Configuration for the "next page" navigation button, including text, color, size (tuple), and position (tuple).
                             This button is only visible if not on the last page.
                   - "back": Configuration for the "home page" navigation button, including text, color, size (tuple), and position (tuple).
                             This button is only visible if not on the first page.
                   - "theme": Specifies the app's theme style, typically using constants like "LIGHT" or "DARK" imported from relevant color/theme modules.
                   - "color": Sets the background color of the page, using color constants (imported from relevant modules) with an optional number suffix to indicate shade.
                   - "tip": A dictionary for the dialog shown when closing the app, which can have:
                           - "txt": The main text content of the dialog.
                           - "tie": The title of the dialog.
                           - "ok": A list for the "OK" button, which can be a simple text (with default color) or a list with text and color.
                           - "cal": A list for the "Cancel" button, similar to the "OK" button. If not needed, can be an empty list.
                   If not provided, it will use a default configuration copied from `i_mode` (assumed to be a predefined template).
        :return: A dictionary that records the interaction results of each page. The structure is:
                 {
                     "page_name": [
                         clicked_button_index_or_none,
                         list_of_input_texts_from_text fields,
                         list_of_fill_button_interactions,
                         list_of_fill_image_button_interactions
                     ]
                 }
                 Here, "page_name" is the key from the input `ps` dictionary, and each value list captures the relevant user interactions on that page.
                 This allows retrieval of what actions the user performed (which button was clicked, what was entered in text fields, etc.) after the app finishes running.
    """
__version__="0.2.2"
__author__="LvYanHua"
__all__=['Imgbook']
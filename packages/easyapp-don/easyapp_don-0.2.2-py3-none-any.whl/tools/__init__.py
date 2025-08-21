"""
This module provides various utility functions and components for the easyapp_don library, including color definitions, style management, type checking, dialog boxes, and custom buttons.

Key functionalities:
1. Color and Style Management:
   - The `WC` class enables printing text with different colors (e.g., red, green, blue) and styles (e.g., bold, underline, italic) in the console.
   - A large number of color tuples (e.g., RED1-RED18, BLUE1-BLUE18, PINK1-PINK18) are defined, where the number suffix indicates the depth of the color (larger numbers mean darker colors). These colors are suitable for setting background colors, text colors, etc., in KivyMD UI elements.
   - Two theme styles are provided: `LIGHT` and `DARK`.

2. Utility Functions:
   - Type checking and parameter filling functions (e.g., `check_type`, `fill_bs`, `fill_es`, `fill_ts`, `fill_fs`) to ensure parameter validity and completeness.
   - A `dialog` function (from `EasyDialog`) for popping up prompt dialog boxes.
   - Custom button components such as `FillButton`, `ImgButton`, and `ImgFillBtn` for specific interaction needs.

Privacy Policy:
This module does not collect, store, or transmit any user personal information. Users are responsible for ensuring compliance with relevant privacy regulations when using this module.

License:
This module is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions specified in the MIT License. The software is provided 'as is' without warranty of any kind.
"""
__version__="0.2.2"
__author__="LvYanHua"
__all__=['colors',
         'EasyDialog',
         'Manner',
         'FillButton',
         'SpecialButtons']
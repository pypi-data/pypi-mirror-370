"""
easyapp_don.message Module

This module provides a set of customizable message dialog functions built with KivyMD,
designed to create interactive message boxes, multi-text displays, and forms with fillable buttons.

Available Functions:
-------------------
1. msg()
   A simple message dialog with a single text element and configurable OK/Cancel buttons.
   Returns True (OK clicked), False (Cancel clicked), or None (window closed via system controls).

   Key Parameters:
   - t: List in format ["message_text", (center_x, center_y)] for main text content and position (0-1 range)
   - tie: Window title (string)
   - color: Background color (from easyapp_don.tools.colors)
   - theme: Visual theme (LIGHT/DARK from easyapp_don.tools.colors)
   - ok: OK button config: ["text", color, (size_hint), (position), is_close]
   - cal: Cancel button config: ["text", color, (size_hint), (position), is_close]
   - tip: Close confirmation dialog config: {"tie": title, "txt": message, "ok": [btn config], "cal": [btn config]}

2. esmsg()
   Extended message dialog supporting multiple text elements. Inherits all features of msg().

   Key Parameters:
   - ts: List of text configurations: [["text1", (x1, y1)], ["text2", (x2, y2)], ...]
   - (Other parameters same as msg())

3. fillmsg()
   Advanced dialog with fillable buttons (checkbox-like functionality), ideal for forms or answer sheets.
   Returns [action_result, fill_values] where action_result is True/False/None, and fill_values contain button states.

   Key Parameters:
   - ts: Multiple text elements (same format as esmsg())
   - fs: Fillable button configs: [["label", bg_color, text_color, (size_hint), (position)], ...]
   - (Other parameters same as msg())

Import Instructions:
-------------------
- Import functions: from easyapp_don.message import msg, esmsg, fillmsg
- Import color/theme constants: from easyapp_don.tools.colors import LIGHT, DARK, [color names like WHITE12, BLUE13, etc.]

Privacy Policy:
-------------------
This module does not collect, store, or transmit any user data. All interactions are processed locally.

License:
-------------------
MIT License. See LICENSE file for details.
"""
__version__="0.2.2"
__author__="LvYanHua"
__all__=['EsMsg',
         'FillMsg',
         'Msg']
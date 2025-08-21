from kivymd.app import MDApp
from kivymd.uix.button.button import MDRaisedButton
from kivymd.uix.label.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.textfield.textfield import MDTextFieldRect
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.dialog.dialog import MDDialog
from kivy.core.window import Window
from kivy.uix.image import Image
from easyapp_don.tools.colors import *
from easyapp_don.tools.EasyDialog import dialog
from easyapp_don.tools.Manner import *
from easyapp_don.tools.FillButton import FillButton
from easyapp_don.tools.SpecialButtons.ImgButton import ImgBtn
from easyapp_don.tools.SpecialButtons.ImgFillButton import ImgFillBtn
from easyapp_don.supermarket.tools.Checker import *
from easyapp_don.supermarket.tools.SpecialButtons.FillButton import FillBtn
from easyapp_don.supermarket.tools.SpecialButtons.FillImgButton import FillImgBtn
import sys,os,queue
from typing import Tuple,List,Dict,Any,NoReturn,Union,Optional,TypeVar,Callable,Set
qu=queue.Queue()
class BtnApp(MDApp):
    def __init__(self, t=None, tie="BtnEasyapp_don", theme=LIGHT, color=WHITE12,bs=None, tip=None,**kwargs):
        super().__init__(**kwargs)
        if tip is None:
            tip = {"txt": "Close app?",
                   "tie": "Tip",
                   "ok": ["Yes", GREY13],
                   "cal": ["No", BLUE13]}
        if bs is None:
            bs = [["Button0", RED8, (0.1, 0.05), (0.1, 0.05), True],
                  ["Button1", GREEN7, (0.1, 0.05), (0.5, 0.05), True],
                  ["Button2", BLUE1, (0.1, 0.05), (0.9, 0.05), True]]
        if t is None:
            t = ["Hello,easyapp_don!", (0.5, 0.5)]
        theme=str(check_type(theme,"t",LIGHT))
        self.bs=fill_bs(bs)
        self.txt=check_type(t,list,["Hello,easyapp_don!", (0.5, 0.5)])
        self.tip=fill_tip(tip)
        self.title=tie
        self.color=check_type(color,"c",WHITE12)
        self.theme_cls.theme_style=theme
    def build(self):
        Window.bind(on_request_close=self.on_close)
        self.root=MDFloatLayout()
        self.root.md_bg_color=self.color
        if self.txt:
            t_txt=self.txt[0] if len(self.txt)>0 else "ERROR"
            t_pos=self.txt[1] if len(self.txt)>1 else (0.5,0.5)
            t=MDLabel(text=str(t_txt),
                      halign="center",
                      valign="middle",
                      pos_hint={"center_x":t_pos[0],
                                "center_y":t_pos[1]})
            self.root.add_widget(t)
        if self.bs:
            for b_idx,b_config in enumerate(self.bs):
                b_txt=b_config[0]
                b_color=b_config[1]
                b_size=b_config[2]
                b_pos=b_config[3]
                b_is_close=b_config[4]
                if b_is_close:
                    b=MDRaisedButton(text=str(b_txt),
                                     md_bg_color=b_color,
                                     size_hint=b_size,
                                     pos_hint={"center_x":b_pos[0],
                                               "center_y":b_pos[1]},
                                     on_press=lambda instance,idx=b_idx:self.on_btn(idx))
                    self.root.add_widget(b)
                else:
                    b = MDRaisedButton(text=str(b_txt),
                                       md_bg_color=b_color,
                                       size_hint=b_size,
                                       pos_hint={"center_x": b_pos[0],
                                                 "center_y": b_pos[1]},
                                       on_press=self.on_space)
                    self.root.add_widget(b)
        return self.root
    def on_close(self,window,*args):
        if self.tip:
            txt=self.tip["txt"]
            tie=self.tip["tie"]
            ok=self.tip["ok"]
            cal=self.tip["cal"]
            dialog(t=txt,
                   tie=tie,
                   ok=ok,cal=cal)
            return True
        else:
            qu.put(None)
            self.stop()
            return True
    def on_btn(self,btn_idx):
        qu.put(btn_idx)
        self.stop()
    def on_space(self,instance):
        pass
def btn(t=None, tie="BtnEasyapp_don", theme=LIGHT, color=WHITE12,bs=None, tip=None) -> Optional[int] :
    """
        Creates an interactive button dialog window with customizable text, buttons, and styling,
        returning the index of the clicked button or None when closed.

        This function provides a flexible way to create simple dialogs with buttons for user interaction,
        supporting custom text, button styles, themes, and closing confirmations.

        KeyNotes:
        - All color parameters (button colors, background) must be imported from `easyapp_don.tools.colors`
        - Color variable names end with a number indicating shade depth (e.g., RED8 = dark red, GREEN7 = medium green)
        - The `theme` parameter uses `LIGHT` or `DARK` from `easyapp_don.tools.colors`

        :param t: Configuration for the main display text. Format:
            `["text_content", (center_x, center_y)]`
            - `text_content`: String text to display in the dialog
            - `(center_x, center_y)`: Position coordinates (0-1 range, where (0.5, 0.5) is center)
            Example:
            ```python
            t = ["Please select an option", (0.5, 0.7)]  # Text centered, slightly above middle
            ```
            Defaults to a predefined text if None.

        :param bs: Configuration for the button set. List of button sublists with format:
            `["button_text", button_color, (size_hint_x, size_hint_y), (center_x, center_y), close_on_click]`
            - `button_text`: String displayed on the button
            - `button_color`: Background color from `easyapp_don.tools.colors`
            - `(size_hint_x, size_hint_y)`: Button dimensions relative to screen (0-1 range)
            - `(center_x, center_y)`: Button position coordinates (0-1 range)
            - `close_on_click`: Boolean indicating if dialog closes when button is clicked
            Example:
            ```python
            bs = [
                ["Yes", GREEN7, (0.2, 0.08), (0.3, 0.2), True],   # Green "Yes" button (index 0)
                ["No", RED8, (0.2, 0.08), (0.7, 0.2), True],      # Red "No" button (index 1)
                ["Help", BLUE1, (0.15, 0.06), (0.5, 0.35), False] # Blue "Help" button (index 2, doesn't close)
            ]
            ```
            Defaults to a set of 2 standard buttons if None.

        :param tie: Title of the dialog window displayed in the title bar
            Example: `tie = "Confirmation Required"`
            Defaults to "BtnEasyapp_don".

        :param color: Background color of the dialog window
            Must be a color from `easyapp_don.tools.colors`
            Example: `color = GREY13` (dark grey background)
            Defaults to WHITE12.

        :param theme: Visual theme for the dialog (light or dark mode)
            Use `LIGHT` or `DARK` imported from `easyapp_don.tools.colors`
            Example:
            ```python
            from easyapp_don.tools.colors import DARK
            theme = DARK  # Uses dark theme
            ```
            Defaults to LIGHT.

        :param tip: Configuration for the confirmation dialog shown when closing the window
            Dictionary with structure:
            {
                "txt": "Confirmation message text",
                "tie": "Confirmation dialog title",
                "ok": ["OK button text", button_color],
                "cal": ["Cancel button text", button_color]
            }
            Example:
            ```python
            tip = {
                "txt": "Are you sure you want to exit?",
                "tie": "Confirm Exit",
                "ok": ["Exit", RED8],
                "cal": ["Stay", GREEN7]
            }
            ```
            Defaults to a standard close confirmation if None.

        :return:
            - Integer index of the clicked button (0-based, according to `bs` order)
            - None if the window is closed via the close button (after confirmation)
            - None for buttons where `close_on_click` is False

        Example 1: Basic Confirmation Dialog
        -------------------------------------
        ```python
        from easyapp_don.tools.colors import LIGHT, GREEN7, RED8, GREY13

        # Create a simple yes/no dialog
        choice = btn(
            t=["Do you want to save changes?", (0.5, 0.6)],
            bs=[
                ["Save", GREEN7, (0.25, 0.08), (0.3, 0.2), True],
                ["Discard", RED8, (0.25, 0.08), (0.7, 0.2), True]
            ],
            tie="Save Changes",
            color=GREY13,
            tip={} # if it is not {},this will never return None.
        )

        if choice == 0:
            print("User chose to save")
        elif choice == 1:
            print("User chose to discard")
        else:
            print("Window closed without action")
        ```

        Example 2: Help Dialog with Persistent Button
        ---------------------------------------------
        ```python
        from easyapp_don.tools.colors import DARK, BLUE1, GREY4, WHITE12

        # Create a dialog with a help button that doesn't close the window
        def show_help():
            # This would be called when help button is clicked (index 2)
            print("Displaying help information...")

        result = btn(
            t=["Need assistance?", (0.5, 0.7)],
            bs=[
                ["OK", BLUE1, (0.2, 0.07), (0.3, 0.15), True],
                ["Cancel", GREY4, (0.2, 0.07), (0.7, 0.15), True],
                ["Help", BLUE1, (0.15, 0.07), (0.5, 0.3), False]  # Doesn't close window
            ],
            tie="Help Center",
            theme=DARK,
            color=WHITE12,
            tip={
                "txt": "Close help dialog?",
                "tie": "Confirm Close",
                "ok": ["Close", GREY4],
                "cal": ["Continue", BLUE1]
            }
        )

        if result == 0:
            print("User clicked OK")
        elif result == 1:
            print("User clicked Cancel")
        ```

        Example 3: Minimal Default Dialog
        ---------------------------------
        ```python
        # Use all default settings for a quick confirmation
        response = btn()

        # Default behavior: 2 buttons ("Button0" and "Button1")
        if response == 0:
            print("First default button clicked")
        elif response == 1:
            print("Second default button clicked")
        ```
    """
    app=BtnApp(t=t,tie=tie,theme=theme,color=color,bs=bs,tip=tip)
    app.run()
    return qu.get()
__all__=['btn']
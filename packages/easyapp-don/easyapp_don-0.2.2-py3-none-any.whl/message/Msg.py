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
class MsgApp(MDApp):
    def __init__(self, t=None, tie="MsgEasyapp_don", color=WHITE12, theme=LIGHT,
                 ok=None, cal=None, tip=None, **kwargs):
        super().__init__(**kwargs)
        if tip is None:
            tip = {"tie": "Tip",
                   "txt": "Close app?",
                   "ok": ["Yes", GREY4],
                   "cal": ["No", BLUE13]}
        if t is None:
            t = ["Hello,easyapp_don!", (0.5, 0.5)]
        if ok is None:
            ok = ["Ok", BLUE13, (0.15, 0.05), (0.15, 0.1), True]
        if cal is None:
            cal = ["Cancel", GREY4, (0.15, 0.05), (0.85, 0.1), True]
        tie=str(tie)
        t=check_type(t,list,["Hello,easyapp_don!", (0.5, 0.5)])
        color=check_type(color,"c",WHITE2)
        theme=check_type(theme,"t",LIGHT)
        ok=check_type(ok,list,["Ok", BLUE13, (0.15, 0.05), (0.15, 0.1), True])
        cal=check_type(cal,list,["Cancel", GREY4, (0.15, 0.05), (0.85, 0.1), True])
        self.t=t
        self.theme_cls.theme_style=theme
        self.color=color
        self.ok=ok
        self.cal=cal
        self.title=tie
        self.tip=fill_tip(tip)
    def build(self):
        Window.bind(on_request_close=self.on_close)
        self.root=MDFloatLayout()
        self.root.md_bg_color=self.color
        if self.t:
            t_txt=str(self.t[0]) if len(self.t)>0 else "Hello,easyapp_don!"
            t_pos=self.t[1] if len(self.t)>1 else (0.5,0.5)
            t=MDLabel(text=t_txt,
                      halign="center",
                      valign="middle",
                      pos_hint={"center_x":t_pos[0],
                                "center_y":t_pos[1]})
            self.root.add_widget(t)
        if self.ok:
            ok_txt=str(self.ok[0]) if len(self.ok)>0 else "Ok"
            ok_color=self.ok[1] if len(self.ok)>1 else BLUE13
            ok_size=self.ok[2] if len(self.ok)>2 else (0.15,0.05)
            ok_pos=self.ok[3] if len(self.ok)>3 else (0.15,0.1)
            ok_is_close=self.ok[4] if len(self.ok)>4 else True
            if ok_is_close:
                ok=MDRaisedButton(text=ok_txt,
                                  pos_hint={"center_x":ok_pos[0],
                                            "center_y":ok_pos[1]},
                                  size_hint=ok_size,
                                  md_bg_color=ok_color,
                                  on_press=self.on_ok)
                self.root.add_widget(ok)
            else:
                ok=MDRaisedButton(text=ok_txt,
                                  pos_hint={"center_x":ok_pos[0],
                                            "center_y":ok_pos[1]},
                                  size_hint=ok_size,
                                  md_bg_color=ok_color,
                                  on_press=self.on_space)
                self.root.add_widget(ok)
        if self.cal:
            cal_txt=str(self.cal[0]) if len(self.cal)>0 else "Cancel"
            cal_color=self.cal[1] if len(self.cal)>1 else GREY4
            cal_size=self.cal[2] if len(self.cal)>2 else (0.15,0.05)
            cal_pos=self.cal[3] if len(self.cal)>3 else (0.85,0.1)
            cal_is_close=self.cal[4] if len(self.cal)>4 else True
            if cal_is_close:
                cal=MDRaisedButton(text=cal_txt,
                                   size_hint=cal_size,
                                   pos_hint={"center_x":cal_pos[0],
                                             "center_y":cal_pos[1]},
                                   md_bg_color=cal_color,
                                   on_press=self.on_cal)
                self.root.add_widget(cal)
            else:
                cal = MDRaisedButton(text=cal_txt,
                                     size_hint=cal_size,
                                     pos_hint={"center_x": cal_pos[0],
                                               "center_y": cal_pos[1]},
                                     md_bg_color=cal_color,
                                     on_press=self.on_space)
                self.root.add_widget(cal)
        return self.root
    def on_close(self,window,*args):
        if self.tip:
            tie=self.tip["tie"]
            txt=self.tip["txt"]
            ok=self.tip["ok"]
            cal=self.tip["cal"]
            ok=check_type(ok,list,["Yes",GREY4])
            cal=check_type(cal,list,["No",BLUE13])
            dialog(t=txt,
                   tie=tie,
                   ok=ok,
                   cal=cal)
            return True
        else:
            qu.put(None)
            self.stop()
            return True
    def on_ok(self,instance):
        qu.put(True)
        self.stop()
    def on_cal(self,instance):
        qu.put(False)
        self.stop()
    def on_space(self,instance):
        pass
def msg(t=None, tie="MsgEasyapp_don", color=WHITE12, theme=LIGHT,
        ok=None, cal=None, tip=None) -> Optional[bool]:
    """
        Displays a simple message dialog window with customizable text and buttons,
        returning a boolean result based on user interaction (OK/Cancel clicks) or None if closed.

        KeyNotes:
        - The `theme` parameter values (`LIGHT`/`DARK`) can be imported from `easyapp_don.tools.colors`.
        - All color parameters should be imported from `easyapp_don.tools.colors` (e.g., `WHITE12`, `BLUE13`).
        - Color variable names end with a number indicating shade depth (e.g., `GREY4` = medium grey).

        :param t: Configuration for the main message text. Format:
            `["message_text", (center_x, center_y)]`
            - `message_text`: String content to display as the main message
            - `(center_x, center_y)`: Position on screen (0-1 range, (0.5, 0.5) = center)
            Example:
            ```python
            t = ["Please confirm your action", (0.5, 0.6)]  # Centered text slightly above middle
            ```
            Defaults to `["Hello,easyapp_don!", (0.5, 0.5)]` if None.

        :param tie: Title of the message window (string)
            Example: `tie = "Confirmation Required"`
            Defaults to "MsgEasyapp_don".

        :param color: Background color of the message window.
            Should be a color from `easyapp_don.tools.colors`
            Example: `color = GREY2` (light grey background)
            Defaults to WHITE12.

        :param theme: Overall theme style for the window.
            Import `LIGHT` or `DARK` from `easyapp_don.tools.colors`
            Example:
            ```python
            from easyapp_don.tools.colors import DARK
            theme = DARK  # Uses dark mode
            ```
            Defaults to LIGHT.

        :param ok: Configuration for the OK/Confirm button. Format:
            `["button_text", button_color, (size_hint_x, size_hint_y), (center_x, center_y), is_close_button]`
            - `button_text`: Label displayed on the button (string)
            - `button_color`: Color from `easyapp_don.tools.colors`
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Button position (0-1 range)
            - `is_close_button`: Boolean indicating if click closes the window
            Example:
            ```python
            ok = ["Proceed", GREEN4, (0.2, 0.07), (0.3, 0.1), True]
            ```
            Defaults to `["Ok", BLUE13, (0.15, 0.05), (0.15, 0.1), True]`.

        :param cal: Configuration for the Cancel button. Format same as `ok`:
            `["button_text", button_color, (size_hint_x, size_hint_y), (center_x, center_y), is_close_button]`
            Example:
            ```python
            cal = ["Abort", RED6, (0.2, 0.07), (0.7, 0.1), True]
            ```
            Defaults to `["Cancel", GREY4, (0.15, 0.05), (0.85, 0.1), True]`.

        :param tip: Configuration for the confirmation dialog shown when closing the window via window controls.
            Dictionary with keys:
            - `"tie"`: Dialog title (string)
            - `"txt"`: Dialog message (string)
            - `"ok"`: OK button config: `["text", color]`
            - `"cal"`: Cancel button config: `["text", color]`
            Example:
            ```python
            tip = {
                "tie": "Close Confirmation",
                "txt": "Are you sure you want to close?",
                "ok": ["Yes", RED6],
                "cal": ["No", GREY4]
            }
            ```
            Defaults to a predefined close confirmation dialog.

        :return:
            - `True` if the OK button is clicked
            - `False` if the Cancel button is clicked
            - `None` if the window is closed via the close confirmation dialog's OK button

        Example Usage:
        ```python
        from easyapp_don.tools.colors import LIGHT, BLUE13, RED6, GREY2

        # Show a confirmation dialog
        result = msg(
            t=["Do you want to save changes?", (0.5, 0.6)],
            tie="Save Changes",
            color=GREY2,
            ok=["Save", BLUE13, (0.2, 0.07), (0.3, 0.1), True],
            cal=["Don't Save", RED6, (0.2, 0.07), (0.7, 0.1), True]
        )

        if result is True:
            print("User clicked Save")
        elif result is False:
            print("User clicked Don't Save")
        else:
            print("User closed the window")
        ```
    """
    app=MsgApp(t=t,
               tie=tie,
               color=color,
               theme=theme,
               ok=ok,
               cal=cal,
               tip=tip)
    app.run()
    return qu.get()
__all__=['msg']
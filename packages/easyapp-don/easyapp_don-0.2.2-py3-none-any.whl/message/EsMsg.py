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
class EsMsgApp(MDApp):
    def __init__(self, ts=None, ok=None, cal=None,tie="EsMsgEasyapp_don",color=WHITE12,theme=LIGHT,
                 tip=None,**kwargs):
        super().__init__(**kwargs)
        if tip is None:
            tip = {"tie": "Tip",
                   "txt": "Close app?",
                   "ok": ["Yes", GREY4],
                   "cal": ["No", BLUE13]}
        if cal is None:
            cal = ["Cancel", GREY4, (0.15, 0.05), (0.85, 0.1), True]
        if ok is None:
            ok = ["Ok", BLUE13, (0.15, 0.05), (0.15, 0.1), True]
        if ts is None:
            ts = [["Hello,easyapp_don!", (0.5, 0.95)],
                  ["Text1", (0.15, 0.55)],
                  ["Text2", (0.15, 0.45)],
                  ["Text3", (0.15, 0.35)]]
        ts=fill_ts(ts)
        ok=check_type(ok,list,["Ok", BLUE13, (0.15, 0.05), (0.15, 0.1), True])
        cal=check_type(cal,list,["Cancel", GREY4, (0.15, 0.05), (0.85, 0.1), True])
        tip=fill_tip(tip)
        tie=str(tie)
        color=check_type(color,"c",WHITE12)
        theme=check_type(theme,"t")
        self.ts=fill_ts(ts)
        self.ok=ok
        self.cal=cal
        self.tip=tip
        self.title=tie
        self.color=color
        self.theme_cls.theme_style=theme
    def build(self):
        Window.bind(on_request_close=self.on_close)
        self.root=MDFloatLayout()
        self.root.md_bg_color=self.color
        if self.ts:
            for tt in self.ts:
                t_txt=tt[0]
                t_pos=tt[1]
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
                ok = MDRaisedButton(text=ok_txt,
                                    pos_hint={"center_x": ok_pos[0],
                                              "center_y": ok_pos[1]},
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
                                   pos_hint={"center_x":cal_pos[0],
                                             "center_y":cal_pos[1]},
                                   size_hint=cal_size,
                                   md_bg_color=cal_color,
                                   on_press=self.on_cal)
                self.root.add_widget(cal)
            else:
                cal = MDRaisedButton(text=cal_txt,
                                     pos_hint={"center_x": cal_pos[0],
                                               "center_y": cal_pos[1]},
                                     size_hint=cal_size,
                                     md_bg_color=cal_color,
                                     on_press=self.on_space)
                self.root.add_widget(cal)
        return self.root
    def on_close(self,window,*args):
        if self.tip:
            txt=self.tip["txt"]
            tie=self.tip["tie"]
            ok=self.tip["ok"]
            cal=self.tip["cal"]
            ok=check_type(ok,list,["Yes", GREY4])
            cal=check_type(cal,list,["No", BLUE13])
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
def esmsg(ts=None, ok=None, cal=None,tie="EsMsgEasyapp_don",color=WHITE12,theme=LIGHT,
          tip=None) -> Optional[bool]:
    """
    Displays a customizable message window with multiple text labels and confirmation buttons,
    returning a boolean result based on user interaction (OK/Cancel clicks) or None if closed.

    This function creates a flexible message dialog that supports multiple text elements,
    configurable buttons, and custom styling, making it suitable for displaying detailed
    information or confirmation prompts.

    KeyNotes:
    - The `theme` parameter values (`LIGHT`/`DARK`) can be imported from `easyapp_don.tools.colors`.
    - All color parameters should be imported from `easyapp_don.tools.colors` (e.g., `WHITE12`, `BLUE13`).
    - Color variable names end with a number indicating shade depth (e.g., `GREY4` = medium grey, `BLUE13` = dark blue).

    :param ts: Configuration for multiple text labels. List of sublists with format:
        `["text_content", (center_x, center_y)]`
        - `text_content`: String text to display (supports multiple lines)
        - `(center_x, center_y)`: Position on screen (0-1 range, where (0.5, 0.5) is center)
        Example:
        ```python
        ts = [
            ["System Notification", (0.5, 0.9)],  # Title at top-center
            ["Your settings have been updated", (0.5, 0.7)],  # Main message
            ["Changes will take effect after restart", (0.5, 0.6)],  # Subtext
            ["Version: 2.1.0", (0.5, 0.1)]  # Footer text
        ]
    Defaults to a predefined set of text labels if None.
    :param ok: Configuration for the OK/Confirm button. Sublist with format:
    ["button_text", button_color, (size_hint_x, size_hint_y), (center_x, center_y), is_close_button]
    button_text: Label displayed on the button (string)
    button_color: Button background color from easyapp_don.tools.colors
    (size_hint_x, size_hint_y): Button size relative to screen (0-1 range)
    (center_x, center_y): Button position on screen (0-1 range)
    is_close_button: Boolean (True/False) indicating if clicking closes the window
    Example:
    python

    ok = ["Confirm", GREEN4, (0.2, 0.07), (0.3, 0.15), True]
    Defaults to ["Ok", BLUE13, (0.15, 0.05), (0.15, 0.1), True].
    :param cal: Configuration for the Cancel button. Sublist with same format as ok:
    ["button_text", button_color, (size_hint_x, size_hint_y), (center_x, center_y), is_close_button]
    Example:
    python

    cal = ["Decline", RED6, (0.2, 0.07), (0.7, 0.15), True]
    Defaults to ["Cancel", GREY4, (0.15, 0.05), (0.85, 0.1), True].
    :param tie: Title of the message window (displayed in window title bar)
    Example: tie = "System Update Notification"
    Defaults to "EsMsgEasyapp_don".
    :param color: Background color of the message window.
    Should be a color variable from easyapp_don.tools.colors
    Example: color = GREY2 (light grey background)
    Defaults to WHITE12.
    :param theme: Overall visual theme for the window (light or dark mode).
    Import LIGHT or DARK from easyapp_don.tools.colors
    Example:
    python

    from easyapp_don.tools.colors import DARK
    theme = DARK  # Uses dark mode theme
    Defaults to LIGHT.
    :param tip: Configuration for the confirmation dialog shown when closing the window via window controls.
    Dictionary with keys:
    "tie": Dialog title (string)
    "txt": Dialog message (string)
    "ok": OK button configuration: ["button_text", button_color]
    "cal": Cancel button configuration: ["button_text", button_color]
    Example:
    python

    tip = {
        "tie": "Close Confirmation",
        "txt": "Are you sure you want to close this message?",
        "ok": ["Yes, Close", RED6],
        "cal": ["Stay", BLUE13]
    }
    Defaults to a predefined close confirmation dialog.
    :return:
    True if the OK button is clicked
    False if the Cancel button is clicked
    None if the window is closed via the system close button (after confirming)
    Example Usage 1: Basic Notification
    python

    from easyapp_don.tools.colors import LIGHT, BLUE13, GREY4, GREY2

    # Show a simple notification with multiple texts
    result = esmsg(
        ts=[
            ["Operation Successful", (0.5, 0.8)],
            ["Your data has been saved to cloud", (0.5, 0.6)],
            ["Last updated: 2023-10-05 14:30", (0.5, 0.5)]
        ],
        tie="Success Notification",
        color=GREY2,
        ok=["OK", BLUE13, (0.2, 0.07), (0.5, 0.2), True],
        cal=None  # Hide cancel button by setting to None
    )

    if result is True:
        print("User acknowledged the message")
    Example Usage 2: Confirmation Prompt
    python

    from easyapp_don.tools.colors import DARK, GREEN4, RED6, GREY8

    # Show a critical action confirmation dialog
    confirmation = esmsg(
        ts=[
            ["Warning: Critical Action", (0.5, 0.9)],
            ["This will permanently delete all local data", (0.5, 0.7)],
            ["This operation cannot be undone", (0.5, 0.6)],
            ["Proceed with caution", (0.5, 0.5)]
        ],
        tie="Delete Confirmation",
        color=GREY8,
        theme=DARK,
        ok=["Proceed", GREEN4, (0.25, 0.08), (0.3, 0.15), True],
        cal=["Abort", RED6, (0.25, 0.08), (0.7, 0.15), True],
        tip={
            "tie": "Close Warning",
            "txt": "Close without taking action?",
            "ok": ["Yes", GREY4],
            "cal": ["No", BLUE13]
        }
    )

    if confirmation is True:
        print("User confirmed deletion")
    elif confirmation is False:
        print("User aborted operation")
    else:
        print("User closed the window")
    """
    app=EsMsgApp(ts=ts,
                 ok=ok,
                 cal=cal,
                 tie=tie,
                 color=color,
                 theme=theme,
                 tip=tip)
    app.run()
    return qu.get()
__all__=['esmsg']
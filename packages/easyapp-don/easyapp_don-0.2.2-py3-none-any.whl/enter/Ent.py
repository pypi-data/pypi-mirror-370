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
class EntApp(MDApp):
    def __init__(self, t=None, tie="EntEasyapp_don", color=WHITE12, theme=LIGHT,tip=None, ok=None, cal=None,e=None, **kwargs):
        super().__init__(**kwargs)
        if e is None:
            e = ["Enter something.", (0.96, 0.05), (0.5, 0.5)]
        if cal is None:
            cal = ["Cancel", GREY4, (0.15, 0.05), (0.9, 0.1), True]
        if ok is None:
            ok = ["Ok", BLUE8, (0.15, 0.05), (0.1, 0.1), True]
        if tip is None:
            tip = {"txt": "Close app?",
                   "tie": "Tip",
                   "ok": ["Yes", GREY13],
                   "cal": ["No", BLUE13]}
        if t is None:
            t = ["Hello,easyapp_don!", (0.5, 0.7)]
        self.theme_cls.theme_style=check_type(theme,"t")
        self.color=check_type(color,"c",WHITE12)
        self.e=check_type(e,list,["Enter something.", (0.96, 0.05), (0.5, 0.5)])
        self.ok=check_type(ok,list,["Ok", BLUE8, (0.15, 0.05), (0.1, 0.1), True])
        self.cal=check_type(cal,list,["Cancel",GREY4,(0.15,0.05),(0.9,0.1)])
        self.title=str(tie)
        self.tip=fill_tip(tip)
        self.t=check_type(t,list,["Hello,easyapp_don!",(0.5,0.7)])
        self.inputs=None
        self.res=[]
    def build(self):
        Window.bind(on_request_close=self.on_close)
        self.root=MDFloatLayout()
        self.root.md_bg_color=self.color
        if self.t:
            t_txt=str(self.t[0]) if len(self.t)>0 else "ERROR"
            t_pos=self.t[1] if len(self.t)>1 else (0.5,0.7)
            t=MDLabel(text=t_txt,
                      halign="center",
                      valign="middle",
                      pos_hint={"center_x":t_pos[0],
                                "center_y":t_pos[1]})
            self.root.add_widget(t)
        if self.e:
            e_txt=self.e[0] if len(self.e)>0 else "ERROR"
            e_size=self.e[1] if len(self.e)>1 else (0.96,0.05)
            e_pos=self.e[3] if len(self.e)>3 else (0.5,0.5)
            self.inputs=MDTextFieldRect(hint_text=e_txt,
                                        size_hint=e_size,
                                        pos_hint={"center_x":e_pos[0],
                                                  "center_y":e_pos[1]})
            self.root.add_widget(self.inputs)
        if self.ok:
            o_txt=str(self.ok[0]) if len(self.ok)>0 else "Ok"
            o_color=self.ok[1] if len(self.ok)>1 else BLUE8
            o_size=self.ok[2] if len(self.ok)>2 else (0.15,0.05)
            o_pos=self.ok[3] if len(self.ok)>3 else (0.1,0.1)
            o_is_close=self.ok[4] if len(self.ok)>4 else True
            if o_is_close:
                ok=MDRaisedButton(text=o_txt,
                                  pos_hint={"center_x":o_pos[0],
                                            "center_y":o_pos[1]},
                                  size_hint=o_size,
                                  md_bg_color=o_color,
                                  on_press=self.on_ok)
                self.root.add_widget(ok)
            else:
                ok = MDRaisedButton(text=o_txt,
                                    pos_hint={"center_x": o_pos[0],
                                              "center_y": o_pos[1]},
                                    size_hint=o_size,
                                    md_bg_color=o_color,
                                    on_press=self.on_space)
                self.root.add_widget(ok)
        if self.cal:
            c_txt=str(self.cal[0]) if len(self.cal)>0 else "Cancel"
            c_color=self.cal[1] if len(self.cal)>1 else GREY4
            c_size=self.cal[2] if len(self.cal)>2 else (0.15,0.05)
            c_pos=self.cal[3] if len(self.cal)>3 else (0.9,0.1)
            c_is_close=self.cal[4] if len(self.cal)>4 else True
            if c_is_close:
                cal=MDRaisedButton(text=c_txt,
                                   size_hint=c_size,
                                   pos_hint={"center_x":c_pos[0],
                                             "center_y":c_pos[1]},
                                   md_bg_color=c_color,
                                   on_press=self.on_cal)
                self.root.add_widget(cal)
            else:
                cal = MDRaisedButton(text=c_txt,
                                     size_hint=c_size,
                                     pos_hint={"center_x": c_pos[0],
                                               "center_y": c_pos[1]},
                                     md_bg_color=c_color,
                                     on_press=self.on_space)
                self.root.add_widget(cal)
    def on_close(self,window,*args):
        if self.tip:
            txt=self.tip["txt"]
            tie=self.tip["tie"]
            ok=self.tip["ok"]
            cal=self.tip["cal"]
            dialog(txt,tie, ok, cal)
            return True
        else:
            self.res=[None,str(self.inputs.text)]
            qu.put(self.res)
            self.stop()
            return True
    def on_ok(self,instance):
        self.res=[True,str(self.inputs.text)]
        qu.put(self.res)
        self.stop()
    def on_cal(self,instance):
        self.res=[False,str(self.inputs.text)]
        qu.put(self.res)
        self.stop()
    def on_space(self,instance):
        pass
def ent(t=None, tie="EntEasyapp_don", color=WHITE12, theme=LIGHT,tip=None, ok=None, cal=None,e=None) -> list :
    """
    Creates an interactive input dialog application using KivyMD framework.
    This function initializes and runs a simple input interface with customizable
    text, buttons, and styling. It returns user interaction results including
    the action performed (OK/Cancel/Close) and the input text.
    :param t: Optional list specifying title text and position.
    Format: [text_str, (x_pos, y_pos)] where positions are normalized (0-1)
    :type t: list
    :param tie: Title of the application window
    :type tie: str
    :param color: Background color of the main layout
    :type color: tuple
    :param theme: Application theme style (LIGHT or DARK)
    :type theme: str
    :param tip: Dictionary configuring the close confirmation dialog
    Format: {"txt": message, "tie": title, "ok": [button_text, color], "cal": [button_text, color]}
    :type tip: dict
    :param ok: Configuration for the OK button
    Format: [text, color, (width, height), (x_pos, y_pos), is_close_bool]
    :type ok: list
    :param cal: Configuration for the Cancel button
    Format: [text, color, (width, height), (x_pos, y_pos), is_close_bool]
    :type cal: list
    :param e: Configuration for the input text field
    Format: [hint_text, (width, height), (x_pos, y_pos)]
    :type e: list
    :return: A list containing interaction result and input text
    Format: [action_bool, input_text] where action_bool indicates OK (True),
    Cancel (False), or None (window close) when tip={}
    :rtype: list
    """
    app=EntApp(t,tie,color,theme,tip,ok,cal,e)
    app.run()
    return qu.get()
__all__=['ent']
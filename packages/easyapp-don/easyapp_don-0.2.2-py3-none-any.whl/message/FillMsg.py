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
class FillMsg(MDApp):
    def __init__(self, ts=None, tie="FillMsgEasyapp_don",theme=LIGHT,color=WHITE12,ok=None,cal=None,tip=None,fs=None,**kwargs):
        super().__init__(**kwargs)
        if ok is None:
            ok = ["Ok", BLUE13, (0.15, 0.05), (0.15, 0.1), True]
        if cal is None:
            cal = ["Cancel", GREY4, (0.15, 0.05), (0.85, 0.1), True]
        if tip is None:
            tip = {"txt": "Close app?",
                   "tie": "Tip",
                   "ok": ["Yes", GREY1],
                   "cal": ["No", GREEN6]}
        if fs is None:
            fs = [["0", GREY10, BLUE3, (0.01, 0.05), (0.3, 0.7)],
                  ["1", GREY10, BLUE3, (0.01, 0.05), (0.3, 0.5)],
                  ["2", GREY10, BLUE3, (0.01, 0.05), (0.3, 0.3)]]
        if ts is None:
            ts = [["Text1", (0.7, 0.7)],
                  ["Text2", (0.7, 0.5)],
                  ["Text3", (0.7, 0.3)],
                  ["Hello,easyapp_don!", (0.5, 0.2)]]
        self.theme_cls.theme_style=check_type(theme,"t")
        self.color=check_type(color,"c",WHITE12)
        self.title=str(tie)
        self.ok=check_type(ok,list,["Ok", BLUE13, (0.15, 0.05), (0.15, 0.1), True])
        self.cal=check_type(cal,list,["Cancel", GREY4, (0.15, 0.05), (0.85, 0.1), True])
        self.tip=fill_tip(tip)
        self.fs=fill_fs(fs)
        self.ts=fill_ts(ts)
        self.res=[]
        self.ff=[]
        self.ffs=[]
    def build(self):
        Window.bind(on_request_close=self.on_close)
        self.root=MDFloatLayout()
        self.root.md_bg_color=self.color
        if self.ts:
            for tt in self.ts:
                if isinstance(tt,list):
                    t_txt=str(tt[0]) if len(tt)>0 else "ERROR"
                    t_pos=tt[1] if len(tt)>1 else (0.5,0.5)
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
                                  md_bg_color=ok_color,
                                  pos_hint={"center_x":ok_pos[0],
                                            "center_y":ok_pos[1]},
                                  size_hint=ok_size,
                                  on_press=self.on_ok)
                self.root.add_widget(ok)
            else:
                ok = MDRaisedButton(text=ok_txt,
                                    md_bg_color=ok_color,
                                    pos_hint={"center_x": ok_pos[0],
                                              "center_y": ok_pos[1]},
                                    size_hint=ok_size,
                                    on_press=self.on_space)
                self.root.add_widget(ok)
        if self.cal:
            c_txt=str(self.cal[0]) if len(self.cal)>0 else "Cancel"
            c_color=self.cal[1] if len(self.cal)>1 else GREY4
            c_size=self.cal[2] if len(self.cal)>2 else (0.15,0.05)
            c_pos=self.cal[3] if len(self.cal)>3 else (0.85,0.1)
            c_is_close=self.cal[4] if len(self.cal)>4 else True
            if c_is_close:
                c=MDRaisedButton(text=c_txt,
                                 md_bg_color=c_color,
                                 size_hint=c_size,
                                 pos_hint={"center_x":c_pos[0],
                                           "center_y":c_pos[1]},
                                 on_press=self.on_cal)
                self.root.add_widget(c)
            else:
                c = MDRaisedButton(text=c_txt,
                                   md_bg_color=c_color,
                                   size_hint=c_size,
                                   pos_hint={"center_x": c_pos[0],
                                             "center_y": c_pos[1]},
                                   on_press=self.on_space)
                self.root.add_widget(c)
        if self.fs:
            for f_idx,f_config in enumerate(self.fs):
                f_idx=int(f_idx)
                f_txt=str(f_config[0]) if len(f_config)>0 else "ERROR"
                f_color=f_config[1] if len(f_config)>1 else GREY13
                f_t_color=f_config[2] if len(f_config)>2 else BLUE1
                f_size=f_config[3] if len(f_config)>3 else (0.05,0.05)
                f_pos=f_config[4] if len(f_config)>4 else (0.7,0.3)
                f=FillButton(txt=f_txt,
                             color=f_color,
                             t_color=f_t_color,
                             size=f_size,
                             pos=f_pos,
                             idx=f_idx,
                             add_to=self.ff)
                self.ffs.append(f)
                self.root.add_widget(f)
        return self.root
    def on_close(self,window,*args):
        if self.tip:
            txt=self.tip["txt"]
            tie=self.tip["tie"]
            ok=self.tip["ok"]
            cal=self.tip["cal"]
            dialog(t=txt,
                   tie=tie,
                   ok=ok,
                   cal=cal)
            return True
        else:
            for f_idx,f_btn in enumerate(self.ffs):
                self.ff=f_btn.get_return()
            self.res=[None,self.ff]
            qu.put(self.res)
            self.stop()
            return True
    def on_ok(self,instance):
        for f_idx,f_btn in enumerate(self.ffs):
            self.ff=f_btn.get_return()
        self.res=[True,self.ff]
        qu.put(self.res)
        self.stop()
    def on_cal(self,instance):
        for f_idx,f_btn in enumerate(self.ffs):
            self.ff=f_btn.get_return()
        self.res=[False,self.ff]
        qu.put(self.res)
        self.stop()
    def on_space(self,instance):
        pass
def fillmsg(ts=None, tie="FillMsgEasyapp_don",theme=LIGHT,color=WHITE12,ok=None,cal=None,tip=None,fs=None) -> list:
    """
    This is an upgraded esmsg() function with filled buttons,
    featuring more advanced capabilities than the general msg() and esmsg() functions.

    :param ts: Two-dimensional list of page texts. Format: [[text, text_pos], [text, text_pos]].
               - text: Displayed text content (string)
               - text_pos: Position in the window, expressed as (center_x, center_y) where values range from 0 to 1
               Example: [["Welcome!", (0.5, 0.8)], ["Please select an option:", (0.5, 0.6)]]
    :type ts: list
    :param tie: Page title
               Example: "Survey Form"
    :type tie: str
    :param theme: Page theme, there are 2 options: LIGHT and DARK. You need to import easyapp_don.tools.colors to get them.
               Example: LIGHT
    :type theme: str
    :param color: Page background color. You need to import easyapp_don.tools.colors to get color variables,
                  where the number after the color name indicates the shade.
               Example: BLUE5
    :type color: tuple
    :param ok: OK button configuration. It is a list in the format:
               [ok_text, ok_color, ok_size, ok_pos, ok_is_close]
               - ok_text: Button text (string)
               - ok_color: Button background color (from easyapp_don.tools.colors)
               - ok_size: Button size, (width_ratio, height_ratio) where values range from 0 to 1
               - ok_pos: Button position, (center_x, center_y) where values range from 0 to 1
               - ok_is_close: Whether to close the page after clicking (boolean)
               Example: ["Submit", GREEN6, (0.2, 0.08), (0.3, 0.1), True]
    :type ok: list
    :param cal: Cancel button configuration. It is a list in the format:
               [cancel_text, cancel_color, cancel_size, cancel_pos, cancel_is_close]
               - cancel_text: Button text (string)
               - cancel_color: Button background color (from easyapp_don.tools.colors)
               - cancel_size: Button size, (width_ratio, height_ratio) where values range from 0 to 1
               - cancel_pos: Button position, (center_x, center_y) where values range from 0 to 1
               - cancel_is_close: Whether to close the page after clicking (boolean)
               Example: ["Reset", RED5, (0.2, 0.08), (0.7, 0.1), True]
    :type cal: list
    :param tip: A prompt box that pops up when clicking the window close button.
                If set to {}, it will not pop up. Basic format:
                {"tie": "Tip (page title)", "txt": "page text", "ok": [ok_text, ok_color], "cal": [cal_text, cal_color]}
                - tie: Prompt box title (string)
                - txt: Prompt content (string)
                - ok: Confirm button [text, color]
                - cal: Cancel button [text, color]
               Example: {"tie": "Confirm Exit", "txt": "Are you sure you want to exit?",
                         "ok": ["Yes", RED5], "cal": ["No", GREY4]}
    :type tip: dict
    :param fs: Checkable buttons, commonly used in answer sheets. Format:
               [[option_text, normal_color, selected_color, size, position], ...]
               - option_text: Display text on the button (string)
               - normal_color: Button color when not selected (from easyapp_don.tools.colors)
               - selected_color: Button color when selected (from easyapp_don.tools.colors)
               - size: Button size, (width_ratio, height_ratio) where values range from 0 to 1
               - position: Button position, (center_x, center_y) where values range from 0 to 1
               Example: [["Option 1", GREY10, BLUE3, (0.4, 0.1), (0.5, 0.5)],
                         ["Option 2", GREY10, BLUE3, (0.4, 0.1), (0.5, 0.35)]]
    :type fs: list
    :return: Returns a list with two elements [status, selected_buttons]
             - status: True (OK clicked), False (Cancel clicked), None (window closed)
             - selected_buttons: List of indexes of selected checkable buttons (from fs parameter)
             Example: [True, [0, 2]] means OK was clicked and the 1st and 3rd buttons were selected
    :rtype: list
    """
    app=FillMsg(ts=ts,tie=tie,theme=theme,color=color,ok=ok,cal=cal,tip=tip,fs=fs)
    app.run()
    return qu.get()
__all__=['fillmsg']
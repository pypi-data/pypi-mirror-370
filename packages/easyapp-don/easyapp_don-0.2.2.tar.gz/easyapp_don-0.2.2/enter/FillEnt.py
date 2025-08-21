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
class FillEntApp(MDApp):
    def __init__(self, ts=None, fs=None, es=None,color=WHITE12, theme=LIGHT, tip=None, ok=None,cal=None, tie="FillEntEasyapp_don", **kwargs):
        super().__init__(**kwargs)
        if cal is None:
            cal = ["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1)]
        if ok is None:
            ok = ["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True]
        if tip is None:
            tip = {"txt": "Close app?",
                   "tie": "Tip",
                   "ok": ["Yes", GREY4],
                   "cal": ["No", BLUE13]}
        if es is None:
            es = [["Enter1", (0.3, 0.05), (0.75, 0.7)],
                  ["Enter2", (0.3, 0.05), (0.75, 0.5)],
                  ["Enter3", (0.3, 0.05), (0.75, 0.3)]]
        if fs is None:
            fs = [["a(0)", GREY4, RED8, (0.05, 0.05), (0.4, 0.7)],
                  ["b(1)", GREY4, GREEN10, (0.05, 0.05), (0.4, 0.5)],
                  ["c(2)", GREY4, BLUE8, (0.05, 0.05), (0.4, 0.3)]]
        if ts is None:
            ts = [["Hello,easyapp_don!", (0.5, 0.9)],
                  ["Text1", (0.2, 0.7)],
                  ["Text2", (0.2, 0.5)],
                  ["Text3", (0.2, 0.3)],
                  ["1/1", (0.5, 0.05)]]
        self.theme_cls.theme_style=check_type(theme,"t")
        self.title=str(tie)
        self.tip=fill_tip(tip)
        self.fs=fill_fs(fs)
        self.es=fill_es(es)
        self.ok=check_type(ok,list,["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True])
        self.cal=check_type(cal,list,["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1)])
        self.ts=fill_ts(ts)
        self.color=check_type(color,"c",WHITE12)
        self.f_add_to=[]
        self.f_s=[]
        self.res=[]
        self.inputs=[]
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
            o_txt=str(self.ok[0])
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
            c_txt=str(self.cal[0])
            c_color=self.cal[1] if len(self.cal)>1 else GREY4
            c_size=self.cal[2] if len(self.cal)>2 else (0.15,0.05)
            c_pos=self.cal[3] if len(self.cal)>3 else (0.9,0.1)
            c_is_close=self.cal[4] if len(self.cal)>4 else True
            if c_is_close:
                cal=MDRaisedButton(text=c_txt,
                                   pos_hint={"center_x":c_pos[0],
                                             "center_y":c_pos[1]},
                                   size_hint=c_size,
                                   md_bg_color=c_color,
                                   on_press=self.on_cal)
                self.root.add_widget(cal)
            else:
                cal = MDRaisedButton(text=c_txt,
                                     pos_hint={"center_x": c_pos[0],
                                               "center_y": c_pos[1]},
                                     size_hint=c_size,
                                     md_bg_color=c_color,
                                     on_press=self.on_space)
                self.root.add_widget(cal)
        if self.es:
            for e_idx,e_config in enumerate(self.es):
                e_txt=e_config[0]
                e_size=e_config[1]
                e_pos=e_config[2]
                e1=MDTextFieldRect(hint_text=e_txt,
                                   pos_hint={"center_x":e_pos[0],
                                             "center_y":e_pos[1]},
                                   size_hint=e_size)
                self.inputs.append(e1)
                self.root.add_widget(e1)
        if self.fs:
            for f_idx,f_config in enumerate(self.fs):
                f_txt=f_config[0]
                f_color=f_config[1]
                f_c_color=f_config[2]
                f_size=f_config[3]
                f_pos=f_config[4]
                f=FillButton(txt=f_txt,
                             color=f_color,
                             t_color=f_c_color,
                             size=f_size,
                             pos=f_pos,
                             idx=f_idx,
                             add_to=self.f_add_to)
                self.f_s.append(f)
                self.root.add_widget(f)
        return self.root
    def on_close(self,window,*args):
        if self.tip:
            txt=self.tip["txt"]
            tie=self.tip["tie"]
            ok=self.tip["ok"]
            cal=self.tip["cal"]
            dialog(txt,tie, ok, cal)
            return True
        else:
            inputs=[t.text for t in self.inputs]
            for f_idx,f_config in enumerate(self.f_s):
                self.f_add_to=f_config.get_return()
            self.res=[None,self.f_add_to,inputs]
            qu.put(self.res)
            self.stop()
            return True
    def on_ok(self,instance):
        inputs=[t.text for t in self.inputs]
        for f_idx,f_config in enumerate(self.f_s):
            self.f_add_to=f_config.get_return()
        self.res=[True,self.f_add_to,inputs]
        qu.put(self.res)
        self.stop()
    def on_cal(self,instance):
        inputs = [t.text for t in self.inputs]
        for f_idx, f_config in enumerate(self.f_s):
            self.f_add_to = f_config.get_return()
        self.res = [False, self.f_add_to, inputs]
        qu.put(self.res)
        self.stop()
    def on_space(self,instance):
        pass
def fillent(ts=None, fs=None, es=None,color=WHITE12, theme=LIGHT, tip=None, ok=None,cal=None, tie="FillEntEasyapp_don") -> list:
    """
    Create an interactive interface application based on KivyMD with text labels, input fields, and custom fill buttons for data collection.
    This function generates a customizable interface that includes text labels, input fields, special fill buttons,
    confirmation/cancellation buttons, and supports theme customization, color settings, and closing prompts.
    It returns the user's operation status, selections from fill buttons, and text input content.

    Parameters:
        ts (Optional[List[List]]): Configuration list for text labels. Each element follows the format
            ["Text content", (x_position, y_position)], where x and y are proportional coordinates (0-1 relative to screen).
            Contains sample text by default.
        fs (Optional[List[List]]): Configuration list for fill buttons. Each element follows the format
            ["Button text", default_color, selected_color, (width_ratio, height_ratio), (x_position, y_position)].
            These interactive buttons can maintain selection states. Contains 3 sample buttons by default.
        es (Optional[List[List]]): Configuration list for text input fields. Each element follows the format
            ["Hint text", (width_ratio, height_ratio), (x_position, y_position)]. Contains 3 input fields by default.
        color (Tuple[float, float, float, float]): Background color in RGBA format (values 0-1). Defaults to WHITE12.
        theme (str): Application theme style, should be "LIGHT" or "DARK". Defaults to LIGHT.
        tip (Optional[Dict]): Configuration for closing confirmation dialog. Format:
            {"txt": "Dialog content", "tie": "Dialog title", "ok": [ok_text, ok_color], "cal": [cancel_text, cancel_color]}.
            Defaults to a basic close confirmation.
        ok (Optional[List]): Confirmation button configuration. Format:
            [text, color, (width_ratio, height_ratio), (x_position, y_position), is_close].
            Last parameter indicates if app closes on click. Defaults to ["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True].
        cal (Optional[List]): Cancellation button configuration. Format:
            [text, color, (width_ratio, height_ratio), (x_position, y_position), is_close].
            Last parameter indicates if app closes on click. Defaults to ["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1)].
        tie (str): Application window title. Defaults to "FillEntEasyapp_don".

    Returns:
        list: A list containing three elements:
            - First element (Union[bool, None]): Operation status - True for OK click, False for Cancel click, None for direct closure.
            - Second element (List[int]): Selection index from fill buttons.
            - Third element (List[str]): User input text from all input fields.
    """
    app=FillEntApp(ts,fs,es,color,theme,tip,ok,cal,tie)
    app.run()
    return qu.get()
__all__=['fillent']
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
class EsEntApp(MDApp):
    def __init__(self, ts=None, es=None, ok=None,cal=None, tie="EsEntEasyapp_don", theme=LIGHT, color=WHITE12,tip=None, **kwargs):
        super().__init__(**kwargs)
        if tip is None:
            tip = {"txt": "Close app?",
                   "tie": "Tip",
                   "ok": ["Yes", GREY13],
                   "cal": ["No", GREEN7]}
        if cal is None:
            cal = ["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True]
        if ok is None:
            ok = ["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True]
        if es is None:
            es = [["Enter1", (0.3, 0.05), (0.75, 0.7)],
                  ["Enter2", (0.3, 0.05), (0.75, 0.5)],
                  ["Enter3", (0.3, 0.05), (0.75, 0.3)]]
        if ts is None:
            ts = [["Hello,easyapp_don!", (0.5, 0.9)],
                  ["Text1", (0.2, 0.7)],
                  ["Text2", (0.2, 0.5)],
                  ["Text3", (0.2, 0.3)]]
        self.theme_cls.theme_style=check_type(theme,"t")
        self.title=str(tie)
        self.color=check_type(color,"c",WHITE12)
        self.ts=fill_ts(ts)
        self.es=fill_es(es)
        self.ok=check_type(ok,list,["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True])
        self.cal=check_type(cal,list,["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True])
        self.tip=fill_tip(tip)
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
            for ee in self.es:
                e_txt=ee[0]
                e_size=ee[1]
                e_pos=ee[2]
                e1=MDTextFieldRect(hint_text=e_txt,
                                   pos_hint={"center_x":e_pos[0],
                                             "center_y":e_pos[1]},
                                   size_hint=e_size)
                self.inputs.append(e1)
                self.root.add_widget(e1)
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
            self.res=[None,inputs]
            qu.put(self.res)
            self.stop()
            return True
    def on_ok(self,instance):
        inputs=[t.text for t in self.inputs]
        self.res=[True,inputs]
        qu.put(self.res)
        self.stop()
    def on_cal(self,instance):
        inputs=[t.text for t in self.inputs]
        self.res=[False,inputs]
        qu.put(self.res)
        self.stop()
    def on_space(self,instance):
        pass
def esent(ts=None, es=None, ok=None,cal=None, tie="EsEntEasyapp_don", theme=LIGHT, color=WHITE12,tip=None):
    """
    Create a simple interactive interface application based on KivyMD for collecting user input and returning interaction results.
    This function generates an interface containing text labels, input fields, confirmation buttons, and cancellation buttons
    through configuration parameters. It supports custom themes, colors, and closing prompts, and finally returns the user's
    operation status and input content.

    Parameters:
        ts (Optional[List[List]]): Configuration list for text labels. Each element follows the format
            ["Text content", (x_position, y_position)], where x and y are proportional coordinates relative to the screen (0-1).
            Contains sample text by default.
        es (Optional[List[List]]): Configuration list for input fields. Each element follows the format
            ["Hint text", (width_ratio, height_ratio), (x_position, y_position)], where width/height ratios are relative to
            screen size, and x/y are center coordinates. Contains 3 input fields by default.
        ok (Optional[List]): Configuration for the confirmation button. Format:
            [text, color, (width_ratio, height_ratio), (x_position, y_position), is_close], where the last parameter
            indicates whether to close the app after clicking. Defaults to ["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True].
        cal (Optional[List]): Configuration for the cancellation button. Format:
            [text, color, (width_ratio, height_ratio), (x_position, y_position), is_close], where the last parameter
            indicates whether to close the app after clicking. Defaults to ["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True].
        tie (str): Title of the application window. Defaults to "EsEntEasyapp_don".
        theme (str): Theme style of the application. Should be either "LIGHT" or "DARK". Defaults to LIGHT.
        color (Tuple[float, float, float, float]): Background color of the interface in RGBA format (values 0-1).
            Defaults to WHITE12.
        tip (Optional[Dict]): Configuration for the closing confirmation dialog. Format:
            {"txt": "Dialog content", "tie": "Dialog title", "ok": [ok_button_text, ok_button_color],
             "cal": [cancel_button_text, cancel_button_color]}. Defaults to a confirmation dialog for closing the app.

    Returns:
        List[Union[bool, None], List[str]]: A list containing two elements:
            - The first element indicates the operation status: True for OK button click, False for Cancel button click,
              None for direct window closure.
            - The second element is a list of strings representing the user input from all input fields.
    """
    app=EsEntApp(ts,es,ok,cal,tie,theme,color,tip)
    app.run()
    return qu.get()
__all__=['esent']
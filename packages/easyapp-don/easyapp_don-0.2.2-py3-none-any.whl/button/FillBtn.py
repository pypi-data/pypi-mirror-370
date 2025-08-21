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
class FillBtnApp(MDApp):
    def __init__(self, ts=None, tie="FillBtnEasyapp_don", theme=LIGHT, color=WHITE12, tip=None,bs=None, fs=None, **kwargs):
        super().__init__(**kwargs)
        if fs is None:
            fs = [["0", GREY13, RED8, (0.05, 0.05), (0.7, 0.7)],
                  ["1", GREY13, GREEN7, (0.05, 0.05), (0.7, 0.5)],
                  ["2", GREY13, BLUE13, (0.05, 0.05), (0.7, 0.3)]]
        if bs is None:
            bs = [["Button0", RED8, (0.15, 0.05), (0.1, 0.1), True],
                  ["Button1", GREEN6, (0.15, 0.05), (0.5, 0.1), True],
                  ["Button2", BLUE13, (0.15, 0.05), (0.9, 0.1), True]]
        if tip is None:
            tip = {"txt": "Close app?",
                   "tie": "Tip",
                   "ok": ["Yes", GREY4],
                   "cal": ["No", GREEN7]}
        if ts is None:
            ts = [["Hello,easyapp_don!", (0.5, 0.95)],
                  ["Text1", (0.2, 0.7)],
                  ["Text2", (0.2, 0.5)],
                  ["Text3", (0.2, 0.3)],
                  ["1/1", (0.5, 0.05)]]
        self.theme_cls.theme_style=check_type(theme,"t")
        self.title=str(tie)
        self.color=check_type(color,"c",WHITE12)
        self.ts=fill_ts(ts)
        self.tip=fill_tip(tip)
        self.bs=fill_bs(bs)
        self.fs=fill_fs(fs)
        self.f_s=[]
        self.f_add_to=[]
        self.res=[]
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
        if self.bs:
            for b_idx,b_config in enumerate(self.bs):
                b_txt=b_config[0]
                b_color=b_config[1]
                b_size=b_config[2]
                b_pos=b_config[3]
                b_is_close=b_config[4]
                if b_is_close:
                    b=MDRaisedButton(text=b_txt,
                                     pos_hint={"center_x":b_pos[0],
                                               "center_y":b_pos[1]},
                                     size_hint=b_size,
                                     md_bg_color=b_color,
                                     on_press=lambda instance,idx=b_idx:self.on_btn(idx))
                    self.root.add_widget(b)
                else:
                    b = MDRaisedButton(text=b_txt,
                                       pos_hint={"center_x": b_pos[0],
                                                 "center_y": b_pos[1]},
                                       size_hint=b_size,
                                       md_bg_color=b_color,
                                       on_press=self.on_space)
                    self.root.add_widget(b)
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
            for f_idx,f_config in enumerate(self.f_s):
                self.f_add_to=f_config.get_return()
            self.res=[None,self.f_add_to]
            qu.put(self.res)
            self.stop()
            return True
    def on_btn(self,btn_idx):
        for f_idx,f_config in enumerate(self.f_s):
            self.f_add_to=f_config.get_return()
        self.res=[btn_idx,self.f_add_to]
        qu.put(self.res)
        self.stop()
    def on_space(self,instance):
        pass
def fillbtn(ts=None, tie="FillBtnEasyapp_don", theme=LIGHT, color=WHITE12, tip=None,bs=None, fs=None) -> list:
    """
    A flexible interface for creating interactive applications with customizable text, buttons, and fillable components.
    This function initializes a KivyMD application that supports multiple text elements, standard buttons,
    and specialized fillable buttons. It returns a dictionary containing the user's interaction results,
    including which button was pressed and the state of fillable components.

    :param ts: List of text elements to display. Each element should be a list in format:
               [text_content, (x_position, y_position)]
               where positions are normalized values between 0 and 1.
    :type ts: list

    :param tie: Title for the application window.
    :type tie: str

    :param theme: Application theme style. Should be either LIGHT or DARK.
    :type theme: str

    :param color: Background color for the main layout, using color tuples from easyapp_don.tools.colors.
    :type color: tuple

    :param tip: Configuration for the close confirmation dialog. Should be a dictionary with:
                - "txt": Message text
                - "tie": Dialog title
                - "ok": [Button text, Button color] for confirmation
                - "cal": [Button text, Button color] for cancellation
                Set to None to disable close confirmation.
    :type tip: dict

    :param bs: List of standard button configurations. Each button is defined as:
               [button_text, button_color, (width, height), (x_position, y_position), close_on_click]
               where close_on_click is a boolean indicating if the app should close when clicked.
    :type bs: list

    :param fs: List of fillable button configurations. Each fillable button is defined as:
               [default_text, base_color, text_color, (width, height), (x_position, y_position)]
               These specialized buttons can maintain state and be interactively modified.
    :type fs: list

    :return:The list of return.example:[clicked_btn_index,[filled_btn_index,....]]
    :rtype: list
    """
    app=FillBtnApp(ts,tie,theme,color,tip,bs,fs)
    app.run()
    return qu.get()
__all__=['fillbtn']
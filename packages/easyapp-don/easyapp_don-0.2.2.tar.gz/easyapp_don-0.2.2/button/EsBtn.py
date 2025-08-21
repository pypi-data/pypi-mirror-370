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
class EsBtnApp(MDApp):
    def __init__(self, ts=None, tie="EsBtnEasyapp_don", color=WHITE12, theme=LIGHT,tip=None, bs=None, **kwargs):
        super().__init__(**kwargs)
        if ts is None:
            ts = [["Hello,easyapp_don!", (0.5, 0.95)],
                  ["Text1", (0.15, 0.7)],
                  ["Text2", (0.15, 0.5)],
                  ["Text3", (0.15, 0.3)],
                  ["1/1", (0.5, 0.05)]]
        if bs is None:
            bs = [["Button0", RED1, (0.15, 0.05), (0.1, 0.1), True],
                  ["Button1", GREEN6, (0.15, 0.05), (0.5, 0.1), True],
                  ["Button2", BLUE3, (0.15, 0.05), (0.9, 0.1), True]]
        if tip is None:
            tip = {"tie": "Tip",
                   "txt": "Close app?",
                   "ok": ["Yes", GREY4],
                   "cal": ["No", BLUE13]}
        self.ts=fill_ts(ts)
        self.title=str(tie)
        self.color=check_type(color,"c",WHITE12)
        self.theme_cls.theme_style=check_type(theme,"t")
        self.tip=fill_tip(tip)
        self.bs=fill_bs(bs)
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
        return self.root
    def on_close(self,window,*args):
        if self.tip:
            txt=self.tip["txt"]
            tie=self.tip["tie"]
            ok=self.tip["ok"]
            cal=self.tip["cal"]
            dialog(t=txt,tie=tie,ok=ok,cal=cal)
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
def esbtn(ts=None, tie="EsBtnEasyapp_don", color=WHITE12, theme=LIGHT,tip=None, bs=None) -> Optional[int] :
    """
        This is an upgraded version of the msg() function, which is more flexible than the msg() function and has multiple buttons.
        :param ts: List of page texts. Format: [[text1 content, text position],[text2_content,text_position]]
        :type ts: list
        :param tie: Page title.Example:"Easyapp_don title"
        :type tie: str
        :param theme: Page theme, only LIGHT and DARK are available. You need to import easyapp_don.tools.colors to get the colors.
                Example: LIGHT
        :type theme: str
        :param color: Page background color.
        You also need to import easyapp_don.tools.colors to get color variables,
        where the number after the variable indicates the shade.
        Example: WHITE12
        :type color: tuple
        :param bs: Two-dimensional list of page buttons.
        Format: [[button text, button color, button size, button position, boolean value indicating whether to close after clicking]]
        :type bs: list
        :param tip: Prompt box that pops up after clicking to close the page,
        with the format as shown in msg().
        :type tip: dict
        :return: Returns the index of the button. When tip={}, returns None after clicking to close.
        :rtype: int | None
    """
    app=EsBtnApp(ts=ts,tie=tie,color=color,theme=theme,tip=tip,bs=bs)
    app.run()
    return qu.get()
__all__=['esbtn']
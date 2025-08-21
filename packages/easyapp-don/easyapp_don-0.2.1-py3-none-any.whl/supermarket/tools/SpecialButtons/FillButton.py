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
from easyapp_don.supermarket.tools.Checker import *
import sys,os,queue
from typing import Tuple,List,Dict,Any,NoReturn,Union,Optional,TypeVar,Callable,Set
class FillBtn(MDRaisedButton):
    def __init__(self, txt="Btn0", color=GREY4, t_color=BLUE1, size=(0.05,0.05), pos=(0.5,0.1), idx=0, add_to=None,**kwargs):
        super().__init__(**kwargs)
        if add_to is None:
            add_to = []
        self.text=str(txt)
        self.color=check_type(color,"c",GREY1)
        self.md_bg_color=check_type(color,"c",GREY4)
        self.t_color=check_type(t_color,"c",BLUE8)
        self.size_hint=size
        self.pos_hint={"center_x":pos[0],
                       "center_y":pos[1]}
        self.idx=idx
        self.add_to=add_to
        self.clicked=False
    def on_press(self):
        super().on_press()
        self.clicked=not self.clicked
        if self.clicked:
            self.md_bg_color=self.t_color
            if self.idx not in self.add_to:
                self.add_to.append(self.idx)
        else:
            self.md_bg_color=self.color
            if self.idx in self.add_to:
                self.add_to.remove(self.idx)
    def get_res(self) -> list:
        return self.add_to
__all__=['FillBtn']
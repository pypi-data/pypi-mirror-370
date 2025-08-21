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
qu=queue.Queue()
class FillButton(MDRaisedButton):
    def __init__(self, txt="1", color=GREY4, t_color=BLUE13, size=(0.1, 0.1),
                 pos=(0.25, 0.55), idx:int=0, add_to:list=None, **kwargs):
        super().__init__(**kwargs)
        if add_to is None:
            add_to = []
        self.idx:int=check_type(idx,int,0)
        self.add_to:list=check_type(add_to,list,[])
        self.text=str(txt)
        color=check_type(color,"c",GREY4)
        t_color=check_type(t_color,"c",BLUE13)
        size=check_type(size,tuple,(0.1,0.1))
        pos=check_type(pos,(list,tuple),(0.25,0.55))
        self.color=color
        self.md_bg_color=self.color
        self.size_hint=size
        self.pos_hint={"center_x":pos[0],
                       "center_y":pos[1]}
        self.t_color=t_color
        self.clicked=False
        self.current_value : Optional[int] = None
    def on_press(self):
        self.clicked = not self.clicked
        if self.clicked:
            self.md_bg_color=self.t_color
            if self.idx not in self.add_to:
                self.add_to.append(self.idx)
            self.current_value=self.idx
        else:
            self.md_bg_color=self.color
            if self.idx in self.add_to:
                self.add_to.remove(self.idx)
            self.current_value=None
    def get_return(self) -> list:
        return self.add_to
__all__=['FillButton']
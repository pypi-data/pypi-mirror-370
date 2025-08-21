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
class ImgFillBtn(MDRaisedButton):
    def __init__(self, img1="images/dino.png", img2="images/gold.png",
                 size=(0.05,0.05), pos=(0.5,0.5), img:Image=None, add_to=None,idx=0, **kwargs):
        super().__init__(**kwargs)
        if add_to is None:
            add_to = []
        self.img2 = img2
        self.img1 = img1
        self.size_hint=size
        self.pos_hint={"center_x":pos[0],
                       "center_y":pos[1]}
        self.img = img
        self.img.source=img1
        self.opacity=0
        self.clicked=False
        self.add_to=add_to
        self.img.size_hint=size
        self.img.opacity=1
        self.img.pos_hint={"center_x":pos[0],
                           "center_y":pos[1]}
        self.img.keep_ratio=False
        self.img.allow_stretch=True
        self.idx=idx
    def on_press(self):
        super().on_press()
        self.clicked=not self.clicked
        if self.clicked:
            self.img.source=self.img2
            if self.idx not in self.add_to:
                self.add_to.append(self.idx)
        else:
            self.img.source=self.img1
            if self.idx in self.add_to:
                self.add_to.remove(self.idx)
    def get_fill_return(self) -> list:
        return self.add_to
__all__=['ImgFillBtn']
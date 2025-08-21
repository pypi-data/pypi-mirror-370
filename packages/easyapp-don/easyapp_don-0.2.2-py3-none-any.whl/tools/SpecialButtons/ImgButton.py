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
class ImgBtn(MDRaisedButton):
    def __init__(self,img="images/easyapp_don.png",size=(0.15,0.05),pos=(0.5,0.05),
                 press=None,o=1,**kwargs):
        super().__init__(**kwargs)
        self.size_hint=size
        self.pos_hint={"center_x":pos[0],
                       "center_y":pos[1]}
        self.image=MDFloatLayout()
        self.o=o
        self.press=press
        i=Image(source=img,
                allow_stretch=True,
                keep_ratio=False,
                size_hint=size,
                pos_hint={"center_x":pos[0],
                          "center_y":pos[1]},
                opacity=self.o)
        self.image.add_widget(i)
    def on_press(self):
        super().on_press()
        self.opacity=0.6
        if self.press is not None:
            self.press(self)
    def on_release(self):
        self.opacity=1
        super().on_release()
__all__=['ImgBtn']
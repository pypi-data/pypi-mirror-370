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
class BtnImgApp(MDApp):
    def __init__(self, ts=None, tip=None, tie="BtnImgEasyapp_don", theme=LIGHT, color=WHITE12,ok=None, cal=None,i=None, bi=None,**kwargs):
        super().__init__(**kwargs)
        if bi is None:
            bi = [["images/sky.png", (0.15, 0.1), (0.3, 0.2), 0.65],
                  ["images/four_d.png", (0.15, 0.1), (0.7, 0.2), 0.65]]
        if i is None:
            i = [["images/easyapp_don.png", (1, 1), (0.5, 0.5), 0.6]]
        if cal is None:
            cal = ["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True]
        if ok is None:
            ok = ["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True]
        if tip is None:
            tip = {"txt": "Close app?",
                   "tie": "Tip",
                   "ok": ["Yes", GREY4],
                   "cal": ["No", BLUE8]}
        if ts is None:
            ts = [["Hello,easyapp_don!", (0.5, 0.95)],
                  ["Text1", (0.5, 0.5)],
                  ["Text2", (0.5, 0.4)],
                  ["Text3", (0.5, 0.3)],
                  ["1/1", (0.5, 0.05)]]
        self.ts=fill_ts(ts)
        self.tip=fill_tip(tip)
        self.ok=check_type(ok,list,["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True])
        self.cal=check_type(cal,list,["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True])
        self.bi=fill_bi(bi)
        self.i=fill_i(i)
        self.title=str(tie)
        self.theme_cls.theme_style=check_type(theme,"t")
        self.color=check_type(color,"c",WHITE12)
    def build(self):
        Window.bind(on_request_close=self.on_close)
        self.root=MDFloatLayout()
        self.root.md_bg_color=self.color
        if self.i:
            for ii in self.i:
                i_path=ii[0]
                i_size=ii[1]
                i_pos=ii[2]
                i_o=ii[3]
                iii=Image(source=i_path,
                          size_hint=i_size,
                          pos_hint={"center_x":i_pos[0],
                                    "center_y":i_pos[1]},
                          allow_stretch=True,
                          keep_ratio=False,
                          opacity=i_o)
                self.root.add_widget(iii)
        if self.ok:
            ok_txt=str(self.ok[0])
            ok_color=self.ok[1] if len(self.ok)>1 else BLUE8
            ok_size=self.ok[2] if len(self.ok)>2 else (0.15,0.05)
            ok_pos=self.ok[3] if len(self.ok)>3 else (0.1,0.1)
            ok_is_close=self.ok[4] if len(self.ok)>4 else True
            if ok_is_close:
                ok=MDRaisedButton(text=ok_txt,
                                  size_hint=ok_size,
                                  pos_hint={"center_x":ok_pos[0],
                                            "center_y":ok_pos[1]},
                                  md_bg_color=ok_color,
                                  on_press=self.on_ok)
                self.root.add_widget(ok)
            else:
                ok = MDRaisedButton(text=ok_txt,
                                    size_hint=ok_size,
                                    pos_hint={"center_x": ok_pos[0],
                                              "center_y": ok_pos[1]},
                                    md_bg_color=ok_color,
                                    on_press=self.on_space)
                self.root.add_widget(ok)
        if self.cal:
            cal_txt=str(self.cal[0])
            cal_color=self.cal[1] if len(self.cal)>1 else GREY13
            cal_size=self.cal[2] if len(self.cal)>2 else (0.15,0.05)
            cal_pos=self.cal[3] if len(self.cal)>3 else (0.9,0.1)
            cal_is_close=self.cal[4] if len(self.cal)>4 else True
            if cal_is_close:
                cal=MDRaisedButton(text=cal_txt,
                                   pos_hint={"center_x":cal_pos[0],
                                             "center_y":cal_pos[1]},
                                   size_hint=cal_size,
                                   md_bg_color=cal_color,
                                   on_press=self.on_cal)
                self.root.add_widget(cal)
            else:
                cal = MDRaisedButton(text=cal_txt,
                                     pos_hint={"center_x": cal_pos[0],
                                               "center_y": cal_pos[1]},
                                     size_hint=cal_size,
                                     md_bg_color=cal_color,
                                     on_press=self.on_space)
                self.root.add_widget(cal)
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
        if self.bi:
            for bi_idx,bi_config in enumerate(self.bi):
                bi_path=bi_config[0]
                bi_size=bi_config[1]
                bi_pos=bi_config[2]
                bi_o=bi_config[3]
                bi=MDRaisedButton(text="",
                                  size_hint=bi_size,
                                  pos_hint={"center_x":bi_pos[0],
                                            "center_y":bi_pos[1]},
                                  opacity=0,
                                  on_press=lambda instance,idx=bi_idx:self.on_bi(idx),
                                  md_bg_color=PINK6)
                self.root.add_widget(bi)
                bi_p=Image(source=bi_path,
                           size_hint=bi_size,
                           pos_hint={"center_x":bi_pos[0],
                                     "center_y":bi_pos[1]},
                           allow_stretch=True,
                           keep_ratio=False,
                           opacity=bi_o)
                self.root.add_widget(bi_p)
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
            qu.put(None)
            self.stop()
            return True
    def on_ok(self,instance):
        qu.put(True)
        self.stop()
    def on_cal(self,instance):
        qu.put(False)
        self.stop()
    def on_space(self,instance):
        pass
    def on_bi(self,bi_idx):
        qu.put(bi_idx)
        self.stop()
def btn_img(ts=None, tip=None, tie="BtnImgEasyapp_don", theme=LIGHT,
            color=WHITE12,ok=None, cal=None,i=None, bi=None) -> Union[bool,int,None]:
    """
        Creates an application interface with images, text, standard buttons, and image-based buttons.
        This function initializes a graphical interface that can display background images, text labels,
        OK/Cancel buttons, and interactive image buttons. User interactions with these elements return
        specific values to indicate the action taken.

        :param ts: List of text elements to display. Each element is a list in format:
                   [["Text content", (center_x, center_y)], ...]
                   - "Text content": String to display
                   - (center_x, center_y): Position coordinates (0-1 range relative to window)
                   Defaults to a predefined list of sample texts if None.

        :param tip: Configuration for the close confirmation dialog (dictionary with keys):
                    {
                        "txt": Dialog message text,
                        "tie": Dialog title,
                        "ok": [OK button text, button color],
                        "cal": [Cancel button text, button color]
                    }
                    If set to empty dict {}, no confirmation dialog appears when closing the app.
                    Defaults to a predefined close dialog if None.

        :param tie: Title of the application window.
                    Defaults to "BtnImgEasyapp_don".

        :param theme: Application theme style (LIGHT or DARK).
                      Defaults to LIGHT.

        :param color: Background color of the main window in RGB/RGBA format.
                      Defaults to WHITE12.

        :param ok: Configuration for the OK button (list in format):
                   [button_text, bg_color, (size_hint_x, size_hint_y), (center_x, center_y), is_close]
                   - button_text: String displayed on the button
                   - bg_color: Background color in RGB/RGBA format
                   - (size_hint_x, size_hint_y): Button size relative to window
                   - (center_x, center_y): Button position coordinates
                   - is_close: Boolean indicating if clicking closes the app
                   Defaults to ["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True] if None.

        :param cal: Configuration for the Cancel button (same format as `ok` parameter):
                    [button_text, bg_color, (size_hint_x, size_hint_y), (center_x, center_y), is_close]
                    Defaults to ["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True] if None.

        :param i: List of background images to display. Each element is a list in format:
                  [["image_path.png", (size_hint_x, size_hint_y), (center_x, center_y), opacity], ...]
                  - "image_path.png": Path to the image file
                  - (size_hint_x, size_hint_y): Image size relative to window
                  - (center_x, center_y): Image position coordinates
                  - opacity: Transparency level (0.0-1.0)
                  Defaults to displaying a sample background image if None.

        :param bi: List of image-based buttons (interactive images). Each element is a list in format:
                   [["image_path.png", (size_hint_x, size_hint_y), (center_x, center_y), opacity], ...]
                   - "image_path.png": Path to the button image file
                   - (size_hint_x, size_hint_y): Button size relative to window
                   - (center_x, center_y): Button position coordinates
                   - opacity: Transparency level (0.0-1.0)
                   Defaults to two sample image buttons if None.

        :return:
                 - True: If the OK button is pressed
                 - False: If the Cancel button is pressed
                 - int: Index of the image button (from `bi` list) that was pressed
                 - None: If the app is closed directly and `tip` is set to empty dict {}
    """
    app=BtnImgApp(ts,tip,tie,theme,color,ok,cal,i,bi)
    app.run()
    return qu.get()
__all__=['btn_img']
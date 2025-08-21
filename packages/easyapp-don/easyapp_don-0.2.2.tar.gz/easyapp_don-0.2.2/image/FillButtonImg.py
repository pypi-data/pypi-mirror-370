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
class FillBtnImgApp(MDApp):
    def __init__(self, ts=None, tip=None, color=WHITE2, theme=LIGHT, tie="FillBtnImgEasyapp_don",
                 ok=None, cal=None,i=None,fs=None,bi=None,fi=None, **kwargs):
        super().__init__(**kwargs)
        if fi is None:
            fi = [["images/dinos.png", "images/gold.png", (0.05, 0.05), (0.75, 0.65)],
                  ["images/dinos.png", "images/four_d.png", (0.05, 0.05), (0.75, 0.45)]]
        if bi is None:
            bi = [["images/sky.png", (0.15, 0.1), (0.3, 0.2), 0.9],
                  ["images/four_d.png", (0.15, 0.1), (0.7, 0.2), 0.9]]
        if fs is None:
            fs = [["a(0)", GREY4, RED8, (0.05, 0.05), (0.25, 0.75)],
                  ["b(1)", GREY4, GREEN4, (0.05, 0.05), (0.25, 0.55)],
                  ["c(2)", GREY4, BLUE8, (0.05, 0.05), (0.25, 0.35)]]
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
                  ["Text a", (0.5, 0.75)],
                  ["Text b", (0.5, 0.55)],
                  ["Text c", (0.5, 0.35)]]
        self.ts=fill_ts(ts)
        self.tip=fill_tip(tip)
        self.ok=check_type(ok,list,["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True])
        self.cal=check_type(cal,list,["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True])
        self.i=fill_i(i)
        self.fs=fill_fs(fs)
        self.bi=fill_bi(bi)
        self.fi=fill_fi(fi)
        self.color=check_type(color,"c",WHITE12)
        self.theme_cls.theme_style=check_type(theme,"t")
        self.title=str(tie)
        self.res=[]
        self.f_s=[]
        self.f_add_to=[]
        self.f_i_s=[]
        self.fi_add_to=[]
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
                i=Image(source=i_path,
                        size_hint=i_size,
                        pos_hint={"center_x":i_pos[0],
                                  "center_y":i_pos[1]},
                        allow_stretch=True,
                        keep_ratio=False,
                        opacity=i_o)
                self.root.add_widget(i)
        if self.ok:
            ok_txt=self.ok[0]
            ok_color=self.ok[1] if len(self.ok)>1 else BLUE8
            ok_size=self.ok[2] if len(self.ok)>2 else (0.1,0.05)
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
            cal_txt = str(self.cal[0])
            cal_color = self.cal[1] if len(self.cal) > 1 else GREY13
            cal_size = self.cal[2] if len(self.cal) > 2 else (0.15, 0.05)
            cal_pos = self.cal[3] if len(self.cal) > 3 else (0.9, 0.1)
            cal_is_close = self.cal[4] if len(self.cal) > 4 else True
            if cal_is_close:
                cal = MDRaisedButton(text=cal_txt,
                                     pos_hint={"center_x": cal_pos[0],
                                               "center_y": cal_pos[1]},
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
                bi_img=Image(source=bi_path,
                             size_hint=bi_size,
                             allow_stretch=True,
                             keep_ratio=False,
                             pos_hint={"center_x":bi_pos[0],
                                       "center_y":bi_pos[1]},
                             opacity=bi_o)
                self.root.add_widget(bi_img)
                bi=MDRaisedButton(text="",
                                  pos_hint={"center_x":bi_pos[0],
                                            "center_y":bi_pos[1]},
                                  size_hint=bi_size,
                                  opacity=0,
                                  on_press=lambda instance,idx=bi_idx:self.on_bi(idx))
                self.root.add_widget(bi)
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
                self.root.add_widget(f)
                self.f_s.append(f)
        if self.fi:
            for fi_idx,fi_config in enumerate(self.fi):
                fi_path=fi_config[0]
                fi_t_path=fi_config[1]
                fi_size=fi_config[2]
                fi_pos=fi_config[3]
                fi_img=Image(source=fi_path,
                             allow_stretch=True,
                             keep_ratio=False,
                             size_hint=fi_size,
                             pos_hint={"center_x":fi_pos[0],
                                       "center_y":fi_pos[1]},
                             opacity=1)
                self.root.add_widget(fi_img)
                fi=ImgFillBtn(img1=fi_path,
                              img2=fi_t_path,
                              size=fi_size,
                              pos=fi_pos,
                              img=fi_img,
                              add_to=self.fi_add_to,
                              idx=fi_idx)
                self.root.add_widget(fi)
                self.f_i_s.append(fi)
        return self.root
    def on_close(self,window,*args):
        if self.tip:
            txt=self.tip["txt"]
            tie=self.tip["tie"]
            ok=self.tip["ok"]
            cal=self.tip["cal"]
            dialog(txt.tie, ok, cal)
            return True
        else:
            for fs in self.f_s:
                self.f_add_to=fs.get_return()
            for fi_s in self.f_i_s:
                self.fi_add_to=fi_s.get_fill_return()
            self.res=[None,self.f_add_to,self.fi_add_to]
            qu.put(self.res)
            self.stop()
            return True
    def on_ok(self,instance):
        for fs in self.f_s:
            self.f_add_to = fs.get_return()
        for fi_s in self.f_i_s:
            self.fi_add_to = fi_s.get_fill_return()
        self.res = [True, self.f_add_to, self.fi_add_to]
        qu.put(self.res)
        self.stop()
    def on_cal(self,instance):
        for fs in self.f_s:
            self.f_add_to = fs.get_return()
        for fi_s in self.f_i_s:
            self.fi_add_to = fi_s.get_fill_return()
        self.res = [False, self.f_add_to, self.fi_add_to]
        qu.put(self.res)
        self.stop()
    def on_space(self,instance):
        pass
    def on_bi(self,bi_idx):
        for fs in self.f_s:
            self.f_add_to = fs.get_return()
        for fi_s in self.f_i_s:
            self.fi_add_to = fi_s.get_fill_return()
        self.res = [bi_idx, self.f_add_to, self.fi_add_to]
        qu.put(self.res)
        self.stop()
def fill_btn_img(ts=None, tip=None, color=WHITE2, theme=LIGHT, tie="FillBtnImgEasyapp_don",
                 ok=None, cal=None,i=None,fs=None,bi=None,fi=None) -> list:
    """
        A function to launch a KivyMD-based application with customizable UI elements, including text labels,
        buttons, image buttons, and interactive widgets. The application captures user interactions (e.g., button clicks)
        and returns the results after closure.

        Detailed Description:
        This function initializes a `FillBtnImgApp` instance, which builds a graphical user interface (GUI) using KivyMD components.
        The UI can be customized via parameters to include text labels, confirmation dialogs, background colors, themes,
        standard buttons, image buttons, and fillable buttons. User interactions with these elements are tracked, and the results
        (e.g., which button was clicked, state of fillable widgets) are returned as a list after the app is closed.

        :param ts: Configuration for text labels. Each sublist defines a text label's content and position.
            - Structure: List of sublists, where each sublist is `[text_content, (center_x, center_y)]`
                - `text_content` (str): Text to display in the label.
                - `(center_x, center_y)` (tuple of floats): Position hint (0-1 range) relative to the screen.
            - Default: `[["Hello,easyapp_don!", (0.5, 0.95)], ["Text a", (0.5, 0.75)], ["Text b", (0.5, 0.55)], ["Text c", (0.5, 0.35)]]`
        :type ts: Optional[List[List[Union[str, Tuple[float, float]]]]]

        :param tip: Configuration for the confirmation dialog shown when closing the app.
            - Structure: Dictionary with keys:
                - `txt` (str): Message displayed in the dialog.
                - `tie` (str): Title of the dialog.
                - `ok` (list): `[button_text, button_color]` for the "OK" dialog button.
                - `cal` (list): `[button_text, button_color]` for the "Cancel" dialog button.
            - Default: `{"txt": "Close app?", "tie": "Tip", "ok": ["Yes", GREY4], "cal": ["No", BLUE8]}`
        :type tip: Optional[Dict[str, Union[str, List[Union[str, Tuple[float, float]]]]]

        :param color: Background color of the app screen. Uses color constants from `easyapp_don.tools.colors`.
            - Default: `WHITE2`
        :type color: Optional[str]

        :param theme: App theme style (`LIGHT` or `DARK`). Uses theme constants from `easyapp_don.tools.Manner`.
            - Default: `LIGHT`
        :type theme: Optional[str]

        :param tie: Title of the app window.
            - Default: `"FillBtnImgEasyapp_don"`
        :type tie: Optional[str]

        :param ok: Configuration for the "OK" button.
            - Structure: List `[text, color, size_hint, pos_hint, is_close]`
                - `text` (str): Button text.
                - `color` (str): Button background color (from `easyapp_don.tools.colors`).
                - `size_hint` (tuple): `(width_ratio, height_ratio)` (0-1 range).
                - `pos_hint` (tuple): `(center_x, center_y)` position hint.
                - `is_close` (bool): If `True`, clicking closes the app.
            - Default: `["Ok", BLUE8, (0.1, 0.05), (0.1, 0.1), True]`
        :type ok: Optional[List[Union[str, Tuple[float, float], bool]]]

        :param cal: Configuration for the "Cancel" button (similar structure to `ok`).
            - Default: `["Cancel", GREY4, (0.1, 0.05), (0.9, 0.1), True]`
        :type cal: Optional[List[Union[str, Tuple[float, float], bool]]]

        :param i: Configuration for static images displayed in the app.
            - Structure: List of sublists `[image_path, size_hint, pos_hint, opacity]`
                - `image_path` (str): Path to the image file.
                - `size_hint` (tuple): `(width_ratio, height_ratio)` (0-1 range).
                - `pos_hint` (tuple): `(center_x, center_y)` position hint.
                - `opacity` (float): Transparency (0.0-1.0 range).
            - Default: `[["images/easyapp_don.png", (1, 1), (0.5, 0.5), 0.6]]`
        :type i: Optional[List[List[Union[str, Tuple[float, float], float]]]]

        :param fs: Configuration for fillable text buttons (`FillButton` widgets).
            - Structure: List of sublists `[text, bg_color, text_color, size_hint, pos_hint]`
                - `text` (str): Button text.
                - `bg_color` (str): Background color.
                - `text_color` (str): Text color.
                - `size_hint` (tuple): `(width_ratio, height_ratio)`.
                - `pos_hint` (tuple): `(center_x, center_y)` position hint.
            - Default: `[["a(0)", GREY4, RED8, (0.05, 0.05), (0.25, 0.75)], ...]`
        :type fs: Optional[List[List[Union[str, Tuple[float, float]]]]]

        :param bi: Configuration for background image buttons (clickable images with transparent overlay buttons).
            - Structure: List of sublists `[image_path, size_hint, pos_hint, opacity]`
                - `image_path` (str): Path to the background image.
                - `size_hint` (tuple): `(width_ratio, height_ratio)`.
                - `pos_hint` (tuple): `(center_x, center_y)` position hint.
                - `opacity` (float): Image transparency.
            - Default: `[["images/sky.png", (0.15, 0.1), (0.3, 0.2), 0.9], ...]`
        :type bi: Optional[List[List[Union[str, Tuple[float, float], float]]]]

        :param fi: Configuration for image fill buttons (`ImgFillBtn` widgets with toggleable images).
            - Structure: List of sublists `[image1_path, image2_path, size_hint, pos_hint]`
                - `image1_path` (str): Path to the default image.
                - `image2_path` (str): Path to the toggled image.
                - `size_hint` (tuple): `(width_ratio, height_ratio)`.
                - `pos_hint` (tuple): `(center_x, center_y)` position hint.
            - Default: `[["images/dinos.png", "images/gold.png", (0.05, 0.05), (0.75, 0.65)], ...]`
        :type fi: Optional[List[List[Union[str, Tuple[float, float]]]]]

        :example:
            >>> # Example: Launch app with custom text and buttons
            >>> from easy_app.tools.colors import BLUE8, GREY4
            >>> result = fill_btn_img(
            ...     ts=[["Custom Title", (0.5, 0.9)], ["Welcome!", (0.5, 0.8)]],
            ...     ok=["Submit", BLUE8, (0.2, 0.07), (0.3, 0.1), True],
            ...     cal=["Abort", GREY4, (0.2, 0.07), (0.7, 0.1), True],
            ...     theme="DARK"
            ... )
            >>> print("User action result:", result)
            >>>print("Demo end.")# Output: [True, fill_button_states, image_button_states]

        :return: A list containing interaction results:
            - `result[0]`: State indicator (True if OK clicked, False if Cancel clicked, int index if background image button clicked).
            - `result[1]`: Index of fillable buttons (`fs`).
            - `result[2]`: Index of image fill buttons (`fi`).
        :rtype: list
        """
    app=FillBtnImgApp(ts,tip,color,theme,tie,ok,cal,i,fs,bi,fi)
    app.run()
    return qu.get()
__all__=['fill_btn_img']
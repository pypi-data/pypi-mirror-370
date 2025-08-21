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
class OnePageApp(MDApp):
    def __init__(self, ts=None, tip=None, color=WHITE12, theme=LIGHT, tie="OnePageEasyapp_don",
                 i=None, bi=None,fi=None,es=None, bs=None,fs=None, **kwargs):
        super().__init__(**kwargs)
        if fs is None:
            fs = [["a(0)", GREY4, RED1, (0.05, 0.05), (0.1, 0.8)],
                  ["b(1)", GREY4, GREEN4, (0.05, 0.05), (0.5, 0.8)],
                  ["c(2)", GREY4, BLUE8, (0.05, 0.05), (0.9, 0.8)]]
        if bs is None:
            bs = [["Button0", RED8, (0.1, 0.05), (0.1, 0.05)],
                  ["Button1", GREEN6, (0.1, 0.05), (0.5, 0.05)],
                  ["Button2", BLUE8, (0.1, 0.05), (0.9, 0.05)]]
        if es is None:
            es = [["Enter1", (0.2, 0.05), (0.15, 0.5)],
                  ["Enter2", (0.2, 0.05), (0.5, 0.5)],
                  ["Enter3", (0.2, 0.05), (0.85, 0.5)]]
        if fi is None:
            fi = [["images/dinos.png", "images/gold.png", (0.05, 0.05), (0.1, 0.7)],
                  ["images/dinos.png", "images/sky.png", (0.05, 0.05), (0.5, 0.7)],
                  ["images/dinos.png", "images/eto.png", (0.05, 0.05), (0.9, 0.7)]]
        if bi is None:
            bi = [["images/sky.png", (0.15, 0.1), (0.15, 0.3), 0.9, True],
                  ["images/four_d.png", (0.15, 0.1), (0.5, 0.3), 0.9, True],
                  ["images/eto.png", (0.15, 0.1), (0.85, 0.3), 0.9, True]]
        if i is None:
            i = [["images/easyapp_don.png", (1, 1), (0.5, 0.5), 0.6]]
        if tip is None:
            tip = {"txt": "Close app?",
                   "tie": "Tip",
                   "ok": ["Yes", GREY4],
                   "cal": ["No", BLUE8]}
        if ts is None:
            ts = [["Hello,easyapp_don!", (0.5, 0.95)],
                  ["Text1", (0.1, 0.6)],
                  ["Text2", (0.5, 0.6)],
                  ["Text3", (0.9, 0.6)]]
        self.title=str(tie)
        self.theme_cls.theme_style=check_type(theme,"t")
        self.color=check_type(color,"c",WHITE12)
        self.bs=fill_bs_page(bs)
        self.fs=fill_fs(fs)
        self.i=fill_i(i)
        self.es=fill_es(es)
        self.ts=fill_ts(ts)
        self.tip=fill_tip(tip)
        self.bi=fill_bi_page(bi)
        self.fi=fill_fi(fi)
        self.f_s=[]
        self.f_i_s=[]
        self.inputs=[]
        self.f_add_to=[]
        self.fi_add_to=[]
        self.res=[]
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
                        allow_stretch=True,
                        keep_ratio=False,
                        size_hint=i_size,
                        pos_hint={"center_x":i_pos[0],
                                  "center_y":i_pos[1]},
                        opacity=i_o)
                self.root.add_widget(i)
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
        if self.es:
            for ee in self.es:
                e_txt=ee[0]
                e_size=ee[1]
                e_pos=ee[2]
                e=MDTextFieldRect(hint_text=e_txt,
                                  size_hint=e_size,
                                  pos_hint={"center_x":e_pos[0],
                                            "center_y":e_pos[1]})
                self.root.add_widget(e)
                self.inputs.append(e)
        if self.fs:
            for f_idx,f_config in enumerate(self.fs):
                f_txt=f_config[0]
                f_color=f_config[1]
                f_t_color=f_config[2]
                f_size=f_config[3]
                f_pos=f_config[4]
                f=FillBtn(txt=f_txt,color=f_color,t_color=f_t_color,size=f_size,pos=f_pos,
                          idx=f_idx,add_to=self.f_add_to)
                self.root.add_widget(f)
                self.f_s.append(f)
        if self.fi:
            for fi_idx,fi_config in enumerate(self.fi):
                fi_img1=fi_config[0]
                fi_img2=fi_config[1]
                fi_size=fi_config[2]
                fi_pos=fi_config[3]
                fi_img=Image(source=fi_img1,
                             allow_stretch=True,
                             keep_ratio=False,
                             size_hint=fi_size,
                             pos_hint={"center_x":fi_pos[0],
                                       "center_y":fi_pos[1]},
                             opacity=1)
                fi=FillImgBtn(img1=fi_img1,img2=fi_img2,
                              img=fi_img,size=fi_size,
                              pos=fi_pos,idx=fi_idx,add_to=self.fi_add_to)
                self.root.add_widget(fi_img)
                self.root.add_widget(fi)
                self.f_i_s.append(fi)
        if self.bs:
            for b_idx,b_config in enumerate(self.bs):
                b_txt=b_config[0]
                b_color=b_config[1]
                b_size=b_config[2]
                b_pos=b_config[3]
                b=MDRaisedButton(text=b_txt,
                                 pos_hint={"center_x":b_pos[0],
                                           "center_y":b_pos[1]},
                                 size_hint=b_size,
                                 md_bg_color=b_color,
                                 on_press=lambda instance,idx=b_idx:self.on_btn(idx))
                self.root.add_widget(b)
        if self.bi:
            for bi_idx,bi_config in enumerate(self.bi,start=len(self.bs)):
                bi_path=bi_config[0]
                bi_size=bi_config[1]
                bi_pos=bi_config[2]
                bi_o=bi_config[3]
                bi_is_close=bi_config[4]
                if bi_is_close:
                    bi_img=Image(source=bi_path,
                                 allow_stretch=True,
                                 keep_ratio=False,
                                 pos_hint={"center_x":bi_pos[0],
                                           "center_y":bi_pos[1]},
                                 size_hint=bi_size,
                                 opacity=bi_o)
                    self.root.add_widget(bi_img)
                    bi=MDRaisedButton(text="",
                                      size_hint=bi_size,
                                      pos_hint={"center_x":bi_pos[0],
                                                "center_y":bi_pos[1]},
                                      opacity=0,
                                      on_press=lambda instance,idx=bi_idx:self.on_bi(idx))
                    self.root.add_widget(bi)
                else:
                    bi_img = Image(source=bi_path,
                                   allow_stretch=True,
                                   keep_ratio=False,
                                   pos_hint={"center_x": bi_pos[0],
                                             "center_y": bi_pos[1]},
                                   size_hint=bi_size,
                                   opacity=bi_o)
                    self.root.add_widget(bi_img)
                    bi = MDRaisedButton(text="",
                                        size_hint=bi_size,
                                        pos_hint={"center_x": bi_pos[0],
                                                  "center_y": bi_pos[1]},
                                        opacity=0,
                                        on_press=self.on_space)
                    self.root.add_widget(bi)
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
            inputs=[e.text for e in self.inputs]
            for f_config in self.f_s:
                self.f_add_to=f_config.get_res()
            for fi_config in self.f_i_s:
                self.fi_add_to=fi_config.get_rec()
            self.res=[None,inputs,self.f_add_to,self.fi_add_to]
            qu.put(self.res)
            self.stop()
            return True
    def on_space(self,instance):
        pass
    def on_btn(self,btn_idx):
        inputs=[e.text for e in self.inputs]
        for f_c in self.f_s:
            self.f_add_to=f_c.get_res()
        for fi_c in self.f_i_s:
            self.fi_add_to=fi_c.get_rec()
        self.res=[btn_idx,inputs,self.f_add_to,self.fi_add_to]
        qu.put(self.res)
        self.stop()
    def on_bi(self,bi_idx):
        inputs=[e.text for e in self.inputs]
        for f_c in self.f_s:
            self.f_add_to=f_c.get_res()
        for f_i_c in self.f_i_s:
            self.fi_add_to=f_i_c.get_rec()
        self.res=[bi_idx,inputs,self.f_add_to,self.fi_add_to]
        qu.put(self.res)
        self.stop()
def page(ts=None, tip=None, color=WHITE12, theme=LIGHT, tie="OnePageEasyapp_don",
         i=None, bi=None,fi=None,es=None, bs=None,fs=None):
    """
        Creates a customizable single-page interactive application using KivyMD, with configurable UI elements,
        and returns structured data about user interactions (clicks, inputs, and toggle states).

        This function abstracts the complexity of building a KivyMD app by allowing you to define UI components
        through simple parameter configurations. It runs the app, waits for user interaction (button clicks or app closure),
        then returns a detailed list of interaction results.

        KeyNotes:
        - The `theme` parameter values (`LIGHT`/`DARK`) can be imported from `easyapp_don.tools.colors`.
        - All color parameters (e.g., button colors, background color) should be imported from `easyapp_don.tools.colors`
          (no need to define custom RGBA tuples). Color variable names end with a number indicating shade depth
          (e.g., `RED1` = light red, `RED8` = dark red; `GREY4` = medium grey).

        :param ts: Configuration for text labels. Each element is a sublist with format:
            `["text_content", (center_x, center_y)]`
            - `text_content`: String text to display
            - `(center_x, center_y)`: Position on the page (0-1 range, (0.5, 0.5) is center)
            Example:
            ```python
            ts = [
                ["Welcome to My App", (0.5, 0.95)],  # Title at top-center
                ["Enter details below", (0.5, 0.85)]  # Subtitle below title
            ]
            ```
            Defaults to predefined text elements if None.

        :param tip: Configuration for the confirmation dialog when closing the app. Dictionary with keys:
            - `"txt"`: Dialog message (string)
            - `"tie"`: Dialog title (string)
            - `"ok"`: Sublist for confirm button: `["button_text", button_color]`
            - `"cal"`: Sublist for cancel button: `["button_text", button_color]`
            Example:
            ```python
            tip = {
                "txt": "Are you sure you want to exit?",
                "tie": "Exit Confirmation",
                "ok": ["Yes, Exit", RED6],
                "cal": ["Cancel", GREY4]
            }
            ```
            Defaults to a close confirmation dialog if None.

        :param color: Page background color. Should be a color variable from `easyapp_don.tools.colors`
            Example: `color = GREY2` (light grey background)
            Defaults to WHITE12.

        :param theme: App theme style (light or dark mode). Import `LIGHT` or `DARK` from `easyapp_don.tools.colors`
            Example:
            ```python
            from easyapp_don.tools.colors import DARK
            theme = DARK  # Uses dark mode theme
            ```
            Defaults to LIGHT.

        :param tie: Title of the application window (string)
            Example: `tie = "My Shopping List App"`
            Defaults to "OnePageEasyapp_don".

        :param i: Configuration for static (non-interactive) images. Each element is a sublist with format:
            `["image_path", (size_hint_x, size_hint_y), (center_x, center_y), opacity]`
            - `image_path`: Path to image file (e.g., `"images/logo.png"`)
            - `(size_hint_x, size_hint_y)`: Image size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            - `opacity`: Transparency (0 = fully transparent, 1 = fully opaque)
            Example:
            ```python
            i = [
                ["images/logo.png", (0.3, 0.2), (0.5, 0.7), 0.9],  # Semi-transparent logo
            ]
            ```
            Defaults to a predefined image if None.

        :param bi: Configuration for image-based buttons. These buttons have indices starting after the last index of `bs` buttons.
            Each element is a sublist with format:
            `["image_path", (size_hint_x, size_hint_y), (center_x, center_y), opacity, is_close_button]`
            - `image_path`: Path to button's image (e.g., `"images/settings.png"`)
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            - `opacity`: Image transparency (0-1 range)
            - `is_close_button`: Boolean indicating if clicking triggers app closure
            Example:
            ```python
            bi = [
                ["images/home_btn.png", (0.1, 0.1), (0.2, 0.3), 1.0, True],
            ]
            ```
            Defaults to predefined image buttons if None.

        :param fi: Configuration for image toggle buttons (toggle between two images). Each element is a sublist with format:
            `["image1_path", "image2_path", (size_hint_x, size_hint_y), (center_x, center_y)]`
            - `image1_path`: Default image path (e.g., `"images/unchecked.png"`)
            - `image2_path`: Toggled image path (e.g., `"images/checked.png"`)
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            Example:
            ```python
            fi = [
                ["images/off.png", "images/on.png", (0.08, 0.08), (0.3, 0.6)],
            ]
            ```
            Defaults to predefined image fill buttons if None.

        :param es: Configuration for text input fields. Each element is a sublist with format:
            `["hint_text", (size_hint_x, size_hint_y), (center_x, center_y)]`
            - `hint_text`: Gray placeholder text (e.g., "Enter your name")
            - `(size_hint_x, size_hint_y)`: Input field size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            Example:
            ```python
            es = [
                ["Username", (0.3, 0.05), (0.5, 0.6)],
                ["Age", (0.15, 0.05), (0.5, 0.5)]
            ]
            ```
            Defaults to predefined input fields if None.

        :param bs: Configuration for standard raised buttons. These buttons have indices starting from 0.
            Each element is a sublist with format:
            `["button_text", button_color, (size_hint_x, size_hint_y), (center_x, center_y)]`
            - `button_text`: String displayed on the button (e.g., "Submit")
            - `button_color`: Color from `easyapp_don.tools.colors` (e.g., `GREEN4`)
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            Example:
            ```python
            bs = [
                ["Submit", GREEN4, (0.2, 0.07), (0.3, 0.1)],  # Index 0
                ["Cancel", RED6, (0.2, 0.07), (0.7, 0.1)]     # Index 1
            ]
            ```
            Defaults to predefined buttons if None.

        :param fs: Configuration for color fill toggle buttons (toggle background color). Each element is a sublist with format:
            `["button_text", default_color, fill_color, (size_hint_x, size_hint_y), (center_x, center_y)]`
            - `button_text`: String displayed on the button (e.g., "Option A")
            - `default_color`: Initial background color (from `easyapp_don.tools.colors`)
            - `fill_color`: Toggled background color (from `easyapp_don.tools.colors`)
            - `(size_hint_x, size_hint_y)`: Button size relative to screen (0-1 range)
            - `(center_x, center_y)`: Position on the page (0-1 range)
            Example:
            ```python
            fs = [
                ["Red Team", GREY4, RED3, (0.15, 0.07), (0.25, 0.4)],
            ]
            ```
            Defaults to predefined fill buttons if None.

        :return: A list containing interaction results with structure:
            `[clicked_index, input_values, fs_states, fi_states]`
            - `clicked_index`: Index of clicked button (int) or None (app closed without clicking)
              - For `bs` buttons: Indices start at 0
              - For `bi` buttons: Indices start after last `bs` index
            - `input_values`: List of text values from `es` input fields
            - `fs_indexes`: List of states from `fs` toggle buttons
            - `fi_indexes`: List of states from `fi` image toggle buttons
    """
    app=OnePageApp(ts,tip,color,theme,tie,i,bi,fi,es,bs,fs)
    app.run()
    return qu.get()
__all__=['page']
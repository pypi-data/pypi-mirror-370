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
class ImgBookApp(MDApp):
    def __init__(self, ps=None,**kwargs):
        super().__init__(**kwargs)
        if ps is None:
            ps = i_mode.copy()
        self.ps=img_ps_fill(ps)
        self.p_names=list(self.ps.keys())
        self.this_page_idx=0
        self.this_page_name=self.p_names[self.this_page_idx]
        self.this_page=self.ps[self.this_page_name]
        self.res={}
        self.manager=MDScreenManager()
        for page_name,page_config in self.ps.items():
            es=es_fill(page_config["es"])
            inp=[]
            for _ in es:
                inp.append("")
            self.res[page_name]=[None,inp,[],[]]
        self.build_screens()
    def build(self):
        Window.bind(on_request_close=self.on_close)
        self.theme_cls.theme_style=check_type(self.this_page["theme"],"t")
        self.title=str(self.this_page["tie"])
        self.manager.bind(current=self.on_screen_changed)
        return self.manager
    def on_stop(self):
        if qu.empty():
            qu.put(self.res)
    def on_close(self,window,*args):
        self.save_screen()
        this_screen=self.ps[self.manager.current]
        tip=fill_tip(this_screen["tip"])
        if tip:
            t=tip["txt"]
            tie=tip["tie"]
            ok=tip["ok"]
            cal=tip["cal"]
            dialog(t, tie, ok, cal)
            return True
        else:
            qu.put(self.res)
            self.stop()
            return True
    def on_screen_changed(self,instance,value):
        self.this_page_idx=self.p_names.index(value)
        self.this_page=self.ps[value]
        self.this_page_name=self.p_names[self.this_page_idx]
        self.title=str(self.this_page["tie"])
        self.theme_cls.theme_style=check_type(self.this_page["theme"],"t")
    def save_screen(self):
        this_screen=self.manager.current_screen
        this_screen_name=this_screen.name
        inputs=[]
        f_s=[]
        f_is=[]
        if hasattr(this_screen,"inputs"):
            inputs=[e.text for e in this_screen.inputs]
        if hasattr(this_screen,"f_s"):
            for f in this_screen.f_s:
                f_s=f.get_res()
        if hasattr(this_screen,"f_is"):
            for ff in this_screen.f_is:
                f_is=ff.get_rec()
        self.res[this_screen_name]=[getattr(this_screen,"click",None),inputs,f_s,f_is]
    def go_last(self,page_idx):
        self.save_screen()
        if page_idx>0:
            self.this_page_idx=page_idx-1
            self.manager.current=self.p_names[self.this_page_idx]
    def go_next(self,page_idx):
        self.save_screen()
        if page_idx<len(self.p_names)-1:
            self.this_page_idx=page_idx+1
            self.manager.current=self.p_names[self.this_page_idx]
    def go_home(self,instance=None):
        self.save_screen()
        self.this_page_idx=0
        self.manager.current=self.p_names[self.this_page_idx]
    def build_screens(self):
        for page_idx,page_name in enumerate(self.p_names):
            screen=self.create_screen(page_name, page_idx)
            self.manager.add_widget(screen)
    def create_screen(self,page_name,page_idx):
        screen_config=self.ps[page_name]
        screen=MDScreen(name=page_name)
        screen.md_bg_color=check_type(screen_config["color"],"c",WHITE12)
        screen.page_config=screen_config
        screen.page_idx=page_idx
        screen.inputs=[]
        screen.f_s=[]
        screen.f_is=[]
        screen.f_add_to=[]
        screen.f_i_add_to=[]
        ts=ts_fill(screen_config["ts"])
        fs=fs_fill(screen_config["fs"])
        es=es_fill(screen_config["es"])
        bs=bs_fill(screen_config["bs"])
        i=fill_i(screen_config["i"])
        bi=fill_bi_page(screen_config["bi"])
        fi=fill_fi(screen_config["fi"])
        last=last_fill(screen_config["last"])
        next1=next_fill(screen_config["next"])
        back=back_fill(screen_config["back"])
        inp=[]
        for _ in es:
            inp.append("")
        self.res[page_name]=[None,inp,[],[]]
        if i:
            for ii in i:
                i_path=ii[0]
                i_size=ii[1]
                i_pos=ii[2]
                i_o=ii[3]
                i_img=Image(source=i_path,
                            allow_stretch=True,
                            keep_ratio=False,
                            size_hint=i_size,
                            pos_hint={"center_x":i_pos[0],
                                      "center_y":i_pos[1]},
                            opacity=i_o)
                screen.add_widget(i_img)
        if ts:
            for tt in ts:
                t_txt=tt[0]
                t_pos=tt[1]
                t=MDLabel(text=t_txt,
                          halign="center",
                          valign="middle",
                          pos_hint={"center_x":t_pos[0],
                                    "center_y":t_pos[1]})
                screen.add_widget(t)
        if es:
            for ee in es:
                e_txt=ee[0]
                e_size=ee[1]
                e_pos=ee[2]
                e1=MDTextFieldRect(hint_text=e_txt,
                                   size_hint=e_size,
                                   pos_hint={"center_x":e_pos[0],
                                             "center_y":e_pos[1]})
                screen.add_widget(e1)
                screen.inputs.append(e1)
        if fs:
            for f_idx,f_config in enumerate(fs):
                f_txt=f_config[0]
                f_color=f_config[1]
                f_t_color=f_config[2]
                f_size=f_config[3]
                f_pos=f_config[4]
                f1=FillBtn(f_txt,f_color,f_t_color,f_size,f_pos,f_idx,screen.f_add_to)
                screen.add_widget(f1)
                screen.f_s.append(f1)
        if fi:
            for fi_idx,fi_config in enumerate(fi):
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
                             opacity=0.9)
                screen.add_widget(fi_img)
                fis=FillImgBtn(fi_path,fi_t_path,fi_img,fi_size,fi_pos,fi_idx,screen.f_i_add_to)
                screen.add_widget(fis)
                screen.f_is.append(fis)
        if bs:
            for b_idx,b_config in enumerate(bs):
                b_txt=b_config[0]
                b_color=b_config[1]
                b_size=b_config[2]
                b_pos=b_config[3]
                b=MDRaisedButton(text=b_txt,
                                 size_hint=b_size,
                                 pos_hint={"center_x":b_pos[0],
                                           "center_y":b_pos[1]},
                                 md_bg_color=b_color,
                                 on_press=lambda instance,idx=b_idx:self.on_btn(idx))
                screen.add_widget(b)
        if bi:
            for bi_idx,bi_config in enumerate(bi,start=len(bs)):
                bi_path=bi_config[0]
                bi_size=bi_config[1]
                bi_pos=bi_config[2]
                bi_o=bi_config[3]
                bi_is_close=bi_config[4]
                bi_img=Image(source=bi_path,
                             allow_stretch=True,
                             keep_ratio=False,
                             size_hint=bi_size,
                             pos_hint={"center_x":bi_pos[0],
                                       "center_y":bi_pos[1]},
                             opacity=bi_o)
                screen.add_widget(bi_img)
                if bi_is_close:
                    bis=MDRaisedButton(text="",
                                       size_hint=bi_size,
                                       pos_hint={"center_x":bi_pos[0],
                                                 "center_y":bi_pos[1]},
                                       opacity=0,
                                       on_press=lambda instance,idx=bi_idx:self.on_bi(idx))
                    screen.add_widget(bis)
                else:
                    bis = MDRaisedButton(text="",
                                         size_hint=bi_size,
                                         pos_hint={"center_x": bi_pos[0],
                                                   "center_y": bi_pos[1]},
                                         opacity=0,
                                         on_press=self.on_space)
                    screen.add_widget(bis)
        if last and page_idx>0:
            l_txt=last["txt"]
            l_color=last["color"]
            l_size=last["size"]
            l_pos=last["pos"]
            l_b=MDRaisedButton(text=l_txt,
                               size_hint=l_size,
                               pos_hint={"center_x":l_pos[0],
                                         "center_y":l_pos[1]},
                               md_bg_color=l_color,
                               on_press=lambda instance,idx=page_idx:self.go_last(idx))
            screen.add_widget(l_b)
        if back and page_idx>0:
            ba_txt=back["txt"]
            ba_color=back["color"]
            ba_size=back["size"]
            ba_pos=back["pos"]
            ba=MDRaisedButton(text=ba_txt,
                              size_hint=ba_size,
                              pos_hint={"center_x":ba_pos[0],
                                        "center_y":ba_pos[1]},
                              md_bg_color=ba_color,
                              on_press=self.go_home)
            screen.add_widget(ba)
        if next1 and page_idx<len(self.p_names)-1:
            n_txt=next1["txt"]
            n_color=next1["color"]
            n_size=next1["size"]
            n_pos=next1["pos"]
            n_b=MDRaisedButton(text=n_txt,
                               size_hint=n_size,
                               pos_hint={"center_x":n_pos[0],
                                         "center_y":n_pos[1]},
                               md_bg_color=n_color,
                               on_press=lambda instance,idx=page_idx:self.go_next(idx))
            screen.add_widget(n_b)
        return screen
    def on_btn(self,btn_idx):
        this_screen=self.manager.current_screen
        this_screen.click=btn_idx
        self.save_screen()
        qu.put(self.res)
        self.stop()
    def on_space(self,instance):
        pass
    def on_bi(self,bi_idx):
        this_screen=self.manager.current_screen
        this_screen.click=bi_idx
        self.save_screen()
        qu.put(self.res)
        self.stop()
def img_pages(ps=None):
    """
        Create and run a multipage application with image support, enabling page navigation (previous, next, home),
        user interactions like button clicks, text input, and handling of various UI elements (labels, images, special buttons).
        It is built on top of KivyMD for the UI and provides a simplified way to set up a multipage structure
        compared to directly using lower - level Kivy/KivyMD APIs.

        :param ps: A dictionary that configures multiple aspects of the multipage application.
                   Each key in the dictionary represents a page name (not displayed as the title directly),
                   and the corresponding value is another dictionary with detailed page - specific settings.
                   These settings can include:
                   - "tie": The title of the page, which will be shown in the app's title bar.
                   - "ts": A list for text elements, where each element can be a simple text string (will be centered by default)
                           or a list with text and a (x, y) position tuple (ranging from 0 to 1, relative to the parent container).
                   - "fs": A list for fill buttons, each element can be a simplified form (just text, with other properties like color, size filled with defaults)
                           or a detailed list specifying text, initial color, clicked color, size (as a tuple), and position (as a tuple).
                   - "es": A list for text fields, each element can be a simple hint text (with default size and position)
                           or a detailed list with hint text, size (tuple), and position (tuple).
                   - "bs": A list for action buttons, each element can be a basic setup (text and color, with default size and position)
                           or a detailed list with text, color, size (tuple), and position (tuple). Clicking these buttons can trigger app termination with recorded results.
                   - "i": A list for images, each element can be a simple image path (with default size, position, and opacity)
                           or a detailed list with path, size (tuple), position (tuple), and opacity (float).
                   - "bi": A list for button - linked images, similar to regular images but can be associated with button - like press actions.
                   - "fi": A list for fill - image buttons, combining image display with fill - button - like interaction logic.
                   - "last": Configuration for the "previous page" navigation button, including text, color, size (tuple), and position (tuple).
                             This button is only visible if not on the first page.
                   - "next": Configuration for the "next page" navigation button, including text, color, size (tuple), and position (tuple).
                             This button is only visible if not on the last page.
                   - "back": Configuration for the "home page" navigation button, including text, color, size (tuple), and position (tuple).
                             This button is only visible if not on the first page.
                   - "theme": Specifies the app's theme style, typically using constants like "LIGHT" or "DARK" imported from relevant color/theme modules.
                   - "color": Sets the background color of the page, using color constants (imported from relevant modules) with an optional number suffix to indicate shade.
                   - "tip": A dictionary for the dialog shown when closing the app, which can have:
                           - "txt": The main text content of the dialog.
                           - "tie": The title of the dialog.
                           - "ok": A list for the "OK" button, which can be a simple text (with default color) or a list with text and color.
                           - "cal": A list for the "Cancel" button, similar to the "OK" button. If not needed, can be an empty list.
                   If not provided, it will use a default configuration copied from `i_mode` (assumed to be a predefined template).
        :return: A dictionary that records the interaction results of each page. The structure is:
                 {
                     "page_name": [
                         clicked_button_index_or_none,
                         list_of_input_texts_from_text fields,
                         list_of_fill_button_interactions,
                         list_of_fill_image_button_interactions
                     ]
                 }
                 Here, "page_name" is the key from the input `ps` dictionary, and each value list captures the relevant user interactions on that page.
                 This allows retrieval of what actions the user performed (which button was clicked, what was entered in text fields, etc.) after the app finishes running.
    """
    if ps is None:
        ps = i_mode.copy()
    app=ImgBookApp(ps)
    app.run()
    return qu.get()
__all__=['img_pages']
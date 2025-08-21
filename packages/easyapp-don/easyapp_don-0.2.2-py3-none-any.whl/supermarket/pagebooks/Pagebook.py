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
class PagesApp(MDApp):
    def __init__(self, ps=None,**kwargs):
        super().__init__(**kwargs)
        if ps is None:
            ps = p_mode.copy()
        self.ps=ps_fill(ps)
        self.page_names=list(self.ps.keys())
        self.manner=MDScreenManager()
        self.this_page_idx=0
        self.this_page_name=self.page_names[self.this_page_idx]
        self.this_page=self.ps[self.this_page_name]
        self.res={}
        for page_name,page_config in self.ps.items():
            es=es_fill(page_config["es"])
            inp=[]
            for _ in es:
                inp.append("")
            self.res[page_name]=[None,inp,[],[]]
        self.build_screens()
    def build(self):
        Window.bind(on_request_close=self.on_close)
        self.title=str(self.this_page["tie"])
        self.theme_cls.theme_style=check_type(self.this_page["theme"],"t")
        self.manner.bind(current=self.on_screen_changed)
        return self.manner
    def on_stop(self):
        if qu.empty():
            qu.put(self.res)
    def save_screen(self):
        this_screen=self.manner.current_screen
        this_screen_name=this_screen.name
        inputs=[]
        if hasattr(this_screen,"inputs"):
            inputs=[e.text for e in this_screen.inputs]
        f_s=[]
        if hasattr(this_screen,"f_s"):
            for f in this_screen.f_s:
                f_s=f.get_res()
        self.res[this_screen_name]=[getattr(this_screen,"click",None),inputs,f_s]
    def on_screen_changed(self,instance,value):
        self.this_page_idx=self.page_names.index(value)
        self.this_page=self.ps[value]
        self.title=str(self.this_page["tie"])
        self.theme_cls.theme_style=check_type(self.this_page["theme"],"t")
    def on_close(self,window,*args):
        self.save_screen()
        this_screen=self.ps[self.manner.current]
        tip=fill_tip(this_screen["tip"])
        if tip:
            txt=tip["txt"]
            tie=tip["tie"]
            ok=tip["ok"]
            cal=tip["cal"]
            dialog(txt,tie, ok, cal)
            return True
        else:
            qu.put(self.res)
            self.stop()
            return True
    def go_next(self,page_idx):
        self.save_screen()
        if page_idx<len(self.page_names)-1:
            self.this_page_idx=page_idx+1
            self.manner.current=self.page_names[self.this_page_idx]
    def go_last(self,page_idx):
        self.save_screen()
        if page_idx>0:
            self.this_page_idx=page_idx-1
            self.manner.current=self.page_names[self.this_page_idx]
    def go_home(self,instance=None):
        self.save_screen()
        self.this_page_idx=0
        self.manner.current=self.page_names[self.this_page_idx]
    def build_screens(self):
        for page_idx,page_name in enumerate(self.page_names):
            screen=self.create_screen(page_name, page_idx)
            self.manner.add_widget(screen)
    def create_screen(self,page_name,page_idx):
        page_config=self.ps[page_name]
        screen=MDScreen(name=page_name)
        screen.md_bg_color=check_type(page_config["color"],"c",WHITE12)
        screen.page_config=page_config
        screen.page_idx=page_idx
        screen.inputs=[]
        screen.f_s=[]
        ts=ts_fill(page_config["ts"])
        fs=fs_fill(page_config["fs"])
        es=es_fill(page_config["es"])
        bs=bs_fill(page_config["bs"])
        last=last_fill(page_config["last"])
        next1=next_fill(page_config["next"])
        back=back_fill(page_config["back"])
        screen.f_add_to=[]
        inp=[]
        for _ in es:
            inp.append("")
        self.res[page_name]=[None,inp,[]]
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
        if fs:
            for f_idx,f_config in enumerate(fs):
                f_txt=f_config[0]
                f_color=f_config[1]
                f_t_color=f_config[2]
                f_size=f_config[3]
                f_pos=f_config[4]
                f=FillBtn(f_txt,f_color,f_t_color,f_size,f_pos,f_idx,screen.f_add_to)
                screen.add_widget(f)
                screen.f_s.append(f)
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
        if last and page_idx>0:
            l_txt=last["txt"]
            l_color=last["color"]
            l_size=last["size"]
            l_pos=last["pos"]
            l=MDRaisedButton(text=l_txt,
                             size_hint=l_size,
                             pos_hint={"center_x":l_pos[0],
                                       "center_y":l_pos[1]},
                             md_bg_color=l_color,
                             on_press=lambda instance,idx=page_idx:self.go_last(idx))
            screen.add_widget(l)
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
        if next1 and page_idx<len(self.page_names)-1:
            n_txt=next1["txt"]
            n_color=next1["color"]
            n_size=next1["size"]
            n_pos=next1["pos"]
            n=MDRaisedButton(text=n_txt,
                             size_hint=n_size,
                             pos_hint={"center_x":n_pos[0],
                                       "center_y":n_pos[1]},
                             md_bg_color=n_color,
                             on_press=lambda instance,idx=page_idx:self.go_next(idx))
            screen.add_widget(n)
        return screen
    def on_btn(self,btn_idx):
        this_screen=self.manner.current_screen
        this_screen.click=btn_idx
        self.save_screen()
        qu.put(self.res)
        self.stop()
def pages(page=None):
    """
    This function differs from previous functions in that it enables multipage navigation, allowing you to freely return
    to the previous page, navigate to the next page, and return to the homepage. However,
    it does not have image functionality and is only suitable for quick apps without image features.
    If you need image functionality, please import the img_pages() function from easyapp_don.supermarket.imgbooks.Imgbook.
    It is actually a simplified version of the img_pages() function without image support, making it convenient for users who don't
     have image materials to run.
    The advantage is that you don't even need to write much code - just write a pages() function to create a simple 3-page scenario.
    Note that when writing the function, do not mistakenly write it as page() - that would be incorrect! page() is a function for creating a single page, which can create a multi-functional single page, not multiple pages like pages().
    The pages() function is the foundation of img_pages(). Let's talk about the parameters of Pagebook's pages().
    Special note: Sizes and positions are between 0 and 1, referring to the proportion of the parent container.
    :param page: This is a dictionary with numerous custom parameters. When writing this parameter, it's best to
    follow the format in easyapp_don.supermarket.pagebooks.__main__, where each page can automatically populate parameters.
     Many local parameters like tip also have custom sub-parameters such as txt, yie, ok, cal.
      You don't need to write all of them - just modify the parameters you want to change, achieving parameter freedom.
       We also emphasize fault tolerance. For example, in the text 2D list ts,
       the default position is the center (i.e., (0.5, 0.5)). If you don't want to change the position, just write the content,
    and we will automatically complete it for you.
    Take a look at the parameter format (not required; you only need to modify key parameters when filling in):
    {
    "Page1 name (not displayed)": {
    "tie": "This is the page title",
    "ts": [
    ["Hello, easyapp_don!", (0.5, 0.9)], # This is page content. The first part is text content, the second is position. If you don't want to write the position, you can omit it, and it will default to the center.
    ["Text1", (0.1, 0.65)],
    ["Text2", (0.5, 0.65)],
    ["Text3", (0.9, 0.65)],
    ["1/1", (0.5, 0.05)]
    ],
    "fs": [
    ["a[0]", GREY4, RED8, (0.05, 0.05), (0.1, 0.8)], # These are fill buttons for the page, like multiple-choice answer sheet buttons. They are a type of button that records its index when clicked and removes the index when clicked again.
    ["b[1]", GREY8, BLUE1, (0.05, 0.05), (0.5, 0.8)], # The first is the button text, the second is the initial color, the third is the color after clicking, the fourth is the size, and the fifth is the position. All have default values and can be abbreviated as [["example"]].
    ["c[2]", GREY8, GREEN8, (0.05, 0.05), (0.9, 0.8)]
    ],
    "es": [
    ["Enter1", (0.2, 0.05), (0.15, 0.5)], # These are input boxes for the page, which can input content and accurately display the input.
    ["Enter2", (0.2, 0.05), (0.5, 0.5)], # The first is the prompt content of the input box, the second is the size, and the third is the position.
    ["Enter3", (0.2, 0.05), (0.85, 0.5)] # You can abbreviate and omit the position, but it's not recommended for multiple input boxes as it may cause overlap in size and position.
    ],
    "bs": [
    ["Button0", RED1, (0.15, 0.05), (0.15, 0.3)], # These are button parameters. Clicking the button will immediately exit the set page and return a value.
    ["Button1", GREEN8, (0.15, 0.05), (0.5, 0.3)], # Its return value is its index. For example, clicking "Button1" will return 1.
    ["Button2", BLUE8, (0.15, 0.05), (0.85, 0.3)] # You can abbreviate, but it's not recommended as it may cause button overlap.
    ],
    "theme": LIGHT, # Page theme, there are LIGHT and DARK. You need to import from easyapp_don.tools.colors to get them.
    "color": WHITE12, # Page background color. You need to import from easyapp_don.tools.colors. The depth of the color is indicated by the number after it; the smaller the number, the darker the color.
    "tip": { # This is the input box that pops up when clicking to close the page. If you don't want it, set it to {}.
    "txt": "Close app?", # Text content of the pop-up
    "tie": "Tip", # Title of the pop-up
    "ok": ["Yes", GREY8], # OK button of the pop-up. The first is the text, the second is the color. You can also abbreviate to only the text.
    "cal": ["No", BLUE8] # Cancel button of the pop-up, same as the OK button. If you only want one button, set ok or cal to [].
    },
    "last": { # This is the previous navigation button of the page. Not available on the first page. txt is the button text, color is the button color.
    "txt": "<<Last",
    "color": ORANGE7,
    "size": (0.15, 0.05), # size is the button size
    "pos": (0.1, 0.1) # pos is the button position
    },
    "next": { # Similar to last, it navigates to the next page. Not available on the last page.
    "txt": "Next>>", # txt, color, size, pos are all button configurations
    "color": ORANGE7,
    "size": (0.15, 0.05),
    "pos": (0.9, 0.1)
    },
    "back": { # Similar to last, it functions to return to the homepage. Not available on the homepage.
    "txt": "<<<Back", # txt, color, size, pos are button configurations
    "color": ORANGE7,
    "size": (0.15, 0.05),
    "pos": (0.9, 0.95)
    }
    },
    "Page2 name (not displayed)": {...},
    ...
    "Page n name (not displayed)": {...}
    }
    :return: The return value is a dictionary. Format: {Page name (not title): [Clicked button, list of input texts, list of clicked fill buttons]}. For other questions, call 18903502392 to reach me!
    For complete examples, please refer to main.py
    """
    if page is None:
        page = p_mode.copy()
    app=PagesApp(page)
    app.run()
    return qu.get()
__all__=['pages']
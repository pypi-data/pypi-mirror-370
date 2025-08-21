"""
They are tools of easyapp_don.supermarket.
"""
from easyapp_don.tools.colors import *
from easyapp_don.tools.Manner import *
import warnings
from typing import List,Tuple,Set,Callable,ClassVar,TypeVar,Union,Optional
def check_size(size=(0.2,0.1),a="fs",mode=(0.05,0.05)):
    if not isinstance(size,tuple) or len(size) != 2:
        warnings.warn(f"Argument <{a}>'s size must be tuple,and its len must be 2.")
        return mode
    else:
        return size
def check_pos(pos=(0.5,0.5),a="fs",mode=(0.5,0.5)):
    if not isinstance(pos,(list,tuple)) or len(pos) <2 :
        warnings.warn(f"Argument <{a}>'s pos must be tuple or list,and its len must be 2.")
        return mode
    else:
        return pos
def fill_bi_page(bi=None) -> list:
    if bi is None:
        bi = []
    filled_bi=[]
    if bi:
        for b in bi:
            if not isinstance(b,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b} must be list.",UserWarning)
                b=["images/easyapp_don.png",(0.2,0.1),(0.5,0.5),0.9,True]
                filled_bi.append(b)
            else:
                bi_path=str(b[0]) if len(b)>0 else "images/easyapp_don.png"
                bi_size=b[1] if len(b)>1 else (0.2,0.1)
                bi_pos=b[2] if len(b)>2 else (0.5,0.5)
                bi_o=b[3] if len(b)>3 else 0.9
                bi_is_close=b[4] if len(b)>4 else True
                if not isinstance(bi_size,tuple) or len(bi_size) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b}'s size (b[1]) must be tuple,"
                                  f"and its len must be 2.",UserWarning)
                    bi_size=(0.2,0.1)
                if not isinstance(bi_pos,(list,tuple)) or len(bi_pos) < 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b}'s position (b[2]) must be tuple or list,"
                                  f"and its len must be 2.",UserWarning)
                    bi_pos=(0.5,0.5)
                if not isinstance(bi_o,(int,float)) or not 0<=bi_o<=1:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b}'s opacity (b[3]) must be int or float,"
                                  f"and its value must between 0 and 1.",UserWarning)
                    bi_o=0.9
                if not isinstance(bi_is_close,bool):
                    warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b}'s is_close (b[4]) must be bool.",UserWarning)
                    bi_is_close=True
                b=[bi_path,bi_size,bi_pos,bi_o,bi_is_close]
                filled_bi.append(b)
        return filled_bi
    else:
        return []
def fill_bs_page(bs=None) -> list:
    if bs is None:
        bs = []
    filled_bs=[]
    if bs:
        for b in bs:
            if not isinstance(b,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b} must be list.",UserWarning)
                b=["ERROR",RED8,(0.1,0.05),(0.5,0.1)]
                filled_bs.append(b)
            else:
                b_txt=str(b[0]) if len(b)>0 else "Button0"
                b_color=b[1] if len(b)>1 else GREEN6
                b_size=b[2] if len(b)>2 else (0.1,0.05)
                b_pos=b[3] if len(b)>3 else (0.5,0.1)
                b_color=check_type(b_color,"c",GREEN6)
                if not isinstance(b_size,tuple) or len(b_size) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b}'s size (b[2]) must be tuple,"
                                  f"and its len must be 2.",UserWarning)
                    b_size=(0.1,0.05)
                if not isinstance(b_pos,(list,tuple)) or len(b_pos)<2 :
                    warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b}'s position (b[3]) must be list or tuple,"
                                  f"and its len must be 2.",UserWarning)
                    b_pos=(0.5,0.1)
                b=[b_txt,b_color,b_size,b_pos]
                filled_bs.append(b)
        return filled_bs
    else:
        return []
def ts_fill(ts) -> list:
    ts_=[]
    if ts:
        for t in ts:
            if not isinstance(t,list):
                warnings.warn(f"\nArgument <ts>'s {t} must be list.")
                t=["ERROR",(0.5,0.5)]
                ts_.append(t)
            else:
                t_txt=str(t[0]) if len(t)>0 else "ERROR"
                t_pos=check_pos(t[1],f"ts's {t}'s") if len(t)>1 else (0.5,0.5)
                if not isinstance(t_pos,(list,tuple)) or len(t_pos) < 2:
                    warnings.warn(f"\nArgument <ts>'s {t}'s pos (t[0]) must be list or tuple,"
                                  f"and its len must be 2.")
                    t_pos=(0.5,0.5)
                t=[t_txt,t_pos]
                ts_.append(t)
        return ts_
    else:
        return []
def fs_fill(fs) -> list:
    fs_=[]
    if fs:
        for f in fs:
            if not isinstance(f,list):
                warnings.warn(f"\nArgument <fs>'s {f} must be list.")
                f=["ERROR",GREY4,BLUE8,(0.05,0.05),(0.5,0.5)]
                fs_.append(f)
            else:
                f_txt=str(f[0]) if len(f)>0 else "ERROR"
                f_color=f[1] if len(f)>1 else GREY4
                f_c_color=f[2] if len(f)>2 else BLUE1
                f_size=f[3] if len(f)>3 else (0.05,0.05)
                f_pos=f[4] if len(f)>4 else (0.5,0.5)
                f_color=check_type(f_color,"c",GREY8)
                f_c_color=check_type(f_c_color,"c",BLUE1)
                f_size=check_size(f_size,f"fs's {f}",(0.05,0.05))
                f_pos=check_pos(f_pos,f"fs's {f}",(0.05,0.05))
                f=[f_txt,f_color,f_c_color,f_size,f_pos]
                fs_.append(f)
        return fs_
    else:
        return []
def es_fill(es) -> list:
    f_e=[]
    if es:
        for e in es:
            if not isinstance(e,list):
                warnings.warn(f"Argument <es>'s {e} must be list.")
                e=["Enter something.",(0.9,0.1),(0.5,0.5)]
                f_e.append(e)
            else:
                e_txt=str(e[0]) if len(e)>0 else "ERROR"
                e_size=check_size(e[1],f"<es>'s {e}",(0.9,0.1)) if len(e)>1 else (0.9,0.1)
                e_pos=check_pos(e[2],f"<es>'s {e}",(0.5,0.5)) if len(e)>2 else (0.5,0.5)
                e=[e_txt,e_size,e_pos]
                f_e.append(e)
        return f_e
    else:
        return []
def bs_fill(bs) -> list:
    f_b=[]
    if bs:
        for b in bs:
            if not isinstance(b,list):
                warnings.warn(f"Argument bs's {b} must be list.")
                b=["ERROR",RED1,(0.1,0.05),(0.5,0.5)]
                f_b.append(b)
            else:
                b_txt=str(b[0]) if len(b)>0 else "ERROR"
                b_color=check_type(b[1],"c",GREEN6) if len(b)>1 else GREEN6
                b_size=check_size(b[2], f"<bs>'s {b}", (0.1, 0.1))
                b_pos=check_pos(b[3],f"<bs>'s {b}",(0.5,0.5))
                b=[b_txt,b_color,b_size,b_pos]
                f_b.append(b)
        return f_b
    else:
        return []
p_m={"tie":"SuperEasyapp_don",
     "ts":[["Hello,easyapp_don!",(0.5,0.9)],
           ["Text1",(0.1,0.65)],
           ["Text2",(0.5,0.65)],
           ["Text3",(0.9,0.65)],
           ["1/1",(0.5,0.05)]],
     "fs":[["a[0]",GREY4,RED8,(0.05,0.05),(0.1,0.8)],
           ["b[1]",GREY8,BLUE1,(0.05,0.05),(0.5,0.8)],
           ["c[2]",GREY8,GREEN8,(0.05,0.05),(0.9,0.8)]],
     "es":[["Enter1",(0.2,0.05),(0.15,0.5)],
           ["Enter2",(0.2,0.05),(0.5,0.5)],
           ["Enter3",(0.2,0.05),(0.85,0.5)]],
     "bs":[["Button0",RED1,(0.15,0.05),(0.15,0.3)],
           ["Button1",GREEN8,(0.15,0.05),(0.5,0.3)],
           ["Button2",BLUE8,(0.15,0.05),(0.85,0.3)]],
     "theme":LIGHT,
     "color":WHITE12,
     "tip":{"txt":"Close app?",
            "tie":"Tip",
            "ok":["Yes",GREY8],
            "cal":["No",BLUE8]},
     "last":{"txt":"<<Last",
             "color":ORANGE7,
             "size":(0.15,0.05),
             "pos":(0.1,0.1)},
     "next":{"txt":"Next>>",
             "color":ORANGE7,
             "size":(0.15,0.05),
             "pos":(0.9,0.1)},
     "back":{"txt":"<<<Back",
             "color":ORANGE7,
             "size":(0.15,0.05),
             "pos":(0.9,0.95)}}
p_em={"Page0":{"tie":"",
               "ts":[],
               "fs":[],
               "bs":[],
               "es":[],
               "color":WHITE12,
               "theme":LIGHT,
               "last":{},
               "next":{},
               "tip":{},
               "back":{}}}
p_mode={"Page1":{"tie":"SuperEasyapp_don-1",
                 "ts":[["Hello,easyapp_don!",(0.5,0.9)],
                       ["Text1",(0.1,0.65)],
                       ["Text2",(0.5,0.65)],
                       ["Text3",(0.9,0.65)],
                       ["1/3",(0.5,0.05)]],
                 "fs":[["a[0]",GREY4,RED8,(0.05,0.05),(0.1,0.8)],
                       ["b[1]",GREY8,BLUE1,(0.05,0.05),(0.5,0.8)],
                       ["c[2]",GREY8,GREEN8,(0.05,0.05),(0.9,0.8)]],
                 "es":[["Enter1",(0.2,0.05),(0.15,0.5)],
                       ["Enter2",(0.2,0.05),(0.5,0.5)],
                       ["Enter3",(0.2,0.05),(0.85,0.5)]],
                 "bs":[["Button1",RED1,(0.15,0.05),(0.15,0.3)],
                       ["Button2",GREEN8,(0.15,0.05),(0.5,0.3)],
                       ["Button3",BLUE8,(0.15,0.05),(0.85,0.3)]],
                 "theme":LIGHT,
                 "color":WHITE12,
                 "tip":{"txt":"Close app?",
                        "tie":"Tip",
                        "ok":["Yes",GREY8],
                        "cal":["No",BLUE8]},
                 "last":{"txt":"<<Last",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.1,0.1)},
                 "next":{"txt":"Next>>",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.1)},
                 "back":{"txt":"<<<Back",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.95)}},
        "Page2":{"tie":"SuperEasyapp_don-2",
                 "ts":[["Hello from easyapp_don!",(0.5,0.9)],
                       ["Text4",(0.1,0.65)],
                       ["Text5",(0.5,0.65)],
                       ["Text6",(0.9,0.65)],
                       ["2/3",(0.5,0.05)]],
                 "fs":[["d[3]",GREY4,RED8,(0.05,0.05),(0.1,0.8)],
                       ["e[4]",GREY8,BLUE1,(0.05,0.05),(0.5,0.8)],
                       ["f[5]",GREY8,GREEN8,(0.05,0.05),(0.9,0.8)]],
                 "es":[["Enter4",(0.2,0.05),(0.15,0.5)],
                       ["Enter5",(0.2,0.05),(0.5,0.5)],
                       ["Enter6",(0.2,0.05),(0.85,0.5)]],
                 "bs":[["Button4",RED1,(0.15,0.05),(0.15,0.3)],
                       ["Button5",GREEN8,(0.15,0.05),(0.5,0.3)],
                       ["Button6",BLUE8,(0.15,0.05),(0.85,0.3)]],
                 "theme":LIGHT,
                 "color":PINK8,
                 "tip":{"txt":"Close app?",
                        "tie":"Tip",
                        "ok":["Yes",GREY8],
                        "cal":["No",BLUE8]},
                 "last":{"txt":"<<Last",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.1,0.1)},
                 "next":{"txt":"Next>>",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.1)},
                 "back":{"txt":"<<<Back",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.95)}},
        "Page3":{"tie":"SuperEasyapp_don-3",
                 "ts":[["Welcome to easyapp_don.supermarket.pagebooks class!",(0.5,0.9)],
                       ["Text7",(0.1,0.65)],
                       ["Text8",(0.5,0.65)],
                       ["Text9",(0.9,0.65)],
                       ["3/3",(0.5,0.05)]],
                 "fs":[["g[6]",GREY4,RED8,(0.05,0.05),(0.1,0.8)],
                       ["h[7]",GREY8,BLUE1,(0.05,0.05),(0.5,0.8)],
                       ["i[8]",GREY8,GREEN8,(0.05,0.05),(0.9,0.8)]],
                 "es":[["Enter7",(0.2,0.05),(0.15,0.5)],
                       ["Enter8",(0.2,0.05),(0.5,0.5)],
                       ["Enter9",(0.2,0.05),(0.85,0.5)]],
                 "bs":[["Finish",RED1,(0.15,0.05),(0.5,0.3)]],
                 "theme":LIGHT,
                 "color":GOLD8,
                 "tip":{"txt":"Close app?",
                        "tie":"Tip",
                        "ok":["Yes",GREY8],
                        "cal":["No",BLUE8]},
                 "last":{"txt":"<<Last",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.1,0.1)},
                 "next":{"txt":"Next>>",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.1)},
                 "back":{"txt":"<<<Back",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.95)}}}
i_m={"tie":"SuperEasyapp_don",
     "ts":[["Hello,easyapp_don!",(0.5,0.95)],
           ["Text1",(0.1,0.6)],
           ["Text2",(0.5,0.6)],
           ["Text3",(0.9,0.6)],
           ["1/1",(0.5,0.05)]],
     "fs":[["a[0]",GREY4,RED8,(0.05,0.05),(0.1,0.8)],
           ["b[1]",GREY8,BLUE1,(0.05,0.05),(0.5,0.8)],
           ["c[2]",GREY8,GREEN8,(0.05,0.05),(0.9,0.8)]],
     "es":[["Enter1",(0.2,0.05),(0.15,0.45)],
           ["Enter2",(0.2,0.05),(0.5,0.45)],
           ["Enter3",(0.2,0.05),(0.85,0.45)]],
     "bs":[["Button0",RED1,(0.15,0.05),(0.15,0.2)],
           ["Button1",GREEN8,(0.15,0.05),(0.5,0.2)],
           ["Button2",BLUE8,(0.15,0.05),(0.85,0.2)]],
     "theme":LIGHT,
     "color":WHITE12,
     "tip":{"txt":"Close app?",
            "tie":"Tip",
            "ok":["Yes",GREY8],
            "cal":["No",BLUE8]},
     "last":{"txt":"<<Last",
             "color":ORANGE7,
             "size":(0.15,0.05),
             "pos":(0.1,0.1)},
     "next":{"txt":"Next>>",
             "color":ORANGE7,
             "size":(0.15,0.05),
             "pos":(0.9,0.1)},
     "back":{"txt":"<<<Back",
             "color":ORANGE7,
             "size":(0.15,0.05),
             "pos":(0.9,0.95)},
     "i":[["images/easyapp_don.png",(1,1),(0.5,0.5),0.6]],
     "fi":[["images/dinos.png","images/gold.png",(0.05,0.05),(0.1,0.7)],
           ["images/dinos.png","images/sky.png",(0.05,0.05),(0.5,0.7)],
           ["images/dinos.png","images/stone.png",(0.05,0.05),(0.9,0.7)]],
     "bi":[["images/four_d.png",(0.2,0.1),(0.25,0.3),0.8,True],
           ["images/eto.png",(0.2,0.1),(0.5,0.3),0.8,True],
           ["images/future.png",(0.2,0.1),(0.75,0.3),0.8,True]]}
i_em={"Page0":{"tie":"",
               "tip":{},
               "color":WHITE12,
               "theme":LIGHT,
               "last":{},
               "next":{},
               "back":{},
               "i":[],
               "fi":[],
               "bi":[],
               "ts":[],
               "fs":[],
               "bs":[],
               "es":[]}}
i_mode={"Page1":{"tie":"SuperEasyapp_don-1",
                 "ts":[["Hello,easyapp_don!",(0.5,0.95)],
                       ["Text1",(0.1,0.6)],
                       ["Text2",(0.5,0.6)],
                       ["Text3",(0.9,0.6)],
                       ["1/3",(0.5,0.05)]],
                 "fs":[["a[0]",GREY4,RED8,(0.05,0.05),(0.1,0.8)],
                       ["b[1]",GREY8,BLUE1,(0.05,0.05),(0.5,0.8)],
                       ["c[2]",GREY8,GREEN8,(0.05,0.05),(0.9,0.8)]],
                 "es":[["Enter1",(0.2,0.05),(0.15,0.45)],
                       ["Enter2",(0.2,0.05),(0.5,0.45)],
                       ["Enter3",(0.2,0.05),(0.85,0.45)]],
                 "bs":[["Button0",RED1,(0.15,0.05),(0.15,0.2)],
                       ["Button1",GREEN8,(0.15,0.05),(0.5,0.2)],
                       ["Button2",BLUE8,(0.15,0.05),(0.85,0.2)]],
                 "theme":LIGHT,
                 "color":WHITE12,
                 "tip":{"txt":"Close app?",
                        "tie":"Tip",
                        "ok":["Yes",GREY8],
                        "cal":["No",BLUE8]},
                 "last":{"txt":"<<Last",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.1,0.1)},
                 "next":{"txt":"Next>>",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.1)},
                 "back":{"txt":"<<<Back",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.95)},
                 "i":[["images/easyapp_don.png",(1,1),(0.5,0.5),0.6]],
                 "fi":[["images/dinos.png","images/gold.png",(0.05,0.05),(0.1,0.7)],
                       ["images/dinos.png","images/sky.png",(0.05,0.05),(0.5,0.7)],
                       ["images/dinos.png","images/stone.png",(0.05,0.05),(0.9,0.7)]],
                 "bi":[["images/four_d.png",(0.2,0.1),(0.25,0.3),0.8,False],
                       ["images/eto.png",(0.2,0.1),(0.5,0.3),0.8,False],
                       ["images/future.png",(0.2,0.1),(0.75,0.3),0.8,False]]},
        "Page2":{"tie":"SuperEasyapp_don-2",
                 "ts":[["Hello,easyapp_don!",(0.5,0.95)],
                       ["Text4",(0.1,0.6)],
                       ["Text5",(0.5,0.6)],
                       ["Text6",(0.9,0.6)],
                       ["2/3",(0.5,0.05)]],
                 "fs":[["d[0]",GREY4,RED8,(0.05,0.05),(0.1,0.8)],
                       ["e[1]",GREY8,BLUE1,(0.05,0.05),(0.5,0.8)],
                       ["f[2]",GREY8,GREEN8,(0.05,0.05),(0.9,0.8)]],
                 "es":[["Enter4",(0.2,0.05),(0.15,0.45)],
                       ["Enter5",(0.2,0.05),(0.5,0.45)],
                       ["Enter6",(0.2,0.05),(0.85,0.45)]],
                 "bs":[["Button3",RED1,(0.15,0.05),(0.15,0.2)],
                       ["Button4",GREEN8,(0.15,0.05),(0.5,0.2)],
                       ["Button5",BLUE8,(0.15,0.05),(0.85,0.2)]],
                 "theme":DARK,
                 "color":PINK8,
                 "tip":{"txt":"Close app?",
                        "tie":"Tip",
                        "ok":["Yes",GREY8],
                        "cal":["No",BLUE8]},
                 "last":{"txt":"<<Last",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.1,0.1)},
                 "next":{"txt":"Next>>",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.1)},
                 "back":{"txt":"<<<Back",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.95)},
                 "i":[["images/eto.png",(1,1),(0.5,0.5),0.6]],
                 "fi":[["images/dinos.png","images/sky.png",(0.05,0.05),(0.1,0.7)],
                       ["images/dinos.png","images/stone.png",(0.05,0.05),(0.5,0.7)],
                       ["images/dinos.png","images/gold.png",(0.05,0.05),(0.9,0.7)]],
                 "bi":[["images/forest.png",(0.2,0.1),(0.25,0.3),0.8,False],
                       ["images/sky.png",(0.2,0.1),(0.5,0.3),0.8,False],
                       ["images/future.png",(0.2,0.1),(0.75,0.3),0.8,False]]},
        "Page3":{"tie":"SuperEasyapp_don-3",
                 "ts":[["Hello,easyapp_don!",(0.5,0.95)],
                       ["Text7",(0.1,0.6)],
                       ["Text8",(0.5,0.6)],
                       ["Text9",(0.9,0.6)],
                       ["3/3",(0.5,0.05)]],
                 "fs":[["g[0]",GREY4,RED8,(0.05,0.05),(0.1,0.8)],
                       ["h[1]",GREY8,BLUE1,(0.05,0.05),(0.5,0.8)],
                       ["i[2]",GREY8,GREEN8,(0.05,0.05),(0.9,0.8)]],
                 "es":[["Enter7",(0.2,0.05),(0.15,0.45)],
                       ["Enter8",(0.2,0.05),(0.5,0.45)],
                       ["Enter9",(0.2,0.05),(0.85,0.45)]],
                 "bs":[["Finish",RED1,(0.15,0.05),(0.5,0.2)]],
                 "theme":DARK,
                 "color":GOLD1,
                 "tip":{"txt":"Close app?",
                        "tie":"Tip",
                        "ok":["Yes",GREY8],
                        "cal":["No",BLUE8]},
                 "last":{"txt":"<<Last",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.1,0.1)},
                 "next":{"txt":"Next>>",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.1)},
                 "back":{"txt":"<<<Back",
                         "color":ORANGE7,
                         "size":(0.15,0.05),
                         "pos":(0.9,0.95)},
                 "i":[["images/future.png",(1,1),(0.5,0.5),0.6]],
                 "fi":[["images/dinos.png","images/stone.png",(0.05,0.05),(0.1,0.7)],
                       ["images/dinos.png","images/gold.png",(0.05,0.05),(0.5,0.7)],
                       ["images/dinos.png","images/sky.png",(0.05,0.05),(0.9,0.7)]],
                 "bi":[["images/four_d.png",(0.2,0.1),(0.25,0.3),0.8,True],
                       ["images/eto.png",(0.2,0.1),(0.5,0.3),0.8,True],
                       ["images/sky.png",(0.2,0.1),(0.75,0.3),0.8,True]]}}
def gps_fill(gps:dict):
    if gps:
        gps:dict=check_type(gps,dict,{"txt":"Next>>",
                                     "color":ORANGE7,
                                     "size":(0.15,0.05),
                                     "pos":(0.1,0.1)})
        txt=str(gps["txt"]) if "txt" in gps.keys() else "Next>>"
        color=gps["color"] if "color" in gps.keys() else ORANGE3
        color=check_type(color,"c",ORANGE3)
        size=gps["size"] if "size" in gps.keys() else (0.15,0.05)
        pos=gps["pos"] if "pos" in gps.keys() else (0.9,0.1)
        f_gps={"txt":txt,
               "color":color,
               "size":size,
               "pos":pos}
        return f_gps
    else:
        return {}
def ps_fill(ps=None):
    if ps is None:
        ps = p_mode.copy()
    f_ps={}
    if ps:
        for p_name,p_config in ps.items():
            p_name=str(p_name)
            if not isinstance(p_config,dict):
                warnings.warn(f"Argument <ps>'s {p_name}'s config must be dict.")
                p_config={}
            f_config=p_m.copy()
            for k in f_config:
                if k in p_config:
                    f_config[k]=p_config[k]
            f_ps[p_name]=f_config
        return f_ps
    else:
        return p_em.copy()
def img_ps_fill(img_ps=None):
    if img_ps is None:
        img_ps = i_mode.copy()
    f_super_ps={}
    if img_ps:
        for p_name,p_config in img_ps.items():
            p_name=str(p_name)
            if not isinstance(p_config,dict):
                warnings.warn(f"Argument <ps>'s {p_name}'s config must be dict.")
                p_config={}
            f_config=i_m.copy()
            for k in f_config:
                if k in p_config:
                    f_config[k]=p_config[k]
            f_super_ps[p_name]=f_config
        return f_super_ps
    else:
        return i_em.copy()
def last_fill(last):
    if last:
        if not isinstance(last,dict):
            warnings.warn(f"Argument {last} must be dict.")
            last={"txt":"<<Last",
                 "color":ORANGE7,
                 "size":(0.15,0.05),
                 "pos":(0.1,0.1)}
            f_last=last.copy()
        else:
            txt=str(last["txt"]) if "txt" in last.keys() else "<<Last"
            color=check_type(last["color"],"c",ORANGE3) if "color" in last.keys() else ORANGE3
            size=check_size(last["size"],"last's size",(0.15,0.05)) if "size" in last.keys() else (0.15,0.05)
            pos=check_pos(last["pos"],"last's pos",(0.1,0.1)) if "pos" in last.keys() else (0.1,0.1)
            f_last={"txt":txt,
                    "color":color,
                    "size":size,
                    "pos":pos}
        return f_last
    else:
        return {}
def next_fill(next1):
    if next1:
        if not isinstance(next1,dict):
            warnings.warn(f"Argument next 's {next1} must be dict.")
            next1={"txt":"Next>>",
                   "color":ORANGE7,
                   "size":(0.15,0.05),
                    "pos":(0.9,0.1)}
        else:
            txt=str(next1["txt"]) if "txt" in next1.keys() else "Next>>"
            color=check_type(next1["color"],"c",ORANGE3) if "color" in next1.keys() else ORANGE3
            size=check_size(next1["size"],"next's size",(0.15,0.05)) if "size" in next1.keys() else (0.15,0.05)
            pos=check_pos(next1["pos"],"next's pos",(0.9,0.1)) if "pos" in next1.keys() else (0.9,0.1)
            next1={"txt":txt,
                   "color":color,
                   "size":size,
                   "pos":pos}
        return next1
    else:
        return {}
def back_fill(back):
    if back:
        if not isinstance(back,dict):
            warnings.warn(f"Argument back's {back} must be dict.")
            back={"txt":"<<<Back",
                    "color":ORANGE7,
                    "size":(0.15,0.05),
                    "pos":(0.9,0.95)}
        else:
            txt=str(back["txt"]) if "txt" in back.keys() else "<<<Back"
            color=check_type(back["color"],"c",ORANGE3) if "color" in back.keys() else ORANGE3
            size=check_size(back["size"],f"back's {back}'s size",(0.15,0.05)) if "size" in back.keys() else (0.15,0.05)
            pos=check_pos(back["pos"],f"back's {back}'s pos",(0.9,0.95)) if "pos" in back.keys() else (0.9,0.95)
            back={"txt":txt,
                  "color":color,
                  "size":size,
                  "pos":pos}
        return back
    else:
        return {}
__all__=['fill_bi_page',
         'fill_bs_page',
         'ts_fill',
         'fs_fill',
         'check_pos',
         'check_size',
         'es_fill',
         'bs_fill',
         'p_em',
         'p_m',
         'p_mode',
         'i_em',
         'i_m',
         'i_mode',
         'ps_fill',
         'img_ps_fill',
         'gps_fill',
         'back_fill',
         'last_fill',
         'next_fill']
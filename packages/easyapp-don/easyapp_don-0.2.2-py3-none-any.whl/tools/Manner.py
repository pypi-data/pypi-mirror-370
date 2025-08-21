"""
There are many manner for build app.
"""
import warnings
from easyapp_don.tools.colors import *
from typing import Any,Tuple,List,Set,ClassVar,Callable
from kivy.core.image import ImageLoader
from kivy.uix.image import Image
import os
import sys
def check_type(obj:object=(1,2,3,4),t:object=tuple,mr:object=LIGHT) -> object:
    """
    This is a function used to check whether the parameter type matches the required type. When <t> is <'t'>, it will verify if obj is either 'Light' or 'Dark'; if not, it will automatically use 'Light'.
    :param mr: The default value of obj.
    :type mr:object
    :param obj: The parameter to be checked
    :type obj: object
    :param t: The target type or the string 't'
    :type t: object
    :return: When <t> is <'t'>, returns LIGHT or DARK; when t is a type, it will automatically verify the type.
    """
    if t == "t":
        if obj != LIGHT and obj != DARK:
            warnings.warn(f"\n[Easyapp_donError] Argument <theme> must be variable <LIGHT> or <DARK> from easyapp_don.manner.colors.",UserWarning)
            return mr
        else:
            return obj
    elif t == "c":
        if not isinstance(obj,tuple):
            o_e=type(obj).__name__
            warnings.warn(f"\n[Easyapp_donError] Argument <{obj}> must be tuple, not {o_e}",UserWarning)
            return mr
        else:
            if len(obj) != 4:
                warnings.warn(f"\n[Easyapp_donError] Argument <{obj}>'s len must be 4.",UserWarning)
                return mr
            else:
                return obj
    else:
        if not isinstance(obj,t):
            o_error=type(obj).__name__
            warnings.warn(f"\n[Easyapp_donError] Argument <{obj}> must be {t}, not {o_error}.",UserWarning)
            return mr
        else:
            return obj
def fill_bs(bs=None) -> list:
    """
    This is a function that can fill bs.
    :param bs: Be filled of list.
    :type bs:list
    :return: The new list that already fill bs.
    :rtype:list
    """
    if bs is None:
        bs = []
    if bs:
        if not isinstance(bs,list):
            warnings.warn("\n\n[Easyapp_donTypeError] Argument <bs> must be list,below will set it to [].\n\n",UserWarning)
            return []
        filled_bs=[]
        for b in bs:
            if not isinstance(b,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b} must be list.",UserWarning)
                b=["ERROR",(0.15,0.05),(0.5,0.1),RED1,False]
                filled_bs.append(b)
            else:
                if len(b) != 5:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b}'s len must be 5.",UserWarning)
                b_t=str(b[0]) if len(b) >0 else "ERROR"
                b_color=b[1] if len(b)>1 else RED1
                b_size=b[2] if len(b)>2 else (0.15,0.05)
                b_pos=b[3] if len(b) > 3 else (0.5,0.1)
                is_close=b[4] if len(b) >4 else True
                if not isinstance(b_size,(list,tuple)) or len(b_size) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b}'s size must be list or tuple,"
                                  f"and its len must be 2.",UserWarning)
                    b_size=(0.15,0.05)
                if not isinstance(b_pos,(list,tuple)) or len(b_pos) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b}'s pos must be list or tuple,"
                                  f"and its len must be 2.",UserWarning)
                    b_pos=(0.5,0.1)
                if not isinstance(b_color,tuple) or len(b_color) != 4:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b}'s color must be tuple,"
                                  f"and its len must be 4.",UserWarning)
                    b_color=RED1
                if not isinstance(is_close,bool):
                    warnings.warn(f"\n[Easyapp_donError] Argument <bs>'s {b}'s is_close must be bool.",UserWarning)
                    is_close=True
                b=[b_t,b_color,b_size,b_pos,is_close]
                filled_bs.append(b)
        return filled_bs
    else:
        return []
def fill_es(es=None) -> list:
    """
    This is a function that can fill param fs.
    :param es: Be filled of object.
    :type es:list
    :return: The new list that already filled.
    :rtype:list
    """
    if es is None:
        es = []
    if es:
        filled_es=[]
        for e1 in es:
            if not isinstance(e1,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <es>'s {e1} must be list.",UserWarning)
                e1=["ERROR",(0.9,0.1),(0.5,0.6)]
                filled_es.append(e1)
            else:
                if len(e1) != 3:
                    warnings.warn(f"\n[Easyapp_donError] Argument <es>'s {e1}'s len must be 3.",UserWarning)
                e_t=str(e1[0]) if len(e1) >0 else "ERROR"
                e_size=e1[1] if len(e1)>1 else (0.9,0.1)
                e_pos=e1[2] if len(e1)>2 else (0.5,0.6)
                if not isinstance(e_size,(list,tuple)) or len(e_size)!=2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <es>'s {e1}'s size must be list or tuple "
                                  f"and its len must be 2.",UserWarning)
                    e_size=(0.9,0.1)
                if not isinstance(e_pos,(list,tuple)) or len(e_pos) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <es>'s {e1}'s pos must be list or "
                                  f"tuple and its len must be 2.",UserWarning)
                    e_pos=(0.5,0.6)
                e1=[e_t,e_size,e_pos]
                filled_es.append(e1)
        return filled_es
    else:
        return []
def fill_ts(ts=None) -> list:
    """
    This is a function that can fill ts.
    :param ts: Be filled of objects.
    :type ts:list
    :return: The new list that already filled.
    :rtype:list
    """
    if ts is None:
        ts = []
    if ts:
        filled_ts=[]
        for t in ts:
            if not isinstance(t,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <ts>'s {t} must be list.",UserWarning)
                t=["ERROR",(0.5,0.5)]
                filled_ts.append(t)
            else:
                if not len(t)==2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <ts>'s {t}'s len must be 2.",UserWarning)
                t_t=str(t[0]) if len(t)>0 else "ERROR"
                t_pos=t[1] if len(t)>1 else (0.5,0.5)
                if not isinstance(t_pos,(list,tuple)) or len(t_pos)!=2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <ts>'s {t}'s position's len must be 2 "
                                  f"and it must be list or tuple",UserWarning)
                    t_pos=(0.5,0.5)
                t=[t_t,t_pos]
                filled_ts.append(t)
        return filled_ts
    else:
        return []
def fill_fs(fs=None) -> list:
    """
    This is a function that can fill fs.
    :param fs: Be filled of object.
    :type fs:list
    :return: Filled list.
    :rtype:list
    """
    if fs is None:
        fs = []
    if fs:
        filled_fs=[]
        for f in fs:
            if not isinstance(f,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <fs>'s {f} must be list.",UserWarning)
                f=["ERROR",GREY13,RED1,(0.15,0.05),(0.5,0.65)]
                filled_fs.append(f)
            else:
                if len(f) != 5:
                    warnings.warn(f"\n[Easyapp_donError] Argument <fs>'s {f}'s len must be 5.",UserWarning)
                f_t=str(f[0]) if len(f)>0 else "ERROR"
                f_color=f[1] if len(f)>1 else GREY13
                f_c_color=f[2] if len(f)>2 else RED8
                f_size=f[3] if len(f) > 3 else (0.05,0.05)
                f_pos=f[4] if len(f) >4 else (0.3,0.5)
                if not isinstance(f_size,tuple) or len(f_size) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <fs>'s {f}'s size's len must be 2 and it's must be tuple.",UserWarning)
                    f_size=(0.15,0.05)
                if not isinstance(f_pos,(list,tuple)) or len(f_pos) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <fs>'s {f}'s position must be list or tuple and its len must be 2.",UserWarning)
                    f_pos=(0.5,0.65)
                if not isinstance(f_color,tuple) or len(f_color) != 4:
                    warnings.warn(f"\n[Easyapp_donError] Argument <fs>'s {f}'s color must be tuple and its len must be 4.",UserWarning)
                    f_color=GREY3
                if not isinstance(f_c_color,tuple) or len(f_c_color) != 4:
                    warnings.warn(f"\n[Easyapp_donError] Argument <fs>'s {f}'s clicked_color must be tuple and its len must be 4.",UserWarning)
                    f_c_color=RED8
                f=[f_t,f_color,f_c_color,f_size,f_pos]
                filled_fs.append(f)
        return filled_fs
    else:
        return []
m_dg={"tie":"Easyapp_don-example",
    "color":WHITE12,
    "theme":LIGHT,
    "ts":[["Hello,easyapp_don!",(0.5,0.5)],
          ["1/1",(0.5,0.1)]]}
m_mode={"Page1":{"tie":"Easyapp_don-example-1",
                "color":WHITE12,
                "theme":LIGHT,
                "ts":[["Hello,easyapp_don!",(0.5,0.5)],
                      ["1/2",(0.5,0.1)]]},
        "Page2":{"tie":"Easyapp_don-example-2",
                "color":WHITE12,
                "theme":LIGHT,
                "ts":[["Hello,easyapp_don!",(0.5,0.5)],
                      ["2/2",(0.5,0.1)]]}}
m_swk={"Page0":{"tie": "",
                "color": WHITE12,
                "theme": LIGHT,
                "ts": []}}
def fill_ps(ps:dict=None, mode:dict=None, empty:dict=None) -> dict:
    """
    This is a function that can fill ps.
    :param empty: If ps is [],it will be filled to it.
    :type empty:dict
    :param ps: Be filled of object.
    :type ps:dict
    :param mode: The will filled's model.
    :type mode:dict
    :return: The new dict that is already filled.
    :rtype:dict
    """
    global m_swk,m_mode,m_dg
    if empty is None:
        empty = m_swk.copy()
    if mode is None:
        mode = m_mode.copy()
    if ps is None:
        ps = m_mode.copy()
    filled_ps={}
    if not isinstance(ps,dict):
        p_e = type(ps).__name__
        warnings.warn(f"\n[Easyapp_donError] Argument <ps> must be dict, not {p_e}.",UserWarning)
        ps={}
    if ps:
        for p_name,p_config in ps.items():
            p_name=str(p_name)
            if not isinstance(p_config,dict):
                p_config={}
            filled_config=mode.copy()
            for k in filled_config:
                if k in p_config:
                    filled_config[k]=p_config[k]
            filled_ps[p_name]=filled_config
        return filled_ps
    else:
        filled_ps=empty.copy()
        return filled_ps
def fill_tip(tip=None) -> dict:
    """
    This is a function that can fill tip.
    :param tip: Be filled with tip.
    :type tip:dict
    :return: The dict that is already filled.
    :rtype:dict
    """
    if tip is None:
        tip = {"tie": "Tip"}
    filled_tip={}
    if tip:
        tie=str(tip["tie"]) if "tie" in tip.keys() else "Tip"
        filled_tip["tie"]=tie
        txt=str(tip["txt"]) if "txt" in tip.keys() else "Close app?"
        filled_tip["txt"]=txt
        ok=tip["ok"] if "ok" in tip.keys() else ["Yes",GREY4]
        filled_tip["ok"]=ok
        cal=tip["cal"] if "cal" in tip.keys() else ["No",BLUE13]
        filled_tip["cal"]=cal
        return filled_tip
    else:
        return {}
def fill_i(i=None) -> list:
    """
    This is a function that can fill i.
    :param i: Be filled of object.
    :type i:list
    :return: The new list that already be filled.
    :rtype:list
    """
    if i is None:
        i = [["images/sky.png", (0.6, 0.3), (0.5, 0.75), 1]]
    filled_i=[]
    if i:
        for ii in i:
            if not isinstance(i,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <i>'s {ii} must be list.",UserWarning)
                ii=[["images/error.png",(0.6,0.3),(0.5,0.75),0]]
                filled_i.append(ii)
            else:
                if len(ii) != 4:
                    warnings.warn(f"\n[Easyapp_donError] Argument <i>'s {ii}'s len must be 4.",UserWarning)
                i_path=str(ii[0]) if len(ii)>0 else "images/none.png"
                i_size=ii[1] if len(ii)>1 else (0.6,0.3)
                i_pos=ii[2] if len(ii)>2 else (0.5,0.75)
                i_see=ii[3] if len(ii)>3 else 1
                if not isinstance(i_size,tuple) or len(i_size) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <i>'s {ii}'s size's len must be 2"
                                  f" and it must be tuple.",UserWarning)
                    i_size=(0.6,0.3)
                if not isinstance(i_pos,(tuple,list)) or len(i_pos) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <i>'s {ii}'s position's len must be 2"
                                  f" and it must be tuple or list.",UserWarning)
                    i_pos=(0.5,0.75)
                if not isinstance(i_see,(float,int)) or not 0<=i_see<=1:
                    warnings.warn(f"\n[Easyapp_donError] Argument <i>'s {ii}'s opacity must be float or int "
                                  f"and its value must between 0 to 1.",UserWarning)
                    i_see=1
                ii=[i_path,i_size,i_pos,i_see]
                filled_i.append(ii)
        return filled_i
    else:
        return []
def fill_bi(bi=None):
    if bi is None:
        bi = []
    filled_bi=[]
    if bi:
        for b in bi:
            if not isinstance(b,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b} must be list.",UserWarning)
                b=["images/none.png",(0.15,0.05),(0.5,0.05),1]
                filled_bi.append(b)
            else:
                if not len(b) == 4:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b}'s len must be 5.",UserWarning)
                path=str(b[0]) if len(b) >0 else "images/none.png"
                size=b[1] if len(b)>1 else (0.15,0.05)
                pos=b[2] if len(b)>2 else (0.5,0.05)
                o=b[3] if len(b)>3 else 1
                if not isinstance(size,tuple) or len(size) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b} [2] (size_hint) must be tuple "
                                  f"and its len must be 2.",UserWarning)
                    size=(0.15,0.05)
                if not isinstance(pos,(list,tuple)) or len(pos) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b}'s pos [3] must be tuple or list "
                                  f"and its len must be 2.",UserWarning)
                    pos=(0.5,0.05)
                if not isinstance(o,(float,int)) or not 0<=o<=1:
                    warnings.warn(f"\n[Easyapp_donError] Argument <bi>'s {b}'s opacity must be float or int "
                                  f"and its value must between 0 and 1.",UserWarning)
                    o=1
                b=[path,size,pos,o]
                filled_bi.append(b)
        return filled_bi
    else:
        return []
def fill_fi(fi=None) -> list :
    if fi is None:
        fi = [["images/easyapp_don.png", "images/four_d.png", (0.05, 0.05), (0.5, 0.5)]]
    filled_fi=[]
    if fi:
        for f in fi:
            if not isinstance(f,list):
                warnings.warn(f"\n[Easyapp_donError] Argument <fi>'s {f} must be list.",UserWarning)
                f=["images/easyapp_don.png","images/four_d.png",(0.05,0.05),(0.5,0.5)]
                filled_fi.append(f)
            else:
                if len(f) != 4:
                    warnings.warn(f"\n[Easyapp_donError] Argument <fi>'s {f}'s len must be 4.",UserWarning)
                f_path=str(f[0]) if len(f)>0 else "images/easyapp_don.png"
                f_t_path=str(f[1]) if len(f)>1 else "images/four_d.png"
                f_size=f[2] if len(f)>2 else (0.05,0.05)
                f_pos=f[3] if len(f)>3 else (0.5,0.5)
                if not isinstance(f_size,tuple) or len(f_size) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <fi>'s {f}'s size's len must be 2 "
                                  f"and it must be tuple.",UserWarning)
                    f_size=(0.05,0.05)
                if not isinstance(f_pos,(tuple,list)) or len(f_pos) != 2:
                    warnings.warn(f"\n[Easyapp_donError] Argument <fi>'s {f}'s position's len must be 2 "
                                  f"and it must be tuple or list.",UserWarning)
                    f_pos=(0.5,0.5)
                f=[f_path,f_t_path,f_size,f_pos]
                filled_fi.append(f)
        return filled_fi
    else:
        return []
__all__=['check_type',
         'fill_bs',
         'fill_fs',
         'fill_es',
         'fill_ps',
         'fill_ts',
         'fill_tip',
         'fill_i',
         'fill_bi',
         'fill_fi']
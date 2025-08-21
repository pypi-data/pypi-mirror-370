from kivymd.uix.dialog import MDDialog
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from easyapp_don.tools.colors import *
from easyapp_don.tools.Manner import *
import warnings
import sys
def dialog(t="Close app?", tie="Tip", ok=None, cal=None):
    """
    This is a function that can appear a dialog.
    :param t: The text of dialog.
    :type t:str
    :param tie: The title of dialog.
    :type tie:str
    :param ok: The list <ok> of dialog.Example:[ok_text,ok_color]
    :type ok:list
    :param cal: The list <cal> of dialog.Example:[ok_text,ok_color]
    :type cal:list
    :return: None.
    :rtype:None
    """
    if cal is None:
        cal = ["No", BLUE13]
    if ok is None:
        ok = ["Yes", GREY4]
    if ok and cal:
        if not isinstance(ok,list):
            ok_e=type(ok).__name__
            warnings.warn(f"\nArgument <ok> must be list ,not {ok_e}.",UserWarning)
            ok=["Yes",GREY4]
        if len(ok) != 2:
            warnings.warn(f"\nArgument <ok>'s len must be 2.",UserWarning)
        if not isinstance(cal,list):
            cal_e=type(cal).__name__
            warnings.warn(f"\nArgument <cal> must be list, not {cal_e}.",UserWarning)
            cal=["No",BLUE13]
        if len(cal) != 2:
            warnings.warn(f"\nArgument <cal>'s len must be 2.",UserWarning)
        ok_txt=str(ok[0]) if len(ok)>0 else "Yes"
        ok_color=ok[1] if len(ok)>1 else GREY13
        ok_color=check_type(ok_color,"c",GREY13)
        cal_txt=str(cal[0]) if len(cal)>0 else "No"
        cal_color=cal[1] if len(cal)>1 else BLUE13
        cal_color=check_type(cal_color,"c",BLUE13)
        app=MDDialog(title=str(tie),
                     text=str(t),
                     auto_dismiss=False,
                     size=(300,200),
                     buttons=[MDRaisedButton(text=ok_txt,
                                             md_bg_color=ok_color,
                                             on_press=lambda instance:sys.exit(0)),
                              MDRaisedButton(text=cal_txt,
                                             md_bg_color=cal_color,
                                             on_press=lambda instance:app.dismiss())])
        app.open()
    elif ok == [] and cal != []:
        cal=check_type(cal,list,["No",BLUE13])
        if len(cal) != 2:
            warnings.warn("\n[Easyapp_donError] Argument <cal>'s len must be 2.",UserWarning)
        cal_txt=str(cal[0]) if len(cal)>0 else "No"
        cal_color=cal[1] if len(cal)>1 else BLUE13
        app=MDDialog(title=str(tie),
                     text=str(t),
                     auto_dismiss=False,
                     buttons=[MDRaisedButton(text=cal_txt,
                                             md_bg_color=cal_color,
                                             on_press=lambda instance:app.dismiss())])
        app.open()
    elif ok != [] and cal == []:
        ok = check_type(ok, list, ["Yes", BLUE13])
        if len(ok) != 2:
            warnings.warn("\n[Easyapp_donError] Argument <ok>'s len must be 2.", UserWarning)
        ok_txt = str(ok[0]) if len(ok) > 0 else "No"
        ok_color = ok[1] if len(ok) > 1 else GREY13
        app = MDDialog(title=str(tie),
                       text=str(t),
                       auto_dismiss=False,
                       buttons=[MDRaisedButton(text=ok_txt,
                                               md_bg_color=ok_color,
                                               on_press=lambda instance: sys.exit(0))])
        app.open()
    else:
        app=MDDialog(title=str(tie),
                     text=str(t),
                     auto_dismiss=False,
                     buttons=[])
        app.open()
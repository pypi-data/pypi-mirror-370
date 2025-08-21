from easyapp_don.tools.colors import *
from easyapp_don.message.Msg import msg
from easyapp_don.message.EsMsg import esmsg
from easyapp_don.message.FillMsg import fillmsg
print("\nWelcome to the easyapp_don.message module!"
"\nWe have msg(), esmsg(), and fillmsg() functions here, which are very powerful."
"\n1. msg(): It can display a message box with default parameters that don't need to be filled in manually but can be completely modified. It has two buttons: ok and cancel. For details, please refer to the msg() function."
"\n2. esmsg(): It can display a message box with multiple texts. Other features are the same as the msg() function."
"\n3. fillmsg(): Based on msg() and esmsg(), it adds a checkbox parameter fs, making it easy to create electronic answer sheets!"
"\nFinally, don't plagiarize me. Watch out, I'll teach you a lesson!!!")



if __name__=='__main__':
    print("\n\n\n\n\n\n<<<<<<<<<<<<<--------------------------------------MainDemo-------------------------------------------->>>>>>>>>>>>")
    print("-------------------------------MainDemo of easyapp_don.message start-------------------------------\n")
    print("-------------------------------Demo of msg()---------------------------------------------\n\n\n\n\n\n")
    a = msg()
    print(f"\n\n\n\n\n\n---------------------The first page return: {a}--------------------------------\n\n\n\n\n\n")
    b = msg(t=[f"The last page returns:\n{a}",(0.5,0.6)],
              tie="Welcome to easyapp_don.message.Msg class!",
              color=PINK10,
              theme=DARK,
              cal=[],
              ok=["Next",GREEN6,(0.2,0.1),(0.5,0.15),"""True(You can ignore it)"""])
    print(f"\n\n\n\n\n\n----------------------The second page return: {b}----------------------------------")
    print("------------------------------Demo of msg() was successful--------------------------")
    print("------------------------------Demo of esmsg()---------------------------------------\n\n\n\n\n\n")
    c = esmsg()
    print(f"\n\n\n\n\n\n------------------------The third page return: {c}----------------------------------\n\n\n\n\n\n")
    f = esmsg(ts=[[f"The last page returns: \n{c}",(0.5,0.6)],
                  ["Welcome to easyapp_don.message.EsMsg class!",(0.5,0.05)]],
              tie="Welcome to easyapp_don.message.EsMsg class!",
              color=SILVER8,
              ok=["Next",GREEN6,(0.15,0.05),(0.5,0.15)],
              cal=[])
    print(f"\n\n\n\n\n\n-----------------------------The fourth page return: {f}----------------------------")
    print("-----------------------Demo of esmsg() was successful---------------------------------")
    print("-------------------------------Demo of fillmsg()--------------------------------------\n\n\n\n\n\n")
    g = fillmsg()
    print(f"\n\n\n\n\n\n--------------------------------The fifth page return: {g}----------------------------------------\n\n\n\n\n\n")
    h = fillmsg(ts=[[f"The last page returns: \n{g}",(0.5,0.6)],
                    ["Welcome to easyapp_don.message.FillMsg class!",(0.5,0.05)]],
                tie="Hello from easyapp_don.message.FillMsg class!",
                color=GOLD2,
                fs=[["Looking my eyes!",GOLD2,GREEN7,(0.2,0.05),(0.5,0.4)]],
                ok=["Bye",PINK10,(0.05,0.05),(0.5,0.3),True],
                cal=[],
            tip={"ok":[]})
    print(f"\n\n\n\n\n\n----------------------------------The sixth page return: {h}-----------------------------------")
    print("--------------------------Demo of fillmsg() was successful-------------------------------\n")
    print("---------------------------------------MainDemo end---------------------------------------------------")
    print("--------------------------------------easyapp_don.message MainDemo was successful-------------------------------------\n\n\n\n\n\n")
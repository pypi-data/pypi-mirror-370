from easyapp_don.button.Btn import btn
from easyapp_don.tools.colors import *
from easyapp_don.button.EsBtn import esbtn
from easyapp_don.button.FillBtn import fillbtn
if __name__ == '__main__':
    print("\n\n\n\n\n\n------------------MainDemo-------------------------------")
    print("---------------easyapp_don.button main demo start-----------------\n")
    print("---------------demo btn()-----------\n\n\n\n\n\n")
    a = btn()
    print(f"\n\n\n\n\n\n-------------- The first page return: {a} ,it is the index of btn().bs--------------\n\n\n\n\n\n")
    b = btn(t=[f"The first page return: \n{a}",(0.5,0.5)],
            theme=DARK,
            color=PINK10,
            bs=[["Next",GREEN6,(0.15,0.05),(0.5,0.1),True]],
            tie="Hello from easyapp_don.button's btn() class!")
    print(f"\n\n\n\n\n\n-----------------The second page return: {b}-----------------------------")
    print("---------------------------demo btn() was successful--------------------------------------")
    print("---------------demo esbtn()-----------------\n\n\n\n\n\n")
    c = esbtn()
    print(f"\n\n\n\n\n\n--------------------The second page return: {c}, it is the index of esbtn().bs-------------------\n\n\n\n\n\n")
    d = esbtn(ts=[[f"The third page return :\n{c}",(0.5,0.5)],
                  ["2/1",(0.5,0.05)]],
              theme=DARK,
              color=PINK10,
              tie="Hello from easyapp_don.button's esbtn() class!",
              bs=[["Next",GREEN7,(0.15,0.05),(0.5,0.15),True]])
    print(f"\n\n\n\n\n\n----------------------The fourth page return: {d}---------------------------------------")
    print("-----------------------------------demo esbtn() was successful--------------------------------------------")
    print("-------------------------demo fillbtn()-------------------------\n\n\n\n\n\n")
    f = fillbtn()
    print(f"\n\n\n\n\n\n--------------------The fifth page return: {f}----------------------------------")
    g = fillbtn(ts=[[f"The fifth page return: \n{f}",(0.5,0.5)]],
                color=GOLD2,
                tie="Hello from easyapp_don.button's fillbtn() class!",
                bs=[["Bye",GREEN7,(0.15,0.05),(0.5,0.1),True]],
                fs=[["Looking my eyes!",BROWN7,GOLD8,(0.2,0.05),(0.5,0.2)]])
    print(f"\n\n\n\n\n\n----------------------The sixth page return: {g}-----------------------------------------")
    print("--------------------------------------demo fillbtn() was successful---------------------------------------\n")
    print("----------------------------------------MainDemo end-------------------------------------------------------")
    print("-------------------------------------easyapp_don.buttons demo was successful---------------------------------------\n\n\n\n\n\n")
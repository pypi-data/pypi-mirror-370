if __name__ == '__main__':
    from easyapp_don.tools.colors import *
    from easyapp_don.image.Img import img
    from easyapp_don.image.ButtonImg import btn_img
    from easyapp_don.image.FillImg import fill_img
    from easyapp_don.image.FillButtonImg import fill_btn_img
    print("\n\n\n\n\n\n-------------------------------------MainDemo----------------------------------------")
    print("---------------------------------------Demo easyapp_don.image start-----------------------------------")
    print("\n-------------------------------------demo img()--------------------------------------------------")
    a = img()
    print(f"\n\n\n\n\n\n------------------------------Page1 return: {a}-------------------------------------------------\n\n\n\n\n\n")
    b = img(i=[["images/sky.png",(1,1),(0.5,0.5),0.6]],
            ts=[[f"Page1 return: \n{a}",(0.5,0.5)]],
            ok=["Next",GREEN6,(0.1,0.05),(0.5,0.1),True],
            cal=[],
            color=PINK10,
            tip={"ok":[]},
            tie="Welcome to easyapp_don.image's img() class!")
    print(f"\n\n\n\n\n\n----------------------------------Page2 return: {b}----------------------------------------------------------")
    print("----------------------------------------demo img() was successful------------------------------------------------------")
    print("------------------------------------------demo btn_img()------------------"
          "--------------------------------------------\n\n\n\n\n\n")
    c = btn_img()
    print(f"\n\n\n\n\n\n-------------------------------------Page3 return: {c}------------------------------------------"
          f"-----\n\n\n\n\n\n")
    d = btn_img(ts=[[f"Page3 return:\n {c}",(0.5,0.5)]],
                bi=[["images/n_btn.png",(0.2,0.12),(0.5,0.1),0.9]],
                tie="Welcome to easyapp_don.image's btn_img() class!",
                i=[["images/four_d.png",(1,1),(0.5,0.5),0.6]],
                ok=[],
                cal=[],
                tip={"ok":[]})
    print(f"\n\n\n\n\n\n-----------------------------Page4 return : {d}-----------------------------------")
    print("--------------------------------------demo btn_img() was successful-------------------------------------------")
    print("-----------------------------------demo fill_img()-----------------------------------------------\n\n\n\n\n\n")
    e = fill_img()
    print(f"\n\n\n\n\n\n--------------------------------Page5 return: {e}-----------------------------------------------\n\n\n\n\n\n")
    f = fill_img(ts=[[f"Page5 return: \n{e}",(0.5,0.5)]],
                 tie="Welcome to easyapp_don.image's fill_msg() class!",
                 i=[["images/four_d.png",(1,0.5),(0.5,0.75),0.8],
                    ["images/sky.png",(1,0.5),(0.5,0.25),0.8]],
                 ok=["Next",PINK8,(0.1,0.05),(0.5,0.1)],
                 cal=[],
                 tip={"ok":[]},
                 fs=[["Looking my eyes!",RED8,GOLD8,(0.2,0.05),(0.5,0.2)]],
                 theme=DARK)
    print(f"\n\n\n\n\n\n---------------------------Page6 return: {f}------------------------------------------")
    print("-----------------------------------------demo fill_img() was successful------------------------------------------")
    print("-----------------------------------------demo fill_btn_img()------------------------------------------------\n\n\n\n\n\n")
    g = fill_btn_img()
    print(f"\n\n\n\n\n\n-----------------------------Page7 return: {g}-------------------------------------------\n\n\n\n\n\n")
    h = fill_btn_img(ts=[[f"Page7 return: \n{g}",(0.5,0.5)]],
                     theme=DARK,
                     i=[["images/four_d.png",(1,1),(0.5,0.5),0.8]],
                     ok=["Bye",GREEN6,(0.15,0.05),(0.5,0.1),True],
                     cal=[],
                     tip={"ok":[]},
                     fi=[["images/dinos.png","images/gold.png",(0.05,0.05),(0.5,0.2)]],
                     bi=[["images/sky.png",(0.15,0.1),(0.5,0.3),1]],
                     fs=[],
                     tie="Welcome to easyapp_don.image's fill_btn_img() class!")
    print(f"\n\n\n\n\n\n--------------------------------Page8 return: {h}------------------------------------------")
    print("-------------------------------------------demo fill_btn_img() was successful-----------------------------------------")
    print("\n-----------------------------------easyapp_don.image demo end----------------------------------------------")
    print("-----------------------------------demo easyapp_don.images MainDemo was successful--------------------------------------------")
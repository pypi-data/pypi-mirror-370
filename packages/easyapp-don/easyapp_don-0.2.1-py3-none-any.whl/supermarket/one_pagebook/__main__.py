if __name__ == '__main__':
    from easyapp_don.tools.colors import *
    from easyapp_don.supermarket.one_pagebook.OnePagebook import page
    print("\n\n\n\n\n\n----------------------------MainDemo--------------------------------------")
    print("-----------------------------demo easyapp_don.supermarket.one_pagebook start----------------------------------")
    print("\n---------------------------------demo page()-----------------------------------------------\n\n\n\n\n\n")
    a = page()
    print(f"\n\n\n\n\n\n----------------------------Page1 return: {a}----------------------------------------------------\n\n\n\n\n\n")
    b = page(ts=[[f"Page1 return: \n{a}",(0.5,0.5)]],
             i=[["images/eto.png",(1,1),(0.5,0.5),0.6]],
             theme=DARK,
             bi=[["images/dinos.png",(0.05,0.1),(0.5,0.15),0.9,True]],
             bs=[],
             fs=[],
             es=[],
             fi=[],
             tie="Welcome to easyapp_don.supermarket.one_pagebook's page() class!",
             tip={"ok":[]})
    print(f"\n\n\n\n\n\n----------------------------------Page2 return: {b}-------------------------------------------")
    print("--------------------------------------------demo page() was successful---------------------------------------------\n")
    print("------------------------------------------demo easyapp_don.supermarket.one_pagebook end---------------------------------------")
    print("-----------------------------------easyapp_don.supermarket.one_pagebook MainDemo was successful-------------------------------"
          "---\n\n\n\n\n\n")
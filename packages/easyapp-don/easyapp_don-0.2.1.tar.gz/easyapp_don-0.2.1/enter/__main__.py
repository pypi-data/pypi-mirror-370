if __name__=='__main__':
    from easyapp_don.enter.Ent import ent
    from easyapp_don.enter.EsEnt import esent
    from easyapp_don.enter.FillEnt import fillent
    from easyapp_don.tools.colors import *
    print("\n\n\n\n\n\n----------------------------MainDemo-----------------------------")
    print("-----------------------------easyapp_don.enter demo start--------------------------------\n")
    print("-----------------------------demo ent()------------------------------\n\n\n\n\n\n")
    a = ent()
    print(f"\n\n\n\n\n\n-------------------Page1 return: {a}--------------------------------------\n\n\n\n\n\n")
    b = ent(t=[f"Page1 return: {a}"],
            e=["YourName:"],
            ok=["Next",GOLD8,(0.1,0.1),(0.5,0.1),True],
            cal=[],
            color=PINK10,
            theme=DARK,
            tie="Welcome to easyapp_don.enter's ent() class!")
    print(f"\n\n\n\n\n\n-------------------------Page2 return: {b}----------------------------------")
    print("-----------------------------------demo easyapp_don.enter's ent() was successful--------------------------------------------")
    print("-----------------------------------demo esent()------------------------------------------\n\n\n\n\n\n")
    c = esent()
    print(f"\n\n\n\n\n\n--------------------------------Page3 return: {c}-----------------------------------------\n\n\n\n\n\n")
    d = esent(theme=DARK,
              ts=[["Hello from easyapp_don!",(0.5,0.05)],
                  [f"Page3 return: {c}",(0.5,0.5)]],
              es=[["Your email: ",(0.8,0.1),(0.5,0.4)]],
              ok=["Next",RED8,(0.1,0.05),(0.5,0.3),True],
              cal=[],
              color=PINK10,
              tie="Welcome to easyapp_don.enter's esent() class!")
    print(f"\n\n\n\n\n\n--------------------------------------Page4 return: {d}-----------------------------------------------")
    print("----------------------------------------------demo easyapp_don.enter's esent() was successful-------------------------------------")
    print("-------------------------------------------demo fillent()-----------------------------------------\n\n\n\n\n\n")
    e = fillent()
    print(f"\n\n\n\n\n\n---------------------------------------Page5 return: {e}--------------------------------------\n\n\n\n\n\n")
    f = fillent(theme=DARK,
                ok=["Bye",GREEN2,(0.15,0.05),(0.5,0.1),True],
                cal=[],
                color=PINK10,
                es=[["Enter something.",(0.9,0.05),(0.5,0.5)]],
                fs=[["Looking my eyes!",GREY4,GOLD8,(0.2,0.05),(0.5,0.2)]],
                ts=[[f"Page5 return: {e}",(0.5,0.6)]],
                tie="Welcome to easyapp_don.enter's fillent() community!")
    print(f"\n\n\n\n\n\n------------------------------Page6 return: {f}------------------------------------------------")
    print("------------------------------------------demo easyapp_don.enter's fillent() was successful-------------------------------------\n")
    print("--------------------------------------easyapp_don.enter demo end--------------------------------------")
    print("-----------------------------------easyapp_don.enter MainDemo was successful-----------------------------------------------\n\n\n\n\n\n")
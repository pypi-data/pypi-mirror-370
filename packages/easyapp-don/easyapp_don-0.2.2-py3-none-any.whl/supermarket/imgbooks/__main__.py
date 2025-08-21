if __name__ == '__main__':
    from easyapp_don.supermarket.imgbooks.Imgbook import img_pages
    from easyapp_don.tools.colors import *
    print("-----MainDemo------")
    print("---------------demo img_pages()--------------")
    a = img_pages()
    print(f"---------Page1,2,3 return: {a}------------")
    b_pages={"Page0":{"tie":"Welcome to easyapp_don.supermarket.imgbooks.Imgbook's img_pages() class!",
                      "color":PINK8,
                      "i":[["images/sky.png",(1,1),(0.5,0.5),0.6]],
                      "bi":[],
                      "ts":[[f"Page1,2,3 return: \n{a}",(0.5,0.5)]],
                      "fs":[],
                      "bs":[["exit",RED8,(0.1,0.05),(0.5,0.1)]],
                      "fi":[],
                      "es":[]}}
    b = img_pages(b_pages)
    print(f"----------Page4 return: {b}-----------------")
    print("---------------demo img_pages() was successful-------------------")
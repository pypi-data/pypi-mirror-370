if __name__ == '__main__':
    from easyapp_don.tools.colors import *
    from easyapp_don.supermarket.pagebooks.Pagebook import pages
    print("\n\n\n\n\n\n---------------------------MainDemo-------------------------------")
    print("---------------------demo easyapp_don.supermarket.pagebooks---------------------------\n")
    print("----------------------demo pages()------------------")
    a = pages()
    print(f"\n\n\n\n\n\n----------------------Page1,2,3 return:\n {a}-----------------------------------------\n\n\n\n\n\n")
    t=("  Once upon a time,the Moon was not so beautiful as be is now.He was too _1_ to light up the sky."
       "No one was interested in him, _2_ he was very sad.\n\n"
       "  He turned to the stars and the flowers and said _3_, 'I wish I were a star or a flower.If I were a star, "
       "people would look up at me at night.If I could be a flower, young girls would come to enjoy my _4_.'\n\n"
       "  'We can't help you. We just twinkle in the dark night to make the sky _5_,'the stars answered.\n\n"
       "  The flowers _6_ sweetly and said,'We don't know how we can help you. We just live near the most beautiful _7_ "
       "in the world.Her name is Emma.Maybe you can ask her for some advice.\n\n"
       "  The Moon went to Emma.As soon as he saw her, he _8_ her.He went to see the girl every night,"
       "and his love touched Emma.The girl decided to live with the Moon forever.")
    b_page={"Page1":{"tie":"Welcome to easyapp_don.supermarket.pagebooks' pages() class!",
                     "ts":[[f"Page 1,2,3 return: \n{a}",(0.5,0.5)],
                           ["1/2",(0.5,0.05)]],
                     "bs":[],
                     "fs":[],
                     "es":[],
                     "tip":{"ok":[]}},
            "Page2":{"tie":"English Examination",
                     "color":PINK1,
                     "ts":[[t,(0.5,0.7)],
                           ["2/2",(0.5,0.05)],
                           ["1.",(0.05,0.425)],
                           ["2.",(0.05,0.35)],
                           ["3.",(0.05,0.275)],
                           ["4.",(0.05,0.2)],
                           ["5.",(0.55,0.425)],
                           ["6.",(0.55,0.35)],
                           ["7.",(0.55,0.275)],
                           ["8.",(0.55,0.2)]],
                     "fs":[["A.dark",GREY8,BLUE8,(0.075,0.025),(0.125,0.425)],
                           ["B.small",GREY8,BLUE8,(0.075,0.025),(0.275,0.425)],
                           ["C.round",GREY8,BLUE8,(0.075,0.025),(0.425,0.425)],
                           ["A.but",GREY8,BLUE8,(0.075,0.025),(0.125,0.35)],
                           ["B.though",GREY8,BLUE8,(0.075,0.025),(0.275,0.35)],
                           ["C.so",GREY8,BLUE8,(0.075,0.025),(0.425,0.35)],
                           ["A.excitedly",GREY8,BLUE8,(0.075,0.025),(0.125,0.275)],
                           ["B.unhappily",GREY8,BLUE8,(0.075,0.025),(0.275,0.275)],
                           ["C.life",GREY8,BLUE8,(0.075,0.025),(0.425,0.275)],
                           ["A.beauty",GREY8,BLUE8,(0.075,0.025),(0.125,0.2)],
                           ["B.light",GREY8,BLUE8,(0.075,0.025),(0.275,0.2)],
                           ["C.life",GREY8,BLUE8,(0.075,0.025),(0.425,0.2)],

                           ["A.higher",GREY8,BLUE8,(0.075,0.025),(0.625,0.425)],
                           ["B.clearer",GREY8,BLUE8,(0.075,0.025),(0.775,0.425)],
                           ["C.brighter",GREY8,BLUE8,(0.075,0.025),(0.925,0.425)],
                           ["A.jumped",GREY8,BLUE8,(0.075,0.025),(0.625,0.35)],
                           ["B.smiled",GREY8,BLUE8,(0.075,0.025),(0.775,0.35)],
                           ["C.reminded",GREY8,BLUE8,(0.075,0.025),(0.925,0.35)],
                           ["A.star",GREY8,BLUE8,(0.075,0.025),(0.625,0.275)],
                           ["B.flower",GREY8,BLUE8,(0.075,0.025),(0.775,0.275)],
                           ["C.girl",GREY8,BLUE8,(0.075,0.025),(0.925,0.275)],
                           ["A.fell in love",GREY8,BLUE8,(0.05,0.025),(0.7,0.2)],
                           ["B.took care of",GREY8,BLUE8,(0.05,0.025),(0.85,0.2)],
                           ["C.get on well with",GREY8,BLUE8,(0.05,0.025),(0.775,0.125)]],
                     "bs":[["Complete",GREEN8,(0.1,0.05),(0.5,0.12)]],
                     "es":[],
                     "tip":{"ok":[]},
                     "last":{"pos":(0.1,0.05)}}}
    b = pages(b_page)
    print(f"\n\n\n\n\n\n-----------------------------Page4,5 return: {b}-------------------------------------------------")
    print("--------------------------------demo pages() was successful--------------------------------------------------------\n")
    print("--------------------------------demo easyapp_don.supermarket.pagebooks end-------------------------------------------------")
    print("-----------------------------MainDemo was successful----------------------------\n\n\n\n\n\n")
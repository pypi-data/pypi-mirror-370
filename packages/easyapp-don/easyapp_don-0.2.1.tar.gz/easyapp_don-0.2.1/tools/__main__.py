print("\n\nWelcome to the tools module of the easyapp_don library!\n"
"Its functions are: 1. Define various colors and styles - there are 300 colors available for use, and 2 styles: LIGHT and DARK.\n"
" 2. Define methods such as variable type checking and parameter filling.\n"
" 3. Define a dialog() function that can pop up prompt boxes. For details, please import the easyapp_don.tools.EasyDialog file.\n"
" 4. Usage scenarios: It is often used only for setting colors and styles; other functions are suitable for other modules of easyapp_don and belong to internal modules.\n"
"Finally, if you have any questions, call me at 18803602392!")
if __name__=='__main__':
    from easyapp_don.tools.Manner import *
    from easyapp_don.tools.colors import *
    from easyapp_don.tools.EasyDialog import dialog
    from kivymd.app import MDApp
    from kivymd.uix.label import MDLabel
    from kivymd.uix.floatlayout import MDFloatLayout
    from kivymd.uix.button import MDRaisedButton
    from kivy.core.window import Window
    import sys
    class MannerApp(MDApp):
        def __init__(self):
            super().__init__()
            self.theme_cls.theme_style=DARK
            self.title="Welcome to easyapp_don.tools class!"
        def build(self):
            Window.bind(on_request_close=self.on_close)
            self.root=MDFloatLayout()
            self.root.md_bg_color=PINK10
            t=MDLabel(text="Hello,easyapp_don!",
                      halign="center",
                      valign="middle",
                      pos_hint={"center_x":0.5,"center_y":0.5})
            self.root.add_widget(t)
            b=MDRaisedButton(text="EXIT",
                             pos_hint={"center_x":0.5,"center_y":0.25},
                             size_hint=(0.15,0.05),
                             md_bg_color=PURPLE10,
                             on_press=lambda instance:self.stop())
            self.root.add_widget(b)
            return self.root
        def on_close(self,window,*args):
            dialog()
            return True
    print("\n\n\n\n------------------------------------Main-Demo------------------------------------------\n"
          "-----------------MainDemo-Of-easyapp_don.tools-Module------------------\n\n\n\n")
    MannerApp().run()
    print("\n\n\n--------------------------------------Main-Demo-End-----------------------------------------\n"
          "-----------------------------------------MainDemo was successful-----------------------------------------\n\n\n")
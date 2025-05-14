from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
MDScreenManager:
    MenuScreen:

<MenuScreen@MDScreen>:
    name: "menu"
    MDLabel:
        text: "Welcome"
        halign: "center"
'''

class TestApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

TestApp().run()

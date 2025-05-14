from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
MDScreenManager:
    Screen:
        name: 'one'
        MDRaisedButton:
            text: "Press me"
            pos_hint: {"center_x": .5, "center_y": .5}
    Screen:
        name: 'two'
'''

class TestApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == "__main__":
    TestApp().run()

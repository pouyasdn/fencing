from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
MDScreenManager:
    Screen:
        name: 'one'
    Screen:
        name: 'two'
'''

class TestApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == "__main__":
    TestApp().run()

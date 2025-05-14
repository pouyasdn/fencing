from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder

KV = '''
ScreenManager:
    FirstScreen:

<FirstScreen>:
    name: "first"
    Label:
        text: "This is the first screen"
'''

class TestApp(App):
    def build(self):
        return Builder.load_string(KV)

TestApp().run()

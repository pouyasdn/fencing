from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

KV = '''
ScreenManager:
    FirstScreen:

<FirstScreen>:
    name: "first"
    BoxLayout:
        orientation: "vertical"
        spacing: 10
        padding: 20

        Label:
            text: "Hello from ScreenManager!"
            font_size: 24

        Button:
            text: "Click Me"
            size_hint_y: None
            height: "48dp"
'''

class FirstScreen(Screen):
    pass

class MyApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    MyApp().run()

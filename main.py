from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
MDScreen:
    name: 'one'
    ScrollView:
        MDList:
            id: test_list
'''

class TestApp(MDApp):
    def build(self):
        screen = Builder.load_string(KV)
        from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget
        item = OneLineAvatarIconListItem(text="Alice")
        item.add_widget(IconLeftWidget(icon="account"))
        screen.ids.test_list.add_widget(item)
        return screen

if __name__ == "__main__":
    TestApp().run()

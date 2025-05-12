from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase
from kivy.app import App
import os
import sqlite3

# Register Material Icons font for icon buttons
here = os.path.dirname(__file__)
LabelBase.register(
    name="Icons",
    fn_regular=os.path.join(here, "MaterialIcons-Regular.ttf")
)

# Custom Header widget with title and back callback
class Header(BoxLayout):
    title = StringProperty('')
    back_callback = ObjectProperty(lambda *args: None)

KV = '''
<IconButton@Button>:
    size_hint: None, None
    size: dp(56), dp(56)
    background_normal: ''
    background_color: 0,0,0,0
    font_name: 'Icons'
    font_size: dp(24)

<RoundButton@Button>:
    size_hint: 0.8, None
    height: dp(60)
    font_size: '16sp'
    background_normal: ''
    background_color: 0.26,0.12,0.53,1
    color: 1,1,1,1
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<Header>:
    size_hint_y: None
    height: dp(56)
    canvas.before:
        Color:
            rgba: 0.26,0.12,0.53,1
        Rectangle:
            pos: self.pos
            size: self.size
    IconButton:
        text: '\ue5c4'  # arrow-left
        on_release: root.back_callback()
    Label:
        text: root.title
        color: 1,1,1,1
        valign: 'middle'
        halign: 'center'

ScreenManager:
    MenuScreen:
    SavedScreen:
    MatchScreen:
    SummaryScreen:
    RankingScreen:

<MenuScreen>:
    name: 'menu'
    FloatLayout:
        BoxLayout:
            orientation: 'vertical'
            padding: dp(12)
            spacing: dp(16)
            size_hint: 0.9,0.9
            pos_hint: {'center_x': .5, 'center_y': .5}
            Header:
                title: 'Fencing Tournament'
                back_callback: lambda *args: None
            BoxLayout:
                size_hint_y: None
                height: dp(56)
                spacing: dp(12)
                TextInput:
                    id: name_input
                    hint_text: 'Participant Name'
                    font_size: '16sp'
                    size_hint_x: .7
                IconButton:
                    text: '\ue7fe'  # account-plus
                    on_release: root.add_member(name_input.text)
                IconButton:
                    text: '\ue2c4'  # database-import
                    on_release: root.manager.current='saved'
            ScrollView:
                GridLayout:
                    id: member_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
            RoundButton:
                text: 'Start Tournament'
                disabled: len(root.members) < 2
                on_release: root.start_tournament()

<SavedScreen>:
    name: 'saved'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(16)
        Header:
            title: 'Saved Players'
            back_callback: lambda *args: app.back_to_menu()
        ScrollView:
            GridLayout:
                id: saved_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height

<MatchScreen>:
    name: 'match'
    FloatLayout:
        Header:
            id: top_bar
            title: 'Match'
            back_callback: lambda *args: app.back_to_menu()
        BoxLayout:
            orientation: 'vertical'
            size_hint: .9, None
            height: dp(260)
            pos_hint: {'center_x': .5, 'center_y': .6}
            canvas.before:
                Color:
                    rgba: 1,1,1,1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(12)]
            Label:
                id: match_label
                text: 'A vs B'
                font_size: '24sp'
                halign: 'center'
                valign: 'middle'
            BoxLayout:
                spacing: dp(12)
                size_hint_y: None
                height: dp(60)
                Button:
                    id: btn1
                    text: ''
                    on_release: root.select_winner(btn1.text)
                Button:
                    id: btn2
                    text: ''
                    on_release: root.select_winner(btn2.text)

<SummaryScreen>:
    name: 'summary'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(16)
        Header:
            title: 'Summary'
            back_callback: lambda *args: app.back_to_menu()
        ScrollView:
            GridLayout:
                id: summary_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        RoundButton:
            text: 'View Rankings'
            on_release: root.manager.current='ranking'

<RankingScreen>:
    name: 'ranking'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(16)
        Header:
            title: 'Rankings'
            back_callback: lambda *args: app.back_to_menu()
        ScrollView:
            GridLayout:
                id: rank_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        RoundButton:
            text: 'Back to Menu'
            on_release: app.back_to_menu()
'''

class MenuScreen(Screen):
    members = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect('players.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS players (name TEXT UNIQUE)')
        self.conn.commit()

    def add_member(self, name):
        name = name.strip()
        if not name or name in self.members:
            return
        self.members.append(name)
        self.ids.member_list.add_widget(self._make_member_item(name))

    def _make_member_item(self, name):
        box = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(12))
        box.add_widget(Label(text=name, halign='left'))
        del_btn = Button(text='\ue14c', font_name='Icons', size_hint_x=None, width=dp(48))
        del_btn.bind(on_release=lambda *a: self.perform_remove(box, name))
        save_btn = Button(text='\ue838', font_name='Icons', size_hint_x=None, width=dp(48))
        save_btn.bind(on_release=lambda *a: self.perform_save(save_btn, name))
        box.add_widget(del_btn)
        box.add_widget(save_btn)
        return box

    def perform_remove(self, widget, name):
        if name in self.members:
            self.members.remove(name)
        self.ids.member_list.remove_widget(widget)

    def perform_save(self, btn, name):
        self.cursor.execute('INSERT OR IGNORE INTO players (name) VALUES (?)', (name,))
        self.conn.commit()
        btn.text = '\ue838'

    def load_players(self):
        return [r[0] for r in self.cursor.execute('SELECT name FROM players')]

    def start_tournament(self):
        if len(self.members) < 2:
            return
        match = self.manager.get_screen('match')
        match.setup_matches(self.members[:])
        self.manager.current = 'match'

class SavedScreen(Screen):
    def on_enter(self):
        self.ids.saved_list.clear_widgets()
        menu = self.manager.get_screen('menu')
        for name in menu.load_players():
            box = menu._make_member_item(name)
            self.ids.saved_list.add_widget(box)

class MatchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.matches = []
        self.current_index = 0
        self.results = {}

    def setup_matches(self, members):
        self.matches = [(a, b) for i, a in enumerate(members) for b in members[i+1:]]
        self.current_index = 0
        self.results = {m: 0 for m in members}
        self.show_match()

    def show_match(self):
        a, b = self.matches[self.current_index]
        self.ids.match_label.text = f"{a} vs {b}"
        self.ids.btn1.text = f"{a} Wins"
        self.ids.btn2.text = f"{b} Wins"
        self.ids.top_bar.back_callback = lambda *args: app.back_to_menu()
        self.ids.top_bar.title = f"Match {self.current_index+1}/{len(self.matches)}"

    def select_winner(self, winner_text):
        w = winner_text.replace(" Wins", "")
        self.results[w] += 1
        self.current_index += 1
        if self.current_index >= len(self.matches):
            summ = self.manager.get_screen('summary')
            summ.display_summary(self.matches, self.results)
            self.manager.current = 'summary'
        else:
            self.show_match()

class SummaryScreen(Screen):
    def display_summary(self, matches, results):
        self.ids.summary_list.clear_widgets()
        for a, b in matches:
            if results[a] == results[b]:
                txt = 'Draw'
            else:
                txt = a if results[a] > results[b] else b
            box = BoxLayout(size_hint_y=None, height=dp(48))
            box.add_widget(Label(text=f"{a} vs {b} → {txt}"))
            self.ids.summary_list.add_widget(box)

class RankingScreen(Screen):
    def on_enter(self):
        self.ids.rank_list.clear_widgets()
        match_screen = self.manager.get_screen('match')
        for n, s in sorted(match_screen.results.items(), key=lambda x: -x[1]):
            box = BoxLayout(size_hint_y=None, height=dp(48))
            box.add_widget(Label(text=f"{n}: {s} wins"))
            self.ids.rank_list.add_widget(box)

class FencingApp(App):
    def build(self):
        global app
        app = self
        return Builder.load_string(KV)

    def back_to_menu(self):
        self.root.current = 'menu'

if __name__ == '__main__':
    FencingApp().run()

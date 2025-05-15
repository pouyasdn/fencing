from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as rgba
from kivy.properties import ListProperty
from kivy.uix.button import Button
import os, json

# آماده‌سازی JsonStore
DB_PATH = 'players_store.json'
if os.path.exists(DB_PATH):
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            json.load(f)
    except:
        os.remove(DB_PATH)
store = JsonStore(DB_PATH)

KV = '''
#:import rgba kivy.utils.get_color_from_hex
#:import dp kivy.metrics.dp

<ContentCard@BoxLayout>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.1
        RoundedRectangle:
            pos: self.x + 2, self.y - 2
            size: self.size
            radius: [12]
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]

<StyledButton@Button>:
    bg_color: rgba('#3F51B5')
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: '16sp'
    size_hint_y: None
    height: dp(48)
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]

ScreenManager:
    PlayerInputScreen:
    GameScreen:
    ResultsScreen:

<PlayerInputScreen>:
    name: 'input'
    player_list: player_list

    FloatLayout:
        canvas.before:
            Color:
                rgba: rgba('#ECEFF1')
            Rectangle:
                pos: self.pos
                size: self.size

        ContentCard:
            orientation: 'vertical'
            size_hint: 0.9, 0.85
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            padding: dp(20)
            spacing: dp(16)

            Label:
                text: 'Tournament Setup'
                font_size: '24sp'
                bold: True
                color: rgba('#263238')
                size_hint_y: None
                height: dp(32)
                halign: 'center'
                text_size: self.width, None

            BoxLayout:
                size_hint_y: None
                height: dp(48)
                spacing: dp(8)

                TextInput:
                    id: player_input
                    hint_text: 'Player name'
                    background_color: 1, 1, 1, 1
                    foreground_color: 0, 0, 0, 1
                    padding: [dp(12), dp(12)]
                    multiline: False

                StyledButton:
                    text: 'Add'
                    on_release: root.add_player(player_input.text)

            Label:
                text: 'Players:'
                font_size: '18sp'
                color: rgba('#37474F')
                size_hint_y: None
                height: dp(28)

            ScrollView:
                do_scroll_x: False
                do_scroll_y: True

                GridLayout:
                    id: player_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)

            StyledButton:
                text: 'Start Tournament'
                pos_hint: {'center_x': 0.5}
                on_release: root.start_tournament()

<GameScreen>:
    name: 'game'

    FloatLayout:
        canvas.before:
            Color:
                rgba: rgba('#ECEFF1')
            Rectangle:
                pos: self.pos
                size: self.size

        ContentCard:
            orientation: 'vertical'
            size_hint: 0.9, 0.6
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}
            padding: dp(20)
            spacing: dp(16)

            Label:
                id: match_label
                text: ''
                font_size: '22sp'
                bold: True
                color: rgba('#263238')
                size_hint_y: None
                height: dp(36)
                halign: 'center'
                text_size: self.width, None

            BoxLayout:
                spacing: dp(16)
                size_hint_y: None
                height: dp(48)

                StyledButton:
                    id: p1_btn
                    text: ''
                    on_release: root.submit_result(root.player1)

                StyledButton:
                    id: p2_btn
                    text: ''
                    on_release: root.submit_result(root.player2)

        StyledButton:
            text: 'Back'
            size_hint: None, None
            size: dp(100), dp(40)
            pos_hint: {'x': 0.05, 'y': 0.92}
            on_release: app.back_to_input()

<ResultsScreen>:
    name: 'results'

    FloatLayout:
        canvas.before:
            Color:
                rgba: rgba('#ECEFF1')
            Rectangle:
                pos: self.pos
                size: self.size

        ContentCard:
            orientation: 'vertical'
            size_hint: 0.9, 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            padding: dp(20)
            spacing: dp(16)

            Label:
                text: 'Final Standings'
                font_size: '24sp'
                bold: True
                color: rgba('#263238')
                size_hint_y: None
                height: dp(36)
                halign: 'center'
                text_size: self.width, None

            ScrollView:
                do_scroll_x: False
                do_scroll_y: True

                GridLayout:
                    id: standings_layout
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)

            Label:
                text: 'Match Results'
                font_size: '20sp'
                color: rgba('#37474F')
                size_hint_y: None
                height: dp(28)
                halign: 'center'
                text_size: self.width, None

            ScrollView:
                do_scroll_x: False
                do_scroll_y: True

                GridLayout:
                    id: results_layout
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)

            StyledButton:
                text: 'Back to Start'
                pos_hint: {'center_x': 0.5}
                on_release: app.back_to_input()
'''
class StyledButton(Button):
    bg_color = ListProperty([0.25, 0.4, 0.71, 1])  # مقدار پیش‌فرض rgba('#3F51B5')

class PlayerInputScreen(Screen):
    player_list = ObjectProperty(None)
    players = []

    def on_kv_post(self, *args):
        self.reload_players()

    def reload_players(self):
        self.players.clear()
        self.player_list.clear_widgets()
        for key in store.keys():
            name = store.get(key)['name']
            self.players.append(name)
            Clock.schedule_once(lambda dt, n=name: self._add_item(n), 0)

    def add_player(self, name):
        name = name.strip()
        if not name or name in self.players:
            return
        store.put(f"player_{name}", name=name)
        self.players.append(name)
        Clock.schedule_once(lambda dt: self._add_item(name), 0)
        self.ids.player_input.text = ''

    def _add_item(self, name):
        layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8), padding=[dp(8), 0])
        lbl = Label(text=name, color=(0.2, 0.2, 0.2, 1))
        btn_toggle = Factory.StyledButton(
            text='Unsave' if store.exists(f"player_{name}") else 'Save',
            bg_color=rgba('#F44336') if store.exists(f"player_{name}") else rgba('#4CAF50'),
            size_hint_x=None, width=dp(80), height=dp(36)
        )
        btn_toggle.bind(on_release=lambda btn, nm=name: self.toggle_save(btn, nm))
        btn_del = Factory.StyledButton(
            text='Delete',
            bg_color=rgba('#9E9E9E'),
            size_hint_x=None, width=dp(80), height=dp(36)
        )
        btn_del.bind(on_release=lambda btn, nm=name, w=layout: self.delete_player(w, nm))
        layout.add_widget(lbl)
        layout.add_widget(btn_toggle)
        layout.add_widget(btn_del)
        self.player_list.add_widget(layout)

    def toggle_save(self, btn, name):
        key = f"player_{name}"
        if store.exists(key):
            store.delete(key)
            btn.text = 'Save'
            btn.bg_color = rgba('#4CAF50')
        else:
            store.put(key, name=name)
            btn.text = 'Unsave'
            btn.bg_color = rgba('#F44336')

    def delete_player(self, widget, name):
        key = f"player_{name}"
        if store.exists(key):
            store.delete(key)
        if name in self.players:
            self.players.remove(name)
        self.player_list.remove_widget(widget)

    def start_tournament(self):
        if len(self.players) < 2:
            return
        app = App.get_running_app()
        app.players = list(self.players)
        app.matches = [
            (app.players[i], app.players[j])
            for i in range(len(app.players)) for j in range(i+1, len(app.players))
        ]
        app.results = []
        app.scores = {n: 0 for n in app.players}
        app.current_match = 0
        self.manager.current = 'game'
        self.manager.get_screen('game').load_match()

class GameScreen(Screen):
    player1 = ''
    player2 = ''

    def load_match(self):
        app = App.get_running_app()
        if app.current_match >= len(app.matches):
            self.manager.current = 'results'
            return
        self.player1, self.player2 = app.matches[app.current_match]
        self.ids.match_label.text = f"{self.player1} vs {self.player2}"
        self.ids.p1_btn.text = f"{self.player1} Wins"
        self.ids.p2_btn.text = f"{self.player2} Wins"

    def submit_result(self, winner):
        app = App.get_running_app()
        app.results.append((self.player1, self.player2, winner))
        app.scores[winner] += 1
        app.current_match += 1
        self.load_match()

class ResultsScreen(Screen):
    def on_enter(self):
        self.ids.standings_layout.clear_widgets()
        self.ids.results_layout.clear_widgets()
        app = App.get_running_app()
        for name, sc in sorted(app.scores.items(), key=lambda x: x[1], reverse=True):
            self.ids.standings_layout.add_widget(
                Label(text=f"{name}: {sc} wins", size_hint_y=None, height=dp(30), color=(0.2, 0.2, 0.2, 1))
            )
        for p1, p2, w in app.results:
            self.ids.results_layout.add_widget(
                Label(text=f"{p1} vs {p2} - Winner: {w}", size_hint_y=None, height=dp(30), color=(0.2, 0.2, 0.2, 1))
            )

class FencingApp(App):
    def build(self):
        return Builder.load_string(KV)

    def back_to_input(self):
        screen = self.root.get_screen('input')
        screen.reload_players()
        self.root.current = 'input'

if __name__ == '__main__':
    FencingApp().run()

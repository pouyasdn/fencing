from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.properties import StringProperty, ListProperty
from kivy.metrics import dp
import sqlite3

# Set a reasonable default size
Window.size = (360, 640)

KV = '''
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        MDLabel:
            text: 'Players'
            font_style: 'H6'
            halign: 'center'

        ScrollView:
            size_hint_y: None
            height: root.height * 0.6
            MDList:
                id: player_list

        BoxLayout:
            size_hint_y: None
            height: dp(56)
            spacing: dp(8)

            MDTextField:
                id: name_input
                hint_text: 'New player name'
                mode: 'rectangle'

            MDFillRoundFlatButton:
                text: '+'
                size_hint_x: None
                width: dp(56)
                on_release: root.add_player(name_input.text)

        MDFillRoundFlatButton:
            text: 'Start Tournament'
            size_hint_y: None
            height: dp(48)
            pos_hint: {'center_x': .5}
            on_release: root.start_tournament()
            disabled: len(root.players) < 2

<SavedScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        MDTopAppBar:
            title: 'Saved Players'
            left_action_items: [['arrow-left', lambda x: app.back_to_menu()]]

        ScrollView:
            MDList:
                id: saved_list

<GameScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)

        MDLabel:
            id: match_label
            text: root.player1 + ' vs ' + root.player2
            font_style: 'H5'
            halign: 'center'

        MDFillRoundFlatButton:
            text: root.player1 + ' wins'
            on_release: root.submit_result(root.player1)

        MDFillRoundFlatButton:
            text: root.player2 + ' wins'
            on_release: root.submit_result(root.player2)

<ResultsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        MDLabel:
            text: 'Final Standings'
            font_style: 'H6'
            halign: 'left'

        ScrollView:
            size_hint_y: None
            height: root.height * 0.4
            MDList:
                id: standings_list
                padding: [dp(8), 0]
                spacing: dp(4)

        MDLabel:
            text: 'Match Results'
            font_style: 'H6'
            halign: 'left'

        ScrollView:
            size_hint_y: None
            height: root.height * 0.5
            MDList:
                id: results_list
                padding: [dp(8), 0]
                spacing: dp(4)
'''

class MenuScreen(MDScreen):
    players = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize SQLite
        self.conn = sqlite3.connect('players.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS players (name TEXT UNIQUE)')
        self.conn.commit()

    def on_enter(self):
        self.ids.player_list.clear_widgets()
        for name in self.players:
            self.add_player_item(name)

    def add_player(self, name):
        name = name.strip()
        if not name or name in self.players:
            return
        self.players.append(name)
        self.add_player_item(name)
        self.ids.name_input.text = ''

    def add_player_item(self, name):
        item = OneLineAvatarIconListItem(text=name)
        item.add_widget(IconLeftWidget(icon='account'))
        # Delete button
        del_btn = IconRightWidget(icon='delete')
        del_btn.on_release = lambda x, it=item, nm=name: self.remove_player(it, nm)
        item.add_widget(del_btn)
        # Save button
        save_btn = IconRightWidget(icon='star-outline')
        save_btn.on_release = lambda x, btn=save_btn, nm=name: self.toggle_save(btn, nm)
        item.add_widget(save_btn)
        self.ids.player_list.add_widget(item)

    def remove_player(self, item, name):
        if name in self.players:
            self.players.remove(name)
        self.ids.player_list.remove_widget(item)

    def toggle_save(self, btn, name):
        if btn.icon == 'star-outline':
            self.cursor.execute('INSERT OR IGNORE INTO players (name) VALUES (?)', (name,))
            self.conn.commit()
            btn.icon = 'star'
        else:
            self.cursor.execute('DELETE FROM players WHERE name=?', (name,))
            self.conn.commit()
            btn.icon = 'star-outline'

    def start_tournament(self):
        if len(self.players) < 2:
            Popup(title='Error', content=Label(text='At least 2 players required'), size_hint=(None, None), size=(dp(300), dp(200))).open()
        else:
            game_screen = self.manager.get_screen('game')
            game_screen.setup_matches(self.players)
            self.manager.transition = NoTransition()
            self.manager.current = 'game'

class SavedScreen(MDScreen):
    def on_enter(self):
        self.ids.saved_list.clear_widgets()
        menu = self.manager.get_screen('menu')
        for (name,) in menu.cursor.execute('SELECT name FROM players'):
            item = OneLineAvatarIconListItem(text=name)
            # Add back button
            add_btn = IconRightWidget(icon='account-plus')
            add_btn.on_release = lambda x, nm=name: self.add_back(nm)
            item.add_widget(add_btn)
            # Delete from saved
            del_btn = IconRightWidget(icon='delete')
            del_btn.on_release = lambda x, nm=name: self.delete_saved(nm)
            item.add_widget(del_btn)
            self.ids.saved_list.add_widget(item)

    def add_back(self, name):
        menu = self.manager.get_screen('menu')
        menu.add_player(name)
        self.manager.current = 'menu'

    def delete_saved(self, name):
        menu = self.manager.get_screen('menu')
        menu.cursor.execute('DELETE FROM players WHERE name=?', (name,))
        menu.conn.commit()
        self.on_enter()

class GameScreen(MDScreen):
    player1 = StringProperty('')
    player2 = StringProperty('')

    def setup_matches(self, names):
        self.games = [(a, b) for i, a in enumerate(names) for b in names[i+1:]]
        self.results = []
        self.current_index = 0
        self.on_enter()

    def on_enter(self):
        if hasattr(self, 'games') and self.current_index < len(self.games):
            a, b = self.games[self.current_index]
            self.player1, self.player2 = a, b
            self.ids.match_label.text = f"{a} vs {b}"
        else:
            self.manager.current = 'results'

    def submit_result(self, winner):
        self.results.append((self.player1, self.player2, winner))
        self.current_index += 1
        self.on_enter()

class ResultsScreen(MDScreen):
    def on_enter(self):
        menu = self.manager.get_screen('menu')
        players = menu.players
        scores = {p: 0 for p in players}
        for a, b, w in self.manager.get_screen('game').results:
            scores[w] += 1
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.ids.standings_list.clear_widgets()
        for name, score in sorted_scores:
            self.ids.standings_list.add_widget(OneLineAvatarIconListItem(text=f"{name}: {score} wins"))
        self.ids.results_list.clear_widgets()
        for a, b, w in self.manager.get_screen('game').results:
            self.ids.results_list.add_widget(OneLineAvatarIconListItem(text=f"{a} vs {b} → {w}"))

class TournamentApp(MDApp):
    def build(self):
        Builder.load_string(KV)
        sm = MDScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SavedScreen(name='saved'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ResultsScreen(name='results'))
        sm.current = 'menu'
        return sm

if __name__ == '__main__':
    TournamentApp().run()

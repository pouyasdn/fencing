from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import NoTransition

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.list import MDList, OneLineAvatarIconListItem
from kivy.properties import StringProperty, ListProperty

Window.size = (360, 640)

KV = '''
<PlayerInputScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 16
        spacing: 16

        Label:
            text: 'Enter player names (at least 3):'
            font_size: 18
            size_hint_y: None
            height: self.texture_size[1]

        TextInput:
            id: player_input
            multiline: True
            hint_text: 'One name per line'
            font_size: 16
            size_hint_y: None
            height: 150

        Button:
            text: 'Start Tournament'
            size_hint_y: None
            height: 50
            on_press: root.start_tournament()

<GameScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 16
        spacing: 20

        Label:
            id: match_label
            text: root.player1 + ' vs ' + root.player2
            font_size: 20
            size_hint_y: None
            height: 40

        Button:
            text: root.player1 + ' wins'
            font_size: 16
            size_hint_y: None
            height: 50
            on_press: root.submit_result(root.player1)

        Button:
            text: root.player2 + ' wins'
            font_size: 16
            size_hint_y: None
            height: 50
            on_press: root.submit_result(root.player2)

<ResultsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 16
        spacing: 16

        Label:
            text: 'Final Standings'
            font_size: 20
            size_hint_y: None
            height: 30

        ScrollView:
            size_hint_y: None
            height: root.height * 0.4
            MDList:
                id: standings_list

        Label:
            text: 'Match Results'
            font_size: 18
            size_hint_y: None
            height: 30

        ScrollView:
            size_hint_y: None
            height: root.height * 0.5
            MDList:
                id: results_list
'''

class PlayerInputScreen(MDScreen):
    def start_tournament(self):
        text = self.ids.player_input.text
        names = [n.strip() for n in text.split('\n') if n.strip()]
        if len(names) < 3:
            Popup(title='Error', content=Label(text='Please enter at least 3 players.'),
                  size_hint=(None, None), size=(300, 200)).open()
        else:
            self.manager.players = names
            self.manager.games = [(a, b) for i, a in enumerate(names) for b in names[i+1:]]
            self.manager.results = []
            self.manager.current_game_index = 0
            self.manager.transition = NoTransition()
            self.manager.current = 'game'

class GameScreen(MDScreen):
    player1 = StringProperty('')
    player2 = StringProperty('')

    def on_enter(self):
        idx = self.manager.current_game_index
        if idx < len(self.manager.games):
            a, b = self.manager.games[idx]
            self.player1, self.player2 = a, b
            self.ids.match_label.text = f"{a} vs {b}"
        else:
            self.manager.transition = NoTransition()
            self.manager.current = 'results'

    def submit_result(self, winner):
        a, b = self.player1, self.player2
        self.manager.results.append((a, b, winner))
        self.manager.current_game_index += 1
        self.on_enter()

class ResultsScreen(MDScreen):
    standings = ListProperty()

    def on_enter(self):
        scores = {p: 0 for p in self.manager.players}
        for a, b, w in self.manager.results:
            scores[w] += 1
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.ids.standings_list.clear_widgets()
        for name, score in sorted_scores:
            self.ids.standings_list.add_widget(
                OneLineAvatarIconListItem(text=f"{name}: {score} wins")
            )
        self.ids.results_list.clear_widgets()
        for a, b, w in self.manager.results:
            self.ids.results_list.add_widget(
                OneLineAvatarIconListItem(text=f"{a} vs {b} → {w}")
            )

class TournamentApp(MDApp):
    def build(self):
        Builder.load_string(KV)
        sm = MDScreenManager()
        sm.add_widget(PlayerInputScreen(name='input'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ResultsScreen(name='results'))
        sm.current = 'input'
        return sm

if __name__ == '__main__':
    TournamentApp().run()

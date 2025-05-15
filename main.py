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
from kivy.metrics import dp

# Set a reasonable default size (useful in mobile testing environments)
Window.size = (360, 640)

KV = '''
<PlayerInputScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)

        MDLabel:
            text: 'Enter player names (at least 3):'
            font_style: 'H6'
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: player_input
            multiline: True
            hint_text: 'One name per line'
            size_hint_y: None
            height: dp(150)
            mode: 'rectangle'

        MDFillRoundFlatButton:
            text: 'Start Tournament'
            size_hint_y: None
            height: dp(50)
            pos_hint: {'center_x': .5}
            on_release: root.start_tournament()

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
            size_hint_y: None
            height: dp(40)

        MDFillRoundFlatButton:
            text: root.player1 + ' wins'
            size_hint_y: None
            height: dp(50)
            on_release: root.submit_result(root.player1)

        MDFillRoundFlatButton:
            text: root.player2 + ' wins'
            size_hint_y: None
            height: dp(50)
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
            size_hint_y: None
            height: dp(30)

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
            size_hint_y: None
            height: dp(30)

        ScrollView:
            size_hint_y: None
            height: root.height * 0.5
            MDList:
                id: results_list
                padding: [dp(8), 0]
                spacing: dp(4)
'''

class PlayerInputScreen(MDScreen):
    def start_tournament(self):
        names = [n.strip() for n in self.ids.player_input.text.split('\n') if n.strip()]
        if len(names) < 3:
            Popup(
                title='Error', content=Label(text='Please enter at least 3 players.'),
                size_hint=(None, None), size=(dp(300), dp(200))
            ).open()
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
        # Calculate scores
        scores = {p: 0 for p in self.manager.players}
        for a, b, w in self.manager.results:
            scores[w] += 1
        # Sort standings
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Populate standings list
        self.ids.standings_list.clear_widgets()
        for name, score in sorted_scores:
            item = OneLineAvatarIconListItem(text=f"{name}: {score} wins")
            self.ids.standings_list.add_widget(item)

        # Populate match results list
        self.ids.results_list.clear_widgets()
        for a, b, w in self.manager.results:
            item = OneLineAvatarIconListItem(text=f"{a} vs {b} → Winner: {w}")
            self.ids.results_list.add_widget(item)

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

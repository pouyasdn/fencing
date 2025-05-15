from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager, NoTransition
from kivy.uix.scrollview import ScrollView

# Set a reasonable default size (useful in mobile testing environments)
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
            GridLayout:
                id: standings_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 8
                padding: [0, 0, 0, 10]

        Label:
            text: 'Match Results'
            font_size: 18
            size_hint_y: None
            height: 30

        ScrollView:
            size_hint_y: None
            height: root.height * 0.5
            GridLayout:
                id: results_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 6
'''

class PlayerInputScreen(MDScreen):
    def start_tournament(self):
        input_text = self.ids.player_input.text
        names = [n.strip() for n in input_text.split('\n') if n.strip()]
        if len(names) < 3:
            popup = Popup(
                title='Error', content=Label(text='Please enter at least 3 players.'),
                size_hint=(None, None), size=(300, 200)
            )
            popup.open()
        else:
            self.manager.players = names
            self.manager.games = self.generate_games(names)
            self.manager.results = []
            self.manager.current_game_index = 0
            self.manager.transition = NoTransition()
            self.manager.current = 'game'

    def generate_games(self, players):
        games = []
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                games.append((players[i], players[j]))
        return games

class GameScreen(MDScreen):
    player1 = StringProperty('')
    player2 = StringProperty('')

    def on_enter(self):
        if self.manager.current_game_index < len(self.manager.games):
            p1, p2 = self.manager.games[self.manager.current_game_index]
            self.player1, self.player2 = p1, p2
            self.ids.match_label.text = f"{p1} vs {p2}"
        else:
            self.manager.transition = NoTransition()
            self.manager.current = 'results'

    def submit_result(self, winner):
        self.manager.results.append((self.player1, self.player2, winner))
        self.manager.current_game_index += 1
        self.on_enter()

class ResultsScreen(MDScreen):
    standings = ListProperty()

    def on_enter(self):
        scores = {p: 0 for p in self.manager.players}
        for p1, p2, winner in self.manager.results:
            scores[winner] += 1

        sorted_players = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.standings = sorted_players

        self.ids.standings_layout.clear_widgets()
        for name, score in sorted_players:
            self.ids.standings_layout.add_widget(
                Label(text=f"{name}: {score} wins", font_size=16, size_hint_y=None, height=30)
            )

        self.ids.results_layout.clear_widgets()
        for p1, p2, winner in self.manager.results:
            self.ids.results_layout.add_widget(
                Label(text=f"{p1} vs {p2} → Winner: {winner}", font_size=14, size_hint_y=None, height=24)
            )

class TournamentApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    TournamentApp().run()

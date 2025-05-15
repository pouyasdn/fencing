from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.uix.label import Label

KV = '''
<StyledScreen@Screen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1  # Light background
        Rectangle:
            pos: self.pos
            size: self.size

ScreenManager:
    PlayerInputScreen:
    GameScreen:
    ResultsScreen:

<PlayerInputScreen>:
    name: 'input'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10

        canvas.before:
            Color:
                rgba: 1, 1, 1, 1  # سفید
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: 'Enter player names (one per line, min 3):'
            size_hint_y: None
            height: '30dp'
            color: 0, 0, 0, 1  # مشکی

        TextInput:
            id: player_input
            multiline: True
            size_hint_y: None
            height: '150dp'
            background_color: 1, 1, 1, 1  # سفید
            foreground_color: 0, 0, 0, 1  # مشکی
            hint_text: 'Player Names'

        Button:
            text: 'Start Tournament'
            size_hint_y: None
            height: '40dp'
            background_color: 0.2, 0.4, 0.8, 1
            color: 1, 1, 1, 1
            on_release: root.start_tournament()


<GameScreen@StyledScreen>:
    name: 'game'
    player1: ''
    player2: ''
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10

        Label:
            id: match_label
            text: root.player1 + " vs " + root.player2
            font_size: '20sp'
            size_hint_y: None
            height: '40dp'
            color: 0, 0, 0, 1

        Button:
            text: root.player1 + ' Wins'
            size_hint_y: None
            height: '40dp'
            background_color: 0.2, 0.6, 0.4, 1
            color: 1, 1, 1, 1
            on_release: root.submit_result(root.player1)

        Button:
            text: root.player2 + ' Wins'
            size_hint_y: None
            height: '40dp'
            background_color: 0.7, 0.2, 0.2, 1
            color: 1, 1, 1, 1
            on_release: root.submit_result(root.player2)

<ResultsScreen@StyledScreen>:
    name: 'results'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10

        Label:
            text: 'Final Standings'
            size_hint_y: None
            height: '30dp'
            color: 0, 0, 0, 1

        ScrollView:
            GridLayout:
                id: standings_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 5

        Label:
            text: 'Match Results'
            size_hint_y: None
            height: '30dp'
            color: 0, 0, 0, 1

        ScrollView:
            GridLayout:
                id: results_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
'''


class PlayerInputScreen(Screen):
    def start_tournament(self):
        input_text = self.ids.player_input.text
        names = [name.strip() for name in input_text.split('\n') if name.strip()]
        if len(names) < 3:
            print("❌ Please enter at least 3 players.")
            return

        self.manager.players = names
        self.manager.games = self.generate_games(names)
        self.manager.results = []
        self.manager.current_game_index = 0
        self.manager.current = 'game'

    def generate_games(self, players):
        games = []
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                games.append((players[i], players[j]))
        return games


class GameScreen(Screen):
    player1 = StringProperty()
    player2 = StringProperty()

    def on_enter(self):
        if self.manager.current_game_index < len(self.manager.games):
            game = self.manager.games[self.manager.current_game_index]
            self.player1, self.player2 = game
        else:
            self.manager.current = 'results'

    def submit_result(self, winner):
        self.manager.results.append((self.player1, self.player2, winner))
        self.manager.current_game_index += 1
        self.on_enter()


class ResultsScreen(Screen):
    def on_enter(self):
        self.ids.standings_layout.clear_widgets()
        self.ids.results_layout.clear_widgets()

        scores = {player: 0 for player in self.manager.players}
        for p1, p2, winner in self.manager.results:
            scores[winner] += 1

        sorted_players = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for name, score in sorted_players:
            self.ids.standings_layout.add_widget(Label(
                text=f"{name}: {score} wins",
                size_hint_y=None,
                height=30,
                color=(0, 0, 0, 1)
            ))

        for p1, p2, winner in self.manager.results:
            self.ids.results_layout.add_widget(Label(
                text=f"{p1} vs {p2} → Winner: {winner}",
                size_hint_y=None,
                height=30,
                color=(0, 0, 0, 1)
            ))


class FencingApp(App):
    def build(self):
        sm = Builder.load_string(KV)
        sm.players = []
        sm.games = []
        sm.results = []
        sm.current_game_index = 0
        return sm


if __name__ == '__main__':
    FencingApp().run()

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.metrics import dp

KV = '''
ScreenManager:
    PlayerInputScreen:
    GameScreen:
    ResultsScreen:

<PlayerInputScreen>:
    name: 'input'
    FloatLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(20)
            size_hint: 0.9, 0.7
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            canvas.before:
                Color:
                    rgba: 0.96, 0.96, 0.96, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [12]

            Label:
                text: 'Tournament Setup'
                font_size: '24sp'
                size_hint_y: None
                height: dp(40)
                color: 0, 0, 0, 1

            Label:
                text: 'Enter player name:'
                size_hint_y: None
                height: dp(30)
                color: 0, 0, 0, 1

            TextInput:
                id: player_input
                multiline: False
                size_hint_y: None
                height: dp(40)
                hint_text: 'Player name'
                background_color: 1, 1, 1, 1
                foreground_color: 0, 0, 0, 1

            Button:
                text: 'Add'
                size_hint_y: None
                height: dp(40)
                on_release: root.add_player()

            Label:
                text: 'Players:'
                size_hint_y: None
                height: dp(30)
                color: 0, 0, 0, 1

            ScrollView:
                size_hint_y: 1
                do_scroll_x: False

                GridLayout:
                    id: player_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: dp(30)
                    row_force_default: True

            Button:
                text: 'Start Tournament'
                size_hint_y: None
                height: dp(50)
                on_release: root.start_tournament()


<GameScreen>:
    name: 'game'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: 'Match Play'
            font_size: '24sp'
            size_hint_y: None
            height: dp(40)
            color: 0, 0, 0, 1

        Label:
            id: match_label
            text: ''
            font_size: '20sp'
            size_hint_y: None
            height: dp(40)
            color: 0, 0, 0, 1

        BoxLayout:
            spacing: dp(10)
            size_hint_y: None
            height: dp(50)

            Button:
                id: p1_btn
                text: ''
                on_release: root.submit_result(root.player1)

            Button:
                id: p2_btn
                text: ''
                on_release: root.submit_result(root.player2)


<ResultsScreen>:
    name: 'results'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: 'Final Standings'
            font_size: '24sp'
            size_hint_y: None
            height: dp(40)
            color: 0, 0, 0, 1

        ScrollView:
            GridLayout:
                id: standings_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: dp(30)
                row_force_default: True

        Label:
            text: 'Match Results'
            font_size: '20sp'
            size_hint_y: None
            height: dp(30)
            color: 0, 0, 0, 1

        ScrollView:
            GridLayout:
                id: results_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: dp(30)
                row_force_default: True

        Button:
            text: 'Back to Start'
            size_hint_y: None
            height: dp(50)
            on_release: app.back_to_input()
'''

class PlayerInputScreen(Screen):
    players = []

    def add_player(self):
        name = self.ids.player_input.text.strip()
        if name:
            self.players.append(name)
            self.ids.player_list.add_widget(Label(
                text=name, size_hint_y=None, height=dp(30), color=(0, 0, 0, 1)
            ))
            self.ids.player_input.text = ''

    def start_tournament(self):
        if len(self.players) < 2:
            return
        app = App.get_running_app()
        app.players = self.players[:]
        app.matches = [(app.players[i], app.players[j]) for i in range(len(app.players)) for j in range(i+1, len(app.players))]
        app.results = []
        app.scores = {name: 0 for name in app.players}
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
            self.manager.get_screen('results').on_enter()
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
        sorted_scores = sorted(app.scores.items(), key=lambda x: x[1], reverse=True)
        for name, sc in sorted_scores:
            lbl = Label(text=f"{name}: {sc} wins", size_hint_y=None, height=dp(30), color=(0,0,0,1))
            self.ids.standings_layout.add_widget(lbl)

        for p1, p2, winner in app.results:
            lbl = Label(text=f"{p1} vs {p2} - Winner: {winner}", size_hint_y=None, height=dp(30), color=(0,0,0,1))
            self.ids.results_layout.add_widget(lbl)


class FencingApp(App):
    def build(self):
        return Builder.load_string(KV)

    def back_to_input(self):
        self.root.get_screen('input').players = []
        self.root.get_screen('input').ids.player_list.clear_widgets()
        self.root.current = 'input'


if __name__ == '__main__':
    FencingApp().run()

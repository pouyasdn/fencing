from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

# اندازه پیش‌فرض موبایل
Window.size = (360, 640)

KV = '''
ScreenManager:
    PlayerInputScreen:
    GameScreen:
    ResultsScreen:

<PlayerInputScreen>:
    name: 'input'
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)
        md_bg_color: app.theme_cls.bg_normal

        MDTopAppBar:
            title: 'Tournament Setup'
            elevation: 4

        MDCard:
            orientation: 'vertical'
            padding: dp(12)
            spacing: dp(12)
            size_hint: 0.95, None
            height: dp(250)
            pos_hint: {'center_x': 0.5}

            MDLabel:
                text: 'Enter player names (one per line, min 3):'
                font_style: 'Subtitle1'
                size_hint_y: None
                height: self.texture_size[1]

            MDTextField:
                id: player_input
                hint_text: 'Player Name'
                multiline: True
                size_hint_y: None
                height: dp(120)

        MDRaisedButton:
            text: 'Start Tournament'
            pos_hint: {'center_x': 0.5}
            size_hint: 0.6, None
            height: dp(48)
            on_release: root.start_tournament()

<GameScreen>:
    name: 'game'
    player1: ''
    player2: ''
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(20)
        md_bg_color: app.theme_cls.bg_normal

        MDTopAppBar:
            title: 'Match Play'
            left_action_items: [['arrow-left', lambda x: app.back_to_input()]]
            elevation: 4

        MDCard:
            orientation: 'vertical'
            padding: dp(16)
            size_hint: 0.9, None
            height: dp(120)
            pos_hint: {'center_x': 0.5}

            MDLabel:
                id: match_label
                text: root.player1 + ' vs ' + root.player2
                font_style: 'H5'
                halign: 'center'

        MDBoxLayout:
            spacing: dp(16)
            size_hint_y: None
            height: dp(60)
            pos_hint: {'center_x': 0.5}

            MDRaisedButton:
                text: root.player1 + ' Wins'
                on_release: root.submit_result(root.player1)

            MDRaisedButton:
                text: root.player2 + ' Wins'
                on_release: root.submit_result(root.player2)

<ResultsScreen>:
    name: 'results'
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)
        md_bg_color: app.theme_cls.bg_normal

        MDTopAppBar:
            title: 'Results'
            left_action_items: [['arrow-left', lambda x: app.back_to_input()]]
            elevation: 4

        MDLabel:
            text: 'Final Standings'
            font_style: 'Subtitle1'
            size_hint_y: None
            height: dp(30)

        ScrollView:
            size_hint_y: 0.4
            MDList:
                id: standings_layout

        MDLabel:
            text: 'Match Results'
            font_style: 'Subtitle1'
            size_hint_y: None
            height: dp(30)

        ScrollView:
            size_hint_y: 0.5
            MDList:
                id: results_layout
'''


class PlayerInputScreen(MDScreen):
    def start_tournament(self):
        input_text = self.ids.player_input.text
        names = [name.strip() for name in input_text.split('\n') if name.strip()]
        if len(names) < 3:
            MDDialog(
                title="Error",
                text="Please enter at least 3 players.",
                buttons=[MDRaisedButton(text="OK", on_release=lambda x: self.dismiss_dialog())]
            ).open()
        else:
            self.manager.players = names
            self.manager.games = self.generate_games(names)
            self.manager.results = []
            self.manager.current_game_index = 0
            self.manager.current = 'game'

    def dismiss_dialog(self):
        for dialog in MDDialog._instances:
            dialog.dismiss()

    def generate_games(self, players):
        games = []
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                games.append((players[i], players[j]))
        return games


class GameScreen(MDScreen):
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


class ResultsScreen(MDScreen):
    def on_enter(self):
        self.ids.standings_layout.clear_widgets()
        self.ids.results_layout.clear_widgets()

        scores = {player: 0 for player in self.manager.players}
        for p1, p2, winner in self.manager.results:
            scores[winner] += 1

        sorted_players = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for name, score in sorted_players:
            self.ids.standings_layout.add_widget(
                OneLineListItem(text=f"{name}: {score} wins")
            )

        for p1, p2, winner in self.manager.results:
            self.ids.results_layout.add_widget(
                OneLineListItem(text=f"{p1} vs {p2} → Winner: {winner}")
            )


class TournamentApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.root = Builder.load_string(KV)
        self.root.players = []
        self.root.games = []
        self.root.results = []
        self.root.current_game_index = 0
        return self.root

    def back_to_input(self):
        self.root.current = 'input'


if __name__ == '__main__':
    TournamentApp().run()

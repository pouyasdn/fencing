from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.core.window import Window

Window.size = (480, 800)

class PlayerInputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.label = Label(text='نام بازیکنان را وارد کنید (حداقل 3 نفر):', font_size=18)
        self.players_input = TextInput(hint_text='هر نام را با Enter جدا کنید', multiline=True, font_size=16)
        self.start_button = Button(text='شروع مسابقات', size_hint=(1, 0.2), on_press=self.start_tournament)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.players_input)
        self.layout.add_widget(self.start_button)
        self.add_widget(self.layout)

    def start_tournament(self, instance):
        names = [name.strip() for name in self.players_input.text.split('\n') if name.strip()]
        if len(names) < 3:
            popup = Popup(title='خطا', content=Label(text='حداقل 3 بازیکن وارد کنید.'), size_hint=(None, None), size=(300, 200))
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

class GameScreen(Screen):
    player1 = StringProperty('')
    player2 = StringProperty('')

    def on_enter(self):
        if self.manager.current_game_index < len(self.manager.games):
            game = self.manager.games[self.manager.current_game_index]
            self.player1, self.player2 = game
            self.ids.label.text = f"نتیجه بازی بین {self.player1} و {self.player2} را وارد کنید:"
        else:
            self.manager.transition = NoTransition()
            self.manager.current = 'results'

    def submit_result(self, winner):
        self.manager.results.append((self.player1, self.player2, winner))
        self.manager.current_game_index += 1
        self.on_enter()

class ResultsScreen(Screen):
    standings = ListProperty()

    def on_enter(self):
        scores = {player: 0 for player in self.manager.players}
        for p1, p2, winner in self.manager.results:
            if winner in scores:
                scores[winner] += 1

        sorted_players = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.standings = sorted_players

        self.ids.standings_layout.clear_widgets()
        for name, score in sorted_players:
            self.ids.standings_layout.add_widget(Label(text=f"{name}: {score} برد", font_size=16))

        self.ids.results_layout.clear_widgets()
        for p1, p2, winner in self.manager.results:
            self.ids.results_layout.add_widget(Label(text=f"{p1} vs {p2} → برنده: {winner}", font_size=14))

class TournamentApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PlayerInputScreen(name='input'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ResultsScreen(name='results'))
        return sm

from kivy.lang import Builder

Builder.load_string('''
<GameScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20

        Label:
            id: label
            text: root.player1 + ' vs ' + root.player2
            font_size: 18

        Button:
            text: root.player1 + ' برنده شد'
            on_press: root.submit_result(root.player1)
            font_size: 16
            size_hint_y: 0.2

        Button:
            text: root.player2 + ' برنده شد'
            on_press: root.submit_result(root.player2)
            font_size: 16
            size_hint_y: 0.2

<ResultsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10

        Label:
            text: 'رده‌بندی نهایی:'
            font_size: 20

        GridLayout:
            id: standings_layout
            cols: 1
            size_hint_y: None
            height: self.minimum_height

        Label:
            text: 'نتایج بازی‌ها:'
            font_size: 18
            size_hint_y: None
            height: 30

        GridLayout:
            id: results_layout
            cols: 1
            size_hint_y: None
            height: self.minimum_height

<PlayerInputScreen>:
''')

if __name__ == '__main__':
    TournamentApp().run()

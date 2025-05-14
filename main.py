from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen

class Player:
    def __init__(self, name):
        self.name = name
        self.wins = 0
        self.losses = 0

class Match:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.winner = None

class PlayerInputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.input_box = TextInput(hint_text='Enter player names, one per line')
        self.layout.add_widget(self.input_box)
        self.start_button = Button(text='Start Tournament', size_hint=(1, 0.2))
        self.start_button.bind(on_press=self.start_tournament)
        self.layout.add_widget(self.start_button)
        self.add_widget(self.layout)

    def start_tournament(self, instance):
        player_names = self.input_box.text.strip().split('\n')
        if len(player_names) < 2:
            popup = Popup(title='Error', content=Label(text='Enter at least 2 players'), size_hint=(0.6, 0.4))
            popup.open()
            return

        players = [Player(name.strip()) for name in player_names if name.strip()]
        matches = []
        for i in range(len(players)):
            for j in range(i+1, len(players)):
                matches.append(Match(players[i], players[j]))

        self.manager.players = players
        self.manager.matches = matches
        self.manager.current_match_index = 0
        self.manager.current = 'match'

class MatchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text='')
        self.layout.add_widget(self.label)
        self.btn1 = Button(text='', size_hint=(1, 0.3))
        self.btn2 = Button(text='', size_hint=(1, 0.3))
        self.btn1.bind(on_press=self.set_winner1)
        self.btn2.bind(on_press=self.set_winner2)
        self.layout.add_widget(self.btn1)
        self.layout.add_widget(self.btn2)
        self.add_widget(self.layout)

    def on_enter(self):
        if self.manager.current_match_index >= len(self.manager.matches):
            self.manager.current = 'ranking'
            return

        match = self.manager.matches[self.manager.current_match_index]
        self.label.text = f"Who won this match?"
        self.btn1.text = match.p1.name
        self.btn2.text = match.p2.name

    def set_winner1(self, instance):
        self.set_winner(self.manager.matches[self.manager.current_match_index].p1,
                        self.manager.matches[self.manager.current_match_index].p2)

    def set_winner2(self, instance):
        self.set_winner(self.manager.matches[self.manager.current_match_index].p2,
                        self.manager.matches[self.manager.current_match_index].p1)

    def set_winner(self, winner, loser):
        winner.wins += 1
        loser.losses += 1
        self.manager.matches[self.manager.current_match_index].winner = winner
        self.manager.current_match_index += 1
        self.on_enter()

class RankingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.scroll = ScrollView()
        self.label_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.label_box.bind(minimum_height=self.label_box.setter('height'))
        self.scroll.add_widget(self.label_box)
        layout.add_widget(self.scroll)
        self.restart_btn = Button(text='Restart', size_hint=(1, 0.2))
        self.restart_btn.bind(on_press=self.restart)
        layout.add_widget(self.restart_btn)
        self.add_widget(layout)

    def on_enter(self):
        self.label_box.clear_widgets()
        players = self.manager.players
        players.sort(key=lambda p: p.wins, reverse=True)
        for i, player in enumerate(players):
            self.label_box.add_widget(Label(text=f"{i+1}. {player.name} - Wins: {player.wins}, Losses: {player.losses}", size_hint_y=None, height=40))

    def restart(self, instance):
        self.manager.current = 'player_input'

class TournamentApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PlayerInputScreen(name='player_input'))
        sm.add_widget(MatchScreen(name='match'))
        sm.add_widget(RankingScreen(name='ranking'))
        return sm

if __name__ == '__main__':
    TournamentApp().run()

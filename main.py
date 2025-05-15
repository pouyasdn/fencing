from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import NoTransition

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.list import MDList, OneLineAvatarIconListItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, ListProperty

KV = '''
<PlayerInputScreen>:
    name: 'input'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)

        MDTopAppBar:
            title: 'Tournament Setup'
            left_action_items: []

        MDLabel:
            text: 'Enter player names (at least 3):'
            font_style: 'H6'
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: player_input
            hint_text: 'One name per line'
            helper_text: 'Press enter after each name'
            helper_text_mode: 'on_focus'
            multiline: True
            size_hint_y: None
            height: dp(160)
            mode: 'rectangle'

        MDFillRoundFlatButton:
            text: 'Start Tournament'
            size_hint_y: None
            height: dp(48)
            pos_hint: {'center_x': .5}
            on_release: root.start_tournament()

<GameScreen>:
    name: 'game'
    player1: ''
    player2: ''
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)

        MDTopAppBar:
            id: top_bar
            title: 'Match'
            left_action_items: [['arrow-left', lambda x: app.back_to_menu()]]

        MDLabel:
            id: match_label
            text: f"{root.player1} vs {root.player2}"
            font_style: 'H5'
            halign: 'center'
            size_hint_y: None
            height: dp(40)

        MDFillRoundFlatButton:
            text: f"{root.player1} Wins"
            size_hint_y: None
            height: dp(48)
            on_release: root.submit_result(root.player1)

        MDFillRoundFlatButton:
            text: f"{root.player2} Wins"
            size_hint_y: None
            height: dp(48)
            on_release: root.submit_result(root.player2)

<ResultsScreen>:
    name: 'results'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)

        MDTopAppBar:
            title: 'Results'
            left_action_items: [['arrow-left', lambda x: app.back_to_menu()]]

        MDLabel:
            text: 'Final Standings'
            font_style: 'H6'
            halign: 'center'
            size_hint_y: None
            height: dp(32)

        ScrollView:
            size_hint_y: None
            height: dp(200)
            MDList:
                id: standings_list

'''  
class PlayerInputScreen(MDScreen):
    def start_tournament(self):
        names = [l.strip() for l in self.ids.player_input.text.split('\n') if l.strip()]
        if len(names) < 3:
            dialog = MDDialog(
                title='Error',
                text='Please enter at least 3 players.',
                buttons=[MDFillRoundFlatButton(text='OK', on_release=lambda d: d.dismiss())]
            )
            dialog.open()
            return
        self.manager.players = names
        self.manager.games = [(a, b) for i, a in enumerate(names) for b in names[i+1:]]
        self.manager.results = {n: 0 for n in names}
        self.manager.current_index = 0
        self.manager.transition = NoTransition()
        self.manager.current = 'game'

class GameScreen(MDScreen):
    player1 = StringProperty('')
    player2 = StringProperty('')

    def on_enter(self):
        idx = self.manager.current_index
        if idx < len(self.manager.games):
            a, b = self.manager.games[idx]
            self.player1, self.player2 = a, b
            self.ids.match_label.text = f"{a} vs {b}"
            self.ids.top_bar.title = f"Match {idx+1}/{len(self.manager.games)}"
        else:
            self.manager.transition = NoTransition()
            self.manager.current = 'results'

    def submit_result(self, winner):
        self.manager.results[winner] += 1
        self.manager.current_index += 1
        self.on_enter()

class ResultsScreen(MDScreen):
    def on_enter(self):
        self.ids.standings_list.clear_widgets()
        for name, score in sorted(self.manager.results.items(), key=lambda x: -x[1]):
            self.ids.standings_list.add_widget(OneLineAvatarIconListItem(text=f"{name}: {score} wins"))

class FencingApp(MDApp):
    def build(self):
        Builder.load_string(KV)
        sm = MDScreenManager()
        sm.add_widget(PlayerInputScreen(name='input'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ResultsScreen(name='results'))
        sm.players = []
        sm.games = []
        sm.results = {}
        sm.current_index = 0
        return sm

    def back_to_menu(self):
        self.root.current = 'input'

if __name__ == '__main__':
    FencingApp().run()

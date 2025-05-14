from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.factory import Factory
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.behaviors.hover_behavior import HoverBehavior
from kivymd.uix.button import MDIconButton
import sqlite3
import os
from kivy.app import App

KV = '''
<HoverIconButton@HoverBehavior+MDIconButton>:
    size_hint: None, None
    size: dp(56), dp(56)
    md_bg_color: app.theme_cls.accent_color
    theme_icon_color: "Custom"
    icon_color: 1,1,1,1
    on_enter: self.md_bg_color = (0.2,0.8,0.8,1)
    on_leave: self.md_bg_color = app.theme_cls.accent_color

<StarIconRightWidget@IconRightWidget>:
    size_hint: None, None
    size: dp(36), dp(36)
    pos_hint: {"center_y": .5}
    padding: dp(8), 0

<IconRightWidget@IconRightWidget>:
    size_hint: None, None
    size: dp(32), dp(32)
    pos_hint: {"center_y": .5}

<MDFillRoundFlatButton>:
    size_hint: 0.8, None
    height: dp(60)
    font_size: "16sp"
    md_bg_color: app.theme_cls.primary_color
    text_color: 1,1,1,1
    radius: [dp(12)]
    pos_hint: {"center_x": .5}

<MDTextField>:
    size_hint_x: 0.8
    font_size: "16sp"
    line_color_focus: app.theme_cls.accent_color
    hint_text_color: app.theme_cls.text_color

<MDTopAppBar>:
    size_hint_y: None
    height: dp(56)
    icon_size: dp(28)
    specific_text_color: 1,1,1,1
    md_bg_color: app.theme_cls.primary_color

MDScreenManager:
    MenuScreen:
    SavedScreen:
    MatchScreen:
    SummaryScreen:
    RankingScreen:

<MenuScreen>:
    name: "menu"
    md_bg_color: 0.95,0.95,1,1

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(16)
        size_hint: 0.9,0.9
        pos_hint: {"center_x": .5, "center_y": .5}

        MDTopAppBar:
            title: "Fencing Tournament"
            left_action_items: []

        MDCard:
            size_hint: 1, None
            height: dp(140)
            padding: dp(16)
            radius: dp(12)
            elevation: 2

            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(12)
                size_hint_y: None
                height: dp(56)

                MDTextField:
                    id: name_input
                    hint_text: "Participant Name"

                HoverIconButton:
                    icon: "account-plus"
                    on_release:
                        root.add_member(name_input.text)
                        name_input.text = ""

                HoverIconButton:
                    icon: "database-import"
                    on_release: root.toggle_saved_screen()

        ScrollView:
            MDList:
                id: member_list

        MDFillRoundFlatButton:
            text: "Start Tournament"
            on_release: root.start_tournament()
            disabled: len(root.members) < 2

<SavedScreen>:
    name: "saved"
    md_bg_color: 1,1,1,1

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(16)

        MDTopAppBar:
            title: "Saved Players"
            left_action_items: [['arrow-left', lambda x: app.back_to_menu()]]

        ScrollView:
            MDList:
                id: saved_list

<MatchScreen>:
    name: "match"
    md_bg_color: 0.95,0.95,1,1

    FloatLayout:

        MDTopAppBar:
            id: top_bar
            title: "Match"
            left_action_items: [['arrow-left', lambda x: app.back_to_menu()]]
            size_hint_x: 1
            pos_hint: {"top": 1}

        MDCard:
            size_hint: 0.9, None
            height: dp(160)
            padding: dp(16)
            radius: dp(12)
            elevation: 4
            pos_hint: {"center_x": .5, "center_y": .6}

            MDLabel:
                id: match_label
                text: "A vs B"
                halign: "center"
                font_style: "H4"

        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(12)
            size_hint: 0.9, None
            height: dp(60)
            pos_hint: {"center_x": .5, "y": .1}

            MDFillRoundFlatButton:
                id: btn1
                text: ""
                size_hint_x: 0.48
                on_release: root.select_winner(btn1.text)

            MDFillRoundFlatButton:
                id: btn2
                text: ""
                size_hint_x: 0.48
                on_release: root.select_winner(btn2.text)

<SummaryScreen>:
    name: "summary"

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(16)

        MDTopAppBar:
            title: "Summary"
            left_action_items: [['arrow-left', lambda x: app.back_to_menu()]]

        ScrollView:
            MDList:
                id: summary_list

        MDFillRoundFlatButton:
            text: "View Rankings"
            on_release: root.manager.current = "ranking"

<RankingScreen>:
    name: "ranking"

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(16)

        MDTopAppBar:
            title: "Rankings"
            left_action_items: [['arrow-left', lambda x: app.back_to_menu()]]

        ScrollView:
            MDList:
                id: rank_list

        MDFillRoundFlatButton:
            text: "Back to Menu"
            on_release: app.back_to_menu()
'''

class MenuScreen(MDScreen):
    members = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db_path = os.path.join(App.get_running_app().user_data_dir, 'players.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS players (name TEXT UNIQUE)')
        self.conn.commit()

    def add_member(self, name):
        name = name.strip()
        if not name or name in self.members:
            return
        self.members.append(name)
        item = OneLineAvatarIconListItem(text=name)
        item.add_widget(IconLeftWidget(icon='account'))

        del_btn = IconRightWidget(icon='delete')
        del_btn.on_release = lambda *a, nm=name: self.confirm_remove(item, nm)
        item.add_widget(del_btn)

        save_btn = Factory.StarIconRightWidget(icon='star-outline')
        save_btn.on_release = lambda *a, btn=save_btn, nm=name: self.confirm_save(btn, nm)
        item.add_widget(save_btn)

        self.ids.member_list.add_widget(item)

    def confirm_remove(self, item, name):
        self.members.remove(name)
        self.ids.member_list.remove_widget(item)

    def confirm_save(self, btn, name):
        try:
            self.cursor.execute('INSERT INTO players (name) VALUES (?)', (name,))
            self.conn.commit()
            btn.icon = 'star'
        except sqlite3.IntegrityError:
            btn.icon = 'star'

    def remove_member(self, name):
        self.cursor.execute('DELETE FROM players WHERE name=?', (name,))
        self.conn.commit()

    def toggle_saved_screen(self):
        self.manager.current = 'saved'

    def start_tournament(self):
        if not self.members:
            return
        self.manager.get_screen('match').setup_matches(self.members[:])
        self.manager.current = 'match'

class SavedScreen(MDScreen):
    def on_enter(self):
        self.ids.saved_list.clear_widgets()
        conn = sqlite3.connect(os.path.join(App.get_running_app().user_data_dir, 'players.db'))
        cursor = conn.cursor()
        for row in cursor.execute('SELECT name FROM players'):
            nm = row[0]
            item = OneLineAvatarIconListItem(text=nm)
            item.add_widget(IconLeftWidget(icon='account'))
            self.ids.saved_list.add_widget(item)
        conn.close()

class MatchScreen(MDScreen):
    def setup_matches(self, members):
        self.matches = [(a, b) for i, a in enumerate(members) for b in members[i+1:]]
        self.results = {m: 0 for m in members}
        self.index = 0
        self.show_match()

    def show_match(self):
        a, b = self.matches[self.index]
        self.ids.match_label.text = f"{a} vs {b}"
        self.ids.btn1.text = f"{a} wins"
        self.ids.btn2.text = f"{b} wins"
        self.ids.top_bar.title = f"Match {self.index+1}/{len(self.matches)}"

    def select_winner(self, winner):
        w = winner.replace(" wins", "")
        self.results[w] += 1
        self.index += 1
        if self.index >= len(self.matches):
            self.manager.get_screen('summary').display_summary(self.matches, self.results)
            self.manager.current = 'summary'
        else:
            self.show_match()

class SummaryScreen(MDScreen):
    def display_summary(self, matches, results):
        self.ids.summary_list.clear_widgets()
        for a, b in matches:
            res = "Draw" if results[a] == results[b] else (a if results[a] > results[b] else b)
            item = OneLineAvatarIconListItem(text=f"{a} vs {b} → {res}")
            self.ids.summary_list.add_widget(item)

class RankingScreen(MDScreen):
    def on_enter(self):
        self.ids.rank_list.clear_widgets()
        ms = self.manager.get_screen('match')
        for n, s in sorted(ms.results.items(), key=lambda x: -x[1]):
            item = OneLineAvatarIconListItem(text=f"{n}: {s} wins")
            self.ids.rank_list.add_widget(item)

Factory.register('MenuScreen', cls=MenuScreen)
Factory.register('SavedScreen', cls=SavedScreen)
Factory.register('MatchScreen', cls=MatchScreen)
Factory.register('SummaryScreen', cls=SummaryScreen)
Factory.register('RankingScreen', cls=RankingScreen)

class FencingApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.accent_hue = "400"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def back_to_menu(self):
        self.root.current = 'menu'

if __name__ == '__main__':
    FencingApp().run()

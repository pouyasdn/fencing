from kivy.config import Config
Config.set('graphics', 'multisamples', '0')

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, MDList
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDToolbar
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty, NumericProperty
from kivy.animation import Animation

class TournamentScreen(MDScreen):
    members = ListProperty([])
    matches = ListProperty([])
    match_index = NumericProperty(0)
    results = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Toolbar
        self.toolbar = MDToolbar(title="مدیریت تورنمنت")
        self.toolbar.pos_hint = {"top": 1}
        self.toolbar.md_bg_color = self.theme_cls.primary_color
        self.add_widget(self.toolbar)

        # Main Layout
        main = MDBoxLayout(orientation="vertical", spacing=10, padding=20, size_hint_y=None)
        main.bind(minimum_height=main.setter('height'))

        # Input
        self.input_field = MDTextField(hint_text="نام شرکت‌کننده را وارد کنید", size_hint_x=1)
        self.add_widget(self.input_field)
        add_btn = MDRaisedButton(text="افزودن", pos_hint={"center_x": .5}, on_release=self.add_member)
        self.add_widget(add_btn)

        # Members List
        members_label = MDLabel(text="اعضا:", halign="right", font_style="H6")
        main.add_widget(members_label)
        self.member_list = MDList()
        scroll_members = ScrollView(size_hint=(1, 0.3))
        scroll_members.add_widget(self.member_list)
        main.add_widget(scroll_members)

        # Start Button
        start_btn = MDRaisedButton(text="شروع مسابقات", size_hint=(1, None), height=50, on_release=self.start_matches)
        main.add_widget(start_btn)

        # Wrap in ScrollView
        scroll = ScrollView()
        scroll.add_widget(main)
        self.add_widget(scroll)

    def add_member(self, instance):
        name = self.input_field.text.strip()
        if name and name not in self.members:
            self.members.append(name)
            self.input_field.text = ''
            self.member_list.add_widget(OneLineListItem(text=name))

    def start_matches(self, instance):
        if len(self.members) < 2:
            return
        self.matches = [(self.members[i], self.members[j]) for i in range(len(self.members)) for j in range(i+1, len(self.members))]
        self.match_index = 0
        self.results.clear()
        self.show_next_match()

    def show_next_match(self):
        if self.match_index >= len(self.matches):
            return self.show_summary()
        p1, p2 = self.matches[self.match_index]
        content = MDBoxLayout(orientation="vertical", spacing=20, padding=20)
        content.add_widget(MDLabel(text=f"{p1} در برابر {p2}", halign="center", font_style="H5"))
        btn1 = MDRaisedButton(text=f"{p1} برنده است", on_release=lambda x: self.record(p1))
        btn2 = MDRaisedButton(text=f"{p2} برنده است", on_release=lambda x: self.record(p2))
        content.add_widget(btn1)
        content.add_widget(btn2)
        self.dialog = MDDialog(title="نتیجه مسابقه", type="custom", content_cls=content, auto_dismiss=False)
        self.dialog.open()

    def record(self, winner):
        p1, p2 = self.matches[self.match_index]
        self.results[(p1, p2)] = winner
        self.dialog.dismiss()
        Animation(opacity=0, d=0.3).start(self)
        self.match_index += 1
        Animation(opacity=1, d=0.3).start(self)
        self.show_next_match()

    def show_summary(self):
        content = MDBoxLayout(orientation="vertical", spacing=10, padding=20)
        for p1, p2 in self.matches:
            winner = self.results.get((p1, p2), "-")
            content.add_widget(MDLabel(text=f"{p1} vs {p2} : {winner}", halign="right"))
        btn = MDRaisedButton(text="نمایش رنکینگ", on_release=self.show_ranking)
        content.add_widget(btn)
        self.summary = MDDialog(title="خلاصه مسابقات", type="custom", content_cls=content, size_hint=(0.9, 0.9))
        self.summary.open()

    def show_ranking(self, instance):
        scores = {m: 0 for m in self.members}
        for win in self.results.values():
            scores[win] += 1
        ranking = sorted(scores.items(), key=lambda x: -x[1])
        content = MDBoxLayout(orientation="vertical", spacing=10, padding=20)
        for idx, (name, score) in enumerate(ranking, 1):
            content.add_widget(MDLabel(text=f"{idx}. {name} - {score}"))
        self.rank_dialog = MDDialog(title="رنکینگ نهایی", type="custom", content_cls=content)
        self.rank_dialog.open()

class TournamentApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return TournamentScreen()

if __name__ == '__main__':
    TournamentApp().run()

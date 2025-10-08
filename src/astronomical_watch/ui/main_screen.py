from astronomical_watch import lang
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from astronomical_watch.lang.lang_config import save_language, load_language
from astronomical_watch.lang.translations import tr

# Prilikom starta aplikacije
self.selected_language = load_language()  # default: "en"

# Pretpostavljamo da imaš core funkcije za izračunavanje dies, miliDies, vreme itd.
from astronomical_watch.core.timeframe import astronomical_time

LANGUAGES = [
    "English",
    "Español",
    "中文",
    "العربية",
    "Português",
    "Français",
    "Deutsch",
    "Русский",
    "日本語",
    "हिन्दी",
    "فارسی",
    "Bahasa Indonesia",
    "Kiswahili",
    "Hausa",
    "Türkçe",
    "Ελληνικά",
    "Srpski",
    "Polski",
    "Italiano",
    "Nederlands"
]

class WidgetMode(Screen):
    dies = NumericProperty(0)
    milidies = NumericProperty(0)
    progress = NumericProperty(0)  # 0-100 (stotinke milidiesa)
    show_alert = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        self.title = Label(text=tr("title", self.selected_language), font_size='24sp', size_hint=(1, .2))
        self.dies_label = Label(font_size='56sp', size_hint=(1, .3), halign="center", valign="middle")
        self.progress_bar = ProgressBar(max=100, size_hint=(1, .08))
        self.alert_label = Label(text="", color=(0, 1, 0, 1), font_size='18sp', size_hint=(1, .1))
        self.layout.add_widget(self.title)
        self.layout.add_widget(self.dies_label)
        self.layout.add_widget(self.progress_bar)
        self.layout.add_widget(self.alert_label)
        self.add_widget(self.layout)
        self.bind(on_touch_down=self.on_widget_touch)

        # Update every 0.2 sec
        Clock.schedule_interval(self.update, 0.2)

    def update(self, dt=0):
        # Ovdje koristiš core funkcije za izračun trenutnog dies i milidies
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        dies, milidies = astronomical_time(now)
        self.dies = dies
        self.milidies = milidies
        self.progress = int((now.microsecond / 1e6 + now.second) * 100 / 86.4) % 100  # 1 milidies = 86.4s
        # Formatiraj prikaz
        self.dies_label.text = f"[b]{dies}[/b] . [b]{milidies:03d}[/b]"
        self.progress_bar.value = self.progress

        # Zeleno polje ako je manje od 11 diesa do sledeće ravnodnevnice (dummy implementacija)
        dies_to_equinox = 10  # TODO: izračunaj stvarnu vrednost
        if dies_to_equinox < 11:
            self.alert_label.text = f"Only {dies_to_equinox} dies to Equinox!"
            self.alert_label.color = (0, 1, 0, 1)
        else:
            self.alert_label.text = ""

    def on_widget_touch(self, instance, touch):
        if self.collide_point(*touch.pos):
            self.manager.current = "normal"

class NormalMode(Screen):
    dies = NumericProperty(0)
    milidies = NumericProperty(0)
    progress = NumericProperty(0)
    time_text = StringProperty("")
    show_alert = BooleanProperty(False)
    selected_language = StringProperty(LANGUAGES[0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Top bar: title, back, language
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.13))
        back_btn = Button(text="<", size_hint=(.15, 1), on_press=self.back_to_widget)
        title = Label(text=tr("title", self.selected_language), font_size='20sp')
        lang_btn = Button(text="🌐", size_hint=(.15, 1), on_press=self.show_languages)
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        top_bar.add_widget(lang_btn)
        main_layout.add_widget(top_bar)

        # Dies
        self.dies_label = Label(font_size='50sp', halign="center")
        main_layout.add_widget(self.dies_label)
        main_layout.add_widget(Label(text="Dies", font_size='16sp'))

        # milidies
        self.milidies_label = Label(font_size='50sp', halign="center")
        main_layout.add_widget(self.milidies_label)
        main_layout.add_widget(Label(text="miliDies", font_size='16sp'))

        # Progress bar
        self.progress_bar = ProgressBar(max=100, size_hint=(1, .08))
        main_layout.add_widget(self.progress_bar)

        # Standard time
        self.time_label = Label(text="", font_size='16sp')
        main_layout.add_widget(self.time_label)

        # Alert
        self.alert_label = Label(text="", color=(0, 1, 0, 1), font_size='16sp')
        main_layout.add_widget(self.alert_label)

        # Buttons for card selection
        card_buttons = BoxLayout(orientation='horizontal', size_hint=(1, .17))
        for card_key in ["explanation", "comparison", "calculations"]:
            card_buttons.add_widget(Button(text=tr(card_key, self.selected_language)))
        main_layout.add_widget(card_buttons)

        self.add_widget(main_layout)
        Clock.schedule_interval(self.update, 0.3)

    def update(self, dt=0):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        dies, milidies = astronomical_time(now)
        self.dies = dies
        self.milidies = milidies
        self.progress = int((now.microsecond / 1e6 + now.second) * 100 / 86.4) % 100
        self.dies_label.text = f"{dies}"
        self.milidies_label.text = f"{milidies:03d}"
        self.progress_bar.value = self.progress
        self.time_label.text = now.strftime("%m/%d %H:%M")

        dies_to_equinox = 10  # TODO: izračunaj stvarnu vrednost
        if dies_to_equinox < 11:
            self.alert_label.text = f"Only {dies_to_equinox} dies to Equinox!"
            self.alert_label.color = (0, 1, 0, 1)
        else:
            self.alert_label.text = ""

    def back_to_widget(self, instance):
        self.manager.current = "widget"

    def show_languages(self, instance):
        layout = GridLayout(cols=2, spacing=8, padding=10)
        for lang in LANGUAGES:
            btn = Button(text=lang, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.select_language(btn.text))
            layout.add_widget(btn)
        popup = Popup(title="Choose language", content=layout, size_hint=(.9, .8))
        self._lang_popup = popup
        popup.open()

    def select_language(self, lang):
        self.selected_language = lang
        save_language(lang)
        self.refresh_ui()

    def refresh_ui(self):
        # Primer za labelu i dugmad
        self.title_label.text = lang.tr("title", self.selected_language)
        self.explanation_button.text = tr("explanation", self.selected_language)
        self.comparison_button.text = tr("comparison", self.selected_language)
        self.calculation_button.text = tr("calculations", self.selected_language)
        # ... i sve ostale koje postoje na ekranu

class MainScreenManager(ScreenManager):
    pass

def get_main_screen():
    sm = MainScreenManager()
    sm.add_widget(WidgetMode(name="widget"))
    sm.add_widget(NormalMode(name="normal"))
    sm.current = "widget"
    return sm
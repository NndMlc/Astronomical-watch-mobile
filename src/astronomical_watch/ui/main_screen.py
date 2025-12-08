from astronomical_watch.ui.sky_theme import get_sky_theme
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from astronomical_watch.lang.lang_config import save_language, load_language
from astronomical_watch.lang.translations import tr
from astronomical_watch.core.timeframe import astronomical_time

LANGUAGES = [
    "English", "Español", "中文", "العربية", "Português", "Français", "Deutsch", 
    "Русский", "日本語", "हिन्दी", "فارسی", "Bahasa Indonesia", "Kiswahili", "Hausa", 
    "Türkçe", "Ελληνικά", "Srpski", "Polski", "Italiano", "Nederlands",
    "বাংলা", "עברית", "한국어", "Kurdî", "Română", "اردو", "Tiếng Việt", "isiZulu"
]

class WidgetMode(Screen):
    """Minimalist widget showing current astronomical time"""
    dies = NumericProperty(0)
    milidies = NumericProperty(0)
    progress = NumericProperty(0)
    selected_language = StringProperty(load_language())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        self.title = Label(text=tr("title", self.selected_language), font_size='24sp', size_hint=(1, .2))
        self.dies_label = Label(font_size='56sp', size_hint=(1, .3), halign="center", valign="middle")
        self.dies_label.markup = True
        self.progress_bar = ProgressBar(max=100, size_hint=(1, .08))
        self.alert_label = Label(text="", color=(0, 1, 0, 1), font_size='18sp', size_hint=(1, .1))
        
        self.layout.add_widget(self.title)
        self.layout.add_widget(self.dies_label)
        self.layout.add_widget(self.progress_bar)
        self.layout.add_widget(self.alert_label)
        self.add_widget(self.layout)
        
        self.bind(on_touch_down=self.on_widget_touch)
        Clock.schedule_interval(self.update, 0.2)

    def update(self, dt=0):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        dies, milidies = astronomical_time(now)
        
        self.dies = dies
        self.milidies = milidies
        self.progress = int((now.microsecond / 1e6 + now.second) * 100 / 86.4) % 100
        self.dies_label.text = f"[b]{dies}[/b] . [b]{milidies:03d}[/b]"
        self.progress_bar.value = self.progress

        # Dynamic sky theme
        theme = get_sky_theme(now)
        self.layout.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with self.layout.canvas.before:
            Color(*[int(theme.top_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
            Rectangle(pos=self.layout.pos, size=(self.layout.size[0], self.layout.size[1]/2))
            Color(*[int(theme.bottom_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
            Rectangle(pos=(self.layout.pos[0], self.layout.pos[1]+self.layout.size[1]/2), 
                     size=(self.layout.size[0], self.layout.size[1]/2))
        
        text_color = [int(theme.text_color[i:i+2], 16)/255 for i in (1, 3, 5)] + [1]
        self.title.color = text_color
        self.dies_label.color = text_color
        self.alert_label.color = text_color

    def on_widget_touch(self, instance, touch):
        if self.collide_point(*touch.pos):
            self.manager.current = "normal"


class NormalMode(Screen):
    """Full screen with detailed information and language cards"""
    dies = NumericProperty(0)
    milidies = NumericProperty(0)
    progress = NumericProperty(0)
    selected_language = StringProperty(load_language())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Top bar: back button, title, language selector
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.13))
        back_btn = Button(text="<", size_hint=(.15, 1), on_press=self.back_to_widget)
        title = Label(text=tr("title", self.selected_language), font_size='20sp')
        lang_btn = Button(text="🌐", size_hint=(.15, 1), on_press=self.show_languages)
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        top_bar.add_widget(lang_btn)
        main_layout.add_widget(top_bar)

        # Dies display
        self.dies_label = Label(font_size='50sp', halign="center")
        main_layout.add_widget(self.dies_label)
        main_layout.add_widget(Label(text="Dies", font_size='16sp'))

        # MiliDies display
        self.milidies_label = Label(font_size='50sp', halign="center")
        main_layout.add_widget(self.milidies_label)
        main_layout.add_widget(Label(text="miliDies", font_size='16sp'))

        # Progress bar
        self.progress_bar = ProgressBar(max=100, size_hint=(1, .08))
        main_layout.add_widget(self.progress_bar)

        # Standard time reference
        self.time_label = Label(text="", font_size='16sp')
        main_layout.add_widget(self.time_label)

        # Alert label
        self.alert_label = Label(text="", color=(0, 1, 0, 1), font_size='16sp')
        main_layout.add_widget(self.alert_label)

        # Card selection buttons
        card_buttons = BoxLayout(orientation='horizontal', size_hint=(1, .17))
        self.card_buttons = {}
        for card_key in ["explanation", "comparison", "calculations"]:
            btn = Button(text=tr(card_key, self.selected_language))
            card_buttons.add_widget(btn)
            self.card_buttons[card_key] = btn
        
        # Bind buttons
        self.card_buttons["explanation"].bind(on_release=self.show_explanation_card)
        self.card_buttons["comparison"].bind(on_release=lambda x: self.show_simple_popup(
            tr("comparison", self.selected_language), 
            "Feature coming soon: Compare astronomical time with standard calendars"))
        self.card_buttons["calculations"].bind(on_release=lambda x: self.show_simple_popup(
            tr("calculations", self.selected_language),
            "Feature coming soon: Show local solar noon and equation of time"))
        
        main_layout.add_widget(card_buttons)
        self.add_widget(main_layout)
        
        Clock.schedule_interval(self.update, 0.2)

    def show_simple_popup(self, title, message):
        """Display a simple popup message"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size='18sp'))
        close_btn = Button(text=tr("close_button", self.selected_language), size_hint=(1, 0.3))
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(.8, .5))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_explanation_card(self, instance):
        """Show explanation in the selected language"""
        # Map language names to file codes
        lang_map = {
            "English": "en", "Español": "es", "中文": "zh", "العربية": "ar", "Português": "pt",
            "Français": "fr", "Deutsch": "de", "Русский": "ru", "日本語": "ja", "हिन्दी": "hi",
            "فارسی": "fa", "Bahasa Indonesia": "id", "Kiswahili": "sw", "Hausa": "ha", "Türkçe": "tr",
            "Ελληνικά": "el", "Srpski": "sr", "Polski": "pl", "Italiano": "it", "Nederlands": "nl",
            "বাংলা": "bn", "עברית": "he", "한국어": "ko", "Kurdî": "ku", "Română": "ro",
            "اردو": "ur", "Tiếng Việt": "vi", "isiZulu": "zu"
        }
        lang_code = lang_map.get(self.selected_language, "en")
        
        try:
            # Dynamic import of explanation text
            module_name = f"astronomical_watch.lang.explanation_{lang_code}_card"
            import importlib
            explanation_module = importlib.import_module(module_name)
            explanation_text = explanation_module.EXPLANATION_TEXT
        except Exception as e:
            explanation_text = f"[b]Error loading explanation:[/b]\n{e}\n\nModule: {module_name}"
        
        from astronomical_watch.ui.sky_theme import get_sky_theme
        from datetime import datetime, timezone
        from kivy.uix.scrollview import ScrollView
        
        theme = get_sky_theme(datetime.now(timezone.utc))
        
        # Scrollable content
        scroll = ScrollView()
        content = Label(
            text=explanation_text, 
            markup=True, 
            text_size=(Window.width * 0.85, None),
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        content.bind(texture_size=content.setter('size'))
        scroll.add_widget(content)
        
        popup = Popup(title=tr("explanation", self.selected_language), 
                     content=scroll, size_hint=(.95, .95))
        
        # Apply sky theme to popup background
        def update_bg(*_):
            popup.canvas.before.clear()
            from kivy.graphics import Color, Rectangle
            with popup.canvas.before:
                Color(*[int(theme.top_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
                Rectangle(pos=popup.pos, size=(popup.size[0], popup.size[1]/2))
                Color(*[int(theme.bottom_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
                Rectangle(pos=(popup.pos[0], popup.pos[1]+popup.size[1]/2), 
                         size=(popup.size[0], popup.size[1]/2))
        
        popup.bind(pos=update_bg, size=update_bg)
        update_bg()
        
        content.color = [int(theme.text_color[i:i+2], 16)/255 for i in (1, 3, 5)] + [1]
        popup.open()

    def update(self, dt=0):
        """Update time display"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        dies, milidies = astronomical_time(now)
        
        self.dies = dies
        self.milidies = milidies
        self.progress = int((now.microsecond / 1e6 + now.second) * 100 / 86.4) % 100
        
        self.dies_label.text = f"{dies}"
        self.milidies_label.text = f"{milidies:03d}"
        self.progress_bar.value = self.progress
        self.time_label.text = now.strftime("%Y-%m-%d %H:%M UTC")

        # Dynamic sky theme
        theme = get_sky_theme(now)
        text_color = [int(theme.text_color[i:i+2], 16)/255 for i in (1, 3, 5)] + [1]
        self.dies_label.color = text_color
        self.milidies_label.color = text_color
        self.time_label.color = text_color

    def back_to_widget(self, instance):
        """Return to widget mode"""
        self.manager.current = "widget"

    def show_languages(self, instance):
        """Show language selection popup"""
        layout = GridLayout(cols=2, spacing=8, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        for lang in LANGUAGES:
            btn = Button(text=lang, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn_inst: self.select_language(btn_inst.text))
            layout.add_widget(btn)
        
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView()
        scroll.add_widget(layout)
        
        popup = Popup(title="Choose language", content=scroll, size_hint=(.9, .8))
        self._lang_popup = popup
        popup.open()

    def select_language(self, lang):
        """Change the display language"""
        self.selected_language = lang
        save_language(lang)
        if hasattr(self, '_lang_popup'):
            self._lang_popup.dismiss()
        
        # Refresh button texts
        for key in self.card_buttons:
            self.card_buttons[key].text = tr(key, self.selected_language)

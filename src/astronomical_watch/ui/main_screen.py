from astronomical_watch.ui.sky_theme import get_sky_theme
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

        # Dinamička tema neba
        theme = get_sky_theme(now)
        # Postavi boje pozadine i teksta
        self.layout.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with self.layout.canvas.before:
            Color(*[int(theme.top_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
            Rectangle(pos=self.layout.pos, size=(self.layout.size[0], self.layout.size[1]/2))
            Color(*[int(theme.bottom_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
            Rectangle(pos=(self.layout.pos[0], self.layout.pos[1]+self.layout.size[1]/2), size=(self.layout.size[0], self.layout.size[1]/2))
        self.title.color = self.dies_label.color = self.alert_label.color = [int(theme.text_color[i:i+2], 16)/255 for i in (1, 3, 5)] + [1]

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
    # Bind calculation button to show calculation popup
    def show_calculation_card(self, instance):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.image import Image
        from kivy.uix.popup import Popup
        import io
        import matplotlib.pyplot as plt
        import numpy as np
        # Placeholder for location permission and reading
        # On mobile, use platform-specific API for permission and location
        # Here, simulate with fixed location (e.g. Belgrade)
        lat, lon = 44.7866, 20.4489
        # Calculate local meridian (miliDies at mean solar noon)
        from astronomical_watch.core.timeframe import get_meridian_milidies, get_eot_curve
        try:
            meridian_md = get_meridian_milidies(lat, lon)
            meridian_label = tr("meridian_label", self.selected_language)
            meridian_value = tr("meridian_value_label", self.selected_language, milidies=meridian_md)
        except Exception as e:
            meridian_label = tr("meridian_label", self.selected_language)
            meridian_value = tr("error_text", self.selected_language, error=str(e))

        # Generate EoT graph
        try:
            days, eot_minutes, eot_md, markers = get_eot_curve(lat, lon)
            fig, ax1 = plt.subplots(figsize=(7, 3))
            ax2 = ax1.twinx()
            ax1.plot(days, eot_minutes, 'r-', label='Minutes')
            ax2.plot(days, eot_md, 'b-', label='miliDies')
            ax1.set_xlabel(tr("eqt_graph_xlabel", self.selected_language))
            ax1.set_ylabel(tr("eqt_graph_ylabel", self.selected_language))
            ax2.set_ylabel(tr("eqt_graph_ylabel", self.selected_language))
            # Markers for equinoxes, solstices, Jan 1
            for m in markers:
                ax1.axvline(m["day"], color=m["color"], linestyle='--', label=m["label"])
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close(fig)
            graph_img = Image(texture=None)
            from kivy.core.image import Image as CoreImage
            graph_img.texture = CoreImage(buf, ext='png').texture
        except Exception as e:
            graph_img = Label(text=tr("graph_unavailable", self.selected_language) + f"\n{e}")

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(Label(text=meridian_label, font_size='16sp'))
        layout.add_widget(Label(text=meridian_value, font_size='20sp'))
        layout.add_widget(Label(text=tr("eqt_curve_label", self.selected_language), font_size='16sp'))
        layout.add_widget(graph_img)
        close_btn = Button(text=tr("close_button", self.selected_language), size_hint=(1, 0.15))
        layout.add_widget(close_btn)
        from astronomical_watch.ui.sky_theme import get_sky_theme
        from datetime import datetime, timezone
        theme = get_sky_theme(datetime.now(timezone.utc))
        popup = Popup(title=tr("calculations", self.selected_language), content=layout, size_hint=(.98, .98))
        def update_bg(*_):
            popup.canvas.before.clear()
            from kivy.graphics import Color, Rectangle
            with popup.canvas.before:
                Color(*[int(theme.top_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
                Rectangle(pos=popup.pos, size=(popup.size[0], popup.size[1]/2))
                Color(*[int(theme.bottom_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
                Rectangle(pos=(popup.pos[0], popup.pos[1]+popup.size[1]/2), size=(popup.size[0], popup.size[1]/2))
        popup.bind(pos=update_bg, size=update_bg)
        update_bg()
        for widget in layout.children:
            if hasattr(widget, 'color'):
                widget.color = [int(theme.text_color[i:i+2], 16)/255 for i in (1, 3, 5)] + [1]
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
    # Bind comparison button to show comparison popup
    def show_comparison_card(self, instance):
        from kivy.uix.textinput import TextInput
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from tzlocal import get_localzone
        import datetime
        from astronomical_watch.core.timeframe import astronomical_time
        # Helper functions
        def std_to_astro(dt):
            dies, milidies = astronomical_time(dt.astimezone(datetime.timezone.utc))
            return dies, milidies
        def astro_to_std(dies, milidies):
            # Pretpostavljamo da postoji funkcija koja vraća datetime za dati dies i milidies
            from astronomical_watch.core.timeframe import datetime_from_astro
            return datetime_from_astro(dies, milidies)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        # Standard time to Astro
        std_label = Label(text=tr("std_to_astro_label", self.selected_language))
        std_input = TextInput(hint_text="YYYY-MM-DD HH:MM", multiline=False)
        std_btn = Button(text=tr("convert_button", self.selected_language))
        std_result = Label(text="")
        # Astro to Standard
        astro_label = Label(text=tr("astro_to_std_label", self.selected_language))
        dies_input = TextInput(hint_text="Dies", multiline=False, input_filter='int')
        milidies_input = TextInput(hint_text="miliDies", multiline=False, input_filter='int')
        astro_btn = Button(text=tr("convert_button", self.selected_language))
        astro_result = Label(text="")
        # Countdown to next equinox
        countdown_label = Label(text=tr("countdown_next_equinox_label", self.selected_language))
        countdown_result = Label(text="")

        def on_std_btn(instance):
            try:
                local_tz = get_localzone()
                dt = datetime.datetime.strptime(std_input.text, "%Y-%m-%d %H:%M")
                dt = local_tz.localize(dt)
                dies, milidies = std_to_astro(dt)
                std_result.text = tr("astro_result", self.selected_language, day=dies, milidies=milidies)
            except Exception as e:
                std_result.text = tr("error_text", self.selected_language, error=str(e))

        def on_astro_btn(instance):
            try:
                dies = int(dies_input.text)
                milidies = int(milidies_input.text)
                dt = astro_to_std(dies, milidies)
                local_tz = get_localzone()
                dt_local = dt.astimezone(local_tz)
                astro_result.text = tr("std_result", self.selected_language, std_time=dt_local.strftime("%Y-%m-%d %H:%M"))
            except Exception as e:
                astro_result.text = tr("error_text", self.selected_language, error=str(e))

        def update_countdown(*args):
            try:
                now = datetime.datetime.now(datetime.timezone.utc)
                # Pretpostavljamo da postoji funkcija koja vraća (dies, milidies, days, hours, mins, secs) do sledeće ravnodnevnice
                from astronomical_watch.core.timeframe import countdown_to_next_equinox
                dies, milidies, days, hours, mins, secs = countdown_to_next_equinox(now)
                countdown_result.text = f"{tr('countdown_label', self.selected_language, dies=dies, milidies=milidies)}\n{days}d {hours}h {mins}m {secs}s"
            except Exception as e:
                countdown_result.text = tr("error_text", self.selected_language, error=str(e))

        std_btn.bind(on_release=on_std_btn)
        astro_btn.bind(on_release=on_astro_btn)

        layout.add_widget(std_label)
        layout.add_widget(std_input)
        layout.add_widget(std_btn)
        layout.add_widget(std_result)
        layout.add_widget(astro_label)
        layout.add_widget(dies_input)
        layout.add_widget(milidies_input)
        layout.add_widget(astro_btn)
        layout.add_widget(astro_result)
        layout.add_widget(countdown_label)
        layout.add_widget(countdown_result)

        from astronomical_watch.ui.sky_theme import get_sky_theme
        from datetime import datetime, timezone
        theme = get_sky_theme(datetime.now(timezone.utc))
        popup = Popup(title=tr("comparison", self.selected_language), content=layout, size_hint=(.95, .95))
        def update_bg(*_):
            popup.canvas.before.clear()
            from kivy.graphics import Color, Rectangle
            with popup.canvas.before:
                Color(*[int(theme.top_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
                Rectangle(pos=popup.pos, size=(popup.size[0], popup.size[1]/2))
                Color(*[int(theme.bottom_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
                Rectangle(pos=(popup.pos[0], popup.pos[1]+popup.size[1]/2), size=(popup.size[0], popup.size[1]/2))
        popup.bind(pos=update_bg, size=update_bg)
        update_bg()
        for widget in layout.children:
            if hasattr(widget, 'color'):
                widget.color = [int(theme.text_color[i:i+2], 16)/255 for i in (1, 3, 5)] + [1]
        popup.open()
        # Update countdown every second
        from kivy.clock import Clock
        Clock.schedule_interval(update_countdown, 1)
    dies = NumericProperty(0)
    milidies = NumericProperty(0)
    progress = NumericProperty(0)
    time_text = StringProperty("")
    show_alert = BooleanProperty(False)
    selected_language = StringProperty(load_language())

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
        self.card_buttons = {}
        for card_key in ["explanation", "comparison", "calculations"]:
            btn = Button(text=tr(card_key, self.selected_language))
            card_buttons.add_widget(btn)
            self.card_buttons[card_key] = btn
        # Bind explanation and comparison buttons to their popups
        self.card_buttons["explanation"].bind(on_release=self.show_explanation_card)
        self.card_buttons["comparison"].bind(on_release=self.show_comparison_card)
        main_layout.add_widget(card_buttons)
    def show_explanation_card(self, instance):
        # Map language name to language code used in file names
        lang_map = {
            "English": "en", "Español": "es", "中文": "zh", "العربية": "ar", "Português": "pt",
            "Français": "fr", "Deutsch": "de", "Русский": "ru", "日本語": "ja", "हिन्दी": "hi",
            "فارسی": "fa", "Bahasa Indonesia": "id", "Kiswahili": "sw", "Hausa": "ha", "Türkçe": "tr",
            "Ελληνικά": "el", "Srpski": "sr", "Polski": "pl", "Italiano": "it", "Nederlands": "nl"
        }
        lang_code = lang_map.get(self.selected_language, "en")
        try:
            # Dynamic import of explanation text for the selected language
            module_name = f"astronomical_watch.lang.explanation_{lang_code}_card"
            import importlib
            explanation_module = importlib.import_module(module_name)
            explanation_text = explanation_module.EXPLANATION_TEXT
        except Exception as e:
            explanation_text = f"[b]Error loading explanation:[/b] {e}"
        from astronomical_watch.ui.sky_theme import get_sky_theme
        from datetime import datetime, timezone
        theme = get_sky_theme(datetime.now(timezone.utc))
        content = Label(text=explanation_text, markup=True, text_size=(600, None), size_hint_y=None)
        popup = Popup(title=tr("explanation", self.selected_language), content=content, size_hint=(.95, .95))
        def update_bg(*_):
            popup.canvas.before.clear()
            from kivy.graphics import Color, Rectangle
            with popup.canvas.before:
                Color(*[int(theme.top_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
                Rectangle(pos=popup.pos, size=(popup.size[0], popup.size[1]/2))
                Color(*[int(theme.bottom_color[i:i+2], 16)/255 for i in (1, 3, 5)], 1)
                Rectangle(pos=(popup.pos[0], popup.pos[1]+popup.size[1]/2), size=(popup.size[0], popup.size[1]/2))
        popup.bind(pos=update_bg, size=update_bg)
        update_bg()
        content.color = [int(theme.text_color[i:i+2], 16)/255 for i in (1, 3, 5)] + [1]
        popup.open()


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

        # Dinamička tema neba
        theme = get_sky_theme(now)
        self.dies_label.color = self.milidies_label.color = self.time_label.color = self.alert_label.color = [int(theme.text_color[i:i+2], 16)/255 for i in (1, 3, 5)] + [1]
        # Pozadina bi se mogla postaviti na main_layout, ako je dostupan

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
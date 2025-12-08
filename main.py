from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from astronomical_watch.ui.main_screen import WidgetMode, NormalMode

class AstronomicalWatchApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WidgetMode(name="widget"))
        sm.add_widget(NormalMode(name="normal"))
        return sm

if __name__ == "__main__":
    AstronomicalWatchApp().run()
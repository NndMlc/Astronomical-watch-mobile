from kivy.app import App
from src.astronomical_watch.ui.main_screen import get_main_screen

class AstronomicalWatchApp(App):
    def build(self):
        return get_main_screen()

if __name__ == "__main__":
    AstronomicalWatchApp().run()
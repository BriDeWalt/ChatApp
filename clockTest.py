import time
import kivy

kivy.require('1.11.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty


Builder.load_string("""
<MySec>:
    orientation: 'vertical'
    Label:
        id: kv_sec
        text: root.seconds_string
        font_size: 200
""")


class MySec(BoxLayout):
    seconds_string = StringProperty('')


class MyApp(App):
    def build(self):
        Clock.schedule_interval(lambda dt: self.update_time(), 1)
        return MySec()

    def update_time(self):
        self.root.seconds_string = time.strftime("%S")


if __name__ == '__main__':
    MyApp().run()
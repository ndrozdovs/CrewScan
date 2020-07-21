from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
import keyboard
from kivy.core.window import Window


pop_active = 0


class BeginWindow(Screen):
    pass

class InfoWindow(Screen):
    pass

class TravelWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass


def invalidAnswer():
    pop = Popup(title='Warning',
                content=Label(text='Warning: Invalid answer'),
                size_hint=(None, None), size=(400, 400))
    pop.open()
    return pop


kv = Builder.load_file("my.kv")

sm = WindowManager()
screens = [BeginWindow(name="begin"), InfoWindow(name="info"), TravelWindow(name="travel")]
for screen in screens:
    sm.add_widget(screen)

class MyApp(App):
    def build(self):
        def answer_input(dt):
            global pop_active
            if pop_active == 0:
                if self.root.current is 'begin':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'info'
                        self.root.transition.direction = "left"

                elif self.root.current is 'info':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'travel'
                        self.root.transition.direction = "left"
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'begin'
                        self.root.transition.direction = "right"

                elif self.root.current is 'travel':
                    if keyboard.is_pressed('d'):
                        while (keyboard.is_pressed('d')):
                            pass
                        self.root.current = 'begin'
                        self.root.transition.direction = "right"
                        self.pop = invalidAnswer()
                        pop_active = 1
                    elif keyboard.is_pressed('a'):
                        while (keyboard.is_pressed('a')):
                            pass
                        self.root.current = 'info'
                        self.root.transition.direction = "right"
            elif pop_active == 1:
                if keyboard.is_pressed('d'):
                    while (keyboard.is_pressed('d')):
                        pass
                    self.pop.dismiss()
                    pop_active = 0

        Clock.schedule_interval(answer_input, 1/20)

        return sm


if __name__ == "__main__":
    # Window.fullscreen = 'auto'
    MyApp().run()

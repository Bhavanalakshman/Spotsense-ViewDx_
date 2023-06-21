from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp

#from dialog import show_dialog
from utils.QR import QR_scan_function

KV = '''
BoxLayout:
    orientation: 'vertical'

    MDFlatButton:
        text: 'Show Dialog'
        on_release: app.show_dialog()
'''


class MyApp(MDApp):
    def build(self):
        self.root = Builder.load_string(KV)

    def show_dialog(self):
        QR_scan_function()


if __name__ == "__main__":
    MyApp().run()

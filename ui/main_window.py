'''
Diese Datei enthält das Hauptfenster der Desktop-Anwendung und 
steuert den Wechsel zwischen Startscreen (SplashPage) und der eigentlichen App (AppPage). 
Dafür wird ein QStackedWidget genutzt, das mehrere Seiten im selben Fenster verwalten kann. 
So wirkt die Anwendung wie eine “echte App” mit Startscreen und Navigation.
'''

from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QGraphicsOpacityEffect

from ui.splash import SplashPage
from ui.app_page import AppPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atemgurt")
        self.resize(1100, 650)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.app_page = AppPage()
        self.splash = SplashPage(self.go_to_app)

        self.stack.addWidget(self.splash)
        self.stack.addWidget(self.app_page)
        self.stack.setCurrentWidget(self.splash)

        # Opacity Effects
        self.splash_fx = QGraphicsOpacityEffect(self.splash)
        self.splash.setGraphicsEffect(self.splash_fx)
        self.splash_fx.setOpacity(1.0)

        self.app_fx = QGraphicsOpacityEffect(self.app_page)
        self.app_page.setGraphicsEffect(self.app_fx)
        self.app_fx.setOpacity(1.0)

        # Animation handles (damit sie nicht vom GC gelöscht werden)
        self._anim_out = None
        self._anim_in = None

    def go_to_app(self):
        # Fade OUT Splash
        self._anim_out = QPropertyAnimation(self.splash_fx, b"opacity", self)
        self._anim_out.setDuration(220)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)

        def after_fade_out():
            # Switch page
            self.stack.setCurrentWidget(self.app_page)

            # Prepare app fade in
            self.app_fx.setOpacity(0.0)
            self._anim_in = QPropertyAnimation(self.app_fx, b"opacity", self)
            self._anim_in.setDuration(220)
            self._anim_in.setStartValue(0.0)
            self._anim_in.setEndValue(1.0)

            def after_fade_in():
                # optional: splash wieder normal setzen, falls du später zurück willst
                self.splash_fx.setOpacity(1.0)

            self._anim_in.finished.connect(after_fade_in)
            self._anim_in.start()

        self._anim_out.finished.connect(after_fade_out)
        self._anim_out.start()

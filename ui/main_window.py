"""
ui/main_window.py

Diese Datei enthält das Hauptfenster der Desktop-App.

Aufgabe dieser Datei:
- Startpunkt der grafischen Oberfläche (nach main.py)
- Zeigt zuerst einen Startscreen (SplashPage)
- Wechselt danach zur eigentlichen App (AppPage)
- Der Wechsel passiert mit einer Fade-Animation, damit es modern wirkt

Warum das sinnvoll ist:
- Alles läuft in EINEM Fenster
- Kein neues Fenster, kein „Pop-up-Chaos“
- Klare Trennung: Startscreen vs. eigentliche Anwendung
"""

from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QGraphicsOpacityEffect

from ui.splash import SplashPage
from ui.app_page import AppPage


class MainWindow(QMainWindow):
    """
    MainWindow = äußeres Fenster der Anwendung.

    Es enthält:
    - ein QStackedWidget als zentralen Bereich
    - darin:
        - SplashPage (Startscreen)
        - AppPage (eigentliche App)

    Der Wechsel zwischen den Seiten wird animiert (Fade).
    """

    def __init__(self):
        super().__init__()

        # Fenstertitel und Startgröße
        self.setWindowTitle("Atemgurt")
        self.resize(1100, 650)

        # ===== Zentrales Widget =====
        # QStackedWidget funktioniert wie ein Stapel von Seiten.
        # Es ist immer genau EINE Seite sichtbar.
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ===== Seiten erstellen =====
        # SplashPage bekommt eine Funktion übergeben,
        # die beim Klick auf „Start“ aufgerufen wird.
        self.app_page = AppPage()
        self.splash = SplashPage(self.go_to_app)

        # Reihenfolge ist egal, wichtig ist nur,
        # welche Seite wir aktuell anzeigen.
        self.stack.addWidget(self.splash)
        self.stack.addWidget(self.app_page)

        # Startzustand: Splash anzeigen
        self.stack.setCurrentWidget(self.splash)

        # ===== Opacity Effects =====
        # Diese Effekte erlauben es, die Transparenz eines Widgets zu ändern.
        # Sie sind die Grundlage für die Fade-Animation.
        self.splash_fx = QGraphicsOpacityEffect(self.splash)
        self.splash.setGraphicsEffect(self.splash_fx)
        self.splash_fx.setOpacity(1.0)  # voll sichtbar

        self.app_fx = QGraphicsOpacityEffect(self.app_page)
        self.app_page.setGraphicsEffect(self.app_fx)
        self.app_fx.setOpacity(1.0)  # wird später angepasst

        # ===== Animation-Referenzen =====
        # Wichtig: Wir speichern die Animationen als Attribute,
        # damit Python sie nicht „wegputzt“ (Garbage Collection).
        self._anim_out = None
        self._anim_in = None

    def go_to_app(self):
        """
        Diese Funktion wird aufgerufen,
        wenn im Splash-Screen der Start-Button gedrückt wird.

        Ablauf:
        1) Splash fade-out
        2) Seite wechseln (Splash -> App)
        3) App fade-in
        """

        # ===== Fade OUT Splash =====
        self._anim_out = QPropertyAnimation(self.splash_fx, b"opacity", self)
        self._anim_out.setDuration(220)     # Dauer in ms
        self._anim_out.setStartValue(1.0)   # sichtbar
        self._anim_out.setEndValue(0.0)     # unsichtbar

        def after_fade_out():
            """
            Wird aufgerufen, wenn der Splash-Fade beendet ist.
            """
            # Seite wechseln: jetzt App anzeigen
            self.stack.setCurrentWidget(self.app_page)

            # App-Seite erst unsichtbar machen
            self.app_fx.setOpacity(0.0)

            # ===== Fade IN App =====
            self._anim_in = QPropertyAnimation(self.app_fx, b"opacity", self)
            self._anim_in.setDuration(220)
            self._anim_in.setStartValue(0.0)   # unsichtbar
            self._anim_in.setEndValue(1.0)     # sichtbar

            def after_fade_in():
                """
                Optional:
                Splash-Opacity wieder auf 1 setzen,
                falls man später noch einmal zurückwechseln will.
                """
                self.splash_fx.setOpacity(1.0)

            self._anim_in.finished.connect(after_fade_in)
            self._anim_in.start()

        # Wenn Fade-Out fertig ist, starten wir den Seitenwechsel
        self._anim_out.finished.connect(after_fade_out)
        self._anim_out.start()

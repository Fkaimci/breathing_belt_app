"""


Diese Datei ist die „Hauptseite“ der App nach dem Startscreen (Splash).
Hier wird das Layout zusammengebaut:

- Oben: TopBar (Name, aktuelle Seite, später BLE-Status)
- Links: Sidebar-Navigation (Live / Kalibrierung / Einstellungen)
- Rechts: der Seitenbereich (QStackedWidget), wo die aktuellen Seiten angezeigt werden

Wichtig für unser Projekt:
- Hier sitzt auch die Kalibrierlogik (2 Sekunden Mittelwert).
- Der Offset wird gespeichert und an die LivePage weitergegeben.
- Später wird die Fake-Datenquelle durch BLE-Daten ersetzt, ohne das UI neu zu bauen.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QSizePolicy, QStackedWidget
)

from core.theme import add_shadow
from core.data_source import FakeBreathSource
from ui.topbar import TopBar
from ui.live_page import LivePage
from ui.calibration_page import CalibrationPage
from ui.settings_page import SettingsPage


class AppPage(QWidget):
    """
    AppPage = „Haupt-Container“ der Anwendung.

    Aufgabe:
    - Baut das Layout (TopBar + Sidebar + Seitenbereich).
    - Verwaltet die Navigation zwischen Seiten.
    - Enthält die Kalibrierlogik:
        -> 2 Sekunden lang Rohwerte sammeln
        -> Mittelwert berechnen
        -> als Offset speichern
        -> Offset an LivePage geben (damit das Signal um 0 liegt)
    """

    def __init__(self):
        super().__init__()

        # Offset = gespeicherter Nullpunkt.
        # Der wird bei der Kalibrierung gesetzt.
        self.offset = 0.0

        # ====== Grundlayout (oben/unten) ======
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ====== TopBar (oben) ======
        self.topbar = TopBar()
        root.addWidget(self.topbar)
        add_shadow(self.topbar, radius=24, dy=8, alpha=120)

        # ====== Inhalt (links Sidebar / rechts Seiten) ======
        content = QHBoxLayout()
        content.setSpacing(12)
        root.addLayout(content, stretch=1)

        # ====== Sidebar (links) ======
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")     # wichtig fürs Styling im Theme
        sidebar.setFixedWidth(220)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(14, 14, 14, 14)
        side.setSpacing(10)

        # App-Name / Branding
        brand = QLabel("🫁  Atemgurt")
        brand.setStyleSheet("font-size: 18px; font-weight: 800;")
        side.addWidget(brand)

        # Projekt-Hinweis (Uni)
        tag = QLabel("Programmierübung 3")
        tag.setStyleSheet("font-size: 11px; color: #9b9b9b;")
        side.addWidget(tag)

        # dünne Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.08);")
        side.addWidget(line)

        # ---- Helfer-Funktion für moderne Nav-Buttons ----
        # Vorteil: Alle Buttons sehen gleich aus und man kopiert weniger Code.
        def make_nav_button(icon_text: str, label: str) -> QPushButton:
            b = QPushButton(f"{icon_text}   {label}")  # Emoji + Text
            b.setObjectName("NavButton")               # wichtig fürs Styling im Theme
            b.setCursor(Qt.PointingHandCursor)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setMinimumHeight(42)
            return b

        # Drei Navigationseinträge
        self.btn_live = make_nav_button("📈", "Live")
        self.btn_cal = make_nav_button("🎯", "Kalibrierung")
        self.btn_settings = make_nav_button("⚙️", "Einstellungen")

        side.addWidget(self.btn_live)
        side.addWidget(self.btn_cal)
        side.addWidget(self.btn_settings)

        # Stretch drückt die Buttons nach oben, damit unten Platz bleibt
        side.addStretch(1)

        content.addWidget(sidebar)
        add_shadow(sidebar, radius=26, dy=10, alpha=120)

        # ====== Seitenbereich (rechts) ======
        # QStackedWidget ist wie ein „Kartenstapel“:
        # Es zeigt immer nur eine Seite gleichzeitig.
        self.pages = QStackedWidget()

        # Datenquelle:
        # aktuell FakeBreathSource (Sinus), später BLE-Daten vom ESP32.
        data_source = FakeBreathSource()

        # Live-Seite (Plot)
        self.page_live = LivePage(data_source)

        # Settings-Seite (Platzhalter)
        self.page_settings = SettingsPage()

        # Kalibrierseite:
        # Wir geben Funktionen rein, damit die CalibrationPage „Rückfragen“ an AppPage stellen kann.
        # So bleibt CalibrationPage UI-lastig und AppPage macht die Logik.
        self.page_cal = CalibrationPage(
            on_set_zero_avg=self.set_zero_avg_from_live,  # starte 2s Mittelwert-Kalibrierung
            on_reset=self.reset_offset,                   # Offset löschen
            get_offset=self.get_offset,                   # Offset anzeigen
            get_raw_value=self.get_raw_value              # Rohwert anzeigen
        )

        # Reihenfolge in pages ist wichtig:
        # index 0 = Live, index 1 = Kalibrierung, index 2 = Einstellungen
        self.pages.addWidget(self.page_live)
        self.pages.addWidget(self.page_cal)
        self.pages.addWidget(self.page_settings)

        content.addWidget(self.pages, stretch=1)

        # ====== Navigation (Button-Klicks) ======
        # Beim Klick wechseln wir die Seite und setzen den Titel in der TopBar.
        self.btn_live.clicked.connect(lambda: self.set_page(0, "Live"))
        self.btn_cal.clicked.connect(lambda: self.set_page(1, "Kalibrierung"))
        self.btn_settings.clicked.connect(lambda: self.set_page(2, "Einstellungen"))

        # Startzustand: Live-Seite
        self.set_page(0, "Live")

        # Statusanzeige (später wird hier BLE-Status gesetzt)
        self.topbar.set_status(False)  # False = Offline

    def set_page(self, idx: int, title: str):
        """
        Wechselt die aktuell sichtbare Seite.

        - idx = Index im QStackedWidget (0/1/2)
        - title = Text, der oben in der TopBar angezeigt wird
        """
        self.pages.setCurrentIndex(idx)
        self.topbar.set_page_title(title)

        # Active-State in der Sidebar setzen:
        # Der aktive Button bekommt im Theme eine andere Hintergrundfarbe.
        buttons = [self.btn_live, self.btn_cal, self.btn_settings]
        for i, b in enumerate(buttons):
            b.setProperty("active", i == idx)

            # unpolish/polish zwingt Qt, das Styling neu anzuwenden
            b.style().unpolish(b)
            b.style().polish(b)

    # ====== Kalibrierung / Offset ======

    def get_offset(self) -> float:
        """Gibt den aktuellen Offset (Nullpunkt) zurück."""
        return float(self.offset)

    def get_raw_value(self) -> float:
        """
        Gibt den aktuellen Rohwert zurück.
        Der Rohwert kommt aus der LivePage (dort wird er bei jedem Update gespeichert).
        """
        return float(self.page_live.last_raw)

    def reset_offset(self):
        """
        Setzt den Offset zurück auf 0.
        Dadurch wird wieder das Rohsignal ohne Nullpunkt-Korrektur angezeigt.
        """
        self.offset = 0.0
        self.page_live.set_offset(self.offset)
        self.topbar.status_text.setText("Offset reset")

    def set_zero_avg_from_live(self, done_callback=None):
        """
        Kalibrierung: Nullpunkt setzen über einen Mittelwert.

        Idee:
        - 2 Sekunden lang Rohwerte sammeln (alle 50ms ein Sample)
        - Mittelwert berechnen
        - Mittelwert als Offset speichern
        - Offset an LivePage geben

        Vorteil:
        - weniger empfindlich gegen kurze Zuckler/Bewegung als „nur ein einzelner Wert“
        """

        samples = []
        self.topbar.status_text.setText("Kalibrieren…")

        # collect() wird regelmäßig aufgerufen und sammelt Rohwerte
        def collect():
            samples.append(float(self.page_live.last_raw))

        # finish() wird nach 2 Sekunden einmalig aufgerufen
        def finish():
            self.sample_timer.stop()
            self.finish_timer.stop()

            # Offset = Mittelwert, wenn wir Samples haben.
            # Falls nicht (sollte fast nie passieren), nehmen wir den aktuellen Rohwert.
            self.offset = (sum(samples) / len(samples)) if samples else float(self.page_live.last_raw)

            # Offset an LivePage geben:
            # LivePage zieht offset dann von allen neuen Rohwerten ab.
            self.page_live.set_offset(self.offset)

            self.topbar.status_text.setText("Kalibriert")

            # done_callback: damit die CalibrationPage weiß, dass die Kalibrierung fertig ist
            # (z.B. um „✅“ anzuzeigen)
            if done_callback:
                done_callback()

        # Timer 1: sammelt alle 50ms einen Rohwert
        self.sample_timer = QTimer(self)
        self.sample_timer.timeout.connect(collect)
        self.sample_timer.start(50)

        # Timer 2: stoppt nach 2 Sekunden und berechnet den Offset
        self.finish_timer = QTimer(self)
        self.finish_timer.setSingleShot(True)
        self.finish_timer.timeout.connect(finish)
        self.finish_timer.start(2000)

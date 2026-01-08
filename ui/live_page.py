"""
ui/live_page.py

Diese Seite zeigt die Atmung als Live-Plot.

Wichtig für unser Projekt:
- Der ESP32 (später per BLE) liefert Rohwerte.
- Wir ziehen einen Offset ab (Kalibrierung), damit „Nullpunkt“ bei 0 liegt.
- Der Plot wächst nach rechts (Zeit läuft vorwärts).
- Alte Werte verschwinden links aus dem sichtbaren Bereich (wie ein Live-Monitor).

UI/UX:
- Startpunkt (x=0) wird als Punkt angezeigt.
- „Jetzt“-Punkt zeigt den aktuellen Wert und ändert seine Größe (pulsieren).
- Nutzer:innen sollen nicht zoomen oder verschieben -> Plot bleibt kontrolliert.
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
import pyqtgraph as pg

from core.theme import add_shadow
from core.data_source import FakeBreathSource


class LivePage(QWidget):
    """
    LivePage = Live-Ansicht der Atmung.

    Aufgabe:
    - Holt regelmäßig neue Werte (Timer).
    - Rechnet Rohwert -> Live-Wert (Rohwert minus Offset).
    - Zeichnet die Kurve und zwei Punkte:
        - Startpunkt: wo die Messung angefangen hat
        - Jetzt-Punkt: aktueller Wert (pulsierend)
    """

    def __init__(self, data_source: FakeBreathSource):
        super().__init__()

        # data_source liefert neue Messwerte.
        # Aktuell FakeBreathSource (Sinus), später BLE-Quelle.
        self.data_source = data_source

        # ===== Kalibrierung =====
        # offset wird bei „Nullpunkt setzen“ gesetzt.
        # live_value = raw_value - offset
        self.offset = 0.0

        # last_raw speichern wir, damit die Kalibrierseite den Rohwert anzeigen kann.
        self.last_raw = 0.0

        # ===== Zeit & Daten =====
        # t = Zeit (Sekunden) seit Start/Reset
        self.t = 0.0

        # x_data / y_data sind die gespeicherten Punkte für die Kurve
        self.x_data = []
        self.y_data = []

        # Wie viele Sekunden sollen sichtbar sein?
        # Alles ältere läuft links aus dem Bild raus.
        self.window_seconds = 10.0

        # ===== Layout =====
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel("Live")
        header.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(header)

        # Card ist die „schöne Box“ um den Plot (modernes UI)
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)

        # ===== PlotWidget (pyqtgraph) =====
        self.plot = pg.PlotWidget()
        self.plot.setLabel("left", "Dehnung")
        self.plot.setLabel("bottom", "Zeit (s)")

        # Clean look: kein kariertes Grid
        self.plot.showGrid(x=False, y=False)

        # Wichtig: Nutzer:innen sollen NICHT zoomen/verschieben.
        # Die Skalierung steuert unsere App automatisch.
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.setMenuEnabled(False)  # Rechtsklick-Menü aus

        # Extra-Sicherheit: ViewBox ebenfalls „stumm“ stellen
        self.plot.getViewBox().setMouseEnabled(x=False, y=False)

        # ===== Null-Linie bei y=0 =====
        # Hilft zu sehen: ist man über/unter dem Nullpunkt.
        self.zero_line = pg.InfiniteLine(pos=0, angle=0, movable=False)
        self.plot.addItem(self.zero_line)

        # ===== Atemkurve =====
        # Leere Kurve am Anfang, wird später mit Daten gefüllt.
        self.curve = self.plot.plot([], [])

        # ===== Startpunkt =====
        # Punkt an x=0, y=erstem Wert.
        # Zeigt: hier hat die Messung angefangen.
        self.start_point = self.plot.plot(
            [0], [0],
            pen=None,
            symbol='o',
            symbolSize=10,
            symbolBrush='w'
        )

        # ===== Jetzt-Punkt =====
        # Zeigt: aktueller Wert ganz rechts.
        self.now_point = self.plot.plot(
            [], [],
            pen=None,
            symbol='o',
            symbolSize=9,
            symbolBrush='#2F80ED'
        )

        # ===== Pulsieren (Größe des Jetzt-Punkts) =====
        # Wir begrenzen die Größe, damit es nicht „wild“ wird.
        self.now_point_size = 9
        self.min_point_size = 6
        self.max_point_size = 16

        card_layout.addWidget(self.plot)
        layout.addWidget(card, stretch=1)
        add_shadow(card, radius=28, dy=12, alpha=120)

        # ===== Timer für Live-Update =====
        # Alle 50ms (20 Hz) holen wir einen neuen Wert und aktualisieren den Plot.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

    def update_plot(self):
        """
        Diese Funktion läuft 20x pro Sekunde (alle 50ms).

        Schritte:
        1) Rohwert holen (aktuell Fake, später BLE)
        2) Rohwert speichern (für Kalibrierseite)
        3) Offset abziehen -> Live-Wert
        4) Daten an Kurve anhängen
        5) Sichtfenster (X-Achse) auf „letzte 10 Sekunden“ setzen
        6) Y-Achse automatisch passend setzen
        7) Jetzt-Punkt aktualisieren und „pulsieren“ lassen
        """

        # 1) Rohwert holen
        raw = self.data_source.get_value()

        # 2) speichern (damit andere Seiten darauf zugreifen können)
        self.last_raw = raw

        # 3) Kalibrierung: Offset abziehen
        value = raw - self.offset

        # 4) neuen Punkt an die Kurve anhängen
        self.x_data.append(self.t)
        self.y_data.append(value)
        self.curve.setData(self.x_data, self.y_data)

        # Startpunkt aktualisieren (y = erster Messwert)
        if self.y_data:
            self.start_point.setData([0], [self.y_data[0]])

        # Zeit fortschreiben:
        # current_t ist die Zeit, die zu *diesem* value gehört.
        current_t = self.t
        self.t += 0.05  # weil wir alle 50ms updaten

        # 5) X-Achse: immer die letzten window_seconds anzeigen
        left = max(0.0, self.t - self.window_seconds)
        self.plot.setXRange(left, self.t, padding=0)

        # 6) Y-Achse automatisch anpassen (nur aktuelle Fenster-Werte)
        # Dadurch bleibt der Plot immer „passend“, ohne Nutzer-Zoom.
        if len(self.y_data) > 5:
            # Anzahl Samples im sichtbaren Fenster:
            # 0.05s pro Sample -> window_seconds / 0.05
            n = int(self.window_seconds / 0.05)
            recent = self.y_data[-n:] if len(self.y_data) > n else self.y_data

            y_min = min(recent)
            y_max = max(recent)

            # Kleiner Rand, damit die Linie nicht am Rand klebt
            pad = max(0.1, (y_max - y_min) * 0.15)
            self.plot.setYRange(y_min - pad, y_max + pad, padding=0)

        # 7) Pulsieren: Punkt wird größer bei größerem Ausschlag
        # (abs(value) = „Atemtiefe“, ganz grob)
        scale = abs(value)
        target_size = 8 + scale * 8
        target_size = max(self.min_point_size, min(self.max_point_size, target_size))
        self.now_point_size = target_size

        # Jetzt-Punkt an das rechte Ende setzen
        self.now_point.setData([current_t], [value], symbolSize=self.now_point_size)

    def set_offset(self, offset: float):
        """
        Setzt einen neuen Offset (Nullpunkt).

        Zusätzlich machen wir einen Reset der Kurve, damit:
        - Zeit wieder bei 0 startet
        - der Startpunkt wieder sinnvoll ist
        - man sofort erkennt: neue Messung ab jetzt
        """
        self.offset = float(offset)

        # Reset bei neuer Kalibrierung
        self.t = 0.0
        self.x_data.clear()
        self.y_data.clear()
        self.curve.setData([], [])
        self.start_point.setData([0], [0])
        self.now_point.setData([], [])

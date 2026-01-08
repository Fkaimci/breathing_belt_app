'''
Diese Seite visualisiert die Atembewegung in Echtzeit als wachsenden Graphen. 
Der Plot zeigt den Startpunkt der Messung sowie einen pulsierenden „Jetzt“-Punkt, 
der den aktuellen Atemzustand darstellt. Die Darstellung ist zeitbasiert und 
blendet ältere Daten nach links aus, um einen klaren Live-Charakter zu erzeugen.
'''
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
import pyqtgraph as pg

from core.theme import add_shadow
from core.data_source import FakeBreathSource


class LivePage(QWidget):
    def __init__(self, data_source: FakeBreathSource):
        super().__init__()
        self.data_source = data_source

        # Kalibrierung
        self.offset = 0.0
        self.last_raw = 0.0

        # Zeit & Daten
        self.t = 0.0
        self.x_data = []
        self.y_data = []
        self.window_seconds = 10.0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel("Live")
        header.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)

        self.plot = pg.PlotWidget()
        self.plot.setLabel("left", "Dehnung")
        self.plot.setLabel("bottom", "Zeit (s)")

        # Clean look: kein Grid
        self.plot.showGrid(x=False, y=False)

        # Nutzer-Interaktion deaktivieren (kein Zoom/Pan)
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.setMenuEnabled(False)

        # Optional: auch kein Zoom per Mausrad (meist schon durch setMouseEnabled ok)
        self.plot.getViewBox().setMouseEnabled(x=False, y=False)


        # Null-Linie
        self.zero_line = pg.InfiniteLine(pos=0, angle=0, movable=False)
        self.plot.addItem(self.zero_line)

        # Atemkurve
        self.curve = self.plot.plot([], [])

        # Startpunkt
        self.start_point = self.plot.plot(
            [0], [0],
            pen=None,
            symbol='o',
            symbolSize=10,
            symbolBrush='w'
        )

        # Jetzt-Punkt
        self.now_point = self.plot.plot(
            [], [],
            pen=None,
            symbol='o',
            symbolSize=9,
            symbolBrush='#2F80ED'
        )

        # Pulsieren
        self.now_point_size = 9
        self.min_point_size = 6
        self.max_point_size = 16

        card_layout.addWidget(self.plot)
        layout.addWidget(card, stretch=1)
        add_shadow(card, radius=28, dy=12, alpha=120)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)  # 20 Hz

    def update_plot(self):
        raw = self.data_source.get_value()
        self.last_raw = raw
        value = raw - self.offset

        self.x_data.append(self.t)
        self.y_data.append(value)
        self.curve.setData(self.x_data, self.y_data)

        if self.y_data:
            self.start_point.setData([0], [self.y_data[0]])

        current_t = self.t
        self.t += 0.05

        left = max(0.0, self.t - self.window_seconds)
        self.plot.setXRange(left, self.t, padding=0)

        # Y-Achse automatisch anpassen (letzte Werte im Fenster)
        if len(self.y_data) > 5:
            # nur die Werte im sichtbaren X-Fenster betrachten
            # (wir nehmen grob die letzten window_seconds / 0.05 Samples)
            n = int(self.window_seconds / 0.05)
            recent = self.y_data[-n:] if len(self.y_data) > n else self.y_data

            y_min = min(recent)
            y_max = max(recent)

            # kleiner Rand, damit es nicht am Rand klebt
            pad = max(0.1, (y_max - y_min) * 0.15)
            self.plot.setYRange(y_min - pad, y_max + pad, padding=0)


        # Pulsieren abhängig von Atemtiefe
        scale = abs(value)
        target_size = 8 + scale * 8
        target_size = max(self.min_point_size, min(self.max_point_size, target_size))
        self.now_point_size = target_size

        self.now_point.setData([current_t], [value], symbolSize=self.now_point_size)

    def set_offset(self, offset: float):
        self.offset = float(offset)

        # Reset bei neuer Kalibrierung
        self.t = 0.0
        self.x_data.clear()
        self.y_data.clear()
        self.curve.setData([], [])
        self.start_point.setData([0], [0])
        self.now_point.setData([], [])

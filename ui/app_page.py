'''
Diese Datei enthält das Hauptlayout der Anwendung nach dem Startscreen: 
TopBar, Sidebar-Navigation und die einzelnen Seiten (Live, Kalibrierung, Einstellungen). 
Außerdem liegt hier die Kalibrierlogik (2-Sekunden-Mittelwert), 
die den Offset setzt und an die LivePage weitergibt. 
Damit ist die UI-Struktur zentral organisiert und bleibt trotzdem modular.
'''

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
    def __init__(self):
        super().__init__()
        self.offset = 0.0

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        self.topbar = TopBar()
        root.addWidget(self.topbar)
        add_shadow(self.topbar, radius=24, dy=8, alpha=120)

        content = QHBoxLayout()
        content.setSpacing(12)
        root.addLayout(content, stretch=1)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(14, 14, 14, 14)
        side.setSpacing(10)

        brand = QLabel("🫁  Atemgurt")
        brand.setStyleSheet("font-size: 18px; font-weight: 800;")
        side.addWidget(brand)

        tag = QLabel("Programmierübung 3")
        tag.setStyleSheet("font-size: 11px; color: #9b9b9b;")
        side.addWidget(tag)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.08);")
        side.addWidget(line)

        # --- Modern Nav Buttons (Icon + Text) ---
        def make_nav_button(icon_text: str, label: str) -> QPushButton:
            b = QPushButton(f"{icon_text}   {label}")
            b.setObjectName("NavButton")
            b.setCursor(Qt.PointingHandCursor)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setMinimumHeight(42)
            return b

        self.btn_live = make_nav_button("📈", "Live")
        self.btn_cal = make_nav_button("🎯", "Kalibrierung")
        self.btn_settings = make_nav_button("⚙️", "Einstellungen")

        side.addWidget(self.btn_live)
        side.addWidget(self.btn_cal)
        side.addWidget(self.btn_settings)

        side.addStretch(1)

        content.addWidget(sidebar)
        add_shadow(sidebar, radius=26, dy=10, alpha=120)

        # Pages
        self.pages = QStackedWidget()

        data_source = FakeBreathSource()
        self.page_live = LivePage(data_source)
        self.page_settings = SettingsPage()

        self.page_cal = CalibrationPage(
            on_set_zero_avg=self.set_zero_avg_from_live,
            on_reset=self.reset_offset,
            get_offset=self.get_offset,
            get_raw_value=self.get_raw_value
        )

        self.pages.addWidget(self.page_live)
        self.pages.addWidget(self.page_cal)
        self.pages.addWidget(self.page_settings)

        content.addWidget(self.pages, stretch=1)

        # Navigation
        self.btn_live.clicked.connect(lambda: self.set_page(0, "Live"))
        self.btn_cal.clicked.connect(lambda: self.set_page(1, "Kalibrierung"))
        self.btn_settings.clicked.connect(lambda: self.set_page(2, "Einstellungen"))

        self.set_page(0, "Live")
        self.topbar.set_status(False)  # später BLE

    def set_page(self, idx: int, title: str):
        self.pages.setCurrentIndex(idx)
        self.topbar.set_page_title(title)

        buttons = [self.btn_live, self.btn_cal, self.btn_settings]
        for i, b in enumerate(buttons):
            b.setProperty("active", i == idx)
            b.style().unpolish(b)
            b.style().polish(b)

    # ---- Kalibrierung ----
    def get_offset(self) -> float:
        return float(self.offset)

    def get_raw_value(self) -> float:
        return float(self.page_live.last_raw)

    def reset_offset(self):
        self.offset = 0.0
        self.page_live.set_offset(self.offset)
        self.topbar.status_text.setText("Offset reset")

    def set_zero_avg_from_live(self, done_callback=None):
        samples = []
        self.topbar.status_text.setText("Kalibrieren…")

        def collect():
            samples.append(float(self.page_live.last_raw))

        def finish():
            self.sample_timer.stop()
            self.finish_timer.stop()

            self.offset = (sum(samples) / len(samples)) if samples else float(self.page_live.last_raw)
            self.page_live.set_offset(self.offset)
            self.topbar.status_text.setText("Kalibriert")

            if done_callback:
                done_callback()

        self.sample_timer = QTimer(self)
        self.sample_timer.timeout.connect(collect)
        self.sample_timer.start(50)

        self.finish_timer = QTimer(self)
        self.finish_timer.setSingleShot(True)
        self.finish_timer.timeout.connect(finish)
        self.finish_timer.start(2000)
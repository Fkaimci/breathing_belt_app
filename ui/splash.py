#Startscreen mit GIF + Start-Button
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class SplashPage(QWidget):
    def __init__(self, on_start_clicked):
        super().__init__()
        self.setStyleSheet("background: white; color: #111;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(14)

        gif_path = Path(__file__).resolve().parents[1] / "assets" / "atemgurt_breathing_logo_clean.gif"

        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)

        if gif_path.exists():
            self.movie = QMovie(str(gif_path))
            self.movie.setCacheMode(QMovie.CacheAll)
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.gif_label.setText(f"GIF fehlt:\n{gif_path}")
            self.gif_label.setStyleSheet("color: #cc0000; font-size: 14px;")

        title = QLabel("Atemgurt")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 34px; font-weight: 800; color: #111;")

        subtitle = QLabel("Live Atemanalyse")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #555;")

        self.start_btn = QPushButton("Start")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setFixedSize(240, 46)
        self.start_btn.clicked.connect(on_start_clicked)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: #2F80ED;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover { background: #2b73d6; }
            QPushButton:pressed { background: #245fb1; }
        """)

        layout.addStretch(1)
        layout.addWidget(self.gif_label)
        layout.addSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(18)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)
        layout.addStretch(2)

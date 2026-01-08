"""
ui/calibration_page.py

Diese Seite erklärt dem/der Nutzer:in Schritt für Schritt die Kalibrierung.

Wichtig fürs Projekt:
- Der Atemgurt misst „Rohwerte“ (Dehnung).
- Damit die Kurve später sinnvoll um 0 liegt, setzen wir einen Nullpunkt (Offset).
- Der Nullpunkt wird als 2-Sekunden-Mittelwert gemessen, um stabiler zu sein.

UI/UX:
- Schritt 1: Gurt anlegen (mit Bild + Info-Button)
- Schritt 2: Nullpunkt setzen (Countdown + Progressbar)
- Schritt 3: Danach normal weiteratmen (Hinweis + Info-Button)
- Scrollbar: damit man auf kleinen Fenstern trotzdem alles lesen kann
"""

from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QMessageBox, QToolButton, QProgressBar,
    QScrollArea
)


class CalibrationPage(QWidget):
    """
    CalibrationPage = Kalibrier-Anleitung + UI-Steuerung.

    Wichtig: Diese Klasse macht hauptsächlich UI.
    Die eigentliche Kalibrierlogik (Mittelwert berechnen, Offset setzen)
    passiert in AppPage. Deshalb bekommt diese Seite „Callbacks“ übergeben:

    - on_set_zero_avg(done_callback=...): startet Kalibrierung in AppPage
    - on_reset(): setzt Offset zurück
    - get_offset(): liefert aktuellen Offset zum Anzeigen
    - get_raw_value(): liefert aktuellen Rohwert zum Anzeigen
    """

    def __init__(self, on_set_zero_avg, on_reset, get_offset, get_raw_value):
        super().__init__()

        # Callbacks/„Funktionen von außen“
        self.on_set_zero_avg = on_set_zero_avg
        self.on_reset = on_reset
        self.get_offset = get_offset
        self.get_raw_value = get_raw_value

        # ===== Grundlayout =====
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        header = QLabel("Kalibrierung")
        header.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(header)

        # Card enthält den gesamten Inhalt (1/2/3)
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(18)

        # 1) / 2) / 3) als eigene „Bausteine“
        self._add_step_1(card_layout)
        self._divider(card_layout)
        self._add_step_2(card_layout)
        self._divider(card_layout)
        self._add_step_3(card_layout)

        # ===== ScrollArea =====
        # Damit man auch bei kleinen Fenstern alles sehen kann
        # (z.B. Schritt 3 wird sonst abgeschnitten).
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Scrollbar etwas „cleaner“ gestalten
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 8px 2px 8px 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.18);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255,255,255,0.28);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        scroll.setWidget(card)
        layout.addWidget(scroll, stretch=1)

        # ===== Live-Refresh =====
        # Wir aktualisieren Rohwert/Offset regelmäßig, damit man „live“ sieht,
        # was gerade ankommt (auch während man sich auf die Kalibrierung vorbereitet).
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.refresh)
        self.ui_timer.start(150)

        # ===== Countdown (3..2..1) =====
        self._countdown = 0
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._tick_countdown)

        # ===== Progress (2 Sekunden messen) =====
        self._progress_ms = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self._tick_progress)

        # initial einmal anzeigen
        self.refresh()

    # ---------------- STEP 1 ----------------
    def _add_step_1(self, layout):
        """
        Schritt 1: Gurt anlegen.
        - Text erklärt Position + Festigkeit
        - Bild zeigt die Stelle
        - Info-Button erklärt das „Warum“
        """
        title = QLabel("1) Gurt anlegen")
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(14)

        # Bildbox
        img = QLabel()
        img.setFixedSize(300, 220)
        img.setAlignment(Qt.AlignCenter)
        img.setStyleSheet("background: rgba(255,255,255,0.04); border-radius: 12px;")

        # Bild laden aus assets/
        img_path = Path(__file__).resolve().parents[1] / "assets" / "belt_placement.png"
        if img_path.exists():
            pix = QPixmap(str(img_path)).scaled(
                img.width(), img.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            img.setPixmap(pix)
        else:
            # Falls die Datei fehlt, zeigen wir einen Hinweis im UI
            img.setText("Bild fehlt:\nassets/belt_placement.png")
            img.setStyleSheet("color: #ff6b6b; background: rgba(255,255,255,0.03); border-radius: 12px;")

        row.addWidget(img)

        # Erklärungstext (leicht verständlich)
        text = QLabel(
            "• Direkt auf der Haut tragen (nicht über Kleidung).\n"
            "• Position: Bauchhöhe, unterhalb der Brust.\n"
            "• Eng anliegend, aber nicht einschnürend\n"
            "  (1–2 Finger sollten noch darunter passen)."
        )
        text.setStyleSheet("color: #cfcfcf; line-height: 1.4;")
        text.setWordWrap(True)
        row.addWidget(text, stretch=1)

        # Info-Button: erklärt „Warum genau dort?“
        row.addWidget(
            self._info_button(
                "Warum auf Bauchhöhe?",
                "Auf Bauchhöhe ist die Umfangsänderung beim Atmen meist am größten.\n\n"
                "Das liefert stabilere Messwerte und minimiert Störungen durch Schulter- oder Brustbewegungen."
            ),
            alignment=Qt.AlignTop
        )

        layout.addLayout(row)

    # ---------------- STEP 2 ----------------
    def _add_step_2(self, layout):
        """
        Schritt 2: Nullpunkt setzen.
        - Nutzer:in atmet aus
        - Countdown hilft, kurz still zu bleiben
        - Progress zeigt: wir messen 2 Sekunden
        """
        title = QLabel("2) Nullpunkt setzen")
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(14)

        text = QLabel(
            "• Setz dich ruhig hin oder steh entspannt.\n"
            "• Atme vollständig aus.\n"
            "• Halte kurz still.\n"
            "• Drücke dann „Nullpunkt setzen“.\n\n"
            "Die App misst 2 Sekunden und speichert den Mittelwert als Nullpunkt."
        )
        text.setStyleSheet("color: #cfcfcf; line-height: 1.4;")
        text.setWordWrap(True)
        row.addWidget(text, stretch=1)

        row.addWidget(
            self._info_button(
                "Warum beim Ausatmen?",
                "Beim vollständigen Ausatmen ist der Bauchumfang am kleinsten.\n\n"
                "Das ist ein stabiler Referenzpunkt, damit die Atemkurve später sauber um die Null-Linie liegt."
            ),
            alignment=Qt.AlignTop
        )

        layout.addLayout(row)

        # Live-Anzeige: Rohwert und aktueller Offset
        values_row = QHBoxLayout()
        values_row.setSpacing(18)

        self.raw_label = QLabel("Rohwert: —")
        self.raw_label.setStyleSheet("font-size: 12px; color: #cfcfcf;")
        values_row.addWidget(self.raw_label)

        self.offset_label = QLabel("Offset: 0.000")
        self.offset_label.setStyleSheet("font-size: 12px; color: #cfcfcf;")
        values_row.addWidget(self.offset_label)

        values_row.addStretch(1)
        layout.addLayout(values_row)

        # Status: zeigt Countdown / Messen / Fertig
        self.status_label = QLabel("Status: bereit")
        self.status_label.setStyleSheet("color: #9b9b9b; font-size: 12px;")
        layout.addWidget(self.status_label)

        # Progressbar: sichtbar nur während der 2s Messung
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar { background: rgba(255,255,255,0.06); border-radius: 4px; border: none; }
            QProgressBar::chunk { background: rgba(47,128,237,0.85); border-radius: 4px; }
        """)
        layout.addWidget(self.progress)

        # Buttons: Kalibrieren / Reset
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_zero = QPushButton("Nullpunkt setzen (2s Mittelwert)")
        self.btn_zero.setCursor(Qt.PointingHandCursor)
        self.btn_zero.clicked.connect(self.start_countdown)

        self.btn_reset = QPushButton("Offset zurücksetzen")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self._handle_reset)

        btn_row.addWidget(self.btn_zero)
        btn_row.addWidget(self.btn_reset)
        layout.addLayout(btn_row)

    # ---------------- STEP 3 ----------------
    def _add_step_3(self, layout):
        """
        Schritt 3: Live messen.
        - Nutzer:in atmet normal weiter
        - Hinweis: Kurve steigt beim Einatmen, fällt beim Ausatmen
        - Info-Button erklärt, was die Kurve bedeutet
        """
        title = QLabel("3) Live messen")
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(14)

        text = QLabel(
            "• Atme danach normal weiter.\n"
            "• Die Kurve steigt typischerweise beim Einatmen und fällt beim Ausatmen.\n"
            "• Wichtig sind Rhythmus und Ausschlagshöhe.\n\n"
            "Wenn sich der Gurt verschiebt oder die Kurve driftet:\n"
            "→ Kalibrierung erneut durchführen."
        )
        text.setStyleSheet("color: #cfcfcf; line-height: 1.4;")
        text.setWordWrap(True)
        row.addWidget(text, stretch=1)

        row.addWidget(
            self._info_button(
                "Was zeigt die Kurve?",
                "Die Kurve zeigt die relative Dehnung des Gurts.\n\n"
                "Sie misst keine Liter Luft, sondern das Atemmuster (Rhythmus und Tiefe der Atmung)."
            ),
            alignment=Qt.AlignTop
        )

        layout.addLayout(row)

    # ---------- Helpers ----------
    def _divider(self, layout):
        """Kleine Trennlinie zwischen den Schritten."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.08);")
        layout.addWidget(line)

    def _info_button(self, title, text):
        """
        Baut einen kleinen Info-Button („i“).
        Beim Klick öffnet sich ein Fenster mit einer kurzen Erklärung.
        """
        btn = QToolButton()
        btn.setText("i")
        btn.setFixedSize(32, 32)
        btn.setStyleSheet("""
            QToolButton {
                border-radius: 16px;
                background: rgba(255,255,255,0.06);
                color: #eaeaea;
                font-weight: 800;
                border: 1px solid rgba(255,255,255,0.08);
            }
            QToolButton:hover { background: rgba(255,255,255,0.12); }
        """)
        btn.clicked.connect(lambda: QMessageBox.information(self, title, text))
        return btn

    # ---------- Live refresh ----------
    def refresh(self):
        """
        Aktualisiert Rohwert und Offset-Anzeige.
        Läuft alle 150ms über self.ui_timer.
        """
        raw = float(self.get_raw_value())
        self.raw_label.setText(f"Rohwert: {raw:.3f}")
        self.offset_label.setText(f"Offset: {self.get_offset():.3f}")

    # ---------- Reset ----------
    def _handle_reset(self):
        """
        Offset zurücksetzen:
        - ruft on_reset() aus AppPage auf
        - setzt UI wieder in den Startzustand
        """
        self.on_reset()
        self.status_label.setText("Status: Offset zurückgesetzt")

        # laufende Timer stoppen, falls gerade Kalibrierung läuft
        self.progress_timer.stop()
        self.countdown_timer.stop()

        # Progressbar zurücksetzen
        self.progress.setVisible(False)
        self.progress.setValue(0)

        # Buttons wieder freigeben
        self.btn_zero.setEnabled(True)
        self.btn_reset.setEnabled(True)

    # ---------- Countdown + measurement ----------
    def start_countdown(self):
        """
        Startet den Countdown (3..2..1).
        Ziel: Nutzer:in soll kurz still bleiben, bevor gemessen wird.
        """
        self.btn_zero.setEnabled(False)
        self.btn_reset.setEnabled(False)

        self.progress.setVisible(False)
        self.progress.setValue(0)

        self._countdown = 3
        self.status_label.setText("Status: bereitmachen… (3)")
        self.countdown_timer.start(1000)

    def _tick_countdown(self):
        """
        Wird jede Sekunde aufgerufen, solange der Countdown läuft.
        Wenn Countdown fertig ist, startet die 2-Sekunden-Messung.
        """
        self._countdown -= 1

        if self._countdown > 0:
            self.status_label.setText(f"Status: bereitmachen… ({self._countdown})")
            return

        # Countdown fertig -> messen
        self.countdown_timer.stop()
        self.status_label.setText("Status: messe 2 Sekunden…")
        self._start_progress_2s()

        # Wichtig:
        # on_set_zero_avg() startet die echte Kalibrierlogik in AppPage
        # und ruft am Ende _calibration_done() über den Callback auf.
        self.on_set_zero_avg(done_callback=self._calibration_done)

    def _start_progress_2s(self):
        """Startet die Progressbar für 2 Sekunden."""
        self._progress_ms = 0
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.progress_timer.start(50)

    def _tick_progress(self):
        """
        Wird alle 50ms aufgerufen und erhöht die Progressbar.
        2000ms = 2 Sekunden -> dann stoppt sie.
        """
        self._progress_ms += 50
        pct = int(min(100, (self._progress_ms / 2000) * 100))
        self.progress.setValue(pct)

        if pct >= 100:
            self.progress_timer.stop()

    def _calibration_done(self):
        """
        Wird am Ende der Kalibrierlogik aufgerufen (über done_callback).
        Setzt UI wieder auf „fertig“.
        """
        self.progress_timer.stop()
        self.progress.setValue(100)
        self.status_label.setText("Status: Nullpunkt gesetzt ✅")
        self.btn_zero.setEnabled(True)
        self.btn_reset.setEnabled(True)

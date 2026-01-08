"""
core/theme.py

Diese Datei enthält das zentrale Styling der gesamten Anwendung.

Idee:
- Design (Farben, Schrift, Schatten) ist von Logik getrennt.
- Änderungen am Look müssen nur hier gemacht werden.
- Alle Seiten (Live, Kalibrierung, Settings, Splash) sehen automatisch gleich aus.

Das ist wichtig für größere Projekte und Teamarbeit.
"""

from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QApplication
import pyqtgraph as pg


def add_shadow(widget, radius=22, dx=0, dy=6, alpha=90):
    """
    Fügt einem Widget einen weichen Schatten hinzu.

    Zweck:
    - UI wirkt „angehoben“ und moderner
    - Card-Design wie in echten Apps

    Parameter:
    - radius: wie weich/unscharf der Schatten ist
    - dx, dy: Verschiebung des Schattens
    - alpha: Transparenz (0 = unsichtbar, 255 = schwarz)
    """
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setOffset(dx, dy)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)


def apply_theme(app: QApplication):
    """
    Wendet das globale Design der App an.

    Wird einmal beim Start (in main.py) aufgerufen.
    Ab dann gilt das Styling für ALLE Widgets.
    """

    # ===== pyqtgraph Styling =====
    # Hintergrund & Textfarbe für alle Plots
    pg.setConfigOption("background", "#141821")
    pg.setConfigOption("foreground", "w")

    # ===== Globale Schrift =====
    # Segoe UI ist unter Windows Standard -> gut lesbar
    app.setFont(QFont("Segoe UI", 10))

    # ===== Globales Qt-Stylesheet =====
    app.setStyleSheet("""
        /* Standard-Hintergrund für alle Widgets */
        QWidget {
            background: #0f1115;
            color: #eaeaea;
        }

        /* TopBar und Sidebar */
        QFrame#TopBar, QFrame#Sidebar {
            background: #141821;
            border: none;
            border-radius: 18px;
        }

        /* Karten (Cards) für Inhalte */
        QFrame#Card {
            background: #141821;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }

        /* ===== Sidebar Navigation Buttons ===== */
        QPushButton#NavButton {
            background: transparent;
            border: none;
            border-radius: 14px;
            text-align: left;
            padding: 10px 12px;
            font-size: 13px;
            color: #d7d7d7;
        }

        /* Hover-Effekt */
        QPushButton#NavButton:hover {
            background: rgba(255,255,255,0.06);
        }

        /* Aktiver Button (aktuelle Seite) */
        QPushButton#NavButton[active="true"] {
            background: rgba(47,128,237,0.20);
            color: white;
        }
    """)

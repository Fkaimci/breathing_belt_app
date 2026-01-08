#Damit wird später alles Styling sauber ausgelagert.
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QApplication
import pyqtgraph as pg


def add_shadow(widget, radius=22, dx=0, dy=6, alpha=90):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setOffset(dx, dy)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)


def apply_theme(app: QApplication):
    pg.setConfigOption("background", "#141821")
    pg.setConfigOption("foreground", "w")

    app.setFont(QFont("Segoe UI", 10))

    app.setStyleSheet("""
        QWidget { background: #0f1115; color: #eaeaea; }

        QFrame#TopBar, QFrame#Sidebar {
            background: #141821;
            border: none;
            border-radius: 18px;
        }

        QFrame#Card {
            background: #141821;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }

                /* Sidebar Buttons */
        QPushButton#NavButton {
            background: transparent;
            border: none;
            border-radius: 14px;
            text-align: left;
            padding: 10px 12px;
            font-size: 13px;
            color: #d7d7d7;
        }
        QPushButton#NavButton:hover {
            background: rgba(255,255,255,0.06);
        }
        QPushButton#NavButton[active="true"] {
            background: rgba(47,128,237,0.20);
            color: white;
        }

    """)

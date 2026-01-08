'''
Diese Seite dient als Platzhalter für zukünftige Einstellungen der Anwendung, 
wie Bluetooth-Verbindung, Abtastrate oder Datenexport. 
Sie zeigt die Struktur der App und ermöglicht eine klare Trennung zwischen Mess-, Kalibrier- und 
Konfigurationsfunktionen. 
Dadurch bleibt die Anwendung modular und erweiterbar.
'''
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QLabel("Einstellungen")
        header.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(header)

        text = QLabel("Hier kommt später BLE / Sampling / Export / Theme.")
        text.setStyleSheet("color: #bdbdbd;")
        layout.addWidget(text)

        layout.addStretch(1)

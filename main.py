'''
Diese Datei ist der Einstiegspunkt der Anwendung. 
Sie erstellt die Qt-Application, wendet das Theme an und startet das Hauptfenster. 
Alle UI- und Logik-Bausteine liegen ausgelagert in ui/ und core/, 
wodurch main.py bewusst klein und übersichtlich bleibt.
'''
import sys
from PySide6.QtWidgets import QApplication

from core.theme import apply_theme
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    apply_theme(app)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

'''
TopBar:
Die TopBar ist eine wiederverwendbare UI-Komponente,
die am oberen Rand der Anwendung angezeigt wird. 
Sie zeigt den Namen der Applikation, den aktuell geöffneten Bereich
sowie den aktuellen Verbindungsstatus zum Sensor an. 
Dadurch erhält die Nutzerin bzw. der Nutzer jederzeit
eine klare Orientierung innerhalb der Anwendung.
'''



from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout


class TopBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("TopBar")
        self.setFixedHeight(54)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        self.app_name = QLabel("Atemgurt")
        self.app_name.setStyleSheet("font-size: 14px; font-weight: 800;")

        self.page_title = QLabel("Live")
        self.page_title.setStyleSheet("font-size: 13px; color: #cfcfcf;")

        layout.addWidget(self.app_name)
        layout.addSpacing(10)
        layout.addWidget(self.page_title)
        layout.addStretch(1)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #ff4d4d; font-size: 14px;")
        self.status_text = QLabel("Offline")
        self.status_text.setStyleSheet("color: #bdbdbd; font-size: 12px;")

        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_text)

    def set_status(self, connected: bool):
        if connected:
            self.status_dot.setStyleSheet("color: #4cd964; font-size: 14px;")
            self.status_text.setText("Verbunden")
        else:
            self.status_dot.setStyleSheet("color: #ff4d4d; font-size: 14px;")
            self.status_text.setText("Offline")

    def set_page_title(self, text: str):
        self.page_title.setText(text)

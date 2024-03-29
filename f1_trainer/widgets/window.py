from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class Window(QWidget):
    _lbl_title: QLabel
    _txt_process_name: QLineEdit
    _txt_dll_path: QLineEdit
    _btn_inject: QPushButton
    _btn_eject: QPushButton

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Modding Framework")
        self.setWindowIcon(QIcon(":/icon.ico"))
        self._widgets()
        self._layout()
        self.setStyleSheet(
            """
            QLabel { font-size: 36px; font-weight: bold; }
            QWidget { font-size: 24px; }
        """
        )

    def _widgets(self):
        self._lbl_title = QLabel("DLL injection")
        self._txt_process_name = QLineEdit()
        self._txt_process_name.setPlaceholderText("Process name")
        self._txt_dll_path = QLineEdit()
        self._txt_dll_path.setPlaceholderText("DLL path")
        self._btn_inject = QPushButton("Inject")
        self._btn_eject = QPushButton("Eject")

    def _layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self._lbl_title)
        layout.addWidget(self._txt_process_name)
        layout.addWidget(self._txt_dll_path)
        layout.addWidget(self._btn_inject)
        layout.addWidget(self._btn_eject)
        layout.addStretch()

    # def _on_click(self) -> None:
    #     dll_absolute_path = "C:/Code/mrowrpurr/Fallout1_Trainer_Example/build/windows/x86/debug/f1_trainer.dll"
    #     process_name = "falloutwHR.exe"
    #     print(f"Injecting DLL: {dll_absolute_path} into process: {process_name}...")
    #     inject_dll(process_name, dll_absolute_path)

import platform

import win32file
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from f1_trainer.lib.dll_injection import inject_dll

DEFAULT_DLL_PATH = (
    "C:/Code/mrowrpurr/Fallout1_Trainer_Example/build/windows/x86/debug/f1_trainer.dll"
)


class Window(QWidget):
    _lbl_title: QLabel
    _txt_process_name: QLineEdit
    _txt_dll_path: QLineEdit
    _btn_inject: QPushButton
    _btn_eject: QPushButton
    _btn_quick_test: QPushButton

    def __init__(self) -> None:
        super().__init__()

        print(f"Platform: {platform.architecture()[0]}")

        self.setWindowTitle("Modding Framework")
        self.setWindowIcon(QIcon(":/icon.ico"))
        self._widgets()
        self._layout()
        self._events()
        self.setStyleSheet(
            """
            QLabel { font-size: 36px; font-weight: bold; }
            QWidget { font-size: 24px; }
        """
        )
        self._txt_dll_path.setText(DEFAULT_DLL_PATH)

    def _widgets(self):
        self._lbl_title = QLabel("DLL injection")
        self._txt_process_name = QLineEdit()
        self._txt_process_name.setPlaceholderText("Process name")
        self._txt_dll_path = QLineEdit()
        self._txt_dll_path.setPlaceholderText("DLL path")
        self._btn_inject = QPushButton("Inject")
        self._btn_eject = QPushButton("Eject")
        self._btn_quick_test = QPushButton("Quick Test")

    def _layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self._lbl_title)
        layout.addWidget(self._txt_process_name)
        layout.addWidget(self._txt_dll_path)
        layout.addWidget(self._btn_inject)
        layout.addWidget(self._btn_eject)
        layout.addStretch()
        layout.addWidget(self._btn_quick_test)

    def _events(self):
        self._btn_inject.clicked.connect(self._on_inject)
        self._btn_eject.clicked.connect(self._on_eject)
        self._btn_quick_test.clicked.connect(self._on_quick_test)

    def _on_inject(self) -> None:
        dll_absolute_path = self._txt_dll_path.text()
        process_name = self._txt_process_name.text()
        print(f"Injecting DLL: {dll_absolute_path} into process: {process_name}...")
        inject_dll(process_name, dll_absolute_path)

    def _on_eject(self) -> None:
        print("TODO")

    def run_client(self):
        pipe_name = r"\\.\pipe\ExamplePipe"
        try:
            handle = win32file.CreateFile(
                pipe_name,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None,
            )

            test_string = "hello world"
            win32file.WriteFile(handle, test_string.encode())

            resp = win32file.ReadFile(handle, 1024)
            print(f"Received: {resp[1].decode()}")

            win32file.CloseHandle(handle)
        except Exception as e:
            print(f"Failed to communicate with the named pipe: {e}")

    def _on_quick_test(self) -> None:
        self.run_client()

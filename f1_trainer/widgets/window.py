from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from f1_trainer.lib.dll_injection import inject_dll


class Window(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fallout 1 Trainer")
        self.setWindowIcon(QIcon(":/icon.ico"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        # One button!
        the_button = QPushButton("Inject DLL!")
        the_button.clicked.connect(self._on_click)
        layout.addWidget(the_button)

        layout.addStretch()

    def _on_click(self) -> None:
        dll_absolute_path = "C:/Code/mrowrpurr/Fallout1_Trainer_Example/build/windows/x86/debug/f1_trainer.dll"
        process_name = "falloutwHR.exe"
        print(f"Injecting DLL: {dll_absolute_path} into process: {process_name}...")
        inject_dll(process_name, dll_absolute_path)

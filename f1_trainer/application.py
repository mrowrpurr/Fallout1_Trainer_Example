from PySide6.QtWidgets import QApplication


class Application(QApplication):
    def __init__(self, argv: list[str] | None = None) -> None:
        super().__init__(argv or [])
        self.setApplicationName("Fallout 1 Trainer")
        self.setApplicationVersion("0.1.0")

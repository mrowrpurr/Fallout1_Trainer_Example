from PySide6.QtWidgets import QApplication

from mychatroombot.app.config import APPLICATION_NAME, APPLICATION_VERSION


class Application(QApplication):
    def __init__(self, argv: list[str] | None = None) -> None:
        super().__init__(argv or [])
        self.setApplicationName(APPLICATION_NAME)
        self.setApplicationVersion(APPLICATION_VERSION)

import asyncio
from pathlib import Path

import qasync  # type: ignore
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from f1_trainer.application import Application
from f1_trainer.files import read_file
from f1_trainer.fonts import load_fonts
from f1_trainer.qrc_resources import qt_resource_data
from f1_trainer.styles import watch_qss

QRC = qt_resource_data

DEVELOPMENT_PROJECT_ROOT = Path(__file__).parent.parent

STYLES_QSS_RESOURCE = ":/styles.qss"
STYLES_QSS_LOCAL_PATH = DEVELOPMENT_PROJECT_ROOT / "resources" / "styles.qss"
STYLES_SCSS_LOCAL_PATH = DEVELOPMENT_PROJECT_ROOT / "resources" / "styles" / "main.scss"


def main(development: bool = False) -> None:
    app = Application()
    app.setStyle("Fusion")

    # Setup asyncio
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    event_loop = qasync.QEventLoop(app)  # type: ignore
    asyncio.set_event_loop(event_loop)  # type: ignore

    # Load fonts
    load_fonts()

    # Setup styles
    if development:
        watch_qss(
            app,
            main_scss=str(STYLES_SCSS_LOCAL_PATH),
            out_qss=str(STYLES_QSS_LOCAL_PATH),
        )
    else:
        app.setStyleSheet(read_file(STYLES_QSS_RESOURCE))

    # Hello, app!
    window = QLabel("Hello, Fallout 1 trainer!")
    window.show()
    window.resize(800, 600)
    window.setWindowIcon(QPixmap(":/icon.ico"))

    # Run the app
    with event_loop:  # type: ignore
        event_loop.run_until_complete(future=app_close_event.wait())  # type: ignore

    print("Exiting...")


def dev():
    main(development=True)


def prod():
    main(development=False)


if __name__ == "__main__":
    main()

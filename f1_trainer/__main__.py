import asyncio
import os
from pathlib import Path

import qasync  # type: ignore
from dotenv import load_dotenv
from mychatroombot.database.config import init_database
from mychatroombot.speech_to_text import SpeechToText
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap

from mychatroombot.app.application import Application
from mychatroombot.app.files import read_file
from mychatroombot.app.fonts import load_fonts
from mychatroombot.app.qrc_resources import qt_resource_data
from mychatroombot.app.services.chat_service import ChatService
from mychatroombot.app.services.obs_microphone_service import ObsMicrophoneService
from mychatroombot.app.services.speech_to_text_service import SpeechToTextService
from mychatroombot.app.services.twitch_bot_service import TwitchBotService
from mychatroombot.app.styles import watch_qss
from mychatroombot.app.widgets.chat_view_widget import ChatViewWidget
from mychatroombot.app.widgets.obs_microphone_widget import ObsMicrophoneWidget
from mychatroombot.app.widgets.twitch_bot_widget import TwitchBotWidget

QRC = qt_resource_data

DOTENV_PATH = os.environ.get("DOTENV_PATH", ".env")

# TODO: make this less... parent.parent.parent. etc
DEVELOPMENT_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

STYLES_QSS_RESOURCE = ":/styles.qss"
STYLES_QSS_LOCAL_PATH = DEVELOPMENT_PROJECT_ROOT / "resources" / "styles.qss"
STYLES_SCSS_LOCAL_PATH = DEVELOPMENT_PROJECT_ROOT / "resources" / "styles" / "main.scss"


async def load_database(chat_view_widget: ChatViewWidget) -> None:
    await init_database()
    chat_view_widget.refresh_database.emit()


def main(development: bool = False) -> None:
    if DOTENV_PATH and Path(DOTENV_PATH).exists():
        load_dotenv(dotenv_path=DOTENV_PATH)

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

    # Chat View
    chat_view_widget = ChatViewWidget()
    chat_view_widget.resize(800, 600)
    chat_view_widget.setWindowIcon(QPixmap(":/icon.ico"))
    chat_view_widget.show()

    # Twitch Bot
    client_id = os.environ.get("TWITCH_APP_CLIENT_ID", "")
    client_secret = os.environ.get("TWITCH_APP_SECRET", "")
    channel_name = os.environ.get("TWITCH_CHANNEL", "")
    bot_username = os.environ.get("TWITCH_BOT_USERNAME", "")
    token_storage_file = os.environ.get("TWITCH_TOKEN_STORAGE_FILE", "")
    twitch_bot_service = TwitchBotService(
        client_id, client_secret, channel_name, bot_username, token_storage_file
    )
    twitch_bot_widget = TwitchBotWidget(twitch_bot_service)
    twitch_bot_widget.resize(800, 600)
    twitch_bot_widget.setWindowIcon(QPixmap(":/icon.ico"))
    twitch_bot_widget.show()

    # Chat Bot Service
    chat_service = ChatService(twitch_bot_service)

    # Speech to Text Callback
    speech_to_text_service = SpeechToTextService()

    # Speech to Text Service
    azure_region = os.environ.get("AZURE_REGION", "")
    azure_key = os.environ.get("AZURE_KEY", "")
    speech_to_text = SpeechToText(azure_region, azure_key)
    speech_to_text.on_recognized(speech_to_text_service.on_speech_utterance)

    # OBS Microphone Service
    websocket_uri = os.environ.get("OBS_WEBSOCKET_URI", "")
    websocket_password = os.environ.get("OBS_WEBSOCKET_PASSWORD", "")
    microphone_source_name = os.environ.get("OBS_MIC_SOURCE_NAME", "")
    obs_microphone_service = ObsMicrophoneService(
        microphone_source_name=microphone_source_name,
        websocket_uri=websocket_uri,
        websocket_password=websocket_password,
    )

    # OBS Microphone Widget
    obs_microphone_widget = ObsMicrophoneWidget(speech_to_text, obs_microphone_service)
    obs_microphone_widget.resize(800, 600)
    obs_microphone_widget.setWindowIcon(QPixmap(":/icon.ico"))
    obs_microphone_widget.show()

    # Using a QTimer, call window.refresh_database.emit() every 5 seconds
    timer = QTimer()
    timer.timeout.connect(chat_view_widget.refresh_database.emit)  # type: ignore
    timer.start(1000)

    # Run the app
    with event_loop:  # type: ignore
        event_loop.create_task(load_database(chat_view_widget))  # type: ignore
        event_loop.run_until_complete(future=app_close_event.wait())  # type: ignore

    print("Exiting...")


def dev():
    main(development=True)


def prod():
    main(development=False)


if __name__ == "__main__":
    main()

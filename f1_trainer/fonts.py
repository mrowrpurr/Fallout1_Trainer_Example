from PySide6.QtGui import QFontDatabase


def load_fonts():
    # Generated using BASH script (found in [root]/resources/qt/font-names.sh)
    custom_font_names = [
        "FuckinGwenhwyfar",
    ]

    for font_name in custom_font_names:
        QFontDatabase.addApplicationFont(f":/fonts/{font_name}.ttf")

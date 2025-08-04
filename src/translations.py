import os
import logging
from gettext import translation, NullTranslations

logging.basicConfig(level=logging.INFO)

localedir = os.path.join(os.path.dirname(__file__), "locales")


def get_translation():
    lang = os.getenv("PROJECT_LANG", "en_US")
    try:
        translations = translation("messages", localedir=localedir, languages=[lang])
    except FileNotFoundError:
        logging.warning(
            f"Translation file not found for language '{lang}'. Falling back to default (English)."
        )
        translations = NullTranslations()  # Fallback to no-op translations
    return translations.gettext

import os.path

import lime_translation as translate
from lime_application import LimeApplication


def register_translations():
    """
    Returns the path to the directory containing po-files.
    """
    return os.path.abspath(os.path.dirname(__file__))


def get_translation(
    app: LimeApplication, key: str, language: str = "", **kwargs
) -> str:
    """Fetches a translation for the current language by key.

    Args:
        app (LimeApplication): Application to use
        key (str): The Key you want to fetch a translation for.
                   Called msgid in the .po file.
        language (str): The language you want to fetch a translation for.
                        Defaults to app.language.
        **kwargs: Sent to lime_translation get_text() function

    Returns:
        LimeObject: The translation string
    """
    return translate.get_text(
        language if language else app.language, f"limepkg_scrive.{key}", **kwargs
    )

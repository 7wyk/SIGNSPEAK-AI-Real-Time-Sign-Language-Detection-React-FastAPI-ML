"""
Translation service using googletrans.
Preserves the exact language mapping from the Flask implementation.
"""

import logging

from googletrans import Translator

logger = logging.getLogger(__name__)

# Singleton translator instance (same as Flask's module-level initialization)
translator = Translator()

# Language name → ISO code mapping (matches frontend's SUPPORTED_LANGUAGES)
LANG_CODES = {
    "hindi": "hi",
    "kannada": "kn",
    "malayalam": "ml",
}


def translate_text(text: str, target_lang: str) -> tuple[bool, str, str]:
    """
    Translate text to the target language.

    Args:
        text: The text to translate.
        target_lang: Language name (hindi, kannada, malayalam) as sent by the frontend.

    Returns:
        Tuple of (success, translated_text_or_error, original_text)
    """
    target_code = LANG_CODES.get(target_lang.lower(), "hi")

    try:
        translated = translator.translate(text, dest=target_code)
        logger.info("Translated '%s' to %s (%s)", text, target_lang, target_code)
        return True, translated.text, text
    except Exception as e:
        logger.error("Translation error: %s", e)
        return False, str(e), text

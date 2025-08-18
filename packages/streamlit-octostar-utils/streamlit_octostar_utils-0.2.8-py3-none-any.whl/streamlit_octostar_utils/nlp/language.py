import re
import py3langid as langid
import iso639 as languages


def detect_language(text, min_confidence=None):
    detector = langid.langid.LanguageIdentifier.from_pickled_model(
        langid.langid.MODEL_FILE, norm_probs=True
    )
    detected_lang, confidence = detector.classify(text)
    if min_confidence and confidence < min_confidence:
        return None, confidence
    detected_lang = re.sub("[^A-Za-z]", "", detected_lang).lower()
    detected_lang = languages.to_name(detected_lang).lower()
    return detected_lang, confidence

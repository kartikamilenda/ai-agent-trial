def find_context(text: str, phrase: str, window: int = 110) -> str:
    """Return text around a matching phrase for meeting-context verification."""
    if not phrase:
        return ''
    index = text.casefold().find(phrase.casefold())
    return '' if index < 0 else text[max(0, index-window):index+len(phrase)+window]

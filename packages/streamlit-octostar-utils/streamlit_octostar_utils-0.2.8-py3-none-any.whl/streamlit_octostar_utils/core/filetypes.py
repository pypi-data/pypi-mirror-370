import mimetypes
import filetype


def add_filetypes():
    mimetypes.add_type("text/csv", ".csv")


def recognize_filetype(file=None, filename=None):
    if not (file or filename):
        raise ValueError("Must provide either file content or filename")
    from_name_guess = None
    from_file_guess = None
    if filename:
        from_name_guess, _ = mimetypes.guess_type(filename)
    if file:
        ft = filetype.guess(file)
        from_file_guess = ft.mime if ft else None
    def _family(m):
        return m.split("/", 1)[0] if isinstance(m, str) and "/" in m else None
    def _subtype(m):
        return m.split("/", 1)[-1] if isinstance(m, str) and "/" in m else None
    if not from_file_guess and not from_name_guess:
        return "unknown"
    if not (from_file_guess and from_name_guess):
        return from_file_guess or from_name_guess
    if _family(from_file_guess) != _family(from_name_guess):
        return from_file_guess
    if _subtype(from_file_guess) != _subtype(from_name_guess):
        return from_name_guess
    return from_name_guess

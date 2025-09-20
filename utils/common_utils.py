import json


def _read_text_with_fallback(file_path: str) -> str:
    """Read text from a file using a set of fallback encodings.

    Tries UTF-8 first (with and without BOM), then common Windows encodings.
    Final fallback uses UTF-8 with replacement to avoid crashing on bad bytes.
    """
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc, errors="strict") as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # Last resort: replace undecodable bytes so processing can continue
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def read_file(file_path: str) -> str:
    """
    Read a file and return its contents as a stripped string.
    Uses robust encoding fallbacks to avoid UnicodeDecodeError on Windows.
    """
    content = _read_text_with_fallback(file_path)
    return content.strip()


def load_json_file(file_path: str):
    """
    Load a JSON file and return its contents as a dictionary.

    Attempts multiple encodings, preferring UTF-8. Does not silently
    corrupt JSON; only as a last resort uses UTF-8 with replacement
    and will raise if JSON remains invalid.
    """
    # Read raw bytes to control decoding attempts
    with open(file_path, "rb") as f:
        data = f.read()

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    last_error = None
    for enc in encodings:
        try:
            text = data.decode(enc)
            return json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            last_error = e
            continue

    # Final attempt: decode with replacement and try to parse
    try:
        text = data.decode("utf-8", errors="replace")
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Failed to decode/parse JSON from {file_path}: {e.msg}", e.doc, e.pos
        )

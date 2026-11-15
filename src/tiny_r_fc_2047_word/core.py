import base64
import quopri
import re

# RFC 2047 encoded-word grammar:
#   encoded-word = "=?" charset "?" encoding "?" encoded-text "?="
# We deliberately accept any non-? bytes for charset to avoid rejecting
# slightly malformed real-world headers, but we still require the exact
# delimiters so that plain text containing "=?" is not eaten.
_ENCODED_WORD_RE = re.compile(
    r"=\?([^?]+)\?([QqBb])\?([^?]*)\?="
)


def decode_word(charset, encoding, encoded_text):
    """Decode a single encoded-word body into a ``str``.

    ``encoding`` is the single letter from the encoded-word (``Q``/``q`` or
    ``B``/``b``).  The encoded text is first decoded to bytes, then decoded
    using ``charset``.  Unknown charsets fall back to latin-1 instead of
    raising, because a header that cannot be decoded at all is worse than one
    decoded approximately.
    """
    encoding = encoding.upper()
    if encoding == "Q":
        # quopri.decodestring expects bytes; RFC 2047 Q encoding uses '_'
        # as a space, which quopri does not know about.
        raw = encoded_text.replace("_", " ").encode("ascii")
        data = quopri.decodestring(raw)
    elif encoding == "B":
        # base64.b64decode with validate=False silently ignores characters
        # outside the alphabet, matching common mail-client behaviour.
        data = base64.b64decode(encoded_text.encode("ascii"))
    else:
        raise ValueError("unsupported encoding: %r" % (encoding,))

    try:
        return data.decode(charset)
    except (LookupError, UnicodeDecodeError):
        return data.decode("latin-1")


def decode_header_value(value):
    """Replace every RFC 2047 encoded-word in ``value`` with its decoded text.

    Adjacent encoded-words separated only by whitespace are joined without
    the whitespace, as required by RFC 2047 section 6.2.  Whitespace between
    an encoded-word and ordinary text is preserved.
    """
    if not isinstance(value, str):
        raise TypeError("value must be str, got %r" % (type(value).__name__,))

    parts = []
    pos = 0
    last_was_word = False
    for match in _ENCODED_WORD_RE.finditer(value):
        between = value[pos:match.start()]
        if between:
            if last_was_word and between.strip() == "":
                # Drop whitespace-only separators between encoded-words.
                pass
            else:
                parts.append(between)
        charset, encoding, encoded_text = match.group(1, 2, 3)
        try:
            parts.append(decode_word(charset, encoding, encoded_text))
        except Exception:
            # Leave the original encoded-word untouched if it cannot be
            # decoded; that is more useful than dropping data.
            parts.append(match.group(0))
        last_was_word = True
        pos = match.end()
    parts.append(value[pos:])
    return "".join(parts)


def decode(value):
    """Alias for :func:`decode_header_value`."""
    return decode_header_value(value)

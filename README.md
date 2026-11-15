# tiny_r_fc_2047_word

Decode RFC 2047 encoded-word headers in email messages, handling
quoted-printable and base64 payloads inside charset-specified boundaries.

```python
from tiny_r_fc_2047_word import decode, decode_header_value, decode_word

# Whole header value: adjacent encoded-words are joined, ordinary text kept.
decode_header_value("=?utf-8?Q?caf=C3=A9?= =?utf-8?Q?_time?=")
# -> 'café time'

# A single encoded-word.
decode_word("utf-8", "B", "Y2Fmw6k=")
# -> 'café'

# `decode` is an alias for `decode_header_value`.
decode("=?utf-8?Q?ok?=")
# -> 'ok'
```

The three exported names are `decode_header_value`, `decode_word`, and the
alias `decode`.

## Why this exists

Header values arrive as a mix of plain text and RFC 2047 encoded-words, and
real mail clients are loose about the spec. The trade-off here is to decode
what we can and pass through what we cannot: an unknown charset falls back to
latin-1, and a malformed encoded-word is left verbatim rather than dropped or
allowed to raise. That keeps a single bad word from destroying an otherwise
readable subject line.

## The awkward edge

Whitespace between two adjacent encoded-words is removed, because RFC 2047
section 6.2 says the whitespace is an artefact of folding and is not part of
the text. Whitespace between an encoded-word and ordinary text is preserved.
If you need the raw header, read it from the message object instead of calling
this library.

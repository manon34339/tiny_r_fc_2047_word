"""Decode RFC 2047 encoded-word headers."""

from .core import decode, decode_header_value, decode_word

__all__ = ["decode", "decode_header_value", "decode_word"]

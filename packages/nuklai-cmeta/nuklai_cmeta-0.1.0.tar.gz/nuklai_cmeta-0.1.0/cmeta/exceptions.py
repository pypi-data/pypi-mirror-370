class CMetaError(Exception):
    """Base exception for CMeta package."""


class CMetaParseError(CMetaError):
    """Raised on invalid CMeta text."""

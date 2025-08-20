class MMDBError(Exception):
    """Base exception for mmdb-lite."""


class MetadataError(MMDBError):
    """Raised when the MMDB metadata block is invalid or missing required fields."""


class CorruptDatabaseError(MMDBError):
    """Raised when the MMDB file appears corrupt or structurally invalid."""


class UnsupportedRecordSizeError(MMDBError):
    """Raised when the MMDB record size is not one of the supported values (24, 28, 32)."""

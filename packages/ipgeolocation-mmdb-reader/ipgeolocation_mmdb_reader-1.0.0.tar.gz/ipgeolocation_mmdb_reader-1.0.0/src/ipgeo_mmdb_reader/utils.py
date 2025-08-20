from typing import Tuple, Protocol


class _Readable(Protocol):
    def __getitem__(self, key): ...  # noqa: E701


def decode_length(size_flag: int, mv: _Readable, offset: int) -> Tuple[int, int]:
    """Decode the variable-length size field used by MMDB values.

    Returns (length, new_offset).
    """
    if size_flag < 29:
        return size_flag, offset
    if size_flag == 29:
        b = mv[offset]
        return 29 + b, offset + 1
    if size_flag == 30:
        b1 = mv[offset]; b2 = mv[offset + 1]
        return 285 + ((b1 << 8) | b2), offset + 2
    b1 = mv[offset]; b2 = mv[offset + 1]; b3 = mv[offset + 2]
    return 65821 + ((b1 << 16) | (b2 << 8) | b3), offset + 3


def decode_pointer(size_flag: int, mv: _Readable, offset: int) -> Tuple[int, int]:
    """Decode a pointer header and return (relative_target, new_offset).

    The caller is responsible for adding the data-section base to the returned pointer.
    """
    sel = (size_flag >> 3) & 0x03
    part = size_flag & 0x07
    if sel == 0:
        return ((part << 8) | mv[offset]), offset + 1
    if sel == 1:
        return ((part << 16) | (mv[offset] << 8) | mv[offset + 1]) + 2048, offset + 2
    if sel == 2:
        return ((part << 24) | (mv[offset] << 16) | (mv[offset + 1] << 8) | mv[offset + 2]) + 526336, offset + 3
    v = (mv[offset] << 24) | (mv[offset + 1] << 16) | (mv[offset + 2] << 8) | mv[offset + 3]
    return v, offset + 4

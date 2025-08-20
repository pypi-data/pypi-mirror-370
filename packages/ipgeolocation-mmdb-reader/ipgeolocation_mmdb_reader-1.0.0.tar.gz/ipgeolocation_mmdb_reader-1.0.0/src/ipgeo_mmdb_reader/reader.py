from __future__ import annotations

import ipaddress
import struct
from array import array
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from .errors import UnsupportedRecordSizeError, CorruptDatabaseError, MMDBError, MetadataError
from .utils import decode_pointer, decode_length

try:
    import mmap
except Exception:
    mmap = None


_MAGIC = b"\xAB\xCD\xEFMaxMind.com"
_DATA_SECTION_SEPARATOR_SIZE = 16

class IPGeolocationMMDBReader:
    metadata: Dict[str, Any]
    node_count: int
    record_size: int
    ip_version: int
    bytes_per_node: int
    tree_size_bytes: int
    data_section_start: int

    def __init__(self, filename: Union[str, Path]) -> None:
        self._fh = None
        self._mm = None
        self._buf: Union[bytes, "mmap.mmap"]
        self._buf_size: int

        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError(str(path))

        if mmap is not None:
            f = path.open("rb")
            self._fh = f
            self._mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            self._buf = self._mm
            self._buf_size = self._mm.size()
        else:
            data = path.read_bytes()
            self._buf = data
            self._buf_size = len(data)

        self._mv = memoryview(self._buf)

        start = max(0, self._buf_size - 128 * 1024)
        marker_at = self._rfind_in_buffer(_MAGIC, start)
        if marker_at == -1:
            marker_at = self._rfind_in_buffer(_MAGIC, 0)
        if marker_at == -1:
            self.close()
            raise MetadataError("Not a valid MMDB file: metadata marker not found")
        self.metadata_start = marker_at + len(_MAGIC)

        meta, _ = self._parse_value(self.metadata_start, pointer_base=self.metadata_start, context="metadata")
        if not isinstance(meta, dict):
            self.close()
            raise MetadataError("Invalid metadata map")
        self.metadata = meta

        try:
            self.node_count = int(self.metadata["node_count"])
            self.record_size = int(self.metadata["record_size"])
            self.ip_version = int(self.metadata["ip_version"])
        except KeyError as e:
            self.close()
            raise MetadataError(f"Missing metadata field: {e!s}")

        if self.record_size not in (24, 28, 32):
            self.close()
            raise UnsupportedRecordSizeError(f"Unsupported record_size: {self.record_size}")

        self.bytes_per_node = (self.record_size * 2) // 8
        self.tree_size_bytes = self.bytes_per_node * self.node_count
        self.data_section_start = self.tree_size_bytes + _DATA_SECTION_SEPARATOR_SIZE
        if self.data_section_start > self.metadata_start:
            self.close()
            raise CorruptDatabaseError("Corrupt MMDB: data overlaps metadata")

        self._data_cache: Dict[int, Any] = {}

        self._left: Optional[array] = None
        self._right: Optional[array] = None

        self._ipv4_start_node: Optional[int] = None
        if self.ip_version == 6:
            self._ipv4_start_node = self._compute_ipv4_start_node()

    def __enter__(self) -> "IPGeolocationMMDBReader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        try:
            mv = getattr(self, "_mv", None)
            if mv is not None and hasattr(mv, "release"):
                try:
                    mv.release()
                except Exception:
                    pass
            self._mv = None
            if self._mm is not None:
                self._mm.close()
        except Exception:
            pass
        try:
            if self._fh is not None:
                self._fh.close()
        except Exception:
            pass

    def get_metadata(self) -> Dict[str, Any]:
        """Return a shallow copy of the metadata block."""
        return dict(self.metadata)

    def lookup(self, ip: Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address]) -> Optional[Any]:
        """Return the decoded data for an IP, or None if not found."""
        node = self._walk_from_ip(ip)
        if node == self.node_count:
            return None
        if node > self.node_count:
            return self._parse_value_at_data_pointer(node)
        return self._descend_to_data(node)

    def lookup_ipobj(self, ip: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> Optional[Any]:
        """Like :meth:`lookup` but requires an already-parsed ipaddress object."""
        node = self._walk_from_ip_obj(ip)
        if node == self.node_count:
            return None
        if node > self.node_count:
            return self._parse_value_at_data_pointer(node)
        return self._descend_to_data(node)

    def lookup_packed(self, packed: bytes, *, ipv4: bool) -> Optional[Any]:
        """Lookup using a packed 4/16-byte address.

        Set `ipv4=True` when passing a 4-byte IPv4 address against an IPv6 DB
        to start from the IPv4 subtree root.
        """
        node = self._walk_packed(packed, start_node=(self._ipv4_start_node or 0) if (ipv4 and self.ip_version == 6) else 0)
        if node == self.node_count:
            return None
        if node > self.node_count:
            return self._parse_value_at_data_pointer(node)
        return self._descend_to_data(node)

    def lookup_offset(self, ip: Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address]) -> int:
        """Return absolute data offset (0 if empty/no match). No decoding."""
        node = self._walk_from_ip(ip)
        if node == self.node_count:
            return 0
        if node > self.node_count:
            return self.tree_size_bytes + (node - self.node_count)
        l = self._left
        if l is not None:
            n = node
            nc = self.node_count
            while True:
                p = l[n]
                if p < nc:
                    n = p
                elif p == nc:
                    return 0
                else:
                    return self.tree_size_bytes + (p - nc)
        else:
            return self._descend_to_data_offset_fallback(node)

    def decode_at(self, absolute_offset: int) -> Any:
        """Decode a value starting at `absolute_offset` in the file's data section."""
        value, _ = self._parse_value(absolute_offset, pointer_base=self.data_section_start, context="data")
        return value

    def lookup_many(self, ips: Iterable[Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address]]) -> Iterable[Tuple[Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address], Optional[Any]]]:
        """Batch helper yielding (ip, result)."""
        for ip in ips:
            yield ip, self.lookup(ip)

    def _walk_from_ip(self, ip: Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address]) -> int:
        ip_obj = self._coerce_ip(ip)
        return self._walk_from_ip_obj(ip_obj)

    def _walk_from_ip_obj(self, ip_obj: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> int:
        if isinstance(ip_obj, ipaddress.IPv6Address) and self.ip_version == 4:
            raise MMDBError("IPv6 lookup in an IPv4-only DB")
        if isinstance(ip_obj, ipaddress.IPv4Address) and self.ip_version == 6:
            start = self._ipv4_start_node or 0
            return self._walk_packed(ip_obj.packed, start_node=start)
        return self._walk_packed(ip_obj.packed, start_node=0)

    def _walk_packed(self, packed: bytes, *, start_node: int) -> int:
        node = start_node
        nc = self.node_count
        bit_count = len(packed) * 8

        mv = self._mv
        rs = self.record_size
        bpn = self.bytes_per_node
        buf = self._buf
        i = 0
        while i < bit_count and node < nc:
            off = node * bpn
            if rs == 24:
                l = (mv[off] << 16) | (mv[off + 1] << 8) | mv[off + 2]
                r = (mv[off + 3] << 16) | (mv[off + 4] << 8) | mv[off + 5]
            elif rs == 28:
                b0 = mv[off]; b1 = mv[off + 1]; b2 = mv[off + 2]; b3 = mv[off + 3]
                l = (b0 << 20) | (b1 << 12) | (b2 << 4) | (b3 >> 4)
                r = ((b3 & 0x0F) << 24) | (mv[off + 4] << 16) | (mv[off + 5] << 8) | mv[off + 6]
            else:
                l, r = struct.unpack_from(">II", buf, off)
            bit = (packed[i >> 3] >> (7 - (i & 7))) & 1
            node = r if bit else l
            i += 1
        return node

    def _descend_to_data(self, node: int) -> Optional[Any]:
        nc = self.node_count
        l = self._left
        if l is not None:
            while True:
                p = l[node]
                if p < nc:
                    node = p
                elif p == nc:
                    return None
                else:
                    return self._parse_value_at_data_pointer(p)
        else:
            off = self._descend_to_data_offset_fallback(node)
            return None if off == 0 else self._parse_value_at_data_offset(off)

    def _descend_to_data_offset_fallback(self, node: int) -> int | None | Any:
        mv = self._mv
        rs = self.record_size
        bpn = self.bytes_per_node
        buf = self._buf
        nc = self.node_count
        while True:
            off = node * bpn
            if rs == 24:
                left = (mv[off] << 16) | (mv[off + 1] << 8) | mv[off + 2]
            elif rs == 28:
                b0 = mv[off]; b1 = mv[off + 1]; b2 = mv[off + 2]; b3 = mv[off + 3]
                left = (b0 << 20) | (b1 << 12) | (b2 << 4) | (b3 >> 4)
            else:
                left = struct.unpack_from(">I", buf, off)[0]
            if left < nc:
                node = left
                continue
            elif left == nc:
                return 0
            else:
                return self.tree_size_bytes + (left - nc)

    def _build_node_arrays(self) -> None:
        n = self.node_count
        left = array("I", [0]) * n
        right = array("I", [0]) * n
        mv = self._mv
        rs = self.record_size
        buf = self._buf

        if rs == 24:
            off = 0
            for i in range(n):
                left[i]  = (mv[off] << 16) | (mv[off + 1] << 8) | mv[off + 2]
                right[i] = (mv[off + 3] << 16) | (mv[off + 4] << 8) | mv[off + 5]
                off += 6
        elif rs == 28:
            off = 0
            for i in range(n):
                b0 = mv[off]; b1 = mv[off + 1]; b2 = mv[off + 2]; b3 = mv[off + 3]
                left[i]  = (b0 << 20) | (b1 << 12) | (b2 << 4) | (b3 >> 4)
                right[i] = ((b3 & 0x0F) << 24) | (mv[off + 4] << 16) | (mv[off + 5] << 8) | mv[off + 6]
                off += 7
        else:
            off = 0
            for i in range(n):
                left[i], right[i] = struct.unpack_from(">II", buf, off)
                off += 8

        self._left, self._right = left, right

    def _compute_ipv4_start_node(self) -> int:
        node = 0
        nc = self.node_count
        for _ in range(96):
            if node >= nc:
                break
            node = self._read_node(node, 0)
        return node

    def _parse_value_at_data_pointer(self, node_pointer: int) -> Any:
        off = self.tree_size_bytes + (node_pointer - self.node_count)
        return self._parse_value_at_data_offset(off)

    def _parse_value_at_data_offset(self, absolute_offset: int) -> Any:
        cached = self._data_cache.get(absolute_offset)
        if cached is not None:
            return cached
        value, _ = self._parse_value(absolute_offset, pointer_base=self.data_section_start, context="data")
        self._data_cache[absolute_offset] = value
        return value

    def _parse_value(self, offset: int, *, pointer_base: int, context: str) -> Tuple[Any, int]:
        mv = self._mv

        ctrl = mv[offset]
        offset += 1
        type_code = ctrl >> 5
        size_flag = ctrl & 0x1F

        if type_code == 0:
            ext = mv[offset]; offset += 1
            type_code = 7 + ext

        if type_code == 1:
            ptr_value, offset = decode_pointer(size_flag, mv, offset)
            target = pointer_base + ptr_value
            val, _ = self._parse_value(target, pointer_base=pointer_base, context=context)
            return val, offset

        length, offset = decode_length(size_flag, mv, offset)

        if type_code == 2:
            data = self._buf[offset: offset + length]
            offset += length
            return data.decode("utf-8", errors="strict"), offset

        if type_code == 3:
            (val,) = struct.unpack_from(">d", self._buf, offset); offset += 8
            return val, offset

        if type_code == 4:
            data = bytes(mv[offset: offset + length]); offset += length
            return data, offset

        if type_code in (5, 6, 9, 10):
            if length == 0:
                return 0, offset
            v = 0; end = offset + length
            for i in range(offset, end):
                v = (v << 8) | mv[i]
            return v, end

        if type_code == 7:
            result: Dict[str, Any] = {}
            for _ in range(length):
                k, offset = self._parse_value(offset, pointer_base=pointer_base, context=context)
                if not isinstance(k, str):
                    raise CorruptDatabaseError("Map key must be a string")
                v, offset = self._parse_value(offset, pointer_base=pointer_base, context=context)
                result[k] = v
            return result, offset

        if type_code == 8:
            if length == 0:
                return 0, offset
            v = 0; end = offset + length
            for i in range(offset, end):
                v = (v << 8) | mv[i]
            if length >= 4 and (mv[offset] & 0x80):
                v -= 1 << (length * 8)
            return v, end

        if type_code == 11:
            arr: List[Any] = []
            for _ in range(length):
                x, offset = self._parse_value(offset, pointer_base=pointer_base, context=context)
                arr.append(x)
            return arr, offset

        if type_code == 12:
            end = offset + length
            vals: List[Any] = []
            cur = offset
            while cur < end:
                x, cur = self._parse_value(cur, pointer_base=pointer_base, context=context)
                vals.append(x)
            if cur != end:
                raise CorruptDatabaseError("Container length mismatch")
            return {"_container": vals}, cur

        if type_code == 13:
            return None, offset

        if type_code == 14:
            if length not in (0, 1):
                raise CorruptDatabaseError("Invalid boolean encoding")
            return bool(length), offset

        if type_code == 15:
            (val,) = struct.unpack_from(">f", self._buf, offset); offset += 4
            return val, offset

        raise UnsupportedRecordSizeError(f"Unsupported MMDB type code: {type_code}")

    def _read_node(self, node_number: int, index: int) -> int:
        base = node_number * self.bytes_per_node
        rs = self.record_size
        if rs == 24:
            off = base + index * 3
            return struct.unpack_from(">I", b"\x00" + self._buf[off:off+3])[0]
        if rs == 28:
            off = base + 3 * index
            nb = bytearray(self._buf[off:off+4])
            if index:
                nb[0] &= 0x0F
            else:
                mid = (nb.pop() & 0xF0) >> 4
                nb.insert(0, mid)
            return struct.unpack_from(">I", nb)[0]
        off = base + index * 4
        return struct.unpack_from(">I", self._buf, off)[0]

    def _rfind_in_buffer(self, needle: bytes, start: int) -> int:
        tail = self._buf[start:]
        try:
            r = tail.rfind(needle)
        except Exception:
            r = bytes(tail).rfind(needle)
        return -1 if r == -1 else start + r

    def _coerce_ip(self, ip: Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address]):
        if isinstance(ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return ip
        try:
            return ipaddress.IPv4Address(ip)
        except Exception:
            try:
                return ipaddress.IPv6Address(ip)
            except Exception as e:
                raise MMDBError("Invalid IP address") from e
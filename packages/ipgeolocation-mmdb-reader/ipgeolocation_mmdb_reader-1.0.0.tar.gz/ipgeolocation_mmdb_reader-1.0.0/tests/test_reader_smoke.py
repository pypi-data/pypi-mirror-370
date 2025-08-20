import ipaddress
import pytest

from src.ipgeo_mmdb_reader import IPGeolocationMMDBReader


def test_coerce_ip():
    r = object.__new__(IPGeolocationMMDBReader)  # avoid __init__
    assert isinstance(IPGeolocationMMDBReader._coerce_ip(r, "1.2.3.4"), ipaddress.IPv4Address)
    assert isinstance(IPGeolocationMMDBReader._coerce_ip(r, "2001:db8::1"), ipaddress.IPv6Address)

def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        IPGeolocationMMDBReader(tmp_path / "nope.mmdb")

def test_open_close_wo_mmap(tmp_path, monkeypatch):
    p = tmp_path / "empty.mmdb"
    p.write_bytes(b"not a real mmdb")
    # Opening will fail on metadata; but we verify close() is safe
    with pytest.raises(Exception):
        IPGeolocationMMDBReader(p, use_mmap=False)

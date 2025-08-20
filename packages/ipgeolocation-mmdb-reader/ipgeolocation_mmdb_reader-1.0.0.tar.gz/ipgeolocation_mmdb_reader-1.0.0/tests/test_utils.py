from src.ipgeo_mmdb_reader.utils import decode_length, decode_pointer

def test_decode_length_small():
    mv = bytes([0,0,0,0,0])
    assert decode_length(5, mv, 0) == (5, 0)

def test_decode_length_extended_29():
    mv = bytes([7])
    assert decode_length(29, mv, 0) == (36, 1)  # 29 + 7

def test_decode_length_extended_30():
    mv = bytes([0x01, 0x02])
    assert decode_length(30, mv, 0) == (285 + 0x0102, 2)

def test_decode_length_extended_31():
    mv = bytes([0x00, 0x01, 0x02])
    assert decode_length(31, mv, 0) == (65821 + 0x000102, 3)

def test_decode_pointer_modes():
    # sel=0
    mv = bytes([0xAA])
    assert decode_pointer(0b00000_101, mv, 0) == (((5 << 8) | 0xAA), 1)
    # sel=1
    mv = bytes([0x01, 0x02])
    assert decode_pointer(0b00100_011, mv, 0) == (((3 << 16) | (0x01 << 8) | 0x02) + 2048, 2)
    # sel=2
    mv = bytes([0x01, 0x02, 0x03])
    assert decode_pointer(0b01000_111, mv, 0) == (((7 << 24) | (0x01 << 16) | (0x02 << 8) | 0x03) + 526336, 3)
    # sel=3
    mv = bytes([0x01, 0x02, 0x03, 0x04])
    assert decode_pointer(0b01100_000, mv, 0) == ((0x01 << 24) | (0x02 << 16) | (0x03 << 8) | 0x04, 4)

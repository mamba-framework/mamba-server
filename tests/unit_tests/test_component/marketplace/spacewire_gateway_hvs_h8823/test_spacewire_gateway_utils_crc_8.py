from mamba.core.rmap_utils.crc_8 import crc_8


def test_crc_8():
    # Test patterns from ECSS-E-50-11
    assert crc_8(b'\x01\x02\x03\x04\x05\x06\x07\x08') == b'\xb0'
    assert crc_8(
        b'\x53\x70\x61\x63\x65\x57\x69\x72\x65\x20\x69\x73\x20\x62\x65\x61\x75\x74\x69\x66\x75\x6C\x21\x21'
    ) == b'\x84'
    assert crc_8(
        b'\x10\x56\xC3\x95\xA5\x75\x38\x63\x2F\x86\x7B\x01\x32\xDE\x35\x7A'
    ) == b'\x18'

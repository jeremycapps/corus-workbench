from codec import (
    decode_timpo,
    encode_spatial,
    encode_spatial_mas,
    encode_timpo,
    place_changed,
    reseed_timpo,
    same_place,
    spatial_lat_mas,
    spatial_lon_mas,
    spatial_u64,
    time_ns_u64,
)


LAT = 40.7127
LON = -74.0134
TIME_NS = 1_700_000_000_000_000_000
SPATIAL = 0x8BC6A58F01E5290
TIMPO = 0x8BC6A58F01E529017979CFE362A0000


def test_spatial_golden() -> None:
    assert encode_spatial(LAT, LON) == SPATIAL


def test_spatial_mas_roundtrip() -> None:
    spatial = encode_spatial_mas(146_565_720, -266_448_240)
    assert spatial_lat_mas(spatial) == 146_565_720
    assert spatial_lon_mas(spatial) == -266_448_240


def test_spatial_mas_signed_boundaries() -> None:
    spatial = encode_spatial_mas(2_147_483_647, -2_147_483_648)
    assert spatial_lat_mas(spatial) == 2_147_483_647
    assert spatial_lon_mas(spatial) == -2_147_483_648

    zero_spatial = encode_spatial_mas(0, 0)
    assert spatial_lat_mas(zero_spatial) == 0
    assert spatial_lon_mas(zero_spatial) == 0


def test_timpo_golden() -> None:
    assert encode_timpo(LAT, LON, TIME_NS) == TIMPO
    assert encode_timpo(LAT, LON, TIME_NS) == 11612132757493222933514833726911676416


def test_nyc_roundtrip() -> None:
    lat, lon, time_ns = decode_timpo(encode_timpo(LAT, LON, TIME_NS))
    assert abs(lat - LAT) < 1e-7
    assert abs(lon + 74.0134) < 1e-7
    assert time_ns == TIME_NS


def test_reseed() -> None:
    a = encode_timpo(LAT, LON, 1000)
    b = reseed_timpo(a, 2000)
    assert same_place(a, b)
    assert a != b
    assert time_ns_u64(b) == 2000


def test_same_place() -> None:
    a = encode_timpo(LAT, LON, 1000)
    b = encode_timpo(LAT, LON, 2000)
    assert same_place(a, b)


def test_distinct_place() -> None:
    a = encode_timpo(LAT, LON, 1000)
    b = encode_timpo(LAT + 0.0001, LON, 1000)
    assert place_changed(a, b)


def test_no_identity_in_timpo() -> None:
    decoded = decode_timpo(TIMPO)
    assert len(decoded) == 3


def test_layout_extractors() -> None:
    assert spatial_u64(TIMPO) == SPATIAL
    assert time_ns_u64(TIMPO) == TIME_NS

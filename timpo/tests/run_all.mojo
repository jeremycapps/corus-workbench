from model import Observation
from wire.codec import (
    decode_timpo,
    encode_spatial,
    encode_spatial_mas,
    encode_timpo,
    place_changed,
    same_place,
    spatial_lat_mas,
    spatial_lon_mas,
)
from wire.layout import LAT_BITS, LON_BITS, TIME_NS_BITS, spatial_u64, time_ns_u64
from wire.reseed import reseed_timpo
from support import expect


def assert_equal_uint64(actual: UInt64, expected: UInt64, name: String) raises:
    if actual != expected:
        print(name, "failed")
        print(actual)
        print(expected)
        raise Error(name)


def assert_equal_uint128(actual: UInt128, expected: UInt128, name: String) raises:
    if actual != expected:
        print(name, "failed")
        print(actual)
        print(expected)
        raise Error(name)


def assert_equal_int32(actual: Int32, expected: Int32, name: String) raises:
    if actual != expected:
        print(name, "failed")
        print(actual)
        print(expected)
        raise Error(name)


def assert_true(value: Bool, name: String) raises:
    expect(value, name)


def assert_close(actual: Float64, expected: Float64, tolerance: Float64, name: String) raises:
    var delta = actual - expected
    if delta < 0:
        delta = -delta
    if delta >= tolerance:
        print(name, "failed")
        print(actual)
        print(expected)
        raise Error(name)


def test_bit_budget() raises:
    assert_true(LAT_BITS + LON_BITS == 64, "lat_lon_bits")
    assert_true(TIME_NS_BITS == 64, "time_bits")
    assert_true(LAT_BITS + LON_BITS + TIME_NS_BITS == 128, "total_bits")


def test_spatial_golden() raises:
    var spatial = encode_spatial(40.7127, -74.0134)
    assert_equal_uint64(spatial, 0x8BC6A58F01E5290, "spatial_golden")


def test_spatial_mas_roundtrip() raises:
    var spatial = encode_spatial_mas(146565720, -266448240)
    assert_equal_int32(spatial_lat_mas(spatial), 146565720, "lat_mas_roundtrip")
    assert_equal_int32(spatial_lon_mas(spatial), -266448240, "lon_mas_roundtrip")


def test_spatial_mas_signed_boundaries() raises:
    var max_spatial = encode_spatial_mas(2147483647, -2147483648)
    assert_equal_int32(spatial_lat_mas(max_spatial), 2147483647, "lat_mas_max")
    assert_equal_int32(spatial_lon_mas(max_spatial), -2147483648, "lon_mas_min")

    var zero_spatial = encode_spatial_mas(0, 0)
    assert_equal_int32(spatial_lat_mas(zero_spatial), 0, "lat_mas_zero")
    assert_equal_int32(spatial_lon_mas(zero_spatial), 0, "lon_mas_zero")


def test_timpo_golden() raises:
    var obs = Observation(40.7127, -74.0134, 1700000000000000000)
    var value = encode_timpo(obs)
    assert_equal_uint128(value, 0x8BC6A58F01E529017979CFE362A0000, "timpo_hex")
    assert_equal_uint128(value, 11612132757493222933514833726911676416, "timpo_decimal")


def test_nyc_roundtrip() raises:
    var obs = Observation(40.7127, -74.0134, 1700000000000000000)
    var decoded = decode_timpo(encode_timpo(obs))
    assert_close(decoded.lat_deg, 40.7127, 0.0000001, "lat_roundtrip")
    assert_close(decoded.lon_deg, -74.0134, 0.0000001, "lon_roundtrip")
    assert_equal_uint64(decoded.time_ns, 1700000000000000000, "time_roundtrip")


def test_reseed() raises:
    var a = encode_timpo(Observation(40.7127, -74.0134, 1000))
    var b = reseed_timpo(a, 2000)
    assert_true(same_place(a, b), "reseed_same_place")
    assert_true(a != b, "reseed_changes_value")
    assert_equal_uint64(time_ns_u64(b), 2000, "reseed_time")


def test_same_place() raises:
    var a = encode_timpo(Observation(40.7127, -74.0134, 1000))
    var b = encode_timpo(Observation(40.7127, -74.0134, 2000))
    assert_true(same_place(a, b), "same_place")


def test_distinct_place() raises:
    var a = encode_timpo(Observation(40.7127, -74.0134, 1000))
    var b = encode_timpo(Observation(40.7128, -74.0134, 1000))
    assert_true(place_changed(a, b), "distinct_place")


def test_no_identity_in_timpo() raises:
    var decoded = decode_timpo(0x8BC6A58F01E529017979CFE362A0000)
    assert_close(decoded.lat_deg, 40.7127, 0.0000001, "identity_lat_only")
    assert_close(decoded.lon_deg, -74.0134, 0.0000001, "identity_lon_only")
    assert_equal_uint64(decoded.time_ns, 1700000000000000000, "identity_time_only")


def main() raises:
    test_bit_budget()
    test_spatial_golden()
    test_spatial_mas_roundtrip()
    test_spatial_mas_signed_boundaries()
    test_timpo_golden()
    test_nyc_roundtrip()
    test_reseed()
    test_same_place()
    test_distinct_place()
    test_no_identity_in_timpo()
    print("Timpo Mojo tests passed")

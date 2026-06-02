from model import Observation, DecodedObservation
from wire.layout import LON_MASK_SPATIAL, MAS_PER_DEG, pack_timpo, spatial_u64, time_ns_u64


def _round_to_int32(value: Float64) -> Int32:
    if value >= 0:
        return Int32(value + 0.5)
    return Int32(value - 0.5)


def _int32_to_uint32_bits(value: Int32) -> UInt32:
    if value < 0:
        return UInt32(Int64(value) + 4294967296)
    return UInt32(value)


def _uint32_bits_to_int32(value: UInt32) -> Int32:
    if value >= UInt32(0x80000000):
        return Int32(Int64(value) - 4294967296)
    return Int32(value)


def encode_spatial_mas(lat_mas: Int32, lon_mas: Int32) -> UInt64:
    var lat_u = _int32_to_uint32_bits(lat_mas)
    var lon_u = _int32_to_uint32_bits(lon_mas)
    return (UInt64(lat_u) << 32) | UInt64(lon_u)


def spatial_lat_mas(spatial: UInt64) -> Int32:
    var lat_u = UInt32((spatial >> 32) & LON_MASK_SPATIAL)
    return _uint32_bits_to_int32(lat_u)


def spatial_lon_mas(spatial: UInt64) -> Int32:
    var lon_u = UInt32(spatial & LON_MASK_SPATIAL)
    return _uint32_bits_to_int32(lon_u)


def encode_spatial(lat_deg: Float64, lon_deg: Float64) -> UInt64:
    var lat_mas = _round_to_int32(lat_deg * Float64(MAS_PER_DEG))
    var lon_mas = _round_to_int32(lon_deg * Float64(MAS_PER_DEG))
    return encode_spatial_mas(lat_mas, lon_mas)


def encode_timpo(obs: Observation) -> UInt128:
    return pack_timpo(encode_spatial(obs.lat_deg, obs.lon_deg), obs.time_ns)


def decode_timpo(timpo: UInt128) -> DecodedObservation:
    var spatial = spatial_u64(timpo)
    var lat_mas = spatial_lat_mas(spatial)
    var lon_mas = spatial_lon_mas(spatial)
    return DecodedObservation(
        Float64(lat_mas) / Float64(MAS_PER_DEG),
        Float64(lon_mas) / Float64(MAS_PER_DEG),
        time_ns_u64(timpo),
    )


def same_place(a: UInt128, b: UInt128) -> Bool:
    return spatial_u64(a) == spatial_u64(b)


def place_changed(a: UInt128, b: UInt128) -> Bool:
    return spatial_u64(a) != spatial_u64(b)

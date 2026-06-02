from __future__ import annotations

import struct

MAS_PER_DEG = 3_600_000
UINT32_MASK = (1 << 32) - 1
UINT64_MASK = (1 << 64) - 1


def int32_to_uint32_bits(v: int) -> int:
    return struct.unpack("I", struct.pack("i", v))[0]


def uint32_bits_to_int32(v: int) -> int:
    return struct.unpack("i", struct.pack("I", v & UINT32_MASK))[0]


def encode_spatial_mas(lat_mas: int, lon_mas: int) -> int:
    return (int32_to_uint32_bits(lat_mas) << 32) | int32_to_uint32_bits(lon_mas)


def spatial_lat_mas(spatial: int) -> int:
    return uint32_bits_to_int32((int(spatial) >> 32) & UINT32_MASK)


def spatial_lon_mas(spatial: int) -> int:
    return uint32_bits_to_int32(int(spatial) & UINT32_MASK)


def encode_spatial(lat_deg: float, lon_deg: float) -> int:
    lat_mas = int(round(lat_deg * MAS_PER_DEG))
    lon_mas = int(round(lon_deg * MAS_PER_DEG))
    return encode_spatial_mas(lat_mas, lon_mas)


def encode_timpo(lat_deg: float, lon_deg: float, time_ns: int) -> int:
    return (encode_spatial(lat_deg, lon_deg) << 64) | (int(time_ns) & UINT64_MASK)


def spatial_u64(timpo: int) -> int:
    return (int(timpo) >> 64) & UINT64_MASK


def time_ns_u64(timpo: int) -> int:
    return int(timpo) & UINT64_MASK


def decode_timpo(timpo: int) -> tuple[float, float, int]:
    spatial = spatial_u64(timpo)
    lat_mas = spatial_lat_mas(spatial)
    lon_mas = spatial_lon_mas(spatial)
    return (
        lat_mas / MAS_PER_DEG,
        lon_mas / MAS_PER_DEG,
        time_ns_u64(timpo),
    )


def same_place(a: int, b: int) -> bool:
    return spatial_u64(a) == spatial_u64(b)


def place_changed(a: int, b: int) -> bool:
    return spatial_u64(a) != spatial_u64(b)


def reseed_timpo(timpo: int, time_ns: int) -> int:
    return (spatial_u64(timpo) << 64) | (int(time_ns) & UINT64_MASK)

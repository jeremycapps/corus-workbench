comptime SPATIAL_SHIFT: Int = 64
comptime LON_BITS: Int = 32
comptime LAT_BITS: Int = 32
comptime LAT_SHIFT_SPATIAL: Int = 32
comptime TIME_NS_BITS: Int = 64
comptime MAS_PER_DEG: Int = 3_600_000

comptime LON_MASK_SPATIAL: UInt64 = (UInt64(1) << 32) - 1
comptime LAT_MASK_SPATIAL: UInt64 = ((UInt64(1) << 32) - 1) << 32
comptime TIME_NS_MASK: UInt128 = (UInt128(1) << 64) - 1


def spatial_u64(timpo: UInt128) -> UInt64:
    return UInt64(timpo >> UInt128(SPATIAL_SHIFT))


def time_ns_u64(timpo: UInt128) -> UInt64:
    return UInt64(timpo & TIME_NS_MASK)


def pack_timpo(spatial: UInt64, time_ns: UInt64) -> UInt128:
    return (UInt128(spatial) << UInt128(SPATIAL_SHIFT)) | UInt128(time_ns)

from wire.layout import pack_timpo, spatial_u64


def reseed_timpo(timpo: UInt128, time_ns: UInt64) -> UInt128:
    return pack_timpo(spatial_u64(timpo), time_ns)

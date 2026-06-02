from std.collections import List
from std.sys import argv
from std.time import perf_counter_ns

from wire.codec import encode_spatial_mas, spatial_lat_mas, spatial_lon_mas
from wire.layout import pack_timpo, spatial_u64, time_ns_u64


comptime DEFAULT_COUNT = 1_000_000
comptime LAT_MAS = 146_565_720
comptime LON_MAS = -266_448_240


def elapsed_seconds(start_ns: UInt, end_ns: UInt) -> Float64:
    return Float64(end_ns - start_ns) / 1_000_000_000.0


def per_second(count: Int, seconds: Float64) -> Float64:
    if seconds == 0:
        return 0.0
    return Float64(count) / seconds


def ns_per_timpo(count: Int, seconds: Float64) -> Float64:
    if count == 0:
        return 0.0
    return seconds * 1_000_000_000.0 / Float64(count)


def benchmark(count: Int) raises:
    var values = List[UInt128]()
    var spatial = encode_spatial_mas(LAT_MAS, LON_MAS)

    var write_start = perf_counter_ns()
    for i in range(count):
        values.append(pack_timpo(spatial, UInt64(i)))
    var write_end = perf_counter_ns()

    var checksum = UInt64(0)
    var read_start = perf_counter_ns()
    for i in range(count):
        var timpo = values[i]
        var timpo_spatial = spatial_u64(timpo)
        var lat_mas = spatial_lat_mas(timpo_spatial)
        var lon_mas = spatial_lon_mas(timpo_spatial)
        if lat_mas != LAT_MAS or lon_mas != LON_MAS:
            raise Error("decoded spatial MAS did not match encoded value")
        checksum = checksum + time_ns_u64(timpo)
    var read_end = perf_counter_ns()

    var write_seconds = elapsed_seconds(write_start, write_end)
    var read_seconds = elapsed_seconds(read_start, read_end)
    var total_seconds = elapsed_seconds(write_start, read_end)

    print("timpo_rw_count", count)
    print("write_seconds", write_seconds)
    print("write_timpos_per_second", per_second(count, write_seconds))
    print("write_ns_per_timpo", ns_per_timpo(count, write_seconds))
    print("read_seconds", read_seconds)
    print("read_timpos_per_second", per_second(count, read_seconds))
    print("read_ns_per_timpo", ns_per_timpo(count, read_seconds))
    print("total_seconds", total_seconds)
    print("total_timpos_per_second", per_second(count, total_seconds))
    print("total_ns_per_timpo", ns_per_timpo(count, total_seconds))
    print("checksum", checksum)


def main() raises:
    var count = DEFAULT_COUNT
    var args = argv()
    if len(args) > 1:
        count = Int(args[1])

    benchmark(count)

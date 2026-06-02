# Timpo

Timpo is the Corus observation primitive.

A Timpo is when + where encoded as a UInt128.

Timpo = UInt128(lat|lon mas, time_ns)

The Timpo itself is the value. There is no separate Timpo ID.

Timpo contains:
- latitude in signed int32 milli-arcseconds
- longitude in signed int32 milli-arcseconds
- unsigned nanoseconds since Unix epoch

Timpo does not contain:
- who
- what
- why
- altitude
- tenant
- domain
- profile
- value
- crypto
- version flags

Those belong in ledger payloads, protocols, or reconstructed Context.

Mojo is the canonical Timpo implementation.
Python parity exists for ingest and workbench integration.

.timpos is a collection of Timpo observations.
.ledger is append-only retained observation history.

Core equation:

Timpo + Domain = Context

There is exactly one wire layout:

```txt
UInt128 timpo = (spatial_u64 << 64) | time_ns_u64

spatial_u64 = (lat_u32 << 32) | lon_u32
lat/lon are signed int32 milli-arcseconds stored as UInt32 bit patterns.
time_ns_u64 is unsigned nanoseconds since Unix epoch.
```

## Mojo Benchmark

Run the Timpo read/write baseline from this directory:

```bash
mojo run -I src bench/timpo_rw.mojo
```

Pass a count to override the default 1,000,000 Timpos:

```bash
mojo run -I src bench/timpo_rw.mojo 10000000
```

The benchmark writes canonical MAS Timpos into a `List[UInt128]`, then reads
them back by extracting spatial MAS and time fields. It reports separate write,
read, and total Timpos per second, plus nanoseconds per Timpo.

# Public Timpo model/type-level definitions.

struct Observation:
    var lat_deg: Float64
    var lon_deg: Float64
    var time_ns: UInt64

    def __init__(out self, lat_deg: Float64, lon_deg: Float64, time_ns: UInt64):
        self.lat_deg = lat_deg
        self.lon_deg = lon_deg
        self.time_ns = time_ns


struct DecodedObservation:
    var lat_deg: Float64
    var lon_deg: Float64
    var time_ns: UInt64

    def __init__(out self, lat_deg: Float64, lon_deg: Float64, time_ns: UInt64):
        self.lat_deg = lat_deg
        self.lon_deg = lon_deg
        self.time_ns = time_ns

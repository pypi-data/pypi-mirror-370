from __future__ import annotations
from math import cos, radians
import json
import argparse

# Approx km per degree of latitude (near equator, varies slightly)
KM_PER_DEG_LAT = 111.32


def _wrap_lon(lon: float) -> float:
    """Wrap longitude to [-180, 180)."""
    return ((lon + 180.0) % 360.0) - 180.0


def bounding_box(lat: float, lon: float, radius_km: float) -> dict:
    """
    Return a bounding box around (lat, lon) with given radius in km.
    Result dict: {min_lat, max_lat, min_lon, max_lon}
    """
    if not (-90.0 <= lat <= 90.0):
        raise ValueError("lat must be in [-90, 90]")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError("lon must be in [-180, 180]")
    if radius_km < 0:
        raise ValueError("radius_km must be >= 0")

    # Latitude delta
    lat_delta = radius_km / KM_PER_DEG_LAT

    # Longitude delta depends on latitude
    c = abs(cos(radians(lat)))
    if c < 1e-12:  # near the poles, any small radius spans all longitudes
        lon_delta = 180.0
    else:
        lon_delta = radius_km / (KM_PER_DEG_LAT * c)

    min_lat = max(-90.0, lat - lat_delta)
    max_lat = min(90.0, lat + lat_delta)
    min_lon = _wrap_lon(lon - lon_delta)
    max_lon = _wrap_lon(lon + lon_delta)

    return {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon,
    }


def main():
    """CLI entrypoint."""
    p = argparse.ArgumentParser(description="Compute bounding box for (lat, lon, radius_km).")
    p.add_argument("lat", type=float)
    p.add_argument("lon", type=float)
    p.add_argument("radius_km", type=float)
    args = p.parse_args()
    box = bounding_box(args.lat, args.lon, args.radius_km)
    print(json.dumps(box, indent=2))

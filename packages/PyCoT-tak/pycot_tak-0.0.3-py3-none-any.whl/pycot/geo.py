from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Union

from .models import CoTEvent

logger = logging.getLogger(__name__)


def event_to_geojson(evt: Union[Dict[str, Any], CoTEvent]) -> Dict[str, Any]:
    """
    Convert CoT event to GeoJSON format.

    Args:
        evt: CoT event object or dictionary

    Returns:
        GeoJSON Feature object
    """
    try:
        # Convert to dict if it's a CoTEvent
        if isinstance(evt, CoTEvent):
            d = evt.to_dict()
        else:
            d = evt

        pt = d.get("point", {})
        lat = pt.get("lat", 0.0)
        lon = pt.get("lon", 0.0)

        # Validate coordinates
        if not (-90 <= lat <= 90):
            logger.warning(f"Invalid latitude: {lat}")
            lat = 0.0
        if not (-180 <= lon <= 180):
            logger.warning(f"Invalid longitude: {lon}")
            lon = 0.0

        # Build properties
        properties = {
            "type": d.get("type"),
            "uid": d.get("uid"),
            "time": d.get("time"),
            "start": d.get("start"),
            "stale": d.get("stale"),
            "how": d.get("how"),
            "hae": pt.get("hae"),
            "ce": pt.get("ce"),
            "le": pt.get("le"),
            "detail": d.get("detail", {}),
        }

        # Remove None values
        properties = {k: v for k, v in properties.items() if v is not None}

        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],  # GeoJSON uses [lon, lat] order
            },
            "properties": properties,
        }

        # Add optional fields
        if d.get("version"):
            geojson["properties"]["version"] = d["version"]
        if d.get("opex"):
            geojson["properties"]["opex"] = d["opex"]
        if d.get("access"):
            geojson["properties"]["access"] = d["access"]
        if d.get("q"):
            geojson["properties"]["q"] = d["q"]

        return geojson

    except Exception as e:
        logger.error(f"Error converting to GeoJSON: {e}")
        raise


def event_to_json(evt: Union[Dict[str, Any], CoTEvent], **kwargs) -> str:
    """
    Convert CoT event to JSON string.

    Args:
        evt: CoT event object or dictionary
        **kwargs: Additional arguments for json.dumps

    Returns:
        JSON string representation
    """
    try:
        if isinstance(evt, CoTEvent):
            d = evt.to_dict()
        else:
            d = evt

        # Use faster JSON serialization if available
        try:
            import orjson

            return orjson.dumps(
                d, option=orjson.OPT_NAIVE_UTC | orjson.OPT_OMIT_MICROSECONDS
            ).decode("utf-8")
        except ImportError:
            # Fall back to standard json
            return json.dumps(d, ensure_ascii=False, separators=(",", ":"), **kwargs)

    except Exception as e:
        logger.error(f"Error converting to JSON: {e}")
        raise


def events_to_geojson_collection(
    events: List[Union[Dict[str, Any], CoTEvent]]
) -> Dict[str, Any]:
    """
    Convert multiple CoT events to GeoJSON FeatureCollection.

    Args:
        events: List of CoT events

    Returns:
        GeoJSON FeatureCollection object
    """
    features = []
    for evt in events:
        try:
            feature = event_to_geojson(evt)
            features.append(feature)
        except Exception as e:
            logger.warning(f"Skipping event due to error: {e}")
            continue

    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "count": len(features),
            "source": "PyCoT",
            "format": "Cursor on Target (CoT)",
        },
    }


def event_to_kml(evt: Union[Dict[str, Any], CoTEvent]) -> str:
    """
    Convert CoT event to KML format.

    Args:
        evt: CoT event object or dictionary

    Returns:
        KML string representation
    """
    try:
        if isinstance(evt, CoTEvent):
            d = evt.to_dict()
        else:
            d = evt

        pt = d.get("point", {})
        lat = pt.get("lat", 0.0)
        lon = pt.get("lon", 0.0)
        hae = pt.get("hae", 0.0)

        # Build KML
        kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Placemark>
    <name>{d.get('uid', 'Unknown')}</name>
    <description>
      Type: {d.get('type', 'Unknown')}
      Time: {d.get('time', 'Unknown')}
      How: {d.get('how', 'Unknown')}
    </description>
    <Point>
      <coordinates>{lon},{lat},{hae}</coordinates>
    </Point>
  </Placemark>
</kml>"""

        return kml

    except Exception as e:
        logger.error(f"Error converting to KML: {e}")
        raise


def event_to_wkt(evt: Union[Dict[str, Any], CoTEvent]) -> str:
    """
    Convert CoT event to Well-Known Text (WKT) format.

    Args:
        evt: CoT event object or dictionary

    Returns:
        WKT string representation
    """
    try:
        if isinstance(evt, CoTEvent):
            d = evt.to_dict()
        else:
            d = evt

        pt = d.get("point", {})
        lat = pt.get("lat", 0.0)
        lon = pt.get("lon", 0.0)
        hae = pt.get("hae", 0.0)

        return f"POINT({lon} {lat} {hae})"

    except Exception as e:
        logger.error(f"Error converting to WKT: {e}")
        raise


def validate_geojson(geojson: Dict[str, Any]) -> bool:
    """
    Validate GeoJSON structure.

    Args:
        geojson: GeoJSON object to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        # Check required fields
        if not isinstance(geojson, dict):
            return False

        if geojson.get("type") != "Feature":
            return False

        if "geometry" not in geojson:
            return False

        geometry = geojson["geometry"]
        if geometry.get("type") != "Point":
            return False

        if "coordinates" not in geometry:
            return False

        coords = geometry["coordinates"]
        if not isinstance(coords, list) or len(coords) < 2:
            return False

        # Validate coordinate values
        lon, lat = coords[0], coords[1]
        if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
            return False

        return True

    except Exception:
        return False


def geojson_to_cot(geojson: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert GeoJSON back to CoT format.

    Args:
        geojson: GeoJSON Feature object

    Returns:
        CoT event dictionary
    """
    try:
        if not validate_geojson(geojson):
            raise ValueError("Invalid GeoJSON structure")

        geometry = geojson["geometry"]
        properties = geojson.get("properties", {})
        coords = geometry["coordinates"]

        # Extract coordinates
        lon, lat = coords[0], coords[1]
        hae = coords[2] if len(coords) > 2 else 0.0

        # Build CoT event
        cot_event = {
            "type": properties.get("type", "a-f-G-U-C"),
            "uid": properties.get("uid", "unknown"),
            "time": properties.get("time"),
            "start": properties.get("start"),
            "stale": properties.get("stale"),
            "how": properties.get("how"),
            "version": properties.get("version"),
            "opex": properties.get("opex"),
            "access": properties.get("access"),
            "q": properties.get("q"),
            "point": {
                "lat": lat,
                "lon": lon,
                "hae": hae,
                "ce": properties.get("ce", 9999999.0),
                "le": properties.get("le", 9999999.0),
            },
            "detail": properties.get("detail", {}),
        }

        # Remove None values
        return {k: v for k, v in cot_event.items() if v is not None}

    except Exception as e:
        logger.error(f"Error converting GeoJSON to CoT: {e}")
        raise

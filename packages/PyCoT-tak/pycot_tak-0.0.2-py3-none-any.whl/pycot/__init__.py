"""
PyCoT: Python Cursor-on-Target toolkit

A comprehensive library for working with Cursor on Target (CoT) data,
including XML parsing, conversion to various formats (GeoJSON, Cesium, KML, WKT),
and network transport capabilities.

Features:
- Fast XML parsing with lxml
- Validation with Pydantic models
- Multiple output formats (GeoJSON, Cesium, KML, WKT)
- Async network transport (UDP, TCP, TLS, WebSocket)
- Comprehensive error handling and logging
- CLI tools for data processing
"""

from .cesium import cesium_to_html, to_cesium, to_cesium_collection, to_cesium_scene
from .cot import CoT, CoTCollection
from .geo import (
    event_to_geojson,
    event_to_json,
    event_to_kml,
    event_to_wkt,
    events_to_geojson_collection,
    geojson_to_cot,
    validate_geojson,
)
from .models import (
    Contact,
    ContactLegacy,
    CoTEvent,
    # Legacy support
    CoTEventLegacy,
    Detail,
    DetailLegacy,
    Emergency,
    EmergencyLegacy,
    Group,
    GroupLegacy,
    Point,
    PointLegacy,
    PrecisionLocation,
    PrecisionLocationLegacy,
    Remarks,
    RemarksLegacy,
    Status,
    StatusLegacy,
    Takv,
    TakvLegacy,
    Track,
    TrackLegacy,
)
from .parser import (
    CoTParserError,
    CoTValidationError,
    parse_event,
    parse_event_dict,
    parse_file,
    parse_many,
    validate_cot_xml,
)
from .transport import TLSConfig, send_event, stream_events
from .writer import dict_to_xml, event_to_xml, format_xml, validate_xml_structure

# Version information
__version__ = "0.0.1"
__author__ = "PyCoT Contributors"
__description__ = "Python Cursor-on-Target toolkit with XML->CoTEvent, GeoJSON, Cesium, async transports"

# Main exports
__all__ = [
    # Core classes
    "CoT",
    "CoTCollection",
    # Models
    "CoTEvent",
    "Point",
    "Detail",
    "Contact",
    "Track",
    "PrecisionLocation",
    "Takv",
    "Group",
    "Status",
    "Emergency",
    "Remarks",
    # Legacy models
    "CoTEventLegacy",
    "PointLegacy",
    "DetailLegacy",
    "ContactLegacy",
    "TrackLegacy",
    "PrecisionLocationLegacy",
    "TakvLegacy",
    "GroupLegacy",
    "StatusLegacy",
    "EmergencyLegacy",
    "RemarksLegacy",
    # Parser functions
    "parse_event",
    "parse_event_dict",
    "parse_many",
    "parse_file",
    "validate_cot_xml",
    # Exceptions
    "CoTParserError",
    "CoTValidationError",
    # Geo conversion functions
    "event_to_geojson",
    "event_to_json",
    "events_to_geojson_collection",
    "event_to_kml",
    "event_to_wkt",
    "validate_geojson",
    "geojson_to_cot",
    # Cesium conversion functions
    "to_cesium",
    "to_cesium_collection",
    "to_cesium_scene",
    "cesium_to_html",
    # Transport functions
    "stream_events",
    "send_event",
    "TLSConfig",
    # Writer functions
    "event_to_xml",
    "dict_to_xml",
    "validate_xml_structure",
    "format_xml",
]

# Configure logging
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

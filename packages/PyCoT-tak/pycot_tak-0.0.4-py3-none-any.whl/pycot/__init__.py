"""
PyCoT: Python Cursor-on-Target toolkit

A comprehensive library for working with Cursor on Target (CoT) data,
including XML parsing and conversion to various formats (GeoJSON, Cesium, KML, WKT).

Features:
- Fast XML parsing with lxml
- Validation with Pydantic models
- Multiple output formats (GeoJSON, Cesium, KML, WKT)
- Comprehensive error handling and logging
- Data conversion and validation tools
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

# Transport functionality not yet implemented
# from .transport import TLSConfig, send_event, stream_events
from .writer import dict_to_xml, event_to_xml, format_xml, validate_xml_structure

# Version information
__version__ = "0.0.4"
__author__ = "COASsoft, Oscar Aguilar Ramos"
__description__ = "Python Cursor-on-Target toolkit with XML->CoTEvent, GeoJSON, Cesium conversion capabilities"

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
    # Writer functions
    "event_to_xml",
    "dict_to_xml",
    "validate_xml_structure",
    "format_xml",
]

# Configure logging
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

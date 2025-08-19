from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from .cesium import cesium_to_html, to_cesium, to_cesium_collection, to_cesium_scene
from .geo import (
    event_to_geojson,
    event_to_json,
    event_to_kml,
    event_to_wkt,
    events_to_geojson_collection,
)
from .models import CoTEvent
from .parser import CoTParserError, parse_event, parse_file, validate_cot_xml
from .writer import event_to_xml

logger = logging.getLogger(__name__)


class CoT:
    """
    Main CoT (Cursor on Target) processing class.

    This class provides a high-level interface for working with CoT events,
    including parsing, conversion to various formats, and validation.
    """

    def __init__(self, event: CoTEvent):
        """
        Initialize CoT with an event.

        Args:
            event: CoT event object
        """
        self.event = event
        self._validate_event()

    @classmethod
    def from_xml(cls, xml: Union[bytes, str]) -> "CoT":
        """
        Create CoT instance from XML string or bytes.

        Args:
            xml: XML string or bytes

        Returns:
            CoT instance

        Raises:
            CoTParserError: If XML parsing fails
        """
        try:
            event = parse_event(xml)
            return cls(event)
        except Exception as e:
            logger.error(f"Failed to parse XML: {e}")
            raise

    @classmethod
    def from_file(cls, file_path: str) -> "CoT":
        """
        Create CoT instance from XML file.

        Args:
            file_path: Path to XML file

        Returns:
            CoT instance

        Raises:
            CoTParserError: If file reading or parsing fails
        """
        try:
            events = parse_file(file_path)
            if not events:
                raise CoTParserError(f"No valid CoT events found in {file_path}")
            return cls(events[0])
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoT":
        """
        Create CoT instance from dictionary.

        Args:
            data: Dictionary representation of CoT event

        Returns:
            CoT instance
        """
        try:
            event = CoTEvent(**data)
            return cls(event)
        except Exception as e:
            logger.error(f"Failed to create CoT from dict: {e}")
            raise

    @classmethod
    def validate_xml(cls, xml: Union[bytes, str]) -> bool:
        """
        Validate XML without creating CoT instance.

        Args:
            xml: XML string or bytes

        Returns:
            True if valid, False otherwise
        """
        return validate_cot_xml(xml)

    def _validate_event(self) -> None:
        """Validate the internal event object."""
        if not isinstance(self.event, CoTEvent):
            raise ValueError("Event must be a CoTEvent instance")

        if not self.event.uid:
            raise ValueError("Event must have a UID")

        if not self.event.type:
            raise ValueError("Event must have a type")

    def to_event(self) -> CoTEvent:
        """
        Get the underlying CoT event object.

        Returns:
            CoTEvent object
        """
        return self.event

    def to_xml(self, pretty: bool = False) -> bytes:
        """
        Convert event to XML format.

        Args:
            pretty: Whether to format XML with indentation

        Returns:
            XML bytes
        """
        try:
            xml_bytes = event_to_xml(self.event)
            if pretty:
                # Pretty print XML
                from lxml import etree

                root = etree.fromstring(xml_bytes)
                return etree.tostring(root, pretty_print=True, encoding="utf-8")
            return xml_bytes
        except Exception as e:
            logger.error(f"Failed to convert to XML: {e}")
            raise

    def to_geojson(self) -> Dict[str, Any]:
        """
        Convert event to GeoJSON format.

        Returns:
            GeoJSON Feature object
        """
        try:
            return event_to_geojson(self.event)
        except Exception as e:
            logger.error(f"Failed to convert to GeoJSON: {e}")
            raise

    def to_json(self, **kwargs) -> str:
        """
        Convert event to JSON string.

        Args:
            **kwargs: Additional arguments for JSON serialization

        Returns:
            JSON string
        """
        try:
            return event_to_json(self.event, **kwargs)
        except Exception as e:
            logger.error(f"Failed to convert to JSON: {e}")
            raise

    def to_cesium(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert event to Cesium entity format.

        Args:
            options: Cesium conversion options

        Returns:
            Cesium entity dictionary
        """
        try:
            return to_cesium(self.event, options)
        except Exception as e:
            logger.error(f"Failed to convert to Cesium: {e}")
            raise

    def to_kml(self) -> str:
        """
        Convert event to KML format.

        Returns:
            KML string
        """
        try:
            return event_to_kml(self.event)
        except Exception as e:
            logger.error(f"Failed to convert to KML: {e}")
            raise

    def to_wkt(self) -> str:
        """
        Convert event to Well-Known Text (WKT) format.

        Returns:
            WKT string
        """
        try:
            return event_to_wkt(self.event)
        except Exception as e:
            logger.error(f"Failed to convert to WKT: {e}")
            raise

    def get_position(self) -> Dict[str, float]:
        """
        Get position information.

        Returns:
            Dictionary with lat, lon, hae
        """
        return self.event.get_position()

    def get_accuracy(self) -> Dict[str, float]:
        """
        Get accuracy information.

        Returns:
            Dictionary with ce, le
        """
        return self.event.get_accuracy()

    def is_stale(self, current_time: Optional[str] = None) -> bool:
        """
        Check if event is stale.

        Args:
            current_time: Current time string (optional)

        Returns:
            True if stale, False otherwise
        """
        return self.event.is_stale(current_time)

    def validate_times(self) -> bool:
        """
        Validate time fields.

        Returns:
            True if times are valid, False otherwise
        """
        return self.event.validate_times()

    def update_position(
        self, lat: float, lon: float, hae: Optional[float] = None
    ) -> None:
        """
        Update event position.

        Args:
            lat: New latitude
            lon: New longitude
            hae: New height above ellipsoid (optional)
        """
        try:
            self.event.point.lat = lat
            self.event.point.lon = lon
            if hae is not None:
                self.event.point.hae = hae
            logger.debug(f"Updated position for event {self.event.uid}")
        except Exception as e:
            logger.error(f"Failed to update position: {e}")
            raise

    def add_contact(self, callsign: str, **kwargs) -> None:
        """
        Add or update contact information.

        Args:
            callsign: Radio callsign
            **kwargs: Additional contact fields
        """
        try:
            from .models import Contact

            self.event.detail.contact = Contact(callsign=callsign, **kwargs)
            logger.debug(f"Added contact info for event {self.event.uid}")
        except Exception as e:
            logger.error(f"Failed to add contact: {e}")
            raise

    def add_track(
        self, course: Optional[float] = None, speed: Optional[float] = None
    ) -> None:
        """
        Add or update track information.

        Args:
            course: Course in degrees
            speed: Speed in m/s
        """
        try:
            from .models import Track

            self.event.detail.track = Track(course=course, speed=speed)
            logger.debug(f"Added track info for event {self.event.uid}")
        except Exception as e:
            logger.error(f"Failed to add track: {e}")
            raise

    def export_all_formats(
        self, output_dir: str = ".", prefix: str = ""
    ) -> Dict[str, str]:
        """
        Export event to all supported formats.

        Args:
            output_dir: Output directory
            prefix: File prefix

        Returns:
            Dictionary mapping format to file path
        """
        import json
        import os

        results = {}
        uid = self.event.uid or "unknown"

        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Export XML
            xml_path = os.path.join(output_dir, f"{prefix}{uid}.xml")
            with open(xml_path, "wb") as f:
                f.write(self.to_xml(pretty=True))
            results["xml"] = xml_path

            # Export JSON
            json_path = os.path.join(output_dir, f"{prefix}{uid}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(self.to_json(indent=2))
            results["json"] = json_path

            # Export GeoJSON
            geojson_path = os.path.join(output_dir, f"{prefix}{uid}.geojson")
            with open(geojson_path, "w", encoding="utf-8") as f:
                json.dump(self.to_geojson(), f, indent=2)
            results["geojson"] = geojson_path

            # Export KML
            kml_path = os.path.join(output_dir, f"{prefix}{uid}.kml")
            with open(kml_path, "w", encoding="utf-8") as f:
                f.write(self.to_kml())
            results["kml"] = kml_path

            # Export Cesium
            cesium_path = os.path.join(output_dir, f"{prefix}{uid}.cesium.json")
            with open(cesium_path, "w", encoding="utf-8") as f:
                json.dump(self.to_cesium(), f, indent=2)
            results["cesium"] = cesium_path

            logger.info(
                f"Exported event {uid} to {len(results)} formats in {output_dir}"
            )
            return results

        except Exception as e:
            logger.error(f"Failed to export formats: {e}")
            raise

    def __repr__(self) -> str:
        """String representation of CoT instance."""
        return f"CoT(event={self.event.uid}, type={self.event.type})"

    def __str__(self) -> str:
        """String representation of CoT instance."""
        return f"CoT Event: {self.event.uid} ({self.event.type}) at {self.event.point.lat:.6f}, {self.event.point.lon:.6f}"


class CoTCollection:
    """
    Collection of CoT events for batch processing.
    """

    def __init__(self, events: Optional[List[CoTEvent]] = None):
        """
        Initialize collection with events.

        Args:
            events: List of CoT events
        """
        self.events = events or []
        self._validate_events()

    def _validate_events(self) -> None:
        """Validate all events in collection."""
        for event in self.events:
            if not isinstance(event, CoTEvent):
                raise ValueError("All events must be CoTEvent instances")

    def add_event(self, event: CoTEvent) -> None:
        """Add event to collection."""
        if not isinstance(event, CoTEvent):
            raise ValueError("Event must be a CoTEvent instance")
        self.events.append(event)

    def to_geojson_collection(self) -> Dict[str, Any]:
        """Convert to GeoJSON FeatureCollection."""
        return events_to_geojson_collection(self.events)

    def to_cesium_collection(
        self, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert to Cesium entity collection."""
        return to_cesium_collection(self.events, options)

    def to_cesium_scene(
        self, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert to complete Cesium scene."""
        return to_cesium_scene(self.events, options)

    def export_html_viewer(
        self, output_path: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Export HTML viewer for the collection."""
        scene = self.to_cesium_scene(options)
        html = cesium_to_html(scene, options)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return output_path

    def __len__(self) -> int:
        """Number of events in collection."""
        return len(self.events)

    def __getitem__(self, index: int) -> CoTEvent:
        """Get event by index."""
        return self.events[index]

    def __iter__(self):
        """Iterate over events."""
        return iter(self.events)

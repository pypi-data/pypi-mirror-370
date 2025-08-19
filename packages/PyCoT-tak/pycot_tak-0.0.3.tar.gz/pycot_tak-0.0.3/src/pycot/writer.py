from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Union

from lxml import etree

from .models import (
    Contact,
    CoTEvent,
    Detail,
    Emergency,
    Group,
    PrecisionLocation,
    Remarks,
    Status,
    Takv,
    Track,
)

logger = logging.getLogger(__name__)


def event_to_xml(
    event: CoTEvent, pretty: bool = False, encoding: str = "utf-8"
) -> bytes:
    """
    Convert CoT event to XML format.

    Args:
        event: CoT event object
        pretty: Whether to format XML with indentation
        encoding: XML encoding

    Returns:
        XML bytes
    """
    try:
        # Create root element
        root = etree.Element("event")

        # Add attributes
        _add_attribute(root, "type", event.type)
        _add_attribute(root, "uid", event.uid)
        _add_attribute(root, "time", event.time)
        _add_attribute(root, "start", event.start)
        _add_attribute(root, "stale", event.stale)
        _add_attribute(root, "how", event.how)
        _add_attribute(root, "version", event.version)
        _add_attribute(root, "opex", event.opex)
        _add_attribute(root, "access", event.access)
        _add_attribute(root, "q", event.q)

        # Add point element
        point_elem = etree.SubElement(root, "point")
        point_elem.set("lat", str(event.point.lat))
        point_elem.set("lon", str(event.point.lon))
        point_elem.set("hae", str(event.point.hae))
        point_elem.set("ce", str(event.point.ce))
        point_elem.set("le", str(event.point.le))

        # Add detail element
        detail_elem = etree.SubElement(root, "detail")
        _write_detail(detail_elem, event.detail)

        # Convert to bytes
        if pretty:
            return etree.tostring(
                root, pretty_print=True, encoding=encoding, xml_declaration=True
            )
        else:
            return etree.tostring(root, encoding=encoding, xml_declaration=True)

    except Exception as e:
        logger.error(f"Failed to convert event to XML: {e}")
        raise


def _add_attribute(
    element: etree._Element, name: str, value: Optional[Union[str, int, float]]
) -> None:
    """Add attribute to element if value is not None."""
    if value is not None:
        element.set(name, str(value))


def _write_detail(detail_elem: etree._Element, detail: Detail) -> None:
    """Write detail element and its children."""
    try:
        # Contact information
        if detail.contact:
            _write_contact(detail_elem, detail.contact)

        # Track information
        if detail.track:
            _write_track(detail_elem, detail.track)

        # Precision location
        if detail.precisionlocation:
            _write_precision_location(detail_elem, detail.precisionlocation)

        # TAK version
        if detail.takv:
            _write_takv(detail_elem, detail.takv)

        # Group information
        if detail.group:
            _write_group(detail_elem, detail.group)

        # Status
        if detail.status:
            _write_status(detail_elem, detail.status)

        # Emergency
        if detail.emergency:
            _write_emergency(detail_elem, detail.emergency)

        # Remarks
        if detail.remarks and detail.remarks.text:
            _write_remarks(detail_elem, detail.remarks)

        # Complex elements
        _write_complex_element(detail_elem, "link", detail.link)
        _write_complex_element(detail_elem, "chat", detail.chat)
        _write_complex_element(detail_elem, "video", detail.video)
        _write_complex_element(detail_elem, "usericon", detail.usericon)
        _write_complex_element(detail_elem, "color", detail.color)

        # Extra fields
        for name, value in detail.extra.items():
            _write_extra_field(detail_elem, name, value)

    except Exception as e:
        logger.warning(f"Error writing detail element: {e}")


def _write_contact(detail_elem: etree._Element, contact: Contact) -> None:
    """Write contact element."""
    contact_elem = etree.SubElement(detail_elem, "contact")
    _add_attribute(contact_elem, "callsign", contact.callsign)
    _add_attribute(contact_elem, "endpoint", contact.endpoint)
    _add_attribute(contact_elem, "phone", contact.phone)
    _add_attribute(contact_elem, "email", contact.email)


def _write_track(detail_elem: etree._Element, track: Track) -> None:
    """Write track element."""
    track_elem = etree.SubElement(detail_elem, "track")
    _add_attribute(track_elem, "course", track.course)
    _add_attribute(track_elem, "speed", track.speed)


def _write_precision_location(
    detail_elem: etree._Element, precision: PrecisionLocation
) -> None:
    """Write precision location element."""
    precision_elem = etree.SubElement(detail_elem, "precisionlocation")
    _add_attribute(precision_elem, "altsrc", precision.altsrc)
    _add_attribute(precision_elem, "geopointsrc", precision.geopointsrc)
    _add_attribute(precision_elem, "spreadover", precision.spreadover)


def _write_takv(detail_elem: etree._Element, takv: Takv) -> None:
    """Write TAK version element."""
    takv_elem = etree.SubElement(detail_elem, "takv")
    _add_attribute(takv_elem, "device", takv.device)
    _add_attribute(takv_elem, "platform", takv.platform)
    _add_attribute(takv_elem, "os", takv.os)
    _add_attribute(takv_elem, "version", takv.version)
    _add_attribute(takv_elem, "appid", takv.appid)


def _write_group(detail_elem: etree._Element, group: Group) -> None:
    """Write group element."""
    group_elem = etree.SubElement(detail_elem, "group")
    _add_attribute(group_elem, "name", group.name)
    _add_attribute(group_elem, "role", group.role)


def _write_status(detail_elem: etree._Element, status: Status) -> None:
    """Write status element."""
    status_elem = etree.SubElement(detail_elem, "status")
    _add_attribute(status_elem, "battery", status.battery)
    _add_attribute(status_elem, "readiness", status.readiness)


def _write_emergency(detail_elem: etree._Element, emergency: Emergency) -> None:
    """Write emergency element."""
    emergency_elem = etree.SubElement(detail_elem, "emergency")
    _add_attribute(emergency_elem, "type", emergency.type)


def _write_remarks(detail_elem: etree._Element, remarks: Remarks) -> None:
    """Write remarks element."""
    remarks_elem = etree.SubElement(detail_elem, "remarks")
    if remarks.text:
        remarks_elem.text = remarks.text


def _write_complex_element(detail_elem: etree._Element, name: str, value: Any) -> None:
    """Write complex element (link, chat, video, usericon, color)."""
    if value is None:
        return

    if isinstance(value, dict):
        elem = etree.SubElement(detail_elem, name)
        for k, v in value.items():
            if v is not None:
                elem.set(k, str(v))
    elif isinstance(value, (str, int, float, bool)):
        elem = etree.SubElement(detail_elem, name)
        elem.text = str(value)


def _write_extra_field(detail_elem: etree._Element, name: str, value: Any) -> None:
    """Write extra field from detail.extra."""
    if value is None:
        return

    elem = etree.SubElement(detail_elem, name)

    if isinstance(value, dict):
        # Handle attributes
        if "@" in value:
            for k, v in value["@"].items():
                if v is not None:
                    elem.set(k, str(v))

        # Handle text content
        if "#text" in value:
            elem.text = str(value["#text"])

        # Handle child elements
        for k, v in value.items():
            if k not in ("@", "#text"):
                if isinstance(v, list):
                    for item in v:
                        child_elem = etree.SubElement(elem, k)
                        _write_value_to_element(child_elem, item)
                else:
                    child_elem = etree.SubElement(elem, k)
                    _write_value_to_element(child_elem, v)
    else:
        elem.text = str(value)


def _write_value_to_element(elem: etree._Element, value: Any) -> None:
    """Write value to element."""
    if isinstance(value, dict):
        for k, v in value.items():
            if k == "#text":
                elem.text = str(v)
            elif k == "@":
                for attr_k, attr_v in v.items():
                    if attr_v is not None:
                        elem.set(attr_k, str(attr_v))
            else:
                child_elem = etree.SubElement(elem, k)
                _write_value_to_element(child_elem, v)
    else:
        elem.text = str(value)


def dict_to_xml(
    data: Dict[str, Any],
    root_name: str = "event",
    pretty: bool = False,
    encoding: str = "utf-8",
) -> bytes:
    """
    Convert dictionary to XML format.

    Args:
        data: Dictionary data
        root_name: Name of root element
        pretty: Whether to format XML with indentation
        encoding: XML encoding

    Returns:
        XML bytes
    """
    try:
        root = etree.Element(root_name)
        _dict_to_xml_recursive(root, data)

        if pretty:
            return etree.tostring(
                root, pretty_print=True, encoding=encoding, xml_declaration=True
            )
        else:
            return etree.tostring(root, encoding=encoding, xml_declaration=True)

    except Exception as e:
        logger.error(f"Failed to convert dict to XML: {e}")
        raise


def _dict_to_xml_recursive(parent: etree._Element, data: Any) -> None:
    """Recursively convert dictionary to XML elements."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "@":
                # Handle attributes
                for attr_key, attr_value in value.items():
                    if attr_value is not None:
                        parent.set(attr_key, str(attr_value))
            elif key == "#text":
                # Handle text content
                if value is not None:
                    parent.text = str(value)
            else:
                # Handle child elements
                child = etree.SubElement(parent, key)
                _dict_to_xml_recursive(child, value)
    elif isinstance(data, list):
        # Handle lists
        for item in data:
            _dict_to_xml_recursive(parent, item)
    else:
        # Handle simple values
        if data is not None:
            parent.text = str(data)


def validate_xml_structure(xml_bytes: bytes) -> bool:
    """
    Validate XML structure without parsing content.

    Args:
        xml_bytes: XML bytes to validate

    Returns:
        True if valid XML structure, False otherwise
    """
    try:
        etree.fromstring(xml_bytes)
        return True
    except etree.XMLSyntaxError:
        return False
    except Exception:
        return False


def format_xml(xml_bytes: bytes, encoding: str = "utf-8") -> bytes:
    """
    Format XML with proper indentation.

    Args:
        xml_bytes: Raw XML bytes
        encoding: XML encoding

    Returns:
        Formatted XML bytes
    """
    try:
        root = etree.fromstring(xml_bytes)
        return etree.tostring(
            root, pretty_print=True, encoding=encoding, xml_declaration=True
        )
    except Exception as e:
        logger.error(f"Failed to format XML: {e}")
        raise

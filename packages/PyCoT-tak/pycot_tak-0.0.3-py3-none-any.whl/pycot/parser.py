from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

from lxml import etree

from .models import (
    Contact,
    CoTEvent,
    Detail,
    Emergency,
    Group,
    Point,
    PrecisionLocation,
    Remarks,
    Status,
    Takv,
    Track,
)

# Configure logging
logger = logging.getLogger(__name__)

XML = Union[str, bytes]


class CoTParserError(Exception):
    """Custom exception for CoT parsing errors."""

    pass


class CoTValidationError(CoTParserError):
    """Exception for CoT validation errors."""

    pass


def _strip(tag: str) -> str:
    """Remove namespace prefix from XML tag."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _coerce(value: Optional[str]) -> Union[str, int, float, bool, None]:
    """Coerce string value to appropriate Python type."""
    if value is None:
        return None

    v = value.strip()
    if v == "":
        return ""

    low = v.lower()
    if low in ("true", "false"):
        return low == "true"

    try:
        if "." in v or "e" in low:
            return float(v)
        return int(v)
    except (ValueError, TypeError):
        return v


def _safe_float(value: str, default: float = 0.0) -> float:
    """Safely convert string to float with default value."""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        logger.warning(f"Could not convert '{value}' to float, using default {default}")
        return default


def parse_event(xml_input: XML) -> CoTEvent:
    """
    Parse XML input and return a CoTEvent object.

    Args:
        xml_input: XML string or bytes

    Returns:
        CoTEvent object

    Raises:
        CoTParserError: If XML is invalid or required fields are missing
        CoTValidationError: If parsed data fails validation
    """
    try:
        # Use lxml for better performance
        parser = etree.XMLParser(recover=False, remove_blank_text=True)
        root = etree.fromstring(xml_input, parser)
    except etree.XMLSyntaxError as e:
        raise CoTParserError(f"Invalid XML: {e}") from e
    except Exception as e:
        raise CoTParserError(f"Unexpected error parsing XML: {e}") from e

    if _strip(root.tag) != "event":
        raise CoTParserError("Expected root <event> element")

    try:
        # Parse attributes
        a = root.attrib
        uid = a.get("uid")
        if not uid:
            raise CoTValidationError("Missing required 'uid' attribute")

        typ = a.get("type")
        if not typ:
            raise CoTValidationError("Missing required 'type' attribute")

        # Optional attributes
        time = a.get("time")
        start = a.get("start")
        stale = a.get("stale")
        how = a.get("how")
        version = a.get("version")
        opex = a.get("opex")
        access = a.get("access")
        q = a.get("q")

        # Parse point element
        p = _find_element(root, "point")
        if p is None:
            raise CoTValidationError("Missing required <point> element")

        lat = _safe_float(p.attrib.get("lat"))
        lon = _safe_float(p.attrib.get("lon"))

        if not (-90 <= lat <= 90):
            raise CoTValidationError(f"Invalid latitude: {lat}")
        if not (-180 <= lon <= 180):
            raise CoTValidationError(f"Invalid longitude: {lon}")

        hae = _safe_float(p.attrib.get("hae"), 0.0)
        ce = _safe_float(p.attrib.get("ce"), 9999999.0)
        le = _safe_float(p.attrib.get("le"), 9999999.0)

        point = Point(lat=lat, lon=lon, hae=hae, ce=ce, le=le)

        # Parse detail element
        dnode = _find_element(root, "detail")
        detail = _parse_detail(dnode) if dnode is not None else Detail()

        # Create and validate CoTEvent
        event = CoTEvent(
            type=typ,
            uid=uid,
            time=time,
            start=start,
            stale=stale,
            how=how,
            version=version,
            opex=opex,
            access=access,
            q=q,
            point=point,
            detail=detail,
        )

        logger.debug(f"Successfully parsed CoT event: {uid} ({typ})")
        return event

    except CoTValidationError:
        raise
    except Exception as e:
        raise CoTParserError(f"Error parsing CoT event: {e}") from e


def parse_event_dict(xml_input: XML) -> Dict[str, Any]:
    """Parse XML input and return dictionary representation."""
    return parse_event(xml_input).to_dict()


def _find_element(root: etree._Element, name: str) -> Optional[etree._Element]:
    """Find child element by name, ignoring namespace."""
    for child in root:
        if _strip(child.tag) == name:
            return child
    return None


def _parse_detail(node: etree._Element) -> Detail:
    """Parse detail element and its children."""
    detail = Detail()
    extras: Dict[str, Any] = {}

    for child in node:
        name = _strip(child.tag)

        try:
            if name == "contact":
                detail.contact = Contact(
                    callsign=child.attrib.get("callsign"),
                    endpoint=child.attrib.get("endpoint"),
                    phone=child.attrib.get("phone"),
                    email=child.attrib.get("email"),
                )
            elif name == "track":
                detail.track = Track(
                    course=_coerce(child.attrib.get("course")),
                    speed=_coerce(child.attrib.get("speed")),
                )
            elif name in ("precisionlocation", "precisionLocation"):
                detail.precisionlocation = PrecisionLocation(
                    altsrc=child.attrib.get("altsrc"),
                    geopointsrc=child.attrib.get("geopointsrc"),
                    spreadover=_coerce(child.attrib.get("spreadover")),
                )
            elif name == "takv":
                detail.takv = Takv(
                    device=child.attrib.get("device"),
                    platform=child.attrib.get("platform"),
                    os=child.attrib.get("os"),
                    version=child.attrib.get("version"),
                    appid=child.attrib.get("appid"),
                )
            elif name in ("__group", "group"):
                detail.group = Group(
                    name=child.attrib.get("name"),
                    role=child.attrib.get("role"),
                )
            elif name == "status":
                detail.status = Status(
                    battery=_coerce(child.attrib.get("battery")),
                    readiness=child.attrib.get("readiness"),
                )
            elif name == "emergency":
                detail.emergency = Emergency(type=child.attrib.get("type"))
            elif name == "remarks":
                txt = (child.text or "").strip() or None
                detail.remarks = Remarks(text=txt)
            elif name in ("link", "chat", "video", "usericon", "color"):
                # Handle complex elements
                setattr(detail, name, _element_to_dict(child))
            else:
                # Store unknown elements in extras
                extras[name] = _element_to_dict(child)

        except Exception as e:
            logger.warning(f"Error parsing detail element '{name}': {e}")
            extras[name] = _element_to_dict(child)

    detail.extra = extras
    return detail


def _element_to_dict(elem: etree._Element) -> Dict[str, Any]:
    """Convert XML element to dictionary representation."""
    out: Dict[str, Any] = {}

    # Handle attributes
    if elem.attrib:
        out["@"] = {k: _coerce(v) for k, v in elem.attrib.items()}

    # Handle text content
    text = (elem.text or "").strip()
    if text:
        out["#text"] = text

    # Handle child elements
    for child in elem:
        nm = _strip(child.tag)
        val = (
            _element_to_dict(child)
            if (child.attrib or len(child))
            else (_coerce(child.text) or "")
        )

        # Handle multiple elements with same name
        if nm in out:
            cur = out[nm]
            if not isinstance(cur, list):
                out[nm] = [cur]
            out[nm].append(val)
        else:
            out[nm] = val

    return out


def parse_many(xml_stream: Iterable[XML]) -> Iterator[Dict[str, Any]]:
    """
    Parse multiple XML documents from a stream.

    Args:
        xml_stream: Iterable of XML strings/bytes

    Yields:
        Dictionary representation of each parsed event
    """
    for i, xml_doc in enumerate(xml_stream):
        if not xml_doc:
            continue

        try:
            yield parse_event(xml_doc).to_dict()
        except Exception as e:
            logger.error(f"Error parsing document {i}: {e}")
            continue


def parse_file(file_path: str) -> List[CoTEvent]:
    """
    Parse CoT events from a file.

    Args:
        file_path: Path to XML file

    Returns:
        List of CoTEvent objects
    """
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        # Try to parse as single event first
        try:
            return [parse_event(content)]
        except CoTParserError:
            # If single event fails, try parsing as multiple events
            # This is a simplified approach - in production you might want more sophisticated XML parsing
            pass

        # For now, return empty list if not a single event
        # TODO: Implement proper multi-event XML parsing
        logger.warning(f"File {file_path} does not contain a valid single CoT event")
        return []

    except FileNotFoundError:
        raise CoTParserError(f"File not found: {file_path}")
    except Exception as e:
        raise CoTParserError(f"Error reading file {file_path}: {e}")


def validate_cot_xml(xml_input: XML) -> bool:
    """
    Validate that XML input conforms to CoT format.

    Args:
        xml_input: XML string or bytes

    Returns:
        True if valid, False otherwise
    """
    try:
        parse_event(xml_input)
        return True
    except (CoTParserError, CoTValidationError):
        return False

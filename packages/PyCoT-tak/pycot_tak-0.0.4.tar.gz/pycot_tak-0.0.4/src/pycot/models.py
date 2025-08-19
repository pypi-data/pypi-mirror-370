from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class Point(BaseModel):
    """Geographic point with coordinates and accuracy information."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    hae: float = Field(0.0, description="Height above ellipsoid in meters")
    ce: float = Field(9999999.0, description="Circular error in meters")
    le: float = Field(9999999.0, description="Linear error in meters")

    @validator("lat", "lon")
    def validate_coordinates(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError("Coordinates must be numeric")
        return float(v)


class Contact(BaseModel):
    """Contact information for a CoT event."""

    callsign: Optional[str] = Field(None, description="Radio callsign")
    endpoint: Optional[str] = Field(None, description="Network endpoint")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")


class Track(BaseModel):
    """Track information including course and speed."""

    course: Optional[float] = Field(None, ge=0, le=360, description="Course in degrees")
    speed: Optional[float] = Field(None, ge=0, description="Speed in meters per second")


class PrecisionLocation(BaseModel):
    """Precision location information."""

    altsrc: Optional[str] = Field(None, description="Altitude source")
    geopointsrc: Optional[str] = Field(None, description="Geopoint source")
    spreadover: Optional[float] = Field(None, ge=0, description="Spread over distance")


class Takv(BaseModel):
    """TAK version information."""

    device: Optional[str] = Field(None, description="Device identifier")
    platform: Optional[str] = Field(None, description="Platform name")
    os: Optional[str] = Field(None, description="Operating system")
    version: Optional[str] = Field(None, description="Version string")
    appid: Optional[str] = Field(None, description="Application ID")


class Group(BaseModel):
    """Group information."""

    name: Optional[str] = Field(None, description="Group name")
    role: Optional[str] = Field(None, description="Role in group")


class Status(BaseModel):
    """Status information."""

    battery: Optional[float] = Field(
        None, ge=0, le=100, description="Battery percentage"
    )
    readiness: Optional[str] = Field(None, description="Readiness status")


class Emergency(BaseModel):
    """Emergency information."""

    type: Optional[str] = Field(None, description="Emergency type")


class Remarks(BaseModel):
    """Remarks or notes."""

    text: Optional[str] = Field(None, description="Remark text")


class Detail(BaseModel):
    """Detailed information for a CoT event."""

    contact: Optional[Contact] = None
    track: Optional[Track] = None
    precisionlocation: Optional[PrecisionLocation] = None
    takv: Optional[Takv] = None
    group: Optional[Group] = None
    status: Optional[Status] = None
    emergency: Optional[Emergency] = None
    remarks: Optional[Remarks] = None
    link: Optional[Any] = None
    chat: Optional[Any] = None
    video: Optional[Any] = None
    usericon: Optional[Any] = None
    color: Optional[Any] = None
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional fields")

    class Config:
        extra = "allow"  # Allow additional fields


class CoTEvent(BaseModel):
    """Cursor on Target (CoT) event representation."""

    type: str = Field(..., description="Event type identifier")
    uid: str = Field(..., description="Unique identifier")
    time: Optional[str] = Field(None, description="Event time")
    start: Optional[str] = Field(None, description="Start time")
    stale: Optional[str] = Field(None, description="Stale time")
    how: Optional[str] = Field(None, description="How the event was created")
    version: Optional[str] = Field(None, description="Version string")
    opex: Optional[str] = Field(None, description="Operation exercise")
    access: Optional[str] = Field(None, description="Access level")
    q: Optional[str] = Field(None, description="Quality indicator")
    point: Point = Field(default_factory=lambda: Point(lat=0, lon=0))
    detail: Detail = Field(default_factory=Detail)

    class Config:
        validate_assignment = True
        extra = "forbid"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return self.model_dump(exclude_none=True)

    def to_json(self, **kwargs) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True, **kwargs)

    def validate_times(self) -> bool:
        """Validate time fields are in correct format."""
        # Basic validation - could be enhanced with proper datetime parsing
        time_fields = [self.time, self.start, self.stale]
        for field in time_fields:
            if field and not isinstance(field, str):
                return False
        return True

    def is_stale(self, current_time: Optional[str] = None) -> bool:
        """Check if event is stale based on current time."""
        if not self.stale:
            return False
        # This is a simplified check - in production you'd want proper datetime comparison
        return True  # Placeholder

    def get_accuracy(self) -> Dict[str, float]:
        """Get accuracy information from point."""
        return {"ce": self.point.ce, "le": self.point.le}

    def get_position(self) -> Dict[str, float]:
        """Get position information."""
        return {"lat": self.point.lat, "lon": self.point.lon, "hae": self.point.hae}


# Legacy dataclass support for backward compatibility
@dataclass(slots=True)
class PointLegacy:
    lat: float
    lon: float
    hae: float = 0.0
    ce: float = 9999999.0
    le: float = 9999999.0


@dataclass(slots=True)
class ContactLegacy:
    callsign: Optional[str] = None
    endpoint: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


@dataclass(slots=True)
class TrackLegacy:
    course: Optional[float] = None
    speed: Optional[float] = None


@dataclass(slots=True)
class PrecisionLocationLegacy:
    altsrc: Optional[str] = None
    geopointsrc: Optional[str] = None
    spreadover: Optional[float] = None


@dataclass(slots=True)
class TakvLegacy:
    device: Optional[str] = None
    platform: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
    appid: Optional[str] = None


@dataclass(slots=True)
class GroupLegacy:
    name: Optional[str] = None
    role: Optional[str] = None


@dataclass(slots=True)
class StatusLegacy:
    battery: Optional[float] = None
    readiness: Optional[str] = None


@dataclass(slots=True)
class EmergencyLegacy:
    type: Optional[str] = None


@dataclass(slots=True)
class RemarksLegacy:
    text: Optional[str] = None


@dataclass(slots=True)
class DetailLegacy:
    contact: Optional[ContactLegacy] = None
    track: Optional[TrackLegacy] = None
    precisionlocation: Optional[PrecisionLocationLegacy] = None
    takv: Optional[TakvLegacy] = None
    group: Optional[GroupLegacy] = None
    status: Optional[StatusLegacy] = None
    emergency: Optional[EmergencyLegacy] = None
    remarks: Optional[RemarksLegacy] = None
    link: Any = None
    chat: Any = None
    video: Any = None
    usericon: Any = None
    color: Any = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CoTEventLegacy:
    type: str
    uid: str
    time: Optional[str]
    start: Optional[str]
    stale: Optional[str]
    how: Optional[str]
    version: Optional[str] = None
    opex: Optional[str] = None
    access: Optional[str] = None
    q: Optional[str] = None
    point: PointLegacy = field(default_factory=lambda: PointLegacy(0, 0))
    detail: DetailLegacy = field(default_factory=DetailLegacy)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "uid": self.uid,
            "time": self.time,
            "start": self.start,
            "stale": self.stale,
            "how": self.how,
            "version": self.version,
            "opex": self.opex,
            "access": self.access,
            "q": self.q,
            "point": {
                "lat": self.point.lat,
                "lon": self.point.lon,
                "hae": self.point.hae,
                "ce": self.point.ce,
                "le": self.point.le,
            },
            "detail": detail_to_dict(self.detail),
        }


def detail_to_dict(d: DetailLegacy) -> Dict[str, Any]:
    """Convert legacy detail to dictionary."""
    out: Dict[str, Any] = {}
    if d.contact:
        out["contact"] = {k: v for k, v in vars(d.contact).items() if v is not None}
    if d.track:
        out["track"] = {k: v for k, v in vars(d.track).items() if v is not None}
    if d.precisionlocation:
        out["precisionlocation"] = {
            k: v for k, v in vars(d.precisionlocation).items() if v is not None
        }
    if d.takv:
        out["takv"] = {k: v for k, v in vars(d.takv).items() if v is not None}
    if d.group:
        out["__group"] = {k: v for k, v in vars(d.group).items() if v is not None}
    if d.status:
        out["status"] = {k: v for k, v in vars(d.status).items() if v is not None}
    if d.emergency:
        out["emergency"] = {k: v for k, v in vars(d.emergency).items() if v is not None}
    if d.remarks and d.remarks.text:
        out["remarks"] = d.remarks.text
    if d.link is not None:
        out["link"] = d.link
    if d.chat is not None:
        out["chat"] = d.chat
    if d.video is not None:
        out["video"] = d.video
    if d.usericon is not None:
        out["usericon"] = d.usericon
    if d.color is not None:
        out["color"] = d.color
    if d.extra:
        out.update(d.extra)
    return out

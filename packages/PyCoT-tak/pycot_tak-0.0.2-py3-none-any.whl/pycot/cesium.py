from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .models import CoTEvent

logger = logging.getLogger(__name__)

# Color schemes for different groups and types
_GROUP_COLORS = {
    "Blue": [0, 122, 255, 255],
    "Red": [255, 59, 48, 255],
    "Green": [52, 199, 89, 255],
    "Yellow": [255, 204, 0, 255],
    "Orange": [255, 149, 0, 255],
    "Purple": [175, 82, 222, 255],
    "Pink": [255, 45, 85, 255],
    "Brown": [162, 132, 94, 255],
    "Gray": [142, 142, 147, 255],
    "Black": [0, 0, 0, 255],
    "White": [255, 255, 255, 255],
}

# Type-based colors for different CoT event types
_TYPE_COLORS = {
    "a-f-G-U-C": [0, 122, 255, 255],  # Blue - Unit
    "a-f-G-E-V": [255, 59, 48, 255],  # Red - Enemy
    "a-f-G-F": [52, 199, 89, 255],  # Green - Friendly
    "a-f-G-A": [255, 204, 0, 255],  # Yellow - Aircraft
    "a-f-G-M": [175, 82, 222, 255],  # Purple - Maritime
    "a-f-G-T": [255, 149, 0, 255],  # Orange - Track
    "a-f-G-I": [142, 142, 147, 255],  # Gray - Infrastructure
}


def _get_color_for_entity(
    event: CoTEvent, group_name: Optional[str] = None
) -> List[int]:
    """Determine color for entity based on group and type."""
    # First try group-based color
    if group_name and group_name in _GROUP_COLORS:
        return _GROUP_COLORS[group_name]

    # Fall back to type-based color
    if event.type in _TYPE_COLORS:
        return _TYPE_COLORS[event.type]

    # Default color
    return [128, 128, 128, 255]


def _get_entity_name(event: CoTEvent) -> str:
    """Get display name for entity."""
    # Try to get callsign from contact details
    detail = event.detail
    if detail.contact and detail.contact.callsign:
        return detail.contact.callsign

    # Fall back to type or UID
    return event.type or event.uid


def to_cesium(
    event: CoTEvent, options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convert CoT event to Cesium entity format.

    Args:
        event: CoT event object
        options: Additional options for customization

    Returns:
        Cesium entity dictionary
    """
    try:
        if options is None:
            options = {}

        # Extract point information
        pt = event.point
        detail = event.detail

        # Get contact and group information
        callsign = None
        group_name = None

        if detail.contact:
            callsign = detail.contact.callsign

        if detail.group:
            group_name = detail.group.name

        # Determine color
        color = _get_color_for_entity(event, group_name)

        # Get altitude
        alt = float(pt.hae or 0.0)

        # Build basic entity
        entity: Dict[str, Any] = {
            "id": event.uid,
            "name": _get_entity_name(event),
            "position": {"cartographicDegrees": [pt.lon, pt.lat, alt]},
            "point": {
                "pixelSize": options.get("pointSize", 10),
                "color": {"rgba": color},
                "outlineColor": {"rgba": [255, 255, 255, 255]},
                "outlineWidth": options.get("outlineWidth", 2),
            },
            "properties": {
                "how": event.how,
                "detail": (
                    event.detail.model_dump(exclude_none=True)
                    if hasattr(event.detail, "model_dump")
                    else event.detail
                ),
                "ce": pt.ce,
                "le": pt.le,
                "type": event.type,
                "uid": event.uid,
            },
        }

        # Add availability if time information exists
        if event.time and event.stale:
            entity["availability"] = f"{event.time}/{event.stale}"

        # Add label
        label_text = callsign or event.uid
        entity["label"] = {
            "text": label_text,
            "scale": options.get("labelScale", 0.8),
            "horizontalOrigin": "LEFT",
            "verticalOrigin": "CENTER",
            "pixelOffset": [12, 0],
            "fillColor": {"rgba": [255, 255, 255, 255]},
            "outlineColor": {"rgba": [0, 0, 0, 255]},
            "outlineWidth": 1,
            "style": "FILL_AND_OUTLINE",
        }

        # Add billboard if usericon is specified
        if detail.usericon:
            entity["billboard"] = {
                "image": detail.usericon,
                "scale": options.get("billboardScale", 1.0),
                "horizontalOrigin": "CENTER",
                "verticalOrigin": "BOTTOM",
            }

        # Add model if specified in options
        if options.get("modelUrl"):
            entity["model"] = {
                "uri": options["modelUrl"],
                "scale": options.get("modelScale", 1.0),
                "minimumPixelSize": options.get("minimumPixelSize", 128),
            }

        # Add path if track information exists
        if detail.track and detail.track.course is not None:
            # Calculate end point based on course and speed
            import math

            course_rad = math.radians(detail.track.course)
            speed = detail.track.speed or 0.0
            distance = speed * 60  # 1 minute at current speed

            end_lat = pt.lat + (
                distance * math.cos(course_rad) / 111320.0
            )  # Approximate
            end_lon = pt.lon + (
                distance
                * math.sin(course_rad)
                / (111320.0 * math.cos(math.radians(pt.lat)))
            )

            entity["path"] = {
                "positions": {
                    "cartographicDegrees": [pt.lon, pt.lat, alt, end_lon, end_lat, alt]
                },
                "material": {"polyline": {"color": {"rgba": color}}},
                "width": options.get("pathWidth", 3),
            }

        # Add polygon if precision location has spread
        if detail.precisionlocation and detail.precisionlocation.spreadover:
            spread = detail.precisionlocation.spreadover
            # Create a simple circular uncertainty area
            import math

            positions = []
            for i in range(32):
                angle = (i / 32) * 2 * math.pi
                lat_offset = (spread / 111320.0) * math.cos(angle)
                lon_offset = (
                    spread / (111320.0 * math.cos(math.radians(pt.lat)))
                ) * math.sin(angle)
                positions.extend([pt.lon + lon_offset, pt.lat + lat_offset, alt])

            entity["polygon"] = {
                "positions": {"cartographicDegrees": positions},
                "material": {"color": {"rgba": [color[0], color[1], color[2], 50]}},
                "outline": True,
                "outlineColor": {"rgba": color},
            }

        logger.debug(f"Successfully converted CoT event {event.uid} to Cesium entity")
        return entity

    except Exception as e:
        logger.error(f"Error converting to Cesium entity: {e}")
        raise


def to_cesium_collection(
    events: List[CoTEvent], options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convert multiple CoT events to Cesium entity collection.

    Args:
        events: List of CoT events
        options: Additional options for customization

    Returns:
        Cesium entity collection
    """
    try:
        entities = []
        for event in events:
            try:
                entity = to_cesium(event, options)
                entities.append(entity)
            except Exception as e:
                logger.warning(f"Skipping event {event.uid} due to error: {e}")
                continue

        return {
            "entities": entities,
            "properties": {
                "count": len(entities),
                "source": "PyCoT",
                "format": "Cursor on Target (CoT)",
            },
        }

    except Exception as e:
        logger.error(f"Error creating Cesium collection: {e}")
        raise


def to_cesium_scene(
    events: List[CoTEvent], options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convert CoT events to a complete Cesium scene.

    Args:
        events: List of CoT events
        options: Additional options for customization

    Returns:
        Complete Cesium scene configuration
    """
    try:
        if options is None:
            options = {}

        # Get entity collection
        entity_collection = to_cesium_collection(events, options)

        # Build scene configuration
        scene = {
            "scene": {
                "globe": {
                    "enableLighting": options.get("enableLighting", False),
                    "showGroundAtmosphere": options.get("showGroundAtmosphere", True),
                    "showWaterEffect": options.get("showWaterEffect", True),
                },
                "camera": {
                    "defaultPosition": {
                        "cartographicDegrees": options.get(
                            "defaultCameraPosition", [-74.0, 40.0, 1000000.0]
                        )
                    }
                },
                "skyBox": {
                    "sources": {
                        "positiveX": "https://cesium.com/public/assets/Textures/SkyBox2/px.jpg",
                        "negativeX": "https://cesium.com/public/assets/Textures/SkyBox2/nx.jpg",
                        "positiveY": "https://cesium.com/public/assets/Textures/SkyBox2/py.jpg",
                        "negativeY": "https://cesium.com/public/assets/Textures/SkyBox2/ny.jpg",
                        "positiveZ": "https://cesium.com/public/assets/Textures/SkyBox2/pz.jpg",
                        "negativeZ": "https://cesium.com/public/assets/Textures/SkyBox2/nz.jpg",
                    }
                },
            },
            "entities": entity_collection["entities"],
            "properties": entity_collection["properties"],
        }

        return scene

    except Exception as e:
        logger.error(f"Error creating Cesium scene: {e}")
        raise


def cesium_to_html(
    cesium_scene: Dict[str, Any], options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate HTML page with Cesium viewer for the scene.

    Args:
        cesium_scene: Cesium scene configuration
        options: Additional HTML options

    Returns:
        Complete HTML page as string
    """
    try:
        if options is None:
            options = {}

        cesium_url = options.get("cesiumUrl", "https://cesium.com/cesiumjs/")
        title = options.get("title", "PyCoT Cesium Viewer")

        # Convert scene to JSON
        import json

        scene_json = json.dumps(cesium_scene, indent=2)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="{cesium_url}Build/Cesium/Cesium.js"></script>
    <link href="{cesium_url}Build/Cesium/Widgets/widgets.css" rel="stylesheet">
    <style>
        html, body, #cesiumContainer {{
            width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden;
        }}
    </style>
</head>
<body>
    <div id="cesiumContainer"></div>
    <script>
        // Initialize Cesium
        Cesium.Ion.defaultAccessToken = '{options.get("accessToken", "")}';
        
        const viewer = new Cesium.Viewer('cesiumContainer', {{
            terrainProvider: Cesium.createWorldTerrain(),
            infoBox: true,
            selectionIndicator: true,
            shadows: true,
            shouldAnimate: true
        }});
        
        // Load scene data
        const sceneData = {scene_json};
        
        // Add entities
        sceneData.entities.forEach(entity => {{
            viewer.entities.add(entity);
        }});
        
        // Set camera position if specified
        if (sceneData.scene && sceneData.scene.camera) {{
            const pos = sceneData.scene.camera.defaultPosition.cartographicDegrees;
            viewer.camera.setView({{
                destination: Cesium.Cartesian3.fromDegrees(pos[0], pos[1], pos[2])
            }});
        }}
        
        // Enable lighting if specified
        if (sceneData.scene && sceneData.scene.globe) {{
            viewer.scene.globe.enableLighting = sceneData.scene.globe.enableLighting || false;
        }}
    </script>
</body>
</html>"""

        return html

    except Exception as e:
        logger.error(f"Error generating HTML: {e}")
        raise

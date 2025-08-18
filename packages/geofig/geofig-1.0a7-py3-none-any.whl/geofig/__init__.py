"""Library to procedurally generate geometric figures as SVG images."""

from .figure import Figure
from .geometry import Arc, Scalar, closest_entity, closest_point, ellipse_angle


__all__ = [
    "Arc",
    "Figure",
    "Scalar",
    "closest_entity",
    "closest_point",
    "ellipse_angle",
]

"""..."""

import svgwrite as sw

from .geometry import Arc, Scalar, Transformer
from collections.abc import Callable
from math import ceil
from pathlib import Path
from sympy import Abs, pi
from sympy.geometry.ellipse import Circle, Ellipse
from sympy.geometry.entity import GeometryEntity
from sympy.geometry.line import Line, LinearEntity
from sympy.geometry.point import Point
from sympy.geometry.polygon import Polygon
from typing import Any, Iterable, NamedTuple
from xml.dom import minidom
from xml.etree import ElementTree


def _n(x: Any) -> int | float:
    f = round(float(x), 4)
    i = int(f)
    return i if i == f else f


class _Bounds(NamedTuple):
    """..."""

    xmin: Scalar
    ymin: Scalar
    xmax: Scalar
    ymax: Scalar

    def union(self, other: "Bounds") -> "Bounds":
        """..."""
        return _Bounds(
            min(self.xmin, other.xmin),
            min(self.ymin, other.ymin),
            max(self.xmax, other.xmax),
            max(self.ymax, other.ymax),
        )


class _Padding(NamedTuple):
    """..."""

    top: float
    right: float
    bottom: float
    left: float


class _CSS:
    """..."""

    def __init__(self):
        self._rules: dict[str, str] = {}
        self._selected: set[str] = set(("*", "svg"))

    def __str__(self) -> str:
        result = []
        result.append("")
        for style in self._rules:
            if style in self._selected:
                result.append(f"{style} {{")
                for line in self._rules[style].split("\n"):
                    line = line.strip()
                    if line:
                        result.append(f"\t{line}")
                result.append("}")
        result.append("")
        return f"{'\n'.join(result)}"

    def __setitem__(self, key: str, value: str) -> None:
        if key in self._rules:
            raise ValueError(f"{key} rule already defined")
        self._rules[key] = value

    def select(self, key: str) -> None:
        self._selected.add(key)

    def update(self, rules: dict[str, str]) -> None:
        for key, value in rules.items():
            self[key] = value


class Figure:
    """
    A geometric figure, expressed on a Cartesian plane, rendered as an SVG drawing.
    """

    scale: int | float

    def __init__(self):
        self._background: dict[str, Any] | None = None
        self._bounds: _Bounds | None = None
        self._desc = None
        self._ops: list[Callable[[Transformer], sw.base.BaseElement]] = []
        self._selectors: set[str] = set()
        self._css = _CSS()
        self._title = None
        self.scale(1)
        self.padding(4)

    def _include(self, entity: GeometryEntity) -> None:
        """Update the internal bounding box to include the given entity."""
        bounds = _Bounds(*entity.bounds)
        self._bounds = self._bounds.union(bounds) if self._bounds else bounds

    def _select(self, type: str, **kwargs: dict[str, Any]):
        """Register an element selector for styling."""
        self._css.select(type)
        if "id" in kwargs:
            self._css.select(f"#{kwargs['id']}")
        if "class_" in kwargs:
            self._css.select(f".{kwargs['class_']}")

    def arc(self, arc: Arc, **kwargs: Any):
        """Add an arc to the figure."""

        def op(transformer: Transformer) -> sw.base.BaseElement:
            path = sw.path.Path(**kwargs)
            a = transformer.apply(arc)
            points = a.points
            path.push("M", _n(points[0].x), _n(points[0].y))
            path.push_arc(
                r=(_n(a.ellipse.hradius), _n(a.ellipse.vradius)),
                rotation=0,
                large_arc=bool(a.length > pi or a.length < -pi),
                angle_dir="+" if a.length > 0 else "-",
                target=(_n(points[1].x), _n(points[1].y)),
                absolute=True,
            )
            self._select("path", **kwargs)
            return path

        self._ops.append(op)
        self._include(arc)

    def circle(self, circle: Circle, **kwargs: Any) -> None:
        """Add a circle to the figure."""

        def op(transformer: Transformer) -> sw.base.BaseElement:
            c = transformer.apply(circle)
            if isinstance(c, Circle):
                self._select("circle", **kwargs)
            elif isinstance(c, Ellipse):  # transformed to ellipse
                self._select("ellipse", **kwargs)
            else:
                raise TypeError(f"unsupported type: {type(c)}")
            return sw.shapes.Circle(
                center=(_n(c.center.x), _n(c.center.y)),
                r=_n(c.radius),
                **kwargs,
            )

        self._ops.append(op)
        self._include(circle)

    def curve(self, *vertices: Point, **kwargs: Any):
        """Add a smooth Bézier curve to figure."""

        def op(transformer: Transformer) -> sw.base.BaseElement:
            path = sw.path.Path(**kwargs)
            vtxs = [transformer.apply(v) for v in vertices]
            path.push("M", _n(vtxs[0].x), _n(vtxs[0].y))
            for i in range(1, len(vtxs) - 1):
                p0 = vtxs[i - 1]
                p1 = vtxs[i]
                p2 = vtxs[i + 1]
                p3 = vtxs[i + 2] if i + 2 < len(vtxs) else vtxs[i + 1]
                cp1 = Point(p1.x + (p2.x - p0.x) / 6, p1.y + (p2.y - p0.y) / 6)
                cp2 = Point(p2.x - (p3.x - p1.x) / 6, p2.y - (p3.y - p1.y) / 6)
                path.push("C", _n(cp1.x), _n(cp1.y), _n(cp2.x), _n(cp2.y), _n(p2.x), _n(p2.y))
            self._select("path", **kwargs)
            return path

        self._ops.append(op)
        for vertex in vertices:
            self._include(vertex)

    def ellipse(self, ellipse: Ellipse, **kwargs: dict[str, Any]) -> None:
        """Add an ellipse to the figure."""

        def op(transformer: Transformer) -> sw.base.BaseElement:
            e = transformer.apply(ellipse)
            if isinstance(e, Ellipse):
                self._select("ellipse", **kwargs)
            elif isinstance(e, Circle):  # transformed to circle
                self._select("circle", **kwargs)
            else:
                raise TypeError(f"unsupported type: {type(e)}")
            return sw.shapes.Ellipse(
                center=(_n(e.center.x), _n(e.center.y)),
                r=(_n(e.hradius), _n(e.vradius)),
                **kwargs,
            )

        self._ops.append(op)
        self._include(ellipse)

    def line(self, entity: LinearEntity, **kwargs: dict[str, Any]) -> None:
        """Add a line to figure."""

        def op(transformer: Transformer) -> sw.base.BaseElement:
            e = transformer.apply(entity)
            self._select("line", **kwargs)
            return sw.shapes.Line(
                start=(_n(e.p1.x), _n(e.p1.y)),
                end=(_n(e.p2.x), _n(e.p2.y)),
                **kwargs,
            )

        self._ops.append(op)
        self._include(entity)

    def path(self, *entities: Iterable[GeometryEntity], **kwargs) -> None:
        """Add a connected path to the figure."""

        def op(transformer: Transformer) -> sw.base.BaseElement:
            path = sw.path.Path(**kwargs)
            es = [transformer.apply(e) for e in entities]
            last = None
            count = len(es)
            for n in range(count):
                entity = es[n]
                p1, p2 = entity.points
                if last == p2:
                    p1, p2 = p2, p1
                if last != p1:
                    if n < count - 1:
                        next = es[n + 1]
                        if p1 in next.points:
                            p1, p2 = p2, p1
                if last != p1:
                    path.push("M", _n(p1.x), _n(p1.y))
                if isinstance(entity, LinearEntity):
                    path.push("L", _n(p2.x), _n(p2.y))
                elif isinstance(entity, Arc):
                    arc = entity
                    path.push_arc(
                        r=(_n(arc.ellipse.hradius), _n(arc.ellipse.vradius)),
                        rotation=0,
                        large_arc=bool(arc.length > pi or arc.length < -pi),
                        angle_dir=("+" if (arc.length > 0) ^ (p1 != arc.points[0]) else "-"),
                        target=(_n(p2.x), _n(p2.y)),
                        absolute=True,
                    )
                else:
                    raise ValueError(f"unsupported entity: {type(entity)}")
                last = p2
            self._select("path", **kwargs)
            return path

        self._ops.append(op)
        for entity in entities:
            self._include(entity)

    def polygon(self, polygon: Polygon, **kwargs: Any) -> None:
        """Add a polygon to the figure."""

        def op(transformer: Transformer) -> sw.base.BaseElement:
            p = transformer.apply(polygon)
            self._select("polygon", **kwargs)
            return sw.shapes.Polygon(
                points=[(_n(v.x), _n(v.y)) for v in p.vertices],
                **kwargs,
            )

        self._ops.append(op)
        self._include(polygon)

    def polyline(self, *vertices: Point, **kwargs: Any) -> None:
        """Add a polyline to the figure."""

        def op(transformer: Transformer) -> sw.base.BaseElement:
            vtxs = [transformer.apply(v) for v in vertices]
            self._select("polyline", **kwargs)
            return sw.shapes.Polyline(
                points=[(_n(v.x), _n(v.y)) for v in vtxs],
                **kwargs,
            )

        self._ops.append(op)
        for vertex in vertices:
            self._include(vertex)

    def text(
        self,
        text: str,
        point: Point,
        shift: tuple[Scalar, Scalar] = (0, 0),
        **kwargs: Any,
    ) -> None:
        """
        Add text to the figure.

        Parameters:
        • text: text to be added
        • point: point of text, in Cartesian space
        • shift: offset of text, in SVG pixels
        """

        def op(transformer: Transformer) -> sw.base.BaseElement:
            p = transformer.apply(point)
            self._select("text", **kwargs)
            return sw.text.Text(
                text=text,
                insert=(_n(p.x + shift[0]), _n(p.y + shift[1])),
                **kwargs,
            )

        self._ops.append(op)
        self._include(point)

    def background(self, **kwargs: Any) -> None:
        """
        Add a background rectangle with the dimensions of the figure.

        The background `rect` SVG element can be identified with an `id` or `class_`
        keyword argument, and styled accordingly.
        """
        self._background = kwargs

    def desc(self, value: str) -> None:
        """Set the figure description."""
        self._desc = value

    def padding(self, *args: int | float) -> None:
        """
        Set padding around the figure, in SVG pixels.

        Parameters:
        • 1 value: all sides
        • 2 values: vertical, horizontal
        • 4 values: top, right, bottom, left
        """
        args = [float(arg) for arg in args]
        match len(args):
            case 1:
                self._padding = _Padding(args[0], args[0], args[0], args[0])
            case 2:
                self._padding = _Padding(args[0], args[1], args[0], args[1])
            case 4:
                self._padding = _Padding(args[0], args[1], args[2], args[3])
            case _:
                raise ValueError("padding requires 1, 2 or 4 arguments")

    def scale(self, value: int | float) -> None:
        """Set scaling factor to be applied to output drawing."""
        self._scale = value

    def styles(self, rules: dict[str, str]) -> None:
        """Set CSS style rules."""
        self._css.update(rules)

    def title(self, value: str) -> None:
        """Set the figure title."""
        self._title = value

    def save(self, path: str | Path) -> None:
        """Save the figure as an SVG file."""
        if not self._ops:
            raise RuntimeError("nothing to save")
        transformer = Transformer()
        transformer.scale(self._scale, -self._scale)
        transformer.translate(
            -self._bounds.xmin * self._scale + self._padding.left,
            self._bounds.ymax * self._scale + self._padding.top,
        )
        drawing = sw.Drawing(size=None)
        width = ceil(
            _n(
                (self._bounds.xmax - self._bounds.xmin) * self._scale
                + self._padding.right
                + self._padding.left
            )
        )
        height = ceil(
            _n(
                (self._bounds.ymax - self._bounds.ymin) * self._scale
                + self._padding.top
                + self._padding.bottom
            )
        )
        drawing.viewbox(
            0,
            0,
            width,
            height,
        )
        drawing.set_desc(title=self._title, desc=self._desc)
        if self._background is not None:
            self._select("rect", **self._background)
            drawing.add(sw.shapes.Rect(insert=(0, 0), size=(width, height), **self._background))
        for op in self._ops:
            drawing.add(op(transformer))
        drawing.defs.add(drawing.style(str(self._css)))
        svg = drawing.get_xml()
        del svg.attrib["baseProfile"]
        with open(path, "w", encoding="utf-8") as file:
            file.write(
                minidom.parseString(ElementTree.tostring(svg, encoding="utf-8")).toprettyxml()
            )

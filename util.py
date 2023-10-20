import re
from dataclasses import dataclass
from typing import Dict

import shapely
from pykml import parser
from shapely.geometry.base import BaseGeometry


@dataclass
class Shape:
    shape_id: str
    name: str
    shape: BaseGeometry


def load_kml(kml_file: str) -> Dict[str, Shape]:
    with open(kml_file) as f:
        kml_shapes: Dict[str, Shape] = dict()
        parse(_root=parser.parse(f).getroot(), _kml_shapes=kml_shapes)
        return kml_shapes


def parse(_root, _kml_shapes: Dict[str, Shape]):
    # Recursively traverse kml document. Extract geospatial entities and their corresponding shapely shapes
    for elt in _root.getchildren():
        tag = re.sub(r"^.*\}", "", elt.tag)
        if tag in {"Document", "Folder"}:
            parse(elt, _kml_shapes)
        elif tag == "Placemark":
            if hasattr(elt, "Point") or hasattr(elt, "LineString") or hasattr(elt, "Polygon"):
                shape_id = "".join(elt["name"].text.lower().split())
                name = elt["name"].text
                if hasattr(elt, "Point"):
                    if shape_id in _kml_shapes:
                        if type(_kml_shapes[shape_id].shape) != shapely.Point:
                            print(f"Existing entity {shape_id} of type {type(_kml_shapes[shape_id].shape)}! Skip.")
                            continue
                    _kml_shapes[shape_id] = Shape(shape_id=shape_id,
                                                  name=name,
                                                  shape=shapely.Point([float(x) for x in
                                                                       elt.Point.coordinates.text.split(",")[
                                                                       :-1]]))
                elif hasattr(elt, "LineString"):
                    _kml_shapes[shape_id] = Shape(shape_id=shape_id,
                                                  name=name,
                                                  shape=shapely.LineString(
                                                      coordinates=[tuple(float(c) for c in p.split(",")) for p in
                                                                   elt.LineString.coordinates.text.strip().split()]))
                elif hasattr(elt, "Polygon"):
                    _kml_shapes[shape_id] = Shape(shape_id=shape_id,
                                                  name=name,
                                                  shape=shapely.Polygon(
                                                      shell=[tuple(float(c) for c in p.split(",")) for p in
                                                             elt.Polygon.outerBoundaryIs.LinearRing.coordinates.text.strip().split()]))
            elif hasattr(elt, "MultiGeometry"):
                if len(elt.MultiGeometry.getchildren()) > 0:
                    for gg in elt.MultiGeometry.getchildren():
                        name = elt.ExtendedData.SchemaData.attrib["schemaUrl"]
                        name = f"{name}_{elt.sourceline}"
                        tag = re.sub(r"^.*\}", "", gg.tag)
                        if tag == "Point":
                            if name in _kml_shapes:
                                if type(_kml_shapes[name].shape) != shapely.Point:
                                    print(f"Existing entity {name} of type {type(_kml_shapes[name].shape)}! Skip.")
                                    continue
                            _kml_shapes[name] = Shape(shape_id=name, name=name, shape=shapely.Point(
                                [float(x) for x in elt.Point.coordinates.text.split(",")[:-1]]))
                        elif tag == "LineString":
                            _kml_shapes[name] = Shape(shape_id=name,
                                                      name=name,
                                                      shape=shapely.LineString(
                                                          coordinates=[tuple(float(c) for c in p.split(",")) for p
                                                                       in gg.coordinates.text.strip().split()]))
                        elif tag == "Polygon":
                            _kml_shapes[name] = Shape(shape_id=name,
                                                      name=name,
                                                      shape=shapely.Polygon(
                                                          shell=[tuple(float(c) for c in p.split(",")) for p in
                                                                 gg.outerBoundaryIs.LinearRing.coordinates.text.strip().split()]))

import json
import warnings

from .extension import _export, _import

StoreType = 1
PropertiesType = 2
RandomVariableType = 3
ExpressionType = 4
NativeType = 5  # Used for native python objects
MediumType = 6
LayerSpecType = 7
MaskSpecType = 8
ExtrusionSpecType = 9
PortSpecType = 10
TechnologyType = 11
RectangleType = 12
CircleType = 13
PolygonType = 14
PathType = 15
PolyhedronType = 16
ExtrudedType = 17
ConstructiveSolidType = 18
LabelType = 19
PortType = 20
FiberPortType = 21
GaussianPortType = 22
TerminalType = 23
ModelType = 24
ReferenceType = 25
ComponentType = 26
SMatrixType = 27
PoleResidueMatrixType = 28
TimeDomainModelType = 29


def _scale(n, obj=None):
    v = obj[n] if obj is not None else n
    if isinstance(v, list):
        v = [_scale(x) for x in v]
    elif isinstance(v, dict):
        v = {k: _scale(x) for k, x in v.items()}
    elif v is not None:
        v *= 1e-5
    if obj is not None:
        obj[n] = v
    return v


def _replace(name, obj, data):
    v = obj[name]
    if isinstance(v, list):
        if len(v) > 0 and isinstance(v[0], list) and len(v[0]) == 2 and isinstance(v[0][0], str):
            obj[name] = [[k, _compose(data[x], data)] for k, x in v]
        else:
            obj[name] = [_compose(data[x], data) for x in v]
    elif isinstance(v, dict):
        obj[name] = {k: _compose(data[x], data) for k, x in v.items()}
    else:
        obj[name] = _compose(data[v], data)


def _convert_interpolator(obj):
    v = obj.pop("variant")
    obj["type"] = v
    if v == "constant":
        _scale("value", obj)
    elif v == "linear" or v == "smooth":
        _scale("values", obj)
    elif v == "parametric":
        _scale("offset", obj)


def _convert_path_section(obj):
    v = obj.pop("variant")
    obj["type"] = v
    _convert_interpolator(obj["width"])
    _convert_interpolator(obj["offset"])
    if v == "segment":
        _scale("vertices", obj)
    elif v == "arc":
        _scale("radius", obj)
        _scale("center", obj)
        _scale("endpoint_delta", obj)
    elif v == "euler":
        _scale("radius_eff", obj)
        _scale("origin", obj)
        _scale("endpoint_delta", obj)
    elif v == "bezier":
        _scale("controls", obj)
    elif v == "parametric":
        _scale("origin", obj)


def _compose(obj, data):
    t = obj["type"]
    if t == ExtrusionSpecType:
        obj["media"] = {k: data[v]["medium"] for k, v in obj["media"].items() if len(v) > 0}
        _replace("mask_spec", obj, data)
        _scale("limits", obj)
        _scale("reference", obj)
    elif t == PortSpecType:
        _scale("default_radius", obj)
        _scale("electrical_spec", obj)
        _scale("width", obj)
        _scale("limits", obj)
        for pp in obj["path_profiles"]:
            _scale("width", pp)
            _scale("offset", pp)
    elif t == TechnologyType:
        obj["background_media"] = {
            k: data[v]["medium"] for k, v in obj["background_media"].items() if len(v) > 0
        }
        _replace("layers", obj, data)
        _replace("extrusion_specs", obj, data)
        _replace("ports", obj, data)
        obj["parametric_data"]["random_variables"] = []
    elif t == RectangleType:
        obj["type"] = "Rectangle"
        _scale("center", obj)
        _scale("size", obj)
    elif t == CircleType:
        obj["type"] = "Circle"
        _scale("center", obj)
        _scale("radius", obj)
        _scale("inner_radius", obj)
    elif t == PolygonType:
        obj["type"] = "Polygon"
        _scale("vertices", obj)
        _scale("holes", obj)
    elif t == PathType:
        obj["type"] = "Path"
        _scale("end_position", obj)
        _scale("end_width", obj)
        _scale("end_offset", obj)
        for s in obj["path_sections"]:
            _convert_path_section(s)
    return obj


def _to_json(obj):
    warnings.warn(
        "json formats are deprecated and scheduled to be removed in the next release. "
        "Please use native phf formats instead.",
        DeprecationWarning,
        3,
    )
    store = json.loads(_export(obj, use_json=True))
    data = dict(store["data"])
    return json.dumps(_compose(data[store["top_content"][0][0]], data))


def _decompose_media(name, obj, data):
    media = {"optical": "", "electrical": ""}
    for k in obj[name]:
        m = obj[name][k]
        v = {
            "id": str(id(m)),
            "type": MediumType,
            "type_version": "0.0",
            "properties": "",
            "medium": m,
        }
        media[k] = _decompose(v, data)
    obj[name] = media


def _descale(n, obj=None):
    v = obj[n] if obj is not None else n
    if isinstance(v, list):
        v = [_descale(x) for x in v]
    elif isinstance(v, dict):
        v = {k: _descale(x) for k, x in v.items()}
    elif v is not None:
        v = round(v * 1e5)
    if obj is not None:
        obj[n] = v
    return v


def _dereplace(name, obj, data):
    v = obj[name]
    if isinstance(v, list):
        if len(v) > 0 and isinstance(v[0], list) and len(v[0]) == 2 and isinstance(v[0][0], str):
            obj[name] = [[k, _decompose(x, data)] for k, x in v]
        else:
            obj[name] = [_decompose(x, data) for x in v]
    else:
        obj[name] = _decompose(v, data)


def _deconvert_interpolator(obj):
    v = obj.pop("type")
    obj["variant"] = v
    if v == "constant":
        _descale("value", obj)
    elif v == "linear" or v == "smooth":
        _descale("values", obj)
    elif v == "parametric":
        _descale("offset", obj)


def _deconvert_path_section(obj):
    v = obj.pop("type")
    obj["variant"] = v
    _deconvert_interpolator(obj["width"])
    _deconvert_interpolator(obj["offset"])
    if v == "segment":
        _descale("vertices", obj)
    elif v == "arc":
        _descale("radius", obj)
        _descale("center", obj)
        _descale("endpoint_delta", obj)
    elif v == "euler":
        _descale("radius_eff", obj)
        _descale("origin", obj)
        _descale("endpoint_delta", obj)
    elif v == "bezier":
        _descale("controls", obj)
    elif v == "parametric":
        _descale("origin", obj)


def _decompose(obj, data):
    t = obj["type"]
    if t == ExtrusionSpecType:
        _decompose_media("media", obj, data)
        _dereplace("mask_spec", obj, data)
        _descale("limits", obj)
        _descale("reference", obj)
    elif t == PortSpecType:
        _descale("default_radius", obj)
        _descale("electrical_spec", obj)
        _descale("width", obj)
        _descale("limits", obj)
        for pp in obj["path_profiles"]:
            _descale("width", pp)
            _descale("offset", pp)
    elif t == TechnologyType:
        _decompose_media("background_media", obj, data)
        _dereplace("layers", obj, data)
        _dereplace("extrusion_specs", obj, data)
        _dereplace("ports", obj, data)
    elif t == "Rectangle":
        obj["type"] = RectangleType
        _descale("center", obj)
        _descale("size", obj)
    elif t == "Circle":
        obj["type"] = CircleType
        _descale("center", obj)
        _descale("radius", obj)
        _descale("inner_radius", obj)
    elif t == "Polygon":
        obj["type"] = PolygonType
        _descale("vertices", obj)
        _descale("holes", obj)
    elif t == "Path":
        obj["type"] = PathType
        _descale("end_position", obj)
        _descale("end_width", obj)
        _descale("end_offset", obj)
        for s in obj["path_sections"]:
            _deconvert_path_section(s)
    i = obj["id"]
    data[i] = obj
    return i


def _from_json(json_str):
    warnings.warn(
        "json formats are deprecated and scheduled to be removed in the next release. "
        "Please use native phf formats instead.",
        DeprecationWarning,
        3,
    )
    obj = json.loads(json_str)
    data = {}
    top = [_decompose(obj, data), obj["type"]]
    store = {
        "id": "0",
        "type": StoreType,
        "type_version": "0.0",
        "properties": "",
        "config": {
            "grid": 100,
            "tolerance": 500,
            "mesh_refinement": 20,
            "default_technology": "",
            "default_kwargs": {"type": "dict", "values": []},
        },
        "top_content": [top],
        "data": [[k, v] for k, v in data.items()],
    }
    return _import(byte_repr=json.dumps(store).encode(), use_json=True)[0][0]

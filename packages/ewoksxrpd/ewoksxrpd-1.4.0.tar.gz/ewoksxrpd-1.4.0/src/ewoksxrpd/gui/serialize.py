import json
from numbers import Integral
from typing import Union
import numpy


def json_dumps(value) -> str:
    return json.dumps(value)


def json_loads(value: str):
    return json.loads(value)


def float_serialize(value: float) -> str:
    return str(value)


def float_deserialize(value: str) -> float:
    return float(value)


def strfloat_serialize(value: Union[float, str]) -> str:
    return str(value)


def strfloat_deserialize(value: str) -> float:
    return float(value)


def cm_serialize(value: float) -> str:
    return str(value * 1e2)


def cm_deserialize(value: str) -> float:
    return float(value) * 1e-2


def degrees_serialize(value: float) -> str:
    return str(numpy.degrees(value))


def degrees_deserialize(value: str) -> float:
    return numpy.radians(float(value))


def posint_serialize(value: Integral) -> Integral:
    return max(value, 0)


def posint_deserialize(value: Integral) -> Integral:
    return max(value, 0)

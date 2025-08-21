from typing import List, Mapping, Union

# Note: mypy does not yet have support for recursive types, so this will have to do for now
# See discussion here: https://github.com/python/typing/issues/182
_JSONPrimitive = Union[str, float, int, bool, None]
_JSONSerializable1 = Union[_JSONPrimitive, Mapping[str, _JSONPrimitive], List[_JSONPrimitive]]
_JSONSerializable2 = Union[
    _JSONPrimitive, Mapping[str, _JSONSerializable1], List[_JSONSerializable1]
]
_JSONSerializable3 = Union[
    _JSONPrimitive, Mapping[str, _JSONSerializable2], List[_JSONSerializable2]
]
_JSONSerializable4 = Union[
    _JSONPrimitive, Mapping[str, _JSONSerializable3], List[_JSONSerializable3]
]
_JSONSerializable5 = Union[
    _JSONPrimitive, Mapping[str, _JSONSerializable4], List[_JSONSerializable4]
]
JSONSerializable = Union[_JSONPrimitive, Mapping[str, _JSONSerializable5], List[_JSONSerializable5]]

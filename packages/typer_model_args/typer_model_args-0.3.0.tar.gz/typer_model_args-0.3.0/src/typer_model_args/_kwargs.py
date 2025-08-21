import dataclasses
from inspect import Signature

Property = object()

@dataclasses.dataclass(frozen=True)
class ModelParameterInfo:
    kwarg_names: list[str]
    model: type

@dataclasses.dataclass(frozen=True)
class FlatSignature:
    signature: Signature
    original_kwargs_map: dict[str, object | ModelParameterInfo]

def rebuild_kwargs(
        original_function_name: str,
        kwargs: dict[str, any],
        flat_signature: FlatSignature
) -> dict[str, any]:
    rebuilt_kwargs = {}
    for kwarg_name, value in flat_signature.original_kwargs_map.items():
        if value is Property:
            rebuilt_kwargs[kwarg_name] = _get_parameter_value(original_function_name, kwargs, kwarg_name)
        elif isinstance(value, ModelParameterInfo):
            object_kwargs = {
                object_kwarg_name: _get_parameter_value(original_function_name, kwargs, object_kwarg_name)
                for object_kwarg_name
                in value.kwarg_names
            }
            rebuilt_kwargs[kwarg_name] = value.model(**object_kwargs)
        else:
            raise TypeError(f"Invalid value type in original_kwargs_map {value}")
    return rebuilt_kwargs

def _get_parameter_value(function_name: str, kwargs: dict[str, any], key: str) -> any:
    if key not in kwargs:
        error_message = f"{function_name}() missing 1 required keyword argument: '{key}'"
        raise TypeError(error_message)
    return kwargs[key]

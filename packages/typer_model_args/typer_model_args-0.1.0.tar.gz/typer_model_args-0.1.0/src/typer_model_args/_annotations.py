import inspect
from inspect import Signature, Parameter
from typing import Annotated

import click
import typer
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic.v1.typing import is_literal_type, get_args
from pydantic_core._pydantic_core import PydanticUndefined
from typer.models import OptionInfo, ArgumentInfo

from ._kwargs import FlatSignature, ModelParameterInfo, Property


def flatten_signature(signature: inspect.Signature) -> FlatSignature:
    parameters = []
    original_kwargs_map = {}
    for parameter in signature.parameters.values():
        if issubclass(parameter.annotation, BaseModel):
            flat_parameters = _flatten_model_to_parameters(parameter)
            original_kwargs_map[parameter.name] = ModelParameterInfo(
                kwarg_names=list(flat_parameters.keys()),
                model=parameter.annotation
            )
            parameters.extend(flat_parameters.values())
        else:
            field = FieldInfo.from_annotation(parameter.annotation)
            original_kwargs_map[parameter.name] = Property
            parameters.append(_create_parameter(parameter.name, field))
    return FlatSignature(
        signature=Signature(parameters),
        original_kwargs_map=original_kwargs_map
    )

def _create_parameter(field_name: str, field: FieldInfo) -> Parameter:
    if _is_typer_annotated_field(field):
        return _create_typer_parameter(field_name, field)
    elif is_literal_type(field.annotation):
        return _create_literal_parameter(field_name, field)
    return _create_regular_parameter(field_name, field)

def _is_typer_annotated_field(field: FieldInfo) -> bool:
    for metadata in field.metadata:
        if isinstance(metadata, OptionInfo | ArgumentInfo):
            return True
    return False

def _create_typer_parameter(field_name: str, field: FieldInfo) -> Parameter:
    return Parameter(
        name=field_name,
        kind=Parameter.KEYWORD_ONLY,
        default=_get_field_default_value(field),
        annotation=field.rebuild_annotation()
    )

def _create_literal_parameter(field_name: str, field: FieldInfo) -> Parameter:
    return Parameter(
        name=field_name,
        kind=Parameter.KEYWORD_ONLY,
        default=_get_field_default_value(field),
        annotation=Annotated[
            str,
            typer.Option(
                f"--{field_name.replace('_', '-')}",
                show_choices=True,
                click_type=click.Choice(get_args(field.annotation)),
                help=field.description
            )
        ]
    )

def _create_regular_parameter(field_name: str, field: FieldInfo) -> Parameter:
    field = FieldInfo.from_annotation(field.annotation)
    return Parameter(
        name=field_name,
        kind=Parameter.KEYWORD_ONLY,
        default=_get_field_default_value(field),
        annotation=Annotated[
            str,
            typer.Option(
                f"--{field_name.replace('_', '-')}",
                help=field.description
            )
        ]
    )

def _get_field_default_value(field: FieldInfo) -> any:
    if field.default is PydanticUndefined:
        return Parameter.empty
    return field.default

def _flatten_model_to_parameters(parameter: Parameter) -> dict[str, Parameter]:
    return {
        name: _create_parameter(name, field)
        for name, field
        in parameter.annotation.model_fields.items()
    }

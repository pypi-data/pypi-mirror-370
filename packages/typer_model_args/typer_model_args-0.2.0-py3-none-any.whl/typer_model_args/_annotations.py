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


def flatten_signature(
        signature: inspect.Signature,
        literals_to_enums: bool = True,
) -> FlatSignature:
    parameters = []
    original_kwargs_map = {}
    for parameter in signature.parameters.values():
        if issubclass(parameter.annotation, BaseModel):
            flat_parameters = _flatten_model_to_parameters(parameter, literals_to_enums=literals_to_enums)
            original_kwargs_map[parameter.name] = ModelParameterInfo(
                kwarg_names=list(flat_parameters.keys()),
                model=parameter.annotation
            )
            parameters.extend(flat_parameters.values())
        else:
            field = FieldInfo.from_annotation(parameter.annotation)
            original_kwargs_map[parameter.name] = Property
            parameters.append(_create_parameter(parameter.name, field, literals_to_enums=literals_to_enums))
    return FlatSignature(
        signature=Signature(parameters),
        original_kwargs_map=original_kwargs_map
    )

def _create_parameter(
        field_name: str,
        field: FieldInfo,
        *,
        literals_to_enums: bool,
) -> Parameter:
    typer_parameter_meta = _get_typer_parameter_metadata(field)
    if typer_parameter_meta is not None:
        return _create_typer_parameter(typer_parameter_meta, field_name, field, literals_to_enums=literals_to_enums)
    elif literals_to_enums and is_literal_type(field.annotation):
        return _create_literal_parameter(field_name, field, OptionInfo())
    return _create_regular_parameter(field_name, field)

def _is_typer_annotated_field(field: FieldInfo) -> bool:
    for metadata in field.metadata:
        if isinstance(metadata, OptionInfo | ArgumentInfo):
            return True
    return False

def _get_typer_parameter_metadata(field: FieldInfo) -> OptionInfo | ArgumentInfo | None:
    for metadata in field.metadata:
        if isinstance(metadata, OptionInfo | ArgumentInfo):
            return metadata
    return None

def _create_typer_parameter(
        typer_parameter_meta: OptionInfo | ArgumentInfo,
        field_name: str,
        field: FieldInfo,
        *,
    literals_to_enums: bool,
) -> Parameter:
    if literals_to_enums and is_literal_type(field.annotation):
        return _create_literal_parameter(field_name, field, typer_parameter_meta)
    return Parameter(
        name=field_name,
        kind=Parameter.KEYWORD_ONLY,
        default=_get_field_default_value(field),
        annotation=field.rebuild_annotation()
    )

def _create_literal_parameter(
        field_name: str,
        field: FieldInfo,
        typer_parameter_origin: ArgumentInfo | OptionInfo
) -> Parameter:
    argument_properties = typer_parameter_origin.__dict__ | {
        "default": f"--{field_name.replace('_', '-')}",
        "show_choices": True,
        "click_type": click.Choice(get_args(field.annotation)),
        "help": field.description,
    }
    return Parameter(
        name=field_name,
        kind=Parameter.KEYWORD_ONLY,
        default=_get_field_default_value(field),
        annotation=Annotated[
            str,
            type(typer_parameter_origin)(**argument_properties)
        ]
    )

def _create_regular_parameter(field_name: str, field: FieldInfo) -> Parameter:
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

def _flatten_model_to_parameters(
        parameter: Parameter,
        *,
        literals_to_enums: bool
) -> dict[str, Parameter]:
    return {
        name: _create_parameter(name, field, literals_to_enums =literals_to_enums)
        for name, field
        in parameter.annotation.model_fields.items()
    }

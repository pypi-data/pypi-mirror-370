from dataclasses import dataclass, field
from typing import Dict, List, Any

from marshmallow import Schema, fields


@dataclass
class ExposedParameter:
    parameter: str
    title: str
    field_type: fields.Field
    field_options: Dict[str, Any] = field(default_factory=dict)
    field_args: List[Any] = field(default_factory=list)
    read_only: bool = False


class DaiquiriProcessorMixin:
    EXPOSED_PARAMETERS: List[ExposedParameter] = []

    @property
    def parameters_schema(self) -> Schema:
        uiorder = ["state", "state_ok", "enabled"]
        uischema = {
            "enabled": {
                "ui:widget": "BoolButton",
            }
        }

        parameters = {}
        for parameter in self.EXPOSED_PARAMETERS:
            parameters[parameter.parameter] = parameter.field_type(
                metadata={"title": parameter.title, "readOnly": parameter.read_only},
                *parameter.field_args,
                **parameter.field_options,
            )
            uiorder.append(parameter.parameter)

        return type(
            "ExposedParameters",
            (Schema,),
            {
                "Meta": type(
                    "Meta", (object,), {"uiorder": uiorder, "uischema": uischema}
                ),
                "enabled": fields.Bool(metadata={"title": "Enabled"}),
                **parameters,
            },
        )

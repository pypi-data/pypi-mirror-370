from __future__ import annotations
from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional, Dict, Any, List
from nestful.schemas.sequences import SequenceStep
from nestful.schemas.api import Component, QueryParameter, API
from nestful.utils import get_token


class ToolCall(SequenceStep):
    model_config = ConfigDict(extra="ignore")

    id: Optional[str] = None
    type: Optional[str] = "function"

    @model_validator(mode="after")
    def set_id(self) -> ToolCall:
        if self.id is None:
            self.id = str(hash(self.name))

        return self

    @staticmethod
    def initialize_from_list(
        tool_calls: List[Dict[str, Any]]
    ) -> List[SequenceStep]:
        list_of_steps = []

        for index, tool_call in enumerate(tool_calls):
            tool_call_object = ToolCall(**tool_call)
            tool_call_object.label = tool_call.get(
                "label", get_token(index + 1)
            )

            list_of_steps.append(tool_call_object.convert_to_sequence_step())

        return list_of_steps

    def convert_to_sequence_step(self) -> SequenceStep:
        return SequenceStep(
            name=self.name,
            arguments=self.arguments,
            label=self.label,
        )


class OpenAIToolCall(BaseModel):
    id: Optional[str] = None
    type: str = "function"
    function: ToolCall

    @staticmethod
    def initialize_from_list(
        tool_calls: List[Dict[str, Any]]
    ) -> List[SequenceStep]:
        tool_calls_internal = [
            OpenAIToolCall(**item).function.dict() for item in tool_calls
        ]
        return ToolCall.initialize_from_list(tool_calls_internal)

    def convert_to_sequence_step(self) -> SequenceStep:
        return self.function.convert_to_sequence_step()


class Tool(BaseModel):
    name: str
    description: str
    parameters: Component
    output_parameters: Optional[Component] = None

    def convert_to_catalog_spec(self) -> API:
        query_parameters: Dict[str, QueryParameter] = dict()

        for param, props in self.parameters.properties.items():
            tmp_props = props.dict()

            del tmp_props["required"]

            query_parameters[param] = QueryParameter(
                **tmp_props, required=param in self.parameters.required
            )

        api = API(
            name=self.name,
            description=self.description,
            query_parameters=query_parameters,
        )

        if self.output_parameters is not None:
            tmp_props = (
                self.output_parameters.items
                if self.output_parameters.type == "array"
                else self.output_parameters
            )

            if isinstance(tmp_props, Component):
                api.output_parameters = {}

                for k, v in tmp_props.properties.items():
                    if isinstance(v, Component):
                        api.output_parameters[k] = v
                    else:
                        raise NotImplementedError()

        return api


class OpenAITool(BaseModel):
    type: str = "function"
    function: Tool

    def convert_to_catalog_spec(self) -> API:
        return self.function.convert_to_catalog_spec()

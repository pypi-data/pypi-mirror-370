from typing import List, Dict, Union, Any, Tuple, Optional
from enum import StrEnum, auto
from pydantic import BaseModel
from genson import SchemaBuilder
from nestful.schemas.openapi import Component
from nestful.utils import get_token
from nestful.schemas.api import API, Catalog, QueryParameter
from nestful.schemas.sequences import (
    SequenceStep,
    SequencingData,
    SequencingDataset,
)


class Role(StrEnum):
    USER = auto()
    ASSISTANT = auto()
    OBSERVATION = auto()


class FunctionCall(BaseModel):
    role: Role = Role.ASSISTANT
    function_call: List[SequenceStep]


class Content(BaseModel):
    role: Role
    content: str = ""


class Data(BaseModel):
    status: bool
    message: str
    data: Dict[str, Any] | List[Dict[str, Any]] | Any


class Observation(BaseModel):
    role: Role = Role.OBSERVATION
    content: List[Data | Dict[str, Any]]


class Function(BaseModel):
    name: str
    description: str
    parameters: Component

    def convert_to_nestful_api(
        self,
        cached_responses: List[Dict[str, Any] | List[Dict[str, Any]]],
        store_responses: bool = True,
    ) -> API:
        parameters: Dict[str, QueryParameter] = {}

        for item, value in self.parameters.properties.items():
            if isinstance(value, Component):
                parameters[item] = QueryParameter(
                    type=(
                        value.type[0]
                        if isinstance(value.type, List)
                        else value.type
                    ),
                    description=value.description,
                    enum=value.enum,
                    required=item in self.parameters.required,
                )

            else:
                raise NotImplementedError(
                    "Complex schema nesting not identified in data."
                )

        schema_builder = SchemaBuilder()

        for response in cached_responses:
            schema_builder.add_object(response)

        schema = schema_builder.to_schema()

        if "type" in schema:
            if schema["type"] == "object":
                output_schema = schema.get("properties", {})
            elif schema["type"] == "array":
                output_schema = schema.get("items", {}).get("properties", {})
            else:
                raise NotImplementedError("ISS3/ISS4")

        else:
            output_schema = {}

        output_parameters = {
            k: Component.model_validate(v) for k, v in output_schema.items()
        }

        if "EndPoint" in self.description:
            description_split = self.description.split("EndPoint:")
            description = description_split[0].strip()
            endpoint = description_split[1].strip()

        else:
            description = self.description
            endpoint = None

        return API(
            name=self.name,
            description=description,
            host="booking-com15.p.rapidapi.com",
            endpoint=endpoint,
            query_parameters=parameters,
            output_parameters=output_parameters,
            sample_responses=cached_responses if store_responses else [],
        )


class Conversation(BaseModel):
    id: str
    conversations: List[Union[FunctionCall, Content, Observation]]
    functions: List[Function]


class ComplexFuncBench(BaseModel):
    data: List[Conversation]

    def convert_to_nestful(
        self, store_responses: bool = True
    ) -> Tuple[SequencingDataset, Catalog]:
        new_catalog = Catalog()
        sequences: List[SequencingData] = []
        response_map: Dict[str, List[Dict[str, Any] | List[Dict[str, Any]]]] = (
            dict()
        )

        for sample in self.data:
            new_sequence = SequencingData()

            for index, step in enumerate(sample.conversations):
                if isinstance(step, Content) and step.role == Role.USER:
                    new_sequence.input = f"{new_sequence.input} {step.content}"

                if isinstance(step, FunctionCall):
                    for pos, func_call in enumerate(step.function_call):
                        if func_call.name:
                            current_cache = response_map.get(func_call.name, [])
                            new_response_inner: Optional[
                                Dict[str, Any] | List[Dict[str, Any]]
                            ] = None

                            for lookahead_step in sample.conversations[
                                index + 1 :
                            ]:
                                if isinstance(lookahead_step, Observation):
                                    new_response = lookahead_step.content[pos]
                                    new_response_inner = (
                                        new_response.data
                                        if isinstance(new_response, Data)
                                        else new_response
                                    )

                                    current_cache.append(new_response_inner)
                                    break

                            func_call.response = new_response_inner
                            func_call.label = get_token(
                                index=len(new_sequence.output) + 1
                            )

                            new_sequence.output.append(func_call)

                            response_map[func_call.name] = current_cache

            new_sequence.add_references()
            sequences.append(new_sequence)

        for sample in self.data:
            for func in sample.functions:
                existing_api = new_catalog.get_api(name=func.name or "")

                if existing_api is None:
                    cached_responses = response_map.get(func.name, [])

                    api = func.convert_to_nestful_api(
                        cached_responses=cached_responses,
                        store_responses=store_responses,
                    )

                    new_catalog.apis.append(api)

        return SequencingDataset(data=sequences), new_catalog

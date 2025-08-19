from __future__ import annotations
from nestful.schemas.openapi import Component
from pydantic import BaseModel, ConfigDict
from typing import List, Set, Dict, Optional, Union, Any, Mapping
from copy import deepcopy


class QueryParameter(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: Optional[str] = None
    description: Optional[str] = None
    required: bool = False
    enum: List[str] = []
    default: Optional[str | int | float] = None


class MinifiedAPI(BaseModel):
    name: str
    inputs: List[str]
    outputs: List[str]


class API(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: Optional[str] = None
    name: str
    description: str
    host: Optional[str] = None
    endpoint: Optional[str] = None
    query_parameters: Dict[str, QueryParameter] = dict()
    output_parameters: Mapping[str, Component] = dict()
    sample_responses: List[Dict[str, Any] | List[Dict[str, Any]]] = []

    def __str__(self) -> str:
        self_dict = self.dict(
            include={
                "name",
                "description",
                "query_parameters",
                "output_parameters",
            }
        )

        name_transform = {
            "query_parameters": "parameters",
            "output_parameters": "output_schema",
        }

        for item, transform in name_transform.items():
            self_dict[transform] = self_dict[item]
            del self_dict[item]

        return str(self_dict)

    def get_arguments(self, required: Optional[bool] = True) -> List[str]:
        if required is None:
            return list(self.query_parameters.keys())
        else:
            return [
                key
                for key in self.query_parameters.keys()
                if self.query_parameters[key].required is required
            ]

    def get_outputs(self) -> List[str]:
        return list(flatten_schema(self.output_parameters))

    def get_input_as_component(self) -> Component:
        required_props = [
            k for k, v in self.query_parameters.items() if v.required is True
        ]

        return Component(
            type="object",
            properties=self.query_parameters,
            required=required_props,
        )

    def get_output_as_component(self) -> Component:
        required_props = [
            k for k, v in self.output_parameters.items() if v.required is True
        ]

        return Component(
            type="object",
            properties=self.output_parameters,
            required=required_props,
        )

    def minified(self, required: Optional[bool] = True) -> MinifiedAPI:
        return MinifiedAPI(
            name=self.name,
            inputs=self.get_arguments(required),
            outputs=self.get_outputs(),
        )


class Catalog(BaseModel):
    apis: List[API] = []

    def get_api(
        self,
        name: str,
        minified: bool = False,
        required: Optional[bool] = False,
    ) -> Union[API, MinifiedAPI, None]:
        api_object: Optional[API] = next(
            (api for api in self.apis if api.name == name), None
        )

        if api_object is None:
            api_object = next(
                (
                    api
                    for api in self.apis
                    if api.id is not None and api.id == name
                ),
                None,
            )

        if api_object:
            return api_object if not minified else api_object.minified(required)

        return None


def flatten_schema(
    schema: Mapping[str, Any],
    delimiter: str = ".",
    keychain: Optional[List[str]] = None,
) -> Set[str]:
    flattened_keys: Set[str] = set()
    keychain = keychain or []

    type_of_schema = schema.get("type", None)

    if type_of_schema == "array":
        schema = schema.get("items", {}) or {}
        type_of_schema = schema.get("type", "object")

    if type_of_schema is not None:
        schema = schema.get("properties", {})

    for key, value in schema.items():
        tmp_keychain = deepcopy(keychain)
        tmp_keychain.append(key)

        flattened_keys.add(f"{delimiter}".join(tmp_keychain))

        if isinstance(value, Component):
            value = value.model_dump()

        if isinstance(value, Dict):
            flattened_keys.update(
                flatten_schema(value, delimiter, tmp_keychain)
            )

    return flattened_keys

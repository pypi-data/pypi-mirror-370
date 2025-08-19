from nestful import Catalog, API, SequenceStep, SequencingData
from nestful.schemas.openapi import Component, ResponseSelection
from nestful.hypothesis_generator.faker_generator import FakerGenerator
from typing import Dict, Any, Optional, Mapping
from hypothesis_jsonschema import from_schema
from hypothesis.strategies import SearchStrategy
from hypothesis import given, settings, HealthCheck


class Hypothesis:
    def __init__(self, name: str, catalog: Catalog) -> None:
        self.api = catalog.get_api(name)
        self.faker = FakerGenerator()

        if self.api is None:
            raise ValueError(f"No API with name: {name}")

        self.strategy: Optional[SearchStrategy] = None
        self.random_value: Dict[str, Any] = {}

    def generate_sample(
        self,
        min_string_length: int = 3,
        min_array_length: int = 3,
        pattern: str = "^[a-zA-Z0-9_.-]*$",
    ) -> None:
        assert isinstance(self.api, API)

        json_form = get_output_in_json_form(
            self.api.output_parameters,
            min_string_length,
            min_array_length,
            pattern,
        )

        self.strategy = from_schema(json_form)
        self.store_value()  # type: ignore

    @(
        lambda method: lambda self, *args, **kwargs: given(self.strategy)(
            method
        )(self, *args, **kwargs)
    )
    @settings(
        suppress_health_check=(
            HealthCheck.too_slow,
            HealthCheck.filter_too_much,
        )
    )
    def store_value(self, value: Any) -> None:
        self.random_value = value


def add_basic_item(
    component: Optional[Component], min_string_length: int, pattern: str
) -> Dict[str, Any]:
    if component is not None:
        type_form = (
            "number"
            if component.type in ["float", "double"]
            else component.type
        )
    else:
        type_form = "string"

    return {
        "type": type_form,
        "minimum": 0,
        "maximum": 100,
        "minLength": min_string_length,
        "pattern": pattern,
    }


def get_output_in_json_form(
    output_parameters: Mapping[str, Component],
    min_string_length: int = 3,
    min_array_length: int = 3,
    pattern: str = "^[a-zA-Z0-9_.-]*$",
) -> Dict[str, Any]:
    json_form: Dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "required": list(output_parameters.keys()),
        "properties": dict(),
    }

    for item, value in output_parameters.items():
        if value.required:
            json_form["required"].append(item)

        json_form["properties"][item] = {"type": value.type}

        if value.type == "object":
            if value.properties:
                if any(
                    [
                        isinstance(v, ResponseSelection)
                        for v in value.properties.values()
                    ]
                ):
                    raise NotImplementedError()

                if all(
                    [
                        isinstance(v, Component)
                        for v in value.properties.values()
                    ]
                ):
                    json_form["properties"][item] = get_output_in_json_form(
                        value.properties,  # type: ignore
                        min_string_length,
                        min_array_length,
                        pattern,
                    )

                else:
                    tmp_properties = {
                        key: Component(type=value)
                        for key, value in value.properties.items()
                        if isinstance(value, str)
                    }

                    json_form["properties"][item] = get_output_in_json_form(
                        tmp_properties,
                        min_string_length,
                        min_array_length,
                        pattern,
                    )
            else:
                json_form["properties"][item]["additionalProperties"] = True

        elif value.type == "array":
            json_form["properties"][item]["minItems"] = min_array_length

            if (
                isinstance(value.items, Component)
                and value.items.type == "object"
            ):
                json_form["properties"][item]["items"] = (
                    get_output_in_json_form(
                        value.items.properties,  # type: ignore
                        min_string_length,
                        min_array_length,
                        pattern,
                    )
                )
            else:
                json_form["properties"][item]["items"] = add_basic_item(
                    value.items, min_string_length, pattern
                )
        else:
            json_form["properties"][item] = add_basic_item(
                value, min_string_length, pattern
            )

    return json_form


def generate_dummy_output_sequence(
    sequence: SequencingData,
    catalog: Catalog,
    index: int,
    use_memory: bool = False,
    min_string_length: int = 3,
    min_array_length: int = 3,
) -> Dict[str, Any]:
    memory: Dict[str, Any] = {}

    for i in range(index):
        label = sequence.output[i].label

        if label is not None:
            step_memory = generate_dummy_output_step(
                sequence.output[i],
                catalog,
                use_memory,
                min_string_length,
                min_array_length,
            )
            memory[label] = step_memory

    return memory


def generate_dummy_output_step(
    step: SequenceStep,
    catalog: Catalog,
    use_memory: bool = False,
    min_string_length: int = 3,
    min_array_length: int = 3,
) -> Dict[str, Any]:
    if use_memory is True:
        return step.get_memory(fill_in_memory=False).get(step.label or "", {})
    else:
        try:
            hypothesis = Hypothesis(name=step.name or "", catalog=catalog)

            hypothesis.generate_sample(min_string_length, min_array_length)
            return hypothesis.random_value

        except Exception as e:
            print(e)
            return {}

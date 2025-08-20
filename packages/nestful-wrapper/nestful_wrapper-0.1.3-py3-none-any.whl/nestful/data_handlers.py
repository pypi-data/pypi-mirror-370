from enum import StrEnum, auto
from pathlib import Path
from json import load
from os import listdir
from os.path import isfile, join
from jsonref import replace_refs
from http import HTTPStatus
from typing import Any, Optional, Tuple, List

from nestful import SequencingDataset, SequencingData, Catalog, API
from nestful.schemas.openapi import OpenAPI, Component, PathSpec
from nestful.schemas.api import QueryParameter


class DataType(StrEnum):
    DATA = auto()
    SPEC = auto()


class DataID(StrEnum):
    EXE = ""
    GLAIVE = auto()
    SGD = auto()
    COMPLEXFUNCBENCH = auto()


def data_path_constructor(
    data_type: DataType = DataType.DATA,
    executable: bool = True,
    name: Optional[DataID | str] = None,
    version: Optional[str] = "v1",
) -> Path:
    assert (
        version == "v1"
    ), "The NESTFUL wrapper only supports version v1 for now."

    path_to_file = Path(__file__).parent.resolve()

    if name is not None:
        name = name.value if isinstance(name, DataID) else DataID(name).value

    if name == DataID.COMPLEXFUNCBENCH:
        relative_path_to_data = (
            f"../data_{version}/{name}/{name}-{data_type}.json"
        )

    else:
        exe_string = f"{'non-' if not executable else ''}executable"
        name = f"-{name}" if name else ""

        relative_path_to_data = f"../data_{version}/{exe_string}/{exe_string}{name}-{data_type}.json"

    return Path.joinpath(path_to_file, relative_path_to_data).resolve()


def read_raw_data(
    data_type: DataType = DataType.DATA,
    executable: bool = True,
    name: Optional[DataID | str] = None,
    version: Optional[str] = "v1",
) -> Any:
    path_to_data = data_path_constructor(data_type, executable, name, version)

    with open(path_to_data) as f:
        data = load(f)

    return data


def get_nestful_catalog(
    executable: bool = True,
    name: Optional[DataID | str] = None,
    version: Optional[str] = "v1",
) -> Catalog:
    data = read_raw_data(DataType.SPEC, executable, name, version)
    return Catalog(apis=[API.model_validate(item) for item in data])


def get_nestful_data(
    executable: bool = True,
    name: Optional[DataID | str] = None,
    version: Optional[str] = "v1",
) -> Tuple[SequencingDataset, Catalog]:
    catalog = get_nestful_catalog(executable, name, version)
    raw_sequence_data = read_raw_data(DataType.DATA, executable, name, version)
    sequence_data = SequencingDataset(data=[])

    for item in raw_sequence_data:
        sequence_instance = SequencingData.model_validate(item)
        sequence_data.data.append(sequence_instance)

    return sequence_data, catalog


def get_nestful_data_instance(
    index: int,
    executable: bool = True,
    name: Optional[DataID | str] = None,
    version: Optional[str] = "v1",
) -> Tuple[SequencingData, Catalog]:
    sequence_data, catalog = get_nestful_data(executable, name, version)

    assert index < len(sequence_data.data), (
        f"Requested dataset has {len(sequence_data.data)} samples, asked"
        f" for {index}!"
    )

    return sequence_data.data[index], catalog


def parse_api_from_openapi_spec(openapi_spec: OpenAPI) -> List[API]:
    list_of_apis = []
    path_objects = openapi_spec.paths

    for _, item in path_objects.items():
        for http_method, path_spec in item.items():
            if not isinstance(path_spec, PathSpec):
                continue

            for http_status, response_object in path_spec.responses.items():
                if http_status == HTTPStatus.OK:
                    output_parameters = response_object.get_parameters()

                    new_api = API(
                        name=path_spec.operationId,
                        description=path_spec.description or "",
                        query_parameters={
                            p.name: QueryParameter(required=p.required is True)
                            for p in path_spec.parameters
                        },
                        output_parameters={
                            item.name: Component() for item in output_parameters
                        },
                    )

                    list_of_apis.append(new_api)

    return list_of_apis


def get_catalog_from_openapi_specs(abs_path_to_specs: Path) -> Catalog:
    new_catalog = Catalog()

    if str(abs_path_to_specs).endswith(".json"):
        only_json_files = [str(abs_path_to_specs)]
    else:
        only_json_files = [
            filename
            for filename in listdir(abs_path_to_specs)
            if isfile(join(abs_path_to_specs, filename))
            and filename.endswith(".json")
        ]

    for file in only_json_files:
        try:
            with open(join(abs_path_to_specs, file)) as f:
                openapi_spec = load(f)

            openapi_spec_flat = replace_refs(
                openapi_spec, proxies=False, lazy_load=False
            )

            openapi_object = OpenAPI(**openapi_spec_flat)
            new_catalog.apis.extend(parse_api_from_openapi_spec(openapi_object))

        except Exception as e:
            print(e)

    return new_catalog

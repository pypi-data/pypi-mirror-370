from typing import List, Optional, Tuple
from re import match
from warnings import warn

TOKEN = "var"


def merge_quoted_parameters(list_of_parameters: List[str]) -> List[str]:
    new_parameters = []

    new_parameter = ""
    merge_on = False
    num_mergers = 0

    for parameter in list_of_parameters:
        if parameter.startswith('"') and parameter.count('"') % 2 == 1:
            merge_on = True

        if '="' in parameter and parameter.count('"') % 2 == 1:
            merge_on = True

        if merge_on:
            new_parameter += f'{", " if new_parameter else ""}{parameter}'
            num_mergers += 1

        if new_parameter.count('"') % 2 == 0:
            merge_on = False

        if not merge_on:
            temp = new_parameter or parameter
            new_parameter = ""

            if temp:
                new_parameters.append(temp)

    if num_mergers > 0:
        return merge_quoted_parameters(new_parameters)

    return new_parameters


def parse_parameters(signature: str) -> Tuple[str, List[str]]:
    try:
        match_object = match(
            pattern=r"\s*(?P<action_name>.*)\((?P<parameters>.*)\)\s*",
            string=signature,
        )

        if match_object:
            action_name = match_object.groupdict().get("action_name", "")
            parameters = match_object.groupdict().get("parameters", [])

            parameters = [p.strip() for p in parameters.split(",")]
            parameters = merge_quoted_parameters(parameters)

            return action_name, parameters
        else:
            return "", []

    except Exception as e:
        warn(
            message=f"Could not parse {signature}: {e}", category=SyntaxWarning
        )
        return "", []


def get_token(index: int, token: str = TOKEN) -> str:
    return f"{token}{index}"


def extract_label(label_string: Optional[str]) -> Tuple[str, Optional[str]]:
    label, mapping = "", None

    if label_string is not None:
        if "." in label_string:
            match_object = match(
                pattern=r".*\$(?P<label>[^\.]*)\.(?P<map>.*)\$.*",
                string=label_string,
            )

            if match_object:
                label = match_object.groupdict().get("label", "")
                mapping = match_object.groupdict().get("map", None)

        else:
            match_object = match(
                pattern=r".*\$(?P<map>.*)\$.*",
                string=label_string,
            )

            if match_object:
                label = get_token(index=0)
                mapping = match_object.groupdict().get("map", None)

    # TODO: Generic transformation
    if mapping is not None and "[" in mapping:
        mapping = mapping.split("[")[0]

    return label, mapping

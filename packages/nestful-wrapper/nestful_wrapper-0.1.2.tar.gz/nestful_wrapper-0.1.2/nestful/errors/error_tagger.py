from nestful import SequenceStep, SequencingData, Catalog
from nestful.schemas.sequences import ErrorTag
from nestful.schemas.errors import ErrorType
from nestful.utils import extract_label, TOKEN
from typing import Dict, Any


def tag_sequence_step(
    step: SequenceStep, ground_truth: SequenceStep, memory: Dict[str, Any]
) -> SequenceStep:
    step.errors = []

    if step.name != ground_truth.name:
        step.errors.append(
            ErrorTag(
                error_type=ErrorType.MADE_UP_API,
                info=step.name,
            )
        )

        return step

    for arg in ground_truth.arguments:
        if arg not in step.arguments:
            step.errors.append(
                ErrorTag(
                    error_type=ErrorType.MISSING_PARAMETER,
                    info=arg,
                )
            )

    for arg, value in step.arguments.items():
        if arg not in ground_truth.arguments:
            step.errors.append(
                ErrorTag(
                    error_type=ErrorType.MADE_UP_PARAMETER,
                    info=arg,
                )
            )

        else:
            original_assignment = ground_truth.arguments[arg]

            if value != original_assignment:
                step.errors.append(
                    ErrorTag(
                        error_type=ErrorType.WRONG_ASSIGNMENT,
                        info={arg: value},
                    )
                )

        label, mapping = extract_label(str(value))

        if label.startswith(TOKEN):
            reference = memory.get(label, {})

            if mapping:
                keys = mapping.split(".")

                for item in keys:
                    if item not in reference:
                        step.errors.append(
                            ErrorTag(
                                error_type=ErrorType.MADE_UP_ASSIGNMENT,
                                info=item,
                            )
                        )

                    reference = reference.get(item, {})

                if not reference:
                    step.errors.append(
                        ErrorTag(
                            error_type=ErrorType.MISSING_MEMORY,
                            info=value,
                        )
                    )

    return step


def tag_sequence(
    sequence: SequencingData,
    ground_truth: SequencingData,
    memory: Dict[str, Any],
    catalog: Catalog,
    fill_in_memory: bool = True,
) -> SequencingData:
    for index, step in enumerate(sequence.output):
        target_indices, gt_step = sequence.get_ground_truth_step(
            index, ground_truth
        )

        if gt_step is not None:
            tmp_memory = sequence.get_memory(
                catalog=catalog, index=index, fill_in_memory=fill_in_memory
            )

            tmp_memory = {**memory, **tmp_memory}

            sequence.output[index] = tag_sequence_step(
                step,
                ground_truth=gt_step,
                memory=tmp_memory,
            )

        else:
            if len(target_indices) == 0:
                reference_api = catalog.get_api(step.name or "")

                if reference_api is None:
                    sequence.errors.append(
                        ErrorTag(
                            error_type=ErrorType.MADE_UP_API, info=step.name
                        )
                    )

                sequence.errors.append(
                    ErrorTag(error_type=ErrorType.NEW_CALL, info=step.name)
                )

            else:
                sequence.errors.append(
                    ErrorTag(error_type=ErrorType.BAD_REPEAT, info=step.name)
                )

    for step in ground_truth.output:
        name, repeat_index = ground_truth.who_produced(step.label or "")
        label = None if name is None else sequence.get_label(name, repeat_index)

        if label is None or step.name not in [
            item.name for item in sequence.output
        ]:
            sequence.errors.append(
                ErrorTag(error_type=ErrorType.MISSING_CALL, info=step.name)
            )

    return sequence

from nestful.utils import extract_label, TOKEN
from nestful.schemas.errors import ErrorType
from random import sample, randint, seed
from typing import Optional, Dict, Any, Tuple, List, Set
from copy import deepcopy
from nestful.errors.error_tagger import tag_sequence_step, tag_sequence
from nestful import (
    SequenceStep,
    SequencingData,
    SequencingDataset,
    Catalog,
    AtomicCall,
    AtomicSequence,
)

MAX_COLLISIONS = 100
MAX_ATTEMPTS = 10


def induce_error_in_step(
    step: SequenceStep,
    catalog: Catalog,
    memory: Dict[str, Any],
    error_type: ErrorType = ErrorType.UNKNOWN,
    num_errors: int = 1,
    referred_only: bool = True,
    random_seed: Optional[int] = None,
) -> Tuple[Optional[SequenceStep], Dict[str, Any]]:
    if random_seed:
        seed(random_seed)

    if error_type == ErrorType.UNKNOWN:
        error_type = ErrorType.get_random_error()

    if error_type == ErrorType.MISSING_PARAMETER:
        error_step = remove_required_argument(
            step, catalog, num_errors, referred_only
        )

    elif error_type == ErrorType.MADE_UP_PARAMETER:
        error_step = rename_required_argument(
            step, catalog, num_errors, referred_only
        )

    elif error_type == ErrorType.MISSING_MEMORY:
        new_memory = remove_memory_item(step, memory, num_errors)
        step = tag_sequence_step(step, step, memory)

        return step if new_memory != memory else None, memory

    elif error_type == ErrorType.MADE_UP_ASSIGNMENT:
        error_step = rename_assignment(step, num_errors)

    else:
        raise NotImplementedError(f"Error type {error_type} not supported yet.")

    if error_step:
        error_step = tag_sequence_step(error_step, step, memory)

    return error_step, memory


def induce_error_in_sequence(
    sequence: SequencingData,
    catalog: Catalog,
    memory: Dict[str, Any],
    error_type: ErrorType = ErrorType.UNKNOWN,
    num_errors: int = 1,
    referred_only: bool = True,
    random_seed: Optional[int] = None,
) -> SequencingData:
    error_count = 0
    num_attempts = 0
    new_sequence = deepcopy(sequence)

    if random_seed:
        seed(random_seed)

    if error_type in [ErrorType.NEW_CALL, ErrorType.MADE_UP_API]:
        raise NotImplementedError(f"Error type {error_type} not supported yet.")

    while error_count < num_errors and num_attempts < MAX_ATTEMPTS:
        index = randint(a=0, b=len(new_sequence.output) - 1)
        step = new_sequence.output[index]

        num_attempts += 1

        if error_type == ErrorType.MISSING_CALL:
            who_used = new_sequence.who_used(step.label or "")

            if referred_only is False or len(who_used) > 0:
                new_sequence = new_sequence.remove_reference(step.label or "")
                error_count += 1
            else:
                continue

        elif error_type == ErrorType.BAD_REPEAT:
            error_step, new_memory = induce_error_in_step(
                step, catalog, memory, referred_only=referred_only
            )

            if error_step is not None:
                new_sequence.output = (
                    new_sequence.output[:index]
                    + [error_step]
                    + new_sequence.output[index:]
                )
                memory = new_memory

                error_count += 1
        else:
            error_step, new_memory = induce_error_in_step(
                step, catalog, memory, error_type, referred_only=referred_only
            )

            if error_step is not None:
                new_sequence.output[index] = error_step
                memory = new_memory

                error_count += 1

    new_sequence = tag_sequence(new_sequence, sequence, memory, catalog)
    return new_sequence


def batch_generate_error_steps(
    dataset: SequencingDataset,
    catalog: Catalog,
    num_samples: int,
    error_type: ErrorType = ErrorType.UNKNOWN,
    num_error_per_sample: int = 1,
    referred_only: bool = True,
    forbidden_indices: Optional[List[int]] = None,
    random_seed: Optional[int] = None,
    fill_in_memory: bool = True,
) -> List[AtomicCall]:
    current_samples: List[AtomicCall] = []
    stored_hashes = set()
    total_collisions = 0

    if random_seed:
        seed(random_seed)

    new_dataset = SequencingDataset(data=[])

    if forbidden_indices:
        for index, data in enumerate(dataset.data):
            if index not in forbidden_indices:
                new_dataset.data.append(data)
    else:
        new_dataset.data = dataset.data

    while len(current_samples) < num_samples:
        num_collisions = 0

        while num_collisions < MAX_COLLISIONS:
            random_index = randint(a=0, b=len(new_dataset.data) - 1)
            random_sequence = new_dataset.data[random_index]

            random_index = randint(a=0, b=len(random_sequence.output) - 1)
            step = random_sequence.output[random_index]

            memory = random_sequence.get_memory(
                catalog, index=random_index, fill_in_memory=fill_in_memory
            )

            error_step, new_memory = induce_error_in_step(
                step,
                catalog,
                memory,
                error_type,
                num_error_per_sample,
                referred_only,
            )

            if error_step is not None:
                call_str = error_step.pretty_print(collapse_maps=True)
                new_hash = hash(call_str)

                if new_hash in stored_hashes:
                    num_collisions += 1
                else:
                    stored_hashes.add(new_hash)

                    current_samples.append(
                        AtomicCall(
                            input=random_sequence.input,
                            call=error_step,
                            memory=new_memory,
                            ground_truth=AtomicCall(
                                input=random_sequence.input,
                                call=step,
                                memory=memory,
                            ),
                        )
                    )

                    break

            if num_collisions == MAX_COLLISIONS:
                total_collisions += 1

                if total_collisions == MAX_COLLISIONS:
                    return current_samples

    return current_samples


def batch_generate_error_sequences(
    dataset: SequencingDataset,
    catalog: Catalog,
    num_samples: int,
    error_type: ErrorType = ErrorType.UNKNOWN,
    num_error_per_sample: int = 1,
    referred_only: bool = True,
    forbidden_indices: Optional[List[int]] = None,
    random_seed: Optional[int] = None,
) -> List[AtomicSequence]:
    current_samples: List[AtomicSequence] = []
    stored_hashes = set()
    total_collisions = 0

    if random_seed:
        seed(random_seed)

    new_dataset = SequencingDataset(data=[])

    if forbidden_indices:
        for index, data in enumerate(dataset.data):
            if index not in forbidden_indices:
                new_dataset.data.append(data)
    else:
        new_dataset.data = dataset.data

    while len(current_samples) < num_samples:
        num_collisions = 0

        while num_collisions < MAX_COLLISIONS:
            random_index = randint(a=0, b=len(new_dataset.data) - 1)
            random_sequence = new_dataset.data[random_index]
            memory: Dict[str, Any] = {}

            error_sequence = induce_error_in_sequence(
                random_sequence,
                catalog,
                memory,
                error_type,
                num_error_per_sample,
                referred_only,
            )

            if error_sequence.num_errors > 0:
                call_str = error_sequence.pretty_print(
                    mapper_tag="=", collapse_maps=True
                )
                new_hash = hash(call_str)

                if new_hash in stored_hashes:
                    num_collisions += 1
                else:
                    stored_hashes.add(new_hash)

                    current_samples.append(
                        AtomicSequence(
                            sequence=error_sequence,
                            ground_truth=random_sequence,
                        )
                    )

                    break

            if num_collisions == MAX_COLLISIONS:
                total_collisions += 1

                if total_collisions == MAX_COLLISIONS:
                    return current_samples

    return current_samples


def remove_required_argument(
    step: SequenceStep,
    catalog: Catalog,
    num: int = 1,
    referred_only: bool = True,
) -> Optional[SequenceStep]:
    error_step = deepcopy(step)
    required_params = error_step.get_required_args(catalog)

    if referred_only:
        referred_assignments = get_args_with_labeled_assignments(step.arguments)
        required_params = {
            item for item in required_params if item in referred_assignments
        }

    if num > len(required_params):
        return None

    else:
        params_to_remove = sample(list(required_params), num)

        for item in params_to_remove:
            del error_step.arguments[item]

        return error_step


def rename_required_argument(
    step: SequenceStep,
    catalog: Catalog,
    num: int = 1,
    referred_only: bool = True,
) -> Optional[SequenceStep]:
    error_step = deepcopy(step)
    required_params = error_step.get_required_args(catalog)

    if referred_only:
        referred_assignments = get_args_with_labeled_assignments(step.arguments)
        required_params = {
            item for item in required_params if item in referred_assignments
        }

    if num > len(required_params):
        return None

    else:
        params_to_rename = sample(list(required_params), num)

        for item in params_to_rename:
            new_argument = transform_variable(item)
            error_step.arguments[new_argument] = step.arguments[item]

            del error_step.arguments[item]

        return error_step


def remove_memory_item(
    step: SequenceStep, memory: Dict[str, Any], num: int = 1
) -> Dict[str, Any]:
    keys_of_interest = get_labels_from_labeled_assignments(step.arguments)

    if num > len(keys_of_interest):
        return memory

    else:
        key_to_remove = sample(list(keys_of_interest), num)

        for item in key_to_remove:
            memory[item] = {}

        return memory


def rename_assignment(
    step: SequenceStep, num: int = 1
) -> Optional[SequenceStep]:
    error_step = deepcopy(step)
    args_of_interest = get_args_with_labeled_assignments(step.arguments)

    if num > len(args_of_interest):
        return None

    else:
        assignments_to_reassign = sample(list(args_of_interest), num)

        for item in assignments_to_reassign:
            label, mapping = extract_label(str(step.arguments[item]))

            if mapping:
                mapping_components = mapping.split(".")
                mapping_components[-1] = transform_variable(
                    mapping_components[-1]
                )

                new_mapping = ".".join(mapping_components)
                error_step.arguments[item] = f"${label}.{new_mapping}$"

        return error_step


def get_labels_from_labeled_assignments(arguments: Dict[str, Any]) -> Set[str]:
    args_of_interest = set()

    for arg, value in arguments.items():
        label, mapping = extract_label(str(value))

        if label.startswith(TOKEN):
            args_of_interest.add(label)

    return args_of_interest


def get_args_with_labeled_assignments(arguments: Dict[str, Any]) -> Set[str]:
    args_of_interest = set()

    for arg, value in arguments.items():
        label, mapping = extract_label(str(value))

        if label.startswith(TOKEN) and mapping is not None:
            args_of_interest.add(arg)

    return args_of_interest


def transform_variable(name: str) -> str:
    # TODO: ISS24 Need to replace with better generator
    return name[::-1]

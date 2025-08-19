from random import randint, choice
from typing import Optional, List
from nestful import SequencingDataset, SequencingData, Catalog
from nestful.schemas.sequences import AtomicCall, Question
from nestful.memory import resolve_item_in_memory
from nestful.errors.error_generator import get_args_with_labeled_assignments
from nestful.hypothesis_generator.utils import merge_in_order
from nestful.hypothesis_generator.random_hypothesis import (
    generate_dummy_output_sequence,
)

MAX_COLLISIONS = 100


def generate_atomic_calls(
    dataset: SequencingDataset,
    catalog: Catalog,
    num_samples: int,
    use_memory: bool = False,
    min_string_length: int = 3,
    min_array_length: int = 3,
    min_backing_steps: int = 1,
    split_merge: bool = False,
    forbidden_indices: Optional[List[int]] = None,
    max_collisions: int = MAX_COLLISIONS,
) -> List[AtomicCall]:
    def get_random_sequence() -> SequencingData:
        random_id = randint(a=0, b=len(new_dataset.data) - 1)
        return new_dataset.data[random_id]

    current_samples: List[AtomicCall] = []
    stored_hashes = set()
    total_collisions = 0

    new_dataset = SequencingDataset(data=[])

    if forbidden_indices:
        for index, data in enumerate(dataset.data):
            if index not in forbidden_indices:
                new_dataset.data.append(data)
    else:
        new_dataset.data = dataset.data

    while len(current_samples) < num_samples:
        num_collisions = 0

        while num_collisions < max_collisions:
            indices_of_interest: List[int] = []
            random_sequence = get_random_sequence()

            for index, step in enumerate(random_sequence.output):
                args_of_interest = get_args_with_labeled_assignments(
                    step.arguments
                )

                if args_of_interest:
                    indices_of_interest.append(index)

            if indices_of_interest:
                random_index = choice(indices_of_interest)
                step = random_sequence.output[random_index]

                args_of_interest = get_args_with_labeled_assignments(
                    step.arguments
                )

                arg_of_interest = choice(list(args_of_interest))

                memory = generate_dummy_output_sequence(
                    random_sequence,
                    catalog,
                    index=random_index,
                    use_memory=use_memory,
                    min_string_length=min_string_length,
                    min_array_length=min_array_length,
                )

                call_str = step.pretty_print(collapse_maps=True)
                new_hash = hash(f"{call_str} + {arg_of_interest}")

                if new_hash in stored_hashes:
                    num_collisions += 1
                else:
                    stored_hashes.add(new_hash)

                    assignment = step.arguments[arg_of_interest]
                    backing_steps = random_sequence.output[:random_index]

                    while len(backing_steps) < min_backing_steps:
                        random_backing_sequence = get_random_sequence()
                        backing_memory = generate_dummy_output_sequence(
                            random_backing_sequence,
                            catalog,
                            index=len(random_backing_sequence.output),
                            use_memory=use_memory,
                            min_string_length=min_string_length,
                            min_array_length=min_array_length,
                        )

                        memory = {**backing_memory, **memory}

                        if split_merge:
                            backing_steps = merge_in_order(
                                random_backing_sequence.output, backing_steps
                            )

                        else:
                            backing_steps = (
                                random_backing_sequence.output + backing_steps
                            )

                    answer = resolve_item_in_memory(assignment, memory)

                    if answer:
                        question_object = Question(
                            user_said=random_sequence.input,
                            argument=arg_of_interest,
                            assignment=assignment,
                            resolved=answer,
                        )

                        print(f"Question: {question_object}, Answer: {answer}")

                        current_samples.append(
                            AtomicCall(
                                call=step,
                                memory=memory,
                                question=question_object,
                                backing_steps=backing_steps,
                            )
                        )

                    break

                if num_collisions == max_collisions:
                    total_collisions += 1

                    if total_collisions == max_collisions:
                        return current_samples

    return current_samples

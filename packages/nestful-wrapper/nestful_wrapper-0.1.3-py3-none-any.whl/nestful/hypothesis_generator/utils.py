from typing import List, Any
from random import randint


def merge_in_order(
    l1: List[Any], l2: List[Any], allow_duplicates: bool = True
) -> List[Any]:
    merged_list = []
    l1_index, l2_index = 0, 0

    while l1_index < len(l1) or l2_index < len(l2):
        if l1_index == len(l1):
            choose_source = 2
        elif l2_index == len(l2):
            choose_source = 1
        else:
            choose_source = randint(a=1, b=2)

        if choose_source == 1:
            new_item = l1[l1_index]
            l1_index += 1

        else:
            new_item = l2[l2_index]
            l2_index += 1

        if allow_duplicates is True or new_item not in merged_list:
            merged_list.append(new_item)

    return merged_list

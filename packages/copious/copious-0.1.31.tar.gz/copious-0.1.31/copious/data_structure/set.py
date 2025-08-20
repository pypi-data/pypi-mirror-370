from typing import List, Union, Set


def find_consecutive_subsets(numbers: Union[List, Set]) -> List[List]:
    # Convert the set to a sorted list
    sorted_numbers = sorted(numbers)
    
    subsets = []
    current_subset = []
    
    for i in range(len(sorted_numbers)):
        if not current_subset or sorted_numbers[i] == current_subset[-1] + 1:
            current_subset.append(sorted_numbers[i])
        else:
            subsets.append(current_subset)
            current_subset = [sorted_numbers[i]]
    
    if current_subset:
        subsets.append(current_subset)
    
    return subsets


__all__ = ["find_consecutive_subsets"]

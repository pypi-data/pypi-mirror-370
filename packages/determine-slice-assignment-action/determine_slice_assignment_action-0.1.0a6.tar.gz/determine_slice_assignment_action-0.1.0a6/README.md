This function determines what action should be taken when performing slice assignment on a sequence.

## Usage

```python
class SliceAssignmentAction: ...


class NoAction(SliceAssignmentAction): pass


class ReplaceOffsetRange(SliceAssignmentAction):
    offset_start: int
    offset_stop: int
    offset_step: int


class Insert(SliceAssignmentAction):
    index: int
    reverse: bool


def determine_slice_assignment_action(sequence_length: int, slice_object: slice) -> SliceAssignmentAction: ...
```

The function takes:

- `sequence_length: int`: Length of the target sequence
- `slice_object: slice`: The slice object

It returns one of several action classes that describe how the assignment should be handled:

- `NoAction`: No operation needed
- `ReplaceOffsetRange`: Replace a valid and **canonicalized** (`step != 0, length >= 0, stop == start + length * step`)
  offset range of elements in the sequence
- `Insert`: Insert new elements at a specific index (in the closed interval `[0, sequence_length]`)

## Implementation

1. The function first converts the slice to absolute offsets using `slice_to_offset_range`.
2. For empty selections (where `start == stop`):
    - If the index is within bounds, it's an insertion
    - If before the sequence, it's an insertion at the beginning
    - If after, it's an insertion at the end
3. For non-empty sequences:
    - With positive step: splits the interval and either replaces or inserts at the beginning or end
    - With negative step: similar but works in reverse

One notable limitation is that some negative step cases aren't fully supported in Python's actual slice assignment (
`ValueError: attempt to assign sequence of size 2 to extended slice of size 0`), but the function still returns the
theoretically correct action.

## Examples

```python
from determine_slice_assignment_action import *

# Non-empty sequence, non-empty slice (`ReplaceOffsetRange`)

# l = list(range(10)); l[2:20] = [False, True]; print(l)
# [0, 1, False, True]
result = determine_slice_assignment_action(10, slice(2, 20))
assert isinstance(result, ReplaceOffsetRange)
assert (result.offset_start, result.offset_stop, result.offset_step) == (2, 10, 1)  # Canonicalized

# l = list(range(10)); l[2:-3:2] = [False, True, False]; print(l)
# [0, 1, False, 3, True, 5, False, 7, 8, 9]
result = determine_slice_assignment_action(10, slice(2, -3, 2))
assert isinstance(result, ReplaceOffsetRange)
assert (result.offset_start, result.offset_stop, result.offset_step) == (2, 8, 2)  # Canonicalized

# l = list(range(10)); l[5:3:-1] = [False, True]; print(l)
# [0, 1, 2, 3, True, False, 6, 7, 8, 9]
result = determine_slice_assignment_action(10, slice(5, 3, -1))
assert isinstance(result, ReplaceOffsetRange)
assert (result.offset_start, result.offset_stop, result.offset_step) == (5, 3, -1)

# l = list(range(10)); l[5:-12:-1] = [False, True, False, True, False, True]; print(l)
# [True, False, True, False, True, False, 6, 7, 8, 9]
result = determine_slice_assignment_action(10, slice(5, -12, -1))
assert isinstance(result, ReplaceOffsetRange)
assert (result.offset_start, result.offset_stop, result.offset_step) == (5, -1, -1)  # Canonicalized

# Non-empty sequence, empty slice (`Insert`)

# l = list(range(10)); l[5:5] = [False, True]; print(l)
# [0, 1, 2, 3, 4, False, True, 5, 6, 7, 8, 9]
result = determine_slice_assignment_action(10, slice(5, 5))
assert isinstance(result, Insert)
assert result.reverse == False
assert result.index == 5

# l = list(range(10)); l[5:3] = [False, True]; print(l)
# [0, 1, 2, 3, 4, False, True, 5, 6, 7, 8, 9]
result = determine_slice_assignment_action(10, slice(5, 3))
assert isinstance(result, Insert)
assert result.reverse == False
assert result.index == 5

# l = list(range(10)); l[-11:-11] = [False, True]; print(l)
# [False, True, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
result = determine_slice_assignment_action(10, slice(-11, -11))
assert isinstance(result, Insert)
assert result.reverse == False
assert result.index == 0

# l = list(range(10)); l[-12:0] = [False, True]; print(l)
# [False, True, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
result = determine_slice_assignment_action(10, slice(-12, 0))
assert isinstance(result, Insert)
assert result.reverse is False
assert result.index == 0

# l = list(range(10)); l[10:10] = [False, True]; print(l)
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, False, True]
result = determine_slice_assignment_action(10, slice(10, 10))
assert isinstance(result, Insert)
assert result.reverse == False
assert result.index == 10

# l = list(range(10)); l[15:20] = [False, True]; print(l)
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, False, True]
result = determine_slice_assignment_action(10, slice(15, 20))
assert isinstance(result, Insert)
assert result.reverse is False
assert result.index == 10

# l = list(range(10)); l[10:10:-1] = [False, True]; print(l)
# Theoretically possible, not yet supported by Python
# ValueError: attempt to assign sequence of size 2 to extended slice of size 0
result = determine_slice_assignment_action(10, slice(10, 10, -1))
assert isinstance(result, Insert)
assert result.reverse == True
assert result.index == 10

# l = list(range(10)); l[20:15:-1] = [False, True]; print(l)
# Theoretically possible, not yet supported by Python
# ValueError: attempt to assign sequence of size 2 to extended slice of size 0
result = determine_slice_assignment_action(10, slice(20, 15, -1))
assert isinstance(result, Insert)
assert result.reverse is True
assert result.index == 10

# l = list(range(10)); l[-11:-15:-1] = [False, True]; print(l)
# Theoretically possible, not yet supported by Python
# ValueError: attempt to assign sequence of size 2 to extended slice of size 0
result = determine_slice_assignment_action(10, slice(-11, -15, -1))
assert isinstance(result, Insert)
assert result.reverse is True
assert result.index == 0

# Empty sequence, empty slice (`Insert`)

# l = list(); l[0:5] = [False, True]; print(l)
# [False, True]
result = determine_slice_assignment_action(0, slice(0, 5))
assert isinstance(result, Insert)
assert result.reverse is False
assert result.index == 0

# l = list(); l[5:0:-1] = [False, True]; print(l)
# Theoretically possible, not yet supported by Python
# ValueError: attempt to assign sequence of size 2 to extended slice of size 0
result = determine_slice_assignment_action(0, slice(5, 0, -1))
assert isinstance(result, Insert)
assert result.reverse is True
assert result.index == 0
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
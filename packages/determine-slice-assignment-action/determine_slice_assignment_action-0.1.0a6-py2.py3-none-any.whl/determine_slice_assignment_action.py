# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from operator import gt, lt

from canonical_interval import CanonicalInterval
from canonical_range import canonicalize_stop, slice_to_offset_range


class SliceAssignmentAction(object): pass


class NoAction(SliceAssignmentAction): pass


class ReplaceOffsetRange(SliceAssignmentAction):
    __slots__ = ('offset_start', 'offset_stop', 'offset_step')

    def __new__(cls, offset_start, offset_stop, offset_step):
        instance = super(ReplaceOffsetRange, cls).__new__(cls)
        instance.offset_start = offset_start
        instance.offset_stop = canonicalize_stop(offset_start, offset_stop, offset_step)
        instance.offset_step = offset_step
        return instance


class Insert(SliceAssignmentAction):
    __slots__ = ('index', 'reverse')

    def __new__(cls, index, reverse):
        instance = super(Insert, cls).__new__(cls)
        instance.index = index
        instance.reverse = reverse
        return instance


def determine_slice_assignment_action(sequence_length, slice_object):
    # type: (int, slice) -> SliceAssignmentAction
    if sequence_length < 0:
        raise ValueError('sequence length must be non-negative')

    # new_offset_step > 0, new_offset_start <= canonicalized_new_offset_stop
    # new_offset_step < 0, new_offset_start >= canonicalized_new_offset_stop
    new_offset_start, canonicalized_new_offset_stop, new_offset_step = slice_to_offset_range(sequence_length, slice_object)

    # The slice is empty
    if new_offset_start == canonicalized_new_offset_stop:
        if new_offset_start < 0:
            return Insert(0, reverse=new_offset_step < 0)
        elif new_offset_start < sequence_length:
            return Insert(new_offset_start, reverse=new_offset_step < 0)
        else:
            return Insert(sequence_length, reverse=new_offset_step < 0)
    # The sequence is empty
    elif sequence_length == 0:
        return Insert(0, reverse=new_offset_step < 0)
    # Non-empty slice and sequence
    # new_offset_step > 0, new_offset_start < canonicalized_new_offset_stop
    # new_offset_step < 0, new_offset_start > canonicalized_new_offset_stop
    else:
        if new_offset_step > 0:
            first_valid_offset = 0
            one_past_last_valid_offset = sequence_length

            leftmost_insertion_point = 0
            rightmost_insertion_point = sequence_length

            comparator = lt
        else:
            first_valid_offset = sequence_length - 1
            one_past_last_valid_offset = -1

            leftmost_insertion_point = sequence_length
            rightmost_insertion_point = 0

            comparator = gt

        current_offset_interval = CanonicalInterval(first_valid_offset, one_past_last_valid_offset, comparator)
        nonempty_new_offset_interval = CanonicalInterval(new_offset_start, canonicalized_new_offset_stop, comparator)
        before, within, after = current_offset_interval.three_way_split(nonempty_new_offset_interval)
        if within:
            intersection_offset_start = within.start
            intersection_offset_stop = within.stop
            return ReplaceOffsetRange(intersection_offset_start, intersection_offset_stop, new_offset_step)
        elif before:
            return Insert(leftmost_insertion_point, reverse=new_offset_step < 0)
        else:
            return Insert(rightmost_insertion_point, reverse=new_offset_step < 0)

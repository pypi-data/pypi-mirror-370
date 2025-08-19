from typing import Container, Iterable, Sequence, TypeVar
from cowlist import COWList

T = TypeVar('T')


def seqtok(sequence, separators):
    # type: (Sequence[T], Container[T]) -> Iterable[Sequence[T]]
    """Splits a sequence into tokens separated by any of the separator elements.

    Mimics the behavior of C's strtok() function:

    - Consecutive separators are treated as a single separator
    - Leading/trailing separators are ignored (no empty tokens)
    - Returns tokens one at a time via iteration

    But with crucial differences:

    - State is encapsulated in the generator instance (no global state)
        - No thread safety concerns from global state
    - Each iterator maintains independent state (safe for separate instances)
        - Multiple tokenizers can operate simultaneously
    - Original sequence is never modified
    - Immutable tokens via COWList (Copy-On-Write List)

    Args:
        sequence: Input sequence to be tokenized (any Sequence[T])
        separators: Container of separator elements (any Container[T])

    Yields:
        Immutable subsequences of the original sequence between separators

    Example:
        >>> list(seqtok([1, 2, 0, 3, 4, 0, 0, 5], {0}))
        [COWList([1, 2]), COWList([3, 4]), COWList([5])]
    """
    last_element_is_separator = True
    immutable_element_buffer = COWList()

    for element in sequence:
        if last_element_is_separator:
            if element not in separators:
                # State transition
                last_element_is_separator = False
                immutable_element_buffer = immutable_element_buffer.append(element)
        else:
            if element not in separators:
                immutable_element_buffer = immutable_element_buffer.append(element)
            else:
                # State transition
                last_element_is_separator = True
                yield immutable_element_buffer
                immutable_element_buffer = immutable_element_buffer.clear()

    if immutable_element_buffer:
        yield immutable_element_buffer

from typing import Iterator, List, TypeVar

T = TypeVar("T")


def batch_of_length(
    elements: List[T],
    batch_size: int,
) -> Iterator[List[T]]:
    """
    Split the given elements into smaller chunks
    """
    assert batch_size > 1, "batch size must be greater or equal to 1"
    element_count = len(elements)
    for index in range(0, element_count, batch_size):
        yield elements[index : min((index + batch_size), element_count)]

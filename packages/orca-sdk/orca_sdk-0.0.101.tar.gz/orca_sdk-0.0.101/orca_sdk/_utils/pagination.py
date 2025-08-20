from __future__ import annotations

from typing import Callable, Generic, Iterator, TypedDict, TypeVar, cast, overload

T = TypeVar("T")
R = TypeVar("R")


class Page(TypedDict, Generic[T]):
    items: list[T]
    count: int


class _PagedIterable(Generic[T, R]):
    def __init__(
        self,
        fetch: Callable[[int, int], Page[T]],
        *,
        transform: Callable[[T], R] | None = None,
        page_size: int = 100,
    ) -> None:
        """
        Iterate over a paginated endpoint.

        Parameters:
            fetch: function to fetch a page from the endpoint `(limit: int, offset: int) -> TypedDict[{items: list[T], count: int}]`
            transform: Optional function to transforms item types `(item: T) -> R`, defaults to identity
            limit: maximum number of items to fetch per page
        """
        self.fetch = fetch
        self.transform = transform or (lambda x: cast(R, x))
        self.page_size = page_size
        self.offset = 0  # tracks how much has been yielded, not fetched
        self.page = fetch(self.page_size, self.offset)  # fetch first page to populate count
        self.count = self.page["count"]

    def __iter__(self) -> Iterator[R]:
        if self.offset >= self.count:
            self.offset = 0
            if len(self.page["items"]) < self.count:
                # refetch first page unless we are still on the first page
                self.page = self.fetch(self.page_size, self.offset)

        # yield prefetched first page
        if self.offset == 0:
            yield from map(self.transform, self.page["items"])
            self.offset += len(self.page["items"])

        # yield remaining pages one by one
        while self.offset < self.count:
            self.page = self.fetch(self.page_size, self.offset)
            yield from map(self.transform, self.page["items"])
            self.offset += len(self.page["items"])

    @overload
    def __getitem__(self, key: int) -> R:
        pass

    @overload
    def __getitem__(self, key: slice) -> list[R]:
        pass

    def __getitem__(self, key: int | slice) -> R | list[R]:
        if isinstance(key, int):
            effective_key = key
            if effective_key < 0:
                effective_key += self.count
            if not 0 <= effective_key < self.count:
                raise IndexError(f"Index {key} out of range")
            # if key is on current page, return item
            if self.offset <= effective_key < self.offset + len(self.page["items"]):
                return self.transform(self.page["items"][effective_key - self.offset])
            # otherwise, fetch and return the single item
            return self.transform(self.fetch(1, effective_key)["items"][0])

        elif isinstance(key, slice):
            start, stop, step = key.indices(self.count)
            if step != 1:
                raise ValueError("Stepped slicing is not supported")
            start = start + self.count if start < 0 else start or 0
            stop = stop + self.count if stop < 0 else stop or self.count
            if start >= self.count or stop > self.count:
                raise IndexError(f"Slice {key} out of range")
            limit = min(self.page_size, stop - start)
            if limit <= 0:
                return []
            items = []
            for i in range(start, stop, limit):
                page = self.fetch(limit, i)
                items.extend(map(self.transform, page["items"]))
            return items

    def __len__(self) -> int:
        return self.count


# type checking workaround until python 3.13 allows declaring the class as PagedIterable[T, R = T]


@overload
def PagedIterable(
    fetch: Callable[[int, int], Page[T]],
    *,
    transform: None = None,
    page_size: int = 100,
) -> _PagedIterable[T, T]:
    pass


@overload
def PagedIterable(
    fetch: Callable[[int, int], Page[T]],
    *,
    transform: Callable[[T], R],
    page_size: int = 100,
) -> _PagedIterable[T, R]:
    pass


def PagedIterable(
    fetch: Callable[[int, int], Page[T]],
    *,
    transform: Callable[[T], R] | None = None,
    page_size: int = 100,
) -> _PagedIterable[T, R]:
    return _PagedIterable(fetch, transform=transform, page_size=page_size)

import pytest

from .pagination import Page, PagedIterable


class MockEndpoint:
    """Mock paginated endpoint for testing"""

    def __init__(self, total_items: int):
        self.items = list(range(total_items))
        self.fetch_count = 0

    def fetch(self, limit: int, offset: int) -> Page[int]:
        self.fetch_count += 1
        end_index = min(offset + limit, len(self.items))
        items = self.items[offset:end_index]
        return {"items": items, "count": len(self.items)}


def test_basic_pagination():
    # Given a mock endpoint with 5 items
    endpoint = MockEndpoint(5)
    # When doing a paginated iteration
    paginated = PagedIterable(endpoint.fetch, page_size=2)
    # Then we should be able to iterate through all items
    assert list(paginated) == [0, 1, 2, 3, 4]
    # And the length should be correct
    assert len(paginated) == 5
    # And 3 requests: [0,1], [2,3], [4] should have been made, one for each page
    assert endpoint.fetch_count == 3


def test_empty_results():
    # Given an empty mock endpoint
    endpoint = MockEndpoint(0)
    # When doing a paginated iteration
    paginated = PagedIterable(endpoint.fetch, page_size=5)
    # Then we should get an empty list
    assert list(paginated) == []
    # And the length should be 0
    assert len(paginated) == 0
    # And only one request should have been made, for the first page
    assert endpoint.fetch_count == 1


def test_transform_function():
    # Given a mock endpoint with 4 items
    endpoint = MockEndpoint(4)
    # And a transform function that doubles the items
    transform = lambda x: f"2x={2*x}"
    # When doing a paginated iteration with a transform function
    paginated = PagedIterable(endpoint.fetch, transform=transform, page_size=2)
    # Then we should get the transformed items
    assert list(paginated) == ["2x=0", "2x=2", "2x=4", "2x=6"]


def test_multiple_iterations():
    # Given a mock endpoint with 5 items
    endpoint = MockEndpoint(5)
    # When we do 2 paginated iterations
    paginated = PagedIterable(endpoint.fetch, page_size=2)
    result1 = list(paginated)
    result2 = list(paginated)
    # Then we should get the same items twice
    assert result1 == result2 == [0, 1, 2, 3, 4]
    # And 6 requests should have been made, 3 for each iteration
    assert endpoint.fetch_count == 6


def test_single_page_optimization():
    # Given a mock endpoint with 5 items
    endpoint = MockEndpoint(5)
    # When doing a paginated iteration with a limit that is greater than the number of items
    paginated = PagedIterable(endpoint.fetch, page_size=10)
    # Then we should get all items
    assert list(paginated) == [0, 1, 2, 3, 4]
    # And the length should be 5
    assert len(paginated) == 5
    # And only one request should have been made
    assert endpoint.fetch_count == 1
    # And a second iteration should not make any additional requests
    assert list(paginated) == [0, 1, 2, 3, 4]
    assert endpoint.fetch_count == 1


def test_indexing():
    # Given a mock endpoint with 7 items
    endpoint = MockEndpoint(7)
    # When creating a paginated iterable with page size 3
    paginated = PagedIterable(endpoint.fetch, page_size=3)
    # Then we should be able to access items by index
    assert paginated[0] == 0
    assert paginated[2] == 2
    assert paginated[6] == 6
    # And negative indices should work
    assert paginated[-1] == 6
    # And accessing out of bounds should raise IndexError
    with pytest.raises(IndexError):
        paginated[7]
    with pytest.raises(IndexError):
        paginated[-8]
    # And transforms are applied
    assert PagedIterable(endpoint.fetch, transform=lambda x: x * 10, page_size=3)[1] == 10


def test_slicing():
    # Given a mock endpoint with 10 items
    endpoint = MockEndpoint(10)
    # When creating a paginated iterable
    paginated = PagedIterable(endpoint.fetch, page_size=3)
    # Then we should be able to slice it
    assert list(paginated[2:5]) == [2, 3, 4]
    assert list(paginated[:3]) == [0, 1, 2]
    assert list(paginated[7:]) == [7, 8, 9]
    # And negative indices should work
    assert list(paginated[:-5]) == [0, 1, 2, 3, 4, 5]
    assert list(paginated[-3:]) == [7, 8, 9]
    assert list(paginated[-5:-2]) == [5, 6, 7]
    # And empty slices should work
    assert list(paginated[5:5]) == []
    # And slicing with a start and stop that are out of bounds should raise IndexError
    with pytest.raises(IndexError):
        list(paginated[20:25])
    # And slicing with a step other than 1 should raise ValueError
    with pytest.raises(ValueError):
        list(paginated[::2])
    with pytest.raises(ValueError):
        list(paginated[1:8:3])
    with pytest.raises(ValueError):
        list(paginated[::-1])
    # And transforms are applied
    assert list(PagedIterable(endpoint.fetch, transform=lambda x: x * 10, page_size=3)[1:3]) == [10, 20]
